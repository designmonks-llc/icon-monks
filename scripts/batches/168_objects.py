import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Objects'
SLASH = L(48, 48, 208, 208)


def rpoly(points, r=12, close=True):
    """Polygon with rounded corners (quadratic corners, radius ~r)."""
    n = len(points)
    if not close:
        raise ValueError
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        rr = r[i] if isinstance(r, (list, tuple)) else r
        d1, d2 = dist(p0, p1), dist(p1, p2)
        k1, k2 = min(rr, d1 / 2), min(rr, d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * k1 / d1, p1[1] + (p0[1] - p1[1]) * k1 / d1)
        b = (p1[0] + (p2[0] - p1[0]) * k2 / d2, p1[1] + (p2[1] - p1[1]) * k2 / d2)
        segs.append((a, p1, b))
    d = f'M{pt(segs[0][2])}'
    for a, c, b in segs[1:] + segs[:1]:
        d += f' L{pt(a)} Q{pt(c)} {pt(b)}'
    return d + ' Z'


def T(points, dx=0, dy=0):
    return [(x + dx, y + dy) for x, y in points]


def as_lines(name):
    """Base icon's strokes (line + detail) as plain lines, for slash variants."""
    g = load(name)
    return g['line'] + g['detail']


# ---------------------------------------------------------------- clothing
mit = ('M84 176 V156 C60 156 40 140 40 116 C40 100 52 92 64 96 C74 100 80 108 84 116 V96 '
       'A56 56 0 0 1 196 96 V176 Z')
mit_cuff = R(76, 176, 128, 48, 14)
icon('mitten', CAT, ['gloves', 'mittens', 'winter', 'clothing'],
     line=[P(mit), mit_cuff], area=[P(mit), mit_cuff], detail=[L(100, 176, 180, 176)])

pants = 'M64 32 H192 L212 224 H148 L128 104 L108 224 H44 Z'
icon('pants', CAT, ['trousers', 'jeans', 'clothing', 'pants'],
     line=[P(rpoly([(64, 32), (192, 32), (212, 224), (148, 224), (128, 104), (108, 224), (44, 224)], [8, 8, 8, 8, 4, 8, 8]))],
     area=[P(rpoly([(64, 32), (192, 32), (212, 224), (148, 224), (128, 104), (108, 224), (44, 224)], [8, 8, 8, 8, 4, 8, 8]))],
     detail=[L(92, 64, 164, 64)])

sh = rpoly([(60, 48), (196, 48), (220, 200), (148, 200), (128, 136), (108, 200), (36, 200)], [8, 8, 8, 8, 4, 8, 8])
icon('shorts', CAT, ['short pants', 'summer', 'clothing', 'shorts', 'pants'],
     line=[P(sh)], area=[P(sh)], detail=[L(92, 80, 164, 80)])

sk_band = R(80, 36, 96, 36, 10)
sk = rpoly([(84, 72), (172, 72), (216, 216), (40, 216)], 10)
icon('skirt', CAT, ['skirt', 'clothing', 'fashion', 'mini'],
     line=[sk_band, P(sk)], area=[sk_band, P(sk)],
     detail=[L(108, 108, 96, 184), L(148, 108, 160, 184)])

ls = ('M100 40 A28 28 0 0 0 156 40 L196 52 L224 180 L192 192 L168 116 V216 H88 V116 L64 192 L32 180 L60 52 Z')
icon('shirt-long-sleeve', CAT, ['long sleeve', 'shirt', 'clothing', 'top'], line=[P(ls)], area=[P(ls)])

sf_body = R(40, 64, 176, 160, 16)
icon('shirt-folded', CAT, ['folded shirt', 'laundry', 'clothing'],
     line=[sf_body, PL([(88, 64), (104, 36), (152, 36), (168, 64)])],
     area=[sf_body, PG([(88, 64), (104, 36), (152, 36), (168, 64)])],
     detail=[PL([(104, 36), (128, 92), (152, 36)]), L(128, 92, 128, 192)])

tie_knot = rpoly([(100, 36), (156, 36), (144, 80), (112, 80)], 8)
tie_blade = rpoly([(112, 80), (144, 80), (172, 184), (128, 224), (84, 184)], 8)
icon('necktie', CAT, ['tie', 'necktie', 'formal', 'business'],
     line=[P(tie_knot), P(tie_blade)], area=[P(tie_knot), P(tie_blade)])

scarf_band = 'M48 48 Q128 104 208 48 A12 12 0 0 1 224 60 V84 Q128 168 32 84 V60 A12 12 0 0 1 48 48 Z'
scarf_l = rpoly([(92, 112), (132, 120), (112, 196), (72, 184)], [4, 4, 8, 8])
scarf_r = rpoly([(140, 120), (180, 108), (188, 224), (144, 224)], [4, 4, 8, 8])
icon('scarf', CAT, ['winter', 'clothing', 'warm'],
     line=[P(scarf_band), P(scarf_l), P(scarf_r)], area=[P(scarf_band), P(scarf_l), P(scarf_r)],
     detail=[L(156, 184, 172, 184)])

sock = ('M84 32 H156 V128 L204 164 A36 36 0 0 1 160 220 L100 176 C90 168 84 156 84 140 Z')
icon('socks', CAT, ['socks', 'clothing', 'feet', 'laundry', 'sock'],
     line=[P(sock)], area=[P(sock)], detail=[L(108, 68, 132, 68)])

# shoes
shoe = ('M40 64 C64 64 72 104 112 104 L160 112 C204 120 224 140 224 164 V168 A16 16 0 0 1 208 184 H40 Z')
shoe_heel = R(40, 184, 56, 32, 8)
shoe_heel_p = 'M40 184 V208 A8 8 0 0 0 48 216 H88 A8 8 0 0 0 96 208 V184'
icon('shoe', CAT, ['shoe', 'dress shoe', 'footwear', 'formal'],
     line=[P(shoe), P(shoe_heel_p)], area=[P(shoe), shoe_heel],
     detail=[L(116, 136, 144, 140)])
icon('shoe-slash', CAT, ['shoe', 'off', 'disabled', 'hidden'],
     line=[P(shoe), P(shoe_heel_p), SLASH])

sl_sole = R(32, 168, 192, 40, 20)
sl_top = 'M84 168 C84 124 104 96 132 96 C172 96 204 128 212 168'
icon('slippers', CAT, ['slippers', 'flip flops', 'sandals', 'home'],
     line=[sl_sole, P(sl_top)], area=[sl_sole, P(sl_top + ' Z')], detail=[L(56, 188, 200, 188)])

sand = []
sand_det = []
for cx, cy in ((80, 116), (176, 140)):
    sand.append(E(cx, cy, 32, 84))
    sand_det.append(PL([(cx - 32, cy - 4), (cx, cy - 48), (cx + 32, cy - 4)]))
icon('sandals', CAT, ['sandals', 'flip flops', 'footwear', 'summer'], line=sand, area=sand, detail=sand_det)

# ---------------------------------------------------------------- jewelry & beauty
gem = rpoly([(100, 148), (156, 148), (180, 176), (128, 224), (76, 176)], 6)
icon('necklace', CAT, ['necklace', 'jewelry', 'pendant', 'diamond'],
     line=[P('M52 32 C52 96 72 128 100 148'), P('M204 32 C204 96 184 128 156 148'), P(gem)],
     area=[P(gem)])

ring_gem = rpoly([(104, 32), (152, 32), (172, 56), (128, 96), (84, 56)], 6)
icon('ring', CAT, ['ring', 'wedding', 'engagement', 'jewelry', 'diamond ring'],
     line=[C(128, 160, 64), P(ring_gem)], area=[C(128, 160, 64), P(ring_gem)], hole=[C(128, 160, 40)])

np_body = R(60, 112, 136, 112, 28)
np_cap = R(104, 32, 48, 80, 12)
icon('nail-polish', CAT, ['nail polish', 'manicure', 'beauty', 'cosmetics'],
     line=[np_body, np_cap], area=[np_body, np_cap], detail=[L(96, 152, 96, 184)])

pf_body = R(40, 112, 160, 112, 28)
pf_cap = R(92, 64, 56, 48, 10)
icon('perfume', CAT, ['perfume', 'fragrance', 'scent', 'bottle', 'spray'],
     line=[pf_body, pf_cap, L(148, 80, 180, 80), C(200, 80, 20)],
     area=[pf_body, pf_cap, C(200, 80, 20)], detail=[L(92, 168, 148, 168)])

pb_body = R(64, 112, 128, 112, 24)
pb_collar = R(104, 88, 48, 24, 6)
icon('pump-bottle', CAT, ['soap', 'lotion', 'pump', 'dispenser', 'soap dispenser'],
     line=[pb_body, P('M104 112 V96 A8 8 0 0 1 112 88 H144 A8 8 0 0 1 152 96 V112'), L(128, 88, 128, 56),
           PL([(96, 56), (176, 56), (176, 72)])],
     area=[pb_body, pb_collar], detail=[L(100, 168, 156, 168)])

rz_head = R(48, 40, 160, 56, 14)
rz_handle = R(112, 116, 32, 108, 16)
icon('razor', CAT, ['razor', 'shave', 'grooming', 'barber', 'blade'],
     line=[rz_head, L(128, 96, 128, 116), rz_handle], area=[rz_head, rz_handle], detail=[L(76, 68, 180, 68)])

br_top = 'M84 120 C76 72 100 36 128 36 C156 36 180 72 172 120 Z'
br_handle = 'M96 120 C96 152 72 168 72 196 A20 20 0 0 0 92 216 H164 A20 20 0 0 0 184 196 C184 168 160 152 160 120 Z'
icon('shaving-brush', CAT, ['brush', 'shaving', 'barber', 'grooming'],
     line=[P(br_top), P(br_handle)], area=[P(br_top), P(br_handle)], detail=[L(128, 68, 128, 92)])

# ---------------------------------------------------------------- sewing
ec = (176, 80); u = (math.sqrt(.5), -math.sqrt(.5))
eye = capsule(ec, 18, 18, u)
eb = (ec[0] - u[0] * 36, ec[1] - u[1] * 36)
icon('needle', CAT, ['needle', 'sewing', 'thread', 'stitch'],
     line=[P(eye), L(48, 208, eb[0], eb[1]),
           P('M176 80 C224 72 224 136 192 152 C164 166 172 204 212 212')])

sp_body = R(56, 64, 96, 128, 0)
icon('needle-thread', CAT, ['sewing', 'needle', 'thread', 'tailor'],
     line=[L(32, 48, 144, 48), L(32, 208, 144, 208), P('M56 48 V208'), P('M120 48 V208'),
           P('M120 168 C160 168 176 120 196 84'), P(capsule((204, 64), 12, 14, (0.24, -0.97))), L(*(204 - 0.24 * 26, 64 + 0.97 * 26), 188, 216)],
     area=[R(56, 48, 64, 160)], detail=[L(80, 96, 96, 96), L(80, 128, 96, 128), L(80, 160, 96, 160)])

sm = rpoly([(48, 56), (216, 56), (216, 184), (168, 184), (168, 104), (96, 104), (96, 136), (48, 136)], [16, 16, 4, 4, 12, 12, 8, 8])
sm_base = R(32, 184, 192, 32, 10)
icon('sewing-machine', CAT, ['sewing', 'tailor', 'machine', 'stitch'],
     line=[P(sm), sm_base, L(72, 136, 72, 164), L(120, 56, 120, 36)], area=[P(sm), sm_base],
     detail=[L(184, 80, 200, 80)])

# ---------------------------------------------------------------- tools
oil_body = R(40, 128, 128, 88, 16)
icon('oil-can', CAT, ['oil', 'lubricant', 'oil can', 'maintenance'],
     line=[oil_body, P('M80 128 V108 A8 8 0 0 1 88 100 H120 A8 8 0 0 1 128 108 V128'), L(168, 152, 216, 80)],
     area=[oil_body, R(80, 100, 48, 28, 8)],
     detail=[L(72, 172, 136, 172)],
     dot=[])
icon_drop = 'M212 120 C220 132 224 140 224 148 A12 12 0 0 1 200 148 C200 140 204 132 212 120 Z'
ICONS[-1]['line'].append(P(icon_drop)); ICONS[-1]['area'].append(P(icon_drop))

# pickaxe: crescent head + handle, rotated
A, B = (40, 104), (216, 104)
r1 = (88 ** 2 + 64 ** 2) / (2 * 64); r2 = (88 ** 2 + 32 ** 2) / (2 * 32)
deg = 35
Ar, Br = rot([A], deg)[0], rot([B], deg)[0]
head = f'M{pt(Ar)} A{f(r1)} {f(r1)} 0 0 1 {pt(Br)} A{f(r2)} {f(r2)} 0 0 0 {pt(Ar)} Z'
h1, h2 = rot([(128, 76), (128, 224)], deg)
icon('pickaxe', CAT, ['pickaxe', 'mining', 'dig', 'tool'], line=[P(head), L(*h1, *h2)], area=[P(head)])

# shovel
sh_blade = [(88, 124), (168, 124), (168, 176), (128, 224), (88, 176)]
deg = 40
blade = rot(sh_blade, deg)
bp = rot([(160, 180), (128, 220), (96, 180)], deg)
bd = rpoly(blade, [8, 8, 20, 6, 20])
g1, g2, s1, s2 = rot([(104, 36), (152, 36), (128, 36), (128, 124)], deg)
icon('shovel', CAT, ['shovel', 'dig', 'spade', 'garden'],
     line=[P(bd), L(*g1, *g2), L(*s1, *s2)], area=[P(bd)])

# saw
teeth = []
x = 216
y0, y1 = 148, 172
n = 5
pts_t = []
for i in range(n * 2 + 1):
    t = i / (n * 2)
    xx = 216 - t * (216 - 96)
    yy = 148 + t * (172 - 148) + (10 if i % 2 else 0)
    pts_t.append((xx, yy))
saw_blade = 'M96 76 L216 116 L216 148 ' + ' '.join('L' + pt(p) for p in pts_t[1:]) + ' Z'
saw_handle = R(32, 72, 64, 112, 20)
icon('saw', CAT, ['saw', 'carpenter', 'woodwork', 'tool'],
     line=[P(saw_blade), saw_handle, R(52, 100, 24, 56, 12)], area=[P(saw_blade), saw_handle], hole=[R(52, 100, 24, 56, 12)])

# pliers
pl_l = 'M100 36 C96 68 104 92 128 112 C152 136 164 176 172 216'
pl_r = 'M156 36 C160 68 152 92 128 112 C104 136 92 176 84 216'
icon('pliers', CAT, ['pliers', 'wire stripper', 'tool', 'grip'],
     line=[P(pl_l), P(pl_r), P(capsule((160, 172), 28, 18, (0.27, 0.96))), P(capsule((96, 172), 28, 18, (-0.27, 0.96)))],
     area=[P(capsule((160, 172), 28, 18, (0.27, 0.96))), P(capsule((96, 172), 28, 18, (-0.27, 0.96)))],
     dotcut=[C(128, 112, 8)])

# pocket knife
pk_body = R(32, 144, 192, 56, 28)
pk_blade = 'M64 144 L48 56 C96 72 124 104 128 144'
icon('pocket-knife', CAT, ['swiss army knife', 'multitool', 'camping', 'blade'],
     line=[pk_body, P(pk_blade), L(184, 144, 208, 64)], area=[pk_body, P(pk_blade + ' Z')],
     dotcut=[C(64, 172, 12), C(192, 172, 12)])

# screw
icon('screw', CAT, ['screw', 'hardware', 'fastener', 'diy'],
     line=[R(68, 32, 120, 36, 12), P(rpoly([(100, 68), (156, 68), (156, 176), (128, 220), (100, 176)], [4, 4, 8, 6, 8]))],
     area=[R(68, 32, 120, 36, 12), P(rpoly([(100, 68), (156, 68), (156, 176), (128, 220), (100, 176)], [4, 4, 8, 6, 8]))],
     detail=[L(100, 112, 156, 96), L(100, 148, 156, 132)])

# spirit level
icon('spirit-level', CAT, ['level', 'bubble level', 'tool', 'straight', 'spirit level'],
     line=[R(32, 80, 192, 96, 16)], area=[R(32, 80, 192, 96, 16)],
     detail=[R(72, 108, 112, 40, 20)], dotcut=[C(128, 128, 10)])

# stapler
st = rpoly([(40, 184), (40, 108), (192, 88), (216, 104), (216, 148), (96, 152), (96, 184)], [8, 24, 16, 16, 12, 8, 4])
st_base = R(32, 184, 192, 32, 12)
icon('stapler', CAT, ['stapler', 'office', 'staples', 'paper'], line=[P(st), st_base], area=[P(st), st_base],
     detail=[L(72, 128, 168, 116)])

# ---------------------------------------------------------------- toys & games
icon('paper-boat', CAT, ['paper boat', 'origami', 'toy', 'boat'],
     line=[P(rpoly([(32, 136), (224, 136), (188, 200), (68, 200)], 8)), P(rpoly([(76, 136), (128, 44), (180, 136)], 8))],
     area=[P(rpoly([(32, 136), (224, 136), (188, 200), (68, 200)], 8)), P(rpoly([(76, 136), (128, 44), (180, 136)], 8))],
     detail=[L(128, 96, 128, 168)])

pen = rpoly([(56, 44), (208, 92), (56, 140)], [4, 10, 4])
icon('pennant', CAT, ['pennant', 'flag', 'team', 'banner', 'triangular flag'],
     line=[L(56, 32, 56, 224), P(pen)], area=[P(pen)])
icon('pennant-slash', CAT, ['pennant', 'off', 'disabled', 'hidden'],
     line=[L(56, 32, 56, 224), P(pen), SLASH])

# pinwheel
pc = (120, 104)
blades = []
for i in range(4):
    th = -90 + i * 90 + 20
    tip = polar(pc, 76, th)
    back = polar(pc, 44, th + 70)
    ctrl = polar(pc, 84, th + 45)
    blades.append(P(f'M{pt(pc)} L{pt(tip)} Q{pt(ctrl)} {pt(back)} Z'))
icon('pinwheel', CAT, ['pinwheel', 'toy', 'wind', 'spin'],
     line=blades + [L(120, 172, 152, 224)], area=blades)

card = R(56, 32, 144, 192, 16)
diamond_pip = PG([(128, 92), (156, 128), (128, 164), (100, 128)])
icon('playing-card', CAT, ['playing card', 'cards', 'poker', 'game'], line=[card], area=[card], detail=[diamond_pip])
icon('playing-card-ace', CAT, ['ace', 'card', 'poker', 'game'], line=[card], area=[card],
     detail=[PL([(100, 132), (128, 68), (156, 132)]), L(110, 110, 146, 110), PG([(128, 160), (146, 180), (128, 200), (110, 180)])])
icon('playing-card-slash', CAT, ['playing card', 'off', 'disabled', 'hidden', 'playing'],
     line=[card, diamond_pip, SLASH])

# two fanned cards: back card rotated, front card upright; back card clipped where the front covers it
def rrect_pts(x, y, w, h, r, step=6):
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(0, 91, step):
            pts.append(polar((cx, cy), r, a0 + k))
    dense = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n = max(1, int(dist(p, q) // 4))
        dense += [(p[0] + (q[0] - p[0]) * t / n, p[1] + (q[1] - p[1]) * t / n) for t in range(n)]
    return dense


def visible_runs(pts, inside):
    runs, cur = [], []
    n = len(pts)
    start = next(i for i in range(n) if inside(pts[i]))
    for j in range(1, n + 1):
        q = pts[(start + j) % n]
        if inside(q):
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append(q)
    if len(cur) > 1:
        runs.append(cur)
    out = []
    for r in runs:
        k = [r[0]]
        for i in range(1, len(r) - 1):
            a1 = math.atan2(r[i][1] - k[-1][1], r[i][0] - k[-1][0])
            a2 = math.atan2(r[i + 1][1] - r[i][1], r[i + 1][0] - r[i][0])
            if abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi) > 0.02:
                k.append(r[i])
        out.append(k + [r[-1]])
    return out


piv = (128, 232)
front_pts = rot(rrect_pts(76, 56, 104, 160, 14), 10, piv)
back = rot(rrect_pts(76, 56, 104, 160, 14), -14, piv)


def cover(q, m=18):
    x, y = rot([q], -10, piv)[0]
    return 76 - m < x < 180 + m and 56 - m < y < 216 + m


gap = rot(rrect_pts(76 - 18, 56 - 18, 104 + 36, 160 + 36, 28), 10, piv)
gap_in = rot(rrect_pts(76 - 8, 56 - 8, 104 + 16, 160 + 16, 20), 10, piv)[::-1]
icon('playing-cards', CAT, ['cards', 'poker', 'deck', 'game'],
     line=[PG(front_pts)] + [PL(r) for r in visible_runs(back, cover)],
     area=[PG(front_pts), PG(back)],
     detail=[PG(rot([(128, 104), (152, 136), (128, 168), (104, 136)], 10, piv))],
     hole=[P(poly(gap, True) + ' ' + poly(gap_in, True))])

chip_det = [C(128, 128, 44)]
for i in range(8):
    a = i * 45 + 22.5
    chip_det.append(L(*polar((128, 128), 72, a), *polar((128, 128), 96, a)))
icon('poker-chip', CAT, ['casino', 'chip', 'gambling', 'bet', 'poker chip'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], detail=chip_det)

rl_det = [C(128, 128, 56), L(128, 102, 128, 154), L(102, 128, 154, 128)]
icon('roulette', CAT, ['roulette', 'casino', 'gambling', 'wheel'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], detail=rl_det)

top_body = 'M128 64 C176 64 216 88 216 112 C216 120 212 128 204 136 L136 212 A11 11 0 0 1 120 212 L52 136 C44 128 40 120 40 112 C40 88 80 64 128 64 Z'
icon('spinning-top', CAT, ['spinning top', 'toy', 'spin', 'game'],
     line=[P(top_body), L(128, 64, 128, 32)], area=[P(top_body)], detail=[L(72, 124, 184, 124)])

icon('stacking-rings', CAT, ['stacking toy', 'rings', 'baby toy', 'pyramid'],
     line=[R(40, 176, 176, 40, 20), R(64, 136, 128, 40, 20), R(88, 96, 80, 40, 20), L(128, 96, 128, 64), L(96, 216, 160, 216)],
     area=[R(40, 176, 176, 40, 20), R(64, 136, 128, 40, 20), R(88, 96, 80, 40, 20)], dot=[C(128, 52, 16)], detail=[L(84, 176, 172, 176), L(108, 136, 148, 136)])
ICONS[-1]['line'] = ICONS[-1]['line'][:4]

track = 'M32 184 C64 184 64 96 104 96 C144 96 144 160 172 160 C196 160 204 128 224 128'
car = R(76, 56, 56, 40, 10)
icon('rollercoaster', CAT, ['rollercoaster', 'amusement park', 'ride', 'fun'],
     line=[P(track), L(104, 64, 104, 216), L(168, 152, 168, 216), L(32, 216, 224, 216), L(56, 156, 56, 216), L(216, 116, 216, 216)])
ICONS[-1]['line'] = [P(track), car, L(104, 128, 104, 216), L(172, 192, 172, 216), L(32, 216, 224, 216)]
ICONS[-1]['area'] = [car]
icon('rollercoaster-slash', CAT, ['rollercoaster', 'off', 'disabled', 'hidden'],
     line=[P(track), car, L(104, 128, 104, 216), L(172, 192, 172, 216), L(32, 216, 224, 216), SLASH])

# ---------------------------------------------------------------- misc
dome = 'M48 176 A80 80 0 0 1 208 176 Z'
icon('service-bell', CAT, ['concierge', 'hotel bell', 'reception', 'service', 'service bell'],
     line=[P(dome), R(32, 176, 192, 32, 12), L(128, 96, 128, 72), L(104, 64, 152, 64)],
     area=[P(dome), R(32, 176, 192, 32, 12)], detail=[P('M84 152 A48 48 0 0 1 104 120')])

sc = (128, 140)
siren_dome = f'M76 176 V{sc[1]} A52 52 0 0 1 180 {sc[1]} V176'
icon('siren', CAT, ['alarm', 'warning light', 'emergency', 'beacon', 'siren'],
     line=[P(siren_dome), R(56, 176, 144, 40, 12), L(128, 32, 128, 52),
           L(*polar(sc, 80, -40), *polar(sc, 100, -40)), L(*polar(sc, 80, -140), *polar(sc, 100, -140))],
     area=[P(siren_dome + ' Z'), R(56, 176, 144, 40, 12)], detail=[P('M104 156 V140 A24 24 0 0 1 128 116')])

# slash variants of existing icons
icon('puzzle-piece-slash', CAT, ['puzzle piece', 'off', 'disabled', 'hidden', 'puzzle'], line=as_lines('puzzle-piece') + [SLASH])
icon('ruler-slash', CAT, ['ruler', 'off', 'disabled', 'hidden'], line=as_lines('ruler') + [SLASH])
icon('scales-slash', CAT, ['scales', 'off', 'disabled', 'hidden'], line=as_lines('scales') + [SLASH])
icon('scissors-slash', CAT, ['scissors', 'off', 'disabled', 'hidden'], line=as_lines('scissors') + [SLASH])

print(save(overwrite=True))
