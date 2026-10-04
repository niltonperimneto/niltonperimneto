#!/usr/bin/env python3
import json
import os
import re
import subprocess
import urllib.request
import base64
import html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def xesc(val):
    return html.escape(str(val), quote=True)

# Matching isometric cube / hexagon vector paths for C and C++
C_HEXAGON_PATH = "M11.5 2.1a1 1 0 0 1 1 0l7.8 4.5a1 1 0 0 1 .5.87v9.06a1 1 0 0 1-.5.87l-7.8 4.5a1 1 0 0 1-1 0l-7.8-4.5a1 1 0 0 1-.5-.87V7.47a1 1 0 0 1 .5-.87z M12 6.5a5.5 5.5 0 1 0 3.89 9.39l-1.42-1.42A3.5 3.5 0 1 1 12 8.5c.97 0 1.85.39 2.47 1.03l1.42-1.42A5.47 5.47 0 0 0 12 6.5z"
CPP_HEXAGON_PATH = "M11.5 2.1a1 1 0 0 1 1 0l7.8 4.5a1 1 0 0 1 .5.87v9.06a1 1 0 0 1-.5.87l-7.8 4.5a1 1 0 0 1-1 0l-7.8-4.5a1 1 0 0 1-.5-.87V7.47a1 1 0 0 1 .5-.87z M10.5 7a4.5 4.5 0 1 0 3.18 7.68l-1.42-1.42A2.5 2.5 0 1 1 10.5 9c.69 0 1.32.28 1.77.73l1.42-1.42A4.47 4.47 0 0 0 10.5 7z M15 11h1v-1h1v1h1v1h-1v1h-1v-1h-1z M19 11h1v-1h1v1h1v1h-1v1h-1v-1h-1z"

# Monochrome vector logos for the 6 stack languages
LANGUAGE_ICONS = {
    "rust": "M23.8346 11.7033l-1.0073-.6236a13.7268 13.7268 0 00-.0283-.2936l.8656-.8069a.3483.3483 0 00-.1154-.578l-1.1066-.414a8.4958 8.4958 0 00-.087-.2856l.6904-.9587a.3462.3462 0 00-.2257-.5446l-1.1663-.1894a9.3574 9.3574 0 00-.1407-.2622l.49-1.0761a.3437.3437 0 00-.0274-.3361.3486.3486 0 00-.3006-.154l-1.1845.0416a6.7444 6.7444 0 00-.1873-.2268l.2723-1.153a.3472.3472 0 00-.417-.4172l-1.1532.2724a14.0183 14.0183 0 00-.2278-.1873l.0415-1.1845a.3442.3442 0 00-.49-.328l-1.076.491c-.0872-.0476-.1742-.0952-.2623-.1407l-.1903-1.1673A.3483.3483 0 0016.256.955l-.9597.6905a8.4867 8.4867 0 00-.2855-.086l-.414-1.1066a.3483.3483 0 00-.5781-.1154l-.8069.8666a9.2936 9.2936 0 00-.2936-.0284L12.2946.1683a.3462.3462 0 00-.5892 0l-.6236 1.0073a13.7383 13.7383 0 00-.2936.0284L9.9803.3374a.3462.3462 0 00-.578.1154l-.4141 1.1065c-.0962.0274-.1903.0567-.2855.086L7.744.955a.3483.3483 0 00-.5447.2258L7.009 2.348a9.3574 9.3574 0 00-.2622.1407l-1.0762-.491a.3462.3462 0 00-.49.328l.0416 1.1845a7.9826 7.9826 0 00-.2278.1873L3.8413 3.425a.3472.3472 0 00-.4171.4171l.2713 1.1531c-.0628.075-.1255.1509-.1863.2268l-1.1845-.0415a.3462.3462 0 00-.328.49l.491 1.0761a9.167 9.167 0 00-.1407.2622l-1.1662.1894a.3483.3483 0 00-.2258.5446l.6904.9587a13.303 13.303 0 00-.087.2855l-1.1065.414a.3483.3483 0 00-.1155.5781l.8656.807a9.2936 9.2936 0 00-.0283.2935l-1.0073.6236a.3442.3442 0 000 .5892l1.0073.6236c.008.0982.0182.1964.0283.2936l-.8656.8079a.3462.3462 0 00.1155.578l1.1065.4141c.0273.0962.0567.1914.087.2855l-.6904.9587a.3452.3452 0 00.2268.5447l1.1662.1893c.0456.088.0922.1751.1408.2622l-.491 1.0762a.3462.3462 0 00.328.49l1.1834-.0415c.0618.0769.1235.1528.1873.2277l-.2713 1.1541a.3462.3462 0 00.4171.4161l1.153-.2713c.075.0638.151.1255.2279.1863l-.0415 1.1845a.3442.3442 0 00.49.327l1.0761-.49c.087.0486.1741.0951.2622.1407l.1903 1.1662a.3483.3483 0 00.5447.2268l.9587-.6904a9.299 9.299 0 00.2855.087l.414 1.1066a.3452.3452 0 00.5781.1154l.8079-.8656c.0972.0111.1954.0203.2936.0294l.6236 1.0073a.3472.3472 0 00.5892 0l.6236-1.0073c.0982-.0091.1964-.0183.2936-.0294l.8069.8656a.3483.3483 0 00.578-.1154l.4141-1.1066a8.4626 8.4626 0 00.2855-.087l.9587.6904a.3452.3452 0 00.5447-.2268l.1903-1.1662c.088-.0456.1751-.0931.2622-.1407l1.0762.49a.3472.3472 0 00.49-.327l-.0415-1.1845a6.7267 6.7267 0 00.2267-.1863l1.1531.2713a.3472.3472 0 00.4171-.416l-.2713-1.1542c.0628-.0749.1255-.1508.1863-.2278l1.1845.0415a.3442.3442 0 00.328-.49l-.49-1.076c.0475-.0872.0951-.1742.1407-.2623l1.1662-.1893a.3483.3483 0 00.2258-.5447l-.6904-.9587.087-.2855 1.1066-.414a.3462.3462 0 00.1154-.5781l-.8656-.8079c.0101-.0972.0202-.1954.0283-.2936l1.0073-.6236a.3442.3442 0 000-.5892zm-6.7413 8.3551a.7138.7138 0 01.2986-1.396.714.714 0 11-.2997 1.396zm-.3422-2.3142a.649.649 0 00-.7715.5l-.3573 1.6685c-1.1035.501-2.3285.7795-3.6193.7795a8.7368 8.7368 0 01-3.6951-.814l-.3574-1.6684a.648.648 0 00-.7714-.499l-1.473.3158a8.7216 8.7216 0 01-.7613-.898h7.1676c.081 0 .1356-.0141.1356-.088v-2.536c0-.074-.0536-.0881-.1356-.0881h-2.0966v-1.6077h2.2677c.2065 0 1.1065.0587 1.394 1.2088.0901.3533.2875 1.5044.4232 1.8729.1346.413.6833 1.2381 1.2685 1.2381h3.5716a.7492.7492 0 00.1296-.0131 8.7874 8.7874 0 01-.8119.9526zM6.8369 20.024a.714.714 0 11-.2997-1.396.714.714 0 01.2997 1.396zM4.1177 8.9972a.7137.7137 0 11-1.304.5791.7137.7137 0 011.304-.579zm-.8352 1.9813l1.5347-.6824a.65.65 0 00.33-.8585l-.3158-.7147h1.2432v5.6025H3.5669a8.7753 8.7753 0 01-.2834-3.348zm6.7343-.5437V8.7836h2.9601c.153 0 1.0792.1772 1.0792.8697 0 .575-.7107.7815-1.2948.7815zm10.7574 1.4862c0 .2187-.008.4363-.0243.651h-.9c-.09 0-.1265.0586-.1265.1477v.413c0 .973-.5487 1.1846-1.0296 1.2382-.4576.0517-.9648-.1913-1.0275-.4717-.2704-1.5186-.7198-1.8436-1.4305-2.4034.8817-.5599 1.799-1.386 1.799-2.4915 0-1.1936-.819-1.9458-1.3769-2.3153-.7825-.5163-1.6491-.6195-1.883-.6195H5.4682a8.7651 8.7651 0 014.907-2.7699l1.0974 1.151a.648.648 0 00.9182.0213l1.227-1.1743a8.7753 8.7753 0 016.0044 4.2762l-.8403 1.8982a.652.652 0 00.33.8585l1.6178.7188c.0283.2875.0425.577.0425.8717zm-9.3006-9.5993a.7128.7128 0 11.984 1.0316.7137.7137 0 01-.984-1.0316zm8.3389 6.71a.7107.7107 0 01.9395-.3625.7137.7137 0 11-.9405.3635z",
    "typescript": "M1.125 0C.502 0 0 .502 0 1.125v21.75C0 23.498.502 24 1.125 24h21.75c.623 0 1.125-.502 1.125-1.125V1.125C24 .502 23.498 0 22.875 0zm17.363 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.396.441v2.544a4.95 4.95 0 0 0-1.42-.519 7.02 7.02 0 0 0-1.503-.162c-.752 0-1.32.164-1.704.491-.384.327-.576.792-.576 1.396 0 .408.096.75.288 1.026.192.276.474.522.846.738.372.216.852.426 1.44.63.852.288 1.542.618 2.07.99.528.372.924.816 1.188 1.332.264.516.396 1.128.396 1.836 0 .972-.258 1.8-.774 2.484-.516.684-1.236 1.206-2.16 1.566-.924.36-2.016.54-3.276.54-1.008 0-1.932-.108-2.772-.324a9.07 9.07 0 0 1-2.196-.936v-2.7a8.55 8.55 0 0 0 2.448.972 6.8 6.8 0 0 0 2.232.36c.792 0 1.404-.18 1.836-.54.432-.36.648-.852.648-1.476 0-.444-.108-.816-.324-1.116-.216-.3-.528-.564-.936-.792-.408-.228-.948-.456-1.62-.684-.864-.3-1.566-.636-2.106-1.008-.54-.372-.942-.816-1.206-1.332-.264-.516-.396-1.128-.396-1.836 0-.948.252-1.758.756-2.43.504-.672 1.2-1.188 2.088-1.548.888-.36 1.932-.54 3.132-.54zm-9.036.216H12.9v11.784H9.452V9.966z",
    "python": "M11.914 0C5.825 0 6.2 2.656 6.2 2.656l.006 2.75h5.813v.825H3.9S0 5.769 0 11.897c0 6.125 3.4 5.915 3.4 5.915h2.031v-2.868s-.11-3.4 3.344-3.4h5.75s3.235.053 3.235-3.14V2.656S18.232 0 11.914 0zm-3.27 1.872a1.045 1.045 0 1 1 0 2.09 1.045 1.045 0 0 1 0-2.09zm3.442 10.214c6.089 0 5.714-2.656 5.714-2.656l-.006-2.75H11.98v-.825h8.12s3.9.462 3.9-5.666c0-6.128-3.4-5.918-3.4-5.918h-2.03v2.868s.11 3.4-3.345 3.4H9.47s-3.235-.053-3.235 3.14v5.747s-.472 2.66 5.849 2.66zm3.27 10.042a1.045 1.045 0 1 1 0-2.09 1.045 1.045 0 0 1 0 2.09z",
    "c": C_HEXAGON_PATH,
    "cplusplus": CPP_HEXAGON_PATH,
    "assemblyscript": "M12 0L1.5 6v12L12 24l10.5-6V6L12 0zm0 3.27l7.5 4.29v8.88L12 20.73l-7.5-4.29V7.56L12 3.27z M12 6.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11zm0 2a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7z"
}

def fetch_avatar_data_uri(avatar_url):
    if not avatar_url:
        return ""
    try:
        req = urllib.request.Request(avatar_url, headers={"User-Agent": "ProfileGenerator/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            mime = resp.headers.get_content_type()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"Warning: Failed to fetch avatar: {e}")
        return ""

def fetch_github_data(username):
    query = """
    query {
      viewer {
        login
        name
        bio
        location
        avatarUrl
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            forkCount
            primaryLanguage { name color }
          }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
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
    # 1. Try GitHub CLI (gh)
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
        "avatarUrl": "https://avatars.githubusercontent.com/u/118851240?v=4",
        "repositories": { "totalCount": 30, "nodes": [] },
        "contributionsCollection": {
            "contributionCalendar": {
                "totalContributions": 963,
                "weeks": [{"contributionDays": [{"contributionCount": 0}]}] * 52
            }
        }
    }

def generate_svg(theme="dark", data=None, config=None, avatar_data_uri=""):
    if config is None:
        config = {}
    if data is None:
        data = {}

    is_dark = (theme == "dark")
    
    # Strictly monochromatic / neutral grayscale palettes (no green, no red)
    if is_dark:
        bg = "#090a0d"
        card_bg = "#111318"
        inner_bg = "#181b22"
        border = "#272b35"
        border_subtle = "#1c2028"
        text_primary = "#f3f4f6"
        text_secondary = "#9ca3af"
        text_tertiary = "#6b7280"
        accent = "#ffffff"
        accent_stroke = "#e5e7eb"
        accent_fill_opacity = 0.12
    else:
        bg = "#ffffff"
        card_bg = "#f8fafc"
        inner_bg = "#f1f5f9"
        border = "#d1d5db"
        border_subtle = "#e5e7eb"
        text_primary = "#0f172a"
        text_secondary = "#475569"
        text_tertiary = "#94a3b8"
        accent = "#0f172a"
        accent_stroke = "#1e293b"
        accent_fill_opacity = 0.08

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

    # Full-width Activity chart dimensions
    wave_x = 42
    wave_w = 716
    wave_y_base = 340
    wave_y_top = 286
    wave_h = wave_y_base - wave_y_top

    points = []
    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        normalized = count / max_week if max_week > 0 else 0
        py = wave_y_base - (normalized * wave_h)
        points.append((px, py))

    # Path construction with clean angular straight segments (sharp angles only)
    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for px, py in points[1:]:
        path_d += f" L {px:.1f} {py:.1f}"

    area_d = path_d + f" L {points[-1][0]:.1f} {wave_y_base} L {points[0][0]:.1f} {wave_y_base} Z"
    peak_x, peak_y = points[peak_idx]

    # 6 Stack Languages
    stack_langs = config.get("stack_languages", [
        {"name": "Rust", "slug": "rust"},
        {"name": "TypeScript", "slug": "typescript"},
        {"name": "Python", "slug": "python"},
        {"name": "C", "slug": "c"},
        {"name": "C++", "slug": "cplusplus"},
        {"name": "Assembly", "slug": "assemblyscript"}
    ])[:6]

    featured = config.get("featured_repos", [])[:4]
    
    raw_name = config.get("name", "Nilton Perim Neto")
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(config.get("tagline", "Not a Programmer, just a historian."))
    affiliation = xesc(config.get("affiliation", "Universidade Federal de Goiás"))
    location = xesc(config.get("location", "Goiás, Brazil"))
    
    # Employment Status: Unemployed / Seeking Employment
    emp_status_raw = config.get("employment_status", "Seeking Employment · Open to Work")
    employment_status = xesc(emp_status_raw)
    badge_w = max(215, len(emp_status_raw) * 6.5 + 34)
    badge_x = 776 - badge_w - 12

    # Avatar image embedding or monogram fallback
    if avatar_data_uri:
        avatar_svg = f"""      <image href="{avatar_data_uri}" x="36" y="32" width="44" height="44" preserveAspectRatio="xMidYMid slice"/>
      <rect x="36" y="32" width="44" height="44" fill="none" stroke="{border}" stroke-width="1"/>"""
    else:
        avatar_svg = f"""      <rect x="36" y="32" width="44" height="44" fill="{inner_bg}" stroke="{border}" stroke-width="1"/>
      <text x="58" y="59" text-anchor="middle" font-size="14" font-weight="700" fill="{text_primary}">NP</text>"""

    # Single Bento Block at a time (Full width stacked, strictly sharp angles, strictly monochrome)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 604" width="100%" height="100%">
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
        stroke-dasharray: 3000;
        stroke-dashoffset: 3000;
        animation: drawPath 1.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}

      .fade-in {{
        opacity: 0;
        animation: fadeIn 0.5s ease forwards;
      }}

      .delay-1 {{ animation-delay: 0.08s; }}
      .delay-2 {{ animation-delay: 0.16s; }}
      .delay-3 {{ animation-delay: 0.24s; }}
      .delay-4 {{ animation-delay: 0.32s; }}

      .pulse-marker {{
        animation: pulse 2.4s infinite ease-in-out;
        transform-origin: center;
        transform-box: fill-box;
      }}

      @keyframes drawPath {{
        to {{ stroke-dashoffset: 0; }}
      }}

      @keyframes fadeIn {{
        to {{ opacity: 1; }}
      }}

      @keyframes pulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(2.2); opacity: 0.25; }}
      }}
    </style>

    <linearGradient id="curveGrad_{theme}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="{accent_fill_opacity}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <!-- Canvas Background -->
  <rect width="800" height="604" fill="{bg}"/>
  <rect x="0.5" y="0.5" width="799" height="603" fill="none" stroke="{border}" stroke-width="1"/>

  <!-- ==================== BENTO BLOCK 1: PROFILE HEADER ==================== -->
  <g class="fade-in">
    <rect x="24" y="20" width="752" height="68" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <!-- Profile Picture (GitHub Avatar) -->
{avatar_svg}

    <!-- Name & Tagline -->
    <text x="94" y="49" font-size="16" font-weight="600" fill="{text_primary}" letter-spacing="-0.01em">{display_name}</text>
    <text x="94" y="67" font-size="11" font-weight="400" fill="{text_secondary}">{tagline}</text>

    <!-- Employment Status Badge -->
    <rect x="{badge_x:.1f}" y="40" width="{badge_w:.1f}" height="28" fill="{inner_bg}" stroke="{border}" stroke-width="1"/>
    <rect x="{badge_x + 10:.1f}" y="50" width="7" height="7" fill="{text_primary}"/>
    <text x="{badge_x + 24:.1f}" y="58" font-size="10.5" font-weight="600" fill="{text_primary}">{employment_status}</text>
  </g>

  <!-- ==================== BENTO BLOCK 2: MY STACK ==================== -->
  <g class="fade-in delay-1">
    <rect x="24" y="98" width="752" height="58" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    <text x="40" y="118" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// MY STACK</text>
"""

    tile_w = 112
    tile_h = 26
    tile_start_x = 40
    tile_gap = 9

    for idx, lang in enumerate(stack_langs):
        tx = tile_start_x + idx * (tile_w + tile_gap)
        ty = 122
        lname = xesc(lang.get("name", ""))
        lslug = lang.get("slug", "").lower()
        path_data = LANGUAGE_ICONS.get(lslug, LANGUAGE_ICONS.get("rust"))

        svg += f"""    <!-- {lname} Tile -->
    <g transform="translate({tx}, {ty})">
      <rect width="{tile_w}" height="{tile_h}" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <g transform="translate(8, 4.5) scale(0.65)">
        <path d="{path_data}" fill="{text_secondary}"/>
      </g>
      <text x="30" y="17" font-size="10.5" font-weight="600" fill="{text_primary}">{lname}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== BENTO BLOCK 3: ENGINEERING METRICS ==================== -->
  <g class="fade-in delay-2">
    <rect x="24" y="166" width="752" height="78" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="186" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// ENGINEERING METRICS</text>
    <text x="760" y="186" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">Linux &amp; macOS // x86_64 &amp; ARM64</text>
    <line x1="40" y1="194" x2="760" y2="194" stroke="{border_subtle}" stroke-width="1"/>

    <!-- Stat 1: Repositories -->
    <text x="40" y="210" font-size="8.5" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">REPOSITORIES</text>
    <text x="40" y="232" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{total_repos}</text>

    <!-- Stat 2: Contributions -->
    <text x="280" y="210" font-size="8.5" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">YEARLY CONTRIBUTIONS</text>
    <text x="280" y="232" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{total_contribs}</text>

    <!-- Stat 3: Weekly Peak -->
    <text x="530" y="210" font-size="8.5" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">WEEKLY ACTIVITY PEAK</text>
    <text x="530" y="232" font-size="20" font-weight="600" fill="{text_primary}" class="tabular">{max_week} <tspan font-size="11" font-weight="400" fill="{text_secondary}">commits / wk</tspan></text>
  </g>

  <!-- ==================== BENTO BLOCK 4: ACTIVITY RHYTHM ==================== -->
  <g class="fade-in delay-3">
    <rect x="24" y="254" width="752" height="116" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="274" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// ACTIVITY RHYTHM</text>
    <text x="760" y="274" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">52-Week Oscilloscope</text>

    <!-- Guide Lines -->
    <line x1="42" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="{border_subtle}" stroke-width="1"/>
    <line x1="42" y1="{wave_y_top + wave_h/2:.1f}" x2="{wave_x + wave_w}" y2="{wave_y_top + wave_h/2:.1f}" stroke="{border_subtle}" stroke-dasharray="3,4" stroke-width="0.75"/>

    <!-- Gradient Fill -->
    <path d="{area_d}" fill="url(#curveGrad_{theme})"/>

    <!-- Sharp Angular Trajectory Stroke -->
    <path class="draw-stroke" d="{path_d}" fill="none" stroke="{accent_stroke}" stroke-width="1.6" stroke-linejoin="miter"/>

    <!-- Peak Indicator (Sharp Square) -->
    <g transform="translate({peak_x:.1f}, {peak_y:.1f})">
      <rect x="-3" y="-3" width="6" height="6" fill="{accent_stroke}"/>
      <rect x="-3" y="-3" width="6" height="6" fill="none" stroke="{accent_stroke}" stroke-width="0.8" class="pulse-marker"/>
      <text x="0" y="-10" text-anchor="middle" font-size="9.5" font-weight="600" fill="{text_primary}">Peak: {max_week}</text>
    </g>

    <!-- Timeline Labels -->
    <g font-size="9" font-weight="500" fill="{text_tertiary}">
      <text x="{wave_x}" y="356">W01</text>
      <text x="{wave_x + wave_w*0.25:.1f}" y="356" text-anchor="middle">W13</text>
      <text x="{wave_x + wave_w*0.5:.1f}" y="356" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w*0.75:.1f}" y="356" text-anchor="middle">W39</text>
      <text x="{wave_x + wave_w}" y="356" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- ==================== BENTO BLOCK 5: FEATURED PROJECTS ==================== -->
  <g class="fade-in delay-4">
    <rect x="24" y="380" width="752" height="182" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="400" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// FEATURED PROJECTS</text>
    <text x="760" y="400" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">Open Source Systems &amp; Tools</text>
    <line x1="40" y1="408" x2="760" y2="408" stroke="{border_subtle}" stroke-width="1"/>
"""

    row_ys = [416, 452, 488, 524]

    for idx, repo in enumerate(featured):
        if idx >= len(row_ys):
            break
        ry = row_ys[idx]
        r_name = xesc(repo.get("name", ""))
        r_desc = xesc(repo.get("desc", ""))
        r_stack = xesc(repo.get("stack", ""))
        r_stars = repo.get("stars", 0)

        star_str = f"★ {r_stars}" if r_stars > 0 else ""
        tag_w = max(38, len(r_stack) * 5.8 + 12)

        # Subtle row divider
        div_line = f"""<line x1="40" y1="{ry + 30}" x2="760" y2="{ry + 30}" stroke="{border_subtle}" stroke-width="0.75"/>""" if idx < 3 else ""

        svg += f"""    <!-- Project Row {idx + 1} -->
    <g>
      <text x="40" y="{ry + 19}" font-size="12" font-weight="600" fill="{text_primary}">[{idx + 1:02d}] {r_name}</text>
      <text x="180" y="{ry + 19}" font-size="10.5" font-weight="400" fill="{text_secondary}">{r_desc}</text>
      
      <!-- Tech Badge -->
      <rect x="{670 - tag_w}" y="{ry + 6}" width="{tag_w}" height="17" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <text x="{670 - tag_w/2}" y="{ry + 18}" text-anchor="middle" font-size="8.5" font-weight="500" fill="{text_tertiary}">{r_stack}</text>
      
      <!-- Stars -->
      <text x="756" y="{ry + 19}" text-anchor="end" font-size="9.5" font-weight="600" fill="{text_primary}">{star_str}</text>
      {div_line}
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== FOOTER ==================== -->
  <g class="fade-in delay-4">
    <line x1="24" y1="574" x2="776" y2="574" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="590" font-size="9.5" font-weight="400" fill="{text_tertiary}">{affiliation} · {location} · {employment_status}</text>
    <text x="772" y="590" text-anchor="end" font-size="9.5" font-weight="400" fill="{text_tertiary}">Updated via GitHub Actions · SVG Telemetry</text>
  </g>
</svg>
"""
    return svg

def main():
    config = load_config()
    username = config.get("username", "niltonperimneto")
    
    print(f"Fetching GitHub data for {username}...")
    data = fetch_github_data(username)
    
    avatar_url = data.get("avatarUrl", "https://avatars.githubusercontent.com/u/118851240?v=4")
    print(f"Fetching avatar from {avatar_url}...")
    avatar_data_uri = fetch_avatar_data_uri(avatar_url)
    
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    dark_svg = generate_svg(theme="dark", data=data, config=config, avatar_data_uri=avatar_data_uri)
    dark_path = os.path.join(ASSETS_DIR, "zed-card-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Generated dark SVG: {dark_path}")
    
    light_svg = generate_svg(theme="light", data=data, config=config, avatar_data_uri=avatar_data_uri)
    light_path = os.path.join(ASSETS_DIR, "zed-card-light.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Generated light SVG: {light_path}")
    
    print("SVG Generation completed successfully!")

if __name__ == "__main__":
    main()
