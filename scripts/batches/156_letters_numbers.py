import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Letters & Numbers'

# Glyphs are designed at full size (cap height 48..208, centred on 128) and scaled
# uniformly about the centre for the circle / square versions, so curves stay true.


class G:
    def __init__(self, s=1.0, cx=128, cy=128):
        self.s, self.cx, self.cy = s, cx, cy

    def p(self, x, y):
        return (self.cx + (x - 128) * self.s, self.cy + (y - 128) * self.s)

    def P(self, x, y):
        return pt(self.p(x, y))

    def r(self, v):
        return f(v * self.s)

    def line(self, pts):
        return PL([self.p(*q) for q in pts])

    def poly(self, pts):
        return PG([self.p(*q) for q in pts])


def ept(c, rx, ry, deg):
    a = math.radians(deg)
    return (c[0] + rx * math.cos(a), c[1] + ry * math.sin(a))


def earc(g, c, rx, ry, a0, a1):
    """Elliptical arc from angle a0 to a1 (degrees, screen angles; a1 > a0 means clockwise)."""
    q = ept(c, rx, ry, a1)
    span = a1 - a0
    sweep = 1 if span > 0 else 0
    large = 1 if abs(span) > 180 else 0
    return f'A{g.r(rx)} {g.r(ry)} 0 {large} {sweep} {g.P(*q)}'


def tangent_pt(p, c, r, side):
    """Tangent point on circle (c, r) seen from p; side=+1/-1 picks one of the two."""
    dx, dy = c[0] - p[0], c[1] - p[1]
    d = math.hypot(dx, dy)
    base = math.atan2(-dy, -dx)
    off = math.acos(r / d)
    a = base + side * off
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


# ---------------------------------------------------------------- glyphs
def g_S(g):
    ct, cb, rx, ry = (128, 88), (128, 168), 54, 40
    a = ept(ct, rx, ry, -30)
    b = ept(cb, rx, ry, 150)
    return [P(f'M{g.P(*a)} ' + earc(g, ct, rx, ry, -30, -270) + ' ' + earc(g, cb, rx, ry, -90, 150))]


def g_T(g):
    return [g.line([(64, 48), (192, 48)]), g.line([(128, 48), (128, 208)])]


def g_U(g):
    return [P(f'M{g.P(72, 48)} L{g.P(72, 152)} A{g.r(56)} {g.r(56)} 0 0 0 {g.P(184, 152)} L{g.P(184, 48)}')]


def g_V(g):
    return [g.line([(68, 48), (128, 208), (188, 48)])]


def g_W(g):
    return [g.line([(52, 48), (88, 208), (128, 104), (168, 208), (204, 48)])]


def g_X(g):
    return [g.line([(72, 48), (184, 208)]), g.line([(184, 48), (72, 208)])]


def g_Y(g):
    return [g.line([(68, 48), (128, 132), (188, 48)]), g.line([(128, 132), (128, 208)])]


def g_Z(g):
    return [g.line([(72, 48), (184, 48), (72, 208), (184, 208)])]


def g_0(g):
    x0, x1 = 78, 178
    r = 50
    return [P(f'M{g.P(x0, 98)} A{g.r(r)} {g.r(r)} 0 0 1 {g.P(x1, 98)} L{g.P(x1, 158)} '
              f'A{g.r(r)} {g.r(r)} 0 0 1 {g.P(x0, 158)} Z')]


def g_1(g):
    return [g.line([(88, 82), (136, 48), (136, 208)]), g.line([(92, 208), (180, 208)])]


def g_2(g):
    c, r = (128, 92), 44
    start = 200
    end_pt = (80, 208)
    t = max(tangent_pt(end_pt, c, r, +1), tangent_pt(end_pt, c, r, -1))
    ta = math.degrees(math.atan2(t[1] - c[1], t[0] - c[0])) % 360
    a = ept(c, r, r, start)
    return [P(f'M{g.P(*a)} ' + earc(g, c, r, r, start - 360, ta) + f' L{g.P(*end_pt)} L{g.P(180, 208)}')]


def g_3(g):
    # mirrors letter-b's bowls (batch 155): straight runs into semicircles
    x, t, b = 80, 48, 208
    r1, r2 = 36, 44
    ym = t + 2 * r1
    a1, a2 = 176 - 8 - r1, 176 - r2
    return [P(f'M{g.P(x, t)} H{f(g.p(a1, 0)[0])} A{g.r(r1)} {g.r(r1)} 0 0 1 {g.P(a1, ym)} H{f(g.p(108, 0)[0])}'),
            P(f'M{g.P(108, ym)} H{f(g.p(a2, 0)[0])} A{g.r(r2)} {g.r(r2)} 0 0 1 {g.P(a2, b)} H{f(g.p(x, 0)[0])}')]


def g_4(g):
    return [g.line([(156, 208), (156, 48), (72, 160), (188, 160)])]


def g_5(g):
    c, r = (126, 160), 48
    a = ept(c, r, r, 222)
    return [P(f'M{g.P(176, 48)} L{g.P(96, 48)} L{g.P(*a)} ' + earc(g, c, r, r, 222, 360 + 145))]


def g_6(g):
    c, r = (128, 162), 46
    top = (156, 48)
    t = tangent_pt(top, c, r, +1)
    if t[0] > c[0]:
        t = tangent_pt(top, c, r, -1)
    return [g.line([top, t]), C(*g.p(*c), float(g.r(r)))]


def g_7(g):
    return [g.line([(72, 48), (184, 48), (112, 208)])]


def g_8(g):
    return [E(*g.p(128, 86), float(g.r(42)), float(g.r(38))), E(*g.p(128, 166), float(g.r(48)), float(g.r(42)))]


GLYPHS = {
    's': g_S, 't': g_T, 'u': g_U, 'v': g_V, 'w': g_W, 'x': g_X, 'y': g_Y, 'z': g_Z,
    '0': g_0, '1': g_1, '2': g_2, '3': g_3, '4': g_4, '5': g_5, '6': g_6, '7': g_7, '8': g_8,
}

S_BARE, S_CIRC, S_SQ = 176 / 160, 92 / 160, 104 / 160
CIRC = C(128, 128, 96)
SQ = R(32, 32, 192, 192, 16)

SPECS = [
    ('letter-s', 's', ['letter s', 's', 'alphabet', 'character']),
    ('letter-s-circle', 's', ['letter s', 's', 'circle', 'alphabet', 'initial']),
    ('letter-s-square', 's', ['letter s', 's', 'square', 'alphabet']),
    ('letter-t', 't', ['letter t', 't', 'alphabet', 'character']),
    ('letter-t-circle', 't', ['letter t', 't', 'circle', 'alphabet', 'initial']),
    ('letter-t-square', 't', ['letter t', 't', 'square', 'alphabet']),
    ('letter-u', 'u', ['letter u', 'u', 'alphabet', 'character']),
    ('letter-u-circle', 'u', ['letter u', 'u', 'circle', 'alphabet', 'initial']),
    ('letter-u-square', 'u', ['letter u', 'u', 'square', 'alphabet']),
    ('letter-v', 'v', ['letter v', 'v', 'alphabet', 'character']),
    ('letter-v-circle', 'v', ['letter v', 'v', 'alphabet', 'circle', 'initial']),
    ('letter-v-square', 'v', ['letter v', 'v', 'square', 'alphabet']),
    ('letter-w', 'w', ['letter w', 'w', 'alphabet', 'character']),
    ('letter-w-circle', 'w', ['letter w', 'w', 'circle', 'alphabet', 'initial']),
    ('letter-w-square', 'w', ['letter w', 'w', 'square', 'alphabet']),
    ('letter-x', 'x', ['letter x', 'x', 'alphabet', 'character']),
    ('letter-x-circle', 'x', ['letter x', 'x', 'circle', 'alphabet', 'initial']),
    ('letter-x-square', 'x', ['letter x', 'x', 'square', 'alphabet']),
    ('letter-y', 'y', ['letter y', 'y', 'alphabet', 'character']),
    ('letter-y-circle', 'y', ['y', 'letter', 'circle', 'alphabet', 'letter y']),
    ('letter-y-square', 'y', ['letter y', 'y', 'alphabet', 'square']),
    ('letter-z', 'z', ['letter z', 'z', 'alphabet', 'character']),
    ('letter-z-circle', 'z', ['letter z', 'z', 'circle', 'alphabet', 'initial']),
    ('letter-z-square', 'z', ['letter z', 'z', 'alphabet', 'square']),
    ('number-0', '0', ['zero', '0', 'digit', 'number 0', 'numeral']),
    ('number-0-circle', '0', ['number 0', 'zero', 'digit', 'circle', '0']),
    ('number-0-square', '0', ['number 0', 'zero', 'digit', 'square', '0']),
    ('number-1', '1', ['one', '1', 'digit', 'number', 'numeral']),
    ('number-1-circle', '1', ['number 1', 'one', 'digit', 'circle', '1']),
    ('number-1-square', '1', ['number 1', 'one', 'digit', 'square', '1']),
    ('number-2', '2', ['two', '2', 'digit', 'number', 'numeral']),
    ('number-2-circle', '2', ['number 2', 'two', 'digit', 'circle', '2']),
    ('number-2-square', '2', ['number 2', 'two', 'digit', 'square', '2']),
    ('number-3', '3', ['three', '3', 'digit', 'number', 'numeral']),
    ('number-3-circle', '3', ['number 3', 'three', 'digit', 'circle', '3']),
    ('number-3-square', '3', ['number 3', 'three', 'digit', 'square', '3']),
    ('number-4', '4', ['four', '4', 'digit', 'number', 'numeral']),
    ('number-4-circle', '4', ['number 4', 'four', 'digit', 'circle', '4']),
    ('number-4-square', '4', ['number 4', 'four', 'digit', 'square', '4']),
    ('number-5', '5', ['five', '5', 'digit', 'number', 'numeral']),
    ('number-5-circle', '5', ['number 5', 'five', 'digit', 'circle', '5']),
    ('number-5-square', '5', ['number 5', 'five', 'digit', 'square', '5']),
    ('number-6', '6', ['six', '6', 'digit', 'number', 'numeral']),
    ('number-6-circle', '6', ['number 6', 'six', 'digit', 'circle', '6']),
    ('number-6-square', '6', ['number 6', 'six', 'digit', 'square', '6']),
    ('number-7', '7', ['seven', '7', 'digit', 'number 7', 'numeral']),
    ('number-7-circle', '7', ['number 7', 'seven', 'digit', 'circle', '7']),
    ('number-7-square', '7', ['number 7', 'seven', 'digit', 'square', '7']),
    ('number-8', '8', ['eight', '8', 'digit', 'number 8', 'numeral']),
    ('number-8-circle', '8', ['number 8', 'eight', 'digit', 'circle', '8']),
    ('number-8-square', '8', ['number 8', 'eight', 'digit', 'square', '8']),
]

for name, ch, tags in SPECS:
    fn = GLYPHS[ch]
    if name.endswith('-circle'):
        icon(name, CAT, tags, line=[CIRC], area=[CIRC], detail=fn(G(S_CIRC)))
    elif name.endswith('-square'):
        icon(name, CAT, tags, line=[SQ], area=[SQ], detail=fn(G(S_SQ)))
    else:
        icon(name, CAT, tags, line=fn(G(S_BARE)))

print(save(overwrite=True))
