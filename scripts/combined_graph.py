"""Render one contribution heatmap that sums the activity of several GitHub accounts."""
import datetime as dt
import re
import sys
import urllib.request
from collections import defaultdict

USERS = ["Anujrastogi24", "Anujrastogi-1"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "combined-graph.svg"

CELL, GAP, LEFT, TOP = 13, 3, 40, 112
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "combined-graph"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    dates = dict(re.findall(r'data-date="([\d-]+)" id="(contribution-day-component-[\d-]+)"', html))
    dates = {v: k for k, v in dates.items()}
    counts = {}
    for cid, text in re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', html):
        m = re.match(r"(\d+) contribution", text)
        if cid in dates:
            counts[dates[cid]] = int(m.group(1)) if m else 0
    return counts


def main():
    total = defaultdict(int)
    for user in USERS:
        for day, n in fetch(user).items():
            total[day] += n
    days = sorted(total)
    start = dt.date.fromisoformat(days[0])
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday
    end = dt.date.fromisoformat(days[-1])

    values = sorted(v for v in total.values() if v)
    q = [values[int(len(values) * p)] for p in (0.25, 0.5, 0.75)] if values else [1, 2, 3]

    def level(n):
        if n == 0:
            return 0
        return 1 + sum(n > t for t in q)

    weeks = (end - start).days // 7 + 1
    width = LEFT + weeks * (CELL + GAP) + 20
    height = TOP + 7 * (CELL + GAP) + 50
    grand = sum(total.values())
    active = sum(1 for v in total.values() if v)
    best = max(total.values())

    # longest streak
    streak = longest = 0
    for d in days:
        streak = streak + 1 if total[d] else 0
        longest = max(longest, streak)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
        "<style>.c{opacity:0;animation:f .4s ease forwards}@keyframes f{to{opacity:1}}"
        ".t{fill:#e6edf3}.m{fill:#8b949e;font-size:11px}.s{fill:#38BDF8;font-weight:700;font-size:22px}.l{fill:#8b949e;font-size:11px}</style>",
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="14" fill="url(#bg)" stroke="#30363d"/>',
        f'<text x="{LEFT}" y="32" class="t" font-size="16" font-weight="600">Combined contributions · personal + work</text>',
    ]
    stats = [(f"{grand:,}", "total in the last year"), (f"{active}", "active days"),
             (f"{longest}", "longest streak (days)"), (f"{best}", "best day")]
    for i, (num, label) in enumerate(stats):
        x = LEFT + i * 170
        out.append(f'<text x="{x}" y="62" class="s">{num}</text><text x="{x}" y="77" class="l">{label}</text>')

    for i, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="6" y="{TOP + i * (CELL + GAP) + 10}" class="m">{name}</text>')

    last_month = None
    d = start
    while d <= end:
        w = (d - start).days // 7
        r = (d.weekday() + 1) % 7
        x, y = LEFT + w * (CELL + GAP), TOP + r * (CELL + GAP)
        if r == 0 and d.month != last_month:
            out.append(f'<text x="{x}" y="{TOP - 6}" class="m">{MONTHS[d.month - 1]}</text>')
            last_month = d.month
        n = total.get(d.isoformat(), 0)
        out.append(
            f'<rect class="c" style="animation-delay:{w * 0.02:.2f}s" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{LEVELS[level(n)]}">'
            f"<title>{n} contributions on {d:%b %d, %Y}</title></rect>"
        )
        d += dt.timedelta(days=1)

    ly = TOP + 7 * (CELL + GAP) + 20
    lx = width - 20 - 5 * (CELL + GAP) - 70
    out.append(f'<text x="{lx}" y="{ly + 10}" class="m">Less</text>')
    for i, c in enumerate(LEVELS):
        out.append(f'<rect x="{lx + 32 + i * (CELL + GAP)}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
    out.append(f'<text x="{lx + 36 + 5 * (CELL + GAP)}" y="{ly + 10}" class="m">More</text>')
    out.append(f'<text x="{LEFT}" y="{ly + 10}" class="m">@{"  +  @".join(USERS)}</text>')
    out.append("</svg>")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"wrote {OUT}: {grand} contributions, {active} active days")


if __name__ == "__main__":
    main()
