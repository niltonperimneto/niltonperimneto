"""Behavioral checks for customization, data fallbacks, and standalone output."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
import xml.etree.ElementTree as ET

from generator.activity import extract_weekly_activity, selected_projects
from generator.config import ConfigError, DEFAULTS, ROOT, load_config
from generator.generate import generate_assets
from generator.github import fetch_github_data, public_calendar
from generator.render import render_card

NS = {"svg": "http://www.w3.org/2000/svg"}


class ConfigTests(unittest.TestCase):
    def load(self, value):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return load_config(path)

    def test_minimal_clone_has_neutral_defaults(self):
        config = self.load({"username": "someone-else"})
        self.assertEqual(config["name"], "")
        self.assertEqual(config["featured_repos"], [])
        self.assertEqual(config["footer_joke"], "'Tis but a scratch.")
        self.assertNotIn("Nilton", json.dumps(config))

    def test_partial_theme_and_labels_keep_defaults(self):
        config = self.load({"username": "octocat", "appearance": {"dark": {"c1": "#123456"}},
                            "labels": {"projects": "My work"}})
        root = ET.fromstring(render_card(config, {}))
        css = root.find("svg:defs/svg:style", NS).text
        self.assertIn("--c1:#123456", css)
        self.assertIn("--bg:#191919", css)
        self.assertIn("prefers-color-scheme:light", css)
        self.assertEqual(config["labels"]["languages"], "Languages")
        self.assertEqual(config["labels"]["projects"], "My work")

    def test_invalid_configuration_has_actionable_errors(self):
        cases = [
            ({"username": ""}, "username"),
            ({"unexpected": "setting"}, "Unknown config"),
            ({"platforms": [{"name": "Linux"}] * 4}, "at most 3"),
            ({"project_scopes": [{"name": "Apps", "pct": 75}]}, "add up to 100"),
            ({"project_scopes": [{"name": "Apps", "pct": True}]}, "number between"),
            ({"appearance": {"dark": {"c1": "red; color: blue"}}}, "#rrggbb"),
            ({"appearance": {"font_family": 'mono;}</style><script>bad</script>'}}, "font stack"),
        ]
        for value, message in cases:
            with self.subTest(value=value), self.assertRaisesRegex(ConfigError, message):
                self.load({"username": "octocat"} | value)

    def test_owner_and_example_configs_are_valid(self):
        for path in (ROOT / "config.json", ROOT / "examples/config.example.json"):
            with self.subTest(path=path):
                self.assertTrue(load_config(path)["username"])


class ActivityTests(unittest.TestCase):
    def test_zero_is_distinct_from_missing_activity(self):
        self.assertEqual(extract_weekly_activity({}), ([0] * 52, None))
        data = {"contributionsCollection": {"contributionCalendar": {"weeks": [], "totalContributions": 0}}}
        self.assertEqual(extract_weekly_activity(data), ([0] * 52, 0))

    def test_calendar_trims_oldest_weeks_without_changing_reported_total(self):
        weeks = [{"contributionDays": [{"contributionCount": count}]} for count in range(54)]
        data = {"contributionsCollection": {"contributionCalendar": {"weeks": weeks, "totalContributions": 9000}}}
        counts, total = extract_weekly_activity(data)
        self.assertEqual(counts, list(range(2, 54)))
        self.assertEqual(total, 9000)

    def test_explicit_projects_override_automatic_selection(self):
        config = deepcopy(DEFAULTS)
        data = {"repositories": {"nodes": [{"name": "automatic", "primaryLanguage": {"name": "Rust"}}]}}
        self.assertEqual(selected_projects(config, data), [{"name": "automatic", "stack": "Rust"}])
        config["featured_repos"] = [{"name": "chosen", "stack": "Python"}]
        self.assertEqual(selected_projects(config, data), config["featured_repos"])
        self.assertEqual(selected_projects(DEFAULTS, {}), [])


class FetchTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("generator.github.subprocess.run", side_effect=FileNotFoundError)
    @patch("generator.github.request_json", side_effect=URLError("offline"))
    def test_network_failure_never_uses_original_owner_or_fake_contributions(self, request, run):
        with self.assertLogs("generator.github", level="WARNING"):
            data = fetch_github_data("someone-else")
        self.assertEqual(data["login"], "someone-else")
        self.assertEqual(extract_weekly_activity(data), ([0] * 52, None))
        self.assertTrue(all("someone-else" in call.args[0] for call in request.call_args_list))
        self.assertNotIn("Nilton", json.dumps(data))

    @patch("generator.github.request_json")
    def test_public_calendar_respects_week_boundaries(self, request):
        request.return_value = {"contributions": [
            {"date": "2026-01-06", "count": 3},
            {"date": "2026-01-04", "count": 1},
            {"date": "2026-01-05", "count": 2},
        ]}
        calendar = public_calendar("octocat")
        counts, total = extract_weekly_activity({"contributionsCollection": {"contributionCalendar": calendar}})
        self.assertEqual(counts[-2:], [1, 5])
        self.assertEqual(total, 6)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "examples/config.example.json")

    def text(self, svg):
        root = ET.fromstring(svg)
        return " ".join(node.text or "" for node in root.findall(".//svg:text", NS))

    def test_escapes_user_content_and_derives_initials(self):
        self.config.update(name="Alice & Bob", tagline='<script>alert("x")</script>', footer_joke='Ni! <&>')
        svg = render_card(self.config, {})
        root = ET.fromstring(svg)
        self.assertIn("AB", self.text(svg))
        self.assertIn('<script>alert("x")</script>', self.text(svg))
        self.assertEqual(root.findall(".//svg:script", NS), [])
        self.assertIn("Ni! &lt;&amp;&gt;", svg)

    def test_joke_in_both_layouts_and_can_be_hidden(self):
        for portrait in (False, True):
            with self.subTest(portrait=portrait):
                svg = render_card(self.config, {}, portrait=portrait)
                self.assertIn("'Tis but a scratch.", self.text(svg))
                self.config["footer_joke"] = ""
                self.assertNotIn("scratch", self.text(render_card(self.config, {}, portrait=portrait)))
                self.config["footer_joke"] = "'Tis but a scratch."

    def test_missing_activity_and_actual_zero_have_different_labels(self):
        self.assertIn("Activity unavailable", self.text(render_card(self.config, {})))
        data = {"contributionsCollection": {"contributionCalendar": {"weeks": [], "totalContributions": 0}}}
        self.assertIn("0 contributions", self.text(render_card(self.config, data)))

    def test_unknown_icon_keeps_language_label(self):
        self.config["stack_languages"] = [{"name": "Elixir", "slug": "not-bundled"}]
        self.assertIn("Elixir", self.text(render_card(self.config, {})))

    def test_tiny_focus_segment_preserves_proportions(self):
        self.config["project_scopes"] = [{"name": "Tiny", "pct": 0.01}, {"name": "Large", "pct": 99.99}]
        root = ET.fromstring(render_card(self.config, {}))
        segments = [node for node in root.findall("svg:rect", NS) if node.get("height") == "4"]
        self.assertEqual(len(segments), 2)
        self.assertLess(float(segments[0].get("width")), 1)
        right = float(segments[-1].get("x")) + float(segments[-1].get("width"))
        self.assertAlmostEqual(right, 772, places=1)

    def test_all_variants_validate_and_legacy_aliases_match(self):
        with tempfile.TemporaryDirectory() as directory:
            names = generate_assets(self.config, {}, directory)
            self.assertEqual(len(names), 8)
            for name in names:
                root = ET.parse(Path(directory) / name).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            for theme in ("dark", "light"):
                self.assertEqual((Path(directory) / f"zed-card-{theme}.svg").read_bytes(),
                                 (Path(directory) / f"zed-card-wide-{theme}.svg").read_bytes())


class CommandLineTests(unittest.TestCase):
    def test_offline_command_works_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "generator/generate.py"), "--offline", "--config",
                 str(ROOT / "examples/config.example.json"), "--output-dir", directory],
                cwd=directory, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list(Path(directory).glob("*.svg"))), 8)
            self.assertNotIn("niltonperimneto", (Path(directory) / "zed-card-wide.svg").read_text())

    def test_bad_config_exits_cleanly_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text('{"username": ""}')
            result = subprocess.run(
                [sys.executable, "-m", "generator.generate", "--offline", "--config", str(path),
                 "--output-dir", directory], cwd=ROOT, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("username", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(list(Path(directory).glob("*.svg")), [])


if __name__ == "__main__":
    unittest.main()
