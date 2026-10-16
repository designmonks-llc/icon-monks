import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

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



TM, SY = 'Time', 'Symbols'
PI = math.pi
rad = math.radians


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], dotcut=[], detail=[])
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return out


# ================================================================ badge marks around B (lower right)
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


def heart_path(c, s):
    """The core heart (centre ~ (128,140)) scaled by s around c."""
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def badge(kind):
    """Returns (roles dict, clearance radius around B)."""
    b = dict(line=[], area=[], hole=[], dot=[], dotcut=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
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
            return [(float(a), float(c)) for a, c in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
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
    elif kind == 'user':
        b['dot'] = [C(BX, BY - 18, 18)]
        b['line'] = [P(f'M{BX - 28} {BY + 34} A28 28 0 0 1 {BX + 28} {BY + 34}')]
        cr = 62
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    elif kind == 'stats':
        b['line'] = [L(154, 214, 154, 196), L(184, 214, 184, 176), L(214, 214, 214, 156)]
        cr = 64
    elif kind == 'clock':
        b['line'] = [C(BX, BY, 40)]
        b['area'] = [C(BX, BY, 40)]
        b['detail'] = [PL([(BX, BY - 18), (BX, BY), (BX + 14, BY + 8)])]
        cr = 70
    elif kind in ('smile', 'sad'):
        b['line'] = [C(BX, BY, 40)]
        b['area'] = [C(BX, BY, 40)]
        if kind == 'smile':
            b['detail'] = [P(f'M{BX - 16} {BY + 10} A20 20 0 0 0 {BX + 16} {BY + 10}')]
            b['dotcut'] = [C(BX - 14, BY - 12, 10), C(BX + 14, BY - 12, 10)]
        else:
            b['detail'] = [P(f'M{BX - 16} {BY + 20} A20 20 0 0 1 {BX + 16} {BY + 20}')]
            b['dotcut'] = [C(BX - 13, BY - 10, 9), C(BX + 13, BY - 10, 9)]
        cr = 70
    else:
        raise ValueError(kind)
    return b, cr


# ================================================================ bases (exact geometry of the existing icons)
# calendar: rect 40,48 176x168 rx14, rings at x=88/168, divider y=104
CAL = [('L', (54, 48), (202, 48)), ('A', (202, 62), 14, -PI / 2, 0), ('L', (216, 62), (216, 202)),
       ('A', (202, 202), 14, 0, PI / 2), ('L', (202, 216), (54, 216)), ('A', (54, 202), 14, PI / 2, PI),
       ('L', (40, 202), (40, 62)), ('A', (54, 62), 14, PI, 1.5 * PI)]
CAL_D = load('calendar')
CAL_RINGS = [L(88, 32, 88, 72), L(168, 32, 168, 72)]
CAL_DIV = L(40, 104, 216, 104)
cal_full = dict(line=CAL_D['line'], area=CAL_D['area'])


def cal_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(CAL, B, cr)
    return merge(dict(line=[P(ln)] + CAL_RINGS, area=[P(ar)], detail=[CAL_DIV]), b)


# clock: circle r96 at centre; badge variants point the hands up and left (as clock-lightning / clock-record)
CK_C = (128, 128)
_ck_a = ang(CK_C, B) - PI
CLOCK = [('A', CK_C, 96, _ck_a, _ck_a + 2 * PI)]
CLOCK_HANDS_BADGE = PL([(128, 76), (128, 128), (88, 128)])


def clock_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(CLOCK, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=[CLOCK_HANDS_BADGE]), b)


# alarm: face r80 at (128,136), bells, legs (the right leg is dropped under a badge)
AL_C = (128, 136)
_al_a = ang(AL_C, B) - PI
ALARM = [('A', AL_C, 80, _al_a, _al_a + 2 * PI)]
AL_D = load('alarm')
AL_BELLS = AL_D['line'][1:3]
AL_LEG_L, AL_LEG_R = AL_D['line'][3], AL_D['line'][4]
AL_HANDS_BADGE = PL([(128, 96), (128, 136), (96, 136)])


def alarm_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(ALARM, B, cr)
    return merge(dict(line=[P(ln)] + AL_BELLS + [AL_LEG_L], area=[P(ar)], detail=[AL_HANDS_BADGE]), b)


# ================================================================ slash helpers
SLASH = L(48, 48, 208, 208)
SG = 30


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def run_len(r):
    pts = sample(r, 20) + [seg_end(r[-1])]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def gapped(outline, closed=True, g=SG):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= g, closed)
    if whole and closed:
        return [P(segs_d(outline, True))]
    return [P(segs_d(r)) for r in runs if r and run_len(r) >= 16]


def arc_arrow(c, r, a0, a1, head=40, spread=45):
    """Arc from angle a0 to a1 (degrees; a1 > a0 runs clockwise on screen) with a chevron head at a1."""
    segs = [('A', c, r, rad(a0), rad(a1))]
    e = polar(c, r, a1)
    sgn = 1 if a1 > a0 else -1
    tang = (-math.sin(rad(a1)) * sgn, math.cos(rad(a1)) * sgn)  # direction of travel at the end
    back = math.degrees(math.atan2(-tang[1], -tang[0]))
    hd = PL([polar(e, head, back - spread), e, polar(e, head, back + spread)])
    return segs, hd


# ================================================================ zodiac (Symbols)
ZT = lambda s: [s, 'zodiac', 'astrology', 'horoscope']

# pisces: two arcs bowing towards each other, tied by a bar
pc_r = 125.6
icon('zodiac-pisces', SY, ZT('pisces'),
     line=[P(f'M64 40 A{pc_r} {pc_r} 0 0 1 64 216'), P(f'M192 40 A{pc_r} {pc_r} 0 0 0 192 216'),
           L(48, 128, 208, 128)])

# sagittarius: arrow to the upper right with a cross bar
icon('zodiac-sagittarius', SY, ZT('sagittarius'),
     line=[L(48, 208, 208, 48), PL([(120, 48), (208, 48), (208, 136)]), L(76, 116, 140, 180)])

# scorpio: an m whose last leg kicks out into an arrow
icon('zodiac-scorpio', SY, ZT('scorpio'),
     line=[P('M40 88 A20 20 0 0 1 60 108 V192'),
           P('M60 108 A26 26 0 0 1 112 108 V192'),
           P('M112 108 A26 26 0 0 1 164 108 V168 A28 28 0 0 0 192 196 H216'),
           PL([(196, 176), (216, 196), (196, 216)])])

# taurus: a round head with horns
icon('zodiac-taurus', SY, ZT('taurus'),
     line=[C(128, 164, 56), P('M48 48 C56 92 88 108 128 108 C168 108 200 92 208 48')],
     area=[C(128, 164, 56)])

# virgo: an m whose last leg carries a crossing loop
icon('zodiac-virgo', SY, ZT('virgo'),
     line=[P('M36 84 A20 20 0 0 1 56 104 V192'),
           P('M56 104 A22 22 0 0 1 100 104 V192'),
           P('M100 104 A22 22 0 0 1 144 104 V224'),
           P('M144 164 C164 120 224 116 220 160 C216 200 180 212 124 212')])

# ================================================================ alarm
icon('alarm-check', TM, ['alarm on', 'set', 'reminder', 'clock'], **alarm_badge('check'))
icon('alarm-minus', TM, ['alarm', 'remove', 'subtract', 'clock', 'wake'], **alarm_badge('minus'))
icon('alarm-plus', TM, ['add alarm', 'new', 'reminder', 'clock', 'alarm'], **alarm_badge('plus'))

al_slash = []
al_slash += gapped(ALARM)
al_slash += gapped([('A', (84, 84), 48, PI, 1.5 * PI)], False)
al_slash += [AL_D['line'][2], AL_LEG_L, AL_LEG_R]
icon('alarm-slash', TM, ['alarm off', 'disable', 'mute', 'clock', 'alarm'], line=al_slash + [SLASH])

icon('alarm-snooze', TM, ['snooze', 'alarm', 'sleep', 'zzz', 'alarm snooze'],
     line=AL_D['line'], area=AL_D['area'], detail=[PL([(106, 112), (150, 112), (106, 160), (150, 160)])])

# ================================================================ calendar: badges in the lower right
CAL_BADGES = [
    ('arrow-down', 'arrow-down', ['import event', 'download calendar', 'add date', 'calendar', 'decrease']),
    ('arrow-up', 'arrow-up', ['export event', 'upload calendar', 'share date', 'calendar', 'increase']),
    ('clock', 'clock', ['schedule', 'appointment', 'calendar', 'time', 'date']),
    ('code', 'code', ['calendar', 'developer', 'code', 'date', 'schedule']),
    ('currency-dollar', 'dollar', ['calendar', 'money', 'price', 'date', 'schedule']),
    ('gear', 'gear', ['calendar', 'settings', 'configure', 'date', 'schedule']),
    ('lightning', 'lightning', ['calendar', 'fast', 'power', 'date', 'schedule']),
    ('magnifying-glass', 'magnifying-glass', ['calendar', 'search', 'find', 'date', 'schedule']),
    ('pause', 'pause', ['calendar', 'paused', 'hold', 'date', 'schedule']),
    ('push-pin', 'push-pin', ['calendar', 'pinned', 'pin', 'date', 'schedule']),
    ('question', 'question', ['calendar', 'help', 'unknown', 'date', 'schedule']),
    ('sad', 'sad', ['calendar', 'unhappy', 'negative', 'date', 'schedule']),
    ('share', 'share', ['calendar', 'share', 'send', 'date', 'schedule']),
    ('smile', 'smile', ['calendar', 'happy', 'positive', 'date', 'schedule']),
    ('stats', 'stats', ['calendar', 'statistics', 'activity', 'date', 'schedule']),
    ('user', 'user', ['appointment', 'meeting', 'booking', 'schedule', 'calendar']),
    ('warning', 'warning', ['calendar', 'warning', 'error', 'date', 'schedule']),
]
for suffix, kind, tags in CAL_BADGES:
    icon(f'calendar-{suffix}', TM, tags, **cal_badge(kind))

# ================================================================ calendar: symbols inside the body (like calendar-plus)
# interior below the divider: x 40..216, y 104..216, centre (128,160)
icon('calendar-minus', TM, ['calendar', 'remove', 'minus', 'event', 'remove event'],
     detail=[CAL_DIV, L(100, 160, 156, 160)], **cal_full)
icon('calendar-heart', TM, ['calendar', 'date', 'love', 'anniversary'],
     detail=[CAL_DIV, P(heart_path((128, 164), 0.36))], **cal_full)
cs = [polar((128, 164), 36 if i % 2 == 0 else 16, -90 + i * 36) for i in range(10)]
icon('calendar-star', TM, ['special day', 'favourite', 'event', 'calendar'],
     detail=[CAL_DIV, PG(cs)], **cal_full)
icon('calendar-dot', TM, ['calendar', 'day', 'event', 'today', 'current day'],
     detail=[CAL_DIV], dotcut=[C(128, 160, 22)], **cal_full)
icon('calendar-dots', TM, ['events', 'schedule', 'month view', 'plan', 'agenda'],
     detail=[CAL_DIV], dotcut=[C(x, y, 14) for y in (142, 182) for x in (84, 128, 172)], **cal_full)
icon('calendar-list', TM, ['todo', 'agenda', 'calendar', 'tasks'],
     detail=[CAL_DIV, L(112, 142, 176, 142), L(112, 182, 176, 182)],
     dotcut=[C(80, 142, 12), C(80, 182, 12)], **cal_full)
icon('calendar-range', TM, ['calendar', 'date range', 'period', 'span'],
     detail=[CAL_DIV, L(84, 160, 172, 160)], dotcut=[C(84, 160, 18), C(172, 160, 18)], **cal_full)
icon('calendar-week', TM, ['calendar', 'week', 'schedule', 'row'],
     detail=[CAL_DIV, L(80, 182, 176, 182)], dotcut=[C(x, 142, 12) for x in (84, 128, 172)], **cal_full)
icon('calendar-arrow-left', TM, ['reschedule', 'back', 'return date', 'calendar'],
     detail=[CAL_DIV, P('M90 150 H140 A26 26 0 0 1 166 176 V188'), PL([(110, 130), (90, 150), (110, 170)])],
     **cal_full)
rp_c, rp_r = (128, 160), 32
s1, h1 = arc_arrow(rp_c, rp_r, 200, 320, head=16)
s2, h2 = arc_arrow(rp_c, rp_r, 20, 140, head=16)
icon('calendar-repeat', TM, ['recurring', 'repeat event', 'schedule', 'calendar', 'repeat'],
     detail=[CAL_DIV, P(segs_d(s1)), h1, P(segs_d(s2)), h2], **cal_full)

cal_slash = gapped(CAL) + gapped([('L', (88, 32), (88, 72))], False) + [CAL_RINGS[1]] \
    + gapped([('L', (40, 104), (216, 104))], False)
icon('calendar-slash', TM, ['no events', 'calendar off', 'unavailable', 'cancel'], line=cal_slash + [SLASH])

# ================================================================ clock: badges in the lower right
CLOCK_BADGES = [
    ('arrow-down', 'arrow-down', ['clock', 'decrease', 'download', 'time', 'hour']),
    ('arrow-up', 'arrow-up', ['clock', 'increase', 'upload', 'time', 'hour']),
    ('bitcoin', 'bitcoin', ['clock', 'crypto', 'bitcoin', 'time', 'hour']),
    ('check', 'check', ['clock', 'done', 'approved', 'time', 'hour']),
    ('code', 'code', ['clock', 'developer', 'code', 'time', 'hour']),
    ('currency-dollar', 'dollar', ['clock', 'money', 'price', 'time', 'hour']),
]
for suffix, kind, tags in CLOCK_BADGES:
    icon(f'clock-{suffix}', TM, tags, **clock_badge(kind))

# ================================================================ clock: arrows, rims, durations
CA_C, CA_R = (128, 136), 88
cw_segs, cw_head = arc_arrow(CA_C, CA_R, 0, 315, head=40)
cw_arc = segs_d(cw_segs)
icon('clock-clockwise', TM, ['later', 'forward in time', 'schedule'],
     line=[P(cw_arc), cw_head, PL([(128, 92), (128, 136), (160, 156)])])
ccw_segs, ccw_head = arc_arrow(CA_C, CA_R, 180, -135, head=40)
ccw_arc = segs_d(ccw_segs)
icon('clock-counter-clockwise', TM, ['history', 'recent', 'clock', 'undo', 'past'],
     line=[P(ccw_arc), ccw_head, PL([(128, 92), (128, 136), (96, 156)])])
# the arrow head sits where the usual slash would start, so this slash runs the other way
SLASH_R = ((208, 48), (48, 208))
ccw_gapped = trim(ccw_segs, lambda p: seg_dist(p, *SLASH_R) >= SG, False)[0]
icon('clock-counter-clockwise-slash', TM, ['history off', 'no history', 'private', 'disabled'],
     line=[P(segs_d(r)) for r in ccw_gapped] + [ccw_head, L(208, 48, 48, 208)])

# 24 hours: an open clockwise ring around the number 24
h_segs, h_head = arc_arrow((128, 128), 96, -50, 250, head=32)
icon('clock-24-hours', TM, ['24 hours', 'all day', 'open 24/7', 'clock', 'open'],
     line=[P(segs_d(h_segs)), h_head,
           P('M72 120 A17 17 0 0 1 106 120 C106 138 72 146 72 164 H106'),
           PL([(170, 164), (170, 104), (138, 148), (184, 148)])])

# countdown: a three quarter ring with a single hand
icon('clock-countdown', TM, ['countdown', 'time left', 'deadline'],
     line=[P(f'M128 32 A96 96 0 1 1 32 128')],
     detail=[L(128, 128, 128, 76)],
     area=[P('M128 32 A96 96 0 1 1 32 128 L128 128 Z')])

# dashed: right half solid, left half dashed
dash_line = [P('M128 32 A96 96 0 0 1 128 224')]
for k in range(6):
    a0 = 90 + 7.5 + k * 30
    p0, p1 = polar(CK_C, 96, a0), polar(CK_C, 96, a0 + 15)
    dash_line.append(P(f'M{pt(p0)} A96 96 0 0 1 {pt(p1)}'))
icon('clock-dashed', TM, ['history toggle', 'recent', 'time', 'dashed'],
     line=dash_line + [PL([(128, 72), (128, 128), (168, 152)])])

# duration: the clock with an elapsed wedge
wd_end = (188, 128)
wedge = 'M128 128 V68 A60 60 0 0 1 188 128 Z'
icon('clock-duration', TM, ['duration', 'timer', 'elapsed'],
     line=[C(128, 128, 96)], detail=[P(wedge)], area=[C(128, 128, 96)])
wd_segs = [('L', (128, 128), (128, 68)), ('A', CK_C, 60, -PI / 2, 0), ('L', wd_end, (128, 128))]
icon('clock-duration-slash', TM, ['clock duration', 'disabled', 'off', 'duration', 'timer'],
     line=gapped(CLOCK) + gapped(wd_segs) + [SLASH])

print(save(overwrite=True))
