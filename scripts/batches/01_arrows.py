import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Arrows'
ARROW = [[(40, 128), (216, 128)], [(144, 56), (216, 128), (144, 200)]]   # same as 00_core
CARET = [(96, 48), (176, 128), (96, 208)]                                # same as 00_core


def mxp(pts):
    return [(256 - x, y) for x, y in pts]


def myp(pts):
    return [(x, 256 - y) for x, y in pts]


def head(tip, direction, size):
    """Chevron arrowhead at tip pointing along direction (degrees), legs at 45 deg, axial depth size."""
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


# ---- diagonal arrows: arrow-right rotated 45 deg (same shaft length and head legs)
for nm, deg in (('up-right', -45), ('down-right', 45), ('down-left', 135), ('up-left', 225)):
    s = [rot(seg, deg) for seg in ARROW]
    # rotated arrow is 176 long; pull it in slightly so the diagonal reads the same size as arrow-right
    icon(f'arrow-{nm}', CAT, ['direction', 'diagonal', nm.replace('-', ' '), 'pointer'],
         line=[PL(seg) for seg in s])

# ---- circle arrows: r=96 circle, smaller arrow as detail
CARROW = [[(80, 128), (176, 128)], [(136, 88), (176, 128), (136, 168)]]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', 270)):
    icon(f'arrow-circle-{nm}', CAT, ['direction', nm, 'circle', 'button'],
         line=[C(128, 128, 96)], detail=[PL(rot(s, deg)) for s in CARROW], area=[C(128, 128, 96)])

# ---- bent arrows (turn): head offset 56
def bend(fx, fy):
    pts_head = [(96, 40), (40, 96), (96, 152)]
    tip = (40, 96)
    # path: tip -> right -> quarter turn down -> bottom
    def tx(p):
        x, y = p
        return ((256 - x) if fx else x, (256 - y) if fy else y)
    a = tx(tip); b = tx((136, 96)); c = tx((216, 176)); d = tx((216, 216))
    sweep = 1 if (fx == fy) else 0
    path = f'M{pt(a)} L{pt(b)} A80 80 0 0 {sweep} {pt(c)} L{pt(d)}'
    return [P(path), PL([tx(p) for p in pts_head])]

for nm, fx, fy in (('up-left', 0, 0), ('up-right', 1, 0), ('down-left', 0, 1), ('down-right', 1, 1)):
    icon(f'arrow-bend-{nm}', CAT, ['turn', 'direction', 'bend', nm.split('-')[1]], line=bend(fx, fy))

# ---- U-turn arrows
def uturn(fx):
    tx = (lambda p: (256 - p[0], p[1])) if fx else (lambda p: p)
    sweep = 0 if fx else 1
    path = f'M{pt(tx((40, 88)))} L{pt(tx((160, 88)))} A52 52 0 0 {sweep} {pt(tx((160, 192)))} L{pt(tx((88, 192)))}'
    return [P(path), PL([tx(p) for p in [(96, 32), (40, 88), (96, 144)]])]

icon('arrow-u-up-left', CAT, ['undo', 'back', 'u-turn', 'return'], line=uturn(0))
icon('arrow-u-up-right', CAT, ['redo', 'forward', 'u-turn', 'return'], line=uturn(1))

# ---- double arrows
LR = [L(40, 88, 216, 88), PL([(176, 48), (216, 88), (176, 128)]),
      L(216, 168, 40, 168), PL([(80, 128), (40, 168), (80, 208)])]
icon('arrows-left-right', CAT, ['swap', 'exchange', 'transfer', 'horizontal'], line=LR)
DU = [L(88, 216, 88, 40), PL([(48, 80), (88, 40), (128, 80)]),
      L(168, 40, 168, 216), PL([(128, 176), (168, 216), (208, 176)])]
icon('arrows-down-up', CAT, ['sort', 'swap', 'exchange', 'vertical'], line=DU)

c0 = (128, 128); r0 = 80
s1, e1 = polar(c0, r0, 195), polar(c0, r0, 315)
s2, e2 = polar(c0, r0, 15), polar(c0, r0, 135)
icon('arrows-clockwise', CAT, ['sync', 'refresh', 'reload', 'update'],
     line=[P(f'M{pt(s1)} A{r0} {r0} 0 0 1 {pt(e1)}'), PL(head(e1, 315 + 90, 31.1)),
           P(f'M{pt(s2)} A{r0} {r0} 0 0 1 {pt(e2)}'), PL(head(e2, 135 + 90, 31.1))])

# ---- expand / collapse
card = [L(128, 40, 128, 216), L(40, 128, 216, 128)]
for t, d in (((128, 40), 270), ((128, 216), 90), ((40, 128), 180), ((216, 128), 0)):
    card.append(PL(head(t, d, 32)))
icon('arrows-out-cardinal', CAT, ['move', 'drag', 'pan', 'directions'], line=card)

aout, ain = [], []
for deg in (0, 90, 180, 270):
    aout += [PL(rot(p, deg)) for p in ([(100, 100), (44, 44)], [(44, 96), (44, 44), (96, 44)])]
    ain += [PL(rot(p, deg)) for p in ([(40, 40), (96, 96)], [(96, 52), (96, 96), (52, 96)])]
icon('arrows-out', CAT, ['expand', 'fullscreen', 'enlarge', 'maximize'], line=aout)
icon('arrows-in', CAT, ['collapse', 'shrink', 'minimize', 'reduce'], line=ain)
icon('corners-in', CAT, ['collapse', 'minimize', 'exit fullscreen', 'shrink'],
     line=[PL([(96, 40), (96, 96), (40, 96)]), PL([(160, 40), (160, 96), (216, 96)]),
           PL([(216, 160), (160, 160), (160, 216)]), PL([(96, 216), (96, 160), (40, 160)])])

# ---- box + arrow
box = 'M104 56 H56 A16 16 0 0 0 40 72 V200 A16 16 0 0 0 56 216 H184 A16 16 0 0 0 200 200 V152'
icon('arrow-square-out', CAT, ['external link', 'open', 'new window', 'launch'],
     line=[P(box), L(120, 136, 216, 40), PL([(152, 40), (216, 40), (216, 104)])])
icon('arrow-square-in', CAT, ['import', 'insert', 'embed', 'into'],
     line=[P(box), L(216, 40, 120, 136), PL([(120, 88), (120, 136), (168, 136)])])

door_r = 'M144 40 H200 A16 16 0 0 1 216 56 V200 A16 16 0 0 1 200 216 H144'
door_l = 'M112 40 H56 A16 16 0 0 0 40 56 V200 A16 16 0 0 0 56 216 H112'
icon('sign-in', CAT, ['login', 'enter', 'log in', 'account'],
     line=[P(door_r), L(40, 128, 168, 128), PL([(128, 88), (168, 128), (128, 168)])])
icon('sign-out', CAT, ['logout', 'exit', 'log out', 'leave'],
     line=[P(door_l), L(96, 128, 216, 128), PL([(176, 88), (216, 128), (176, 168)])])

# ---- carets
DC = [[(64, 64), (128, 128), (64, 192)], [(128, 64), (192, 128), (128, 192)]]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', 270)):
    icon(f'caret-double-{nm}', CAT, ['chevrons', 'direction', nm, 'skip'],
         line=[PL(rot([(x + 4, y) for x, y in s], deg)) for s in DC])
icon('caret-up-down', CAT, ['sort', 'select', 'dropdown', 'chevrons'],
     line=[PL([(72, 96), (128, 40), (184, 96)]), PL([(72, 160), (128, 216), (184, 160)])])
icon('caret-circle-down', CAT, ['chevron', 'dropdown', 'expand', 'down'],
     line=[C(128, 128, 96)], detail=[PL([(88, 112), (128, 152), (168, 112)])], area=[C(128, 128, 96)])

# ---- media-style
icon('shuffle', CAT, ['random', 'mix', 'music', 'playlist'],
     line=[P('M40 72 H72 C120 72 136 184 184 184 H216'), P('M40 184 H72 C120 184 136 72 184 72 H216'),
           PL(head((216, 72), 0, 32)), PL(head((216, 184), 0, 32))])
rep = [P('M40 136 V104 A40 40 0 0 1 80 64 H216'), PL(head((216, 64), 0, 32)),
       P('M216 120 V152 A40 40 0 0 1 176 192 H40'), PL(head((40, 192), 180, 32))]
icon('repeat', CAT, ['loop', 'replay', 'cycle', 'music'], line=rep)
icon('repeat-once', CAT, ['loop once', 'replay', 'repeat one', 'music'],
     line=rep + [PL([(116, 116), (132, 104), (132, 152)])])

icon('trend-down', CAT, ['chart', 'decline', 'decrease', 'loss'],
     line=[PL([(32, 64), (96, 128), (136, 88), (216, 168)]), PL([(160, 168), (216, 168), (216, 112)])])

icon('arrow-line-up', CAT, ['top', 'scroll up', 'upload', 'first'],
     line=[L(40, 40, 216, 40), L(128, 216, 128, 88), PL([(72, 144), (128, 88), (184, 144)])])
icon('arrow-line-down', CAT, ['bottom', 'scroll down', 'download', 'last'],
     line=[L(40, 216, 216, 216), L(128, 40, 128, 168), PL([(72, 112), (128, 168), (184, 112)])])

# ---- navigation
nav = [(48, 116), (208, 48), (140, 208), (120, 136)]
icon('navigation-arrow', CAT, ['navigation', 'location', 'gps', 'direction'], line=[PG(nav)], area=[PG(nav)])

u = (1 / math.sqrt(2), -1 / math.sqrt(2)); n = (1 / math.sqrt(2), 1 / math.sqrt(2))
needle = [(128 + u[0] * 64, 128 + u[1] * 64), (128 + n[0] * 26, 128 + n[1] * 26),
          (128 - u[0] * 64, 128 - u[1] * 64), (128 - n[0] * 26, 128 - n[1] * 26)]
icon('compass', CAT, ['navigation', 'direction', 'explore', 'north'],
     line=[C(128, 128, 96)], detail=[PG(needle)], area=[C(128, 128, 96)])
icon('crosshair', CAT, ['aim', 'target', 'focus', 'precision'],
     line=[C(128, 128, 80), L(128, 32, 128, 80), L(128, 176, 128, 224), L(32, 128, 80, 128), L(176, 128, 224, 128)])
icon('target', CAT, ['goal', 'aim', 'bullseye', 'focus'],
     line=[C(128, 128, 96)], detail=[C(128, 128, 56)], area=[C(128, 128, 96)], dotcut=[C(128, 128, 16)])
icon('export', CAT, ['share', 'send', 'upload', 'out'],
     line=[P('M96 112 H72 A16 16 0 0 0 56 128 V200 A16 16 0 0 0 72 216 H184 A16 16 0 0 0 200 200 V128 A16 16 0 0 0 184 112 H160'),
           L(128, 152, 128, 40), PL([(88, 80), (128, 40), (168, 80)])])

print(save(overwrite=True))
