"""Batch 08: weather variants, nature, health & science."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build  # boolean helpers (skia-pathops) for clipped duotone areas

W, N, H = 'Weather', 'Nature', 'Health'


# ---------------------------------------------------------------- helpers
def area_minus(shape_d, block_ds, margin):
    """Filled shape minus the blocking outlines grown by `margin` (as path data)."""
    grown = build.union(build.filled(block_ds), build.stroke(block_ds, 2 * margin))
    return build.to_d(build.difference(build.filled([shape_d]), grown))


def arc_pieces(c, r, a0, a1, blocked, step=0.25):
    """Angular runs (deg, increasing = clockwise) of circle (c, r) between a0..a1 not blocked."""
    def bis(lo, hi):  # lo is free, hi is blocked (or vice versa) -> boundary
        flo = blocked(polar(c, r, lo))
        for _ in range(40):
            mid = (lo + hi) / 2
            if blocked(polar(c, r, mid)) == flo:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    n = int((a1 - a0) / step)
    angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
    runs, start = [], None
    for i, a in enumerate(angs):
        free = not blocked(polar(c, r, a))
        if free and start is None:
            start = a0 if i == 0 else bis(angs[i - 1], a)
        if not free and start is not None:
            runs.append((start, bis(angs[i - 1], a)))
            start = None
    if start is not None:
        runs.append((start, a1))
    return runs


def arc_d(c, r, s, e):
    span = e - s
    return f'M{pt(polar(c, r, s))} A{f(r)} {f(r)} 0 {1 if span > 180 else 0} 1 {pt(polar(c, r, e))}'


def ell_d(cx, cy, rx, ry, deg):
    a = math.radians(deg)
    p1 = (cx + rx * math.cos(a), cy + rx * math.sin(a))
    p2 = (cx - rx * math.cos(a), cy - rx * math.sin(a))
    return f'M{pt(p1)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p2)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p1)} Z'


# Core cloud (00_core): three circles over a flat base at y=192.
CL = [((84, 152), 40), ((132, 116), 60), ((180, 148), 44)]


def cloud(s=1.0, tx=0.0, ty=0.0):
    (Lc, Lr), (Mc, Mr), (Rc, Rr) = [((c[0] * s + tx, c[1] * s + ty), r * s) for c, r in CL]
    base = 192 * s + ty
    irm = circle_x(Mc, Mr, Rc, Rr)[0]
    iml = circle_x(Mc, Mr, Lc, Lr)[0]
    d = (f'M{pt((Lc[0], base))} H{f(Rc[0])} ' + arc_to(Rc, Rr, (Rc[0], base), irm, lambda m: dist(m, Mc)) + ' ' +
         arc_to(Mc, Mr, irm, iml, lambda m: -m[1]) + ' ' +
         arc_to(Lc, Lr, iml, (Lc[0], base), lambda m: dist(m, Mc)) + ' Z')
    circles = [(Lc, Lr), (Mc, Mr), (Rc, Rr)]
    return d, circles, base


def in_cloud(p, circles, base, m):
    if any(dist(p, c) < r + m for c, r in circles):
        return True
    return circles[0][0][0] - m < p[0] < circles[2][0][0] + m and circles[1][0][1] < p[1] < base + m


def moon_d(c1, r1, c2, r2):
    p, q = circle_x(c1, r1, c2, r2)
    return (f'M{pt(p)} ' + arc_to(c1, r1, p, q, lambda m: dist(m, c2)) + ' ' +
            arc_to(c2, r2, q, p, lambda m: -dist(m, c1)) + ' Z')


# Cloud lifted and scaled for precipitation below: x 56..200, y 40..149.
CS, CTX, CTY = 0.8, 20.8, -4.8
cl_up, _, cl_base = cloud(CS, CTX, CTY)

# ---------------------------------------------------------------- Weather
icon('cloud-rain', W, ['rain', 'weather', 'shower', 'storm', 'wet'],
     line=[P(cl_up)] + [L(x, 180, x - 16, 212) for x in (96, 136, 176)], area=[P(cl_up)])

icon('cloud-snow', W, ['snow', 'weather', 'winter', 'cold', 'flurries'],
     line=[P(cl_up)], area=[P(cl_up)],
     dot=[C(80, 180, 14), C(128, 180, 14), C(176, 180, 14), C(104, 214, 14), C(152, 214, 14)])

icon('cloud-lightning', W, ['storm', 'thunder', 'weather', 'lightning', 'bolt'],
     line=[P(cl_up), PL([(140, 172), (116, 200), (144, 200), (124, 224)])], area=[P(cl_up)])

icon('cloud-fog', W, ['fog', 'mist', 'haze', 'weather', 'foggy'],
     line=[P(cl_up), L(56, 184, 200, 184), L(88, 216, 168, 216)], area=[P(cl_up)])

# Cloud in front of a sun / moon peeking out at the top left.
cl_lo, cl_lo_c, cl_lo_base = cloud(0.8, 36.8, 38.4)   # x 72..216, y 83..192
GAP = 24
blk = lambda p: in_cloud(p, cl_lo_c, cl_lo_base, GAP)
sc, sr = (100, 100), 32
sun_line = [arc_d(sc, sr, s, e) for s, e in arc_pieces(sc, sr, 45, 405, blk)]
rays = []
for a in range(0, 360, 45):
    p1, p2 = polar(sc, 52, a), polar(sc, 68, a)
    if not any(blk(((p1[0] * (1 - t) + p2[0] * t), (p1[1] * (1 - t) + p2[1] * t))) for t in (0, .5, 1)):
        rays.append(L(*p1, *p2))
sun_area = area_minus(f'M{sc[0] - sr} {sc[1]} A{sr} {sr} 0 1 1 {sc[0] + sr} {sc[1]} A{sr} {sr} 0 1 1 {sc[0] - sr} {sc[1]} Z',
                      [cl_lo], GAP)
icon('cloud-sun', W, ['partly cloudy', 'weather', 'sun', 'cloud', 'forecast'],
     line=[P(cl_lo)] + [P(d) for d in sun_line] + rays, area=[P(cl_lo), P(sun_area)])

mk = lambda c, s, o: (c[0] * s + o[0], c[1] * s + o[1])
ms, mo = 0.62, (14, 14)
m1, mr1, m2, mr2 = mk((120, 136), ms, mo), 88 * ms, mk((176, 84), ms, mo), 72 * ms
mp, mq = circle_x(m1, mr1, m2, mr2)
a_p = math.degrees(math.atan2(mp[1] - m1[1], mp[0] - m1[0]))
a_q = math.degrees(math.atan2(mq[1] - m1[1], mq[0] - m1[0]))
b_p = math.degrees(math.atan2(mp[1] - m2[1], mp[0] - m2[0]))
b_q = math.degrees(math.atan2(mq[1] - m2[1], mq[0] - m2[0]))
# outer arc goes the long way round c1 (from q clockwise to p); inner arc goes from p to q on c2.
o_s = a_q; o_e = a_p + (360 if a_p < a_q else 0)
i_s = b_p; i_e = b_q + (360 if b_q < b_p else 0)
if i_e - i_s > 180:  # inner arc is the short one nearest c1
    i_s, i_e = b_q, b_p + (360 if b_p < b_q else 0)
moon_line = ([arc_d(m1, mr1, s, e) for s, e in arc_pieces(m1, mr1, o_s, o_e, blk)] +
             [arc_d(m2, mr2, s, e) for s, e in arc_pieces(m2, mr2, i_s, i_e, blk)])
moon_area = area_minus(moon_d(m1, mr1, m2, mr2), [cl_lo], GAP)
icon('cloud-moon', W, ['night', 'cloudy', 'weather', 'moon', 'forecast'],
     line=[P(cl_lo)] + [P(d) for d in moon_line], area=[P(cl_lo), P(moon_area)])

hc = (128, 172)
icon('sun-horizon', W, ['sunrise', 'sunset', 'dawn', 'dusk', 'evening'],
     line=[P(f'M64 172 A64 64 0 0 1 192 172'), L(32, 172, 224, 172), L(88, 208, 168, 208)] +
          [L(*polar(hc, 84, a), *polar(hc, 104, a)) for a in (-150, -120, -90, -60, -30)],
     area=[P('M64 172 A64 64 0 0 1 192 172 Z')])

icon('sun-dim', W, ['brightness', 'dim', 'low light', 'display'],
     line=[C(128, 128, 44)], area=[C(128, 128, 44)],
     dot=[C(*polar((128, 128), 84, a), 16) for a in range(0, 360, 45)])

ms2, mo2 = 0.78, (8, 32)
n1, nr1, n2, nr2 = mk((120, 136), ms2, mo2), 88 * ms2, mk((176, 84), ms2, mo2), 72 * ms2
mn = moon_d(n1, nr1, n2, nr2)
spark = lambda cx, cy, r: (f'M{f(cx)} {f(cy - r)} C{f(cx + r * .12)} {f(cy - r * .12)} {f(cx + r * .12)} {f(cy - r * .12)} {f(cx + r)} {f(cy)} '
                           f'C{f(cx + r * .12)} {f(cy + r * .12)} {f(cx + r * .12)} {f(cy + r * .12)} {f(cx)} {f(cy + r)} '
                           f'C{f(cx - r * .12)} {f(cy + r * .12)} {f(cx - r * .12)} {f(cy + r * .12)} {f(cx - r)} {f(cy)} '
                           f'C{f(cx - r * .12)} {f(cy - r * .12)} {f(cx - r * .12)} {f(cy - r * .12)} {f(cx)} {f(cy - r)} Z')
st = spark(180, 76, 36)
icon('moon-stars', W, ['night', 'sleep', 'evening', 'stars', 'dark'],
     line=[P(mn), P(st)], area=[P(mn), P(st)], dot=[C(212, 140, 12)])

rc = (128, 184)
icon('rainbow', W, ['weather', 'arc', 'colors', 'pride', 'spectrum'],
     line=[P('M32 184 A96 96 0 0 1 224 184'), P('M96 184 A32 32 0 0 1 160 184')],
     detail=[P('M64 184 A64 64 0 0 1 192 184')],
     area=[P('M32 184 A96 96 0 0 1 224 184 H160 A32 32 0 0 0 96 184 Z')])

canopy = 'M32 128 A96 96 0 0 1 224 128 A32 32 0 0 0 160 128 A32 32 0 0 0 96 128 A32 32 0 0 0 32 128 Z'
icon('umbrella', W, ['rain', 'protection', 'insurance', 'weather', 'cover'],
     line=[P(canopy), P('M128 96 V196 A20 20 0 0 1 88 196')], area=[P(canopy)])

tc = 112
th = (f'M{tc - 28} 140 V68 A28 28 0 0 1 {tc + 28} 68 V140 A44 44 0 1 1 {tc - 28} 140 Z')
icon('thermometer', W, ['temperature', 'heat', 'weather', 'fever', 'degrees'],
     line=[P(th), L(176, 64, 208, 64), L(176, 100, 208, 100), L(176, 136, 208, 136)],
     detail=[L(tc, 172, tc, 104)], area=[P(th)])

sf = []
for i in range(6):
    a = -90 + i * 60
    sf.append(L(128, 128, *polar((128, 128), 96, a)))
    base = polar((128, 128), 58, a)
    sf.append(PL([polar(base, 32, a - 45), base, polar(base, 32, a + 45)]))
icon('snowflake', W, ['snow', 'winter', 'cold', 'freeze', 'ice'], line=sf)

icon('wind', W, ['air', 'breeze', 'weather', 'blow', 'windy'],
     line=[P('M32 100 H152 A28 28 0 1 0 124 72'), P('M32 140 H188 A28 28 0 1 1 160 168'),
           L(32, 180, 120, 180)])

icon('tornado', W, ['storm', 'twister', 'cyclone', 'weather', 'hurricane'],
     line=[L(32, 48, 224, 48), L(56, 88, 200, 88), L(88, 128, 184, 128), L(104, 168, 168, 168), L(120, 208, 152, 208)])


def wave(y, x0=32, x1=224, amp=24, per=64):
    d = f'M{x0} {y}'
    x, up = x0, True
    while x < x1 - 1:
        d += f' Q{f(x + per / 4)} {f(y - amp if up else y + amp)} {f(x + per / 2)} {y}'
        x += per / 2; up = not up
    return d
icon('waves', W, ['water', 'ocean', 'sea', 'beach', 'swim'],
     line=[P(wave(76, amp=16)), P(wave(128, amp=16)), P(wave(180, amp=16))])

# ---------------------------------------------------------------- Nature
flame = ('M128 224 C88 224 56 196 56 152 C56 104 100 84 112 32 C144 56 164 84 164 116 '
         'C176 108 184 96 186 84 C196 104 200 128 200 152 C200 196 168 224 128 224 Z')
icon('fire', N, ['flame', 'hot', 'burn', 'trending', 'heat'],
     line=[P(flame)], detail=[P('M104 168 C104 148 120 136 128 116 C136 136 152 148 152 168 A24 24 0 0 1 104 168 Z')],
     area=[P(flame)])

icon('tree', N, ['nature', 'forest', 'park', 'plant', 'environment'],
     line=[C(128, 108, 76), L(128, 184, 128, 224)],
     detail=[L(128, 184, 128, 124), L(128, 154, 100, 126)], area=[C(128, 108, 76)])

pine = [(128, 32), (188, 112), (160, 112), (208, 176), (48, 176), (96, 112), (68, 112)]
icon('tree-evergreen', N, ['pine', 'christmas', 'forest', 'nature', 'fir'],
     line=[PG(pine), L(128, 176, 128, 224)], area=[PG(pine)])

leaf = 'M56 200 C48 112 104 48 216 40 C224 144 160 208 56 200 Z'
icon('leaf', N, ['nature', 'eco', 'green', 'plant', 'organic'],
     line=[P(leaf), L(32, 224, 56, 200)], detail=[L(56, 200, 168, 88)], area=[P(leaf)])

fc, fn, fR, fr = (128, 102), 6, 40, 30
pc = [polar(fc, fR, -90 + i * 360 / fn) for i in range(fn)]
fd = ''
for i in range(fn):
    a, b, cprev = pc[i], pc[(i + 1) % fn], pc[i - 1]
    s = circle_x(a, fr, cprev, fr); s = max(s, key=lambda p: dist(p, fc))
    e = circle_x(a, fr, b, fr); e = max(e, key=lambda p: dist(p, fc))
    if not fd:
        fd = f'M{pt(s)}'
    fd += ' ' + arc_to(a, fr, s, e, lambda m, a=a: dist(m, fc))
fd += ' Z'
stem_leaf = 'M128 204 C128 180 148 168 176 168 C176 192 156 204 128 204 Z'
icon('flower', N, ['nature', 'garden', 'spring', 'bloom', 'plant'],
     line=[P(fd), L(128, 172, 128, 224), P(stem_leaf)], detail=[C(*fc, 20)], area=[P(fd), P(stem_leaf)])

lf1 = 'M128 168 C128 128 104 104 56 104 C56 144 80 168 128 168 Z'
lf2 = 'M128 128 C128 80 152 56 208 56 C208 104 184 128 128 128 Z'
icon('plant', N, ['sprout', 'seedling', 'grow', 'nature', 'eco'],
     line=[L(128, 216, 128, 128), P(lf1), P(lf2), L(72, 216, 184, 216)], area=[P(lf1), P(lf2)])

cactus = ('M104 216 V172 H54 A18 18 0 0 1 36 154 V100 A18 18 0 0 1 72 100 V136 H104 V64 A24 24 0 0 1 152 64 '
          'V100 H184 V76 A18 18 0 0 1 220 76 V118 A18 18 0 0 1 202 136 H152 V216 Z')
icon('cactus', N, ['desert', 'plant', 'succulent', 'nature', 'dry'],
     line=[P(cactus), L(64, 216, 192, 216)], area=[P(cactus)])

pc0, prr, rrx, rry, rdeg = (128, 128), 60, 100, 28, -25
ct2 = (prr ** 2 - rry ** 2) / (rrx ** 2 - rry ** 2)
t0 = math.degrees(math.acos(math.sqrt(ct2)))
def rpt(t):
    t, a = math.radians(t), math.radians(rdeg)
    x, y = rrx * math.cos(t), rry * math.sin(t)
    return (pc0[0] + x * math.cos(a) - y * math.sin(a), pc0[1] + x * math.sin(a) + y * math.cos(a))
ra = lambda t1, t2: f'M{pt(rpt(t1))} A{rrx} {rry} {rdeg} 0 1 {pt(rpt(t2))}'
icon('planet', N, ['space', 'saturn', 'astronomy', 'orbit', 'universe'],
     line=[C(*pc0, prr), P(ra(-t0, t0)), P(ra(180 - t0, 180 + t0))],
     detail=[P(ra(t0, 180 - t0))], area=[C(*pc0, prr)])

pad = 'M128 128 C152 128 184 164 184 188 C184 208 170 216 156 212 C146 209 138 206 128 206 C118 206 110 209 100 212 C86 216 72 208 72 188 C72 164 104 128 128 128 Z'
toes = [ell_d(54, 120, 18, 24, -24), ell_d(94, 64, 18, 24, -8), ell_d(162, 64, 18, 24, 8), ell_d(202, 120, 18, 24, 24)]
icon('paw-print', N, ['pet', 'dog', 'cat', 'animal', 'paw'],
     line=[P(pad)] + [P(t) for t in toes], area=[P(pad)] + [P(t) for t in toes])

def circ(c, r):
    return f'M{f(c[0] - r)} {f(c[1])} A{f(r)} {f(r)} 0 1 1 {f(c[0] + r)} {f(c[1])} A{f(r)} {f(r)} 0 1 1 {f(c[0] - r)} {f(c[1])} Z'
def union_d(ds):
    return build.to_d(build.filled(ds))
bird = union_d([circ((160, 88), 36), circ((124, 148), 60), 'M36 100 L100 112 L84 172 Z'])
icon('bird', N, ['animal', 'tweet', 'nature', 'wildlife', 'pet'],
     line=[P(bird), PG([(194, 78), (216, 94), (192, 104)])],
     detail=[P('M84 144 C100 176 132 180 156 160')], area=[P(bird)], dotcut=[C(166, 82, 12)])

fish = 'M40 128 C72 72 144 64 176 112 L216 80 V176 L176 144 C144 192 72 184 40 128 Z'
icon('fish', N, ['animal', 'sea', 'seafood', 'fishing', 'aquarium'],
     line=[P(fish)], detail=[P('M124 108 C134 120 134 136 124 148')], area=[P(fish)], dotcut=[C(84, 120, 12)])

up_w = 'M128 128 C132 84 164 48 196 48 C220 48 228 72 220 96 C212 120 176 132 128 136 Z'
lo_w = 'M128 136 C168 140 188 160 188 184 C188 208 164 216 148 200 C136 188 128 168 128 136 Z'


def mirror_d(d):
    import re
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    out, cmd, i, k = [], None, 0, 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; out.append(t); i += 1; k = 0; continue
        if cmd in 'MLCQT':
            v = float(t)
            out.append(f(256 - v) if k % 2 == 0 else f(v)); k += 1
        elif cmd == 'H':
            out.append(f(256 - float(t)))
        else:
            out.append(t)
        i += 1
    return ' '.join(out)
wings = [up_w, lo_w, mirror_d(up_w), mirror_d(lo_w)]
icon('butterfly', N, ['insect', 'nature', 'spring', 'garden', 'wings'],
     line=[P(w) for w in wings] + [L(128, 104, 128, 200), P('M128 104 C124 76 112 60 100 52'),
                                   P('M128 104 C132 76 144 60 156 52')],
     area=[P(w) for w in wings])

vane = 'M80 176 C64 128 92 72 136 52 L148 72 L156 44 C176 38 196 36 216 40 C220 80 208 112 184 136 L152 132 L168 152 C144 176 108 188 80 176 Z'
icon('feather', N, ['quill', 'light', 'write', 'bird', 'soft'],
     line=[P(vane), L(36, 220, 80, 176)], detail=[L(80, 176, 168, 88)], area=[P(vane)])

egg = 'M128 32 C172 32 200 108 200 148 A72 72 0 0 1 56 148 C56 108 84 32 128 32 Z'
icon('egg', N, ['easter', 'food', 'breakfast', 'nature', 'birth'], line=[P(egg)], area=[P(egg)])

# ---------------------------------------------------------------- Health
cross = [(100, 40), (156, 40), (156, 100), (216, 100), (216, 156), (156, 156), (156, 216), (100, 216),
         (100, 156), (40, 156), (40, 100), (100, 100)]
icon('first-aid', H, ['medical', 'health', 'hospital', 'cross', 'emergency'], line=[PG(cross)], area=[PG(cross)])

icon('first-aid-kit', H, ['medical', 'emergency', 'health', 'kit', 'doctor'],
     line=[R(32, 72, 192, 144, 16), P('M96 72 V56 A16 16 0 0 1 112 40 H144 A16 16 0 0 1 160 56 V72')],
     detail=[L(128, 116, 128, 172), L(100, 144, 156, 144)], area=[R(32, 72, 192, 144, 16)])

ud = (1 / math.sqrt(2), -1 / math.sqrt(2))
pill = capsule((128, 128), 56, 40, ud)
icon('pill', H, ['medicine', 'drug', 'capsule', 'pharmacy', 'tablet'],
     line=[P(pill)], detail=[L(128 - 40 * ud[1] * -1, 128 - 40 * ud[0], 128 + 40 * ud[1] * -1, 128 + 40 * ud[0])],
     area=[P(pill)])

sy = lambda pts: rot(pts, -45)
barrel = [(60, 96), (168, 96), (168, 160), (60, 160)]
icon('syringe', H, ['vaccine', 'injection', 'medical', 'needle', 'shot'],
     line=[PG(sy(barrel)), PL(sy([(60, 128), (20, 128)])), PL(sy([(168, 128), (216, 128)])),
           PL(sy([(216, 96), (216, 160)]))],
     detail=[PL(sy([(96, 96), (96, 124)])), PL(sy([(132, 96), (132, 124)]))],
     area=[PG(sy(barrel))])

icon('stethoscope', H, ['doctor', 'medical', 'health', 'checkup', 'heartbeat'],
     line=[P('M64 40 V96 A36 36 0 0 0 136 96 V40'), P('M100 132 V168 A46 46 0 0 0 192 168 V136'),
           C(192, 112, 24)],
     area=[C(192, 112, 24)], dot=[C(64, 40, 14), C(136, 40, 14)])

heart = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
icon('heartbeat', H, ['pulse', 'health', 'cardio', 'heart rate', 'vital'],
     line=[P(heart)], detail=[PL([(64, 136), (96, 136), (112, 108), (136, 164), (152, 136), (192, 136)])],
     area=[P(heart)])

s1 = 'M80 32 C80 80 176 80 176 128 C176 176 80 176 80 224'
s2 = 'M176 32 C176 80 80 80 80 128 C80 176 176 176 176 224'
icon('dna', H, ['genetics', 'helix', 'biology', 'science', 'gene'],
     line=[P(s1), P(s2), L(104, 112, 152, 112), L(104, 144, 152, 144)])

vc = (128, 128)
icon('virus', H, ['bacteria', 'germ', 'covid', 'infection', 'disease'],
     line=[C(*vc, 60)] + [L(*polar(vc, 60, a), *polar(vc, 76, a)) for a in range(0, 360, 45)],
     area=[C(*vc, 60)], dot=[C(*polar(vc, 86, a), 16) for a in range(0, 360, 45)],
     dotcut=[C(108, 116, 12), C(148, 144, 12), C(144, 104, 9)])

tube = 'M96 40 V180 A32 32 0 0 0 160 180 V40'
icon('test-tube', H, ['science', 'lab', 'chemistry', 'experiment', 'sample'],
     line=[P(tube), L(80, 40, 176, 40), L(96, 124, 160, 124)],
     area=[P('M96 124 V180 A32 32 0 0 0 160 180 V124 Z')])

flask = 'M104 40 V100 L44 192 C36 204 44 216 60 216 H196 C212 216 220 204 212 192 L152 100 V40'
lx = lambda y: 104 - 60 * (y - 100) / 92
icon('flask', H, ['science', 'lab', 'chemistry', 'experiment', 'beaker'],
     line=[P(flask), L(88, 40, 168, 40), L(lx(152), 152, 256 - lx(152), 152)],
     area=[P(f'M{f(lx(152))} 152 L44 192 C36 204 44 216 60 216 H196 C212 216 220 204 212 192 L{f(256 - lx(152))} 152 Z')])

ta, tb, tw = (84, 46), (120, 120), 20
tl_ = dist(ta, tb); tu = ((tb[0] - ta[0]) / tl_, (tb[1] - ta[1]) / tl_); tn = (-tu[1] * tw, tu[0] * tw)
mt = [(ta[0] + tn[0], ta[1] + tn[1]), (tb[0] + tn[0], tb[1] + tn[1]), (tb[0] - tn[0], tb[1] - tn[1]), (ta[0] - tn[0], ta[1] - tn[1])]
icon('microscope', H, ['science', 'lab', 'research', 'biology', 'magnify'],
     line=[PG(mt), L(48, 216, 208, 216), P('M136 78 A69 69 0 0 1 128 216'), L(64, 164, 148, 164)],
     area=[PG(mt)])

icon('atom', H, ['science', 'physics', 'nuclear', 'energy', 'react'],
     line=[P(ell_d(128, 128, 96, 36, a)) for a in (0, 60, 120)], dot=[C(128, 128, 16)])

band = capsule((128, 128), 60, 44, ud)
icon('bandaids', H, ['bandage', 'first aid', 'injury', 'plaster', 'heal'],
     line=[P(band)],
     detail=[L(*[v for t in (-34,) for v in (128 + t * ud[0] + 44 * ud[1], 128 + t * ud[1] - 44 * ud[0])],
               *[v for t in (-34,) for v in (128 + t * ud[0] - 44 * ud[1], 128 + t * ud[1] + 44 * ud[0])]),
             L(*[v for t in (34,) for v in (128 + t * ud[0] + 44 * ud[1], 128 + t * ud[1] - 44 * ud[0])],
               *[v for t in (34,) for v in (128 + t * ud[0] - 44 * ud[1], 128 + t * ud[1] + 44 * ud[0])])],
     area=[P(band)], dotcut=[C(128, 128, 12)])

tooth = ('M72 48 C96 40 112 56 128 56 C144 56 160 40 184 48 C216 60 212 112 196 136 C184 156 184 216 164 216 '
         'C144 216 148 160 128 160 C108 160 112 216 92 216 C72 216 72 156 60 136 C44 112 40 60 72 48 Z')
icon('tooth', H, ['dental', 'dentist', 'teeth', 'health', 'mouth'], line=[P(tooth)], area=[P(tooth)])

# Bone: drawn horizontally then turned 45 degrees.
kx, ky, kr, sh = 72, 22, 26, 20
kt, kb = (128 - kx, 128 - ky), (128 - kx, 128 + ky)
kt2, kb2 = (128 + kx, 128 - ky), (128 + kx, 128 + ky)
def on_circle_y(c, r, y, side):
    return (c[0] + side * math.sqrt(r * r - (y - c[1]) ** 2), y)
tl = on_circle_y(kt, kr, 128 - sh, 1); bl = on_circle_y(kb, kr, 128 + sh, 1)
tr = on_circle_y(kt2, kr, 128 - sh, -1); br = on_circle_y(kb2, kr, 128 + sh, -1)
nl = circle_x(kt, kr, kb, kr); nl = min(nl, key=lambda p: p[0])
nr = circle_x(kt2, kr, kb2, kr); nr = max(nr, key=lambda p: p[0])
far = lambda c: (lambda m: dist(m, (128, 128)))
bone = (f'M{pt(tl)} H{f(tr[0])} ' + arc_to(kt2, kr, tr, nr, far(kt2)) + ' ' + arc_to(kb2, kr, nr, br, far(kb2)) +
        f' H{f(bl[0])} ' + arc_to(kb, kr, bl, nl, far(kb)) + ' ' + arc_to(kt, kr, nl, tl, far(kt)) + ' Z')
# rotate by wrapping in a transform-free path: rebuild with rotated points
def rot_path(d, deg):
    import re
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    out, i = [], 0
    cur = None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cur = t; out.append(t); i += 1; continue
        if cur in 'ML':
            x, y = float(toks[i]), float(toks[i + 1]); out.append(pt(rot([(x, y)], deg)[0])); i += 2
        elif cur == 'A':
            rx, ry, ang, la, sw, x, y = toks[i:i + 7]
            out.append(f'{rx} {ry} {f(float(ang) + deg)} {la} {sw} {pt(rot([(float(x), float(y))], deg)[0])}'); i += 7
        else:
            raise ValueError(cur)
    return ' '.join(out)
bone_h = bone.replace(f'H{f(tr[0])}', f'L{pt((tr[0], tr[1]))}').replace(f'H{f(bl[0])}', f'L{pt((bl[0], bl[1]))}')
bone_r = rot_path(bone_h, -45)
icon('bone', H, ['dog', 'pet', 'skeleton', 'treat', 'orthopedic'], line=[P(bone_r)], area=[P(bone_r)])

names = save(overwrite=True)
print(names)

# bounds check at regular weight
for n in names:
    roles, _, _ = build.load(os.path.join(build.ROOT, 'icons', n + '.svg'))
    p = build.union(build.stroke(roles['line'] + roles['detail'], 16), build.dots(roles['dot'], 16),
                    build.dots(roles['dotcut'], 16))
    b = p.bounds
    if b[0] < 23.9 or b[1] < 23.9 or b[2] > 232.1 or b[3] > 232.1:
        print('OUT OF BOUNDS', n, [round(v, 1) for v in b])
