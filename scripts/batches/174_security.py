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



# ================================================================== batch 174: Security
CAT = 'Security'


def tf(d, s, c=(128, 128), o=None):
    """Scale an absolute path (M L H V C Q A Z) by s about c, placing c at o."""
    o = o or c
    X = lambda x: o[0] + (x - c[0]) * s
    Y = lambda y: o[1] + (y - c[1]) * s
    toks = re.findall(r'[MLHVCQAZ]|-?\d*\.?\d+', d)
    out = []; i = 0; cmd = None
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Z]', t):
            cmd = t; i += 1; out.append(cmd)
            if cmd == 'Z':
                continue
        n = lambda k: float(toks[i + k])
        if cmd in 'ML':
            out.append(f'{f(X(n(0)))} {f(Y(n(1)))}'); i += 2
        elif cmd == 'H':
            out.append(f(X(n(0)))); i += 1
        elif cmd == 'V':
            out.append(f(Y(n(0)))); i += 1
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(n(k)))} {f(Y(n(k + 1)))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'Q':
            out.append(' '.join(f'{f(X(n(k)))} {f(Y(n(k + 1)))}' for k in (0, 2))); i += 4
        elif cmd == 'A':
            out.append(f'{f(n(0) * s)} {f(n(1) * s)} {f(n(2))} {int(n(3))} {int(n(4))} {f(X(n(5)))} {f(Y(n(6)))}'); i += 7
    return ' '.join(out).replace('M ', 'M').replace('L ', 'L').replace('H ', 'H').replace('V ', 'V') \
        .replace('C ', 'C').replace('Q ', 'Q').replace('A ', 'A')


def bez_segs(*curves, close=False, n=24):
    pts = []
    for c0, c1, c2, c3 in curves:
        for i in range(n + 1):
            t = i / n; u = 1 - t
            pts.append((u**3*c0[0] + 3*u*u*t*c1[0] + 3*u*t*t*c2[0] + t**3*c3[0],
                        u**3*c0[1] + 3*u*u*t*c1[1] + 3*u*t*t*c2[1] + t**3*c3[1]))
    if close:
        pts.append(pts[0])
    return [('L', a, b) for a, b in zip(pts, pts[1:]) if dist(a, b) > 1e-9]


def dval(el):
    return re.search(r' d="([^"]+)"', el).group(1)


def cut_paths(ds, R, minlen=10):
    out = []
    for d in ds:
        segs = parse(d) if isinstance(d, str) else d
        out += [P(to_d(p)) for p in trim(segs, lambda q: dist(q, BC) >= R, minlen=minlen)]
    return out


def slashed(ds, a=SLASH[0], b=SLASH[1], gap=32, minlen=10):
    out = []
    for d in ds:
        segs = parse(d) if isinstance(d, str) else d
        out += [P(to_d(p)) for p in trim(segs, off_slash(a, b, gap), minlen=minlen)]
    return out


# extra badges drawn from the library's own badge icons
BADGES['bitcoin'] = dict(R=60, line=load('eye-bitcoin')['line'][1:], area=[], hole=[], dot=[], detail=[])
_bq = load('bell-question')
BADGES['question'] = dict(R=58, line=_bq['line'][2:], area=[], hole=[], dot=_bq['dot'], detail=[])
_du = load('database-user')
BADGES['user'] = dict(R=64, line=_du['line'][1:], area=[], hole=[], dot=_du['dot'], detail=[])
_hs = load('house-shield')
BADGES['shield'] = dict(R=60, line=[_hs['line'][2]], area=[_hs['area'][1]], hole=[], dot=[], detail=[])
_il = load('image-lock')
BADGES['lock'] = dict(R=62, line=_il['line'][1:], area=_il['area'][1:], hole=[], dot=[], detail=[])
BADGES['clock'] = dict(R=64, line=[C(186, 186, 38)], area=[C(186, 186, 38)], hole=[], dot=[],
                       detail=[P('M186 166 V186 L200 194')])
FIRE = 'M128 224 C88 224 56 196 56 152 C56 104 100 84 112 32 C144 56 164 84 164 116 C176 108 184 96 186 84 C196 104 200 128 200 152 C200 196 168 224 128 224 Z'
_fl = tf(FIRE, 0.36, (128, 128), (184, 182))
BADGES['fire'] = dict(R=60, line=[P(_fl)], area=[P(_fl)], hole=[], dot=[], detail=[])


def with_badge(name, tags, body, b, line=(), detail=(), dotcut=(), detail_cut=(), line_cut=(), area_full=None):
    """body: closed outline path cut around the badge (gives line + area)."""
    bd = BADGES[b]
    lines, areas = badge_cut(body, bd['R']) if body else ([], [])
    if area_full is not None:
        areas = area_full
    icon(name, CAT, tags, line=lines + list(line) + cut_paths(line_cut, bd['R']) + bd['line'],
         detail=list(detail) + cut_paths(detail_cut, bd['R'] + 6, 24) + bd['detail'],
         area=areas + bd['area'], hole=bd['hole'], dot=bd['dot'], dotcut=list(dotcut))


# ------------------------------------------------------------------ lock family
LOCK_BODY = rrect(48, 104, 160, 112, 14)
SHACKLE = 'M88 104 V72 A40 40 0 0 1 168 72 V104'
SHACKLE_OPEN = 'M88 104 V72 A40 40 0 0 1 166 60'
KEYHOLE_BADGE = L(100, 144, 100, 176)

LOCK_BADGES = [
    ('lock-arrow-down', 'arrow-down', ['lock', 'download', 'down', 'decrease']),
    ('lock-arrow-up', 'arrow-up', ['lock', 'upload', 'up', 'increase']),
    ('lock-bitcoin', 'bitcoin', ['lock', 'bitcoin', 'crypto']),
    ('lock-check', 'check', ['lock check', 'done', 'approved', 'lock', 'secure']),
    ('lock-clock', 'clock', ['timed lock', 'lock schedule', 'expire', 'time lock']),
    ('lock-code', 'code', ['lock', 'code', 'developer', 'embed']),
    ('lock-currency-dollar', 'currency-dollar', ['lock', 'dollar', 'price', 'money']),
    ('lock-gear', 'gear', ['lock', 'settings', 'configure']),
    ('lock-heart', 'heart', ['lock', 'favorite', 'like', 'love']),
    ('lock-lightning', 'lightning', ['lock', 'fast', 'power', 'instant']),
    ('lock-magnifying-glass', 'magnifying-glass', ['lock', 'search', 'find']),
    ('lock-minus', 'minus', ['lock minus', 'remove', 'subtract', 'lock', 'secure']),
    ('lock-pause', 'pause', ['lock', 'paused', 'hold']),
    ('lock-plus', 'plus', ['lock plus', 'add', 'new', 'lock', 'secure']),
    ('lock-push-pin', 'push-pin', ['lock', 'pin', 'pinned']),
    ('lock-question', 'question', ['lock', 'help', 'unknown', 'question']),
    ('lock-share', 'share', ['lock', 'share', 'send']),
    ('lock-user', 'user', ['private account', 'user lock', 'locked profile', 'privacy']),
]
for name, b, tags in LOCK_BADGES:
    with_badge(name, tags, LOCK_BODY, b, line=[P(SHACKLE)], detail=[KEYHOLE_BADGE])

# keyhole lock: round head (dot) + slot
KH_DOT = [C(128, 150, 16)]
KH_SLOT = [L(128, 150, 128, 180)]
icon('lock-key', CAT, ['locked', 'keyhole lock', 'secure'],
     line=[P(LOCK_BODY), P(SHACKLE)], detail=KH_SLOT, area=[P(LOCK_BODY)], dotcut=KH_DOT)
icon('lock-key-open', CAT, ['unlocked', 'keyhole lock', 'open'],
     line=[P(LOCK_BODY), P(SHACKLE_OPEN)], detail=KH_SLOT, area=[P(LOCK_BODY)], dotcut=KH_DOT)

# laminated: stacked plates
LAM = [L(48, 141, 208, 141), L(48, 179, 208, 179)]
icon('lock-laminated', CAT, ['padlock', 'heavy lock', 'secure'],
     line=[P(LOCK_BODY), P(SHACKLE)], detail=LAM, area=[P(LOCK_BODY)])
icon('lock-laminated-open', CAT, ['open padlock', 'unlocked', 'access'],
     line=[P(LOCK_BODY), P(SHACKLE_OPEN)], detail=LAM, area=[P(LOCK_BODY)])

# slash
icon('lock-slash', CAT, ['unsecured', 'lock off', 'no lock', 'slash'],
     line=slashed([LOCK_BODY, SHACKLE, 'M128 144 L128 176']) + [L(*SLASH[0], *SLASH[1])])

# reset: small padlock inside a counter-clockwise arrow
RC = (128, 128); RR = 84
r_end = polar(RC, RR, -135)
icon('lock-reset', CAT, ['reset password', 'lock reset', 'recover', 'refresh'],
     line=[P(f'M{pt(polar(RC, RR, 177))} A{RR} {RR} 0 1 0 {pt(r_end)}'),
           PL([(r_end[0] + 34, r_end[1]), r_end, (r_end[0], r_end[1] - 34)]),
           R(98, 126, 60, 46, 10), P('M110 126 V116 A18 18 0 0 1 146 116 V126')],
     area=[R(98, 126, 60, 46, 10)])

# scan corners
CORNERS = ['M32 88 V48 A16 16 0 0 1 48 32 H88', 'M224 88 V48 A16 16 0 0 0 208 32 H168',
           'M224 168 V208 A16 16 0 0 1 208 224 H168', 'M32 168 V208 A16 16 0 0 0 48 224 H88']
SL_BODY = rrect(84, 118, 88, 64, 12)
SL_SHACKLE = 'M102 118 V102 A26 26 0 0 1 154 102 V118'
icon('lock-scan', CAT, ['lock', 'access', 'scan', 'secure'],
     line=[P(c) for c in CORNERS] + [P(SL_BODY), P(SL_SHACKLE)], area=[P(SL_BODY)], dotcut=[C(128, 150, 14)])
SA, SB = (60, 60), (196, 196)
icon('lock-scan-slash', CAT, ['lock scan', 'off', 'disabled', 'hidden', 'lock'],
     line=[P(c) for c in CORNERS] + slashed([SL_BODY, SL_SHACKLE], SA, SB, 24) + [L(*SA, *SB)])

# ------------------------------------------------------------------ keyhole
KHC = (128, 104); KHR = 28
kp, kq = (112, KHC[1] + math.sqrt(KHR ** 2 - 16 ** 2)), (144, KHC[1] + math.sqrt(KHR ** 2 - 16 ** 2))
KEYHOLE = f'M{pt(kp)} A{KHR} {KHR} 0 1 1 {pt(kq)} L156 176 L100 176 Z'
KEYHOLE = tf(KEYHOLE, 1, (0, 0), (0, 4))
icon('keyhole', CAT, ['keyhole', 'lock', 'access', 'secure', 'security'],
     line=[C(128, 128, 96)], detail=[P(KEYHOLE)], area=[C(128, 128, 96)], hole=[P(KEYHOLE)])

# ------------------------------------------------------------------ badge variants of other bases
BR = load('browser')
BR_RECT = rrect(32, 40, 192, 176, 14)
for name, b, tags in [('browser-lock', 'lock', ['locked page', 'secure browser', 'private window']),
                      ('browser-shield', 'shield', ['secure site', 'https', 'safe browsing'])]:
    with_badge(name, tags, BR_RECT, b, detail=BR['detail'], dotcut=BR['dotcut'])

ENV = load('envelope')
with_badge('envelope-shield', ['secure mail', 'protected', 'envelope', 'shield', 'protected mail'],
           rrect(32, 56, 192, 144, 14), 'shield', detail=ENV['detail'])

with_badge('file-shield', ['privacy policy', 'secure document', 'protected file', 'shield', 'safe'],
           'M56 32 H152 L200 80 V224 H56 Z', 'shield', detail=[P('M152 32 V80 H200')])

IMG = rrect(32, 48, 192, 160, 14)
with_badge('image-shield', ['protected image', 'copyright', 'photo', 'shield'], IMG, 'shield',
           detail=[P('M44 188 L96 136 L117 157'), C(152, 96, 16)])

# house: walls cut like house-shield, door dropped
bd = BADGES['lock']
hl = cut_paths(['M48 112 V208 H208 V112'], bd['R'], minlen=24)
_, ha = badge_cut('M48 112 L128 44 L208 112 V208 H48 Z', bd['R'])
icon('house-lock', CAT, ['home security', 'locked', 'house', 'lock'],
     line=hl + [P('M32 124 L128 40 L224 124')] + bd['line'], area=ha + bd['area'])

# cloud with a shield inside
CLOUD = load('cloud')
SHIELD = 'M128 32 L208 64 V120 C208 176 168 208 128 224 C88 208 48 176 48 120 V64 Z'
CS = tf(SHIELD, 0.34, (128, 128), (128, 142))
icon('cloud-shield', CAT, ['cloud security', 'protection', 'backup', 'shield'],
     line=CLOUD['line'], detail=[P(CS)], area=CLOUD['area'])

# ------------------------------------------------------------------ fingerprint
FP = [dval(e) for e in load('fingerprint')['line']]
fc = BADGES['check']
icon('fingerprint-check', CAT, ['verified', 'biometric ok', 'authenticated'],
     line=cut_paths(FP, fc['R'], 14) + fc['line'])
fx = BADGES['x']
icon('fingerprint-x', CAT, ['biometric failed', 'access denied', 'unrecognised'],
     line=cut_paths(FP, fx['R'], 14) + fx['line'])
icon('fingerprint-slash', CAT, ['fingerprint off', 'biometrics disabled', 'touch id', 'security', 'biometrics off'],
     line=slashed(FP, gap=26, minlen=14) + [L(*SLASH[0], *SLASH[1])])

PHONE = load('device-mobile')
icon('device-mobile-fingerprint', CAT, ['phone unlock', 'biometric login', 'touch id'],
     line=PHONE['line'], area=PHONE['area'],
     detail=PHONE['detail'] + [P('M100 180 V140 A28 28 0 0 1 156 140 V164'), L(128, 144, 128, 192)])

# ------------------------------------------------------------------ scans
EYE = 'M24 128 C56 72 96 56 128 56 C160 56 200 72 232 128 C200 184 160 200 128 200 C96 200 56 184 24 128 Z'
ES = tf(EYE, 0.6)
icon('eye-scan', CAT, ['retina scan', 'biometric', 'iris', 'iris scan', 'eye recognition'],
     line=[P(c) for c in CORNERS] + [P(ES)], area=[P(ES)], dotcut=[C(128, 128, 22)])

EAR = load('ear')
EAR_L = tf(dval(EAR['line'][0]), 0.6, (134, 130), (128, 128))
EAR_A = tf(dval(EAR['area'][0]), 0.6, (134, 130), (128, 128))
icon('ear-scan', CAT, ['ear', 'biometric', 'scan'],
     line=[P(c) for c in CORNERS] + [P(EAR_L)], area=[P(EAR_A)])

FACE_EYES = [L(100, 96, 100, 112), L(156, 96, 156, 112)]
icon('face-id', CAT, ['face id', 'face recognition', 'biometric', 'scan'],
     line=[P(c) for c in CORNERS] + FACE_EYES + [PL([(128, 96), (128, 136), (116, 136)]),
           P(f'M100 156 ' + arc_to((128, 128), 40, (100, 156), (156, 156), lambda m: m[1]))])
icon('face-id-error', CAT, ['face id', 'failed', 'biometric'],
     line=[P(c) for c in CORNERS] + [L(100, 100, 100, 116), L(156, 100, 156, 116),
           P(f'M100 168 ' + arc_to((128, 196.6), 40, (100, 168), (156, 168), lambda m: -m[1]))])

# ------------------------------------------------------------------ passport
icon('e-passport', CAT, ['passport', 'biometric', 'travel', 'id'],
     line=[R(48, 32, 160, 192, 14)],
     detail=[R(76, 56, 104, 100, 12), C(128, 106, 18), L(76, 106, 110, 106), L(146, 106, 180, 106),
             L(100, 192, 156, 192)],
     area=[R(48, 32, 160, 192, 14)])

# ------------------------------------------------------------------ firewall
WALL = load('wall')
WALL_D = [dval(e) for e in WALL['detail']]
WALL_R = rrect(32, 48, 192, 160, 12)
with_badge('firewall', ['firewall', 'network', 'protection', 'brick wall'], WALL_R, 'fire', detail_cut=WALL_D)
with_badge('firewall-check', ['firewall', 'protected', 'network', 'allowed'], WALL_R, 'check', detail_cut=WALL_D)

# ------------------------------------------------------------------ fish hook
HOOK = ['M172 72 V152 A56 56 0 0 1 60 152 V104', 'M60 104 L86 130']
HOOK_EYE = (172, 52, 20)
icon('fish-hook', CAT, ['phishing', 'scam', 'hook', 'bait', 'fishing'],
     line=[P(d) for d in HOOK] + [C(*HOOK_EYE)])
icon('fish-hook-slash', CAT, ['fish hook', 'off', 'disabled', 'hidden', 'fish'],
     line=slashed(HOOK + [circ(*HOOK_EYE)]) + [L(*SLASH[0], *SLASH[1])])

# ------------------------------------------------------------------ identification card slash
ID = load('identification-card')
ID_D = [rrect(32, 56, 192, 144, 14), circ(90, 104, 18), 'M150 108 L188 108', 'M150 148 L176 148']
icon('identification-card-slash', CAT, ['identification card', 'off', 'disabled', 'hidden', 'identification'],
     line=slashed(ID_D) + slashed([bez_segs([(60, 168), (60, 152), (72, 144), (90, 144)], [(90, 144), (108, 144), (120, 152), (120, 168)], close=True)])
     + [L(*SLASH[0], *SLASH[1])])

# ------------------------------------------------------------------ incognito
HAT = 'M64 112 L82 54 A12 12 0 0 1 93.5 46 H162.5 A12 12 0 0 1 174 54 L192 112'
INC_LINE = [P(HAT), L(32, 112, 224, 112), C(80, 172, 32), C(176, 172, 32), P('M112 168 Q128 156 144 168')]
icon('incognito', CAT, ['incognito', 'private', 'anonymous', 'spy'],
     line=INC_LINE, area=[P(HAT + ' Z'), C(80, 172, 32), C(176, 172, 32)])
icon('incognito-slash', CAT, ['incognito', 'off', 'disabled', 'hidden'],
     line=slashed([HAT, 'M32 112 L224 112', circ(80, 172, 32), circ(176, 172, 32), 'M112 168 L128 162 L144 168'])
     + [L(*SLASH[0], *SLASH[1])])

# ------------------------------------------------------------------ keys
def rotp(pts):
    return [(x, y - 8) for x, y in rot(pts, -45)]


bow_c = rotp([(46, 128)])[0]
sk_shaft = rotp([(82, 128), (220, 128)])
sk_collar = rotp([(114, 110), (114, 146)])
sk_bit = rotp([(186, 128), (186, 166), (220, 166), (220, 128)])
icon('key-skeleton', CAT, ['skeleton key', 'old key', 'antique', 'unlock'],
     line=[C(*bow_c, 36), PL(sk_shaft), PL(sk_collar), PL(sk_bit)])

KEY = ['M129 127 L208 48', 'M192 64 L216 88', 'M164 92 L184 112']
icon('key-slash', CAT, ['no access', 'key off', 'revoked', 'disabled'],
     line=slashed([circ(92, 164, 52)] + KEY) + [L(*SLASH[0], *SLASH[1])])

print(save(overwrite=True))
