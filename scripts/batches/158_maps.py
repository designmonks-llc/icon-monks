import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

MP = 'Maps'

# ---------------------------------------------------------------- geometry kit
# A shape is a list of cubic segments ((p0, p1, p2, p3), ...); lines and arcs become cubics.

def seg_line(p, q):
    return (p, (p[0] + (q[0] - p[0]) / 3, p[1] + (q[1] - p[1]) / 3),
            (p[0] + 2 * (q[0] - p[0]) / 3, p[1] + 2 * (q[1] - p[1]) / 3), q)


def lines(points, closed=False):
    pts = list(points) + ([points[0]] if closed else [])
    return [seg_line(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def earc(c, rx, ry, a0, a1):
    """Elliptical arc from angle a0 to a1 (degrees, screen angles; a1 > a0 is clockwise)."""
    n = max(1, int(math.ceil(abs(a1 - a0) / 90.0 - 1e-9)))
    out = []
    for i in range(n):
        t0 = math.radians(a0 + (a1 - a0) * i / n)
        t1 = math.radians(a0 + (a1 - a0) * (i + 1) / n)
        k = 4 / 3 * math.tan((t1 - t0) / 4)
        p0 = (c[0] + rx * math.cos(t0), c[1] + ry * math.sin(t0))
        p3 = (c[0] + rx * math.cos(t1), c[1] + ry * math.sin(t1))
        p1 = (p0[0] - k * rx * math.sin(t0), p0[1] + k * ry * math.cos(t0))
        p2 = (p3[0] + k * rx * math.sin(t1), p3[1] - k * ry * math.cos(t1))
        out.append((p0, p1, p2, p3))
    return out


def circ(c, r, start=-90):
    return earc(c, r, r, start, start + 360)


def tf(segs, s=1.0, dx=0.0, dy=0.0, o=(0, 0)):
    m = lambda p: (o[0] + (p[0] - o[0]) * s + dx, o[1] + (p[1] - o[1]) * s + dy)
    return [tuple(m(p) for p in sg) for sg in segs]


def bez(sg, t):
    p0, p1, p2, p3 = sg
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def split(sg, t):
    p0, p1, p2, p3 = sg
    lp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = lp(p0, p1), lp(p1, p2), lp(p2, p3)
    d, e = lp(a, b), lp(b, c)
    m = lp(d, e)
    return (p0, a, d, m), (m, e, c, p3)


def sub(sg, t0, t1):
    if t0 > 0:
        sg = split(sg, t0)[1]
        t1 = (t1 - t0) / (1 - t0)
    if t1 < 1:
        sg = split(sg, t1)[0]
    return sg


def clip(segs, removed, closed=False, N=96):
    """Keep the parts of a shape where removed(p) is False. Returns a list of pieces (lists of segments)."""
    pieces, cur = [], None
    first_start = None
    for si, sg in enumerate(segs):
        ts = [i / N for i in range(N + 1)]
        ins = [removed(bez(sg, t)) for t in ts]
        bounds = []
        for i in range(N):
            if ins[i] != ins[i + 1]:
                lo, hi = ts[i], ts[i + 1]
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if removed(bez(sg, mid)) == ins[i]:
                        lo = mid
                    else:
                        hi = mid
                bounds.append((lo + hi) / 2)
        # walk kept intervals
        state = not ins[0]
        t = 0.0
        for b in bounds + [1.0]:
            if state and b - t > 1e-6:
                part = sub(sg, t, b)
                if cur is not None and t == 0.0:
                    cur.append(part)
                else:
                    cur = [part]
                    pieces.append(cur)
                    if si == 0 and t == 0.0:
                        first_start = cur
            if b < 1.0:
                if state:
                    cur = None
                state = not state
            t = b
        if not state:
            cur = None
    if closed and len(pieces) > 1 and first_start is pieces[0] and cur is pieces[-1]:
        last = pieces.pop()
        pieces[0][:0] = last
    return pieces


def _straight(sg):
    p0, p1, p2, p3 = sg
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    ln = math.hypot(dx, dy) or 1
    return all(abs((p[0] - p0[0]) * dy - (p[1] - p0[1]) * dx) / ln < 0.05 for p in (p1, p2))


def d_of(segs, close=False):
    d = f'M{pt(segs[0][0])}'
    for sg in segs:
        if _straight(sg):
            d += f' L{pt(sg[3])}'
        else:
            d += f' C{pt(sg[1])} {pt(sg[2])} {pt(sg[3])}'
    return d + (' Z' if close else '')


def paths(pieces):
    return [P(d_of(p)) for p in pieces]


def sample(segs, n=24):
    out = [segs[0][0]]
    for sg in segs:
        out += [bez(sg, i / n) for i in range(1, n + 1)]
    return out


def inside_poly(p, poly):
    x, y = p
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def dist_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def near_shape(segs, gap):
    poly = sample(segs)
    def f_(p):
        if inside_poly(p, poly):
            return True
        return min(dist_seg(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1)) < gap
    return f_


def dashes(segs, dash=10, gap=26, offset=0):
    pts = sample(segs, 64)
    acc = [0.0]
    for i in range(1, len(pts)):
        acc.append(acc[-1] + dist(pts[i - 1], pts[i]))
    total = acc[-1]
    period = dash + gap
    n = max(1, int(round((total - dash) / period)))
    period = (total - dash) / n
    def at(s):
        for i in range(1, len(acc)):
            if acc[i] >= s:
                t = (s - acc[i - 1]) / ((acc[i] - acc[i - 1]) or 1)
                return (pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t)
        return pts[-1]
    out = []
    for k in range(n + 1):
        s0 = k * period
        out.append(L(*at(s0), *at(s0 + dash)) if dash > 0 else None)
    return out


def badge_cut(segs, R, closed=True, c=(184, 184), centre=(128, 128)):
    """Cut a shape around the badge circle. Returns (line paths, area path for the closed shape)."""
    rem = lambda p: dist(p, c) < R
    pieces = clip(segs, rem, closed)
    area = None
    if closed and len(pieces) == 1:
        pc = pieces[0]
        area = P(d_of(pc) + ' ' + arc_to(c, R, pc[-1][3], pc[0][0], lambda m: -dist(m, centre)) + ' Z')
    return paths(pieces), area


def slash_cut(segs, closed=False, g=30):
    rem = lambda p: abs(p[0] - p[1]) / math.sqrt(2) < g
    return paths(clip(segs, rem, closed))


SLASH = L(48, 48, 208, 208)

# ---------------------------------------------------------------- base shapes
PIN = ([seg_line((128, 224), (128, 224))[:0]] and []) or [
    ((128, 224), (128, 224), (56, 160), (56, 104))] + earc((128, 104), 72, 72, 180, 360) + [
    ((200, 104), (200, 160), (128, 224), (128, 224))]
PIN_D = 'M128 224 C128 224 56 160 56 104 A72 72 0 0 1 200 104 C200 160 128 224 128 224 Z'

GLOBE = circ((128, 128), 96, 0)
GLOBE_E = earc((128, 128), 40, 96, -90, 270)
GLOBE_H = lines([(32, 128), (224, 128)])

TRI_PTS = [(32, 64), (96, 40), (160, 64), (224, 40), (224, 192), (160, 216), (96, 192), (32, 216)]
TRI = lines(TRI_PTS, True)
TRI_F = [lines([(96, 40), (96, 192)]), lines([(160, 64), (160, 216)])]

# ---------------------------------------------------------------- badges (centred on 184,184)
star_b = [polar((184, 186), 33 if i % 2 == 0 else 14, -90 + i * 36) for i in range(10)]
shield_b = 'M184 151.36 L211.2 162.24 L211.2 181.28 C211.2 200.32 197.6 211.2 184 216.64 C170.4 211.2 156.8 200.32 156.8 181.28 L156.8 162.24 Z'
pencil_b = 'M153.76 214.24 L159.52 194.08 L199.84 153.76 L214.24 168.16 L173.92 208.48 Z'
heart_b = 'M184 213.84 C184 213.84 151.36 196.16 151.36 175.08 A17 17 0 0 1 184 168.28 A17 17 0 0 1 216.64 175.08 C216.64 196.16 184 213.84 184 213.84 Z'
bolt_b = 'M189.76 149.44 L158.08 189.76 L181.12 189.76 L175.36 218.56 L209.92 176.8 L186.88 176.8 Z'
gear_b = ('M174.63 160.82 L176.31 147.81 L191.69 147.81 L193.37 160.82 A25 25 0 0 1 199.39 164.3 L211.5 159.24 '
          'L219.19 172.57 L208.76 180.52 A25 25 0 0 1 208.76 187.48 L219.19 195.43 L211.5 208.76 L199.39 203.7 '
          'A25 25 0 0 1 193.37 207.18 L191.69 220.19 L176.31 220.19 L174.63 207.18 A25 25 0 0 1 168.61 203.7 '
          'L156.5 208.76 L148.81 195.43 L159.24 187.48 A25 25 0 0 1 159.24 180.52 L148.81 172.57 L156.5 159.24 '
          'L168.61 164.3 A25 25 0 0 1 174.63 160.82 Z')
pushpin_b = 'M200.25 146.03 L217.86 160.8 L209.01 166.23 L198.46 178.81 L197.12 203.4 L161.9 173.85 L185.88 168.26 L196.43 155.68 Z'

# name -> (R, dict of roles)
BADGES = {
    'check': (58, dict(line=[PL([(156, 186), (176, 206), (212, 170)])])),
    'plus': (58, dict(line=[L(156, 184, 212, 184), L(184, 156, 184, 212)])),
    'minus': (58, dict(line=[L(156, 184, 212, 184)])),
    'x': (54, dict(line=[L(164, 164, 204, 204), L(204, 164, 164, 204)])),
    'arrow-up': (58, dict(line=[L(184, 214, 184, 154), PL([(160, 178), (184, 154), (208, 178)])])),
    'arrow-down': (58, dict(line=[L(184, 154, 184, 214), PL([(160, 190), (184, 214), (208, 190)])])),
    'arrow': (58, dict(line=[L(160, 208, 208, 160), PL([(168, 160), (208, 160), (208, 200)])])),
    'heart': (60, dict(line=[P(heart_b)], area=[P(heart_b)])),
    'lightning': (60, dict(line=[P(bolt_b)], area=[P(bolt_b)])),
    'magnifying-glass': (60, dict(line=[C(178, 178, 22), L(195, 195, 212, 212)], area=[C(178, 178, 22)])),
    'pause': (58, dict(line=[L(168, 160, 168, 208), L(200, 160, 200, 208)])),
    'star': (60, dict(line=[PG(star_b)], area=[PG(star_b)])),
    'shield': (60, dict(line=[P(shield_b)], area=[P(shield_b)])),
    'pencil': (60, dict(line=[P(pencil_b)], area=[P(pencil_b)])),
    'code': (60, dict(line=[PL([(172, 162), (154, 184), (172, 206)]), PL([(196, 162), (214, 184), (196, 206)])])),
    'currency-dollar': (58, dict(line=[L(184, 148, 184, 220),
                                       P('M202 158 H178 A13 13 0 0 0 178 184 H190 A13 13 0 0 1 190 210 H166')])),
    'discount': (58, dict(line=[L(206, 162, 162, 206)], dot=[C(164, 164, 14), C(204, 204, 14)])),
    'gear': (62, dict(line=[P(gear_b)], area=[P(gear_b)], dotcut=[C(184, 184, 9)])),
    'push-pin': (60, dict(line=[P(pushpin_b), L(179.51, 188.63, 160.51, 211.26)], area=[P(pushpin_b)])),
    'share': (58, dict(line=[P('M160 210 V198 A24 24 0 0 1 184 174 H210'), PL([(194, 158), (210, 174), (194, 190)])])),
    'question': (58, dict(line=[P('M170 158 A14 14 0 1 1 191 170.12 C186 173 184 176 184 182')], dot=[C(184, 210, 16)])),
    'warning': (58, dict(line=[L(184, 150, 184, 182)], dot=[C(184, 210, 16)])),
    'clock': (62, dict(line=[C(184, 184, 34)], area=[C(184, 184, 34)], detail=[PL([(184, 166), (184, 184), (198, 192)])])),
}


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, []).extend(v)
    return out


def globe_badge(name, tags, b):
    R, roles = BADGES[b]
    ln, ar = badge_cut(GLOBE, R)
    det = []
    det += badge_cut(GLOBE_E, R)[0]
    det += badge_cut(GLOBE_H, R, closed=False)[0][:1]
    icon(name, MP, tags, **merge(dict(line=ln, area=[ar], detail=det), roles))


PSH = 12

def pin_badge(name, tags, b):
    R, roles = BADGES[b]
    ln, ar = badge_cut(tf(PIN, dx=-PSH), R)
    icon(name, MP, tags, **merge(dict(line=ln, area=[ar], detail=[C(128 - PSH, 104, 24)]), roles))


def tri_badge(name, tags, b):
    R, roles = BADGES[b]
    ln, ar = badge_cut(TRI, R)
    det = []
    for fl in TRI_F:
        det += badge_cut(fl, R + 12, closed=False)[0]
    icon(name, MP, tags, **merge(dict(line=ln, area=[ar], detail=det), roles))


# ---------------------------------------------------------------- globe badges
globe_badge('globe-question', ['globe', 'help', 'unknown', 'question'], 'question')
globe_badge('globe-share', ['globe', 'share', 'send'], 'share')
globe_badge('globe-star', ['globe', 'favorite', 'starred', 'featured'], 'star')
globe_badge('globe-warning', ['globe', 'warning', 'alert', 'error'], 'warning')
globe_badge('globe-x', ['offline', 'no internet', 'disconnected'], 'x')

# ---------------------------------------------------------------- gps
CROSS = [circ((128, 128), 80, 0), lines([(128, 32), (128, 80)]), lines([(128, 176), (128, 224)]),
         lines([(32, 128), (80, 128)]), lines([(176, 128), (224, 128)])]
icon('gps-fix', MP, ['location found', 'gps', 'my location', 'current location', 'locate me'],
     line=[C(128, 128, 80), L(128, 32, 128, 80), L(128, 176, 128, 224), L(32, 128, 80, 128), L(176, 128, 224, 128)],
     dot=[C(128, 128, 32)])
gl = []
for i, s in enumerate(CROSS):
    gl += slash_cut(s, closed=(i == 0))
icon('gps-fix-slash', MP, ['gps off', 'no location', 'location disabled', 'gps', 'disabled'], line=gl + [SLASH])

# ---------------------------------------------------------------- great wall
HC = (128, 306)
def on(r, deg):
    return polar(HC, r, deg)
lo_r, hi_r, m_r = 144, 184, 208
aL = math.degrees(math.atan2(-math.sqrt(hi_r ** 2 - 96 ** 2), -96))   # left end on top arc (x=32)
aR = -180 - aL
bL = math.degrees(math.atan2(-math.sqrt(lo_r ** 2 - 96 ** 2), -96))
bR = -180 - bL
tower = (100, 56, 156)  # x0, top, x1
def wall_top(a0, a1, n):
    # crenellated top edge from angle a0 to a1: n merlons, starting and ending with a merlon
    pts = []
    k = 2 * n - 1
    step = (a1 - a0) / k
    for i in range(k):
        s0, s1 = a0 + i * step, a0 + (i + 1) * step
        r = m_r if i % 2 == 0 else hi_r
        pts += [on(r, s0), on(r, s1)]
    return pts
# angles where top arc meets the tower walls
tl = math.degrees(math.atan2(-math.sqrt(hi_r ** 2 - 28 ** 2) + 0, -28))
tr = -180 - tl
tbl = math.degrees(math.atan2(-math.sqrt(lo_r ** 2 - 28 ** 2), -28))
left_top = [on(hi_r, aL)] + wall_top(aL + 4, tl - 2, 2)[0:] + [on(hi_r, tl)]
right_top = [on(hi_r, tr)] + wall_top(tr + 2, aR - 4, 2) + [on(hi_r, aR)]
left_wall = [(32, on(lo_r, bL)[1])] + [(32, on(hi_r, aL)[1])]
gw_left = P(poly([on(lo_r, tbl)]) + ' ' + arc_to(HC, lo_r, on(lo_r, tbl), (32, on(lo_r, bL)[1]), lambda m: -m[1]).replace('A', 'A', 1)
            + ' ' + poly([(32, on(hi_r, aL)[1])] + left_top[1:]).replace('M', 'L', 1))
gw_right = P(poly([on(hi_r, tr)] + right_top[1:]) + f' L224 {f(on(lo_r, bR)[1])} '
             + arc_to(HC, lo_r, (224, on(lo_r, bR)[1]), on(lo_r, tbl * 0 + (-180 - tbl)), lambda m: -m[1]))
tw_top = 58
tw = [(100, on(lo_r, tbl)[1]), (100, tw_top), (118, tw_top), (118, tw_top + 18), (138, tw_top + 18), (138, tw_top), (156, tw_top), (156, on(lo_r, tbl)[1])]
icon('great-wall', MP, ['great wall', 'china', 'landmark', 'fortress'],
     line=[gw_left, gw_right, PL(tw)],
     detail=[P('M116 162 V142 A12 12 0 0 1 140 142 V162')],
     area=[P(gw_left[9:-3] + ' Z'), P(gw_right[9:-3] + ' Z'), PG(tw)])

# ---------------------------------------------------------------- hot spring
wisps = []
for x, top in ((84, 56), (128, 40), (172, 56)):
    m = (136 + top) / 2
    wisps.append(P(f'M{x} 136 C{x - 10} {f(136 - (136 - m) / 3)} {x + 10} {f(m + (136 - m) / 3)} {x} {f(m)} '
                   f'C{x - 10} {f(m - (m - top) / 3)} {x + 10} {f(top + (m - top) / 3)} {x} {top}'))
bowl = 'M32 160 C32 196 72 216 128 216 C184 216 224 196 224 160'
icon('hot-spring', MP, ['onsen', 'spa', 'hot spring', 'bath'],
     line=[P(bowl)] + wisps, area=[P(bowl + ' Z')])

# ---------------------------------------------------------------- hotel
blanket = 'M136 176 V128 A16 16 0 0 1 152 112 H192 A32 32 0 0 1 224 144 V176'
icon('hotel', MP, ['hotel', 'lodging', 'stay', 'bed'],
     line=[L(32, 56, 32, 208), P('M32 176 H224 V208'), P(blanket), C(84, 124, 22)],
     area=[P(blanket + ' Z'), C(84, 124, 22)])

# ---------------------------------------------------------------- leaning tower
lean = 9
O = (128, 224)
lean = 10
def lean_pts(pts):
    return rot(pts, lean, O)
up = (math.sin(math.radians(lean)), -math.cos(math.radians(lean)))
def to_ground(p, gy=216):
    t = (gy - p[1]) / up[1]
    return (p[0] + up[0] * t, gy)
tl_, tr_ = lean_pts([(94, 72), (162, 72)])
body = [to_ground(tl_), tl_, tr_, to_ground(tr_)]
cl, cr = lean_pts([(106, 72), (150, 72)])
ctl, ctr = lean_pts([(106, 54), (150, 54)])
cap_d = f'M{pt(cl)} L{pt(ctl)} A22 22 0 0 1 {pt(ctr)} L{pt(cr)}'
tiers = []
for y in (108, 144, 180):
    a_, b_ = lean_pts([(90, y), (170, y)])
    # trim to the body edges
    def edge_x(p0, q0):
        return None
    tiers.append((a_, b_))
def clip_to_body(a_, b_):
    poly_ = body
    rem = lambda p: not inside_poly(p, poly_)
    pcs = clip(lines([a_, b_]), rem)
    return pcs[0][0][0], pcs[0][-1][3]
tiers = [clip_to_body(a_, b_) for a_, b_ in tiers]
icon('leaning-tower', MP, ['pisa', 'tower', 'landmark', 'italy'],
     line=[PL(body), P(cap_d), L(40, 216, 216, 216)],
     detail=[L(*a_, *b_) for a_, b_ in tiers],
     area=[PG(body), P(cap_d + ' Z')])

# ---------------------------------------------------------------- lighthouse
lt_body = [(84, 216), (100, 112), (156, 112), (172, 216)]
icon('lighthouse', MP, ['lighthouse', 'coast', 'beacon', 'navigation'],
     line=[PL(lt_body), L(48, 216, 208, 216), L(84, 112, 172, 112), PL([(108, 112), (108, 76), (148, 76), (148, 112)]),
           P('M100 76 H156 A28 28 0 0 0 100 76 Z'),
           L(72, 68, 40, 56), L(72, 100, 40, 112), L(184, 68, 216, 56), L(184, 100, 216, 112)],
     detail=[L(95.38, 152, 160.62, 152), L(90.15, 184, 165.85, 184)],
     area=[PG(lt_body), R(108, 76, 40, 36), P('M100 76 H156 A28 28 0 0 0 100 76 Z')])

# ---------------------------------------------------------------- map area / route / ruler
region = [(104, 96), (150, 84), (172, 128), (140, 168), (90, 152)]
reg_rem = near_shape(lines(region, True), 26)
fold_cut = []
for fl in TRI_F:
    fold_cut += paths(clip(fl, reg_rem))
icon('map-area', MP, ['area', 'region', 'map', 'boundary'],
     line=[PG(TRI_PTS), PG(region)] + fold_cut, area=[PG(region)])

route = [((72, 184), (72, 132), (112, 152), (128, 120)), ((128, 120), (144, 88), (184, 108), (184, 76))]
icon('map-route', MP, ['route', 'map', 'directions', 'path'],
     line=[PG(TRI_PTS)], area=[PG(TRI_PTS)],
     detail=[d for d in dashes(route, 2, 26)])

icon('map-ruler', MP, ['distance', 'measure', 'route length', 'map'],
     line=[PG(TRI_PTS)], area=[PG(TRI_PTS)],
     detail=[L(76, 164, 180, 104), L(64, 143.2, 88, 184.8), L(168, 83.2, 192, 124.8)])

# ---------------------------------------------------------------- pin variants
pin_badge('map-pin-arrow', ['navigate', 'pin', 'location', 'direction'], 'arrow')
pin_badge('map-pin-arrow-up', ['map pin', 'upload', 'up', 'increase', 'map'], 'arrow-up')
pin_badge('map-pin-arrow-down', ['map pin', 'download', 'down', 'decrease', 'map'], 'arrow-down')
pin_badge('map-pin-check', ['vote location', 'confirmed place', 'check in', 'pin', 'map pin check'], 'check')
pin_badge('map-pin-clock', ['location time', 'map', 'pin', 'schedule'], 'clock')
pin_badge('map-pin-code', ['map pin', 'code', 'developer', 'embed', 'map'], 'code')
pin_badge('map-pin-currency-dollar', ['map pin', 'dollar', 'price', 'money', 'map'], 'currency-dollar')
pin_badge('map-pin-discount', ['map pin', 'discount', 'sale', 'percent', 'map'], 'discount')
pin_badge('map-pin-gear', ['map pin', 'settings', 'configure', 'map', 'pin'], 'gear')
pin_badge('map-pin-heart', ['favourite place', 'saved location', 'love', 'pin'], 'heart')
pin_badge('map-pin-lightning', ['map pin', 'fast', 'power', 'instant', 'map'], 'lightning')
pin_badge('map-pin-magnifying-glass', ['map pin', 'search', 'find', 'map', 'pin'], 'magnifying-glass')
pin_badge('map-pin-minus', ['remove location', 'pin', 'place', 'minus', 'map pin minus'], 'minus')
pin_badge('map-pin-pause', ['map pin', 'paused', 'hold', 'map', 'pin'], 'pause')
pin_badge('map-pin-pencil', ['edit location', 'pin', 'place', 'pencil'], 'pencil')
pin_badge('map-pin-plus', ['add location', 'pin', 'place', 'plus', 'new place'], 'plus')
pin_badge('map-pin-push-pin', ['map pin', 'pin', 'pinned', 'map'], 'push-pin')
pin_badge('map-pin-question', ['unknown location', 'pin', 'place', 'help', 'unlisted place'], 'question')
pin_badge('map-pin-share', ['map pin', 'share', 'send', 'map', 'pin'], 'share')
pin_badge('map-pin-shield', ['safe location', 'pin', 'place', 'security'], 'shield')
pin_badge('map-pin-star', ['place review', 'rated place', 'favourite', 'pin'], 'star')
pin_badge('map-pin-warning', ['map pin', 'warning', 'alert', 'error', 'map'], 'warning')
pin_badge('map-pin-x', ['remove location', 'wrong place', 'delete pin', 'wrong location', 'invalid place'], 'x')

icon('map-pin-house', MP, ['home location', 'address', 'home', 'pin'],
     line=[P(PIN_D)], area=[P(PIN_D)],
     detail=[P('M100 136 V108 L128 82 L156 108 V136 Z')])
icon('map-pin-info', MP, ['location info', 'pin', 'place', 'details'],
     line=[P(PIN_D)], area=[P(PIN_D)], detail=[L(128, 104, 128, 136)], dotcut=[C(128, 72, 16)])
icon('map-pin-user', MP, ['person location', 'people nearby', 'user pin', 'where', 'map'],
     line=[P(PIN_D)], area=[P(PIN_D)],
     detail=[P('M98 156 A30 30 0 0 1 158 156 Z')], dotcut=[C(128, 82, 16)])
icon('map-pin-slash', MP, ['location off', 'pin', 'gps off', 'slash', 'hide location'],
     line=slash_cut(PIN, True) + [SLASH])

# pin + ellipse ring
s_pin = tf(PIN, 0.74, o=(128, 224), dy=-28)
ring = earc((128, 196), 92, 28, 0, 360)
icon('map-pin-area', MP, ['range', 'radius', 'map', 'pin', 'area'],
     line=[P(d_of(s_pin, True))] + paths(clip(ring, near_shape(s_pin, 22), True)),
     detail=[C(128, 196 - 120 * 0.74, 18)],
     area=[P(d_of(s_pin, True))])

# two pins, distance
pa = tf(PIN, 0.6, o=(128, 224), dx=-48, dy=-72)    # tip (80,152)
pb = tf(PIN, 0.6, o=(128, 224), dx=48, dy=-8)      # tip (176,216)
pa_c = (80, 152 - 72); pb_c = (176, 216 - 72)
dash_path = [((80, 184), (80, 210), (104, 218), (140, 216))]
icon('map-pin-distance', MP, ['distance', 'route', 'map', 'pins'],
     line=[P(d_of(pa, True)), P(d_of(pb, True))],
     area=[P(d_of(pa, True)), P(d_of(pb, True))],
     dotcut=[C(pa_c[0], pa_c[1], 14), C(pb_c[0], pb_c[1], 14)])
ICONS[-1]['line'] += dashes(dash_path, 2, 24)

# overlapping pins
front = tf(PIN, 0.82, o=(128, 224), dx=29, dy=0)
back = tf(PIN, 0.7, o=(128, 224), dx=-37.6, dy=-40)
icon('map-pins', MP, ['multiple locations', 'pins', 'places', 'map'],
     line=[P(d_of(front, True))] + paths(clip(back, near_shape(front, 24), True)),

     area=[P(d_of(front, True))],
     detail=[C(157, 224 - 120 * 0.82, 20)])

# ---------------------------------------------------------------- map trifold badges
tri_badge('map-trifold-arrow-down', ['map trifold', 'download', 'down', 'decrease', 'map'], 'arrow-down')
tri_badge('map-trifold-arrow-up', ['map trifold', 'upload', 'up', 'increase', 'map'], 'arrow-up')
tri_badge('map-trifold-check', ['map trifold check', 'done', 'approved', 'map', 'location'], 'check')
tri_badge('map-trifold-code', ['map trifold', 'code', 'developer', 'embed', 'map'], 'code')
tri_badge('map-trifold-currency-dollar', ['map trifold', 'dollar', 'price', 'money', 'map'], 'currency-dollar')
tri_badge('map-trifold-discount', ['map trifold', 'discount', 'sale', 'percent', 'map'], 'discount')
tri_badge('map-trifold-gear', ['map trifold', 'settings', 'configure', 'map', 'trifold'], 'gear')

print(save(overwrite=True))
