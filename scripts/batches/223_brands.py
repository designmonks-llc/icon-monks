"""Brand logos: airlines, hotels and travel."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
fix_d = __import__('198_extremes').fix_d

B = 'Brands'
RING = C(128, 128, 96)


def tags(*t):
    return list(t) + ['logo', 'brand']


# ---------------------------------------------------------------- tail symbols in a disc
# Lufthansa: the flying crane in its ring; neck, body and wing in one stroke, feathers and tail below.
icon('lufthansa-logo', B, tags('lufthansa', 'airline', 'crane', 'bird', 'travel'),
     area=[RING], line=[RING],
     detail=[P('M56 100 L80 104 C96 116 108 136 120 156 C132 128 144 108 164 100 H200'),
             L(156, 128, 192, 124), L(120, 156, 168, 168)])

# Turkish Airlines: the crescent-winged bird cut out of the red disc.
icon('turkish-airlines-logo', B, tags('turkish airlines', 'airline', 'bird', 'turkey', 'travel'),
     area=[RING], line=[RING],
     detail=[P('M84 44 C116 64 128 100 144 140 C112 120 92 84 84 44 Z'), L(52, 184, 204, 140)])

# Air Canada: the maple leaf inside a ring that opens at the bottom for the stem.
_half = [(0, 0), (10, 20), (22, 14), (18, 44), (40, 24), (46, 36), (64, 32), (56, 56), (64, 62), (32, 84), (34, 96), (4, 92)]
_s = 1.0
_leaf = [(128 + x * _s, 60 + y * _s) for x, y in _half] + [(128 - x * _s, 60 + y * _s) for x, y in reversed(_half[1:])]
_leaf = [(round(x), round(y)) for x, y in _leaf]
icon('air-canada-logo', B, tags('air canada', 'airline', 'maple leaf', 'canada', 'travel'),
     area=[PG(_leaf)], line=[PG(_leaf), P('M100 220 A96 96 0 1 1 156 220'), L(128, 152, 128, 224)])

# ---------------------------------------------------------------- tail fins and shapes
# Delta: the widget, a triangle split down the middle with the chevron cut across its base.
icon('delta-logo', B, tags('delta', 'delta air lines', 'airline', 'widget', 'triangle', 'travel'),
     area=[PG([(128, 40), (224, 204), (32, 204)])], line=[PG([(128, 40), (224, 204), (32, 204)])],
     detail=[PL([(72, 180), (128, 152), (184, 180)])])

# Cathay Pacific: the brushwing, a single brush stroke bent into a wing.
CX = 'M52 32 C60 100 100 144 212 156 L64 224 L128 184 C84 152 56 104 52 32 Z'
icon('cathay-pacific-logo', B, tags('cathay pacific', 'airline', 'brushwing', 'hong kong', 'travel'),
     area=[P(CX)], line=[P(CX)])

# American Airlines: the flight symbol, a blue blade above the red-and-silver tail with its folded top.
AA1 = 'M44 36 H88 L144 104 H100 Z'
AA2 = 'M116 156 C108 140 116 132 128 132 H172 C184 132 192 140 188 148 L224 212 H172 Z'
icon('american-airlines-logo', B, tags('american airlines', 'airline', 'flight symbol', 'eagle', 'travel'),
     area=[P(AA1), P(AA2)], line=[P(AA1), P(AA2)],
     detail=[P('M128 164 C144 152 164 148 188 148')])

# Singapore Airlines: the bird, three chevron wing bands over the swept tail and head.
icon('singapore-airlines-logo', B, tags('singapore airlines', 'airline', 'bird', 'singapore', 'travel'),
     line=[PL([(100, 36), (164, 128), (128, 192)]), PL([(72, 68), (132, 152), (104, 196)]),
           PL([(44, 100), (100, 176), (80, 216)]),
           P('M80 216 H148 C168 216 180 172 204 168 H224')])

# Ryanair: the winged harp; figure and wing frame the strings.
icon('ryanair-logo', B, tags('ryanair', 'airline', 'harp', 'ireland', 'travel'),
     line=[P('M60 72 C104 88 164 76 208 40'), P('M68 84 C68 132 112 180 180 220'),
           L(108, 100, 108, 136), L(140, 96, 140, 172), L(172, 88, 172, 196)])

# Southwest: the heart with its diagonal colour bands.
HEART = ('M128 216 C96 192 40 160 40 104 C40 76 60 56 88 56 C104 56 120 64 128 80 '
         'C136 64 152 56 168 56 C196 56 216 76 216 104 C216 160 160 192 128 216 Z')
icon('southwest-logo', B, tags('southwest', 'southwest airlines', 'airline', 'heart', 'travel'),
     area=[P(HEART)], line=[P(HEART)],
     detail=[L(56, 120, 148, 196), L(108, 80, 200, 152)])

# KLM: the crown, a cross over four balls on a bar.
icon('klm-logo', B, tags('klm', 'royal dutch airlines', 'airline', 'crown', 'travel'),
     line=[L(128, 56, 128, 104), L(108, 76, 148, 76), L(48, 188, 208, 188)],
     dot=[C(56, 140, 16), C(104, 140, 16), C(152, 140, 16), C(200, 140, 16)])

# ---------------------------------------------------------------- travel apps
# Hopper: the leaping bunny, an arched body with its ears up at the front.
HOP = 'M40 192 C64 136 108 104 156 104 C188 104 208 124 220 152 C196 140 176 136 156 136 C112 136 72 160 40 192 Z'
icon('hopper-logo', B, tags('hopper', 'travel', 'flights', 'bunny', 'rabbit', 'booking'),
     area=[P(HOP)], line=[P(HOP), P('M184 108 C176 84 180 56 196 40 C212 60 212 88 204 116')],
     dot=[C(84, 116, 16)])

if __name__ == '__main__':
    import re
    for ic in ICONS:  # anchors on curve extremes (198_extremes.fix_d)
        for k, v in ic.items():
            if isinstance(v, list) and k != 'tags':
                ic[k] = [re.sub(r' d="([^"]*)"', lambda m: f' d="{fix_d(m.group(1))}"', e) for e in v]
    print(save(overwrite='--overwrite' in sys.argv))
