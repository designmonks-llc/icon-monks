import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Design'
SLASH = L(48, 48, 208, 208)
BADGE = (184, 184)


# ---------------------------------------------------------------- helpers
def rpoly(points, r, close=True):
    """Polygon path with rounded corners; r is a number or a per-vertex list (0 = sharp)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        if not close and (i == 0 or i == n - 1) or rs[i] == 0:
            segs.append((p1, None))
            continue
        a = (p0[0] - p1[0], p0[1] - p1[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        t = rs[i] / math.tan(ang / 2)
        s = (p1[0] + a[0] * t, p1[1] + a[1] * t); e = (p1[0] + b[0] * t, p1[1] + b[1] * t)
        cross = a[0] * b[1] - a[1] * b[0]
        sweep = 0 if cross > 0 else 1
        segs.append((s, f'A{f(rs[i])} {f(rs[i])} 0 0 {sweep} {pt(e)}'))
    d = ''
    for i, (p, arc) in enumerate(segs):
        d += ('M' if i == 0 else ' L') + pt(p)
        if arc:
            d += ' ' + arc
    return d + (' Z' if close else '')


def rrect(cx, cy, w, h, r, deg=0):
    pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    return rpoly(rot(pts, deg, (cx, cy)), r)


def badge_cut(points, B=BADGE, R=56):
    """Open outline of a closed polygon with the part near B removed, and the matching area with a concave notch."""
    n = len(points)
    inside = lambda p: dist(p, B) < R
    hits = []  # (edge index, t, point, entering)
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


def mark(kind, c=BADGE):
    x, y = c
    if kind == 'plus':
        return [L(x, y - 26, x, y + 26), L(x - 26, y, x + 26, y)]
    if kind == 'minus':
        return [L(x - 26, y, x + 26, y)]
    return [L(x - 20, y - 20, x + 20, y + 20), L(x + 20, y - 20, x - 20, y + 20)]


def dashed(points, closed=False, h=24, D0=40, G=40, end_gap=None):
    """Dashed polyline. Corners get an L-shaped dash (h each way), straight runs get evenly spaced dashes
    with gaps near G. Open ends: end_gap=None starts a dash at the end; a number leaves that much gap
    (use where the dashed outline meets a solid shape)."""
    pts = list(points) + ([points[0]] if closed else [])
    cum = [0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + dist(pts[i - 1], pts[i]))
    total = cum[-1]
    reserved = []  # dash intervals in arclength
    corners = cum[1:-1] + ([0, total] if closed else [])
    for c in cum[1:-1]:
        reserved.append((c - h, c + h))
    if closed:
        reserved.append((-h, h)); reserved.append((total - h, total + h))
        stops = [(-h, h)] + [(c - h, c + h) for c in cum[1:-1]] + [(total - h, total + h)]
    else:
        first = (0, h) if end_gap is None else (end_gap - G, end_gap - G)
        last = (total - h, total) if end_gap is None else (total - end_gap + G, total - end_gap + G)
        stops = [first] + [(c - h, c + h) for c in cum[1:-1]] + [last]
    ivs = [s_ for s_ in stops if s_[1] > s_[0]]
    for (a0, a1), (b0, b1) in zip(stops, stops[1:]):
        free = b0 - a1
        nd = max(0, round((free - G) / (D0 + G)))
        while nd and (free - (nd + 1) * G) / nd < 20:
            nd -= 1
        if nd:
            Dd = (free - (nd + 1) * G) / nd
            for j in range(nd):
                st = a1 + G + j * (Dd + G)
                ivs.append((st, st + Dd))

    def at(sv):
        sv = sv % total if closed else sv
        for i in range(1, len(pts)):
            if sv <= cum[i] + 1e-9:
                t = (sv - cum[i - 1]) / (cum[i] - cum[i - 1])
                return (pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t)
        return pts[-1]
    out = []
    for s0, s1 in sorted(ivs):
        if closed and s0 >= total - h - 1e-6:
            continue
        line_pts = [at(s0)]
        for c in cum[1:-1] + ([total] if closed else []):
            for cc in (c, c - total):
                if s0 < cc < s1:
                    line_pts.append(pts[cum.index(c)] if cc == c else pts[0])
        line_pts.append(at(s1))
        out.append(PL(line_pts))
    return out


def arrow_head(tip, direction_deg, arm=40, spread=45):
    a = polar(tip, arm, direction_deg + 180 - spread)
    b = polar(tip, arm, direction_deg + 180 + spread)
    return PL([a, tip, b])


def slash_variant(name, tags, lines):
    icon(name, CAT, tags, line=list(lines) + [SLASH])


# ---------------------------------------------------------------- pentagon family
pent = regular_polygon((128, 138), 100, 5)
icon('pentagon', CAT, ['pentagon', 'shape', 'polygon', 'geometry', 'five sides'], line=[PG(pent)], area=[PG(pent)])
for kind, tags, R_ in (('x', ['pentagon', 'remove', 'delete', 'cancel'], 54),
                       ('plus', ['pentagon', 'add', 'new', 'create'], 56),
                       ('minus', ['pentagon', 'remove', 'subtract'], 56)):
    o, a = badge_cut(pent, R=R_)
    icon(f'pentagon-{kind}', CAT, tags, line=[P(o)] + mark(kind), area=[P(a)])
slash_variant('pentagon-slash', ['pentagon', 'off', 'disabled', 'hidden'], [PG(pent)])

# ---------------------------------------------------------------- perspective
persp = [(84, 52), (172, 52), (224, 204), (32, 204)]
persp_d = rpoly(persp, [8, 8, 8, 8])
icon('perspective', CAT, ['perspective', '3d', 'transform', 'distort'], line=[P(persp_d)], area=[P(persp_d)])
slash_variant('perspective-slash', ['perspective', 'off', 'disabled', 'hidden'], [P(persp_d)])

# ---------------------------------------------------------------- polygon
polyg = [(112, 36), (216, 96), (188, 212), (60, 204), (36, 104)]
icon('polygon', CAT, ['polygon', 'shape', 'vertices', 'irregular'], line=[PG(polyg)], area=[PG(polyg)])
slash_variant('polygon-slash', ['polygon', 'off', 'disabled', 'hidden'], [PG(polyg)])

# ---------------------------------------------------------------- polyhedron (octahedron)
T, Bm, Lp, Rp, F = (128, 32), (128, 224), (36, 120), (220, 120), (112, 148)
oct_out = [T, Rp, Bm, Lp]
F = (110, 150)
oct_det = [PL([Lp, F, Rp]), L(*T, *F), L(*F, *Bm)]
icon('polyhedron', CAT, ['polyhedron', '3d shape', 'gem', 'geometry'],
     line=[PG(oct_out)], detail=oct_det, area=[PG(oct_out)])
slash_variant('polyhedron-slash', ['polyhedron', 'off', 'disabled', 'hidden'], [PG(oct_out)] + oct_det)

# ---------------------------------------------------------------- polyline
nodes = [(52, 188), (104, 76), (152, 180), (204, 68)]
pl_lines, pl_nodes = [], []
hs = 16
for i, n_ in enumerate(nodes):
    pl_nodes.append(R(n_[0] - hs, n_[1] - hs, 2 * hs, 2 * hs, 6))
    if i:
        a, b = nodes[i - 1], n_
        d = dist(a, b); u = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
        t = hs / max(abs(u[0]), abs(u[1]))
        pl_lines.append(L(a[0] + u[0] * t, a[1] + u[1] * t, b[0] - u[0] * t, b[1] - u[1] * t))
icon('polyline', CAT, ['polyline', 'path', 'vector', 'connected points'], line=pl_lines + pl_nodes, area=pl_nodes)

# ---------------------------------------------------------------- radius
icon('radius', CAT, ['corner radius', 'circle radius', 'measure'],
     line=[C(128, 128, 96)], detail=[L(128, 128, 192, 128)], area=[C(128, 128, 96)], dotcut=[C(128, 128, 16)])

# ---------------------------------------------------------------- rectangles
icon('rectangle', CAT, ['rectangle', 'shape', 'geometry', 'box'], line=[R(32, 56, 192, 144, 16)], area=[R(32, 56, 192, 144, 16)])
icon('rectangle-vertical', CAT, ['rectangle', 'portrait', 'shape', 'vertical'],
     line=[R(56, 32, 144, 192, 16)], area=[R(56, 32, 144, 192, 16)])

prism = [(32, 96), (80, 48), (224, 48), (224, 176), (176, 224), (32, 224)]
prism_det = [PL([(32, 96), (176, 96), (176, 224)]), L(176, 96, 224, 48)]
icon('rectangular-prism', CAT, ['cuboid', 'box', '3d shape', 'prism'], line=[PG(prism)], detail=prism_det, area=[PG(prism)])
slash_variant('rectangular-prism-slash', ['rectangular prism', 'off', 'disabled', 'hidden', 'rectangular'],
              [PG(prism)] + prism_det)

# ---------------------------------------------------------------- resize
icon('resize', CAT, ['custom size', 'scale', 'dimensions', 'resize', 'corner handle'],
     line=[R(32, 32, 192, 192, 16)],
     detail=[L(84, 172, 172, 84), PL([(128, 84), (172, 84), (172, 128)]), PL([(84, 128), (84, 172), (128, 172)])],
     area=[R(32, 32, 192, 192, 16)])

# ---------------------------------------------------------------- rhombus
s = 144 / 2
rh = rot([(128 - s, 128 - s), (128 + s, 128 - s), (128 + s, 128 + s), (128 - s, 128 + s)], 45)
rh_d = rpoly(rh, 14)
icon('rhombus', CAT, ['rhombus', 'diamond shape', 'square rotated', 'shape'], line=[P(rh_d)], area=[P(rh_d)])
slash_variant('rhombus-slash', ['rhombus', 'off', 'disabled', 'hidden'], [P(rh_d)])

# ---------------------------------------------------------------- rotate
# rotate-3d: sphere under a clockwise arc arrow (same head as arrow-clockwise)
sc, sr = (128, 144), 60
oc, orr = (128, 144), 96
o_s, o_e = polar(oc, orr, 200), polar(oc, orr, 325)
icon('rotate-3d', CAT, ['rotate 3d', 'orbit', 'transform', 'view'],
     line=[C(*sc, sr), P(f'M{pt(o_s)} A{orr} {orr} 0 0 1 {pt(o_e)}'),
           PL([(o_e[0] - 34, o_e[1]), o_e, (o_e[0], o_e[1] - 34)])],
     detail=[P(f'M{f(sc[0] - sr)} {f(sc[1])} A{sr} 22 0 0 0 {f(sc[0] + sr)} {f(sc[1])}')],
     area=[C(*sc, sr)])

ac = load('arrow-clockwise')
icon('rotate-dot', CAT, ['rotate', 'pivot', 'transform', 'center'], line=ac['line'], dot=[C(128, 132, 16)])

# rotate-right / rotate-left / rotate-rectangle: a shape inside a larger clockwise arrow (arrow-clockwise style)
rc_, rr_ = (128, 130), 90
r_end = polar(rc_, rr_, -45)
rot_arrow = [P(f'M{pt(polar(rc_, rr_, 0))} A{rr_} {rr_} 0 1 1 {pt(r_end)}'),
             PL([(r_end[0] - 34, r_end[1]), r_end, (r_end[0], r_end[1] - 34)])]
sq = R(92, 94, 72, 72, 12)
icon('rotate-right', CAT, ['rotate', 'clockwise', 'turn', 'transform'], line=rot_arrow + [sq], area=[sq])


def mirror(el):
    import re
    if el.startswith('<rect'):
        m = dict(re.findall(r'(\w+)="([^"]+)"', el))
        x, w = float(m['x']), float(m['width'])
        return R(256 - x - w, float(m['y']), w, float(m['height']), float(m.get('rx', 0)))
    d = re.search(r'd="([^"]+)"', el).group(1)
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        tk = toks[i]
        if tk.isalpha():
            cmd = tk; out.append(tk); i += 1; continue
        if cmd in 'ML':
            out += [f(256 - float(toks[i])), toks[i + 1]]; i += 2
        elif cmd == 'A':
            rx, ry, xr, la, sw, x, y = toks[i:i + 7]
            out += [rx, ry, xr, la, str(1 - int(sw)), f(256 - float(x)), y]; i += 7
        elif cmd == 'H':
            out.append(f(256 - float(tk))); i += 1
        else:
            out.append(tk); i += 1
    return P(' '.join(out))


icon('rotate-left', CAT, ['rotate', 'counterclockwise', 'turn', 'transform'],
     line=[mirror(e) for e in rot_arrow] + [mirror(sq)], area=[mirror(sq)])

tilt = rrect(128, 130, 56, 88, 10, 30)
icon('rotate-rectangle', CAT, ['rotate shape', 'transform', 'rectangle', 'orientation'],
     line=rot_arrow + [P(tilt)], area=[P(tilt)])

# ---------------------------------------------------------------- ruler-measure
ticks = [L(72, 128, 72, 160), L(112, 128, 112, 176), L(152, 128, 152, 160), L(192, 128, 192, 176)]
icon('ruler-measure', CAT, ['measure', 'ruler', 'dimension', 'size'],
     line=[R(32, 128, 192, 80, 12), L(40, 64, 216, 64), PL([(68, 36), (40, 64), (68, 92)]), PL([(188, 36), (216, 64), (188, 92)])],
     detail=ticks, area=[R(32, 128, 192, 80, 12)])

# ---------------------------------------------------------------- scribble
scrib = ('M32 196 C64 176 88 120 80 84 C72 52 40 72 56 112 C72 152 120 168 140 128 '
         'C156 96 152 60 132 64 C112 68 120 136 168 152 C200 162 216 120 224 96')
scrib_loop = 'M32 176 C80 176 112 160 136 128 C160 96 160 56 128 56 C96 56 96 104 136 136 C168 160 200 160 224 120'
icon('scribble', CAT, ['scribble', 'gesture', 'doodle', 'freehand', 'draw'], line=[P(scrib)])
icon('scribble-loop', CAT, ['scribble', 'doodle', 'freehand'], line=[P(scrib_loop)])
slash_variant('scribble-slash', ['scribble', 'off', 'disabled', 'hidden'], [P(scrib)])

# ---------------------------------------------------------------- selection
sel = load('selection')['line']
icon('selection-all', CAT, ['select all', 'selection', 'marquee', 'everything', 'checkbox'],
     line=sel + [R(80, 80, 96, 96, 10)], area=[R(80, 80, 96, 96, 10)])

front_tl = R(32, 32, 112, 112, 14)
front_br = R(112, 112, 112, 112, 14)
icon('selection-background', CAT, ['send to back', 'layer', 'arrange'],
     line=[front_br] + dashed([(176, 112), (176, 32), (32, 32), (32, 176), (112, 176)], h=24, D0=32, G=36, end_gap=40),
     area=[front_br])
icon('selection-foreground', CAT, ['bring to front', 'layer', 'arrange'],
     line=[front_tl] + dashed([(144, 80), (224, 80), (224, 224), (80, 224), (80, 144)], h=24, D0=32, G=36, end_gap=40),
     area=[front_tl])

# boolean circles
c1, c2, cr = (100, 128), (156, 128), 68
xt, xb = circle_x(c1, cr, c2, cr)
union_d = f'M{pt(xt)} ' + arc_to(c1, cr, xt, xb, lambda m: dist(m, c2)) + ' ' + arc_to(c2, cr, xb, xt, lambda m: dist(m, c1)) + ' Z'
lens_d = f'M{pt(xt)} ' + arc_to(c1, cr, xt, xb, lambda m: -dist(m, c2)) + ' ' + arc_to(c2, cr, xb, xt, lambda m: -dist(m, c1)) + ' Z'
lune1 = f'M{pt(xt)} ' + arc_to(c1, cr, xt, xb, lambda m: dist(m, c2)) + ' ' + arc_to(c2, cr, xb, xt, lambda m: -dist(m, c1)) + ' Z'
lune2 = f'M{pt(xt)} ' + arc_to(c2, cr, xt, xb, lambda m: dist(m, c1)) + ' ' + arc_to(c1, cr, xb, xt, lambda m: -dist(m, c2)) + ' Z'
icon('selection-exclude', CAT, ['exclude', 'boolean', 'difference', 'shapes'],
     line=[C(*c1, cr), C(*c2, cr)], area=[P(lune1), P(lune2)])
icon('selection-intersect', CAT, ['intersect', 'boolean', 'overlap', 'shapes'],
     line=[C(*c1, cr), C(*c2, cr)], area=[P(lens_d)])
icon('selection-union', CAT, ['union', 'boolean', 'combine', 'shapes'], line=[P(union_d)], area=[P(union_d)])

tri_inv = rpoly([(180, 76), (180, 180), (76, 180)], 10)
icon('selection-inverse', CAT, ['invert selection', 'inverse', 'marquee'], line=sel + [P(tri_inv)], area=[P(tri_inv)])

sel_trim = [sel[0], sel[1], sel[3], sel[4], sel[6], L(104, 216, 136, 216), L(216, 104, 216, 136)]
icon('selection-plus', CAT, ['add to selection', 'expand', 'marquee'], line=sel_trim + mark('plus'))
icon('selection-slash', CAT, ['deselect', 'clear selection', 'marquee', 'dashed', 'slash'],
     line=sel + [L(80, 80, 176, 176)])

sub_l = rpoly([(32, 32), (160, 32), (160, 96), (96, 96), (96, 160), (32, 160)], [14, 14, 6, 14, 6, 14])
icon('selection-subtract', CAT, ['subtract', 'boolean', 'minus front', 'shapes'],
     line=[P(sub_l)] + dashed([(160, 96), (224, 96), (224, 224), (96, 224), (96, 160)], h=26, D0=24, G=36, end_gap=36),
     area=[P(sub_l)])

# ---------------------------------------------------------------- arrange
def visible(points, r=14):
    return rpoly(points, [0] + [r] * (len(points) - 2) + [0], close=False)


back_vis = [(160, 96), (224, 96), (224, 224), (96, 224), (96, 160)]
back_area = rpoly(back_vis + [(160, 160)], [0, 14, 14, 14, 0, 0])
icon('send-to-back', CAT, ['arrange', 'layer', 'back', 'order', 'send backward'],
     line=[R(32, 32, 128, 128, 14), P(visible(back_vis))], area=[P(back_area)])

mid_vis = [(128, 80), (176, 80), (176, 176), (80, 176), (80, 128)]
mid_area = rpoly(mid_vis + [(128, 128)], [0, 12, 12, 12, 0, 0])
far_vis = [(176, 128), (224, 128), (224, 224), (128, 224), (128, 176)]
icon('send-backward', CAT, ['send backward', 'layer', 'arrange', 'order', 'layers'],
     line=[R(32, 32, 96, 96, 12), P(visible(mid_vis, 12)), P(visible(far_vis, 12))], area=[P(mid_area)])

# ---------------------------------------------------------------- shadow
sh_front = R(32, 32, 152, 152, 16)
sh_line = 'M216 72 V200 A16 16 0 0 1 200 216 H72'
sh_area = 'M184 72 H216 V200 A16 16 0 0 1 200 216 H72 V184 H184 Z'
icon('shadow', CAT, ['shadow', 'drop shadow', 'depth', 'effect'], line=[sh_front, P(sh_line)], area=[P(sh_area)])
slash_variant('shadow-slash', ['shadow', 'off', 'disabled', 'hidden'], [sh_front, P(sh_line)])

# ---------------------------------------------------------------- shape-divide
def shift(points, d):
    return [(x + d, y + d) for x, y in points]


dv_a = [(32, 32), (120, 32), (120, 72), (72, 72), (72, 120), (32, 120)]
dv_b = shift([(72, 72), (120, 72), (120, 120), (72, 120)], 32)
dv_c = shift([(120, 72), (160, 72), (160, 160), (72, 160), (72, 120), (120, 120)], 64)
dv = [P(rpoly(dv_a, [10, 8, 8, 6, 8, 10])), P(rpoly(dv_b, 8)), P(rpoly(dv_c, [8, 10, 10, 10, 8, 6]))]
icon('shape-divide', CAT, ['divide', 'boolean', 'split', 'pathfinder'], line=dv, area=dv)

# ---------------------------------------------------------------- shapes
tri_s = PG([(128, 32), (170, 104), (86, 104)])
shapes_l = [tri_s, C(72, 180, 40), R(144, 140, 80, 80, 12)]
icon('shapes', CAT, ['shapes', 'interests', 'circle square triangle', 'geometry', 'square circle triangle'],
     line=shapes_l, area=shapes_l)
slash_variant('shapes-slash', ['shapes', 'off', 'disabled', 'hidden'], shapes_l)

# ---------------------------------------------------------------- skew
skh = rpoly([(96, 56), (224, 56), (160, 200), (32, 200)], 8)
icon('skew-horizontal', CAT, ['skew x', 'slant', 'transform', 'shear'], line=[P(skh)], area=[P(skh)])
skv = rpoly([(56, 96), (200, 32), (200, 160), (56, 224)], 8)
icon('skew-vertical', CAT, ['skew y', 'slant', 'transform', 'shear'], line=[P(skv)], area=[P(skv)])

# ---------------------------------------------------------------- spacing
sp_h = [L(40, 40, 40, 216), L(216, 40, 216, 216), L(80, 128, 176, 128),
        PL([(104, 104), (80, 128), (104, 152)]), PL([(152, 104), (176, 128), (152, 152)])]
icon('spacing-horizontal', CAT, ['horizontal spacing', 'gap', 'padding', 'layout'], line=sp_h)
sp_v = [L(40, 40, 216, 40), L(40, 216, 216, 216), L(128, 80, 128, 176),
        PL([(104, 104), (128, 80), (152, 104)]), PL([(104, 152), (128, 176), (152, 152)])]
icon('spacing-vertical', CAT, ['vertical spacing', 'gap', 'padding', 'layout'], line=sp_v)

# ---------------------------------------------------------------- sphere
eq = P('M32 128 A96 36 0 0 0 224 128')
icon('sphere', CAT, ['sphere', 'ball', '3d', 'globe'], line=[C(128, 128, 96)], detail=[eq], area=[C(128, 128, 96)])
slash_variant('sphere-slash', ['sphere', 'off', 'disabled', 'hidden'], [C(128, 128, 96), eq])

print(save(overwrite=True))
