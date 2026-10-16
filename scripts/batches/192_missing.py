import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

# Three missing icons: currency-afghani, currency-riyal (bare pure-line glyphs like batch 110)
# and envelope-at (the envelope with an @ inside; see the note above it).

# ================================================================ currency glyphs (batch 110: line only, glyph ~40..216)
CM = 'Commerce'

# ---- afghani ؋: a waw-like head loop with a long tail sweeping down to the left, plus the small mark below
glyph_afn = [
    P('M164 134 H134 A30 30 0 1 1 164 104 V168 A40 40 0 0 1 124 208 H56'),
    L(108, 164, 116, 184),
]
dots_afn = [C(134, 44, 16)]
icon('currency-afghani', CM, ['currency afghani', 'currency', 'money', 'afghani', 'afghanistan', 'afn'],
     line=glyph_afn, dot=dots_afn)

# ---- riyal: simplified mark after the Saudi riyal symbol, two stems crossed by rising bars
glyph_sar = [
    P('M100 40 V176 A24 24 0 0 1 76 200'),
    L(156, 56, 156, 176),
    L(48, 132, 208, 100),
    L(48, 172, 208, 140),
    L(148, 216, 208, 204),
]
icon('currency-riyal', CM, ['currency riyal', 'currency', 'money', 'riyal', 'saudi arabia', 'qatar', 'yemen',
                            'oman', 'iran', 'sar'],
     line=glyph_sar)

# ================================================================ envelope-at
def at_sign(c, r_out, r_in, end=50):
    """@ : inner ring, stem on its right, hook into the outer ring that wraps round counter-clockwise."""
    x, y = c
    sx = x + r_in
    hr = (r_out - r_in) / 2
    hc = (sx + hr, y + 4)
    ring = C(x, y, r_in)
    tail = (f'M{f(sx)} {f(y - r_in)} V{f(hc[1])} A{f(hr)} {f(hr)} 0 0 0 {f(x + r_out)} {f(hc[1])} '
            f'V{f(y)} A{f(r_out)} {f(r_out)} 0 1 0 {pt(polar(c, r_out, end))}')
    return ring, P(tail)


# Badge layout (@ at 184,184) was tried: at that size the @'s inner ring closes up in bold and turns to mush at
# 24px, so the @ sits inside the envelope instead (no flap, which would cross it). The sign is a detail so it
# is knocked out of the filled envelope in the fill weight.
ENV_D = load('envelope')['line'][0]
at_ring, at_tail = at_sign((128, 128), 48, 18, end=55)
icon('envelope-at', 'Communication', ['email', 'address', 'mail', 'at', 'envelope', 'email address'],
     line=[ENV_D], area=[ENV_D], detail=[at_ring, at_tail])

print(save())
