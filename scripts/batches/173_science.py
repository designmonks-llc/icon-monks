import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

S = 'Science'
SLASH = L(48, 48, 208, 208)


def rpoly(points, r):
    """Closed polygon with rounded corners of radius r (circular arcs)."""
    n = len(points)
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1]); v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1); u2 = (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        d = min(r / math.tan(ang / 2), l1 / 2, l2 / 2)
        rr = d * math.tan(ang / 2)
        a = (p1[0] + u1[0] * d, p1[1] + u1[1] * d); b = (p1[0] + u2[0] * d, p1[1] + u2[1] * d)
        cross = u1[0] * u2[1] - u1[1] * u2[0]
        segs.append((a, b, rr, 1 if cross < 0 else 0))
    dd = f'M{pt(segs[0][1])}'
    for a, b, rr, sw in segs[1:] + segs[:1]:
        dd += f' L{pt(a)} A{f(rr)} {f(rr)} 0 0 {sw} {pt(b)}'
    return dd + ' Z'


def lines_only(parts):
    """Slash variant: everything stroked becomes line, dots stay dots, no area."""
    return dict(line=parts.get('line', []) + parts.get('detail', []) + [SLASH],
                dot=parts.get('dot', []) + parts.get('dotcut', []))


# ================================================================ logic gates (match logic-and / logic-nand)
def or_body(bx, tx, bulge=44):
    w = tx - bx
    top = f'M{f(bx)} 64 C{f(bx + 0.55 * w)} 64 {f(tx - 0.22 * w)} 84 {f(tx)} 128'
    bot = f' C{f(tx - 0.22 * w)} 172 {f(bx + 0.55 * w)} 192 {f(bx)} 192'
    back = f' Q{f(bx + bulge)} 128 {f(bx)} 64 Z'
    return top + bot + back


def back_x(bx, bulge=44, y=96):
    t = (y - 64) / 128
    return bx + 2 * bulge * t * (1 - t)


def gate(name, tags, bx, tx, bubble=False, extra=None):
    body = or_body(bx, tx)
    line = [P(body)]
    area = [P(body)]
    x_in = back_x(bx) if extra is None else back_x(extra)
    line += [L(32, 96, x_in, 96), L(32, 160, x_in, 160)]
    if extra is not None:
        line.append(P(f'M{f(extra)} 64 Q{f(extra + 44)} 128 {f(extra)} 192'))
    if bubble:
        line += [C(tx + 18, 128, 18), L(tx + 36, 128, 224, 128)]
        area.append(C(tx + 18, 128, 18))
    else:
        line.append(L(tx, 128, 224, 128))
    icon(name, S, tags, line=line, area=area)


gate('logic-or', ['or gate', 'logic', 'circuit', 'boolean'], 72, 192)
gate('logic-nor', ['nor gate', 'logic', 'circuit', 'boolean'], 56, 176, bubble=True)
gate('logic-xor', ['xor gate', 'logic', 'circuit', 'boolean'], 84, 192, extra=48)
gate('logic-xnor', ['xnor gate', 'logic', 'circuit', 'boolean'], 76, 176, bubble=True, extra=40)

tri = 'M56 64 L168 128 L56 192 Z'
icon('logic-not', S, ['not gate', 'inverter', 'logic', 'circuit'],
     line=[P(tri), C(186, 128, 18), L(32, 128, 56, 128), L(204, 128, 224, 128)],
     area=[P(tri), C(186, 128, 18)])

# ================================================================ magnet
mag = load('magnet')
icon('magnet-slash', S, ['magnet', 'off', 'disabled', 'hidden'], **lines_only(mag))

# magnetic field: horseshoe magnet, field lines arcing from pole to pole above it
HS = 'M64 136 V160 A64 64 0 0 0 192 160 V136 H152 V160 A24 24 0 0 1 104 160 V136 Z'
icon('magnetic-field', S, ['magnetic field', 'magnet', 'physics', 'flux'],
     line=[P(HS), P('M84 108 A44 44 0 0 1 172 108'), P('M44 108 A84 76 0 0 1 212 108')],
     detail=[L(64, 172, 104, 172), L(152, 172, 192, 172)] if False else [],
     area=[P(HS)])

# ================================================================ math operations
MO = [L(80, 48, 80, 112), L(48, 80, 112, 80),          # plus
      L(144, 80, 208, 80),                             # minus
      L(56, 152, 104, 200), L(104, 152, 56, 200),      # times
      L(144, 176, 208, 176)]                           # divide bar
MO_DOT = [C(176, 144, 14), C(176, 208, 14)]
icon('math-operations', S, ['math', 'calculate', 'operators', 'plus minus', 'calculation'], line=MO, dot=MO_DOT)
icon('math-operations-slash', S, ['math operations', 'off', 'disabled', 'hidden', 'math'],
     line=MO + [SLASH], dot=MO_DOT)

# ================================================================ meteor
mc, mr = (92, 164), 50
u = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
nv = (-u[1], u[0])
rock = C(mc[0], mc[1], mr)
streaks = []
for o, s0, s1 in ((-34, 72, 128), (0, 80, 156), (34, 72, 112)):
    s0 = math.sqrt(mr * mr - o * o) + 24
    a = (mc[0] + u[0] * s0 + nv[0] * o, mc[1] + u[1] * s0 + nv[1] * o)
    b = (mc[0] + u[0] * s1 + nv[0] * o, mc[1] + u[1] * s1 + nv[1] * o)
    streaks.append(L(a[0], a[1], b[0], b[1]))
craters = [C(76, 176, 14), C(108, 148, 10)]
icon('meteor', S, ['meteor', 'comet', 'space', 'asteroid'], line=[rock] + streaks, area=[rock], dotcut=craters)
icon('meteor-slash', S, ['meteor', 'off', 'disabled', 'hidden'], line=[rock] + streaks + [SLASH], dot=craters)

icon('microscope-slash', S, ['microscope', 'off', 'disabled', 'hidden'], **lines_only(load('microscope')))

# ================================================================ nuclear plant
tower = 'M48 216 C80 168 80 136 68 100 H148 C136 136 136 168 168 216'
cloud = 'M80 80 H140 A20 20 0 0 0 144 40.4 A28 28 0 0 0 92 44 A18 18 0 0 0 80 80 Z'
dome = 'M184 216 V180 A20 20 0 0 1 224 180 V216'
icon('nuclear-plant', S, ['nuclear plant', 'power station', 'energy', 'cooling tower'],
     line=[P(tower), P(dome), L(32, 216, 224, 216), P(cloud)],
     area=[P(tower + ' Z'), P(dome + ' Z')])

# ================================================================ orbit / orbits / universe
oc = (128, 128)
moon_a, ro = -45, 92
g = 22
icon('orbit', S, ['orbit', 'planet', 'space', 'rotation'],
     line=[C(128, 128, 40),
           P(f'M{pt(polar(oc, ro, moon_a + g))} A{ro} {ro} 0 1 1 {pt(polar(oc, ro, moon_a - g))}')],
     area=[C(128, 128, 40)], dot=[C(*polar(oc, ro, moon_a), 20)])

def ell(rx, ry, deg, c=(128, 128)):
    p1 = polar(c, 1, deg); p1 = (c[0] + rx * math.cos(math.radians(deg)), c[1] + rx * math.sin(math.radians(deg)))
    p2 = (2 * c[0] - p1[0], 2 * c[1] - p1[1])
    return P(f'M{pt(p1)} A{rx} {ry} {deg} 1 1 {pt(p2)} A{rx} {ry} {deg} 1 1 {pt(p1)} Z')

icon('orbits', S, ['orbits', 'atom', 'solar system', 'rings'],
     line=[C(128, 128, 24), ell(96, 50, 30), ell(96, 50, -30)], area=[C(128, 128, 24)])

def ring_gaps(r, dots, gap):
    """Circle r around oc with gaps (degrees) around each dot angle."""
    ds = sorted(dots)
    out = []
    for i, d in enumerate(ds):
        nxt = ds[(i + 1) % len(ds)] + (360 if i == len(ds) - 1 else 0)
        a1, a2 = d + gap, nxt - gap
        span = a2 - a1
        out.append(P(f'M{pt(polar(oc, r, a1))} A{r} {r} 0 {1 if span > 180 else 0} 1 {pt(polar(oc, r, a2))}'))
    return out
uni_line = ring_gaps(52, [-60], 34) + ring_gaps(92, [20, 150], 20)
icon('universe', S, ['universe', 'cosmos', 'space', 'orbits'],
     line=uni_line,
     dot=[C(128, 128, 20), C(*polar(oc, 52, -60), 14), C(*polar(oc, 92, 150), 14), C(*polar(oc, 92, 20), 14)])

# ================================================================ parabola, pendulum, pi
icon('parabola', S, ['parabola', 'curve', 'quadratic', 'math'],
     line=[PL([(48, 40), (48, 208), (224, 208)]), P('M84 48 Q148 272 212 48')])

pv = (120, 40)
plen = 132
bob = polar(pv, plen, 68)
trail = [C(*polar(pv, plen, 104), 18), C(*polar(pv, plen, 127), 13)]
icon('pendulum', S, ['pendulum', 'physics', 'swing', 'motion'],
     line=[L(56, 40, 184, 40), L(pv[0], pv[1], *polar(pv, plen - 36, 68)), C(bob[0], bob[1], 36)],
     area=[C(bob[0], bob[1], 36)], dot=trail)

icon('pi', S, ['pi', 'math', 'constant', 'greek'],
     line=[P('M44 96 Q56 72 88 72 H212'), P('M104 72 Q104 164 76 204'), P('M164 72 V176 Q164 204 192 204')])

icon('planet-slash', S, ['planet', 'off', 'disabled', 'hidden'], **lines_only(load('planet')))

# ================================================================ potion
pc, pr = (128, 156), 64
ny = pc[1] - math.sqrt(pr * pr - 20 * 20)
bottle = f'M108 {f(ny)} V68 H148 V{f(ny)} A{pr} {pr} 0 1 1 108 {f(ny)} Z'
wy = 150
wx = math.sqrt(pr * pr - (wy - pc[1]) ** 2)
wave = f'M{f(pc[0] - wx)} {wy} Q{f(pc[0] - wx / 2)} {wy - 18} 128 {wy} T{f(pc[0] + wx)} {wy}'
liquid = wave + f' A{pr} {pr} 0 0 1 {f(pc[0] - wx)} {wy} Z'
icon('potion', S, ['elixir', 'magic', 'flask'],
     line=[P(bottle), R(100, 36, 56, 32, 8), P(wave)], area=[P(liquid)],
     dotcut=[C(106, 184, 14), C(152, 176, 11)])

# ================================================================ prism
PT = [(112, 56), (176, 176), (48, 176)]
pr_tri = rpoly(PT, 12)
def on(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
pin = on(PT[0], PT[2], 0.5)
rays = []
for t, ang in ((0.3, -4), (0.55, 16), (0.8, 36)):
    q = on(PT[0], PT[1], t)
    s0 = polar(q, 24, ang)
    e = s0
    while e[0] < 224 and e[1] < 216:
        e = polar(e, 1, ang)
    rays.append(L(s0[0], s0[1], e[0], e[1]))
pin2 = on(PT[0], PT[2], 0.6)
prism_line = [P(pr_tri), L(32, 140, pin2[0] - 4, pin2[1] + 1)] + rays
icon('prism', S, ['prism', 'optics', 'light', 'refraction'], line=prism_line, area=[P(pr_tri)])
icon('prism-slash', S, ['prism', 'off', 'disabled', 'hidden'], line=prism_line + [SLASH])

# ================================================================ radar
sweep_a = -45
sector = f'M128 128 L{pt(polar(oc, 96, sweep_a - 60))} A96 96 0 0 1 {pt(polar(oc, 96, sweep_a))} Z'
radar_line = [C(128, 128, 96), C(128, 128, 52), L(128, 128, *polar(oc, 96, sweep_a))]
icon('radar', S, ['radar', 'scan', 'sonar', 'detection', 'sweep'],
     line=radar_line, area=[P(sector)], dot=[C(128, 128, 16)])
icon('radar-slash', S, ['radar', 'off', 'disabled', 'hidden'], line=radar_line + [SLASH], dot=[C(128, 128, 16)])

# ================================================================ radioactive
def blade(mid, ri=40, ro=92, half=30):
    a1, a2 = mid - half, mid + half
    return (f'M{pt(polar(oc, ri, a1))} L{pt(polar(oc, ro, a1))} A{ro} {ro} 0 0 1 {pt(polar(oc, ro, a2))} '
            f'L{pt(polar(oc, ri, a2))} A{ri} {ri} 0 0 0 {pt(polar(oc, ri, a1))} Z')
blades = [P(blade(m)) for m in (-150, -30, 90)]
icon('radioactive', S, ['radioactive', 'radiation', 'nuclear', 'hazard'],
     line=blades, area=blades, dot=[C(128, 128, 20)])
icon('radioactive-slash', S, ['radioactive', 'off', 'disabled', 'hidden'],
     line=blades + [SLASH], dot=[C(128, 128, 20)])

# ================================================================ robot arm
sh, el, wr = (96, 164), (128, 72), (192, 100)
def toward(a, b, d):
    l = dist(a, b)
    return (a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l)
pa = toward(sh, el, 24); pb = toward(el, sh, 24)
pc2 = toward(el, wr, 24)
icon('robot-arm', S, ['industrial robot', 'automation', 'manufacturing', 'machine'],
     line=[R(48, 192, 96, 24, 8), C(*sh, 24), L(*pa, *pb), C(*el, 24), L(*pc2, *wr),
           L(192, 100, 192, 132), PL([(168, 172), (168, 132), (216, 132), (216, 172)])],
     area=[R(48, 192, 96, 24, 8), C(*sh, 24), C(*el, 24)])

# ================================================================ satellite (drawn horizontal, rotated -45)
def rrect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
SAT_ROT = -45
sat_body = rpoly(rot(rrect_pts(100, 96, 56, 64), SAT_ROT), 12)
sat_pl = rpoly(rot(rrect_pts(16, 96, 56, 64), SAT_ROT), 10)
sat_pr = rpoly(rot(rrect_pts(184, 96, 56, 64), SAT_ROT), 10)
st = rot([(72, 128), (100, 128), (156, 128), (184, 128), (128, 96), (128, 64)], SAT_ROT)
sat_line = [P(sat_body), P(sat_pl), P(sat_pr), L(*st[0], *st[1]), L(*st[2], *st[3]), L(*st[4], *st[5])]
icon('satellite', S, ['satellite', 'orbit', 'space', 'signal', 'communication'],
     line=sat_line, area=[P(sat_body), P(sat_pl), P(sat_pr)], dot=[C(*st[5], 14)])
icon('satellite-slash', S, ['satellite', 'off', 'disabled', 'hidden'], line=sat_line + [SLASH], dot=[C(*st[5], 14)])

# ================================================================ sigma
sig = PL([(188, 76), (188, 48), (68, 48), (136, 128), (68, 208), (188, 208), (188, 180)])
icon('sigma', S, ['sum', 'summation', 'math', 'sigma', 'greek'], line=[sig])
icon('sigma-slash', S, ['sigma', 'off', 'disabled', 'hidden'], line=[sig, SLASH])

# ================================================================ slope
st_tri = [(40, 200), (216, 200), (216, 72)]
ang = math.degrees(math.atan2(72 - 200, 216 - 40))
icon('slope', S, ['incline', 'gradient', 'angle'],
     line=[PG(st_tri)], area=[PG(st_tri)],
     detail=[P(f'M{pt(polar((40, 200), 80, 0))} A80 80 0 0 0 {pt(polar((40, 200), 80, ang))}')])

# ================================================================ solar panel
PT4 = [(100, 124), (208, 124), (224, 184), (60, 184)]
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
cols = [L(*lerp(PT4[0], PT4[1], t), *lerp(PT4[3], PT4[2], t)) for t in (1 / 3, 2 / 3)]
sunc = (76, 76)
rays = [L(*polar(sunc, 34, a), *polar(sunc, 44, a)) for a in (180, 240, 300, 0)]
panel = rpoly(PT4, 8)
icon('solar-panel', S, ['solar power', 'renewable', 'energy', 'sun panel', 'solar panel'],
     line=[P(panel), L(142, 184, 142, 216), L(108, 216, 176, 216), C(*sunc, 20)] + rays,
     detail=cols, area=[P(panel), C(*sunc, 20)])

# ================================================================ square meter
c2, r2 = (194, 70), 22
two = (f'M{pt(polar(c2, r2, 195))} A{r2} {r2} 0 1 1 {pt(polar(c2, r2, 40))} L172 116 H218')
icon('square-meter', S, ['square meter', 'area', 'm2', 'unit'],
     line=[P('M44 120 V208 M44 146 A26 26 0 0 1 96 146 V208 M96 146 A26 26 0 0 1 148 146 V208'), P(two)])

# ================================================================ surveyor level
icon('surveyor-level', S, ['surveying', 'theodolite', 'tripod', 'measure'],
     line=[R(64, 56, 128, 44, 12), L(40, 78, 64, 78), L(128, 100, 128, 124), L(92, 124, 164, 124),
           L(116, 124, 72, 216), L(140, 124, 184, 216), L(128, 124, 128, 216)],
     area=[R(64, 56, 128, 44, 12)])

# ================================================================ telescope
tb, tang = (44, 164), -30
tu = (math.cos(math.radians(tang)), math.sin(math.radians(tang)))
tn = (-tu[1], tu[0])
def tp(s, o):
    return (tb[0] + tu[0] * s + tn[0] * o, tb[1] + tu[1] * s + tn[1] * o)
tube = rpoly([tp(40, -20), tp(184, -30), tp(184, 30), tp(40, 20)], 10)
ey = [tp(4, 0), tp(28, 0)]
apex = (136, 140)
tele_line = [P(tube), L(*ey[0], *ey[1]), L(*apex, 96, 216), L(*apex, 176, 216)]
icon('telescope', S, ['telescope', 'astronomy', 'stars', 'observe'], line=tele_line, area=[P(tube)])
icon('telescope-slash', S, ['telescope', 'off', 'disabled', 'hidden'], line=tele_line + [SLASH])

icon('test-tube-slash', S, ['test tube', 'off', 'disabled', 'hidden', 'test'], **lines_only(load('test-tube')))
icon('thermometer-slash', S, ['thermometer', 'off', 'disabled', 'hidden'], **lines_only(load('thermometer')))

# ================================================================ ufo
saucer = E(128, 148, 96, 36)
ex = 128 - 44; eyy = 148 - 36 * math.sqrt(1 - (44 / 96) ** 2)
dome = f'M{f(ex)} {f(eyy)} A44 44 0 0 1 {f(256 - ex)} {f(eyy)}'
ufo_line = [saucer, P(dome), L(100, 192, 84, 216), L(156, 192, 172, 216)]
lights = [C(88, 152, 10), C(128, 156, 10), C(168, 152, 10)]
icon('ufo', S, ['ufo', 'alien spaceship', 'flying saucer', 'sci fi', 'alien craft'],
     line=ufo_line, area=[saucer, P(dome + ' Z')], dotcut=lights)
icon('ufo-slash', S, ['ufo', 'off', 'disabled', 'hidden'], line=ufo_line + [SLASH], dot=lights)

# ================================================================ water level
wl_y = 116
wl_wave = f'M56 {wl_y} Q92 {wl_y - 20} 128 {wl_y} T200 {wl_y}'
icon('water-level', S, ['water level', 'gauge', 'flood', 'tank'],
     line=[R(56, 40, 144, 176, 16), P(wl_wave)],
     area=[P(wl_wave + ' V200 A16 16 0 0 1 184 216 H72 A16 16 0 0 1 56 200 Z')],
     detail=[L(88, 152, 116, 152), L(88, 184, 116, 184)])

# ================================================================ waves
icon('wave-sawtooth', S, ['sawtooth', 'signal', 'waveform', 'sawtooth wave', 'audio'],
     line=[PL([(32, 176), (96, 80), (96, 176), (160, 80), (160, 176), (224, 80)])])
sine = [(32 + i * 3, 128 - 56 * math.sin((i * 3) / 128 * 2 * math.pi)) for i in range(65)]
icon('wave-sine', S, ['sine', 'oscillation', 'signal', 'wave', 'oscillator'], line=[PL(sine)])
icon('wave-square', S, ['square wave', 'digital signal', 'pulse', 'signal', 'digital'],
     line=[PL([(32, 168), (64, 168), (64, 88), (128, 88), (128, 168), (192, 168), (192, 88), (224, 88)])])
icon('wave-triangle', S, ['triangle wave', 'signal', 'waveform'],
     line=[PL([(32, 168), (80, 88), (128, 168), (176, 88), (224, 168)])])

# ================================================================ wind turbine
hub = (128, 108)
bl = []
for a in (-90, 30, 150):
    uu = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    nn = (-uu[1], uu[0])
    q = lambda s, o: (hub[0] + uu[0] * s + nn[0] * o, hub[1] + uu[1] * s + nn[1] * o)
    bl.append(P(f'M{pt(q(22, -6))} C{pt(q(40, 18))} {pt(q(60, 12))} {pt(q(76, 0))} C{pt(q(56, -6))} {pt(q(40, -8))} {pt(q(22, -6))} Z'))
icon('wind-turbine', S, ['wind power', 'renewable', 'energy', 'turbine', 'wind turbine'],
     line=bl + [C(*hub, 14), P('M120 128 L112 216 M136 128 L144 216'), L(88, 216, 168, 216)],
     area=bl + [C(*hub, 14)])

print(save(overwrite=True))
