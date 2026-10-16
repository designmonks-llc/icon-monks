import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Arrows'
CARET = [(96, 48), (176, 128), (96, 208)]   # same as 00_core caret-right
CIRC_CHEV = [(88, 112), (128, 152), (168, 112)]  # caret-circle-down's chevron


def head(tip, direction, size):
    """Chevron arrowhead at tip pointing along direction (deg), legs at 45 deg, axial depth size."""
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


def scale(points, k, c=(128, 128)):
    return [(c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k) for x, y in points]


def shift(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def arrow(a, b, size):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return [L(a[0], a[1], b[0], b[1]), PL(head(b, ang, size))]


# ---- badges (lower right, around x=184)
BADGE_UP = arrow((184, 216), (184, 144), 28)
BADGE_DOWN = arrow((184, 144), (184, 216), 28)
BADGE_UPDOWN = [L(184, 136, 184, 216), PL(head((184, 136), 270, 22)), PL(head((184, 216), 90, 22))]

# ---- move: double-headed arrows split by a centre dot
mv = arrow((88, 128), (32, 128), 36) + arrow((168, 128), (224, 128), 36)
icon('arrows-move-horizontal', CAT, ['arrows move horizontal', 'arrows', 'direction', 'move', 'horizontal'],
     line=mv, dot=[C(128, 128, 16)])
icon('arrows-move-vertical', CAT, ['arrows move vertical', 'arrows', 'direction', 'move', 'vertical'],
     line=arrow((128, 88), (128, 32), 36) + arrow((128, 168), (128, 224), 36), dot=[C(128, 128, 16)])

# ---- out from a line
ol = [L(128, 48, 128, 208)] + arrow((92, 128), (32, 128), 36) + arrow((164, 128), (224, 128), 36)
icon('arrows-out-line-horizontal', CAT, ['expand', 'width', 'horizontal', 'arrows', 'split'], line=ol)
icon('arrows-out-line-vertical', CAT, ['expand', 'vertical', 'spread', 'split', 'height'],
     line=[L(48, 128, 208, 128)] + arrow((128, 92), (128, 32), 36) + arrow((128, 164), (128, 224), 36))

# ---- out simple: two diagonal arrows
icon('arrows-out-simple', CAT, ['expand', 'maximize', 'fullscreen'],
     line=[L(144, 112, 216, 40), PL([(156, 40), (216, 40), (216, 100)]),
           L(112, 144, 40, 216), PL([(100, 216), (40, 216), (40, 156)])])

# ---- two parallel arrows
def two_right(y1, y2, size=32):
    return arrow((40, y1), (216, y1), size) + arrow((40, y2), (216, y2), size)

icon('arrows-right', CAT, ['arrows right', 'arrows', 'direction', 'right'], line=two_right(80, 176))

u = (-1 / math.sqrt(2), -1 / math.sqrt(2)); n = (1 / math.sqrt(2), -1 / math.sqrt(2))
ul = []
for s in (1, -1):
    c = (128 + n[0] * 52 * s, 128 + n[1] * 52 * s)
    a = (c[0] - u[0] * 56, c[1] - u[1] * 56); b = (c[0] + u[0] * 64, c[1] + u[1] * 64)
    ul += [L(a[0], a[1], b[0], b[1]), PL(head(b, 225, 26))]
icon('arrows-up-left', CAT, ['arrows up left', 'arrows', 'direction', 'up', 'left'], line=ul)

# ---- split
sp = [PL([(40, 128), (120, 128)]), P('M120 128 L200 48'), PL([(148, 48), (200, 48), (200, 100)]),
      P('M120 128 L200 208'), PL([(148, 208), (200, 208), (200, 156)])]
def sp_pts(deg):
    segs = [[(40, 128), (120, 128)], [(120, 128), (200, 48)], [(148, 48), (200, 48), (200, 100)],
            [(120, 128), (200, 208)], [(148, 208), (200, 208), (200, 156)]]
    return [PL(shift(rot(s, deg), 0, 0)) for s in segs]
icon('arrows-split', CAT, ['split', 'diverge', 'fork', 'alternate route', 'branch'],
     line=[PL(shift(s, 8, 0)) for s in [[(40, 128), (120, 128)], [(120, 128), (200, 48)], [(148, 48), (200, 48), (200, 100)],
                                          [(120, 128), (200, 208)], [(148, 208), (200, 208), (200, 156)]]])
icon('arrows-split-vertical', CAT, ['split', 'diverge', 'fork'],
     line=[PL(shift(rot(s, -90), 0, -8)) for s in [[(40, 128), (120, 128)], [(120, 128), (200, 48)], [(148, 48), (200, 48), (200, 100)],
                                                      [(120, 128), (200, 208)], [(148, 208), (200, 208), (200, 156)]]])

# ---- badge variants
TRANSFER = arrow((40, 72), (216, 72), 36) + arrow((120, 144), (40, 144), 36)
TRANSFER_HI = arrow((40, 64), (216, 64), 36) + arrow((120, 136), (40, 136), 36)
icon('arrows-transfer-down', CAT, ['arrows transfer', 'decrease', 'download', 'arrows', 'direction'],
     line=TRANSFER + BADGE_DOWN)
icon('arrows-transfer-up', CAT, ['arrows transfer', 'increase', 'upload', 'arrows', 'direction'],
     line=TRANSFER + BADGE_UP)
icon('arrows-transfer-up-down', CAT, ['arrows transfer up', 'decrease', 'download', 'arrows', 'direction'],
     line=TRANSFER_HI + BADGE_UPDOWN)
ARROWS2 = arrow((40, 72), (216, 72), 32) + arrow((40, 144), (120, 144), 32)
icon('arrows-up', CAT, ['arrows', 'increase', 'upload', 'direction'], line=ARROWS2 + BADGE_UP)

icon('arrows-vertical', CAT, ['resize', 'vertical', 'height', 'double arrow'],
     line=[L(128, 40, 128, 216), PL(head((128, 40), 270, 44)), PL(head((128, 216), 90, 44))])

# ---- caret + bar
icon('caret-bar-contract', CAT, ['collapse', 'chevrons', 'bar', 'inward'],
     line=[L(40, 128, 216, 128), PL([(72, 40), (128, 96), (184, 40)]), PL([(72, 216), (128, 160), (184, 216)])])
icon('caret-bar-expand', CAT, ['expand', 'chevrons', 'bar', 'outward'],
     line=[L(40, 128, 216, 128), PL([(72, 96), (128, 40), (184, 96)]), PL([(72, 160), (128, 216), (184, 160)])])

# ---- caret circles
def ccircle(detail):
    return dict(line=[C(128, 128, 96)], detail=detail, area=[C(128, 128, 96)])

DCH = [[(82, 88), (122, 128), (82, 168)], [(134, 88), (174, 128), (134, 168)]]
for nm, deg, tags in (('right', 0, ['forward', 'last', 'next', 'double', 'circle']),
                      ('down', 90, ['expand all', 'scroll down', 'more', 'double', 'circle']),
                      ('left', 180, ['rewind', 'first', 'back', 'double', 'circle']),
                      ('up', 270, ['collapse all', 'scroll up', 'top', 'double', 'circle'])):
    icon(f'caret-circle-double-{nm}', CAT, tags, **ccircle([PL(rot(s, deg)) for s in DCH]))
for nm, deg, tags in (('left', 90, ['caret', 'chevron', 'left', 'circle', 'previous']),
                      ('right', 270, ['caret', 'chevron', 'right', 'circle', 'next']),
                      ('up', 180, ['caret', 'chevron', 'up', 'circle', 'collapse'])):
    icon(f'caret-circle-{nm}', CAT, tags, **ccircle([PL(rot(CIRC_CHEV, deg))]))
icon('caret-circle-up-down', CAT, ['sort', 'select', 'dropdown'],
     **ccircle([PL([(92, 108), (128, 72), (164, 108)]), PL([(92, 148), (128, 184), (164, 148)])]))

icon('caret-contract', CAT, ['collapse', 'chevrons', 'contract', 'inward'],
     line=[PL([(72, 48), (128, 104), (184, 48)]), PL([(72, 208), (128, 152), (184, 208)])])
icon('caret-left-right', CAT, ['caret left right', 'caret', 'chevron', 'left', 'right'],
     line=[PL(rot([(72, 96), (128, 40), (184, 96)], 90)), PL(rot([(72, 160), (128, 216), (184, 160)], 90))])

# ---- diagonal carets: right-angle corners, centred on the grid
def corner_pts(cx, cy, leg):
    return [(cx - leg, cy), (cx, cy), (cx, cy + leg)]   # opens down-left, points up-right

DIAG = {'up-right': 0, 'down-right': 90, 'down-left': 180, 'up-left': 270}
SINGLE = corner_pts(180, 76, 104)
DLEG, DOFF = 88, 44
DOUBLE = [corner_pts(128 + (DLEG + DOFF) / 2, 128 - (DLEG + DOFF) / 2, DLEG),
          corner_pts(128 + (DLEG + DOFF) / 2 - DOFF, 128 - (DLEG + DOFF) / 2 + DOFF, DLEG)]
for nm, deg in DIAG.items():
    words = nm.replace('-', ' ')
    icon(f'caret-double-{nm}', CAT, ['caret', 'chevron', 'double', nm.split('-')[0], nm.split('-')[1]],
         line=[PL(rot(s, deg)) for s in DOUBLE])
    icon(f'caret-{nm}', CAT, ['diagonal', 'chevron', words, 'corner', f'caret {words}'],
         line=[PL(rot(SINGLE, deg))])

# ---- caret to a line
CL = [[(48, 60), (128, 140), (208, 60)], [(40, 196), (216, 196)]]
for nm, deg, tags in (('down', 0, ['chevron', 'bar', 'down', 'end', 'bottom']),
                      ('left', 90, ['chevron', 'bar', 'left', 'start', 'first']),
                      ('up', 180, ['chevron', 'bar', 'up', 'top', 'first']),
                      ('right', 270, ['chevron', 'bar', 'right', 'end', 'last'])):
    icon(f'caret-line-{nm}', CAT, tags, line=[PL(rot(s, deg)) for s in CL])

# ---- caret squares
SQ = R(32, 32, 192, 192, 16)
for nm, deg, tags in (('down', 0, ['chevron', 'square', 'down', 'dropdown', 'caret down']),
                      ('left', 90, ['chevron', 'square', 'left', 'back', 'previous']),
                      ('up', 180, ['chevron', 'square', 'up', 'collapse', 'caret up']),
                      ('right', 270, ['chevron', 'square', 'right', 'next', 'forward'])):
    icon(f'caret-square-{nm}', CAT, tags, line=[SQ], detail=[PL(rot(CIRC_CHEV, deg))], area=[SQ])

# ---- corner arrows with a double head. Canonical: travels down, then turns left.
def corner_double(tf):
    path = [(208, 40), (208, 128)]
    arc_end = (168, 168)
    tip = (48, 168)
    t = lambda p: tf(p)
    a, b, e = t(path[0]), t(path[1]), t(arc_end)
    # sweep: canonical (down then left) turns clockwise on screen; mirrored transforms flip it
    cross = (b[0] - a[0]) * (e[1] - b[1]) - (b[1] - a[1]) * (e[0] - b[0])
    sweep = 1 if cross > 0 else 0
    d = f'M{pt(a)} L{pt(b)} A40 40 0 0 {sweep} {pt(e)} L{pt(t(tip))}'
    h1 = [(84, 132), (48, 168), (84, 204)]
    h2 = [(136, 132), (100, 168), (136, 204)]
    return [P(d), PL([t(p) for p in h1]), PL([t(p) for p in h2])]

TF = {
    'down-left': lambda p: (p[0], p[1]),
    'down-right': lambda p: (256 - p[0], p[1]),
    'left-down': lambda p: (256 - p[1], 256 - p[0]),
    'left-up': lambda p: (256 - p[1], p[0]),
    'right-down': lambda p: (p[1], 256 - p[0]),
    'right-up': lambda p: (p[1], p[0]),
}
for nm in ('down-left', 'down-right', 'left-down', 'left-up', 'right-down', 'right-up'):
    a, b = nm.split('-')
    icon(f'corner-{nm}-double', CAT, ['corner', 'arrow', 'turn', a, b], line=corner_double(TF[nm]))

# ---- direction
tri = lambda deg: PG(rot([(128, 62), (146, 84), (110, 84)], deg))
icon('direction-arrows', CAT, ['d-pad', 'arrows', 'directions', 'navigate'],
     **ccircle([tri(d) for d in (0, 90, 180, 270)]))
LT = [(32, 128), (100, 68), (100, 188)]
RT = [(256 - x, y) for x, y in LT]
icon('direction-horizontal', CAT, ['left right', 'direction', 'arrows'],
     line=[PG(LT), PG(RT)], area=[PG(LT), PG(RT)])

# ---- rotate 360: elliptical arrow
rx, ry = 96, 64
ep = lambda deg: (128 + rx * math.cos(math.radians(deg)), 128 + ry * math.sin(math.radians(deg)))
s0, e0 = ep(115), ep(65)
tan = (-rx * math.sin(math.radians(65)), ry * math.cos(math.radians(65)))  # direction of increasing angle
ang = math.degrees(math.atan2(tan[1], tan[0]))
icon('rotate-360', CAT, ['360', 'panorama', 'rotate', 'view'],
     line=[P(f'M{pt(s0)} A{rx} {ry} 0 1 1 {pt(e0)}'), PL(head(e0, ang, 32))])

# ---- stairs down: stairs geometry plus a down-left arrow above the steps
st = load('stairs')
k = (-6 / math.sqrt(61), 5 / math.sqrt(61))  # down the slope
a0 = (104, 40)
b0 = (40, 93.3)
icon('stairs-down', CAT, ['downstairs', 'stairs', 'descend', 'down'],
     line=st['line'] + arrow(a0, b0, 24), area=st['area'])

print(save(overwrite=True))
