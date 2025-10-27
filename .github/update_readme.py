"""This script fetches GitHub user statistics and updates the README.md file"""

import logging
from datetime import UTC, datetime

import requests

USERNAME = "ju-c-lopes"
README_PATH = "README.md"


def _get_json(url, timeout=15):
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logging.error("Request failed for %s: %s", url, exc)
        return {}


def fetch_github_data():
    """Fetch user statistics from GitHub API."""
    user_data = _get_json(f"https://api.github.com/users/{USERNAME}")
    repos_data = _get_json(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    )

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
        "updated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    }


def update_readme(stats):
    """Update the README.md file with the fetched statistics."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!--STATS-START-->"
    end_marker = "<!--STATS-END-->"

    stats_block = f"""
{start_marker}
### 📊 **GitHub Stats**
- 👥 Followers: **`{stats['followers']}`**
- 📦 Public Repositories: **`{stats['repos']}`**
- 🌟 Earned stars: **`{stats['stars']}`**
- 💬 Most used languages: **`{stats['languages']}`**
- 🕓 Latest update: **`{stats['updated']}`**
{end_marker}
"""

    if start_marker in readme and end_marker in readme:
        start = readme.index(start_marker)
        end = readme.index(end_marker) + len(end_marker)
        new_readme = readme[:start] + stats_block + readme[end:]
    else:
        new_readme = readme + "\n" + stats_block

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)


if __name__ == "__main__":
    github_stats = fetch_github_data()
    update_readme(github_stats)
