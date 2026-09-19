"""Builds footer.svg: Remielle Dan art with a looping typing effect drawn on top of it.
Run locally:  python build_footer.py  ->  commit footer.svg, embed with <img src="assets/footer.svg" width="100%">
"""
import base64, urllib.request
from xml.sax.saxutils import escape

BG_URL = "https://static.wikia.nocookie.net/zenless-zone-zero/images/1/1b/Mindscape_Remielle_Dan_Full.png/revision/latest/scale-to-width-down/1000?cb=20260731001807"

LINES = ['"If it\'s running, let it run."', "> END OF TRANSMISSION", "> SEE YOU IN THE NEXT HOLLOW"]

W, H = 1000, 500
COLOR = "#FF3B7F"
FONT_SIZE = 20
CW = FONT_SIZE * 0.6          # fixed character width (enforced with textLength)
TEXT_Y = H - 50               # baseline of the text; raise/lower to move it
CENTER_X = W / 2
STROKE = 4                    # dark outline so the pink stays readable on the art; set 0 to remove
IMG_ALIGN = "xMidYMid slice"

TYPE, HOLD, ERASE = 2.5, 1.2, 0.8   # seconds per line: typing / pause / erasing
SLOT = TYPE + HOLD + ERASE
TOTAL = SLOT * len(LINES)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()

def steps(n, s):
    """Breakpoints (time, chars_visible) for one line: type, hold, erase, then 0 until the loop restarts."""
    pts = [] if s == 0 else [(0.0, 0)]
    for i in range(1, n + 1):
        pts.append((s + TYPE * (i - 1) / n, i))
    hold_end = s + TYPE + HOLD
    for i in range(n - 1, -1, -1):
        pts.append((hold_end + ERASE * (n - 1 - i) / n, i))
    return pts

def animate(attr, pts, fn):
    kt = ";".join(f"{t / TOTAL:.4f}" for t, _ in pts)
    vals = ";".join(fn(v) for _, v in pts)
    return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{TOTAL}s" '
            f'repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/>')

def line_svg(k, text):
    n = len(text)
    s = k * SLOT
    x0 = CENTER_X - n * CW / 2
    pts = steps(n, s)
    top, height = TEXT_Y - FONT_SIZE, FONT_SIZE * 1.5
    clip = (f'<clipPath id="t{k}"><rect x="{x0 - 2:.1f}" y="{top}" height="{height}" width="0">'
            f'{animate("width", pts, lambda v: f"{v * CW + 2:.1f}")}</rect></clipPath>')
    stroke = (f' stroke="#000" stroke-width="{STROKE}" paint-order="stroke" stroke-linejoin="round"' if STROKE else "")
    label = (f'<text x="{x0:.1f}" y="{TEXT_Y}" textLength="{n * CW:.1f}" lengthAdjust="spacing" '
             f'class="mono" font-size="{FONT_SIZE}" fill="{COLOR}"{stroke} clip-path="url(#t{k})">{escape(text)}</text>')
    # cursor follows the typed text; visible only during this line's slot, blinking
    vis_pts = ([(0.0, 1)] if s == 0 else [(0.0, 0), (s, 1)]) + [(s + SLOT, 0)]
    cursor = (f'<g opacity="0">{animate("opacity", vis_pts, str)}'
              f'<rect y="{top + 2}" width="2" height="{FONT_SIZE * 1.2:.1f}" fill="{COLOR}">'
              f'{animate("x", pts, lambda v: f"{x0 + v * CW:.1f}")}'
              f'<animate attributeName="opacity" values="1;0" dur="0.8s" calcMode="discrete" repeatCount="indefinite"/>'
              f'</rect></g>')
    return clip, label + cursor

def build(bg_bytes):
    bg = "data:image/png;base64," + base64.b64encode(bg_bytes).decode()
    clips, body = [], []
    for k, t in enumerate(LINES):
        c, b = line_svg(k, t)
        clips.append(c); body.append(b)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>END OF TRANSMISSION</title>
  <style>.mono {{ font-family: "Share Tech Mono", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}</style>
  <defs><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath>{"".join(clips)}</defs>
  <g clip-path="url(#c)">
    <image href="{bg}" width="{W}" height="{H}" preserveAspectRatio="{IMG_ALIGN}"/>
    {"".join(body)}
  </g>
</svg>'''

if __name__ == "__main__":
    svg = build(fetch(BG_URL))
    open("footer.svg", "w", encoding="utf-8").write(svg)
    print(f"footer.svg written ({len(svg)/1024:.0f} KB)")