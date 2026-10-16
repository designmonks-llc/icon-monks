import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Letters & Numbers'

# ======================================================================= capital letterforms
# Each glyph draws stroke centrelines in the box (x, t, w, h); 16-unit strokes, round caps/joins.


def g_B(x, t, w, h):
    b = t + h
    ht = h * 0.46
    r1, r2 = ht / 2, (h - ht) / 2
    a1 = x + w * 0.92 - r1
    a2 = x + w - r2
    ym = t + ht
    return [P(f'M{f(x)} {f(ym)} H{f(a2)} A{f(r2)} {f(r2)} 0 0 1 {f(a2)} {f(b)} H{f(x)} V{f(t)} '
              f'H{f(a1)} A{f(r1)} {f(r1)} 0 0 1 {f(a1)} {f(ym)}')]


def stadium_arc(x, t, w, h, end):
    r = w / 2
    ct, cb = (x + r, t + r), (x + r, t + h - r)
    s = polar(ct, r, -end)
    return r, ct, cb, s


def g_C(x, t, w, h, end=40):
    r, ct, cb, s = stadium_arc(x, t, w, h, end)
    e = polar(cb, r, end)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 {pt(e)}')]


def g_G(x, t, w, h, end=40):
    r, ct, cb, s = stadium_arc(x, t, w, h, end)
    yb = min(t + h * 0.56, t + h - r)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 '
              f'{f(x + w)} {f(t + h - r)} V{f(yb)} H{f(x + w * 0.56)}')]


def g_D(x, t, w, h):
    R_ = min(w * 0.62, h / 2)
    b = t + h
    return [P(f'M{f(x)} {f(t)} H{f(x + w - R_)} A{f(R_)} {f(R_)} 0 0 1 {f(x + w)} {f(t + R_)} V{f(b - R_)} '
              f'A{f(R_)} {f(R_)} 0 0 1 {f(x + w - R_)} {f(b)} H{f(x)} Z')]


def g_E(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b), (x + w, b)]), L(x, t + h / 2, x + w * 0.84, t + h / 2)]


def g_F(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b)]), L(x, t + h * 0.5, x + w * 0.84, t + h * 0.5)]


def g_H(x, t, w, h):
    return [L(x, t, x, t + h), L(x + w, t, x + w, t + h), L(x, t + h / 2, x + w, t + h / 2)]


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h), L(x, t, x + w, t), L(x, t + h, x + w, t + h)]


def g_J(x, t, w, h):
    r = w / 2
    b = t + h
    return [P(f'M{f(x + w * 0.3)} {f(t)} H{f(x + w)} V{f(b - r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(b - r)}')]


def g_K(x, t, w, h):
    b = t + h
    a0, a1 = (x + w, t), (x, t + h * 0.62)
    m = (a0[0] + (a1[0] - a0[0]) * 0.58, a0[1] + (a1[1] - a0[1]) * 0.58)
    return [L(x, t, x, b), L(*a0, *a1), L(*m, x + w, b)]


def g_L(x, t, w, h):
    return [PL([(x, t), (x, t + h), (x + w, t + h)])]


def g_M(x, t, w, h):
    b = t + h
    return [PL([(x, b), (x, t), (x + w / 2, t + h * 0.62), (x + w, t), (x + w, b)])]


def g_N(x, t, w, h):
    b = t + h
    return [PL([(x, b), (x, t), (x + w, b), (x + w, t)])]


def g_O(x, t, w, h):
    return [R(x, t, w, h, w / 2)]


def g_Q(x, t, w, h, over=6):
    return [R(x, t, w, h, w / 2), L(x + w * 0.6, t + h * 0.7, x + w + over, t + h + over)]


def bowl(x, t, w, h, k=0.56):
    r = h * k / 2
    return r, f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 2 * r)} H{f(x)}'


def g_P(x, t, w, h):
    return [P(bowl(x, t, w, h)[1])]


def g_R(x, t, w, h):
    r, d = bowl(x, t, w, h)
    return [P(d), L(x + w * 0.46, t + 2 * r, x + w, t + h)]


GLYPH = {'B': g_B, 'C': g_C, 'D': g_D, 'E': g_E, 'F': g_F, 'G': g_G, 'H': g_H, 'I': g_I, 'J': g_J,
         'K': g_K, 'L': g_L, 'M': g_M, 'N': g_N, 'O': g_O, 'P': g_P, 'Q': g_Q, 'R': g_R}
# width / height ratio of each capital
RATIO = {'B': 0.66, 'C': 0.78, 'D': 0.72, 'E': 0.6, 'F': 0.6, 'G': 0.8, 'H': 0.7, 'I': 0.44, 'J': 0.6,
         'K': 0.68, 'L': 0.58, 'M': 0.88, 'N': 0.72, 'O': 0.84, 'P': 0.64, 'Q': 0.84, 'R': 0.68}
# optical horizontal nudges (fraction of h) for letters whose weight sits on one side
NUDGE = {'L': 0.03, 'F': 0.03, 'P': 0.02, 'J': -0.02}


def glyph(ch, h, cy=128, **kw):
    w = h * RATIO[ch]
    x = 128 - w / 2 + h * NUDGE.get(ch, 0)
    return GLYPH[ch](x, cy - h / 2, w, h, **kw)


CIRCLE = C(128, 128, 96)
SQUARE = R(32, 32, 192, 192, 16)

for ch in 'BCDEFGHIJKLMNOPQR':
    n = ch.lower()
    base = f'letter {n}'
    extra = {'P': 'parking'}.get(ch, 'initial')
    kw_plain = {'over': 8} if ch == 'Q' else {}
    kw_small = {'over': 0} if ch == 'Q' else {}
    icon(f'letter-{n}', CAT, [base, n, 'alphabet', 'character'], line=glyph(ch, 176, **kw_plain))
    circle_tags = [base, n, 'circle', 'alphabet', extra]
    if ch in 'HLNR':
        circle_tags = [base, n, 'alphabet', 'circle'] + ([] if ch == 'R' else ['initial'])
    icon(f'letter-{n}-circle', CAT, circle_tags,
         line=[CIRCLE], area=[CIRCLE], detail=glyph(ch, 92, **kw_small))
    sq_tags = [base, n, 'alphabet', 'square'] if ch in 'FNOPR' else [base, n, 'square', 'alphabet']
    icon(f'letter-{n}-square', CAT, sq_tags,
         line=[SQUARE], area=[SQUARE], detail=glyph(ch, 104, **kw_small))

print(save(overwrite=True))
