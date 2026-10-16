import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

# ------------------------------------------------------------------ geometry helpers
# A path is a list of segments: ('L', p, q) or ('A', c, r, a0, a1) (angles in radians, a0 -> a1).


def _arc_center(p, q, r, large, sweep):
    x1, y1 = p; x2, y2 = q
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    d2 = dx * dx + dy * dy
    r = max(r, math.sqrt(d2))
    k = math.sqrt(max(r * r * r * r - r * r * d2, 0) / (r * r * d2))
    if large == sweep:
        k = -k
    cx = k * dy + (x1 + x2) / 2
    cy = -k * dx + (y1 + y2) / 2
    a0 = math.atan2(y1 - cy, x1 - cx); a1 = math.atan2(y2 - cy, x2 - cx)
    span = (a1 - a0) % (2 * math.pi)
    if not sweep:
        span -= 2 * math.pi
    if abs(span) < 1e-9:
        span = 2 * math.pi if sweep else -2 * math.pi
    return (cx, cy), r, a0, a0 + span


def parse(d):
    toks = re.findall(r'[MLHVAZmlhvaz]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cur = None; start = None; segs = []; cmd = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
        if cmd == 'M':
            cur = (num(), num()); start = cur; cmd = 'L'
        elif cmd == 'L':
            q = (num(), num()); segs.append(('L', cur, q)); cur = q
        elif cmd == 'H':
            q = (num(), cur[1]); segs.append(('L', cur, q)); cur = q
        elif cmd == 'V':
            q = (cur[0], num()); segs.append(('L', cur, q)); cur = q
        elif cmd == 'A':
            r = num(); num(); num(); large = int(num()); sweep = int(num()); q = (num(), num())
            c, r, a0, a1 = _arc_center(cur, q, r, large, sweep)
            segs.append(('A', c, r, a0, a1)); cur = q
        elif cmd == 'Z':
            if math.hypot(cur[0] - start[0], cur[1] - start[1]) > 1e-6:
                segs.append(('L', cur, start))
            cur = start
    return segs


def rrect(x, y, w, h, r):
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')


def circ(cx, cy, r, start=-90):
    a = math.radians(start)
    return [('A', (cx, cy), r, a, a + 2 * math.pi)]


def at(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    _, c, r, a0, a1 = s
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', at(s, t0), at(s, t1))
    _, c, r, a0, a1 = s
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_d(s, first):
    out = f'M{pt(at(s, 0))} ' if first else ''
    if s[0] == 'L':
        return out + f'L{pt(s[2])}'
    _, c, r, a0, a1 = s
    span = a1 - a0
    if abs(abs(span) - 2 * math.pi) < 1e-6:  # full circle -> two halves
        mid = at(s, 0.5)
        sw = 1 if span > 0 else 0
        return out + f'A{f(r)} {f(r)} 0 0 {sw} {pt(mid)} A{f(r)} {f(r)} 0 0 {sw} {pt(at(s, 1))}'
    return out + f'A{f(r)} {f(r)} 0 {1 if abs(span) > math.pi else 0} {1 if span > 0 else 0} {pt(at(s, 1))}'


def to_d(segs, close=False):
    return ' '.join(seg_d(s, i == 0) for i, s in enumerate(segs)) + (' Z' if close else '')


def trim(segs, keep, n=800, minlen=6):
    """Split a path into the pieces where keep(point) is True. Returns list of segment lists."""
    pieces = []; curp = []
    closed = math.hypot(at(segs[0], 0)[0] - at(segs[-1], 1)[0], at(segs[0], 0)[1] - at(segs[-1], 1)[1]) < 1e-6
    for s in segs:
        ts = [i / n for i in range(n + 1)]
        ks = [keep(at(s, t)) for t in ts]
        j = 0
        while j <= n:
            if ks[j]:
                k = j
                while k + 1 <= n and ks[k + 1]:
                    k += 1
                t0 = ts[j]; t1 = ts[k]
                # refine boundaries by bisection
                if j > 0:
                    lo, hi = ts[j - 1], ts[j]
                    for _ in range(30):
                        m = (lo + hi) / 2
                        lo, hi = (lo, m) if keep(at(s, m)) else (m, hi)
                    t0 = hi
                if k < n:
                    lo, hi = ts[k], ts[k + 1]
                    for _ in range(30):
                        m = (lo + hi) / 2
                        lo, hi = (m, hi) if keep(at(s, m)) else (lo, m)
                    t1 = lo
                if j > 0 and curp:
                    pieces.append(curp); curp = []
                curp.append(sub(s, t0, t1))
                if k < n:
                    pieces.append(curp); curp = []
                j = k + 1
            else:
                if curp:
                    pieces.append(curp); curp = []
                j += 1
    if curp:
        pieces.append(curp)
    if closed and len(pieces) > 1 and keep(at(segs[0], 0)):
        pieces[0] = pieces[-1] + pieces[0]; pieces.pop()
    def length(p):
        return sum(math.hypot(at(s, 1)[0] - at(s, 0)[0], at(s, 1)[1] - at(s, 0)[1]) if s[0] == 'L'
                   else abs(s[4] - s[3]) * s[2] for s in p)
    return [p for p in pieces if length(p) >= minlen]


def shift(segs, dx, dy):
    out = []
    for s in segs:
        if s[0] == 'L':
            out.append(('L', (s[1][0] + dx, s[1][1] + dy), (s[2][0] + dx, s[2][1] + dy)))
        else:
            out.append(('A', (s[1][0] + dx, s[1][1] + dy)) + s[2:])
    return out


def seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (vx * vx + vy * vy)))
    return math.hypot(p[0] - a[0] - vx * t, p[1] - a[1] - vy * t)


SLASH = ((48, 48), (208, 208))


def off_slash(a=SLASH[0], b=SLASH[1], gap=32):
    return lambda p: seg_dist(p, a, b) >= gap


def slash_cut(d_or_segs, a=SLASH[0], b=SLASH[1], gap=32):
    segs = parse(d_or_segs) if isinstance(d_or_segs, str) else d_or_segs
    return [P(to_d(p)) for p in trim(segs, off_slash(a, b, gap))]


# ------------------------------------------------------------------ badges (reused from the library's badge family)
def _badge(src, nline, narea, R):
    d = load(src)
    return dict(R=R, line=d['line'][nline:], area=d['area'][narea:], hole=d['hole'], dot=d['dot'],
                detail=d['detail'])


BADGES = {
    'check': _badge('bell-check', 2, 1, 56),
    'x': _badge('chat-x', 1, 1, 54),
    'minus': _badge('chat-minus', 1, 1, 50),
    'plus': _badge('chat-plus', 1, 1, 56),
    'share': _badge('chat-share', 1, 1, 60),
    'heart': _badge('chat-heart', 1, 1, 58),
    'gear': _badge('chat-gear', 1, 1, 60),
    'lightning': _badge('chat-lightning', 1, 1, 58),
    'push-pin': _badge('chat-push-pin', 1, 1, 58),
    'magnifying-glass': _badge('chat-magnifying-glass', 1, 1, 56),
    'pause': _badge('chat-pause', 1, 1, 54),
    'currency-dollar': _badge('chat-currency-dollar', 1, 1, 60),
    'code': _badge('chat-code', 1, 1, 60),
    'arrow-up': _badge('bell-arrow-up', 2, 1, 56),
    'arrow-down': _badge('bell-arrow-down', 2, 1, 56),
    'warning': _badge('bell-warning', 2, 1, 58),
}
BC = (184, 184)
inside = lambda m: -dist(m, (128, 128))


def badge_cut(d, R, close_area=True):
    """Trim an outline around the badge circle; returns (line elements, area elements)."""
    pieces = trim(parse(d), lambda p: dist(p, BC) >= R)
    lines = [P(to_d(p)) for p in pieces]
    areas = []
    if close_area and len(pieces) == 1:
        p = pieces[0]
        a, b = at(p[0], 0), at(p[-1], 1)
        areas.append(P(to_d(p) + ' ' + arc_to(BC, R, b, a, inside) + ' Z'))
    return lines, areas


# ------------------------------------------------------------------ bookmarks
BM_FRONT = 'M44 64 H156 V224 L100 188 L44 224 Z'
BM_BACK = 'M100 64 V32 H212 V192 L156 156'
icon('bookmarks', 'Interface', ['saved items', 'bookmarks', 'collection', 'bookmark manager', 'saved'],
     line=[P(BM_FRONT), P(BM_BACK)], area=[P(BM_FRONT)])
icon('bookmarks-slash', 'Education', ['bookmarks', 'disabled', 'off', 'education'],
     line=slash_cut(BM_FRONT) + slash_cut(BM_BACK) + [L(*SLASH[0], *SLASH[1])])

# ------------------------------------------------------------------ brightness
def sun_rays(c, r0, r1, skip=()):
    out = []
    for i in range(8):
        if i in skip:
            continue
        a = i * 45
        p, q = polar(c, r0, a), polar(c, r1, a)
        out.append(L(*p, *q))
    return out


def brightness_parts(c=(128, 128), r=44, skip=()):
    cx, cy = c
    line = [C(cx, cy, r), L(cx, cy - r, cx, cy + r)] + sun_rays(c, 68, 88, skip)
    area = [P(f'M{f(cx)} {f(cy - r)} A{r} {r} 0 0 1 {f(cx)} {f(cy + r)} Z')]
    return line, area


bl, ba = brightness_parts()
icon('brightness', 'Interface', ['brightness', 'half', 'contrast', 'display'], line=bl, area=ba)
bl, ba = brightness_parts((120, 120), skip=(1,))
up = BADGES['arrow-up']
icon('brightness-up', 'Devices', ['brightness', 'increase', 'upload', 'display', 'light'],
     line=bl + [L(196, 216, 196, 160), PL([(176, 180), (196, 160), (216, 180)])], area=ba)
# auto: a larger disc carrying a knocked-out letter A, short rays
A_LET = [PL([(108, 154), (128, 100), (148, 154)]), L(115.4, 136, 140.6, 136)]
icon('brightness-auto', 'Interface', ['auto brightness', 'auto theme', 'display', 'adaptive', 'brightness auto'],
     line=[C(128, 128, 60)] + sun_rays((128, 128), 84, 96), detail=A_LET, area=[C(128, 128, 60)])
sl = slash_cut(circ(128, 128, 44, -90)) + [L(*SLASH[0], *SLASH[1])]
for i in range(8):
    p, q = polar((128, 128), 68, i * 45), polar((128, 128), 88, i * 45)
    sl += slash_cut([('L', p, q)])
icon('brightness-slash', 'Devices', ['brightness', 'disabled', 'off', 'display', 'light'], line=sl)

# ------------------------------------------------------------------ browser family
BR = load('browser')
BR_RECT = rrect(32, 40, 192, 176, 14)
BR_HEAD = [L(32, 104, 224, 104), L(104, 72, 192, 72)]
BR_DOT = [C(64, 72, 10)]


def browser(name, tags, extra_detail=(), extra_line=(), extra_dotcut=()):
    icon(name, 'Interface', tags, line=BR['line'] + list(extra_line), detail=BR['detail'] + list(extra_detail),
         area=BR['area'], dotcut=BR['dotcut'] + list(extra_dotcut))


def browser_badge(name, tags, b):
    bd = BADGES[b]
    lines, areas = badge_cut(BR_RECT, bd['R'])
    icon(name, 'Interface', tags, line=lines + bd['line'], detail=BR['detail'] + bd['detail'],
         area=areas + bd['area'], hole=bd['hole'], dot=bd['dot'], dotcut=BR['dotcut'])


browser('browser-arrow-down', ['download page', 'save from web', 'browser'],
        [L(128, 132, 128, 188), PL([(104, 164), (128, 188), (152, 164)])])
browser('browser-arrow-up', ['upload to web', 'publish', 'browser'],
        [L(128, 188, 128, 132), PL([(104, 156), (128, 132), (152, 156)])])
browser_badge('browser-check', ['page ok', 'verified site', 'browser', 'done', 'approved'], 'check')
browser_badge('browser-magnifying-glass', ['web search', 'search page', 'browser'], 'magnifying-glass')
browser('browser-maximize', ['browser maximize', 'browser', 'window', 'web', 'maximize'],
        [L(100, 188, 156, 132), PL([(124, 132), (156, 132), (156, 164)]), PL([(100, 156), (100, 188), (132, 188)])])
browser_badge('browser-minus', ['browser', 'remove', 'subtract', 'window', 'web'], 'minus')
browser_badge('browser-plus', ['new tab', 'new window', 'open tab', 'add website', 'browser'], 'plus')

# prohibit badge: circle with a diagonal bar, own area so the fill weight reads as a sign
lines, areas = badge_cut(BR_RECT, 70)
pa, pb = polar(BC, 34, 225), polar(BC, 34, 45)
icon('browser-prohibit', 'Interface', ['blocked site', 'forbidden page', 'no access'],
     line=lines + [C(*BC, 34)], detail=BR['detail'] + [L(*pa, *pb)], area=areas + [C(*BC, 34)],
     dotcut=BR['dotcut'])

# refresh: a clockwise circular arrow in the page area (two arrows are illegible at this size)
def clock_arrow(c, r, h, deg):
    cx, cy = c
    p0 = (cx + r, cy); e = polar(c, r, -45)
    pts = [(e[0] - h, e[1]), e, (e[0], e[1] - h)]
    arc = P(f'M{pt(rot([p0], deg, c)[0])} A{r} {r} 0 1 1 {pt(rot([e], deg, c)[0])}')
    return [arc, PL(rot(pts, deg, c))]
browser('browser-refresh', ['reload page', 'refresh window', 'browser'], clock_arrow((128, 164), 26, 16, 0))
browser_badge('browser-share', ['browser', 'share', 'send', 'window', 'web'], 'share')

bsl = slash_cut(BR_RECT, (32, 32), (224, 224)) + [P(to_d(pc)) for pc in trim(parse('M32 104 L224 104'), off_slash((32, 32), (224, 224)), minlen=40)]
bsl += slash_cut('M104 72 L192 72', (32, 32), (224, 224))
icon('browser-slash', 'Interface', ['browser', 'disabled', 'off', 'window', 'web'],
     line=bsl + [L(32, 32, 224, 224)])

TABS = ('M32 54 A14 14 0 0 1 46 40 H90 A14 14 0 0 1 104 54 V80 H210 A14 14 0 0 1 224 94 V202 '
        'A14 14 0 0 1 210 216 H46 A14 14 0 0 1 32 202 Z')
TAB2 = 'M136 80 V60 A12 12 0 0 1 148 48 H180 A12 12 0 0 1 192 60 V80'
icon('browser-tabs', 'Interface', ['tabs', 'multiple tabs', 'tabbed window'],
     line=[P(TABS), P(TAB2)], detail=[L(32, 144, 224, 144), L(96, 112, 192, 112)],
     area=[P(TABS), P(TAB2 + ' Z')], dotcut=[C(64, 112, 10)])
browser_badge('browser-warning', ['site warning', 'unsafe page', 'browser error'], 'warning')
browser_badge('browser-x', ['close window', 'page error', 'close tab', 'browser', 'remove'], 'x')

FRONT = rrect(32, 72, 152, 144, 14)
icon('browsers', 'Interface', ['windows', 'multiple windows', 'tabs'],
     line=[P(FRONT), P('M72 72 V46 A14 14 0 0 1 86 32 H210 A14 14 0 0 1 224 46 V162 A14 14 0 0 1 210 176 H184')],
     detail=[L(32, 124, 184, 124), L(96, 98, 156, 98)], area=[P(FRONT)], dotcut=[C(62, 98, 10)])

# ------------------------------------------------------------------ misc interface
CAPS = [(128, 40), (212, 124), (164, 124), (164, 168), (92, 168), (92, 124), (44, 124)]
icon('caps-lock', 'Interface', ['caps lock', 'keyboard', 'uppercase', 'key', 'shift'],
     line=[PG(CAPS), L(92, 208, 164, 208)], area=[PG(CAPS)])
icon('card-text', 'Interface', ['card', 'content', 'text', 'panel'],
     line=[R(32, 48, 192, 160, 14)], detail=[L(72, 96, 136, 96), L(72, 136, 184, 136), L(72, 168, 152, 168)],
     area=[R(32, 48, 192, 160, 14)])
CARDS3 = [R(32, 80, 32, 96, 10), R(96, 48, 64, 160, 12), R(192, 80, 32, 96, 10)]
icon('carousel', 'Interface', ['slider', 'gallery', 'cards', 'slides', 'carousel'], line=CARDS3, area=CARDS3)
LPART = 'M32 72 H46 A10 10 0 0 1 56 82 V174 A10 10 0 0 1 46 184 H32'
RPART = 'M224 72 H210 A10 10 0 0 0 200 82 V174 A10 10 0 0 0 210 184 H224'
TPART = 'M72 32 V46 A10 10 0 0 0 82 56 H174 A10 10 0 0 0 184 46 V32'
BPART = 'M72 224 V210 A10 10 0 0 1 82 200 H174 A10 10 0 0 1 184 210 V224'
icon('carousel-horizontal', 'Interface', ['carousel', 'slider', 'gallery', 'slides'],
     line=[R(88, 48, 80, 160, 14), P(LPART), P(RPART)], area=[R(88, 48, 80, 160, 14)])
icon('carousel-vertical', 'Interface', ['carousel', 'slider', 'gallery', 'scroll'],
     line=[R(48, 88, 160, 80, 14), P(TPART), P(BPART)], area=[R(48, 88, 160, 80, 14)])

CD = load('circle-dashed')
icon('check-circle-dashed', 'Interface', ['check circle dashed', 'check', 'circle', 'dashed', 'interface'],
     line=CD['line'], detail=[PL([(88, 132), (116, 160), (172, 104)])], area=[C(128, 128, 104)])
SQF = rrect(32, 72, 152, 152, 16)
icon('check-square-stack', 'Interface', ['checkbox', 'multiple', 'select all', 'checked'],
     line=[P(SQF), P('M72 72 V48 A16 16 0 0 1 88 32 H208 A16 16 0 0 1 224 48 V168 A16 16 0 0 1 208 184 H184')],
     detail=[PL([(74, 150), (98, 174), (144, 128)])], area=[P(SQF)])
icon('checks', 'Interface', ['double check', 'read', 'all done', 'checks', 'delivered'],
     line=[PL([(32, 124), (80, 172), (168, 84)]), L(136, 172, 224, 84)])
icon('clear-all', 'Interface', ['clear', 'dismiss all', 'notifications'],
     line=[L(40, 72, 168, 72), L(64, 128, 192, 128), L(88, 184, 216, 184)])

# ------------------------------------------------------------------ clouds
CLOUD = load('cloud')['line'][0]
CLOUD_D = re.search(r'd="([^"]+)"', CLOUD).group(1)
cc = (128, 142); cr = 28
def cloud_arrow(a0, a1, h=16):
    p, q = polar(cc, cr, a0), polar(cc, cr, a1)
    tang = math.radians(a1 + 90)
    ux, uy = math.cos(tang), math.sin(tang)
    nx, ny = math.cos(math.radians(a1)), math.sin(math.radians(a1))
    return [P(f'M{pt(p)} A{cr} {cr} 0 0 1 {pt(q)}'), PL([q, (q[0] - ux * h + nx * h, q[1] - uy * h + ny * h)])]
icon('cloud-arrows-clockwise', 'Interface', ['cloud sync', 'backup', 'syncing', 'refresh', 'cloud'],
     line=[CLOUD], detail=cloud_arrow(200, 325) + cloud_arrow(20, 145), area=[CLOUD])

CLOUD_S = to_d(shift(parse(CLOUD_D), -8, -16), True)


def cloud_badge(name, tags, b):
    bd = BADGES[b]
    lines, areas = badge_cut(CLOUD_S, bd['R'])
    icon(name, 'Interface', tags, line=lines + bd['line'], detail=bd['detail'], area=areas + bd['area'],
         hole=bd['hole'], dot=bd['dot'])


cloud_badge('cloud-heart', ['favourite cloud', 'cloud', 'love', 'saved'], 'heart')
icon('cloud-minus', 'Interface', ['remove from cloud', 'cloud', 'minus', 'delete'],
     line=[CLOUD], detail=[L(100, 144, 156, 144)], area=[CLOUD])
icon('cloud-plus', 'Interface', ['add to cloud', 'cloud', 'plus', 'new'],
     line=[CLOUD], detail=[L(128, 120, 128, 164), L(106, 142, 150, 142)], area=[CLOUD])
icon('cloud-question', 'Interface', ['cloud help', 'unknown', 'cloud', 'question'],
     line=[CLOUD], detail=[P('M110 116 A19 19 0 1 1 137 133 C131 136 128 139 128 145 V146')], area=[CLOUD],
     dotcut=[C(128, 172, 11)])
cloud_badge('cloud-share', ['share cloud', 'upload', 'cloud', 'link'], 'share')
icon('cloud-warning', 'Interface', ['cloud error', 'service alert', 'sync warning', 'cloud alert', 'error'],
     line=[CLOUD], detail=[L(128, 108, 128, 140)], area=[CLOUD], dotcut=[C(128, 170, 11)])

COLS = [R(36, 40, 40, 176, 10), R(108, 40, 40, 176, 10), R(180, 40, 40, 176, 10)]
icon('columns-three', 'Interface', ['three columns', 'layout', 'grid', 'columns'], line=COLS, area=COLS)
icon('corners-out-slash', 'Interface', ['corners out', 'off', 'disabled', 'hidden', 'corners'],
     line=load('corners-out')['line'] + [L(72, 72, 184, 184)])

# ------------------------------------------------------------------ cursor badges
CUR = to_d(shift(parse('M48 40 L208 112 L136 136 L112 208 Z'), -8, -8), True)
for b, tags in [
    ('arrow-down', ['cursor', 'download', 'down', 'decrease']),
    ('arrow-up', ['cursor', 'upload', 'up', 'increase']),
    ('check', ['cursor check', 'done', 'approved', 'cursor', 'pointer']),
    ('code', ['cursor', 'code', 'developer', 'embed']),
    ('currency-dollar', ['cursor', 'dollar', 'price', 'money']),
    ('gear', ['cursor', 'settings', 'configure']),
    ('heart', ['cursor', 'favorite', 'like', 'love']),
    ('lightning', ['cursor', 'fast', 'power', 'instant']),
    ('magnifying-glass', ['cursor', 'search', 'find']),
    ('minus', ['cursor minus', 'remove', 'subtract', 'cursor', 'pointer']),
    ('pause', ['cursor', 'paused', 'hold']),
    ('plus', ['cursor plus', 'add', 'new', 'cursor', 'pointer']),
    ('push-pin', ['cursor', 'pin', 'pinned']),
]:
    bd = BADGES[b]
    icon('cursor-' + b, 'Interface', tags, line=[P(CUR)] + bd['line'], detail=bd['detail'],
         area=[P(CUR)] + bd['area'], hole=bd['hole'], dot=bd['dot'])

print(save(overwrite=True))
