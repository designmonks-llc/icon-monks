import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DV = 'Devices'
TR = 'Transport'

# ================================================================ outline engine (same as batch 113, so badges match)
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


H = math.pi / 2


def rr_segs(x, y, w, h, r):
    """Closed rounded rect as segments, clockwise from the top-left corner's end."""
    return [('L', (x + r, y), (x + w - r, y)), ('A', (x + w - r, y + r), r, -H, 0),
            ('L', (x + w, y + r), (x + w, y + h - r)), ('A', (x + w - r, y + h - r), r, 0, H),
            ('L', (x + w - r, y + h), (x + r, y + h)), ('A', (x + r, y + h - r), r, H, 2 * H),
            ('L', (x, y + h - r), (x, y + r)), ('A', (x + r, y + r), r, 2 * H, 3 * H)]


def sd_rr(p, x, y, w, h, r):
    """Signed distance from p to a rounded rect outline (negative inside)."""
    cx, cy = x + w / 2, y + h / 2
    qx, qy = abs(p[0] - cx) - (w / 2 - r), abs(p[1] - cy) - (h / 2 - r)
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r


B = (184, 184)
BX, BY = B
SLASH = L(48, 48, 208, 208)


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


def cloud_path(c, s):
    """The core cloud, rebuilt at scale s centred on c."""
    o = (134, 124)
    m = lambda p: (c[0] + (p[0] - o[0]) * s, c[1] + (p[1] - o[1]) * s)
    Lc, Lr, Mc, Mr, Rc, Rr = m((84, 152)), 40 * s, m((132, 116)), 60 * s, m((180, 148)), 44 * s
    irm = circle_x(Mc, Mr, Rc, Rr)[0]
    iml = circle_x(Mc, Mr, Lc, Lr)[0]
    b0, b1 = m((84, 192)), m((180, 192))
    return (f'M{pt(b0)} L{pt(b1)} ' + arc_to(Rc, Rr, b1, irm, lambda q: dist(q, Mc)) + ' ' +
            arc_to(Mc, Mr, irm, iml, lambda q: -q[1]) + ' ' + arc_to(Lc, Lr, iml, b0, lambda q: dist(q, Mc)) + ' Z')


def badge(kind):
    """Small mark around B. Returns (roles, clearance radius); marks match batches 113/114."""
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
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'question':
        b['line'] = [P(f'M{BX - 18} {BY - 20} A18 18 0 1 1 {BX + 6} {BY - 3} C{BX + 1} {BY} {BX} {BY + 3} {BX} {BY + 8}')]
        b['dot'] = [C(BX, BY + 32, 14)]
        cr = 58
    elif kind == 'star':
        st = [polar((BX, BY + 3), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 60
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    elif kind == 'cloud':
        cp = cloud_path((BX, BY + 2), 0.4)
        b['line'] = [P(cp)]
        b['area'] = [P(cp)]
        cr = 60
    elif kind == 'wrench':
        hc, hr = (BX + 10, BY - 10), 18
        a0, a1 = polar(hc, hr, -45 + 55), polar(hc, hr, -45 - 55)
        b['line'] = [P(f'M{pt(a0)} A{hr} {hr} 0 1 1 {pt(a1)}'),
                     L(*polar(hc, hr, 135), BX - 26, BY + 26)]
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


# ================================================================ devices: a monitor with a phone in front of it
MON = (72, 32, 152, 92, 14)           # x 72..224, y 32..124
PHN = (32, 96, 80, 128, 14)           # x 32..112, y 96..224
GAP = 32                              # clearance between the phone and the monitor behind it
MON_SEGS = rr_segs(*MON)
PHN_D = R(*PHN)
PHN_DET = [L(60, 128, 84, 128)]
# expanded phone corner (top right) that bounds the monitor's area
EXC = (PHN[0] + PHN[2] - PHN[4], PHN[1] + PHN[4])   # (98, 118)
EXR = PHN[4] + GAP                                   # 46
EX_R = PHN[0] + PHN[2] + GAP                         # x = 144
EX_T = PHN[1] - GAP                                  # y = 72
EX_CLOSE = f' L{f(EX_R)} {f(EXC[1])} A{f(EXR)} {f(EXR)} 0 0 0 {f(EXC[0])} {f(EX_T)} Z'


def behind_phone(p):
    return sd_rr(p, *PHN) >= GAP


runs, _ = trim(MON_SEGS, behind_phone)
assert len(runs) == 1
MON_LINE = segs_d(runs[0])
MON_AREA = MON_LINE + EX_CLOSE
STAND = [L(184, 124, 184, 164), L(152, 164, 216, 164)]

icon('devices', DV, ['devices', 'phone and tablet', 'responsive', 'hardware', 'phone and laptop'],
     line=[P(MON_LINE)] + STAND + [PHN_D], detail=PHN_DET, area=[P(MON_AREA), PHN_D])


def devices_badge(kind):
    b, cr = badge(kind)
    # the monitor's bottom edge sits 60 above the badge centre, so no badge needs to trim it; the stand gives way
    assert BY - (MON[1] + MON[3]) >= cr
    return merge(dict(line=[P(MON_LINE), PHN_D], area=[P(MON_AREA), PHN_D], detail=PHN_DET), b)


for name, kind, tags in [
    ('devices-x', 'x', ['devices', 'remove', 'cancel', 'responsive', 'multi-device']),
    ('devices-code', 'code', ['devices', 'developer', 'code', 'responsive', 'multi-device']),
    ('devices-gear', 'gear', ['devices', 'settings', 'configure', 'responsive', 'multi-device']),
    ('devices-plus', 'plus', ['devices', 'add', 'new', 'responsive', 'multi-device']),
    ('devices-star', 'star', ['devices', 'favorite', 'starred', 'responsive', 'multi-device']),
    ('devices-check', 'check', ['devices', 'done', 'approved', 'responsive', 'multi-device']),
    ('devices-heart', 'heart', ['devices', 'favorite', 'like', 'responsive', 'multi-device']),
    ('devices-minus', 'minus', ['devices', 'remove', 'subtract', 'responsive', 'multi-device']),
    ('devices-pause', 'pause', ['devices', 'paused', 'hold', 'responsive', 'multi-device']),
    ('devices-share', 'share', ['devices', 'share', 'send', 'responsive', 'multi-device']),
    ('devices-warning', 'warning', ['devices', 'warning', 'error', 'responsive', 'multi-device']),
    ('devices-arrow-up', 'arrow-up', ['devices', 'increase', 'upload', 'responsive', 'multi-device']),
    ('devices-push-pin', 'push-pin', ['devices', 'pinned', 'pin', 'responsive', 'multi-device']),
    ('devices-question', 'question', ['devices', 'help', 'unknown', 'responsive', 'multi-device']),
    ('devices-lightning', 'lightning', ['devices', 'fast', 'power', 'responsive', 'multi-device']),
    ('devices-arrow-down', 'arrow-down', ['devices', 'decrease', 'download', 'responsive', 'multi-device']),
    ('devices-currency-dollar', 'dollar', ['devices', 'money', 'price', 'responsive', 'multi-device']),
    ('devices-magnifying-glass', 'magnifying-glass', ['devices', 'search', 'find', 'responsive', 'multi-device']),
]:
    icon(name, DV, tags, **devices_badge(kind))

icon('devices-slash', DV, ['devices', 'disabled', 'off', 'responsive', 'multi-device'],
     line=[P(MON_LINE)] + STAND + [PHN_D, SLASH], detail=PHN_DET)

# ================================================================ connectors
dp = [(32, 64), (224, 64), (224, 192), (76, 192), (32, 148)]
icon('displayport', DV, ['displayport', 'port', 'cable', 'video'],
     line=[PG(dp)], detail=[L(80, 128, 176, 128)], area=[PG(dp)])
hd = [(32, 80), (224, 80), (224, 128), (192, 176), (64, 176), (32, 128)]
icon('hdmi', DV, ['hdmi', 'port', 'cable', 'video', 'connector'],
     line=[PG(hd)], detail=[L(80, 124, 176, 124)], area=[PG(hd)])
rj = [(40, 56), (216, 56), (216, 176), (176, 176), (176, 208), (80, 208), (80, 176), (40, 176)]
RJ_PINS = [L(x, 88, x, 120) for x in (88, 128, 168)]
icon('ethernet', DV, ['ethernet', 'lan', 'network port', 'cable'], line=[PG(rj)], detail=RJ_PINS, area=[PG(rj)])
icon('ethernet-slash', DV, ['disconnected', 'ethernet', 'offline', 'network'], line=[PG(rj)] + RJ_PINS + [SLASH])

plug_body = 'M48 96 H208 V136 C208 168 184 184 160 192 H96 C72 184 48 168 48 136 Z'
icon('electrical-prong', DV, ['prong', 'plug pins', 'outlet', 'electric'],
     line=[P(plug_body), L(88, 40, 88, 96), L(168, 40, 168, 96), L(128, 64, 128, 96), L(128, 192, 128, 224)],
     area=[P(plug_body)])

# ================================================================ drones
DR_ROT = [(68, 68), (188, 68), (68, 188), (188, 188)]   # rotor guards, r 36
DR_R = 36
DR_BODY = R(100, 100, 56, 56, 14)


def drone_arm(c):
    sx, sy = (1 if c[0] > 128 else -1), (1 if c[1] > 128 else -1)
    return L(128 + sx * 24, 128 + sy * 24, *polar(c, DR_R, math.degrees(math.atan2(-sy, -sx))))


icon('drone', DV, ['drone', 'quadcopter', 'uav', 'aerial', 'flying'],
     line=[DR_BODY] + [C(*c, DR_R) for c in DR_ROT] + [drone_arm(c) for c in DR_ROT], area=[DR_BODY],
     dot=[C(*c, 11) for c in DR_ROT], dotcut=[C(128, 128, 14)])
# the slash runs along the top-left and bottom-right arms, so it stands in for them
icon('drone-slash', TR, ['drone', 'disabled', 'off', 'transport'],
     line=[DR_BODY] + [C(*c, DR_R) for c in DR_ROT] + [drone_arm(DR_ROT[1]), drone_arm(DR_ROT[2]), SLASH],
     dot=[C(*DR_ROT[1], 11), C(*DR_ROT[2], 11)])

side = [L(32, 48, 96, 48), L(160, 48, 224, 48), PL([(64, 48), (64, 84), (96, 84)]), PL([(192, 48), (192, 84), (160, 84)]),
        R(96, 64, 64, 40, 12)]
icon('drone-landing', TR, ['drone', 'landing', 'quadcopter'],
     line=side + [L(128, 140, 128, 216), PL([(92, 180), (128, 216), (164, 180)])], area=[R(96, 64, 64, 40, 12)])
icon('drone-takeoff', TR, ['drone', 'takeoff', 'quadcopter'],
     line=side + [L(128, 216, 128, 140), PL([(92, 176), (128, 140), (164, 176)])], area=[R(96, 64, 64, 40, 12)])

# ================================================================ screens and handhelds
BK = (32, 40, 144, 96, 14)            # back screen x 32..176, y 40..136
FR = (80, 88, 144, 96, 14)            # front screen x 80..224, y 88..184
runs, _ = trim(rr_segs(*BK), lambda p: sd_rr(p, *FR) >= GAP)
assert len(runs) == 1
bk_line = segs_d(runs[0])
fx0, fy0, frr = FR[0] - GAP, FR[1] - GAP, FR[4] + GAP
bk_area = bk_line + f' L{f(fx0 + frr)} {f(fy0)} A{f(frr)} {f(frr)} 0 0 0 {f(fx0)} {f(fy0 + frr)} Z'
icon('dual-screen', DV, ['dual screen', 'monitors', 'multi-monitor'],
     line=[P(bk_line), R(*FR), L(152, 184, 152, 208), L(120, 208, 184, 208)], area=[P(bk_area), R(*FR)])

TAB = R(32, 64, 192, 136, 14)
u_, n_ = (math.sqrt(.5), -math.sqrt(.5)), (math.sqrt(.5), math.sqrt(.5))
tip = (108, 168)
at_ = lambda a, w: (tip[0] + u_[0] * a + n_[0] * w, tip[1] + u_[1] * a + n_[1] * w)
pen = [tip, at_(26, 12), at_(96, 12), at_(96, -12), at_(26, -12)]
icon('drawing-tablet', DV, ['pen tablet', 'graphics tablet', 'stylus'],
     line=[TAB], detail=[PG(pen), L(*at_(26, -12), *at_(26, 12))], area=[TAB],
     dotcut=[C(64, 112, 12), C(64, 152, 12)])

ER = R(56, 32, 144, 192, 16)
icon('e-reader', DV, ['ereader', 'kindle', 'ebook', 'reader'],
     line=[ER], detail=[L(92, 76, 164, 76), L(92, 108, 164, 108), L(92, 140, 140, 140), L(112, 188, 144, 188)],
     area=[ER])

HH = R(48, 32, 160, 192, 16)
icon('handheld-console', DV, ['handheld', 'portable console', 'gaming', 'game boy'],
     line=[HH], detail=[R(80, 60, 96, 60, 8), L(76, 176, 112, 176), L(94, 158, 94, 194)],
     area=[HH], dotcut=[C(148, 186, 12), C(174, 162, 12)])

ph = R(96, 128, 64, 96, 14)
hs = []
for rr in (48, 88):
    hs.append(P(f'M{pt(polar((128, 128), rr, -135))} A{rr} {rr} 0 0 1 {pt(polar((128, 128), rr, -45))}'))
icon('hotspot', DV, ['hotspot', 'tethering', 'wifi', 'share internet'],
     line=[ph] + hs, detail=[L(118, 156, 138, 156)], area=[ph])

FT = (80, 56, 96, 144, 40)
yt = FT[1] + FT[4] - math.sqrt(FT[4] ** 2 - 16 ** 2)
yb = FT[1] + FT[3] - FT[4] + math.sqrt(FT[4] ** 2 - 16 ** 2)
icon('fitness-tracker', DV, ['fitness band', 'wearable', 'activity', 'step counter'],
     line=[R(*FT), L(104, 32, 104, yt), L(152, 32, 152, yt), L(104, yb, 104, 224), L(152, yb, 152, 224)],
     detail=[L(112, 112, 144, 112), L(112, 144, 132, 144)], area=[R(*FT)])

# ================================================================ audio
yi = 84 + math.sqrt(36 ** 2 - 4 ** 2)
bud_l = f'M104 84 V200 A16 16 0 0 1 72 200 V{f(yi)} A36 36 0 1 1 104 84 Z'
bud_r = f'M152 84 V200 A16 16 0 0 0 184 200 V{f(yi)} A36 36 0 1 0 152 84 Z'
icon('earbuds', DV, ['earbuds', 'wireless earphones', 'in-ear', 'audio', 'earphones'],
     line=[P(bud_l), P(bud_r)], area=[P(bud_l), P(bud_r)])

case = 'M40 112 H216 V160 A56 56 0 0 1 160 216 H96 A56 56 0 0 1 40 160 Z'
lid_pts = rot([(48, 112), (48, 80), (216, 80), (216, 112)], 16, (216, 112))
lid = f'M{pt(lid_pts[0])} C{pt(lid_pts[1])} {pt(lid_pts[2])} {pt(lid_pts[3])} Z'
icon('earbuds-case', DV, ['earbuds', 'charging case', 'devices'],
     line=[P(case), P(lid)], detail=[C(96, 156, 16), C(160, 156, 16)], area=[P(case), P(lid)])

bt = [(80, 88), (176, 168), (128, 208), (128, 48), (176, 88), (80, 168)]
bt = [(180 + (x - 128) * 0.7, 132 + (y - 128) * 0.7) for x, y in bt]
icon('earbuds-bluetooth', DV, ['bluetooth', 'earbuds', 'wireless'],
     line=[P(bud_l), PL(bt)], area=[P(bud_l)])

hsl = load('headset')
icon('headset-slash', DV, ['headset off', 'mic off', 'support offline', 'audio'],
     line=hsl['line'] + [SLASH], dot=hsl['dot'])

kc = (128, 140)
icon('knob', DV, ['knob', 'dial', 'potentiometer', 'volume'],
     line=[C(*kc, 72)] + [L(*polar(kc, 92, a), *polar(kc, 104, a)) for a in (-150, -120, -90, -60, -30)],
     detail=[L(*polar(kc, 20, -120), *polar(kc, 44, -120))], area=[C(*kc, 72)])

# ================================================================ office and hardware
FAXB = R(32, 120, 192, 96, 16)
paper = 'M80 120 V48 A8 8 0 0 1 88 40 H168 A8 8 0 0 1 176 48 V120'
icon('fax', DV, ['fax', 'fax machine', 'office', 'print'],
     line=[FAXB, P(paper)], detail=[L(104, 72, 152, 72), L(104, 96, 136, 96), R(64, 152, 88, 32, 16)],
     area=[FAXB, P(paper + ' Z')], dotcut=[C(184, 152, 12), C(184, 184, 12)])

GC = R(32, 48, 192, 128, 14)
tab = 'M64 176 V208 H160 V176'
icon('graphics-card', DV, ['gpu', 'graphics card', 'pci', 'hardware', 'video card'],
     line=[GC, P(tab)], detail=[C(96, 112, 36), L(160, 88, 160, 136), L(192, 88, 192, 136)],
     area=[GC, P(tab + ' Z')], dotcut=[C(96, 112, 12)])

HDN = R(32, 32, 192, 104, 14)
icon('hard-drive-network', DV, ['nas', 'network drive', 'storage', 'server', 'shared storage'],
     line=[HDN, L(128, 136, 128, 168), R(104, 168, 48, 48, 10), L(32, 192, 104, 192), L(152, 192, 224, 192)],
     detail=[L(72, 84, 136, 84)], area=[HDN, R(104, 168, 48, 48, 10)], dotcut=[C(184, 84, 12)])

kb = load('keyboard')
kb_dots = [d for d in kb['dotcut'] if not any(f'cx="{x}"' in d for x in (96, 128))]
icon('keyboard-slash', DV, ['keyboard off', 'hide keyboard', 'disabled', 'input'],
     line=kb['line'] + kb['detail'] + [SLASH], dot=kb_dots)

# ================================================================ gamepad buttons
yA = 144
xA = (yA - 80) / 96 * 32
icon('gamepad-button-letter', DV, ['controller button', 'a button', 'gamepad', 'face button'],
     line=[C(128, 128, 96)], detail=[PL([(96, 176), (128, 80), (160, 176)]), L(128 - xA, yA, 128 + xA, yA)],
     area=[C(128, 128, 96)])
tri = [(128, 32), (155, 80), (101, 80)]
icon('gamepad-button-shape', DV, ['controller button', 'gamepad', 'face buttons', 'shapes'],
     line=[PG(tri), C(198, 128, 26), R(32, 102, 52, 52, 6), L(108, 180, 148, 220), L(148, 180, 108, 220)],
     area=[PG(tri), C(198, 128, 26), R(32, 102, 52, 52, 6)])

# ================================================================ item tracker
tc, tr_ = (148, 148), 76
rc, rr_ = (72, 72), 40
pa, pb = circle_x(tc, tr_, rc, rr_)
ring = f'M{pt(pa)} ' + arc_to(rc, rr_, pa, pb, lambda m: dist(m, tc))
icon('item-tracker', DV, ['tracker', 'tag', 'find', 'locator'],
     line=[C(*tc, tr_), P(ring)], detail=[C(*tc, 32)], area=[C(*tc, tr_)])

# ================================================================ laptop variants
LT = load('laptop')
LT_SEGS = rr_segs(52, 56, 152, 112, 12)


def laptop_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(LT_SEGS, B, cr)
    x_end = BX - math.sqrt(cr * cr - (196 - BY) ** 2)
    return merge(dict(line=[P(ln), L(28, 196, x_end, 196)], area=[P(ar)]), b)


for name, kind, tags in [
    ('laptop-charging', 'lightning', ['charging', 'power', 'battery']),
    ('laptop-cloud', 'cloud', ['laptop', 'cloud', 'sync', 'online']),
    ('laptop-warning', 'warning', ['laptop error', 'issue', 'alert']),
    ('laptop-wrench', 'wrench', ['repair', 'it support', 'maintenance']),
]:
    icon(name, DV, tags, **laptop_badge(kind))
icon('laptop-slash', DV, ['laptop', 'disabled', 'off', 'devices'], line=LT['line'] + [SLASH])

print(save(overwrite=True))
