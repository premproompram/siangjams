"""Builds the halftone SVGs in assets/. Run: python -I assets/make_halftones.py (from website/).

Marigold dots, crisp in the middle. Toward the outline they get smaller, fainter and
progressively blurrier, so the shape melts into the background like the soft edge of the
glow reference; a faint blurred copy underneath adds the haze.
"""
import math

def heart(x, y): return (x*x + y*y - 1)**3 - x*x*y**3 <= 0
def radial(R): return lambda x, y: math.hypot(x, y) <= R(math.atan2(y, x))
blob = radial(lambda t: 1 + .10*math.sin(3*t + 1) + .06*math.cos(5*t))
oval = radial(lambda t: 1 / math.sqrt(math.cos(t)**2 + (math.sin(t)/.62)**2) * (1 + .07*math.sin(4*t + 2)))
star = radial(lambda t: .52 + .48*(.5 + .5*math.cos(5*(t - math.pi/2)))**1.6)

def depth(inside, x, y):  # 0 at the outline, 1 at the centre
    if not inside(x, y): return 0
    lo, hi = 0.0, 1.0
    for _ in range(18):
        k = (lo + hi) / 2
        if inside(x / k, y / k): hi = k
        else: lo = k
    return 1 - hi

def smooth(e0, e1, v):
    v = max(0, min(1, (v - e0) / (e1 - e0))); return v * v * (3 - 2 * v)

YELLOW = "#F7C510"
# Edge bands get progressively more blur, like the soft rim of the glow reference.
BANDS = [(.10, 4.0), (.20, 2.6), (.32, 1.4), (.45, .6)]  # (depth below which, blur stdDeviation)

def make(name, inside, W, H, cx, cy, sx, sy, step=13, rmax=5.0, size_fade=.5):
    groups = [[] for _ in range(len(BANDS) + 1)]
    for row in range(H // step + 2):
        for col in range(W // step + 2):
            px = col * step + (step / 2 if row % 2 else 0); py = row * step
            d = depth(inside, (px - cx) / sx, -(py - cy) / sy)
            r = rmax * (.45 + .55 * smooth(0, size_fade, d))
            op = smooth(0, .5, d) ** 1.2  # fades into whatever is behind it
            if d <= 0 or op < .03: continue
            band = next((i for i, (lim, _) in enumerate(BANDS) if d < lim), len(BANDS))
            groups[band].append('<circle cx="%.1f" cy="%.1f" r="%.2f"%s/>' % (px, py, r, "" if op > .98 else ' fill-opacity="%.2f"' % op))
    pad = 40
    filters = "".join('<filter id="b%d" x="-10%%" y="-10%%" width="120%%" height="120%%"><feGaussianBlur stdDeviation="%.1f"/></filter>' % (i, sd) for i, (_, sd) in enumerate(BANDS))
    filters += '<filter id="g" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="18"/></filter>'
    layers = "".join('<g%s>%s</g>' % (' filter="url(#b%d)"' % i if i < len(BANDS) else "", "".join(g)) for i, g in enumerate(groups))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" fill="%s"><defs>%s</defs>'
           '<g filter="url(#g)" opacity=".3">%s</g>%s</svg>'
           % (-pad, -pad, W + 2 * pad, H + 2 * pad, YELLOW, filters, layers, layers))
    open("assets/" + name, "w").write(svg)
    print(name, sum(map(len, groups)), len(svg))

make("halftone-heart.svg", heart, 640, 580, 320, 580 * .58, 640 / 2.4, 580 / 2.6, rmax=4.8, size_fade=.38)
make("halftone-blob.svg", blob, 420, 420, 210, 210, 186, 186)
make("halftone-oval.svg", oval, 520, 360, 260, 180, 236, 236)
make("halftone-star.svg", star, 360, 360, 180, 185, 172, 172, step=12, rmax=4.4)
