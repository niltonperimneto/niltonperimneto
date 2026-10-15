"""Render independent card sections using shared layouts and SVG primitives."""

from .activity import extract_weekly_activity, selected_projects
from .layout import PORTRAIT, WIDE
from .svg import SVG, escape, truncate
from .themes import theme_css


def render_frame(svg, layout, config, data, theme):
    width, height = layout.width, layout.height
    name = config["name"] or data.get("name") or config["username"]
    svg.add(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" role="img" aria-labelledby="title description">
  <title id="title">{escape(name)} — developer profile</title>
  <desc id="description">Platforms, languages, contribution activity and selected projects.</desc>
  <defs><style>{escape(theme_css(theme, config['appearance']))}</style></defs>
  <rect width="{width}" height="{height}" rx="6" fill="var(--bg)"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="6" fill="none" stroke="var(--border)"/>
  <path d="M1 6Q1 1 6 1H{width - 6}Q{width - 1} 1 {width - 1} 6V34H1Z" fill="var(--card)"/>
  <path d="M0 34.5H{width}" stroke="var(--border)"/>''')
    svg.text(layout.margin, 22, truncate(config["labels"]["file"], 40), "muted")
    svg.text(layout.right, 22, "UTF-8", "label", "end")


def render_header(svg, layout, config, data, avatar):
    left, right = layout.margin, layout.right
    name = config["name"] or data.get("name") or config["username"]
    name = name.title() if name.isupper() else name
    if avatar:
        svg.add(f'<image href="{escape(avatar)}" x="{left}" y="58" width="36" height="36" preserveAspectRatio="xMidYMid slice"/>')
    else:
        words = [word for word in name.split() if word[0].isalnum()]
        initials = "".join(word[0] for word in words[:2]).upper()
        svg.add(f'<rect x="{left}" y="58" width="36" height="36" rx="3" fill="var(--card)"/>')
        svg.text(left + 18, 81, initials, anchor="middle")
    svg.text(left + 50, 73, truncate(name, 27 if layout.portrait else 45), "name")
    svg.text(left + 50, 92, "@" + config["username"], "muted")
    tagline = config["tagline"] or data.get("bio") or ""
    svg.text(left, 122, truncate(tagline, 56 if layout.portrait else 110), "muted")
    status = truncate(config["employment_status"].split("·")[-1].strip(), 40 if layout.portrait else 24)
    if status:
        y = 148 if layout.portrait else 76
        x = left + 14 if layout.portrait else right - len(status) * 6.1
        svg.add(f'<circle cx="{x - 11}" cy="{y - 3}" r="2.5" fill="var(--status)"/>')
        svg.text(x, y, status, "muted")
    svg.line(left, layout.header_bottom, right, layout.header_bottom)


def render_languages(svg, layout, config):
    y = layout.languages_y
    svg.text(layout.margin, y, truncate(config["labels"]["languages"], 40), "label")
    columns = 3 if layout.portrait else 6
    step = layout.content_width / columns
    for index, language in enumerate(config["stack_languages"]):
        x = layout.margin + index % columns * step
        baseline = y + 24 + index // columns * 30
        svg.icon(language.get("slug", ""), x, baseline - 13, 16)
        svg.text(x + 24, baseline, truncate(language["name"], 13))


def render_platforms(svg, layout, config):
    y = layout.platforms_y
    svg.text(layout.margin, y, truncate(config["labels"]["platforms"], 30), "label")
    for index, platform in enumerate(config["platforms"]):
        x = layout.margin + index * (114 if layout.portrait else 120)
        svg.icon(platform.get("slug", platform["name"]), x, y + 17, 20)
        svg.text(x + 28, y + 31, truncate(platform["name"], 12))


def render_focus(svg, layout, config):
    x = layout.margin if layout.portrait else 420
    y, width = layout.focus_y, layout.right - x
    svg.text(x, y, truncate(config["labels"]["focus"], 30), "label")
    scopes = config["project_scopes"]
    active = [(index, scope) for index, scope in enumerate(scopes) if scope["pct"] > 0]
    available = width - 3 * max(0, len(active) - 1)
    cursor = x
    for index, scope in active:
        segment = scope["pct"] / 100 * available
        svg.add(f'<rect x="{cursor:.2f}" y="{y + 17}" width="{segment:.2f}" height="4" fill="var(--c{index + 1})"/>')
        cursor += segment + 3
    for index, scope in enumerate(scopes):
        label = scope.get("label", scope["name"])
        value = f"{scope['pct']:g}%"
        label = truncate(label, 17 - len(value) - 1)
        svg.text(x + index * width / 3, y + 41, f"{label} {value}", "muted")


def render_activity(svg, layout, config, data):
    left, right, y = layout.margin, layout.right, layout.activity_y
    weekly, total = extract_weekly_activity(data)
    svg.text(left, y, truncate(config["labels"]["activity"], 14), "label")
    summary = "Activity unavailable" if total is None else f"{total:,} contributions / 52 weeks"
    svg.text(right, y, summary, "muted", "end")
    chart_top, chart_bottom = y + 22, y + 76
    if total is not None:
        peak = max(max(weekly), 1)
        step = layout.content_width / len(weekly)
        for index, count in enumerate(weekly):
            bar_height = max(2, count / peak * (chart_bottom - chart_top))
            x = left + index * step
            svg.add(f'<rect x="{x:.2f}" y="{chart_bottom - bar_height:.2f}" width="{max(2, step - 3):.2f}" height="{bar_height:.2f}" rx="1" fill="var(--c1)" opacity="{0.28 if count == 0 else 0.85}"/>')
    else:
        svg.line(left, chart_bottom, right, chart_bottom)
    svg.text(left, chart_bottom + 17, "52 weeks ago", "label")
    svg.text(right, chart_bottom + 17, "This week", "label", "end")


def render_projects(svg, layout, config, data):
    y = layout.projects_y
    svg.text(layout.margin, y, truncate(config["labels"]["projects"], 45), "label")
    for index, project in enumerate(selected_projects(config, data)):
        x = layout.margin if layout.portrait else layout.margin + index % 2 * 392
        baseline = y + 29 + (index if layout.portrait else index // 2) * 32
        right = layout.right if layout.portrait else x + 352
        stack = truncate(project.get("stack", "Code"), 16)
        name_room = max(8, int((right - x - len(stack) * 6.1 - 18) / 6.7))
        svg.text(x, baseline, truncate(project["name"], name_room))
        svg.text(right, baseline, stack, "muted", "end")
        svg.line(x, baseline + 10, right, baseline + 10)


def render_footer(svg, layout, config, data):
    y = layout.height - (38 if layout.portrait else 18)
    svg.line(layout.margin, y - 18, layout.right, y - 18)
    location = truncate(config["location"] or data.get("location") or "", 56 if layout.portrait else 34)
    svg.text(layout.margin, y, location, "label")
    joke = config["footer_joke"]
    if layout.portrait:
        svg.text(layout.margin, y + 18, truncate(joke, 56), "label")
    else:
        room = int((layout.content_width - len(location) * 6.1 - 24) / 6.1)
        svg.text(layout.right, y, truncate(joke, room), "label", "end")


def render_card(config, data, theme=None, portrait=False, avatar=""):
    """Render a standalone SVG; no network or filesystem writes happen here."""
    layout = PORTRAIT if portrait else WIDE
    svg = SVG()
    render_frame(svg, layout, config, data, theme)
    render_header(svg, layout, config, data, avatar)
    render_languages(svg, layout, config)
    render_platforms(svg, layout, config)
    render_focus(svg, layout, config)
    render_activity(svg, layout, config, data)
    render_projects(svg, layout, config, data)
    render_footer(svg, layout, config, data)
    svg.add("</svg>")
    return svg.render()
