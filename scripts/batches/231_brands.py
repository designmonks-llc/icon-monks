"""Brand logos: databases, data platforms and docs tools."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def arc_path(c, r, degs):
    """Open arc on circle (c, r) through the angles in degs (each step under 180 degrees), whole-unit anchors."""
    pts = [ipt(polar(c, r, d)) for d in degs]
    d = f'M{pt(pts[0])}'
    for a, b, q in zip(degs, degs[1:], pts[1:]):
        d += f' A{f(r)} {f(r)} 0 0 {1 if b > a else 0} {pt(q)}'
    return P(d)


# ---------------------------------------------------------------- databases
# Neon: the square band with the diagonal leg folded in from the bottom-right corner.
NEON = PG([(40, 40), (216, 40), (216, 204), (136, 136), (136, 216), (40, 216)])
icon('neon-logo', B, ['neon', 'postgres', 'database', 'serverless', 'logo', 'brand'],
     line=[NEON], outline=True)

# PlanetScale: the disc split by a diagonal cut, a small segment below it and a stripe inside.
PS_TOP = 'M213 63 A96 96 0 0 0 128 32 A96 96 0 0 0 32 128 A96 96 0 0 0 63 213 Z'
PS_LOW = 'M224 128 A96 96 0 0 1 128 224 Z'
icon('planetscale-logo', B, ['planetscale', 'mysql', 'database', 'serverless', 'logo', 'brand'],
     area=[P(PS_TOP), P(PS_LOW)], line=[P(PS_TOP), P(PS_LOW)],
     detail=[L(136, 104, 60, 180)])

# Upstash: two interlocking hooks, each an outer and an inner half ring around its own centre.
UB, UT = (114, 142), (142, 114)
icon('upstash-logo', B, ['upstash', 'redis', 'database', 'serverless', 'logo', 'brand'],
     line=[arc_path(UB, 72, [135, 90, 0, -45]), arc_path(UB, 31, [135, 90, 0, -45]),
           arc_path(UT, 72, [-45, -90, -180, -225]), arc_path(UT, 31, [-45, -90, -180, -225])])

# Turso: the horned bull mask with slanted eyes and a smile.
TURSO = PG([(60, 48), (64, 76), (192, 76), (196, 48), (220, 84), (220, 96), (184, 104), (180, 160),
            (156, 192), (128, 208), (100, 192), (76, 160), (72, 104), (36, 96), (36, 84)])
icon('turso-logo', B, ['turso', 'sqlite', 'libsql', 'database', 'edge', 'logo', 'brand'],
     area=[TURSO], line=[TURSO],
     detail=[L(92, 116, 112, 128), L(164, 116, 144, 128),
             P('M104 156 C110 164 118 168 128 168 C138 168 146 164 152 156')])

# Couchbase: the round badge with the couch (a tray with a notch) inside.
COUCH = PG([(64, 96), (100, 96), (100, 124), (156, 124), (156, 96), (192, 96), (192, 160), (64, 160)])
icon('couchbase-logo', B, ['couchbase', 'nosql', 'database', 'document database', 'logo', 'brand'],
     area=[RING], line=[RING], detail=[COUCH])

# ---------------------------------------------------------------- media and realtime
# Cloudinary: the cloud outline open at the bottom, with three rising arrows of falling height.
CL = [(72, 140, 40), (128, 104, 56), (184, 140, 40)]
cn = (128, 160)
far = lambda m: dist(m, cn)
s = ipt(polar(CL[0][:2], 40, 110))
e = ipt(polar(CL[2][:2], 40, 70))
x1 = ipt(circle_x(CL[0][:2], 40, CL[1][:2], 56)[0])
x2 = ipt(circle_x(CL[1][:2], 56, CL[2][:2], 40)[0])
CLOUD = (f'M{pt(s)} ' + arc_to((72, 140), 40, s, (32, 140), far) + ' ' + arc_to((72, 140), 40, (32, 140), x1, far)
         + ' ' + arc_to((128, 104), 56, x1, (128, 48), far) + ' ' + arc_to((128, 104), 56, (128, 48), x2, far)
         + ' ' + arc_to((184, 140), 40, x2, (224, 140), far) + ' ' + arc_to((184, 140), 40, (224, 140), e, far))
ARROWS = []
for x, top in ((84, 100), (128, 116), (172, 132)):
    ARROWS += [L(x, top, x, 184), PL([(x - 12, top + 12), (x, top), (x + 12, top + 12)])]
icon('cloudinary-logo', B, ['cloudinary', 'media', 'images', 'video', 'cdn', 'logo', 'brand'],
     line=[P(CLOUD)] + ARROWS)

# LiveKit: the L with the checkerboard arrow of squares beside it.
LK = PG([(38, 38), (74, 38), (74, 182), (136, 182), (136, 218), (38, 218)])
LK_SQ = [R(cx - 8, cy - 8, 16, 16, 4) for cx, cy in ((200, 56), (164, 92), (128, 128), (164, 164), (200, 200))]
icon('livekit-logo', B, ['livekit', 'webrtc', 'realtime', 'video', 'audio', 'logo', 'brand'],
     area=[LK] + LK_SQ, line=[LK] + LK_SQ)

# ---------------------------------------------------------------- workflows and data
# Temporal: two crossing ellipses on the app tile.
icon('temporal-logo', B, ['temporal', 'workflow', 'orchestration', 'durable execution', 'logo', 'brand'],
     area=[SQ], line=[SQ], detail=[E(128, 128, 24, 60), E(128, 128, 60, 24)])


# Apache Airflow: the four-bladed pinwheel; each blade runs straight out to a corner and curves back in.
def blade(k):
    pts = rot([(36, 36), (68, 36), (104, 40), (132, 52), (135, 62), (136, 76), (136, 88), (136, 104),
               (133, 118)], 90 * k)
    q = [pt(ipt(p)) for p in pts]
    return P(f'M128 128 L{q[0]} C{q[1]} {q[2]} {q[3]} C{q[4]} {q[5]} {q[6]} C{q[7]} {q[8]} 128 128 Z')


AIR = [blade(k) for k in range(4)]
icon('airflow-logo', B, ['airflow', 'apache airflow', 'apache', 'workflow', 'pipelines', 'pinwheel', 'logo', 'brand'],
     area=AIR, line=AIR)

# dbt: the broad X with rounded tips and the diamond hole at its centre.
DBT = ('M60 36 C84 36 104 80 128 80 C152 80 172 36 196 36 A24 24 0 0 1 220 60 '
       'C220 84 176 104 176 128 C176 152 220 172 220 196 A24 24 0 0 1 196 220 '
       'C172 220 152 176 128 176 C104 176 84 220 60 220 A24 24 0 0 1 36 196 '
       'C36 172 80 152 80 128 C80 104 36 84 36 60 A24 24 0 0 1 60 36 Z')
icon('dbt-logo', B, ['dbt', 'data build tool', 'analytics engineering', 'sql', 'data', 'logo', 'brand'],
     area=[P(DBT)], line=[P(DBT)], detail=[PG([(128, 112), (144, 128), (128, 144), (112, 128)])])

# Metabase: the M spelled out in a grid of dots.
MB = [(48, 68), (48, 108), (48, 148), (48, 188), (208, 68), (208, 108), (208, 148), (208, 188),
      (88, 108), (168, 108), (128, 148)]
icon('metabase-logo', B, ['metabase', 'business intelligence', 'analytics', 'dashboards', 'logo', 'brand'],
     dot=[C(x, y, 16) for x, y in MB])


# Tableau: the big centre cross, four medium crosses on the diagonals and four small ones on the axes.
def cross(cx, cy, h):
    return P(f'M{cx - h} {cy} H{cx + h} M{cx} {cy - h} V{cy + h}')


TAB = ([cross(128, 128, 28)] + [cross(128 + dx, 128 + dy, 20) for dx in (-52, 52) for dy in (-52, 52)]
       + [cross(128 + dx, 128 + dy, 14) for dx, dy in ((0, -82), (0, 82), (-82, 0), (82, 0))])
icon('tableau-logo', B, ['tableau', 'analytics', 'business intelligence', 'visualization', 'salesforce', 'logo',
                         'brand'],
     line=TAB, reviewed=True)

# Looker: a big ring with two smaller rings stepping up from it.
icon('looker-logo', B, ['looker', 'google', 'business intelligence', 'analytics', 'logo', 'brand'],
     area=[C(140, 168, 52)], line=[C(140, 168, 52), C(72, 84, 20), C(124, 44, 12)])

# ---------------------------------------------------------------- docs
# GitBook: the book cover tilted flat, with the page block wrapping under it.
GB = PG([(52, 104), (128, 60), (204, 104), (128, 148)])
icon('gitbook-logo', B, ['gitbook', 'documentation', 'docs', 'knowledge base', 'book', 'logo', 'brand'],
     area=[GB], line=[GB, P('M52 104 C46 110 44 118 44 126 C44 134 48 142 56 148 L128 192 L204 148 V136')])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
