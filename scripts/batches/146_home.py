import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

HM = 'Home'


def slashed(roles):
    """Slash variant: everything becomes line (no area/holes), plus the standard slash."""
    out = dict(line=list(roles.get('line', [])) + list(roles.get('detail', [])) + [L(48, 48, 208, 208)],
               dot=list(roles.get('dot', [])) + list(roles.get('dotcut', [])))
    return out


def crossed(roles, a=(48, 48), b=(208, 208)):
    """Care-label cross (X) over a symbol."""
    out = dict(line=list(roles.get('line', [])) + list(roles.get('detail', [])) +
               [L(a[0], a[1], b[0], b[1]), L(b[0], a[1], a[0], b[1])],
               dot=list(roles.get('dot', [])) + list(roles.get('dotcut', [])))
    return out


# ================================================================ House family (matches house + other house-* badges)
ROOF = P('M32 124 L128 40 L224 124')
HOUSE_AREA = 'M48 112 L128 44 L208 112 V208 H48 Z'
HOUSE_WALLS = P('M48 112 V208 H208 V112')
B = (184, 184)
BX, BY = B


def house_badge(name, tags, mark, cr=56):
    k = math.sqrt(cr * cr - 24 * 24)
    e = BY - k  # wall end y / floor end x (symmetric)
    ln = [P(f'M48 112 L48 208 L{f(e)} 208'), P(f'M208 {f(e)} L208 112'), ROOF]
    ar = [P(f'M{f(e)} 208 L48 208 L48 112 L128 44 L208 112 L208 {f(e)} A{cr} {cr} 0 0 0 {f(e)} 208 Z')]
    roles = dict(line=ln + mark.get('line', []), area=ar + mark.get('area', []),
                 dot=mark.get('dot', []), detail=mark.get('detail', []))
    icon(name, HM, tags, **roles)


star = [polar((BX, BY + 3), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)]
house_badge('house-star', ['house', 'favorite', 'starred', 'featured'], dict(line=[PG(star)], area=[PG(star)]), cr=60)
house_badge('house-stats', ['house', 'stats', 'analytics'],
            dict(line=[L(154, 196, 154, 214), L(184, 176, 184, 214), L(214, 156, 214, 214)]), cr=64)
house_badge('house-warning', ['home alert', 'house', 'warning', 'danger'],
            dict(line=[L(BX, BY - 32, BX, BY)], dot=[C(BX, BY + 32, 16)]), cr=58)
house_badge('house-x', ['remove home', 'house', 'x', 'delete'],
            dict(line=[L(BX - 20, BY - 20, BX + 20, BY + 20), L(BX + 20, BY - 20, BX - 20, BY + 20)]), cr=54)

# inside-the-house variants (like house-leaf): door dropped, symbol cut into the body
icon('house-thermometer', HM, ['indoor temperature', 'heating', 'climate'],
     line=[HOUSE_WALLS, ROOF], area=[P(HOUSE_AREA)],
     detail=[L(128, 100, 128, 148)], dotcut=[C(128, 160, 22)])

icon('house-user', HM, ['homeowner', 'resident', 'house', 'person'],
     line=[HOUSE_WALLS, ROOF, P('M92 208 A36 36 0 0 1 164 208')], area=[P(HOUSE_AREA)],
     hole=[P('M100 200 A28 28 0 0 1 156 200 Z')], dotcut=[C(128, 132, 18)])

wc = (128, 180)
def warc(r, span=40):
    a, b = polar(wc, r, -90 - span), polar(wc, r, -90 + span)
    return P(f'M{pt(a)} A{r} {r} 0 0 1 {pt(b)}')
icon('house-wifi', HM, ['smart home', 'connected home', 'house', 'wifi', 'connected house'],
     line=[HOUSE_WALLS, ROOF], area=[P(HOUSE_AREA)],
     detail=[warc(40, 42), warc(76, 40)], dotcut=[C(128, 180, 16)])


# houses: front house (right) overlapping a back house (left)
S = 84 / 96  # roof slope of the house icon
def roof_y(apex, x):
    return apex[1] + abs(x - apex[0]) * S
FA = (160, 76)      # front apex
FW = (104, 216)     # front walls x
FE = 16             # eave overhang
FY = 208
BA = (84, 60)       # back apex
BWL = 40            # back left wall
# back roof right side meets the front roof left side
# back right: y = BA.y + (x-BA.x)*S ; front left: y = FA.y + (FA.x-x)*S
xi = (FA[1] - BA[1] + (FA[0] + BA[0]) * S) / (2 * S)
yi = roof_y(BA, xi)
f_eave_l = (FW[0] - FE, roof_y(FA, FW[0] - FE))
f_eave_r = (FW[1] + FE, roof_y(FA, FW[1] + FE))
f_wall_top = roof_y(FA, FW[0])
b_eave = (BWL - FE + 8, roof_y(BA, BWL - FE + 8))
b_wall_top = roof_y(BA, BWL)
front_area = PG([(FW[0], f_wall_top), FA, (FW[1], f_wall_top), (FW[1], FY), (FW[0], FY)])
back_area = PG([(BWL, b_wall_top), BA, (xi, yi), (FW[0], f_wall_top), (FW[0], FY), (BWL, FY)])
icon('houses', HM, ['houses', 'neighborhood', 'real estate', 'homes', 'community'],
     line=[PL([b_eave, BA, (xi, yi)]), PL([f_eave_l, FA, f_eave_r]),
           P(f'M{f(BWL)} {f(b_wall_top)} V{FY} H{FW[1]} V{f(f_wall_top)}'),
           L(FW[0], f_wall_top, FW[0], FY),
           P('M144 208 V180 A16 16 0 0 1 176 180 V208')],
     area=[front_area, back_area], hole=[P('M152 208 V180 A8 8 0 0 1 168 180 V208 Z')],
     detail=[PL([(xi - 14 * math.cos(math.atan(S)), yi + 14 * math.sin(math.atan(S))), f_eave_l]),
             L(FW[0], f_wall_top, FW[0], 184)])


# ================================================================ Irons
def iron(dy=0):
    body = (f'M32 {192 + dy} L216 {192 + dy} V{136 + dy} A24 24 0 0 0 192 {112 + dy} H120 '
            f'C76 {112 + dy} 44 {140 + dy} 32 {192 + dy} Z')
    handle = f'M112 {112 + dy} L124 {72 + dy} H184 A16 16 0 0 1 200 {88 + dy} V{112 + dy}'
    return dict(line=[P(body), P(handle)], area=[P(body)], detail=[L(92, 156 + dy, 180, 156 + dy)])


I0 = iron(0)
icon('iron', HM, ['iron', 'clothes', 'laundry', 'press', 'ironing'], **I0)
icon('iron-slash', HM, ['do not iron', 'laundry', 'care label', 'iron', 'care symbol'], **slashed(I0))

I1 = iron(-40)
steam = []
for x in (84, 128, 172):
    steam.append(P(f'M{x} 180 C{x - 16} 196 {x + 16} 208 {x} 224'))
IS = dict(line=I1['line'] + steam, area=I1['area'], detail=I1['detail'])
icon('iron-steam', HM, ['steam iron', 'laundry', 'care symbol', 'clothes'], **IS)
icon('iron-steam-slash', HM, ['no steam', 'laundry', 'care symbol', 'iron'], **slashed(IS))

# ================================================================ Kettle
kb = [(84, 72), (164, 72), (184, 208), (64, 208)]
icon('kettle', HM, ['kettle', 'tea', 'boil', 'kitchen'],
     line=[PG(kb), P('M108 72 V60 A8 8 0 0 1 116 52 H132 A8 8 0 0 1 140 60 V72'),
           P('M170 100 H196 A20 20 0 0 1 216 120 V156 A20 20 0 0 1 196 176 H180'),
           PL([(80, 100), (40, 84), (75, 136)])],
     area=[PG(kb), PG([(80, 100), (40, 84), (75, 136)])],
     detail=[L(100, 172, 148, 172)])

# ================================================================ Lamps
icon('lamp-pendant', HM, ['ceiling lamp', 'pendant light', 'lighting'],
     line=[L(128, 32, 128, 96), P('M48 176 A80 80 0 0 1 208 176 Z'), P('M104 176 A24 24 0 0 0 152 176')],
     area=[P('M48 176 A80 80 0 0 1 208 176 Z')])
icon('lamp-slash', HM, ['light off', 'lamp', 'dark', 'disabled'], **slashed(load('lamp')))

# ================================================================ Laundry care symbols
def wave(x0, x1, y, n, a):
    w = (x1 - x0) / n
    d = ''
    for i in range(n):
        s = -1 if i % 2 == 0 else 1
        xa = x0 + i * w
        d += f' C{f(xa + w / 3)} {f(y + s * a * 4 / 3)} {f(xa + 2 * w / 3)} {f(y + s * a * 4 / 3)} {f(xa + w)} {f(y)}'
    return d


def tub(top, bottom, xl=32, xr=224, inset=24, n=4, a=12):
    sides = P(f'M{xl} {top} L{xl + inset} {bottom} H{xr - inset} L{xr} {top}')
    wv = P(f'M{xl} {top}' + wave(xl, xr, top, n, a))
    ar = P(f'M{xl} {top}' + wave(xl, xr, top, n, a) + f' L{xr - inset} {bottom} H{xl + inset} Z')
    return dict(line=[sides, wv], area=[ar])


T0 = tub(84, 196)
icon('laundry-temperature', HM, ['wash temperature', 'laundry', 'care symbol', 'degrees'],
     line=T0['line'], area=T0['area'], dotcut=[C(104, 148, 16), C(152, 148, 16)])
icon('laundry-do-not-wash', HM, ['do not wash', 'laundry', 'care symbol', 'hand wash'],
     **crossed(T0, (48, 56), (208, 216)))
leaf = 'M100 176 C98 146 116 128 156 124 C158 160 136 178 100 176 Z'
icon('laundry-eco', HM, ['eco wash', 'laundry', 'low energy', 'green'],
     line=T0['line'], area=T0['area'], detail=[P(leaf)], hole=[P(leaf)])
T1 = tub(60, 164)
icon('laundry-permanent-press', HM, ['permanent press', 'laundry', 'care symbol', 'wash'],
     line=T1['line'] + [L(56, 204, 200, 204)], area=T1['area'])
T2 = tub(40, 140)
icon('laundry-gentle', HM, ['gentle wash', 'delicate', 'laundry', 'care symbol'],
     line=T2['line'] + [L(56, 176, 200, 176), L(56, 212, 200, 212)], area=T2['area'])

# hand wash: hand dipped into the tub
HT, HB = 120, 208
hx0, hx1 = 112, 160
th = tub(HT, HB)
wv_full = 'M32 120' + wave(32, 224, HT, 4, 12)
icon('laundry-hand-wash', HM, ['hand wash', 'laundry', 'care symbol', 'delicate'],
     line=[P(f'M32 {HT} L56 {HB} H200 L224 {HT}'), P(wv_full),
           P(f'M{hx0} {HT} V64 A24 24 0 0 1 {hx1} 64 V{HT}'), L(hx0, 104, 84, 76)],
     area=th['area'] + [P(f'M{hx0} {HT} V64 A24 24 0 0 1 {hx1} 64 V{HT} Z')])

SQ = R(32, 32, 192, 192, 16)
icon('laundry-dry', HM, ['tumble dry', 'laundry', 'care symbol', 'dry'],
     line=[SQ], area=[SQ], detail=[C(128, 128, 60)])
icon('laundry-tumble-dry', HM, ['tumble dry', 'dryer', 'laundry', 'care symbol'],
     line=[SQ], area=[SQ], detail=[C(128, 128, 60)], dotcut=[C(128, 128, 16)])
icon('laundry-do-not-dry', HM, ['do not tumble dry', 'laundry', 'care symbol', 'dryer'],
     **crossed(dict(line=[SQ], detail=[C(128, 128, 60)]), (32, 32), (224, 224)))
icon('laundry-dry-flat', HM, ['dry flat', 'laundry', 'care symbol', 'lay flat'],
     line=[SQ], area=[SQ], detail=[L(72, 128, 184, 128)])
icon('laundry-dry-shade', HM, ['dry in shade', 'laundry', 'care symbol', 'shade'],
     line=[SQ], area=[SQ], detail=[L(64, 120, 120, 64), L(64, 168, 168, 64)])
icon('laundry-line-dry', HM, ['line dry', 'hang dry', 'laundry', 'care symbol'],
     line=[SQ], area=[SQ], detail=[P('M64 76 C96 120 160 120 192 76')])
icon('laundry-dry-clean', HM, ['dry clean', 'laundry', 'care symbol', 'cleaner'],
     line=[C(128, 128, 88)], area=[C(128, 128, 88)])
icon('laundry-do-not-dry-clean', HM, ['do not dry clean', 'laundry', 'care symbol'],
     **crossed(dict(line=[C(128, 128, 88)]), (48, 48), (208, 208)))

# ================================================================ Lawn mower
deck = 'M48 160 V136 A24 24 0 0 1 72 112 H168 A48 48 0 0 1 216 160 Z'
icon('lawn-mower', HM, ['lawn mower', 'garden', 'grass', 'yard'],
     line=[P(deck), C(80, 184, 24), C(184, 184, 24), L(80, 112, 52, 48), L(32, 48, 68, 48)],
     area=[P(deck), C(80, 184, 24), C(184, 184, 24)], hole=[C(80, 184, 8), C(184, 184, 8)])

# ================================================================ Microwave
MW = R(32, 56, 192, 144, 14)
MWD = dict(line=[MW], area=[MW], detail=[R(60, 84, 100, 88, 8), L(192, 156, 192, 172)],
           dotcut=[C(192, 100, 14)])
icon('microwave', HM, ['microwave oven', 'kitchen', 'heat', 'appliance', 'microwave'], **MWD)
icon('microwave-slash', HM, ['microwave', 'off', 'disabled', 'hidden'], **slashed(MWD))

# ================================================================ Mirror
mc = (128, 100)
sh_a, sh_b = (mc[0] + 36 * math.cos(math.radians(190)), mc[1] + 48 * math.sin(math.radians(190))), \
             (mc[0] + 36 * math.cos(math.radians(245)), mc[1] + 48 * math.sin(math.radians(245)))
icon('mirror', HM, ['vanity mirror', 'reflection', 'bathroom', 'mirror', 'vanity'],
     line=[E(128, 100, 60, 72), P('M112 170 V208 A16 16 0 0 0 144 208 V170')],
     area=[E(128, 100, 60, 72), P('M112 170 V208 A16 16 0 0 0 144 208 V170 Z')],
     detail=[P(f'M{pt(sh_a)} A36 48 0 0 1 {pt(sh_b)}')])

# ================================================================ Mop
strands = [P('M96 136 Q72 168 60 208'), P('M117 136 Q104 176 106 216'),
           P('M139 136 Q152 176 150 216'), P('M160 136 Q184 168 196 208')]
icon('mop', HM, ['mop', 'cleaning', 'floor', 'housework'],
     line=[L(128, 32, 128, 120), R(88, 120, 80, 16, 8)] + strands)

# ================================================================ Motion sensor
mc2 = (128, 196)
def sarc(r, span):
    a, b = polar(mc2, r, -90 - span), polar(mc2, r, -90 + span)
    return P(f'M{pt(a)} A{r} {r} 0 0 1 {pt(b)}')
icon('motion-sensor', HM, ['motion sensor', 'presence', 'detector', 'security'],
     line=[P('M68 196 A60 60 0 0 1 188 196 Z'), sarc(96, 42), sarc(132, 40)],
     area=[P('M68 196 A60 60 0 0 1 188 196 Z')])

# ================================================================ Furniture
NS = R(40, 48, 176, 144, 14)
icon('nightstand', HM, ['bedside table', 'nightstand', 'furniture', 'bedroom'],
     line=[NS, L(40, 120, 216, 120), L(68, 192, 68, 216), L(188, 192, 188, 216)], area=[NS],
     detail=[L(112, 84, 144, 84), L(112, 156, 144, 156)])

icon('office-chair', HM, ['desk chair', 'office', 'seat'],
     line=[R(80, 32, 96, 72, 20), L(128, 104, 128, 136), R(48, 136, 160, 32, 16), L(128, 168, 128, 216),
           PL([(64, 216), (128, 192), (192, 216)])],
     area=[R(80, 32, 96, 72, 20), R(48, 136, 160, 32, 16)])

OP = R(40, 40, 176, 176, 28)
icon('outlet', HM, ['socket', 'outlet', 'power', 'electrical', 'power outlet'],
     line=[OP], area=[OP], detail=[L(100, 92, 100, 124), L(156, 92, 156, 124)], dotcut=[C(128, 168, 16)])

OV = R(40, 32, 176, 192, 14)
icon('oven', HM, ['oven', 'stove', 'baking', 'kitchen', 'bake'],
     line=[OV], area=[OV], detail=[R(72, 112, 112, 80, 10)],
     dotcut=[C(88, 68, 14), C(128, 68, 14), C(168, 68, 14)])

pb_bristle = 'M72 136 V208 A16 16 0 0 0 88 224 H168 A16 16 0 0 0 184 208 V136'
icon('paint-brush-household', HM, ['house paint brush', 'decorating', 'diy'],
     line=[P('M108 104 V52 A20 20 0 0 1 148 52 V104'), R(64, 104, 128, 32, 8), P(pb_bristle)],
     area=[P('M108 104 V52 A20 20 0 0 1 148 52 V104 Z'), R(64, 104, 128, 32, 8), P(pb_bristle + ' Z')],
     detail=[L(104, 164, 104, 196), L(152, 164, 152, 196)])

PF = R(40, 80, 176, 144, 14)
icon('picture-frame', HM, ['wall art', 'frame', 'painting', 'photo frame'],
     line=[PF, PL([(84, 80), (128, 44), (172, 80)])], area=[PF],
     detail=[R(72, 112, 112, 80, 4)], dot=[C(128, 40, 16)])

pil = 'M56 60 C104 80 152 80 200 60 C188 104 188 152 200 196 C152 176 104 176 56 196 C68 152 68 104 56 60 Z'
icon('pillow', HM, ['pillow', 'sleep', 'bed', 'cushion'], line=[P(pil)], area=[P(pil)])

pipe = 'M48 88 H144 A64 64 0 0 1 208 152 V216 H152 V152 A8 8 0 0 0 144 144 H48 Z'
icon('pipe', HM, ['plumbing', 'pipe', 'water line'],
     line=[P(pipe), L(80, 72, 80, 160), L(136, 184, 224, 184)], area=[P(pipe)])

# pipe wrench: drawn upright then rotated 45 deg so the jaw points up-right
pw = [(112, 244), (112, 28), (196, 28), (196, 64), (148, 64), (148, 104), (196, 104), (196, 136), (152, 136), (152, 244)]
def pw_tf(pts):
    q = rot(pts, 45)
    return [(128 + (x - 128) * 0.8 - 4, 128 + (y - 128) * 0.8 - 7) for x, y in q]
pwp = pw_tf(pw)
icon('pipe-wrench', 'Objects', ['plumbing wrench', 'tool', 'repair', 'plumbing', 'plumber'],
     line=[PG(pwp)], area=[PG(pwp)])

plg = 'M48 208 C72 208 80 192 80 176 A48 48 0 0 1 176 176 C176 192 184 208 208 208 Z'
icon('plunger', HM, ['plunger', 'toilet', 'plumbing', 'unclog'],
     line=[L(128, 32, 128, 128), P(plg)], area=[P(plg)])

pc_body = R(48, 104, 160, 104, 20)
pc_lid = 'M48 104 C48 76 80 64 128 64 C176 64 208 76 208 104'
icon('pressure-cooker', HM, ['multicooker', 'slow cooker', 'rice cooker', 'kitchen'],
     line=[pc_body, P(pc_lid), L(128, 40, 128, 64), L(28, 128, 48, 128), L(208, 128, 228, 128)],
     area=[pc_body, P(pc_lid + ' Z')], detail=[R(100, 136, 56, 40, 8)])

rh = 'M104 32 V96 L48 144 V184 H208 V144 L152 96 V32'
icon('range-hood', HM, ['cooker hood', 'extractor', 'kitchen', 'vent'],
     line=[P(rh), L(48, 144, 208, 144)], area=[P(rh + ' Z')], dot=[C(96, 216, 12), C(160, 216, 12)])

# rocking chair
r_rk = 176
def rocker_y(x):
    cy = 188 - math.sqrt(r_rk ** 2 - 88 ** 2)
    return cy + math.sqrt(r_rk ** 2 - (x - 128) ** 2)
icon('rocking-chair', HM, ['rocking chair', 'chair', 'relax', 'furniture'],
     line=[P(f'M40 188 A{r_rk} {r_rk} 0 0 0 216 188'),
           PL([(60, 40), (84, 136), (176, 136), (180, rocker_y(180))]),
           L(84, 136, 80, rocker_y(80)), PL([(74, 96), (160, 96), (160, 136)])])

icon('rug', HM, ['carpet', 'rug', 'mat'],
     line=[R(64, 56, 128, 144, 10)] + [L(40, y, 64, y) for y in (80, 112, 144, 176)]
     + [L(192, y, 216, y) for y in (80, 112, 144, 176)],
     area=[R(64, 56, 128, 144, 10)], detail=[PG([(128, 96), (160, 128), (128, 160), (96, 128)])])

book_lean = rot([(160, 128), (160, 72), (192, 72), (192, 128)], 16, (160, 128))
icon('shelves', HM, ['shelves', 'shelf', 'bookcase', 'storage'],
     line=[R(40, 32, 176, 192, 12), L(40, 128, 216, 128), R(72, 72, 32, 56, 4), R(104, 64, 32, 64, 4),
           PG(book_lean), R(120, 176, 64, 48, 4)],
     area=[R(72, 72, 32, 56, 4), R(104, 64, 32, 64, 4), PG(book_lean), R(120, 176, 64, 48, 4)])

icon('shower', HM, ['shower', 'bathroom', 'water', 'wash'],
     line=[P('M48 224 V88 A48 48 0 0 1 144 88 V96'), P('M104 136 A40 40 0 0 1 184 136 Z')],
     area=[P('M104 136 A40 40 0 0 1 184 136 Z')],
     dot=[C(104, 176, 14), C(144, 176, 14), C(184, 176, 14), C(124, 212, 14), C(164, 212, 14)])

SL = R(64, 32, 128, 192, 24)
icon('smart-lock', HM, ['smart lock', 'keypad', 'door', 'security'],
     line=[SL], area=[SL], detail=[C(128, 176, 18)],
     dotcut=[C(108, 76, 14), C(148, 76, 14), C(108, 116, 14), C(148, 116, 14)])

print(save(overwrite=True))
