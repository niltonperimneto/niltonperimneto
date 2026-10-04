#!/usr/bin/env python3
import json
import os
import re
import subprocess
import urllib.request
import base64
import html
import math
from pathlib import Path

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

# Monochrome vector logos for stack languages (Official Simple Icons paths)
LANGUAGE_ICONS = {
    "rust": "M23.8346 11.7033l-1.0073-.6236a13.7268 13.7268 0 00-.0283-.2936l.8656-.8069a.3483.3483 0 00-.1154-.578l-1.1066-.414a8.4958 8.4958 0 00-.087-.2856l.6904-.9587a.3462.3462 0 00-.2257-.5446l-1.1663-.1894a9.3574 9.3574 0 00-.1407-.2622l.49-1.0761a.3437.3437 0 00-.0274-.3361.3486.3486 0 00-.3006-.154l-1.1845.0416a6.7444 6.7444 0 00-.1873-.2268l.2723-1.153a.3472.3472 0 00-.417-.4172l-1.1532.2724a14.0183 14.0183 0 00-.2278-.1873l.0415-1.1845a.3442.3442 0 00-.49-.328l-1.076.491c-.0872-.0476-.1742-.0952-.2623-.1407l-.1903-1.1673A.3483.3483 0 0016.256.955l-.9597.6905a8.4867 8.4867 0 00-.2855-.086l-.414-1.1066a.3483.3483 0 00-.5781-.1154l-.8069.8666a9.2936 9.2936 0 00-.2936-.0284L12.2946.1683a.3462.3462 0 00-.5892 0l-.6236 1.0073a13.7383 13.7383 0 00-.2936.0284L9.9803.3374a.3462.3462 0 00-.578.1154l-.4141 1.1065c-.0962.0274-.1903.0567-.2855.086L7.744.955a.3483.3483 0 00-.5447.2258L7.009 2.348a9.3574 9.3574 0 00-.2622.1407l-1.0762-.491a.3462.3462 0 00-.49.328l.0416 1.1845a7.9826 7.9826 0 00-.2278.1873L3.8413 3.425a.3472.3472 0 00-.4171.4171l.2713 1.1531c-.0628.075-.1255.1509-.1863.2268l-1.1845-.0415a.3462.3462 0 00-.328.49l.491 1.0761a9.167 9.167 0 00-.1407.2622l-1.1662.1894a.3483.3483 0 00-.2258.5446l.6904.9587a13.303 13.303 0 00-.087.2855l-1.1065.414a.3483.3483 0 00-.1155.5781l.8656.807a9.2936 9.2936 0 00-.0283.2935l-1.0073.6236a.3442.3442 0 000 .5892l1.0073.6236c.008.0982.0182.1964.0283.2936l-.8656.8079a.3462.3462 0 00.1155.578l1.1065.4141c.0273.0962.0567.1914.087.2855l-.6904.9587a.3452.3452 0 00.2268.5447l1.1662.1893c.0456.088.0922.1751.1408.2622l-.491 1.0762a.3462.3462 0 00.328.49l1.1834-.0415c.0618.0769.1235.1528.1873.2277l-.2713 1.1541a.3462.3462 0 00.4171.4161l1.153-.2713c.075.0638.151.1255.2279.1863l-.0415 1.1845a.3442.3442 0 00.49.327l1.0761-.49c.087.0486.1741.0951.2622.1407l.1903 1.1662a.3483.3483 0 00.5447.2268l.9587-.6904a9.299 9.299 0 00.2855.087l.414 1.1066a.3452.3452 0 00.5781.1154l.8079-.8656c.0972.0111.1954.0203.2936.0294l.6236 1.0073a.3472.3472 0 00.5892 0l.6236-1.0073c.0982-.0091.1964-.0183.2936-.0294l.8069.8656a.3483.3483 0 00.578-.1154l.4141-1.1066a8.4626 8.4626 0 00.2855-.087l.9587.6904a.3452.3452 0 00.5447-.2268l.1903-1.1662c.088-.0456.1751-.0931.2622-.1407l1.0762.49a.3472.3472 0 00.49-.327l-.0415-1.1845a6.7267 6.7267 0 00.2267-.1863l1.1531.2713a.3472.3472 0 00.4171-.416l-.2713-1.1542c.0628-.0749.1255-.1508.1863-.2278l1.1845.0415a.3442.3442 0 00.328-.49l-.49-1.076c.0475-.0872.0951-.1742.1407-.2623l1.1662-.1893a.3483.3483 0 00.2258-.5447l-.6904-.9587.087-.2855 1.1066-.414a.3462.3462 0 00.1154-.5781l-.8656-.8079c.0101-.0972.0202-.1954.0283-.2936l1.0073-.6236a.3442.3442 0 000-.5892zm-6.7413 8.3551a.7138.7138 0 01.2986-1.396.714.714 0 11-.2997 1.396zm-.3422-2.3142a.649.649 0 00-.7715.5l-.3573 1.6685c-1.1035.501-2.3285.7795-3.6193.7795a8.7368 8.7368 0 01-3.6951-.814l-.3574-1.6684a.648.648 0 00-.7714-.499l-1.473.3158a8.7216 8.7216 0 01-.7613-.898h7.1676c.081 0 .1356-.0141.1356-.088v-2.536c0-.074-.0536-.0881-.1356-.0881h-2.0966v-1.6077h2.2677c.2065 0 1.1065.0587 1.394 1.2088.0901.3533.2875 1.5044.4232 1.8729.1346.413.6833 1.2381 1.2685 1.2381h3.5716a.7492.7492 0 00.1296-.0131 8.7874 8.7874 0 01-.8119.9526zM6.8369 20.024a.714.714 0 11-.2997-1.396.714.714 0 01.2997 1.396zM4.1177 8.9972a.7137.7137 0 11-1.304.5791.7137.7137 0 011.304-.579zm-.8352 1.9813l1.5347-.6824a.65.65 0 00.33-.8585l-.3158-.7147h1.2432v5.6025H3.5669a8.7753 8.7753 0 01-.2834-3.348zm6.7343-.5437V8.7836h2.9601c.153 0 1.0792.1772 1.0792.8697 0 .575-.7107.7815-1.2948.7815zm10.7574 1.4862c0 .2187-.008.4363-.0243.651h-.9c-.09 0-.1265.0586-.1265.1477v.413c0 .973-.5487 1.1846-1.0296 1.2382-.4576.0517-.9648-.1913-1.0275-.4717-.2704-1.5186-.7198-1.8436-1.4305-2.4034.8817-.5599 1.799-1.386 1.799-2.4915 0-1.1936-.819-1.9458-1.3769-2.3153-.7825-.5163-1.6491-.6195-1.883-.6195H5.4682a8.7651 8.7651 0 014.907-2.7699l1.0974 1.151a.648.648 0 00.9182.0213l1.227-1.1743a8.7753 8.7753 0 016.0044 4.2762l-.8403 1.8982a.652.652 0 00.33.8585l1.6178.7188c.0283.2875.0425.577.0425.8717zm-9.3006-9.5993a.7128.7128 0 11.984 1.0316.7137.7137 0 01-.984-1.0316zm8.3389 6.71a.7107.7107 0 01.9395-.3625.7137.7137 0 11-.9405.3635z",
    "typescript": "M0 0h24v24H0V0zm18.488 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.306.34v2.458a3.95 3.95 0 0 0-.643-.361 5.093 5.093 0 0 0-.717-.26 5.453 5.453 0 0 0-1.426-.2c-.3 0-.573.028-.819.086a2.1 2.1 0 0 0-.623.242c-.17.104-.3.229-.393.374a.888.888 0 0 0-.14.49c0 .196.053.373.156.529.104.156.252.304.443.444s.423.276.696.41c.273.135.582.274.926.416.47.197.892.407 1.266.628.374.222.695.473.963.753.268.279.472.598.614.957.142.359.214.776.214 1.253 0 .657-.125 1.21-.373 1.656a3.033 3.033 0 0 1-1.012 1.085 4.38 4.38 0 0 1-1.487.596c-.566.12-1.163.18-1.79.18a9.916 9.916 0 0 1-1.84-.164 5.544 5.544 0 0 1-1.512-.493v-2.63a5.033 5.033 0 0 0 3.237 1.2c.333 0 .624-.03.872-.09.249-.06.456-.144.623-.25.166-.108.29-.234.373-.38a1.023 1.023 0 0 0-.074-1.089 2.12 2.12 0 0 0-.537-.5 5.597 5.597 0 0 0-.807-.444 27.72 27.72 0 0 0-1.007-.436c-.918-.383-1.602-.852-2.053-1.405-.45-.553-.676-1.222-.676-2.005 0-.614.123-1.141.369-1.582.246-.441.58-.804 1.004-1.089a4.494 4.494 0 0 1 1.47-.629 7.536 7.536 0 0 1 1.77-.201zM3.375 9.938h9.563v2.166H9.506v9.646H6.789v-9.646H3.375z",
    "python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z",
    "c": C_HEXAGON_PATH,
    "cplusplus": CPP_HEXAGON_PATH,
    "assemblyscript": "M0 0v24h24V0h-9.225c0 1.406-1.04 2.813-2.756 2.813A2.766 2.766 0 019.234 0zm18.204 10.947c.707 0 1.314.137 1.82.412.517.264.96.717 1.33 1.361l-1.726 1.108c-.19-.338-.395-.58-.617-.728a1.422 1.422 0 00-.807-.222c-.327 0-.586.09-.776.27a.896.896 0 00-.285.68c0 .337.106.596.317.775.222.17.57.36 1.045.57l.554.238c.474.2.891.411 1.25.633.37.21.675.453.918.728.253.264.443.57.57.918.137.337.206.738.206 1.203a3 3 0 01-.285 1.33c-.18.38-.433.701-.76.965a3.419 3.419 0 01-1.171.601c-.443.127-.929.19-1.456.19a5.31 5.31 0 01-1.41-.174 4.624 4.624 0 01-1.139-.475 3.922 3.922 0 01-.886-.712 4.48 4.48 0 01-.602-.902L16.1 18.67c.242.39.527.712.855.966.337.253.78.38 1.33.38.463 0 .827-.1 1.091-.301.275-.211.412-.475.412-.792 0-.38-.143-.664-.428-.854-.285-.19-.68-.396-1.187-.618l-.554-.237a8.12 8.12 0 01-1.092-.554 3.64 3.64 0 01-.839-.696 2.887 2.887 0 01-.538-.903 3.375 3.375 0 01-.19-1.187c0-.411.074-.796.222-1.155a2.91 2.91 0 01.649-.934c.285-.264.628-.47 1.029-.617.4-.148.849-.222 1.345-.222zm-8.796.032h.19l4.922 10.858h-2.327l-.506-1.219H7.318l-.506 1.219H4.675zm.063 3.988a22.21 22.21 0 01-.206.697l-.205.649a6.979 6.979 0 01-.222.585l-.776 1.868h2.834l-.776-1.868a15.492 15.492 0 01-.237-.633 23.741 23.741 0 01-.412-1.298z",
    "assembly": "M0 0v24h24V0h-9.225c0 1.406-1.04 2.813-2.756 2.813A2.766 2.766 0 019.234 0zm18.204 10.947c.707 0 1.314.137 1.82.412.517.264.96.717 1.33 1.361l-1.726 1.108c-.19-.338-.395-.58-.617-.728a1.422 1.422 0 00-.807-.222c-.327 0-.586.09-.776.27a.896.896 0 00-.285.68c0 .337.106.596.317.775.222.17.57.36 1.045.57l.554.238c.474.2.891.411 1.25.633.37.21.675.453.918.728.253.264.443.57.57.918.137.337.206.738.206 1.203a3 3 0 01-.285 1.33c-.18.38-.433.701-.76.965a3.419 3.419 0 01-1.171.601c-.443.127-.929.19-1.456.19a5.31 5.31 0 01-1.41-.174 4.624 4.624 0 01-1.139-.475 3.922 3.922 0 01-.886-.712 4.48 4.48 0 01-.602-.902L16.1 18.67c.242.39.527.712.855.966.337.253.78.38 1.33.38.463 0 .827-.1 1.091-.301.275-.211.412-.475.412-.792 0-.38-.143-.664-.428-.854-.285-.19-.68-.396-1.187-.618l-.554-.237a8.12 8.12 0 01-1.092-.554 3.64 3.64 0 01-.839-.696 2.887 2.887 0 01-.538-.903 3.375 3.375 0 01-.19-1.187c0-.411.074-.796.222-1.155a2.91 2.91 0 01.649-.934c.285-.264.628-.47 1.029-.617.4-.148.849-.222 1.345-.222zm-8.796.032h.19l4.922 10.858h-2.327l-.506-1.219H7.318l-.506 1.219H4.675zm.063 3.988a22.21 22.21 0 01-.206.697l-.205.649a6.979 6.979 0 01-.222.585l-.776 1.868h2.834l-.776-1.868a15.492 15.492 0 01-.237-.633 23.741 23.741 0 01-.412-1.298z",
    "webassembly": "M14.745 0c0 .042 0 .085 0 .129 0 1.52-1.232 2.752-2.752 2.752-1.52 0-2.752-1.232-2.752-2.752 0-.045 0-.087 0-.129H0v24h24V0H14.745zM11.454 21.431l-1.169-5.783h-.02l-1.264 5.783H7.39l-1.824-8.497h1.59l1.088 5.783h.02l1.311-5.783h1.487l1.177 5.854h.02l1.242-5.854h1.561l-2.027 8.497H11.454zM20.209 21.431l-.542-1.891h-2.861l-0.417 1.891h-1.59l2.056-8.497h2.509l2.5 8.497H20.209zM17.812 15.028l-.694 3.118h2.159l-.796-3.118H17.812z"
}

def generate_pie_chart_svg(cx, cy, r, slices, is_dark, card_bg, border):
    """
    Renders a monochromatic precision pie chart ('pizza graphic') with slice dividers.
    """
    total = sum(s.get("pct", 0) for s in slices)
    if total <= 0:
        total = 100

    # High-contrast monochromatic grayscale palette
    if is_dark:
        colors = ["#f3f4f6", "#9ca3af", "#4b5563", "#374151"]
    else:
        colors = ["#1e293b", "#64748b", "#cbd5e1", "#e2e8f0"]

    start_angle = -math.pi / 2  # 12 o'clock
    svg_paths = []
    
    current_angle = start_angle
    for idx, s in enumerate(slices):
        pct = s.get("pct", 0)
        if pct <= 0:
            continue
        slice_angle = (pct / total) * 2 * math.pi
        end_angle = current_angle + slice_angle
        
        fill_color = colors[idx % len(colors)]
        
        # When slice is virtually full circle (>= 99.9%)
        if pct >= total:
            svg_paths.append(
                f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill_color}" stroke="{card_bg}" stroke-width="1.5"/>'
            )
            break
            
        x1 = cx + r * math.cos(current_angle)
        y1 = cy + r * math.sin(current_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy + r * math.sin(end_angle)
        
        large_arc = 1 if slice_angle > math.pi else 0
        
        path = (
            f'    <path d="M {cx:.2f} {cy:.2f} '
            f'L {x1:.2f} {y1:.2f} '
            f'A {r:.2f} {r:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z" '
            f'fill="{fill_color}" stroke="{card_bg}" stroke-width="1.5"/>'
        )
        svg_paths.append(path)
        current_angle = end_angle

    # Outer border circle & center hub pin
    border_circle = f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{border}" stroke-width="0.75"/>'
    center_pin = f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.2" fill="{card_bg}" stroke="{border}" stroke-width="0.75"/>'
    
    return "\n".join(svg_paths) + "\n" + border_circle + "\n" + center_pin

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

def generate_svg_wide(theme="dark", data=None, config=None, avatar_data_uri=""):
    if config is None:
        config = {}
    if data is None:
        data = {}

    is_dark = (theme == "dark")
    
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

    cal = data.get("contributionsCollection", {}).get("contributionCalendar", {})
    weeks = cal.get("weeks", [])
    
    weekly_counts = []
    for w in weeks:
        weekly_counts.append(sum(d.get("contributionCount", 0) for d in w.get("contributionDays", [])))
    
    if len(weekly_counts) > 52:
        weekly_counts = weekly_counts[-52:]
    elif len(weekly_counts) < 52:
        weekly_counts = [0] * (52 - len(weekly_counts)) + weekly_counts

    raw_max = max(weekly_counts) if weekly_counts else 0
    peak_idx = weekly_counts.index(raw_max) if (weekly_counts and raw_max in weekly_counts) else 0
    max_week = raw_max if raw_max > 0 else 1

    # Wide Activity chart dimensions
    wave_x = 42
    wave_w = 716
    wave_y_base = 350
    wave_y_top = 296
    wave_h = wave_y_base - wave_y_top

    points = []
    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        normalized = count / max_week if max_week > 0 else 0
        py = wave_y_base - (normalized * wave_h)
        points.append((px, py))

    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for px, py in points[1:]:
        path_d += f" L {px:.1f} {py:.1f}"

    area_d = path_d + f" L {points[-1][0]:.1f} {wave_y_base} L {points[0][0]:.1f} {wave_y_base} Z"
    peak_x, peak_y = points[peak_idx]

    stack_langs = config.get("stack_languages", [
        {"name": "Rust", "slug": "rust"},
        {"name": "TypeScript", "slug": "typescript"},
        {"name": "Python", "slug": "python"},
        {"name": "C", "slug": "c"},
        {"name": "C++", "slug": "cplusplus"},
        {"name": "Assembly", "slug": "assemblyscript"}
    ])[:6]

    # Target Platforms
    platforms = config.get("platforms", [
        {"name": "Linux", "badge": "Kernel · Drivers"},
        {"name": "macOS", "badge": "Darwin · Systems"},
        {"name": "Web", "badge": "Wasm · Modern UI"}
    ])[:3]

    # Project Scope Breakdown for Pie Chart
    project_scopes = config.get("project_scopes", [
        {"name": "Drivers & Low-Level", "pct": 45},
        {"name": "User Interface / GUI", "pct": 35},
        {"name": "Systems & Daemons", "pct": 20}
    ])[:3]

    featured = config.get("featured_repos", [])[:4]
    
    raw_name = config.get("name", "Nilton Perim Neto")
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(config.get("tagline", "Not a Programmer, just a historian."))
    affiliation = xesc(config.get("affiliation", "Universidade Federal de Goiás"))
    location = xesc(config.get("location", "Goiás, Brazil"))
    
    emp_status_raw = config.get("employment_status", "Seeking Employment · Open to Work")
    employment_status = xesc(emp_status_raw)
    badge_w = max(220, len(emp_status_raw) * 6.5 + 32)
    badge_x = 776 - badge_w - 12

    if avatar_data_uri:
        avatar_svg = f"""      <image href="{avatar_data_uri}" x="36" y="28" width="48" height="48" preserveAspectRatio="xMidYMid slice"/>
      <rect x="36" y="28" width="48" height="48" fill="none" stroke="{border}" stroke-width="1"/>"""
    else:
        avatar_svg = f"""      <rect x="36" y="28" width="48" height="48" fill="{inner_bg}" stroke="{border}" stroke-width="1"/>
      <text x="60" y="57" text-anchor="middle" font-size="14" font-weight="700" fill="{text_primary}">NP</text>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">
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
        animation: pulseSquare 2.5s infinite;
        transform-origin: center;
      }}

      @keyframes drawPath {{
        to {{ stroke-dashoffset: 0; }}
      }}

      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(3px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      @keyframes pulseSquare {{
        0%, 100% {{ opacity: 0.2; transform: scale(1); }}
        50% {{ opacity: 0.9; transform: scale(1.6); }}
      }}
    </style>

    <linearGradient id="curveGrad_wide_{theme}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="{accent_fill_opacity * 1.5:.2f}"/>
      <stop offset="70%" stop-color="{accent}" stop-opacity="{accent_fill_opacity * 0.5:.2f}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
    </linearGradient>

    <pattern id="grid_wide_{theme}" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="{border_subtle}" stroke-width="0.5" opacity="0.35"/>
    </pattern>
  </defs>

  <rect width="800" height="600" fill="{bg}"/>
  <rect width="800" height="600" fill="url(#grid_wide_{theme})"/>

  <!-- ==================== BENTO BLOCK 1: PROFILE HEADER ==================== -->
  <g class="fade-in">
    <rect x="24" y="16" width="752" height="72" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
{avatar_svg}

    <text x="98" y="47" font-size="16" font-weight="700" fill="{text_primary}" letter-spacing="-0.01em">{display_name}</text>
    <text x="98" y="65" font-size="11" font-weight="400" fill="{text_secondary}">{tagline}</text>

    <!-- Employment Status Badge -->
    <rect x="{badge_x:.1f}" y="38" width="{badge_w:.1f}" height="28" fill="{inner_bg}" stroke="{border}" stroke-width="1"/>
    <rect x="{badge_x + 10:.1f}" y="48" width="8" height="8" fill="{text_primary}"/>
    <text x="{badge_x + 24:.1f}" y="56" font-size="10.5" font-weight="600" fill="{text_primary}">{employment_status}</text>
  </g>

  <!-- ==================== BENTO BLOCK 2: MY STACK ==================== -->
  <g class="fade-in delay-1">
    <rect x="24" y="98" width="752" height="58" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    <text x="40" y="118" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// MY STACK</text>
    <text x="760" y="118" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">Primary Languages</text>
"""

    tile_w = 112
    tile_h = 26
    start_x = 40
    gap = 9

    for idx, lang in enumerate(stack_langs):
        tx = start_x + idx * (tile_w + gap)
        ty = 122
        lname = xesc(lang.get("name", ""))
        lslug = lang.get("slug", "").lower()
        path_data = LANGUAGE_ICONS.get(lslug, LANGUAGE_ICONS.get("rust"))

        svg += f"""    <!-- {lname} Tile -->
    <g transform="translate({tx}, {ty})">
      <rect width="{tile_w}" height="{tile_h}" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <g transform="translate(8, 4.5) scale(0.65)">
        <path fill-rule="evenodd" clip-rule="evenodd" d="{path_data}" fill="{text_secondary}"/>
      </g>
      <text x="30" y="17" font-size="10.5" font-weight="600" fill="{text_primary}">{lname}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== BENTO BLOCK 3: PLATFORMS & PROJECT SCOPE ==================== -->
  <g class="fade-in delay-2">
    <rect x="24" y="166" width="752" height="88" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="186" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// PLATFORMS &amp; PROJECT SCOPE</text>
    <text x="760" y="186" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">Linux · macOS · Web // Drivers · UI · Systems</text>
    <line x1="40" y1="194" x2="760" y2="194" stroke="{border_subtle}" stroke-width="1"/>

    <!-- Column 1: Target Platforms -->
    <text x="40" y="209" font-size="8.5" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">TARGET PLATFORMS</text>
"""

    chip_w = 104
    chip_h = 30
    chip_gap = 8
    chip_start_x = 40
    chip_y = 215

    for idx, p in enumerate(platforms):
        px = chip_start_x + idx * (chip_w + chip_gap)
        p_name = xesc(p.get("name", "").upper())
        p_badge = xesc(p.get("badge", ""))
        svg += f"""    <!-- Platform Chip: {p_name} -->
    <g transform="translate({px}, {chip_y})">
      <rect width="{chip_w}" height="{chip_h}" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <rect x="8" y="6" width="4" height="4" fill="{accent}"/>
      <text x="17" y="11" font-size="9.5" font-weight="700" letter-spacing="0.04em" fill="{text_primary}">[ {p_name} ]</text>
      <text x="8" y="23" font-size="8" font-weight="500" fill="{text_tertiary}">{p_badge}</text>
    </g>
"""

    pie_svg = generate_pie_chart_svg(432, 232, 20, project_scopes, is_dark, card_bg, border)

    svg += f"""    <!-- Column Divider -->
    <line x1="385" y1="202" x2="385" y2="246" stroke="{border_subtle}" stroke-width="1"/>

    <!-- Column 2: Preferred Project Scope & Pie Chart -->
    <text x="405" y="209" font-size="8.5" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">PREFERRED PROJECT SCOPE</text>

    <!-- Pizza Graphics (Pie Chart) -->
    <g>
{pie_svg}
    </g>
"""

    legend_colors = ["#f3f4f6", "#9ca3af", "#4b5563"] if is_dark else ["#1e293b", "#64748b", "#cbd5e1"]
    legend_text_colors = [text_primary, text_secondary, text_tertiary]
    legend_ys = [222, 234, 246]

    for idx, s in enumerate(project_scopes):
        if idx >= len(legend_ys):
            break
        ly = legend_ys[idx]
        s_name = xesc(s.get("name", ""))
        s_pct = s.get("pct", 0)
        swatch_c = legend_colors[idx % len(legend_colors)]
        t_color = legend_text_colors[idx % len(legend_text_colors)]

        leader_start = max(615, int(482 + len(s_name) * 6.2 + 8))
        leader_line = f'<line x1="{leader_start}" y1="{ly - 3}" x2="732" y2="{ly - 3}" stroke="{border_subtle}" stroke-dasharray="2,3" stroke-width="0.75"/>' if leader_start < 730 else ''

        svg += f"""    <!-- Scope Item: {s_name} -->
    <g>
      <rect x="468" y="{ly - 7}" width="7" height="7" fill="{swatch_c}"/>
      <text x="482" y="{ly}" font-size="9" font-weight="600" fill="{t_color}">{s_name}</text>
      {leader_line}
      <text x="760" y="{ly}" text-anchor="end" font-size="9.5" font-weight="700" fill="{t_color}" class="tabular">{s_pct}%</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== BENTO BLOCK 4: ACTIVITY RHYTHM ==================== -->
  <g class="fade-in delay-3">
    <rect x="24" y="264" width="752" height="116" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="284" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// ACTIVITY RHYTHM</text>
    <text x="760" y="284" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">52-Week Oscilloscope</text>

    <!-- Guide Lines -->
    <line x1="42" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="{border_subtle}" stroke-width="1"/>
    <line x1="42" y1="{wave_y_top + wave_h/2:.1f}" x2="{wave_x + wave_w}" y2="{wave_y_top + wave_h/2:.1f}" stroke="{border_subtle}" stroke-dasharray="3,4" stroke-width="0.75"/>

    <!-- Gradient Fill -->
    <path d="{area_d}" fill="url(#curveGrad_wide_{theme})"/>

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
      <text x="{wave_x}" y="366">W01</text>
      <text x="{wave_x + wave_w*0.25:.1f}" y="366" text-anchor="middle">W13</text>
      <text x="{wave_x + wave_w*0.5:.1f}" y="366" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w*0.75:.1f}" y="366" text-anchor="middle">W39</text>
      <text x="{wave_x + wave_w}" y="366" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- ==================== BENTO BLOCK 5: FEATURED PROJECTS ==================== -->
  <g class="fade-in delay-4">
    <rect x="24" y="390" width="752" height="164" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="40" y="410" font-size="9.5" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// FEATURED PROJECTS</text>
    <text x="760" y="410" text-anchor="end" font-size="9" font-weight="500" fill="{text_tertiary}">Open Source Systems &amp; Tools</text>
    <line x1="40" y1="418" x2="760" y2="418" stroke="{border_subtle}" stroke-width="1"/>
"""

    row_ys = [426, 458, 490, 522]

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

        div_line = f"""<line x1="40" y1="{ry + 26}" x2="760" y2="{ry + 26}" stroke="{border_subtle}" stroke-width="0.75"/>""" if idx < 3 else ""

        svg += f"""    <!-- Project Row {idx + 1} -->
    <g>
      <text x="40" y="{ry + 17}" font-size="11.5" font-weight="600" fill="{text_primary}">[{idx + 1:02d}] {r_name}</text>
      <text x="180" y="{ry + 17}" font-size="10.5" font-weight="400" fill="{text_secondary}">{r_desc}</text>
      
      <!-- Tech Badge -->
      <rect x="{670 - tag_w}" y="{ry + 4}" width="{tag_w}" height="17" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <text x="{670 - tag_w/2}" y="{ry + 16}" text-anchor="middle" font-size="8.5" font-weight="500" fill="{text_tertiary}">{r_stack}</text>
      
      <!-- Stars -->
      <text x="756" y="{ry + 17}" text-anchor="end" font-size="9.5" font-weight="600" fill="{text_primary}">{star_str}</text>
      {div_line}
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== FOOTER ==================== -->
  <g class="fade-in delay-4">
    <line x1="24" y1="566" x2="776" y2="566" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="582" font-size="9.5" font-weight="400" fill="{text_tertiary}">{affiliation} · {location} · {employment_status}</text>
    <text x="772" y="582" text-anchor="end" font-size="9.5" font-weight="400" fill="{text_tertiary}">Updated via GitHub Actions · SVG Telemetry</text>
  </g>
</svg>
"""
    return svg

def generate_svg_portrait(theme="dark", data=None, config=None, avatar_data_uri=""):
    if config is None:
        config = {}
    if data is None:
        data = {}

    is_dark = (theme == "dark")
    
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

    cal = data.get("contributionsCollection", {}).get("contributionCalendar", {})
    weeks = cal.get("weeks", [])
    
    weekly_counts = []
    for w in weeks:
        weekly_counts.append(sum(d.get("contributionCount", 0) for d in w.get("contributionDays", [])))
    
    if len(weekly_counts) > 52:
        weekly_counts = weekly_counts[-52:]
    elif len(weekly_counts) < 52:
        weekly_counts = [0] * (52 - len(weekly_counts)) + weekly_counts

    raw_max = max(weekly_counts) if weekly_counts else 0
    peak_idx = weekly_counts.index(raw_max) if (weekly_counts and raw_max in weekly_counts) else 0
    max_week = raw_max if raw_max > 0 else 1

    wave_x = 28
    wave_w = 344
    wave_y_base = 414
    wave_y_top = 366
    wave_h = wave_y_base - wave_y_top

    points = []
    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        normalized = count / max_week if max_week > 0 else 0
        py = wave_y_base - (normalized * wave_h)
        points.append((px, py))

    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for px, py in points[1:]:
        path_d += f" L {px:.1f} {py:.1f}"

    area_d = path_d + f" L {points[-1][0]:.1f} {wave_y_base} L {points[0][0]:.1f} {wave_y_base} Z"
    peak_x, peak_y = points[peak_idx]

    stack_langs = config.get("stack_languages", [
        {"name": "Rust", "slug": "rust"},
        {"name": "TypeScript", "slug": "typescript"},
        {"name": "Python", "slug": "python"},
        {"name": "C", "slug": "c"},
        {"name": "C++", "slug": "cplusplus"},
        {"name": "Assembly", "slug": "assemblyscript"}
    ])[:6]

    # Target Platforms
    platforms = config.get("platforms", [
        {"name": "Linux", "badge": "Kernel · Drivers"},
        {"name": "macOS", "badge": "Darwin · Systems"},
        {"name": "Web", "badge": "Wasm · Modern UI"}
    ])[:3]

    # Project Scope Breakdown for Pie Chart
    project_scopes = config.get("project_scopes", [
        {"name": "Drivers & Low-Level", "pct": 45},
        {"name": "User Interface / GUI", "pct": 35},
        {"name": "Systems & Daemons", "pct": 20}
    ])[:3]

    featured = config.get("featured_repos", [])[:4]
    
    raw_name = config.get("name", "Nilton Perim Neto")
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(config.get("tagline", "Not a Programmer, just a historian."))
    affiliation = xesc(config.get("affiliation", "Universidade Federal de Goiás"))
    location = xesc(config.get("location", "Goiás, Brazil"))
    
    emp_status_raw = config.get("employment_status", "Seeking Employment · Open to Work")
    employment_status = xesc(emp_status_raw)

    if avatar_data_uri:
        avatar_svg = f"""      <image href="{avatar_data_uri}" x="28" y="24" width="42" height="42" preserveAspectRatio="xMidYMid slice"/>
      <rect x="28" y="24" width="42" height="42" fill="none" stroke="{border}" stroke-width="1"/>"""
    else:
        avatar_svg = f"""      <rect x="28" y="24" width="42" height="42" fill="{inner_bg}" stroke="{border}" stroke-width="1"/>
      <text x="49" y="50" text-anchor="middle" font-size="13" font-weight="700" fill="{text_primary}">NP</text>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 680" width="100%" height="100%">
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
        animation: pulseSquare 2.5s infinite;
        transform-origin: center;
      }}

      @keyframes drawPath {{
        to {{ stroke-dashoffset: 0; }}
      }}

      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(3px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      @keyframes pulseSquare {{
        0%, 100% {{ opacity: 0.2; transform: scale(1); }}
        50% {{ opacity: 0.9; transform: scale(1.6); }}
      }}
    </style>

    <linearGradient id="curveGrad_portrait_{theme}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{accent}" stop-opacity="{accent_fill_opacity * 1.5:.2f}"/>
      <stop offset="70%" stop-color="{accent}" stop-opacity="{accent_fill_opacity * 0.5:.2f}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.0"/>
    </linearGradient>

    <pattern id="grid_portrait_{theme}" width="16" height="16" patternUnits="userSpaceOnUse">
      <path d="M 16 0 L 0 0 0 16" fill="none" stroke="{border_subtle}" stroke-width="0.5" opacity="0.3"/>
    </pattern>
  </defs>

  <rect width="400" height="680" fill="{bg}"/>
  <rect width="400" height="680" fill="url(#grid_portrait_{theme})"/>

  <!-- ==================== BENTO BLOCK 1: PROFILE HEADER ==================== -->
  <g class="fade-in">
    <rect x="16" y="14" width="368" height="94" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
{avatar_svg}

    <text x="82" y="44" font-size="14.5" font-weight="700" fill="{text_primary}" letter-spacing="-0.01em">{display_name}</text>
    <text x="82" y="60" font-size="10" font-weight="400" fill="{text_secondary}">{tagline}</text>

    <!-- Employment Status Badge -->
    <rect x="28" y="78" width="344" height="22" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
    <rect x="36" y="85" width="7" height="7" fill="{text_primary}"/>
    <text x="49" y="93.5" font-size="9.5" font-weight="600" fill="{text_primary}">{employment_status}</text>
    <text x="364" y="93.5" text-anchor="end" font-size="8.5" font-weight="500" fill="{text_tertiary}">STATUS: ACTIVE</text>
  </g>

  <!-- ==================== BENTO BLOCK 2: MY STACK ==================== -->
  <g class="fade-in delay-1">
    <rect x="16" y="120" width="368" height="92" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    <text x="28" y="137" font-size="9" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// MY STACK</text>
    <text x="372" y="137" text-anchor="end" font-size="8.5" font-weight="500" fill="{text_tertiary}">6 Core Languages</text>
"""

    tile_w = 110
    tile_h = 26
    start_x = 28
    gap_x = 7
    row_ys = [145, 175]

    for idx, lang in enumerate(stack_langs):
        col = idx % 3
        row = idx // 3
        tx = start_x + col * (tile_w + gap_x)
        ty = row_ys[row]
        lname = xesc(lang.get("name", ""))
        lslug = lang.get("slug", "").lower()
        path_data = LANGUAGE_ICONS.get(lslug, LANGUAGE_ICONS.get("rust"))

        svg += f"""    <!-- {lname} Tile -->
    <g transform="translate({tx}, {ty})">
      <rect width="{tile_w}" height="{tile_h}" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <g transform="translate(6, 4.5) scale(0.65)">
        <path fill-rule="evenodd" clip-rule="evenodd" d="{path_data}" fill="{text_secondary}"/>
      </g>
      <text x="27" y="17" font-size="10" font-weight="600" fill="{text_primary}">{lname}</text>
    </g>
"""

    pie_svg = generate_pie_chart_svg(196, 284, 16, project_scopes, is_dark, card_bg, border)

    svg += f"""  </g>

  <!-- ==================== BENTO BLOCK 3: PLATFORMS & PROJECT SCOPE ==================== -->
  <g class="fade-in delay-2">
    <rect x="16" y="222" width="368" height="96" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="239" font-size="9" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// PLATFORMS &amp; PROJECT SCOPE</text>
    <text x="372" y="239" text-anchor="end" font-size="8.5" font-weight="500" fill="{text_tertiary}">Linux · macOS · Web</text>
    <line x1="28" y1="246" x2="372" y2="246" stroke="{border_subtle}" stroke-width="0.75"/>

    <!-- Column 1: Target Platforms -->
    <text x="28" y="259" font-size="8" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">TARGET PLATFORMS</text>
"""

    chip_start_y = 265
    chip_h = 14
    for idx, p in enumerate(platforms):
        cy = chip_start_y + idx * 17
        p_name = xesc(p.get("name", "").upper())
        p_badge = xesc(p.get("badge", "").split("·")[0].strip())
        svg += f"""    <!-- Platform Chip: {p_name} -->
    <g transform="translate(28, {cy})">
      <rect width="130" height="{chip_h}" fill="{inner_bg}" stroke="{border}" stroke-width="0.6"/>
      <rect x="5" y="5" width="4" height="4" fill="{accent}"/>
      <text x="14" y="10.5" font-size="8" font-weight="700" letter-spacing="0.03em" fill="{text_primary}">[ {p_name} ]</text>
      <text x="124" y="10.5" text-anchor="end" font-size="7.5" font-weight="500" fill="{text_tertiary}">{p_badge}</text>
    </g>
"""

    svg += f"""    <!-- Column Divider -->
    <line x1="168" y1="252" x2="168" y2="312" stroke="{border_subtle}" stroke-width="0.75"/>

    <!-- Column 2: Preferred Project Scope & Pie Chart -->
    <text x="180" y="259" font-size="8" font-weight="600" letter-spacing="0.06em" fill="{text_tertiary}">PROJECT SCOPE</text>

    <!-- Pizza Graphics (Pie Chart) -->
    <g>
{pie_svg}
    </g>
"""

    legend_colors = ["#f3f4f6", "#9ca3af", "#4b5563"] if is_dark else ["#1e293b", "#64748b", "#cbd5e1"]
    legend_text_colors = [text_primary, text_secondary, text_tertiary]
    short_names = ["Drivers", "UI / GUI", "Systems"]
    legend_ys = [272, 286, 300]

    for idx, s in enumerate(project_scopes):
        if idx >= len(legend_ys):
            break
        ly = legend_ys[idx]
        s_name = xesc(short_names[idx] if idx < len(short_names) else s.get("name", ""))
        s_pct = s.get("pct", 0)
        swatch_c = legend_colors[idx % len(legend_colors)]
        t_color = legend_text_colors[idx % len(legend_text_colors)]

        svg += f"""    <!-- Scope Item: {s_name} -->
    <g>
      <rect x="222" y="{ly - 6}" width="6" height="6" fill="{swatch_c}"/>
      <text x="232" y="{ly}" font-size="8" font-weight="600" fill="{t_color}">{s_name}</text>
      <text x="372" y="{ly}" text-anchor="end" font-size="8.5" font-weight="700" fill="{t_color}" class="tabular">{s_pct}%</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== BENTO BLOCK 4: ACTIVITY RHYTHM ==================== -->
  <g class="fade-in delay-3">
    <rect x="16" y="328" width="368" height="114" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="345" font-size="9" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// ACTIVITY RHYTHM</text>
    <text x="372" y="345" text-anchor="end" font-size="8.5" font-weight="500" fill="{text_tertiary}">52-Week Rhythm</text>

    <!-- Guide Lines -->
    <line x1="{wave_x}" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="{border_subtle}" stroke-width="1"/>
    <line x1="{wave_x}" y1="{wave_y_top + wave_h/2:.1f}" x2="{wave_x + wave_w}" y2="{wave_y_top + wave_h/2:.1f}" stroke="{border_subtle}" stroke-dasharray="3,4" stroke-width="0.75"/>

    <!-- Gradient Fill -->
    <path d="{area_d}" fill="url(#curveGrad_portrait_{theme})"/>

    <!-- Sharp Angular Trajectory Stroke -->
    <path class="draw-stroke" d="{path_d}" fill="none" stroke="{accent_stroke}" stroke-width="1.5" stroke-linejoin="miter"/>

    <!-- Peak Indicator (Sharp Square) -->
    <g transform="translate({peak_x:.1f}, {peak_y:.1f})">
      <rect x="-3" y="-3" width="6" height="6" fill="{accent_stroke}"/>
      <rect x="-3" y="-3" width="6" height="6" fill="none" stroke="{accent_stroke}" stroke-width="0.8" class="pulse-marker"/>
      <text x="0" y="-8" text-anchor="middle" font-size="8.5" font-weight="600" fill="{text_primary}">Peak: {max_week}</text>
    </g>

    <!-- Timeline Labels -->
    <g font-size="8.5" font-weight="500" fill="{text_tertiary}">
      <text x="{wave_x}" y="429">W01</text>
      <text x="{wave_x + wave_w*0.25:.1f}" y="429" text-anchor="middle">W13</text>
      <text x="{wave_x + wave_w*0.5:.1f}" y="429" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w*0.75:.1f}" y="429" text-anchor="middle">W39</text>
      <text x="{wave_x + wave_w}" y="429" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- ==================== BENTO BLOCK 5: FEATURED PROJECTS ==================== -->
  <g class="fade-in delay-4">
    <rect x="16" y="452" width="368" height="180" fill="{card_bg}" stroke="{border}" stroke-width="1"/>
    
    <text x="28" y="469" font-size="9" font-weight="700" letter-spacing="0.08em" fill="{text_tertiary}">// FEATURED PROJECTS</text>
    <text x="372" y="469" text-anchor="end" font-size="8.5" font-weight="500" fill="{text_tertiary}">Open Source</text>
    <line x1="28" y1="476" x2="372" y2="476" stroke="{border_subtle}" stroke-width="0.75"/>
"""

    row_ys = [481, 517, 553, 589]

    for idx, repo in enumerate(featured):
        if idx >= len(row_ys):
            break
        ry = row_ys[idx]
        r_name = xesc(repo.get("name", ""))
        r_desc = xesc(repo.get("desc", ""))
        r_stack = xesc(repo.get("stack", ""))
        r_stars = repo.get("stars", 0)

        star_str = f"★ {r_stars}" if r_stars > 0 else ""
        tag_w = max(34, len(r_stack) * 5.4 + 10)
        star_offset = 28 if r_stars > 0 else 0
        tag_x = 372 - star_offset - tag_w

        div_line = f"""<line x1="28" y1="{ry + 32}" x2="372" y2="{ry + 32}" stroke="{border_subtle}" stroke-width="0.5"/>""" if idx < 3 else ""

        svg += f"""    <!-- Project Row {idx + 1} -->
    <g>
      <text x="28" y="{ry + 13}" font-size="11" font-weight="600" fill="{text_primary}">[{idx + 1:02d}] {r_name}</text>
      
      <!-- Tech Badge -->
      <rect x="{tag_x:.1f}" y="{ry + 2}" width="{tag_w:.1f}" height="14" fill="{inner_bg}" stroke="{border}" stroke-width="0.75"/>
      <text x="{tag_x + tag_w/2:.1f}" y="{ry + 12}" text-anchor="middle" font-size="7.5" font-weight="500" fill="{text_tertiary}">{r_stack}</text>
      
      <!-- Stars -->
      <text x="372" y="{ry + 13}" text-anchor="end" font-size="9" font-weight="600" fill="{text_primary}">{star_str}</text>

      <!-- Description Line -->
      <text x="28" y="{ry + 26}" font-size="9" font-weight="400" fill="{text_secondary}">{r_desc}</text>
      {div_line}
    </g>
"""

    svg += f"""  </g>

  <!-- ==================== FOOTER ==================== -->
  <g class="fade-in delay-4">
    <line x1="16" y1="642" x2="384" y2="642" stroke="{border}" stroke-width="0.75"/>
    
    <text x="20" y="655" font-size="8" font-weight="400" fill="{text_tertiary}">{affiliation} · {location}</text>
    <text x="20" y="667" font-size="7.5" font-weight="400" fill="{text_tertiary}">Updated via GitHub Actions · SVG Telemetry</text>
    <text x="380" y="667" text-anchor="end" font-size="7.5" font-weight="500" fill="{text_tertiary}">HUD v2.4</text>
  </g>
</svg>
"""
    return svg

def generate_svg(theme="dark", data=None, config=None, avatar_data_uri=""):
    # Default to wide
    return generate_svg_wide(theme, data, config, avatar_data_uri)

def main():
    config = load_config()
    username = config.get("username", "niltonperimneto")

    print(f"Fetching GitHub data for {username}...")
    data = fetch_github_data(username)

    avatar_url = data.get("avatarUrl") or config.get("avatar_url") or "https://avatars.githubusercontent.com/u/118851240?v=4"
    print(f"Fetching avatar from {avatar_url}...")
    avatar_data_uri = fetch_avatar_data_uri(avatar_url)

    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Wide Cards (Desktop / >= 600px)
    wide_dark = generate_svg_wide("dark", data=data, config=config, avatar_data_uri=avatar_data_uri)
    wide_light = generate_svg_wide("light", data=data, config=config, avatar_data_uri=avatar_data_uri)
    (out_dir / "zed-card-wide-dark.svg").write_text(wide_dark, encoding="utf-8")
    (out_dir / "zed-card-wide-light.svg").write_text(wide_light, encoding="utf-8")

    # 2. Portrait Cards (Mobile / < 600px)
    portrait_dark = generate_svg_portrait("dark", data=data, config=config, avatar_data_uri=avatar_data_uri)
    portrait_light = generate_svg_portrait("light", data=data, config=config, avatar_data_uri=avatar_data_uri)
    (out_dir / "zed-card-portrait-dark.svg").write_text(portrait_dark, encoding="utf-8")
    (out_dir / "zed-card-portrait-light.svg").write_text(portrait_light, encoding="utf-8")

    # 3. Standard Fallbacks
    (out_dir / "zed-card-dark.svg").write_text(wide_dark, encoding="utf-8")
    (out_dir / "zed-card-light.svg").write_text(wide_light, encoding="utf-8")

    print("All wide and portrait SVG assets generated successfully!")

if __name__ == "__main__":
    main()
