"""Brand logos: sports leagues, clubs and sportswear."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def chord(c, r, off, u):
    """Whole-unit chord of circle (c, r) along unit vector u, shifted off units along its normal."""
    n = (-u[1], u[0])
    h = math.sqrt(r * r - off * off)
    m = (c[0] + n[0] * off, c[1] + n[1] * off)
    a = ipt((m[0] - u[0] * h, m[1] - u[1] * h))
    b = ipt((m[0] + u[0] * h, m[1] + u[1] * h))
    return L(a[0], a[1], b[0], b[1])


# ---------------------------------------------------------------- leagues and events
# Olympics: the five interlaced rings, three over two.
icon('olympics-logo', B, ['olympics', 'olympic rings', 'olympic games', 'sports', 'logo', 'brand'],
     line=[C(62, 112, 30), C(128, 112, 30), C(194, 112, 30), C(95, 144, 30), C(161, 144, 30)],
     outline=True)

# Formula 1: the slanted F with its inner speed stripe, and the 1.
icon('formula-1-logo', B, ['formula 1', 'f1', 'motorsport', 'racing', 'sports', 'logo', 'brand'],
     line=[P('M32 160 L80 112 C88 104 96 96 112 96 H168'),
           P('M88 160 L100 148 C108 140 112 136 124 136 H128'),
           L(160, 160, 224, 96)])

# WWE: the scratched W, a tall W with a shallow W inside its top.
icon('wwe-logo', B, ['wwe', 'wrestling', 'entertainment', 'sports', 'logo', 'brand'],
     line=[PL([(40, 40), (100, 212), (128, 132), (156, 212), (216, 40)]),
           PL([(76, 40), (100, 96), (128, 40), (156, 96), (180, 40)])])

# LaLiga: the two slanted hooks of the 2023 mark.
icon('la-liga-logo', B, ['laliga', 'la liga', 'football', 'soccer', 'spain', 'league', 'logo', 'brand'],
     line=[PL([(126, 64), (42, 160), (98, 136)]), PL([(214, 64), (102, 192), (158, 164)])])

# NFL: the shield with the football in its top.
NFL = ('M40 56 C72 56 104 48 128 36 C152 48 184 56 216 56 V136 C216 180 176 204 128 224 '
       'C80 204 40 180 40 136 Z')
icon('nfl-logo', B, ['nfl', 'national football league', 'american football', 'football', 'sports', 'league',
                     'logo', 'brand'],
     area=[P(NFL)], line=[P(NFL)],
     detail=[P('M80 168 A72 72 0 0 1 176 96 A72 72 0 0 1 80 168 Z'), L(116, 140, 140, 124)])

# ---------------------------------------------------------------- clubs
# Juventus: the two J strokes.
icon('juventus-logo', B, ['juventus', 'juve', 'football', 'soccer', 'club', 'italy', 'logo', 'brand'],
     area=[P('M48 32 H112 V144 C112 172 92 188 48 196 C72 180 84 168 84 148 V56 H48 Z'),
           P('M168 32 H208 V156 C208 196 168 216 88 224 C136 212 168 192 168 160 Z')],
     line=[P('M48 32 H112 V144 C112 172 92 188 48 196 C72 180 84 168 84 148 V56 H48 Z'),
           P('M168 32 H208 V156 C208 196 168 216 88 224 C136 212 168 192 168 160 Z')])

# Real Madrid: the crown over the ring, crossed by the sash.
RM_C, RM_R = (128, 152), 68
RM_U = (math.sqrt(0.5), math.sqrt(0.5))
CROWN = 'M84 76 L76 40 L104 56 L128 32 L152 56 L180 40 L172 76 Z'
icon('real-madrid-logo', B, ['real madrid', 'football', 'soccer', 'club', 'spain', 'crown', 'logo', 'brand'],
     area=[C(*RM_C, RM_R), P(CROWN)], line=[C(*RM_C, RM_R), P(CROWN)],
     detail=[chord(RM_C, RM_R, 20, RM_U), chord(RM_C, RM_R, -20, RM_U)])

# Barcelona: the crest with the cross and stripes on top, the band, and the stripes below.
FCB = ('M48 36 C60 44 76 48 88 48 C100 48 116 44 128 36 C140 44 156 48 168 48 C180 48 196 44 208 36 '
       'C208 72 212 100 224 124 C200 160 160 196 128 224 C96 196 56 160 32 124 C44 100 48 72 48 36 Z')
icon('barcelona-logo', B, ['fc barcelona', 'barcelona', 'barca', 'football', 'soccer', 'club', 'spain', 'logo',
                           'brand'],
     area=[P(FCB)], line=[P(FCB)],
     detail=[L(128, 44, 128, 100), L(88, 52, 88, 100), L(48, 76, 128, 76), L(168, 52, 168, 100),
             L(36, 120, 220, 120), L(88, 120, 88, 180), L(128, 120, 128, 212), L(168, 120, 168, 180)],
     reviewed=True)

# PSG: the ring around the Eiffel Tower.
TOWER = ('M128 72 C130 112 140 148 157 176 C152 166 140 160 128 160 C116 160 104 166 99 176 '
         'C116 148 126 112 128 72 Z')
icon('psg-logo', B, ['psg', 'paris saint-germain', 'paris', 'football', 'soccer', 'club', 'france', 'eiffel tower',
                     'logo', 'brand'],
     area=[RING], line=[RING], detail=[C(128, 128, 56), P(TOWER)])

# Arsenal: the shield with the cannon.
ARS = 'M40 40 H216 C216 128 184 192 128 224 C72 192 40 128 40 40 Z'
icon('arsenal-logo', B, ['arsenal', 'gunners', 'football', 'soccer', 'club', 'england', 'cannon', 'logo', 'brand'],
     area=[P(ARS)], line=[P(ARS)],
     detail=[P(capsule((128, 112), 52, 12, (1, 0))), C(124, 156, 28)],
     dotcut=[C(124, 156, 14)])

# New York Yankees: the interlocked N and Y.
icon('new-york-yankees-logo', B, ['new york yankees', 'yankees', 'ny', 'baseball', 'mlb', 'club', 'logo', 'brand'],
     line=[PL([(64, 216), (64, 56), (156, 216), (156, 40)]), PL([(40, 40), (156, 124), (216, 40)])],
     outline=True)

# ---------------------------------------------------------------- sportswear
# Converse: the star beside the chevron.
STAR = [ipt(polar((84, 132), 52 if i % 2 == 0 else 20, -90 + i * 36)) for i in range(10)]
CHEV = [(104, 40), (152, 40), (224, 128), (152, 216), (104, 216), (176, 128)]
icon('converse-logo', B, ['converse', 'star chevron', 'sneakers', 'footwear', 'sportswear', 'logo', 'brand'],
     area=[PG(STAR), PG(CHEV)], line=[PG(STAR), PG(CHEV)])

# Reebok: the vector, a wedge crossed by a blade that splits into two legs.
WEDGE = 'M32 88 H102 L192 168 C140 136 88 108 32 88 Z'
icon('reebok-logo', B, ['reebok', 'vector', 'sportswear', 'footwear', 'fitness', 'logo', 'brand'],
     area=[P(WEDGE)], line=[P(WEDGE), P('M224 88 C176 92 96 112 52 168'), P('M152 108 C128 124 112 144 104 168')])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
