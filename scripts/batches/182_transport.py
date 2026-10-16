import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

CAT = 'Transport'
SLASH = L(48, 48, 208, 208)
B = (184, 184)


# ---------------------------------------------------------------- local helpers
def _attrs(el):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', el))


def el_d(el):
    """SVG path data for a path/circle/rect/ellipse element string."""
    tag = re.match(r'<(\w+)', el).group(1)
    a = _attrs(el)
    g = lambda k, d=0: float(a.get(k, d))
    if tag == 'path':
        return a['d']
    if tag == 'circle':
        cx, cy, r = g('cx'), g('cy'), g('r')
        return f'M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'
    if tag == 'ellipse':
        cx, cy, rx, ry = g('cx'), g('cy'), g('rx'), g('ry')
        return (f'M{f(cx - rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx + rx)} {f(cy)} '
                f'A{f(rx)} {f(ry)} 0 1 1 {f(cx - rx)} {f(cy)} Z')
    if tag == 'rect':
        x, y, w, h, r = g('x'), g('y'), g('width'), g('height'), g('rx')
        if not r:
            return f'M{f(x)} {f(y)} H{f(x + w)} V{f(y + h)} H{f(x)} Z'
        return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} '
                f'V{f(y + h - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} '
                f'A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')
    raise ValueError(el)


def xf_el(el, s=1.0, deg=0.0, dx=0.0, dy=0.0, c=(128, 128)):
    """Uniform scale + rotation about c, then translate. Returns a path element."""
    tag = re.match(r'<(\w+)', el).group(1)
    a = math.radians(deg)
    co, si = math.cos(a) * s, math.sin(a) * s
    tx = c[0] + dx - co * c[0] + si * c[1]
    ty = c[1] + dy - si * c[0] - co * c[1]
    if tag == 'circle' and deg == 0:
        at = _attrs(el)
        return C(float(at['cx']) * s + tx, float(at['cy']) * s + ty, float(at['r']) * s)
    pen = SVGPathPen(None, f)
    parse_path(el_d(el), TransformPen(pen, (co, si, -si, co, tx, ty)))
    return P(pen.getCommands())


def xf_pt(p, s=1.0, deg=0.0, dx=0.0, dy=0.0, c=(128, 128)):
    q = rot([p], deg, c)[0]
    return (c[0] + (q[0] - c[0]) * s + dx, c[1] + (q[1] - c[1]) * s + dy)


def xf_dot(el, s=1.0, deg=0.0, dx=0.0, dy=0.0, c=(128, 128), rs=None):
    at = _attrs(el)
    x, y = xf_pt((float(at['cx']), float(at['cy'])), s, deg, dx, dy, c)
    return C(x, y, float(at['r']) * (s if rs is None else rs))


def _pp(ds):
    p = pathops.Path()
    pen = p.getPen()
    for d in ds:
        parse_path(d, pen)
    return p


def _d(p):
    p.convertConicsToQuads(0.05)
    pen = SVGPathPen(None, f)
    p.draw(pen)
    return pen.getCommands()


class _Flat(BasePen):
    def __init__(self, step=2):
        super().__init__(None)
        self.subs, self.step = [], step

    def _moveTo(self, p):
        self.subs.append([p])

    def _lineTo(self, p):
        a = self.subs[-1][-1]
        n = max(1, int(dist(a, p) / self.step))
        self.subs[-1] += [(a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n) for i in range(1, n + 1)]

    def _curveToOne(self, p1, p2, p3):
        p0 = self.subs[-1][-1]
        n = max(2, int((dist(p0, p1) + dist(p1, p2) + dist(p2, p3)) / self.step))
        for i in range(1, n + 1):
            t = i / n; u = 1 - t
            self.subs[-1].append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                                  u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.subs[-1][-1]
        self._curveToOne((p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1])),
                         (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1])), p2)

    def _closePath(self):
        s = self.subs[-1]
        if dist(s[-1], s[0]) > 0.01:
            self._lineTo(s[0])
        self.subs[-1].append('closed')

    _endPath = lambda self: None


def flatten(d, step=2):
    pen = _Flat(step)
    parse_path(d, pen)
    return [([p for p in s if p != 'closed'], s[-1] == 'closed') for s in pen.subs]


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _simplify(run, tol=0.35):
    """Drop collinear points from a flattened run so the output stays compact."""
    if len(run) < 3:
        return run
    out = [run[0]]
    for i in range(1, len(run) - 1):
        a, b, c = out[-1], run[i], run[i + 1]
        if _seg_dist(b, a, c) > tol:
            out.append(b)
    out.append(run[-1])
    return out


def split_by(d, keep, min_len=12):
    out = []
    for pts, closed in flatten(d):
        runs, cur = [], []
        for p in pts:
            if keep(p):
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        if len(runs) == 1 and len(runs[0]) == len(pts):
            out.append(P(d) if not closed else P(d))
            continue
        if closed and len(runs) > 1 and runs[0][0] == pts[0] and runs[-1][-1] == pts[-1]:
            runs[0] = runs.pop() + runs[0][1:]
        for r in runs:
            ln = sum(dist(a, b) for a, b in zip(r, r[1:]))
            if ln >= min_len:
                out.append(P('M' + ' L'.join(pt(p) for p in _simplify(r))))
    return out


def gap_slash(els, gap=28):
    out = []
    for el in els:
        out += split_by(el_d(el), lambda p: _seg_dist(p, (48, 48), (208, 208)) >= gap)
    return out


def slashed(roles, gap=28):
    """Slash variant: strokes become line with a gap around the slash, dotcuts become dots, no area."""
    dots = []
    for el in roles.get('dot', []) + roles.get('dotcut', []):
        a = _attrs(el)
        if _seg_dist((float(a['cx']), float(a['cy'])), (48, 48), (208, 208)) >= gap + 4:
            dots.append(el)
    return dict(line=gap_slash(roles.get('line', []) + roles.get('detail', []), gap) + [SLASH], dot=dots)


def badge_cut(roles, R=60, c=B):
    """Trim a base icon around the badge spot: strokes keep points >= R from c, fills lose a circle."""
    keep = lambda p: dist(p, c) >= R
    out = {k: [] for k in ('line', 'detail', 'area', 'hole', 'dot', 'dotcut')}
    for k in ('line', 'detail'):
        for el in roles.get(k, []):
            out[k] += split_by(el_d(el), keep)
    circ = _pp([el_d(C(c[0], c[1], R - 8))])
    for k in ('area', 'hole'):
        for el in roles.get(k, []):
            res = pathops.op(_pp([el_d(el)]), circ, pathops.PathOp.DIFFERENCE)
            dd = _d(res)
            if dd:
                out[k].append(P(dd))
    for k in ('dot', 'dotcut'):
        for el in roles.get(k, []):
            a = _attrs(el)
            if dist((float(a['cx']), float(a['cy'])), c) >= R + float(a['r']):
                out[k].append(el)
    return out


def merge(*rs):
    out = {k: [] for k in ('line', 'detail', 'area', 'hole', 'dot', 'dotcut')}
    for r in rs:
        for k, v in r.items():
            out[k] += list(v)
    return out


def xf_roles(roles, s=1.0, deg=0.0, dx=0.0, dy=0.0, c=(128, 128), rs=None):
    out = {}
    for k, v in roles.items():
        if k in ('dot', 'dotcut'):
            out[k] = [xf_dot(e, s, deg, dx, dy, c, rs) for e in v]
        else:
            out[k] = [xf_el(e, s, deg, dx, dy, c) for e in v]
    return out


def drop(cx, top, w=12):
    return P(f'M{f(cx)} {f(top)} C{f(cx)} {f(top)} {f(cx - w)} {f(top + 18)} {f(cx - w)} {f(top + 26)} '
             f'A{f(w)} {f(w)} 0 0 0 {f(cx + w)} {f(top + 26)} C{f(cx + w)} {f(top + 18)} {f(cx)} {f(top)} {f(cx)} {f(top)} Z')


def T(pts, c=B):
    return [(c[0] + x, c[1] + y) for x, y in pts]


CAR = load('car')
CAR_B = dict(CAR, detail=[])

# ================================================================ cars
# car-electric: car with a lightning-bolt badge
bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
icon('car-electric', CAT, ['electric vehicle', 'ev', 'car', 'charging'],
     **merge(badge_cut(CAR_B, 58), dict(line=[PG(bolt)], area=[PG(bolt)])))

# car-fan: car with a small three-blade fan badge
fan_blade = 'M120 116 C104 96 104 60 124 44 A8 8 0 0 1 136 46 C152 64 150 96 136 116'
fan_mark = dict(line=[], area=[])
for a in (0, 120, 240):
    bl = xf_el(P(fan_blade), 0.44, a, B[0] - 128, B[1] - 128)
    fan_mark['line'].append(bl)
    fan_mark['area'].append(xf_el(P(fan_blade + ' Z'), 0.44, a, B[0] - 128, B[1] - 128))
icon('car-fan', CAT, ['car fan', 'car', 'vehicle', 'auto', 'fan'],
     **merge(badge_cut(CAR_B, 60), fan_mark))

# car-fan-auto: the library fan with an "A" badge
FAN = load('fan')
fan_s = xf_roles(FAN, 0.84, 75, -16, -16)
A_mark = [PL([(162, 214), (184, 156), (206, 214)]), L(171, 192, 197, 192)]
icon('car-fan-auto', CAT, ['climate', 'ventilation', 'auto', 'car'],
     **merge(badge_cut(fan_s, 58, (184, 186)), dict(line=A_mark)))

# car-lifter: car raised on a scissor lift
car_l = xf_roles(CAR, 0.72, 0, 0, 0, (128, 208), rs=0.75)
car_l = xf_roles(car_l, 1, 0, 0, -48)
icon('car-lifter', CAT, ['car lifter', 'car', 'vehicle', 'auto', 'lifter'],
     line=car_l['line'] + [L(40, 168, 216, 168), L(88, 168, 168, 216), L(168, 168, 88, 216), L(64, 216, 192, 216)],
     detail=car_l['detail'], area=car_l['area'], dotcut=car_l['dotcut'])

# side-view cars
def wheels(xs, y=188, r=20):
    return [C(x, y, r) for x in xs]

offroad = ('M56 64 H124 A12 12 0 0 1 134.3 69.8 L160 112 H212 A12 12 0 0 1 224 124 V148 '
           'A12 12 0 0 1 212 160 H68 A12 12 0 0 1 56 148 V64 Z')
offroad = ('M68 60 H130 A8 8 0 0 1 137.6 65.4 L150 104 H212 A12 12 0 0 1 224 116 V144 '
           'A12 12 0 0 1 212 156 H68 A12 12 0 0 1 56 144 V72 A12 12 0 0 1 68 60 Z')
icon('car-off-road', CAT, ['off-road', 'jeep', '4x4', 'vehicle', 'suv'],
     line=[P(offroad), P('M56 84 A24 24 0 0 0 56 132')] + wheels([98, 186], 190, 26),
     detail=[R(76, 80, 44, 36, 8)],
     area=[P(offroad)])

prof_body = ('M48 112 H176 C196 112 212 116 219 123 A12 12 0 0 1 224 132 V148 A12 12 0 0 1 212 160 '
             'H44 A12 12 0 0 1 32 148 V128 A16 16 0 0 1 48 112 Z')
icon('car-profile', CAT, ['car side view', 'vehicle', 'sedan'],
     line=[P(prof_body), PL([(60, 112), (88, 64), (156, 64), (196, 112)]), L(124, 64, 124, 112)] + wheels([76, 180]),
     area=[P(prof_body)])

sport = ('M44 124 H140 L196 134 C212 137 224 148 224 160 V164 H44 A12 12 0 0 1 32 152 V136 '
         'A12 12 0 0 1 44 124 Z')
icon('car-sport', CAT, ['roadster', 'sports car', 'convertible', 'car'],
     line=[P(sport), L(142, 124, 118, 92), L(80, 124, 90, 102)] + wheels([80, 180], 192),
     area=[P(sport)])

# police-car: the car moved down with a roof light
pc = xf_roles(CAR, 1, 0, 0, 8)
dome = 'M108 64 V56 A20 20 0 0 1 148 56 V64'
icon('police-car', CAT, ['police car', 'cop', 'emergency', 'patrol'],
     line=pc['line'] + [P(dome)], detail=pc['detail'], area=pc['area'] + [P(dome + ' Z')], dotcut=pc['dotcut'])

icon('car-slash', CAT, ['no car', 'car off', 'no parking', 'slash'], **slashed(CAR))

# car-suspension: car body on two coil springs
susp_body = R(32, 72, 192, 48, 14)
spring = lambda x: PL([(x, 120), (x + 20, 128), (x - 20, 144), (x + 20, 160), (x, 168), (x, 180)])
icon('car-suspension', CAT, ['car suspension', 'car', 'vehicle', 'auto', 'suspension'],
     line=[susp_body, PL([(56, 72), (78, 32), (178, 32), (200, 72)]), spring(72), spring(184),
           R(56, 180, 32, 44, 14), R(168, 180, 32, 44, 14)],
     area=[susp_body, R(56, 180, 32, 44, 14), R(168, 180, 32, 44, 14)],
     dotcut=[C(72, 96, 14), C(184, 96, 14)])

# car-turbine: turbo snail housing with an impeller
tc = (120, 140); tr = 76
ty = 104
tx = tc[0] + math.sqrt(tr * tr - (ty - tc[1]) ** 2)
turbo = f'M{f(tx)} {ty} H204 A12 12 0 0 0 216 92 V76 A12 12 0 0 0 204 64 H{tc[0]} A{tr} {tr} 0 1 0 {f(tx)} {ty} Z'
blades = []
for i in range(4):
    a = i * 90 - 45
    blades.append(P(f'M{pt(polar(tc, 18, a))} Q{pt(polar(tc, 40, a))} {pt(polar(tc, 48, a + 50))}'))
icon('car-turbine', CAT, ['turbine', 'turbo', 'car', 'engine'],
     line=[P(turbo)], detail=blades, area=[P(turbo)], dotcut=[])

# car-wash: smaller car with three drops above
cw = xf_roles(CAR, 0.75, 0, 0, 8, (128, 208), rs=0.9)
icon('car-wash', CAT, ['car wash', 'cleaning', 'water', 'car', 'vehicle'],
     line=cw['line'] + [drop(80, 46), drop(128, 32), drop(176, 46)], detail=cw['detail'],
     area=cw['area'] + [drop(80, 46), drop(128, 32), drop(176, 46)], dotcut=cw['dotcut'])

# caravan
cara = 'M56 56 H164 A44 44 0 0 1 208 100 V152 A16 16 0 0 1 192 168 H56 A16 16 0 0 1 40 152 V72 A16 16 0 0 1 56 56 Z'
icon('caravan', CAT, ['caravan', 'camper', 'trailer', 'rv'],
     line=[P(cara), C(100, 196, 20), PL([(200, 168), (224, 184)])],
     detail=[R(68, 84, 48, 36, 8), R(144, 96, 32, 56, 8)],
     area=[P(cara)])

# charging-station
post = 'M48 216 V56 A16 16 0 0 1 64 40 H128 A16 16 0 0 1 144 56 V216'
icon('charging-station', CAT, ['ev charging', 'charger', 'electric car', 'ev charger', 'electric vehicle'],
     line=[P(post), L(32, 216, 160, 216), P('M144 104 H172 A20 20 0 0 1 192 124 V156'), R(176, 156, 32, 40, 8)],
     detail=[PL([(104, 76), (80, 120), (112, 120), (88, 164)])],
     area=[P(post + ' Z'), R(176, 156, 32, 40, 8)])

# control-tower
roof = 'M84 80 L100 48 H156 L172 80'
shaft = 'M100 128 L108 216 H148 L156 128 Z'
icon('control-tower', CAT, ['control tower', 'airport', 'air traffic', 'aviation'],
     line=[L(128, 32, 128, 48), P(roof), PG([(48, 80), (208, 80), (184, 128), (72, 128)]),
           L(100, 128, 108, 216), L(156, 128, 148, 216), L(72, 216, 184, 216)],
     area=[P(roof + ' Z'), P(shaft)])

# crane
crane = dict(line=[L(32, 64, 224, 64), PL([(40, 64), (104, 32), (216, 64)]), R(88, 64, 32, 152), L(64, 216, 144, 216),
                   R(32, 64, 32, 32, 6), L(184, 64, 184, 136), P('M184 136 V156 A16 16 0 0 1 152 156')],
             area=[R(88, 64, 32, 152), R(32, 64, 32, 32, 6)])
icon('crane', CAT, ['crane', 'construction', 'lifting', 'building', 'building site'], **crane)
icon('crane-slash', CAT, ['crane', 'disabled', 'off', 'transport'], **slashed(crane))

# crane-truck
ctb = ('M40 128 H152 V100 A12 12 0 0 1 164 88 H186 A12 12 0 0 1 195 92 L220 120 A12 12 0 0 1 224 128 '
       'V152 A8 8 0 0 1 216 160 H40 A8 8 0 0 1 32 152 V136 A8 8 0 0 1 40 128 Z')
icon('crane-truck', CAT, ['crane', 'tow', 'construction'],
     line=[P(ctb), C(72, 188, 20), C(184, 188, 20), PL([(124, 128), (80, 56), (52, 56)]), L(52, 56, 52, 84),
           P('M52 84 V94 A12 12 0 0 0 76 94')],
     area=[P(ctb)])

# defrost: windshield with three wavy heat arrows
ws = 'M48 64 Q128 40 208 64 L224 192 Q128 168 32 192 Z'
waves = []
for x in (80, 128, 176):
    waves += [P(f'M{x} 156 C{x + 11} 144 {x + 11} 132 {x} 120 S{x - 11} 96 {x} 84'),
              PL([(x - 12, 96), (x, 84), (x + 12, 96)])]
icon('defrost', CAT, ['defrost', 'windshield', 'heater', 'car'], line=[P(ws)], detail=waves, area=[P(ws)])

# engine
eng_r = 'M192 124 H204 L224 108 V180 L204 164 H192'
engine = dict(line=[R(64, 96, 128, 88, 12), P('M88 96 V72 A8 8 0 0 1 96 64 H160 A8 8 0 0 1 168 72 V96'),
                    L(128, 40, 128, 64), L(32, 116, 32, 164), L(32, 140, 64, 140), P(eng_r)],
              area=[R(64, 96, 128, 88, 12), P(eng_r + ' Z')])
engine = xf_roles(engine, 1, 0, 0, 16)
icon('engine', CAT, ['engine', 'motor', 'car', 'mechanic'], **engine)
icon('engine-slash', CAT, ['engine', 'disabled', 'off', 'transport'], **slashed(engine))

# ev-plug
hy = 56; hc = (128, 104); hr = 64
hx = math.sqrt(hr * hr - (hc[1] - hy) ** 2)
head = f'M{f(hc[0] - hx)} {hy} H{f(hc[0] + hx)} A{hr} {hr} 0 1 1 {f(hc[0] - hx)} {hy} Z'
ly = hc[1] + math.sqrt(hr * hr - 24 * 24)
icon('ev-plug', CAT, ['ev connector', 'charging plug', 'electric car'],
     line=[P(head), PL([(104, ly), (112, 200), (144, 200), (152, ly)]), L(128, 200, 128, 224)],
     area=[P(head), PG([(104, ly), (112, 200), (144, 200), (152, ly)])],
     dotcut=[C(106, 88, 15), C(150, 88, 15), C(106, 128, 15), C(150, 128, 15)])

# excavator
exu = 'M56 176 V96 A16 16 0 0 1 72 80 H100 A12 12 0 0 1 112 92 V128 H140 A12 12 0 0 1 152 140 V176'
bucket = 'M212 104 V132 A20 20 0 0 1 192 152 H180 Z'
icon('excavator', CAT, ['excavator', 'construction', 'digger', 'machinery', 'vehicle'],
     line=[R(32, 176, 144, 40, 20), P(exu), PL([(136, 128), (176, 56), (212, 104)]), P(bucket)],
     area=[R(32, 176, 144, 40, 20), P(exu + ' Z'), P(bucket)])

# ferry
hull = 'M32 160 H224 L200 208 H64 Z'
cabin = 'M56 160 V124 A12 12 0 0 1 68 112 H180 L200 160'
bridge = 'M88 112 V84 A8 8 0 0 1 96 76 H148 L164 112'
funnel = 'M104 76 L108 48 H132 L136 76'
icon('ferry', CAT, ['ferry', 'boat', 'ship', 'transport'],
     line=[P(hull), P(cabin), P(bridge), P(funnel)],
     area=[P(hull), P(cabin + ' Z'), P(bridge + ' Z'), P(funnel + ' Z')],
     dotcut=[C(88, 136, 12), C(120, 136, 12), C(152, 136, 12)])

# fire-truck
ftb = ('M40 104 H152 V96 A8 8 0 0 1 160 88 H184 A12 12 0 0 1 193 92 L220 124 A12 12 0 0 1 224 132 '
       'V152 A8 8 0 0 1 216 160 H40 A8 8 0 0 1 32 152 V112 A8 8 0 0 1 40 104 Z')
icon('fire-truck', CAT, ['fire engine', 'emergency', 'firefighter', 'truck', 'vehicle'],
     line=[P(ftb), C(72, 188, 20), C(184, 188, 20), L(44, 72, 124, 72), L(44, 72, 44, 104), L(84, 72, 84, 104),
           L(124, 72, 124, 104)],
     detail=[L(60, 132, 124, 132)],
     area=[P(ftb)])

# forklift
icon('forklift', CAT, ['forklift', 'warehouse', 'lifting', 'logistics'],
     line=[R(40, 128, 104, 48, 12), PL([(56, 128), (72, 64), (136, 64), (136, 128)]),
           PL([(176, 48), (176, 200), (224, 200)]), L(144, 152, 176, 152), C(64, 206, 18), C(130, 206, 18)],
     area=[R(40, 128, 104, 48, 12)])

# front-loader
fl = 'M32 160 V120 A8 8 0 0 1 40 112 H72 V72 A16 16 0 0 1 88 56 H112 A16 16 0 0 1 128 72 V160 Z'
flb = 'M184 96 V152 A8 8 0 0 0 192 160 H224 L208 96 Z'
icon('front-loader', CAT, ['loader', 'construction', 'bulldozer', 'machine'],
     line=[P(fl), L(128, 128, 184, 128), P(flb), C(64, 192, 24), C(144, 192, 24)],
     area=[P(fl), P(flb)])

# gas-can
can = 'M104 64 H184 A16 16 0 0 1 200 80 V208 A16 16 0 0 1 184 224 H72 A16 16 0 0 1 56 208 V112 Z'
icon('gas-can', CAT, ['jerrycan', 'fuel can', 'petrol'],
     line=[P(can), P('M136 64 V40 A8 8 0 0 1 144 32 H184 A8 8 0 0 1 192 40 V64'), L(80, 88, 48, 56)],
     detail=[L(100, 120, 164, 184), L(164, 120, 100, 184)],
     area=[P(can)])

icon('gas-pump-slash', CAT, ['gas pump', 'off', 'disabled', 'hidden', 'gas'], **slashed(load('gas-pump')))

# gear-shift
boot = 'M72 216 A56 32 0 0 1 184 216 Z'
icon('gear-shift', CAT, ['gear stick', 'transmission', 'shifter', 'manual', 'gear shift'],
     line=[C(128, 88, 56), L(128, 144, 128, 184), P(boot)],
     detail=[L(108, 68, 108, 108), L(148, 68, 148, 108), L(108, 88, 148, 88)],
     area=[C(128, 88, 56), P(boot)])

# hand-brake
hb = (128, 128)
arcs = [P(f'M{pt(polar(hb, 96, 140))} A96 96 0 0 1 {pt(polar(hb, 96, 220))}'),
        P(f'M{pt(polar(hb, 96, -40))} A96 96 0 0 1 {pt(polar(hb, 96, 40))}')]
icon('hand-brake', CAT, ['parking brake', 'car warning', 'dashboard'],
     line=[C(128, 128, 64)] + arcs, detail=[L(128, 96, 128, 132)], area=[C(128, 128, 64)], dotcut=[C(128, 162, 14)])

# headlights
lamp = 'M120 56 V200 C72 200 40 168 40 128 C40 88 72 56 120 56 Z'
icon('headlights', CAT, ['headlights', 'high beam', 'car lights'],
     line=[P(lamp)] + [L(152, y, 216, y) for y in (72, 112, 152, 192)], area=[P(lamp)])

# helicopter
heli = 'M120 72 H152 A56 56 0 0 1 208 128 A24 24 0 0 1 184 152 H120 A40 40 0 0 1 120 72 Z'
icon('helicopter', CAT, ['helicopter', 'chopper', 'aviation', 'rotor'],
     line=[P(heli), L(48, 40, 208, 40), L(136, 40, 136, 72), L(82, 104, 40, 96), L(36, 76, 36, 112),
           P('M96 200 H196 A12 12 0 0 0 208 188'), L(120, 152, 120, 200), L(176, 152, 176, 200)],
     detail=[P('M152 100 A28 28 0 0 1 180 128 H160 A8 8 0 0 1 152 120 Z')],
     area=[P(heli)])

# helipad
icon('helipad', CAT, ['helipad', 'helicopter', 'landing', 'h'],
     line=[C(128, 128, 96)], detail=[L(96, 84, 96, 172), L(160, 84, 160, 172), L(96, 128, 160, 128)],
     area=[C(128, 128, 96)])

# hot-air-balloon
env = 'M104 176 C80 156 48 140 48 112 A80 80 0 0 1 208 112 C208 140 176 156 152 176 Z'
icon('hot-air-balloon', CAT, ['balloon', 'flight', 'travel', 'air', 'hot air balloon'],
     line=[P(env), L(108, 176, 112, 200), L(148, 176, 144, 200), R(104, 200, 48, 24, 6)],
     detail=[P('M112 64 C98 88 96 124 110 148'), P('M144 64 C158 88 160 124 146 148')],
     area=[P(env), R(104, 200, 48, 24, 6)])

# jet-ski
js = 'M40 136 H136 L160 112 H184 L224 144 C216 160 200 168 184 168 H48 A8 8 0 0 1 40 160 Z'
icon('jet-ski', CAT, ['jet ski', 'water scooter', 'boat', 'sea'],
     line=[P(js), P('M60 136 V116 A12 12 0 0 1 72 104 H108 A12 12 0 0 1 120 116 V136'), L(172, 112, 156, 72),
           L(140, 72, 172, 72), P('M40 204 Q60 192 80 204 T120 204 T160 204 T200 204')],
     area=[P(js)])

# jetpack
flame = lambda x: P(f'M{x} 224 C{x - 8} 212 {x - 12} 202 {x - 12} 194 A12 12 0 0 1 {x + 12} 194 '
                    f'C{x + 12} 202 {x + 8} 212 {x} 224 Z')
icon('jetpack', CAT, ['jetpack', 'fly', 'rocket pack', 'future'],
     line=[R(56, 40, 56, 120, 28), R(144, 40, 56, 120, 28), L(112, 80, 144, 80), L(112, 128, 144, 128),
           flame(84), flame(172)],
     area=[R(56, 40, 56, 120, 28), R(144, 40, 56, 120, 28), flame(84), flame(172)])

# license-plate
icon('license-plate', CAT, ['license plate', 'car tag', 'number plate', 'registration'],
     line=[R(32, 64, 192, 128, 16)], detail=[L(100, 104, 156, 104), L(72, 152, 184, 152)],
     area=[R(32, 64, 192, 128, 16)], dotcut=[C(64, 96, 14), C(192, 96, 14)])

# luggage-clock
SUIT = load('suitcase')
clock_b = dict(line=[C(184, 184, 40)], detail=[PL([(184, 162), (184, 184), (198, 194)])], area=[C(184, 184, 40)])
icon('luggage-clock', CAT, ['baggage', 'delay', 'luggage', 'travel'], **merge(badge_cut(SUIT, 64), clock_b))

# monorail
mono = ('M48 152 V80 A40 40 0 0 1 88 40 H168 A40 40 0 0 1 208 80 V152 A16 16 0 0 1 192 168 H64 '
        'A16 16 0 0 1 48 152 Z')
beam = 'M108 168 V224 H148 V168'
icon('monorail', CAT, ['monorail', 'train', 'elevated rail', 'transit'],
     line=[P(mono), P(beam)], detail=[R(76, 68, 104, 44, 10)],
     area=[P(mono), P(beam + ' Z')], dotcut=[C(88, 140, 14), C(168, 140, 14)])

# moped
cowl = 'M32 160 C32 128 56 112 88 112 H120 V160 Z'
icon('moped', CAT, ['e-bike', 'scooter', 'moped', 'electric', 'vespa'],
     line=[P(cowl), C(64, 194, 22), C(196, 194, 22), L(120, 160, 189, 160), L(172, 64, 192, 170), L(152, 64, 188, 64)],
     area=[P(cowl)])

# moped-front
shield = [(84, 120), (172, 120), (156, 172), (100, 172)]
icon('moped-front', CAT, ['scooter', 'moped', 'vespa'],
     line=[C(128, 68, 28), L(40, 76, 92, 76), L(164, 76, 216, 76), L(56, 76, 48, 48), L(200, 76, 208, 48), PG(shield),
           R(110, 186, 36, 38, 14)],
     area=[C(128, 68, 28), PG(shield), R(110, 186, 36, 38, 14)])

# parachute
can_p = ('M32 112 A96 80 0 0 1 224 112 A32 16 0 0 0 160 112 A32 16 0 0 0 96 112 A32 16 0 0 0 32 112 Z')
para = dict(line=[P(can_p), L(32, 112, 112, 184), L(96, 112, 116, 184), L(160, 112, 140, 184), L(224, 112, 144, 184),
                  R(108, 184, 40, 32, 8)],
            area=[P(can_p), R(108, 184, 40, 32, 8)])
icon('parachute', CAT, ['parachute', 'skydive', 'drop', 'air'], **para)
icon('parachute-slash', CAT, ['parachute', 'off', 'disabled', 'hidden'], **slashed(para))

# parking-meter
pm = 'M72 88 A56 56 0 0 1 184 88 V132 A12 12 0 0 1 172 144 H84 A12 12 0 0 1 72 132 Z'
icon('parking-meter', CAT, ['parking meter', 'pay parking', 'meter', 'street', 'coin'],
     line=[P(pm), L(128, 144, 128, 216), L(96, 216, 160, 216)],
     detail=[R(100, 76, 56, 36, 8)],
     area=[P(pm)])

# passport
icon('passport', CAT, ['passport', 'travel', 'id', 'border', 'document'],
     line=[R(56, 32, 144, 192, 16)],
     detail=[C(128, 104, 44), E(128, 104, 16, 44), L(96, 184, 160, 184)],
     area=[R(56, 32, 144, 192, 16)])

# personal-transporter (front view)
icon('personal-transporter', CAT, ['personal transporter', 'self balancing', 'scooter', 'ride'],
     line=[R(40, 152, 32, 72, 14), R(184, 152, 32, 72, 14), R(72, 172, 112, 32, 8), L(128, 172, 128, 56),
           L(92, 48, 164, 48)],
     area=[R(40, 152, 32, 72, 14), R(184, 152, 32, 72, 14), R(72, 172, 112, 32, 8)])

# propeller
pc0 = (128, 128)
blade_local = 'M118 111 C106 88 104 56 120 36 C125 30 133 30 138 36 C150 56 148 88 138 111'
prop_lines, prop_area = [C(128, 128, 20)], [C(128, 128, 20)]
for a in (0, 120, 240):
    prop_lines.append(xf_el(P(blade_local), 1, a))
    prop_area.append(xf_el(P(blade_local + ' Z'), 1, a))
prop = xf_roles(dict(line=prop_lines, area=prop_area, dotcut=[C(128, 128, 8)]), 1, 0, 0, 16)
icon('propeller', CAT, ['propeller', 'fan', 'blade', 'aircraft'], **prop)
# rotated 15 degrees so no blade lies along the slash
icon('propeller-slash', CAT, ['propeller', 'off', 'disabled', 'hidden'],
     **slashed(xf_roles(prop, 1, -15, 0, 0, (128, 144)), gap=25))

# rickshaw
rk = ('M48 164 A16 16 0 0 1 32 148 V100 C32 70 56 48 86 48 H162 A12 12 0 0 1 172.7 54.6 L222 152 '
      'A8 8 0 0 1 214.9 164 Z')
rko = 'M60 140 V100 A20 20 0 0 1 80 80 H144 L174 140 Z'
icon('rickshaw', CAT, ['rickshaw', 'tuk tuk', 'auto rickshaw', 'three wheeler'],
     line=[P(rk), P(rko), C(76, 192, 20), C(192, 196, 16)], area=[P(rk)], hole=[P(rko)])

# rocket-launch: the rocket tilted 45 degrees with an exhaust flame
ROCKET = load('rocket')
rl = dict(line=ROCKET['line'][:3] + [P('M108 196 C108 210 118 220 128 236 C138 220 148 210 148 196')],
          detail=ROCKET['detail'], area=ROCKET['area'])
rl = xf_roles(rl, 0.9, 45, 10, -10)
icon('rocket-launch', CAT, ['launch', 'startup', 'rocket', 'takeoff', 'liftoff'], **rl)
icon('rocket-slash', CAT, ['rocket', 'off', 'disabled', 'hidden'], **slashed(ROCKET))

print(save(overwrite=True))
