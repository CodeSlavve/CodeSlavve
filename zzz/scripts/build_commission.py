"""Builds board.svg: Promeia background + commission board, kept to the left so the face stays visible.
Run locally:  python build_board.py  ->  commit board.svg, embed with <img src="assets/board.svg" width="100%">
"""
import base64, textwrap, urllib.request
from xml.sax.saxutils import escape

BG_URL = "https://static.wikia.nocookie.net/zenless-zone-zero/images/7/75/Mindscape_Promeia_Full.png/revision/latest/scale-to-width-down/1000?cb=20260506091557"

W, H = 1000, 470
ACCENT = "#d9ff00"

TX, TW = 40, 600               # table x / width (left side only -> face stays clear)
COL_W = [160, 250, 190]        # sum must equal TW
HEADERS = ["COMMISSION", "BRIEFING", "TAGS"]
PAD = 14
WRAP = [15, 30]                # max chars per line: commission name, briefing
ROW_STYLE = (("#ffffff", 0.06), ("#000000", 0.18))   # (fill, opacity) for even / odd rows

ROWS = [
    ("Samadhan Setu",
     "SIH hackathon run with Team Binary Beast. I built the AI layer of the pipeline.",
     ["AI", "Hackathon", "SIH"]),
    ("Kaushalya",
     "Peer-to-peer skill-sharing and mentorship platform for creative and performing arts.",
     ["Platform", "Mentorship", "Arts"]),
    ("Next-Word Prediction LSTM",
     "Deployable LSTM that predicts the next word, from training to hosting.",
     ["LSTM", "NLP", "Deep Learning"]),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()

def text_cell(x, y, row_h, text, wrap, cls, size, weight, fill):
    lines = textwrap.wrap(text, wrap) or [""]
    lh = size + 5
    y0 = y + (row_h - len(lines) * lh) / 2 + size
    spans = "".join(f'<tspan x="{x}" y="{y0 + k*lh:.1f}">{escape(l)}</tspan>' for k, l in enumerate(lines))
    stroke = 'stroke="#000" stroke-width="1"' if fill == ACCENT else 'stroke="#fff" stroke-width="1"'
    return f'<text class="{cls}" font-size="{size}" font-weight="{weight}" fill="{fill}" {stroke} paint-order="stroke" stroke-linejoin="round">{spans}</text>'

def chip_cell(x, y, row_h, tags, max_w):
    ch, gap, fs = 22, 6, 12
    lines, cur, cur_w = [], [], 0
    for t in tags:
        w = len(t) * 6.8 + 16
        if cur and cur_w + gap + w > max_w:
            lines.append(cur); cur, cur_w = [], 0
        cur.append((t, w)); cur_w += w + (gap if len(cur) > 1 else 0)
    if cur: lines.append(cur)
    total = len(lines) * ch + (len(lines) - 1) * gap
    ty = y + (row_h - total) / 2
    out = []
    for line in lines:
        cx = x
        for t, w in line:
            out.append(f'<rect x="{cx:.1f}" y="{ty:.1f}" width="{w:.1f}" height="{ch}" rx="{ch/2}" fill="#000" fill-opacity="0.88"/>')
            out.append(f'<text x="{cx + w/2:.1f}" y="{ty + 15:.1f}" text-anchor="middle" class="mono" font-size="{fs}" font-weight="700" fill="{ACCENT}">{escape(t)}</text>')
            cx += w + gap
        ty += ch + gap
    return "".join(out)

def build(bg_bytes):
    bg_b64 = base64.b64encode(bg_bytes).decode()
    top, head_h, row_h = 90, 44, 84
    xs = [TX]
    for w in COL_W[:-1]:
        xs.append(xs[-1] + w)

    out = [f'<rect x="{TX}" y="{top}" width="{TW}" height="{head_h}" fill="{ACCENT}"/>']
    hy = top + head_h / 2 + 5
    for x, h in zip(xs, HEADERS):
        out.append(f'<text x="{x+PAD}" y="{hy}" class="mono" font-size="15" font-weight="700" fill="#000">{h}</text>')

    y = top + head_h
    for i, (name, brief, tags) in enumerate(ROWS):
        out.append(f'<rect x="{TX}" y="{y}" width="{TW}" height="{row_h}" fill="{ROW_STYLE[i % 2][0]}" fill-opacity="{ROW_STYLE[i % 2][1]}"/>')
        out.append(f'<line x1="{TX}" y1="{y+row_h}" x2="{TX+TW}" y2="{y+row_h}" stroke="{ACCENT}" stroke-opacity="0.25"/>')
        out.append(text_cell(xs[0] + PAD, y, row_h, name, WRAP[0], "mono", 14, 700, ACCENT))
        out.append(text_cell(xs[1] + PAD, y, row_h, brief, WRAP[1], "sans", 14, 400, "#000"))
        tag_text = " ".join(t.replace(" ", "\u00a0") + ("\u00a0·" if k < len(tags) - 1 else "") for k, t in enumerate(tags))
        out.append(text_cell(xs[2] + PAD, y, row_h, tag_text, 22, "sans", 14, 400, "#000"))
        y += row_h

    table_h = head_h + row_h * len(ROWS)
    out.append(f'<rect x="{TX}" y="{top}" width="{TW}" height="{table_h}" fill="none" stroke="{ACCENT}" stroke-width="2"/>')

    block_top, block_bottom = 44, top + table_h
    dy = (H - (block_bottom - block_top)) / 2 - block_top

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>COMMISSION BOARD</title>
  <style>
    .mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
    .sans {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  </style>
  <defs><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath></defs>
  <g clip-path="url(#c)">
    <image href="data:image/png;base64,{bg_b64}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
    <g transform="translate(0,{dy})">
      <text x="{TX}" y="64" class="mono" font-size="26" font-weight="700" fill="{ACCENT}" stroke="#000" stroke-width="5" paint-order="stroke" stroke-linejoin="round" letter-spacing="3">COMMISSION BOARD</text>
      {"".join(out)}
    </g>
  </g>
</svg>'''

if __name__ == "__main__":
    svg = build(fetch(BG_URL))
    open("board.svg", "w", encoding="utf-8").write(svg)
    print(f"board.svg written ({len(svg)/1024:.0f} KB)")