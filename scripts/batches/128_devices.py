import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Devices'
SLASH = L(48, 48, 208, 208)


# ----------------------------------------------------------------------- generic helpers
def tf_path(d, fn, s=1.0):
    """Transform an absolute path (M L H V C A Z) by point function fn; arc radii scale by s."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cur, cmd = [], 0, (0, 0), None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == 'Z':
                out.append('Z')
            continue
        if cmd in 'ML':
            cur = (float(toks[i]), float(toks[i + 1])); i += 2
            out.append(f'{cmd}{pt(fn(cur))}')
        elif cmd == 'H':
            cur = (float(toks[i]), cur[1]); i += 1
            out.append(f'L{pt(fn(cur))}')
        elif cmd == 'V':
            cur = (cur[0], float(toks[i])); i += 1
            out.append(f'L{pt(fn(cur))}')
        elif cmd == 'C':
            a = (float(toks[i]), float(toks[i + 1])); b = (float(toks[i + 2]), float(toks[i + 3]))
            cur = (float(toks[i + 4]), float(toks[i + 5])); i += 6
            out.append(f'C{pt(fn(a))} {pt(fn(b))} {pt(fn(cur))}')
        elif cmd == 'A':
            rx, ry, xr, la, sw = (float(v) for v in toks[i:i + 5])
            cur = (float(toks[i + 5]), float(toks[i + 6])); i += 7
            out.append(f'A{f(rx * s)} {f(ry * s)} {f(xr)} {int(la)} {int(sw)} {pt(fn(cur))}')
    return ' '.join(out)


def scaler(c_from, c_to, s):
    return lambda p: (c_to[0] + (p[0] - c_from[0]) * s, c_to[1] + (p[1] - c_from[1]) * s)


def rotator(deg, c=(128, 128), shift=(0, 0)):
    a = math.radians(deg)
    return lambda p: (c[0] + shift[0] + (p[0] - c[0]) * math.cos(a) - (p[1] - c[1]) * math.sin(a),
                      c[1] + shift[1] + (p[0] - c[0]) * math.sin(a) + (p[1] - c[1]) * math.cos(a))


def seg_circle_ts(a, b, c, r):
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy; Bq = 2 * (fx * dx + fy * dy); Cq = fx * fx + fy * fy - r * r
    disc = Bq * Bq - 4 * A * Cq
    if disc <= 0:
        return []
    sq = math.sqrt(disc)
    return sorted(t for t in ((-Bq - sq) / (2 * A), (-Bq + sq) / (2 * A)) if 0 < t < 1)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def clip_polyline(pts, c, r):
    """Parts of an open polyline outside circle (c, r), as point lists."""
    out, cur = [], []
    inside = lambda p: dist(p, c) < r
    if not inside(pts[0]):
        cur = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        for t in seg_circle_ts(a, b, c, r):
            p = lerp(a, b, t)
            if cur:
                cur.append(p); out.append(cur); cur = []
            else:
                cur = [p]
        if not inside(b) and cur:
            cur.append(b)
    if len(cur) > 1:
        out.append(cur)
    return [PL(s) for s in out if len(s) > 1 and dist(s[0], s[-1]) > 4]


def rect_bite(x, y, w, h, rx, B, rc):
    """Rounded rect with circle (B, rc) bitten out. Returns (open line paths, area path)."""
    x1, y1 = x + w, y + h
    prims = [('L', (x + rx, y), (x1 - rx, y))]
    if rx: prims.append(('A', (x1 - rx, y), (x1, y + rx), (x1 - rx, y + rx)))
    prims.append(('L', (x1, y + rx), (x1, y1 - rx)))
    if rx: prims.append(('A', (x1, y1 - rx), (x1 - rx, y1), (x1 - rx, y1 - rx)))
    prims.append(('L', (x1 - rx, y1), (x + rx, y1)))
    if rx: prims.append(('A', (x + rx, y1), (x, y1 - rx), (x + rx, y1 - rx)))
    prims.append(('L', (x, y1 - rx), (x, y + rx)))
    if rx: prims.append(('A', (x, y + rx), (x + rx, y), (x + rx, y + rx)))
    pieces = []
    for pr in prims:
        if pr[0] == 'L':
            a, b = pr[1], pr[2]
            ts = [0] + seg_circle_ts(a, b, B, rc) + [1]
            for t0, t1 in zip(ts, ts[1:]):
                p, q = lerp(a, b, t0), lerp(a, b, t1)
                vis = dist(lerp(a, b, (t0 + t1) / 2), B) >= rc
                pieces.append(('L', p, q, vis))
        else:
            a, b, cc = pr[1], pr[2], pr[3]
            m = polar(cc, rx, math.degrees(math.atan2((a[1] + b[1]) / 2 - cc[1], (a[0] + b[0]) / 2 - cc[0])))
            pieces.append(('A', a, b, dist(m, B) >= rc))
    if all(p[3] for p in pieces):
        return [R(x, y, w, h, rx)], R(x, y, w, h, rx)
    k = next(i for i in range(len(pieces)) if pieces[i][3] and not pieces[i - 1][3])
    pieces = pieces[k:] + pieces[:k]
    runs, cur = [], []
    for p in pieces:
        if p[3]:
            cur.append(p)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)

    def run_d(run, move=True):
        d = f'M{pt(run[0][1])}' if move else ''
        for p in run:
            if dist(p[1], p[2]) < 0.01:
                continue
            d += f' L{pt(p[2])}' if p[0] == 'L' else f' A{f(rx)} {f(rx)} 0 0 1 {pt(p[2])}'
        return d.strip()
    cen = (x + w / 2, y + h / 2)
    lines = [P(run_d(r)) for r in runs if not (len(r) == 1 and dist(r[0][1], r[0][2]) < 4)]
    ad = ''
    for j, r in enumerate(runs):
        ad += (' ' if ad else '') + run_d(r, move=(j == 0))
        nxt = runs[(j + 1) % len(runs)][0][1]
        ad += ' ' + arc_to(B, rc, r[-1][2], nxt, lambda m: -dist(m, cen))
    return lines, P(ad + ' Z')


def arrowhead(tip, back_dir_deg, size=24, spread=45):
    a = polar(tip, size * math.sqrt(2), back_dir_deg - spread)
    b = polar(tip, size * math.sqrt(2), back_dir_deg + spread)
    return PL([a, tip, b])


def star_pts(c, ro, ri):
    return [polar(c, ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]


def bolt(c, s=1.0):
    pts = [(10, -36), (-20, 4), (4, 4), (-8, 36), (22, -6), (-2, -6)]
    return [(c[0] + x * s, c[1] + y * s) for x, y in pts]


def gear_path(c, r_in, r_out, n=6, half_base=18, half_top=11):
    pts = []
    for i in range(n):
        t = -90 + i * 360 / n
        pts += [polar(c, r_in, t - half_base), polar(c, r_out, t - half_top),
                polar(c, r_out, t + half_top), polar(c, r_in, t + half_base)]
    d = 'M' + pt(pts[0])
    for i in range(n):
        a, b, cc, dd = pts[i * 4:i * 4 + 4]
        if i:
            d += f' A{f(r_in)} {f(r_in)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    return d + f' A{f(r_in)} {f(r_in)} 0 0 1 {pt(pts[0])} Z'


SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
CLOUD = 'M84 192 H180 A44 44 0 0 0 191.06 105.41 A60 60 0 0 0 72.04 113.83 A40 40 0 0 0 84 192 Z'

# ----------------------------------------------------------------------- monitor (from monitor.svg) + badges
MON = (32, 48, 192, 128, 14)
MON_STAND = [L(128, 176, 128, 208), L(88, 208, 168, 208)]
B = (188, 188)


def mon_badge(name, tags, marks, rc=60, mark_area=(), mark_hole=(), mark_dot=(), mark_detail=()):
    ln, ar = rect_bite(*MON, B, rc)
    stand = clip_polyline([(128, 176), (128, 208)], B, rc) + clip_polyline([(88, 208), (168, 208)], B, rc)
    icon(name, CAT, tags, line=ln + stand + list(marks), area=[ar] + list(mark_area), hole=list(mark_hole),
         dot=list(mark_dot), detail=list(mark_detail))


mon_badge('monitor-arrow-down', ['monitor', 'decrease', 'download', 'desktop', 'computer'],
          [L(188, 158, 188, 216), PL([(164, 192), (188, 216), (212, 192)])])
mon_badge('monitor-arrow-up', ['share screen', 'cast', 'upload', 'monitor', 'increase'],
          [L(188, 218, 188, 160), PL([(164, 184), (188, 160), (212, 184)])])
mon_badge('monitor-check', ['computer ok', 'system healthy', 'verified', 'monitor', 'done'],
          [PL([(162, 190), (180, 208), (214, 172)])])
mon_badge('monitor-code', ['monitor', 'developer', 'code', 'desktop', 'computer'],
          [PL([(172, 166), (152, 188), (172, 210)]), PL([(204, 166), (224, 188), (204, 210)])])
mon_badge('monitor-currency-dollar', ['monitor', 'money', 'price', 'desktop', 'computer'],
          [P('M204 164 H184 A12 12 0 0 0 184 188 H192 A12 12 0 0 1 192 212 H172'),
           L(188, 152, 188, 164), L(188, 212, 188, 224)])
gp = gear_path(B, 22, 34, 6, 20, 12)
mon_badge('monitor-gear', ['monitor', 'settings', 'configure', 'desktop', 'computer'],
          [P(gp)], mark_area=[P(gp)], mark_hole=[C(188, 188, 8)])
hs = tf_path(HEART, scaler((128, 145), (188, 190), 0.32), 0.32)
mon_badge('monitor-heart', ['monitor', 'favorite', 'like', 'desktop', 'computer'], [P(hs)], mark_area=[P(hs)])
bl = bolt((188, 188), 0.8)
mon_badge('monitor-lightning', ['monitor', 'fast', 'power', 'desktop', 'computer'], [PG(bl)], mark_area=[PG(bl)])
mon_badge('monitor-magnifying-glass', ['monitor', 'search', 'find', 'desktop', 'computer'],
          [C(182, 182, 20), L(196, 196, 212, 212)], mark_area=[C(182, 182, 20)])
mon_badge('monitor-minus', ['monitor', 'remove', 'subtract', 'desktop', 'computer'], [L(160, 188, 216, 188)])
mon_badge('monitor-pause', ['monitor', 'paused', 'hold', 'desktop', 'computer'],
          [L(172, 164, 172, 212), L(204, 164, 204, 212)])
mon_badge('monitor-plus', ['add display', 'add to queue', 'screen', 'new', 'new computer'],
          [L(160, 188, 216, 188), L(188, 160, 188, 216)])
pin_body = [(176, 154), (200, 154), (200, 174), (212, 194), (164, 194), (176, 174)]
mon_badge('monitor-push-pin', ['monitor', 'pinned', 'pin', 'desktop', 'computer'],
          [PG(pin_body), L(168, 154, 208, 154), L(188, 194, 188, 222)], mark_area=[PG(pin_body)])
mon_badge('monitor-question', ['monitor', 'help', 'unknown', 'desktop', 'computer'],
          [P('M172 164 A18 18 0 1 1 200 179 C194 183 190 187 190 194')], mark_dot=[C(190, 216, 16)])
mon_badge('monitor-share', ['monitor', 'share', 'send', 'desktop', 'computer'],
          [P('M164 216 V200 A24 24 0 0 1 188 176 H212'), PL([(196, 160), (212, 176), (196, 192)])])
st = star_pts((188, 190), 32, 14)
mon_badge('monitor-star', ['monitor', 'favorite', 'starred', 'desktop', 'computer'], [PG(st)], mark_area=[PG(st)])
mon_badge('monitor-warning', ['computer error', 'system alert', 'crash', 'monitor', 'warning'],
          [L(188, 156, 188, 186)], mark_dot=[C(188, 214, 16)])
mon_badge('monitor-x', ['monitor', 'remove', 'cancel', 'desktop', 'computer'],
          [L(168, 168, 208, 208), L(208, 168, 168, 208)])

icon('monitor-slash', CAT, ['screen off', 'display', 'monitor', 'disabled', 'display off'],
     line=[R(*MON)] + MON_STAND + [SLASH])
cl = tf_path(CLOUD, scaler((134, 124), (128, 112), 0.5), 0.5)
icon('monitor-cloud', CAT, ['cloud desktop', 'monitor', 'remote', 'sync'],
     line=[R(*MON)] + MON_STAND, detail=[P(cl)], area=[R(*MON)])

# ----------------------------------------------------------------------- printer (from printer.svg)
PR_BODY = ('M72 184 H48 A16 16 0 0 1 32 168 V104 A16 16 0 0 1 48 88 H208 A16 16 0 0 1 224 104 V168 '
           'A16 16 0 0 1 208 184 H184')
rcp = 60
body_ln, body_ar = rect_bite(32, 88, 192, 96, 16, B, rcp)
tray_ln, tray_ar = rect_bite(72, 144, 112, 72, 4, B, rcp)
_, tray_hole = rect_bite(80, 152, 96, 56, 0, B, rcp)
# body outline without the stretch hidden behind the paper tray: keep left run, drop part between tray edges
icon('printer-plus', CAT, ['add printer', 'printer', 'new device', 'plus'],
     line=[P('M72 184 H48 A16 16 0 0 1 32 168 V104 A16 16 0 0 1 48 88 H208 A16 16 0 0 1 224 104 V140'),
           P('M72 88 V40 H184 V88')] + tray_ln + [L(160, 188, 216, 188), L(188, 160, 188, 216)],
     area=[body_ar, R(72, 40, 112, 48), tray_ar], hole=[tray_hole], dotcut=[C(192, 116, 12)])
icon('printer-slash', CAT, ['printer off', 'print disabled', 'no print', 'printer', 'no printing'],
     line=[P('M72 88 V40 H184 V88'), P(PR_BODY), R(72, 144, 112, 72, 4), SLASH], dot=[C(192, 116, 12)])

# ----------------------------------------------------------------------- laser pointer
u45 = (math.sqrt(.5), -math.sqrt(.5))
lp = capsule((88, 168), 44, 24, u45)
icon('laser-pointer', CAT, ['laser pointer', 'presentation', 'pointer', 'beam'],
     line=[P(lp), L(154, 102, 160, 96), L(180, 46, 180, 34), L(*polar((180, 76), 30, -45), *polar((180, 76), 42, -45)),
           L(210, 76, 222, 76)],
     area=[P(lp)], dot=[C(180, 76, 13)], dotcut=[C(88, 168, 10)])

# ----------------------------------------------------------------------- memory
icon('memory', CAT, ['ram', 'memory', 'chip', 'hardware', 'stick'],
     line=[R(32, 64, 192, 104, 14)] + [L(x, 168, x, 192) for x in (64, 96, 160, 192)],
     detail=[R(64, 92, 48, 44, 6), R(144, 92, 48, 44, 6)], area=[R(32, 64, 192, 104, 14)])

# ----------------------------------------------------------------------- mobile data
# down arrow left, up arrow right: the slash then crosses only the two shafts, never an arrowhead
MD = [L(88, 40, 88, 216), PL([(52, 180), (88, 216), (124, 180)]), L(168, 216, 168, 40), PL([(132, 76), (168, 40), (204, 76)])]
icon('mobile-data', CAT, ['mobile data', 'cellular', 'up down', 'network'], line=MD)
icon('mobile-data-slash', CAT, ['mobile data off', 'cellular off', 'network', 'disabled'], line=MD + [SLASH])

# ----------------------------------------------------------------------- modem
icon('modem', CAT, ['modem', 'internet', 'router', 'network'],
     line=[R(32, 72, 192, 96, 16), L(64, 168, 64, 188), L(192, 168, 192, 188)], area=[R(32, 72, 192, 96, 16)],
     dotcut=[C(x, 120, 12) for x in (80, 112, 144, 176)])

# ----------------------------------------------------------------------- motherboard
icon('motherboard', CAT, ['motherboard', 'mainboard', 'hardware', 'computer'],
     line=[R(32, 32, 192, 192, 14)],
     detail=[R(72, 72, 56, 56, 8), L(164, 72, 164, 128), L(196, 72, 196, 128), L(72, 176, 152, 176)],
     area=[R(32, 32, 192, 192, 14)], dotcut=[C(192, 176, 14)])

# ----------------------------------------------------------------------- mouse (from mouse.svg)
MS = R(72, 32, 112, 192, 56)
LEFT_BTN = 'M128 136 H72 V88 A56 56 0 0 1 128 32 Z'
RIGHT_BTN = 'M128 136 H184 V88 A56 56 0 0 0 128 32 Z'
DIV = [L(128, 32, 128, 136), L(72, 136, 184, 136)]
icon('mouse-left-click', CAT, ['left click', 'mouse', 'select', 'mouse button', 'primary click'],
     line=[MS] + DIV, area=[P(LEFT_BTN)])
icon('mouse-right-click', CAT, ['right click', 'context menu', 'mouse', 'secondary click'],
     line=[MS] + DIV, area=[P(RIGHT_BTN)])
WHEEL = R(112, 60, 32, 48, 16)
icon('mouse-middle-click', CAT, ['middle click', 'mouse', 'wheel'],
     line=[MS, L(128, 32, 128, 60), L(128, 108, 128, 136), L(72, 136, 184, 136), WHEEL], area=[WHEEL])
icon('mouse-scroll', CAT, ['scroll', 'mouse wheel', 'scroll wheel'],
     line=[MS], detail=[PL([(112, 76), (128, 60), (144, 76)]), L(128, 108, 128, 132), PL([(112, 164), (128, 180), (144, 164)])],
     area=[MS])
icon('mouse-slash', CAT, ['mouse', 'off', 'disabled', 'hidden'], line=[MS, L(128, 72, 128, 104), SLASH])

# ----------------------------------------------------------------------- nfc
NFC_SQ = R(32, 32, 192, 192, 40)
NFC_N = 'M84 172 V100 C84 78 108 74 118 94 L138 162 C148 182 172 178 172 156 V84'
icon('nfc', CAT, ['nfc', 'near field', 'tap', 'contactless'], line=[NFC_SQ], detail=[P(NFC_N)], area=[NFC_SQ])
icon('nfc-slash', CAT, ['nfc off', 'contactless off', 'tap', 'disabled'], line=[NFC_SQ, P(NFC_N), SLASH])

# ----------------------------------------------------------------------- numpad
icon('numpad', CAT, ['keypad', 'number pad', 'dial pad', 'numpad', 'phone keypad'],
     dot=[C(x, y, 18) for y in (56, 104, 152, 200) for x in (80, 128, 176)])

# ----------------------------------------------------------------------- desk phone
HANDSET = ('M48 112 L40 80 C40 56 80 40 128 40 C176 40 216 56 216 80 L208 112 H168 L160 84 '
           'C140 79 116 79 96 84 L88 112 Z')
DESK = R(48, 112, 160, 96, 16)
icon('phone-desk', CAT, ['desk phone', 'landline', 'office phone', 'telephone'],
     line=[P(HANDSET), DESK], area=[P(HANDSET), DESK],
     dotcut=[C(x, y, 10) for y in (144, 176) for x in (96, 128, 160)])

# ----------------------------------------------------------------------- phone sparkle (marks sit in the phone family's free upper-right)
PH = 'M64 40 H96 L112 92 L88 112 C108 132 124 148 144 168 L164 144 L216 160 V192 A24 24 0 0 1 192 216 C104 216 40 152 40 64 A24 24 0 0 1 64 40 Z'
spk = tf_path(SPARK, scaler((128, 128), (180, 76), 0.36), 0.36)
icon('phone-sparkle', CAT, ['phone', 'ai', 'magic', 'smart'], line=[P(PH), P(spk)], area=[P(PH), P(spk)])

# ----------------------------------------------------------------------- plugs (from plug.svg)
PLUG = 'M64 72 H192 V120 A64 64 0 0 1 64 120 Z'
PLUG_L = [P(PLUG), L(104, 32, 104, 72), L(152, 32, 152, 72), L(128, 184, 128, 224)]
icon('plug-charging', CAT, ['charging', 'power plug', 'electricity'],
     line=PLUG_L, detail=[P('M138 100 L114 130 L142 124 L118 156')], area=[P(PLUG)])
icon('plug-x', CAT, ['disconnected', 'plug', 'error', 'power'],
     line=PLUG_L, detail=[L(108, 104, 148, 144), L(148, 104, 108, 144)], area=[P(PLUG)])
icon('plug-slash', CAT, ['unplugged', 'disconnected', 'power off', 'offline'], line=PLUG_L + [SLASH])

FACE = R(40, 40, 176, 176, 56)
icon('plug-type-a', CAT, ['us plug', 'socket type a', 'power plug'],
     line=[FACE], detail=[L(100, 96, 100, 160), L(156, 96, 156, 160)], area=[FACE])
icon('plug-type-c', CAT, ['euro plug', 'socket type c', 'power plug'],
     line=[FACE], area=[FACE], dotcut=[C(92, 128, 18), C(164, 128, 18)])
icon('plug-type-g', CAT, ['uk plug', 'socket type g', 'power plug'],
     line=[FACE], detail=[L(128, 80, 128, 116), L(80, 168, 112, 168), L(144, 168, 176, 168)], area=[FACE])
icon('plug-type-l', CAT, ['italian plug', 'socket type l', 'power plug'],
     line=[FACE], area=[FACE], dotcut=[C(x, 128, 16) for x in (80, 128, 176)])


def rrect_d(x0, y0, x1, y1, r):
    return (f'M{x0 + r} {y0} H{x1 - r} A{r} {r} 0 0 1 {x1} {y0 + r} V{y1 - r} A{r} {r} 0 0 1 {x1 - r} {y1} '
            f'H{x0 + r} A{r} {r} 0 0 1 {x0} {y1 - r} V{y0 + r} A{r} {r} 0 0 1 {x0 + r} {y0} Z')


def plug_pair(face):
    """Socket on the left, plug with two prongs on the right, faces at 128 -/+ face; rotated to run diagonally."""
    fn = rotator(-45)
    T = lambda d: P(tf_path(d, fn))
    sock = rrect_d(128 - face - 52, 96, 128 - face, 160, 12)
    plug = rrect_d(128 + face, 96, 128 + face + 52, 160, 12)
    ln = [T(sock), T(plug), T(f'M{128 - face - 52} 128 L16 128'), T(f'M{128 + face + 52} 128 L240 128')]
    pr = [T(f'M{128 + face} {112} L{128 + face - (2 * face if face < 30 else 32)} 112'),
          T(f'M{128 + face} {144} L{128 + face - (2 * face if face < 30 else 32)} 144')]
    return ln + pr, [T(sock), T(plug)]


ln, ar = plug_pair(36)
icon('plugs', CAT, ['unplugged', 'disconnected', 'plug and socket'], line=ln, area=ar)
ln, ar = plug_pair(20)
icon('plugs-connected', CAT, ['plugged in', 'connected', 'power on', 'plug connect', 'power'], line=ln, area=ar)

# ----------------------------------------------------------------------- ports
DVI = [(32, 80), (224, 80), (224, 136), (192, 176), (64, 176), (32, 136)]
icon('port-dvi', CAT, ['dvi', 'video port', 'connector', 'display'], line=[PG(DVI)], area=[PG(DVI)],
     dotcut=[C(x, y, 10) for y in (112, 144) for x in (80, 112, 144, 176)])
USBC = R(32, 88, 192, 80, 40)
icon('port-usb-c', CAT, ['usb-c', 'type-c', 'connector', 'charging', 'usb c'],
     line=[USBC], detail=[L(80, 128, 176, 128)], area=[USBC])
MICRO = [(40, 88), (216, 88), (216, 120), (176, 168), (80, 168), (40, 120)]
icon('port-usb-micro', CAT, ['micro usb', 'connector', 'port', 'cable'],
     line=[PG(MICRO)], detail=[L(96, 124, 160, 124)], area=[PG(MICRO)])

# ----------------------------------------------------------------------- power
PB = R(64, 32, 128, 192, 20)
icon('power-bank', CAT, ['power bank', 'portable charger', 'battery', 'charging'],
     line=[PB], detail=[P('M142 84 L112 124 L146 118 L116 158'), L(112, 190, 144, 190)], area=[PB])
HEAD = R(96, 56, 64, 40, 12); BRICK = R(32, 128, 192, 80, 16)
icon('power-supply', CAT, ['power supply', 'psu', 'adapter', 'charger'],
     line=[HEAD, BRICK, L(112, 32, 112, 56), L(144, 32, 144, 56), L(128, 96, 128, 128)],
     area=[HEAD, BRICK], dotcut=[C(184, 168, 12)])

print(save(overwrite=True))
