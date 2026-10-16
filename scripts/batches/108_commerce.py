import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM, TM, CH = 'Commerce', 'Time', 'Charts'


# ---------------------------------------------------------------- helpers
def seg_outside(p, q, c, r):
    """Portion(s) of segment p-q that lie outside circle (c, r), as list of (a, b)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    fx, fy = p[0] - c[0], p[1] - c[1]
    A = dx * dx + dy * dy
    Bq = 2 * (fx * dx + fy * dy)
    Cq = fx * fx + fy * fy - r * r
    disc = Bq * Bq - 4 * A * Cq
    if disc <= 0:
        return [(p, q)]
    s = math.sqrt(disc)
    t1, t2 = (-Bq - s) / (2 * A), (-Bq + s) / (2 * A)
    at = lambda t: (p[0] + dx * t, p[1] + dy * t)
    out = []
    if t1 > 0:
        out.append((p, at(min(t1, 1))))
    if t2 < 1:
        out.append((at(max(t2, 0)), q))
    return [(a, b) for a, b in out if dist(a, b) > 0.5]


def tf(points, s, c_from, c_to):
    return [(c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s) for x, y in points]


def arrowhead(tip, d, arm=24):
    """Open chevron at tip pointing along unit-ish direction d (90-degree head)."""
    a = math.atan2(d[1], d[0])
    return PL([polar(tip, arm * math.sqrt(2), math.degrees(a) + 135), tip,
               polar(tip, arm * math.sqrt(2), math.degrees(a) - 135)])


# ---------------------------------------------------------------- badge marks (centre B, radius ~32)
def marks(kind, B):
    x, y = B
    m = {'line': [], 'area': [], 'dot': [], 'dotcut': [], 'detail': [], 'hole': []}
    if kind == 'plus':
        m['line'] += [L(x - 28, y, x + 28, y), L(x, y - 28, x, y + 28)]
    elif kind == 'minus':
        m['line'] += [L(x - 28, y, x + 28, y)]
    elif kind == 'x':
        m['line'] += [L(x - 22, y - 22, x + 22, y + 22), L(x + 22, y - 22, x - 22, y + 22)]
    elif kind == 'check':
        m['line'] += [PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 14)])]
    elif kind == 'warning':
        m['line'] += [L(x, y - 32, x, y)]
        m['dot'] += [C(x, y + 28, 16)]
    elif kind == 'question':
        c = (x, y - 28)
        st = polar(c, 14, 180)
        en = polar(c, 14, 60)
        m['line'] += [P(f'M{pt(st)} A14 14 0 1 1 {pt(en)} C{f(x + 2)} {f(y - 13)} {f(x)} {f(y - 10)} {f(x)} {f(y - 4)}')]
        m['dot'] += [C(x, y + 28, 16)]
    elif kind == 'arrow-up':
        m['line'] += [L(x, y + 28, x, y - 28), PL([(x - 24, y - 4), (x, y - 28), (x + 24, y - 4)])]
    elif kind == 'arrow-down':
        m['line'] += [L(x, y - 28, x, y + 28), PL([(x - 24, y + 4), (x, y + 28), (x + 24, y + 4)])]
    elif kind == 'pause':
        m['line'] += [L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)]
    elif kind == 'code':
        m['line'] += [PL([(x - 12, y - 22), (x - 30, y), (x - 12, y + 22)]),
                      PL([(x + 12, y - 22), (x + 30, y), (x + 12, y + 22)])]
    elif kind == 'dollar':
        m['line'] += [L(x, y - 36, x, y + 36),
                      P(f'M{f(x + 18)} {f(y - 26)} H{f(x - 6)} A13 13 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A13 13 0 0 1 {f(x + 6)} {f(y + 26)} H{f(x - 18)}')]
    elif kind == 'percent':
        m['line'] += [L(x + 22, y - 22, x - 22, y + 22)]
        m['dot'] += [C(x - 20, y - 20, 14), C(x + 20, y + 20, 14)]
    elif kind == 'gear':
        g = []
        for i in range(6):
            t = i * 60 - 90
            g += [polar(B, 21, t - 22), polar(B, 31, t - 13), polar(B, 31, t + 13), polar(B, 21, t + 22)]
        d = 'M' + pt(g[0])
        for i in range(6):
            a, b, cc, dd = g[i * 4:i * 4 + 4]
            if i:
                d += f' A21 21 0 0 1 {pt(a)}'
            d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
        d += f' A21 21 0 0 1 {pt(g[0])} Z'
        m['line'] += [P(d)]
        m['area'] += [P(d)]
        m['hole'] = [C(x, y, 12)]
    elif kind == 'heart':
        s = 0.34
        T = lambda px, py: pt((x + (px - 128) * s, y + 4 + (py - 136) * s))
        r = f(50 * s)
        d = (f'M{T(128, 212)} C{T(128, 212)} {T(32, 160)} {T(32, 98)} A{r} {r} 0 0 1 {T(128, 78)} '
             f'A{r} {r} 0 0 1 {T(224, 98)} C{T(224, 160)} {T(128, 212)} {T(128, 212)} Z')
        m['line'] += [P(d)]
        m['area'] += [P(d)]
    elif kind == 'star':
        st = [polar((x, y + 3), 36 if i % 2 == 0 else 16, -90 + i * 36) for i in range(10)]
        m['line'] += [PG(st)]
        m['area'] += [PG(st)]
    elif kind == 'lightning':
        pts = [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]
        pp = tf(pts, 0.36, (128, 128), B)
        m['line'] += [PG(pp)]
        m['area'] += [PG(pp)]
    elif kind == 'magnifying-glass':
        m['line'] += [C(x - 6, y - 6, 22), L(x + 11, y + 11, x + 28, y + 28)]
        m['area'] += [C(x - 6, y - 6, 22)]
    elif kind == 'push-pin':
        pts = [(162.03, 33.63), (210.94, 74.67), (186.36, 89.76), (157.05, 124.7), (153.32, 192.99),
               (55.51, 110.92), (122.12, 95.39), (151.43, 60.45)]
        pp = tf(pts, 0.36, (128, 128), (x + 4, y - 4))
        nd = tf([(104.41, 151.96), (51.65, 214.84)], 0.36, (128, 128), (x + 4, y - 4))
        m['line'] += [PG(pp), PL(nd)]
        m['area'] += [PG(pp)]
    elif kind == 'share':
        m['line'] += [P(f'M{f(x - 24)} {f(y + 26)} V{f(y + 14)} A24 24 0 0 1 {f(x)} {f(y - 10)} H{f(x + 26)}'),
                      PL([(x + 10, y - 26), (x + 26, y - 10), (x + 10, y + 6)])]
    return m


# ---------------------------------------------------------------- timeline
tl_c = [50, 128, 206]
icon('timeline', CH, ['timeline', 'history', 'milestones', 'events', 'steps'],
     line=[L(68, 128, 110, 128), L(146, 128, 188, 128)] + [C(cx, 128, 18) for cx in tl_c]
     # labels: above, below, above
     + [L(32, 72, 72, 72), L(104, 184, 152, 184), L(184, 72, 224, 72)],
     area=[C(cx, 128, 18) for cx in tl_c])


def tl_event(dx=0, right_line=True):
    bub = (f'M{70 + dx} 32 H{186 + dx} A14 14 0 0 1 {200 + dx} 46 V110 A14 14 0 0 1 {186 + dx} 124 '
           f'H{148 + dx} L{128 + dx} 144 L{108 + dx} 124 H{70 + dx} A14 14 0 0 1 {56 + dx} 110 V46 '
           f'A14 14 0 0 1 {70 + dx} 32 Z')
    cx = 128 + dx
    ln = [P(bub), C(cx, 204, 20), L(32, 204, cx - 40, 204)]
    if right_line:
        ln.append(L(cx + 40, 204, 224, 204))
    return dict(line=ln, detail=[L(96 + dx, 78, 160 + dx, 78)], area=[P(bub), C(cx, 204, 20)])


icon('timeline-event', TM, ['timeline', 'event', 'milestone', 'history'], **tl_event())

BT = (188, 192)
for kind, nm, tags in [
    ('x', 'timeline-event-x', ['timeline event', 'remove', 'delete', 'cancel', 'timeline']),
    ('plus', 'timeline-event-plus', ['timeline event', 'add', 'new', 'create', 'timeline']),
    ('minus', 'timeline-event-minus', ['timeline event', 'remove', 'subtract', 'timeline', 'event']),
    ('warning', 'timeline-event-warning', ['timeline event', 'warning', 'alert', 'error', 'timeline']),
]:
    base = tl_event(-24, right_line=False)
    mk = marks(kind, (BT[0], BT[1] - (6 if kind == 'warning' else 0)))
    icon(nm, TM, tags, line=base['line'] + mk['line'], detail=base['detail'],
         area=base['area'] + mk['area'], dot=mk['dot'])

# ---------------------------------------------------------------- trend-up-down
icon('trend-up-down', CH, ['volatile', 'up and down', 'trend', 'fluctuation'],
     line=[PL([(40, 80), (104, 144), (144, 104), (216, 176)]),
           PL([(96, 80), (40, 80), (40, 136)]), PL([(160, 176), (216, 176), (216, 120)])])

# ---------------------------------------------------------------- atm
atm_body = ('M80 136 H46 A14 14 0 0 1 32 122 V46 A14 14 0 0 1 46 32 H210 A14 14 0 0 1 224 46 V122 '
            'A14 14 0 0 1 210 136 H176')
bill = 'M80 80 V210 A14 14 0 0 0 94 224 H162 A14 14 0 0 0 176 210 V80'
icon('atm', CM, ['cash machine', 'bank', 'withdraw', 'money'],
     line=[P(atm_body), P(bill)],
     detail=[L(56, 80, 200, 80), C(128, 180, 18)],
     area=[P(atm_body + ' Z'), P(bill + ' Z')])

# ---------------------------------------------------------------- barcodes
bc = load('barcode')
brackets = bc['line'][:4]
icon('barcode-scan', CM, ['scan barcode', 'upc', 'scanner', 'checkout', 'scan line'],
     line=brackets + [L(x, 72, x, 100) for x in (80, 112, 144, 176)]
     + [L(x, 156, x, 184) for x in (80, 112, 144, 176)] + [L(40, 128, 216, 128)])

gun = ('M140 44 H210 A14 14 0 0 1 224 58 V94 A14 14 0 0 1 210 108 H200 L188 202 A14 14 0 0 1 174 214 '
       'H160 A12 12 0 0 1 148 200 L156 108 H140 A32 32 0 0 1 140 44 Z')
icon('barcode-scanner', CM, ['scanner', 'checkout', 'barcode reader', 'retail'],
     line=[P(gun), L(92, 64, 40, 44), L(92, 88, 40, 108)]
     + [L(x, 156, x, 208) for x in (40, 72, 104)],
     area=[P(gun)])

# barcode-slash: base barcode with the bars opened where the slash crosses
SL = ((56, 56), (200, 200))
bars = []
for x in (80, 112, 144, 176):
    for a, b in seg_outside((x, 88), (x, 168), (x, x), 40):
        if dist(a, b) >= 14:
            bars.append(L(a[0], a[1], b[0], b[1]))
icon('barcode-slash', CM, ['barcode', 'disabled', 'off', 'commerce'],
     line=brackets + bars + [L(*SL[0], *SL[1])])

# ---------------------------------------------------------------- basket variants
bk = load('basket')
B = (184, 184)
RB = 64


def basket_badge(name, tags, kind):
    p0, p1, p2, p3 = (48, 104), (68, 208), (188, 208), (208, 104)
    # right side from top corner down to the cut, bottom from left to the cut
    rs = seg_outside(p3, p2, B, RB)[0]
    bt = seg_outside(p1, p2, B, RB)[0]
    ln = P(f'M{pt(rs[1])} L{pt(p3)}') if False else None
    body = P(f'M{pt(bt[1])} L{pt(p1)} L{pt(p0)}')
    stub = P(f'M{pt(p3)} L{pt(rs[1])}')
    area = P(f'M{pt(p0)} L{pt(p3)} L{pt(rs[1])} '
             + arc_to(B, RB, rs[1], bt[1], lambda m: -dist(m, (100, 100))) + f' L{pt(p1)} Z')
    mk = marks(kind, B)
    icon(name, CM, tags,
         line=[body, stub, bk['line'][1], bk['line'][2]] + mk['line'],
         detail=[bk['detail'][0]] + mk['detail'],
         area=[area] + mk['area'], dot=mk['dot'], dotcut=mk['dotcut'], hole=mk['hole'])


for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['basket', 'decrease', 'download', 'shopping', 'cart']),
    ('arrow-up', 'arrow-up', ['basket', 'increase', 'upload', 'shopping', 'cart']),
    ('check', 'check', ['basket', 'done', 'approved', 'shopping', 'cart']),
    ('code', 'code', ['basket', 'developer', 'code', 'shopping', 'cart']),
    ('dollar', 'currency-dollar', ['basket', 'money', 'price', 'shopping', 'cart']),
    ('percent', 'discount', ['basket', 'sale', 'percent', 'shopping', 'cart']),
    ('gear', 'gear', ['basket', 'settings', 'configure', 'shopping', 'cart']),
    ('heart', 'heart', ['basket', 'favorite', 'like', 'shopping', 'cart']),
    ('lightning', 'lightning', ['basket', 'fast', 'power', 'shopping', 'cart']),
    ('magnifying-glass', 'magnifying-glass', ['basket', 'search', 'find', 'shopping', 'cart']),
    ('minus', 'minus', ['basket', 'remove', 'subtract', 'shopping', 'cart']),
    ('pause', 'pause', ['basket', 'paused', 'hold', 'shopping', 'cart']),
    ('plus', 'plus', ['basket', 'add', 'new', 'shopping', 'cart']),
    ('push-pin', 'push-pin', ['basket', 'pinned', 'pin', 'shopping', 'cart']),
    ('question', 'question', ['basket', 'help', 'unknown', 'shopping', 'cart']),
    ('share', 'share', ['basket', 'share', 'send', 'shopping', 'cart']),
    ('star', 'star', ['basket', 'favorite', 'starred', 'shopping', 'cart']),
    ('warning', 'warning', ['basket', 'warning', 'error', 'shopping', 'cart']),
    ('x', 'x', ['basket', 'remove', 'cancel', 'shopping', 'cart']),
]:
    basket_badge('basket-' + suffix, tags, kind)

icon('basket-slash', CM, ['basket', 'disabled', 'off', 'shopping', 'cart'],
     line=bk['line'] + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- boxes
box_out = ('M32 140 A12 12 0 0 1 44 128 H80 V44 A12 12 0 0 1 92 32 H164 A12 12 0 0 1 176 44 V128 H212 '
           'A12 12 0 0 1 224 140 V212 A12 12 0 0 1 212 224 H44 A12 12 0 0 1 32 212 Z')
icon('boxes', CM, ['boxes', 'inventory', 'stock', 'warehouse'],
     line=[P(box_out), L(80, 128, 176, 128), L(128, 128, 128, 224)],
     detail=[L(94, 128, 162, 128), L(128, 142, 128, 210),
             L(112, 72, 144, 72), L(64, 168, 96, 168), L(160, 168, 192, 168)],
     area=[P(box_out)])

# ---------------------------------------------------------------- cards
card_in = 'M48 88 V194 A14 14 0 0 0 62 208 H194 A14 14 0 0 0 208 194 V88'
icon('card-insert', CM, ['insert card', 'chip', 'atm', 'payment'],
     line=[L(32, 56, 224, 56), P(card_in)],
     detail=[R(72, 120, 44, 36, 10), L(164, 180, 164, 116), PL([(148, 132), (164, 116), (180, 132)])],
     area=[P(card_in + ' Z')])

term = R(48, 112, 160, 112, 16)
card_top = 'M80 112 V44 A12 12 0 0 1 92 32 H164 A12 12 0 0 1 176 44 V112'
icon('card-reader', CM, ['payment terminal', 'pos', 'card machine', 'smart card reader', 'card terminal'],
     line=[term, P(card_top)],
     detail=[L(80, 68, 176, 68)],
     area=[term, P(card_top + ' Z')],
     dotcut=[C(x, y, 14) for y in (152, 188) for x in (92, 128, 164)])

pen = 'M196 56 A12 12 0 0 1 220 56 V180 L208 212 L196 180 Z'
icon('checkbook', CM, ['cheque', 'checkbook', 'payment', 'bank'],
     line=[R(24, 56, 136, 104, 14), L(40, 192, 144, 192), P(pen)],
     detail=[L(56, 92, 128, 92), L(88, 128, 128, 128)],
     area=[R(24, 56, 136, 104, 14), P(pen)])

# ---------------------------------------------------------------- coins
FC = (108, 128); FRX, FRY = 76, 96
face = E(FC[0], FC[1], FRX, FRY)
edge_d = f'M{FC[0]} 32 H{FC[0] + 36} A{FRX} {FRY} 0 0 1 {FC[0] + 36} 224 H{FC[0]}'
edge = P(edge_d)
fa, fb = (FC[0] + FRX * math.cos(math.radians(50)), FC[1] - FRY * math.sin(math.radians(50))), \
         (FC[0] + FRX * math.cos(math.radians(50)), FC[1] + FRY * math.sin(math.radians(50)))
seam = P(f'M{pt(fa)} A{FRX} {FRY} 0 0 1 {pt(fb)}')
coin_area = [face, P(edge_d + ' Z')]


def coin(name, tags, sym, dots=()):
    icon(name, CM, tags, line=[face, edge], detail=[seam] + sym, area=coin_area, dotcut=list(dots))


coin('coin', ['coin', 'money', 'token', 'currency', 'cent'], [E(FC[0], FC[1], 40, 60)])
coin('coin-yen', ['coin yen', 'coin', 'money', 'yen', 'commerce'],
     [PL([(84, 64), (108, 104), (132, 64)]), L(108, 104, 108, 192), L(84, 132, 132, 132), L(84, 164, 132, 164)])
coin('coin-euro', ['coin euro', 'coin', 'money', 'euro', 'commerce'],
     [P(f'M{pt((122 + 34 * math.cos(math.radians(-45)), 128 + 48 * math.sin(math.radians(-45))))} '
        f'A34 48 0 1 0 {pt((122 + 34 * math.cos(math.radians(45)), 128 + 48 * math.sin(math.radians(45))))}'),
      L(72, 112, 120, 112), L(72, 144, 120, 144)])
coin('coin-taka', ['coin taka', 'coin', 'money', 'taka', 'commerce'],
     [P('M74 84 A13 13 0 0 1 100 84 V156 A22 22 0 0 0 144 156 C144 144 138 138 128 138'),
      L(84, 112, 136, 112)])
coin('coin-yuan', ['coin yuan', 'coin', 'money', 'yuan', 'commerce'],
     [L(88, 76, 128, 76), L(72, 108, 144, 108), P('M98 108 C98 144 92 164 76 176'),
      P('M120 108 V160 A16 16 0 0 0 136 176 H144')])
pc = (125, 100)
p_st = polar(pc, 21, -25)
coin('coin-pound', ['coin pound', 'coin', 'money', 'pound', 'commerce'],
     [P(f'M{pt(p_st)} ' + arc_to(pc, 21, p_st, (104, 100), lambda m: -m[1]) + ' V160 C104 174 98 180 84 182 H144'),
      L(84, 136, 128, 136)])
coin('coin-rupee', ['coin rupee', 'coin', 'money', 'rupee', 'commerce'],
     [L(80, 76, 140, 76), L(80, 108, 140, 108), P('M84 76 H100 A32 32 0 0 1 100 140 H84 L136 188')])
icon('coin-slash', CM, ['no money', 'free', 'coin off', 'slash'], line=[face, edge, L(48, 48, 208, 208)])
coin('coin-bitcoin', ['bitcoin', 'crypto', 'coin'],
     [P('M80 80 V176 M80 80 H108 A22 22 0 0 1 108 124 H80 M108 124 H112 A26 26 0 0 1 112 176 H80'),
      L(100, 64, 100, 80), L(100, 176, 100, 192)])

# coins-swap
c1, c2 = (76, 76), (180, 180)
icon('coins-swap', CM, ['exchange', 'convert currency', 'swap'],
     line=[C(*c1, 40), C(*c2, 40),
           P('M144 52 H176 A28 28 0 0 1 204 80 V112'), PL([(184, 92), (204, 112), (224, 92)]),
           P('M112 204 H80 A28 28 0 0 1 52 176 V144'), PL([(32, 164), (52, 144), (72, 164)])],
     area=[C(*c1, 40), C(*c2, 40)],
     dotcut=[C(*c1, 14), C(*c2, 14)])

# ---------------------------------------------------------------- contactless
card = R(24, 56, 208, 144, 14)
wc = (96, 128)
cl_waves = []
for r, a in ((36, 45), (72, 40)):
    p, q = polar(wc, r, -a), polar(wc, r, a)
    cl_waves.append(P(f'M{pt(p)} A{r} {r} 0 0 1 {pt(q)}'))
icon('contactless', CM, ['rfid', 'nfc', 'tap to pay', 'contactless', 'nfc payment'],
     line=[card], detail=cl_waves, area=[card], dotcut=[C(*wc, 16)])

wc2 = (72, 128)
big = []
for r, a in ((40, 45), (80, 45), (120, 45)):
    p, q = polar(wc2, r, -a), polar(wc2, r, a)
    big.append(P(f'M{pt(p)} A{r} {r} 0 0 1 {pt(q)}'))
icon('contactless-slash', CM, ['contactless off', 'nfc off', 'tap to pay', 'disabled'],
     line=big + [L(48, 48, 208, 208)], dot=[C(*wc2, 16)])

# ---------------------------------------------------------------- coupon
tk = load('ticket')
icon('coupon', CM, ['coupon', 'voucher', 'discount', 'percent'],
     line=tk['line'], detail=[L(156, 100, 100, 156)], area=tk['area'],
     dotcut=[C(102, 102, 16), C(154, 154, 16)])

# ---------------------------------------------------------------- credit cards
X0, Y0, X1, Y1, RX = 24, 56, 232, 200, 14


def card_cut(B, rc):
    yr = B[1] - math.sqrt(rc * rc - (X1 - B[0]) ** 2)
    xb = B[0] - math.sqrt(rc * rc - (Y1 - B[1]) ** 2)
    outline = (f'M{f(X1)} {f(yr)} V{Y0 + RX} A{RX} {RX} 0 0 0 {X1 - RX} {Y0} H{X0 + RX} '
               f'A{RX} {RX} 0 0 0 {X0} {Y0 + RX} V{Y1 - RX} A{RX} {RX} 0 0 0 {X0 + RX} {Y1} H{f(xb)}')
    return P(outline), P(outline + f' A{f(rc)} {f(rc)} 0 0 1 {f(X1)} {f(yr)} Z')


icon('credit-card-back', CM, ['card back', 'cvv', 'magnetic stripe', 'credit card'],
     line=[card], detail=[L(24, 88, 232, 88), L(24, 124, 232, 124), L(56, 164, 136, 164), L(168, 164, 192, 164)],
     area=[card])

hand_sleeve = R(32, 144, 32, 72, 8)
hand = 'M64 152 H108 C120 152 126 160 132 168 H160 L194 146 A15 15 0 0 1 212 168 L168 212 H64 Z'
hcard = R(72, 32, 144, 84, 12)
icon('credit-card-hand', CM, ['credit card hand', 'payment', 'card', 'pay', 'credit'],
     line=[hand_sleeve, P(hand), hcard],
     detail=[L(96, 184, 140, 184), L(72, 64, 216, 64)],
     area=[P(hand), hcard])

BL = (186, 186)
ln, ar = card_cut(BL, 68)
lock_body = R(152, 172, 68, 52, 10)
icon('credit-card-lock', CM, ['secure payment', 'locked card', 'card security'],
     line=[ln, lock_body, P('M168 172 V160 A18 18 0 0 1 204 160 V172')],
     detail=[L(24, 104, 232, 104), L(56, 160, 96, 160)],
     area=[ar, lock_body], dotcut=[C(186, 198, 10)])

BM = (186, 184)
ln, ar = card_cut(BM, 66)
icon('credit-card-magnifying-glass', CM, ['card', 'search', 'find payment', 'credit card'],
     line=[ln, C(178, 176, 26), L(197, 195, 218, 216)],
     detail=[L(24, 104, 232, 104), L(56, 160, 96, 160)],
     area=[ar, C(178, 176, 26)])

print(save(overwrite=True))
