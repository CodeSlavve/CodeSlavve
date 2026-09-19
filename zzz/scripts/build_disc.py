"""Builds discs.svg: Ellen Joe art on the right, heading + skill icons arranged in the blank space on the left.
Run locally:  python build_discs.py  ->  commit discs.svg, embed with <img src="assets/discs.svg" width="100%">
"""
import base64, urllib.request, re

BG_URL = "https://static.wikia.nocookie.net/zenless-zone-zero/images/c/c5/Mindscape_Ellen_Joe_Full.png/revision/latest/scale-to-width-down/1000?cb=20240711034944"
ICONS = ["py", "tensorflow", "pytorch", "sklearn", "java", "git", "github", "vscode"]   # skillicons.dev ids
EXTRA = {"pandas": "e70488", "numpy": "4dabcf", "jupyter": "f37626"}   # Simple Icons slug: glyph color (hex)

W, H = 1000, 460
ACCENT = "#d9ff00"
HEADING = "DRIVE DISC SLOTS"

GRID_X = 60          # left edge of heading + icon grid
COLS = 4             # icons per row
SIZE, GAP = 72, 16   # icon size / spacing
IMG_ALIGN = "xMaxYMid slice"   # keeps the character on the right; try xMidYMid slice if the crop is off

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()

def data_uri(b, mime):
    return f"data:{mime};base64," + base64.b64encode(b).decode()

def build(bg_bytes, icon_bytes):
    rows = -(-len(icon_bytes) // COLS)
    grid_h = rows * SIZE + (rows - 1) * GAP
    head_h, head_gap = 30, 26
    block_h = head_h + head_gap + grid_h
    top = (H - block_h) / 2

    parts = [f'<text x="{GRID_X}" y="{top + 26:.1f}" class="mono" font-size="26" font-weight="700" fill="{ACCENT}" '
             f'stroke="#000" stroke-width="5" paint-order="stroke" stroke-linejoin="round" letter-spacing="3">{HEADING}</text>']
    gy = top + head_h + head_gap
    for n, ib in enumerate(icon_bytes):
        r, c = divmod(n, COLS)
        x = GRID_X + c * (SIZE + GAP)
        y = gy + r * (SIZE + GAP)
        parts.append(f'<image href="{data_uri(ib, "image/svg+xml")}" x="{x}" y="{y:.1f}" width="{SIZE}" height="{SIZE}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{HEADING}</title>
  <style>.mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}</style>
  <defs><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath></defs>
  <g clip-path="url(#c)">
    <image href="{data_uri(bg_bytes, "image/png")}" width="{W}" height="{H}" preserveAspectRatio="{IMG_ALIGN}"/>
    {"".join(parts)}
  </g>
</svg>'''

def tile(glyph_svg, color):
    """Puts a Simple Icons glyph on a dark rounded tile, like the skillicons ones."""
    paths = "".join(p.decode() for p in re.findall(rb"<path[^>]*/>", glyph_svg))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
            f'<rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<svg x="56" y="56" width="144" height="144" viewBox="0 0 24 24" fill="#{color}">{paths}</svg></svg>').encode()

if __name__ == "__main__":
    icons = [fetch(f"https://skillicons.dev/icons?i={i}") for i in ICONS]
    icons += [tile(fetch(f"https://cdn.simpleicons.org/{s}/{c}"), c) for s, c in EXTRA.items()]
    svg = build(fetch(BG_URL), icons)
    open("discs.svg", "w", encoding="utf-8").write(svg)
    print(f"discs.svg written ({len(svg)/1024:.0f} KB)")