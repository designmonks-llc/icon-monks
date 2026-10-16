import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

NA, OB, HO, HE = 'Nature', 'Objects', 'Home', 'Health'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def rpoly(points, r, close=True):
    """Polygon with rounded corners (quadratic through each vertex)."""
    n = len(points)
    out = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        if not close and (i == 0 or i == n - 1):
            out.append(('P', p1))
            continue
        d1, d2 = dist(p0, p1), dist(p1, p2)
        k1, k2 = min(r, d1 / 2), min(r, d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * k1 / d1, p1[1] + (p0[1] - p1[1]) * k1 / d1)
        b = (p1[0] + (p2[0] - p1[0]) * k2 / d2, p1[1] + (p2[1] - p1[1]) * k2 / d2)
        out.append(('Q', a, p1, b))
    d = ''
    for i, o in enumerate(out):
        if o[0] == 'P':
            d += ('M' if i == 0 else ' L') + pt(o[1])
        else:
            d += ('M' if i == 0 else ' L') + pt(o[1]) + f' Q{pt(o[2])} {pt(o[3])}'
    return d + (' Z' if close else '')


def tp(cmds, deg=0, c=(128, 128), close=False):
    """Path from ('M'|'L'|'Q'|'C', pts...) commands, rotated about c."""
    d = []
    for cmd in cmds:
        ps = rot(list(cmd[1:]), deg, c) if deg else cmd[1:]
        d.append(cmd[0] + ' '.join(pt(p) for p in ps))
    return ' '.join(d) + (' Z' if close else '')


def lens(p, q, w):
    """Leaf/grain lens between p and q; w = control offset (half-thickness ~ w/2)."""
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    dx, dy = q[0] - p[0], q[1] - p[1]
    ln = math.hypot(dx, dy)
    n = (-dy / ln * w, dx / ln * w)
    c1 = (m[0] + n[0], m[1] + n[1])
    c2 = (m[0] - n[0], m[1] - n[1])
    return f'M{pt(p)} Q{pt(c1)} {pt(q)} Q{pt(c2)} {pt(p)} Z'


def slashed(base, name, cat, tags, extra_line=()):
    icon(name, cat, tags, line=base.get('line', []) + base.get('detail', []) + list(extra_line) + [SLASH],
         dot=base.get('dot', []) + base.get('dotcut', []))


# ================================================================ Nature
# mushroom
MUSH_CAP = 'M40 136 C40 80 80 40 128 40 C176 40 216 80 216 136 Q216 148 204 148 H52 Q40 148 40 136 Z'
MUSH_STEM = 'M100 148 L94 198 A16 16 0 0 0 110 216 H146 A16 16 0 0 0 162 198 L156 148'
MUSH_STEM_A = MUSH_STEM + ' Z'
MUSH = dict(line=[P(MUSH_CAP), P(MUSH_STEM)], area=[P(MUSH_CAP), P(MUSH_STEM_A)],
            dotcut=[C(88, 112, 14), C(128, 80, 14), C(168, 112, 14)])
icon('mushroom', NA, ['mushroom', 'fungus', 'toadstool', 'forest'], **MUSH)
slashed(MUSH, 'mushroom-slash', NA, ['mushroom', 'off', 'disabled', 'hidden'])

# north-star
ns = [(128, 32), (142, 114), (200, 128), (142, 142), (128, 224), (114, 142), (56, 128), (114, 114)]
diag = []
for a in (-45, 45, 135, 225):
    diag.append(L(*polar((128, 128), 62, a), *polar((128, 128), 82, a)))
icon('north-star', NA, ['north star', 'guiding star', 'compass', 'sky'],
     line=[P(rpoly(ns, 6))] + diag, area=[P(rpoly(ns, 6))])

# plant-slash
slashed(load('plant'), 'plant-slash', NA, ['plant', 'off', 'disabled', 'hidden'])

# potted-plant
POT_RIM = R(56, 144, 144, 32, 8)
POT = 'M72 176 L80 206 Q83 216 94 216 H162 Q173 216 176 206 L184 176'
leaves = [lens((128, 128), (128, 36), 40), lens((112, 140), (48, 100), 34), lens((144, 140), (208, 100), 34)]
icon('potted-plant', NA, ['houseplant', 'pot plant', 'decor', 'plant pot', 'indoor plant'],
     line=[P(l) for l in leaves] + [POT_RIM, P(POT)],
     area=[P(l) for l in leaves] + [POT_RIM, P(POT + ' Z')])

# rainbow-slash
slashed(load('rainbow'), 'rainbow-slash', NA, ['rainbow', 'off', 'disabled', 'hidden'])

# recycle: three chasing arrows on a rounded triangle
RC = (128, 142)
V = [polar(RC, 106, -90), polar(RC, 106, 30), polar(RC, 106, 150)]


def recycle_lines():
    out = []
    for k in range(3):
        v0, v1, vp = V[k], V[(k + 1) % 3], V[(k + 2) % 3]
        s = lerp_(vp, v0, 0.62)
        a = lerp_(vp, v0, 0.84)
        b = lerp_(v0, v1, 0.16)
        e = lerp_(v0, v1, 0.40)
        out.append(P(f'M{pt(s)} L{pt(a)} Q{pt(v0)} {pt(b)} L{pt(e)}'))
        ang = math.degrees(math.atan2(v1[1] - v0[1], v1[0] - v0[0]))
        w1 = polar(e, 30, ang + 180 - 45)
        w2 = polar(e, 30, ang + 180 + 45)
        out.append(PL([w1, e, w2]))
    return out


def lerp_(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


REC = dict(line=recycle_lines())
icon('recycle', NA, ['recycle', 'eco', 'environment', 'reuse', 'green'], **REC)
slashed(REC, 'recycle-slash', NA, ['recycle', 'off', 'disabled', 'hidden'])

# rock
rock = rpoly([(32, 212), (40, 164), (72, 124), (104, 116), (132, 72), (180, 68), (208, 108), (224, 168), (220, 212)], 10)
icon('rock', NA, ['rock', 'stone', 'boulder', 'geology'],
     line=[P(rock)], area=[P(rock)], detail=[PL([(108, 156), (144, 120), (180, 132)])])

# shooting-star
sc = (160, 96)
st = [polar(sc, 60 if i % 2 == 0 else 26, -90 + i * 36) for i in range(10)]
icon('shooting-star', NA, ['wish', 'meteor', 'falling star'],
     line=[P(rpoly(st, 5)), L(100, 156, 44, 212), L(76, 128, 44, 160), L(128, 180, 100, 208)],
     area=[P(rpoly(st, 5))])

# snowman
HC, HR = (128, 72), 36
BC, BR = (128, 160), 60
q1, q2 = circle_x(BC, BR, HC, HR)  # sorted by y, both same y
i1, i2 = sorted(circle_x(BC, BR, HC, HR), key=lambda p: p[0])
body = f'M{pt(i1)} ' + arc_to(BC, BR, i1, i2, lambda m: m[1])
head_a = f'M{pt(i2)} ' + arc_to(HC, HR, i2, i1, lambda m: -m[1])
snow_area = body + ' ' + arc_to(HC, HR, i2, i1, lambda m: -m[1])[0:] + ' Z'
icon('snowman', NA, ['snowman', 'winter', 'snow', 'christmas'],
     line=[P(body), C(*HC, HR), L(70, 140, 40, 116), L(186, 140, 216, 116)],
     area=[P(snow_area)],
     dotcut=[C(128, 144, 12), C(128, 184, 12)])

# soil
soil = 'M32 208 C40 120 88 64 128 64 C168 64 216 120 224 208 Z'
icon('soil', NA, ['dirt', 'ground', 'earth'],
     line=[P(soil)], area=[P(soil)],
     detail=[P('M88 124 Q108 112 128 124 T168 124'), P('M64 168 Q96 152 128 168 T192 168')])

# tree-acacia
canopy = 'M52 116 C32 116 32 84 58 80 C68 56 104 50 128 58 C152 50 188 56 198 80 C224 84 224 116 204 116 Z'
icon('tree-acacia', NA, ['acacia', 'savanna', 'africa'],
     line=[P(canopy), PL([(128, 224), (128, 168), (96, 116)]), L(128, 168, 168, 116)],
     area=[P(canopy)])

# tree-palm
icon('tree-palm', NA, ['palm tree', 'tropical', 'beach', 'palm', 'coconut'],
     line=[P('M100 224 C112 176 128 136 128 92'),
           P('M128 92 C104 60 64 60 40 100'), P('M128 92 C152 60 192 60 216 100'),
           P('M128 92 C116 64 92 44 60 44'), P('M128 92 C140 64 164 44 196 44')],
     dot=[C(112, 112, 14), C(144, 112, 14)])

# trees: round tree behind, smaller round tree in front
LC, LR = (92, 96), 60
RCc, RR = (168, 132), 48
G = 24
t1, t2 = circle_x(LC, LR, RCc, RR + G)
left_arc = f'M{pt(t1)} ' + arc_to(LC, LR, t1, t2, lambda m: dist(m, RCc))
left_area = left_arc + ' ' + arc_to(RCc, RR + G, t2, t1, lambda m: -dist(m, LC)) + ' Z'
icon('trees', NA, ['trees', 'forest', 'woods', 'nature'],
     line=[P(left_arc), L(92, 156, 92, 224), C(*RCc, RR), L(168, 180, 168, 224)],
     area=[P(left_area), C(*RCc, RR)])

# twig
twig_leaf = lens((88, 112), (56, 56), 40)
icon('twig', NA, ['twig', 'branch', 'stick', 'wood'],
     line=[L(40, 216, 200, 56), PL([(104, 152), (88, 112)]), L(152, 104, 208, 112), P(twig_leaf)],
     area=[P(twig_leaf)])

# volcano
cone = rpoly([(32, 216), (92, 116), (164, 116), (224, 216)], 14)
icon('volcano', NA, ['volcano', 'eruption', 'mountain', 'steam', 'lava'],
     line=[P(cone), P('M108 92 C96 76 120 64 108 44'), P('M148 92 C136 76 160 64 148 44')],
     area=[P(cone)],
     detail=[PL([(96, 168), (112, 152), (128, 168), (144, 152), (160, 168)])])

# watering-can
can = R(32, 96, 112, 88, 16)
icon('watering-can', NA, ['gardening', 'watering', 'plants'],
     line=[can, P('M56 96 C56 52 120 52 120 96'), L(144, 160, 192, 112), L(180, 100, 204, 124),
           P('M152 220 Q188 192 224 220 Z')],
     area=[can, P('M152 220 Q188 192 224 220 Z')],
     dot=[C(216, 144, 12), C(200, 176, 12)])

# waves-slash
slashed(load('waves'), 'waves-slash', NA, ['waves', 'off', 'disabled', 'hidden'])

# wheat
wg = [lens((128, 108), (128, 44), 24)]
for y in (124, 176):
    wg.append(lens((128, y), (86, y - 42), 24))
    wg.append(lens((128, y), (170, y - 42), 24))
WHEAT = dict(line=[L(128, 108, 128, 224)] + [P(g) for g in wg] + [L(80, 74, 64, 52), L(176, 74, 192, 52)],
             area=[P(g) for g in wg])
icon('wheat', NA, ['wheat', 'grain', 'harvest', 'gluten'], **WHEAT)
slashed(WHEAT, 'wheat-slash', NA, ['wheat', 'off', 'disabled', 'hidden'])

# windmill
HUB = (128, 100)
tower = 'M106 164 L94 216 H162 L150 164'
sails = []
for a in (-135, -45, 45, 135):
    u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    n = (-u[1], u[0])
    p0 = (HUB[0] + u[0] * 22, HUB[1] + u[1] * 22)
    p1 = (HUB[0] + u[0] * 88, HUB[1] + u[1] * 88)
    sails.append(rpoly([p0, p1, (p1[0] + n[0] * 26, p1[1] + n[1] * 26), (p0[0] + n[0] * 26, p0[1] + n[1] * 26)], 6))
WIND = dict(line=[P(tower)] + [P(s) for s in sails] + [C(*HUB, 12)],
            area=[P(tower + ' Z')] + [P(s) for s in sails],
            detail=[P('M116 216 V196 A12 12 0 0 1 140 196 V216')])
icon('windmill', NA, ['windmill', 'farm', 'wind', 'energy'], **WIND)
slashed(WIND, 'windmill-slash', NA, ['windmill', 'off', 'disabled', 'hidden'])

# wood: log end with growth rings
WC = (128, 128)
ring1 = f'M{pt(polar(WC, 60, 160))} ' + arc_to(WC, 60, polar(WC, 60, 160), polar(WC, 60, 110), lambda m: dist(m, polar(WC, 60, 135)))
icon('wood', NA, ['wood', 'log', 'timber', 'lumber'],
     line=[C(*WC, 96)], area=[C(*WC, 96)],
     detail=[P(ring1), C(*WC, 24)])

# ================================================================ Objects
# afro-pick
icon('afro-pick', OB, ['comb', 'hair pick', 'hair', 'grooming'],
     line=[L(64, 112, 192, 112)] + [L(x, 112, x, 36) for x in (64, 101, 155, 192)] + [R(84, 112, 88, 104, 22)],
     area=[R(84, 112, 88, 104, 22)],
     detail=[L(114, 140, 114, 168), L(142, 140, 142, 168)])

# anvil with hammer
anvil = ('M40 136 H208 V148 A16 16 0 0 1 192 164 H172 L164 192 H180 V216 H76 V192 H92 L84 164 '
         'C64 164 48 156 40 136 Z')
hc = (128, 80)
handle = rot([(56, 84), (140, 84)], -24, hc)
head = rot([(140, 56), (176, 56), (176, 112), (140, 112)], -24, hc)
icon('anvil', OB, ['anvil', 'blacksmith', 'forge', 'hammer'],
     line=[P(anvil), PL(handle), P(rpoly(head, 8))], area=[P(anvil), P(rpoly(head, 8))])

# axe (drawn upright, rotated)
AXD = 28
axe_head = tp([('M', (172, 60)), ('L', (124, 60)), ('C', (108, 60), (92, 52), (72, 40)),
               ('C', (56, 72), (56, 120), (72, 152)), ('C', (92, 140), (108, 132), (124, 132)),
               ('L', (172, 132))], AXD, close=True)
icon('axe', OB, ['axe', 'wood', 'chop', 'tool'],
     line=[P(axe_head), P(tp([('M', (152, 40)), ('L', (152, 228))], AXD))],
     area=[P(axe_head)])

slashed(load('backpack'), 'backpack-slash', OB, ['backpack', 'disabled', 'off', 'objects'])

# bag-duffle
duf = R(32, 104, 192, 104, 48)
icon('bag-duffle', OB, ['duffle bag', 'gym bag', 'travel', 'luggage'],
     line=[duf, P('M88 104 V92 C88 56 168 56 168 92 V104')], area=[duf],
     detail=[L(84, 132, 84, 180), L(172, 132, 172, 180)])


# balloon-heart
def heart(cx, top, s):
    def T(x, y):
        return (cx + (x - 128) * s, top + (y - 48) * s)
    a = 50 * s
    return (f'M{pt(T(128, 212))} C{pt(T(128, 212))} {pt(T(32, 160))} {pt(T(32, 98))} '
            f'A{f(a)} {f(a)} 0 0 1 {pt(T(128, 78))} A{f(a)} {f(a)} 0 0 1 {pt(T(224, 98))} '
            f'C{pt(T(224, 160))} {pt(T(128, 212))} {pt(T(128, 212))} Z')


hb = heart(128, 36, 0.76)
hb_bottom = 36 + 164 * 0.76
icon('balloon-heart', OB, ['balloon', 'love', 'party', 'valentine', 'heart balloon'],
     line=[P(hb), PG([(128, hb_bottom), (116, hb_bottom + 14), (140, hb_bottom + 14)]),
           P(f'M128 {f(hb_bottom + 14)} C128 {f(hb_bottom + 28)} 114 {f(hb_bottom + 36)} 122 224')],
     area=[P(hb)],
     detail=[P('M84 104 A28 28 0 0 1 100 76')])

slashed(load('balloon'), 'balloon-slash', OB, ['balloon', 'disabled', 'off', 'objects'])

# barrel
brl = 'M68 36 H188 C216 88 216 168 188 220 H68 C40 168 40 88 68 36 Z'
BARREL = dict(line=[P(brl)], area=[P(brl)], detail=[L(80, 92, 176, 92), L(80, 164, 176, 164)])
icon('barrel', OB, ['oil barrel', 'drum', 'container', 'storage', 'barrel'], **BARREL)
slashed(BARREL, 'barrel-slash', OB, ['barrel', 'disabled', 'off', 'cask', 'wine'])

# barricade
board = R(32, 56, 192, 96, 14)
icon('barricade', OB, ['construction', 'roadblock', 'under construction', 'detour', 'barricade'],
     line=[board, L(72, 152, 56, 216), L(184, 152, 200, 216)], area=[board],
     detail=[L(x - 14, 126, x + 14, 82) for x in (80, 128, 176)])

# beanie
dome = 'M56 152 C56 100 88 72 128 72 C168 72 200 100 200 152'
band = R(40, 152, 176, 56, 16)
icon('beanie', OB, ['winter hat', 'knit cap', 'clothing', 'beanie', 'hat'],
     line=[P(dome), band, C(128, 52, 18)], area=[P(dome + ' Z'), band, C(128, 52, 18)],
     detail=[L(x, 172, x, 188) for x in (80, 112, 144, 176)])

# belt
strap_a = 'M32 96 H192 L224 128 L192 160 H32'
icon('belt', OB, ['belt', 'buckle', 'clothing', 'fashion'],
     line=[L(32, 96, 56, 96), L(32, 160, 56, 160), P('M136 96 H192 L224 128 L192 160 H136'),
           R(56, 72, 80, 112, 16)],
     area=[P(strap_a + ' Z'), R(56, 72, 80, 112, 16)],
     detail=[L(84, 128, 136, 128)],
     dotcut=[C(168, 128, 10), C(196, 128, 9)])

# blazer
jacket = 'M100 40 L60 56 Q40 64 40 84 V200 Q40 216 56 216 H200 Q216 216 216 200 V84 Q216 64 196 56 L156 40 Z'
icon('blazer', OB, ['suit', 'jacket', 'blazer', 'formal'],
     line=[P(jacket)], area=[P(jacket)],
     detail=[PL([(100, 56), (76, 104), (128, 184)]), PL([(156, 56), (180, 104), (128, 184)]),
             P(rpoly([(128, 60), (138, 72), (136, 132), (128, 146), (120, 132), (118, 72)], 4))])

# bomb
bc = (112, 148)
cap = rot([(156, 84), (184, 84), (184, 108), (156, 108)], -45, (170, 96))
cap = [(p[0] - 3, p[1] + 3) for p in cap]
icon('bomb', OB, ['bomb', 'explosive', 'danger', 'fuse'],
     line=[C(*bc, 72), P(rpoly(cap, 5)), P('M180 84 C184 64 196 60 200 52'),
           L(208, 32, 208, 36), L(220, 44, 224, 44)],
     area=[C(*bc, 72), P(rpoly(cap, 5))],
     detail=[P('M72 140 A44 44 0 0 1 104 106')])

# bong
bong_c, bong_r = (128, 168), 52
by = bong_c[1] - math.sqrt(bong_r ** 2 - 20 ** 2)
bong_body = f'M108 40 V{f(by)} ' + arc_to(bong_c, bong_r, (108, by), (148, by), lambda m: m[1]) + ' V40'
BONG = dict(line=[P(bong_body), L(100, 40, 156, 40), L(112, 180, 72, 140), P(rpoly([(48, 120), (88, 112), (84, 132), (60, 140)], 4))],
            area=[P(bong_body + ' Z')])
icon('bong', OB, ['bong', 'smoking', 'pipe'], **BONG)
slashed(BONG, 'bong-slash', OB, ['bong', 'disabled', 'off', 'smoking', 'pipe'])

# boot
boot = ('M80 36 H144 V132 L196 152 Q216 160 216 184 V204 A12 12 0 0 1 204 216 H76 A12 12 0 0 1 64 204 '
        'V52 Q64 36 80 36 Z')
icon('boot', OB, ['boot', 'footwear', 'hiking', 'boots', 'shoes'],
     line=[P(boot)], area=[P(boot)], detail=[L(92, 184, 188, 184), L(92, 72, 116, 72)])


# bucket
def bucket(handle=True):
    body = 'M48 104 H208 L190 204 Q188 216 176 216 H80 Q68 216 66 204 Z'
    d = dict(line=[P(body)], area=[P(body)], detail=[L(84, 144, 172, 144)])
    if handle:
        d['line'].append(P('M56 108 C56 30 200 30 200 108'))
    return d


BUCKET = bucket()
icon('bucket', OB, ['pail', 'cleaning', 'mop bucket', 'water', 'bucket'], **BUCKET)
bd = bucket(False)
drop = 'M128 30 C120 42 110 52 110 62 A18 18 0 0 0 146 62 C146 52 136 42 128 30 Z'
icon('bucket-drop', HO, ['bucket', 'water', 'fill'],
     line=bd['line'] + [P(drop)], area=bd['area'] + [P(drop)], detail=bd['detail'])
slashed(BUCKET, 'bucket-slash', HO, ['bucket', 'disabled', 'off', 'home'])

# chisel (upright, rotated 45)
CH = 45
ch_handle = rot([(104, 32), (152, 32), (152, 112), (104, 112)], CH)
ch_blade = rot([(110, 128), (146, 128), (146, 216), (110, 196)], CH)
icon('chisel', OB, ['chisel', 'tool', 'woodwork'],
     line=[P(rpoly(ch_handle, 14)), P(rpoly(ch_blade, 6)), P(tp([('M', (128, 112)), ('L', (128, 128))], CH))],
     area=[P(rpoly(ch_handle, 14)), P(rpoly(ch_blade, 6))])

# christmas-ornament
icon('christmas-ornament', OB, ['christmas', 'bauble', 'ornament', 'holiday'],
     line=[C(128, 140, 76), R(104, 44, 48, 24, 8), P('M116 44 A12 12 0 0 1 140 44')],
     area=[C(128, 140, 76), R(104, 44, 48, 24, 8)],
     detail=[P('M84 132 L106 114 L128 132 L150 114 L172 132'), P('M84 176 L106 158 L128 176 L150 158 L172 176')])

# cigarette
CIG_BODY = R(32, 156, 192, 40, 8)
CIG = dict(line=[CIG_BODY, P('M168 132 C152 116 184 100 168 84 C160 76 164 68 168 60'),
                 P('M204 132 C188 116 220 100 204 84 C196 76 200 68 204 60')],
           area=[CIG_BODY], detail=[L(80, 156, 80, 196)])
icon('cigarette', OB, ['smoking', 'cigarette', 'tobacco', 'smoking area', 'smoke area'], **CIG)
slashed(CIG, 'cigarette-slash', HE, ['no smoking', 'smoke free', 'prohibited', 'non smoking', 'tobacco'])

# coat
coat = 'M100 36 L128 76 L156 36 L192 52 Q208 60 208 76 L216 208 Q216 220 204 220 H52 Q40 220 40 208 L48 76 Q48 60 64 52 Z'
icon('coat', OB, ['coat', 'jacket', 'outerwear', 'winter'],
     line=[P(coat)], area=[P(coat)],
     detail=[L(128, 104, 128, 192), L(80, 92, 96, 124), L(176, 92, 160, 124)])

# coffin
cof = rpoly([(96, 32), (160, 32), (192, 88), (168, 224), (88, 224), (64, 88)], 12)
icon('coffin', OB, ['coffin', 'death', 'funeral', 'halloween'],
     line=[P(cof)], area=[P(cof)], detail=[L(128, 72, 128, 156), L(100, 100, 156, 100)])

# comb
spine = R(32, 64, 192, 56, 14)
icon('comb', OB, ['comb', 'hair', 'grooming', 'barber'],
     line=[spine] + [L(x, 120, x, 192) for x in (56, 92, 128, 164, 200)], area=[spine])

slashed(load('confetti'), 'confetti-slash', OB, ['confetti', 'disabled', 'off', 'objects'])

print(save(overwrite=True))
