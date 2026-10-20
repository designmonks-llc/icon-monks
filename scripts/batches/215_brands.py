"""Brand logos: creative apps, music, streaming and games."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
fix_d = __import__('198_extremes').fix_d

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)      # Adobe-style product tile
APP = R(40, 40, 176, 176, 40)     # Apple-style app tile
RING = C(128, 128, 96)
O = (128, 128)


def brand(name, tags, **roles):
    """Register a logo; every curve gets anchors on its extremes (198_extremes.fix_d)."""
    import re
    anchor = lambda e: re.sub(r' d="([^"]*)"', lambda m: f' d="{fix_d(m.group(1))}"', e) if isinstance(e, str) else e
    for k, v in roles.items():
        if isinstance(v, list):
            roles[k] = [anchor(e) for e in v]
    icon(name, B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


def line_circle(a, b, c, r):
    """Intersections of the infinite line a-b with circle (c, r), ordered along a -> b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy
    Bq = 2 * (fx * dx + fy * dy)
    Cq = fx * fx + fy * fy - r * r
    disc = math.sqrt(max(Bq * Bq - 4 * A * Cq, 0))
    ts = sorted([(-Bq - disc) / (2 * A), (-Bq + disc) / (2 * A)])
    return [(a[0] + t * dx, a[1] + t * dy) for t in ts]


def drop(tip, c, r):
    """Closed teardrop: round end (c, r), pointed at tip."""
    d = dist(tip, c)
    a = math.atan2(tip[1] - c[1], tip[0] - c[0])
    off = math.acos(r / d)
    p1 = ipt((c[0] + r * math.cos(a + off), c[1] + r * math.sin(a + off)))
    p2 = ipt((c[0] + r * math.cos(a - off), c[1] + r * math.sin(a - off)))
    far = lambda m: dist(m, tip)
    return f'M{pt(ipt(tip))} L{pt(p1)} ' + arc_to(c, r, p1, p2, far) + ' Z'


# ---------------------------------------------------------------- Adobe
# Adobe: the A of two outer wedges and the small centre piece with its notch.
AD = [PG([(32, 48), (104, 48), (32, 208)]), PG([(152, 48), (224, 48), (224, 208)]),
      PG([(128, 108), (176, 208), (140, 208), (124, 172), (96, 172)])]
brand('adobe-logo', ['adobe', 'creative cloud', 'software', 'design'], area=AD, line=AD)

# Acrobat: the looped ribbon triangle on the product tile.
brand('adobe-acrobat-logo', ['adobe acrobat', 'acrobat', 'adobe', 'pdf', 'documents', 'reader'],
      area=[SQ], line=[SQ],
      detail=[P('M100 166 C132 152 164 148 190 154 C210 160 204 184 186 174 C160 160 140 130 126 96 '
                'C118 76 120 64 128 64 C136 64 140 76 132 96 C120 126 100 162 80 182 '
                'C66 196 56 186 68 176 C76 170 88 168 100 166 Z')])

# Lightroom: the lettered tile, as the other Adobe app logos.
brand('adobe-lightroom-logo', ['adobe lightroom', 'lightroom', 'adobe', 'lr', 'photo editing', 'photography'],
      area=[SQ], line=[SQ],
      detail=[P('M76 88 V172 H116'), P('M148 172 V124'), P('M148 144 C148 128 160 120 180 120')])

# ---------------------------------------------------------------- creative apps
# Procreate: the tapering brush swoosh on the app tile.
SW = 'M76 188 C72 124 116 76 188 64 C180 124 140 168 76 188 Z'
brand('procreate-logo', ['procreate', 'drawing', 'painting', 'illustration', 'ipad'],
      area=[APP], line=[APP], detail=[P(SW)])

# DaVinci Resolve: three teardrops pointing to the centre, in a ring.
DO = (128, 132)
drops = []
for k in range(3):
    c = ipt(rot([(128, 88)], 120 * k, DO)[0])
    t = ipt(rot([(128, 110)], 120 * k, DO)[0])
    drops.append(P(drop(t, c, 18)))
brand('davinci-resolve-logo', ['davinci resolve', 'blackmagic', 'video editing', 'color grading', 'film'],
      area=[RING], line=[RING], detail=drops)

# Final Cut Pro: the clapperboard on the app tile.
brand('final-cut-logo', ['final cut pro', 'final cut', 'apple', 'video editing', 'film'],
      area=[APP], line=[APP],
      detail=[R(72, 120, 112, 64, 16), P('M80 120 V104 C80 96 86 90 94 88 L184 68')])

# OBS Studio: three curved blades swirling round the centre, in a ring.
blades = []
for k in range(3):
    p1, p2 = [ipt(p) for p in rot([(96, 56), (152, 124)], 120 * k)]
    blades.append(P(f'M{pt(p1)} A48 48 0 0 0 {pt(p2)}'))
brand('obs-logo', ['obs', 'obs studio', 'streaming', 'recording', 'broadcast'],
      area=[RING], line=[RING], detail=blades)

# VLC: the round-tipped cone with two curved stripes on its tray.
CONE = 'M116 48 C120 40 136 40 140 48 L176 176 H80 Z'
TRAY = 'M80 176 H176 L208 196 C216 202 212 212 202 212 H54 C44 212 40 202 48 196 Z'
brand('vlc-logo', ['vlc', 'videolan', 'media player', 'video', 'cone'],
      area=[P(CONE), P(TRAY)], line=[P(CONE), P(TRAY)],
      detail=[P('M103 96 C120 104 136 104 153 96'), P('M91 136 C114 146 142 146 165 136')])

# Audacity: headphones around a waveform.
brand('audacity-logo', ['audacity', 'audio editing', 'recording', 'sound', 'waveform'],
      area=[R(36, 136, 36, 72, 16), R(184, 136, 36, 72, 16)],
      line=[P('M54 136 V128 A74 74 0 0 1 202 128 V136'), R(36, 136, 36, 72, 16), R(184, 136, 36, 72, 16)],
      detail=[PL([(92, 172), (102, 148), (114, 196), (128, 120), (142, 196), (154, 148), (164, 172)])])

# Ableton: four bars and four lines.
brand('ableton-logo', ['ableton', 'ableton live', 'music production', 'daw', 'audio'],
      line=[L(x, 72, x, 184) for x in (40, 68, 96, 124)] + [L(152, y, 216, y) for y in (72, 108, 148, 184)])

# ---------------------------------------------------------------- music
# Deezer: rounded bars rising and falling in the shape of a heart.
brand('deezer-logo', ['deezer', 'music', 'streaming', 'audio'],
      line=[L(48, 84, 48, 140), L(88, 48, 88, 176), L(128, 96, 128, 212), L(168, 48, 168, 176),
            L(208, 84, 208, 140)])

# Tidal: four diamonds, three across and one below the middle.
DIA = [PG([(cx, cy - 32), (cx + 32, cy), (cx, cy + 32), (cx - 32, cy)])
       for cx, cy in ((64, 96), (128, 96), (192, 96), (128, 160))]
brand('tidal-logo', ['tidal', 'music', 'streaming', 'hifi', 'audio'], area=DIA, line=DIA)

# Shazam: two interlocking hooks forming an S, in a ring.
def sz(u, v):
    s = math.sqrt(0.5)
    return ipt((128 + (u + v) * s, 128 + (-u + v) * s))

hooks = []
for sgn in (1, -1):
    a = sz(sgn * 52, -sgn * 36)
    b = sz(-sgn * 18, -sgn * 36)
    e = sz(-sgn * 18, 0)
    hooks.append(P(f'M{pt(a)} L{pt(b)} A18 18 0 0 0 {pt(e)}'))
brand('shazam-logo', ['shazam', 'apple', 'music recognition', 'music', 'song'],
      area=[RING], line=[RING], detail=hooks)

# ---------------------------------------------------------------- Apple
def scale_path(d, s, tx, ty):
    """Scale and move a path of M/L/C/Z commands (absolute x, y pairs), rounding to whole units."""
    import re
    res, xy = [], 0
    for tok in re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d):
        if tok.isalpha():
            res.append(tok); xy = 0
        else:
            res.append(str(round(float(tok) * s + (tx if xy == 0 else ty)))); xy ^= 1
    return ' '.join(res)


APPLE = ('M128 88 C116 82 104 78 90 78 C64 78 48 104 48 136 C48 172 68 224 90 224 '
         'C104 224 114 216 128 216 C142 216 152 224 166 224 C182 224 200 196 208 172 '
         'C188 162 178 152 178 136 C178 120 188 106 202 98 C190 84 176 78 162 78 '
         'C150 78 140 82 128 88 Z')
LEAF = 'M124 64 C124 46 142 32 164 32 C164 50 146 64 124 64 Z'
sa, sl = P(scale_path(APPLE, 0.5, 8, 72)), P(scale_path(LEAF, 0.5, 8, 72))
brand('apple-tv-logo', ['apple tv', 'apple', 'tv', 'streaming', 'video'],
      area=[sa, sl],
      line=[sa, sl, P('M140 80 V164 C140 176 148 184 164 180'), L(124, 108, 160, 108), PL([(172, 108), (196, 180), (220, 108)])])

# Apple Podcasts: the broadcasting figure, open rings over a head and body, on the app tile.
def open_arc(c, r, half):
    p1 = ipt(polar(c, r, 90 + half)); p2 = ipt(polar(c, r, 90 - half))
    return P(f'M{pt(p1)} A{r} {r} 0 1 1 {pt(p2)}')

brand('apple-podcasts-logo', ['apple podcasts', 'podcasts', 'apple', 'podcast', 'audio'],
      area=[APP], line=[APP],
      detail=[open_arc((128, 124), 56, 40), open_arc((128, 124), 32, 45), L(128, 160, 128, 188)],
      dot=[C(128, 124, 16)])

# ---------------------------------------------------------------- streaming
# YouTube Shorts: two tilted pills, offset into the S-shaped tile, with the play triangle.
u = (math.cos(math.radians(-30)), math.sin(math.radians(-30)))
n_ = (-u[1], u[0])  # points down-right of the axis
RS = 40
L1, R1 = (88, 116), (164, 72)
L2, R2 = (92, 184), (168, 140)
top1 = ((L1[0] - n_[0] * RS, L1[1] - n_[1] * RS), (R1[0] - n_[0] * RS, R1[1] - n_[1] * RS))
bot1 = ((L1[0] + n_[0] * RS, L1[1] + n_[1] * RS), (R1[0] + n_[0] * RS, R1[1] + n_[1] * RS))
top2 = ((L2[0] - n_[0] * RS, L2[1] - n_[1] * RS), (R2[0] - n_[0] * RS, R2[1] - n_[1] * RS))
bot2 = ((L2[0] + n_[0] * RS, L2[1] + n_[1] * RS), (R2[0] + n_[0] * RS, R2[1] + n_[1] * RS))
x_r = ipt(line_circle(top2[0], top2[1], R1, RS)[1])   # right notch: pill 1 cap meets pill 2 top edge
x_l = ipt(line_circle(bot1[0], bot1[1], L2, RS)[0])   # left notch: pill 2 cap meets pill 1 bottom edge
pa, pb = ipt(top1[0]), ipt(top1[1])
pc, pd = ipt(bot2[1]), ipt(bot2[0])
SH = (f'M{pt(pa)} L{pt(pb)} ' + arc_to(R1, RS, pb, x_r, lambda m: dist(m, L1)) +
      f' L{pt(ipt(top2[1]))} ' + arc_to(R2, RS, ipt(top2[1]), pc, lambda m: dist(m, L2)) +
      f' L{pt(pd)} ' + arc_to(L2, RS, pd, x_l, lambda m: dist(m, R2)) +
      f' L{pt(ipt(bot1[0]))} ' + arc_to(L1, RS, ipt(bot1[0]), pa, lambda m: dist(m, R1)) + ' Z')
brand('youtube-shorts-logo', ['youtube shorts', 'shorts', 'youtube', 'short video', 'video'],
      area=[P(SH)], line=[P(SH)], detail=[P('M112 104 L148 128 L112 152 Z')])

# HBO: the letters with the dot inside the O.
brand('hbo-max-logo', ['hbo max', 'hbo', 'max', 'streaming', 'tv'],
      line=[L(32, 92, 32, 164), L(64, 92, 64, 164), L(32, 128, 64, 128),
            P('M88 128 H108 A18 18 0 0 1 108 164 H88 V92 H104 A18 18 0 0 1 104 128'), C(188, 128, 36)],
      dotcut=[C(188, 128, 14)], outline=True)

# Paramount+: the mountain under an arch of stars.
MT = PG([(48, 200), (104, 128), (128, 104), (156, 132), (208, 200)])
stars = [ipt(polar((128, 152), 88, 180 + 30 * k)) for k in range(7)]
brand('paramount-plus-logo', ['paramount plus', 'paramount', 'streaming', 'movies', 'mountain'],
      area=[MT], line=[MT], dot=[C(x, y, 16) for x, y in stars], reviewed=True)

# Crunchyroll: the disc with a bite out of its upper right, inside the round badge.
DC, DR = (136, 140), 60
BC, BR = (178, 100), 28
b1, b2 = [ipt(p) for p in circle_x(DC, DR, BC, BR)]
DISC = (f'M{pt(b1)} ' + arc_to(DC, DR, b1, b2, lambda m: dist(m, BC)) + ' ' +
        arc_to(BC, BR, b2, b1, lambda m: -dist(m, DC)) + ' Z')
brand('crunchyroll-logo', ['crunchyroll', 'anime', 'streaming', 'video'],
      area=[RING], line=[RING], detail=[P(DISC)])

# ---------------------------------------------------------------- 3D, motion and games
# Rive: the stemless R, a bar curling into the bowl with its leg.
brand('rive-logo', ['rive', 'animation', 'interactive', 'motion design'],
      line=[P('M40 52 H150 A42 42 0 0 1 150 136 H96'), L(140, 136, 204, 212)], outline=True)

# Cinema 4D: the sphere in its orbit, in the hexagon badge.
HEX = [ipt(p) for p in regular_polygon(O, 96, 6)]
orb1, orb2 = ipt(polar(O, 52, -70)), ipt(polar(O, 52, -10))
brand('cinema-4d-logo', ['cinema 4d', 'maxon', '3d', 'modeling', 'motion graphics'],
      area=[PG(HEX)], line=[PG(HEX)],
      detail=[P(f'M{pt(orb1)} A52 52 0 1 0 {pt(orb2)}'), C(124, 132, 20)])

# Maya: the lettered tile with its folded left edge.
FLAP = [(80, 40), (40, 64), (40, 208), (80, 184)]
FACE = R(80, 40, 144, 152, 8)
brand('maya-logo', ['autodesk maya', 'maya', 'autodesk', '3d', 'animation', 'modeling'],
      area=[FACE, PG(FLAP)], line=[FACE, PL(FLAP)],
      detail=[PL([(112, 152), (112, 76), (152, 132), (192, 76), (192, 152)])])

# Unity: the cube, its outline broken at three corners, with the inner edges.
brand('unity-logo', ['unity', 'game engine', 'games', 'game development', '3d'],
      line=[PL([(120, 37), (45, 80), (45, 160)]), PL([(136, 37), (211, 80), (211, 160)]),
            PL([(52, 184), (128, 224), (204, 184)]),
            PL([(90, 86), (128, 108), (166, 86)]), PL([(74, 116), (112, 138), (112, 180)]),
              PL([(182, 116), (144, 138), (144, 180)])])

# Unreal Engine: the gothic U with its flag and spur, in a ring.
brand('unreal-engine-logo', ['unreal engine', 'unreal', 'epic games', 'game engine', 'games'],
      area=[RING], line=[RING],
      detail=[P('M80 120 L104 96 V148 A28 28 0 0 0 160 148 V76 L140 96'), L(160, 168, 176, 180)])

# Godot: the robot head with ears, round eyes and a notched mouth.
HEAD = ('M44 112 C44 96 48 84 56 76 L52 60 C60 52 72 48 80 52 L88 64 C100 60 112 58 116 58 L120 44 '
        'C124 40 132 40 136 44 L140 58 C144 58 156 60 168 64 L176 52 C184 48 196 52 204 60 L200 76 '
        'C208 84 212 96 212 112 V180 C212 192 204 200 192 200 H64 C52 200 44 192 44 180 Z')
brand('godot-logo', ['godot', 'game engine', 'games', 'game development', 'open source'],
      area=[P(HEAD)], line=[P(HEAD)],
      detail=[C(88, 116, 24), C(168, 116, 24), P('M64 164 H88 V176 H116 V164 H140 V176 H168 V164 H192')],
      dotcut=[C(92, 118, 14), C(164, 118, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
