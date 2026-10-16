import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Commerce'

# ---------------------------------------------------------------- outline cutter
# A path is a list of segments: ('L', p0, p1) or ('A', centre, r, a0, a1) (circular arc from angle a0 to a1,
# radians, screen coordinates so increasing angle = clockwise). cut() removes the part inside a badge
# clearance circle so a badge can sit in the corner, and returns the open outline and the matching area.

def seg_pt(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', seg_pt(s, t0), seg_pt(s, t1))
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_len(s):
    if s[0] == 'L':
        return dist(s[1], s[2])
    return abs(s[4] - s[3]) * s[2]


def seg_hits(s, B, rc):
    ts = []
    if s[0] == 'L':
        (x0, y0), (x1, y1) = s[1], s[2]
        dx, dy = x1 - x0, y1 - y0
        fx, fy = x0 - B[0], y0 - B[1]
        a = dx * dx + dy * dy; b = 2 * (fx * dx + fy * dy); cc = fx * fx + fy * fy - rc * rc
        disc = b * b - 4 * a * cc
        if disc > 0:
            for sg in (-1, 1):
                t = (-b + sg * math.sqrt(disc)) / (2 * a)
                if 1e-6 < t < 1 - 1e-6:
                    ts.append(t)
    else:
        c, r, a0, a1 = s[1:]
        d = dist(c, B)
        if abs(r - rc) < d < r + rc:
            for p in circle_x(c, r, B, rc):
                ang = math.atan2(p[1] - c[1], p[0] - c[0])
                for k in (-2, -1, 0, 1, 2):
                    aa = ang + 2 * math.pi * k
                    t = (aa - a0) / (a1 - a0)
                    if 1e-6 < t < 1 - 1e-6:
                        ts.append(t)
    return sorted(ts)


def pieces(segs, B, rc):
    """Split segments at the circle; return list of (segment, inside) in order."""
    out = []
    for s in segs:
        ts = [0] + seg_hits(s, B, rc) + [1]
        for t0, t1 in zip(ts, ts[1:]):
            sub = seg_sub(s, t0, t1)
            out.append((sub, dist(seg_pt(sub, 0.5), B) < rc))
    return out


def seg_d(s):
    p1 = seg_pt(s, 1)
    if s[0] == 'L':
        return f' L{pt(p1)}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f' A{f(r)} {f(r)} 0 {large} {sweep} {pt(p1)}'


def run_d(run):
    return f'M{pt(seg_pt(run[0], 0))}' + ''.join(seg_d(s) for s in run)


def cut(segs, B, rc, centroid=(128, 128), closed=True):
    """Return (line d, area d) for a closed outline opened around the badge at B."""
    ps = pieces(segs, B, rc)
    k = next(i for i, (s, ins) in enumerate(ps) if ins)
    ps = ps[k:] + ps[:k]
    run = [s for s, ins in ps if not ins]
    d = run_d(run)
    a, b = seg_pt(run[-1], 1), seg_pt(run[0], 0)
    area = d + ' ' + arc_to(B, rc, a, b, lambda m: -dist(m, centroid)) + ' Z'
    return P(d), P(area)


def cut_open(segs, B, rc, minlen=10):
    """Open path: keep the runs outside the circle (drops stubs shorter than minlen)."""
    out, run = [], []
    for s, ins in pieces(segs, B, rc) + [(None, True)]:
        if ins:
            if run and sum(seg_len(x) for x in run) >= minlen:
                out.append(P(run_d(run)))
            run = []
        else:
            run.append(s)
    return out


def poly_segs(points, closed=True):
    pts = list(points) + ([points[0]] if closed else [])
    return [('L', a, b) for a, b in zip(pts, pts[1:])]


def rect_segs(x, y, w, h, rx):
    r = rx; R2 = math.pi / 2
    return [('L', (x + r, y), (x + w - r, y)), ('A', (x + w - r, y + r), r, -R2, 0),
            ('L', (x + w, y + r), (x + w, y + h - r)), ('A', (x + w - r, y + h - r), r, 0, R2),
            ('L', (x + w - r, y + h), (x + r, y + h)), ('A', (x + r, y + h - r), r, R2, 2 * R2),
            ('L', (x, y + h - r), (x, y + r)), ('A', (x + r, y + r), r, 2 * R2, 3 * R2)]


# ---------------------------------------------------------------- badge marks (relative to centre B)
def off(B, pts):
    return [(B[0] + x, B[1] + y) for x, y in pts]


def mk_plus(B):
    return dict(line=[L(B[0] - 28, B[1], B[0] + 28, B[1]), L(B[0], B[1] - 28, B[0], B[1] + 28)])


def mk_minus(B):
    return dict(line=[L(B[0] - 28, B[1], B[0] + 28, B[1])])


def mk_x(B):
    return dict(line=[L(B[0] - 22, B[1] - 22, B[0] + 22, B[1] + 22), L(B[0] + 22, B[1] - 22, B[0] - 22, B[1] + 22)])


def mk_check(B):
    return dict(line=[PL(off(B, [(-28, 2), (-8, 22), (28, -14)]))])


def mk_heart(B):
    x, y = B[0], B[1] - 4
    d = (f'M{f(x)} {f(y + 30)} L{f(x - 22)} {f(y + 6)} A15 15 0 0 1 {f(x)} {f(y - 14)} '
         f'A15 15 0 0 1 {f(x + 22)} {f(y + 6)} Z')
    return dict(line=[P(d)], area=[P(d)])


def mk_pencil(B):
    pg = PG(off(B, [(-30, 30), (-24, 8), (8, -24), (22, -10), (-10, 22)]))
    return dict(line=[pg], area=[pg])


def mk_arrow(B, deg):
    """Arrow pointing in direction deg (0 = right, 90 = down)."""
    shaft = rot([(-28, 0), (28, 0)], deg, (0, 0))
    head = rot([(6, -22), (28, 0), (6, 22)], deg, (0, 0))
    return dict(line=[PL(off(B, shaft)), PL(off(B, head))])


def mk_diag(B, out=True):
    if out:  # up-right
        return dict(line=[L(B[0] - 24, B[1] + 24, B[0] + 24, B[1] - 24), PL(off(B, [(-6, -24), (24, -24), (24, 6)]))])
    return dict(line=[L(B[0] + 24, B[1] - 24, B[0] - 24, B[1] + 24), PL(off(B, [(-24, -6), (-24, 24), (6, 24)]))])


def mk_percent(B):
    return dict(line=[L(B[0] - 26, B[1] + 26, B[0] + 26, B[1] - 26)],
                dot=[C(B[0] - 22, B[1] - 22, 14), C(B[0] + 22, B[1] + 22, 14)])


def mk_search(B):
    c = (B[0] - 8, B[1] - 8)
    return dict(line=[C(c[0], c[1], 20), L(c[0] + 15, c[1] + 15, B[0] + 28, B[1] + 28)])


def mk_lock(B):
    x, y = B
    body = R(x - 28, y - 4, 56, 40, 8)
    return dict(line=[body, P(f'M{f(x - 16)} {f(y - 4)} V{f(y - 18)} A16 16 0 0 1 {f(x + 16)} {f(y - 18)} V{f(y - 4)}')],
                area=[body])


def mk_dollar(B, s=1.0):
    x, y = B
    S = (f'M{f(x + 24)} {f(y - 32)} H{f(x - 8)} A16 16 0 0 0 {f(x - 8)} {f(y)} H{f(x + 8)} '
         f'A16 16 0 0 1 {f(x + 8)} {f(y + 32)} H{f(x - 24)}')
    return dict(line=[L(x, y - 44, x, y + 44), P(S)])


def mk_euro(B):
    x, y = B
    c = (x + 8, y)
    a, b = polar(c, 36, -48), polar(c, 36, 48)
    return dict(line=[P(f'M{pt(a)} A36 36 0 1 0 {pt(b)}'), L(x - 36, y - 14, x + 8, y - 14), L(x - 36, y + 14, x + 8, y + 14)])


def mk_bitcoin(B):
    x, y = B
    d = (f'M{f(x - 20)} {f(y - 32)} H{f(x + 2)} A16 16 0 0 1 {f(x + 2)} {f(y)} H{f(x - 20)} '
         f'M{f(x + 2)} {f(y)} H{f(x + 6)} A16 16 0 0 1 {f(x + 6)} {f(y + 32)} H{f(x - 20)} V{f(y - 32)}')
    return dict(line=[P(d), L(x - 4, y - 44, x - 4, y - 32), L(x - 4, y + 32, x - 4, y + 44)])


def mk_refund(B):
    x, y = B[0] - 188, B[1] - 184
    return dict(line=[P(f'M{f(160 + x)} {f(168 + y)} L{f(196 + x)} {f(168 + y)} A20 20 0 0 1 {f(196 + x)} {f(208 + y)} L{f(172 + x)} {f(208 + y)}'),
                      PL(off((x, y), [(180, 148), (160, 168), (180, 188)]))])


def badge_icon(name, tags, ln, ar, mark, line=(), detail=(), area=(), dot=(), dotcut=(), hole=()):
    icon(name, CM, tags, line=[ln] + list(line) + mark.get('line', []), detail=list(detail),
         area=[ar] + list(area) + mark.get('area', []), dot=list(dot) + mark.get('dot', []),
         dotcut=list(dotcut), hole=list(hole))


# ---------------------------------------------------------------- exchange
A1, B1, RC1 = (194, 62), (62, 194), 30
ex_lines = [C(*A1, RC1), C(*B1, RC1),
            P('M124 62 A62 62 0 0 0 62 124'), PL([(40, 102), (62, 124), (84, 102)]),
            P('M132 194 A62 62 0 0 0 194 132'), PL([(216, 154), (194, 132), (172, 154)])]
icon('exchange', CM, ['exchange', 'swap', 'trade', 'transfer'], line=ex_lines, area=[C(*A1, RC1), C(*B1, RC1)])
icon('exchange-slash', CM, ['exchange', 'disabled', 'off', 'commerce'], line=ex_lines + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- gift card
bow = 'M100 128 C88 94 60 86 60 108 C60 125 80 128 100 128 C120 128 140 125 140 108 C140 86 112 94 100 128'
icon('gift-card', CM, ['gift card', 'voucher', 'present', 'coupon'],
     line=[R(32, 64, 192, 128, 14)],
     detail=[L(100, 64, 100, 192), L(32, 128, 224, 128), P(bow)],
     area=[R(32, 64, 192, 128, 14)])

g = load('gift')
icon('gift-slash', CM, ['gift', 'off', 'disabled', 'hidden'], line=g['line'] + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- gold bars
def bar(xb0, xb1, yb, h=72, inset=20):
    return PG([(xb0, yb), (xb1, yb), (xb1 - inset, yb - h), (xb0 + inset, yb - h)])
bars = [bar(32, 112, 216), bar(144, 224, 216), bar(88, 168, 112)]
icon('gold-bars', CM, ['gold', 'bullion', 'wealth', 'bars'], line=bars, area=bars)

# ---------------------------------------------------------------- hands (hand-coins hand)
hc = load('hand-coins')
CUFF = hc['line'][0]
PALM = hc['line'][1]
PALM_AREA = hc['area'][0]
CREASE = hc['detail'][0]
hand = dict(line=[CUFF, PALM], detail=[CREASE], area=[PALM_AREA])


def hand_icon(name, tags, line=(), detail=(), area=(), dot=()):
    icon(name, CM, tags, line=hand['line'] + list(line), detail=hand['detail'] + list(detail),
         area=hand['area'] + list(area), dot=list(dot))


hand_icon('hand-arrow-down', ['receive', 'take', 'deposit'],
          line=[L(144, 32, 144, 116), PL([(112, 84), (144, 116), (176, 84)])])
hand_icon('hand-arrow-up', ['give', 'offer', 'withdraw'],
          line=[L(144, 116, 144, 32), PL([(112, 64), (144, 32), (176, 64)])])
coin = (100, 80)
hand_icon('hand-deposit', ['deposit', 'pay in', 'savings'],
          line=[C(*coin, 36), L(184, 36, 184, 112), PL([(160, 88), (184, 112), (208, 88)])],
          detail=[L(100, 66, 100, 94)], area=[C(*coin, 36)])
hand_icon('hand-withdraw', ['withdraw', 'cash out', 'take money'],
          line=[C(*coin, 36), L(184, 112, 184, 36), PL([(160, 60), (184, 36), (208, 60)])],
          detail=[L(100, 66, 100, 94)], area=[C(*coin, 36)])
hand_icon('hand-card', ['pay by card', 'give card', 'card payment'],
          line=[R(88, 40, 128, 76, 12)], detail=[L(88, 72, 216, 72)], area=[R(88, 40, 128, 76, 12)])
hand_icon('hand-package', ['delivery', 'handover', 'consignment', 'parcel'],
          line=[R(96, 32, 96, 88, 10)], detail=[L(144, 32, 144, 64)], area=[R(96, 32, 96, 88, 10)])

# ---------------------------------------------------------------- kiosk
aw = 'M56 32 H200 L216 72 A29.33 29.33 0 0 1 157.33 72 A29.33 29.33 0 0 1 98.67 72 A29.33 29.33 0 0 1 40 72 Z'
icon('kiosk', CM, ['booth', 'kiosk', 'stand', 'stall'],
     line=[P(aw), L(56, 104, 56, 144), L(200, 104, 200, 144), R(40, 144, 176, 72, 12)],
     detail=[L(104, 32, 98.67, 72), L(152, 32, 157.33, 72)],
     area=[P(aw), R(40, 144, 176, 72, 12)])

# ---------------------------------------------------------------- money bag
MBC, MBR = (128, 152), 72
nk = math.degrees(math.asin(24 / MBR))
nl, nr = polar(MBC, MBR, -90 - nk), polar(MBC, MBR, -90 + nk)
bag_d = (f'M{pt(nl)} L80 40 H176 L{pt(nr)} A{MBR} {MBR} 0 1 1 {pt(nl)} Z')
TIE = L(92, nl[1], 164, nl[1])
icon('money-bag', CM, ['money bag', 'savings', 'wealth', 'cash', 'sack'],
     line=[P(bag_d), TIE], detail=mk_dollar((128, 156))['line'], area=[P(bag_d)])
bag_segs = (poly_segs([nr, (176, 40), (80, 40), nl], closed=False)
            + [('A', MBC, MBR, math.radians(-90 - nk) + 2 * math.pi, math.radians(-90 + nk))])
# segments run nr -> top -> nl -> (arc counter-clockwise on screen around the bottom) -> nr
BB, RCB = (196, 196), 62
bag_ln, bag_ar = cut(bag_segs, BB, RCB, centroid=MBC)
small_dollar = mk_dollar((116, 148))['line']
for nm, tags, mk in [
    ('money-bag-plus', ['moneybag plus', 'add', 'new', 'money bag', 'savings'], mk_plus),
    ('money-bag-heart', ['money bag', 'favorite', 'like', 'love', 'money'], mk_heart),
    ('money-bag-minus', ['moneybag minus', 'remove', 'subtract', 'money bag', 'savings'], mk_minus),
    ('money-bag-pencil', ['money bag', 'edit', 'write', 'money', 'bag'], mk_pencil),
]:
    badge_icon(nm, tags, bag_ln, bag_ar, mk(BB), line=[TIE], detail=small_dollar)

# ---------------------------------------------------------------- money (banknote) variants
m = load('money')
MONEY_SEGS = rect_segs(24, 64, 208, 128, 14)
BM, RCM = (196, 196), 64
mon_ln, mon_ar = cut(MONEY_SEGS, BM, RCM)
for nm, tags, mk in [
    ('money-heart', ['money', 'favorite', 'like', 'love'], mk_heart),
    ('money-minus', ['money minus', 'remove', 'subtract', 'money', 'cash'], mk_minus),
    ('money-pencil', ['money', 'edit', 'write'], mk_pencil),
    ('money-plus', ['money plus', 'add', 'new', 'money', 'cash'], mk_plus),
    ('money-receive', ['receive payment', 'income', 'get paid'], lambda b: mk_diag(b, False)),
    ('money-send', ['send money', 'pay', 'transfer'], lambda b: mk_diag(b, True)),
]:
    icon_dc = m['dotcut'][:1]  # the right-hand dot would crowd the badge
    badge_icon(nm, tags, mon_ln, mon_ar, mk(BM), detail=m['detail'], dotcut=icon_dc)

icon('money-slash', CM, ['no cash', 'money', 'cashless', 'slash', 'no money'],
     line=m['line'] + m['detail'] + [L(48, 48, 208, 208)], dot=m['dotcut'])

# insert / withdraw: portrait note half inside a slot
note = 'M64 56 V186 A14 14 0 0 0 78 200 H178 A14 14 0 0 0 192 186 V56'
SLOT = L(32, 56, 224, 56)
icon('money-insert', CM, ['deposit', 'insert cash', 'atm', 'money'],
     line=[SLOT, P(note)], detail=[L(128, 168, 128, 96), PL([(100, 124), (128, 96), (156, 124)])],
     area=[P(note + ' Z')])
icon('money-withdraw', CM, ['withdraw', 'atm', 'cash out', 'money'],
     line=[SLOT, P(note)], detail=[L(128, 96, 128, 168), PL([(100, 140), (128, 168), (156, 140)])],
     area=[P(note + ' Z')])

# stack: one note on top, edges of two more below
icon('money-stack', CM, ['cash', 'bills', 'stack', 'wealth'],
     line=[R(24, 40, 208, 112, 14), L(40, 184, 216, 184), L(56, 216, 200, 216)],
     detail=[C(128, 96, 28)], area=[R(24, 40, 208, 112, 14)],
     dotcut=[C(64, 96, 16), C(192, 96, 16)])

# transfer: bank whose base is a two-way arrow
roof = PG([(40, 80), (128, 32), (216, 80)])
icon('money-transfer', CM, ['transfer', 'bank', 'send money', 'payment'],
     line=[roof, L(80, 112, 80, 156), L(128, 112, 128, 156), L(176, 112, 176, 156),
           L(32, 196, 224, 196), PL([(52, 176), (32, 196), (52, 216)]), PL([(204, 176), (224, 196), (204, 216)])],
     area=[roof])

# wavy banknote
wave = ('M24 72 C59 48 93 48 128 72 C163 96 197 96 232 72 V184 '
        'C197 208 163 208 128 184 C93 160 59 160 24 184 Z')
icon('money-wavy', CM, ['banknote', 'cash', 'bill'],
     line=[P(wave)], detail=[C(128, 128, 28)], area=[P(wave)], dotcut=[C(68, 120, 16), C(188, 136, 16)])

# ---------------------------------------------------------------- package variants
pk = load('package')
HEX = [(128, 32), (216, 80), (216, 176), (128, 224), (40, 176), (40, 80)]
HEX_SEGS = poly_segs(HEX)
BP, RCP = (184, 196), 64
pk_ln, pk_ar = cut(HEX_SEGS, BP, RCP)
pk_det = [P('M40 80 L128 128 L216 80')] + cut_open(poly_segs([(128, 128), (128, 224)], False), BP, RCP) + [P('M172 56 L84 104 L84 144')]
for nm, tags, mk in [
    ('package-export', ['ship package', 'export', 'outgoing', 'box'], lambda b: mk_arrow(b, 0)),
    ('package-import', ['receive package', 'import', 'incoming', 'box'], lambda b: mk_arrow(b, 180)),
    ('package-heart', ['gift box', 'parcel', 'donation', 'love'], mk_heart),
]:
    badge_icon(nm, tags, pk_ln, pk_ar, mk(BP), detail=pk_det)
BPL = (184, 192)
pkl_ln, pkl_ar = cut(HEX_SEGS, BPL, 66)
pkl_det = [P('M40 80 L128 128 L216 80')] + cut_open(poly_segs([(128, 128), (128, 224)], False), BPL, 66) + [P('M172 56 L84 104 L84 144')]
badge_icon('package-lock', ['secure package', 'locked box', 'protected delivery'], pkl_ln, pkl_ar, mk_lock(BPL), detail=pkl_det)
icon('package-slash', CM, ['package', 'disabled', 'off', 'commerce'],
     line=pk['line'] + pk['detail'] + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- paper bag
teeth = [(56 + 18 * i, 40 if i % 2 == 0 else 52) for i in range(9)]
pb = P(poly(teeth) + ' V214 A10 10 0 0 1 190 224 H66 A10 10 0 0 1 56 214 Z')
icon('paper-bag', CM, ['paper bag', 'grocery', 'takeaway', 'shopping'],
     line=[pb], detail=[L(56, 92, 200, 92), P('M108 92 A20 20 0 0 0 148 92')], area=[pb])
icon('paper-bag-slash', CM, ['paper bag', 'off', 'disabled', 'hidden', 'paper'],
     line=[pb, L(56, 92, 200, 92), P('M108 92 A20 20 0 0 0 148 92'), L(48, 48, 208, 208)])

# ---------------------------------------------------------------- paywall: page behind a dollar coin
COIN = (128, 160)
page_l = P('M40 168 V48 A16 16 0 0 1 56 32 H200 A16 16 0 0 1 216 48 V168')
page_segs = poly_segs([(216, 168), (40, 168)], False)
xa = math.sqrt(88 ** 2 - 8 ** 2)
page_area = P(f'M40 168 V48 A16 16 0 0 1 56 32 H200 A16 16 0 0 1 216 48 V168 H{f(128 + xa)} A88 88 0 0 0 {f(128 - xa)} 168 Z')
icon('paywall', CM, ['paywall', 'subscription', 'locked content', 'premium'],
     line=[page_l, C(*COIN, 64)], detail=[L(80, 68, 176, 68)] + mk_dollar(COIN)['line'],
     area=[page_area, C(*COIN, 64)])

# ---------------------------------------------------------------- receipt variants
rc_ = load('receipt')
RECEIPT = [(56, 32), (200, 32), (200, 224), (176, 208), (152, 224), (128, 208), (104, 224), (80, 208), (56, 224)]
REC_SEGS = poly_segs(RECEIPT)
REC_C = (128, 120)


def receipt_badge(name, tags, B, rc, mark, lines):
    ln, ar = cut(REC_SEGS, B, rc, centroid=REC_C)
    badge_icon(name, tags, ln, ar, mark, detail=lines)


tall_lines = [L(88, 80, 168, 80), L(88, 120, 148, 120)]
receipt_badge('receipt-bitcoin', ['receipt', 'bitcoin', 'crypto'], (190, 176), 68, mk_bitcoin((190, 176)), tall_lines)
receipt_badge('receipt-currency-dollar', ['receipt', 'dollar', 'price', 'money'], (188, 176), 68, mk_dollar((188, 176)), tall_lines)
receipt_badge('receipt-currency-euro', ['receipt', 'euro', 'price', 'money'], (186, 180), 66, mk_euro((186, 180)), tall_lines)
short_lines = [L(88, 80, 168, 80), L(88, 120, 136, 120)]
receipt_badge('receipt-refund', ['refund', 'return', 'receipt', 'money back'], (188, 184), 64, mk_refund((188, 184)), short_lines)
receipt_badge('receipt-x', ['void receipt', 'refund', 'cancelled order'], (188, 188), 60, mk_x((188, 188)), short_lines)
icon('receipt-slash', CM, ['receipt', 'off', 'disabled', 'hidden'], line=rc_['line'] + rc_['detail'] + [L(48, 48, 208, 208)])
icon('receipt-tax', CM, ['tax receipt', 'invoice', 'percent', 'bill'],
     line=rc_['line'], detail=[L(168, 88, 88, 168)], area=rc_['area'],
     dotcut=[C(96, 96, 16), C(160, 160, 16)])

# ---------------------------------------------------------------- red envelope
env = R(56, 32, 144, 192, 14)
icon('red-envelope', CM, ['hongbao', 'red packet', 'gift money', 'lucky money'],
     line=[env], detail=[P('M56 76 C88 112 168 112 200 76'), C(128, 116, 22)], area=[env])

# ---------------------------------------------------------------- refund: coin-dollar inside a returning arrow
RFC, RFR = (128, 128), 88
s0, s1 = polar(RFC, RFR, 60), polar(RFC, RFR, 150)
tang = (math.sin(math.radians(150)), -math.cos(math.radians(150)))
def wing(deg):
    v = rot([tang], deg, (0, 0))[0]
    return (s1[0] - 34 * v[0], s1[1] - 34 * v[1])
icon('refund', CM, ['refund', 'money back', 'return', 'payment'],
     line=[P(f'M{pt(s0)} A{RFR} {RFR} 0 1 0 {pt(s1)}'), PL([wing(45), s1, wing(-45)])] + mk_dollar(RFC)['line'])

# ---------------------------------------------------------------- shopping bag variants
sb = load('shopping-bag')
BAG = [(48, 80), (208, 80), (200, 216), (56, 216)]
BAG_SEGS = poly_segs(BAG)
HANDLE = sb['line'][1]
BS, RCS = (192, 192), 62
sb_ln, sb_ar = cut(BAG_SEGS, BS, RCS)
for nm, tags, mk in [
    ('shopping-bag-arrow-down', ['add to bag', 'buy', 'purchase'], lambda b: mk_arrow(b, 90)),
    ('shopping-bag-arrow-up', ['remove from bag', 'return', 'refund'], lambda b: mk_arrow(b, -90)),
    ('shopping-bag-check', ['bag', 'purchase', 'done', 'check', 'order complete'], mk_check),
    ('shopping-bag-discount', ['shopping bag', 'discount', 'sale', 'percent', 'shopping'], mk_percent),
    ('shopping-bag-heart', ['bag', 'wishlist', 'favorite', 'heart'], mk_heart),
    ('shopping-bag-magnifying-glass', ['shopping bag', 'search', 'find', 'shopping', 'bag'], mk_search),
]:
    badge_icon(nm, tags, sb_ln, sb_ar, mk(BS), line=[HANDLE])

print(save(overwrite=True))
