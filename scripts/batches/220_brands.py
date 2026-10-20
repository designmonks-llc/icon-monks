"""Brand logos: games, studios and gaming platforms."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
CN = (128, 128)


def brand(name, tags, **roles):
    icon(name + '-logo', B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


# Minecraft: the grass block, with the grass hanging over both side faces in a stepped edge.
CUBE = PG([(128, 32), (212, 80), (212, 176), (128, 224), (44, 176), (44, 80)])
brand('minecraft', ['minecraft', 'mojang', 'game', 'gaming', 'grass block', 'sandbox'],
      area=[CUBE], line=[CUBE],
      detail=[P('M44 80 L128 128 L212 80 M128 128 V224'),
              P('M44 112 L72 128 V148 L100 164 V144 L128 160 L156 144 V164 L184 148 V128 L212 112')])

# Valorant: the V split into a long left blade and a small right wedge.
V_L = PG([(32, 48), (32, 124), (92, 208), (156, 208)])
V_R = PG([(224, 48), (224, 128), (204, 152), (144, 152)])
brand('valorant', ['valorant', 'riot games', 'game', 'gaming', 'shooter', 'v'],
      area=[V_L, V_R], line=[V_L, V_R])

# EA: the slanted E and the open A of Electronic Arts.
icon('ea-logo', B, ['ea', 'electronic arts', 'game', 'gaming', 'publisher', 'logo', 'brand'], outline=True,
     line=[PL([(124, 80), (64, 80), (40, 176), (100, 176)]), L(52, 128, 104, 128),
           PL([(124, 176), (176, 80), (224, 176)]), L(140, 148, 208, 148)])

# Ubisoft: the swirl, a spiral of half-turns closing in on the centre dot, opening at the top left.
SPIRAL = rot([(128, 32), (128, 224), (128, 64), (128, 192), (128, 96)], -40)
SPIRAL = [ipt(p) for p in SPIRAL]
brand('ubisoft', ['ubisoft', 'game', 'gaming', 'publisher', 'swirl'],
      area=[P(f'M{pt(SPIRAL[0])} A96 96 0 0 1 {pt(SPIRAL[1])} A80 80 0 0 1 {pt(SPIRAL[2])} Z')],
      line=[P(f'M{pt(SPIRAL[0])} A96 96 0 0 1 {pt(SPIRAL[1])} A80 80 0 0 1 {pt(SPIRAL[2])}')],
      detail=[P(f'M{pt(SPIRAL[2])} A64 64 0 0 1 {pt(SPIRAL[3])} A48 48 0 0 1 {pt(SPIRAL[4])}')],
      dotcut=[C(128, 136, 14)])


# Rockstar Games: the slanted R with the star at its foot, on the rounded tile.
STAR = PG([ipt(polar((168, 164), 32 if i % 2 == 0 else 13, -90 + i * 36)) for i in range(10)])
brand('rockstar-games', ['rockstar games', 'rockstar', 'gta', 'game', 'gaming', 'publisher', 'r', 'star'],
      area=[SQ], line=[SQ],
      detail=[P('M64 168 L80 64 H128 A26 26 0 0 1 128 116 H72'), L(112, 116, 116, 168), STAR])

# itch.io: the shop front with its scalloped awning and a game controller in the window.
SHOP = ('M60 40 H196 L224 72 V88 C224 98 218 106 212 110 V216 Q212 224 204 224 H52 Q44 224 44 216 V110 '
        'C38 106 32 98 32 88 V72 Z')
PAD = ('M92 140 H164 C176 140 180 152 182 164 L186 184 C188 196 180 200 172 200 C162 200 156 194 156 186 '
       'H100 C100 194 94 200 84 200 C76 200 68 196 70 184 L74 164 C76 152 80 140 92 140 Z')
brand('itch-io', ['itch.io', 'itch', 'indie games', 'game store', 'gaming', 'controller'],
      area=[P(SHOP)], line=[P(SHOP)],
      detail=[P('M32 88 A24 24 0 0 0 80 88 A24 24 0 0 0 128 88 A24 24 0 0 0 176 88 A24 24 0 0 0 224 88'),
              P(PAD)])

# Kick: the blocky pixel K.
KICK = ('M48 48 H80 V112 H112 V80 H144 V48 H208 V80 H176 V112 H144 V144 H176 V176 H208 V208 H144 V176 '
        'H112 V144 H80 V208 H48 Z')
brand('kick', ['kick', 'streaming', 'live stream', 'gaming', 'k'],
      area=[P(KICK)], line=[P(KICK)])

# Among Us: the crewmate in profile, with its visor and backpack.
BODY = 'M80 216 V100 C80 60 104 36 136 36 C168 36 192 60 192 100 V216 H152 V188 H120 V216 Z'
PACK = 'M80 100 H60 Q44 100 44 116 V172 Q44 188 60 188 H80'
VISOR = capsule((164, 92), 28, 24, (1, 0))
brand('among-us', ['among us', 'crewmate', 'impostor', 'game', 'gaming', 'innersloth'],
      area=[P(BODY), P(PACK + ' Z')], line=[P(BODY), P(PACK)], detail=[P(VISOR)])

# Overwatch: the ring broken at the top, the loose top arc, and the two shards meeting in the middle.
def ring_arc(a0, a1, large):
    return P(f'M{pt(ipt(polar(CN, 96, a0)))} A96 96 0 {large} 1 {pt(ipt(polar(CN, 96, a1)))}')


brand('overwatch', ['overwatch', 'blizzard', 'game', 'gaming', 'shooter', 'hero shooter'],
      area=[C(128, 128, 96)],
      line=[ring_arc(-40, -140, 1), ring_arc(-126, -54, 0)],
      detail=[PL([(116, 80), (116, 148), (60, 196)]), PL([(140, 80), (140, 148), (196, 196)])])

# Dota 2: the red tile crossed by the wide diagonal band, with a wedge in two corners.
brand('dota', ['dota', 'dota 2', 'valve', 'moba', 'game', 'gaming'],
      area=[SQ], line=[SQ],
      detail=[PG([(64, 96), (96, 64), (192, 160), (160, 192)]),
              PG([(152, 64), (192, 64), (192, 104)]), PG([(64, 152), (64, 192), (104, 192)])])

# World of Warcraft: the W on the round medallion, with the square plate's corners behind it.
WOW = ('M176 64 H192 V80 A80 80 0 0 1 192 176 V192 H176 A80 80 0 0 1 80 192 H64 V176 '
       'A80 80 0 0 1 64 80 V64 H80 A80 80 0 0 1 176 64 Z')
brand('world-of-warcraft', ['world of warcraft', 'warcraft', 'wow', 'blizzard', 'mmo', 'game', 'gaming'],
      area=[P(WOW)], line=[P(WOW)],
      detail=[PL([(84, 92), (106, 168), (128, 112), (150, 168), (172, 92)])])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
