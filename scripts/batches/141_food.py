import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path

SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- local helpers
def smooth(points, t=1.0):
    """Closed Catmull-Rom spline through points, as cubic path data."""
    n = len(points)
    d = 'M' + pt(points[0])
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * t, p1[1] + (p2[1] - p0[1]) / 6 * t)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * t, p2[1] - (p3[1] - p1[1]) / 6 * t)
        d += f' C{pt(c1)} {pt(c2)} {pt(p2)}'
    return d + ' Z'


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


def union_d(ds):
    acc = None
    for d in ds:
        q = _pp([d])
        q.simplify()
        acc = q if acc is None else pathops.op(acc, q, pathops.PathOp.UNION)
    return _d(acc)


class _Flat(BasePen):
    def __init__(self, step=3):
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


def flatten(d, step=3):
    pen = _Flat(step)
    parse_path(d, pen)
    out = []
    for s in pen.subs:
        closed = s[-1] == 'closed'
        out.append(([p for p in s if p != 'closed'], closed))
    return out


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def occlude(d, front, gap=20, step=2):
    """Parts of path d that stay `gap` units clear of the closed shapes in `front` (list of path data)."""
    fp = _pp(front)
    edges = []
    for pts, _ in sum((flatten(x, 2) for x in front), []):
        edges += list(zip(pts, pts[1:]))

    def visible(p):
        if fp.contains(p):
            return False
        return all(_seg_dist(p, a, b) >= gap for a, b in edges)

    out = []
    for pts, closed in flatten(d, step):
        runs, cur = [], []
        for p in pts:
            if visible(p):
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        if closed and len(runs) > 1 and runs[0][0] == pts[0] and runs[-1][-1] == pts[-1]:
            runs[0] = runs.pop() + runs[0][1:]
        if closed and len(runs) == 1 and len(runs[0]) == len(pts):
            out.append(P(d)); continue
        for r in runs:
            if len(r) > 1:
                out.append(P('M' + ' L'.join(f'{x:.1f} {y:.1f}'.replace('.0 ', ' ') for x, y in r)))
    return out


def cut_d(d, front, grow=16):
    """Closed shape d minus the closed shapes in front grown by `grow` units (for areas behind other parts)."""
    a = _pp([d]); a.simplify()
    g = _pp(front); g.simplify()
    st = _pp(front)
    st.stroke(grow * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    st.convertConicsToQuads(0.05)
    st.simplify()
    g = pathops.op(g, st, pathops.PathOp.UNION)
    return _d(pathops.op(a, g, pathops.PathOp.DIFFERENCE))


def inter_d(d, poly_pts):
    a = _pp([d]); a.simplify()
    b = _pp([poly(poly_pts, True)]); b.simplify()
    return _d(pathops.op(a, b, pathops.PathOp.INTERSECTION))


SLASH_SHAPE = capsule((128, 128), 113.1, 1, (0.7071, 0.7071))


def clear_of_slash(d, gap=24):
    pts = sum((x[0] for x in flatten(d, 2)), [])
    return all(abs((x - y)) / math.sqrt(2) >= gap or not (48 - gap < (x + y) / 2 < 208 + gap) for x, y in pts)


def slashed(elements, gap=20):
    """Elements with a clear gap cut around the standard slash, plus the slash itself."""
    out = []
    for e in elements:
        import re
        m = re.search(r' d="([^"]+)"', e)
        if m:
            d = m.group(1)
        else:
            from xml.etree import ElementTree as ET
            el = ET.fromstring(e)
            if el.tag == 'circle':
                cx, cy, r = (float(el.get(k)) for k in ('cx', 'cy', 'r'))
                d = f'M{cx - r} {cy} A{r} {r} 0 1 1 {cx + r} {cy} A{r} {r} 0 1 1 {cx - r} {cy} Z'
            else:
                raise ValueError(e)
        out += occlude(d, [SLASH_SHAPE], gap)
    return out + [SLASH]


def lens(a, b, bulge):
    """Closed leaf/lens shape between points a and b; bulge = half width."""
    l = dist(a, b) / 2
    r = (l * l + bulge * bulge) / (2 * bulge)
    return f'M{pt(a)} A{f(r)} {f(r)} 0 0 1 {pt(b)} A{f(r)} {f(r)} 0 0 1 {pt(a)} Z'


def els(x):
    """Wrap raw path data strings as path elements."""
    return [P(d) for d in x]




def rounded_polygon(points, r):
    """Closed polygon with every corner rounded by radius r (r may be a list)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        a = (p0[0] - p1[0], p0[1] - p1[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        t = rs[i] / math.tan(ang / 2)
        s = (p1[0] + a[0] * t, p1[1] + a[1] * t); e = (p1[0] + b[0] * t, p1[1] + b[1] * t)
        cross = a[0] * b[1] - a[1] * b[0]
        segs.append((s, e, rs[i], 0 if cross > 0 else 1))
    d = 'M' + pt(segs[0][1])
    for i in range(1, n + 1):
        s, e, rr, sw = segs[i % n]
        d += f' L{pt(s)} A{f(rr)} {f(rr)} 0 0 {sw} {pt(e)}'
    return d + ' Z'


def squiggle(x, y0, y1, amp=12):
    """Short vertical wavy line (steam)."""
    h = (y1 - y0) / 2
    return P(f'M{f(x)} {f(y0)} C{f(x - amp)} {f(y0 + h * 0.5)} {f(x + amp)} {f(y0 + h * 1.5)} {f(x)} {f(y1)}')


# ---------------------------------------------------------------- egg family
EGG = 'M128 32 C172 32 200 108 200 148 A72 72 0 0 1 56 148 C56 108 84 32 128 32 Z'


def egg_d(cx, top, s):
    """The library egg scaled by s, top point at (cx, top)."""
    X = lambda x: f(cx + (x - 128) * s)
    Y = lambda y: f(top + (y - 32) * s)
    r = f(72 * s)
    return (f'M{X(128)} {Y(32)} C{X(172)} {Y(32)} {X(200)} {Y(108)} {X(200)} {Y(148)} '
            f'A{r} {r} 0 0 1 {X(56)} {Y(148)} C{X(56)} {Y(108)} {X(84)} {Y(32)} {X(128)} {Y(32)} Z')


egg = load('egg')
icon('egg-crack', 'Food', ['cracked egg', 'breaking', 'cooking', 'egg', 'cracked'],
     line=egg['line'], area=egg['area'],
     detail=[PL([(60, 128), (88, 104), (112, 136), (140, 104), (164, 136), (196, 112)])])

fried = smooth([polar((128, 128), r, a) for a, r in
                ((-96, 92), (-38, 88), (14, 96), (72, 84), (128, 96), (196, 90))])
icon('egg-fried', 'Food', ['fried egg', 'breakfast', 'sunny side up', 'egg', 'food'],
     line=[P(fried)], detail=[C(120, 120, 36)], area=[P(fried)])

icon('egg-slash', 'Food', ['egg', 'disabled', 'off', 'food'], line=egg['line'] + [SLASH])

back = egg_d(96, 36, 0.66)
front = egg_d(160, 92, 0.70)
icon('eggs', 'Food', ['eggs', 'breakfast', 'groceries'],
     line=occlude(back, [front], 24) + [P(front)], area=[P(cut_d(back, [front], 16)), P(front)])

# ---------------------------------------------------------------- dishes
dc = (128, 160)
dv = [polar(dc, 88, a) for a in range(195, 346, 30)]
dump = f'M{pt(dv[0])}' + ''.join(f' A30 30 0 0 1 {pt(dv[i + 1])}' for i in range(len(dv) - 1)) + \
    f' C200 204 56 204 {pt(dv[0])} Z'
icon('dumpling', 'Food', ['dumpling', 'dim sum', 'gyoza', 'food'],
     line=[P(dump)], area=[P(dump)],
     detail=[L(*polar(dc, 88, a), *polar(dc, 64, a)) for a in range(225, 316, 30)])

head = 'M40 128 C48 100 66 88 88 88 V168 C66 168 48 156 40 128 Z'
tail = PG([(192, 128), (224, 92), (224, 164)])
icon('fish-bone', 'Food', ['fish bone', 'skeleton', 'leftovers', 'cat food'],
     line=[P(head), L(88, 128, 192, 128), P('M122 92 Q134 128 122 164'), P('M154 100 Q164 128 154 156'), tail],
     area=[P(head), tail], dotcut=[C(64, 120, 12)])

box = R(36, 92, 60, 52, 10)
cowl = 'M36 180 C36 160 52 144 76 144 H108 L120 180 Z'
icon('food-delivery', 'Food', ['takeaway', 'delivery', 'takeout', 'food'],
     line=[C(68, 200, 18), C(196, 200, 18), P(cowl), P('M120 180 H156 C172 180 180 168 178 152 L164 96'),
           L(178, 152, 196, 200), L(148, 92, 172, 100), box],
     detail=[L(56, 118, 76, 118)], area=[box, P(cowl)])

icon('fork', 'Food', ['fork', 'utensil', 'eat', 'cutlery'],
     line=[P('M88 32 V80 A40 40 0 0 0 168 80 V32'), L(128, 32, 128, 224)])

fk = load('fork-knife')
icon('fork-knife-slash', 'Food', ['no food', 'no eating', 'fasting', 'food off'], line=fk['line'] + [SLASH])

carton = 'M48 112 C96 132 160 132 208 112 L188 206 Q185 220 170 220 H86 Q71 220 68 206 Z'
icon('french-fries', 'Food', ['fries', 'chips', 'fast food', 'potato'],
     line=[P(carton), L(84, 122, 72, 48), L(112, 126, 108, 36), L(144, 126, 148, 36), L(172, 122, 184, 48)],
     area=[P(carton)])

bowl = 'M40 136 H216 A88 88 0 0 1 40 136 Z'
fl = 'M56 112 A32 32 0 1 1 120 112 A32 32 0 1 1 56 112 Z'
fb = 'M116 96 A40 40 0 1 1 196 96 A40 40 0 1 1 116 96 Z'
icon('fruit-bowl', 'Food', ['fruit', 'bowl', 'produce', 'healthy'],
     line=[P(bowl)] + occlude(fl, [bowl], 0.1) + occlude(fb, [bowl, fl], 20)
     + [P('M156 56 C156 50 158 45 162 40'), P(lens((166, 45), (204, 43), 10))],
     area=[P(bowl), P(cut_d(fl, [bowl], 12)), P(cut_d(fb, [bowl, fl], 16)), P(lens((166, 45), (204, 43), 10))])

u = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
grip = capsule((190, 66), 22, 14, u)
icon('frying-pan', 'Food', ['skillet', 'frying pan', 'cook', 'kitchen'],
     line=[C(100, 156, 68), P(grip), L(148, 108, 170, 86)], detail=[C(100, 156, 40)],
     area=[C(100, 156, 68), P(grip)])

garlic = 'M128 36 C128 64 208 88 208 152 C208 196 172 216 128 216 C84 216 48 196 48 152 C48 88 128 64 128 36 Z'
icon('garlic', 'Food', ['garlic', 'bulb', 'clove', 'cooking'],
     line=[P(garlic)], area=[P(garlic)],
     detail=[P('M104 104 C80 136 84 184 108 212'), P('M152 104 C176 136 172 184 148 212')])

# ---------------------------------------------------------------- glasses
GLASS = 'M64 40 H192 L180 202 Q178 224 156 224 H100 Q78 224 76 202 Z'
icon('glass', 'Food', ['drinking glass', 'water', 'empty glass', 'glass', 'tumbler'],
     line=[P(GLASS)], detail=[L(98, 76, 102, 128)], area=[P(GLASS)])
icon('glass-half', 'Food', ['half full', 'drink', 'water level'],
     line=[P(GLASS), L(71, 132, 185, 132)], area=[P('M71 132 H185 L180 202 Q178 224 156 224 H100 Q78 224 76 202 Z')])
icon('glass-water', 'Food', ['water', 'glass', 'drink', 'hydration', 'cup'],
     line=[P(GLASS), P('M68 100 C88 88 104 88 128 100 C152 112 168 112 188 100')],
     area=[P('M68 100 C88 88 104 88 128 100 C152 112 168 112 188 100 L180 202 Q178 224 156 224 H100 Q78 224 76 202 Z')])
icon('glass-slash', 'Food', ['glass', 'off', 'disabled', 'hidden'], line=[P(GLASS), SLASH])

tall = 'M72 48 H180 L172 206 Q171 224 154 224 H98 Q81 224 80 206 Z'
lemon_c = 'M128 80 A44 44 0 1 1 216 80 A44 44 0 1 1 128 80 Z'
icon('gin-glass', 'Food', ['gin tonic', 'highball', 'drink', 'bar'],
     line=occlude(tall, [lemon_c], 22) + [C(172, 80, 44)],
     detail=[L(*polar((172, 80), 10, a), *polar((172, 80), 26, a)) for a in range(-90, 270, 60)],
     area=[P(cut_d(tall, [lemon_c], 16)), C(172, 80, 44)], dotcut=[C(108, 188, 12), C(128, 152, 10)])

tulip = 'M84 40 H172 C172 72 152 88 152 112 C152 136 172 148 172 168 A16 16 0 0 1 156 184 H100 A16 16 0 0 1 84 168 C84 148 104 136 104 112 C104 88 84 72 84 40 Z'
icon('glass-tea', 'Food', ['tea', 'glass', 'drink', 'hot'],
     line=[P(tulip), L(56, 216, 200, 216)], area=[P(tulip)])

wine = load('wine')
icon('glass-broken', 'Objects', ['broken glass', 'fragile', 'goblet', 'damage', 'cracked'],
     line=wine['line'], area=wine['area'], detail=[PL([(112, 32), (126, 58), (108, 78), (124, 104)])])

cup = 'M56 32 H200 V64 A72 72 0 0 1 56 64 Z'
zz = [(134, 16), (118, 60), (142, 92), (126, 144)]
pieces = [inter_d(cup, [(x - 18, y) for x, y in zz] + [(0, 144), (0, 16)]),
          inter_d(cup, [(x + 18, y) for x, y in zz] + [(256, 144), (256, 16)])]
icon('glass-fragile', 'Objects', ['fragile', 'handle with care', 'shipping'],
     line=els(pieces) + [L(128, 152, 128, 208), L(84, 208, 172, 208)], area=els(pieces))

gob = 'M56 40 H200 V64 A72 72 0 0 1 56 64 Z'
foot = 'M128 136 V176 C128 196 100 200 88 216 H168 C156 200 128 196 128 176'
icon('goblet', 'Food', ['goblet', 'chalice', 'cup', 'trophy'],
     line=[P(gob), P(foot)], area=[P(gob)])

# ---------------------------------------------------------------- produce
def grain_parts():
    parts = [lens((128, 86), (128, 32), 13)]
    for y0 in (110, 156, 202):
        for s in (-1, 1):
            e = (128 + s * 48 * math.sin(math.radians(58)), y0 - 48 * math.cos(math.radians(58)))
            parts.append(lens((128, y0), e, 10) if s > 0 else lens(e, (128, y0), 10))
    return parts


gp = grain_parts()
icon('grains', 'Food', ['wheat', 'grain', 'cereal'], line=[L(128, 88, 128, 224)] + els(gp), area=els(gp))
icon('grains-slash', 'Food', ['gluten free', 'no wheat', 'allergy'], line=slashed([L(128, 86, 128, 224)] + els(gp), 18))

grapes = [(76, 100), (128, 100), (180, 100), (102, 146), (154, 146), (128, 192)]
icon('grapes', 'Food', ['grapes', 'fruit', 'wine', 'vineyard'],
     line=[C(x, y, 24) for x, y in grapes] + [P('M128 76 C128 60 130 50 136 42'), P(lens((140, 52), (190, 42), 12))],
     area=[C(x, y, 24) for x, y in grapes] + [P(lens((140, 52), (190, 42), 12))])

kettle = 'M48 104 H208 A80 80 0 0 1 48 104 Z'
grill_lines = [P(kettle), L(88, 173, 72, 224), L(168, 173, 184, 224), squiggle(92, 32, 76), squiggle(128, 32, 76), squiggle(164, 32, 76)]
icon('grill', 'Food', ['barbecue', 'bbq', 'cookout', 'grill'], line=grill_lines, area=[P(kettle)])
icon('grill-slash', 'Food', ['grill', 'off', 'disabled', 'hidden'], line=grill_lines + [SLASH])

handle = R(112, 152, 32, 72, 16)
icon('grill-fork', 'Food', ['barbecue fork', 'bbq', 'utensil', 'grill'],
     line=[P('M100 32 V84 A28 28 0 0 0 156 84 V32'), L(128, 112, 128, 152), handle], area=[handle])

jarb = 'M80 92 C52 108 48 140 48 164 C48 196 72 220 104 220 H152 C184 220 208 196 208 164 C208 140 204 108 176 92 Z'
lid = R(72, 64, 112, 28, 10)
icon('honey-jar', 'Food', ['honey', 'jar', 'sweet', 'bee'],
     line=[P(jarb), lid, L(150, 64, 192, 36)], area=[P(jarb), lid],
     detail=[P('M48 128 H80 V144 A12 12 0 0 0 104 144 V128 H140 V160 A12 12 0 0 0 164 160 V128 H208')])

pot = 'M44 108 A84 28 0 0 1 212 108 V156 A44 44 0 0 1 168 200 H88 A44 44 0 0 1 44 156 Z'
icon('hot-pot', 'Food', ['hot pot', 'fondue', 'soup', 'asian food'],
     line=[P(pot), squiggle(96, 32, 64, 10), squiggle(128, 32, 64, 10), squiggle(160, 32, 64, 10)],
     detail=[P('M44 108 A84 28 0 0 0 212 108'), P('M100 84 C128 92 128 124 156 132')], area=[P(pot)])

ic = load('ice-cream')
icon('ice-cream-slash', 'Food', ['ice cream', 'off', 'disabled', 'hidden', 'ice'], line=ic['line'] + [SLASH])

jar = 'M88 60 V72 C64 80 56 96 56 116 V200 A24 24 0 0 0 80 224 H176 A24 24 0 0 0 200 200 V116 C200 96 192 80 168 72 V60 Z'
jlid = R(72, 32, 112, 28, 8)
icon('jar', 'Food', ['jar', 'preserve', 'container'],
     line=[P(jar), jlid], detail=[R(84, 132, 88, 56, 8)], area=[P(jar), jlid])

jg = 'M60 72 H196 L184 206 Q182 224 162 224 H94 Q74 224 72 206 Z'
half = 'M52 72 A36 36 0 0 1 124 72 Z'
icon('juice', 'Food', ['juice', 'glass', 'drink', 'orange juice'],
     line=[P(jg), P(half), PL([(156, 72), (168, 36), (200, 36)])],
     detail=[L(148, 168, 156, 72)] + [L(88, 72, *polar((88, 72), 24, a)) for a in (-45, -90, -135)],
     area=[P(jg), P(half)])

icon('ladle', 'Food', ['ladle', 'soup spoon', 'kitchen', 'cooking'],
     line=[P('M48 152 H160 A56 56 0 0 1 48 152 Z'), P('M160 152 L192 60 A18 18 0 0 0 158 48')],
     area=[P('M48 152 H160 A56 56 0 0 1 48 152 Z')])


def rotp(d_points, deg):
    return rot(d_points, deg)


lp = [(36, 128), (48, 120), (52, 116), (56, 108), (72, 72), (184, 72), (200, 108), (204, 116), (208, 120), (220, 128),
      (208, 136), (204, 140), (200, 148), (184, 184), (72, 184), (56, 148), (52, 140), (48, 136), (36, 128)]
lp = [(128 + (x - 128) * 0.92, 128 + (y - 128) * 1.2) for x, y in lp]
lp = rot(lp, -24)
lemon = 'M' + pt(lp[0]) + ''.join(f' C{pt(lp[i])} {pt(lp[i + 1])} {pt(lp[i + 2])}' for i in range(1, 18, 3)) + ' Z'
icon('lemon', 'Food', ['lemon', 'citrus', 'fruit', 'sour'],
     line=[P(lemon)], area=[P(lemon)], detail=[P('M92 116 C100 100 112 92 128 88')])

icon('lollipop', 'Food', ['lollipop', 'candy', 'sweet', 'treat'],
     line=[C(128, 96, 64), L(128, 160, 128, 224)], area=[C(128, 96, 64)],
     detail=[P('M124 96 A14 14 0 0 1 152 96 A30 30 0 0 1 92 96')])
icon('lollipop-slash', 'Food', ['lollipop', 'off', 'disabled', 'hidden'],
     line=[C(128, 96, 64), L(128, 160, 128, 224), P('M124 96 A14 14 0 0 1 152 96 A30 30 0 0 1 92 96'), SLASH])

mglass = PG([(32, 64), (224, 64), (128, 160)])
icon('martini', 'Food', ['cocktail', 'martini', 'drink', 'bar', 'nightlife'],
     line=[mglass, L(128, 160, 128, 216), L(88, 216, 168, 216), L(151, 64, 172, 37)],
     detail=[C(118, 100, 12), L(124, 92, 151, 64)], area=[mglass])
icon('martini-slash', 'Food', ['no alcohol', 'cocktail', 'drink', 'prohibited'],
     line=slashed([mglass, L(128, 160, 128, 216), L(88, 216, 168, 216), L(124, 92, 172, 37), C(118, 100, 12)]))

mcup = 'M48 48 H184 L176 206 Q174 224 154 224 H82 Q62 224 60 206 L56 72 Z'
icon('measuring-cup', 'Food', ['measuring cup', 'baking', 'kitchen', 'volume'],
     line=[P(mcup), P('M180 88 H200 A16 16 0 0 1 216 104 V152 A16 16 0 0 1 200 168 H176')],
     detail=[L(92, 104, 124, 104), L(92, 144, 140, 144), L(92, 184, 124, 184)], area=[P(mcup)])

melon = 'M32 80 H224 A96 96 0 0 1 32 80 Z'
icon('melon', 'Food', ['melon', 'watermelon slice', 'fruit', 'summer'],
     line=[P(melon)], area=[P(melon)], detail=[P('M60 80 A68 68 0 0 0 196 80')],
     dotcut=[C(102, 104, 12), C(154, 104, 12), C(128, 124, 12)])

milk = 'M88 32 H168 V56 L192 96 V208 A16 16 0 0 1 176 224 H80 A16 16 0 0 1 64 208 V96 L88 56 Z'
drop = 'M128 124 C140 140 148 152 148 164 A20 20 0 0 1 108 164 C108 152 116 140 128 124 Z'
icon('milk', 'Food', ['milk', 'carton', 'dairy', 'drink'],
     line=[P(milk)], detail=[L(64, 96, 192, 96), L(88, 56, 168, 56), P(drop)], area=[P(milk)])
icon('milk-slash', 'Food', ['milk', 'off', 'disabled', 'hidden'],
     line=[P(milk), L(64, 96, 192, 96), L(88, 56, 168, 56), SLASH])

shake = 'M72 120 H184 L170 208 Q168 224 152 224 H104 Q88 224 86 208 Z'
dome = 'M72 120 C72 88 96 76 128 76 C160 76 184 88 184 120 Z'
icon('milkshake', 'Food', ['milkshake', 'smoothie', 'drink', 'straw'],
     line=[P(shake), L(56, 120, 200, 120), P(dome), PL([(144, 78), (164, 36), (192, 36)])],
     area=[P(shake), P(dome)])

nbowl = 'M40 128 H216 A88 88 0 0 1 40 128 Z'
icon('noodles', 'Food', ['ramen', 'noodle bowl', 'soup', 'chopsticks', 'noodles'],
     line=[P(nbowl), L(40, 56, 216, 32), L(40, 88, 216, 80),
           P('M96 86 C84 100 108 112 96 128'), P('M128 85 C116 100 140 112 128 128'), P('M160 83 C148 100 172 112 160 128')],
     area=[P(nbowl)])

nut = 'M128 32 C184 32 208 80 208 132 C208 188 172 224 128 224 C84 224 48 188 48 132 C48 80 72 32 128 32 Z'
icon('nut', 'Food', ['nut', 'macadamia', 'walnut', 'snack', 'hex nut'],
     line=[P(nut)], area=[P(nut)],
     detail=[L(128, 32, 128, 224), P('M92 76 C76 100 104 116 88 140 C76 160 100 172 92 192'),
             P('M164 76 C180 100 152 116 168 140 C180 160 156 172 164 192')])

oni = rounded_polygon([(128, 12), (240, 208), (16, 208)], [36, 32, 32])
icon('onigiri', 'Food', ['rice ball', 'japanese food', 'snack'],
     line=[P(oni)], area=[P(oni)], detail=[P('M100 208 V156 A8 8 0 0 1 108 148 H148 A8 8 0 0 1 156 156 V208')])

icon('orange', 'Food', ['orange', 'citrus', 'fruit', 'vitamin c'],
     line=[C(128, 140, 84), L(128, 56, 128, 40), P(lens((132, 48), (180, 40), 12))],
     area=[C(128, 140, 84), P(lens((132, 48), (180, 40), 12))],
     detail=[P(f'M{pt(polar((128, 140), 56, 195))} A56 56 0 0 1 {pt(polar((128, 140), 56, 245))}')])

icon('orange-half', 'Food', ['citrus', 'orange slice', 'fruit'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[C(128, 128, 64)] + [L(*polar((128, 128), 18, a), *polar((128, 128), 64, a)) for a in range(-90, 270, 60)])

peach = 'M128 80 C100 60 40 72 40 144 C40 196 80 224 128 224 C176 224 216 196 216 144 C216 72 156 60 128 80 Z'
icon('peach', 'Food', ['peach', 'fruit', 'summer', 'sweet'],
     line=[P(peach), P('M128 80 C128 68 130 60 136 52'), P(lens((136, 56), (180, 36), 13))],
     area=[P(peach), P(lens((136, 56), (180, 36), 13))],
     detail=[P('M128 92 C108 124 108 172 124 204')])

# eggplant: tapered capsule drawn upright, then tilted 45 degrees
c1, r1, c2, r2 = (128, 72), 30, (128, 164), 54
sk = (r2 - r1) / (c2[1] - c1[1]); ck = math.sqrt(1 - sk * sk)
t1r, t2r = (c1[0] + r1 * ck, c1[1] - r1 * sk), (c2[0] + r2 * ck, c2[1] - r2 * sk)
t1l, t2l = (256 - t1r[0], t1r[1]), (256 - t2r[0], t2r[1])
T = lambda *p: rot(list(p), 45)
a1, a2, b2, b1 = T(t1r, t2r, t2l, t1l)
eggplant = f'M{pt(a1)} L{pt(a2)} A{r2} {r2} 0 1 1 {pt(b2)} L{pt(b1)} A{r1} {r1} 0 0 1 {pt(a1)} Z'
calyx = T((94, 84), (110, 116), (128, 96), (146, 116), (162, 84))
icon('eggplant', 'Food', ['eggplant', 'aubergine', 'vegetable', 'food'],
     line=[P(eggplant), PL(T((128, 42), (128, 18)))], detail=[PL(calyx)], area=[P(eggplant)])

gb = union_d([C(128, 64, 32).replace('<circle', '<c') and 'M96 64 A32 32 0 1 1 160 64 A32 32 0 1 1 96 64 Z',
              capsule((128, 124), 68, 20, (1, 0)), 'M88 104 H168 V168 H88 Z',
              capsule((96, 182), 22, 20, (-0.55, 0.835)), capsule((160, 182), 22, 20, (0.55, 0.835))])
icon('gingerbread-man', 'Food', ['gingerbread', 'cookie', 'christmas'],
     line=[P(gb)], area=[P(gb)], dotcut=[C(116, 60, 10), C(140, 60, 10), C(128, 124, 10), C(128, 156, 10)])

print(save(overwrite=True))
