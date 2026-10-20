"""Brand logos: hardware and electronics makers."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import importlib.util

_spec = importlib.util.spec_from_file_location('extremes', os.path.join(os.path.dirname(os.path.abspath(__file__)), '198_extremes.py'))
_ext = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ext)


def PX(d):
    """Path with anchors added on its curve extremes."""
    return P(_ext.fix_d(d))


B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def disc(name, tags, detail, **kw):
    icon(name, B, tags + ['logo', 'brand'], area=[RING], line=[RING], detail=detail, **kw)


# ---------------------------------------------------------------- boards and chips

# Arduino: the infinity loop with minus and plus.
INF = ('M128 128 C148 100 160 84 180 84 A44 44 0 0 1 180 172 C160 172 148 156 128 128 '
       'C108 100 96 84 76 84 A44 44 0 0 0 76 172 C96 172 108 156 128 128 Z')
icon('arduino-logo', B, ['arduino', 'microcontroller', 'electronics', 'maker', 'hardware', 'logo', 'brand'],
     area=[P(INF)], line=[P(INF)],
     detail=[L(60, 128, 92, 128), L(164, 128, 196, 128), L(180, 112, 180, 144)])

# NVIDIA: the eye, its outer lid running out of the square and its swirl curling inside.
NV_BOX = R(124, 52, 100, 152, 8)
NV_LID = 'M124 72 C88 80 52 100 32 128 C52 156 88 176 124 184'
icon('nvidia-logo', B, ['nvidia', 'gpu', 'graphics', 'chips', 'ai', 'gaming', 'logo', 'brand'],
     area=[NV_BOX, P(NV_LID + ' Z')], line=[NV_BOX, P(NV_LID)],
     detail=[P('M124 156 C100 154 80 144 64 128 C80 114 100 104 124 100 C156 96 180 120 188 164')],
     dotcut=[C(104, 130, 14)])

# AMD: the arrow, an open square bracket and the wedge it points from.
icon('amd-logo', B, ['amd', 'chips', 'processor', 'cpu', 'gpu', 'semiconductor', 'logo', 'brand'],
     area=[PG([(40, 40), (216, 40), (216, 216), (164, 164), (164, 92), (92, 92)]),
           PG([(76, 116), (40, 152), (40, 216), (100, 216), (140, 176), (76, 176)])],
     line=[PG([(40, 40), (216, 40), (216, 216), (164, 164), (164, 92), (92, 92)]),
           PG([(76, 116), (40, 152), (40, 216), (100, 216), (140, 176), (76, 176)])])

# ---------------------------------------------------------------- phones and computers

# Xiaomi: the "mi" on the rounded tile.
icon('xiaomi-logo', B, ['xiaomi', 'mi', 'phone', 'smartphone', 'electronics', 'logo', 'brand'],
     area=[R(40, 40, 176, 176, 56)], line=[R(40, 40, 176, 176, 56)],
     detail=[P('M72 176 V88 H124 A32 32 0 0 1 156 120 V176'), L(114, 128, 114, 176), L(184, 88, 184, 176)])

# OnePlus: the 1 in a square that opens at the top right for the plus.
icon('oneplus-logo', B, ['oneplus', '1+', 'phone', 'smartphone', 'android', 'logo', 'brand'],
     line=[P('M128 40 H40 V216 H216 V128'), PL([(96, 112), (120, 96), (120, 176)]),
           L(184, 40, 184, 104), L(152, 72, 216, 72)], outline=True)

# LG: the face, a G round the edge, the L for a nose and one eye.
disc('lg-logo', ['lg', 'life is good', 'electronics', 'appliances', 'phone'],
     [P('M128 64 A64 64 0 1 0 192 128 H152'), PL([(128, 88), (128, 168), (152, 168)])],
     dotcut=[C(100, 104, 14)])

# HP: the slanted h and p in the circle.
def sl(x, y):
    return (round(x - (y - 128) * 0.3), y)
disc('hp-logo', ['hp', 'hewlett packard', 'computers', 'printers', 'laptops'],
     [PL([sl(84, 60), sl(84, 176)]), PL([sl(84, 108), sl(116, 108), sl(116, 176)]),
      PL([sl(148, 108), sl(148, 212)]), PG([sl(148, 108), sl(180, 108), sl(180, 164), sl(148, 164)])])

# Motorola: the pointed batwing M in the circle.
disc('motorola-logo', ['motorola', 'moto', 'phone', 'smartphone', 'electronics'],
     [PL([(64, 188), (100, 60), (128, 148), (156, 60), (192, 188)])])

# ---------------------------------------------------------------- audio and wearables

# Beats: the b in the circle.
disc('beats-logo', ['beats', 'beats by dre', 'headphones', 'audio', 'apple', 'b'],
     [L(96, 56, 96, 148), C(136, 148, 40)])

# Fitbit: the diamond of dots.
FIT = [(48, 128), (88, 88), (88, 128), (88, 168), (128, 48), (128, 88), (128, 128), (128, 168), (128, 208),
       (168, 88), (168, 128), (168, 168), (208, 128)]
icon('fitbit-logo', B, ['fitbit', 'fitness tracker', 'wearable', 'health', 'google', 'logo', 'brand'],
     dot=[C(x, y, 16) for x, y in FIT])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
