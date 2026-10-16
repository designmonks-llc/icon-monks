import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

# ---------------------------------------------------------------- helpers

def xf_d(d, s=1.0, deg=0.0, c=(128, 128), tx=0.0, ty=0.0):
    """Scale by s and rotate by deg around c, then translate. Absolute M L H V C Q A Z only."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)

    def tp(x, y):
        dx, dy = (x - c[0]) * s, (y - c[1]) * s
        return (c[0] + dx * ca - dy * sa + tx, c[1] + dx * sa + dy * ca + ty)

    toks = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', d)
    out = []
    i = 0
    cmd = None
    cur = (0, 0)
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                out.append('Z')
                continue
        n = lambda k: float(toks[i + k])
        if cmd in 'ML':
            cur = (n(0), n(1)); out.append(f'{cmd}{pt(tp(*cur))}'); i += 2
            if cmd == 'M':
                cmd = 'L'
        elif cmd == 'H':
            cur = (n(0), cur[1]); out.append(f'L{pt(tp(*cur))}'); i += 1
        elif cmd == 'V':
            cur = (cur[0], n(0)); out.append(f'L{pt(tp(*cur))}'); i += 1
        elif cmd == 'C':
            p1, p2, cur = (n(0), n(1)), (n(2), n(3)), (n(4), n(5))
            out.append(f'C{pt(tp(*p1))} {pt(tp(*p2))} {pt(tp(*cur))}'); i += 6
        elif cmd == 'Q':
            p1, cur = (n(0), n(1)), (n(2), n(3))
            out.append(f'Q{pt(tp(*p1))} {pt(tp(*cur))}'); i += 4
        elif cmd == 'A':
            rx, ry, xr, la, sw = n(0), n(1), n(2), int(n(3)), int(n(4))
            cur = (n(5), n(6))
            out.append(f'A{f(rx * s)} {f(ry * s)} {f(xr + deg)} {la} {sw} {pt(tp(*cur))}'); i += 7
        else:
            raise ValueError(cmd)
    return ' '.join(out)


def el_d(e):
    """Element string (path/circle/rect/ellipse) -> path d."""
    g = lambda k: float(re.search(r'\b' + k + r'="([-\d.]+)"', e).group(1))
    if e.startswith('<path'):
        return re.search(r'd="([^"]+)"', e).group(1)
    if e.startswith('<circle'):
        cx, cy, r = g('cx'), g('cy'), g('r')
        return f'M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'
    if e.startswith('<ellipse'):
        cx, cy, rx, ry = g('cx'), g('cy'), g('rx'), g('ry')
        return f'M{f(cx - rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx + rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx - rx)} {f(cy)} Z'
    if e.startswith('<rect'):
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        r = g('rx') if 'rx=' in e else 0
        return rr_d(x, y, w, h, r)
    raise ValueError(e)


def rr_d(x, y, w, h, r):
    if not r:
        return f'M{f(x)} {f(y)} H{f(x + w)} V{f(y + h)} H{f(x)} Z'
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')


def circ_d(cx, cy, r):
    return f'M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'


def rpoly(points, r, close=True):
    """Polygon (or polyline) with corners rounded by radius r (r may be a list per corner)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    segs = []
    idx = range(n) if close else range(1, n - 1)
    corners = {}
    for i in idx:
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1]); v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1); u2 = (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        rad = rs[i]
        t = rad / math.tan(ang / 2) if rad else 0
        t = min(t, l1 / 2, l2 / 2)
        rad = t * math.tan(ang / 2)
        a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t); b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
        cross = u1[0] * u2[1] - u1[1] * u2[0]
        sweep = 1 if cross < 0 else 0
        corners[i] = (a, b, rad, sweep)
    if close:
        a0 = corners[0][1]
        d = f'M{pt(a0)}'
        for i in list(range(1, n)) + [0]:
            a, b, rad, sw = corners[i]
            d += f' L{pt(a)}' + (f' A{f(rad)} {f(rad)} 0 0 {sw} {pt(b)}' if rad > 0.01 else '')
        return d + ' Z'
    d = f'M{pt(points[0])}'
    for i in range(1, n - 1):
        a, b, rad, sw = corners[i]
        d += f' L{pt(a)}' + (f' A{f(rad)} {f(rad)} 0 0 {sw} {pt(b)}' if rad > 0.01 else '')
    return d + f' L{pt(points[-1])}'


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def as_lines(roles):
    """For slash variants: everything stroked becomes line, dotcuts become dots, no area."""
    return roles['line'] + roles['detail'], roles['dot'] + roles['dotcut']


SLASH = L(48, 48, 208, 208)
HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
BOWL = 'M32 120 H224 A96 96 0 0 1 32 120 Z'

# ---------------------------------------------------------------- Food

pear = ('M128 64 C150 64 156 86 158 106 C160 128 192 140 192 172 C192 204 164 224 128 224 '
        'C92 224 64 204 64 172 C64 140 96 128 98 106 C100 86 106 64 128 64 Z')
pear_leaf = 'M134 54 C142 40 160 34 180 38 C174 54 156 60 134 54 Z'
icon('pear', 'Food', ['pear', 'fruit', 'food', 'healthy'],
     line=[P(pear), P('M128 64 C128 54 126 46 120 38'), P(pear_leaf)], area=[P(pear), P(pear_leaf)])

# open pea pod: a lens with three peas, tilted
pod_c = (128, 132)
pod = 'M44 132 A100 100 0 0 1 212 132 A100 100 0 0 1 44 132 Z'
pod_r = xf_d(pod, deg=-30, c=pod_c, tx=-4)
peas = [(lambda q: (q[0] - 4, q[1]))(rot([(128 + dx, 132)], -30, pod_c)[0]) for dx in (-46, 0, 46)]
stem_end = (lambda q: (q[0] - 4, q[1]))(rot([(212, 132)], -30, pod_c)[0])
icon('peas', 'Food', ['peas', 'pod', 'vegetable', 'green'],
     line=[P(pod_r), P(f'M{pt(stem_end)} C{pt((stem_end[0] + 4, stem_end[1] - 16))} '
                      f'{pt((stem_end[0] + 16, stem_end[1] - 24))} {pt((stem_end[0] + 24, stem_end[1] - 24))}')],
     area=[P(pod_r)], dotcut=[C(x, y, 20) for x, y in peas])

# chili pepper
chili = ('M120 96 C116 144 96 184 48 208 C120 224 188 176 200 112 C204 92 192 80 176 80 '
         'C152 80 124 80 120 96 Z')
chili_cap = 'M120 100 C140 112 176 112 200 104'
chili_stem = 'M160 82 C160 60 168 44 188 36'
pep_line = [P(chili), P(chili_stem)]
icon('pepper', 'Food', ['chili', 'pepper', 'spicy', 'hot', 'vegetable'],
     line=pep_line, detail=[P(chili_cap)], area=[P(chili)])
icon('pepper-slash', 'Food', ['pepper', 'off', 'disabled', 'hidden'],
     line=pep_line + [P(chili_cap), SLASH])

# pineapple
pa_c, pa_rx, pa_ry = (128, 156), 64, 68
crown = [(100, 92), (80, 52), (112, 68), (128, 32), (144, 68), (176, 52), (156, 92)]

def clip_ellipse_line(p, u, c, rx, ry):
    # intersections of line p + t u with ellipse
    px, py = p[0] - c[0], p[1] - c[1]
    A = (u[0] / rx) ** 2 + (u[1] / ry) ** 2
    B = 2 * (px * u[0] / rx ** 2 + py * u[1] / ry ** 2)
    Cc = (px / rx) ** 2 + (py / ry) ** 2 - 1
    disc = B * B - 4 * A * Cc
    t1 = (-B - math.sqrt(disc)) / (2 * A); t2 = (-B + math.sqrt(disc)) / (2 * A)
    return (p[0] + u[0] * t1, p[1] + u[1] * t1), (p[0] + u[0] * t2, p[1] + u[1] * t2)

lattice = []
for sgn in (1, -1):
    u = (1 / math.sqrt(2), sgn / math.sqrt(2))
    nrm = (-u[1], u[0])
    for off in (-22, 22):
        p = (pa_c[0] + nrm[0] * off, pa_c[1] + nrm[1] * off)
        a, b = clip_ellipse_line(p, u, pa_c, pa_rx, pa_ry)
        lattice.append(L(*a, *b))
icon('pineapple', 'Food', ['pineapple', 'tropical', 'fruit', 'food'],
     line=[E(*pa_c, pa_rx, pa_ry), PL(crown)], detail=lattice,
     area=[E(*pa_c, pa_rx, pa_ry), PG(crown)])

# pint glass (nonic bulge near the top)
pint = ('M64 40 H192 L186 72 C192 84 192 92 188 104 L176 204 A14 14 0 0 1 162 216 H94 '
        'A14 14 0 0 1 80 204 L68 104 C64 92 64 84 70 72 Z')
icon('pint-glass', 'Food', ['beer glass', 'pint', 'pub'],
     line=[P(pint)], detail=[L(70, 88, 186, 88)], area=[P(pint)])

pz = load('pizza')
pl, pd = as_lines(pz)
icon('pizza-slash', 'Food', ['pizza', 'off', 'disabled', 'hidden'], line=pl + [SLASH], dot=pd)

# popcorn
c1, c2, c3 = (84, 84), (128, 64), (172, 84)
p12 = circle_x(c1, 28, c2, 32)[0]
p23 = circle_x(c2, 32, c3, 28)[0]
puff = (f'M56 104 V84 A28 28 0 0 1 {pt(p12)} A32 32 0 0 1 {pt(p23)} A28 28 0 0 1 200 84 V104')
bucket = rpoly([(48, 104), (208, 104), (184, 216), (72, 216)], [4, 4, 12, 12])
icon('popcorn', 'Food', ['popcorn', 'movie snack', 'cinema', 'bucket', 'movie'],
     line=[P(bucket), P(puff)], detail=[L(104, 112, 110, 208), L(152, 112, 146, 208)],
     area=[P(bucket), P(puff + ' Z')])

# popsicle
pop = 'M80 80 A48 48 0 0 1 176 80 V164 A12 12 0 0 1 164 176 H92 A12 12 0 0 1 80 164 Z'
icon('popsicle', 'Food', ['ice pop', 'summer', 'dessert'],
     line=[P(pop), L(128, 176, 128, 216)], detail=[L(112, 88, 112, 140), L(144, 88, 144, 140)], area=[P(pop)])

# pumpkin
pumpkin = ('M128 76 C160 60 224 72 224 144 C224 200 176 224 128 212 C80 224 32 200 32 144 '
           'C32 72 96 60 128 76 Z')
icon('pumpkin', 'Food', ['pumpkin', 'halloween', 'squash', 'autumn'],
     line=[P(pumpkin), P('M128 74 C128 56 132 44 144 36')],
     detail=[P('M100 70 C76 104 76 184 100 214'), P('M156 70 C180 104 180 184 156 214')], area=[P(pumpkin)])

# radish
radish = ('M128 100 C172 100 196 128 192 158 C188 186 160 204 128 224 C96 204 68 186 64 158 '
          'C60 128 84 100 128 100 Z')
rleaf1 = 'M120 96 C92 92 72 68 76 36 C104 40 124 64 120 96 Z'
rleaf2 = 'M136 96 C164 92 184 68 180 36 C152 40 132 64 136 96 Z'
icon('radish', 'Food', ['radish', 'root vegetable', 'turnip', 'food'],
     line=[P(radish), P(rleaf1), P(rleaf2)], area=[P(radish), P(rleaf1), P(rleaf2)])

# rice bowl with chopsticks
heap = 'M52 120 C52 88 88 68 128 68 C168 68 204 88 204 120'
icon('rice-bowl', 'Food', ['rice', 'bowl', 'grain', 'asian food', 'bowl chopsticks'],
     line=[P(BOWL), P(heap), L(146, 70, 196, 32), L(174, 88, 224, 52)],
     area=[P(BOWL), P(heap + ' Z')])

# salad
sleaf = 'M64 120 C56 88 76 60 116 56 C124 92 104 116 64 120 Z'
icon('salad', 'Food', ['salad', 'bowl', 'healthy', 'vegetables'],
     line=[P(BOWL), P(sleaf), P('M148 120 A32 32 0 1 1 212 120')],
     area=[P(BOWL), P(sleaf), P('M148 120 A32 32 0 1 1 212 120 Z')])

# salt shaker
cap = 'M80 104 V88 A48 48 0 0 1 176 88 V104'
shaker = 'M80 104 H176 L184 208 A16 16 0 0 1 168 224 H88 A16 16 0 0 1 72 208 Z'
icon('salt', 'Food', ['salt shaker', 'seasoning', 'kitchen', 'spice'],
     line=[P(shaker), P(cap)], area=[P(shaker), P(cap + ' Z')],
     dotcut=[C(110, 78, 12), C(146, 78, 12)])

# sandwich
# a triangular half seen in 3/4: front face, thick cut edge with the filling showing
SA, SB, SC = (40, 208), (148, 208), (40, 84)
SO = (72, -32)
SB2, SC2 = (SB[0] + SO[0], SB[1] + SO[1]), (SC[0] + SO[0], SC[1] + SO[1])
sand = rpoly([SA, SB, SB2, SC2, SC], [12, 10, 12, 12, 10])
def wave(p, q, n, amp):
    dx, dy = q[0] - p[0], q[1] - p[1]
    ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
    d = f'M{pt(p)}'
    for i in range(n):
        a = (p[0] + dx * i / n, p[1] + dy * i / n); b = (p[0] + dx * (i + 1) / n, p[1] + dy * (i + 1) / n)
        sgn = 1 if i % 2 == 0 else -1
        c1 = (a[0] + dx / n * 0.33 + nx * amp * sgn, a[1] + dy / n * 0.33 + ny * amp * sgn)
        c2 = (a[0] + dx / n * 0.67 + nx * amp * sgn, a[1] + dy / n * 0.67 + ny * amp * sgn)
        d += f' C{pt(c1)} {pt(c2)} {pt(b)}'
    return d
icon('sandwich', 'Food', ['sandwich', 'lunch', 'bread', 'sub'],
     line=[P(sand)],
     detail=[P(wave(SB, SC, 5, 10))],
     area=[P(sand)])

# sausage
sc = (128, 184); rm = 76; hw = 32
a0, a1 = 213, 327
def ring_pt(r, a):
    return polar(sc, r, a)
sausage = (f'M{pt(ring_pt(rm + hw, a0))} A{rm + hw} {rm + hw} 0 0 1 {pt(ring_pt(rm + hw, a1))} '
           f'A{hw} {hw} 0 0 1 {pt(ring_pt(rm - hw, a1))} A{rm - hw} {rm - hw} 0 0 0 {pt(ring_pt(rm - hw, a0))} '
           f'A{hw} {hw} 0 0 1 {pt(ring_pt(rm + hw, a0))} Z')
e0 = ring_pt(rm, a0); e1 = ring_pt(rm, a1)
t0 = (math.cos(math.radians(a0 - 90)), math.sin(math.radians(a0 - 90)))
t1 = (math.cos(math.radians(a1 + 90)), math.sin(math.radians(a1 + 90)))
tie0 = L(e0[0] + t0[0] * (hw + 2), e0[1] + t0[1] * (hw + 2), e0[0] + t0[0] * (hw + 14), e0[1] + t0[1] * (hw + 14))
tie1 = L(e1[0] + t1[0] * (hw + 2), e1[1] + t1[1] * (hw + 2), e1[0] + t1[0] * (hw + 14), e1[1] + t1[1] * (hw + 14))
SG = dict()
icon('sausage', 'Food', ['sausage', 'hot dog', 'meat', 'bbq'],
     line=[P(xf_d(sausage, **SG)), P(xf_d(el_d(tie0), **SG)), P(xf_d(el_d(tie1), **SG))],
     detail=[P(xf_d(f'M{pt(ring_pt(rm + 4, 245))} A{rm + 4} {rm + 4} 0 0 1 {pt(ring_pt(rm + 4, 280))}', **SG))],
     area=[P(xf_d(sausage, **SG))])

# scallion
icon('scallion', 'Food', ['scallion', 'green onion', 'leek', 'vegetable'],
     line=[R(108, 124, 40, 92, 20), L(128, 124, 128, 32), P('M116 124 C108 92 92 68 64 48'),
           P('M140 124 C148 92 164 68 192 48')],
     detail=[L(108, 172, 148, 172)],
     area=[R(108, 124, 40, 92, 20)])

# shrimp: tapered crescent body with tail fan
oc, orr = (124, 124), 88
ic, irr = (140, 136), 44
def on(c, r, a):
    return polar(c, r, a)
h_o = on(oc, orr, -40); h_i = on(ic, irr, -40)
t_o = on(oc, orr, 100); t_i = on(ic, irr, 100)
shrimp = (f'M{pt(h_o)} A{orr} {orr} 0 1 0 {pt(t_o)} L{pt(t_i)} A{irr} {irr} 0 1 1 {pt(h_i)} '
          f'A{dist(h_o, h_i) / 2} {dist(h_o, h_i) / 2} 0 0 0 {pt(h_o)} Z')
segs = []
for a in (150, 196, 242):
    segs.append(L(*on(oc, orr, a), *on(ic, irr, a)))
tm = ((t_o[0] + t_i[0]) / 2, (t_o[1] + t_i[1]) / 2)
fan = rpoly([tm, (tm[0] + 44, tm[1] - 20), (tm[0] + 40, tm[1] + 8), (tm[0] + 52, tm[1] + 28)], 6)
icon('shrimp', 'Food', ['shrimp', 'prawn', 'seafood', 'food'],
     line=[P(shrimp), P(fan), P(f'M{pt(on(oc, orr - 8, -46))} C200 40 212 40 224 36')],
     detail=segs, area=[P(shrimp), P(fan)])

# skewer
def diamond(cx, cy, h, r=8):
    return P(rpoly([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)], r))
sq, cr, sk = 36, 28, 59.4
k1, k3 = (128 - sk, 128 + sk), (128 + sk, 128 - sk)
e_sq = sq / 2  # half extent of the diamond along the skewer, per axis
e_c = cr / math.sqrt(2)
icon('skewer', 'Food', ['kebab', 'skewer', 'grill', 'bbq'],
     line=[diamond(*k1, sq, 10), C(128, 128, cr), diamond(*k3, sq, 10),
           L(k1[0] - e_sq, k1[1] + e_sq, 36, 220), L(k1[0] + e_sq, k1[1] - e_sq, 128 - e_c, 128 + e_c),
           L(128 + e_c, 128 - e_c, k3[0] - e_sq, k3[1] + e_sq), L(k3[0] + e_sq, k3[1] - e_sq, 220, 36)],
     area=[diamond(*k1, sq, 10), C(128, 128, cr), diamond(*k3, sq, 10)])

# soda cup with lid and straw
cup = 'M72 104 H184 L172 208 A16 16 0 0 1 156 224 H100 A16 16 0 0 1 84 208 Z'
lid = 'M56 104 H200 M72 104 V88 A16 16 0 0 1 88 72 H168 A16 16 0 0 1 184 88 V104'
icon('soda', 'Food', ['drinks', 'soft drink', 'cup', 'straw', 'soda'],
     line=[P(cup), P(lid), PL([(136, 72), (148, 32), (184, 32)])],
     area=[P(cup), P('M72 104 V88 A16 16 0 0 1 88 72 H168 A16 16 0 0 1 184 88 V104 Z')])

# soup with spoon
soup_line = [P(BOWL), P('M76 40 C60 56 92 72 76 88'), P('M116 40 C100 56 132 72 116 88'), L(160, 112, 208, 40)]
icon('soup', 'Food', ['soup', 'bowl', 'hot', 'broth'], line=soup_line, area=[P(BOWL)])
icon('soup-slash', 'Food', ['soup', 'off', 'disabled', 'hidden'], line=[soup_line[0]] + soup_line[2:] + [SLASH])

# spatula (built upright, rotated 45 degrees)
sp_head = rr_d(84, 32, 88, 84, 14)
sp_handle = rr_d(112, 156, 32, 68, 16)
SPD = 45
icon('spatula', 'Food', ['spatula', 'turner', 'cooking', 'kitchen'],
     line=[P(xf_d(sp_head, deg=SPD)), P(xf_d(sp_handle, deg=SPD)), P(xf_d('M128 116 L128 156', deg=SPD))],
     detail=[P(xf_d('M112 60 L112 92', deg=SPD)), P(xf_d('M144 60 L144 92', deg=SPD))],
     area=[P(xf_d(sp_head, deg=SPD)), P(xf_d(sp_handle, deg=SPD))])

# spoon
sp_bowl = 'M88 84 A40 52 0 1 1 168 84 A40 52 0 1 1 88 84 Z'
icon('spoon', 'Food', ['spoon', 'utensil', 'soup', 'cutlery'],
     line=[P(xf_d(sp_bowl, deg=45, c=(128, 132))), P(xf_d('M128 136 L128 228', deg=45, c=(128, 132)))],
     area=[P(xf_d(sp_bowl, deg=45, c=(128, 132)))])

# star fruit slice
sfc = (128, 134)
sf = [polar(sfc, 98 if i % 2 == 0 else 58, -90 + i * 36) for i in range(10)]
icon('star-fruit', 'Food', ['carambola', 'fruit', 'star'],
     line=[P(rpoly(sf, [14 if i % 2 == 0 else 10 for i in range(10)]))],
     area=[P(rpoly(sf, [14 if i % 2 == 0 else 10 for i in range(10)]))],
     detail=[L(*polar(sfc, 30, -90 + i * 72), *polar(sfc, 58, -90 + i * 72)) for i in range(5)])

# swiss roll
spiral = 'M144 128 A16 16 0 0 0 112 128 A32 32 0 0 0 176 128 A48 48 0 0 0 80 128 A64 64 0 0 0 144 192'
icon('swiss-roll', 'Food', ['cake roll', 'dessert', 'swiss roll'],
     line=[C(128, 128, 92)], detail=[P(spiral)], area=[C(128, 128, 92)])

# takeout box
tbox = rpoly([(88, 72), (168, 72), (204, 112), (184, 216), (72, 216), (52, 112)], [6, 6, 6, 12, 12, 6])
icon('takeout-box', 'Food', ['takeout', 'takeaway', 'noodle box', 'delivery'],
     line=[P(tbox), P('M70 92 C56 16 200 16 186 92')],
     detail=[L(56, 112, 200, 112), PL([(92, 76), (128, 108), (164, 76)])], area=[P(tbox)])

# tea bag
bag = 'M56 128 L80 104 H128 L152 128 V200 A16 16 0 0 1 136 216 H72 A16 16 0 0 1 56 200 Z'
icon('tea-bag', 'Food', ['tea', 'tea bag', 'drink'],
     line=[P(bag), P('M104 104 C104 64 128 56 164 56'), R(164, 36, 52, 40, 8)],
     detail=[L(80, 168, 128, 168)],
     area=[P(bag), R(164, 36, 52, 40, 8)])

# teapot pouring
TPC = (120, 140)
TP = dict(deg=16, c=TPC, s=0.9, tx=-2, ty=-16)
def tpp(p):
    q = rot([p], 16, TPC)[0]
    return (TPC[0] + (q[0] - TPC[0]) * 0.9 - 2, TPC[1] + (q[1] - TPC[1]) * 0.9 - 16)
tp_body = 'M56 104 H184 C192 160 172 200 120 200 C68 200 48 160 56 104 Z'
tp_lid = 'M80 104 C80 74 160 74 160 104'
tp_handle = 'M57 120 C20 116 20 172 66 172'
tp_spout = 'M182 140 C200 140 204 112 220 100'
icon('teapot', 'Food', ['tea', 'teapot', 'brew', 'kettle', 'pot'],
     line=[P(xf_d(d, **TP)) for d in (tp_body, tp_lid, tp_handle, tp_spout)],
     area=[P(xf_d(tp_body, **TP))],
     dot=[C(*tpp((120, 66)), 16), C(*(lambda t: (t[0], t[1] + 36))(tpp((220, 100))), 14),
          C(*(lambda t: (t[0], t[1] + 72))(tpp((220, 100))), 14)])

# toast
toast = ('M64 208 V116 C44 108 36 92 36 76 C36 48 64 36 128 36 C192 36 220 48 220 76 '
         'C220 92 212 108 192 116 V208 A8 8 0 0 1 184 216 H72 A8 8 0 0 1 64 208 Z')
crumb = ('M96 184 V104 C80 100 68 92 68 80 C68 72 88 68 128 68 C168 68 188 72 188 80 '
         'C188 92 176 100 160 104 V184 Z')
icon('toast', 'Food', ['toast', 'bread', 'breakfast', 'slice'],
     line=[P(toast)], detail=[P(crumb)], area=[P(toast)])

# tomato
icon('tomato', 'Food', ['tomato', 'vegetable', 'red', 'food'],
     line=[E(128, 142, 92, 76), P('M128 70 C128 54 132 44 144 36')],
     detail=[PL([(88, 82), (108, 98), (128, 84), (148, 98), (168, 82)])],
     area=[E(128, 142, 92, 76)])

# vegan: leaf forming a V
vleaf = 'M124 208 C108 136 140 72 212 48 C224 124 188 184 124 208 Z'
icon('vegan', 'Food', ['plant-based', 'vegan', 'vegetarian'],
     line=[L(44, 64, 116, 200), P(vleaf)], detail=[L(134, 190, 184, 104)], area=[P(vleaf)])

# watermelon wedge
wc_ = (128, 40); wr = 176
wa, wb = polar(wc_, wr, 60), polar(wc_, wr, 120)
wedge = f'M128 40 L{pt(wa)} A{wr} {wr} 0 0 1 {pt(wb)} Z'
ra, rb = polar(wc_, 148, 60.5), polar(wc_, 148, 119.5)
icon('watermelon', 'Food', ['watermelon', 'fruit', 'summer', 'slice'],
     line=[P(wedge)], detail=[P(f'M{pt(ra)} A148 148 0 0 1 {pt(rb)}')], area=[P(wedge)],
     dotcut=[C(128, 116, 12), C(108, 156, 12), C(148, 156, 12)])

# whisk
WK = dict(deg=45, c=(128, 128))
wk_handle = rr_d(110, 152, 36, 76, 18)
icon('whisk', 'Food', ['whisk', 'whip', 'baking', 'kitchen'],
     line=[P(xf_d(wk_handle, **WK)),
           P(xf_d('M114 152 C70 112 76 24 128 24 C180 24 186 112 142 152', **WK)),
           P(xf_d('M121 152 C106 120 106 60 128 60 C150 60 150 120 135 152', **WK)),
           ],
     area=[P(xf_d(wk_handle, **WK))])

# ---------------------------------------------------------------- Health

hand = load('hand')
hand_line = el_d(hand['line'][0])
HS = dict(s=0.8, c=(128, 224))
hl = xf_d(hand_line, **HS)
hdet = [P(xf_d(el_d(e), **HS)) for e in hand['detail']]
def htr(p):
    return (128 + (p[0] - 128) * 0.8, 224 + (p[1] - 224) * 0.8)
tip1 = htr((94, 64)); tip2 = htr((166, 52))
n1 = (tip1[0] - 22, tip1[1] - 50); n2 = (tip2[0] + 22, tip2[1] - 46)
icon('acupuncture', 'Health', ['needles', 'therapy', 'traditional medicine', 'acupressure'],
     line=hand['line'], area=hand['area'],
     detail=hand['detail'] + [L(104, 206, 126, 184), L(156, 208, 176, 188)],
     dotcut=[C(130, 180, 18), C(180, 184, 18)])

icon('allergy', 'Health', ['allergen', 'pollen', 'reaction', 'sneeze'],
     line=hand['line'], detail=hand['detail'], area=hand['area'],
     dotcut=[C(112, 176, 12), C(152, 166, 12), C(132, 198, 12), C(182, 190, 12)])

# ambulance
amb = rpoly([(36, 56), (164, 56), (220, 116), (220, 164), (36, 164)], [16, 12, 12, 12, 12])
icon('ambulance', 'Health', ['ambulance', 'emergency', 'hospital', 'vehicle'],
     line=[P(amb), C(80, 192, 20), C(180, 192, 20)],
     detail=[L(92, 88, 92, 132), L(70, 110, 114, 110), PL([(160, 84), (172, 84), (196, 116)])],
     area=[P(amb)])

# rod of asclepius
# snake: half-loops alternating right/left between crossings of the staff
def split_bez(b, t):
    p0, p1, p2, p3 = b
    lerp = lambda a, c, t: (a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
    a, bb, c = lerp(p0, p1, t), lerp(p1, p2, t), lerp(p2, p3, t)
    d, e = lerp(a, bb, t), lerp(bb, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p3)
def bez_d(b, move=True):
    return (f'M{pt(b[0])} ' if move else '') + f'C{pt(b[1])} {pt(b[2])} {pt(b[3])}'
cross_y = [192, 144, 96]
loops = []
for i in range(2):
    y0, y1 = cross_y[i], cross_y[i + 1]
    sx = 60 if i % 2 == 0 else -60
    loops.append(((128, y0), (128 + sx, y0 - 2), (128 + sx, y1 + 2), (128, y1)))
tail = ((92, 218), (104, 214), (118, 202), (128, 192))
head = ((128, 96), (156, 92), (170, 76), (164, 58))
# the staff passes in front of the snake at the middle crossing
gap_t = 0.17
l0a, _ = split_bez(loops[0], 1 - gap_t)
_, l1b = split_bez(loops[1], gap_t)
snake = [P(bez_d(tail) + ' ' + bez_d(l0a, False)), P(bez_d(l1b) + ' ' + bez_d(head, False))]
icon('asclepius', 'Health', ['rod of asclepius', 'medicine', 'healthcare'],
     line=[L(128, 32, 128, 78), L(128, 114, 128, 174), L(128, 210, 128, 224)] + snake,
     dot=[C(163, 54, 18)])

ear = load('ear')
ES = dict(s=0.74, c=(40, 128), tx=0)
icon('assistive-listening', 'Health', ['hearing', 'ear', 'accessibility', 'sound'],
     line=[P(xf_d(el_d(e), **ES)) for e in ear['line']] + [P('M168 100 A40 40 0 0 1 168 156'), P('M192 72 A72 72 0 0 1 192 184')],
     detail=[P(xf_d(el_d(e), **ES)) for e in ear['detail']],
     area=[P(xf_d(el_d(e), **ES)) for e in ear['area']])

# awareness ribbon
ribbon = 'M80 216 L150 110 C176 72 164 40 128 40 C92 40 80 72 106 110 L176 216'
icon('awareness-ribbon', 'Health', ['awareness ribbon', 'cancer', 'support', 'health'],
     line=[P(ribbon)], area=[P('M128 143.3 L150 110 C176 72 164 40 128 40 C92 40 80 72 106 110 Z')])

bd = load('bandaids')
icon('bandaids-slash', 'Health', ['bandaids', 'disabled', 'off', 'health'],
     line=bd['line'] + bd['detail'] + [SLASH])

# blood pressure: cuff + tube + gauge
icon('blood-pressure', 'Health', ['blood pressure', 'cuff', 'sphygmomanometer', 'hypertension'],
     line=[P('M60 128 H108 A20 40 0 0 1 108 208 H60'), E(60, 168, 20, 40), C(168, 88, 56),
           P('M168 144 V160 C168 176 160 184 140 184 H128')],
     detail=[L(168, 88, 192, 64)],
     area=[P('M60 128 H108 A20 40 0 0 1 108 208 H60 Z'), C(168, 88, 56)])

book = load('book')
icon('book-medical', 'Health', ['medical book', 'health', 'manual', 'reference', 'health record'],
     line=book['line'], detail=book['detail'] + [L(128, 76, 128, 132), L(100, 104, 156, 104)], area=book['area'])

# brain with a warning triangle badge
BC, BR = (184, 184), 58
import build as _build

def arc_center(p, q, r, sweep, large=0):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    d = dist(p, q) / 2
    h = math.sqrt(max(r * r - d * d, 0))
    ux, uy = (q[0] - p[0]) / (2 * d), (q[1] - p[1]) / (2 * d)
    for sg in (1, -1):
        c = (mx - uy * h * sg, my + ux * h * sg)
        a1 = math.atan2(p[1] - c[1], p[0] - c[0]); a2 = math.atan2(q[1] - c[1], q[0] - c[0])
        span = (a2 - a1) % (2 * math.pi) if sweep else (a1 - a2) % (2 * math.pi)
        if (span > math.pi) == bool(large):
            return c

def trimmed_arcs(pts, r, sweep, cut_c, cut_r, keep_start=True):
    """Chain of arcs through pts; stop (or start) where it meets the cut circle."""
    d = None
    seq = list(zip(pts, pts[1:]))
    if not keep_start:
        seq = [(q, p) for p, q in reversed(seq)]
        sweep = 1 - sweep
    out = f'M{pt(seq[0][0])}'
    for p, q in seq:
        if dist(q, cut_c) >= cut_r:
            out += f' A{r} {r} 0 0 {sweep} {pt(q)}'
            continue
        c = arc_center(p, q, r, sweep)
        xs = circle_x(c, r, cut_c, cut_r)
        # the crossing closest to p along the arc
        def ang(x):
            a1 = math.atan2(p[1] - c[1], p[0] - c[0]); a2 = math.atan2(x[1] - c[1], x[0] - c[0])
            return (a2 - a1) % (2 * math.pi) if sweep else (a1 - a2) % (2 * math.pi)
        x = min(xs, key=ang)
        out += f' A{r} {r} 0 0 {sweep} {pt(x)}'
        break
    return out

brain_r_pts = [(128, 56), (184, 64), (212, 112), (204, 164), (160, 204), (128, 200)]
brain_l_pts = [(128, 56), (72, 64), (44, 112), (52, 164), (96, 204), (128, 200)]
WR = 64
brain_r = trimmed_arcs(brain_r_pts, 32, 1, BC, WR)
brain_l = trimmed_arcs(brain_l_pts, 32, 0, BC, WR)
br = load('brain')
_full = _build.filled([el_d(e) for e in br['area']])
_cut = _build.filled([circ_d(*BC, WR)])
brain_area = _build.to_d(_build.difference(_full, _cut))
tri = rpoly([(184, 140), (224, 210), (144, 210)], 8)
icon('brain-warning', 'Health', ['mental health', 'overload', 'stress'],
     line=[P(brain_l), P(brain_r), P(tri)],
     detail=[L(128, 72, 128, 152), P('M84 132 A28 28 0 0 1 100 104'), P('M172 132 A28 28 0 0 0 156 104'),
             L(184, 166, 184, 180)],
     area=[P(brain_area), P(tri)], dotcut=[C(184, 196, 9)])

# breast pump
icon('breast-pump', 'Health', ['breast pump', 'nursing', 'baby', 'feeding'],
     line=[P('M108 100 L60 64 C40 84 40 140 60 160 L108 124'), R(108, 84, 80, 56, 12), R(116, 140, 64, 84, 16),
           L(188, 100, 222, 70)],
     detail=[L(140, 172, 156, 172)],
     area=[P('M108 100 L60 64 C40 84 40 140 60 160 L108 124 Z'), R(108, 84, 80, 56, 12), R(116, 140, 64, 84, 16)])

clip = load('clipboard')
icon('checkup-list', 'Health', ['checkup', 'medical', 'checklist', 'health'],
     line=clip['line'], hole=clip['hole'], area=clip['area'],
     detail=[PL([(76, 120), (100, 120), (112, 100), (128, 140), (140, 120), (180, 120)]),
             PL([(76, 180), (88, 192), (108, 168)]), L(132, 180, 180, 180)])

house = load('house')
icon('clinic', 'Health', ['clinic', 'medical', 'health center', 'house'],
     line=[house['line'][0], house['line'][1]], area=house['area'],
     detail=[L(128, 126, 128, 178), L(102, 152, 154, 152)])

heart_small = xf_d(HEART, s=0.42, c=(128, 145), ty=-4)
icon('clipboard-heart', 'Health', ['clipboard', 'health', 'favorite', 'heart', 'health record'],
     line=clip['line'], hole=clip['hole'], area=clip['area'], detail=[P(heart_small)])
icon('clipboard-pulse', 'Health', ['clipboard', 'health record', 'heartbeat', 'medical'],
     line=clip['line'], hole=clip['hole'], area=clip['area'],
     detail=[PL([(76, 140), (100, 140), (116, 108), (140, 172), (156, 140), (180, 140)])])

# clock with lightning badge
pa, pb = circle_x((128, 128), 96, BC, BR)
clock_arc = f'M{pt(pa)} A96 96 0 1 0 {pt(pb)}'
clock_area = clock_arc + ' ' + arc_to(BC, BR, pb, pa, lambda m: -dist(m, (128, 128))) + ' Z'
bolt = PG([(190, 150), (162, 190), (184, 190), (178, 218), (206, 178), (184, 178)])
icon('clock-lightning', 'Health', ['acute', 'urgent', 'emergency', 'fast', 'clock'],
     line=[P(clock_arc), bolt], detail=[PL([(128, 76), (128, 128), (88, 128)])],
     area=[P(clock_area), bolt])

# crutches
def crutch(cx):
    return [L(cx - 24, 40, cx + 24, 40), PL([(cx - 16, 40), (cx - 16, 136), (cx, 168), (cx, 216)]),
            PL([(cx + 16, 40), (cx + 16, 136), (cx, 168)]), L(cx - 16, 104, cx + 16, 104)]
cr_line = crutch(84) + crutch(172)
icon('crutches', 'Health', ['crutches', 'health', 'symbol'], line=cr_line)
icon('crutches-slash', 'Health', ['crutches', 'disabled', 'off', 'health'], line=cr_line + [SLASH])

print(save(overwrite=True))
