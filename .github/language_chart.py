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

# Gera o gráfico
plt.figure(figsize=(6, 6))
plt.pie(
    list(langs.values()), labels=list(langs.keys()), autopct="%1.1f%%", startangle=140
)
plt.title("Languages Distribution")
plt.savefig("languages.png")
