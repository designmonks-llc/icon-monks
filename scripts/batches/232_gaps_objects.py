"""Gap fill from the 2026-10-20 comparison with eight other libraries: objects, food, science and music."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *


def turn(points, deg, c=(128, 128)):
    """Rotate points about c and round to whole units."""
    return [(round(x), round(y)) for x, y in rot(points, deg, c)]


# ---------------------------------------------------------------- household and personal care
# toothbrush: a long handle with the bristle block standing on its head end
icon('toothbrush', 'Health', ['toothbrush', 'teeth', 'dental', 'hygiene', 'brush'],
     line=[R(32, 152, 192, 32, 16), R(144, 96, 64, 56, 8)],
     area=[R(32, 152, 192, 32, 16), R(144, 96, 64, 56, 8)],
     detail=[L(176, 96, 176, 152)])

# lotion-tube: a squeeze tube, crimped flat at the top and narrowing to a screw cap
TUBE = 'M64 40 H192 C192 112 152 136 152 176 H104 C104 136 64 112 64 40 Z'
icon('lotion-tube', 'Health', ['lotion', 'cream', 'tube', 'skincare', 'cosmetics', 'toothpaste'],
     line=[P(TUBE), R(96, 176, 64, 48, 8)], area=[P(TUBE), R(96, 176, 64, 48, 8)],
     detail=[L(80, 72, 176, 72)])

# robot-vacuum: the round robot seen from above, with its front bumper arc and a button
icon('robot-vacuum', 'Home', ['robot vacuum', 'roomba', 'cleaning', 'vacuum', 'smart home'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[P('M72 104 A64 64 0 0 1 184 104')], dotcut=[C(128, 156, 14)])

# floor-lamp: shade on a tall pole with a foot
SHADE = PG([(96, 40), (160, 40), (184, 104), (72, 104)])
icon('floor-lamp', 'Home', ['floor lamp', 'lamp', 'light', 'furniture', 'standing lamp'],
     line=[SHADE, L(128, 104, 128, 216), L(88, 216, 168, 216)], area=[SHADE])

# wall-lamp: a sconce, a wall plate with an arm reaching out to a shade
WSHADE = PG([(136, 56), (200, 56), (224, 136), (112, 136)])
icon('wall-lamp', 'Home', ['wall lamp', 'sconce', 'lamp', 'light', 'fixture'],
     line=[WSHADE, L(48, 120, 48, 208), P('M48 164 H120 C152 164 168 156 168 136')], area=[WSHADE])

# thread-spool: two flanges with the wound thread between them
icon('thread-spool', 'Objects', ['thread', 'spool', 'sewing', 'bobbin', 'yarn'],
     line=[L(56, 48, 200, 48), L(56, 208, 200, 208), L(80, 48, 80, 208), L(176, 48, 176, 208)],
     area=[R(80, 48, 96, 160)],
     detail=[L(80, 116, 176, 92), L(80, 164, 176, 140)])

# typewriter: the paper standing out of the body, a row of keys and the space bar
icon('typewriter', 'Objects', ['typewriter', 'typing', 'writer', 'vintage', 'keyboard'],
     line=[R(32, 104, 192, 112, 16), P('M80 104 V40 H176 V104')], area=[R(32, 104, 192, 112, 16)],
     detail=[L(72, 184, 184, 184)], dotcut=[C(80, 144, 14), C(128, 144, 14), C(176, 144, 14)])

# bunting: a line of pennant flags
FLAGS = [PG([(44, 72), (92, 72), (68, 176)]), PG([(104, 72), (152, 72), (128, 176)]),
         PG([(164, 72), (212, 72), (188, 176)])]
icon('bunting', 'Objects', ['bunting', 'garland', 'party', 'flags', 'celebration', 'decoration'],
     line=[L(32, 72, 224, 72)] + FLAGS, area=FLAGS)

# diploma: a rolled scroll tied with a ribbon whose two tails hang below
ROLL = 'M64 104 H192 A24 24 0 0 1 192 152 H64 A24 24 0 0 1 64 104 Z'
icon('diploma', 'Education', ['diploma', 'degree', 'graduation', 'scroll', 'certificate'],
     line=[P(ROLL), L(120, 152, 104, 216), L(144, 152, 160, 216)], area=[P(ROLL)],
     detail=[P('M64 104 A24 24 0 0 1 64 152'), L(132, 104, 132, 152)])

# slot-machine: cabinet with three reels, the payout tray and the pull lever
icon('slot-machine', 'Objects', ['slot machine', 'casino', 'gambling', 'jackpot', 'fruit machine'],
     line=[R(32, 48, 160, 176, 16), P('M192 160 H216 V88')], area=[R(32, 48, 160, 176, 16)],
     detail=[R(56, 88, 112, 64, 8), L(93, 88, 93, 152), L(131, 88, 131, 152), L(72, 192, 152, 192)],
     dot=[C(216, 72, 16)])

# ---------------------------------------------------------------- food and drink
# bacon: a wavy strip with a stripe of fat running along it
TOPW = 'M32 72 C64 40 96 104 128 72 C160 40 192 104 224 72'
BACON = (TOPW + ' L224 152 C192 184 160 120 128 152 C96 184 64 120 32 152 Z')
icon('bacon', 'Food', ['bacon', 'breakfast', 'meat', 'pork', 'strip'],
     line=[P(BACON)], area=[P(BACON)],
     detail=[P('M32 112 C64 80 96 144 128 112 C160 80 192 144 224 112')])

# onion: the bulb with its pointed tip and two inner layers
ONION = 'M128 40 C152 80 208 104 208 152 C208 196 172 216 128 216 C84 216 48 196 48 152 C48 104 104 80 128 40 Z'
icon('onion', 'Food', ['onion', 'vegetable', 'cooking', 'garlic', 'bulb'],
     line=[P(ONION), L(128, 40, 128, 32)], area=[P(ONION)],
     detail=[P('M108 96 C84 124 84 176 112 212'), P('M148 96 C172 124 172 176 144 212')])

# squid: a pointed mantle with eyes and three wavy arms
MANTLE = 'M128 32 C160 56 176 88 176 128 H80 C80 88 96 56 128 32 Z'
icon('squid', 'Animals', ['squid', 'calamari', 'sea', 'seafood', 'ocean'],
     line=[P(MANTLE), P('M88 128 C88 176 64 184 64 216'), L(128, 128, 128, 224),
           P('M168 128 C168 176 192 184 192 216')],
     area=[P(MANTLE)], dotcut=[C(108, 104, 14), C(148, 104, 14)])

# protein-shaker: a tapered cup, a screw lid and the drinking spout
CUP = PG([(64, 96), (192, 96), (176, 224), (80, 224)])
icon('protein-shaker', 'Sports', ['protein shaker', 'shaker', 'bottle', 'gym', 'fitness', 'drink'],
     line=[CUP, R(64, 64, 128, 32, 8), P('M104 64 V40 H136 V64')], area=[CUP, R(64, 64, 128, 32, 8)],
     detail=[L(92, 136, 120, 136), L(96, 176, 120, 176)])

# amphora: a two-handled jar with a narrow neck and a small foot
JAR = ('M108 40 V72 C72 88 64 112 64 136 C64 168 96 192 112 208 H144 C160 192 192 168 192 136 '
       'C192 112 184 88 148 72 V40 Z')
icon('amphora', 'Objects', ['amphora', 'vase', 'jar', 'ancient', 'pottery', 'greek'],
     line=[P(JAR), P('M108 52 C76 52 64 72 72 96'), P('M148 52 C180 52 192 72 184 96'),
           PL([(112, 208), (104, 224), (152, 224), (144, 208)])],
     area=[P(JAR)])

# ---------------------------------------------------------------- science and electronics
# petri-dish: a shallow dish seen from the side, with two colonies on the agar
icon('petri-dish', 'Science', ['petri dish', 'lab', 'culture', 'bacteria', 'biology', 'experiment'],
     line=[E(128, 104, 96, 40), P('M32 104 V152 A96 40 0 0 0 224 152 V104')],
     area=[P('M32 104 A96 40 0 0 1 224 104 V152 A96 40 0 0 1 32 152 Z')],
     dot=[C(100, 100, 16), C(156, 108, 16)])

# circuit-fuse: the schematic fuse, a box with the wire running through it
icon('circuit-fuse', 'Science', ['circuit fuse', 'fuse', 'circuit', 'electronics', 'schematic'],
     line=[L(32, 128, 224, 128), R(72, 96, 112, 64)], area=[R(72, 96, 112, 64)])

# monitor-curved: a display with curved top and bottom edges on a stand
SCREEN = 'M32 48 C96 72 160 72 224 48 V168 C160 192 96 192 32 168 Z'
icon('monitor-curved', 'Devices', ['curved monitor', 'monitor', 'display', 'ultrawide', 'screen'],
     line=[P(SCREEN), L(128, 186, 128, 216), L(88, 216, 168, 216)], area=[P(SCREEN)])

# air-vent: an air conditioner unit with its vent slot and air flowing down
icon('air-vent', 'Home', ['air vent', 'air conditioner', 'ac', 'ventilation', 'cooling'],
     line=[R(32, 40, 192, 80, 16), P('M80 152 C80 176 64 184 64 216'), L(128, 152, 128, 216),
           P('M176 152 C176 176 192 184 192 216')],
     area=[R(32, 40, 192, 80, 16)], detail=[L(64, 88, 192, 88)])

# rubiks-cube: an isometric cube, each visible face split into four
HEX = [(128, 32), (212, 80), (212, 176), (128, 224), (44, 176), (44, 80)]
icon('rubiks-cube', 'Objects', ['rubiks cube', 'puzzle', 'cube', 'toy', 'game'],
     line=[PG(HEX), P('M44 80 L128 128 L212 80 M128 128 L128 224')], area=[PG(HEX)],
     detail=[L(170, 56, 86, 104), L(86, 56, 170, 104), L(86, 104, 86, 200), L(44, 128, 128, 176),
             L(170, 104, 170, 200), L(212, 128, 128, 176)], reviewed=True)

# ant: head, thorax and abdomen, three pairs of legs and the antennae
icon('ant', 'Animals', ['ant', 'insect', 'bug', 'colony', 'pest'],
     line=[C(128, 60, 20), E(128, 114, 16, 22), E(128, 180, 30, 40),
           P('M76 76 L120 104'), P('M180 76 L136 104'), L(64, 120, 192, 120),
           P('M76 168 L104 140 M180 168 L152 140'), P('M104 32 L118 44 M152 32 L138 44')],
     area=[C(128, 60, 20), E(128, 114, 16, 22), E(128, 180, 30, 40)])

# scalpel: a slim handle with a curved blade, laid on the diagonal
HANDLE = turn([(8, 116), (148, 116), (148, 140), (8, 140)], -45)
BLADE = turn([(148, 116), (248, 116), (232, 140), (196, 148), (148, 140)], -45)
blade = f'M{pt(BLADE[0])} L{pt(BLADE[1])} C{pt(BLADE[2])} {pt(BLADE[3])} {pt(BLADE[4])} Z'
icon('scalpel', 'Health', ['scalpel', 'surgery', 'knife', 'medical', 'blade', 'cut'],
     line=[PG(HANDLE), P(blade)], area=[PG(HANDLE), P(blade)])

# ---------------------------------------------------------------- music
# bass-clef: the F clef, a hook that starts at a dot, and its two dots on the right
icon('bass-clef', 'Media', ['bass clef', 'f clef', 'clef', 'music', 'notation'],
     line=[P('M48 104 C48 72 76 56 104 56 C144 56 168 84 168 120 C168 168 120 200 48 216')],
     dot=[C(64, 104, 16), C(200, 96, 16), C(200, 144, 16)])

# alto-clef: the C clef, two bars and the two brackets meeting at the middle line
icon('alto-clef', 'Media', ['alto clef', 'c clef', 'clef', 'music', 'notation'],
     line=[L(56, 40, 56, 216), L(96, 40, 96, 216),
           P('M96 128 C128 96 136 48 168 48 C196 48 208 72 196 92'),
           P('M96 128 C128 160 136 208 168 208 C196 208 208 184 196 164')])

# tambourine: the frame ring with four pairs of jingles
icon('tambourine', 'Media', ['tambourine', 'percussion', 'instrument', 'music', 'jingle'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     dotcut=[C(128, 64, 14), C(192, 128, 14), C(128, 192, 14), C(64, 128, 14)])

# pan-flute: pipes of falling length bound together by a band
PIPES = PG([(40, 48), (216, 48), (216, 112), (184, 112), (184, 136), (148, 136), (148, 160), (112, 160),
            (112, 184), (76, 184), (76, 208), (40, 208)])
icon('pan-flute', 'Media', ['pan flute', 'pan pipes', 'flute', 'instrument', 'music'],
     line=[PIPES], area=[PIPES],
     detail=[L(76, 48, 76, 184), L(112, 48, 112, 160), L(148, 48, 148, 136), L(184, 48, 184, 112),
             L(40, 80, 216, 80)])

print(save(overwrite=True))
