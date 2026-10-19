"""Build assets/codechef.svg, a CodeChef stats card styled like the Codeforces card.

Run: python3 scripts/codechef_card.py [handle]
Data comes from competeapi.vercel.app. If the API fails, the existing card is kept.
"""
import json
import sys
import urllib.request
from pathlib import Path

HANDLE = sys.argv[1] if len(sys.argv) > 1 else "kingab"
NAME = "Arpit Bhomia"
OUT = Path(__file__).resolve().parent.parent / "assets" / "codechef.svg"
API = f"https://competeapi.vercel.app/user/codechef/{HANDLE}/"

# CodeChef star bands: (min rating, stars, colour)
BANDS = [(2500, 7, "#ff7f00"), (2200, 6, "#ff7f00"), (2000, 5, "#ffbf00"), (1800, 4, "#684273"),
         (1600, 3, "#3366cc"), (1400, 2, "#1e7d22"), (0, 1, "#666666")]


def fetch(retries=4):
    for _ in range(retries):
        try:
            req = urllib.request.Request(API, headers={"User-Agent": "profile-card"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            continue
    return None


def clean(v):
    return " ".join(str(v).split()) if v is not None else ""


def band(rating):
    for lo, stars, colour in BANDS:
        if rating >= lo:
            return stars, colour
    return 1, "#666666"


def render(d):
    rating = int(d.get("rating_number") or 0)
    max_rating = int(d.get("max_rank") or rating)  # the API calls max rating "max_rank"
    stars, colour = band(max(rating, max_rating))
    global_rank = clean(d.get("global_rank")) or "–"
    country_rank = clean(d.get("country_rank")) or "–"
    country = clean(d.get("country")) or "–"

    rows = [
        ("Current rating", str(rating)),
        ("Max rating", str(max_rating)),
        ("Global rank", global_rank),
        ("Country rank", country_rank),
        ("Country", country),
    ]
    row_svg = "\n".join(
        f'''  <g class="row" style="animation-delay:{0.25 + i * 0.12:.2f}s" transform="translate(28,{150 + i * 27})">
    <circle cx="6" cy="-5" r="3.5" fill="{colour}"/>
    <text x="20" class="label">{label}</text>
    <text x="324" class="value" text-anchor="end">{value}</text>
  </g>'''
        for i, (label, value) in enumerate(rows)
    )
    star_svg = "".join(
        f'<text x="{i * 22}" class="star" style="animation-delay:{0.1 + i * 0.08:.2f}s" fill="{colour}">★</text>'
        for i in range(stars)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="380" height="290" viewBox="0 0 380 290">
  <title>{NAME} | CodeChef Stats</title>
  <style>
    text {{ font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
    .title {{ font-size: 22px; font-weight: 800; fill: #ffffff; }}
    .handle {{ font-size: 14px; font-weight: 600; fill: #9f9f9f; }}
    .big {{ font-size: 40px; font-weight: 800; fill: {colour}; }}
    .tier {{ font-size: 14px; font-weight: 600; fill: #9f9f9f; }}
    .star {{ font-size: 20px; opacity: 0; animation: fade .5s ease-out forwards; }}
    .label {{ font-size: 15px; font-weight: 600; fill: #9f9f9f; }}
    .value {{ font-size: 15px; font-weight: 700; fill: #ffffff; }}
    .row {{ opacity: 0; animation: fade .5s ease-out forwards; }}
    @keyframes fade {{ to {{ opacity: 1; }} }}
  </style>
  <rect x="0.5" y="0.5" width="379" height="289" rx="4" fill="#151515" stroke="#e4e2e2"/>
  <g transform="translate(28,44)">
    <path transform="translate(0,-24) scale(1.2)" d="M7 11.5a4 4 0 0 1-.8-7.9A5 5 0 0 1 12 1a5 5 0 0 1 5.8 2.6 4 4 0 0 1-.8 7.9V17H7v-5.5ZM7 19h10v2.5a1.5 1.5 0 0 1-1.5 1.5h-7A1.5 1.5 0 0 1 7 21.5V19Z" fill="#c8a27c"/>
    <text x="38" class="title">{NAME}</text>
    <text x="38" y="20" class="handle">@{HANDLE} · CodeChef</text>
  </g>
  <g transform="translate(28,114)">
    <text class="big">{rating}</text>
    <g transform="translate(110,-12)">{star_svg}</g>
    <text x="110" y="8" class="tier">{stars}★ coder</text>
  </g>
{row_svg}
</svg>
'''


def main():
    d = fetch()
    if not d or "rating_number" not in d:
        print("CodeChef API unavailable, keeping the existing card")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(d), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
