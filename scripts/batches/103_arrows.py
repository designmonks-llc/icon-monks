import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Arrows'


def head(tip, direction, size):
    """Chevron arrowhead at tip pointing along direction (degrees, screen), legs at 45 deg, axial depth size."""
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


def arrow(a, b, size):
    """Straight arrow from a to b with a chevron head at b."""
    d = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return [PL([a, b]), PL(head(b, d, size))]


MX = lambda p: (256 - p[0], p[1])
MY = lambda p: (p[0], 256 - p[1])
MXY = lambda p: (256 - p[0], 256 - p[1])
TR = lambda p: (p[1], p[0])
ID = lambda p: p


def tp(fn, pts):
    return [fn(p) for p in pts]


# ---------------------------------------------------------------- sharp turns
# vertical stem that folds back at 45 degrees into a down-left arrow
ST = [(188, 216), (188, 40), (68, 160)]
STH = [(68, 88), (68, 160), (140, 160)]
icon('arrow-sharp-turn-left', CAT, ['arrow', 'direction', 'sharp', 'turn', 'left'],
     line=[PL(ST), PL(STH)])
icon('arrow-sharp-turn-right', CAT, ['arrow', 'direction', 'sharp', 'turn', 'right'],
     line=[PL(tp(MX, ST)), PL(tp(MX, STH))])

# ---------------------------------------------------------------- arrow in a square
SQ = R(32, 32, 192, 192, 16)
SARROW = [[(76, 128), (180, 128)], [(136, 84), (180, 128), (136, 172)]]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', 270)):
    icon(f'arrow-square-{nm}', CAT, ['arrow', nm, 'square', 'box', 'direction'],
         line=[SQ], detail=[PL(rot(s, deg)) for s in SARROW], area=[SQ])
DARROW = [[(88, 168), (168, 88)], [(104, 88), (168, 88), (168, 152)]]  # up-right
for nm, deg in (('up-right', 0), ('down-right', 90), ('down-left', 180), ('up-left', 270)):
    icon(f'arrow-square-{nm}', CAT, ['arrow', 'diagonal', 'square', nm.replace('-', ' '), 'direction'],
         line=[SQ], detail=[PL(rot(s, deg)) for s in DARROW], area=[SQ])

# arrow-square-out with a slash; the arrow shaft starts past the slash so they never touch
aso = load('arrow-square-out')
icon('arrow-square-out-slash', CAT, ['arrow square out', 'disabled', 'off', 'arrow', 'direction'],
     line=[aso['line'][0], L(152, 104, 216, 40), aso['line'][2], L(40, 40, 216, 216)])

# ---------------------------------------------------------------- U-turns (geometry of arrow-u-up-left)
def uturn(fn):
    a, b, c, d = tp(fn, [(40, 88), (160, 88), (160, 192), (88, 192)])
    # sweep flips when the transform is a reflection
    det = (fn((1, 0))[0] - fn((0, 0))[0]) * (fn((0, 1))[1] - fn((0, 0))[1]) - \
          (fn((1, 0))[1] - fn((0, 0))[1]) * (fn((0, 1))[0] - fn((0, 0))[0])
    sweep = 1 if det > 0 else 0
    return [P(f'M{pt(a)} L{pt(b)} A52 52 0 0 {sweep} {pt(c)} L{pt(d)}'),
            PL(tp(fn, [(96, 32), (40, 88), (96, 144)]))]


def comp(*fns):
    def g(p):
        for fn in fns:
            p = fn(p)
        return p
    return g


UT = [('down-left', MY, ['u-turn', 'return', 'back', 'turn around', 'u turn']),
      ('down-right', MXY, ['u-turn', 'return', 'forward', 'u turn', 'turn back']),
      ('left-up', TR, ['u-turn', 'return', 'back', 'undo', 'curve']),
      ('left-down', comp(TR, MY), ['u-turn', 'return', 'back']),
      ('right-up', comp(TR, MX), ['u-turn', 'return', 'forward']),
      ('right-down', comp(TR, MXY), ['u-turn', 'return', 'forward'])]
for nm, fn, tags in UT:
    icon(f'arrow-u-{nm}', CAT, tags, line=uturn(fn))

# reply-all style: two nested chevrons on one U-turn
UD_PATH = [(92, 96), (156, 96), (156, 200), (104, 200)]
UD_H1 = [(80, 56), (40, 96), (80, 136)]
UD_H2 = [(132, 56), (92, 96), (132, 136)]


def udouble(fn, sweep):
    a, b, c, d = tp(fn, UD_PATH)
    return [P(f'M{pt(a)} L{pt(b)} A52 52 0 0 {sweep} {pt(c)} L{pt(d)}'), PL(tp(fn, UD_H1)), PL(tp(fn, UD_H2))]


icon('arrow-u-up-left-double', CAT, ['undo all', 'reply all', 'back'], line=udouble(ID, 1))
icon('arrow-u-up-right-double', CAT, ['redo all', 'forward all', 'arrows'], line=udouble(MX, 0))

# ---------------------------------------------------------------- arrow up family
UPH = [(72, 96), (128, 40), (184, 96)]
icon('arrow-up-dashed', CAT, ['arrow up dashed', 'arrow', 'direction', 'up', 'dashed'],
     line=[L(128, 40, 128, 104), L(128, 144, 128, 160), L(128, 200, 128, 216), PL(UPH)])

# from-arc: a bowl at the bottom, the arrow rises from its centre
icon('arrow-up-from-arc', CAT, ['arrow up from arc', 'arrow', 'direction', 'up', 'arc'],
     line=[P('M40 160 A120 120 0 0 0 216 160'), L(128, 168, 128, 40), PL(UPH)])
# to-arc: a dome at the top, the arrow points up into it
icon('arrow-up-to-arc', CAT, ['arrow up to arc', 'arrow', 'direction', 'up', 'arc'],
     line=[P('M40 88 A120 120 0 0 1 216 88'), L(128, 216, 128, 104), PL([(80, 152), (128, 104), (176, 152)])])
icon('arrow-up-from-line', CAT, ['raise', 'lift', 'upload', 'arrow up from line', 'arrow'],
     line=[L(40, 216, 216, 216), L(128, 176, 128, 40), PL(UPH)])

RH = PG([(128, 144), (164, 180), (128, 216), (92, 180)])
icon('arrow-up-rhombus', CAT, ['arrow up rhombus', 'arrow', 'direction', 'up', 'rhombus'],
     line=[L(128, 40, 128, 144), PL(UPH), RH], area=[RH])
icon('arrow-up-tail', CAT, ['arrow up tail', 'arrow', 'direction', 'up', 'tail'],
     line=[L(128, 40, 128, 216), PL(UPH), PL([(88, 216), (128, 176), (168, 216)])])

# ---------------------------------------------------------------- wave arrows with a badge
# wave pointing left: straight lead from the tip, then an S-wave with flat crests
WAVE = 'M40 80 H72 C92 80 92 56 112 56 C138 56 138 104 164 104 C190 104 190 56 216 56'
WAVE_H = head((40, 80), 180, 36)
B_DOWN = [L(184, 156, 184, 216), PL([(154, 186), (184, 216), (214, 186)])]
B_UP = [L(184, 216, 184, 156), PL([(154, 186), (184, 156), (214, 186)])]


def mx_path(d):
    import re
    nums = re.split(r'([A-Za-z])', d)
    out = []
    cmd = ''
    for tok in nums:
        tok = tok.strip()
        if not tok:
            continue
        if tok.isalpha():
            cmd = tok
            out.append(cmd)
            continue
        vals = [float(v) for v in tok.split()]
        if cmd == 'H':
            vals = [256 - v for v in vals]
        elif cmd in 'MLC':
            vals = [256 - v if i % 2 == 0 else v for i, v in enumerate(vals)]
        out.append(' '.join(f(v) for v in vals))
    return ''.join(o if o.isalpha() else o + ' ' for o in out).replace(' ', ' ').strip()


WAVE_R = mx_path(WAVE)
for nm, w, h in (('left', WAVE, WAVE_H), ('right', WAVE_R, tp(MX, WAVE_H))):
    for dn, badge, tags in (('down', B_DOWN, ['decrease', 'download']), ('up', B_UP, ['increase', 'upload'])):
        icon(f'arrow-wave-{nm}-{dn}', CAT, [f'arrow wave {nm}'] + tags + ['arrow', 'direction'],
             line=[P(w), PL(h)] + badge)

# ---------------------------------------------------------------- zig-zag
icon('arrow-zig-zag', CAT, ['arrow zig zag', 'arrow', 'direction', 'zig', 'zag'],
     line=[PL([(40, 176), (96, 120), (144, 168), (216, 96)]), PL([(160, 96), (216, 96), (216, 152)])])

# ---------------------------------------------------------------- circular arrows
def two_arcs(c0, r0, size, ccw=False):
    s1, e1 = polar(c0, r0, 195), polar(c0, r0, 315)
    s2, e2 = polar(c0, r0, 15), polar(c0, r0, 135)
    out = [P(f'M{pt(s1)} A{f(r0)} {f(r0)} 0 0 1 {pt(e1)}'), PL(head(e1, 315 + 90, size)),
           P(f'M{pt(s2)} A{f(r0)} {f(r0)} 0 0 1 {pt(e2)}'), PL(head(e2, 135 + 90, size))]
    return out


# arrows-clockwise geometry (r=80, same arcs) with a slightly smaller head so the legs stay inside 24..232
acw = two_arcs((128, 128), 80, 26)
icon('arrows-clockwise-dot', CAT, ['sync', 'refresh', 'status'], line=acw, dot=[C(128, 128, 16)])


def mirror_el(el):
    """Mirror a <path> made of M/L/A commands left-right (flip arc sweep)."""
    import re
    d = re.search(r'd="([^"]+)"', el).group(1)
    toks = re.findall(r'[MLA]|-?[\d.]+', d)
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t in 'ML':
            out.append(f'{t}{f(256 - float(toks[i + 1]))} {toks[i + 2]}'); i += 3
        elif t == 'A':
            rx, ry, xr, la, sw, x, y = toks[i + 1:i + 8]
            out.append(f'A{rx} {ry} {xr} {la} {1 - int(sw)} {f(256 - float(x))} {y}'); i += 8
        else:  # implicit L continuation
            out.append(f'L{f(256 - float(toks[i]))} {toks[i + 1]}'); i += 2
    return P(' '.join(out))


icon('arrows-counter-clockwise', CAT, ['sync', 'refresh', 'reverse'], line=[mirror_el(e) for e in acw])
icon('arrows-clockwise-circle', CAT, ['refresh', 'sync', 'reload'],
     line=[C(128, 128, 96)], detail=two_arcs((128, 128), 46, 20), area=[C(128, 128, 96)])

# ---------------------------------------------------------------- double-headed / crossing
icon('arrows-cross', CAT, ['crossing', 'swap', 'intersect'],
     line=[L(40, 216, 216, 40), PL([(152, 40), (216, 40), (216, 104)]),
      L(40, 40, 216, 216), PL([(152, 216), (216, 216), (216, 152)])])
icon('arrows-diagonal', CAT, ['resize', 'diagonal', 'double arrow', 'scale'],
     line=[L(48, 208, 208, 48), PL([(144, 48), (208, 48), (208, 112)]), PL([(48, 144), (48, 208), (112, 208)])])
icon('arrows-horizontal', CAT, ['resize', 'horizontal', 'width', 'double arrow'],
     line=[L(40, 128, 216, 128), PL([(84, 84), (40, 128), (84, 172)]), PL([(172, 84), (216, 128), (172, 172)])])
icon('arrows-diff', CAT, ['diff', 'compare', 'versions'],
     line=[L(40, 80, 184, 80), PL(head((184, 80), 0, 36)), L(216, 176, 72, 176), PL(head((72, 176), 180, 36))])

# two opposite diagonal arrows side by side (arrows-left-right turned 45 deg, shortened)
LR2 = [[(52, 92), (204, 92)], head((204, 92), 0, 36), [(204, 164), (52, 164)], head((52, 164), 180, 36)]
LR2m = [tp(MX, s) for s in LR2]
for nm, src, deg in (('ne-sw', LR2, -45), ('sw-ne', LR2m, -45), ('se-nw', LR2, 45), ('nw-se', LR2m, 45)):
    icon(f'arrows-double-{nm}', CAT, ['arrows', 'direction', 'double'] + nm.split('-'),
         line=[PL(rot(s, deg)) for s in src])

# arrows-left-right compressed into the upper left, with a down-arrow badge
icon('arrows-down', CAT, ['arrows', 'decrease', 'download', 'direction'],
     line=[L(40, 64, 216, 64), PL(head((216, 64), 0, 32)), L(136, 136, 40, 136), PL(head((40, 136), 180, 32))]
     + B_DOWN)

# ---------------------------------------------------------------- inward arrows
inc = []
for deg in (0, 90, 180, 270):
    inc += [PL(rot(s, deg)) for s in ([(128, 32), (128, 88)], head((128, 88), 90, 28))]
icon('arrows-in-cardinal', CAT, ['collapse', 'compress', 'center'], line=inc)

IH = [L(40, 64, 40, 192), L(216, 64, 216, 192)] + arrow((40, 128), (108, 128), 32) + arrow((216, 128), (148, 128), 32)
icon('arrows-in-horizontal', CAT, ['shrink', 'collapse horizontal', 'narrow', 'compress'], line=IH)
icon('arrows-in-vertical', CAT, ['shrink', 'collapse vertical', 'compress', 'height'],
     line=[L(64, 40, 192, 40), L(64, 216, 192, 216)] + arrow((128, 40), (128, 108), 32) + arrow((128, 216), (128, 148), 32))
icon('arrows-in-line-horizontal', CAT, ['compress', 'collapse', 'horizontal', 'merge', 'contract'],
     line=[L(128, 40, 128, 216)] + arrow((32, 128), (92, 128), 32) + arrow((224, 128), (164, 128), 32))
icon('arrows-in-line-vertical', CAT, ['compress', 'collapse', 'vertical', 'merge', 'contract'],
     line=[L(40, 128, 216, 128)] + arrow((128, 32), (128, 92), 32) + arrow((128, 224), (128, 164), 32))
icon('arrows-in-simple', CAT, ['collapse', 'minimize', 'shrink'],
     line=[L(216, 40, 144, 112), PL([(144, 64), (144, 112), (192, 112)]),
           L(40, 216, 112, 144), PL([(112, 192), (112, 144), (64, 144)])])

# ---------------------------------------------------------------- merge / join
MERGE = [P('M40 64 C88 64 88 128 136 128'), P('M40 192 C88 192 88 128 136 128'),
         L(136, 128, 216, 128), PL(head((216, 128), 0, 40))]
icon('arrows-merge', CAT, ['merge', 'combine', 'join', 'arrows', 'converge'], line=MERGE)
MV = [P('M64 216 C64 168 128 168 128 120'), P('M192 216 C192 168 128 168 128 120'),
      L(128, 120, 128, 40), PL(head((128, 40), 270, 40))]
icon('arrows-merge-vertical', CAT, ['merge', 'converge', 'join'], line=MV)
icon('arrows-join', CAT, ['arrows join', 'arrows', 'direction', 'join'],
     line=[PL([(40, 64), (72, 64), (128, 128)]), PL([(40, 192), (72, 192), (128, 128)]),
           L(128, 128, 216, 128), PL(head((216, 128), 0, 40))])
icon('arrows-left', CAT, ['arrows left', 'arrows', 'direction', 'left'],
     line=[L(216, 80, 40, 80), PL(head((40, 80), 180, 36)), L(216, 176, 40, 176), PL(head((40, 176), 180, 36))])

print(save(overwrite=True))
