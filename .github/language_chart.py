"""This script generates a pie chart of programming languages used in the user's GitHub repositories."""

import matplotlib.pyplot as plt
from update_readme import _get_json

USERNAME = "ju-c-lopes"

repos = _get_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100")

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
plt.xlabel("Number of Repositories", color="white")
plt.title("Languages Distribution", color="white")
plt.tick_params(axis="x", colors="white")
plt.tick_params(axis="y", colors="white")

# Add percentage labels to each bar
for i, v in enumerate(counts):
    plt.text(v, i, f" {v/total_repos*100:.1f}%", color="white", va="center")

plt.tight_layout()
plt.savefig("languages.png", transparent=True)
