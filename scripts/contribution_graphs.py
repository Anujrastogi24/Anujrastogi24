"""Render a compact contribution heatmap per GitHub account, for side-by-side display."""
import datetime as dt
import os
import re
import sys
import urllib.request

# account -> output file name
USERS = {"Anujrastogi-1": "graph-work.svg", "Anujrastogi24": "graph-personal.svg"}
START = dt.date(2026, 6, 1)  # first month with real activity; earlier weeks are empty
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

WIDTH, GAP, LEFT, TOP = 460, 3, 36, 104
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "contribution-graphs"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    ids = {cid: date for date, cid in re.findall(
        r'data-date="([\d-]+)" id="(contribution-day-component-[\d-]+)"', html)}
    counts = {}
    for cid, text in re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', html):
        m = re.match(r"(\d+) contribution", text)
        if cid in ids:
            counts[dt.date.fromisoformat(ids[cid])] = int(m.group(1)) if m else 0
    return counts


def render(user, counts, end):
    start = START - dt.timedelta(days=(START.weekday() + 1) % 7)  # align to Sunday
    days = [START + dt.timedelta(days=i) for i in range((end - START).days + 1)]
    total = {d: counts.get(d, 0) for d in days}

    values = sorted(v for v in total.values() if v)
    q = [values[int(len(values) * p)] for p in (0.25, 0.5, 0.75)] if values else [1, 2, 3]

    def level(n):
        return 0 if n == 0 else 1 + sum(n > t for t in q)

    weeks = (end - start).days // 7 + 1
    cell = min((WIDTH - LEFT - 16) // weeks - GAP, 24)
    height = TOP + 7 * (cell + GAP) + 40

    grand = sum(total.values())
    active = sum(1 for v in total.values() if v)
    streak = longest = 0
    for d in days:
        streak = streak + 1 if total[d] else 0
        longest = max(longest, streak)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
        "<style>.c{opacity:0;animation:f .4s ease forwards}@keyframes f{to{opacity:1}}"
        ".t{fill:#e6edf3}.m{fill:#8b949e;font-size:10px}.s{fill:#38BDF8;font-weight:700;font-size:20px}.l{fill:#8b949e;font-size:10px}</style>",
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="12" fill="url(#bg)" stroke="#30363d"/>',
        f'<text x="{LEFT}" y="28" class="t" font-size="14" font-weight="600">@{user} · since {START:%B %Y}</text>',
    ]
    stats = [(f"{grand:,}", "contributions"), (f"{active}", "active days"), (f"{longest}", "longest streak")]
    for i, (num, label) in enumerate(stats):
        x = LEFT + i * 135
        out.append(f'<text x="{x}" y="56" class="s">{num}</text><text x="{x}" y="70" class="l">{label}</text>')

    for i, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="6" y="{TOP + i * (cell + GAP) + cell // 2 + 4}" class="m">{name}</text>')

    last_month = None
    for d in days:
        w, r = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = LEFT + w * (cell + GAP), TOP + r * (cell + GAP)
        if d.month != last_month and (r == 0 or d == START):
            out.append(f'<text x="{x}" y="{TOP - 6}" class="m">{MONTHS[d.month - 1]}</text>')
            last_month = d.month
        n = total[d]
        out.append(
            f'<rect class="c" style="animation-delay:{w * 0.03:.2f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{LEVELS[level(n)]}">'
            f"<title>{n} contributions on {d:%b %d, %Y}</title></rect>"
        )

    ly = TOP + 7 * (cell + GAP) + 14
    lx = WIDTH - 16 - 5 * 14 - 62
    out.append(f'<text x="{lx}" y="{ly + 9}" class="m">Less</text>')
    for i, c in enumerate(LEVELS):
        out.append(f'<rect x="{lx + 28 + i * 14}" y="{ly}" width="11" height="11" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 32 + 5 * 14}" y="{ly + 9}" class="m">More</text>')
    out.append("</svg>")
    return "\n".join(out), grand, active


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = {user: fetch(user) for user in USERS}
    end = max(max(c) for c in data.values())  # same end date for both graphs
    for user, name in USERS.items():
        svg, grand, active = render(user, data[user], end)
        path = os.path.join(OUT_DIR, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"wrote {path}: {grand} contributions, {active} active days")


if __name__ == "__main__":
    main()
