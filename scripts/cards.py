"""Render the README's text sections as dark SVG cards, so the profile looks dark in any GitHub theme.

Run after editing any text below:  python scripts/cards.py
"""
import os
from html import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
W = 900
FONT = "Segoe UI,Helvetica,Arial,sans-serif"
MONO = "Fira Code,Consolas,Menlo,monospace"
BG = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#0d1117"/></linearGradient>'
      '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="#38BDF8"/><stop offset="1" stop-color="#A78BFA"/></linearGradient></defs>')


def card(height, body, width=W):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">'
            f"{BG}<rect x=\"0.5\" y=\"0.5\" width=\"{width - 1}\" height=\"{height - 1}\" rx=\"14\" fill=\"url(#bg)\" stroke=\"#30363d\"/>"
            f"{body}</svg>")


def text(x, y, s, size=14, fill="#c9d1d9", weight=400, family=FONT, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" font-family="{family}" {extra}>{escape(s)}</text>'


def chip(x, y, label, color):
    w = 14 + len(label) * 7.2
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-opacity="0.6"/>'
            + text(x + 7, y + 16, label, 12, color, 600)), w


def title(name, label):
    body = (f'<rect x="24" y="18" width="5" height="28" rx="2" fill="url(#accent)"/>'
            + text(42, 40, label, 22, "#e6edf3", 700)
            + f'<rect x="42" y="50" width="{len(label) * 12}" height="2" rx="1" fill="url(#accent)" opacity="0.5"/>')
    save(name, card(64, body))


def about():
    # left: code panel
    code = [
        [("class ", "#ff7b72"), ("AnujRastogi", "#d2a8ff"), (":", "#c9d1d9")],
        [("    role      = ", "#c9d1d9"), ('"Software Engineer & Data Analyst"', "#a5d6ff")],
        [("    company   = ", "#c9d1d9"), ('"IntelligenceX"', "#a5d6ff")],
        [("    portfolio = ", "#c9d1d9"), ('"anujrastogi.in"', "#a5d6ff")],
        [],
        [("    focus = [", "#c9d1d9")],
        [("        ", ""), ('"Django · REST APIs · Next.js"', "#a5d6ff"), (",", "#c9d1d9")],
        [("        ", ""), ('"API architecture & testing"', "#a5d6ff"), (",", "#c9d1d9")],
        [("        ", ""), ('"Production deploys on Vercel"', "#a5d6ff"), (",", "#c9d1d9")],
        [("        ", ""), ('"Power BI analytics"', "#a5d6ff"), (",", "#c9d1d9")],
        [("        ", ""), ('"AI-assisted workflows"', "#a5d6ff"), (",", "#c9d1d9")],
        [("    ]", "#c9d1d9")],
        [],
        [("    ", ""), ("def ", "#ff7b72"), ("motto", "#d2a8ff"), ("(self):", "#c9d1d9")],
        [("        ", ""), ("return ", "#ff7b72"), ('"Useful, reliable, measurable."', "#a5d6ff")],
    ]
    body = ['<rect x="20" y="20" width="500" height="360" rx="10" fill="#0b1220" stroke="#21262d"/>']
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        body.append(f'<circle cx="{40 + i * 18}" cy="38" r="5" fill="{c}"/>')
    body.append(text(100, 42, "about_me.py", 12, "#8b949e", 400, MONO))
    for n, line in enumerate(code):
        y = 74 + n * 20
        body.append(text(36, y, str(n + 1).rjust(2), 12, "#484f58", 400, MONO))
        spans = "".join(f'<tspan fill="{c or "#c9d1d9"}">{escape(s)}</tspan>' for s, c in line)
        body.append(f'<text x="64" y="{y}" font-size="13" font-family="{MONO}" xml:space="preserve">{spans}</text>')

    # right: highlights
    points = [
        ("#38BDF8", "Software Engineer", "at IntelligenceX"),
        ("#A78BFA", "Shipping SaaS platforms", "end to end, frontend to backend"),
        ("#34D399", "Deployed company projects", "to production on Vercel"),
        ("#F2C811", "Data into decisions", "with Power BI dashboards"),
        ("#F472B6", "AI-powered developer tools", "exploring and building"),
        ("#FB923C", "Always learning,", "always shipping"),
    ]
    for i, (color, head, sub) in enumerate(points):
        y = 52 + i * 56
        body.append(f'<rect x="548" y="{y - 16}" width="4" height="40" rx="2" fill="{color}"/>')
        body.append(text(564, y, head, 15, "#e6edf3", 600))
        body.append(text(564, y + 20, sub, 13, "#8b949e"))
    save("about.svg", card(400, "".join(body)))


def wrap(s, limit):
    lines, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + 1 > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def project(name, heading, badges, description, stack):
    body = [text(32, 44, heading, 22, "#e6edf3", 700)]
    x = 32 + len(heading) * 12.5 + 12
    for label, color in badges:
        c, w = chip(x, 26, label, color)
        body.append(c)
        x += w + 8
    lines = wrap(description, 108)
    for i, line in enumerate(lines):
        body.append(text(32, 78 + i * 21, line, 14, "#c9d1d9"))
    y = 78 + len(lines) * 21 + 6
    x = 32
    for label, color in stack:
        c, w = chip(x, y, label, color)
        body.append(c)
        x += w + 8
    height = y + 44
    body.insert(0, f'<rect x="14" y="20" width="4" height="{height - 40}" rx="2" fill="url(#accent)"/>')
    save(name, card(height, "".join(body)))


def save(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote", name)


if __name__ == "__main__":
    title("title-about.svg", "About Me")
    title("title-work.svg", "Featured Work")
    title("title-activity.svg", "GitHub Activity · Work + Personal")
    about()
    project(
        "project-rudra.svg", "Rudra Analyzer",
        [("● Live · rudraanalyzer.in", "#22C55E")],
        "Automated website testing platform that scores any URL across 7 categories (Performance, SEO, "
        "Responsive, Accessibility, Security/SSL, API health, Functional/UI), with a full-site crawler, "
        "real-device responsive testing, PDF reports, a 7-language UI and Stripe / Razorpay subscriptions.",
        [("Next.js", "#e6edf3"), ("Django REST", "#34D399"), ("Playwright", "#22C55E"), ("Docker", "#38BDF8"), ("Vercel", "#e6edf3")],
    )
    project(
        "project-policymitra.svg", "Policy Mitra AIOS",
        [("● Live · policymitra.online", "#22C55E"), ("Client Project", "#A78BFA")],
        "An intelligent operating system for insurance advisors: manage customers, families, policies and "
        "renewals in one platform built for advisors, brokers, enterprises and families.",
        [("InsurTech", "#A78BFA"), ("Advisor CRM", "#38BDF8"), ("Renewals tracking", "#34D399")],
    )
    save("activity-note.svg", card(64, text(24, 30, "Two accounts: @Anujrastogi-1 for day-to-day work at IntelligenceX (mostly private repos)", 14, "#c9d1d9")
                                   + text(24, 50, "and @Anujrastogi24 for personal projects. Numbers include private contributions.", 14, "#8b949e")))
