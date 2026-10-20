"""Brand logos: media, games, cars and companies; pagination, party horn, file page number."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

BADGE = R(40, 40, 176, 176, 16)
B = 'Brands'

# ------------------------------------------------------------------ media and games

# Netflix: the ribbon N, the diagonal running over both posts.
N = 'M64 224 V32 H104 L152 136 V32 H192 V224 H152 L104 120 V224 Z'
icon('netflix-logo', B, ['netflix', 'streaming', 'video', 'movies', 'tv', 'n', 'logo', 'brand'],
     area=[P(N)], line=[P(N)], detail=[L(64, 32, 104, 120), L(152, 136, 192, 224)])

# YouTube Music: a disc with a ring and a play triangle inside.
icon('youtube-music-logo', B, ['youtube music', 'youtube', 'music', 'streaming', 'audio', 'logo', 'brand'],
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[C(128, 128, 56), P('M116 108 L148 128 L116 148 Z')])

# Xbox: the sphere crossed by the two curved strands of the X.
icon('xbox-logo', B, ['xbox', 'gaming', 'console', 'games', 'microsoft', 'logo', 'brand'],
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[P('M64 64 C112 100 156 152 176 212'), P('M192 64 C144 100 100 152 80 212')])

# Chromecast: the cast mark, a screen with broadcast waves rising from its lower-left corner.
icon('chromecast-logo', B, ['chromecast', 'google', 'cast', 'streaming', 'tv', 'logo', 'brand'],
     line=[P('M32 88 V64 A16 16 0 0 1 48 48 H208 A16 16 0 0 1 224 64 V192 A16 16 0 0 1 208 208 H152'),
           P('M40 160 A40 40 0 0 1 80 200'), P('M40 112 A88 88 0 0 1 128 200')],
     dot=[C(40, 200, 16)],
     area=[P('M32 120 A88 88 0 0 1 120 208 H208 A16 16 0 0 0 224 192 V64 A16 16 0 0 0 208 48 H48 A16 16 0 0 0 32 64 Z')])

# Goodreads: the lowercase g on its app tile.
icon('goodreads-logo', B, ['goodreads', 'books', 'reading', 'reviews', 'g', 'logo', 'brand'],
     area=[BADGE], line=[BADGE],
     detail=[C(124, 112, 32), P('M156 80 V152 C156 180 140 192 120 192 C108 192 98 188 92 180')])

# ------------------------------------------------------------------ companies

# Tesla: the T badge with the arc above it.
T = 'M40 100 C64 92 96 88 128 88 C160 88 192 92 216 100 C196 112 172 116 148 116 L128 224 L108 116 C84 116 60 112 40 100 Z'
icon('tesla-logo', B, ['tesla', 'electric', 'car', 'ev', 'automotive', 't', 'logo', 'brand'],
     area=[P(T)], line=[P(T)], detail=[P('M40 56 C72 44 100 40 128 40 C156 40 184 44 216 56')])

# Yahoo: the Y! on its app tile.
icon('yahoo-logo', B, ['yahoo', 'search', 'mail', 'news', 'web', 'logo', 'brand'],
     area=[BADGE], line=[BADGE],
     detail=[P('M68 80 L104 128 L140 80'), L(104, 128, 104, 176), L(176, 80, 176, 140)],
     dot=[C(176, 176, 16)])

# ------------------------------------------------------------------ cars

# BMW: the roundel, inner disc split into quarters with two quarters filled.
icon('bmw-logo', B, ['bmw', 'car', 'automotive', 'roundel', 'logo', 'brand'],
     line=[C(128, 128, 96), C(128, 128, 56), L(72, 128, 184, 128), L(128, 72, 128, 184)],
     area=[P('M128 128 V72 A56 56 0 0 0 72 128 Z'), P('M128 128 V184 A56 56 0 0 0 184 128 Z')])

# Audi: four interlocking rings.
icon('audi-logo', B, ['audi', 'car', 'automotive', 'rings', 'logo', 'brand'],
     line=[C(62, 128, 30), C(106, 128, 30), C(150, 128, 30), C(194, 128, 30)], outline=True)

# Mercedes-Benz: the three-pointed star in a ring.
STAR = PG([(128, 32), (149, 116), (211, 176), (128, 152), (45, 176), (107, 116)])
icon('mercedes-logo', B, ['mercedes', 'mercedes-benz', 'benz', 'car', 'automotive', 'star', 'logo', 'brand'],
     line=[C(128, 128, 96), STAR], area=[STAR])

# Toyota: three ellipses, a wide ring holding a crossbar and a stem.
icon('toyota-logo', B, ['toyota', 'car', 'automotive', 'ellipses', 'logo', 'brand'],
     area=[E(128, 128, 96, 76)], line=[E(128, 128, 96, 76)],
     detail=[E(128, 104, 60, 28), E(128, 128, 20, 52)])

# Volkswagen: V over W in a circle.
icon('volkswagen-logo', B, ['volkswagen', 'vw', 'car', 'automotive', 'logo', 'brand'],
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[PL([(80, 46), (128, 140), (176, 46)]), PL([(36, 100), (84, 204), (128, 164), (172, 204), (220, 100)])])

# ------------------------------------------------------------------ regular icons

icon('pagination', 'Interface', ['pagination', 'pages', 'paging', 'previous', 'next', 'carousel', 'dots'],
     line=[PL([(56, 104), (32, 128), (56, 152)]), PL([(200, 104), (224, 128), (200, 152)])],
     dot=[C(88, 128, 16), C(128, 128, 16), C(168, 128, 16)])

HORN = 'M44 196 C92 148 108 112 112 72 A72 72 0 0 1 184 144 C144 148 108 164 60 212 Z'
icon('party-horn', 'Objects', ['party horn', 'party blower', 'noisemaker', 'party', 'celebrate', 'birthday', 'new year'],
     area=[P(HORN)], line=[P(HORN), L(52, 204, 36, 220), L(184, 72, 208, 48), L(200, 128, 224, 124), L(128, 56, 132, 32)],
     detail=[L(84, 152, 104, 172)])

fb = load('file')
icon('file-page-number', 'Files', ['file page number', 'page number', 'footer', 'document', 'page', 'file', 'numbering'],
     area=fb['area'], line=fb['line'],
     detail=fb['detail'] + [L(88, 96, 120, 96), P('M116 140 L132 128 V192'), L(80, 160, 96, 160), L(164, 160, 180, 160)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
