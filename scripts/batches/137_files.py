import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

F = 'Files'
SLASH = L(48, 48, 208, 208)
B = (184, 184)  # badge centre

# ---------------------------------------------------------------- base geometry (file.svg)
base = load('file')
FILEP = 'M56 32 H152 L200 80 V224 H56 Z'
FOLD = P('M152 32 V80 H200')
DOC = [(56, 32), (152, 32), (200, 80), (200, 224), (56, 224)]
assert base['line'][0] == P(FILEP)


def file_icon(name, tags, det=(), **kw):
    kw.setdefault('line', [])
    kw['line'] = [P(FILEP)] + list(kw['line'])
    icon(name, F, tags, detail=[FOLD] + list(det), area=[P(FILEP)] + list(kw.pop('area', [])), **kw)


# ---------------------------------------------------------------- helpers
def head(tip, direction, size):
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


def badge_cut(points, B=B, R=64):
    """Open outline of a closed polygon with the part near B removed, and the matching area with a concave notch."""
    n = len(points)
    inside = lambda p: dist(p, B) < R
    hits = []
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        fx, fy = a[0] - B[0], a[1] - B[1]
        A = dx * dx + dy * dy; Bq = 2 * (fx * dx + fy * dy); Cq = fx * fx + fy * fy - R * R
        disc = Bq * Bq - 4 * A * Cq
        if disc <= 0:
            continue
        for t in sorted(((-Bq - math.sqrt(disc)) / (2 * A), (-Bq + math.sqrt(disc)) / (2 * A))):
            if 0 <= t <= 1:
                p = (a[0] + dx * t, a[1] + dy * t)
                q = (a[0] + dx * min(t + 1e-3, 1), a[1] + dy * min(t + 1e-3, 1))
                hits.append((i, t, p, inside(q)))
    enter = [h for h in hits if h[3]][0]
    leave = [h for h in hits if not h[3]][0]
    pts = [leave[2]]
    i = leave[0]
    while True:
        i = (i + 1) % n
        if i == (enter[0] + 1) % n:
            break
        pts.append(points[i])
    pts.append(enter[2])
    open_d = poly(pts)
    cen = (sum(p[0] for p in points) / n, sum(p[1] for p in points) / n)
    area_d = open_d + ' ' + arc_to(B, R, enter[2], leave[2], lambda m: -dist(m, cen)) + ' Z'
    return open_d, area_d


def badge_file(name, tags, R=64, line=(), area=(), detail=(), **kw):
    """The file with its lower-right corner cleared for a badge around B."""
    o, a = badge_cut(DOC, B, R)
    icon(name, F, tags, line=[P(o)] + list(line), detail=[FOLD] + list(detail), area=[P(a)] + list(area), **kw)


def xform_d(d, s, dx, dy):
    """Scale an absolute-command path (M L H V C A Z) by s then translate."""
    toks = re.findall(r'[MLHVCAZ]|-?[\d.]+', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; out.append(t); i += 1
            continue
        if cmd in 'MLC':
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            out.append(f'{f(x * s + dx)} {f(y * s + dy)}')
        elif cmd == 'H':
            out.append(f(float(t) * s + dx)); i += 1
        elif cmd == 'V':
            out.append(f(float(t) * s + dy)); i += 1
        elif cmd == 'A':
            rx, ry, rotn, la, sw, x, y = toks[i:i + 7]; i += 7
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {rotn} {la} {sw} {f(float(x) * s + dx)} {f(float(y) * s + dy)}')
    return re.sub(r' ?([MLHVCAZ]) ?', r' \1', ' '.join(out)).strip().replace(' Z', ' Z')


def xform(el, s, c_from, c_to):
    dx, dy = c_to[0] - c_from[0] * s, c_to[1] - c_from[1] * s
    m = re.match(r'<path d="([^"]*)"/>', el)
    if m:
        return P(xform_d(m.group(1), s, dx, dy))
    m = re.match(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/>', el)
    cx, cy, r = map(float, m.groups())
    return C(cx * s + dx, cy * s + dy, r * s)


def rpoly(points, r, close=True):
    """Polyline with rounded corners; r is a number or per-vertex list (0 = sharp)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        if (not close and (i == 0 or i == n - 1)) or rs[i] == 0:
            segs.append((p1, None))
            continue
        a = (p0[0] - p1[0], p0[1] - p1[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        t = rs[i] / math.tan(ang / 2)
        s = (p1[0] + a[0] * t, p1[1] + a[1] * t); e = (p1[0] + b[0] * t, p1[1] + b[1] * t)
        cross = a[0] * b[1] - a[1] * b[0]
        segs.append((s, f'A{f(rs[i])} {f(rs[i])} 0 0 {0 if cross > 0 else 1} {pt(e)}'))
    d = ''
    for i, (p, arc) in enumerate(segs):
        d += ('M' if i == 0 else ' L') + pt(p)
        if arc:
            d += ' ' + arc
    return d + (' Z' if close else '')


def clip_polyline(points, keep, closed=False, steps=400):
    """Split a polyline into the runs where keep(p) holds (boundaries found by bisection)."""
    pts = list(points) + ([points[0]] if closed else [])
    runs, cur = [], []

    def edge(a, b):
        lo, hi = 0.0, 1.0
        ka = keep(a)
        for _ in range(40):
            m = (lo + hi) / 2
            pm = (a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)
            if keep(pm) == ka:
                lo = m
            else:
                hi = m
        return (a[0] + (b[0] - a[0]) * lo, a[1] + (b[1] - a[1]) * lo)

    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int(dist(a, b) / 2))
        prev = a
        if i == 0 and keep(a):
            cur = [a]
        for k in range(1, n + 1):
            q = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if keep(prev) and not keep(q):
                cur.append(edge(prev, q)); runs.append(cur); cur = []
            elif not keep(prev) and keep(q):
                cur = [edge(q, prev)]
            prev = q
        if keep(b) and cur:
            cur.append(b)
    if cur:
        runs.append(cur)
    if closed and len(runs) > 1 and keep(pts[0]):
        runs[0] = runs[-1][:-1] + runs[0]
        runs.pop()
    out = []
    for r_ in runs:
        clean = [r_[0]]
        for p in r_[1:]:
            if dist(p, clean[-1]) > 0.01:
                clean.append(p)
        if len(clean) > 1 and sum(dist(clean[j], clean[j + 1]) for j in range(len(clean) - 1)) > 6:
            out.append(clean)
    return out


def off_slash(p, gap=30):
    return abs(p[1] - p[0]) / math.sqrt(2) >= gap


# ---------------------------------------------------------------- stroke lettering (as batch 105)
def g_A(x, t, w, h):
    b = t + h; yb = t + h * 0.66; hw = (w / 2) * (yb - t) / h
    return [PL([(x, b), (x + w / 2, t), (x + w, b)]), L(x + w / 2 - hw, yb, x + w / 2 + hw, yb)]


def g_C(x, t, w, h, end=20):
    r = w / 2
    ct, cb = (x + r, t + r), (x + r, t + h - r)
    s, e = polar(ct, r, -end), polar(cb, r, end)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 {pt(e)}')]


def g_D(x, t, w, h):
    R_ = min(w * 0.6, h / 2); b = t + h
    return [P(f'M{f(x)} {f(t)} H{f(x + w - R_)} A{f(R_)} {f(R_)} 0 0 1 {f(x + w)} {f(t + R_)} V{f(b - R_)} '
              f'A{f(R_)} {f(R_)} 0 0 1 {f(x + w - R_)} {f(b)} H{f(x)} Z')]


def g_E(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b), (x + w, b)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_F(x, t, w, h):
    return [PL([(x + w, t), (x, t), (x, t + h)]), L(x, t + h * 0.5, x + w * 0.8, t + h * 0.5)]


def g_G(x, t, w, h):
    r = w / 2; ct = (x + r, t + r); s = polar(ct, r, -20); yb = t + h * 0.54
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 '
              f'{f(x + w)} {f(t + h - r)} V{f(yb)} H{f(x + w * 0.55)}')]


def g_H(x, t, w, h):
    return [L(x, t, x, t + h), L(x + w, t, x + w, t + h), L(x, t + h / 2, x + w, t + h / 2)]


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h)]


def g_J(x, t, w, h):
    r = w / 2
    return [P(f'M{f(x + w)} {f(t)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(t + h - r)}')]


def g_K(x, t, w, h):
    b = t + h; a0, a1 = (x + w, t), (x, t + h * 0.62)
    m = (a0[0] + (a1[0] - a0[0]) * 0.55, a0[1] + (a1[1] - a0[1]) * 0.55)
    return [L(x, t, x, b), L(*a0, *a1), L(*m, x + w, b)]


def g_L(x, t, w, h):
    return [PL([(x, t), (x, t + h), (x + w, t + h)])]


def g_M(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w / 2, t + h * 0.62), (x + w, t), (x + w, t + h)])]


def g_N(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w, t + h), (x + w, t)])]


def bowl(x, t, w, h, k=0.56):
    r = h * k / 2
    return r, f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 2 * r)} H{f(x)}'


def g_P(x, t, w, h):
    return [P(bowl(x, t, w, h)[1])]


def g_O(x, t, w, h):
    return [R(x, t, w, h, w / 2)]


def g_S(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x + w)} {f(t)} H{f(x + r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(t + 2 * r)} H{f(x + w - r)} '
              f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + h)} H{f(x)}')]


def g_T(x, t, w, h):
    return [L(x, t, x + w, t), L(x + w / 2, t, x + w / 2, t + h)]


def g_V(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h), (x + w, t)])]


def g_X(x, t, w, h):
    return [L(x, t, x + w, t + h), L(x + w, t, x, t + h)]


def g_Y(x, t, w, h):
    m = (x + w / 2, t + h * 0.5)
    return [PL([(x, t), m, (x + w, t)]), L(*m, m[0], t + h)]


def bowl_low(x, t, w, h):
    Rb = h * 0.3; c = (x + w - Rb, t + h - Rb)
    return Rb, c, polar(c, Rb, 150)


def g_3(x, t, w, h):
    Rb, c, e = bowl_low(x, t, w, h)
    return [P(f'M{f(x)} {f(t)} H{f(x + w)} L{f(c[0])} {f(c[1] - Rb)} A{f(Rb)} {f(Rb)} 0 1 1 {pt(e)}')]


def g_4(x, t, w, h):
    yb = t + h * 0.64
    return [PL([(x + w * 0.42, t), (x, yb), (x + w, yb)]), L(x + w * 0.74, t + h * 0.36, x + w * 0.74, t + h)]


def g_1(x, t, w, h):
    return [PL([(x, t + h * 0.26), (x + w, t), (x + w, t + h)])]


GLYPH = dict(A=g_A, C=g_C, D=g_D, E=g_E, F=g_F, G=g_G, H=g_H, I=g_I, J=g_J, K=g_K, L=g_L, M=g_M, N=g_N,
             O=g_O, P=g_P, S=g_S, T=g_T, V=g_V, X=g_X, Y=g_Y)
GLYPH.update({'3': g_3, '4': g_4, '0': g_O, '1': g_1})
WIDTH = dict(A=44, C=36, D=40, E=32, F=32, G=40, H=38, I=0, J=32, K=38, L=30, M=48, N=40, O=40, P=36, S=38,
             T=40, V=44, X=40, Y=42)
WIDTH.update({'3': 36, '4': 40})

LABEL_TOP = 128    # where the document sides stop above the label
LABEL_CY = 194     # label centreline (letters 164..224)
LABEL_H = 60


def label_text(s, cy=LABEL_CY, h=LABEL_H, run=192, gmax=32, gmin=26):
    ws = [WIDTH[ch] for ch in s]
    n = len(s)
    gap = gmax if n == 1 else min(gmax, (run - sum(ws)) / (n - 1))
    if gap < gmin:  # squeeze the wide letters so the gaps never close up
        gap = gmin
        k = (run - gap * (n - 1)) / sum(ws)
        ws = [w * k for w in ws]
    total = sum(ws) + gap * (n - 1)
    x = 128 - total / 2
    out = []
    for ch, w in zip(s, ws):
        out += GLYPH[ch](x, cy - h / 2, w, h)
        x += w + gap
    return out


DOC_TOP = f'M56 {LABEL_TOP} V32 H152 L200 80 V{LABEL_TOP}'
DOC_TOP_AREA = f'M56 32 H152 L200 80 V{LABEL_TOP + 8} H56 Z'


def type_icon(name, tags, s):
    icon(name, F, tags, line=[P(DOC_TOP)] + label_text(s), detail=[FOLD], area=[P(DOC_TOP_AREA)])


# ================================================================= icons in the document
file_icon('file-database', ['file database', 'document', 'page', 'file', 'database'],
          [E(128, 120, 40, 16), P('M88 120 V176 A40 16 0 0 0 168 176 V120')])

file_icon('file-delta', ['file delta', 'document', 'page', 'file', 'delta'],
          [PG([(128, 116), (168, 188), (88, 188)])])

file_icon('file-diff', ['diff', 'compare', 'changes', 'document'],
          [L(128, 100, 128, 148), L(104, 124, 152, 124), L(104, 184, 152, 184)])

file_icon('file-digit', ['file digit', 'document', 'page', 'file', 'digit'],
          [R(82, 116, 36, 76, 18)] + g_1(150, 116, 22, 76))

file_icon('file-dots', ['file dots', 'document', 'page', 'file', 'dots'],
          dotcut=[C(92, 152, 14), C(128, 152, 14), C(164, 152, 14)])

# italic f with a crossbar
file_icon('file-function', ['file function', 'document', 'page', 'file', 'function'],
          [P(rpoly([(168, 112), (148, 112), (120, 196), (96, 196)], [0, 20, 20, 0], close=False)), L(104, 148, 156, 148)])

file_icon('file-font', ['font file', 'typography', 'document', 'type', 'typeface'],
          g_A(92, 116, 72, 80))

file_icon('file-hash', ['hash', 'checksum', 'file', 'tag'],
          [L(112, 120, 104, 192), L(152, 120, 144, 192), L(88, 140, 168, 140), L(84, 172, 164, 172)])

heart = load('heart')['line'][0]
file_icon('file-heart', ['document', 'favorite', 'love', 'file'], [xform(heart, 0.42, (128, 145), (128, 156))])

inf = 'M128 156 C142 130 172 130 172 156 C172 182 142 182 128 156 C114 130 84 130 84 156 C84 182 114 182 128 156 Z'
file_icon('file-infinity', ['file infinity', 'document', 'page', 'file', 'infinity'], [P(inf)])

file_icon('file-info', ['file info', 'details', 'document', 'i'], [L(128, 148, 128, 192)], dotcut=[C(128, 112, 16)])

file_icon('file-invoice', ['file invoice', 'document', 'page', 'file', 'invoice'],
          [P('M128 64 V54'), P('M128 124 V134')] + g_S(106, 64, 44, 60) +
          [L(88, 168, 168, 168), L(88, 200, 136, 200)])

lam_a, lam_b = (108, 116), (160, 196)
lam_m = (lam_a[0] + (lam_b[0] - lam_a[0]) * 0.42, lam_a[1] + (lam_b[1] - lam_a[1]) * 0.42)
file_icon('file-lambda', ['file lambda', 'document', 'page', 'file', 'lambda'],
          [PL([(92, 116), lam_a, lam_b]), L(*lam_m, 96, 196)])

file_icon('file-neutral', ['file neutral', 'document', 'page', 'file', 'neutral'],
          [L(100, 180, 156, 180)], dotcut=[C(104, 136, 14), C(152, 136, 14)])

pc = (128, 160)
file_icon('file-power', ['file power', 'document', 'page', 'file', 'power'],
          [L(128, 112, 128, 156), P(f'M{pt(polar(pc, 34, -126))} ' + arc_to(pc, 34, polar(pc, 34, -126), polar(pc, 34, -54), lambda m: m[1]))])

file_icon('file-percent', ['file percent', 'document', 'page', 'file', 'percent'],
          [L(160, 116, 96, 196)], dotcut=[C(100, 128, 14), C(156, 184, 14)])

file_icon('file-question', ['unknown file', 'file', 'question', 'missing', 'quiz'],
          [P('M104 124 A24 24 0 1 1 138 145.8 C131 149 128 152 128 158 V160')], dotcut=[C(128, 192, 14)])

eye = load('eye')['line'][0]
file_icon('file-eye-slash', ['hidden file', 'private', 'invisible', 'document'],
          [xform(eye, 0.46, (128, 128), (128, 156)), L(92, 120, 164, 192)], dotcut=[C(128, 156, 14)])

# ================================================================= landscape and composites
LAND = 'M32 56 H176 L224 104 V200 H32 Z'
icon('file-horizontal', F, ['file horizontal', 'document', 'page', 'file', 'horizontal'],
     line=[P(LAND)], detail=[P('M176 56 V104 H224')], area=[P(LAND)])

SMALL = 'M84 32 H140 L172 64 V144 H84 Z'
icon('file-network', F, ['shared file', 'network', 'document', 'server'],
     line=[P(SMALL), L(128, 144, 128, 208), L(32, 208, 104, 208), L(152, 208, 224, 208)],
     detail=[P('M140 32 V64 H172')], area=[P(SMALL)], dot=[C(128, 208, 20)])

ORI = 'M40 112 H96 L128 144 V224 H40 Z'
oc, orr = (84, 168), 104
o_end = polar(oc, orr, 0)
icon('file-orientation', F, ['file orientation', 'document', 'page', 'file', 'orientation'],
     line=[P(ORI), P(f'M{pt(polar(oc, orr, -90))} A{orr} {orr} 0 0 1 {pt(o_end)}'), PL(head(o_end, 90, 24))],
     detail=[P('M96 112 V144 H128')], area=[P(ORI)])

# ================================================================= badges in the lower-right corner
env = load('envelope-gear')
badge_file('file-gear', ['file settings', 'config', 'document', 'preferences', 'configure'], R=60,
           line=[env['line'][1]], area=[env['area'][1]], hole=env['hole'])

pen = load('database-pencil')
badge_file('file-pencil', ['edit document', 'write', 'modify file', 'file', 'pencil'], R=64,
           line=[pen['line'][1]], area=[pen['area'][1]])

badge_file('file-prohibit', ['file blocked', 'document', 'restricted', 'prohibit', 'blocked'], R=66,
           line=[C(184, 184, 36)], area=[C(184, 184, 36)],
           detail=[L(*polar(B, 36, 225), *polar(B, 36, 45))])

badge_file('file-export', ['export file', 'document', 'arrow out', 'save as'], R=64,
           line=[L(148, 184, 216, 184), PL(head((216, 184), 0, 24))])
badge_file('file-import', ['import file', 'document', 'arrow in', 'load'], R=64,
           line=[L(216, 184, 148, 184), PL(head((148, 184), 180, 24))])

phone = load('phone')['line'][0]
ph = xform(phone, 0.4, (128, 128), B)
badge_file('file-phone', ['file phone', 'document', 'page', 'file', 'phone'], R=68, line=[ph], area=[ph])

# ================================================================= slash
img = load('file-image')
runs = []
for seg in [DOC]:
    runs += clip_polyline(seg, off_slash, closed=True)
inner = clip_polyline([(84, 192), (116, 152), (140, 176), (152, 164), (172, 184)], lambda p: off_slash(p, 20))
fold_runs = clip_polyline([(152, 32), (152, 80), (200, 80)], off_slash)
icon('file-image-slash', F, ['no image', 'image off', 'document', 'slash'],
     line=[PL(r_) for r_ in runs + fold_runs + inner] + [SLASH])

# ================================================================= labelled file types
for nm, s, tags in [
    ('file-doc', 'DOC', ['doc', 'word', 'document', 'file type', 'word document']),
    ('file-exe', 'EXE', ['exe', 'executable', 'program', 'file type']),
    ('file-gif', 'GIF', ['gif', 'animation', 'image', 'file type', 'image file']),
    ('file-heic', 'HEIC', ['heic', 'photo', 'image', 'file type']),
    ('file-html', 'HTML', ['html', 'web', 'code', 'file type', 'web page']),
    ('file-java', 'JAVA', ['java', 'code', 'source', 'file type']),
    ('file-jpg', 'JPG', ['jpg', 'jpeg', 'photo', 'file type', 'photo file']),
    ('file-js', 'JS', ['js', 'javascript', 'code', 'file type', 'script']),
    ('file-json', 'JSON', ['json', 'data', 'code', 'file type']),
    ('file-jsx', 'JSX', ['jsx', 'code', 'component', 'file type', 'react component']),
    ('file-key', 'KEY', ['key', 'keynote', 'presentation', 'file type']),
    ('file-m4p', 'M4P', ['m4p', 'audio', 'music', 'file type']),
    ('file-md', 'MD', ['md', 'markdown', 'text', 'file type', 'readme']),
    ('file-mdx', 'MDX', ['mdx', 'markdown', 'component', 'file type']),
    ('file-mov', 'MOV', ['mov', 'video', 'movie', 'file type']),
    ('file-mp3', 'MP3', ['mp3', 'audio', 'music', 'file type']),
    ('file-mp4', 'MP4', ['mp4', 'video', 'movie', 'file type']),
    ('file-otf', 'OTF', ['otf', 'font', 'typeface', 'file type']),
    ('file-pdf', 'PDF', ['pdf', 'document', 'file type', 'acrobat', 'file']),
    ('file-php', 'PHP', ['php', 'code', 'server', 'file type', 'script']),
    ('file-png', 'PNG', ['png', 'image', 'graphic', 'file type', 'image file']),
    ('file-ppt', 'PPT', ['ppt', 'powerpoint', 'slides', 'file type', 'presentation']),
    ('file-psd', 'PSD', ['psd', 'layered image', 'design', 'file type']),
    ('file-py', 'PY', ['py', 'python', 'code', 'file type']),
]:
    type_icon(nm, tags, s)

print(save(overwrite=True))
