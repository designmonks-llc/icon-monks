import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Communication'

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


# ---------------------------------------------------------------- bases (exact geometry of the existing icons)
BELL = [('L', (208, 184), (48, 184)),
        ('C', (48, 184), (64, 168), (72, 144), (72, 112)),
        ('A', (128, 112), 56, math.pi, 2 * math.pi),
        ('C', (184, 112), (184, 144), (192, 168), (208, 184))]
BELL_NUB = L(128, 40, 128, 56)
BELL_CLAPPER = P('M108 200 A20 20 0 0 0 148 200')

CHAT = [('L', (80, 200), (40, 224)), ('L', (40, 224), (40, 72)),
        ('A', (56, 72), 16, math.pi, 1.5 * math.pi), ('L', (56, 56), (200, 56)),
        ('A', (200, 72), 16, 1.5 * math.pi, 2 * math.pi), ('L', (216, 72), (216, 184)),
        ('A', (200, 184), 16, 0, 0.5 * math.pi), ('L', (200, 200), (80, 200))]
CHAT_D = load('chat')['line'][0]

CC_C, CC_R = (132, 124), 92
_cc_a0 = ang(CC_C, (52.33, 170))
_cc_a1 = ang(CC_C, (97.54, 209.3)) + 2 * math.pi
CHATC = [('L', (97.54, 209.3), (40, 216)), ('L', (40, 216), (52.33, 170)), ('A', CC_C, CC_R, _cc_a0, _cc_a1)]
CHATC_D = load('chat-circle')['line'][0]

# ---------------------------------------------------------------- badge marks around B
B = (184, 184)
BX, BY = B


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
    # the core heart (centre ~ (128,140)) scaled by s around c
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def badge(kind):
    """Returns (roles dict, clearance radius)."""
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
        # the library push-pin, scaled down onto the badge
        pp = load('push-pin')
        import re
        def pin_pts(d):
            return [(float(a), float(b)) for a, b in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
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
    elif kind == 'user':
        b['dot'] = [C(BX, BY - 18, 18)]
        b['line'] = [P(f'M{BX - 28} {BY + 34} A28 28 0 0 1 {BX + 28} {BY + 34}')]
        cr = 62
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[])
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return out


def bell_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(BELL, B, cr)
    return merge(dict(line=[P(ln), BELL_NUB], area=[P(ar)]), b)


def chat_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(CHAT, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)]), b)


def chatc_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(CHATC, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)]), b)


# ================================================================ bell family
BELL_TAGS = {
    'arrow-down': ['bell', 'decrease', 'download', 'notification', 'alert'],
    'arrow-up': ['bell', 'increase', 'upload', 'notification', 'alert'],
    'check': ['bell', 'done', 'approved', 'notification', 'alert'],
    'code': ['bell', 'developer', 'code', 'notification', 'alert'],
    'currency-dollar': ['bell', 'money', 'price', 'notification', 'alert'],
    'gear': ['notification settings', 'alert settings', 'bell', 'configure', 'settings'],
    'heart': ['bell', 'favorite', 'like', 'notification', 'alert'],
    'lightning': ['bell', 'fast', 'power', 'notification', 'alert'],
    'magnifying-glass': ['bell', 'search', 'find', 'notification', 'alert'],
    'minus': ['bell', 'remove', 'subtract', 'notification', 'alert'],
    'pause': ['bell', 'paused', 'hold', 'notification', 'alert'],
    'plus': ['add alert', 'notification', 'new reminder', 'bell', 'add notification'],
    'push-pin': ['bell', 'pinned', 'pin', 'notification', 'alert'],
    'question': ['bell', 'help', 'unknown', 'notification', 'alert'],
    'share': ['bell', 'share', 'send', 'notification', 'alert'],
    'star': ['bell', 'favorite', 'starred', 'notification', 'alert'],
    'warning': ['important notification', 'urgent alert', 'bell', 'exclamation', 'warning'],
    'x': ['bell', 'remove', 'cancel', 'notification', 'alert'],
}
KIND = {'currency-dollar': 'dollar'}
for suffix, tags in BELL_TAGS.items():
    icon(f'bell-{suffix}', CM, tags, **bell_badge(KIND.get(suffix, suffix)))

# bell-dot: the whole bell with an unread dot clear of the dome at the top right
icon('bell-dot', CM, ['unread', 'notification badge', 'alert', 'unread notification', 'new alert'],
     line=load('bell')['line'], area=load('bell')['area'], dot=[C(204, 48, 22)])

# ================================================================ chat circle family
CC_TAGS = {
    'arrow-down': ['chat circle', 'decrease', 'download', 'message', 'conversation'],
    'arrow-up': ['chat circle', 'increase', 'upload', 'message', 'conversation'],
    'check': ['chat circle', 'done', 'approved', 'message', 'conversation'],
    'code': ['chat circle', 'developer', 'code', 'message', 'conversation'],
    'currency-dollar': ['chat circle', 'money', 'price', 'message', 'conversation'],
    'gear': ['chat circle', 'settings', 'configure', 'message', 'conversation'],
    'heart': ['chat circle', 'favorite', 'like', 'message', 'conversation'],
    'lightning': ['chat circle', 'fast', 'power', 'message', 'conversation'],
    'magnifying-glass': ['chat circle', 'search', 'find', 'message', 'conversation'],
    'minus': ['chat circle', 'remove', 'subtract', 'message', 'conversation'],
    'pause': ['chat circle', 'paused', 'hold', 'message', 'conversation'],
    'plus': ['chat circle', 'add', 'new', 'message', 'conversation'],
    'push-pin': ['chat circle', 'pinned', 'pin', 'message', 'conversation'],
    'question': ['chat circle', 'help', 'unknown', 'message', 'conversation'],
    'share': ['chat circle', 'share', 'send', 'message', 'conversation'],
    'star': ['chat circle', 'favorite', 'starred', 'message', 'conversation'],
    'user': ['chat circle', 'user', 'profile', 'message', 'conversation'],
    'warning': ['chat circle', 'warning', 'error', 'message', 'conversation'],
    'x': ['chat circle', 'remove', 'cancel', 'message', 'conversation'],
}
for suffix, tags in CC_TAGS.items():
    icon(f'chat-circle-{suffix}', CM, tags, **chatc_badge(KIND.get(suffix, suffix)))

# ================================================================ chat (square bubble)
for suffix, tags in {
    'code': ['chat', 'developer', 'code', 'message', 'conversation'],
    'currency-dollar': ['chat', 'money', 'price', 'message', 'conversation'],
    'gear': ['chat', 'settings', 'configure', 'message', 'conversation'],
    'heart': ['chat', 'love', 'like', 'message', 'favorite'],
}.items():
    icon(f'chat-{suffix}', CM, tags, **chat_badge(KIND.get(suffix, suffix)))

# symbols drawn inside the bubble as details (bubble interior: 40..216 x 56..200)
chat_full = dict(line=[CHAT_D], area=[CHAT_D])
icon('chat-check', CM, ['chat', 'verified', 'read', 'message', 'message sent'],
     detail=[PL([(92, 130), (116, 154), (164, 106)])], **chat_full)
icon('chat-arrow-down', CM, ['chat', 'download', 'receive', 'message', 'download message'],
     detail=[L(128, 88, 128, 164), PL([(100, 136), (128, 164), (156, 136)])], **chat_full)
icon('chat-arrow-up', CM, ['chat', 'upload', 'send', 'message', 'send message'],
     detail=[L(128, 168, 128, 92), PL([(100, 120), (128, 92), (156, 120)])], **chat_full)
icon('chat-chart', CM, ['chat', 'chart', 'stats', 'message'],
     detail=[L(92, 164, 92, 136), L(128, 164, 128, 92), L(164, 164, 164, 116)], **chat_full)
ac, arr, a_th = (128, 130), 40, -20
a_end = polar(ac, arr, a_th)
icon('chat-arrow-clockwise', CM, ['chat', 'redo', 'refresh', 'message'],
     detail=[P(f'M{pt(polar(ac, arr, a_th + 60))} A{arr} {arr} 0 1 1 {pt(a_end)}'),
             PL([polar(a_end, 26, a_th - 135), a_end, polar(a_end, 26, a_th - 45)])], **chat_full)
icon('chat-forward', CM, ['forward message', 'share', 'pass on', 'chat', 'reply'],
     detail=[P('M88 164 V148 A28 28 0 0 1 116 120 H164'), PL([(136, 92), (164, 120), (136, 148)])], **chat_full)

# ================================================================ slashed
SLASH = L(48, 48, 208, 208)
SG = 30  # clear gap (centreline) left in the base strokes on each side of the slash


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= SG, closed)
    if whole and closed:
        return [P(segs_d(outline, True))]
    return [P(segs_d(r)) for r in runs if r]


# address book and at: the slash simply overlays the base, like the other slashed icons in the library
ab = load('address-book')
icon('address-book-slash', CM, ['address book', 'disabled', 'off', 'communication'],
     line=ab['line'] + ab['detail'] + [SLASH])
at = load('at')
icon('at-slash', CM, ['at', 'disabled', 'off', 'communication'], line=at['line'] + [SLASH])

# broadcast: the waves are opened where the slash crosses them
bc_line = [C(128, 128, 18)]
for r_ in (56, 96):
    a0 = math.radians(-42.03) if r_ == 56 else ang((128, 128), (199.34, 63.76))
    bc_line += gapped([('A', (128, 128), r_, a0, -a0)], False)
    bc_line += gapped([('A', (128, 128), r_, math.pi + a0, math.pi - a0)], False)
icon('broadcast-slash', CM, ['broadcast', 'disabled', 'off', 'communication'], line=bc_line + [SLASH])

# ================================================================ cell signal warning: the tallest bar becomes an exclamation mark
icon('cell-signal-warning', CM, ['signal alert', 'network problem', 'cell', 'mobile'],
     line=[L(56, 208, 56, 168), L(104, 208, 104, 128), L(152, 208, 152, 88), L(200, 48, 200, 160)],
     dot=[C(200, 204, 16)])

print(save(overwrite=True))
