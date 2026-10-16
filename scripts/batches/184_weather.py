import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

TAU = 2 * math.pi


# ------------------------------------------------------------------ geometry engine
class Arc:
    def __init__(self, c, r, a0, span, sweep):
        self.c, self.r, self.a0, self.span, self.sweep = c, r, a0, span, sweep

    def point(self, t):
        a = self.a0 + (t * self.span if self.sweep else -t * self.span)
        return (self.c[0] + self.r * math.cos(a), self.c[1] + self.r * math.sin(a))

    def cmd(self, t0, t1):
        sp = abs(t1 - t0) * self.span
        sw = self.sweep if t1 > t0 else 1 - self.sweep
        return f'A{f(self.r)} {f(self.r)} 0 {1 if sp > math.pi else 0} {sw} {pt(self.point(t1))}'

    def tf(self, s, dx, dy):
        return Arc((self.c[0] * s + dx, self.c[1] * s + dy), self.r * s, self.a0, self.span, self.sweep)


class Seg:
    def __init__(self, p, q):
        self.p, self.q = p, q

    def point(self, t):
        return (self.p[0] + (self.q[0] - self.p[0]) * t, self.p[1] + (self.q[1] - self.p[1]) * t)

    def cmd(self, t0, t1):
        return f'L{pt(self.point(t1))}'

    def tf(self, s, dx, dy):
        return Seg((self.p[0] * s + dx, self.p[1] * s + dy), (self.q[0] * s + dx, self.q[1] * s + dy))


def make_arc(c, r, p, q, prefer):
    a1 = math.atan2(p[1] - c[1], p[0] - c[0])
    a2 = math.atan2(q[1] - c[1], q[0] - c[0])
    span1 = (a2 - a1) % TAU
    best = None
    for sweep, span in ((1, span1), (0, TAU - span1)):
        mid = a1 + (span / 2 if sweep else -span / 2)
        m = (c[0] + r * math.cos(mid), c[1] + r * math.sin(mid))
        sc = prefer(m)
        if best is None or sc > best[0]:
            best = (sc, sweep, span)
    return Arc(c, r, a1, best[2], best[1])


def circle_segs(c, r, start=-90, sweep=1):
    a = math.radians(start)
    return [Arc(c, r, a, math.pi, sweep), Arc(c, r, a + (math.pi if sweep else -math.pi), math.pi, sweep)]


def run_d(run, close=False):
    seg, t0, t1 = run[0]
    d = 'M' + pt(seg.point(t0))
    for seg, t0, t1 in run:
        d += ' ' + seg.cmd(t0, t1)
    return d + (' Z' if close else '')


def shape_d(segs, close=True):
    return run_d([(s, 0, 1) for s in segs], close)


def sample(segs, n=120):
    pts = []
    for s in segs:
        for i in range(n):
            pts.append(s.point(i / n))
    return pts


def poly_inside(poly):
    def inside(p):
        x, y = p
        c = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]; xj, yj = poly[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
            j = i
        return c
    return inside


def shape_inside(segs, margin=0):
    poly = sample(segs)
    ins = poly_inside(poly)
    if not margin:
        return ins
    return lambda p: ins(p) or min(dist(p, q) for q in poly) < margin


def union_inside(*fns):
    return lambda p: any(fn(p) for fn in fns)


def clip(segs, inside, closed=True, n=200):
    """Return runs (lists of (seg,t0,t1)) of the outline that lie outside `inside`."""
    pieces = []  # (seg_index, t0, t1)
    for k, s in enumerate(segs):
        ts = [i / n for i in range(n + 1)]
        st = [not inside(s.point(t)) for t in ts]
        i = 0
        while i <= n:
            if st[i]:
                j = i
                while j + 1 <= n and st[j + 1]:
                    j += 1
                def edge(ta, tb):  # ta outside, tb inside
                    for _ in range(40):
                        tm = (ta + tb) / 2
                        if inside(s.point(tm)):
                            tb = tm
                        else:
                            ta = tm
                    return ta
                t0 = ts[i] if i == 0 else edge(ts[i], ts[i - 1])
                t1 = ts[j] if j == n else edge(ts[j], ts[j + 1])
                if t1 - t0 > 1e-4:
                    pieces.append((k, t0, t1))
                i = j + 1
            else:
                i += 1
    runs = []
    for k, t0, t1 in pieces:
        if runs and runs[-1][-1][0] == k - 1 and runs[-1][-1][2] == 1 and t0 == 0:
            runs[-1].append((k, t0, t1))
        else:
            runs.append([(k, t0, t1)])
    if closed and len(runs) > 1 and runs[0][0][0] == 0 and runs[0][0][1] == 0 \
            and runs[-1][-1][0] == len(segs) - 1 and runs[-1][-1][2] == 1:
        runs[0] = runs.pop() + runs[0]
    return [[(segs[k], t0, t1) for k, t0, t1 in r] for r in runs]


def run_len(run):
    pts = [s.point(t0 + (t1 - t0) * i / 20) for s, t0, t1 in run for i in range(21)]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def clipped(segs, inside, closed=True, min_len=12):
    runs = [r for r in clip(segs, inside, closed) if run_len(r) >= min_len]
    if len(runs) == 1 and closed and runs[0][0][1] == 0 and runs[0][-1][2] == 1 and len(runs[0]) == len(segs):
        return [P(shape_d(segs))]
    return [P(run_d(r)) for r in runs]


# ------------------------------------------------------------------ cloud model (library cloud)
_J1, _J2 = (191.06, 105.41), (72.04, 113.83)
def _top_center():
    mx, my = (_J1[0] + _J2[0]) / 2, (_J1[1] + _J2[1]) / 2
    dx, dy = _J2[0] - _J1[0], _J2[1] - _J1[1]
    d = math.hypot(dx, dy)
    h = math.sqrt(60 * 60 - (d / 2) ** 2)
    c1 = (mx + h * dy / d, my - h * dx / d)
    c2 = (mx - h * dy / d, my + h * dx / d)
    return c1 if c1[1] > c2[1] else c2
_CT = _top_center()


def cloud_segs(s=1, dx=0, dy=0):
    big = lambda m: -1
    base = [Seg((84, 192), (180, 192)),
            make_arc((180, 148), 44, (180, 192), _J1, lambda m: m[0]),
            make_arc(_CT, 60, _J1, _J2, lambda m: -m[1]),
            make_arc((84, 152), 40, _J2, (84, 192), lambda m: -m[0])]
    return [g.tf(s, dx, dy) for g in base]


def cloud(s=1, dx=0, dy=0):
    return P(shape_d(cloud_segs(s, dx, dy)))


SMALL = (0.8, 20.8, -4.8)   # cloud-rain / cloud-snow cloud
SC = cloud(*SMALL)
BC = cloud()


# ------------------------------------------------------------------ path transform (uniform scale + translate)
def tf_d(d, s, dx, dy):
    toks = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', d)
    out = []; i = 0; cmd = None
    X = lambda v: f(float(v) * s + dx)
    Y = lambda v: f(float(v) * s + dy)
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; out.append(t); i += 1
            if cmd in 'Zz':
                continue
        if cmd in 'ML':
            out += [X(toks[i]), Y(toks[i + 1])]; i += 2
        elif cmd == 'H':
            out.append(X(toks[i])); i += 1
        elif cmd == 'V':
            out.append(Y(toks[i])); i += 1
        elif cmd == 'C':
            for k in range(3):
                out += [X(toks[i + 2 * k]), Y(toks[i + 2 * k + 1])]
            i += 6
        elif cmd == 'Q':
            for k in range(2):
                out += [X(toks[i + 2 * k]), Y(toks[i + 2 * k + 1])]
            i += 4
        elif cmd == 'A':
            out += [f(float(toks[i]) * s), f(float(toks[i + 1]) * s), toks[i + 2], toks[i + 3], toks[i + 4],
                    X(toks[i + 5]), Y(toks[i + 6])]
            i += 7
        else:
            raise ValueError(cmd)
    return ' '.join(out).replace(' A', ' A')


def tf_el(el, s, dx, dy):
    m = re.match(r'<path d="([^"]+)"/>', el)
    if m:
        return P(tf_d(m.group(1), s, dx, dy))
    m = re.match(r'<circle cx="([^"]+)" cy="([^"]+)" r="([^"]+)"/>', el)
    if m:
        return C(float(m.group(1)) * s + dx, float(m.group(2)) * s + dy, float(m.group(3)) * s)
    raise ValueError(el)


def tf_roles(src, s, dx, dy, keep_dot_r=True):
    out = {}
    for role, els in src.items():
        res = []
        for el in els:
            e = tf_el(el, s, dx, dy)
            if role in ('dot', 'dotcut') and keep_dot_r:
                m = re.match(r'<circle cx="([^"]+)" cy="([^"]+)" r="([^"]+)"/>', el)
                e = C(float(m.group(1)) * s + dx, float(m.group(2)) * s + dy, float(m.group(3)))
            res.append(e)
        out[role] = res
    return out


def wave(x0, x1, y, h=32, a=16, phase=1):
    d = f'M{f(x0)} {f(y)}'
    x = x0; k = 0
    while x < x1 - 0.01:
        nx = min(x + h, x1)
        sgn = -phase if k % 2 == 0 else phase
        d += f' Q{f((x + nx) / 2)} {f(y + sgn * a)} {f(nx)} {f(y)}'
        x = nx; k += 1
    return P(d)


def merge(*dicts):
    out = {}
    for dct in dicts:
        for k, v in dct.items():
            out.setdefault(k, [])
            out[k] = out[k] + list(v)
    return out


SLASH = L(48, 48, 208, 208)


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))

SLASH_GAP = lambda p: seg_dist(p, (48, 48), (208, 208)) < 30


def wave_arcs(x0, x1, y, h=32, sag=6, phase=1):
    r = (h * h / 4 + sag * sag) / (2 * sag)
    segs = []; x = x0; k = 0
    while x < x1 - 0.01:
        up = (k % 2 == 0) == (phase == 1)
        c = (x + h / 2, y + (r - sag) if up else y - (r - sag))
        segs.append(make_arc(c, r, (x, y), (x + h, y), (lambda m: -m[1]) if up else (lambda m: m[1])))
        x += h; k += 1
    return segs


def lines_to_segs(els):
    out = []
    for el in els:
        nums = [float(v) for v in re.findall(r'-?\d*\.?\d+', el.split('d="')[1])]
        pts = list(zip(nums[0::2], nums[1::2]))
        out.append([Seg(pts[i], pts[i + 1]) for i in range(len(pts) - 1)])
    return out


def moon_pair(c, r):
    """Outer/inner circles of the library moon scaled to outer radius r at centre c."""
    k = r / 88
    return (c, r), ((c[0] + 56.1 * k, c[1] - 52 * k), 72 * k)


def crescent_segs(o, i):
    (oc, orr), (ic, ir) = o, i
    xa, xb = circle_x(oc, orr, ic, ir)
    a_out = make_arc(oc, orr, xa, xb, lambda m: dist(m, ic))
    a_in = make_arc(ic, ir, xb, xa, lambda m: -dist(m, oc))
    return [a_out, a_in]

# ------------------------------------------------------------------ precipitation for the small cloud (bottom 148.8)
def rain(xs, y0=180, y1=212, slant=16):
    return [L(x, y0, x - slant * (y1 - y0) / 32, y1) for x in xs]


BOLT = lambda dx=0, dy=0: PL([(140 + dx, 172 + dy), (116 + dx, 200 + dy), (144 + dx, 200 + dy), (124 + dx, 224 + dy)])


def flake(cx, cy, r=18):
    return [L(*polar((cx, cy), r, a), *polar((cx, cy), r, a + 180)) for a in (90, 30, 150)]


# ================================================================== icons
T = 'Weather'

# --- cloud + precipitation (reuse cloud-rain's cloud)
icon('cloud-drizzle', T, ['drizzle', 'light rain', 'cloud', 'rain', 'shower'],
     line=[SC] + rain([96, 136, 176], 178, 190) + rain([84, 124, 164], 206, 218), area=[SC])

icon('cloud-hail', T, ['hail', 'ice', 'storm', 'weather'],
     line=[SC] + rain([88, 128, 168], 176, 188),
     dot=[C(100, 214, 14), C(140, 214, 14), C(180, 214, 14)], area=[SC])

icon('cloud-haze', T, ['haze', 'smog', 'mist', 'weather'],
     line=[SC, L(56, 184, 112, 184), L(148, 184, 200, 184), L(80, 216, 120, 216), L(156, 216, 176, 216)], area=[SC])

icon('cloud-lightning-rain', T, ['thunderstorm', 'storm', 'rain', 'lightning'],
     line=[SC, BOLT(-8, 0)] + rain([84, 180], 180, 212), area=[SC])

icon('cloud-rain-heavy', T, ['heavy rain', 'downpour', 'storm', 'showers', 'cloud'],
     line=[SC] + rain([80, 116, 152, 188], 176, 220, 12), area=[SC])

icon('cloud-sleet', T, ['sleet', 'snow', 'rain', 'ice', 'rain and snow'],
     line=[SC] + rain([84, 184], 180, 212) + flake(130, 196, 22), area=[SC])

SCW = cloud(0.8, 20.8, -12.8)
icon('cloud-wind', T, ['windy', 'cloud', 'wind', 'breeze'],
     line=[SCW, P('M40 212 H182 A18 18 0 1 0 164 194'), L(64, 176, 136, 176)], area=[SCW])

# --- big cloud with inner mark (like cloud-check / cloud-warning)
icon('cloud-info', T, ['cloud', 'info', 'status', 'details'],
     line=[BC], detail=[L(128, 140, 128, 166)], dotcut=[C(128, 110, 11)], area=[BC])
icon('cloud-x', T, ['cloud error', 'offline', 'cloud', 'x', 'sync failed'],
     line=[BC], detail=[L(110, 124, 146, 160), L(146, 124, 110, 160)], area=[BC])

# --- cloud with lock badge (cloud shifted like cloud-gear, trimmed around the badge)
def badge_cloud(cx=184, cy=192, R=60):
    segs = cloud_segs(1, -8, -16)
    ins = lambda p: dist(p, (cx, cy)) < R
    run = clip(segs, ins)[0]
    d = run_d(run)
    start = run[0][0].point(run[0][1]); end = run[-1][0].point(run[-1][2])
    cin = shape_inside(segs)
    area = d + ' ' + arc_to((cx, cy), R, end, start, lambda m: 1 if cin(m) else -1) + ' Z'
    return d, area

cl_line, cl_area = badge_cloud()
LOCK_BODY = R(156, 180, 56, 40, 8)
icon('cloud-lock', T, ['secure cloud', 'private', 'storage', 'lock', 'encrypted'],
     line=[P(cl_line), LOCK_BODY, P('M169 180 V166 A15 15 0 0 1 199 166 V180')], area=[P(cl_area), LOCK_BODY])
op = polar((184, 166), 15, -20)
icon('cloud-lock-open', 'Security', ['unlocked cloud', 'public', 'shared', 'open'],
     line=[P(cl_line), LOCK_BODY, P(f'M169 180 V166 A15 15 0 0 1 {pt(op)}')], area=[P(cl_area), LOCK_BODY])

# --- sun / moon peeking behind a cloud, precipitation below
WC = cloud_segs(0.7, 59, 25.6)          # x 90..216, top 65, bottom 160
WC_IN = shape_inside(WC)
WC_D = P(shape_d(WC))
sun_c, sun_r = (98, 96), 28
SUN_PART = dict(line=clipped(circle_segs(sun_c, sun_r), WC_IN) +
                [L(*polar(sun_c, 46, a), *polar(sun_c, 62, a)) for a in (135, 180, 225, 270)],
                area=[C(*sun_c, sun_r)])
mo, mi = moon_pair((90, 98), 42)
MOON_SEGS = crescent_segs(mo, mi)
MOON_PART = dict(line=clipped(MOON_SEGS, WC_IN), area=[P(shape_d(MOON_SEGS))])
CLOUD_PART = dict(line=[WC_D], area=[WC_D])

def under(kind):
    if kind == 'rain':
        return dict(line=rain([128, 164, 200], 188, 216, 14))
    if kind == 'lightning':
        return dict(line=[PL([(166, 182), (144, 204), (170, 204), (152, 224)])])
    if kind == 'hail':
        return dict(line=rain([128, 164, 200], 184, 196, 14), dot=[C(136, 216, 14), C(172, 216, 14), C(208, 216, 14)])

TAGS = {('sun', 'rain'): ['showers', 'sun', 'rain', 'partly cloudy'],
        ('sun', 'lightning'): ['thunderstorm', 'sun', 'lightning', 'storm'],
        ('sun', 'hail'): ['hail', 'sun', 'storm', 'weather'],
        ('moon', 'rain'): ['rain', 'night', 'moon', 'showers'],
        ('moon', 'lightning'): ['thunderstorm', 'night', 'moon', 'lightning'],
        ('moon', 'hail'): ['hail', 'night', 'moon', 'weather']}
for nm, part in (('sun', SUN_PART), ('moon', MOON_PART)):
    for kind in ('rain', 'lightning', 'hail'):
        icon(f'cloud-{nm}-{kind}', T, TAGS[(nm, kind)], **merge(CLOUD_PART, part, under(kind)))

# --- clouds: big front cloud lower-left, smaller cloud behind upper-right
front = cloud_segs(0.8, 0, 56)
back = cloud_segs(0.62, 80, 4)
icon('clouds', T, ['cloudy', 'overcast', 'clouds', 'weather'],
     line=[P(shape_d(front))] + clipped(back, shape_inside(front)),
     area=[P(shape_d(front)), P(shape_d(back))])

# --- rainbow over a cloud
rb_cloud = cloud_segs(0.56, 96, 108)
rb_in = shape_inside(rb_cloud)
rb_arcs = []
for r in (96, 64, 32):
    rb_arcs += clipped([make_arc((128, 172), r, (128 - r, 172), (128 + r, 172), lambda m: -m[1])], rb_in, closed=False)
icon('rainbow-cloud', T, ['rainbow', 'after rain', 'weather'],
     line=rb_arcs + [P(shape_d(rb_cloud))],
     area=[P(shape_d(rb_cloud))])

# --- temperature units
icon('celsius', T, ['celsius', 'temperature', 'degrees', 'metric'],
     line=[C(60, 76, 20), P(f'M{pt(polar((168, 136), 64, -48))} ' + f'A64 64 0 1 0 {pt(polar((168, 136), 64, 48))}')])
icon('fahrenheit', T, ['fahrenheit', 'temperature', 'degrees', 'imperial'],
     line=[C(60, 76, 20), PL([(200, 72), (120, 72), (120, 200)]), L(120, 136, 184, 136)])

# --- cyclone
def cyclone_lines(r=32, R=76, end=-64):
    c = (128, 128)
    a1c = (c[0] - r + R, c[1])
    t1 = polar(a1c, R, end)
    arm1 = P(f'M{pt(t1)} ' + arc_to(a1c, R, t1, (c[0] - r, c[1]), lambda m: -m[1]))
    a2c = (c[0] + r - R, c[1])
    t2 = polar(a2c, R, end + 180)
    arm2 = P(f'M{pt(t2)} ' + arc_to(a2c, R, t2, (c[0] + r, c[1]), lambda m: m[1]))
    return [C(*c, r), arm1, arm2]

icon('cyclone', T, ['cyclone', 'hurricane', 'typhoon', 'storm', 'tropical storm'], line=cyclone_lines())
icon('cyclone-slash', T, ['cyclone', 'off', 'disabled', 'hidden'], line=cyclone_lines() + [SLASH])

# --- thermometers
THERMO = load('thermometer')
TUBE = THERMO['line'][0]
TICKS = THERMO['line'][1:]
def thermo_level(y):
    return dict(line=[TUBE] + TICKS, detail=[L(112, 172, 112, y)], area=THERMO['area'])

icon('thermometer-low', T, ['cold', 'temperature', 'low', 'thermometer'], **thermo_level(148))
icon('thermometer-half', T, ['temperature', 'medium', 'half', 'thermometer'], **thermo_level(120))
icon('thermometer-high', T, ['hot', 'temperature', 'high', 'thermometer'], **thermo_level(76))

TS = tf_roles(dict(line=[TUBE], detail=[THERMO['detail'][0]], area=THERMO['area']), 1, -28, 0)
def thermo_with(extra_line=(), extra_area=()):
    return dict(line=TS['line'] + list(extra_line), detail=TS['detail'], area=TS['area'] + list(extra_area))

icon('thermometer-cold', T, ['cold', 'freezing', 'snow', 'thermometer', 'temperature'],
     **thermo_with(flake(180, 82, 30)))
sunc = (180, 80)
icon('thermometer-hot', T, ['hot', 'heat', 'sun', 'thermometer', 'temperature'],
     **thermo_with([C(*sunc, 14)] + [L(*polar(sunc, 34, a), *polar(sunc, 44, a)) for a in (0, 45, 90, 135, 225, 270, 315)],
                   extra_area=[C(*sunc, 14)]))
icon('thermometer-plus', T, ['temperature up', 'increase', 'warmer', 'thermometer', 'plus'],
     **thermo_with([L(180, 56, 180, 104), L(156, 80, 204, 80)]))
icon('thermometer-minus', T, ['temperature down', 'decrease', 'cooler', 'thermometer', 'minus'],
     **thermo_with([L(156, 80, 204, 80)]))

# dew point: thermometer + drop
DROP_S = 'M184 92 C172 108 152 134 152 158 A32 32 0 0 0 216 158 C216 134 196 108 184 92 Z'
icon('dew-point', T, ['humidity', 'dew', 'condensation'], **thermo_with([P(DROP_S)], extra_area=[P(DROP_S)]))

# --- drops
DROP = load('drop')['line'][0]
icon('drop-slash', T, ['no water', 'dry', 'drop', 'slash', 'water off'], line=[DROP, SLASH])
D1 = 'M100 76 C82 102 44 138 44 172 A52 52 0 0 0 148 172 C148 138 118 102 100 76 Z'
D2 = 'M184 32 C174 46 154 70 154 90 A30 30 0 0 0 214 90 C214 70 194 46 184 32 Z'
icon('drops', T, ['raindrops', 'moisture', 'humidity', 'water', 'liquid'], line=[P(D1), P(D2)], area=[P(D1), P(D2)])
icon('humidity', T, ['humidity', 'moisture', 'percent', 'drop', 'water'],
     line=[DROP], detail=[L(152, 124, 104, 188)], dotcut=[C(104, 130, 12), C(152, 182, 12)], area=[DROP])

# --- earthquake: seismogram
icon('earthquake', T, ['earthquake', 'seismic', 'tremor', 'disaster'],
     line=[PL([(32, 128), (48, 128), (64, 104), (84, 156), (108, 60), (136, 196), (164, 76), (186, 152), (202, 112), (214, 128), (224, 128)])])

# --- eclipse
moon_c, moon_r = (152, 112), 72
esun_c, esun_r = (100, 148), 68
front_m = circle_segs(moon_c, moon_r)
icon('eclipse', T, ['eclipse', 'moon', 'sun', 'astronomy'],
     line=[C(*moon_c, moon_r)] + clipped(circle_segs(esun_c, esun_r), shape_inside(front_m)),
     area=[C(*moon_c, moon_r)])

# --- flood
FH = 'M64 102 L128 50 L192 102 V144 H64 Z'
icon('flood', T, ['flood', 'water', 'disaster', 'house'],
     line=[P('M64 102 V144'), P('M192 102 V144'), PL([(40, 120), (128, 46), (216, 120)]),
           wave(32, 224, 178, 32, 12), wave(32, 224, 216, 32, 12)],
     area=[FH])

# --- heat waves
def vwave(x, y0, y1, h=44, a=16):
    d = f'M{f(x)} {f(y0)}'; y = y0; k = 0
    while y > y1 + 0.01:
        ny = max(y - h, y1)
        sgn = -1 if k % 2 == 0 else 1
        d += f' Q{f(x + sgn * a)} {f((y + ny) / 2)} {f(x)} {f(ny)}'
        y = ny; k += 1
    return P(d)
icon('heat-waves', T, ['heat', 'heating', 'hot', 'warm'],
     line=[vwave(80, 212, 36), vwave(128, 212, 36), vwave(176, 212, 36)])

# --- mist (arc waves so the slash variant can trim them)
MIST_SEGS = [wave_arcs(48, 208, 56, 40, 5), wave_arcs(32, 192, 104, 40, 5), wave_arcs(64, 224, 152, 40, 5), wave_arcs(48, 168, 200, 40, 5)]
icon('mist', T, ['mist', 'haze', 'fog', 'weather'], line=[P(shape_d(s, False)) for s in MIST_SEGS])
icon('mist-slash', T, ['mist', 'off', 'disabled', 'hidden'],
     line=sum([clipped(s, SLASH_GAP, closed=False, min_len=26) for s in MIST_SEGS], []) + [SLASH])

# --- moon / sun above fog
MOON = load('moon')['line'][0]
MF = tf_el(MOON, 0.66, 40, 4)
icon('moon-fog', T, ['foggy night', 'fog', 'moon', 'mist', 'haze'],
     line=[MF, L(48, 188, 208, 188), L(80, 220, 176, 220)], area=[MF])
sfc = (128, 102)
icon('sun-fog', T, ['foggy', 'haze', 'sun', 'mist'],
     line=[C(*sfc, 28)] + [L(*polar(sfc, 50, a), *polar(sfc, 64, a)) for a in (0, 45, 135, 180, 225, 270, 315)]
     + [L(40, 188, 216, 188), L(72, 220, 184, 220)],
     area=[C(*sfc, 28)])

# --- moonset: crescent half under the horizon, arrow pointing down
HZ = 180
mso, msi = moon_pair((100, 140), 64)
MS = crescent_segs(mso, msi)
ms_runs = clip(MS, lambda p: p[1] > HZ - 0.01)
ms_line = [P(run_d(r)) for r in ms_runs]
ms_area = [P(run_d(r) + ' Z') for r in ms_runs]
icon('moonset', T, ['moonset', 'moon', 'horizon', 'night'],
     line=ms_line + [L(32, HZ, 224, HZ), L(88, 214, 168, 214), L(192, 40, 192, 120), PL([(168, 96), (192, 120), (216, 96)])],
     area=ms_area)

# --- sandstorm
icon('sandstorm', T, ['sandstorm', 'dust', 'haze', 'wind'],
     line=[L(56, 76, 152, 76), L(88, 128, 216, 128), L(32, 180, 120, 180)],
     dot=[C(196, 76, 16), C(44, 128, 16), C(164, 180, 16), C(208, 180, 16)])

# --- snowflake slash (arms trimmed around the slash)
SF = lines_to_segs(load('snowflake')['line'])
icon('snowflake-slash', T, ['cooling off', 'ac off', 'no snow', 'cold off'],
     line=sum([clipped(s, SLASH_GAP, closed=False, min_len=26) for s in SF], []) + [SLASH])

# --- sun + moon split by a diagonal
s_c = (84, 84)
smo, smi = moon_pair((172, 176), 44)
SM = crescent_segs(smo, smi)
icon('sun-moon', T, ['day night', 'light dark', 'theme', 'cycle'],
     line=[C(*s_c, 22)] + [L(*polar(s_c, 38, a), *polar(s_c, 50, a)) for a in (0, 90, 135, 180, 225, 270, 315)]
     + [P(shape_d(SM)), L(208, 48, 48, 208)],
     area=[C(*s_c, 22), P(shape_d(SM))])

# --- sun slash
SUN = load('sun')
icon('sun-slash', T, ['sun', 'off', 'disabled', 'hidden'],
     line=[SUN['line'][0]] + [l for i, l in enumerate(SUN['line'][1:]) if i not in (1, 5)] + [SLASH])

# --- sun + wind
swc = (92, 92)
icon('sun-wind', T, ['sunny windy', 'breeze', 'weather', 'sun'],
     line=[C(*swc, 24)] + [L(*polar(swc, 42, a), *polar(swc, 56, a)) for a in (135, 180, 225, 270, 315, 0, 45)]
     + [P('M104 168 H184 A20 20 0 1 0 164 148'), L(48, 208, 200, 208)],
     area=[C(*swc, 24)])

# --- tsunami
icon('tsunami', T, ['tsunami', 'wave', 'disaster', 'flood'],
     line=[P('M32 168 C48 104 96 56 160 56 C200 56 224 80 224 112 C224 136 204 152 180 152 C156 152 144 132 152 112'),
           wave(32, 224, 206, 32, 12)])

# --- uv index
uvc = (128, 86)
icon('uv-index', T, ['uv index', 'ultraviolet', 'sun', 'exposure'],
     line=[C(*uvc, 20)] + [L(*polar(uvc, 40, a), *polar(uvc, 50, a)) for a in range(0, 360, 45)]
     + [P('M56 164 V190 A28 28 0 0 0 112 190 V164'), PL([(144, 164), (172, 218), (200, 164)])],
     area=[C(*uvc, 20)])

# --- whirl: three nested open arcs, openings staggered
wc = (128, 128)
whirl = []
for r, a0 in ((96, 200), (60, 320), (24, 80)):
    p = polar(wc, r, a0); q = polar(wc, r, a0 + 250)
    whirl.append(P(f'M{pt(p)} A{r} {r} 0 1 1 {pt(q)}'))
icon('whirl', T, ['whirl', 'swirl', 'vortex', 'spiral'], line=whirl)

# --- air quality: gauge above wavy air lines
gc = (128, 96); gr = 60
g0 = polar(gc, gr, 135); g1 = polar(gc, gr, 45)
GA = f'M{pt(g0)} A{gr} {gr} 0 1 1 {pt(g1)} Z'
icon('air-quality', T, ['aqi', 'pollution', 'smog', 'air'],
     line=[P(GA), wave(40, 216, 178, 32, 12), wave(40, 216, 216, 32, 12)],
     detail=[L(128, 104, 152, 76)], dotcut=[C(128, 104, 14)], area=[P(GA)])

print(save(overwrite=True))
