"""Generate the animated terminal header for the profile README.

Writes assets/terminal-dark.svg and assets/terminal-light.svg. Edit SESSION
below and re-run:  python3 scripts/build-terminal.py

The animation is SMIL rather than CSS: GitHub serves README images through an
<img> tag, and SMIL is the most reliable way to animate inside one across
browsers. It plays once per page load; only the cursor keeps blinking.
"""

from pathlib import Path
from xml.sax.saxutils import escape

# (command, [output lines]). An output line starting with "●" gets the status dot.
SESSION = [
    ("whoami", ["Eloi Chrysanthe — Mobile Full-Stack Developer · Kigali, Rwanda"]),
    ("cat stack.txt", ["React Native · Expo · Kotlin · Flutter", "Node.js · TypeScript · PostgreSQL · Redis"]),
    ("uptime", ["4+ yrs shipping · 17 apps released"]),
    ("status", ["● open to work → chrysanthe.dev"]),
]

# Mirrors the portfolio's @theme tokens (portfolio/app/globals.css).
THEMES = {
    "dark": dict(
        surface="#111318", bar="#181b22", line="#1f2330",
        ink="#e4e8f0", soft="#a3abbb", muted="#7e8698", accent="#00e5c8",
        online="#66da85", danger="#ff5f57", warn="#febc2e",
    ),
    # Accent and status darkened so both clear WCAG AA on the light surface.
    "light": dict(
        surface="#ffffff", bar="#f6f8fa", line="#d0d7de",
        ink="#1f2328", soft="#424a53", muted="#59636e", accent="#007a6b",
        online="#1a7f37", danger="#ff5f57", warn="#febc2e",
    ),
}

W = 820
PAD_X = 28
BAR_H = 40
TOP = BAR_H + 32
LINE_H = 24
FONT = 15
CHAR_W = FONT * 0.6  # advance of most monospace faces
TYPE_SPEED = 0.07  # seconds per character
PAUSE = 0.45  # between a command's output and the next prompt
FONT_STACK = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def build(t: dict) -> str:
    rows: list[str] = []
    clips: list[str] = []
    y = TOP
    clock = 0.6

    def reveal_at(begin: float) -> str:
        return (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.01s" '
            f'begin="{begin:.2f}s" fill="freeze"/>'
        )

    for i, (cmd, output) in enumerate(SESSION):
        # Prompt appears, then the command types out behind a growing clip.
        rows.append(
            f'<g opacity="0">{reveal_at(clock)}'
            f'<text x="{PAD_X}" y="{y}" fill="{t["accent"]}">$</text></g>'
        )
        cmd_x = PAD_X + CHAR_W * 2
        steps = ";".join(f"{CHAR_W * n:.1f}" for n in range(len(cmd) + 1))
        type_dur = TYPE_SPEED * len(cmd)
        clips.append(
            f'<clipPath id="c{i}"><rect x="{cmd_x}" y="{y - FONT}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" values="{steps};{W}" calcMode="discrete" '
            f'begin="{clock + 0.25:.2f}s" dur="{type_dur + 0.01:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        rows.append(
            f'<text x="{cmd_x}" y="{y}" fill="{t["ink"]}" clip-path="url(#c{i})">{escape(cmd)}</text>'
        )
        clock += 0.25 + type_dur + 0.2
        y += LINE_H

        out = [f'<g opacity="0">{reveal_at(clock)}']
        for line in output:
            if line.startswith("●"):
                out.append(
                    f'<circle cx="{PAD_X + 5}" cy="{y - 5}" r="5" fill="{t["online"]}">'
                    f'<animate attributeName="opacity" values="1;0.35;1" dur="2s" '
                    f'begin="{clock:.2f}s" repeatCount="indefinite"/></circle>'
                    f'<text x="{PAD_X + 18}" y="{y}" fill="{t["online"]}">{escape(line[1:].strip())}</text>'
                )
            else:
                out.append(f'<text x="{PAD_X}" y="{y}" fill="{t["soft"]}">{escape(line)}</text>')
            y += LINE_H
        out.append("</g>")
        rows.append("".join(out))
        clock += PAUSE
        y += 8  # breathing room between commands

    # Idle prompt with a blinking block cursor.
    rows.append(
        f'<g opacity="0">{reveal_at(clock)}'
        f'<text x="{PAD_X}" y="{y}" fill="{t["accent"]}">$</text>'
        f'<rect x="{PAD_X + CHAR_W * 2}" y="{y - FONT + 2}" width="{CHAR_W}" height="{FONT + 2}" fill="{t["accent"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
        f'begin="{clock:.2f}s" repeatCount="indefinite"/></rect></g>'
    )

    h = y + 24
    summary = " / ".join(f"$ {c}: {' '.join(o)}" for c, o in SESSION)
    dots = "".join(
        f'<circle cx="{22 + n * 20}" cy="{BAR_H / 2}" r="6" fill="{c}"/>'
        for n, c in enumerate((t["danger"], t["warn"], t["online"]))
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="title">
<title id="title">{escape(summary)}</title>
<defs>{"".join(clips)}<clipPath id="win"><rect width="{W}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{h}" fill="{t["surface"]}"/>
<rect width="{W}" height="{BAR_H}" fill="{t["bar"]}"/>
<line x1="0" y1="{BAR_H}" x2="{W}" y2="{BAR_H}" stroke="{t["line"]}"/>
{dots}
<text x="{W / 2}" y="{BAR_H / 2 + 4.5}" text-anchor="middle" fill="{t["muted"]}" font-family="{FONT_STACK}" font-size="13">chrysloi@github: ~</text>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="11.5" fill="none" stroke="{t["line"]}"/>
<g font-family="{FONT_STACK}" font-size="{FONT}" xml:space="preserve">
{chr(10).join(rows)}
</g>
</svg>
"""


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        (out_dir / f"terminal-{name}.svg").write_text(build(theme), encoding="utf-8")
        print(f"wrote assets/terminal-{name}.svg")
