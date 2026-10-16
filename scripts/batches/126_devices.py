import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build as B_

DV = 'Devices'
SLASH = L(48, 48, 208, 208)


# ------------------------------------------------------------------ helpers
def xf(d, s, src, dst):
    """Scale an absolute path string (M L H V C A Z) by s about src and move src to dst."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cmd = [], 0, None
    X = lambda v: dst[0] + (float(v) - src[0]) * s
    Y = lambda v: dst[1] + (float(v) - src[1]) * s
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCAZ':
            cmd = t; out.append(t); i += 1
            continue
        if cmd in 'ML':
            out.append(f'{f(X(toks[i]))} {f(Y(toks[i + 1]))}'); i += 2
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(toks[i + k]))} {f(Y(toks[i + k + 1]))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'H':
            out.append(f(X(toks[i]))); i += 1
        elif cmd == 'V':
            out.append(f(Y(toks[i]))); i += 1
        elif cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {a} {la} {sw} {f(X(x))} {f(Y(y))}'); i += 7
    return re.sub(r'([MLHVCAZ]) ', r'\1', ' '.join(out))


# ------------------------------------------------------------------ badge marks
# each returns (roles dict, R) where R is the centreline radius used for clearance
def m_plus(c, h=26):
    return dict(line=[L(c[0] - h, c[1], c[0] + h, c[1]), L(c[0], c[1] - h, c[0], c[1] + h)]), h

def m_minus(c, h=26):
    return dict(line=[L(c[0] - h, c[1], c[0] + h, c[1])]), h

def m_x(c, h=21):
    return dict(line=[L(c[0] - h, c[1] - h, c[0] + h, c[1] + h), L(c[0] + h, c[1] - h, c[0] - h, c[1] + h)]), 28

def m_check(c):
    x, y = c
    return dict(line=[PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 16)])]), 30

def m_arrow(c, up):
    x, y = c
    s = -1 if up else 1
    return dict(line=[L(x, y - 28 * s, x, y + 28 * s), PL([(x - 22, y + 6 * s), (x, y + 28 * s), (x + 22, y + 6 * s)])]), 30

def m_code(c):
    x, y = c
    return dict(line=[PL([(x - 14, y - 24), (x - 34, y), (x - 14, y + 24)]),
                      PL([(x + 14, y - 24), (x + 34, y), (x + 14, y + 24)])]), 34

def m_dollar(c):
    x, y = c
    return dict(line=[L(x, y - 38, x, y + 38),
                      P(f'M{f(x + 22)} {f(y - 28)} H{f(x - 6)} A14 14 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A14 14 0 0 1 {f(x + 6)} {f(y + 28)} H{f(x - 22)}')]), 34

def m_percent(c):
    x, y = c
    return dict(line=[L(x + 28, y - 28, x - 28, y + 28)], dot=[C(x - 24, y - 24, 12), C(x + 24, y + 24, 12)]), 34

def m_gear(c, n=6, rb=25, rt=37):
    pts = []
    for i in range(n):
        t = -90 + i * 360 / n
        pts += [polar(c, rb, t - 22), polar(c, rt, t - 12), polar(c, rt, t + 12), polar(c, rb, t + 22)]
    d = 'M' + pt(pts[0])
    for i in range(n):
        a, b, cc, dd = pts[i * 4:i * 4 + 4]
        if i:
            d += f' A{rb} {rb} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{rb} {rb} 0 0 1 {pt(pts[0])} Z'
    return dict(line=[P(d)], area=[P(d)], dotcut=[C(c[0], c[1], 9)]), 38

HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
def m_heart(c, s=0.36):
    d = xf(HEART, s, (128, 140), c)
    return dict(line=[P(d)], area=[P(d)]), 34

LIGHTNING = 'M144 32 L56 144 H120 L104 224 L200 108 H136 Z'
def m_lightning(c, s=0.4):
    d = xf(LIGHTNING, s, (128, 128), c)
    return dict(line=[P(d)], area=[P(d)]), 36

def m_magnifier(c):
    x, y = c
    k = (x - 8, y - 8)
    e = polar(k, 20, 45)
    return dict(line=[C(k[0], k[1], 20), L(e[0], e[1], x + 26, y + 26)], area=[C(k[0], k[1], 20)]), 36

def m_pause(c):
    x, y = c
    return dict(line=[L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)]), 30

PIN = 'M162.03 33.63 L210.94 74.67 L186.36 89.76 L157.05 124.7 L153.32 192.99 L55.51 110.92 L122.12 95.39 L151.43 60.45 Z'
def m_pin(c, s=0.42):
    d = xf(PIN, s, (132, 124), c)
    nx = lambda v: c[0] + (v - 132) * s
    ny = lambda v: c[1] + (v - 124) * s
    return dict(line=[P(d), L(nx(104.41), ny(151.96), nx(51.65), ny(214.84))], area=[P(d)]), 38

def m_question(c):
    x, y = c
    k = (x, y - 18)
    a = polar(k, 18, 50)
    return dict(line=[P(f'M{f(x - 18)} {f(y - 18)} A18 18 0 1 1 {pt(a)} C{f(x + 4)} {f(y)} {f(x)} {f(y + 2)} {f(x)} {f(y + 8)} V{f(y + 10)}')],
                dot=[C(x, y + 38, 13)]), 36

def m_warning(c):
    x, y = c
    return dict(line=[L(x, y - 36, x, y + 6)], dot=[C(x, y + 36, 13)]), 36

def m_share(c):
    x, y = c
    return dict(line=[P(f'M{f(x - 30)} {f(y + 28)} C{f(x - 30)} {f(y - 2)} {f(x - 10)} {f(y - 12)} {f(x + 26)} {f(y - 12)}'),
                      PL([(x + 6, y - 32), (x + 26, y - 12), (x + 6, y + 8)])]), 34

def m_star(c, ro=36, ri=16):
    pts = [polar((c[0], c[1] + 3), ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]
    return dict(line=[PG(pts)], area=[PG(pts)]), 36

def m_pencil(c):
    u = (math.sqrt(0.5), -math.sqrt(0.5)); n = (math.sqrt(0.5), math.sqrt(0.5))
    at = lambda a, b: (c[0] + u[0] * a + n[0] * b, c[1] + u[1] * a + n[1] * b)
    pts = [at(-38, 0), at(-18, -15), at(36, -15), at(36, 15), at(-18, 15)]
    return dict(line=[PG(pts)], area=[PG(pts)]), 40


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, []).extend(v)
    return out



# ------------------------------------------------------------------ device bodies
MOB = dict(x=72, y=32, w=112, h=192, r=20)
TAB = dict(x=48, y=32, w=160, h=192, r=16)
mob = load('device-mobile')
tab = load('device-tablet')
SPEAKER = L(112, 64, 144, 64)


def rrect_bitten(b, c, rc):
    """Rounded-rect outline with its lower-right corner bitten by circle (c, rc): (line path, area path)."""
    x, y, w, h, r = b['x'], b['y'], b['w'], b['h'], b['r']
    X, Y = x + w, y + h
    yA = c[1] - math.sqrt(rc * rc - (X - c[0]) ** 2)
    xB = c[0] - math.sqrt(rc * rc - (Y - c[1]) ** 2)
    assert yA > y + r + 4 and xB > x + r + 4, (yA, xB)
    d = (f'M{f(X)} {f(yA)} V{f(y + r)} A{f(r)} {f(r)} 0 0 0 {f(X - r)} {f(y)} H{f(x + r)} '
         f'A{f(r)} {f(r)} 0 0 0 {f(x)} {f(y + r)} V{f(Y - r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(Y)} H{f(xB)}')
    area = d + ' ' + arc_to(c, rc, (xB, Y), (X, yA), lambda m: -dist(m, (x + w / 2, y + h / 2))) + ' Z'
    return P(d), P(area)


def dev_badge(name, tags, body, mark, c=(186, 188), gap=30):
    roles, R = mark(c)
    line, area = rrect_bitten(body, c, R + gap)
    base = dict(line=[line], area=[area], detail=[SPEAKER])
    icon(name, DV, tags, **merge(base, roles))


def T(s):
    return [t.strip() for t in s.split(',')]


def m_wrench(c, r=19):
    """Small open-ended wrench on the diagonal: ring with a slot to the upper right and a handle."""
    h = (c[0] + 13, c[1] - 13)
    a0, a1 = polar(h, r, -45 + 52), polar(h, r, -45 - 52)
    head = P(f'M{pt(a0)} A{r} {r} 0 1 1 {pt(a1)}')
    s = polar(h, r, 135)
    return dict(line=[head, L(s[0], s[1], c[0] - 30, c[1] + 30)]), 40


# ------------------------------------------------------------------ phone badges
dev_badge('device-mobile-magnifying-glass', T('device mobile, search, find, phone, smartphone'), MOB, m_magnifier)
dev_badge('device-mobile-minus', T('device mobile, remove, subtract, phone, smartphone'), MOB, m_minus)
dev_badge('device-mobile-pause', T('device mobile, paused, hold, phone, smartphone'), MOB, m_pause)
dev_badge('device-mobile-plus', T('device mobile, add, new, phone, smartphone'), MOB, m_plus)
dev_badge('device-mobile-push-pin', T('device mobile, pinned, pin, phone, smartphone'), MOB, m_pin, c=(186, 185), gap=26)
dev_badge('device-mobile-question', T('phone help, mobile question, support, phone, device mobile'), MOB, m_question, c=(188, 182))
dev_badge('device-mobile-star', T('device mobile, favorite, starred, phone, smartphone'), MOB, m_star, c=(186, 188))
dev_badge('device-mobile-warning', T('phone alert, mobile warning, error, phone, device mobile'), MOB, m_warning, c=(188, 182))
dev_badge('device-mobile-wrench', T('phone repair, mobile service, fix, phone'), MOB, m_wrench, c=(186, 186), gap=26)
dev_badge('device-mobile-x', T('blocked phone, mobile cancel, remove device, phone, device mobile'), MOB, m_x)

icon('device-mobile-slash', DV, T('phone off, mobile, no phone, disabled, device off'),
     line=mob['line'] + mob['detail'] + [SLASH])

# ------------------------------------------------------------------ tablet badges
dev_badge('device-tablet-arrow-down', T('device tablet, decrease, download, tablet, ipad'), TAB, lambda c: m_arrow(c, False))
dev_badge('device-tablet-arrow-up', T('device tablet, increase, upload, tablet, ipad'), TAB, lambda c: m_arrow(c, True))
dev_badge('device-tablet-check', T('device tablet, done, approved, tablet, ipad'), TAB, m_check)
dev_badge('device-tablet-code', T('device tablet, developer, code, tablet, ipad'), TAB, m_code, c=(186, 192))
dev_badge('device-tablet-currency-dollar', T('device tablet, money, price, tablet, ipad'), TAB, m_dollar, c=(188, 186))
dev_badge('device-tablet-gear', T('device tablet, settings, configure, tablet, ipad'), TAB, m_gear, c=(186, 186), gap=26)
dev_badge('device-tablet-heart', T('device tablet, favorite, like, tablet, ipad'), TAB, m_heart)
dev_badge('device-tablet-lightning', T('device tablet, fast, power, tablet, ipad'), TAB, m_lightning, c=(188, 185))
dev_badge('device-tablet-magnifying-glass', T('device tablet, search, find, tablet, ipad'), TAB, m_magnifier)
dev_badge('device-tablet-minus', T('device tablet, remove, subtract, tablet, ipad'), TAB, m_minus)
dev_badge('device-tablet-pause', T('device tablet, paused, hold, tablet, ipad'), TAB, m_pause)
dev_badge('device-tablet-plus', T('device tablet, add, new, tablet, ipad'), TAB, m_plus)
dev_badge('device-tablet-push-pin', T('device tablet, pinned, pin, tablet, ipad'), TAB, m_pin, c=(186, 185), gap=26)
dev_badge('device-tablet-question', T('device tablet, help, unknown, tablet, ipad'), TAB, m_question, c=(188, 182))
dev_badge('device-tablet-share', T('device tablet, share, send, tablet, ipad'), TAB, m_share)
dev_badge('device-tablet-star', T('device tablet, favorite, starred, tablet, ipad'), TAB, m_star, c=(186, 188))
dev_badge('device-tablet-warning', T('device tablet, warning, error, tablet, ipad'), TAB, m_warning, c=(188, 182))
dev_badge('device-tablet-x', T('device tablet, remove, cancel, tablet, ipad'), TAB, m_x)

icon('device-tablet-slash', DV, T('device tablet, disabled, off, tablet, ipad'),
     line=tab['line'] + tab['detail'] + [SLASH])


# ------------------------------------------------------------------ rotate: phone with a clockwise arc arrow
def arc_arrow(cc, ra, a0, a1, head=28):
    p, q = polar(cc, ra, a0), polar(cc, ra, a1)
    t = (-math.sin(math.radians(a1)), math.cos(math.radians(a1)))  # clockwise tangent at the tip
    back = (q[0] - t[0] * head, q[1] - t[1] * head)
    w1 = rot([back], 45, q)[0]; w2 = rot([back], -45, q)[0]
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return [P(f'M{pt(p)} A{ra} {ra} 0 {large} 1 {pt(q)}'), PL([w1, q, w2])]

ph = dict(x=40, y=84, w=88, h=140, r=16)
icon('device-mobile-rotate', DV, T('rotate, orientation, phone, flip, rotate screen'),
     line=[R(ph['x'], ph['y'], ph['w'], ph['h'], ph['r'])] + arc_arrow((104, 144), 100, -112, -12),
     detail=[L(72, 112, 96, 112)],
     area=[R(ph['x'], ph['y'], ph['w'], ph['h'], ph['r'])])


# ------------------------------------------------------------------ share: arrow leaving the phone to the right
icon('device-mobile-share', DV, T('share from phone, send, mobile share, transfer, device mobile'),
     line=[P('M144 100 V52 A20 20 0 0 0 124 32 H60 A20 20 0 0 0 40 52 V204 A20 20 0 0 0 60 224 H124 '
             'A20 20 0 0 0 144 204 V172'),
           L(96, 136, 216, 136), PL([(184, 104), (216, 136), (184, 168)])],
     detail=[L(76, 64, 108, 64)],
     area=[R(40, 32, 104, 192, 20)])


# ------------------------------------------------------------------ speaker: phone with sound waves
def wave(cc, r, span):
    p, q = polar(cc, r, -span), polar(cc, r, span)
    return P(f'M{pt(p)} A{r} {r} 0 0 1 {pt(q)}')

icon('device-mobile-speaker', DV, T('speakerphone, phone, audio, speaker, phone sound'),
     line=[R(32, 32, 96, 192, 20), wave((112, 128), 72, 32), wave((112, 128), 108, 34)],
     detail=[L(64, 64, 96, 64)],
     area=[R(32, 32, 96, 192, 20)])


# ------------------------------------------------------------------ ticket on the phone screen
TK = 'M100 100 H116 A12 12 0 0 0 140 100 H156 V180 H140 A12 12 0 0 0 116 180 H100 Z'
icon('device-mobile-ticket', DV, T('mobile ticket, e-ticket, boarding pass, phone'),
     line=mob['line'], detail=mob['detail'] + [P(TK)], area=mob['area'])


# ------------------------------------------------------------------ tap: pointing hand over the phone screen
HAND = load('hand-pointing')
HAND_D = re.search(r'd="([^"]+)"', HAND['line'][0]).group(1)
HAND_DET = [re.search(r'd="([^"]+)"', e).group(1) for e in HAND['detail']]


def rrect_pieces(b, keep, step=0.5):
    """Sub-paths of a rounded-rect outline (clockwise from top-left) where keep(point) is True."""
    x, y, w, h, r = b['x'], b['y'], b['w'], b['h'], b['r']
    segs = [('L', (x + r, y), (x + w - r, y)), ('A', (x + w - r, y + r), -90),
            ('L', (x + w, y + r), (x + w, y + h - r)), ('A', (x + w - r, y + h - r), 0),
            ('L', (x + w - r, y + h), (x + r, y + h)), ('A', (x + r, y + h - r), 90),
            ('L', (x, y + h - r), (x, y + r)), ('A', (x + r, y + r), 180)]
    lens = [dist(s[1], s[2]) if s[0] == 'L' else math.pi * r / 2 for s in segs]
    total = sum(lens)

    def at(s):
        s %= total
        for sg, ln in zip(segs, lens):
            if s <= ln:
                k = s / ln
                if sg[0] == 'L':
                    return (sg[1][0] + (sg[2][0] - sg[1][0]) * k, sg[1][1] + (sg[2][1] - sg[1][1]) * k)
                return polar(sg[1], r, sg[2] + 90 * k)
            s -= ln
        return at(0)

    n = int(total / step)
    flags = [keep(at(i * step)) for i in range(n)]
    if all(flags):
        return None
    k0 = flags.index(False)
    runs, cur = [], None
    for j in range(1, n + 1):
        i = (k0 + j) % n
        if flags[i] and cur is None:
            cur = [i * step]
        if not flags[i] and cur is not None:
            cur.append(((i - 1) % n) * step); runs.append(cur); cur = None
    out = []
    bounds = [0]
    for ln in lens:
        bounds.append(bounds[-1] + ln)
    for s0, s1 in runs:
        if s1 < s0:
            s1 += total
        d = 'M' + pt(at(s0))
        b_ = [bv for bv in bounds + [bv + total for bv in bounds] if s0 < bv < s1]
        for s in b_ + [s1]:
            # which segment does the stretch ending at s belong to?
            mid = (s - 1e-3) % total
            idx = max(i for i in range(len(segs)) if bounds[i] <= mid)
            p = at(s)
            d += (f' L{pt(p)}' if segs[idx][0] == 'L' else f' A{f(r)} {f(r)} 0 0 1 {pt(p)}')
        out.append(P(d))
    return out


s_h, tip, tip0 = 0.6, (118, 116), (94, 58)
hand_d = xf(HAND_D, s_h, tip0, tip)
hand_det = [xf(d, s_h, tip0, tip) for d in HAND_DET]
pb = dict(x=40, y=32, w=120, h=184, r=20)
hand_fill = B_.filled([hand_d])
clear_line = B_.union(hand_fill, B_.stroke([hand_d], 64))
clear_area = B_.union(hand_fill, B_.stroke([hand_d], 44))
phone_lines = rrect_pieces(pb, lambda p: not clear_line.contains(p))
phone_area = B_.to_d(B_.difference(B_.filled([R_d := f"M{pb['x']+pb['r']} {pb['y']} H{pb['x']+pb['w']-pb['r']} A{pb['r']} {pb['r']} 0 0 1 {pb['x']+pb['w']} {pb['y']+pb['r']} V{pb['y']+pb['h']-pb['r']} A{pb['r']} {pb['r']} 0 0 1 {pb['x']+pb['w']-pb['r']} {pb['y']+pb['h']} H{pb['x']+pb['r']} A{pb['r']} {pb['r']} 0 0 1 {pb['x']} {pb['y']+pb['h']-pb['r']} V{pb['y']+pb['r']} A{pb['r']} {pb['r']} 0 0 1 {pb['x']+pb['r']} {pb['y']} Z"]), clear_area))
icon('device-mobile-tap', DV, T('tap phone, contactless, touch, nfc'),
     line=phone_lines + [P(hand_d)],
     detail=[L(84, 64, 116, 64)] + [P(d) for d in hand_det],
     area=[P(phone_area), P(hand_d)])


# ------------------------------------------------------------------ bounds check (regular stroke must stay in 24..232)
for ic in ICONS:
    ds = []
    for role in ('line', 'detail'):
        for e in ic[role]:
            import xml.etree.ElementTree as ET
            ds.append(B_.element_d(ET.fromstring(e)))
    bx = B_.stroke(ds, 16).bounds
    if bx[0] < 23.9 or bx[1] < 23.9 or bx[2] > 232.1 or bx[3] > 232.1:
        print('OUT OF BOUNDS', ic['name'], [round(v, 1) for v in bx])

print(save(overwrite=True))
