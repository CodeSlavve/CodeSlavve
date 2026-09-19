"""Builds header.svg: yellow banner with glitchy 'PROXY / YASH' (text breaks into shifting slices, RGB split, flashing blocks).
Run:  python build_header.py  ->  header.svg   (no downloads needed). Change SEED for a different glitch pattern.
"""
import random
from xml.sax.saxutils import escape

SEED = 7
W, H = 1000, 240
DUR = 4                       # seconds per loop
BANDS, BAND_Y0, BAND_H = 6, 62, 12   # title is sliced into BANDS horizontal strips
MAX_SHIFT = 22                # max horizontal displacement of a slice (px)
BLOCKS = 4                    # small flashing glitch rectangles
TITLE, DESC = "PROXY / YASH", "ヤシュ ✦ AI / ML ✦ CodeSlavve"

# keyframes as fractions of the loop: burst 1 = steps 1-5, burst 2 = steps 7-11
KT = [0, .55, .57, .59, .61, .65, .85, .87, .89, .91, 1.0]
BURST = {1, 2, 3, 7, 8, 9}
N = len(KT)

rnd = random.Random(SEED)


# --- subtitle "decode" effect: each letter flickers through random glyphs, then settles left to right ---
SUB_LOOP = 8            # seconds between replays of the decode effect
SUB_START = 0.5         # delay before decoding starts (s)
SUB_STAGGER = 0.045     # extra delay per letter (s) -> settles left to right
SUB_FRAME = 0.09        # how long each random glyph shows (s)
SCRAMBLE_COLOR = "#ff2d6f"
POOL_LATIN = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789#%&@$<>/=+*"
POOL_KANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
rnd_sub = random.Random(SEED + 1)   # separate generator so the title glitch pattern doesn't change

def cell(ch):
    return 9 if ch == " " else (22 if ord(ch) > 0x2000 else 15)   # width reserved per character

def decode(sub_t=None):
    """sub_t=None -> animated; sub_t=<seconds> -> frozen frame for previewing."""
    total = sum(cell(c) for c in DESC)
    x, out, k = 500 - total / 2, [], 0
    for ch in DESC:
        w = cell(ch)
        cx = x + w / 2
        x += w
        if ch == " ":
            continue
        pool = POOL_KANA + "✦" if ord(ch) > 0x2000 else POOL_LATIN
        settle = SUB_START + k * SUB_STAGGER + rnd_sub.uniform(0.3, 0.6)
        k += 1
        n = max(1, int((settle - SUB_START) / SUB_FRAME))
        frames = []
        for f in range(n):
            g = rnd_sub.choice([p for p in pool if p != ch])
            s = SUB_START + f * SUB_FRAME
            e = settle if f == n - 1 else s + SUB_FRAME
            frames.append((g, s, e))
        base = f'<text class="desc" x="{cx:.1f}" y="168"'
        if sub_t is not None:
            if sub_t >= settle:
                out.append(f'{base} fill="#000">{ch}</text>')
            elif sub_t >= SUB_START:
                g = next(g for g, s, e in frames if s <= sub_t < e)
                out.append(f'{base} fill="{SCRAMBLE_COLOR}">{escape(g)}</text>')
            continue
        T = SUB_LOOP
        for g, s, e in frames:
            out.append(f'{base} fill="{SCRAMBLE_COLOR}" opacity="0">{escape(g)}<animate attributeName="opacity" calcMode="discrete" '
                       f'dur="{T}s" repeatCount="indefinite" keyTimes="0;{s/T:.4f};{e/T:.4f}" values="0;1;0"/></text>')
        out.append(f'{base} fill="#000" opacity="0">{ch}<animate attributeName="opacity" calcMode="discrete" '
                   f'dur="{T}s" repeatCount="indefinite" keyTimes="0;{settle/T:.4f}" values="0;1"/></text>')
    return "".join(out)

def anim(attr, vals, kind=None):
    kt = ";".join(f"{k:.2f}" for k in KT)
    v = ";".join(str(x) for x in vals)
    tag = "animateTransform" if kind else "animate"
    extra = f' type="{kind}"' if kind else ""
    return (f'<{tag} attributeName="{attr}"{extra} calcMode="discrete" dur="{DUR}s" '
            f'repeatCount="indefinite" keyTimes="{kt}" values="{v}"/>')

def build(static=None, sub_t=99):
    """static=None -> animated file; static=<step index> -> frozen frame for previewing."""
    def pick(vals, attr, kind=None):
        return anim(attr, vals, kind) if static is None else ""
    def first(vals):
        return vals[0] if static is None else vals[static]

    out = []
    # RGB-split copies (full title, flash at burst steps)
    for color, sign in (("#ff2d6f", -1), ("#00c8e6", 1)):
        ops = [round(rnd.choice([0.85, 0.7]), 2) if i in BURST else 0 for i in range(N)]
        xs = [500 + sign * rnd.randint(3, 6) if i in BURST else 500 for i in range(N)]
        out.append(f'<text class="title" x="{first(xs)}" y="122" fill="{color}" opacity="{first(ops)}">{TITLE}'
                   f'{pick(ops, "opacity")}{pick(xs, "x")}</text>')

    # main title, cut into strips that jump sideways / vanish during bursts
    bands = []
    for b in range(BANDS):
        dxs, dys, ops = [], [], []
        for i in range(N):
            if i in BURST and rnd.random() < 0.55:
                dx = rnd.choice([-1, 1]) * rnd.randint(8, MAX_SHIFT)
                dy = rnd.choice([-3, 0, 0, 3])
                op = 0 if rnd.random() < 0.15 else 1
            else:
                dx, dy, op = 0, 0, 1
            dxs.append(f"{dx} {dy}"); ops.append(op)
        bands.append((dxs, ops))
        y0 = BAND_Y0 + b * BAND_H
        out.append(f'<g clip-path="url(#b{b})" opacity="{first(ops)}">{pick(ops, "opacity")}'
                   f'<use href="#t" transform="translate({first(dxs)})">{pick(dxs, "transform", "translate")}</use></g>')

    # flashing black/pink blocks
    for _ in range(BLOCKS):
        x, y = rnd.randint(230, 720), rnd.randint(68, 128)
        w, h = rnd.randint(24, 90), rnd.randint(4, 10)
        color = rnd.choice(["#000", "#000", "#ff2d6f"])
        ops = [1 if (i in BURST and rnd.random() < 0.4) else 0 for i in range(N)]
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" opacity="{first(ops)}">{pick(ops, "opacity")}</rect>')

    # subtitle: decodes letter by letter, and shakes a little during title bursts
    dxs = [f"{rnd.choice([-1, 1]) * rnd.randint(2, 5)} 0" if (i in BURST and rnd.random() < 0.5) else "0 0" for i in range(N)]
    out.append(f'<g transform="translate({first(dxs)})">{pick(dxs, "transform", "translate")}'
               f'{decode(None if static is None else sub_t)}</g>')

    clips = "".join(f'<clipPath id="b{b}"><rect x="0" y="{BAND_Y0 + b*BAND_H}" width="{W}" height="{BAND_H}"/></clipPath>' for b in range(BANDS))
    fade = "" if static is not None else '<animate attributeName="opacity" from="0" to="1" dur="0.6s" fill="freeze"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{TITLE}</title>
  <style>
    .title {{ font-family: "Segoe UI", -apple-system, Helvetica, Arial, sans-serif; font-weight: 800; font-size: 64px; letter-spacing: 2px; text-anchor: middle; }}
    .desc  {{ font-family: "Segoe UI", "Yu Gothic", "Hiragino Sans", "Noto Sans JP", Arial, sans-serif; font-weight: 600; font-size: 20px; letter-spacing: 1px; text-anchor: middle; }}
  </style>
  <defs>
    <clipPath id="clip"><rect width="{W}" height="{H}"/></clipPath>
    {clips}
    <text id="t" class="title" x="500" y="122" fill="#000">{TITLE}</text>
  </defs>
  <g clip-path="url(#clip)">
    <rect width="{W}" height="{H}" fill="#d9ff00"/>
    <g opacity="{1 if static is not None else 0}">{fade}
      {"".join(out)}
    </g>
  </g>
</svg>'''

if __name__ == "__main__":
    open("header.svg", "w", encoding="utf-8").write(build())
    print("header.svg written")