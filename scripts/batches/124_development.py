import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DEV = 'Development'
SLASH_A, SLASH_B = (48, 48), (208, 208)
SLASH = L(48, 48, 208, 208)
BADGE = (184, 184)


# ---------------------------------------------------------------- helpers
def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def link(c1, r1, c2, r2):
    """Straight connector between two circle nodes, trimmed to their outlines."""
    u = unit(c1, c2)
    return L(c1[0] + u[0] * r1, c1[1] + u[1] * r1, c2[0] - u[0] * r2, c2[1] - u[1] * r2)


def node_arcs(c, R, nodes, r):
    """Arcs of the ring (c, R) between consecutive nodes (all on the ring), each trimmed by node radius r."""
    out = []
    n = len(nodes)
    angs = [math.degrees(math.atan2(p[1] - c[1], p[0] - c[0])) for p in nodes]
    da = math.degrees(2 * math.asin(r / (2 * R)))  # angle subtended by node radius along the ring
    for i in range(n):
        a1 = angs[i] + da
        a2 = angs[(i + 1) % n] - da
        while a2 < a1:
            a2 += 360
        p, q = polar(c, R, a1), polar(c, R, a2)
        large = 1 if a2 - a1 > 180 else 0
        out.append(P(f'M{pt(p)} A{f(R)} {f(R)} 0 {large} 1 {pt(q)}'))
    return out


def slash_dist(p):
    """Distance of a point from the slash line y = x."""
    return abs(p[0] - p[1]) / math.sqrt(2)


def gap_seg(a, b, gap=24):
    """Pieces of segment a-b that stay at least `gap` from the slash centerline (as L elements)."""
    n = 200
    pts = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
    out, cur = [], []
    for p in pts:
        if slash_dist(p) >= gap:
            cur.append(p)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return [L(s[0][0], s[0][1], s[-1][0], s[-1][1]) for s in out if dist(s[0], s[-1]) > 4]


def mark(kind, c=BADGE):
    x, y = c
    if kind == 'plus':
        return [L(x, y - 26, x, y + 26), L(x - 26, y, x + 26, y)]
    if kind == 'minus':
        return [L(x - 26, y, x + 26, y)]
    return [L(x - 20, y - 20, x + 20, y + 20), L(x + 20, y - 20, x - 20, y + 20)]


def arrow_head(tip, direction_deg, arm=36, spread=45):
    a = polar(tip, arm, direction_deg + 180 - spread)
    b = polar(tip, arm, direction_deg + 180 + spread)
    return PL([a, tip, b])


def bez(Pc, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = Pc
    mt = 1 - t
    return (mt ** 3 * x0 + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t ** 3 * x3,
            mt ** 3 * y0 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t ** 3 * y3)


def split(Pc, t):
    p0, p1, p2, p3 = Pc
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = lerp(p0, p1), lerp(p1, p2), lerp(p2, p3)
    d, e = lerp(a, b), lerp(b, c)
    m = lerp(d, e)
    return [p0, a, d, m], [m, e, c, p3]


def cub(Pc, move=True):
    return (f'M{pt(Pc[0])} ' if move else '') + f'C{pt(Pc[1])} {pt(Pc[2])} {pt(Pc[3])}'


def rrect_badge(x, y, w, h, rx, B=BADGE, Rc=56):
    """Rounded rect whose lower-right corner is cleared for a badge: (open outline, notched area)."""
    x2, y2 = x + w, y + h
    yy = B[1] - math.sqrt(Rc * Rc - (x2 - B[0]) ** 2)   # where the clearance circle meets the right edge
    xx = B[0] - math.sqrt(Rc * Rc - (y2 - B[1]) ** 2)   # ... and the bottom edge
    o = (f'M{f(x2)} {f(yy)} V{f(y + rx)} A{f(rx)} {f(rx)} 0 0 0 {f(x2 - rx)} {f(y)} H{f(x + rx)} '
         f'A{f(rx)} {f(rx)} 0 0 0 {f(x)} {f(y + rx)} V{f(y2 - rx)} A{f(rx)} {f(rx)} 0 0 0 {f(x + rx)} {f(y2)} H{f(xx)}')
    a = o + ' ' + arc_to(B, Rc, (xx, y2), (x2, yy), lambda m: -dist(m, (x + w / 2, y + h / 2))) + ' Z'
    return o, a


# ---------------------------------------------------------------- notebook-code (notebook with code chevrons)
nb = load('notebook')
icon('notebook-code', DEV, ['code notebook', 'journal', 'development', 'code'],
     line=nb['line'], area=nb['area'],
     detail=[nb['detail'][0], PL([(140, 100), (120, 128), (140, 156)]), PL([(172, 100), (192, 128), (172, 156)])])

# ---------------------------------------------------------------- pipeline: three stages in a row
stages = [R(x, 92, 40, 72, 12) for x in (32, 108, 184)]
icon('pipeline', DEV, ['pipeline', 'ci', 'stages', 'workflow'],
     line=stages + [L(72, 128, 108, 128), L(148, 128, 184, 128)], area=stages)

# ---------------------------------------------------------------- qr-code-slash
qr = load('qr-code')
icon('qr-code-slash', DEV, ['qr code', 'off', 'disabled', 'hidden', 'qr'],
     line=qr['line'] + [SLASH],
     dot=[C(188, 68, 16), C(68, 188, 16), C(212, 164, 16), C(164, 212, 16)])

# ---------------------------------------------------------------- regex: dot followed by an asterisk
AST_C, AST_R = (156, 100), 60
ast = [(polar(AST_C, AST_R, a), polar(AST_C, AST_R, a + 180)) for a in (90, 30, 150)]
REGEX_DOT = C(68, 188, 28)
icon('regex', DEV, ['regular expression', 'pattern', 'search', 'code', 'regex'],
     line=[L(p[0], p[1], q[0], q[1]) for p, q in ast], dot=[REGEX_DOT])
rx_lines = []
for p, q in ast:
    rx_lines += gap_seg(p, q)
icon('regex-slash', DEV, ['regex', 'off', 'disabled', 'hidden'], line=rx_lines + [SLASH], dot=[REGEX_DOT])

# ---------------------------------------------------------------- ER relations (crow's foot notation)
ONE_L = [L(64, 88, 64, 168), L(96, 88, 96, 168)]
ONE_R = [L(256 - 64, 88, 256 - 64, 168), L(256 - 96, 88, 256 - 96, 168)]
MANY_R = [PL([(216, 80), (168, 128), (216, 176)])]
MANY_L = [PL([(40, 80), (88, 128), (40, 176)])]
icon('relation-one-to-one', DEV, ['one to one', 'database', 'relation', 'er diagram'],
     line=[L(32, 128, 224, 128)] + ONE_L + ONE_R)
icon('relation-one-to-many', DEV, ['one to many', 'database', 'relation', 'er diagram'],
     line=[L(32, 128, 216, 128)] + ONE_L + MANY_R)
icon('relation-many-to-many', DEV, ['many to many', 'database', 'relation', 'er diagram'],
     line=[L(40, 128, 216, 128)] + MANY_L + MANY_R)

# ---------------------------------------------------------------- robot-face
HEAD = R(56, 72, 144, 136, 28)
EAR_L = P('M56 116 H44 A12 12 0 0 0 32 128 V152 A12 12 0 0 0 44 164 H56')
EAR_R = P('M200 116 H212 A12 12 0 0 1 224 128 V152 A12 12 0 0 1 212 164 H200')
icon('robot-face', DEV, ['robot face', 'bot', 'ai', 'android head'],
     line=[HEAD, EAR_L, EAR_R, L(128, 72, 128, 52)],
     area=[HEAD, P('M56 116 H44 A12 12 0 0 0 32 128 V152 A12 12 0 0 0 44 164 H56 Z'),
           P('M200 116 H212 A12 12 0 0 1 224 128 V152 A12 12 0 0 1 212 164 H200 Z')],
     detail=[L(104, 168, 152, 168)],
     dot=[C(128, 44, 16)], dotcut=[C(100, 128, 16), C(156, 128, 16)])

# ---------------------------------------------------------------- robot-slash
rb = load('robot')
icon('robot-slash', DEV, ['robot', 'off', 'disabled', 'hidden'],
     line=rb['line'] + rb['detail'] + [SLASH], dot=rb['dot'] + [C(96, 140, 16)])

# ---------------------------------------------------------------- router-slash
rt = load('router')
icon('router-slash', DEV, ['router', 'off', 'disabled', 'hidden'],
     line=rt['line'] + [SLASH], dot=rt['dotcut'])

# ---------------------------------------------------------------- sandbox: open box, sand mound, shovel
BOX = R(32, 144, 192, 72, 14)
MOUND = 'M48 144 C64 116 84 104 100 104 C116 104 136 116 152 144'
BLADE = 'M176 144 V124 A20 20 0 0 1 216 124 V144'
icon('sandbox', DEV, ['sandbox', 'isolated', 'playground', 'test'],
     line=[BOX, P(MOUND), P(BLADE), L(196, 104, 196, 48), L(180, 48, 212, 48)],
     area=[BOX, P(MOUND + ' Z'), P(BLADE + ' Z')], detail=[L(32, 180, 224, 180)])

# ---------------------------------------------------------------- slash-command
SQ = R(32, 32, 192, 192, 16)
icon('slash-command', DEV, ['slash', 'command', 'shortcut', 'prompt'],
     line=[SQ], area=[SQ], detail=[L(152, 80, 104, 176)])

# ---------------------------------------------------------------- stack push / pop
LAYER = PG([(128, 108), (224, 148), (128, 188), (32, 148)])
UNDER = PL([(32, 184), (128, 224), (224, 184)])
icon('stack-push', DEV, ['push', 'stack', 'add top', 'data structure'],
     line=[LAYER, UNDER, L(128, 32, 128, 80), arrow_head((128, 80), 90, 30)], area=[LAYER])
icon('stack-pop', DEV, ['pop', 'stack', 'remove top', 'data structure'],
     line=[LAYER, UNDER, L(128, 80, 128, 32), arrow_head((128, 32), -90, 30)], area=[LAYER])

# ---------------------------------------------------------------- step into / out (debugger)
STEP_DOT = C(128, 192, 32)
icon('step-into', DEV, ['step into', 'debugger', 'debug', 'arrow'],
     line=[L(128, 36, 128, 140), arrow_head((128, 140), 90, 40)], dot=[STEP_DOT])
icon('step-out', DEV, ['step out', 'debugger', 'debug', 'arrow'],
     line=[L(128, 140, 128, 36), arrow_head((128, 36), -90, 40)], dot=[STEP_DOT])

# ---------------------------------------------------------------- terminal badges
tm = load('terminal')
t_o, t_a = rrect_badge(32, 48, 192, 160, 14)
T_PROMPT = PL([(72, 104), (104, 128), (72, 152)])
for kind, tags in (('plus', ['new terminal', 'console', 'add', 'plus']),
                   ('minus', ['terminal', 'remove', 'console', 'minus']),
                   ('x', ['close terminal', 'console', 'error', 'x'])):
    icon(f'terminal-{kind}', DEV, tags, line=[P(t_o)] + mark(kind), area=[P(t_a)],
         detail=[T_PROMPT, L(120, 152, 140, 152)])

# ---------------------------------------------------------------- topologies
NR = 22
bus_nodes = [((64, 64), True), ((128, 192), False), ((192, 64), True)]
bus_line = [L(32, 128, 224, 128)]
for c, up in bus_nodes:
    bus_line.append(L(c[0], 128, c[0], c[1] + (NR if up else -NR)))
icon('topology-bus', DEV, ['bus topology', 'network', 'nodes', 'line'],
     line=bus_line + [C(c[0], c[1], NR) for c, _ in bus_nodes], area=[C(c[0], c[1], NR) for c, _ in bus_nodes])

CORN = [(64, 64), (192, 64), (192, 192), (64, 192)]
CR = 24
mesh_links = []
for i in range(4):
    for j in range(i + 1, 4):
        mesh_links.append(link(CORN[i], CR, CORN[j], CR))
icon('topology-full-mesh', DEV, ['full mesh', 'network', 'nodes', 'connected'],
     line=[C(x, y, CR) for x, y in CORN] + mesh_links, area=[C(x, y, CR) for x, y in CORN])

MN = [(56, 72, 22), (176, 56, 22), (200, 172, 22), (88, 200, 22), (128, 128, 18)]
M_LINKS = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 2), (4, 3), (1, 4)]
icon('topology-mesh', DEV, ['complex topology', 'network', 'nodes', 'mesh'],
     line=[C(x, y, r) for x, y, r in MN] + [link(MN[a][:2], MN[a][2], MN[b][:2], MN[b][2]) for a, b in M_LINKS],
     area=[C(x, y, r) for x, y, r in MN])

RC = (128, 128)
RR = dist(RC, CORN[0])
ring_nodes = [CORN[0], CORN[1], CORN[2], CORN[3]]
icon('topology-ring', DEV, ['ring topology', 'network', 'nodes', 'loop'],
     line=[C(x, y, CR) for x, y in CORN] + node_arcs(RC, RR, ring_nodes, CR + 1),
     area=[C(x, y, CR) for x, y in CORN])

HUB = 28
icon('topology-star', DEV, ['star topology', 'network', 'hub', 'nodes'],
     line=[C(128, 128, HUB)] + [C(x, y, CR) for x, y in CORN] + [link(RC, HUB, c, CR) for c in CORN],
     area=[C(128, 128, HUB)] + [C(x, y, CR) for x, y in CORN])

HUB2, CR2 = 18, 20
icon('topology-star-ring', DEV, ['star ring topology', 'network', 'hub', 'loop'],
     line=[C(128, 128, HUB2)] + [C(x, y, CR2) for x, y in CORN] + node_arcs(RC, RR, ring_nodes, CR2 + 1)
     + [link(RC, HUB2, c, CR2) for c in CORN],
     area=[C(128, 128, HUB2)] + [C(x, y, CR2) for x, y in CORN])

ROOT_N = (128, 60, 24)
KIDS = [(52, 188, 20), (128, 188, 20), (204, 188, 20)]
icon('topology-tree', DEV, ['hierarchy topology', 'network', 'tree', 'nodes'],
     line=[C(*ROOT_N)] + [C(*k) for k in KIDS] + [link(ROOT_N[:2], ROOT_N[2], k[:2], k[2]) for k in KIDS],
     area=[C(*ROOT_N)] + [C(*k) for k in KIDS])

# ---------------------------------------------------------------- tree-structure-slash
ts = load('tree-structure')
icon('tree-structure-slash', DEV, ['tree structure', 'off', 'disabled', 'hidden', 'tree'], line=ts['line'] + [SLASH])

# ---------------------------------------------------------------- user-code: user with code brackets
U_HEAD = C(100, 84, 40)
BODY = [(32, 216), (32, 172), (64, 148), (100, 148)]
BODY2 = [(100, 148), (136, 148), (168, 172), (168, 216)]
BR_L = [(168, 160), (148, 184), (168, 208)]
BR_R = [(204, 160), (224, 184), (204, 208)]


def seg_pt_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def clear_t(Pc, pts, need):
    t = 0
    while t < 1:
        q = bez(Pc, t)
        d = min(seg_pt_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if d < need:
            return max(0, t - 0.005)
        t += 0.005
    return 1


tc = clear_t(BODY2, BR_L, 36)
b2a, _ = split(BODY2, tc)
end = b2a[3]
body_d = cub(BODY) + ' ' + cub(b2a, move=False)
icon('user-code', DEV, ['developer', 'programmer', 'coder'],
     line=[U_HEAD, P(body_d), PL(BR_L), PL(BR_R)],
     area=[U_HEAD, P(body_d + f' L{f(end[0] - 8)} 216 Z')])

# ---------------------------------------------------------------- variable: italic x inside parentheses
def var_geom(dx=0, dy=0, s=1.0, o=(128, 128)):
    T = lambda p: (o[0] + (p[0] - o[0]) * s + dx, o[1] + (p[1] - o[1]) * s + dy)
    pl = [T(p) for p in [(80, 40), (44, 84), (44, 172), (80, 216)]]
    pr = [T(p) for p in [(176, 40), (212, 84), (212, 172), (176, 216)]]
    x1 = [T((108, 96)), T((148, 160))]
    x2 = [T((152, 96)), T((104, 160))]
    return pl, pr, x1, x2


pl, pr, x1, x2 = var_geom()
icon('variable', DEV, ['variable', 'x', 'code', 'math'],
     line=[P(cub(pl)), P(cub(pr)), L(*x1[0], *x1[1]), L(*x2[0], *x2[1])])

vpl, vpr, vx1, vx2 = var_geom(-16, -16, 0.9)
mpts = {'plus': [(BADGE[0], BADGE[1] - 26), (BADGE[0], BADGE[1] + 26), (BADGE[0] - 26, BADGE[1]),
                 (BADGE[0] + 26, BADGE[1])],
        'minus': [(BADGE[0] - 26, BADGE[1]), (BADGE[0] + 26, BADGE[1])]}
for kind, tags in (('plus', ['variable', 'add', 'new', 'create']), ('minus', ['variable', 'remove', 'subtract'])):
    segs = mpts[kind]
    segs = [segs[i:i + 2] for i in range(0, len(segs), 2)]

    def mdist(q):
        return min(seg_pt_dist(q, a, b) for a, b in segs)
    t = 0
    while t < 1 and mdist(bez(vpr, t)) >= 38:
        t += 0.005
    rp, _ = split(vpr, max(0, t - 0.005))
    icon(f'variable-{kind}', DEV, tags,
         line=[P(cub(vpl)), P(cub(rp)), L(*vx1[0], *vx1[1]), L(*vx2[0], *vx2[1])] + mark(kind))

icon('variable-slash', DEV, ['variable', 'off', 'disabled', 'hidden'],
     line=[P(cub(pl)), P(cub(pr)), L(*x2[0], *x2[1]), SLASH])

# ---------------------------------------------------------------- versions: front card, two thinner cards behind
CARD = R(32, 48, 128, 160, 14)
BEHIND = [L(192, 68, 192, 188), L(224, 88, 224, 168)]
icon('versions', DEV, ['versions', 'history', 'stack', 'layers'], line=[CARD] + BEHIND, area=[CARD])
icon('versions-slash', DEV, ['versions', 'off', 'disabled', 'hidden'], line=[CARD] + BEHIND + [SLASH])

# ---------------------------------------------------------------- webhook: three nodes joined by inward-curving links
WC = (128, 146)
WN = [polar(WC, 84, -90 + 120 * i) for i in range(3)]
WR = 22
hooks = []
for i in range(3):
    a, b = WN[i], WN[(i + 1) % 3]
    u = unit(a, b)
    s0 = (a[0] + u[0] * (WR + 2), a[1] + u[1] * (WR + 2))
    e0 = (b[0] - u[0] * (WR + 2), b[1] - u[1] * (WR + 2))
    oc = (a[0] + b[0] - WC[0], a[1] + b[1] - WC[1])  # arc centre mirrored outside the edge
    hooks.append(P(f'M{pt(s0)} ' + arc_to(oc, dist(oc, s0), s0, e0, lambda m: -dist(m, WC))))
WNODES = [C(x, y, WR) for x, y in WN]
icon('webhook', DEV, ['webhook', 'integration', 'callback', 'api'], line=WNODES + hooks, area=WNODES)
icon('webhook-slash', DEV, ['webhook', 'off', 'disabled', 'hidden'], line=WNODES + hooks + [SLASH])

print(save(overwrite=True))
