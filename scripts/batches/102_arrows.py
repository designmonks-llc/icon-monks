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


def my(p):
    return (p[0], 256 - p[1])


def r1(p, deg):
    return rot([p], deg)[0]


def deg_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


# Shape spec: list of ('pl', pts) | ('pg', pts) | ('arc', p0, r, large, sweep, p1, [extra pts...]) | ('path', [cmds])
# transformed by rotation / mirroring so whole families share one geometry.
def tf(spec, deg=0, flip=False, vflip=False):
    def t(p):
        if flip:
            p = mx(p)
        if vflip:
            p = my(p)
        return r1(p, deg) if deg else p
    mirror = flip ^ vflip
    out = []
    for s in spec:
        kind = s[0]
        if kind == 'pl':
            out.append(PL([t(p) for p in s[1]]))
        elif kind == 'pg':
            out.append(PG([t(p) for p in s[1]]))
        elif kind == 'path':
            # list of (cmd, args) with cmd in M L A C Q; A args = (r, large, sweep, p)
            d = []
            for cmd, *args in s[1]:
                if cmd in 'ML':
                    d.append(f'{cmd}{pt(t(args[0]))}')
                elif cmd == 'A':
                    rr, large, sweep, p = args
                    d.append(f'A{f(rr)} {f(rr)} 0 {large} {sweep ^ mirror} {pt(t(p))}')
                elif cmd == 'C':
                    d.append('C' + ' '.join(pt(t(p)) for p in args))
                elif cmd == 'Q':
                    d.append('Q' + ' '.join(pt(t(p)) for p in args))
                elif cmd == 'Z':
                    d.append('Z')
            out.append(P(' '.join(d)))
    return out


def seg(a, b):
    return ('pl', [a, b])


# ---------------------------------------------------------------- fat arrows (same polygon as arrow-fat-down / left)
FAT = [(96, 40), (160, 40), (160, 120), (216, 120), (128, 216), (40, 120), (96, 120)]
g = rot(FAT, 270)
icon('arrow-fat-right', CAT, ['block arrow', 'right', 'bold arrow', 'arrow big right', 'arrow'], line=[PG(g)], area=[PG(g)])
g = rot(FAT, 180)
icon('arrow-fat-up', CAT, ['block arrow', 'shift', 'bold arrow', 'upvote', 'up'], line=[PG(g)], area=[PG(g)])

# ---------------------------------------------------------------- fork
FORK = [seg((128, 216), (128, 144)), ('pl', [(128, 144), (52, 68)]), ('pl', [(128, 144), (204, 68)]),
        ('pl', head((52, 68), 225, 34)), ('pl', head((204, 68), 315, 34))]
icon('arrow-fork', CAT, ['arrow fork', 'arrow', 'direction', 'fork', 'arrows'], line=tf(FORK))

FORK3 = [seg((128, 216), (128, 40)), ('pl', head((128, 40), 270, 30)),
         ('pl', [(128, 184), (56, 112)]), ('pl', head((56, 112), 225, 26)),
         ('pl', [(128, 184), (200, 112)]), ('pl', head((200, 112), 315, 26))]
icon('arrow-fork-triple', CAT, ['arrow fork triple', 'arrow', 'direction', 'fork', 'triple'], line=tf(FORK3))

# ---------------------------------------------------------------- guide: dashed start, solid curve, head up
GUIDE = [seg((40, 200), (48, 200)), seg((88, 200), (96, 200)),
         ('path', [('M', (136, 200)), ('L', (144, 200)), ('A', 40, 0, 0, (184, 160)), ('L', (184, 48))]),
         ('pl', head((184, 44), 270, 40))]
icon('arrow-guide', CAT, ['guide', 'route', 'path'], line=tf(GUIDE))

# ---------------------------------------------------------------- iteration: 270 deg loop, then forward
ic, ir = (104, 116), 56
IT = [('path', [('M', (ic[0] - ir, ic[1])), ('A', ir, 1, 1, (ic[0], ic[1] + ir)), ('L', (216, ic[1] + ir))]),
      ('pl', head((216, ic[1] + ir), 0, 36))]
icon('arrow-iteration', CAT, ['iteration', 'loop', 'cycle'], line=tf(IT))

# ---------------------------------------------------------------- left / right families (rotations of the down family)
DOWN = {
    'dashed': [seg((128, 40), (128, 56)), seg((128, 96), (128, 112)), seg((128, 152), (128, 216)),
               ('pl', head((128, 216), 90, 56))],
    'from-arc': [('path', [('M', (48, 120)), ('A', 80, 0, 1, (208, 120))]), seg((128, 88), (128, 216)),
                 ('pl', head((128, 216), 90, 48))],
    'to-arc': [('path', [('M', (48, 136)), ('A', 80, 0, 0, (208, 136))]), seg((128, 40), (128, 168)),
               ('pl', head((128, 168), 90, 48))],
    'from-line': [seg((48, 40), (208, 40)), seg((128, 88), (128, 216)), ('pl', head((128, 216), 90, 56))],
    'rhombus': [('pg', [(128, 40), (164, 76), (128, 112), (92, 76)]), seg((128, 112), (128, 216)),
                ('pl', head((128, 216), 90, 48))],
    'tail': [seg((128, 40), (128, 216)), ('pl', head((128, 216), 90, 56)), ('pl', head((128, 88), 90, 48))],
}
RH = [(128, 40), (164, 76), (128, 112), (92, 76)]
for side, deg in (('left', 90), ('right', -90)):
    for key, spec in DOWN.items():
        nm = f'arrow-{side}-{key}'
        word = key.split('-')[-1]
        tags = [f'arrow {side} {key.replace("-", " ")}', 'arrow', 'direction', side, word]
        area = [PG(rot(RH, deg))] if key == 'rhombus' else []
        icon(nm, CAT, tags, line=tf(spec, deg), area=area)

# ---------------------------------------------------------------- arrow-line (to a bar) family, base = arrow-line-up
LINE_UP = [seg((40, 40), (216, 40)), seg((128, 216), (128, 88)), ('pl', [(72, 144), (128, 88), (184, 144)])]
LINE_UP_DASHED = [seg((40, 40), (216, 40)), seg((128, 88), (128, 112)), seg((128, 152), (128, 168)),
                  seg((128, 208), (128, 216)), ('pl', [(72, 144), (128, 88), (184, 144)])]
icon('arrow-line-left', CAT, ['arrow', 'left', 'start', 'line', 'skip'], line=tf(LINE_UP, -90))
icon('arrow-line-right', CAT, ['arrow', 'right', 'end', 'line', 'skip'], line=tf(LINE_UP, 90))
for nm, deg in (('up', 0), ('down', 180), ('left', -90), ('right', 90)):
    icon(f'arrow-line-{nm}-dashed', CAT, ['arrow', 'direction', 'line', nm, 'dashed'], line=tf(LINE_UP_DASHED, deg))

# diagonal: arrow to a corner bracket (canonical up-left)
CORNER = [('pl', [(40, 128), (40, 40), (128, 40)]), seg((204, 204), (88, 88)), ('pl', head((88, 88), 225, 32))]
diag_tags = {'up-left': ['diagonal', 'corner', 'direction', 'insert', 'top left'],
             'up-right': ['diagonal', 'corner', 'direction'], 'down-right': ['diagonal', 'corner', 'direction'],
             'down-left': ['diagonal', 'corner', 'direction']}
for nm, deg in (('up-left', 0), ('up-right', 90), ('down-right', 180), ('down-left', 270)):
    icon(f'arrow-line-{nm}', CAT, diag_tags[nm], line=tf(CORNER, deg))

# ---------------------------------------------------------------- loop: up, loop over, cross, exit (canonical right)
lc, lr = (88, 100), 48
LOOP = [('path', [('M', (lc[0] + lr, 216)), ('L', (lc[0] + lr, lc[1])), ('A', lr, 1, 0, (lc[0], lc[1] + lr)),
                  ('L', (216, lc[1] + lr))]),
        ('pl', head((216, lc[1] + lr), 0, 36))]
icon('arrow-loop-right', CAT, ['arrow loop right', 'arrow', 'direction', 'loop', 'right'], line=tf(LOOP))
icon('arrow-loop-left', CAT, ['arrow loop left', 'arrow', 'direction', 'loop', 'left'], line=tf(LOOP, flip=True))

# ---------------------------------------------------------------- merge (canonical: branch from the left)
BR = ('path', [('M', (56, 216)), ('L', (56, 200)), ('C', (56, 160), (128, 160), (128, 112))])
MERGE = [seg((128, 216), (128, 40)), ('pl', head((128, 40), 270, 40)), BR]
icon('arrow-merge-left', CAT, ['arrow merge left', 'arrow', 'direction', 'merge', 'left'], line=tf(MERGE))
icon('arrow-merge-right', CAT, ['arrow merge right', 'arrow', 'direction', 'merge', 'right'], line=tf(MERGE, flip=True))
MERGE2 = [seg((128, 112), (128, 40)), ('pl', head((128, 40), 270, 40)), BR]
icon('arrow-merge-both', CAT, ['arrow merge both', 'arrow', 'direction', 'merge', 'both'],
     line=tf(MERGE2) + tf([BR], flip=True))

# ---------------------------------------------------------------- move (four-way move + direction badge)
mc, ma, mh = (108, 108), 72, 22
MOVE = [seg((mc[0], mc[1] - ma), (mc[0], mc[1] + ma)), seg((mc[0] - ma, mc[1]), (mc[0] + ma, mc[1]))]
for t, d in (((mc[0], mc[1] - ma), 270), ((mc[0], mc[1] + ma), 90), ((mc[0] - ma, mc[1]), 180), ((mc[0] + ma, mc[1]), 0)):
    MOVE.append(('pl', head(t, d, mh)))
bc = (188, 188)
BADGE = {'down': [seg((bc[0], 144), (bc[0], 224)), ('pl', head((bc[0], 224), 90, 28))],
         'up': [seg((bc[0], 224), (bc[0], 144)), ('pl', head((bc[0], 144), 270, 28))],
         'right': [seg((144, bc[1]), (224, bc[1])), ('pl', head((224, bc[1]), 0, 28))],
         'left': [seg((224, bc[1]), (144, bc[1])), ('pl', head((144, bc[1]), 180, 28))]}
move_tags = {'down': ['arrow move', 'decrease', 'download', 'arrow', 'direction'],
             'up': ['arrow move', 'increase', 'upload', 'arrow', 'direction'],
             'left': ['arrow move left', 'arrow', 'direction', 'move', 'left'],
             'right': ['arrow move right', 'arrow', 'direction', 'move', 'right']}
for nm in ('down', 'left', 'right', 'up'):
    icon(f'arrow-move-{nm}', CAT, move_tags[nm], line=tf(MOVE) + tf(BADGE[nm]))

# ---------------------------------------------------------------- ramp (canonical right): main road up, ramp exits right
RAMP = [seg((72, 216), (72, 40)), ('pl', head((72, 40), 270, 32)),
        ('path', [('M', (72, 216)), ('A', 112, 0, 1, (184, 104)), ('L', (216, 104))]),
        ('pl', head((216, 104), 0, 32))]
icon('arrow-ramp-right', CAT, ['arrow ramp right', 'arrow', 'direction', 'ramp', 'right'], line=tf(RAMP))
icon('arrow-ramp-left', CAT, ['arrow ramp left', 'arrow', 'direction', 'ramp', 'left'], line=tf(RAMP, flip=True))

# ---------------------------------------------------------------- rotary / roundabout
rr = 40


def rotary(c, exit_deg, tip, hs=30):
    """Island ring, entry from below, exit arrow leaving the ring at exit_deg."""
    return c, [seg((c[0], c[1] + rr), (c[0], 216)), seg(polar(c, rr, exit_deg), tip),
                                 ('pl', head(tip, exit_deg, hs))]


ROTARY = {'right': rotary((96, 104), 0, (216, 104))}
for side, flip in (('right', False), ('left', True)):
    c, spec = ROTARY['right']
    cx = 256 - c[0] if flip else c[0]
    icon(f'arrow-rotary-{side}', CAT, [f'arrow rotary {side}', 'arrow', 'direction', 'rotary', side],
         line=[C(cx, c[1], rr)] + tf(spec, flip=flip))


# first / last: the exit road leaves along the bottom (first exit) or the top (last exit) of the island
def rotary_tangent(c, y_exit):
    return c, [seg((c[0], c[1] + rr), (c[0], 216)), seg((c[0], y_exit), (216, y_exit)),
               ('pl', head((216, y_exit), 0, 30))]


ROTT = {'first': rotary_tangent((100, 100), 140), 'last': rotary_tangent((100, 136), 96)}
for key, (c, spec) in ROTT.items():
    for side, flip in (('right', False), ('left', True)):
        cx = 256 - c[0] if flip else c[0]
        icon(f'arrow-rotary-{key}-{side}', CAT, ['arrow', 'direction', 'rotary', key, side],
             line=[C(cx, c[1], rr)] + tf(spec, flip=flip))
c = (128, 136)
icon('arrow-rotary-straight', CAT, ['arrow rotary straight', 'arrow', 'direction', 'rotary', 'straight'],
     line=[C(c[0], c[1], rr)] + tf([seg((128, 176), (128, 216)), seg((128, 96), (128, 40)),
                                    ('pl', head((128, 40), 270, 28))]))
# roundabout: full turn back the way you came (u-turn round the island)
uc, ur = (128, 112), 56
UL, UR = (uc[0] - 32, 216), (uc[0] + 32, 216)
# entry on the right lane going up, round the top, exit down on the left
yr = uc[1] + math.sqrt(ur * ur - 32 * 32)
ROUND = [('path', [('M', UR), ('L', (UR[0], yr)), ('A', ur, 1, 0, (UL[0], yr)), ('L', UL)]),
         ('pl', head(UL, 90, 30))]
icon('arrow-roundabout-left', CAT, ['arrow roundabout left', 'arrow', 'direction', 'roundabout', 'left'], line=tf(ROUND))
icon('arrow-roundabout-right', CAT, ['arrow roundabout right', 'arrow', 'direction', 'roundabout', 'right'],
     line=tf(ROUND, flip=True))

# ---------------------------------------------------------------- s-turn (canonical right)
ST = [('path', [('M', (40, 176)), ('L', (80, 176)), ('C', (128, 176), (128, 80), (176, 80)), ('L', (216, 80))]),
      ('pl', head((216, 80), 0, 40))]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', -90)):
    icon(f'arrow-s-turn-{nm}', CAT, ['s turn', 'curve', 'road', nm], line=tf(ST, deg))

print(save(overwrite=True))
