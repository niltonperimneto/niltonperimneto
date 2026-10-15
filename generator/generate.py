#!/usr/bin/env python3
"""CLI entry point. Run from any directory with Python 3.10 or newer."""

import argparse
import json
import logging
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

# Keep both `python3 generator/generate.py` and `python3 -m generator.generate` working.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator.config import ConfigError, DEFAULT_CONFIG_PATH, DEFAULT_OUTPUT_DIR, load_config
from generator.github import fetch_avatar_data_uri, fetch_github_data
from generator.render import render_card


def generate_assets(config, data, output_dir, avatar=""):
    """Build and validate all variants before writing any output files."""
    assets = {}
    for layout in ("wide", "portrait"):
        for theme in (None, "dark", "light"):
            suffix = f"-{theme}" if theme else ""
            name = f"zed-card-{layout}{suffix}.svg"
            assets[name] = render_card(config, data, theme, layout == "portrait", avatar)
    for theme in ("dark", "light"):
        assets[f"zed-card-{theme}.svg"] = assets[f"zed-card-wide-{theme}.svg"]
    for svg in assets.values():
        ET.fromstring(svg)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in assets.items():
        (output_dir / name).write_text(svg, encoding="utf-8")
    return list(assets)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate minimal GitHub profile cards (Python standard library only).")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="JSON customization file")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="destination for the eight SVG variants")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--offline", action="store_true", help="use config only; make no network requests")
    source.add_argument("--data-file", type=Path, help="render a saved GitHub GraphQL user object without network requests")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        config = load_config(args.config)
        if args.data_file:
            data = json.loads(args.data_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("--data-file must contain a GitHub user object.")
        elif args.offline:
            data = {}
        else:
            data = fetch_github_data(config["username"])
        avatar = ""
        if not args.offline and not args.data_file:
            avatar = fetch_avatar_data_uri(config["avatar_url"] or data.get("avatarUrl"))
        names = generate_assets(config, data, args.output_dir, avatar)
    except (ConfigError, OSError, ValueError, ET.ParseError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Generated {len(names)} SVG cards for @{config['username']} in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
