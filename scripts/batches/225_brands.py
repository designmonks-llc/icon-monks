"""Brand logos: Google, Microsoft and Apple apps."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
TILE_APPLE = R(40, 40, 176, 176, 40)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


# ---------------------------------------------------------------- google
# YouTube Kids: the YouTube play button, tipped over to one side.
KID_C = (128, 128)
kr = 36
kx0, ky0, kx1, ky1 = 40, 72, 216, 184
kcorners = [((kx1 - kr, ky0 + kr), -90, 0), ((kx1 - kr, ky1 - kr), 0, 90),
            ((kx0 + kr, ky1 - kr), 90, 180), ((kx0 + kr, ky0 + kr), 180, 270)]
kd = ''
for i, (c, a0, a1) in enumerate(kcorners):
    p0 = ipt(rot([polar(c, kr, a0)], -8, KID_C)[0])
    p1 = ipt(rot([polar(c, kr, a1)], -8, KID_C)[0])
    kd += (f'M{pt(p0)} ' if i == 0 else f'L{pt(p0)} ') + f'A{kr} {kr} 0 0 1 {pt(p1)} '
kd += 'Z'
ktri = [ipt(p) for p in rot([(108, 100), (164, 128), (108, 156)], -8, KID_C)]
brand('youtube-kids-logo', ['youtube kids', 'youtube', 'google', 'video', 'kids', 'children'],
      area=[P(kd)], line=[P(kd)], detail=[PG(ktri)])

# Google Podcasts: five columns of rounded bars, symmetric under a half turn.
POD = [(40, 120, 136), (216, 120, 136), (84, 80, 124), (84, 164, 176), (172, 132, 176), (172, 80, 92),
       (128, 92, 164), (128, 40, 52), (128, 204, 216)]
brand('google-podcasts-logo', ['google podcasts', 'google', 'podcast', 'audio', 'listening'],
      line=[L(x, a, x, b) for x, a, b in POD], reviewed=True)

# Google Voice: the handset in the lower left and the quarter disc in the upper right.
HANDSET = ('M50 92 H74 L86 131 L68 146 C83 161 95 173 110 188 L125 170 L164 182 V206 '
           'A18 18 0 0 1 146 224 C80 224 32 176 32 110 A18 18 0 0 1 50 92 Z')
QUARTER = 'M136 120 V32 A88 88 0 0 1 224 120 Z'
brand('google-voice-logo', ['google voice', 'google', 'phone', 'calls', 'voicemail'],
      area=[P(HANDSET), P(QUARTER)], line=[P(HANDSET), P(QUARTER)])

# Google Sites: the page tile with its header, side column and the small block in the corner.
SITES = R(32, 52, 192, 152, 16)
brand('google-sites-logo', ['google sites', 'google', 'website builder', 'web page', 'sites'],
      area=[SITES], line=[SITES],
      detail=[L(32, 100, 224, 100), L(88, 100, 88, 204), L(168, 164, 184, 164)])

# Google Colab: the C and the O side by side, the C open towards the O.
brand('google-colab-logo', ['google colab', 'colaboratory', 'google', 'notebook', 'jupyter', 'python'],
      line=[P('M98 73 A56 56 0 1 0 98 183'), C(168, 128, 56)], outline=True)

# Wear OS: two slanted bars and two dots.
brand('wear-os-logo', ['wear os', 'google', 'smartwatch', 'wearable', 'android'],
      line=[L(48, 72, 100, 192), L(108, 72, 160, 192)], dot=[C(184, 120, 16), C(208, 72, 16)])

# ---------------------------------------------------------------- microsoft
# Letter tile in front of the app's back shape (as microsoft-word-logo).
TILE = R(32, 72, 112, 112, 16)
SHEET = R(72, 32, 152, 192, 16)
SHEET_EDGE = P('M72 72 V48 A16 16 0 0 1 88 32 H208 A16 16 0 0 1 224 48 V208 A16 16 0 0 1 208 224 H88 '
               'A16 16 0 0 1 72 208 V184')

# Visio: the diamond, square and circle behind the V tile.
VIS = ('M108 72 L148 32 L196 80 H208 A16 16 0 0 1 224 96 V160 A16 16 0 0 1 208 176 H196 '
       'A48 48 0 0 1 101 184')
brand('microsoft-visio-logo', ['microsoft visio', 'visio', 'microsoft', 'diagram', 'flowchart', 'office'],
      area=[P(VIS + ' Z'), TILE], line=[TILE, P(VIS)],
      detail=[PL([(64, 104), (88, 152), (112, 104)]), L(196, 80, 156, 120)])

# Publisher: the page in two bands behind the P tile.
brand('microsoft-publisher-logo', ['microsoft publisher', 'publisher', 'microsoft', 'desktop publishing',
                                   'layout', 'office'],
      area=[SHEET, TILE], line=[TILE, SHEET_EDGE],
      detail=[P('M68 160 V96 H92 A20 20 0 0 1 92 136 H68'), L(144, 128, 224, 128), L(144, 176, 224, 176)])

# Access: the stacked database cylinder behind the A tile.
CYL = 'M80 56 A72 24 0 0 1 224 56 V200 A72 24 0 0 1 80 200 Z'
brand('microsoft-access-logo', ['microsoft access', 'access', 'microsoft', 'database', 'office'],
      area=[P(CYL), TILE],
      line=[TILE, E(152, 56, 72, 24), P('M224 56 V200 A72 24 0 0 1 80 200 V184')],
      detail=[PL([(64, 160), (88, 96), (112, 160)]), L(76, 136, 100, 136),
              P('M224 104 A72 24 0 0 1 144 128'), P('M224 152 A72 24 0 0 1 144 176')])

# To Do: the check made of two rounded bars, the long one in front.
TD_LONG = 'M114 194 L218 90 A20 20 0 0 0 190 62 L86 166 A20 20 0 0 0 114 194 Z'
TD_SHORT = 'M100 152 L66 118 A20 20 0 0 0 38 146 L84 192'
brand('microsoft-to-do-logo', ['microsoft to do', 'to do', 'microsoft', 'tasks', 'checklist', 'check'],
      area=[P(TD_LONG), P(TD_SHORT + ' Z')], line=[P(TD_LONG), P(TD_SHORT)])

# Loop: the ring with a square lower-left corner, its hole the same shape.
LOOP = 'M40 128 A88 88 0 1 1 128 216 H56 A16 16 0 0 1 40 200 Z'
brand('microsoft-loop-logo', ['microsoft loop', 'loop', 'microsoft', 'collaboration', 'workspace'],
      area=[P(LOOP)], line=[P(LOOP)],
      detail=[P('M96 128 A32 32 0 1 1 128 160 H104 A8 8 0 0 1 96 152 Z')])

# ---------------------------------------------------------------- apple
# Notes: the pad with its band across the top.
brand('apple-notes-logo', ['apple notes', 'notes', 'apple', 'notepad', 'ios'],
      area=[TILE_APPLE], line=[TILE_APPLE],
      detail=[L(40, 96, 216, 96), L(72, 136, 184, 136), L(72, 176, 152, 176)])

# Calendar: the weekday label over the date.
brand('apple-calendar-logo', ['apple calendar', 'calendar', 'apple', 'date', 'ios'],
      area=[TILE_APPLE], line=[TILE_APPLE],
      detail=[L(104, 76, 152, 76), PL([(80, 128), (96, 116), (96, 184)]), PL([(128, 116), (176, 116), (144, 184)])])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
