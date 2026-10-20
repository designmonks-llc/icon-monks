"""Brand logos: car makers."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['car', 'automotive', 'logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


# ---------------------------------------------------------------- japan and korea
# Honda: the H whose legs flare out at the top, with a crossbar that sags in the middle.
honda = ('M40 64 H84 L90 112 C102 117 114 120 128 120 C142 120 154 117 166 112 L172 64 H216 L184 192 H156 '
         'L161 152 C149 157 138 160 128 160 C118 160 107 157 95 152 L100 192 H72 Z')
brand('honda-logo', ['honda', 'japan'], area=[P(honda)], line=[P(honda)])

# Hyundai: the leaning H in a wide oval.
HY = E(128, 128, 96, 72)
brand('hyundai-logo', ['hyundai', 'korea'],
      area=[HY], line=[HY],
      detail=[L(76, 164, 100, 92), L(156, 164, 180, 92), L(88, 128, 168, 128)])

# Kia: the 2021 signature, a K joined to an I and a crossbar-less A in one zigzag.
brand('kia-logo', ['kia', 'korea'],
      line=[PL([(36, 80), (36, 176), (132, 80), (132, 176), (220, 80), (220, 176)]), L(72, 140, 100, 176)])

# Mazda: the winged M in an oval.
MZ = E(128, 128, 96, 76)
brand('mazda-logo', ['mazda', 'japan'],
      area=[MZ], line=[MZ],
      detail=[P('M40 120 C56 100 72 88 88 84 C104 104 116 128 128 156 C140 128 152 104 168 84 '
                'C184 88 200 100 216 120')])

# Subaru: the Pleiades in an oval, one big star and five small ones.
SB = E(128, 128, 96, 72)
brand('subaru-logo', ['subaru', 'pleiades', 'stars', 'japan'],
      area=[SB], line=[SB],
      detail=[PG([(52, 108), (80, 100), (88, 72), (96, 100), (124, 108), (96, 116), (88, 144), (80, 116)])],
      dotcut=[C(176, 92, 14), C(140, 128, 14), C(188, 132, 14), C(104, 168, 14), C(152, 164, 14)])

# Lexus: the slanted L in an oval, its foot running out to the oval's edge.
LX = E(128, 128, 96, 72)
brand('lexus-logo', ['lexus', 'toyota', 'luxury', 'japan'],
      area=[LX], line=[LX], detail=[PL([(148, 80), (96, 152), (218, 152)])])

# Infiniti: the road running to the horizon inside an oval ring.
brand('infiniti-logo', ['infiniti', 'nissan', 'luxury', 'japan'],
      line=[P('M104 182 L128 92 L152 182 A96 56 0 1 0 104 182')])

# Acura: the caliper A inside a rounded square.
AC = R(44, 40, 168, 176, 68)
brand('acura-logo', ['acura', 'honda', 'luxury', 'caliper', 'japan'],
      area=[AC], line=[AC], detail=[PL([(88, 208), (128, 48), (168, 208)]), L(128, 48, 128, 104)])

# Mitsubishi: three diamonds meeting at one point.
O = (128, 142)
dia = [(128, 142), (97, 88), (128, 34), (159, 88)]
MI = [PG([ipt(p) for p in rot(dia, a, O)]) for a in (0, 120, 240)]
brand('mitsubishi-logo', ['mitsubishi', 'diamonds', 'japan'], area=MI, line=MI)

# Suzuki: the angular S with its slit.
SZ = ('M32 92 L130 32 L224 96 C208 104 184 108 160 108 L224 160 L126 224 L32 160 '
      'C48 152 72 148 96 148 Z')
brand('suzuki-logo', ['suzuki', 'motorcycle', 'japan'], area=[P(SZ)], line=[P(SZ)], detail=[L(104, 80, 152, 172)])

# ---------------------------------------------------------------- europe
# Volvo: the iron mark, a circle with its arrow and the name band across it.
VC = C(116, 140, 80)
VH = PG([(224, 32), (180, 36), (220, 76)])
brand('volvo-logo', ['volvo', 'iron mark', 'sweden'],
      area=[VC, VH], line=[VC, L(173, 83, 204, 52), VH], detail=[R(52, 124, 128, 32, 8)])

# MINI: the winged circle.
MN = C(128, 128, 48)
brand('mini-logo', ['mini', 'bmw', 'wings', 'uk'],
      area=[MN], line=[MN, L(32, 104, 86, 104), L(56, 144, 83, 144), L(170, 104, 224, 104), L(173, 144, 200, 144)])

# Renault: the double-outlined lozenge.
RO = PG([(128, 32), (200, 128), (128, 224), (56, 128)])
brand('renault-logo', ['renault', 'diamond', 'lozenge', 'france'],
      area=[RO], line=[RO], detail=[PG([(128, 100), (149, 128), (128, 156), (107, 128)])])

# Citroen: the double chevron in an upright oval.
CI = E(128, 128, 72, 96)
brand('citroen-logo', ['citroen', 'chevrons', 'france'],
      area=[CI], line=[CI], detail=[PL([(56, 128), (128, 88), (200, 128)]), PL([(64, 172), (128, 136), (192, 172)])])

# Maserati: the trident.
brand('maserati-logo', ['maserati', 'trident', 'luxury', 'italy'],
      line=[L(128, 40, 128, 224), PL([(112, 64), (128, 40), (144, 64)]),
            P('M128 148 C88 148 72 128 72 96 V56'), P('M128 148 C168 148 184 128 184 96 V56'),
            L(100, 176, 156, 176)])

# McLaren: the speedmark swoosh.
MC = ('M32 144 C80 96 140 74 196 74 C212 74 224 78 224 84 C224 120 196 156 168 180 '
      'C156 152 128 132 100 132 C72 132 48 136 32 144 Z')
brand('mclaren-logo', ['mclaren', 'speedmark', 'supercar', 'racing', 'uk'], area=[P(MC)], line=[P(MC)])

# Bentley: the B between two swept wings.
BN = 'M112 88 V168 H136 A20 20 0 0 0 136 128 H112 M112 88 H132 A20 20 0 0 1 132 128'
brand('bentley-logo', ['bentley', 'winged b', 'wings', 'luxury', 'uk'],
      line=[P(BN), P('M88 96 C64 96 44 88 32 76'), P('M88 136 C68 136 52 128 44 116'),
            P('M168 96 C192 96 212 88 224 76'), P('M168 136 C188 136 204 128 212 116')])

# Rolls-Royce: the overlapping RR in its badge.
RR = R(56, 32, 144, 192, 16)
brand('rolls-royce-logo', ['rolls-royce', 'rolls royce', 'rr', 'luxury', 'uk'],
      area=[RR], line=[RR],
      detail=[P('M88 184 V72 H112 A24 24 0 0 1 112 120 H88 M108 120 L136 184'),
              P('M136 184 V72 H148 A24 24 0 0 1 148 120 H136 M148 120 L172 184')])

# SEAT: the S cut out of a square badge by two slits.
SE = R(40, 40, 176, 176, 16)
brand('seat-logo', ['seat', 'cupra', 'spain'],
      area=[SE], line=[SE], detail=[L(40, 100, 192, 124), L(64, 144, 216, 168)])

# Opel: the blitz crossing a ring.
OP = C(128, 128, 72)
brand('opel-logo', ['opel', 'vauxhall', 'blitz', 'lightning', 'germany'],
      area=[OP], line=[OP, L(32, 108, 59, 108), L(197, 148, 224, 148)],
      detail=[PL([(59, 108), (156, 108), (100, 148), (197, 148)])])

# Polestar: the four-point star split into two offset chevrons.
brand('polestar-logo', ['polestar', 'volvo', 'electric', 'ev', 'sweden'],
      area=[PG([(120, 32), (128, 112), (40, 120), (112, 112)]), PG([(136, 224), (128, 144), (216, 136), (144, 144)])],
      line=[PG([(120, 32), (128, 112), (40, 120), (112, 112)]), PG([(136, 224), (128, 144), (216, 136), (144, 144)])])

# ---------------------------------------------------------------- americas and china
# Chevrolet: the bowtie.
CH = PG([(32, 104), (92, 104), (92, 76), (164, 76), (164, 104), (224, 104), (208, 152), (164, 152), (164, 180),
         (92, 180), (92, 152), (48, 152)])
brand('chevrolet-logo', ['chevrolet', 'chevy', 'bowtie', 'gm', 'usa'], area=[CH], line=[CH])

# Lincoln: the star, a tall frame crossed by two lines that run past it.
LF = R(88, 48, 80, 160, 8)
brand('lincoln-logo', ['lincoln', 'ford', 'star', 'luxury', 'usa'],
      area=[LF], line=[LF, L(128, 32, 128, 48), L(128, 208, 128, 224), L(56, 120, 88, 120), L(168, 120, 200, 120)],
      detail=[L(128, 48, 128, 208), L(88, 120, 168, 120)])

# GMC: the three block letters.
brand('gmc-logo', ['gmc', 'general motors', 'gm', 'trucks', 'usa'], outline=True,
      line=[P('M80 88 H48 A16 16 0 0 0 32 104 V152 A16 16 0 0 0 48 168 H80 V128 H60'),
            PL([(104, 168), (104, 88), (128, 124), (152, 88), (152, 168)]),
            P('M224 88 H192 A16 16 0 0 0 176 104 V152 A16 16 0 0 0 192 168 H224')])

# Rivian: the compass, two chevrons around two inner brackets.
brand('rivian-logo', ['rivian', 'electric', 'ev', 'compass', 'usa'],
      line=[PL([(36, 116), (128, 32), (220, 116)]), PL([(36, 140), (128, 224), (220, 140)]),
            PL([(116, 76), (116, 96), (84, 128), (116, 160), (116, 180)]),
            PL([(140, 76), (140, 96), (172, 128), (140, 160), (140, 180)])])

# BYD: the 2021 wordmark, a B drawn as a 3, a cupped Y and an open D.
brand('byd-logo', ['byd', 'build your dreams', 'electric', 'ev', 'china'], outline=True,
      line=[P('M32 88 H64 A16 16 0 0 1 80 104 V152 A16 16 0 0 1 64 168 H32'), L(48, 128, 80, 128),
            P('M104 88 V112 A16 16 0 0 0 120 128 H136 A16 16 0 0 0 152 112 V88'), L(128, 128, 128, 168),
            P('M176 88 H196 A28 28 0 0 1 224 116 V140 A28 28 0 0 1 196 168 H176')])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
