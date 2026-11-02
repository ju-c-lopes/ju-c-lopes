"""Fetch GitHub user statistics and update the README.md file."""

import logging
import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import requests

USERNAME = "ju-c-lopes"
README_PATH = "README.md"
PROFILE_TIMEZONE = ZoneInfo("America/Sao_Paulo")


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API response cannot be used."""


def _get_json(url, expected_type, params=None, timeout=15):
    """Fetch JSON from GitHub and validate its top-level type."""
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logging.error("Request failed for %s: %s", url, exc)
        raise GitHubApiError(f"GitHub API request failed: {url}") from exc
    except ValueError as exc:
        logging.error("Invalid JSON response from %s: %s", url, exc)
        raise GitHubApiError(f"GitHub API returned invalid JSON: {url}") from exc

    if not isinstance(data, expected_type):
        actual_type = type(data).__name__
        expected_name = expected_type.__name__
        logging.error(
            "Unexpected JSON response from %s: expected %s, got %s",
            url,
            expected_name,
            actual_type,
        )
        raise GitHubApiError(
            f"GitHub API returned an unexpected response type: {url}"
        )

    return data


def fetch_repositories():
    """Fetch all public repositories for the configured user."""
    repositories = []
    page = 1
    repositories_url = f"https://api.github.com/users/{USERNAME}/repos"

    while True:
        page_data = _get_json(
            repositories_url,
            expected_type=list,
            params={"per_page": 100, "page": page},
        )

        if not all(isinstance(repo, dict) for repo in page_data):
            logging.error("GitHub repository response contains a non-object item")
            raise GitHubApiError("GitHub API returned an invalid repository list")

        repositories.extend(page_data)
        if len(page_data) < 100:
            return repositories

        page += 1


def fetch_github_data():
    """Fetch user statistics from GitHub API."""
    user_data = _get_json(
        f"https://api.github.com/users/{USERNAME}",
        expected_type=dict,
    )
    repos_data = fetch_repositories()

    if not isinstance(user_data.get("followers"), int):
        logging.error("GitHub user response has an invalid followers value")
        raise GitHubApiError("GitHub API returned an invalid user response")

    if any(
        not isinstance(repo.get("stargazers_count"), int)
        or repo.get("language") is not None
        and not isinstance(repo.get("language"), str)
        for repo in repos_data
    ):
        logging.error("GitHub repository response has invalid field types")
        raise GitHubApiError("GitHub API returned invalid repository data")

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
    top_languages = {}
    for repo in repos_data or []:
        lang = repo.get("language")
        if lang:
            top_languages[lang] = top_languages.get(lang, 0) + 1
    top_langs_sorted = sorted(top_languages.items(), key=lambda x: x[1], reverse=True)[
        :3
    ]

    return {
        "followers": user_data.get("followers", 0),
        "repos": len(repos_data),
        "stars": total_stars,
        "languages": ", ".join(lang for lang, _ in top_langs_sorted),
    }


def _render_stats_block(stats, updated):
    return f"""<!--STATS-START-->
### 📊 **GitHub Stats**
- 👥 Followers: **`{stats['followers']}`**
- 📦 Public Repositories: **`{stats['repos']}`**
- 🌟 Earned stars: **`{stats['stars']}`**
- 💬 Most used languages: **`{stats['languages']}`**
- 🕓 Latest update: **`{updated}`**
<!--STATS-END-->"""


def _stats_content(block):
    """Return statistics without the timestamp used for no-op comparison."""
    return "\n".join(
        line
        for line in block.splitlines()
        if not line.startswith("- 🕓 Latest update:")
    )


def _format_update_timestamp(value=None):
    if value:
        try:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(
                "PROFILE_UPDATE_DATE must be an ISO-8601 timestamp"
            ) from exc
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(PROFILE_TIMEZONE).strftime(
            "%Y-%m-%d %H:%M America/Sao_Paulo"
        )

    return datetime.now(PROFILE_TIMEZONE).strftime(
        "%Y-%m-%d %H:%M America/Sao_Paulo"
    )


def update_readme(stats, force_update=False, updated=None):
    """Update the README.md file with the fetched statistics."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!--STATS-START-->"
    end_marker = "<!--STATS-END-->"

    if start_marker in readme and end_marker in readme:
        start = readme.index(start_marker)
        end = readme.index(end_marker) + len(end_marker)
        current_block = readme[start:end]
        stats_unchanged = _stats_content(current_block) == _stats_content(
            _render_stats_block(stats, "")
        )
        if stats_unchanged and not force_update:
            logging.info("GitHub statistics have not changed; README was not updated")
            return False

        updated = updated or _format_update_timestamp()
        stats_block = _render_stats_block(stats, updated)
        new_readme = readme[:start] + stats_block + readme[end:]
    else:
        updated = updated or _format_update_timestamp()
        stats_block = _render_stats_block(stats, updated)
        new_readme = readme + stats_block

    if new_readme == readme:
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)
    return True


if __name__ == "__main__":
    github_stats = fetch_github_data()
    update_readme(
        github_stats,
        force_update=os.getenv("FORCE_PROFILE_UPDATE") == "true",
        updated=_format_update_timestamp(os.getenv("PROFILE_UPDATE_DATE")),
    )
