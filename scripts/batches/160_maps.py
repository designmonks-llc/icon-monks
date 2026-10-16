import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

M = 'Maps'
SLASH = L(48, 48, 208, 208)


def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def rounded_poly(points, r):
    """Closed convex polygon (clockwise on screen) with every corner rounded to radius r."""
    n = len(points)
    corners = []
    for i in range(n):
        A, V, B = points[i - 1], points[i], points[(i + 1) % n]
        u1, u2 = unit(V, A), unit(V, B)
        th = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        t = r / math.tan(th / 2)
        corners.append(((V[0] + u1[0] * t, V[1] + u1[1] * t), (V[0] + u2[0] * t, V[1] + u2[1] * t)))
    d = f'M{pt(corners[0][1])}'
    for i in range(1, n + 1):
        p1, p2 = corners[i % n]
        d += f' L{pt(p1)} A{f(r)} {f(r)} 0 0 1 {pt(p2)}'
    return d + ' Z'


def rel(x, y):
    return (128 + x, 128 + y)


def RL(*pts):
    return PL([rel(*p) for p in pts])


# ---------------------------------------------------------------- sign frames
H = 96 + 16 * (math.sqrt(2) - 1)  # virtual vertex so the rounded tips land on 32 / 224
DIAMOND = rounded_poly([(128, 128 - H), (128 + H, 128), (128, 128 + H), (128 - H, 128)], 16)


def diamond_sign(name, tags, detail=(), dotcut=()):
    icon(name, M, tags, line=[P(DIAMOND)], detail=list(detail), area=[P(DIAMOND)], dotcut=list(dotcut))


PRO_SLASH = load('prohibit')['line'][1]  # TL->BR, same as the prohibit icon
PRO_SLASH_M = L(256 - 60.12, 60.12, 60.12, 195.88)  # mirrored, TR->BL


def prohibit_pieces(mirror):
    # the disc split into two segments either side of the slash, so the fill weight keeps the slash and the cut mark
    c, r, off = (128, 128), 96, 20 * math.sqrt(2)
    out = []
    for sg in (1, -1):
        # line u - v = sg*off (or u + v = sg*off when mirrored); intersect with the circle
        k = sg * off
        # u = v + k  -> 2v^2 + 2kv + k^2 - r^2 = 0
        disc = math.sqrt(4 * k * k - 8 * (k * k - r * r))
        vs = [(-2 * k + disc) / 4, (-2 * k - disc) / 4]
        pts = [(c[0] + v + k, c[1] + v) for v in vs]
        if mirror:
            pts = [(256 - x, y) for x, y in pts]
        far = (c[0] + sg * 60, c[1] - sg * 60) if not mirror else (c[0] - sg * 60, c[1] - sg * 60)
        out.append(P(f'M{pt(pts[0])} L{pt(pts[1])} ' + arc_to(c, r, pts[1], pts[0], lambda m: -dist(m, far)) + ' Z'))
    return out


def prohibit_sign(name, tags, marks, mirror=False):
    icon(name, M, tags, line=[C(128, 128, 96), PRO_SLASH_M if mirror else PRO_SLASH], detail=marks,
         area=prohibit_pieces(mirror))


# ---------------------------------------------------------------- route-square (path geometry, square stops)
icon('route-square', M, ['route', 'waypoints', 'path', 'journey'],
     line=[R(32, 176, 48, 48, 12), R(176, 32, 48, 48, 12),
           P('M80 200 H156 A36 36 0 0 0 156 128 H100 A36 36 0 0 1 100 56 H176')],
     area=[R(32, 176, 48, 48, 12), R(176, 32, 48, 48, 12)])

# ---------------------------------------------------------------- sauna
steam = [P(f'M{x} 108 C{x - 18} 90 {x + 18} 70 {x} 48') for x in (88, 128, 168)]
icon('sauna', M, ['sauna', 'steam room', 'spa', 'heat'],
     line=[R(32, 136, 192, 40, 12), L(64, 176, 64, 216), L(192, 176, 192, 216)] + steam,
     area=[R(32, 136, 192, 40, 12)])

# ---------------------------------------------------------------- road signs
SQ = R(32, 32, 192, 192, 16)
icon('sign-dead-end', M, ['dead end', 'road sign', 'no through road', 'traffic'],
     line=[SQ], detail=[L(88, 76, 168, 76), L(128, 112, 128, 192)], area=[SQ])

pill = R(64, 108, 128, 40, 20)
icon('sign-do-not-enter', M, ['no entry', 'do not enter', 'road sign', 'prohibited'],
     line=[C(128, 128, 96)], detail=[pill], area=[C(128, 128, 96)], hole=[pill])

diamond_sign('sign-intersection', ['intersection', 'crossroads', 'road sign', 'traffic'],
             detail=[RL((0, -60), (0, 60)), RL((-60, 0), (60, 0))])
diamond_sign('sign-intersection-t', ['t junction', 'road sign', 'traffic', 'intersection'],
             detail=[RL((-40, -20), (40, -20)), RL((0, -20), (0, 60))])
diamond_sign('sign-intersection-y', ['y junction', 'fork', 'road sign', 'traffic'],
             detail=[RL((0, 60), (0, 12)), RL((-34, -28), (0, 12), (34, -28))])
diamond_sign('sign-intersection-side', ['side road', 'junction', 'road sign', 'traffic'],
             detail=[RL((0, -60), (0, 60)), RL((0, 4), (50, 4))])


def merge(sx):
    mx = 16 * sx
    return [RL((mx, -46), (mx, 46)),
            P(f'M{pt(rel(-30 * sx, 32))} C{pt(rel(-30 * sx, 8))} {pt(rel(mx, 10))} {pt(rel(mx, -14))}')]


diamond_sign('sign-merge-left', ['merge', 'lane', 'road sign', 'traffic'], detail=merge(1))
diamond_sign('sign-merge-right', ['merge', 'lane', 'road sign', 'traffic'], detail=merge(-1))


def circ_turn(sx):
    # sx = -1 left, +1 right: stem on the opposite side, turning toward sx
    x0 = 128 - sx * 22
    xr = x0 + sx * 28
    sweep = 0 if sx < 0 else 1
    tip = 128 + sx * 58
    y = 94
    return [P(f'M{f(x0)} 184 V{y + 28} A28 28 0 0 {sweep} {f(xr)} {y} H{f(tip)}'),
            PL([(tip - sx * 28, y - 28), (tip, y), (tip - sx * 28, y + 28)])]


prohibit_sign('sign-no-left-turn', ['no left turn', 'road sign', 'traffic', 'prohibited'], circ_turn(-1), mirror=True)
prohibit_sign('sign-no-right-turn', ['no right turn', 'road sign', 'traffic', 'prohibited'], circ_turn(1))
PCIRC = [L(104, 184, 104, 72), P('M104 72 H136 A32 32 0 0 1 136 136 H104')]
prohibit_sign('sign-no-parking', ['no parking', 'road sign', 'traffic', 'prohibited', 'parking'], PCIRC)

icon('sign-parking', M, ['parking', 'p sign', 'car park', 'road sign', 'p'],
     line=[SQ], detail=[L(100, 184, 100, 72), P('M100 72 H132 A32 32 0 0 1 132 136 H100')], area=[SQ])

# crossbuck: board A full, board B split where it passes under A
s2 = 1 / math.sqrt(2)
ua, ub = (s2, s2), (-s2, s2)  # A runs TL->BR, B runs TR->BL
hb, rb = 104, 20
boardA = capsule((128, 128), hb, rb, ua)


def bpt(along, across):
    # along board B axis, across = along board A axis
    return (128 + ub[0] * along + ua[0] * across, 128 + ub[1] * along + ua[1] * across)


halves = []
for sgn in (-1, 1):
    a_in, a_out = sgn * rb, sgn * hb
    p1, p2, p3, p4 = bpt(a_in, rb), bpt(a_out, rb), bpt(a_out, -rb), bpt(a_in, -rb)
    cap = arc_to(bpt(a_out, 0), rb, p2, p3, lambda m: dist(m, (128, 128)))
    halves.append(f'M{pt(p1)} L{pt(p2)} {cap} L{pt(p4)}')
icon('sign-railroad', M, ['railroad crossing', 'train', 'road sign', 'traffic'],
     line=[P(boardA)] + [P(h) for h in halves],
     area=[P(boardA), P(capsule((128, 128), hb, rb, ub))])

octo = regular_polygon((128, 102), 72, 8, start=-90 + 22.5)
icon('sign-stop', M, ['stop sign', 'octagon', 'road sign', 'traffic'],
     line=[P(rounded_poly(octo, 8)), L(128, 168.5, 128, 224)], detail=[L(100, 102, 156, 102)],
     area=[P(rounded_poly(octo, 8))])

diamond_sign('sign-straight', ['go straight', 'road sign', 'directions'],
             detail=[RL((0, 62), (0, -62)), RL((-26, -36), (0, -62), (26, -36))])
diamond_sign('sign-traffic-light', ['traffic signal ahead', 'road sign', 'traffic light', 'warning'],
             dotcut=[C(128, 86, 16), C(128, 128, 16), C(128, 170, 16)])


def dturn(sx):
    x0 = -sx * 18
    sweep = 0 if sx < 0 else 1
    return [P(f'M{pt(rel(x0, 44))} V{f(128 + 2)} A20 20 0 0 {sweep} {pt(rel(x0 + sx * 20, -18))} H{f(128 + sx * 40)}'),
            RL((sx * 14, -44), (sx * 40, -18), (sx * 14, 8))]


diamond_sign('sign-turn-left', ['turn left', 'road sign', 'direction', 'traffic', 'directions'], detail=dturn(-1))
diamond_sign('sign-turn-right', ['turn right', 'road sign', 'direction', 'traffic', 'directions'], detail=dturn(1))


def dslight(sx):
    return [RL((-sx * 14, 46), (-sx * 14, 6), (sx * 26, -34)), RL((sx * 26 - sx * 30, -34), (sx * 26, -34), (sx * 26, -4))]


diamond_sign('sign-turn-slight-left', ['bear left', 'road sign', 'direction', 'traffic'], detail=dslight(-1))
diamond_sign('sign-turn-slight-right', ['bear right', 'road sign', 'direction', 'traffic'], detail=dslight(1))
diamond_sign('sign-u-turn', ['u-turn', 'turn back', 'directions'],
             detail=[P(f'M{pt(rel(24, 38))} V{f(128 - 8)} A22 22 0 0 0 {pt(rel(-20, -8))} V{f(128 + 24)}'),
                     RL((-42, 2), (-20, 24), (2, 2))])

yld = [(44, 36), (212, 36), (128, 181.5)]
icon('sign-yield', M, ['yield', 'give way', 'road sign', 'triangle'],
     line=[P(rounded_poly(yld, 12)), L(128, 181.5, 128, 224)], area=[P(rounded_poly(yld, 12))])

# ---------------------------------------------------------------- buildings & landmarks
sky = ('M64 216 V104 A8 8 0 0 1 72 96 H96 V64 A8 8 0 0 1 104 56 H152 A8 8 0 0 1 160 64 V96 H184 '
       'A8 8 0 0 1 192 104 V216')
icon('skyscraper', M, ['tower', 'city', 'high-rise'],
     line=[P(sky), L(32, 216, 224, 216), L(128, 32, 128, 56)],
     detail=[L(104, 132, 104, 184), L(152, 132, 152, 184)], area=[P(sky + ' Z')])

wave = lambda y: P(f'M32 {y} Q48 {y - 15} 64 {y} T96 {y} T128 {y} T160 {y} T192 {y} T224 {y}')
pool = [P('M96 136 V64 A20 20 0 0 0 56 64'), P('M168 136 V64 A20 20 0 0 0 128 64'),
        L(96, 88, 168, 88), L(96, 124, 168, 124), wave(176), wave(212)]
icon('swimming-pool', M, ['swimming pool', 'pool', 'ladder', 'water'], line=pool)
icon('swimming-pool-slash', M, ['swimming pool', 'off', 'disabled', 'hidden', 'swimming'], line=pool + [SLASH])

syn = 'M48 216 V112 L128 48 L208 112 V216 Z'
star6 = [PG(regular_polygon((128, 152), 40, 3, -90)), PG(regular_polygon((128, 152), 40, 3, 90))]
icon('synagogue', M, ['synagogue', 'judaism', 'religion', 'worship'], line=[P(syn)], detail=star6, area=[P(syn)])

dome = 'M88 128 C64 104 92 84 112 72 C122 66 128 58 128 48 C128 58 134 66 144 72 C164 84 192 104 168 128 Z'
door = 'M108 216 V180 A20 20 0 0 1 148 180 V216'
icon('taj-mahal', M, ['landmark', 'india', 'palace', 'dome'],
     line=[P('M72 216 V128 H184 V216'), P(dome), L(128, 48, 128, 32), L(24, 216, 232, 216), P(door),
           L(36, 108, 36, 216), L(220, 108, 220, 216)],
     area=[P(dome), R(72, 128, 112, 88)], hole=[P(door + ' Z')], dot=[C(36, 84, 16), C(220, 84, 16)])

roof1 = 'M56 84 Q92 80 108 48 H148 Q164 80 200 84 Z'
roof2 = 'M32 152 Q76 148 84 116 H172 Q180 148 224 152 Z'
tdoor = 'M114 216 V196 A14 14 0 0 1 142 196 V216'
icon('temple', M, ['temple', 'shrine', 'worship', 'pagoda'],
     line=[P(roof1), P(roof2), L(128, 32, 128, 48), L(96, 84, 96, 116), L(160, 84, 160, 116),
           P('M64 152 V216 H192 V152'), P(tdoor)],
     area=[P(roof1), P(roof2), R(96, 84, 64, 32), R(64, 152, 128, 64)], hole=[P(tdoor + ' Z')])

lp = lambda t: (44 + 84 * t, 216 - 144 * t)
rp = lambda t: (212 - 84 * t, 216 - 144 * t)
tdoor2 = 'M104 216 L128 168 L152 216'
icon('tipi', M, ['teepee', 'tent', 'camp'],
     line=[L(*lp(0), *lp(1.22)), L(*rp(0), *rp(1.22)), L(32, 216, 224, 216), P(tdoor2)],
     area=[PG([lp(0), lp(1), rp(0)])], hole=[P(tdoor2 + ' Z')])

# treasure map: a scroll (rolls top and bottom) with a dashed trail to an X
def quad(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


trail = [quad((84, 164), (132, 168), (132, 124), i / 400) for i in range(401)]
acc = [0]
for i in range(1, len(trail)):
    acc.append(acc[-1] + dist(trail[i - 1], trail[i]))


def at(sl):
    for i, a in enumerate(acc):
        if a >= sl:
            return trail[i]
    return trail[-1]


dashes = [L(*at(s0), *at(s0 + 8)) for s0 in (0, 34, 68)]
roll_t = capsule((128, 48), 80, 16, (1, 0))
roll_b = capsule((128, 208), 80, 16, (1, 0))
icon('treasure-map', M, ['treasure', 'map', 'adventure', 'x marks'],
     line=[P(roll_t), P(roll_b), L(56, 64, 56, 192), L(200, 64, 200, 192)],
     detail=dashes + [L(146, 90, 172, 116), L(172, 90, 146, 116)],
     area=[P(roll_t), P(roll_b), R(56, 48, 144, 160)])

# ---------------------------------------------------------------- navigation arrows
icon('turn-left', M, ['turn left', 'direction', 'navigation', 'route'],
     line=[P('M184 216 V136 A48 48 0 0 0 136 88 H64'), PL([(112, 40), (64, 88), (112, 136)])])
icon('turn-right', M, ['turn right', 'direction', 'navigation', 'route'],
     line=[P('M72 216 V136 A48 48 0 0 1 120 88 H192'), PL([(144, 40), (192, 88), (144, 136)])])
icon('turn-slight-left', M, ['bear left', 'keep left', 'ramp', 'direction'],
     line=[PL([(164, 216), (164, 156), (76, 68)]), PL([(76, 124), (76, 68), (132, 68)])])
icon('turn-slight-right', M, ['bear right', 'keep right', 'ramp', 'direction'],
     line=[PL([(92, 216), (92, 156), (180, 68)]), PL([(180, 124), (180, 68), (124, 68)])])
icon('u-turn', M, ['u-turn', 'turn around', 'reverse', 'direction'],
     line=[P('M192 216 V104 A48 48 0 0 0 96 104 V184'), PL([(56, 144), (96, 184), (136, 144)])])

tc, tr = (128, 140), 40
uc = (128, 70)
icon('tv-tower', M, ['tv tower', 'landmark', 'shanghai', 'needle'],
     line=[C(*tc, tr), C(*uc, 22), L(128, 32, 128, 48), L(128, 92, 128, 100),
           L(*polar(tc, tr, 120), 72, 216), L(*polar(tc, tr, 60), 184, 216)],
     area=[C(*tc, tr), C(*uc, 22)])

print(save(overwrite=True))
