"""Load and validate the public customization interface: config.json."""

from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT / "config.json"
DEFAULT_OUTPUT_DIR = ROOT / "assets"
DEFAULT_FONT = 'ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
DEFAULTS = {
    "username": "",
    "name": "",
    "tagline": "",
    "location": "",
    "employment_status": "",
    "avatar_url": "",
    "footer_joke": "'Tis but a scratch.",
    "stack_languages": [],
    "platforms": [],
    "project_scopes": [],
    "featured_repos": [],
    "appearance": {"font_family": DEFAULT_FONT, "dark": {}, "light": {}},
    "labels": {
        "file": "~/profile.md", "languages": "Languages", "platforms": "Platforms",
        "focus": "Focus", "activity": "Activity", "projects": "Selected projects",
    },
}
PALETTE_KEYS = {"bg", "card", "border", "border-sub", "fg", "fg-muted", "fg-dim", "c1", "c2", "c3", "status"}


class ConfigError(ValueError):
    """A config problem with a message suitable for the command line."""


def load_config(path=DEFAULT_CONFIG_PATH):
    """Merge optional settings with neutral defaults and fail on invalid inputs."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ConfigError(f"Cannot read config {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigError("Config must be a JSON object.")
    unknown = raw.keys() - DEFAULTS.keys()
    if unknown:
        raise ConfigError(f"Unknown config settings: {', '.join(sorted(unknown))}")
    config = deepcopy(DEFAULTS)
    config.update(raw)
    for field in ("username", "name", "tagline", "location", "employment_status", "avatar_url", "footer_joke"):
        if not isinstance(config[field], str):
            raise ConfigError(f"{field} must be a string.")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", config["username"]):
        raise ConfigError("username must be a GitHub username (1–39 letters, digits or hyphens).")
    for field, limit in (("stack_languages", 6), ("platforms", 3), ("project_scopes", 3), ("featured_repos", 4)):
        items = config[field]
        if not isinstance(items, list) or len(items) > limit:
            raise ConfigError(f"{field} must be a list with at most {limit} entries.")
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
                raise ConfigError(f"Each {field} entry needs a nonempty name.")
            for key in ("slug", "label", "stack"):
                if key in item and not isinstance(item[key], str):
                    raise ConfigError(f"{field}.{key} must be a string.")
            if field == "project_scopes":
                pct = item.get("pct")
                if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not 0 <= pct <= 100:
                    raise ConfigError("project_scopes.pct must be a number between 0 and 100.")
    scopes = config["project_scopes"]
    if scopes and abs(sum(item["pct"] for item in scopes) - 100) > 0.01:
        raise ConfigError("project_scopes percentages must add up to 100.")
    labels = config["labels"]
    if not isinstance(labels, dict) or labels.keys() - DEFAULTS["labels"].keys() or not all(isinstance(v, str) for v in labels.values()):
        raise ConfigError("labels must contain supported label names and string values.")
    config["labels"] = DEFAULTS["labels"] | labels
    appearance = config["appearance"]
    if not isinstance(appearance, dict) or appearance.keys() - {"font_family", "dark", "light"}:
        raise ConfigError("appearance supports font_family, dark and light.")
    appearance = deepcopy(DEFAULTS["appearance"]) | appearance
    font = appearance["font_family"]
    if not isinstance(font, str) or not re.fullmatch(r"[\w\s,\"'-]+", font):
        raise ConfigError("appearance.font_family must be a CSS font stack without CSS rules.")
    for theme in ("dark", "light"):
        palette = appearance[theme]
        if not isinstance(palette, dict) or palette.keys() - PALETTE_KEYS:
            raise ConfigError(f"appearance.{theme} contains unsupported color names.")
        if not all(isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color) for color in palette.values()):
            raise ConfigError(f"appearance.{theme} colors must use #rrggbb format.")
    config["appearance"] = appearance
    return config
