import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

UI = 'Interface'
LN = 'Letters & Numbers'
SLASH = L(48, 48, 208, 208)


def arc(c, r, a1, a2):
    """Arc path from angle a1 to a2 (degrees); a2 > a1 runs clockwise on screen."""
    p, q = polar(c, r, a1), polar(c, r, a2)
    span = abs(a2 - a1)
    return f'M{pt(p)} A{f(r)} {f(r)} 0 {1 if span > 180 else 0} {1 if a2 > a1 else 0} {pt(q)}'


def arc_head(c, r, a1, a2, k=24):
    """Chevron arrowhead at the end (a2) of an arc, pointing along the direction of travel."""
    e = polar(c, r, a2)
    s = 1 if a2 > a1 else -1
    th = math.radians(a2)
    t = (-math.sin(th) * s, math.cos(th) * s)
    n = (-t[1], t[0])
    b = (e[0] - t[0] * k, e[1] - t[1] * k)
    return PL([(b[0] + n[0] * k, b[1] + n[1] * k), e, (b[0] - n[0] * k, b[1] - n[1] * k)])


def seg_circle(p, q, c, r):
    """First point along p->q at distance r from c."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        x = (p[0] + (q[0] - p[0]) * m, p[1] + (q[1] - p[1]) * m)
        if dist(x, c) > r:
            lo = m
        else:
            hi = m
    return (p[0] + (q[0] - p[0]) * lo, p[1] + (q[1] - p[1]) * lo)


# ======================================================================= trash
TR = load('trash')
LID, HANDLE, BODY = TR['line']
TAREA = TR['area']

# trash-arrow-up: restore arrow in place of the slats
icon('trash-arrow-up', UI, ['restore', 'undelete', 'recover', 'trash'],
     line=[LID, HANDLE, BODY],
     detail=[L(128, 188, 128, 108), PL([(100, 136), (128, 108), (156, 136)])], area=TAREA)

# trash-arrows: two chasing arc arrows inside the can
ca, ra = (128, 146), 36
icon('trash-arrows', UI, ['restore', 'recycle bin', 'undelete', 'trash'],
     line=[LID, HANDLE, BODY],
     detail=[P(arc(ca, ra, 196, 316)), arc_head(ca, ra, 196, 316, 18),
             P(arc(ca, ra, 16, 136)), arc_head(ca, ra, 16, 136, 18)],
     area=TAREA)

# trash-clock: body cut around a clock badge
bc, br = (184, 184), 40
cut = br + 36
p_side = seg_circle((192, 64), (184, 208), bc, cut)
p_bot = seg_circle((88, 224), (168, 224), bc, cut)
cut_arc = arc_to(bc, cut, p_bot, p_side, lambda m: -dist(m, (128, 128)))
body_cut = f'M64 64 L72 208 A16 16 0 0 0 88 224 H{f(p_bot[0])} '
icon('trash-clock', UI, ['auto delete', 'scheduled delete', 'trash', 'timer'],
     line=[LID, HANDLE, P(body_cut + f'M{pt(p_side)} L192 64'), C(*bc, br)],
     detail=[L(108, 104, 108, 160), PL([(184, 162), (184, 184), (200, 194)])],
     area=[P(body_cut + cut_arc + ' L192 64 Z'), C(*bc, br)])

icon('trash-slash', UI, ['trash', 'off', 'disabled', 'hidden'], line=[LID, HANDLE, BODY, SLASH])

icon('trash-x', UI, ['delete permanently', 'trash', 'remove', 'bin'],
     line=[LID, HANDLE, BODY],
     detail=[L(104, 116, 152, 164), L(152, 116, 104, 164)], area=TAREA)

# ======================================================================= trays
TRAY = load('tray')
OPEN_SIDES = P('M32 120 V194 A14 14 0 0 0 46 208 H210 A14 14 0 0 0 224 194 V120')
OPEN_RIM = P('M32 152 H84 L100 176 H156 L172 152 H224')
OPEN_AREA = P('M32 152 H84 L100 176 H156 L172 152 H224 V194 A14 14 0 0 1 210 208 H46 A14 14 0 0 1 32 194 Z')

icon('tray-arrow-down', UI, ['download', 'inbox', 'receive', 'import', 'archive'],
     line=[OPEN_SIDES, OPEN_RIM, L(128, 32, 128, 124), PL([(92, 88), (128, 124), (164, 88)])],
     area=[OPEN_AREA])
icon('tray-arrow-up', UI, ['upload', 'outbox', 'send', 'export', 'unarchive'],
     line=[OPEN_SIDES, OPEN_RIM, L(128, 124, 128, 32), PL([(92, 68), (128, 32), (164, 68)])],
     area=[OPEN_AREA])
icon('tray-check', UI, ['inbox zero', 'done', 'processed', 'tray'],
     line=[OPEN_SIDES, OPEN_RIM, PL([(84, 76), (112, 104), (172, 44)])],
     area=[OPEN_AREA])
icon('tray-slash', UI, ['tray', 'off', 'disabled', 'hidden'], line=TRAY['line'] + TRAY['detail'] + [SLASH])

front = R(32, 88, 192, 128, 14)
icon('trays', UI, ['inboxes', 'trays', 'stack', 'mail'],
     line=[front, P('M56 88 V62 A14 14 0 0 1 70 48 H186 A14 14 0 0 1 200 62 V88')],
     detail=[P('M52 148 H84 L100 172 H156 L172 148 H204')], area=[front])

# ======================================================================= tree view
icon('tree-view', UI, ['hierarchy', 'outline', 'nested list'],
     line=[L(40, 56, 152, 56), P('M72 56 V200 H112'), L(72, 128, 112, 128),
           L(148, 128, 216, 128), L(148, 200, 216, 200)])

# ======================================================================= upload slash (mirrors download-slash)
icon('upload-slash', UI, ['upload off', 'no upload', 'blocked', 'offline'],
     line=[L(128, 176, 128, 72), PL([(88, 112), (128, 72), (168, 112)]),
           P('M40 168 V200 A16 16 0 0 0 56 216 H200 A16 16 0 0 0 216 200 V168'), L(44, 44, 184, 184)])

# ======================================================================= viewports
VP = R(32, 32, 192, 192, 16)
narrow = [L(64, 128, 108, 128), PL([(84, 104), (108, 128), (84, 152)]),
          L(192, 128, 148, 128), PL([(172, 104), (148, 128), (172, 152)])]
wide = [L(68, 128, 188, 128), PL([(92, 104), (68, 128), (92, 152)]), PL([(164, 104), (188, 128), (164, 152)])]
for nm, tags, det in [
    ('viewport-narrow', ['narrow', 'viewport', 'compress width', 'responsive'], narrow),
    ('viewport-wide', ['wide', 'viewport', 'expand width', 'responsive'], wide),
]:
    icon(nm, UI, tags, line=[VP], detail=det, area=[VP])
    vert = nm.replace('narrow', 'short').replace('wide', 'tall')
    vtags = [t.replace('narrow', 'short').replace('wide', 'tall').replace('width', 'height') for t in tags]
    rd = []
    for d in det:
        import re
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
        pts = rot(list(zip(nums[0::2], nums[1::2])), 90)
        rd.append(PL(pts))
    icon(vert, UI, vtags, line=[VP], detail=rd, area=[VP])

# ======================================================================= warnings / x shapes
OCT = load('warning-octagon')['line'][0]
RHOMB = load('rhombus')['line'][0]
CIRC = C(128, 128, 96)
SQ = R(32, 32, 192, 192, 16)
BANG_SHORT = L(128, 64, 128, 90)

for nm, shape in [('warning-circle-slash', CIRC), ('warning-octagon-slash', OCT), ('warning-square-slash', SQ)]:
    base = nm.replace('-slash', '')
    icon(nm, UI, [base.replace('-', ' '), 'off', 'disabled', 'hidden', 'warning'],
         line=[shape, BANG_SHORT, SLASH], dot=[C(128, 176, 16)])

icon('warning-slash', UI, ['warning', 'off', 'disabled', 'hidden'],
     line=[PG([(128, 40), (224, 208), (32, 208)]), L(128, 104, 128, 144), L(48, 48, 100, 100), L(156, 156, 208, 208)],
     dot=[C(128, 176, 16)])

icon('warning-diamond', UI, ['alert', 'exclamation', 'error', 'diamond', 'caution'],
     line=[RHOMB], detail=[L(128, 80, 128, 136)], area=[RHOMB], dotcut=[C(128, 176, 16)])
icon('warning-square', UI, ['alert', 'exclamation', 'error', 'square', 'warning'],
     line=[SQ], detail=[L(128, 76, 128, 136)], area=[SQ], dotcut=[C(128, 176, 16)])

XD = [L(100, 100, 156, 156), L(156, 100, 100, 156)]
icon('x-circle-dashed', UI, ['x circle dashed', 'circle', 'dashed', 'interface'],
     line=load('circle-dashed')['line'] + [L(96, 96, 160, 160), L(160, 96, 96, 160)])
icon('x-diamond', UI, ['error', 'close', 'diamond', 'cancel'], line=[RHOMB], detail=XD, area=[RHOMB])
icon('x-octagon', UI, ['stop', 'error', 'octagon', 'close'],
     line=[OCT], detail=[L(96, 96, 160, 160), L(160, 96, 96, 160)], area=[OCT])

# ======================================================================= zoom
lc, lr = (148, 148), 52
hs = polar(lc, lr, 45)
SEL = [PL([(40, 64), (40, 40), (64, 40)]), L(96, 40, 120, 40), PL([(152, 40), (176, 40), (176, 64)]),
       L(40, 96, 40, 120), PL([(40, 152), (40, 176), (64, 176)])]
LENS = [C(*lc, lr), L(hs[0], hs[1], 216, 216)]
icon('zoom-area-in', UI, ['zoom to area', 'zoom in', 'selection', 'magnify'],
     line=SEL + LENS, detail=[L(148, 124, 148, 172), L(124, 148, 172, 148)], area=[C(*lc, lr)])
icon('zoom-area-out', UI, ['zoom out area', 'zoom out', 'selection', 'magnify'],
     line=SEL + LENS, detail=[L(124, 148, 172, 148)], area=[C(*lc, lr)])

pc, pr = (120, 120), 36
ph = polar(pc, pr, 45)
icon('zoom-pan', UI, ['pan', 'move view', 'navigate', 'zoom'],
     line=[C(*pc, pr), L(ph[0], ph[1], 168, 168),
           PL([(104, 56), (128, 32), (152, 56)]), PL([(104, 200), (128, 224), (152, 200)]),
           PL([(56, 104), (32, 128), (56, 152)]), PL([(200, 104), (224, 128), (200, 152)])],
     area=[C(*pc, pr)])

mc, mr = (112, 112), 72
icon('zoom-reset', UI, ['reset zoom', 'fit', 'actual size', 'magnify'],
     line=[P(arc(mc, mr, 180, -135)), arc_head(mc, mr, 180, -135, 20), L(163, 163, 216, 216)],
     area=[C(*mc, mr)])

# ======================================================================= greek & symbols
icon('alpha', LN, ['alpha', 'greek', 'letter', 'math'],
     line=[P('M192 64 C178 150 156 192 108 192 C76 192 52 166 52 128 C52 90 76 64 108 64 '
             'C156 64 178 106 204 192')])
icon('beta', LN, ['beta', 'greek', 'letter', 'preview'],
     line=[P('M84 224 V84 A44 44 0 0 1 172 84 C172 110 152 124 124 124 C172 124 196 144 196 172 '
             'C196 200 172 216 140 216 C116 216 96 208 84 196')])
icon('delta', LN, ['delta', 'greek', 'change', 'difference'], line=[PG([(128, 44), (212, 208), (44, 208)])])
icon('backslash', LN, ['backslash', 'slash', 'character'], line=[L(80, 40, 176, 216)])
icon('ampersand', LN, ['and', 'ampersand', 'symbol'],
     line=[P('M208 216 L96 104 C76 84 76 48 108 44 C136 40 152 64 140 84 C130 100 104 112 84 126 '
             'C56 146 52 186 84 206 C120 226 164 200 192 140')])

# ======================================================================= alphabets
A = 'alphabet'
def alpha_tags(n):
    return [f'alphabet {n}', 'alphabet', 'script', 'language', n]

# Arabic: beh (ب)
icon('alphabet-arabic', LN, alpha_tags('arabic'),
     line=[P('M208 72 V112 C208 160 180 176 128 176 C76 176 48 160 48 120 V104')], dot=[C(128, 212, 16)])
# Bangla: অ  (headline, stem, 3-like body and connector)
icon('alphabet-bangla', LN, alpha_tags('bangla'),
     line=[L(32, 52, 224, 52), L(184, 52, 184, 216),
           P('M60 88 C76 76 112 76 116 104 C118 124 100 132 84 132 C112 132 136 148 132 176 '
             'C128 204 92 212 60 196'), L(130, 148, 184, 148)])
# Chinese: 文
icon('alphabet-chinese', LN, alpha_tags('chinese'),
     line=[L(124, 32, 132, 56), L(40, 84, 216, 84), P('M176 84 C160 160 120 200 44 216'),
           P('M80 84 C96 160 136 200 212 216')])
# Cyrillic: Ж
icon('alphabet-cyrillic', LN, alpha_tags('cyrillic'),
     line=[L(128, 40, 128, 216), PL([(40, 40), (88, 128), (40, 216)]), PL([(216, 40), (168, 128), (216, 216)]),
           L(88, 128, 168, 128)])
# Devanagari: क
icon('alphabet-devanagari', LN, alpha_tags('devanagari'),
     line=[L(32, 52, 224, 52), L(128, 52, 216 - 88, 216),
           P('M128 136 C104 100 44 100 44 144 C44 184 100 184 128 136'),
           P('M128 136 C156 104 208 108 208 148 C208 176 188 192 168 196')])
# Ethiopic: ሀ
icon('alphabet-ethiopic', LN, alpha_tags('ethiopic'),
     line=[P('M76 208 V104 A52 52 0 0 1 180 104 V208'), L(52, 208, 76, 208), L(180, 208, 204, 208)])
# Georgian: ა
icon('alphabet-georgian', LN, alpha_tags('georgian'),
     line=[P('M200 104 V136 A64 64 0 0 1 72 136 V112 C72 76 116 68 124 96 C130 116 112 132 92 128')])
# Greek: Ω
icon('alphabet-greek', LN, alpha_tags('greek'),
     line=[P('M44 208 H92 V190 C62 174 44 148 44 118 A84 84 0 0 1 212 118 C212 148 194 174 164 190 V208 H212')])
# Hebrew: א
icon('alphabet-hebrew', LN, alpha_tags('hebrew'),
     line=[L(64, 48, 192, 208), P('M184 48 V92 C184 112 172 124 152 126'),
           P('M64 208 V164 C64 144 76 132 100 130')])
# Japanese: あ
icon('alphabet-japanese', LN, alpha_tags('japanese'),
     line=[L(60, 72, 180, 64), P('M112 36 C108 96 116 156 140 204'),
           P('M160 100 C136 164 100 196 72 188 C48 180 48 148 72 128 C104 102 168 102 192 132 '
             'C212 160 196 200 152 208')])
# Korean: 한
icon('alphabet-korean', LN, alpha_tags('korean'),
     line=[L(64, 36, 100, 36), L(40, 64, 124, 64), C(82, 108, 24), L(164, 32, 164, 144), L(164, 88, 200, 88),
           PL([(72, 164), (72, 216), (208, 216)])])
# Latin: Az
icon('alphabet-latin', LN, alpha_tags('latin'),
     line=[PL([(32, 208), (80, 48), (128, 208)]), L(46.4, 160, 113.6, 160),
           PL([(156, 112), (220, 112), (156, 208), (220, 208)])])
# Polish: Ł
icon('alphabet-polish', LN, alpha_tags('polish'),
     line=[PL([(96, 40), (96, 216), (192, 216)]), L(56, 152, 136, 104)])
# Runes: fehu ᚠ
icon('alphabet-runes', LN, alpha_tags('runes'),
     line=[L(96, 32, 96, 224), L(96, 96, 176, 40), L(96, 156, 184, 100)])
# Thai: ก
icon('alphabet-thai', LN, alpha_tags('thai'),
     line=[P('M76 208 V116 C76 72 104 48 140 48 C176 48 196 76 196 112 V208'),
           P('M76 136 C76 112 100 104 112 120')])

# ======================================================================= letter A (matches batch 155 letter set)
def g_A(x, t, w, h):
    b = t + h
    k = 0.66
    yb = t + h * k
    xl = x + w / 2 - (w / 2) * k
    xr = x + w / 2 + (w / 2) * k
    return [PL([(x, b), (x + w / 2, t), (x + w, b)]), L(xl, yb, xr, yb)]


def gA(h, cy=128):
    w = h * 0.84
    return g_A(128 - w / 2, cy - h / 2, w, h)


icon('letter-a', LN, ['letter a', 'a', 'alphabet', 'english', 'character'], line=gA(176))
icon('letter-a-circle', LN, ['letter a', 'a', 'circle', 'alphabet', 'initial'],
     line=[CIRC], area=[CIRC], detail=gA(92))
icon('letter-a-square', LN, ['letter a', 'a', 'square', 'alphabet'], line=[SQ], area=[SQ], detail=gA(104))

print(save(overwrite=True))
