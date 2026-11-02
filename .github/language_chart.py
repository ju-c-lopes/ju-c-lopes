"""Generate a chart of programming languages used in public repositories."""

import os
import tempfile
from filecmp import cmp

import matplotlib.pyplot as plt
from update_readme import GitHubApiError, fetch_repositories

repos = fetch_repositories()

if any(
    repo.get("language") is not None and not isinstance(repo.get("language"), str)
    for repo in repos
):
    raise GitHubApiError("GitHub API returned invalid repository data")

langs = {}
for repo in repos:
    lang = repo.get("language")
    if lang:
        langs[lang] = langs.get(lang, 0) + 1

# Sort languages by count
sorted_langs = sorted(langs.items(), key=lambda item: item[1])
languages = [item[0] for item in sorted_langs]
counts = [item[1] for item in sorted_langs]
total_repos = sum(counts)

# Generate the horizontal bar chart
plt.figure(figsize=(10, 8))
plt.barh(languages, counts, color="skyblue")
plt.xlabel("Number of Repositories", color="#A9A9A9")
plt.title("Languages Distribution", color="#A9A9A9")
plt.tick_params(axis="x", colors="#A9A9A9")
plt.tick_params(axis="y", colors="#A9A9A9")

# Add percentage labels to each bar
for i, v in enumerate(counts):
    plt.text(v, i, f" {v/total_repos*100:.1f}%", color="#A9A9A9", va="center")

plt.tight_layout()
with tempfile.NamedTemporaryFile(
    dir=".",
    prefix=".languages-",
    suffix=".png",
    delete=False,
) as temporary_file:
    temporary_path = temporary_file.name

try:
    plt.savefig(temporary_path, transparent=True)
    if not os.path.exists("languages.png") or not cmp(
        temporary_path, "languages.png", shallow=False
    ):
        os.replace(temporary_path, "languages.png")
finally:
    if os.path.exists(temporary_path):
        os.remove(temporary_path)
    plt.close()
