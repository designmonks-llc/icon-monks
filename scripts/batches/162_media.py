import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

MD, IF = 'Media', 'Interface'
B = (184, 184)  # badge centre
BX, BY = B
SLASH = L(48, 48, 208, 208)


# ================================================================ outline engine (as batches 113/114, so badges match)
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []
    for i, s in enumerate(segs):
        ts = [k / steps for k in range(steps + 1)]
        ok = [keep(seg_point(s, t)) for t in ts]

        def edge(ta, tb, oa):
            for _ in range(40):
                tm = (ta + tb) / 2
                if keep(seg_point(s, tm)) == oa:
                    ta = tm
                else:
                    tb = tm
            return (ta + tb) / 2
        start = 0.0 if ok[0] else None
        for k in range(1, len(ts)):
            if ok[k] != ok[k - 1]:
                e = edge(ts[k - 1], ts[k], ok[k - 1])
                if ok[k]:
                    start = e
                else:
                    pieces.append((i, start, e))
                    start = None
        if start is not None:
            pieces.append((i, start, 1.0))
    if len(pieces) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in pieces):
        return [segs], True
    runs = []
    for i, t0, t1 in pieces:
        sub = seg_sub(segs[i], t0, t1)
        if runs and t0 == 0 and runs[-1][1] == (i - 1, 1.0):
            runs[-1][0].append(sub)
        else:
            runs.append([[sub], None])
        runs[-1][1] = (i, t1)
    if closed and len(runs) > 1 and pieces[0][1] == 0 and pieces[0][0] == 0 and pieces[-1][2] == 1.0 \
            and pieces[-1][0] == len(segs) - 1:
        last = runs.pop()
        runs[0][0] = last[0] + runs[0][0]
    return [r[0] for r in runs], False


def sample(segs, n=60):
    return [seg_point(s, k / n) for s in segs for k in range(n)]


def inside(poly_pts, p):
    x, y = p
    c = False
    for i in range(len(poly_pts)):
        x1, y1 = poly_pts[i]
        x2, y2 = poly_pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def carve(segs, cut_c, cut_r):
    """Open the closed outline segs around a circular badge. Returns (line d, area d)."""
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r)
    assert not whole and len(runs) == 1, (whole, len(runs))
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    poly_pts = sample(segs)
    arc = arc_to(cut_c, cut_r, e, s, lambda m: 1 if inside(poly_pts, m) else 0)
    return segs_d(run), segs_d(run) + ' ' + arc + ' Z'


def rrect_segs(x, y, w, h, r):
    H = math.pi / 2
    return [('L', (x + r, y), (x + w - r, y)), ('A', (x + w - r, y + r), r, -H, 0),
            ('L', (x + w, y + r), (x + w, y + h - r)), ('A', (x + w - r, y + h - r), r, 0, H),
            ('L', (x + w - r, y + h), (x + r, y + h)), ('A', (x + r, y + h - r), r, H, 2 * H),
            ('L', (x, y + h - r), (x, y + r)), ('A', (x + r, y + r), r, 2 * H, 3 * H)]


def clip_polyline(points, keep, closed=False):
    """Split a polyline into the runs where keep(p) holds (boundaries found by bisection)."""
    pts = list(points) + ([points[0]] if closed else [])
    runs, cur = [], []

    def edge(a, b):
        lo, hi = 0.0, 1.0
        ka = keep(a)
        for _ in range(40):
            m = (lo + hi) / 2
            if keep(lerp(a, b, m)) == ka:
                lo = m
            else:
                hi = m
        return lerp(a, b, lo)

    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int(dist(a, b) / 2))
        prev = a
        if i == 0 and keep(a):
            cur = [a]
        for k in range(1, n + 1):
            q = lerp(a, b, k / n)
            if keep(prev) and not keep(q):
                cur.append(edge(prev, q)); runs.append(cur); cur = []
            elif not keep(prev) and keep(q):
                cur = [edge(q, prev)]
            prev = q
        if keep(b) and cur:
            cur.append(b)
    if cur:
        runs.append(cur)
    if closed and len(runs) > 1 and keep(pts[0]):
        runs[0] = runs[-1][:-1] + runs[0]
        runs.pop()
    out = []
    for r_ in runs:
        clean = [r_[0]]
        for p in r_[1:]:
            if dist(p, clean[-1]) > 0.01:
                clean.append(p)
        if len(clean) > 1 and sum(dist(clean[j], clean[j + 1]) for j in range(len(clean) - 1)) > 6:
            out.append(clean)
    return out


def off_slash(p, gap=28):
    return abs(p[1] - p[0]) / math.sqrt(2) >= gap


def slashed(segs_list, gap=28, closed=True):
    """Trim arc/line outlines away from the standard slash."""
    out = []
    for segs in segs_list:
        runs, whole = trim(segs, lambda p: off_slash(p, gap), closed=closed)
        out += [P(segs_d(r)) for r in runs]
    return out


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def gear_path(c, r_root, r_tip, n, phase=0):
    step = 360 / n
    hr, ht = step * 0.3, step * 0.17
    pts = []
    for i in range(n):
        t = phase + i * step
        pts.append((polar(c, r_root, t - hr), polar(c, r_tip, t - ht), polar(c, r_tip, t + ht), polar(c, r_root, t + hr)))
    d = 'M' + pt(pts[0][0])
    for i, (a, b, cc, dd) in enumerate(pts):
        if i:
            d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(pts[0][0])} Z'
    return d


def sparkle_path(c, s):
    q = lambda x, y: pt((c[0] + (x - 128) * s, c[1] + (y - 128) * s))
    return (f'M{q(128, 32)} C{q(136, 96)} {q(160, 120)} {q(224, 128)} C{q(160, 136)} {q(136, 160)} {q(128, 224)} '
            f'C{q(120, 160)} {q(96, 136)} {q(32, 128)} C{q(96, 120)} {q(120, 96)} {q(128, 32)} Z')


def badge(kind):
    """Small mark around B (same marks as the chat/bell/envelope badge families). Returns (roles, clearance)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'x':
        b['line'] = [L(BX - 20, BY - 20, BX + 20, BY + 20), L(BX + 20, BY - 20, BX - 20, BY + 20)]
        cr = 54
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), PL(T([(-20, 8), (0, 28), (20, 8)]))]
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'bitcoin':
        x0 = BX - 14
        b['line'] = [P(f'M{x0 - 8} {BY - 26} H{BX + 2} A13 13 0 0 1 {BX + 2} {BY} H{x0}'),
                     P(f'M{x0} {BY} H{BX + 5} A13 13 0 0 1 {BX + 5} {BY + 26} H{x0 - 8}'),
                     L(x0, BY - 26, x0, BY + 26),
                     L(BX - 4, BY - 38, BX - 4, BY - 26), L(BX - 4, BY + 26, BX - 4, BY + 38)]
        cr = 62
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.34)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 58
    elif kind == 'lightning':
        bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bolt)]
        b['area'] = [PG(bolt)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        import re
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(b_)) for a, b_ in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'question':
        b['line'] = [P(f'M{BX - 18} {BY - 20} A18 18 0 1 1 {BX + 6} {BY - 3} C{BX + 1} {BY} {BX} {BY + 3} {BX} {BY + 8}')]
        b['dot'] = [C(BX, BY + 32, 14)]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'star':
        st = [polar((BX, BY + 3), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 60
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    elif kind == 'pencil':
        u, n = (math.sqrt(.5), -math.sqrt(.5)), (math.sqrt(.5), math.sqrt(.5))
        at_ = lambda a, w: (BX + u[0] * a + n[0] * w, BY + u[1] * a + n[1] * w)
        pen = [at_(-32, 0), at_(-14, 12), at_(26, 12), at_(26, -12), at_(-14, -12)]
        b['line'] = [PG(pen)]
        b['area'] = [PG(pen)]
        cr = 58
    elif kind == 'lock':
        body = R(BX - 28, BY - 4, 56, 40, 8)
        b['line'] = [body, P(f'M{BX - 15} {BY - 4} V{BY - 18} A15 15 0 0 1 {BX + 15} {BY - 18} V{BY - 4}')]
        b['area'] = [body]
        cr = 62
    elif kind == 'sparkle':
        sp = sparkle_path(B, 0.4)
        b['line'] = [P(sp)]
        b['area'] = [P(sp)]
        cr = 60
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, []) + list(v)
    return out


# ================================================================ image base (exact geometry of image.svg)
IMG = load('image')
IMG_RECT = rrect_segs(32, 48, 192, 160, 14)
MTN = [(44, 188), (96, 136), (144, 184), (168, 160), (212, 204)]
SUN, SUN_R = (168, 100), 16
assert IMG['detail'] == [PL(MTN), C(*SUN, SUN_R)]


def image_badge(name, tags, kind):
    b, cr = badge(kind)
    ln, ar = carve(IMG_RECT, B, cr)
    mt = clip_polyline(MTN, lambda p: dist(p, B) >= cr + 12)
    sun = SUN if dist(SUN, B) - SUN_R - 8 >= cr + 8 else (152, 96)
    icon(name, MD, tags, **merge(dict(line=[P(ln)], area=[P(ar)], detail=[PL(m) for m in mt] + [C(*sun, SUN_R)]), b))


for nm, kind, tags in [
    ('image-arrow-down', 'arrow-down', ['download image', 'save photo', 'picture', 'download', 'arrow down']),
    ('image-arrow-up', 'arrow-up', ['upload image', 'gallery upload', 'photo', 'share', 'photo upload']),
    ('image-bitcoin', 'bitcoin', ['image', 'bitcoin', 'crypto']),
    ('image-check', 'check', ['photo approved', 'image', 'verified', 'picture', 'image approved']),
    ('image-code', 'code', ['image', 'code', 'developer', 'embed']),
    ('image-currency-dollar', 'dollar', ['image', 'dollar', 'price', 'money']),
    ('image-gear', 'gear', ['image', 'settings', 'configure']),
    ('image-heart', 'heart', ['image', 'favorite', 'like', 'love']),
    ('image-lightning', 'lightning', ['image', 'fast', 'power', 'instant']),
    ('image-lock', 'lock', ['private image', 'locked', 'picture', 'lock']),
    ('image-magnifying-glass', 'magnifying-glass', ['image search', 'find photo', 'lookup', 'picture']),
    ('image-minus', 'minus', ['image minus', 'remove', 'subtract', 'image', 'photo']),
    ('image-pause', 'pause', ['image', 'paused', 'hold']),
    ('image-pencil', 'pencil', ['edit image', 'photo edit', 'pencil', 'picture']),
    ('image-plus', 'plus', ['add photo', 'upload image', 'new picture', 'new image', 'picture']),
    ('image-push-pin', 'push-pin', ['image', 'pin', 'pinned']),
    ('image-question', 'question', ['unknown image', 'photo', 'question', 'help']),
    ('image-share', 'share', ['share image', 'send photo', 'picture', 'arrow']),
    ('image-sparkle', 'sparkle', ['ai image', 'generate image', 'photo', 'sparkle', 'generate']),
    ('image-star', 'star', ['image', 'favorite', 'starred', 'featured']),
    ('image-warning', 'warning', ['image', 'warning', 'alert', 'error']),
    ('image-x', 'x', ['delete image', 'remove', 'picture', 'x', 'remove photo']),
]:
    image_badge(nm, tags, kind)


def mini_image(x0, y0, x1, y1, rx=12):
    """The image icon mapped into a smaller box (frame, mountain, sun)."""
    sx, sy = (x1 - x0) / 192, (y1 - y0) / 160
    m = lambda p: (x0 + (p[0] - 32) * sx, y0 + (p[1] - 48) * sy)
    return R(x0, y0, x1 - x0, y1 - y0, rx), [m(p) for p in MTN], m(SUN)


# image-slash: outline and landscape trimmed clear of the slash
mt = clip_polyline(MTN, lambda p: off_slash(p, 24))
icon('image-slash', MD, ['image off', 'no image', 'picture', 'slash', 'hide image'],
     line=slashed([IMG_RECT]) + [PL(m) for m in mt] + [C(*SUN, SUN_R), SLASH])

# image-compare: left half tinted/filled, right half outlined, divider through the frame
mt_l = clip_polyline(MTN, lambda p: p[0] <= 112)
mt_r = clip_polyline(MTN, lambda p: p[0] >= 144)
icon('image-compare', MD, ['compare', 'before after', 'split', 'picture'],
     line=[IMG['line'][0], L(128, 32, 128, 224)] + [PL(m) for m in mt_r] + [C(*SUN, SUN_R)],
     detail=[PL(m) for m in mt_l],
     area=[P('M128 48 H46 A14 14 0 0 0 32 62 V194 A14 14 0 0 0 46 208 H128 Z')])

# image-broken: the picture torn in two along a zigzag, the pieces pulled apart
ZZ = [(132, 48), (148, 88), (124, 128), (144, 168), (124, 208)]
GAP = 40
ZR = [(x + GAP, y) for x, y in ZZ]
left_d = f'M{pt(ZZ[0])} H46 A14 14 0 0 0 32 62 V194 A14 14 0 0 0 46 208 H{f(ZZ[-1][0])} ' + \
    ' '.join(f'L{pt(p)}' for p in ZZ[-2::-1]) + ' Z'
right_d = f'M{pt(ZR[0])} H210 A14 14 0 0 1 224 62 V194 A14 14 0 0 1 210 208 H{f(ZR[-1][0])} ' + \
    ' '.join(f'L{pt(p)}' for p in ZR[-2::-1]) + ' Z'


def zz_x(y, pts):
    for a, b in zip(pts, pts[1:]):
        if a[1] <= y <= b[1]:
            return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
    return pts[-1][0]


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def poly_dist(p, pts):
    return min(seg_dist(p, a, b) for a, b in zip(pts, pts[1:]))


mt_bl = clip_polyline(MTN, lambda p: p[0] < zz_x(p[1], ZZ) and poly_dist(p, ZZ) >= 26)
mt_br = clip_polyline(MTN, lambda p: p[0] > zz_x(p[1], ZR) and poly_dist(p, ZR) >= 26)
icon('image-broken', MD, ['broken image', 'missing', 'error', 'picture', 'photo'],
     line=[P(left_d), P(right_d)], area=[P(left_d), P(right_d)],
     detail=[PL(m) for m in mt_bl + mt_br] + [C(76, 96, SUN_R)])

# image-scan: a smaller picture inside scan corners
CORNERS = load('frame-corners')['line'][:4]
fr, mt, sun = mini_image(72, 84, 184, 172, 12)
icon('image-scan', MD, ['image recognition', 'scan', 'photo', 'detect'],
     line=CORNERS + [fr], area=[fr],
     detail=[PL([(84, 160), (112, 132), (140, 160)]), PL([(132, 152), (148, 136), (172, 160)])],
     dotcut=[C(152, 110, 14)])

# image-resize: a small picture in the corner of a larger outline, arrow to the far corner
small = R(32, 128, 96, 80, 12)
icon('image-resize', MD, ['resize image', 'scale', 'picture', 'dimensions'],
     line=[P('M32 96 V62 A14 14 0 0 1 46 48 H210 A14 14 0 0 1 224 62 V194 A14 14 0 0 1 210 208 H160'), small,
           L(156, 100, 192, 64), PL([(152, 64), (192, 64), (192, 104)])],
     area=[small], dotcut=[C(98, 158, 14)])

# images: two overlapping pictures
front = R(64, 80, 160, 128, 14)
f_mtn = [(74, 196), (112, 158), (146, 192), (166, 172), (214, 220)]
icon('images', MD, ['gallery', 'photos', 'album', 'pictures', 'multiple images'],
     line=[front, P('M32 176 V62 A14 14 0 0 1 46 48 H178 A14 14 0 0 1 192 62')],
     area=[front],
     detail=[PL(clip_polyline(f_mtn, lambda p: p[1] <= 200)[0]), C(176, 120, 14)])

# images-carousel: a picture card with cards peeking out on both sides
card = R(72, 48, 112, 160, 14)
icon('images-carousel', MD, ['carousel', 'slideshow', 'gallery'],
     line=[card, L(32, 80, 32, 176), L(224, 80, 224, 176)], area=[card],
     detail=[PL([(84, 188), (116, 156), (140, 180), (152, 168), (172, 188)])], dotcut=[C(144, 100, 14)])

# instant-photo: square print with a thick bottom border
inst = R(48, 32, 160, 192, 16)
win = R(80, 64, 96, 96, 6)
icon('instant-photo', MD, ['instant photo', 'snapshot', 'print', 'photo'],
     line=[inst], area=[inst], detail=[win], hole=[win])

# ================================================================ focus family (frame-corners brackets)
icon('focus', MD, ['focus', 'center focus', 'autofocus', 'camera', 'frame'],
     line=CORNERS + [C(128, 128, 40)], area=[C(128, 128, 40)])
icon('focus-center', MD, ['focus', 'center', 'target', 'camera'],
     line=CORNERS, dot=[C(128, 128, 36)])
icon('focus-auto', MD, ['autofocus', 'camera', 'af', 'focus'],
     line=CORNERS + [PL([(92, 180), (128, 76), (164, 180)]), L(105, 144, 151, 144)])
icon('focus-plus', IF, ['focus', 'add', 'frame', 'corners'],
     line=CORNERS + [L(128, 88, 128, 168), L(88, 128, 168, 128)])
ring = [('A', (128, 128), 40, -math.pi, math.pi)]
icon('focus-slash', MD, ['capture', 'disabled', 'off', 'media'],
     line=CORNERS + slashed([ring], 26, closed=True) + [L(72, 72, 184, 184)])
icon('live-view', MD, ['live view', 'preview', 'camera', 'broadcast'],
     line=CORNERS + [C(128, 108, 28), P('M80 184 A48 48 0 0 1 176 184')],
     area=[C(128, 108, 28), P('M80 184 A48 48 0 0 1 176 184 Z')])

# ================================================================ lightning family
BOLT = [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]
icon('lightning-slash', MD, ['flash off', 'no flash', 'lightning', 'disable', 'power off'],
     line=[PL(r) for r in clip_polyline(BOLT, off_slash, closed=True)] + [SLASH])

sbolt = [(40 + (x - 56) * 0.75, y) for x, y in BOLT]
icon('flash-auto', MD, ['flash auto', 'camera flash', 'automatic', 'lightning', 'auto flash'],
     line=[PG(sbolt), PL([(160, 216), (188, 144), (216, 216)]), L(169.3, 192, 206.7, 192)],
     area=[PG(sbolt)])

# ================================================================ flare
fc = (120, 120)
rays = []
for i, (r1, r2) in enumerate([(52, 88), (52, 72), (52, 88), (52, 58), (52, 80), (52, 66), (52, 88), (52, 72)]):
    a = -90 + i * 45
    rays.append(L(*polar(fc, r1, a), *polar(fc, r2, a)))
icon('flare', MD, ['lens flare', 'sparkle', 'light', 'camera'],
     line=[C(*fc, 28), C(196, 196, 18)] + rays, area=[C(*fc, 28), C(196, 196, 18)])

# ================================================================ forward-10
fcen, fr_ = (128, 136), 88
fend = polar(fcen, fr_, -45)
icon('forward-10', MD, ['forward 10 seconds', 'skip', 'ahead', 'video'],
     line=[P(f'M{pt(polar(fcen, fr_, 0))} A{fr_} {fr_} 0 1 1 {pt(fend)}'),
           PL([(fend[0] - 36, fend[1]), fend, (fend[0], fend[1] - 36)]),
           PL([(86, 120), (100, 108), (100, 168)]), R(132, 108, 40, 60, 20)])

# ================================================================ glasses-3d
lens_l = R(32, 92, 84, 80, 16)
lens_r = R(140, 92, 84, 80, 16)
icon('glasses-3d', MD, ['3d glasses', 'cinema', 'movie', 'stereoscopic', 'stereo'],
     line=[lens_l, lens_r, P('M116 116 A12 12 0 0 1 140 116'), L(44, 92, 56, 64), L(212, 92, 200, 64)],
     area=[lens_l])

# ================================================================ guitar
c1, r1, c2, r2 = (88, 168), 56, (134, 122), 38
pu, pl = circle_x(c1, r1, c2, r2)
body = (f'M{pt(pu)} ' + arc_to(c1, r1, pu, pl, lambda m: dist(m, c2)) + ' ' + arc_to(c2, r2, pl, pu, lambda m: dist(m, c1))
        + ' Z')
u = (math.sqrt(.5), -math.sqrt(.5))
neck0 = polar(c2, r2, -45)
head_c = (196, 60)
icon('guitar', MD, ['guitar', 'instrument', 'music'],
     line=[P(body), L(*neck0, 176, 80), P(capsule(head_c, 10, 14, u))],
     area=[P(body), P(capsule(head_c, 10, 14, u))],
     detail=[C(116, 140, 14), L(60, 168, 88, 196)])

# ================================================================ guitar-pick
pick = 'M128 220 C100 200 40 140 40 92 C40 54 84 36 128 36 C172 36 216 54 216 92 C216 140 156 200 128 220 Z'
icon('guitar-pick', MD, ['guitar pick', 'plectrum', 'music', 'rock'], line=[P(pick)], area=[P(pick)])

# ================================================================ headphones-slash
H_ = math.pi / 2
band = [('L', (40, 176), (40, 136)), ('A', (128, 136), 88, 2 * H_, 4 * H_), ('L', (216, 136), (216, 176))]
runs = []
for segs, cl in ((band, False), (rrect_segs(40, 144, 48, 80, 16), True), (rrect_segs(168, 144, 48, 80, 16), True)):
    rr, _ = trim(segs, lambda p: off_slash(p, 28), closed=cl)
    runs += [P(segs_d(r)) for r in rr if sum(dist(seg_point(x, 0), seg_end(x)) for x in r) > 30]
icon('headphones-slash', MD, ['headphones off', 'mute', 'audio', 'slash', 'no audio'], line=runs + [SLASH])

# ================================================================ library
LIB_FRONT = R(32, 96, 128, 128, 14)
LIB_BACK = [P('M64 64 H178 A14 14 0 0 1 192 78 V192'), P('M96 32 H210 A14 14 0 0 1 224 46 V160')]


def library(name, tags, det):
    icon(name, MD, tags, line=[LIB_FRONT] + LIB_BACK, area=[LIB_FRONT], detail=det)


library('library', ['library', 'collection', 'media', 'stack'], [PG([(80, 132), (124, 160), (80, 188)])])
library('library-plus', ['add to library', 'collection', 'add', 'stack', 'library plus'],
        [L(96, 132, 96, 188), L(68, 160, 124, 160)])
library('library-check', ['added to library', 'collection', 'saved', 'stack'],
        [PL([(68, 162), (88, 182), (124, 146)])])
library('library-minus', ['library minus', 'remove', 'subtract', 'library', 'collection'], [L(68, 160, 124, 160)])

# ================================================================ live photo
dashes = []
dash_mid = []
for i in range(10):
    a = i * 36 + 18
    dash_mid.append(polar((128, 128), 92, a))
    dashes.append(P(f'M{pt(polar((128, 128), 92, a - 4))} A92 92 0 0 1 {pt(polar((128, 128), 92, a + 4))}'))
icon('live-photo', MD, ['live photo', 'motion', 'concentric', 'camera'],
     line=dashes + [C(128, 128, 52)], area=[C(128, 128, 52)], dotcut=[C(128, 128, 26)])
icon('live-photo-slash', MD, ['live photo', 'off', 'disabled', 'hidden', 'live'],
     line=[d for d, m in zip(dashes, dash_mid) if off_slash(m, 30)]
     + slashed([[('A', (128, 128), 52, -math.pi, math.pi)]], 26) + [SLASH])

# ================================================================ lullaby
mc1, mr1, mc2, mr2 = (104, 152), 72, (152, 104), 58
mu, ml = circle_x(mc1, mr1, mc2, mr2)
moon = (f'M{pt(mu)} ' + arc_to(mc1, mr1, mu, ml, lambda m: dist(m, mc2)) + ' '
        + arc_to(mc2, mr2, ml, mu, lambda m: -dist(m, mc1)) + ' Z')
icon('lullaby', MD, ['sleep music', 'baby', 'bedtime'],
     line=[P(moon), L(200, 112, 200, 40), P('M200 40 C216 44 228 56 222 76')],
     area=[P(moon)], dot=[C(184, 116, 20)])

# ================================================================ lyrics
CHAT_D = load('chat')['line'][0]
icon('lyrics', MD, ['lyrics', 'song text', 'karaoke', 'music'],
     line=[CHAT_D], area=[CHAT_D],
     detail=[L(128, 156, 128, 88), P('M128 88 C148 92 164 104 158 128')], dotcut=[C(114, 156, 20)])

print(save(overwrite=True))
