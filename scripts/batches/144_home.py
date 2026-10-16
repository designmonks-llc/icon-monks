import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

H, HM, PE = 'Health', 'Home', 'People'
SLASH = L(48, 48, 208, 208)
SG = 32  # centerline clearance kept between the slash and the strokes it crosses


# ---------------------------------------------------------------- slash gapping (exact path splitting)
def _attrs(el):
    return {k: v for k, v in re.findall(r'([\w-]+)="([^"]*)"', el)}


def el_d(el):
    a = _attrs(el)
    g = lambda k, d=0: float(a.get(k, d))
    if el.startswith('<path'):
        return a['d']
    if el.startswith('<circle') or el.startswith('<ellipse'):
        cx, cy = g('cx'), g('cy')
        rx = g('r') if el.startswith('<circle') else g('rx')
        ry = g('r') if el.startswith('<circle') else g('ry')
        return f'M{f(cx - rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx + rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx - rx)} {f(cy)} Z'
    if el.startswith('<rect'):
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        r = min(g('rx'), w / 2, h / 2)
        if not r:
            return f'M{f(x)} {f(y)} H{f(x + w)} V{f(y + h)} H{f(x)} Z'
        return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
                f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
                f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')
    raise ValueError(el)


def _ang(u, v):
    a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    return a


def parse(d):
    """Absolute M L H V C A Z -> list of subpaths [(segments, closed)]."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cmd = None; cur = (0, 0); start = (0, 0); subs = []; segs = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                subs.append((segs, True)); segs = None; cur = start
                continue
        if cmd == 'M':
            if segs:
                subs.append((segs, False))
            cur = start = (num(), num()); segs = []; cmd = 'L'
        elif cmd == 'L':
            p = (num(), num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'H':
            p = (num(), cur[1]); segs.append(('L', cur, p)); cur = p
        elif cmd == 'V':
            p = (cur[0], num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); p = (num(), num())
            segs.append(('C', cur, c1, c2, p)); cur = p
        elif cmd == 'A':
            rx, ry, _, fa, fs = num(), num(), num(), num(), num(); p = (num(), num())
            x1p, y1p = (cur[0] - p[0]) / 2, (cur[1] - p[1]) / 2
            lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
            if lam > 1:
                rx *= math.sqrt(lam); ry *= math.sqrt(lam)
            num_ = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
            den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
            co = math.sqrt(max(0, num_ / den)) * (-1 if fa == fs else 1)
            cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
            cx, cy = cxp + (cur[0] + p[0]) / 2, cyp + (cur[1] + p[1]) / 2
            u = ((x1p - cxp) / rx, (y1p - cyp) / ry); v = ((-x1p - cxp) / rx, (-y1p - cyp) / ry)
            t1 = math.atan2(u[1], u[0]); dt = _ang(u, v)
            if fs == 0 and dt > 0: dt -= 2 * math.pi
            if fs == 1 and dt < 0: dt += 2 * math.pi
            segs.append(('A', (cx, cy), rx, ry, t1, t1 + dt)); cur = p
    if segs:
        subs.append((segs, False))
    return subs


def at(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    if s[0] == 'C':
        p0, p1, p2, p3 = s[1:]
        m = 1 - t
        return tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))
    a = s[4] + (s[5] - s[4]) * t
    return (s[1][0] + s[2] * math.cos(a), s[1][1] + s[3] * math.sin(a))


def subseg(s, t0, t1):
    if s[0] == 'L':
        return ('L', at(s, t0), at(s, t1))
    if s[0] == 'A':
        return ('A', s[1], s[2], s[3], s[4] + (s[5] - s[4]) * t0, s[4] + (s[5] - s[4]) * t1)
    def split(p, t):
        p0, p1, p2, p3 = p
        l = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        a, b, c = l(p0, p1), l(p1, p2), l(p2, p3)
        d, e = l(a, b), l(b, c)
        g = l(d, e)
        return (p0, a, d, g), (g, e, c, p3)
    pts = s[1:]
    if t1 < 1:
        pts = split(pts, t1)[0]
    if t0 > 0:
        pts = split(pts, t0 / t1)[1]
    return ('C',) + tuple(pts)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    dt = s[5] - s[4]
    end = at(s, 1)
    if abs(s[2] - s[3]) < 1e-6:
        r = f(s[2]); rr = f'{r} {r}'
    else:
        rr = f'{f(s[2])} {f(s[3])}'
    return f'A{rr} 0 {1 if abs(dt) > math.pi else 0} {1 if dt > 0 else 0} {pt(end)}'


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gap(el, g=SG, keep=None):
    """Return path elements of el with everything within g of the slash removed."""
    keep = keep or (lambda p: seg_dist(p) >= g)
    out = []
    for segs, closed in parse(el_d(el)):
        pieces = []  # (seg index, t0, t1)
        for si, s in enumerate(segs):
            N = 240
            ks = [keep(at(s, j / N)) for j in range(N + 1)]
            j = 0
            while j <= N:
                if not ks[j]:
                    j += 1; continue
                k = j
                while k < N and ks[k + 1]:
                    k += 1
                def refine(lo, hi):  # lo kept, hi not
                    for _ in range(40):
                        m = (lo + hi) / 2
                        if keep(at(s, m)): lo = m
                        else: hi = m
                    return lo
                t0 = j / N if j == 0 else refine(j / N, (j - 1) / N)
                t1 = k / N if k == N else refine(k / N, (k + 1) / N)
                if t1 - t0 > 1e-4:
                    pieces.append((si, t0, t1))
                j = k + 1
        # join pieces into runs
        runs = []
        for pc in pieces:
            if runs and runs[-1][-1][0] == pc[0] - 1 and runs[-1][-1][2] > 1 - 1e-9 and pc[1] < 1e-9:
                runs[-1].append(pc)
            else:
                runs.append([pc])
        if not runs:
            continue
        full = len(runs) == 1 and len(runs[0]) == len(segs) and runs[0][0][1] < 1e-9 and runs[0][-1][2] > 1 - 1e-9
        if closed and not full and len(runs) > 1 and runs[0][0][0] == 0 and runs[0][0][1] < 1e-9 \
                and runs[-1][-1][0] == len(segs) - 1 and runs[-1][-1][2] > 1 - 1e-9:
            runs[0] = runs.pop() + runs[0]
        for run in runs:
            ss = [subseg(segs[si], t0, t1) for si, t0, t1 in run]
            if sum(dist(at(s, 0), at(s, 0.5)) + dist(at(s, 0.5), at(s, 1)) for s in ss) < 12:
                continue
            d = f'M{pt(at(ss[0], 0))} ' + ' '.join(seg_cmd(s) for s in ss)
            if full and closed:
                d += ' Z'
            out.append(P(d))
    return out


def slashed(src, g=SG, drop_dots=True):
    """Slash variant: area left out, details become lines, every stroke opened around the slash."""
    lines = []
    for el in src.get('line', []) + src.get('detail', []):
        lines += gap(el, g)
    dots = []
    for el in src.get('dot', []) + src.get('dotcut', []):
        a = _attrs(el)
        c, r = (float(a['cx']), float(a['cy'])), float(a['r'])
        if not drop_dots or seg_dist(c) >= g + r * 0.75:
            dots.append(el)
    return dict(line=lines + [SLASH], dot=dots)


# ================================================================ Health
# ---------------------------------------------------------------- stomach
st_in = 'M108 32 V80 C108 124 92 144 48 144'
st_out = 'M148 32 V60 C164 48 216 52 216 120 C216 184 168 216 120 216 C92 216 72 192 48 184'
st_area = 'M148 24 V60 C164 48 216 52 216 120 C216 184 168 216 120 216 C92 216 72 192 48 184 L40 184 L40 144 L48 144 C92 144 108 124 108 80 V24 Z'
icon('stomach', H, ['stomach', 'abdomen', 'digestion', 'organ'],
     line=[P(st_in), P(st_out)], detail=[P('M176 112 C180 148 164 172 132 180')], area=[P(st_area)])

# ---------------------------------------------------------------- stretcher
icon('stretcher', H, ['stretcher', 'gurney', 'emergency', 'ambulance', 'hospital'],
     line=[P('M48 120 V84 A16 16 0 0 1 64 68 H192 A16 16 0 0 1 208 84 V120'), L(32, 120, 224, 120),
           L(80, 120, 176, 184), L(176, 120, 80, 184)],
     area=[P('M48 120 V84 A16 16 0 0 1 64 68 H192 A16 16 0 0 1 208 84 V120 Z')],
     dot=[C(80, 192, 16), C(176, 192, 16)])

# ---------------------------------------------------------------- syringe-slash
icon('syringe-slash', H, ['syringe', 'off', 'disabled', 'hidden'], **slashed(load('syringe')))

# ---------------------------------------------------------------- thermometer-infrared
gun = ('M120 64 H208 A16 16 0 0 1 224 80 V112 A16 16 0 0 1 208 128 H200 L208 192 A16 16 0 0 1 192 208 H176 '
       'A16 16 0 0 1 160 192 L152 128 H120 A16 16 0 0 1 104 112 V80 A16 16 0 0 1 120 64 Z')
ti_c = (112, 96)
ti_arcs = [P(f'M{pt(polar(ti_c, r, 148))} A{r} {r} 0 0 1 {pt(polar(ti_c, r, 212))}') for r in (40, 72)]
icon('thermometer-infrared', H, ['infrared thermometer', 'temperature gun', 'fever', 'scan'],
     line=[P(gun)] + ti_arcs, detail=[L(144, 96, 184, 96)], area=[P(gun)])

# ---------------------------------------------------------------- thyroid
thy = ('M128 128 C112 128 104 112 100 88 C96 60 88 48 76 48 C56 48 40 80 40 128 C40 176 56 208 84 208 '
       'C104 208 112 184 128 184 C144 184 152 208 172 208 C200 208 216 176 216 128 C216 80 200 48 180 48 '
       'C168 48 160 60 156 88 C152 112 144 128 128 128 Z')
icon('thyroid', H, ['endocrine', 'thyroid', 'gland', 'hormone'], line=[P(thy)], area=[P(thy)])

# ---------------------------------------------------------------- tooth
tooth = load('tooth')
icon('tooth-broken', H, ['tooth broken', 'dental', 'teeth', 'dentist', 'tooth'],
     line=tooth['line'], detail=[PL([(128, 56), (112, 84), (144, 104), (120, 128)])], area=tooth['area'])
icon('tooth-slash', H, ['tooth', 'disabled', 'off', 'dental', 'teeth'], **slashed(tooth))

# ---------------------------------------------------------------- uterus
ut = 'M88 88 C88 72 104 64 128 64 C152 64 168 72 168 88 C168 128 152 152 144 168 V200 H112 V168 C104 152 88 128 88 88 Z'
icon('uterus', H, ['uterus', 'womb', 'gynecology', 'reproductive'],
     line=[P(ut), P('M90 80 C72 64 44 68 40 96'), P('M166 80 C184 64 212 68 216 96'), C(56, 132, 16), C(200, 132, 16)],
     area=[P(ut), C(56, 132, 16), C(200, 132, 16)])

# ---------------------------------------------------------------- vaccine vial
vial = 'M104 68 V80 C104 92 80 96 80 112 V208 A16 16 0 0 1 96 224 H160 A16 16 0 0 1 176 208 V112 C176 96 152 92 152 80 V68'
VIAL = dict(line=[R(84, 32, 88, 36, 10), P(vial)], detail=[L(108, 148, 148, 148), L(108, 184, 148, 184)],
            area=[R(84, 32, 88, 36, 10), P(vial + ' Z')])
icon('vaccine-vial', H, ['vaccine vial', 'medicine', 'bottle', 'dose'], **VIAL)
icon('vaccine-vial-slash', H, ['vaccine vial', 'off', 'disabled', 'hidden', 'vaccine'], **slashed(VIAL))

# ---------------------------------------------------------------- virus
mg = load('magnifying-glass')
vc = (112, 112)
vspikes = [L(*polar(vc, 22, a), *polar(vc, 42, a)) for a in range(-90, 270, 60)]
icon('virus-magnifying-glass', H, ['virus scan', 'testing', 'diagnosis', 'search'],
     line=mg['line'], detail=[C(*vc, 22)] + vspikes, area=mg['area'])
icon('virus-slash', H, ['virus free', 'antivirus', 'no germs', 'slash'], **slashed(load('virus')))

# ---------------------------------------------------------------- walker
icon('walker', H, ['walker', 'mobility aid', 'elderly', 'assist'],
     line=[C(84, 52, 24), L(88, 96, 84, 148), PL([(90, 108), (116, 136), (148, 120)]),
           L(84, 148, 108, 216), L(84, 148, 56, 216),
           PL([(140, 216), (152, 120), (196, 120), (212, 216)]), L(146, 168, 204, 168)],
     area=[C(84, 52, 24)])

# ---------------------------------------------------------------- walking-cane
cn = rot([(172, 224), (172, 84), (84, 84), (84, 104)], -12, (128, 140))
icon('walking-cane', H, ['cane', 'walking stick', 'elderly', 'mobility'],
     line=[P(f'M{pt(cn[0])} L{pt(cn[1])} A44 44 0 0 0 {pt(cn[2])} L{pt(cn[3])}')])

# ---------------------------------------------------------------- wheelchair-motion
wm_c, wm_r = (112, 164), 52
wm_a = polar(wm_c, wm_r, -60); wm_b = polar(wm_c, wm_r, 20)
icon('wheelchair-motion', H, ['accessibility', 'accessible', 'disabled', 'wheelchair', 'active wheelchair'],
     line=[P(f'M{pt(wm_a)} A{wm_r} {wm_r} 0 1 0 {pt(wm_b)}'),
           PL([(156, 92), (120, 140), (172, 144), (196, 200)]), PL([(140, 112), (184, 104)]),
           L(32, 128, 56, 128), L(32, 168, 48, 168)],
     dot=[C(176, 60, 16)])
icon('wheelchair-slash', H, ['not accessible', 'no wheelchair', 'inaccessible', 'accessibility', 'wheelchair'],
     **slashed(load('wheelchair')))

# ---------------------------------------------------------------- x-ray
ribs = []
for y in (92, 128, 164):
    ribs.append(P(f'M128 {y} C108 {y} 84 {y + 4} 76 {y + 20}'))
    ribs.append(P(f'M128 {y} C148 {y} 172 {y + 4} 180 {y + 20}'))
icon('x-ray', H, ['radiology', 'scan', 'bones', 'imaging'],
     line=[R(32, 40, 192, 176, 16)], detail=[L(128, 72, 128, 188)] + ribs, area=[R(32, 40, 192, 176, 16)])

# ================================================================ Home
# ---------------------------------------------------------------- air conditioner
AC = dict(line=[R(32, 48, 192, 88, 16), L(88, 172, 80, 208), L(128, 172, 128, 216), L(168, 172, 176, 208)],
          detail=[L(64, 104, 192, 104)], area=[R(32, 48, 192, 88, 16)])
icon('air-conditioner', HM, ['ac', 'cooling', 'climate control', 'mini split', 'climate'], **AC)
icon('air-conditioner-slash', HM, ['air conditioner', 'disabled', 'off', 'home'], **slashed(AC))

# ---------------------------------------------------------------- air freshener
af = [(128, 64), (164, 104), (148, 104), (184, 148), (164, 148), (200, 188), (140, 188), (140, 212),
      (116, 212), (116, 188), (56, 188), (92, 148), (72, 148), (108, 104), (92, 104)]
icon('air-freshener', HM, ['scent', 'fragrance', 'deodorizer', 'car'],
     line=[PG(af), L(128, 32, 128, 64)], area=[PG(af)])

# ---------------------------------------------------------------- air purifier
icon('air-purifier', HM, ['filter', 'clean air', 'appliance', 'purify'],
     line=[R(72, 88, 112, 136, 24), L(96, 32, 96, 56), L(128, 32, 128, 56), L(160, 32, 160, 56)],
     detail=[C(128, 144, 24), L(112, 192, 144, 192)], area=[R(72, 88, 112, 136, 24)])

# ---------------------------------------------------------------- armchair / couch / bed slash
icon('armchair-slash', HM, ['armchair', 'disabled', 'off', 'home'], **slashed(load('armchair')))
icon('couch-slash', HM, ['couch', 'off', 'disabled', 'hidden'], **slashed(load('couch')))
icon('bed-slash', HM, ['bed', 'disabled', 'off', 'home'], **slashed(load('bed')))

# ---------------------------------------------------------------- balcony
door = 'M88 144 V72 A40 40 0 0 1 168 72 V144'
icon('balcony', HM, ['balcony', 'terrace', 'building', 'apartment'],
     line=[P(door), L(32, 144, 224, 144), L(32, 200, 224, 200)] + [L(x, 144, x, 200) for x in (40, 84, 128, 172, 216)],
     detail=[L(128, 76, 128, 144)], area=[P(door + ' Z')])

# ---------------------------------------------------------------- barn
barn = [(48, 216), (48, 112), (72, 64), (128, 40), (184, 64), (208, 112), (208, 216)]
icon('barn', HM, ['farm', 'barn', 'agriculture'],
     line=[PG(barn)], detail=[P('M96 216 V136 H160 V216'), L(96, 136, 160, 216), L(160, 136, 96, 216)],
     area=[PG(barn)])

# ---------------------------------------------------------------- bathtub
tub = 'M48 120 V152 A48 48 0 0 0 96 200 H160 A48 48 0 0 0 208 152 V120'
TUB = dict(line=[L(32, 120, 224, 120), P(tub), L(84, 198, 76, 216), L(172, 198, 180, 216),
                 P('M64 120 V64 A24 24 0 0 1 112 64 V76')],
           area=[P(tub + ' Z')])
icon('bathtub', HM, ['bath', 'tub', 'bathroom', 'soak', 'bathtub'], **TUB)
icon('bathtub-slash', HM, ['bathtub', 'disabled', 'off', 'home'], **slashed(TUB))

# ---------------------------------------------------------------- beds
icon('bed-double', HM, ['double bed', 'hotel', 'bedroom', 'sleep'],
     line=[P('M32 208 V64 A16 16 0 0 1 48 48 H208 A16 16 0 0 1 224 64 V208'), L(32, 120, 224, 120), L(32, 176, 224, 176)],
     detail=[R(64, 84, 48, 36, 14), R(144, 84, 48, 36, 14)],
     area=[P('M32 176 V64 A16 16 0 0 1 48 48 H208 A16 16 0 0 1 224 64 V176 Z')])
icon('bed-flat', HM, ['bed', 'flat', 'rest'],
     line=[R(32, 112, 192, 56, 16), R(56, 80, 64, 32, 16), L(48, 168, 48, 200), L(208, 168, 208, 200)],
     area=[R(32, 112, 192, 56, 16), R(56, 80, 64, 32, 16)])

# ---------------------------------------------------------------- blanket
icon('blanket', HM, ['throw', 'blanket', 'bed', 'warm'],
     line=[R(32, 56, 192, 144, 24)], detail=[P('M224 104 H88 A24 24 0 0 0 88 152 H224')],
     area=[R(32, 56, 192, 144, 24)])

# ---------------------------------------------------------------- bleach
TRI = [(128, 40), (224, 208), (32, 208)]
icon('bleach', HM, ['bleach', 'laundry', 'care label', 'home'], line=[PG(TRI)], area=[PG(TRI)])
icon('bleach-slash', HM, ['bleach', 'disabled', 'off', 'laundry', 'care label'], **slashed(dict(line=[PG(TRI)])))
cl_c = (108, 164)
icon('bleach-chlorine', HM, ['bleach chlorine', 'laundry', 'bleach', 'care label', 'chlorine'],
     line=[PG(TRI)],
     detail=[P(f'M{pt(polar(cl_c, 22, -45))} A22 22 0 1 0 {pt(polar(cl_c, 22, 45))}'), L(150, 140, 150, 186)],
     area=[PG(TRI)])


def tri_dist(p):
    out = []
    for a, b in zip(TRI, TRI[1:] + TRI[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        out.append(((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / math.hypot(dx, dy))
    return min(-o for o in out)  # positive inside


def tri_chord(c, u, inset):
    pts = [(c[0] + u[0] * s, c[1] + u[1] * s) for s in [i * 0.25 for i in range(-800, 801)]]
    ok = [p for p in pts if tri_dist(p) >= inset]
    return ok[0], ok[-1]


u_left = ((128 - 32) / dist(TRI[0], TRI[2]), (40 - 208) / dist(TRI[0], TRI[2]))
nrm = (-u_left[1], u_left[0])
nc_lines = []
for s in (-18, 18):
    c0 = (128 + 10 + nrm[0] * s, 150 + nrm[1] * s)
    a, b = tri_chord(c0, u_left, 28)
    nc_lines.append(L(a[0], a[1], b[0], b[1]))
icon('bleach-no-chlorine', HM, ['bleach no chlorine', 'laundry', 'bleach', 'care label', 'no'],
     line=[PG(TRI)], detail=nc_lines, area=[PG(TRI)])

# ---------------------------------------------------------------- blender
jug = 'M52 56 H164 L148 160 H68 Z'
icon('blender', HM, ['blender', 'mixer', 'smoothie', 'kitchen', 'appliance'],
     line=[P(jug), R(52, 160, 112, 56, 14), P('M161 76 H188 A16 16 0 0 1 204 92 V124 A16 16 0 0 1 188 140 H152')],
     detail=[L(92, 128, 124, 128)], dotcut=[C(108, 188, 12)],
     area=[P(jug), R(52, 160, 112, 56, 14)])

# ---------------------------------------------------------------- blinds
icon('blinds', HM, ['window blinds', 'shades', 'window', 'privacy', 'roller shades'],
     line=[R(32, 40, 192, 176, 14)],
     detail=[L(32, 76, 224, 76), L(32, 112, 224, 112), L(32, 148, 224, 148), L(128, 148, 128, 216)],
     area=[R(32, 40, 192, 176, 14)])

# ---------------------------------------------------------------- bookshelf
icon('bookshelf', HM, ['bookshelf', 'library', 'books', 'shelf'],
     line=[R(40, 32, 176, 192, 14)],
     detail=[L(40, 128, 216, 128), L(76, 64, 76, 128), L(108, 64, 108, 128), L(140, 128, 172, 72),
             L(76, 160, 76, 224), L(108, 160, 108, 224), L(140, 160, 140, 224)],
     area=[R(40, 32, 176, 192, 14)])

# ---------------------------------------------------------------- broom


def rotp(d_pts, deg, c=(128, 128)):
    return rot(d_pts, deg, c)


BR = 30
br_handle = rotp([(128, 24), (128, 104)], BR)
br_body = rotp([(104, 104), (152, 104), (188, 216), (68, 216)], BR)
br_det = [rotp([(118, 160), (110, 216)], BR), rotp([(138, 160), (146, 216)], BR)]
icon('broom', HM, ['sweep', 'clean', 'chores'],
     line=[PL(br_handle), PG(br_body)], detail=[PL(d) for d in br_det], area=[PG(br_body)])

# ---------------------------------------------------------------- cabin
cab = [(48, 112), (128, 44), (208, 112), (208, 208), (48, 208)]
icon('cabin', HM, ['cottage', 'chalet', 'lodge', 'bungalow'],
     line=[P('M48 112 V208 H208 V112'), PL([(32, 124), (128, 40), (224, 124)])],
     detail=[L(48, 144, 208, 144), L(48, 176, 208, 176)], dotcut=[C(128, 92, 12)], area=[PG(cab)])

# ---------------------------------------------------------------- candle
flame = 'M128 32 C144 52 152 64 152 76 A24 24 0 0 1 104 76 C104 64 112 52 128 32 Z'
icon('candle', HM, ['candle', 'spa', 'relax', 'flame', 'light'],
     line=[P(flame), R(88, 128, 80, 96, 14)], area=[P(flame), R(88, 128, 80, 96, 14)])

# ---------------------------------------------------------------- chair
ch_back = 'M80 136 V48 A16 16 0 0 1 96 32 H160 A16 16 0 0 1 176 48 V136'
icon('chair', HM, ['chair', 'seat', 'furniture', 'dining chair', 'dining'],
     line=[P(ch_back), R(56, 136, 144, 36, 12), L(72, 172, 72, 224), L(184, 172, 184, 224)],
     detail=[L(112, 72, 144, 72)], area=[P(ch_back + ' Z'), R(56, 136, 144, 36, 12)])

# ---------------------------------------------------------------- chimney
roof_r = lambda x: 76 + (x - 128) * 80 / 96
icon('chimney', HM, ['chimney', 'roof', 'smoke', 'house'],
     line=[PL([(32, 156), (128, 76), (224, 156)]), P('M56 136 V216 H200 V136'),
           P(f'M152 {f(roof_r(152))} V80 H184 V{f(roof_r(184))}'), P('M168 60 C156 52 180 42 168 32')],
     area=[PG([(56, 136), (128, 76), (200, 136), (200, 216), (56, 216)])])

# ---------------------------------------------------------------- clothes rack


def garment(x, y2):
    return PG([(x, 64), (x + 18, 80), (x + 18, y2), (x - 18, y2), (x - 18, 80)])


RACK = dict(line=[P('M40 208 V48 H216 V208'), L(24 + 8, 208, 64, 208), L(192, 208, 224, 208),
                  L(96, 48, 96, 64), L(160, 48, 160, 64), garment(96, 168), garment(160, 144)],
            area=[garment(96, 168), garment(160, 144)])
icon('clothes-rack', HM, ['clothes rack', 'clothes', 'rack', 'home'], **RACK)
icon('clothes-rack-slash', HM, ['clothes rack', 'disabled', 'off', 'home'], **slashed(RACK))

# ---------------------------------------------------------------- coffee maker
cm = ('M64 32 H192 A16 16 0 0 1 208 48 V88 H104 V192 H208 V208 A16 16 0 0 1 192 224 H64 '
      'A16 16 0 0 1 48 208 V48 A16 16 0 0 1 64 32 Z')
pot = 'M136 120 H176 L188 192 H124 Z'
icon('coffee-maker', HM, ['coffee machine', 'brew', 'espresso', 'kitchen', 'appliance'],
     line=[P(cm), P(pot)], dotcut=[C(76, 140, 12)], area=[P(cm), P(pot)])

# ---------------------------------------------------------------- cooker
ck_body = 'M48 104 H208 V184 A32 32 0 0 1 176 216 H80 A32 32 0 0 1 48 184 Z'
ck_lid = 'M48 104 C48 72 80 56 128 56 C176 56 208 72 208 104'
icon('cooker', HM, ['cooker', 'rice cooker', 'kitchen', 'appliance'],
     line=[P(ck_body), P(ck_lid), R(108, 36, 40, 20, 8)], dotcut=[C(128, 160, 16)],
     area=[P(ck_body), P(ck_lid + ' Z'), R(108, 36, 40, 20, 8)])


# ---------------------------------------------------------------- cottage
def bez(p0, p1, p2, p3, t):
    m = 1 - t
    return tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))


def bez_y_at(x, ps):
    lo, hi = 0, 1
    for _ in range(60):
        mid = (lo + hi) / 2
        if bez(*ps, mid)[0] < x: lo = mid
        else: hi = mid
    return bez(*ps, lo)[1]


RR = ((128, 48), (176, 48), (216, 88), (224, 136))
roof = 'M32 136 C40 88 80 48 128 48 C176 48 216 88 224 136 Z'
icon('cottage', HM, ['cottage', 'cabin', 'house'],
     line=[P(roof), P('M56 136 V208 H200 V136'), P('M108 208 V172 A20 20 0 0 1 148 172 V208'),
           P(f'M160 {f(bez_y_at(160, RR))} V40 H192 V{f(bez_y_at(192, RR))}')],
     hole=[P('M116 208 V172 A12 12 0 0 1 140 172 V208 Z')],
     area=[P(roof), R(56, 136, 144, 72)])

# ---------------------------------------------------------------- crib
icon('crib', HM, ['crib', 'cot', 'baby bed', 'nursery', 'baby'],
     line=[L(40, 48, 40, 216), L(216, 48, 216, 216), L(40, 80, 216, 80), L(40, 176, 216, 176)]
          + [L(x, 80, x, 176) for x in (74, 110, 146, 182)])

# ---------------------------------------------------------------- crib mobile
star5 = [polar((60, 136), 28 if i % 2 == 0 else 12, -90 + i * 36) for i in range(10)]
mo_c = (196, 136)
moon_a, moon_b = circle_x(mo_c, 26, (212, 124), 22)
moon = P(f'M{pt(moon_a)} ' + arc_to(mo_c, 26, moon_a, moon_b, lambda m: -m[0]) + ' '
         + arc_to((212, 124), 22, moon_b, moon_a, lambda m: -m[0]) + ' Z')
icon('crib-mobile', PE, ['mobile', 'crib', 'nursery', 'baby'],
     line=[L(128, 32, 128, 72), L(60, 72, 196, 72), L(60, 72, 60, 108), L(196, 72, 196, 110), L(128, 72, 128, 160),
           PG(star5), C(128, 184, 24), moon],
     area=[PG(star5), C(128, 184, 24), moon])

# ---------------------------------------------------------------- curtains
cur_l = 'M48 40 V216 H96 C88 176 72 152 72 128 C72 104 88 72 104 40'
cur_r = 'M208 40 V216 H160 C168 176 184 152 184 128 C184 104 168 72 152 40'
icon('curtains', HM, ['curtains', 'drapes', 'window', 'theater'],
     line=[L(32, 40, 224, 40), P(cur_l), P(cur_r)], area=[P(cur_l + ' Z'), P(cur_r + ' Z')])

print(save(overwrite=True))
