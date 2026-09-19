"""Builds dossier.svg: background image + dark readable panel + dossier table (native SVG text, no effects).
Run locally:  python build_dossier.py  ->  commit dossier.svg, embed with <img src="dossier.svg" width="100%">
"""
import base64, urllib.request
from xml.sax.saxutils import escape

BG_URL = "https://static.wikia.nocookie.net/zenless-zone-zero/images/5/59/Mindscape_Astra_Yao_Full.png/revision/latest/scale-to-width-down/1000?cb=20250122025651"

W, H = 1000, 540
PANEL_OPACITY = 0.72   # higher = darker panel, more readable; lower = more image shows
ACCENT = "#d9ff00"

ROWS = [
    ("PROXY NAME", [("Yash Verma", True), ("  ·  ", False), ("CodeSlavve", False)]),
    ("AFFILIATION", [("Bharati Vidyapeeth College of Engineering, Navi Mumbai", False)]),
    ("CLASS", [("3rd Year Engineering Student", False)]),
    ("SPECIALTY", [("Machine Learning  ·  AI", False)]),
    ("ACTIVE COMMISSION", [("Landing an internship", False)]),
    ("STAMINA SOURCE", [("ZZZ + late-night music", False)]),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()

def build(bg_bytes):
    bg_b64 = base64.b64encode(bg_bytes).decode()
    px, pw = 60, 880                 # panel x / width
    tx, tw = 100, 800                # table x / width
    label_w = 230
    top, head_h, row_h = 90, 44, 52

    out = []
    # header row
    out.append(f'<rect x="{tx}" y="{top}" width="{tw}" height="{head_h}" fill="{ACCENT}"/>')
    ty = top + head_h / 2 + 5
    out.append(f'<text x="{tx+20}" y="{ty}" class="mono" font-size="15" font-weight="700" fill="#000">FIELD</text>')
    out.append(f'<text x="{tx+label_w+20}" y="{ty}" class="mono" font-size="15" font-weight="700" fill="#000">ENTRY</text>')

    y = top + head_h
    for i, (label, parts) in enumerate(ROWS):
        fill = "#ffffff" if i % 2 == 0 else "#000000"
        op = 0.06 if i % 2 == 0 else 0.18
        out.append(f'<rect x="{tx}" y="{y}" width="{tw}" height="{row_h}" fill="{fill}" fill-opacity="{op}"/>')
        out.append(f'<line x1="{tx}" y1="{y+row_h}" x2="{tx+tw}" y2="{y+row_h}" stroke="{ACCENT}" stroke-opacity="0.25"/>')
        cy = y + row_h / 2 + 5
        out.append(f'<text x="{tx+20}" y="{cy}" class="mono" font-size="15" fill="{ACCENT}">{escape(label)}</text>')
        spans = "".join(
            f'<tspan font-weight="{700 if b else 400}">{escape(t)}</tspan>'.replace("  ", "&#160;&#160;")
            for t, b in parts
        )
        out.append(f'<text x="{tx+label_w+20}" y="{cy}" class="sans" font-size="17" fill="#000000">{spans}</text>')
        y += row_h
    # column divider + outer border
    table_h = head_h + row_h * len(ROWS)
    out.append(f'<line x1="{tx+label_w}" y1="{top+head_h}" x2="{tx+label_w}" y2="{top+table_h}" stroke="{ACCENT}" stroke-opacity="0.25"/>')
    out.append(f'<rect x="{tx}" y="{top}" width="{tw}" height="{table_h}" fill="none" stroke="{ACCENT}" stroke-opacity="0.6"/>')

    panel_h = top + table_h + 30 - 20
    block_top = 44                       # top of the title text
    block_bottom = top + table_h         # bottom of the table
    dy = (H - (block_bottom - block_top)) / 2 - block_top
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>PROXY DOSSIER</title>
  <style>
    .mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
    .sans {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  </style>
  <defs><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath></defs>
  <g clip-path="url(#c)">
    <image href="data:image/png;base64,{bg_b64}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
    <g transform="translate(0,{dy})">
      <text x="{tx}" y="64" class="mono" font-size="26" font-weight="700" fill="{ACCENT}" letter-spacing="3">PROXY DOSSIER</text>      {"".join(out)}
    </g>
  </g>
</svg>'''

if __name__ == "__main__":
    svg = build(fetch(BG_URL))
    open("dossier.svg", "w", encoding="utf-8").write(svg)
    print(f"dossier.svg written ({len(svg)/1024:.0f} KB)")