import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

S = 'Sports'
SLASH = L(48, 48, 208, 208)


def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def tilted_ellipse(c, rx, ry, deg):
    """Closed ellipse path rotated by deg (clockwise on screen)."""
    p0 = polar(c, rx, deg)
    p1 = polar(c, rx, deg + 180)
    return f'M{pt(p0)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p1)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p0)} Z'


def xf_path(d, fn, scale):
    """Apply a point transform fn (uniform scale `scale`) to an absolute path using M L H V C Q A Z."""
    toks = re.findall(r'[MLHVCQAZ]|-?\d*\.?\d+', d)
    out, i, cur, cmd = [], 0, (0, 0), None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == 'Z':
                out.append('Z')
            continue
        if cmd in 'ML':
            p = (float(toks[i]), float(toks[i + 1])); i += 2
            cur = p; out.append(cmd + pt(fn(p)))
        elif cmd == 'H':
            p = (float(toks[i]), cur[1]); i += 1; cur = p; out.append('L' + pt(fn(p)))
        elif cmd == 'V':
            p = (cur[0], float(toks[i])); i += 1; cur = p; out.append('L' + pt(fn(p)))
        elif cmd in 'CQ':
            n = 3 if cmd == 'C' else 2
            ps = [(float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])) for k in range(n)]; i += 2 * n
            cur = ps[-1]; out.append(cmd + ' '.join(pt(fn(p)) for p in ps))
        elif cmd == 'A':
            rx, ry, ang, la, sw, x, y = toks[i:i + 7]; i += 7
            cur = (float(x), float(y))
            out.append(f'A{f(float(rx) * scale)} {f(float(ry) * scale)} {ang} {la} {sw} {pt(fn(cur))}')
    return ' '.join(out)


def xf_el(el, fn, scale):
    m = re.match(r'<path d="([^"]+)"/>', el)
    if m:
        return P(xf_path(m.group(1), fn, scale))
    m = re.match(r'<circle cx="([\d.\-]+)" cy="([\d.\-]+)" r="([\d.\-]+)"/>', el)
    if m:
        c = fn((float(m.group(1)), float(m.group(2))))
        return C(c[0], c[1], float(m.group(3)) * scale)
    raise ValueError(el)


def rrect_rot(c, w, h, r, deg):
    """Rounded rectangle centred at c, rotated by deg."""
    x0, y0, x1, y1 = c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2
    pts = [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)]
    q = rot(pts, deg, c)
    d = f'M{pt(q[0])} L{pt(q[1])} A{f(r)} {f(r)} 0 0 1 {pt(q[2])} L{pt(q[3])} A{f(r)} {f(r)} 0 0 1 {pt(q[4])} ' \
        f'L{pt(q[5])} A{f(r)} {f(r)} 0 0 1 {pt(q[6])} L{pt(q[7])} A{f(r)} {f(r)} 0 0 1 {pt(q[0])} Z'
    return d


def seg_along(c, u, a, b):
    return L(c[0] + u[0] * a, c[1] + u[1] * a, c[0] + u[0] * b, c[1] + u[1] * b)


def all_line(base):
    return base['line'] + base['detail'], base['dot'] + base['dotcut']


# ---------------------------------------------------------------- helmet
dome = 'M48 168 V152 A80 80 0 0 1 208 152 V168'
helmet_area = 'M48 168 V152 A80 80 0 0 1 208 152 V168 Z'
icon('helmet', S, ['helmet', 'safety', 'protection', 'hard hat', 'bike helmet'],
     line=[P(dome), R(32, 168, 192, 32, 16)],
     detail=[L(128, 104, 128, 140)],
     area=[P(helmet_area), R(32, 168, 192, 32, 16)])

# ---------------------------------------------------------------- hockey
icon('hockey', S, ['hockey stick', 'puck', 'ice hockey', 'sport', 'hockey'],
     line=[L(96, 32, 144, 176), P('M144 176 L156 208 H200 A16 16 0 0 0 200 176 Z'), R(32, 176, 80, 32, 16)],
     area=[P('M144 176 L156 208 H200 A16 16 0 0 0 200 176 Z'), R(32, 176, 80, 32, 16)])

# ---------------------------------------------------------------- hula-hoop
icon('hula-hoop', S, ['hula hoop', 'exercise', 'ring', 'play'],
     line=[C(128, 56, 20), L(128, 92, 128, 152), PL([(80, 68), (128, 104), (176, 68)]),
           PL([(96, 220), (128, 152), (160, 220)]), P(tilted_ellipse((128, 140), 96, 28, -8))],
     area=[C(128, 56, 20)])

# ---------------------------------------------------------------- skates (shared boot)
boot = 'M72 52 A12 12 0 0 1 84 40 H124 A12 12 0 0 1 136 52 V100 L180 116 A40 40 0 0 1 208 154 V160 A12 12 0 0 1 196 172 H84 A12 12 0 0 1 72 160 Z'
icon('ice-skate', S, ['ice skating', 'skate', 'winter', 'rink', 'ice skate'],
     line=[P(boot), L(96, 172, 96, 208), L(176, 172, 176, 208), P('M48 208 H196 A20 20 0 0 0 216 188')],
     detail=[L(108, 76, 136, 76), L(112, 108, 144, 108)],
     area=[P(boot)])
boot2 = 'M72 52 A12 12 0 0 1 84 40 H124 A12 12 0 0 1 136 52 V96 L180 112 A40 40 0 0 1 208 150 V152 A12 12 0 0 1 196 164 H84 A12 12 0 0 1 72 152 Z'
icon('roller-skate', S, ['roller skating', 'skate', 'rink', 'quad skate', 'roller skate'],
     line=[P(boot2), C(100, 200, 20), C(180, 200, 20)],
     detail=[L(72, 128, 136, 128)],
     area=[P(boot2), C(100, 200, 20), C(180, 200, 20)])

# ---------------------------------------------------------------- jersey
jer = ('M80 32 H104 C104 56 114 68 128 68 C142 68 152 56 152 32 H176 C176 72 188 92 208 104 V208 '
       'A16 16 0 0 1 192 224 H64 A16 16 0 0 1 48 208 V104 C68 92 80 72 80 32 Z')
icon('jersey', S, ['jersey', 'tank top', 'uniform', 'sports', 'sports shirt'],
     line=[P(jer)], detail=[PL([(104, 120), (152, 120), (120, 184)])], area=[P(jer)])

# ---------------------------------------------------------------- jump-rope
hu_l = unit((76, 108), (56, 36))
hu_r = (-hu_l[0], hu_l[1])
h_l = (76 + hu_l[0] * 36, 108 + hu_l[1] * 36)
h_r = (180 + hu_r[0] * 36, 108 + hu_r[1] * 36)
icon('jump-rope', S, ['jump rope', 'skipping', 'cardio', 'fitness', 'exercise'],
     line=[P(capsule(h_l, 22, 13, hu_l)), P(capsule(h_r, 22, 13, hu_r)), P('M76 108 C80 236 176 236 180 108')],
     area=[P(capsule(h_l, 22, 13, hu_l)), P(capsule(h_r, 22, 13, hu_r))])

# ---------------------------------------------------------------- kayak
hull = 'M32 152 C72 124 184 124 224 152 C184 188 72 188 32 152 Z'
pu = unit((48, 72), (208, 208))
pc = (128, 140)
icon('kayak', S, ['kayak', 'paddle', 'canoe', 'water', 'water sport'],
     line=[P(hull), seg_along(pc, pu, -64, 64),
           P(capsule((pc[0] - pu[0] * 88, pc[1] - pu[1] * 88), 16, 14, pu)),
           P(capsule((pc[0] + pu[0] * 88, pc[1] + pu[1] * 88), 16, 14, pu))],
     area=[P(hull)])

# ---------------------------------------------------------------- kitesurfing
kw = [(36, 92), (128, 0), (220, 92), (128, 52)]
kw = [(128 + (x - 128) * 0.52, 66 + (y - 66) * 0.52) for x, y in kw]
kw = [(x + 40, y - 8) for x, y in rot(kw, 28, (128, 66))]
kite = f'M{pt(kw[0])} Q{pt(kw[1])} {pt(kw[2])} Q{pt(kw[3])} {pt(kw[0])} Z'
bar = (124, 140)
icon('kitesurfing', S, ['kitesurf', 'kite', 'surf', 'water sports'],
     line=[P(kite), L(kw[0][0], kw[0][1] + 4, *bar), L(kw[2][0] - 2, kw[2][1] - 2, *bar),
           C(72, 104, 18), L(80, 136, 100, 172), L(84, 144, 124, 140),
           PL([(100, 172), (84, 204)]), PL([(100, 172), (128, 200)]), L(48, 212, 160, 200)],
     area=[P(kite), C(72, 104, 18)])

# ---------------------------------------------------------------- martial-arts
icon('martial-arts', S, ['kung fu', 'karate', 'martial arts', 'fight', 'kick'],
     line=[C(84, 56, 22), L(96, 96, 112, 152), L(112, 152, 88, 220), L(112, 152, 212, 104),
           PL([(98, 104), (136, 96), (156, 72)]), PL([(98, 104), (60, 120), (44, 100)])],
     area=[C(84, 56, 22)])

# ---------------------------------------------------------------- medal-first
med = load('medal')
icon('medal-first', S, ['first place', 'gold medal', 'winner'],
     line=med['line'], detail=[PL([(116, 146), (132, 136), (132, 184)])], area=med['area'])

# ---------------------------------------------------------------- meeple
hc = (128, 72)
nl, nr = polar(hc, 34, 125), polar(hc, 34, 55)
meeple = (f'M{pt(nl)} A34 34 0 1 1 {pt(nr)} C176 108 220 112 220 136 C220 156 196 156 172 160 '
          f'L196 208 A12 12 0 0 1 184 224 H152 L128 188 L104 224 H72 A12 12 0 0 1 60 208 '
          f'L84 160 C60 156 36 156 36 136 C36 112 80 108 {pt(nl)} Z')
icon('meeple', S, ['meeple', 'board game', 'piece', 'token'], line=[P(meeple)], area=[P(meeple)])

# ---------------------------------------------------------------- padel
pd_c = (136, 100)
pd_u = (-math.sin(math.radians(45)), math.cos(math.radians(45)))
pd_head = tilted_ellipse(pd_c, 64, 58, 45)
grip_c = (pd_c[0] + pd_u[0] * 104, pd_c[1] + pd_u[1] * 104)
holes = [rot([(pd_c[0] + dx, pd_c[1] + dy)], 45, pd_c)[0] for dx, dy in ((0, 0), (-26, 0), (26, 0), (0, -26), (0, 26))]
icon('padel', S, ['padel', 'racket', 'paddle', 'ball sport'],
     line=[P(pd_head), seg_along(pd_c, pd_u, 64, 84), P(capsule(grip_c, 16, 16, pd_u)), C(192, 192, 24)],
     area=[P(pd_head), P(capsule(grip_c, 16, 16, pd_u)), C(192, 192, 24)],
     dotcut=[C(x, y, 9) for x, y in holes])

# ---------------------------------------------------------------- paraglider
icon('paraglider', S, ['paragliding', 'glider', 'flying', 'parachute'],
     line=[P('M36 92 Q128 0 220 92 Q128 52 36 92 Z'), L(48, 92, 106, 192), L(208, 92, 150, 192),
           C(128, 150, 18), P('M100 216 C100 198 112 190 128 190 C144 190 156 198 156 216')],
     area=[P('M36 92 Q128 0 220 92 Q128 52 36 92 Z'), C(128, 150, 18),
           P('M100 216 C100 198 112 190 128 190 C144 190 156 198 156 216 Z')])

# ---------------------------------------------------------------- person-biking
icon('person-biking', S, ['cycling', 'biker', 'riding', 'sport', 'bike'],
     line=[C(68, 176, 36), C(188, 176, 36), C(164, 52, 20),
           PL([(68, 176), (120, 176), (164, 120), (188, 176)]),
           PL([(100, 124), (136, 84), (168, 116)]), PL([(100, 124), (144, 144), (120, 176)])],
     area=[C(164, 52, 20)])

# ---------------------------------------------------------------- person-hiking
icon('person-hiking', S, ['hiking', 'trekking', 'backpack', 'walk', 'walking stick'],
     line=[C(128, 52, 20), L(123, 92, 112, 144), PL([(112, 144), (148, 180), (144, 220)]),
           PL([(112, 144), (92, 184), (76, 216)]), PL([(124, 96), (152, 124), (172, 116)]),
           L(176, 88, 192, 216), R(68, 88, 40, 64, 14)],
     area=[C(128, 52, 20), R(68, 88, 40, 64, 14)])

# ---------------------------------------------------------------- person-jumping
icon('person-jumping', S, ['jump', 'leap', 'exercise', 'fitness'],
     line=[C(128, 52, 20), L(128, 92, 128, 136), PL([(76, 52), (128, 98), (180, 52)]),
           PL([(128, 136), (92, 160), (100, 192)]), PL([(128, 136), (164, 160), (156, 192)]), L(88, 224, 168, 224)],
     area=[C(128, 52, 20)])

# ---------------------------------------------------------------- person-running
icon('person-running', S, ['run', 'running', 'jog', 'exercise', 'sprint'],
     line=[C(156, 52, 20), L(140, 90, 112, 144), PL([(140, 96), (176, 120), (196, 100)]),
           PL([(140, 96), (100, 100), (76, 128)]), PL([(112, 144), (152, 168), (144, 216)]),
           PL([(112, 144), (92, 184), (48, 188)])],
     area=[C(156, 52, 20)])

# ---------------------------------------------------------------- person-skiing
icon('person-skiing', S, ['skiing', 'ski', 'winter sports', 'snow', 'winter sport'],
     line=[C(128, 52, 20), L(122, 90, 100, 128), PL([(100, 128), (140, 148), (128, 192)]),
           PL([(118, 92), (152, 116)]), L(152, 116, 180, 196),
           P('M32 172 L208 220 A12 12 0 0 0 220 204')],
     area=[C(128, 52, 20)])

# ---------------------------------------------------------------- person-snowboarding
icon('person-snowboarding', S, ['snowboarding', 'winter sport', 'board', 'snowboard', 'snow'],
     line=[C(120, 52, 20), L(124, 92, 132, 136), PL([(68, 112), (126, 96), (184, 84)]),
           PL([(132, 136), (96, 160), (92, 196)]), PL([(132, 136), (168, 160), (168, 200)]),
           P(capsule((128, 206), 80, 10, unit((48, 200), (208, 212))))],
     area=[C(120, 52, 20)])

# ---------------------------------------------------------------- person-stretching
icon('person-stretching', S, ['exercise', 'stretch', 'workout', 'sport', 'stretching'],
     line=[C(128, 56, 22), L(128, 96, 128, 152), PL([(72, 56), (128, 108), (184, 56)]),
           PL([(80, 220), (128, 152), (176, 220)])],
     area=[C(128, 56, 22)])

# ---------------------------------------------------------------- person-swimming
icon('person-swimming', S, ['swimming', 'swimmer', 'pool', 'sport', 'exercise'],
     line=[C(176, 104, 22), PL([(48, 152), (108, 120), (140, 140)]), PL([(108, 120), (128, 76), (168, 60)]),
           P('M32 184 Q48 168 64 184 T96 184 T128 184 T160 184 T192 184 T224 184'),
           P('M32 216 Q48 200 64 216 T96 216 T128 216 T160 216 T192 216 T224 216')],
     area=[C(176, 104, 22)])

# ---------------------------------------------------------------- person-tai-chi
icon('person-tai-chi', S, ['tai chi', 'martial arts', 'balance'],
     line=[C(128, 52, 20), L(128, 92, 128, 140), L(128, 140, 124, 220), PL([(128, 140), (172, 140), (164, 184)]),
           PL([(128, 98), (88, 82), (76, 48)]), PL([(128, 98), (172, 110), (196, 98)])],
     area=[C(128, 52, 20)])

# ---------------------------------------------------------------- person-throw
icon('person-throw', S, ['throwing', 'bowling', 'sport'],
     line=[C(140, 54, 20), L(132, 92, 136, 144), PL([(136, 144), (176, 176), (180, 216)]),
           PL([(136, 144), (104, 180), (84, 216)]), PL([(130, 100), (92, 100), (68, 76)]),
           PL([(130, 100), (168, 116), (192, 104)]), C(56, 56, 16)],
     area=[C(140, 54, 20), C(56, 56, 16)])

# ---------------------------------------------------------------- pickleball
pk_c = (132, 102)
pk_head = rrect_rot(pk_c, 104, 120, 38, 45)
pk_grip = (pk_c[0] + pd_u[0] * 94, pk_c[1] + pd_u[1] * 94)
icon('pickleball', S, ['pickleball', 'paddle', 'ball', 'racket'],
     line=[P(pk_head), seg_along(pk_c, pd_u, 60, 74), P(capsule(pk_grip, 14, 16, pd_u)), C(188, 188, 32)],
     area=[P(pk_head), P(capsule(pk_grip, 14, 16, pd_u)), C(188, 188, 32)],
     dotcut=[C(176, 176, 8), C(200, 180, 8), C(184, 202, 8)])

# ---------------------------------------------------------------- ping-pong
pp_c = (140, 104)
pp_u = pd_u
pp_g = (pp_c[0] + pp_u[0] * 98, pp_c[1] + pp_u[1] * 98)
icon('ping-pong', S, ['table tennis', 'ping pong', 'paddle', 'sport', 'ball'],
     line=[C(*pp_c, 68), seg_along(pp_c, pp_u, 68, 80), P(capsule(pp_g, 14, 18, pp_u)), C(196, 196, 20)],
     area=[C(*pp_c, 68), P(capsule(pp_g, 14, 18, pp_u)), C(196, 196, 20)])

# ---------------------------------------------------------------- podium
pod = [(32, 216), (32, 160), (96, 160), (96, 120), (160, 120), (160, 176), (224, 176), (224, 216)]
star = [polar((128, 66), 30 if i % 2 == 0 else 13, -90 + i * 36) for i in range(10)]
icon('podium', S, ['leaderboard', 'ranking', 'winners', 'podium', 'top'],
     line=[PG(pod), PG(star)], detail=[L(96, 160, 96, 216), L(160, 176, 160, 216)], area=[PG(pod), PG(star)])

# ---------------------------------------------------------------- puzzle-cube
fx0, fy0, fs, dd = 36, 84, 140, 44
cube_hull = [(fx0, fy0), (fx0 + dd, fy0 - dd), (fx0 + fs + dd, fy0 - dd), (fx0 + fs + dd, fy0 + fs - dd), (fx0 + fs, fy0 + fs), (fx0, fy0 + fs)]
cdet = [PL([(fx0, fy0), (fx0 + fs, fy0), (fx0 + fs, fy0 + fs)]), L(fx0 + fs, fy0, fx0 + fs + dd, fy0 - dd)]
for k in (1, 2):
    x = fx0 + fs * k / 3
    y = fy0 + fs * k / 3
    cdet.append(PL([(x, fy0 + fs), (x, fy0), (x + dd, fy0 - dd)]))
    cdet.append(PL([(fx0, y), (fx0 + fs, y), (fx0 + fs + dd, y - dd)]))
icon('puzzle-cube', S, ['cube puzzle', 'twisty puzzle', 'brain teaser'],
     line=[PG(cube_hull)], detail=cdet, area=[PG(cube_hull)])

# ---------------------------------------------------------------- racquet
rq_c = (144, 100)
rq_head = tilted_ellipse(rq_c, 72, 56, 45 + 90)
rq_g = (rq_c[0] + pd_u[0] * 112, rq_c[1] + pd_u[1] * 112)
def ell_y(x, a=56, b=72):
    return b * math.sqrt(max(0, 1 - (x / a) ** 2))
strings = []
for sx in (-20, 20):
    yy = ell_y(sx)
    strings.append(PL(rot([(rq_c[0] + sx, rq_c[1] - yy), (rq_c[0] + sx, rq_c[1] + yy)], 45, rq_c)))
for sy in (-24, 16):
    xx = 56 * math.sqrt(1 - (sy / 72) ** 2)
    strings.append(PL(rot([(rq_c[0] - xx, rq_c[1] + sy), (rq_c[0] + xx, rq_c[1] + sy)], 45, rq_c)))
icon('racquet', S, ['tennis racket', 'badminton', 'squash'],
     line=[P(rq_head), seg_along(rq_c, pd_u, 72, 92), P(capsule(rq_g, 18, 14, pd_u))],
     detail=strings, area=[P(rq_head), P(capsule(rq_g, 18, 14, pd_u))])

# ---------------------------------------------------------------- rowing
boat = 'M32 148 H224 C212 176 188 184 164 184 H92 C68 184 44 176 32 148 Z'
ou = unit((112, 96), (64, 184))
icon('rowing', S, ['rowing', 'boat', 'oar', 'crew'],
     line=[P(boat), C(160, 56, 20), L(156, 88, 144, 132), PL([(154, 96), (112, 100)]),
           seg_along((112, 100), ou, -8, 88), P(capsule((112 + ou[0] * 104, 100 + ou[1] * 104), 8, 12, ou))],
     area=[P(boat), C(160, 56, 20)])

# ---------------------------------------------------------------- rugby
ra, rb = (60, 196), (196, 60)
ru = unit(ra, rb)
rmid = (128, 128)
ball = f'M{pt(ra)} A104 104 0 0 1 {pt(rb)} A104 104 0 0 1 {pt(ra)} Z'
rn = (-ru[1], ru[0])
rdet = [seg_along(rmid, ru, -44, 44)]
for t in (-32, 0, 32):
    cc = (rmid[0] + ru[0] * t, rmid[1] + ru[1] * t)
    rdet.append(seg_along(cc, rn, -16, 16))
icon('rugby', S, ['rugby', 'ball', 'sport', 'oval'], line=[P(ball)], detail=rdet, area=[P(ball)])

# ---------------------------------------------------------------- scoreboard
icon('scoreboard', S, ['scoreboard', 'score', 'match', 'game'],
     line=[R(32, 48, 192, 136, 14), L(80, 184, 80, 216), L(176, 184, 176, 216)],
     detail=[L(128, 76, 128, 156), R(64, 84, 32, 64, 16), PL([(164, 96), (180, 84), (180, 148)])],
     area=[R(32, 48, 192, 136, 14)])

# ---------------------------------------------------------------- scuba-diver
icon('scuba-diver', S, ['diving', 'scuba', 'underwater', 'swimming', 'scuba diving'],
     line=[C(184, 136, 20), R(194, 124, 30, 24, 10), P(capsule((116, 140), 36, 14, (1, 0))), R(88, 92, 64, 24, 12),
           L(66, 140, 52, 140), PG([(52, 140), (32, 116), (32, 164)]), L(176, 116, 176, 84)],
     area=[C(184, 136, 20), P(capsule((116, 140), 36, 14, (1, 0))), R(88, 92, 64, 24, 12), PG([(52, 140), (32, 116), (32, 164)])],
     dot=[C(204, 84, 10), C(216, 56, 8)])

# ---------------------------------------------------------------- scuba-tank
tank = 'M80 224 V120 A48 48 0 0 1 176 120 V208 A16 16 0 0 1 160 224 H96 A16 16 0 0 1 80 208 Z'
icon('scuba-tank', S, ['oxygen tank', 'scuba', 'diving', 'air', 'scuba tank'],
     line=[P('M80 208 V120 A48 48 0 0 1 176 120 V208 A16 16 0 0 1 160 224 H96 A16 16 0 0 1 80 208 Z'),
           L(128, 48, 128, 72), L(104, 40, 152, 40)],
     detail=[L(80, 144, 176, 144), L(80, 184, 176, 184)],
     area=[P('M80 208 V120 A48 48 0 0 1 176 120 V208 A16 16 0 0 1 160 224 H96 A16 16 0 0 1 80 208 Z')])

# ---------------------------------------------------------------- skateboard
deck = 'M36 92 C40 108 50 116 68 116 H188 C206 116 216 108 220 92'
icon('skateboard', S, ['skateboard', 'skate', 'board', 'street'],
     line=[P(deck), C(80, 156, 20), C(176, 156, 20)], area=[C(80, 156, 20), C(176, 156, 20)])
icon('skateboard-slash', S, ['skateboard', 'off', 'disabled', 'hidden'],
     line=[P(deck), C(80, 156, 20), C(176, 156, 20), SLASH])

# ---------------------------------------------------------------- ski-jump
icon('ski-jump', S, ['ski jump', 'skiing', 'winter sport', 'jump'],
     line=[P('M32 64 C72 64 88 184 152 184'), L(32, 216, 224, 216), L(72, 104, 72, 216), L(112, 176, 112, 216),
           C(196, 60, 16), L(184, 84, 152, 116), L(136, 104, 216, 128)],
     area=[C(196, 60, 16)])

# ---------------------------------------------------------------- sled
icon('sled', S, ['sledding', 'sledge', 'toboggan', 'winter'],
     line=[R(40, 92, 144, 36, 14), L(76, 128, 76, 176), L(148, 128, 148, 176),
           P('M32 176 H184 A32 32 0 0 0 216 144 V136')],
     area=[R(40, 92, 144, 36, 14)])

# ---------------------------------------------------------------- sneaker-move
sn = load('sneaker')
sk = 0.72
sfn = lambda p: (224 - (224 - p[0]) * sk, 172 - (192 - p[1]) * sk)
icon('sneaker-move', S, ['running shoe', 'moving', 'speed'],
     line=[xf_el(e, sfn, sk) for e in sn['line']] + [L(32, 112, 60, 112), L(44, 144, 64, 144)],
     detail=[xf_el(e, sfn, sk) for e in sn['detail']],
     area=[xf_el(e, sfn, sk) for e in sn['area']])

# ---------------------------------------------------------------- slashes on existing icons
sb = load('soccer-ball')
icon('soccer-ball-slash', S, ['soccer ball', 'disabled', 'off', 'sports'], line=sb['line'] + sb['detail'] + [SLASH])
tg = load('target')
icon('target-slash', S, ['target', 'off', 'disabled', 'hidden'], line=tg['line'] + tg['detail'] + [SLASH],
     dot=tg['dotcut'])

# ---------------------------------------------------------------- soccer-field
icon('soccer-field', S, ['football pitch', 'soccer field', 'stadium', 'sport'],
     line=[R(32, 56, 192, 144, 14)],
     detail=[L(128, 56, 128, 200), C(128, 128, 24), PL([(32, 96), (64, 96), (64, 160), (32, 160)]),
             PL([(224, 96), (192, 96), (192, 160), (224, 160)])],
     area=[R(32, 56, 192, 144, 14)])

# ---------------------------------------------------------------- stadium
st_sil = 'M32 108 A96 40 0 0 1 224 108 V168 A96 40 0 0 1 32 168 Z'
fy = 108 - 40 * math.sqrt(1 - (64 / 96) ** 2)
icon('stadium', S, ['stadium', 'arena', 'venue', 'sports ground', 'sports'],
     line=[P(st_sil), PL([(64, fy), (64, 36), (92, 46), (64, 56)]), PL([(192, fy), (192, 36), (220, 46), (192, 56)])],
     detail=[P('M32 108 A96 40 0 0 0 224 108'), P('M32 140 A96 40 0 0 0 224 140'), E(128, 108, 52, 14)],
     area=[P(st_sil)])

# ---------------------------------------------------------------- suits
heart = 'M128 216 C104 184 36 152 36 100 A46 46 0 0 1 128 80 A46 46 0 0 1 220 100 C220 152 152 184 128 216 Z'
icon('suit-heart', S, ['heart', 'cards', 'poker', 'suit', 'hearts'], line=[P(heart)], area=[P(heart)])
dia = 'M128 32 Q156 88 196 128 Q156 168 128 224 Q100 168 60 128 Q100 88 128 32 Z'
icon('suit-diamond', S, ['diamond', 'cards', 'poker', 'suit', 'diamonds'], line=[P(dia)], area=[P(dia)])
lc, rc_ = (82, 144), (174, 144)
sl, sr = polar(lc, 46, 30), polar(rc_, 46, 150)
spade = (f'M128 32 C152 64 220 96 220 144 ' + arc_to(rc_, 46, (220, 144), sr, lambda m: m[1]) +
         f' Q132 196 160 216 H96 Q124 196 {pt(sl)} ' + arc_to(lc, 46, sl, (36, 144), lambda m: m[1]) +
         ' C36 96 104 64 128 32 Z')
icon('suit-spade', S, ['spade', 'cards', 'poker', 'suit', 'spades'], line=[P(spade)], area=[P(spade)])
ct, cl, cr = (128, 80), (80, 144), (176, 144)
cR = 44
ptl = circle_x(ct, cR, cl, cR)[0]
ptr = circle_x(ct, cR, cr, cR)[0]
cs_r, cs_l = polar(cr, cR, 160), polar(cl, cR, 20)
club = (f'M{pt(ptl)} ' + arc_to(ct, cR, ptl, ptr, lambda m: -m[1]) + ' ' + arc_to(cr, cR, ptr, cs_r, lambda m: m[0]) +
        f' Q132 196 160 216 H96 Q124 196 {pt(cs_l)} ' + arc_to(cl, cR, cs_l, ptl, lambda m: -m[0]) + ' Z')
icon('suit-club', S, ['club', 'cards', 'poker', 'suit', 'clubs'], line=[P(club)], area=[P(club)])

# ---------------------------------------------------------------- surfboard
sb_pts = [(0, -112), (28, -80), (40, -20), (40, 40), (40, 90), (24, 112), (0, 112), (-24, 112), (-40, 90),
          (-40, 40), (-40, -20), (-28, -80)]
sbr = rot([(128 + x, 128 + y) for x, y in sb_pts], 45)
surf = (f'M{pt(sbr[0])} C{pt(sbr[1])} {pt(sbr[2])} {pt(sbr[3])} C{pt(sbr[4])} {pt(sbr[5])} {pt(sbr[6])} '
        f'C{pt(sbr[7])} {pt(sbr[8])} {pt(sbr[9])} C{pt(sbr[10])} {pt(sbr[11])} {pt(sbr[0])} Z')
sline = rot([(128, 128 - 72), (128, 128 + 84)], 45)
icon('surfboard', S, ['surfing', 'surf', 'wave', 'beach'], line=[P(surf)], detail=[PL(sline)], area=[P(surf)])

# ---------------------------------------------------------------- helmet-slash
icon('helmet-slash', S, ['helmet', 'off', 'disabled', 'hidden'],
     line=[P(dome), R(32, 168, 192, 32, 16), L(128, 104, 128, 140), SLASH])

# ---------------------------------------------------------------- tic-tac-toe
icon('tic-tac-toe', S, ['tic tac toe', 'noughts and crosses', 'game', 'grid'],
     line=[L(100, 32, 100, 224), L(156, 32, 156, 224), L(32, 100, 224, 100), L(32, 156, 224, 156),
           L(34, 34, 74, 74), L(74, 34, 34, 74), C(202, 202, 20)])

# ---------------------------------------------------------------- tournament
icon('tournament', S, ['tournament', 'bracket', 'competition', 'matches'],
     line=[PL([(32, 48), (88, 48), (88, 96), (32, 96)]), PL([(32, 160), (88, 160), (88, 208), (32, 208)]),
           PL([(88, 72), (144, 72), (144, 184), (88, 184)]), L(144, 128, 180, 128), C(204, 128, 20)],
     area=[C(204, 128, 20)])

# ---------------------------------------------------------------- treadmill
icon('treadmill', S, ['treadmill', 'running machine', 'gym', 'cardio', 'running'],
     line=[R(32, 176, 176, 36, 18), L(180, 176, 200, 72), L(196, 92, 160, 100),
           C(104, 52, 18), L(100, 82, 92, 122), PL([(92, 122), (120, 140), (116, 160)]), PL([(92, 122), (76, 144), (52, 148)]),
           PL([(98, 90), (124, 104), (140, 96)]), PL([(98, 90), (76, 100), (64, 116)])],
     area=[R(32, 176, 176, 36, 18), C(104, 52, 18)])

print(save(overwrite=True))
