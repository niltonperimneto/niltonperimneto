"""Named editor colors and a small CSS layer shared by all card layouts."""

from .config import DEFAULT_FONT

PALETTES = {
    "dark": {
        "bg": "#191919", "card": "#202020", "border": "#303030", "border-sub": "#252525",
        "fg": "#dededb", "fg-muted": "#a5a5a0", "fg-dim": "#858580",
        "c1": "#adbbb0", "c2": "#808c82", "c3": "#525d55", "status": "#91ad96",
    },
    "light": {
        "bg": "#fafaf8", "card": "#f1f1ee", "border": "#ddddd7", "border-sub": "#eaeae5",
        "fg": "#30302d", "fg-muted": "#64645e", "fg-dim": "#77776f",
        "c1": "#586e5c", "c2": "#92a095", "c3": "#c2cbc3", "status": "#587d60",
    },
}


def theme_css(theme=None, appearance=None):
    appearance = appearance or {}

    def variables(name):
        palette = PALETTES[name] | appearance.get(name, {})
        return ";".join(f"--{key}:{value}" for key, value in palette.items())

    css = ":root {" + variables(theme or "dark") + "}"
    if theme is None:
        css += "@media (prefers-color-scheme:light) {:root {" + variables("light") + "}}"
    return css + f"""
      text {{
        font-family: {appearance.get('font_family', DEFAULT_FONT)};
        font-weight: 400;
        font-variant-numeric: tabular-nums;
      }}
      .label {{ fill: var(--fg-dim); font-size: 10px; }}
      .body {{ fill: var(--fg); font-size: 11px; }}
      .muted {{ fill: var(--fg-muted); font-size: 10px; }}
      .name {{ fill: var(--fg); font-size: 18px; font-weight: 500; }}
    """
