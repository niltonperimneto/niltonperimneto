<picture>
  <source media="(max-width: 600px)" srcset="./assets/zed-card-portrait.svg">
  <img alt="Nilton Perim Neto — developer profile" src="./assets/zed-card-wide.svg" width="100%">
</picture>

## Make it yours

These minimal editor-style profile cards are generated with Python’s standard library. No packages, build tools, or font downloads are required. Wide and portrait cards come in dark, light, and automatic themes.

1. Fork or clone this repository. For a GitHub profile README, name your repository after your GitHub username.
2. Copy [examples/config.example.json](examples/config.example.json) to `config.json`, then set your username, profile details, languages, platforms, and focus areas. Clear `featured_repos` to select your top public nonfork repositories automatically, or list up to four projects yourself.
3. Generate and preview locally with Python 3.10 or newer:

   ```sh
   python3 generator/generate.py --offline
   python3 -m http.server 8000
   ```

   Open [the preview](http://localhost:8000/preview.html) to switch between sizes and themes. Offline mode uses your config and initials; live mode fetches your avatar and GitHub activity:

   ```sh
   python3 generator/generate.py
   ```

4. Update the image’s `alt` text above, then commit your config, README, and generated `assets/*.svg`. In a fork, enable Actions and run **Update Profile Cards** once. The included workflow also refreshes the cards daily and after config or generator changes.

Use [the customization guide](docs/customization.md) for all settings, theme colors, authentication, icons, and embedding the cards elsewhere. The footer joke is configurable—set `footer_joke` to an empty string to hide it.

## Repository guide

| Path | Purpose |
| --- | --- |
| `config.json` | Your profile and visual settings |
| `examples/config.example.json` | Neutral starting point for a clone |
| `generator/config.py` | Defaults and readable configuration errors |
| `generator/github.py`, `github.graphql` | GitHub profile, repository, calendar, and avatar requests |
| `generator/activity.py` | Calendar normalization and project selection |
| `generator/layout.py` | Shared wide and portrait coordinates |
| `generator/render.py`, `svg.py` | Card sections and escaped SVG primitives |
| `generator/themes.py` | Named default palettes and typography |
| `generator/icons.json` | Bundled icon paths; no runtime icon downloads |
| `generator/generate.py` | Command line and SVG output orchestration |
| `preview.html` | Local theme and size preview |
| `tests/` | Configuration, data, rendering, and CLI checks |

Run the checks with:

```sh
python3 -m unittest discover -s tests -v
```
