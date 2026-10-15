"""Normalize calendar data without inventing activity when GitHub is unavailable."""


def extract_weekly_activity(data):
    """Return exactly 52 weekly counts, plus the calendar's contribution total.

    An unavailable calendar has total=None. A real, empty calendar has total=0.
    Keeping these separate prevents an outage from being presented as inactivity.
    """
    calendar = data.get("contributionsCollection", {}).get("contributionCalendar")
    if calendar is None:
        return [0] * 52, None
    counts = [sum(day.get("contributionCount", 0) for day in week.get("contributionDays", []))
              for week in calendar.get("weeks", [])][-52:]
    return [0] * (52 - len(counts)) + counts, calendar.get("totalContributions", sum(counts))


def selected_projects(config, data):
    """Explicit projects win; otherwise use the user's top nonfork repositories."""
    if config["featured_repos"]:
        return config["featured_repos"]
    return [
        {"name": repo["name"], "stack": (repo.get("primaryLanguage") or {}).get("name") or "Code"}
        for repo in data.get("repositories", {}).get("nodes", [])[:4]
    ]
