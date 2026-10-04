#!/usr/bin/env python3
import json
import math
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

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
                    "User-Agent": "ZedProfileCard"
                }
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "data" in data and "viewer" in data["data"]:
                    return data["data"]["viewer"]
        except Exception as e:
            print(f"Warning: GraphQL request with GITHUB_TOKEN failed: {e}")

    # 3. Fallback / mock profile data
    print("Using cached profile telemetry fallback...")
    return {
        "login": username,
        "name": "NILTON PERIM NETO",
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
    is_dark = (theme == "dark")
    
    if is_dark:
        bg = "#09090b"
        panel_bg = "#111114"
        subpanel_bg = "#18181b"
        border = "#27272a"
        border_light = "#3f3f46"
        grid_line = "#1a1a1e"
        text_primary = "#fafafa"
        text_secondary = "#a1a1aa"
        text_dim = "#52525b"
        accent = "#ffffff"
        pulse_color = "#ffffff"
        glow_filter = "drop-shadow(0 0 3px rgba(255, 255, 255, 0.45))"
    else:
        bg = "#ffffff"
        panel_bg = "#fafafa"
        subpanel_bg = "#f4f4f5"
        border = "#e4e4e7"
        border_light = "#d4d4d8"
        grid_line = "#f4f4f6"
        text_primary = "#09090b"
        text_secondary = "#52525b"
        text_dim = "#a1a1aa"
        accent = "#09090b"
        pulse_color = "#09090b"
        glow_filter = "none"

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

    wave_x = 422
    wave_w = 385
    wave_y_base = 188
    wave_y_top = 104
    wave_h = wave_y_base - wave_y_top

    points = []
    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        normalized = count / max_week if max_week > 0 else 0
        py = wave_y_base - (normalized * wave_h)
        points.append((px, py))

    # Path construction with bezier smoothing
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

    lang_bar_x = 46
    lang_bar_w = 325
    lang_rects = []
    curr_x = lang_bar_x
    for lang in langs:
        w_part = (lang["pct"] / 100.0) * lang_bar_w
        lang_rects.append((lang["name"], lang["pct"], curr_x, w_part))
        curr_x += w_part

    featured = config.get("featured_repos", [])[:4]
    now_str = datetime.utcnow().strftime("%Y.%m.%d // %H:%M UTC")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 370" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      
      text {{
        font-family: 'JetBrains Mono', 'SF Mono', Monaco, Menlo, Consolas, monospace;
        letter-spacing: 0.04em;
      }}

      .draw-stroke {{
        stroke-dasharray: 1800;
        stroke-dashoffset: 1800;
        animation: drawPath 2.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}

      .fade-in {{
        opacity: 0;
        animation: fadeIn 0.8s ease forwards;
      }}

      .delay-1 {{ animation-delay: 0.25s; }}
      .delay-2 {{ animation-delay: 0.5s; }}
      .delay-3 {{ animation-delay: 0.75s; }}

      .pulse-marker {{
        animation: pulse 2.2s infinite ease-in-out;
      }}

      .cursor {{
        animation: blink 1s step-end infinite;
      }}

      .scan-line {{
        animation: scan 4.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
      }}

      @keyframes drawPath {{
        to {{
          stroke-dashoffset: 0;
        }}
      }}

      @keyframes fadeIn {{
        to {{
          opacity: 1;
        }}
      }}

      @keyframes pulse {{
        0%, 100% {{ r: 3; opacity: 1; }}
        50% {{ r: 6.5; opacity: 0.25; }}
      }}

      @keyframes blink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
      }}

      @keyframes scan {{
        0% {{ transform: translateX(0px); opacity: 0; }}
        12% {{ opacity: 0.6; }}
        88% {{ opacity: 0.6; }}
        100% {{ transform: translateX({wave_w}px); opacity: 0; }}
      }}
    </style>

    <linearGradient id="areaGrad_{theme}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="{0.12 if is_dark else 0.07}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
    </linearGradient>

    <pattern id="gridPattern_{theme}" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="{grid_line}" stroke-width="0.75"/>
    </pattern>
  </defs>

  <!-- Outer Frame -->
  <rect width="850" height="370" fill="{bg}" rx="6"/>
  <rect x="0.5" y="0.5" width="849" height="369" fill="none" stroke="{border}" stroke-width="1" rx="5.5"/>

  <!-- Precision Corner Crosshairs (+) -->
  <path d="M 7 13 L 19 13 M 13 7 L 13 19" stroke="{border_light}" stroke-width="1"/>
  <path d="M 831 13 L 843 13 M 837 7 L 837 19" stroke="{border_light}" stroke-width="1"/>
  <path d="M 7 357 L 19 357 M 13 351 L 13 363" stroke="{border_light}" stroke-width="1"/>
  <path d="M 831 357 L 843 357 M 837 351 L 837 363" stroke="{border_light}" stroke-width="1"/>

  <!-- ==================== HEADER ==================== -->
  <g class="fade-in">
    <line x1="24" y1="46" x2="826" y2="46" stroke="{border}" stroke-width="1"/>
    <text x="28" y="32" font-size="11.5" font-weight="700" fill="{accent}">[ 01 // NILTON PERIM NETO ]</text>
    <text x="245" y="32" font-size="10" font-weight="400" fill="{text_secondary}">{config.get('tagline', 'Not a Programmer, just a historian.')}</text>
    
    <rect x="674" y="20" width="152" height="18" fill="{subpanel_bg}" stroke="{border_light}" stroke-width="0.8" rx="2"/>
    <circle cx="686" cy="29" r="3" fill="{accent}"/>
    <text x="696" y="33" font-size="9" font-weight="500" fill="{text_primary}">SYS.TELEMETRY // NOMINAL</text>
  </g>

  <!-- ==================== TELEMETRY MATRIX ==================== -->
  <g class="fade-in delay-1">
    <rect x="24" y="60" width="365" height="152" fill="{panel_bg}" stroke="{border}" stroke-width="1" rx="3"/>
    
    <path d="M 24 82 L 389 82" stroke="{border}" stroke-width="1"/>
    <text x="36" y="76" font-size="9.5" font-weight="700" fill="{text_dim}">// TELEMETRY_MATRIX</text>
    <text x="325" y="76" font-size="8.5" fill="{text_dim}">[SYS.STAT]</text>

    <g font-size="10" fill="{text_secondary}">
      <text x="36" y="104">REPOSITORIES</text>
      <line x1="130" y1="102" x2="330" y2="102" stroke="{border}" stroke-dasharray="2,4" stroke-width="0.8"/>
      <text x="375" y="104" text-anchor="end" font-weight="700" fill="{text_primary}">{total_repos}</text>

      <text x="36" y="124">CONTRIBUTIONS (365D)</text>
      <line x1="172" y1="122" x2="330" y2="122" stroke="{border}" stroke-dasharray="2,4" stroke-width="0.8"/>
      <text x="375" y="124" text-anchor="end" font-weight="700" fill="{text_primary}">{total_contribs}</text>

      <text x="36" y="144">ACTIVITY PEAK</text>
      <line x1="135" y1="142" x2="310" y2="142" stroke="{border}" stroke-dasharray="2,4" stroke-width="0.8"/>
      <text x="375" y="144" text-anchor="end" font-weight="700" fill="{text_primary}">{max_week} / WEEK</text>
    </g>

    <text x="36" y="171" font-size="9" font-weight="700" fill="{text_dim}">// STACK_GAUGE</text>
    
    <!-- Hairline Segment Bar -->
    <rect x="{lang_bar_x}" y="181" width="{lang_bar_w}" height="4" fill="{subpanel_bg}" stroke="{border}" stroke-width="0.8"/>
"""

    for name, pct, lx, lw in lang_rects:
        svg += f"""    <rect x="{lx}" y="181" width="{lw - 1:.1f}" height="4" fill="{text_primary}" opacity="0.85"/>\n"""

    svg += f"""    <g font-size="8.5" fill="{text_secondary}">
      <text x="46" y="198">RUST 42%</text>
      <text x="145" y="198">TS 28%</text>
      <text x="235" y="198">PYTHON 18%</text>
      <text x="325" y="198">C/ASM 12%</text>
    </g>
  </g>

  <!-- ==================== OSCILLOSCOPE ==================== -->
  <g class="fade-in delay-2">
    <rect x="403" y="60" width="423" height="152" fill="{panel_bg}" stroke="{border}" stroke-width="1" rx="3"/>
    
    <path d="M 403 82 L 826 82" stroke="{border}" stroke-width="1"/>
    <text x="415" y="76" font-size="9.5" font-weight="700" fill="{text_dim}">// ACTIVITY_OSCILLOSCOPE (52 WEEKS)</text>
    <text x="735" y="76" font-size="8.5" fill="{text_dim}">[SEISMOGRAPH]</text>

    <!-- Scope Grid -->
    <rect x="{wave_x - 10}" y="{wave_y_top - 12}" width="{wave_w + 15}" height="{wave_h + 20}" fill="url(#gridPattern_{theme})" opacity="0.6"/>

    <!-- Baseline & Grids -->
    <line x1="{wave_x - 10}" y1="{wave_y_base}" x2="{wave_x + wave_w + 5}" y2="{wave_y_base}" stroke="{border_light}" stroke-width="0.8"/>
    <line x1="{wave_x - 10}" y1="{wave_y_top + wave_h/2}" x2="{wave_x + wave_w + 5}" y2="{wave_y_top + wave_h/2}" stroke="{border}" stroke-dasharray="2,4" stroke-width="0.8"/>
    
    <!-- Area Fill -->
    <path d="{area_d}" fill="url(#areaGrad_{theme})"/>

    <!-- Animated Waveform Stroke -->
    <path class="draw-stroke" d="{path_d}" fill="none" stroke="{accent}" stroke-width="1.3" stroke-linejoin="round" filter="{glow_filter}"/>

    <!-- Peak Diamond Marker -->
    <g transform="translate({peak_x:.1f}, {peak_y:.1f})">
      <path d="M 0 -4 L 4 0 L 0 4 L -4 0 Z" fill="{accent}"/>
      <circle cx="0" cy="0" r="3" fill="none" stroke="{pulse_color}" class="pulse-marker"/>
      <line x1="0" y1="-5" x2="0" y2="-12" stroke="{border_light}" stroke-width="0.8"/>
      <text x="0" y="-15" text-anchor="middle" font-size="8" font-weight="700" fill="{text_primary}">PEAK: {max_week}</text>
    </g>

    <!-- Laser Scanline Tracer -->
    <g transform="translate({wave_x}, {wave_y_top - 8})">
      <line class="scan-line" x1="0" y1="0" x2="0" y2="{wave_h + 14}" stroke="{accent}" stroke-width="0.8" opacity="0.4"/>
    </g>

    <!-- Ticks -->
    <g font-size="8" fill="{text_dim}">
      <text x="{wave_x}" y="200">W01</text>
      <text x="{wave_x + wave_w*0.25:.1f}" y="200" text-anchor="middle">W13</text>
      <text x="{wave_x + wave_w*0.5:.1f}" y="200" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w*0.75:.1f}" y="200" text-anchor="middle">W39</text>
      <text x="{wave_x + wave_w}" y="200" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- ==================== ARTIFACT REGISTER ==================== -->
  <g class="fade-in delay-3">
    <rect x="24" y="224" width="802" height="98" fill="{panel_bg}" stroke="{border}" stroke-width="1" rx="3"/>
    
    <path d="M 24 246 L 826 246" stroke="{border}" stroke-width="1"/>
    <text x="36" y="240" font-size="9.5" font-weight="700" fill="{text_dim}">// REGISTERED_ARTIFACTS (FEATURED PROJECTS)</text>
    <text x="735" y="240" font-size="8.5" fill="{text_dim}">[SYSTEMS &amp; TOOLS]</text>
"""

    card_coords = [
        (36, 252, 175),
        (232, 252, 175),
        (428, 252, 175),
        (624, 252, 185)
    ]

    for idx, repo in enumerate(featured):
        bx, by, bw = card_coords[idx]
        r_name = repo.get("name", "").upper()
        r_desc = repo.get("desc", "")
        r_stack = repo.get("stack", "")
        r_stars = repo.get("stars", 0)

        if len(r_desc) > 34:
            r_desc = r_desc[:31] + "..."

        star_str = f"★ {r_stars}" if r_stars > 0 else ""

        svg += f"""    <g transform="translate({bx}, {by})">
      <text x="0" y="16" font-size="10.5" font-weight="700" fill="{text_primary}">[{idx + 1:02d}] {r_name}</text>
      <text x="0" y="34" font-size="8.5" fill="{text_secondary}">{r_desc}</text>
      <text x="0" y="52" font-size="8" fill="{text_dim}">{r_stack}</text>
      <text x="{bw - 12}" y="52" text-anchor="end" font-size="8.5" font-weight="700" fill="{text_primary}">{star_str}</text>
      {"<line x1='" + str(bw) + "' y1='8' x2='" + str(bw) + "' y2='54' stroke='" + border + "' stroke-width='0.8'/>" if idx < 3 else ""}
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== FOOTER ==================== -->
  <g class="fade-in delay-3" font-size="8.5" fill="{text_dim}">
    <line x1="24" y1="334" x2="826" y2="334" stroke="{border}" stroke-width="0.8"/>
    
    <text x="28" y="348">ENV: {config.get('system_env', 'x86_64 // ARM64 // Linux & macOS')}</text>
    <text x="425" y="348" text-anchor="middle">LOC: {config.get('location', 'Goiás, Brazil')} ({config.get('coordinates', '-16.68° S, -49.26° W')})</text>
    <text x="822" y="348" text-anchor="end">SYS.SYNC: {now_str} <tspan class="cursor" fill="{accent}">█</tspan></text>
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
