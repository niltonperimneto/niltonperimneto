"""GitHub data and avatar fetching, isolated from SVG rendering.

Use authenticated GraphQL when possible, then public REST and a public
contribution calendar. Missing activity remains unavailable, never synthetic.
"""

import base64
from datetime import date
import json
import logging
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)
QUERY = Path(__file__).with_name("github.graphql").read_text(encoding="utf-8")
NETWORK_ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError)


def request_json(url, token=None, payload=None):
    headers = {"User-Agent": "minimal-profile-card", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    with urlopen(Request(url, data=body, headers=headers), timeout=10) as response:
        return json.load(response)


def public_calendar(username):
    """Group public daily counts by actual Monday-based calendar weeks."""
    try:
        payload = request_json(f"https://github-contributions-api.jogruber.de/v4/{quote(username)}?y=last")
        days = sorted(payload.get("contributions", []), key=lambda day: day["date"])
        if not days:
            return None
        weeks = {}
        for day in days:
            year, week, _ = date.fromisoformat(day["date"]).isocalendar()
            weeks.setdefault((year, week), {"contributionDays": []})["contributionDays"].append(
                {"contributionCount": day.get("count", 0)}
            )
        return {"totalContributions": sum(day.get("count", 0) for day in days), "weeks": list(weeks.values())}
    except NETWORK_ERRORS + (KeyError, TypeError):
        LOG.warning("Public contribution calendar unavailable.")
        return None


def fetch_github_data(username):
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            response = request_json("https://api.github.com/graphql", token,
                                    {"query": QUERY, "variables": {"login": username}})
            user = (response.get("data") or {}).get("user")
            if user:
                return user
        except NETWORK_ERRORS:
            LOG.warning("Authenticated GitHub request failed; trying public data.")
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={username}"],
            capture_output=True, text=True, check=True, timeout=20,
        )
        user = (json.loads(result.stdout).get("data") or {}).get("user")
        if user:
            return user
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    # A clone always uses its configured username, including every fallback.
    user = {"login": username, "repositories": {"nodes": []}}
    try:
        profile = request_json(f"https://api.github.com/users/{quote(username)}", token)
        user.update({"name": profile.get("name"), "bio": profile.get("bio"),
                     "location": profile.get("location"), "avatarUrl": profile.get("avatar_url")})
    except NETWORK_ERRORS:
        LOG.warning("GitHub profile unavailable; using configured profile fields.")
    try:
        repos = request_json(f"https://api.github.com/users/{quote(username)}/repos?per_page=100&sort=updated", token)
        if isinstance(repos, list):
            owned = sorted((repo for repo in repos if not repo.get("fork")),
                           key=lambda repo: repo.get("stargazers_count", 0), reverse=True)
            user["repositories"]["nodes"] = [
                {"name": repo["name"], "primaryLanguage": {"name": repo.get("language")}}
                for repo in owned
            ]
    except NETWORK_ERRORS:
        LOG.warning("GitHub repositories unavailable; using configured projects.")
    calendar = public_calendar(username)
    if calendar is not None:
        user["contributionsCollection"] = {"contributionCalendar": calendar}
    return user


def fetch_avatar_data_uri(url):
    """Embed image bytes so cards work as standalone GitHub README images."""
    if not url:
        return ""
    try:
        request = Request(url, headers={"User-Agent": "minimal-profile-card"})
        with urlopen(request, timeout=10) as response:
            mime = response.headers.get_content_type()
            if mime not in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
                LOG.warning("Avatar is not a supported raster image; showing initials.")
                return ""
            return f"data:{mime};base64,{base64.b64encode(response.read()).decode('ascii')}"
    except NETWORK_ERRORS:
        LOG.warning("Avatar unavailable; showing initials.")
        return ""
