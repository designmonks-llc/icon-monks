import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

EM = 'Emoji'

# ================================================================ small outline engine (same as batch 113)
# ================================================================ small outline engine
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1)  (angles in radians, a1 may be < a0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    if s[0] == 'C':
        p0, c1, c2, p1 = s[1:]
        a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
        d, e = lerp(a, b, t), lerp(b, c, t)
        return lerp(d, e, t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def split_cubic(p0, c1, c2, p1, t):
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p1)


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    if s[0] == 'C':
        _, right = split_cubic(*s[1:], t0)
        if t1 >= 1:
            return ('C',) + right
        left, _ = split_cubic(*right, (t1 - t0) / (1 - t0))
        return ('C',) + left
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []  # (seg index, t0, t1)
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


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])




def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, []) + list(v)
    return out


def scale_path(d, s, c_from, c_to):
    import re
    toks = re.findall(r'[A-Za-z]|-?[\d.]+', d)
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            out.append(t); i += 1
        else:
            x, y = float(t), float(toks[i + 1])
            out.append(pt((c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s))); i += 2
    return ' '.join(out)


# ================================================================ the face (exact geometry of icons/smiley.svg)
FC, FR = (128, 128), 96
FACE = C(128, 128, 96)
EYES = [C(96, 108, 16), C(160, 108, 16)]
SMILE = P('M88 152 A48 48 0 0 0 168 152')
FROWN = P('M88 176 A48 48 0 0 1 168 176')


def face_segs(start_deg):
    a0 = math.radians(start_deg)
    return [('A', FC, FR, a0, a0 + 2 * math.pi)]


def face(**kw):
    return merge(dict(line=[FACE], area=[FACE]), kw)


def swirl(c, r=22):
    """Spiral eye: a half turn of radius r/2 out of the centre, then most of a turn at radius r."""
    end = polar(c, r, 225)
    return P(f'M{pt(c)} A{f(r / 2)} {f(r / 2)} 0 0 1 {f(c[0] + r)} {f(c[1])} A{f(r)} {f(r)} 0 1 1 {pt(end)}')


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


# ================================================================ badge marks around B (shared with batches 113/114)
B = (184, 184)
BX, BY = B


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


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


def badge(kind):
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
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
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
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
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'pencil':
        u, n = (math.sqrt(.5), -math.sqrt(.5)), (math.sqrt(.5), math.sqrt(.5))
        at_ = lambda a, w: (BX + u[0] * a + n[0] * w, BY + u[1] * a + n[1] * w)
        pen = [at_(-32, 0), at_(-14, 12), at_(26, 12), at_(26, -12), at_(-14, -12)]
        b['line'] = [PG(pen)]
        b['area'] = [PG(pen)]
        cr = 58
    elif kind == 'sparkle':
        sp = P(scale_path(load('sparkle')['line'][0].split('d="')[1].split('"')[0], 0.36, (128, 128), B))
        b['line'] = [sp]
        b['area'] = [sp]
        cr = 64
    else:
        raise ValueError(kind)
    return b, cr


# features of the face nudged up and left so the badge has clear space
BF_EYES = [C(84, 96, 16), C(140, 96, 16)]
BF_MOUTH = P('M80 136 A40 40 0 0 0 144 136')


def smiley_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(face_segs(-135), B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=[BF_MOUTH], dotcut=BF_EYES), b)


for suffix, kind, tags in [
    ('arrow-up', 'arrow-up', ['smiley', 'upload', 'up', 'increase']),
    ('bitcoin', 'bitcoin', ['smiley', 'bitcoin', 'crypto']),
    ('check', 'check', ['smiley', 'check', 'done', 'approved']),
    ('currency-dollar', 'dollar', ['smiley', 'dollar', 'price', 'money']),
    ('gear', 'gear', ['smiley', 'settings', 'configure']),
    ('magnifying-glass', 'magnifying-glass', ['smiley', 'search', 'find']),
    ('minus', 'minus', ['smiley', 'remove', 'subtract']),
    ('pencil', 'pencil', ['smiley', 'edit', 'write']),
    ('plus', 'plus', ['add reaction', 'emoji', 'react', 'smiley', 'smiley plus']),
    ('push-pin', 'push-pin', ['smiley', 'pin', 'pinned']),
    ('share', 'share', ['smiley', 'share', 'send']),
    ('sparkle', 'sparkle', ['smiley', 'ai', 'magic', 'smart']),
]:
    icon(f'smiley-{suffix}', EM, tags, **smiley_badge(kind))

# ================================================================ expressions
icon('smiley-angry', EM, ['angry', 'mad', 'emoji', 'face', 'frustrated'],
     **face(detail=[L(80, 84, 112, 100), L(176, 84, 144, 100), P('M96 184 A40 40 0 0 1 160 184')],
            dotcut=[C(96, 128, 16), C(160, 128, 16)]))

ang_mouth = P('M92 188 C92 164 108 156 128 156 C148 156 164 164 164 188 Z')
icon('smiley-anguished', EM, ['anguish', 'distress', 'emoji', 'face'],
     **face(detail=[L(76, 100, 108, 84), L(180, 100, 148, 84), ang_mouth], hole=[ang_mouth],
            dotcut=[C(96, 124, 16), C(160, 124, 16)]))

icon('smiley-annoyed', EM, ['annoyed', 'irritated', 'emoji', 'face'],
     **face(detail=[L(78, 96, 114, 100), L(178, 96, 142, 100), L(100, 172, 156, 172)],
            dotcut=[C(96, 128, 16), C(160, 128, 16)]))

icon('smiley-blank', EM, ['no mouth', 'speechless', 'blank', 'face', 'no words'],
     **face(dotcut=[C(96, 124, 16), C(160, 124, 16)]))

icon('smiley-confused', EM, ['confused', 'unsure', 'emoji', 'face', 'puzzled'],
     **face(detail=[P('M84 172 C100 148 112 148 128 164 C144 180 156 180 172 156')], dotcut=EYES))

lens_l = P('M60 100 H116 V112 C116 132 104 144 88 144 C72 144 60 132 60 112 Z')
lens_r = P('M196 100 H140 V112 C140 132 152 144 168 144 C184 144 196 132 196 112 Z')
icon('smiley-cool', EM, ['cool', 'sunglasses', 'emoji', 'face'],
     **face(detail=[lens_l, lens_r, L(116, 104, 140, 104), P('M100 176 A40 40 0 0 0 156 176')],
            hole=[lens_l, lens_r]))

tear = P('M76 128 C76 128 64 144 64 154 A12 12 0 0 0 88 154 C88 144 76 128 76 128 Z')
icon('smiley-cry', EM, ['crying', 'tears', 'sad', 'emoji', 'tear'],
     **face(detail=[P('M100 184 A40 40 0 0 1 164 184'), tear], hole=[tear], dotcut=[C(96, 108, 16), C(160, 108, 16)]))

icon('smiley-dizzy', EM, ['dizzy', 'confused', 'emoji', 'face', 'spiral eyes'],
     **face(detail=[swirl((86, 108)), swirl((162, 108)), P('M100 172 C116 160 132 176 156 164')]))

icon('smiley-expressionless', EM, ['expressionless', 'blank', 'emoji', 'face'],
     **face(detail=[L(80, 112, 112, 112), L(144, 112, 176, 112), L(96, 164, 160, 164)]))

# glance: eye rings with the pupils rolled to the right
ring_l, ring_r = E(92, 112, 22, 20), E(164, 112, 22, 20)
icon('smiley-glance', EM, ['side eye', 'looking', 'glance'],
     **face(detail=[ring_l, ring_r, P('M112 168 A40 40 0 0 0 164 160')], dotcut=[C(104, 112, 14), C(176, 112, 14)]))

icon('smiley-grimace', EM, ['grimace', 'awkward', 'emoji', 'teeth'],
     **face(detail=[R(76, 144, 104, 44, 20), L(110.67, 144, 110.67, 188), L(145.33, 144, 145.33, 188)], dotcut=EYES))

grin = P('M72 136 H184 C184 172 160 196 128 196 C96 196 72 172 72 136 Z')
icon('smiley-grin', EM, ['grin', 'happy', 'emoji', 'beam', 'very happy'],
     **face(detail=[grin, L(76, 162, 180, 162)], dotcut=[C(96, 96, 16), C(160, 96, 16)]))

HAPPY_EYES = [P('M80 112 A16 16 0 0 1 112 112'), P('M144 112 A16 16 0 0 1 176 112')]
icon('smiley-happy', EM, ['happy', 'joy', 'smiling eyes', 'emoji', 'grin'],
     **face(detail=HAPPY_EYES + [SMILE]))

hl, hr_ = P(heart_path((92, 110), 0.2)), P(heart_path((164, 110), 0.2))
icon('smiley-heart', EM, ['love', 'heart eyes', 'adore', 'emoji'],
     **face(detail=[hl, hr_, SMILE], hole=[hl, hr_]))

o_mouth = E(128, 174, 18, 20)
icon('smiley-hypnotized', EM, ['hypnotized', 'dazed', 'emoji', 'spiral'],
     **face(detail=[swirl((86, 104)), swirl((162, 104)), o_mouth], hole=[o_mouth]))

icon('smiley-kid', EM, ['kid', 'child', 'face', 'baby'],
     **face(detail=[P('M128 32 A28 28 0 0 0 128 88 A14 14 0 0 0 128 60'), P('M96 164 A40 40 0 0 0 160 164')],
            dotcut=[C(96, 132, 16), C(160, 132, 16)]))

icon('smiley-kiss', EM, ['kiss', 'love', 'emoji', 'face'],
     **face(detail=[P('M116 140 C148 140 148 168 124 168 C148 168 148 196 116 196')], dotcut=EYES))

laugh = P('M72 132 H184 C184 172 160 196 128 196 C96 196 72 172 72 132 Z')
icon('smiley-laugh', EM, ['laugh', 'happy', 'grin', 'joy', 'xd'],
     **face(detail=[P('M80 100 A16 16 0 0 1 112 100'), P('M144 100 A16 16 0 0 1 176 100'), laugh], hole=[laugh]))

melt = ('M52 128 A76 76 0 0 1 204 128 V148 C204 172 224 180 224 198 C224 210 216 216 206 216 H50 '
        'C38 216 32 210 32 202 C32 190 52 186 52 170 Z')
icon('smiley-melting', EM, ['melting', 'embarrassed', 'overwhelmed'],
     line=[P(melt)], area=[P(melt)], detail=[P('M92 160 C112 176 140 176 164 164')],
     dotcut=[C(100, 116, 16), C(156, 124, 16)])

icon('smiley-nerd', EM, ['nerd', 'glasses', 'geek', 'emoji'],
     **face(detail=[C(92, 112, 26), C(164, 112, 26), L(118, 112, 138, 112), P('M96 164 A40 40 0 0 0 160 164')]))

icon('smiley-pout', EM, ['pout', 'sulk', 'annoyed', 'emoji'],
     **face(detail=[P('M108 180 A28 28 0 0 1 148 180'), L(80, 108, 112, 108), L(144, 108, 176, 108)],
            dotcut=[C(96, 124, 16), C(160, 124, 16)]))

icon('smiley-puzzled', EM, ['puzzled', 'thinking', 'face', 'emoji'],
     **face(detail=[P('M140 84 A24 24 0 0 1 180 80'), L(80, 96, 112, 96), L(100, 168, 160, 156)],
            dotcut=[C(96, 124, 16), C(160, 116, 16)]))

icon('smiley-relieved', EM, ['relieved', 'content', 'calm', 'emoji'],
     **face(detail=[P('M80 108 A16 16 0 0 0 112 108'), P('M144 108 A16 16 0 0 0 176 108'),
                    P('M92 156 A56 56 0 0 0 164 156')]))

icon('smiley-sick', EM, ['sick', 'ill', 'nausea', 'emoji', 'unwell'],
     **face(detail=[L(80, 116, 112, 108), L(176, 116, 144, 108), L(120, 172, 180, 140)],
            dotcut=[C(116, 174, 20)]))

icon('smiley-smirk', EM, ['smirk', 'sly', 'mischief', 'emoji'],
     **face(detail=[P('M100 168 C124 172 152 168 168 144')], dotcut=EYES))

icon('smiley-squint', EM, ['squint', 'emoji', 'face', 'laugh', 'sad'],
     **face(detail=[PL([(80, 92), (108, 108), (80, 124)]), PL([(176, 92), (148, 108), (176, 124)]), SMILE]))

icon('smiley-surprised', EM, ['surprised', 'astonished', 'wow', 'emoji', 'shock'],
     **face(detail=[o_mouth, P('M80 88 A20 20 0 0 1 112 84'), P('M144 84 A20 20 0 0 1 176 88')], hole=[o_mouth],
            dotcut=[C(96, 120, 16), C(160, 120, 16)]))

TONGUE = P('M108 152 V176 A20 20 0 0 0 148 176 V152')
icon('smiley-tongue', EM, ['tongue', 'silly', 'playful', 'emoji'],
     **face(detail=[L(84, 152, 172, 152), TONGUE], dotcut=EYES))
icon('smiley-tongue-wink', EM, ['tongue', 'wink', 'playful', 'emoji', 'tongue wink'],
     **face(detail=[L(84, 152, 172, 152), TONGUE, P('M144 112 A16 16 0 0 1 176 112')], dotcut=[C(96, 108, 16)]))

icon('smiley-unamused', EM, ['unamused', 'meh', 'bored', 'emoji', 'face'],
     **face(detail=[L(76, 100, 116, 100), L(140, 100, 180, 100), L(104, 168, 156, 164)],
            dotcut=[C(104, 116, 16), C(168, 116, 16)]))

up = rot([(88, 152), (168, 152)], 180)
icon('smiley-upside-down', EM, ['upside down', 'silly', 'emoji', 'sarcasm', 'face'],
     **face(detail=[P(f'M{pt(up[0])} A48 48 0 0 0 {pt(up[1])}')], dotcut=[C(160, 148, 16), C(96, 148, 16)]))

# ================================================================ eyes, ghost, poop
icon('eyes', EM, ['eyes', 'look', 'watching', 'see'],
     detail=[], line=[E(78, 128, 34, 64), E(178, 128, 34, 64)], area=[E(78, 128, 34, 64), E(178, 128, 34, 64)],
     dotcut=[C(92, 140, 20), C(192, 140, 20)])

GHOST = 'M48 216 V112 A80 80 0 0 1 208 112 V216 L181.33 196 L154.67 216 L128 196 L101.33 216 L74.67 196 Z'
icon('ghost-slash', EM, ['ghost', 'off', 'disabled', 'hidden'],
     line=[P(GHOST), L(48, 48, 208, 208)], dot=[C(156, 112, 16)])

poop = ('M64 216 H192 A24 24 0 0 0 192 168 H170 A22 22 0 0 0 170 124 H148 A20 20 0 0 0 148 84 '
        'C148 60 136 48 120 40 C124 56 116 76 108 84 A20 20 0 0 0 108 124 H86 A22 22 0 0 0 86 168 H64 '
        'A24 24 0 0 0 64 216 Z')
icon('poop', EM, ['poop', 'poo', 'emoji', 'joke'], line=[P(poop)], area=[P(poop)])

# ================================================================ face with a mark at the top right (outline opened around it)
TR = (196, 60)


def face_top_right(mark_line, cut_r, mark_area=(), **kw):
    ln, ar = carve(face_segs(135), TR, cut_r)
    return merge(dict(line=[P(ln)] + list(mark_line), area=[P(ar)] + list(mark_area)), kw)


drop = P('M196 30 C196 30 180 52 180 64 A16 16 0 0 0 212 64 C212 52 196 30 196 30 Z')
icon('smiley-nervous', EM, ['nervous', 'anxious', 'awkward', 'face', 'emoji'],
     **face_top_right([drop], 46, [drop],
                      detail=[P('M84 168 C100 152 112 152 128 164 C144 176 156 176 172 160')],
                      dotcut=[C(92, 112, 16), C(152, 112, 16)]))

note = [L(204, 32, 204, 76), P('M204 32 C212 40 220 40 224 48')]
sing_mouth = E(116, 168, 18, 22)
icon('smiley-sing', EM, ['sing', 'singing', 'face', 'emoji', 'music'],
     **face_top_right(note, 46, detail=[P('M68 116 A16 16 0 0 0 100 116'), P('M128 116 A16 16 0 0 0 160 116'), sing_mouth],
                      hole=[sing_mouth], dot=[C(192, 76, 16)]))

# ================================================================ slash
SLASH = L(48, 48, 208, 208)


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


_sc = (128, 152 - math.sqrt(48 ** 2 - 40 ** 2))
smile_segs = [('A', _sc, 48, ang(_sc, (88, 152)), ang(_sc, (168, 152)) - 0)]
smile_segs = [('A', _sc, 48, ang(_sc, (88, 152)), ang(_sc, (168, 152)))]
runs, _ = trim(smile_segs, lambda p: seg_dist(p) >= 30, closed=False)
icon('smiley-slash', EM, ['smiley slash', 'off', 'disabled', 'emoji', 'face'],
     line=[FACE, SLASH] + [P(segs_d(r)) for r in runs], dot=[C(160, 108, 16)])

# ================================================================ sticker: lower right corner peeled up along a fold
SA, SB = polar(FC, FR, -4), polar(FC, FR, 94)
fold_c = (2 * 183.65 - 128, 2 * 183.65 - 128)
icon('smiley-sticker', EM, ['sticker', 'emoji', 'reaction'],
     line=[P(f'M{pt(SA)} A96 96 0 1 0 {pt(SB)} Z')], area=[P(f'M{pt(SA)} A96 96 0 1 0 {pt(SB)} Z')],
     detail=[P(f'M{pt(SA)} A96 96 0 0 1 {pt(SB)}'), BF_MOUTH], dotcut=BF_EYES)

# ================================================================ talking: a slightly smaller face with speech dashes
TC, TRR = (108, 128), 76
tk = TRR / 96
icon('smiley-talking', EM, ['talking', 'chatting', 'speaking'],
     line=[C(*TC, TRR)] + [L(*polar(TC, 100, a), *polar(TC, 116, a)) for a in (-36, 0, 36)],
     area=[C(*TC, TRR)], detail=[E(108, 164, 14, 16)], hole=[E(108, 164, 14, 16)],
     dotcut=[C(84, 112, 14), C(132, 112, 14)])

# ================================================================ thinking: a fist under the chin, index finger up to the chin
FIST = capsule((92, 204), 20, 16, (1, 0))
FINGER = L(128, 192, 144, 172)


def hand_dist(p):
    d1 = max(math.hypot(max(abs(p[0] - 92) - 20, 0), p[1] - 204) - 16, 0)
    return min(d1, seg_dist(p, (128, 192), (144, 172)))


th_runs, _ = trim(face_segs(-45), lambda p: hand_dist(p) >= 28)
icon('smiley-thinking', EM, ['thinking', 'pondering', 'hmm'],
     line=[P(segs_d(r)) for r in th_runs] + [P(FIST), FINGER],
     area=[P(segs_d(th_runs[0]) + ' Z'), P(FIST)],
     detail=[P('M144 80 A20 20 0 0 1 180 84'), L(124, 148, 168, 140)],
     dotcut=[C(96, 108, 16), C(160, 112, 16)])

print(save(overwrite=True))
