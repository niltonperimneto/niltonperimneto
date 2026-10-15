"""Small SVG writing primitives; user-provided text is escaped at the boundary."""

import html
import json
from pathlib import Path

ICONS = json.loads(Path(__file__).with_name("icons.json").read_text(encoding="utf-8"))


def escape(value):
    return html.escape(str(value), quote=True)


def truncate(value, max_length):
    value = str(value).strip()
    return value if len(value) <= max_length else value[:max(0, max_length - 1)].rstrip() + "…"


class SVG:
    def __init__(self):
        self.parts = []

    def add(self, markup):
        self.parts.append(markup)

    def text(self, x, y, value, cls="body", anchor=None):
        alignment = f' text-anchor="{anchor}"' if anchor else ""
        self.add(f'<text x="{x}" y="{y}" class="{cls}"{alignment}>{escape(value)}</text>')

    def line(self, x1, y1, x2, y2):
        self.add(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="var(--border-sub)"/>')

    def icon(self, slug, x, y, size=18):
        path = ICONS.get(slug.lower())
        if path:
            self.add(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24">'
                     f'<path d="{escape(path)}" fill="var(--fg-muted)" fill-rule="evenodd"/></svg>')

    def render(self):
        return "\n".join(self.parts) + "\n"
