import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Arrows'


def head(tip, direction, size):
    """Chevron arrowhead at tip pointing along direction (degrees), legs at 45 deg, axial depth size."""
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


def mx(p):
    return (256 - p[0], p[1])


def deg_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


def T(elems, deg=0, flip=False):
    """Rotate/flip a list of point lists; returns transformed point lists."""
    out = []
    for pts in elems:
        q = [mx(p) for p in pts] if flip else list(pts)
        out.append(rot(q, deg) if deg else q)
    return out


# ---------------------------------------------------------------- arc left / right
def arc_arrow(flip):
    c = (144, 164); r = 80
    s = polar(c, r, 30)          # start, below the right side
    e = polar(c, r, 180)         # end on the left
    if flip:
        s, e, cc = mx(s), mx(e), mx(c)
        path = f'M{pt(s)} A{r} {r} 0 1 1 {pt(e)}'
    else:
        path = f'M{pt(s)} A{r} {r} 0 1 0 {pt(e)}'
    return [P(path), PL(head(e, 90, 32))]


icon('arrow-arc-left', CAT, ['undo', 'back', 'arc'], line=arc_arrow(False))
icon('arrow-arc-right', CAT, ['redo', 'forward', 'arc'], line=arc_arrow(True))

# ---------------------------------------------------------------- autofit
FRAME_W = 'M40 120 V56 A16 16 0 0 1 56 40 H200 A16 16 0 0 1 216 56 V120'   # open frame above a width arrow


FRAME_H = 'M120 40 H56 A16 16 0 0 0 40 56 V200 A16 16 0 0 0 56 216 H120'   # open frame left of a height arrow
Y = 184; X = 184
icon('arrow-autofit-width', CAT, ['arrow autofit width', 'arrow', 'direction', 'autofit', 'width'],
     line=[P(FRAME_W), L(40, Y, 216, Y), PL(head((40, Y), 180, 32)), PL(head((216, Y), 0, 32))])
icon('arrow-autofit-left', CAT, ['arrow autofit left', 'arrow', 'direction', 'autofit', 'left'],
     line=[P(FRAME_W), L(216, Y, 40, Y), PL(head((40, Y), 180, 32))])
icon('arrow-autofit-right', CAT, ['arrow autofit right', 'arrow', 'direction', 'autofit', 'right'],
     line=[P(FRAME_W), L(40, Y, 216, Y), PL(head((216, Y), 0, 32))])
icon('arrow-autofit-content', CAT, ['arrow autofit content', 'arrow', 'direction', 'autofit', 'content'],
     line=[P(FRAME_W), L(40, Y, 108, Y), PL(head((108, Y), 0, 32)), L(216, Y, 148, Y), PL(head((148, Y), 180, 32))])
icon('arrow-autofit-height', CAT, ['arrow autofit height', 'arrow', 'direction', 'autofit', 'height'],
     line=[P(FRAME_H), L(X, 40, X, 216), PL(head((X, 40), 270, 32)), PL(head((X, 216), 90, 32))])
icon('arrow-autofit-up', CAT, ['arrow autofit', 'increase', 'upload', 'arrow', 'direction'],
     line=[P(FRAME_H), L(X, 216, X, 40), PL(head((X, 40), 270, 32))])
icon('arrow-autofit-down', CAT, ['arrow autofit', 'decrease', 'download', 'arrow', 'direction'],
     line=[P(FRAME_H), L(X, 40, X, 216), PL(head((X, 216), 90, 32))])

# ---------------------------------------------------------------- badge (chevron tag)
BADGE = [(56, 48), (136, 48), (200, 128), (136, 208), (56, 208), (120, 128)]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', 270)):
    g = rot(BADGE, deg)
    tags = {'right': ['arrow badge right', 'arrow', 'direction', 'badge', 'right'],
            'left': ['arrow badge left', 'arrow', 'direction', 'badge', 'left'],
            'up': ['arrow badge', 'increase', 'upload', 'arrow', 'direction'],
            'down': ['arrow badge', 'decrease', 'download', 'arrow', 'direction']}[nm]
    icon(f'arrow-badge-{nm}', CAT, tags, line=[PG(g)], area=[PG(g)])

# ---------------------------------------------------------------- bar both
icon('arrow-bar-both', CAT, ['expand', 'both sides', 'width'],
     line=[L(128, 56, 128, 200), L(96, 128, 40, 128), PL(head((40, 128), 180, 40)),
           L(160, 128, 216, 128), PL(head((216, 128), 0, 40))])

# ---------------------------------------------------------------- bear left / right
BEAR = [[(176, 216), (176, 144), (80, 48)], head((80, 48), 225, 40)]
icon('arrow-bear-left', CAT, ['arrow bear left', 'arrow', 'direction', 'bear', 'left'],
     line=[PL(s) for s in BEAR])
icon('arrow-bear-right', CAT, ['arrow bear right', 'arrow', 'direction', 'bear', 'right'],
     line=[PL(s) for s in T(BEAR, flip=True)])


# ---------------------------------------------------------------- bend double (reply all / forward all)
def bend_double(flip):
    tx = mx if flip else (lambda p: p)
    sweep = 0 if flip else 1
    path = f'M{pt(tx((96, 96)))} L{pt(tx((144, 96)))} A72 72 0 0 {sweep} {pt(tx((216, 168)))} L{pt(tx((216, 208)))}'
    return [P(path), PL([tx(p) for p in head((96, 96), 180, 48)]), PL([tx(p) for p in head((44, 96), 180, 48)])]


icon('arrow-bend-double-up-left', CAT, ['reply all', 'back', 'return', 'respond', 'email'], line=bend_double(False))
icon('arrow-bend-double-up-right', CAT, ['forward all', 'share', 'send'], line=bend_double(True))


# ---------------------------------------------------------------- bend (travel one way, then turn; head on the turned end)
def bend_turn(right, down):
    # canonical: right then down
    path_pts = dict(a=(40, 56), b=(88, 56), c=(168, 136), d=(168, 216))
    def tx(p):
        x, y = p
        if not right:
            x = 256 - x
        if not down:
            y = 256 - y
        return (x, y)
    sweep = 1 if right == down else 0
    a, b, c, d = (tx(path_pts[k]) for k in 'abcd')
    hd = [tx(p) for p in head((168, 216), 90, 48)]
    return [P(f'M{pt(a)} L{pt(b)} A80 80 0 0 {sweep} {pt(c)} L{pt(d)}'), PL(hd)]


for nm, right, down in (('left-down', 0, 1), ('left-up', 0, 0), ('right-down', 1, 1), ('right-up', 1, 0)):
    a, b = nm.split('-')
    icon(f'arrow-bend-{nm}', CAT, ['turn', 'bend', 'direction', 'elbow', f'{a} {b}'], line=bend_turn(right, down))

# ---------------------------------------------------------------- bounce
def bounce(pts, ctrl, size=36):
    d = f'M{pt(pts[0])}' + ''.join(f' Q{pt(c)} {pt(p)}' for c, p in zip(ctrl, pts[1:]))
    e, k = pts[-1], ctrl[-1]
    return [P(d), PL(head(e, deg_of((e[0] - k[0], e[1] - k[1])), size))]


icon('arrow-bounce', CAT, ['arrow bounce', 'arrow', 'direction', 'bounce', 'arrows'],
     line=bounce([(36, 204), (124, 204), (212, 76)], [(80, -32), (152, 84)]))

# ---------------------------------------------------------------- capsule
cap = R(64, 32, 128, 192, 64)
icon('arrow-capsule', CAT, ['arrow', 'capsule', 'scroll'],
     line=[cap], detail=[L(128, 80, 128, 172), PL(head((128, 172), 90, 32))], area=[cap])

# ---------------------------------------------------------------- circle diagonals
CARROW = [[(80, 128), (176, 128)], [(136, 88), (176, 128), (136, 168)]]
for nm, deg in (('up-right', -45), ('down-right', 45), ('down-left', 135), ('up-left', 225)):
    a, b = nm.split('-')
    icon(f'arrow-circle-{nm}', CAT, ['arrow', 'diagonal', 'circle', f'{a} {b}', 'direction'],
         line=[C(128, 128, 96)], detail=[PL(rot(s, deg)) for s in CARROW], area=[C(128, 128, 96)])

# ---------------------------------------------------------------- clockwise inside circle
cc = (128, 132); rr = 46
ce = polar(cc, rr, -45)
cw = [P(f'M{pt(polar(cc, rr, 0))} A{rr} {rr} 0 1 1 {pt(ce)}'), PL([(ce[0] - 28, ce[1]), ce, (ce[0], ce[1] - 28)])]
ce2 = mx(ce)
ccw = [P(f'M{pt(mx(polar(cc, rr, 0)))} A{rr} {rr} 0 1 0 {pt(ce2)}'), PL([(ce2[0] + 28, ce2[1]), ce2, (ce2[0], ce2[1] - 28)])]
icon('arrow-clockwise-circle', CAT, ['redo', 'forward', 'rotate'],
     line=[C(128, 128, 96)], detail=cw, area=[C(128, 128, 96)])
icon('arrow-counter-clockwise-circle', CAT, ['undo', 'back', 'rotate'],
     line=[C(128, 128, 96)], detail=ccw, area=[C(128, 128, 96)])

# ---------------------------------------------------------------- curve left / right
def curve(flip):
    tx = mx if flip else (lambda p: p)
    s, k1, k2, e = (192, 216), (192, 128), (152, 80), (64, 80)
    return [P(f'M{pt(tx(s))} C{pt(tx(k1))} {pt(tx(k2))} {pt(tx(e))}'),
            PL([tx(p) for p in head(e, 180, 40)])]


icon('arrow-curve-left', CAT, ['arrow curve left', 'arrow', 'direction', 'curve', 'left'], line=curve(False))
icon('arrow-curve-right', CAT, ['arrow curve right', 'arrow', 'direction', 'curve', 'right'], line=curve(True))

# ---------------------------------------------------------------- down family
DHEAD = head((128, 216), 90, 56)
icon('arrow-down-dashed', CAT, ['arrow down dashed', 'arrow', 'direction', 'down', 'dashed'],
     line=[L(128, 40, 128, 64), L(128, 104, 128, 128), L(128, 168, 128, 216), PL(DHEAD)])
icon('arrow-down-from-arc', CAT, ['arrow down from arc', 'arrow', 'direction', 'down', 'arc'],
     line=[P('M48 120 A80 80 0 0 1 208 120'), L(128, 88, 128, 216), PL(head((128, 216), 90, 48))])
icon('arrow-down-to-arc', CAT, ['arrow down to arc', 'arrow', 'direction', 'down', 'arc'],
     line=[P('M48 136 A80 80 0 0 0 208 136'), L(128, 40, 128, 152), PL(head((128, 152), 90, 44))])
icon('arrow-down-from-line', CAT, ['arrow down from line', 'arrow', 'direction', 'down', 'line'],
     line=[L(48, 40, 208, 40), L(128, 88, 128, 216), PL(head((128, 216), 90, 56))])
rh = [(128, 36), (168, 76), (128, 116), (88, 76)]
icon('arrow-down-rhombus', CAT, ['arrow down rhombus', 'arrow', 'direction', 'down', 'rhombus'],
     line=[PG(rh), L(128, 116, 128, 216), PL(head((128, 216), 90, 48))], area=[PG(rh)])
icon('arrow-down-tail', CAT, ['arrow down tail', 'arrow', 'direction', 'down', 'tail'],
     line=[L(128, 40, 128, 216), PL(head((128, 216), 90, 56)), PL(head((128, 88), 90, 48))])

# ---------------------------------------------------------------- elbow
icon('arrow-elbow-down', CAT, ['elbow', 'turn', 'down', '90 degrees'],
     line=[PL([(40, 60), (168, 60), (168, 216)]), PL(head((168, 216), 90, 48))])
icon('arrow-elbow-up', CAT, ['elbow', 'turn', 'up', '90 degrees'],
     line=[PL([(40, 196), (168, 196), (168, 40)]), PL(head((168, 40), 270, 48))])
icon('arrow-elbow-left', CAT, ['elbow', 'turn', 'left', '90 degrees', 'elbow arrow'],
     line=[PL([(196, 40), (196, 168), (40, 168)]), PL(head((40, 168), 180, 48))])
icon('arrow-elbow-right', CAT, ['elbow', 'turn', 'right', '90 degrees', 'elbow arrow'],
     line=[PL([(60, 40), (60, 168), (216, 168)]), PL(head((216, 168), 0, 48))])

# ---------------------------------------------------------------- fat arrows (canonical: pointing down)
FAT = [(96, 40), (160, 40), (160, 120), (216, 120), (128, 216), (40, 120), (96, 120)]
FAT_LINE = [(96, 40), (160, 40), (160, 96), (208, 96), (128, 176), (48, 96), (96, 96)]
FAT_LINES = [(96, 120), (160, 120), (160, 136), (216, 136), (128, 216), (40, 136), (96, 136)]
DIRS = (('down', 0), ('left', 90), ('up', 180), ('right', 270))
fat_tags = {'down': ['block arrow', 'down', 'bold arrow', 'arrow big', 'decrease'],
            'left': ['block arrow', 'left', 'bold arrow', 'arrow big left', 'arrow']}
line_tags = {'down': ['block arrow', 'down', 'end'], 'left': ['block arrow', 'left', 'start'],
             'right': ['block arrow', 'right', 'end'], 'up': ['block arrow', 'up', 'top']}
lines_tags = {'down': ['block arrow', 'down', 'speed', 'arrow', 'direction'],
              'left': ['block arrow', 'left', 'speed', 'arrow', 'direction'],
              'right': ['block arrow', 'right', 'speed', 'arrow', 'direction'],
              'up': ['block arrow', 'caps lock', 'shift', 'upvote', 'increase']}
for nm, deg in DIRS:
    if nm in fat_tags:
        g = rot(FAT, deg)
        icon(f'arrow-fat-{nm}', CAT, fat_tags[nm], line=[PG(g)], area=[PG(g)])
    g = rot(FAT_LINE, deg)
    ln = rot([(48, 216), (208, 216)], deg)
    icon(f'arrow-fat-line-{nm}', CAT, line_tags[nm], line=[PG(g), PL(ln)], area=[PG(g)])
    g = rot(FAT_LINES, deg)
    bars = [rot([(96, 40), (160, 40)], deg), rot([(96, 80), (160, 80)], deg)]
    icon(f'arrow-fat-lines-{nm}', CAT, lines_tags[nm], line=[PG(g)] + [PL(b) for b in bars], area=[PG(g)])

print(save(overwrite=True))
