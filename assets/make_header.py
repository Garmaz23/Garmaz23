"""Generate the profile header: an ISO-style technical drawing sheet.

Run:  python assets/make_header.py
Writes assets/header-light.svg and assets/header-dark.svg.
Edit the TEXT dict below to change what the title block and notes say.
"""

from pathlib import Path

TEXT = {
    "name": "IVAN GARMAZ",
    "subtitle": "Mechanical Engineer · IT & Security Consultant",
    "drawn": "I. GARMAZ",
    "status": "IN SERVICE",
    "scale": "1:1",
    "material": "MECH. ENG. + CYBERSECURITY",
    "dwg_no": "VLX-GZ-001",
    "rev": "C",
    "firm": "VELAXIS ENGINEERING",
    "origin": "FSB ZAGREB · HR",
    "notes": [
        "GENERAL TOLERANCES ISO 2768-m",
        "ALL UNUSED PORTS CLOSED",
        "HARDENED PER NIS2, MONITORED 24/7",
        "BREAK SHARP EDGES, PATCH MONTHLY",
        "DO NOT SCALE DRAWING, ASK FIRST",
    ],
}

THEMES = {
    "light": {"bg": "#ffffff", "ink": "#24292f", "thin": "#6e7781", "dim": "#0a66c2", "hatch": "#8c959f"},
    "dark": {"bg": "#0d1117", "ink": "#d1d9e0", "thin": "#7d8590", "dim": "#58a6ff", "hatch": "#565f69"},
}

W, H = 1000, 420
FONT = "ui-monospace, SFMono-Regular, 'DejaVu Sans Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(t):
    o = []
    add = o.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
        f'role="img" aria-label="{esc(TEXT["name"])} - {esc(TEXT["subtitle"])}">')
    add(f"<title>{esc(TEXT['name'])} - {esc(TEXT['subtitle'])}</title>")
    add("<style>")
    add(f"""
      text {{ font-family: {FONT}; fill: {t['ink']}; }}
      .o  {{ fill: none; stroke: {t['ink']}; stroke-width: 2.2; stroke-linejoin: round; stroke-linecap: round; }}
      .f  {{ fill: none; stroke: {t['ink']}; stroke-width: 1.2; }}
      .th {{ fill: none; stroke: {t['thin']}; stroke-width: 0.9; }}
      .cl {{ fill: none; stroke: {t['thin']}; stroke-width: 0.9; stroke-dasharray: 18 4 3 4; }}
      .dm {{ fill: none; stroke: {t['dim']}; stroke-width: 0.9; }}
      .dt {{ fill: {t['dim']}; font-size: 14px; }}
      .ah {{ fill: {t['dim']}; }}
      .lb {{ font-size: 9px; fill: {t['thin']}; letter-spacing: .5px; }}
      .vl {{ font-size: 13px; }}
      .nt {{ font-size: 12.5px; }}
      .zn {{ font-size: 11px; fill: {t['thin']}; }}

      .draw {{ stroke-dasharray: 1; stroke-dashoffset: 0; animation: draw 1.6s ease-out both; }}
      .fade {{ animation: fade .9s ease-out both; }}
      @keyframes draw {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
      @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      @media (prefers-reduced-motion: reduce) {{ .draw, .fade {{ animation: none; }} }}
    """)
    add("</style>")

    add("<defs>")
    add(f'<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="7" stroke="{t["hatch"]}" stroke-width="1"/></pattern>')
    add("</defs>")

    # Sheet
    add(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    fx0, fy0, fx1, fy1 = 30, 30, W - 30, H - 30
    add(f'<rect x="12" y="12" width="{W-24}" height="{H-24}" class="th"/>')
    add(f'<rect x="{fx0}" y="{fy0}" width="{fx1-fx0}" height="{fy1-fy0}" class="o" pathLength="1" '
        f'style="stroke-dasharray:1;animation:draw 1.4s ease-out both"/>')

    # Zone markers
    cols, rows = 8, 3
    cw, rh = (fx1 - fx0) / cols, (fy1 - fy0) / rows
    zones = []
    for i in range(cols):
        cx = fx0 + cw * (i + .5)
        zones.append(f'<text x="{cx:.0f}" y="25" class="zn" text-anchor="middle">{i+1}</text>')
        zones.append(f'<text x="{cx:.0f}" y="{H-16}" class="zn" text-anchor="middle">{i+1}</text>')
        if i:
            x = fx0 + cw * i
            zones.append(f'<line x1="{x:.0f}" y1="12" x2="{x:.0f}" y2="{fy0}" class="th"/>')
            zones.append(f'<line x1="{x:.0f}" y1="{fy1}" x2="{x:.0f}" y2="{H-12}" class="th"/>')
    for j in range(rows):
        cy = fy0 + rh * (j + .5) + 4
        letter = "ABC"[j]
        zones.append(f'<text x="21" y="{cy:.0f}" class="zn" text-anchor="middle">{letter}</text>')
        zones.append(f'<text x="{W-21}" y="{cy:.0f}" class="zn" text-anchor="middle">{letter}</text>')
        if j:
            y = fy0 + rh * j
            zones.append(f'<line x1="12" y1="{y:.0f}" x2="{fx0}" y2="{y:.0f}" class="th"/>')
            zones.append(f'<line x1="{fx1}" y1="{y:.0f}" x2="{W-12}" y2="{y:.0f}" class="th"/>')
    # centring marks
    zones.append(f'<line x1="{W/2}" y1="12" x2="{W/2}" y2="44" class="f"/>')
    zones.append(f'<line x1="{W/2}" y1="{H-44}" x2="{W/2}" y2="{H-12}" class="f"/>')
    zones.append(f'<line x1="12" y1="{H/2}" x2="44" y2="{H/2}" class="f"/>')
    zones.append(f'<line x1="{W-44}" y1="{H/2}" x2="{W-12}" y2="{H/2}" class="f"/>')
    add(f'<g class="fade" style="animation-delay:.3s">{"".join(zones)}</g>')

    # ---------- Part: front view (shield plate with keyhole) ----------
    shield = "M150,92 H350 V190 C350,258 302,298 250,326 C198,298 150,258 150,190 Z"
    chamfer = "M164,106 H336 V190 C336,249 294,284 250,309 C206,284 164,249 164,190 Z"
    keyhole = "M242,205.5 L236,250 H264 L258,205.5 A22,22 0 1 0 242,205.5 Z"
    add(f'<path d="{shield}" class="o draw" pathLength="1" style="animation-delay:.6s"/>')
    add(f'<path d="{chamfer}" class="f draw" pathLength="1" style="animation-delay:1.0s"/>')
    add(f'<path d="{keyhole}" class="o draw" pathLength="1" style="animation-delay:1.3s"/>')

    # ---------- Part: section A-A ----------
    sx0, sx1 = 400, 430
    sec = []
    # solid regions hatched (hole spans y 163..250)
    for y0, y1 in ((92, 163), (250, 326)):
        sec.append(f'<rect x="{sx0}" y="{y0}" width="{sx1-sx0}" height="{y1-y0}" fill="url(#hatch)"/>')
    add(f'<g class="fade" style="animation-delay:2.2s">{"".join(sec)}</g>')
    sec_outline = (f"M{sx0+6},92 H{sx1} V163 H{sx0} V98 Z "
                   f"M{sx0},250 H{sx1} V326 H{sx0+6} L{sx0},320 Z")
    add(f'<path d="{sec_outline}" class="o draw" pathLength="1" style="animation-delay:1.6s"/>')
    add(f'<line x1="{sx0}" y1="163" x2="{sx1}" y2="163" class="f fade" style="animation-delay:2s"/>')

    # ---------- Centre lines and section cut ----------
    cl = [
        '<line x1="250" y1="76" x2="250" y2="342" class="cl"/>',
        '<line x1="214" y1="185" x2="286" y2="185" class="cl"/>',
        f'<line x1="415" y1="80" x2="415" y2="340" class="cl"/>',
        f'<line x1="386" y1="185" x2="444" y2="185" class="cl"/>',
        # projection line front -> section
        f'<line x1="356" y1="185" x2="382" y2="185" class="th" stroke-dasharray="2 4"/>',
    ]
    add(f'<g class="fade" style="animation-delay:1.8s">{"".join(cl)}</g>')

    # section cut markers on front view (cut along the vertical centre line)
    cut = [
        f'<line x1="250" y1="62" x2="250" y2="76" stroke="{t["ink"]}" stroke-width="3"/>',
        f'<line x1="250" y1="342" x2="250" y2="356" stroke="{t["ink"]}" stroke-width="3"/>',
        f'<path d="M250,66 h18" class="f"/><path d="M268,66 l-7,-3.5 v7 z" fill="{t["ink"]}"/>',
        f'<path d="M250,352 h18" class="f"/><path d="M268,352 l-7,-3.5 v7 z" fill="{t["ink"]}"/>',
        f'<text x="276" y="70" class="vl" font-weight="700">A</text>',
        f'<text x="276" y="356" class="vl" font-weight="700">A</text>',
        f'<text x="415" y="70" class="vl" font-weight="700" text-anchor="middle">A–A</text>',
    ]
    add(f'<g class="fade" style="animation-delay:2s">{"".join(cut)}</g>')

    # ---------- Dimensions ----------
    def arrow(x, y, ang):
        return (f'<path d="M0,0 L-9,-3 L-9,3 Z" class="ah" '
                f'transform="translate({x},{y}) rotate({ang})"/>')

    d = []
    # overall width 200 (top)
    d += ['<line x1="150" y1="88" x2="150" y2="44" class="dm"/>',
          '<line x1="350" y1="88" x2="350" y2="44" class="dm"/>',
          '<line x1="150" y1="50" x2="350" y2="50" class="dm"/>',
          arrow(150, 50, 180), arrow(350, 50, 0),
          '<text x="250" y="45" class="dt" text-anchor="middle">200</text>']
    # overall height 234 (left)
    d += ['<line x1="146" y1="92" x2="96" y2="92" class="dm"/>',
          '<line x1="246" y1="326" x2="96" y2="326" class="dm"/>',
          '<line x1="102" y1="92" x2="102" y2="326" class="dm"/>',
          arrow(102, 92, 270), arrow(102, 326, 90),
          '<text x="0" y="0" class="dt" text-anchor="middle" transform="translate(96,209) rotate(-90)">234</text>']
    # keyhole diameter (leader)
    d += ['<line x1="266" y1="170" x2="356" y2="140" class="dm"/>',
          '<line x1="356" y1="140" x2="392" y2="140" class="dm"/>',
          arrow(266, 170, 161.6),
          '<text x="358" y="135" class="dt">Ø44</text>']
    # slot width 28
    d += ['<line x1="236" y1="254" x2="236" y2="276" class="dm"/>',
          '<line x1="264" y1="254" x2="264" y2="276" class="dm"/>',
          '<line x1="214" y1="270" x2="236" y2="270" class="dm"/>', arrow(236, 270, 0),
          '<line x1="264" y1="270" x2="286" y2="270" class="dm"/>', arrow(264, 270, 180),
          '<text x="250" y="292" class="dt" text-anchor="middle">28</text>']
    # thickness 30 (section, bottom)
    d += [f'<line x1="{sx0}" y1="330" x2="{sx0}" y2="372" class="dm"/>',
          f'<line x1="{sx1}" y1="330" x2="{sx1}" y2="372" class="dm"/>',
          f'<line x1="{sx0-26}" y1="366" x2="{sx0}" y2="366" class="dm"/>', arrow(sx0, 366, 0),
          f'<line x1="{sx1}" y1="366" x2="{sx1+26}" y2="366" class="dm"/>', arrow(sx1, 366, 180),
          f'<text x="{sx1+32}" y="370" class="dt">30</text>']
    # chamfer callout on section
    d += [f'<line x1="{sx0+3}" y1="95" x2="{sx1+40}" y2="78" class="dm"/>',
          f'<line x1="{sx1+40}" y1="78" x2="{sx1+112}" y2="78" class="dm"/>',
          f'<text x="{sx1+44}" y="73" class="dt">0.5×45°</text>']
    add(f'<g class="fade" style="animation-delay:2.4s">{"".join(d)}</g>')

    # ---------- Surface finish + flatness frame ----------
    gx, gy = 470, 230
    g = [
        # roughness check mark
        f'<path d="M{gx},{gy} l8,14 l18,-32 h38" class="f"/>',
        f'<line x1="{gx-4}" y1="{gy}" x2="{gx+16}" y2="{gy}" class="f"/>',
        f'<text x="{gx+30}" y="{gy-22}" class="vl">Ra 0.8</text>',
        f'<line x1="{gx}" y1="{gy+14}" x2="{sx1+2}" y2="{gy+14}" class="th"/>',
        # flatness feature control frame
        f'<rect x="{gx}" y="{gy+36}" width="96" height="24" class="f"/>',
        f'<line x1="{gx+28}" y1="{gy+36}" x2="{gx+28}" y2="{gy+60}" class="f"/>',
        f'<path d="M{gx+7},{gy+53} l4,-10 h12 l-4,10 z" class="f"/>',
        f'<text x="{gx+36}" y="{gy+53}" class="vl">0.02</text>',
        f'<line x1="{gx}" y1="{gy+48}" x2="{sx1+2}" y2="{gy+48}" class="th"/>',
    ]
    add(f'<g class="fade" style="animation-delay:2.7s">{"".join(g)}</g>')

    # ---------- Notes ----------
    nx, ny = 600, 76
    n = [f'<text x="{nx}" y="{ny}" class="vl" font-weight="700">NOTES</text>']
    for i, line in enumerate(TEXT["notes"]):
        n.append(f'<text x="{nx}" y="{ny + 24 + i*20}" class="nt">{i+1}. {esc(line)}</text>')
    add(f'<g class="fade" style="animation-delay:2.9s">{"".join(n)}</g>')

    # ---------- Title block ----------
    bx0, by0, bx1, by1 = 590, 218, fx1, fy1
    tb = [f'<rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="{by1-by0}" class="o"/>']
    r1, r2, r3 = by0 + 34, by0 + 102, by0 + 136

    def cell(x, y, label, value, size=13, bold=False):
        w = ' font-weight="700"' if bold else ""
        return (f'<text x="{x+6}" y="{y+11}" class="lb">{esc(label)}</text>'
                f'<text x="{x+6}" y="{y+27}" class="vl" style="font-size:{size}px"{w}>{esc(value)}</text>')

    # row 1: drawn | status | scale | projection symbol
    c1 = [bx0, bx0 + 95, bx0 + 200, bx0 + 262, bx1]
    tb += [f'<line x1="{bx0}" y1="{r1}" x2="{bx1}" y2="{r1}" class="f"/>']
    tb += [f'<line x1="{x}" y1="{by0}" x2="{x}" y2="{r1}" class="f"/>' for x in c1[1:-1]]
    tb += [cell(c1[0], by0, "DRAWN", TEXT["drawn"]),
           cell(c1[1], by0, "STATUS", TEXT["status"]),
           cell(c1[2], by0, "SCALE", TEXT["scale"])]
    # first-angle projection symbol (ISO E)
    px, py = c1[3] + 58, by0 + 17
    tb += [f'<path d="M{px-30},{py-8} L{px-6},{py-12} V{py+12} L{px-30},{py+8} Z" class="f"/>',
           f'<circle cx="{px+18}" cy="{py}" r="12" class="f"/>',
           f'<circle cx="{px+18}" cy="{py}" r="7" class="f"/>',
           f'<line x1="{px-34}" y1="{py}" x2="{px+34}" y2="{py}" class="cl" style="stroke-dasharray:6 2 1 2"/>']

    # row 2: big title
    tb += [f'<line x1="{bx0}" y1="{r2}" x2="{bx1}" y2="{r2}" class="f"/>',
           f'<text x="{bx0+8}" y="{r1+12}" class="lb">TITLE</text>',
           f'<text x="{bx0+12}" y="{r1+42}" style="font-size:30px;letter-spacing:3px" font-weight="700">{esc(TEXT["name"])}</text>',
           f'<text x="{bx0+12}" y="{r1+60}" style="font-size:12.5px;fill:{t["dim"]}">{esc(TEXT["subtitle"])}</text>']

    # row 3: firm | origin
    c3 = [bx0, bx0 + 200, bx1]
    tb += [f'<line x1="{bx0}" y1="{r3}" x2="{bx1}" y2="{r3}" class="f"/>',
           f'<line x1="{c3[1]}" y1="{r2}" x2="{c3[1]}" y2="{r3}" class="f"/>',
           cell(c3[0], r2, "FIRM", TEXT["firm"]),
           cell(c3[1], r2, "ORIGIN", TEXT["origin"])]

    # row 4: material | dwg no | rev
    c4 = [bx0, bx0 + 200, bx0 + 310, bx1]
    tb += [f'<line x1="{x}" y1="{r3}" x2="{x}" y2="{by1}" class="f"/>' for x in c4[1:-1]]
    tb += [cell(c4[0], r3, "MATERIAL", TEXT["material"], size=11.5),
           cell(c4[1], r3, "DWG NO.", TEXT["dwg_no"]),
           cell(c4[2], r3, "REV", TEXT["rev"], bold=True)]
    add(f'<g class="fade" style="animation-delay:3.1s">{"".join(tb)}</g>')

    add("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent
    for name, theme in THEMES.items():
        (out / f"header-{name}.svg").write_text(build(theme), encoding="utf-8")
        print(f"wrote header-{name}.svg")
