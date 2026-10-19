"""Build assets/langs.svg, a "Most Used Languages" card with clearly distinct colours.

Run: python3 scripts/langs_card.py [user]
Data comes from the GitHub REST API (set GITHUB_TOKEN to avoid rate limits).
Bytes are summed over the user's own non-fork repos. If the API fails, the existing card is kept.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "KingAB2004"
OUT = Path(__file__).resolve().parent.parent / "assets" / "langs.svg"
API = "https://api.github.com"
TOP = 6

# Hand-picked so no two languages look alike on the dark background
COLOURS = {
    "Jupyter Notebook": "#ff8a5b",
    "Python": "#4b8bd4",
    "C++": "#f34b7d",
    "JavaScript": "#f1e05a",
    "CSS": "#a97bff",
    "HTML": "#3fb950",
    "TypeScript": "#2ec4c4",
    "C": "#a7a197",
}
FALLBACK = ["#e8e8e8", "#c58b5b", "#7bd88f", "#ff6f91"]


def get(path, retries=3):
    headers = {"User-Agent": "profile-card", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for _ in range(retries):
        try:
            req = urllib.request.Request(API + path, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            continue
    return None


def totals():
    repos = get(f"/users/{USER}/repos?per_page=100&type=owner")
    if not isinstance(repos, list):
        return None
    sums = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        langs = get(f"/repos/{repo['full_name']}/languages")
        if langs is None:
            return None
        for lang, size in langs.items():
            sums[lang] = sums.get(lang, 0) + size
    return sums


def render(sums):
    top = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)[:TOP]
    total = sum(size for _, size in top) or 1
    spare = iter(FALLBACK)
    langs = [(name, size * 100 / total, COLOURS.get(name) or next(spare, "#9f9f9f")) for name, size in top]

    x = 0.0
    bar = []
    for _, pct, colour in langs:
        bar.append(f'<rect x="{x:.2f}" y="0" width="{pct * 2.5:.2f}" height="8" fill="{colour}"/>')
        x += pct * 2.5
    legend = "\n".join(
        f'''    <g transform="translate({150 * (i % 2)},{25 * (i // 2)})">
      <circle cx="5" cy="6" r="5" fill="{colour}"/>
      <text x="15" y="10" class="lang">{name} {pct:.2f}%</text>
    </g>'''
        for i, (name, pct, colour) in enumerate(langs)
    )
    height = 90 + 25 * ((len(langs) + 1) // 2)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="{height}" viewBox="0 0 300 {height}">
  <title>Most Used Languages</title>
  <style>
    text {{ font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
    .title {{ font-size: 18px; font-weight: 600; fill: #f2c14e; }}
    .lang {{ font-size: 11px; font-weight: 400; fill: #ece8e1; }}
  </style>
  <rect x="0.5" y="0.5" width="299" height="{height - 1}" rx="4.5" fill="#0e0d0c"/>
  <text x="25" y="35" class="title">Most Used Languages</text>
  <mask id="bar"><rect x="0" y="0" width="250" height="8" rx="5" fill="#fff"/></mask>
  <g transform="translate(25,55)" mask="url(#bar)">
    {"".join(bar)}
  </g>
  <g transform="translate(25,80)">
{legend}
  </g>
</svg>
'''


def main():
    sums = totals()
    if not sums:
        print("GitHub API unavailable, keeping the existing card")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(sums), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
