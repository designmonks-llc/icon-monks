import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

S = 'Sports'


def xf(d, deg=0, O=(0, 0), s=1.0):
    """Transform an absolute path (M L H V C Q A Z) from local coords: scale s, rotate deg, then move to O."""
    toks = re.findall(r'[MLHVCQAZ]|-?\d*\.?\d+', d)
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)

    def m(x, y):
        x, y = x * s, y * s
        return (O[0] + x * ca - y * sa, O[1] + x * sa + y * ca)
    out = []
    i = 0
    cur = (0, 0)
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCQAZ':
            cmd = t
            i += 1
            if t == 'Z':
                out.append('Z')
                continue
        if cmd in 'ML':
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            cur = (x, y); out.append(f'{cmd}{pt(m(x, y))}')
        elif cmd == 'H':
            x = float(toks[i]); i += 1
            cur = (x, cur[1]); out.append(f'L{pt(m(*cur))}')
        elif cmd == 'V':
            y = float(toks[i]); i += 1
            cur = (cur[0], y); out.append(f'L{pt(m(*cur))}')
        elif cmd == 'C':
            v = [float(x) for x in toks[i:i + 6]]; i += 6
            cur = (v[4], v[5])
            out.append('C' + ' '.join(pt(m(v[j], v[j + 1])) for j in (0, 2, 4)))
        elif cmd == 'Q':
            v = [float(x) for x in toks[i:i + 4]]; i += 4
            cur = (v[2], v[3])
            out.append('Q' + ' '.join(pt(m(v[j], v[j + 1])) for j in (0, 2)))
        elif cmd == 'A':
            v = [float(x) for x in toks[i:i + 7]]; i += 7
            cur = (v[5], v[6])
            out.append(f'A{f(v[0] * s)} {f(v[1] * s)} {f(v[2] + (deg if v[0] != v[1] else 0))} {int(v[3])} {int(v[4])} {pt(m(v[5], v[6]))}')
    return ' '.join(out)


def mp(points, deg=0, O=(0, 0), s=1.0):
    a = math.radians(deg)
    return [(O[0] + (x * math.cos(a) - y * math.sin(a)) * s, O[1] + (x * math.sin(a) + y * math.cos(a)) * s)
            for x, y in points]


SLASH = L(48, 48, 208, 208)


def solid(x, y, sz=16):
    # a square that stays solid at every weight: outline plus both diagonals
    return P(f'M{f(x)} {f(y)} H{f(x + sz)} V{f(y + sz)} H{f(x)} Z M{f(x)} {f(y)} L{f(x + sz)} {f(y + sz)} '
             f'M{f(x + sz)} {f(y)} L{f(x)} {f(y + sz)}')

# ---------------------------------------------------------------- figures
def figure(fig, deg, O, s=1.0, hr=20):
    q = lambda p: mp([p], deg, O, s)[0]
    hd = q(fig['head'])
    return [C(hd[0], hd[1], hr), PL([q(fig['hands'][0]), q(fig['S']), q(fig['hands'][1])]),
            PL([q(fig['S']), q(fig['H'])]), PL([q(fig['feet'][0]), q(fig['H']), q(fig['feet'][1])])], hd

# acrobatic: circus acrobat balancing on a ball, arms out
icon('acrobatic', S, ['acrobat', 'gymnastics', 'circus', 'person'],
     line=[C(128, 50, 18), PL([(60, 68), (128, 92), (196, 68)]), L(128, 84, 128, 116),
           PL([(106, 154), (128, 116), (150, 154)]), C(128, 190, 34)],
     area=[C(128, 50, 18), C(128, 190, 34)])

# gymnastics: straddle handstand, head between the arms
hs_fig = dict(head=(0, -82), S=(0, -36), H=(0, 22), hands=[(-74, -96), (74, -96)], feet=[(-62, 88), (62, 88)])
gym, hd2 = figure(hs_fig, 180, (128, 120), 1.0, 16)
icon('gymnastics', S, ['gymnastics', 'acrobat', 'flip', 'athlete', 'sport'], line=gym,
     area=[C(hd2[0], hd2[1], 16)])

# handball: figure throwing a ball overhead
icon('handball', S, ['handball', 'ball', 'team sport', 'throw'],
     line=[C(96, 64, 20), PL([(60, 140), (108, 108), (156, 72)]), L(108, 108, 116, 152),
           PL([(72, 216), (116, 152), (152, 180), (164, 216)]), C(186, 54, 22)],
     area=[C(96, 64, 20), C(186, 54, 22)])

# cliff-jumping: swan dive off a cliff edge above water
cliff = 'M32 112 H92 L112 224'
jump_fig = dict(head=(0, -84), S=(0, -36), H=(0, 22), hands=[(-62, -86), (62, -86)], feet=[(-34, 92), (34, 92)])
diver, dhead = figure(jump_fig, 10, (166, 108), 0.7, 15)
icon('cliff-jumping', S, ['cliff', 'jump', 'diving', 'extreme'],
     line=[P(cliff)] + diver + [
           P("M144 208 Q160 196 176 208 T208 208")],
     area=[P(cliff + ' H32 Z'), C(*dhead, 15)])

# ---------------------------------------------------------------- archery
tc = (112, 144)
u = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
tail = (tc[0] + u[0] * 116, tc[1] + u[1] * 116)
edge = (tc[0] + u[0] * 80, tc[1] + u[1] * 80)
icon('archery', S, ['bow and arrow', 'target', 'sport', 'archery', 'arrow'],
     line=[C(*tc, 80), L(*edge, *tail), PL([(tail[0], tail[1] - 24), tail, (tail[0] + 24, tail[1])])],
     detail=[C(*tc, 40), L(*tc, *edge)],
     area=[C(*tc, 80)])

# bow with an arrow nocked (local: arrow points +x), rotated to point up-right
bow_r = (92 ** 2 + 40 ** 2) / 80
bow_local = [f'M0 -92 A{bow_r} {bow_r} 0 0 1 0 92 L-40 0 Z', 'M-40 0 L96 0', 'M68 -28 L96 0 L68 28']
icon('bow', S, ['bow', 'archery', 'arrow', 'hunting', 'target'],
     line=[P(xf(d, -45, (124, 132))) for d in bow_local])

# ---------------------------------------------------------------- arm flex
arm = ('M40 136 C56 104 96 92 120 104 C140 114 152 132 156 148 L148 104 C124 100 120 64 140 48 '
       'C160 32 200 36 212 60 C220 76 216 92 208 100 L216 172 C220 200 204 216 176 216 H40')
icon('arm-flex', S, ['muscle', 'strong', 'flex', 'bicep'],
     line=[P(arm), L(40, 136, 40, 216)], detail=[P('M156 148 C148 160 136 168 120 168')], area=[P(arm + ' Z')])

# ---------------------------------------------------------------- racket sports
head_pts = 'M0 -60 A44 60 0 0 1 0 60 A44 60 0 0 1 0 -60 Z'
icon('badminton', S, ['badminton', 'shuttlecock', 'racket', 'sport'],
     line=[P(xf(head_pts, -45, (118, 88))), L(160, 130, 212, 182),
           PG([(56, 198), (36, 150), (96, 150), (76, 198)]), L(66, 150, 66, 198)],
     dot=[C(66, 210, 16)],
     area=[P(xf(head_pts, -45, (118, 88))), PG([(56, 198), (36, 150), (96, 150), (76, 198)])])

# ---------------------------------------------------------------- barbell slash
bb = load('barbell')
icon('barbell-slash', S, ['barbell', 'disabled', 'off', 'sports'], line=bb['line'] + [SLASH])

# ---------------------------------------------------------------- baseball
bc = (128, 128)
lA, lB = polar(bc, 96, 225), polar(bc, 96, 135)
rA, rB = polar(bc, 96, -45), polar(bc, 96, 45)
seams = [P(f'M{pt(lA)} A112 112 0 0 1 {pt(lB)}'), P(f'M{pt(rA)} A112 112 0 0 0 {pt(rB)}')]
sc = (60.12 - math.sqrt(112 ** 2 - 67.88 ** 2), 128)
for a in (-22, 0, 22):
    for side in (1, -1):
        p1, p2 = polar(sc, 104, a), polar(sc, 120, a)
        if side < 0:
            p1, p2 = (256 - p1[0], p1[1]), (256 - p2[0], p2[1])
        seams.append(L(*p1, *p2))
icon('baseball', S, ['ball', 'baseball', 'sport', 'stitches', 'bat'],
     line=[C(128, 128, 96)], detail=seams, area=[C(128, 128, 96)])

bat_local = 'M20 -8 L60 -8 C100 -8 120 -22 160 -24 L188 -24 A24 24 0 0 1 188 24 L160 24 C120 22 100 8 60 8 L20 8 Z'
bat = xf(bat_local, -45, (46, 210))
knob = mp([(8, -20), (8, 20)], -45, (46, 210))
icon('baseball-bat', S, ['baseball', 'bat', 'sports', 'softball'],
     line=[P(bat), PL(knob)], area=[P(bat)])

cap = 'M40 168 C40 108 72 68 116 68 C160 68 186 100 188 152 H212 A12 12 0 0 1 224 164 V168 A12 12 0 0 1 212 180 H52 A12 12 0 0 1 40 168 Z'
icon('baseball-cap', 'Objects', ['cap', 'hat', 'baseball cap', 'clothing'],
     line=[P(cap)], detail=[P('M116 72 C104 96 100 120 102 148')], dot=[C(116, 60, 10)],
     area=[P(cap)])

helmet = ('M60 196 C44 176 40 152 40 132 C40 84 80 52 132 52 C180 52 208 84 210 124 L224 136 L176 140 L172 180 '
          'C170 192 160 200 148 200 H72 C66 200 62 198 60 196 Z')
icon('baseball-helmet', S, ['baseball', 'batting helmet', 'sport'],
     line=[P(helmet)], detail=[C(116, 148, 16)], area=[P(helmet)])

# ---------------------------------------------------------------- basketball hoop
icon('basketball-hoop', S, ['hoop', 'net', 'basket', 'sport', 'backboard'],
     line=[R(40, 32, 176, 96, 14), L(80, 144, 176, 144), PL([(88, 144), (104, 216)]), PL([(168, 144), (152, 216)]),
           L(104, 216, 152, 216), L(96, 148, 152, 212), L(160, 148, 104, 212)],
     detail=[R(100, 64, 56, 36, 6)],
     area=[R(40, 32, 176, 96, 14)])

# ---------------------------------------------------------------- billiard
icon('billiard-ball', S, ['billiards', 'pool', 'eight ball', 'snooker', '8 ball'],
     line=[C(128, 128, 96)], detail=[C(128, 128, 58), C(128, 113, 12), C(128, 142, 15)], area=[C(128, 128, 96)])

# ---------------------------------------------------------------- boules
balls = [(72, 172), (184, 172), (128, 79)]
icon('boules', S, ['petanque', 'bocce', 'balls'],
     line=[C(x, y, 40) for x, y in balls], area=[C(x, y, 40) for x, y in balls])

# ---------------------------------------------------------------- bowling
pin = ('M184 36 C196 36 202 46 202 58 C202 74 194 82 194 96 C194 116 214 132 214 160 C214 184 204 200 202 216 '
       'H166 C164 200 154 184 154 160 C154 132 174 116 174 96 C174 82 166 74 166 58 C166 46 172 36 184 36 Z')
icon('bowling', S, ['bowling', 'pins', 'ball', 'strike', 'sport'],
     line=[P(pin), C(80, 168, 48)], area=[P(pin), C(80, 168, 48)],
     dotcut=[C(68, 154, 10), C(94, 148, 10), C(84, 178, 10)])

# ---------------------------------------------------------------- boxing glove
glove = ('M88 176 C64 168 56 144 56 120 V88 C56 52 84 32 124 32 H144 C184 32 208 60 208 100 V128 '
         'C208 152 196 168 180 176 Z')
icon('boxing-glove', S, ['boxing', 'mma', 'fight', 'martial arts', 'glove'],
     line=[P(glove), R(84, 176, 100, 40, 10)], detail=[P('M56 112 C84 112 104 124 112 148')],
     area=[P(glove), R(84, 176, 100, 40, 10)])

# ---------------------------------------------------------------- chess
BASE = L(56, 216, 200, 216)
body = 'M84 184 C96 164 106 150 108 136 H148 C150 150 160 164 172 184 Z'
pawn_body = 'M84 184 C92 160 108 140 112 120 H144 C148 140 164 160 172 184 Z'
icon('chess-pawn', S, ['pawn', 'chess', 'game', 'piece', 'strategy'],
     line=[C(128, 80, 28), P(pawn_body), BASE], area=[C(128, 80, 28), P(pawn_body)])
rook = 'M84 184 L100 112 L64 96 V40 H86 V68 H116 V40 H140 V68 H170 V40 H192 V96 L156 112 L172 184 Z'
icon('chess-rook', S, ['chess', 'rook', 'castle piece', 'castle', 'piece'],
     line=[P(rook), BASE], area=[P(rook)])
bishop = 'M128 52 C152 64 164 88 164 104 C164 120 150 132 128 132 C106 132 92 120 92 104 C92 84 108 64 128 52 Z'
icon('chess-bishop', S, ['chess', 'bishop', 'strategy', 'game', 'piece'],
     line=[P(bishop), P(body), BASE], detail=[L(124, 108, 144, 84)], dot=[C(128, 34, 12)],
     area=[P(bishop), P(body)])
king = 'M100 136 L84 92 Q82 84 90 84 H166 Q174 84 172 92 L156 136 Z'
icon('chess-king', S, ['king', 'chess', 'game', 'piece', 'chess king'],
     line=[P(king), P(body), BASE, L(128, 32, 128, 84), L(108, 52, 148, 52)], area=[P(king), P(body)])
queen = 'M100 136 L80 72 L108 100 L128 60 L148 100 L176 72 L156 136 Z'
icon('chess-queen', S, ['queen', 'chess', 'game', 'piece', 'chess queen'],
     line=[P(queen), P(body), BASE], dot=[C(80, 56, 12), C(128, 42, 12), C(176, 56, 12)],
     area=[P(queen), P(body)])

# ---------------------------------------------------------------- cleats
shoe = 'M48 80 H92 C104 108 128 120 160 124 C196 128 216 140 216 160 V168 A8 8 0 0 1 208 176 H48 A8 8 0 0 1 40 168 V88 A8 8 0 0 1 48 80 Z'
icon('cleats', S, ['football boots', 'soccer shoes', 'cleats', 'studs'],
     line=[P(shoe), L(72, 184, 72, 204), L(128, 184, 128, 204), L(184, 184, 184, 204)],
     detail=[L(68, 148, 168, 148)], area=[P(shoe)])

# ---------------------------------------------------------------- club suit
cT, cL, cR, cr = (128, 80), (84, 148), (172, 148), 42
far = lambda pts: max(pts, key=lambda p: dist(p, (128, 128)))
pTL = far(circle_x(cT, cr, cL, cr)); pTR = far(circle_x(cT, cr, cR, cr))
pL = polar(cL, cr, 20); pR = polar(cR, cr, 160)
awayc = lambda m: dist(m, (128, 128))
club = (f'M{pt(pTL)} ' + arc_to(cL, cr, pTL, pL, awayc) + f' Q124 196 96 212 H160 Q132 196 {pt(pR)} '
        + arc_to(cR, cr, pR, pTR, awayc) + ' ' + arc_to(cT, cr, pTR, pTL, awayc) + ' Z')
icon('club', S, ['club', 'cards', 'suit', 'poker'], line=[P(club)], area=[P(club)])

# ---------------------------------------------------------------- court
icon('court-basketball', S, ['basketball court', 'sports field', 'arena'],
     line=[R(32, 56, 192, 144, 12)],
     detail=[L(128, 56, 128, 200), C(128, 128, 20), P('M32 88 A40 40 0 0 1 32 168'), P('M224 88 A40 40 0 0 0 224 168')],
     area=[R(32, 56, 192, 144, 12)])

# ---------------------------------------------------------------- cricket
blade = xf('M60 -22 H190 A10 10 0 0 1 200 -12 V12 A10 10 0 0 1 190 22 H60 Z', 135, (212, 44))
hnd = mp([(0, 0), (60, 0)], 135, (212, 44))
icon('cricket', S, ['cricket', 'bat', 'ball', 'wicket', 'sport'],
     line=[P(blade), PL(hnd), C(188, 188, 24)], area=[P(blade), C(188, 188, 24)])

# ---------------------------------------------------------------- crossword
cells = [(0, 0), (2, 1), (1, 2), (3, 3)]
icon('crossword', S, ['crossword', 'puzzle', 'word game', 'grid'],
     line=[R(32, 32, 192, 192, 14), L(80, 32, 80, 224), L(128, 32, 128, 224), L(176, 32, 176, 224),
           L(32, 80, 224, 80), L(32, 128, 224, 128), L(32, 176, 224, 176)]
          + [solid(48 + 48 * cx, 48 + 48 * cy) for cx, cy in cells])

# ---------------------------------------------------------------- curling
stone = 'M48 152 C48 124 60 112 88 112 H168 C196 112 208 124 208 152 V168 C208 196 196 208 168 208 H88 C60 208 48 196 48 168 Z'
icon('curling', S, ['curling', 'stone', 'ice', 'winter sport'],
     line=[P(stone), P('M96 112 V92 A20 20 0 0 1 116 72 H196')], detail=[L(76, 160, 180, 160)], area=[P(stone)])

# ---------------------------------------------------------------- dice
die = load('dice-five')
for nm, pips, tags in [
    ('dice-one', [(128, 128)], ['dice', 'one', 'game', 'roll']),
    ('dice-two', [(168, 88), (88, 168)], ['dice', 'two', 'game', 'roll']),
    ('dice-three', [(168, 88), (128, 128), (88, 168)], ['dice', 'three', 'game', 'roll']),
    ('dice-four', [(88, 88), (168, 88), (88, 168), (168, 168)], ['dice', 'four', 'game', 'roll']),
    ('dice-six', [(88, 84), (168, 84), (88, 128), (168, 128), (88, 172), (168, 172)], ['dice', 'six', 'game', 'roll']),
]:
    icon(nm, S, tags, line=die['line'], area=die['area'], dotcut=[C(x, y, 16) for x, y in pips])

hexv = regular_polygon((128, 128), 96, 6)
tri = regular_polygon((128, 128), 48, 3)
# hex vertices: 0 top, 1 upper-right, 2 lower-right, 3 bottom, 4 lower-left, 5 upper-left
spokes = [(tri[0], hexv[1]), (tri[1], hexv[1]), (tri[1], hexv[3]), (tri[2], hexv[3]), (tri[2], hexv[5]), (tri[0], hexv[5])]
icon('dice-hexagon', S, ['polyhedral dice', 'rpg', 'd20'],
     line=[PG(hexv)], detail=[PG(tri)] + [L(*a, *b) for a, b in spokes], area=[PG(hexv)])

# ---------------------------------------------------------------- disc golf
basket = 'M56 128 H200 L184 168 H72 Z'
icon('disc-golf', S, ['disc golf', 'frisbee', 'sport'],
     line=[L(64, 48, 192, 48), P('M72 52 C76 88 92 112 100 128'), P('M184 52 C180 88 164 112 156 128'),
           L(128, 40, 128, 216), L(88, 216, 168, 216), P(basket)],
     area=[P(basket)])

# ---------------------------------------------------------------- diving mask
mask = ('M56 80 H152 A24 24 0 0 1 176 104 V136 C176 164 160 176 144 176 H132 C122 176 114 160 104 160 '
        'C94 160 86 176 76 176 H64 C48 176 32 164 32 136 V104 A24 24 0 0 1 56 80 Z')
snork = 'M208 40 V168 A32 32 0 0 1 176 200 H152'
icon('diving-mask', S, ['diving mask', 'snorkel', 'swim', 'ocean'],
     line=[P(mask), P(snork)], detail=[R(60, 108, 88, 32, 12)], area=[P(mask)])
icon('diving-mask-slash', S, ['diving mask', 'off', 'disabled', 'hidden', 'diving'],
     line=[P(mask), P(snork), SLASH])

# ---------------------------------------------------------------- dumbbell
db_local = ('M40 -52 H68 A8 8 0 0 1 76 -44 V-32 H92 A8 8 0 0 1 100 -24 V24 A8 8 0 0 1 92 32 H76 V44 A8 8 0 0 1 68 52 '
            'H40 A8 8 0 0 1 32 44 V-44 A8 8 0 0 1 40 -52 Z')
db_r = xf(db_local, -45, (128, 128), 0.98)
db_l = xf(db_local, 135, (128, 128), 0.98)
hd1 = mp([(-32, 0), (32, 0)], -45, (128, 128), 0.98)
icon('dumbbell', S, ['dumbbell', 'weights', 'gym', 'fitness'],
     line=[P(db_r), P(db_l), PL(hd1)], area=[P(db_r), P(db_l)])

# ---------------------------------------------------------------- exercise ball
icon('exercise-ball', S, ['fitness', 'yoga ball', 'gym'],
     line=[C(128, 124, 84), L(48, 224, 208, 224)],
     detail=[P('M64 92 C100 116 156 116 192 92'), P('M60 160 C100 140 156 140 196 160')], area=[C(128, 124, 84)])

# ---------------------------------------------------------------- exercise bike
icon('exercise-bike', S, ['stationary bike', 'spin', 'fitness', 'gym'],
     line=[L(40, 216, 216, 216), L(64, 88, 112, 88), PL([(92, 88), (104, 160), (168, 160)]), L(104, 160, 84, 216),
           C(168, 160, 40), PL([(168, 160), (148, 56)]), L(132, 56, 180, 56)],
     area=[C(168, 160, 40)])

# ---------------------------------------------------------------- fishing
icon('fishing', S, ['fishing', 'rod', 'hook', 'angling'],
     line=[L(40, 216, 196, 40), P('M196 40 V172 A24 24 0 0 1 148 172 V160'), C(84, 200, 14)])
icon('fishing-reel', S, ['fishing', 'reel', 'rod', 'angling'],
     line=[L(32, 48, 224, 48), L(128, 48, 128, 96), C(128, 144, 48), R(36, 120, 32, 48, 10), L(68, 144, 80, 144),
           L(176, 144, 208, 144), L(208, 144, 208, 184)],
     detail=[L(128, 144, 176, 144)], dotcut=[C(128, 144, 14)], area=[C(128, 144, 48), R(36, 120, 32, 48, 10)])

# ---------------------------------------------------------------- flag checkered
fcells = [(0, 0), (2, 0), (1, 1)]
icon('flag-checkered', S, ['finish line', 'race', 'checkered flag', 'score'],
     line=[L(56, 32, 56, 224), R(56, 40, 144, 96, 4), L(104, 40, 104, 136), L(152, 40, 152, 136), L(56, 88, 200, 88)]
          + [solid(72 + 48 * cx, 56 + 48 * cy) for cx, cy in fcells])

# ---------------------------------------------------------------- football
fr = (107.5 ** 2 + 60 ** 2) / 120
fa, fb = (52, 204), (204, 52)
ball = f'M{pt(fa)} A{f(fr)} {f(fr)} 0 0 1 {pt(fb)} A{f(fr)} {f(fr)} 0 0 1 {pt(fa)} Z'
lace = [L(94, 162, 162, 94)] + [L(*mp([(t, -16), (t, 16)], -45, (128, 128))[0], *mp([(t, -16), (t, 16)], -45, (128, 128))[1])
                                   for t in (-32, 0, 32)]
icon('football', S, ['american football', 'rugby', 'ball', 'nfl', 'sports'], line=[P(ball)], detail=lace, area=[P(ball)])
icon('football-slash', S, ['football', 'disabled', 'off', 'american football', 'nfl'], line=[P(ball), SLASH])

fh = ('M60 192 C44 176 40 152 40 128 C40 80 80 48 132 48 C176 48 204 76 208 112 H160 C152 112 148 120 148 128 '
      'V168 C148 184 136 192 120 192 Z')
icon('football-helmet', S, ['american football', 'helmet', 'sport'],
     line=[P(fh), P('M148 144 H216 V172 C216 186 208 196 196 196 H152'), L(184, 144, 184, 196)],
     detail=[C(100, 136, 16)], area=[P(fh)])

# ---------------------------------------------------------------- go
def go_lines(stones):
    out = []
    for k in (64, 128, 192):
        for vert in (True, False):
            cuts = sorted([(s[1] if vert else s[0], rr) for s, rr in stones if (s[0] if vert else s[1]) == k])
            a = 32
            segs = []
            for c, rr in cuts:
                if c - rr > a:
                    segs.append((a, c - rr))
                a = c + rr
            if a < 224:
                segs.append((a, 224))
            for s0, s1 in segs:
                out.append(L(k, s0, k, s1) if vert else L(s0, k, s1, k))
    return out
icon('go-game', S, ['go', 'board game', 'stones', 'weiqi'],
     line=go_lines([((128, 128), 46), ((192, 64), 50), ((64, 192), 46)]) + [C(192, 64, 28)],
     dot=[C(128, 128, 36), C(64, 192, 36)])

# ---------------------------------------------------------------- goggles
gog = ('M80 88 H176 A32 32 0 0 1 208 120 V136 A32 32 0 0 1 176 168 H156 C146 168 140 152 128 152 '
       'C116 152 110 168 100 168 H80 A32 32 0 0 1 48 136 V120 A32 32 0 0 1 80 88 Z')
icon('goggles', S, ['goggles', 'swimming', 'ski', 'eyewear'],
     line=[P(gog), R(32, 112, 16, 32, 4), R(208, 112, 16, 32, 4)],
     detail=[P('M84 120 C88 114 96 112 104 112')],
     area=[P(gog)])

# ---------------------------------------------------------------- golf
flag = [(100, 36), (192, 72), (100, 108)]
golf_line = [L(100, 36, 100, 200), PG(flag), E(100, 200, 52, 16)]
icon('golf', S, ['golf', 'flag', 'hole', 'course', 'club'], line=golf_line, dot=[C(184, 176, 20)], area=[PG(flag)])
icon('golf-slash', S, ['golf', 'off', 'disabled', 'hidden'], line=golf_line + [SLASH], dot=[C(184, 176, 20)])

print(save(overwrite=True))
