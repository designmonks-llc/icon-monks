import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

OB = 'Objects'
PE = 'People'
SLASH = L(48, 48, 208, 208)


def T(segs, deg=0, c=(128, 128), s=1.0, off=(0, 0)):
    """Path from segments, scaled by s about c, rotated by deg about c, then offset."""
    def tp(p):
        x = c[0] + (p[0] - c[0]) * s
        y = c[1] + (p[1] - c[1]) * s
        x, y = rot([(x, y)], deg, c)[0]
        return (x + off[0], y + off[1])
    out = []
    for sg in segs:
        k = sg[0]
        if k in 'ML':
            out.append(k + pt(tp(sg[1])))
        elif k == 'C':
            out.append('C' + ' '.join(pt(tp(q)) for q in sg[1:]))
        elif k == 'Q':
            out.append('Q' + ' '.join(pt(tp(q)) for q in sg[1:]))
        elif k == 'A':
            r, large, sweep, p = sg[1:]
            out.append(f'A{f(r * s)} {f(r * s)} 0 {large} {sweep} {pt(tp(p))}')
        elif k == 'Z':
            out.append('Z')
    return ' '.join(out)


# ------------------------------------------------------------------ sun-hat
brim = E(128, 156, 96, 36)
crown = 'M80 124.8 V108 A48 48 0 0 1 176 108 V124.8'
crown_area = crown + ' A96 36 0 0 0 80 124.8 Z'
icon('sun-hat', OB, ['sun hat', 'straw hat', 'summer', 'beach'],
     line=[brim, P(crown)], detail=[P('M80 124.8 A96 36 0 0 1 176 124.8')],
     area=[brim, P(crown_area)])

# ------------------------------------------------------------------ sunglasses
lensL = 'M40 104 H112 V128 A36 36 0 0 1 76 164 A36 36 0 0 1 40 128 Z'
lensR = 'M144 104 H216 V128 A36 36 0 0 1 180 164 A36 36 0 0 1 144 128 Z'
icon('sunglasses', OB, ['sunglasses', 'shades', 'summer', 'cool'],
     line=[P(lensL), P(lensR), P('M112 112 Q128 96 144 112'), L(40, 104, 32, 92), L(216, 104, 224, 92)],
     area=[P(lensL), P(lensR)])

# ------------------------------------------------------------------ sweater
sw = ('M104 44 A24 20 0 0 0 152 44 L184 56 L224 188 L194 196 L172 118 V212 H84 V118 L62 196 L32 188 L72 56 Z')
icon('sweater', OB, ['sweater', 'jumper', 'knit', 'clothing'],
     line=[P(sw)], detail=[L(84, 184, 172, 184)], area=[P(sw)])

# ------------------------------------------------------------------ swimsuit
suit = ('M76 92 C100 120 156 120 180 92 C184 116 168 136 168 156 C168 172 184 180 184 192 '
        'C160 192 148 204 144 216 H112 C108 204 96 192 72 192 C72 180 88 172 88 156 C88 136 72 116 76 92 Z')
icon('swimsuit', OB, ['swimsuit', 'bathing suit', 'beach', 'clothing'],
     line=[P(suit), L(84, 40, 84, 100), L(172, 40, 172, 100)], area=[P(suit)])

# ------------------------------------------------------------------ sword
def sword_parts():
    blade = T([('M', (128, 14)), ('L', (150, 38)), ('L', (150, 156)), ('L', (106, 156)), ('L', (106, 38)), ('Z',)], 45)
    guard = T([('M', (74, 156)), ('L', (182, 156))], 45)
    grip = T([('M', (128, 156)), ('L', (128, 210))], 45)
    pom = rot([(128, 228)], 45)[0]
    return blade, guard, grip, pom

bl, gu, gr, pom = sword_parts()
icon('sword', OB, ['sword', 'blade', 'weapon', 'knight', 'fight'],
     line=[P(bl), P(gu), P(gr)], area=[P(bl)], dot=[C(pom[0], pom[1], 16)])
icon('sword-slash', OB, ['sword', 'off', 'disabled', 'hidden'],
     line=[P(bl), P(gu), P(gr), SLASH], dot=[C(pom[0], pom[1], 16)])

# ------------------------------------------------------------------ t-shirt-slash
ts = load('t-shirt')
icon('t-shirt-slash', OB, ['t shirt', 'off', 'disabled', 'hidden', 'shirt'], line=ts['line'] + ts['detail'] + [SLASH])

# ------------------------------------------------------------------ tape-measure
case = R(32, 56, 152, 144, 28)
strip = 'M184 164 H220 V200 H156'
icon('tape-measure', OB, ['measuring tape', 'measure', 'length', 'tool', 'tape measure'],
     line=[case, P(strip), L(220, 152, 220, 208)], detail=[C(108, 128, 32)],
     area=[case, R(156, 164, 64, 36)])

# ------------------------------------------------------------------ tent-slash
tn = load('tent')
icon('tent-slash', OB, ['tent', 'off', 'disabled', 'hidden'], line=tn['line'] + tn['detail'] + [SLASH])

# ------------------------------------------------------------------ thermos
tbody = R(80, 72, 96, 144, 20)
lid = R(96, 32, 64, 40, 10)
icon('thermos', OB, ['thermos', 'flask', 'insulated', 'bottle'],
     line=[tbody, lid], detail=[L(80, 108, 176, 108), L(80, 180, 176, 180)], area=[tbody, lid])

# ------------------------------------------------------------------ tools
HC = (128, 150)
def hammer_segs():
    # vertical hammer, head on top, then rotated -30 about HC
    head = [('M', (100, 40)), ('L', (160, 40)), ('L', (160, 76)), ('L', (88, 76)), ('L', (72, 64)), ('L', (72, 52)), ('Z',)]
    handle = [('M', (128, 76)), ('L', (128, 228))]
    return head, handle

def wrench_segs():
    c = (128, 72)
    r = 34
    a = polar(c, r, -90 - 24)
    b = polar(c, r, -90 + 24)
    head = [('M', a), ('L', (a[0], 70)), ('L', (b[0], 70)), ('L', b), ('A', r, 1, 1, a), ('Z',)]
    handle = [('M', (128, 106)), ('L', (128, 228))]
    return head, handle

def tools_paths(deg_h=-32, deg_w=32):
    hh, hd = hammer_segs()
    wh, wd = wrench_segs()
    k = dict(c=HC)
    return (T(hh, deg_h, **k), T(hd, deg_h, **k), T(wh, deg_w, **k), T(wd, deg_w, **k))

th, thd, tw, twd = tools_paths()
icon('tools', OB, ['tools', 'hammer and wrench', 'repair', 'settings'],
     line=[P(th), P(thd), P(tw), P(twd)], area=[P(th), P(tw)])
icon('tools-slash', OB, ['tools', 'off', 'disabled', 'hidden'],
     line=[P(th), P(thd), P(tw), P(twd), SLASH])

# ------------------------------------------------------------------ torch
flame = 'M100 116 C84 92 100 64 128 32 C156 64 172 92 156 116'
bowl = [(72, 116), (184, 116), (152, 148), (140, 216), (116, 216), (104, 148)]
icon('torch', OB, ['torch', 'flame', 'olympic', 'fire', 'olympic flame'],
     line=[P(flame), PG(bowl)], detail=[L(104, 148, 152, 148)],
     area=[P(flame + ' Z'), PG(bowl)])

# ------------------------------------------------------------------ tote
tb = 'M48 112 H208 L192 208 A12 12 0 0 1 180 216 H76 A12 12 0 0 1 64 208 Z'
icon('tote', OB, ['tote bag', 'beach bag', 'carry bag'],
     line=[P(tb), P('M88 112 V88 A40 40 0 0 1 168 88 V112')], detail=[], area=[P(tb)])

# ------------------------------------------------------------------ toy-brick
bk = R(32, 104, 192, 96, 14)
studs = ['M56 104 V76 A8 8 0 0 1 64 68 H96 A8 8 0 0 1 104 76 V104',
         'M152 104 V76 A8 8 0 0 1 160 68 H192 A8 8 0 0 1 200 76 V104']
icon('toy-brick', OB, ['toy brick', 'building block', 'toy', 'construction'],
     line=[bk] + [P(s) for s in studs], area=[bk] + [P(s + ' Z') for s in studs])

# ------------------------------------------------------------------ traffic-cone
cone = 'M112 40 H144 L184 184 H72 Z'
cb = R(32, 184, 192, 32, 10)
def cone_x(y):
    h = 16 + (y - 40) / 144 * 56
    return 128 - h, 128 + h
s1 = cone_x(88); s2 = cone_x(136)
cone_details = [L(s1[0], 88, s1[1], 88), L(s2[0], 136, s2[1], 136)]
icon('traffic-cone', OB, ['cone', 'construction', 'road', 'caution', 'roadwork'],
     line=[P(cone), cb], detail=cone_details, area=[P(cone), cb])
icon('traffic-cone-slash', OB, ['traffic cone', 'off', 'disabled', 'hidden', 'traffic'],
     line=[P(cone), cb] + cone_details + [SLASH])

# ------------------------------------------------------------------ treasure-chest
chest = 'M32 208 V96 C32 72 48 56 72 56 H184 C208 56 224 72 224 96 V208 Z'
icon('treasure-chest', OB, ['chest', 'treasure', 'loot', 'reward', 'treasure chest'],
     line=[P(chest)], detail=[L(32, 112, 106, 112), L(150, 112, 224, 112), R(106, 92, 44, 48, 10)],
     area=[P(chest)])

# ------------------------------------------------------------------ trident
icon('trident', OB, ['trident', 'poseidon', 'spear', 'fork'],
     line=[L(128, 40, 128, 220), P('M64 52 V96 C64 120 88 136 128 136 C168 136 192 120 192 96 V52'),
           PL([(110, 58), (128, 38), (146, 58)]), PL([(48, 72), (64, 52), (80, 72)]),
           PL([(176, 72), (192, 52), (208, 72)])])

# ------------------------------------------------------------------ trowel
tro_blade = [('M', (128, 26)), ('C', (156, 50), (166, 74), (166, 98)), ('C', (166, 120), (150, 132), (128, 132)),
             ('C', (106, 132), (90, 120), (90, 98)), ('C', (90, 74), (100, 50), (128, 26)), ('Z',)]
tb_ = T(tro_blade, 45)
neck = T([('M', (128, 132)), ('L', (128, 158))], 45)
handle = T([('M', (128, 166)), ('L', (128, 214))], 45)
hcap = capsule(rot([(128, 190)], 45)[0], 24, 16, (math.cos(math.radians(135)), math.sin(math.radians(135))))
mid = T([('M', (128, 62)), ('L', (128, 108))], 45)
icon('trowel', OB, ['trowel', 'garden', 'masonry', 'tool'],
     line=[P(tb_), P(neck), P(hcap)], detail=[P(mid)], area=[P(tb_), P(hcap)])

# ------------------------------------------------------------------ umbrella-beach
def canopy_segs(cx, cy, R_):
    r3 = R_ / 3
    pts = [(cx - R_ + i * 2 * r3, cy) for i in range(4)]
    segs = [('M', pts[0]), ('A', R_, 0, 1, pts[3])]
    for i in (2, 1, 0):
        segs.append(('A', r3, 0, 0, pts[i]))
    segs.append(('Z',))
    return segs

UB_DEG = -18
UB_C = (120, 200)
can = T(canopy_segs(120, 112, 80), UB_DEG, UB_C)
pole = T([('M', (120, 112)), ('L', (120, 202))], UB_DEG, UB_C)
icon('umbrella-beach', OB, ['beach', 'parasol', 'summer', 'vacation'],
     line=[P(can), P(pole), P('M32 208 C80 196 176 196 224 208')], area=[P(can)])

# ------------------------------------------------------------------ umbrella-closed
uc = 'M128 48 C152 84 164 120 160 156 H96 C92 120 104 84 128 48 Z'
icon('umbrella-closed', OB, ['closed umbrella', 'rain', 'folded', 'accessory'],
     line=[P(uc), L(128, 32, 128, 48), P('M128 156 V196 A20 20 0 0 1 88 196')],
     detail=[L(98, 124, 158, 124)], area=[P(uc)])

# ------------------------------------------------------------------ umbrella-slash
um = load('umbrella')
icon('umbrella-slash', OB, ['umbrella', 'off', 'disabled', 'hidden'], line=um['line'] + um['detail'] + [SLASH])

# ------------------------------------------------------------------ underwear
uw = ('M40 56 H216 V104 C216 136 212 160 204 172 C180 174 158 188 152 208 H104 '
      'C98 188 76 174 52 172 C44 160 40 136 40 104 Z')
icon('underwear', OB, ['briefs', 'underpants', 'clothing', 'underwear', 'undergarment'],
     line=[P(uw)], detail=[L(40, 92, 216, 92)], area=[P(uw)])

# ------------------------------------------------------------------ vest
vest = ('M100 40 L128 112 L156 40 H180 C180 80 192 100 208 104 V196 A12 12 0 0 1 198 208 L128 216 '
        'L58 208 A12 12 0 0 1 48 196 V104 C64 100 76 80 76 40 Z')
icon('vest', OB, ['vest', 'waistcoat', 'clothing', 'sleeveless'],
     line=[P(vest)], area=[P(vest)], dotcut=[C(128, 148, 12), C(128, 184, 12)])

# ------------------------------------------------------------------ water-bottle
wb = R(76, 88, 104, 128, 24)
cap = R(100, 56, 56, 32, 8)
icon('water-bottle', OB, ['bottle', 'water', 'hydration', 'drink'],
     line=[wb, cap, P('M112 56 V48 A16 16 0 0 1 144 48 V56')],
     detail=[P('M76 136 Q102 120 128 136 T180 136')], area=[wb, cap])

# ------------------------------------------------------------------ wheelbarrow
tray = 'M32 72 H200 L168 136 H68 Z'
frame = [(72, 184), (136, 136)]
wheel = C(72, 184, 28)
wb_lines = [P(tray), wheel, PL([(100, 163), (180, 104), (224, 104)]), L(168, 136, 180, 212)]
icon('wheelbarrow', OB, ['wheelbarrow', 'garden', 'construction', 'cart', 'garden cart'],
     line=wb_lines, area=[P(tray), wheel], dotcut=[C(72, 184, 10)])
icon('wheelbarrow-slash', OB, ['wheelbarrow', 'off', 'disabled', 'hidden'], line=wb_lines + [SLASH])

# ------------------------------------------------------------------ wizard-hat
wbrim = E(128, 188, 96, 28)
wcone = 'M72 176 C96 136 112 80 152 36 C152 80 164 136 184 176'
def spark(cx, cy, r):
    k = r * 0.28
    return P(f'M{f(cx)} {f(cy - r)} Q{f(cx + k)} {f(cy - k)} {f(cx + r)} {f(cy)} Q{f(cx + k)} {f(cy + k)} {f(cx)} {f(cy + r)} '
             f'Q{f(cx - k)} {f(cy + k)} {f(cx - r)} {f(cy)} Q{f(cx - k)} {f(cy - k)} {f(cx)} {f(cy - r)} Z')
icon('wizard-hat', OB, ['wizard hat', 'magic', 'sorcerer', 'fantasy'],
     line=[wbrim, P(wcone)], detail=[spark(132, 132, 22), P('M72 176 A96 28 0 0 0 184 176')],
     area=[wbrim, P(wcone + ' A96 28 0 0 1 72 176 Z')])

# ------------------------------------------------------------------ workbench
top = R(32, 104, 192, 36, 10)
vise = R(48, 60, 80, 44, 10)
icon('workbench', OB, ['workbench', 'workshop', 'table', 'tools'],
     line=[top, vise, L(56, 140, 56, 216), L(200, 140, 200, 216), L(56, 184, 200, 184), L(128, 82, 160, 82), L(160, 64, 160, 100)],
     detail=[L(88, 60, 88, 104)], area=[top, vise])

# ------------------------------------------------------------------ wrecking-ball
bc = (160, 164)
piv = (88, 40)
d = dist(piv, bc)
ce = (piv[0] + (bc[0] - piv[0]) * (d - 56) / d, piv[1] + (bc[1] - piv[1]) * (d - 56) / d)
icon('wrecking-ball', OB, ['wrecking ball', 'demolition', 'crane', 'destroy'],
     line=[C(bc[0], bc[1], 56), L(piv[0], piv[1], ce[0], ce[1]), L(32, 104, piv[0], piv[1])],
     detail=[P(f'M{pt(polar(bc, 30, 180))} A30 30 0 0 1 {pt(polar(bc, 30, 270))}')],
     area=[C(bc[0], bc[1], 56)])

# ------------------------------------------------------------------ wrench-adjustable
wa = [('M', (110, 32)), ('L', (110, 70)), ('L', (146, 70)), ('L', (146, 48)), ('L', (172, 48)),
      ('C', (176, 72), (168, 96), (148, 108)), ('L', (148, 212)), ('A', 20, 0, 1, (108, 212)),
      ('L', (108, 108)), ('C', (88, 96), (80, 72), (82, 48)), ('C', (84, 40), (96, 32), (110, 32)), ('Z',)]
wap = T(wa, 45, (128, 124))
icon('wrench-adjustable', OB, ['adjustable wrench', 'spanner', 'tool', 'repair'],
     line=[P(wap)], area=[P(wap)], dotcut=[C(*rot([(128, 196)], 45, (128, 124))[0], 9)])

# ------------------------------------------------------------------ yarn
yc = (112, 144); yr = 80
def yarn_arc(cc, rr):
    a, b = circle_x(yc, yr, cc, rr)
    return P(f'M{pt(a)} ' + arc_to(cc, rr, a, b, lambda m: -dist(m, yc)))
yd = [yarn_arc((0, 256), 110), yarn_arc((0, 256), 150), yarn_arc((224, 40), 96)]
np_ = polar(yc, yr, -45)
icon('yarn', OB, ['yarn', 'knitting', 'wool', 'craft'],
     line=[C(*yc, yr), L(np_[0] + 8, np_[1] - 8, 212, 44)], detail=yd, area=[C(*yc, yr)],
     dot=[C(214, 42, 14)])

# ================================================================== People
# ------------------------------------------------------------------ baby-bonnet
ring = 'M40 148 A88 88 0 0 1 216 148 H176 A48 48 0 0 0 80 148 Z'
icon('baby-bonnet', PE, ['bonnet', 'hat', 'baby', 'child'],
     line=[P(ring), P('M68 156 L128 196 L188 156'), PG([(128, 196), (100, 184), (100, 212)]),
           PG([(128, 196), (156, 184), (156, 212)])],
     area=[P(ring)], dot=[C(108, 136, 10), C(148, 136, 10)])

# ------------------------------------------------------------------ baby-bottle
bb = R(88, 104, 80, 112, 20)
col = R(80, 76, 96, 28, 8)
icon('baby-bottle', PE, ['baby bottle', 'feeding', 'milk', 'infant'],
     line=[bb, col, P('M108 76 C108 56 116 42 128 38 C140 42 148 56 148 76')],
     detail=[L(88, 140, 112, 140), L(88, 176, 112, 176)], area=[bb, col, P('M108 76 C108 56 116 42 128 38 C140 42 148 56 148 76 Z')])

# ------------------------------------------------------------------ baby-carriage
pb = 'M40 96 H216 C216 132 184 152 128 152 C72 152 40 132 40 96 Z'
canp = 'M128 96 V32 A88 64 0 0 0 40 96 Z'
icon('baby-carriage', PE, ['stroller', 'pram', 'baby', 'child friendly', 'carriage'],
     line=[P(pb), P(canp), L(204, 96, 220, 56), C(84, 196, 20), C(172, 196, 20)],
     detail=[L(40, 96, 128, 96)], area=[P(pb), P(canp)])

# ------------------------------------------------------------------ baby-carrier
icon('baby-carrier', PE, ['baby carrier', 'sling', 'parent', 'infant'],
     line=[C(112, 56, 26), P('M40 216 C40 152 72 116 112 116 C152 116 184 152 184 216')],
     detail=[C(128, 160, 18), P('M92 168 C100 208 156 208 164 168')],
     area=[C(112, 56, 26), P('M40 216 C40 152 72 116 112 116 C152 116 184 152 184 216 Z')])

# ------------------------------------------------------------------ baby-changing
icon('baby-changing', PE, ['changing table', 'restroom', 'diaper', 'baby'],
     line=[C(64, 52, 20), PL([(64, 88), (64, 148)]), PL([(44, 216), (64, 148), (84, 216)]),
           PL([(64, 104), (100, 132)]), L(104, 164, 224, 164), L(208, 164, 208, 216),
           C(128, 132, 16), L(160, 140, 208, 140)])

# ------------------------------------------------------------------ baby-feet
def foot(cx, cy, mirror):
    s = -1 if mirror else 1
    sole = E(cx, cy, 26, 42)
    toes = [C(cx + s * 12, cy - 62, 15), C(cx - s * 14, cy - 58, 12), C(cx - s * 34, cy - 44, 10)]
    return sole, toes
s1_, t1 = foot(84, 168, False)
s2_, t2 = foot(172, 112, True)
icon('baby-feet', PE, ['footprints', 'baby', 'newborn', 'feet'],
     line=[s1_, s2_], area=[s1_, s2_], dot=t1 + t2)

# ------------------------------------------------------------------ bib
bib = ('M88 40 H104 A24 24 0 0 0 152 40 H168 C196 56 212 88 212 128 A84 84 0 0 1 44 128 C44 88 60 56 88 40 Z')
icon('bib', PE, ['bib', 'baby', 'feeding', 'infant'],
     line=[P(bib)], detail=[P('M88 156 C104 176 152 176 168 156')], area=[P(bib)])

# ------------------------------------------------------------------ blind
icon('blind', PE, ['blind', 'cane', 'visually impaired', 'accessibility'],
     line=[C(108, 52, 20), L(104, 88, 96, 144), PL([(64, 216), (76, 180), (96, 144), (120, 176), (128, 216)]),
           PL([(80, 136), (104, 100), (140, 128)]), L(140, 128, 196, 216)],
     area=[C(108, 52, 20)])

# ------------------------------------------------------------------ braille
raised = {(0, 0), (1, 0), (0, 1), (0, 2), (1, 2)}
raised2 = {(0, 0), (1, 1), (1, 2), (0, 1)}
big, small = [], []
for cx0, rs in ((48, raised), (160, raised2)):
    for i in range(2):
        for j in range(3):
            p = (cx0 + i * 48, 72 + j * 56)
            (big if (i, j) in rs else small).append(C(p[0], p[1], 20 if (i, j) in rs else 6))
icon('braille', PE, ['braille', 'blind', 'accessibility', 'dots'], dot=big + small)

# ------------------------------------------------------------------ breastfeeding
icon('breastfeeding', PE, ['nursing', 'mother', 'baby', 'feeding'],
     line=[C(100, 56, 24), P('M40 216 C40 152 64 116 100 116 C124 116 140 124 152 136'),
           C(164, 156, 20), P('M64 168 C92 212 176 212 212 164')],
     area=[C(100, 56, 24), C(164, 156, 20)])

# ------------------------------------------------------------------ car-seat
seat = ('M88 40 H168 A16 16 0 0 1 184 56 V120 H200 A16 16 0 0 1 216 136 V200 A16 16 0 0 1 200 216 '
        'H56 A16 16 0 0 1 40 200 V136 A16 16 0 0 1 56 120 H72 V56 A16 16 0 0 1 88 40 Z')
icon('car-seat', PE, ['car seat', 'baby', 'child', 'safety'],
     line=[P(seat)], detail=[PL([(104, 88), (128, 148), (152, 88)]), L(128, 148, 128, 184)],
     area=[P(seat)], dotcut=[])

# ------------------------------------------------------------------ child
icon('child', PE, ['kid', 'child', 'young', 'boy'],
     line=[C(128, 64, 28), L(128, 116, 128, 168), PL([(84, 160), (128, 128), (172, 160)]),
           PL([(96, 216), (128, 168), (160, 216)])],
     area=[C(128, 64, 28)])

# ------------------------------------------------------------------ community
ch = 'M80 208 V96 L128 48 L176 96 V208 Z'
lh = 'M32 208 V148 L68 112 L104 148 V208 Z'
rh = 'M152 208 V148 L188 112 L224 148 V208 Z'
icon('community', PE, ['community', 'neighborhood', 'houses'],
     line=[P('M80 124 V96 L128 48 L176 96 V124'), P(lh), P(rh), L(104, 208, 152, 208)],
     detail=[PL([(80, 124), (104, 148), (104, 208)]), PL([(176, 124), (152, 148), (152, 208)]),
             P('M116 208 V180 H140 V208')],
     area=[P(ch), P(lh), P(rh)])

# ------------------------------------------------------------------ construction-worker
dome = 'M84 88 A44 44 0 0 1 172 88'
face = 'M100 88 A36 36 0 1 0 156 88'
sh = 'M48 216 C48 188 84 176 128 176 C172 176 208 188 208 216'
icon('construction-worker', PE, ['engineer', 'builder', 'hard hat', 'worker', 'construction worker'],
     line=[P(dome), L(60, 88, 196, 88), P(face), P(sh)],
     detail=[L(128, 56, 128, 88)], area=[P(dome + ' Z'), P(sh + ' Z')])

# ------------------------------------------------------------------ detective
crown_d = 'M76 96 L88 52 C90 44 98 40 106 43 L128 52 L150 43 C158 40 166 44 168 52 L180 96'
lens1 = 'M84 132 H120 V140 A16 16 0 0 1 104 156 H100 A16 16 0 0 1 84 140 Z'
lens2 = 'M136 132 H172 V140 A16 16 0 0 1 156 156 H152 A16 16 0 0 1 136 140 Z'
icon('detective', PE, ['detective', 'investigator', 'incognito', 'mystery', 'spy'],
     line=[P(crown_d), P('M32 100 C64 90 192 90 224 100'), P('M84 104 C80 168 100 208 128 208 C156 208 176 168 172 104'),
           P(lens1), P(lens2), L(120, 136, 136, 136)],
     area=[P(crown_d + ' Z'), P(lens1), P(lens2)])

# ------------------------------------------------------------------ diaper
dp = 'M40 72 H216 V112 C216 168 176 208 128 208 C80 208 40 168 40 112 Z'
icon('diaper', PE, ['diaper', 'nappy', 'baby', 'infant'],
     line=[P(dp)], detail=[L(40, 104, 216, 104), P('M76 136 C92 152 100 172 100 196'), P('M180 136 C164 152 156 172 156 196')], area=[P(dp)])

# ------------------------------------------------------------------ eyebrow
brow = 'M40 108 C76 56 168 40 216 84 C172 76 92 92 48 124 Z'
eye = 'M48 168 C88 116 168 116 208 168 C168 220 88 220 48 168 Z'
icon('eyebrow', PE, ['eyebrow', 'face', 'beauty', 'brow'],
     line=[P(brow), P(eye)], area=[P(brow), P(eye)], dotcut=[C(128, 168, 16)])

# ------------------------------------------------------------------ family
icon('family', PE, ['family', 'parents', 'child', 'household'],
     line=[C(68, 72, 24), C(188, 72, 24), C(128, 132, 18),
           P('M32 200 V156 C32 128 48 112 68 112 C88 112 104 128 104 148'),
           P('M224 200 V156 C224 128 208 112 188 112 C168 112 152 128 152 148'),
           P('M96 216 C96 188 108 172 128 172 C148 172 160 188 160 216')],
     area=[C(68, 72, 24), C(188, 72, 24), C(128, 132, 18)])

# ------------------------------------------------------------------ gender-intersex
gc = (108, 128); gr_ = 52
tip = (204, 52)
st = polar(gc, gr_, -45)
icon('gender-intersex', PE, ['intersex', 'gender', 'symbol', 'identity'],
     line=[C(*gc, gr_), L(st[0], st[1], tip[0], tip[1]), PL([(164, 52), tip, (204, 92)]),
           L(108, 180, 108, 224), L(84, 204, 132, 204)])

print(save(overwrite=True))
