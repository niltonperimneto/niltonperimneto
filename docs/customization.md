# Customizing your profile cards

Start by copying `examples/config.example.json` to `config.json`. All commands below run from the repository root. Python 3.10 or newer is the only runtime dependency.

## Profile settings

| Setting | Behavior |
| --- | --- |
| `username` | Required GitHub username. This determines whose data is fetched. |
| `name` | Display name; empty uses GitHub’s name, then the username. |
| `tagline` | Introduction; empty uses GitHub’s bio. |
| `location` | Footer location; empty uses GitHub’s location. |
| `employment_status` | Optional status beside a subtle dot. If it contains `·`, only the final part is shown. Empty hides it. |
| `avatar_url` | Optional image URL overriding the GitHub avatar. A failed or missing avatar shows initials derived from the display name. |
| `footer_joke` | Footer text. Defaults to `'Tis but a scratch.` from Monty Python. Use `""` to hide it. |
| `stack_languages` | Up to six `{ "name": "Python", "slug": "python" }` entries. |
| `platforms` | Up to three `{ "name": "Linux", "slug": "linux" }` entries. |
| `project_scopes` | Up to three `{ "name": "Application development", "label": "Apps", "pct": 60 }` entries. Percentages must total 100. `label` is an optional short legend name. |
| `featured_repos` | Up to four `{ "name": "my-project", "stack": "Python" }` entries. `[]` selects GitHub’s top nonfork repositories from the fetched set. |

Lists default to empty. Profile fields default to empty and never fall back to this repository owner’s identity. Text is escaped for SVG and shortened to fit fixed layout columns. Keep labels concise, especially with custom fonts that have wider characters. The footer uses two lines on portrait cards.

The previous unused `affiliation`, `system_env`, `coordinates`, `exclude_repos_from_stats`, platform `badge`, and project `desc`/`stars` fields have been removed from the example and owner config. They were not rendered by the minimal design. Remove old top-level settings when migrating; unknown top-level keys produce a clear error.

## Typography and colors

The default monospace font stack uses installed system fonts. To customize it and override selected palette colors:

```json
{
  "appearance": {
    "font_family": "Menlo, Consolas, monospace",
    "dark": { "bg": "#191919", "c1": "#a5b8cc" },
    "light": { "bg": "#fafaf8", "c1": "#526d8a" }
  }
}
```

Merge this section into your config; omitted colors keep their defaults. Colors use six-digit hex notation. Fonts must be available on the viewer’s computer; external font downloads are not embedded.

| Color | Purpose |
| --- | --- |
| `bg`, `card` | Main surface and title bar |
| `border`, `border-sub` | Outer border and subtle separators |
| `fg`, `fg-muted`, `fg-dim` | Main text, secondary text/icons, and section/footer labels |
| `c1`, `c2`, `c3` | Focus segments; `c1` also colors activity bars |
| `status` | Employment status dot |

Optional `labels` overrides change section names without editing Python:

```json
{
  "labels": {
    "file": "~/about-me.md",
    "languages": "Languages",
    "platforms": "Platforms",
    "focus": "Focus",
    "activity": "Activity",
    "projects": "Selected projects"
  }
}
```

Spacing and canvas dimensions live in `generator/layout.py`. Individual sections live in `generator/render.py`. Change those files when you want a different layout; JSON settings cover content and appearance.

## Icons

Bundled slugs are `rust`, `typescript`, `python`, `c`, `cplusplus`, `assemblyscript`, `assembly`, `webassembly`, `swift`, `linux`, `macos`, and `web`.

Add a new slug and SVG path string to `generator/icons.json`. Paths use a `0 0 24 24` view box. Use a complete vector path and retain any attribution required by its source. Most bundled brand paths come from [Simple Icons](https://simpleicons.org/); C/C++ and the globe are custom paths. Unknown slugs omit the icon while keeping the text, so a new language does not require an icon.

## Commands and output

```sh
# Fetch your profile and regenerate all eight assets.
python3 generator/generate.py

# No network requests, authentication, or avatar downloads.
python3 generator/generate.py --offline

# Try another config without overwriting committed cards.
python3 generator/generate.py --config examples/config.example.json --offline --output-dir .preview

# Render a saved GraphQL user object deterministically, without fetching an avatar.
python3 generator/generate.py --data-file /path/to/user.json --output-dir .preview

# Equivalent module entry point.
python3 -m generator.generate --help
```

`--config` and `--output-dir` accept absolute or relative paths. Without overrides, paths resolve to this repository’s `config.json` and `assets/`, even when the command is run elsewhere. All variants are parsed as XML before files are written.

| Files | Intended use |
| --- | --- |
| `zed-card-wide.svg`, `zed-card-portrait.svg` | Automatic light/dark theme through SVG media queries |
| `zed-card-wide-dark.svg`, `zed-card-wide-light.svg` | Explicit wide themes |
| `zed-card-portrait-dark.svg`, `zed-card-portrait-light.svg` | Explicit portrait themes |
| `zed-card-dark.svg`, `zed-card-light.svg` | Backward-compatible copies of the explicit wide themes |

The preview reads `assets/`. To preview a separate `.preview` output, embed those SVGs directly or regenerate `assets/` after testing your config.

## Data and authentication

Online generation first tries GraphQL with `PROFILE_TOKEN` or `GITHUB_TOKEN`, then an installed and authenticated `gh` CLI. If neither works, it requests the public GitHub profile and up to 100 recently updated repositories, then sorts nonfork repositories by stars. GraphQL fetches up to 100 nonfork repositories already ordered by stars.

The unauthenticated calendar fallback uses `github-contributions-api.jogruber.de`, a third-party service. Offline mode and `--data-file` never contact GitHub or this service. If all calendar sources fail, the card says **Activity unavailable**; a real zero-activity calendar stays zero. No demonstration contributions are inserted into live cards.

The Actions workflow passes `secrets.PROFILE_TOKEN` when present, or its built-in `GITHUB_TOKEN`. If the built-in token cannot access the GraphQL user data you need, configure an appropriate personal token as the repository’s `PROFILE_TOKEN` Actions secret. Keep tokens out of `config.json`. The workflow needs permission to write repository contents to commit refreshed SVG files; if your repository or organization disables that permission, generate and commit them locally instead.

## Embedding in another README

Copy the generated assets into that repository and add:

```html
<picture>
  <source media="(max-width: 600px)" srcset="./assets/zed-card-portrait.svg">
  <img alt="Your Name — developer profile" src="./assets/zed-card-wide.svg" width="100%">
</picture>
```

For automated updates, keep `config.json`, `generator/`, `tests/`, and `.github/workflows/update-profile.yml` together. The workflow uses the configured username; it does not depend on the original repository owner.
