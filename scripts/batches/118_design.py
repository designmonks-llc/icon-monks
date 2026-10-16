import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

D = 'Design'
I = 'Interface'
SLASH = L(48, 48, 208, 208)


def head(tip, ang, size):
    a1 = math.radians(ang + 180 - 45); a2 = math.radians(ang + 180 + 45)
    return [(tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1)), tip,
            (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2))]


def arrow(a, b, size):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return [L(a[0], a[1], b[0], b[1]), PL(head(b, ang, size))]


def seg_circle(a, b, c, r):
    """Intersection parameter points of segment a-b with circle (c, r)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy; B = 2 * (fx * dx + fy * dy); Cc = fx * fx + fy * fy - r * r
    disc = B * B - 4 * A * Cc
    out = []
    if disc >= 0:
        for s in (-1, 1):
            t = (-B + s * math.sqrt(disc)) / (2 * A)
            if 0 <= t <= 1:
                out.append((a[0] + t * dx, a[1] + t * dy))
    return out


# ---------------------------------------------------------------- drops (reuse drop geometry)
DROP = 'M128 32 C104 64 64 112 64 152 A64 64 0 0 0 192 152 C192 112 152 64 128 32 Z'
icon('drop-half', D, ['contrast', 'invert', 'drop', 'tone', 'half drop'],
     line=[P(DROP), L(128, 32, 128, 216)],
     area=[P('M128 32 C152 64 192 112 192 152 A64 64 0 0 1 128 216 Z')])
icon('drop-half-bottom', D, ['opacity', 'transparency', 'drop', 'fill', 'humidity'],
     line=[P(DROP), L(64, 152, 192, 152)],
     area=[P('M64 152 A64 64 0 0 0 192 152 Z')])

# ---------------------------------------------------------------- drop shadow: outlined square, solid offset shadow
front = R(32, 32, 144, 144, 14)
icon('drop-shadow', D, ['shadow', 'depth', 'effect', 'elevation'],
     line=[front, P('M176 80 H210 A14 14 0 0 1 224 94 V210 A14 14 0 0 1 210 224 H94 A14 14 0 0 1 80 210 V176')],
     area=[P('M176 80 H210 A14 14 0 0 1 224 94 V210 A14 14 0 0 1 210 224 H94 A14 14 0 0 1 80 210 V176 H176 Z')])

# ---------------------------------------------------------------- easing curves
ENDS = [C(48, 208, 16), C(208, 48, 16)]
icon('ease-in', D, ['ease in', 'animation', 'curve', 'timing'],
     line=[P('M48 208 C136 208 208 136 208 48')], dot=ENDS)
icon('ease-out', D, ['ease out', 'animation', 'curve', 'timing'],
     line=[P('M48 208 C48 120 120 48 208 48')], dot=ENDS)
icon('ease-in-out', D, ['ease in out', 'animation', 'curve', 'timing'],
     line=[P('M48 208 C144 208 112 48 208 48')], dot=ENDS)
# smooth anchors: the S curve's tangent handles run outward from each end to a control dot
# smooth anchors (solid dots) with tangent handles running outward to hollow control points
icon('ease-in-out-control-points', D, ['easing', 'bezier', 'animation', 'curve'],
     line=[P('M108 196 C160 196 96 60 148 60'), L(108, 196, 66, 196), L(148, 60, 190, 60),
           C(48, 196, 18), C(208, 60, 18)],
     dot=[C(108, 196, 20), C(148, 60, 20)])

# ---------------------------------------------------------------- ellipses
icon('ellipse', D, ['ellipse', 'oval', 'shape', 'geometry', 'horizontal'],
     line=[E(128, 128, 96, 64)], area=[E(128, 128, 96, 64)])
icon('ellipse-vertical', D, ['vertical ellipse', 'oval', 'shape', 'egg'],
     line=[E(128, 128, 64, 96)], area=[E(128, 128, 64, 96)])

# ---------------------------------------------------------------- boolean shapes
SQ1 = R(32, 32, 128, 128, 14)
SQ2 = R(96, 96, 128, 128, 14)
L1 = 'M46 32 H146 A14 14 0 0 1 160 46 V96 H96 V160 H46 A14 14 0 0 1 32 146 V46 A14 14 0 0 1 46 32 Z'
L2 = 'M160 96 H210 A14 14 0 0 1 224 110 V210 A14 14 0 0 1 210 224 H110 A14 14 0 0 1 96 210 V160 H160 Z'
OVER = 'M110 96 H160 V146 A14 14 0 0 1 146 160 H96 V110 A14 14 0 0 1 110 96 Z'
icon('exclude-square', D, ['exclude', 'boolean', 'xor', 'difference', 'shapes'],
     line=[SQ1, SQ2], area=[P(L1), P(L2)])
icon('intersect-square', D, ['intersect', 'boolean', 'overlap', 'shapes', 'pathfinder'],
     line=[SQ1, SQ2], area=[P(OVER)])

ca, cb, rr = (100, 128), (156, 128), 68
t, b = circle_x(ca, rr, cb, rr)
far_a = lambda m: -m[0]
far_b = lambda m: m[0]
near_mid = lambda m: -abs(m[0] - 128)
cres_a = f'M{pt(t)} ' + arc_to(ca, rr, t, b, far_a) + ' ' + arc_to(cb, rr, b, t, far_a) + ' Z'
cres_b = f'M{pt(t)} ' + arc_to(cb, rr, t, b, far_b) + ' ' + arc_to(ca, rr, b, t, far_b) + ' Z'
lens = f'M{pt(t)} ' + arc_to(ca, rr, t, b, far_b) + ' ' + arc_to(cb, rr, b, t, far_a) + ' Z'
icon('exclude', D, ['exclude', 'boolean', 'difference', 'shapes'],
     line=[C(*ca, rr), C(*cb, rr)], area=[P(cres_a), P(cres_b)])
icon('intersect', D, ['join', 'venn', 'intersection', 'overlap', 'relation'],
     line=[C(*ca, rr), C(*cb, rr)], area=[P(lens)])

c3 = (128, 136)
cs = [polar(c3, 40, a) for a in (-90, 30, 150)]
r3 = 60
def inner_x(p, q):
    return min(circle_x(p, r3, q, r3), key=lambda v: dist(v, c3))
v01, v12, v20 = inner_x(cs[0], cs[1]), inner_x(cs[1], cs[2]), inner_x(cs[2], cs[0])
close3 = lambda m: -dist(m, c3)
tri = (f'M{pt(v01)} ' + arc_to(cs[1], r3, v01, v12, close3) + ' ' + arc_to(cs[2], r3, v12, v20, close3)
       + ' ' + arc_to(cs[0], r3, v20, v01, close3) + ' Z')
icon('intersect-three', D, ['venn', 'intersect', 'overlap'],
     line=[C(*p, r3) for p in cs], area=[P(tri)])

# ---------------------------------------------------------------- extrude: slab with an up arrow
slab = PG([(40, 160), (128, 132), (216, 160), (216, 196), (128, 224), (40, 196)])
icon('extrude', D, ['3d', 'extrude', 'modeling'],
     line=[slab] + arrow((128, 104), (128, 32), 30),
     detail=[PL([(40, 160), (128, 188), (216, 160)]), L(128, 188, 128, 224)],
     area=[slab])

# ---------------------------------------------------------------- eyedropper slash
ed = load('eyedropper')
icon('eyedropper-slash', D, ['eyedropper', 'disabled', 'off', 'design'], line=ed['line'] + [SLASH])

# ---------------------------------------------------------------- flips
TRI = [(96, 64), (96, 200), (32, 200)]
MIR = [(256 - x, y) for x, y in TRI]
DASH = [[(128, 32), (128, 56)], [(128, 116), (128, 140)], [(128, 200), (128, 224)]]
icon('flip-horizontal', D, ['flip', 'mirror', 'horizontal', 'reflect', 'transform'],
     line=[PG(TRI), PG(MIR)] + [PL(d) for d in DASH], area=[PG(TRI)])
icon('flip-vertical', D, ['flip', 'mirror', 'vertical', 'reflect', 'transform'],
     line=[PG(rot(TRI, 90)), PG(rot(MIR, 90))] + [PL(rot(d, 90)) for d in DASH], area=[PG(rot(MIR, 90))])

# ---------------------------------------------------------------- frame tool
FRAME = [L(88, 32, 88, 224), L(168, 32, 168, 224), L(32, 88, 224, 88), L(32, 168, 224, 168)]
icon('frame', D, ['artboard', 'canvas', 'frame tool'], line=FRAME, area=[R(88, 88, 80, 80)])
icon('frame-slash', D, ['frame', 'off', 'disabled', 'hidden'], line=FRAME + [SLASH])

# ---------------------------------------------------------------- frustum
fr_sil = 'M80 64 A48 20 0 0 1 176 64 L216 192 A88 28 0 0 1 40 192 Z'
fr_front = 'M80 64 A48 20 0 0 0 176 64'
icon('frustum', D, ['frustum', 'truncated cone', '3d shape', 'geometry'],
     line=[P(fr_sil)], detail=[P(fr_front)], area=[P(fr_sil)])
icon('frustum-slash', D, ['frustum', 'off', 'disabled', 'hidden'], line=[P(fr_sil), P(fr_front), SLASH])

# ---------------------------------------------------------------- hemisphere
hs_sil = 'M32 144 A96 96 0 0 1 224 144 A96 32 0 0 1 32 144 Z'
hs_back = 'M32 144 A96 32 0 0 1 224 144'
icon('hemisphere', D, ['hemisphere', 'half sphere', 'dome', '3d shape'],
     line=[P(hs_sil)], detail=[P(hs_back)], area=[P(hs_sil)])
icon('hemisphere-slash', D, ['hemisphere', 'off', 'disabled', 'hidden'], line=[P(hs_sil), P(hs_back), SLASH])

# ---------------------------------------------------------------- polygons
hept = regular_polygon((128, 133), 98, 7)
icon('heptagon', D, ['heptagon', 'shape', 'seven sides', 'polygon'], line=[PG(hept)], area=[PG(hept)])

HEX = [(128, 32), (211.14, 80), (211.14, 176), (128, 224), (44.86, 176), (44.86, 80)]
BC, BR = (184, 184), 56
e1 = seg_circle(HEX[2], HEX[3], BC, BR)[-1]
e2 = seg_circle(HEX[1], HEX[2], BC, BR)[0]
hex_open = [e1, HEX[3], HEX[4], HEX[5], HEX[0], HEX[1], e2]
hex_area = poly(hex_open) + ' ' + arc_to(BC, BR, e2, e1, lambda m: -dist(m, (128, 128))) + ' Z'
icon('hexagon-plus', D, ['add', 'hexagon', 'plus', 'new'],
     line=[PL(hex_open), L(184, 158, 184, 210), L(158, 184, 210, 184)], area=[P(hex_area)])
icon('hexagon-minus', D, ['hexagon', 'remove', 'subtract'],
     line=[PL(hex_open), L(156, 184, 212, 184)], area=[P(hex_area)])
icon('hexagon-slash', D, ['hexagon', 'off', 'disabled', 'hidden'], line=[PG(HEX), SLASH])

# ---------------------------------------------------------------- hexagonal prism
def fhex(c, rx, ry):
    return [(c[0] + rx * math.cos(math.radians(a)), c[1] + ry * math.sin(math.radians(a))) for a in range(0, 360, 60)]

T = fhex((128, 72), 88, 32)    # 0 right, 1 front-right, 2 front-left, 3 left, 4 back-left, 5 back-right
B = fhex((128, 184), 88, 32)
pr_sil = [T[3], T[4], T[5], T[0], B[0], B[1], B[2], B[3]]
pr_det = [PL([T[3], T[2], T[1], T[0]]), L(*T[2], *B[2]), L(*T[1], *B[1])]
icon('hexagonal-prism', D, ['hexagonal prism', '3d shape', 'geometry', 'solid'],
     line=[PG(pr_sil)], detail=pr_det, area=[PG(pr_sil)])
icon('hexagonal-prism-slash', D, ['hexagonal prism', 'off', 'disabled', 'hidden', 'hexagonal'],
     line=[PG(pr_sil)] + pr_det + [SLASH])

# ---------------------------------------------------------------- hexagonal pyramid
APEX = (128, 32)
PB = fhex((128, 188), 96, 30)
py_sil = [APEX, PB[0], PB[1], PB[2], PB[3]]
py_det = [L(*APEX, *PB[1]), L(*APEX, *PB[2])]
icon('hexagonal-pyramid', D, ['hexagonal pyramid', '3d shape', 'geometry', 'solid'],
     line=[PG(py_sil)], detail=py_det, area=[PG(py_sil)])
icon('hexagonal-pyramid-slash', D, ['hexagonal pyramid', 'off', 'disabled', 'hidden', 'hexagonal'],
     line=[PG(py_sil)] + py_det + [SLASH])

# ---------------------------------------------------------------- honeycomb
hr = 54
hw = math.sqrt(3) * hr / 2
ty = 87.5
cells = [(128, ty), (128 - hw, ty + 1.5 * hr), (128 + hw, ty + 1.5 * hr)]
hexes = [PG(regular_polygon(c, hr, 6)) for c in cells]
Y = [PL([(128 - hw, ty + hr / 2), (128, ty + hr), (128 + hw, ty + hr / 2)]), L(128, ty + hr, 128, ty + 2 * hr)]
icon('hexagons', D, ['hexagons', 'honeycomb', 'cells', 'pattern'], line=hexes, detail=Y, area=hexes)
icon('hexagons-slash', D, ['hexagons', 'off', 'disabled', 'hidden'], line=hexes + [SLASH])

# ---------------------------------------------------------------- icosahedron
H = HEX
tri_c = [(128, 72), polar((128, 128), 56, 150), polar((128, 128), 56, 30)]
A_, B_, C_ = tri_c
ico_det = [PG(tri_c),
           PL([H[5], A_, H[1]]), L(*A_, *H[0]),
           PL([H[5], B_, H[3]]), L(*B_, *H[4]),
           PL([H[1], C_, H[3]]), L(*C_, *H[2])]
icon('icosahedron', D, ['icosahedron', 'd20', 'polyhedron', '3d shape'],
     line=[PG(HEX)], detail=ico_det, area=[PG(HEX)])

# ---------------------------------------------------------------- reference image: picture with folded corner
pic = 'M46 48 H176 L224 96 V194 A14 14 0 0 1 210 208 H46 A14 14 0 0 1 32 194 V62 A14 14 0 0 1 46 48 Z'
icon('image-reference', D, ['reference image', 'mood board', 'picture', 'inspiration'],
     line=[P(pic)],
     detail=[PL([(176, 48), (176, 96), (224, 96)]), P('M44 188 L96 136 L144 184 L168 160 L212 204')],
     area=[P(pic)], dotcut=[C(108, 96, 16)])

# ---------------------------------------------------------------- inner shadows
icon('inner-shadow', D, ['inner shadow', 'inset', 'effect', 'depth', 'style'],
     line=[R(32, 32, 192, 192, 16), P('M224 72 H88 A16 16 0 0 0 72 88 V224')],
     area=[P('M32 48 A16 16 0 0 1 48 32 H224 V72 H88 A16 16 0 0 0 72 88 V224 H32 Z')])

CC = (128, 128)
for nm, phi in (('left', 180), ('right', 0), ('top-left', 225), ('top-right', 315),
                ('bottom-left', 135), ('bottom-right', 45)):
    u = (math.cos(math.radians(phi)), math.sin(math.radians(phi)))
    c2 = (CC[0] - 44 * u[0], CC[1] - 44 * u[1])
    p1, p2 = circle_x(CC, 96, c2, 96)
    S = (CC[0] + 96 * u[0], CC[1] + 96 * u[1])
    near = lambda m, S=S: -dist(m, S)
    inner = f'M{pt(p2)} ' + arc_to(c2, 96, p2, p1, near)
    cres = f'M{pt(p1)} ' + arc_to(CC, 96, p1, p2, near) + ' ' + arc_to(c2, 96, p2, p1, near) + ' Z'
    words = nm.replace('-', ' ')
    tags = ['inner shadow', words, 'effect', 'depth']
    icon(f'inner-shadow-{nm}', D, tags, line=[C(128, 128, 96), P(inner)], area=[P(cres)])

# ---------------------------------------------------------------- gizmo
G = (128, 148)
gx = polar(G, 96, 30); gz = polar(G, 96, 150)
icon('gizmo', D, ['3d gizmo', 'transform', 'axes', 'manipulator'],
     line=arrow(G, (128, 40), 28) + arrow(G, gx, 28) + arrow(G, gz, 28), dot=[C(*G, 20)])

# ---------------------------------------------------------------- gradient
icon('gradient', D, ['gradient', 'fade', 'color', 'blend'],
     line=[R(32, 32, 192, 192, 16), L(96, 32, 96, 224)],
     area=[P('M48 32 H96 V224 H48 A16 16 0 0 1 32 208 V48 A16 16 0 0 1 48 32 Z')],
     dot=[C(136, 72, 16), C(136, 128, 16), C(136, 184, 16), C(184, 100, 16), C(184, 156, 16)])

# ---------------------------------------------------------------- grids
SQ = R(32, 32, 192, 192, 16)
icon('grid', D, ['grid', 'guides', '3x3', 'layout'],
     line=[SQ], detail=[L(96, 32, 96, 224), L(160, 32, 160, 224), L(32, 96, 224, 96), L(32, 160, 224, 160)],
     area=[SQ])
icon('grid-4x4', I, ['4x4 grid', 'grid', 'matrix', 'tiles'],
     line=[SQ], detail=[L(v, 32, v, 224) for v in (80, 128, 176)] + [L(32, v, 224, v) for v in (80, 128, 176)],
     area=[SQ])
ts = (192 - 64) / 3
def tiles(cols, rows):
    y0 = 128 - (rows * ts + (rows - 1) * 32) / 2
    return [R(32 + i * (ts + 32), y0 + j * (ts + 32), ts, ts, 10) for j in range(rows) for i in range(cols)]
icon('grid-six', I, ['grid', '3x2', 'tiles', 'layout'], line=tiles(3, 2), area=tiles(3, 2))
icon('grid-nine', I, ['grid', '3x3', 'tiles', 'gallery', 'lattice'], line=tiles(3, 3), area=tiles(3, 3))

BRK = [P('M32 88 V48 A16 16 0 0 1 48 32 H88'), P('M168 32 H208 A16 16 0 0 1 224 48 V88'),
       P('M224 168 V208 A16 16 0 0 1 208 224 H168'), P('M88 224 H48 A16 16 0 0 1 32 208 V168')]
inner_sq = R(80, 80, 96, 96, 12)
icon('grid-scan', I, ['grid scan', 'detect', 'layout', 'frame'],
     line=BRK + [inner_sq], detail=[L(128, 80, 128, 176), L(80, 128, 176, 128)], area=[inner_sq])
icon('grid-pattern', D, ['grid pattern', 'texture', 'mesh', 'background'],
     line=[L(v, 32, v, 224) for v in (64, 128, 192)] + [L(32, v, 224, v) for v in (64, 128, 192)])
phi = (math.sqrt(5) - 1) / 2
gx1, gx2 = 32 + 192 * (1 - phi), 32 + 192 * phi
gy1, gy2 = 48 + 160 * (1 - phi), 48 + 160 * phi
GR = R(32, 48, 192, 160, 14)
icon('grid-golden-ratio', D, ['golden ratio', 'composition', 'grid', 'photography'],
     line=[GR], detail=[L(gx1, 48, gx1, 208), L(gx2, 48, gx2, 208), L(32, gy1, 224, gy1), L(32, gy2, 224, gy2)],
     area=[GR])

print(save(overwrite=True))
