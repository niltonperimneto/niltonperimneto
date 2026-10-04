#!/usr/bin/env python3
import json
import math
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from html import escape as xml_escape

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

def xesc(val):
    if val is None:
        return ""
    return xml_escape(str(val), quote=True)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def fetch_github_data(username):
    query = """
    query {
      viewer {
        login
        name
        bio
        location
        company
        repositories(first: 50, ownerAffiliations: OWNER) {
          totalCount
          nodes {
            name
            stargazerCount
            isFork
            primaryLanguage { name }
          }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              firstDay
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    # 1. Try gh CLI first (local dev environment)
    try:
        res = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)
        if "data" in data and "viewer" in data["data"]:
            return data["data"]["viewer"]
    except Exception:
        pass

    # 2. Try GITHUB_TOKEN (CI / GitHub Actions environment)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": query}).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "ProfileCard"
                }
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "data" in data and "viewer" in data["data"]:
                    return data["data"]["viewer"]
        except Exception as e:
            print(f"Warning: GraphQL request with GITHUB_TOKEN failed: {e}")

    # 3. Fallback profile data
    return {
        "login": username,
        "name": "Nilton Perim Neto",
        "bio": "Not a Programmer, just a historian.",
        "location": "Goiás, Brazil",
        "repositories": { "totalCount": 30, "nodes": [] },
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": 963,
                "weeks": [{"contributionDays": [{"contributionCount": 0}]}] * 52
            }
        }
    }

def generate_svg(theme="dark", data=None, config=None):
    if config is None:
        config = {}
    if data is None:
        data = {}

    is_dark = (theme == "dark")
    
    if is_dark:
        bg = "#0d1117"
        card_bg = "#161b22"
        inner_bg = "#21262d"
        border = "#30363d"
        border_subtle = "#21262d"
        text_primary = "#f0f6fc"
        text_secondary = "#8b949e"
        text_tertiary = "#6e7681"
        accent = "#ffffff"
        accent_stroke = "#e6edf3"
        accent_fill_opacity = 0.12
        dot_color = "#3fb950"
        bar_colors = ["#f0f6fc", "#8b949e", "#6e7681", "#30363d"]
    else:
        bg = "#ffffff"
        card_bg = "#f6f8fa"
        inner_bg = "#eaeef2"
        border = "#d0d7de"
        border_subtle = "#e1e4e8"
        text_primary = "#1f2328"
        text_secondary = "#57606a"
        text_tertiary = "#8c959f"
        accent = "#1f2328"
        accent_stroke = "#24292f"
        accent_fill_opacity = 0.08
        dot_color = "#1a7f37"
        bar_colors = ["#1f2328", "#57606a", "#8c959f", "#d0d7de"]

    total_repos = data.get("repositories", {}).get("totalCount", 30)
    cal = data.get("contributionsCollection", {}).get("contributionCalendar", {})
    total_contribs = cal.get("totalContributions", 963)
    weeks = cal.get("weeks", [])
    
    weekly_counts = []
    for w in weeks:
        weekly_counts.append(sum(d.get("contributionCount", 0) for d in w.get("contributionDays", [])))
    
    if len(weekly_counts) > 52:
        weekly_counts = weekly_counts[-52:]
    elif len(weekly_counts) < 52:
        weekly_counts = [0] * (52 - len(weekly_counts)) + weekly_counts

    max_week = max(weekly_counts) if weekly_counts and max(weekly_counts) > 0 else 1
    peak_idx = weekly_counts.index(max_week) if weekly_counts else 0

    # Activity chart dimensions
    wave_x = 430
    wave_w = 376
    wave_y_base = 202
    wave_y_top = 132
    wave_h = wave_y_base - wave_y_top

    points = []
    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        normalized = count / max_week if max_week > 0 else 0
        py = wave_y_base - (normalized * wave_h)
        points.append((px, py))

    # Path construction with smooth Bezier curve
    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for i in range(1, len(points)):
        p0 = points[i - 1]
        p1 = points[i]
        cx1 = p0[0] + (p1[0] - p0[0]) * 0.45
        cy1 = p0[1]
        cx2 = p0[0] + (p1[0] - p0[0]) * 0.55
        cy2 = p1[1]
        path_d += f" C {cx1:.1f} {cy1:.1f}, {cx2:.1f} {cy2:.1f}, {p1[0]:.1f} {p1[1]:.1f}"

    area_d = path_d + f" L {points[-1][0]:.1f} {wave_y_base} L {points[0][0]:.1f} {wave_y_base} Z"
    peak_x, peak_y = points[peak_idx]

    langs = config.get("focus_languages", [
        {"name": "Rust", "pct": 42},
        {"name": "TypeScript", "pct": 28},
        {"name": "Python", "pct": 18},
        {"name": "C / Asm", "pct": 12}
    ])

    lang_bar_x = 44
    lang_bar_w = 328
    lang_bar_h = 7
    curr_x = lang_bar_x
    lang_rects = []
    for idx, lang in enumerate(langs):
        w_part = (lang.get("pct", 0) / 100.0) * lang_bar_w
        color = bar_colors[idx % len(bar_colors)]
        lang_rects.append((xesc(lang.get("name", "")), lang.get("pct", 0), curr_x, w_part, color))
        curr_x += w_part

    featured = config.get("featured_repos", [])[:4]
    
    raw_name = config.get("name", "Nilton Perim Neto")
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(config.get("tagline", "Not a Programmer, just a historian."))
    affiliation = xesc(config.get("affiliation", "Universidade Federal de Goiás"))
    location = xesc(config.get("location", "Goiás, Brazil"))

    # SVG Construction
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 380" width="100%" height="100%">
  <defs>
    <style>
      text {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "SF Pro Display", Roboto, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
      }}

      .tabular {{
        font-variant-numeric: tabular-nums;
      }}

      .draw-stroke {{
        stroke-dasharray: 2000;
        stroke-dashoffset: 2000;
        animation: drawPath 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}

      .fade-in {{
        opacity: 0;
        animation: fadeIn 0.6s ease forwards;
      }}

      .delay-1 {{ animation-delay: 0.15s; }}
      .delay-2 {{ animation-delay: 0.3s; }}
      .delay-3 {{ animation-delay: 0.45s; }}

      .pulse-marker {{
        animation: pulse 2.4s infinite ease-in-out;
      }}

      @keyframes drawPath {{
        to {{ stroke-dashoffset: 0; }}
      }}

      @keyframes fadeIn {{
        to {{ opacity: 1; }}
      }}

      @keyframes pulse {{
        0%, 100% {{ r: 3; opacity: 1; }}
        50% {{ r: 5.5; opacity: 0.3; }}
      }}
    </style>

    <linearGradient id="curveGrad_{theme}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="{accent_fill_opacity}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
    </linearGradient>

    <clipPath id="langBarClip">
      <rect x="{lang_bar_x}" y="184" width="{lang_bar_w}" height="{lang_bar_h}" rx="3.5"/>
    </clipPath>
  </defs>

  <!-- Card Background -->
  <rect width="850" height="380" fill="{bg}" rx="12"/>
  <rect x="0.5" y="0.5" width="849" height="379" fill="none" stroke="{border}" stroke-width="1" rx="11.5"/>

  <!-- ==================== HEADER ==================== -->
  <g class="fade-in">
    <!-- Monogram Circle -->
    <circle cx="44" cy="38" r="16" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    <text x="44" y="42" text-anchor="middle" font-size="11" font-weight="600" fill="{text_primary}">NP</text>

    <!-- Name & Tagline -->
    <text x="70" y="34" font-size="16" font-weight="600" fill="{text_primary}" letter-spacing="-0.01em">{display_name}</text>
    <text x="70" y="50" font-size="11.5" font-weight="400" fill="{text_secondary}">{tagline}</text>

    <!-- Status Badge -->
    <rect x="636" y="24" width="190" height="28" fill="{card_bg}" stroke="{border}" stroke-width="1" rx="14"/>
    <circle cx="652" cy="38" r="3.5" fill="{dot_color}"/>
    <text x="664" y="42" font-size="11" font-weight="500" fill="{text_secondary}">Systems &amp; Open Source</text>

    <!-- Header Divider -->
    <line x1="24" y1="72" x2="826" y2="72" stroke="{border}" stroke-width="1"/>
  </g>

  <!-- ==================== METRICS & LANGUAGES ==================== -->
  <g class="fade-in delay-1">
    <!-- Panel Container -->
    <rect x="24" y="86" width="368" height="148" fill="{card_bg}" stroke="{border}" stroke-width="1" rx="10"/>

    <!-- Stat 1: Repositories -->
    <text x="44" y="110" font-size="9" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">REPOSITORIES</text>
    <text x="44" y="136" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{total_repos}</text>

    <!-- Stat 2: Contributions -->
    <text x="168" y="110" font-size="9" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">YEARLY COMMITS</text>
    <text x="168" y="136" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{total_contribs}</text>

    <!-- Stat 3: Peak Activity -->
    <text x="292" y="110" font-size="9" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">WEEKLY PEAK</text>
    <text x="292" y="136" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{max_week}</text>

    <!-- Sub-divider -->
    <line x1="44" y1="152" x2="372" y2="152" stroke="{border_subtle}" stroke-width="1"/>

    <!-- Languages Header -->
    <text x="44" y="174" font-size="11" font-weight="600" fill="{text_secondary}">Primary Languages</text>

    <!-- Multi-segment Rounded Bar -->
    <g clip-path="url(#langBarClip)">
"""

    for name, pct, lx, lw, col in lang_rects:
        svg += f"""      <rect x="{lx}" y="184" width="{lw:.1f}" height="{lang_bar_h}" fill="{col}"/>\n"""

    svg += """    </g>\n\n    <!-- Language Legend -->\n    <g font-size="10" font-weight="500" fill="{text_secondary}">\n"""
    
    # Legend positions
    legend_xs = [44, 130, 230, 310]
    for idx, (name, pct, lx, lw, col) in enumerate(lang_rects[:4]):
        leg_x = legend_xs[idx]
        svg += f"""      <circle cx="{leg_x}" cy="211" r="3" fill="{col}"/>\n"""
        svg += f"""      <text x="{leg_x + 8}" y="215" fill="{text_secondary}">{name} <tspan font-weight="400" fill="{text_tertiary}">{pct}%</tspan></text>\n"""

    svg += f"""    </g>
  </g>

  <!-- ==================== ACTIVITY FLOW ==================== -->
  <g class="fade-in delay-2">
    <!-- Panel Container -->
    <rect x="408" y="86" width="418" height="148" fill="{card_bg}" stroke="{border}" stroke-width="1" rx="10"/>

    <!-- Panel Header -->
    <text x="428" y="110" font-size="11" font-weight="600" fill="{text_secondary}">Contribution Rhythm</text>
    <text x="806" y="110" text-anchor="end" font-size="10" font-weight="500" fill="{text_tertiary}">52-Week Trajectory</text>

    <!-- Faint Guide Lines -->
    <line x1="428" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="{border_subtle}" stroke-width="1"/>
    <line x1="428" y1="{wave_y_top + wave_h/2:.1f}" x2="{wave_x + wave_w}" y2="{wave_y_top + wave_h/2:.1f}" stroke="{border_subtle}" stroke-dasharray="3,4" stroke-width="0.75"/>

    <!-- Gradient Fill -->
    <path d="{area_d}" fill="url(#curveGrad_{theme})"/>

    <!-- Elegant Curve Stroke -->
    <path class="draw-stroke" d="{path_d}" fill="none" stroke="{accent_stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>

    <!-- Peak Indicator -->
    <g transform="translate({peak_x:.1f}, {peak_y:.1f})">
      <circle cx="0" cy="0" r="3" fill="{accent_stroke}"/>
      <circle cx="0" cy="0" r="3" fill="none" stroke="{accent_stroke}" class="pulse-marker"/>
      <text x="0" y="-10" text-anchor="middle" font-size="9" font-weight="600" fill="{text_primary}">Peak: {max_week}</text>
    </g>

    <!-- Timeline Labels -->
    <g font-size="9.5" font-weight="500" fill="{text_tertiary}">
      <text x="{wave_x}" y="221">Q1</text>
      <text x="{wave_x + wave_w*0.33:.1f}" y="221" text-anchor="middle">Q2</text>
      <text x="{wave_x + wave_w*0.66:.1f}" y="221" text-anchor="middle">Q3</text>
      <text x="{wave_x + wave_w}" y="221" text-anchor="end">Q4</text>
    </g>
  </g>

  <!-- ==================== FEATURED PROJECTS ==================== -->
  <g class="fade-in delay-3">
"""

    card_coords = [
        (24, 248, 187),
        (225, 248, 187),
        (426, 248, 187),
        (627, 248, 199)
    ]

    for idx, repo in enumerate(featured):
        bx, by, bw = card_coords[idx]
        r_name = xesc(repo.get("name", ""))
        r_desc_raw = repo.get("desc", "")
        if len(r_desc_raw) > 36:
            r_desc_raw = r_desc_raw[:33] + "..."
        r_desc = xesc(r_desc_raw)
        r_stack = xesc(repo.get("stack", ""))
        r_stars = repo.get("stars", 0)

        # Star badge
        star_svg = ""
        if r_stars > 0:
            star_str = f"★ {r_stars}"
            star_w = 34 if r_stars < 10 else 40
            star_svg = f"""<rect x="{bw - star_w - 12}" y="12" width="{star_w}" height="18" fill="{inner_bg}" rx="9"/>
      <text x="{bw - 12 - star_w/2}" y="24" text-anchor="middle" font-size="9" font-weight="600" fill="{text_secondary}">{star_str}</text>"""

        # Stack tag width approx
        tag_w = max(38, len(r_stack) * 6 + 12)

        svg += f"""    <!-- Project Card {idx + 1} -->
    <g transform="translate({bx}, {by})">
      <rect width="{bw}" height="84" fill="{card_bg}" stroke="{border}" stroke-width="1" rx="8"/>
      <text x="12" y="25" font-size="12" font-weight="600" fill="{text_primary}">{r_name}</text>
      {star_svg}
      <text x="12" y="45" font-size="9.5" font-weight="400" fill="{text_secondary}">{r_desc}</text>
      
      <!-- Tech Badge -->
      <rect x="12" y="57" width="{tag_w}" height="17" fill="{inner_bg}" rx="4"/>
      <text x="{12 + tag_w/2}" y="69" text-anchor="middle" font-size="8.5" font-weight="500" fill="{text_tertiary}">{r_stack}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== FOOTER ==================== -->
  <g class="fade-in delay-3">
    <line x1="24" y1="346" x2="826" y2="346" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="364" font-size="10" font-weight="400" fill="{text_tertiary}">{affiliation} · {location}</text>
    <text x="822" y="364" text-anchor="end" font-size="10" font-weight="400" fill="{text_tertiary}">Updated via GitHub Actions · SVG Telemetry</text>
  </g>
</svg>
"""
    return svg

def main():
    config = load_config()
    username = config.get("username", "niltonperimneto")
    
    print(f"Fetching GitHub data for {username}...")
    data = fetch_github_data(username)
    
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # 1. Dark Mode SVG
    dark_svg = generate_svg(theme="dark", data=data, config=config)
    dark_path = os.path.join(ASSETS_DIR, "zed-card-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Generated dark SVG: {dark_path}")

    # 2. Light Mode SVG
    light_svg = generate_svg(theme="light", data=data, config=config)
    light_path = os.path.join(ASSETS_DIR, "zed-card-light.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Generated light SVG: {light_path}")

    print("SVG Generation completed successfully!")

if __name__ == "__main__":
    main()
