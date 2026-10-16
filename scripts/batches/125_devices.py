import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build as B_

DV = 'Devices'
SLASH = L(48, 48, 208, 208)


def T(s):
    return [t.strip() for t in s.split(',')]


# ------------------------------------------------------------------ helpers (same badge system as the device batches)
def xf(d, s, src, dst):
    """Scale an absolute path string (M L H V C A Z) by s about src and move src to dst."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cmd = [], 0, None
    X = lambda v: dst[0] + (float(v) - src[0]) * s
    Y = lambda v: dst[1] + (float(v) - src[1]) * s
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCAZ':
            cmd = t; out.append(t); i += 1
            continue
        if cmd in 'ML':
            out.append(f'{f(X(toks[i]))} {f(Y(toks[i + 1]))}'); i += 2
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(toks[i + k]))} {f(Y(toks[i + k + 1]))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'H':
            out.append(f(X(toks[i]))); i += 1
        elif cmd == 'V':
            out.append(f(Y(toks[i]))); i += 1
        elif cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {a} {la} {sw} {f(X(x))} {f(Y(y))}'); i += 7
    return re.sub(r'([MLHVCAZ]) ', r'\1', ' '.join(out))


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, []).extend(v)
    return out


# badge marks: (roles, centreline radius used for clearance)
def m_check(c):
    x, y = c
    return dict(line=[PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 16)])]), 30


def m_arrow(c, up):
    x, y = c
    s = -1 if up else 1
    return dict(line=[L(x, y - 28 * s, x, y + 28 * s), PL([(x - 22, y + 6 * s), (x, y + 28 * s), (x + 22, y + 6 * s)])]), 30


def m_dollar(c):
    x, y = c
    return dict(line=[L(x, y - 38, x, y + 38),
                      P(f'M{f(x + 22)} {f(y - 28)} H{f(x - 6)} A14 14 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A14 14 0 0 1 {f(x + 6)} {f(y + 28)} H{f(x - 22)}')]), 34


def m_gear(c, n=6, rb=25, rt=37):
    pts = []
    for i in range(n):
        t = -90 + i * 360 / n
        pts += [polar(c, rb, t - 22), polar(c, rt, t - 12), polar(c, rt, t + 12), polar(c, rb, t + 22)]
    d = 'M' + pt(pts[0])
    for i in range(n):
        a, b, cc, dd = pts[i * 4:i * 4 + 4]
        if i:
            d += f' A{rb} {rb} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{rb} {rb} 0 0 1 {pt(pts[0])} Z'
    return dict(line=[P(d)], area=[P(d)], dotcut=[C(c[0], c[1], 9)]), 38


HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
def m_heart(c, s=0.36):
    d = xf(HEART, s, (128, 140), c)
    return dict(line=[P(d)], area=[P(d)]), 34


LIGHTNING = 'M144 32 L56 144 H120 L104 224 L200 108 H136 Z'
def m_lightning(c, s=0.4):
    d = xf(LIGHTNING, s, (128, 128), c)
    return dict(line=[P(d)], area=[P(d)]), 36


def m_question(c):
    x, y = c
    k = (x, y - 18)
    a = polar(k, 18, 50)
    return dict(line=[P(f'M{f(x - 18)} {f(y - 18)} A18 18 0 1 1 {pt(a)} C{f(x + 4)} {f(y)} {f(x)} {f(y + 2)} {f(x)} {f(y + 8)} V{f(y + 10)}')],
                dot=[C(x, y + 38, 13)]), 36


def m_warning(c):
    x, y = c
    return dict(line=[L(x, y - 36, x, y + 6)], dot=[C(x, y + 36, 13)]), 36


def m_info(c):
    x, y = c
    return dict(line=[L(x, y - 6, x, y + 36)], dot=[C(x, y - 36, 13)]), 36


def m_share(c):
    x, y = c
    return dict(line=[P(f'M{f(x - 30)} {f(y + 28)} C{f(x - 30)} {f(y - 2)} {f(x - 10)} {f(y - 12)} {f(x + 26)} {f(y - 12)}'),
                      PL([(x + 6, y - 32), (x + 26, y - 12), (x + 6, y + 8)])]), 34


SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
def m_sparkle(c, s=0.36):
    d = xf(SPARK, s, (128, 128), c)
    return dict(line=[P(d)], area=[P(d)]), 34


def m_lock(c):
    x, y = c
    body = R(x - 28, y - 6, 56, 42, 8)
    return dict(line=[body, P(f'M{f(x - 16)} {f(y - 6)} V{f(y - 18)} A16 16 0 0 1 {f(x + 16)} {f(y - 18)} V{f(y - 6)}')],
                area=[body]), 38


def rrect_bitten(b, c, rc):
    """Rounded-rect outline with its lower-right corner bitten by circle (c, rc): (line path, area path, yA)."""
    x, y, w, h, r = b['x'], b['y'], b['w'], b['h'], b['r']
    X, Y = x + w, y + h
    yA = c[1] - math.sqrt(rc * rc - (X - c[0]) ** 2)
    xB = c[0] - math.sqrt(rc * rc - (Y - c[1]) ** 2)
    assert yA > y + r + 4 and xB > x + r + 4, (yA, xB)
    d = (f'M{f(X)} {f(yA)} V{f(y + r)} A{f(r)} {f(r)} 0 0 0 {f(X - r)} {f(y)} H{f(x + r)} '
         f'A{f(r)} {f(r)} 0 0 0 {f(x)} {f(y + r)} V{f(Y - r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(Y)} H{f(xB)}')
    area = d + ' ' + arc_to(c, rc, (xB, Y), (X, yA), lambda m: -dist(m, (x + w / 2, y + h / 2))) + ' Z'
    return P(d), P(area)


# ================================================================== phone
MOB = dict(x=72, y=32, w=112, h=192, r=20)
mob = load('device-mobile')
SPEAKER = L(112, 64, 144, 64)


def dev_badge(name, tags, mark, c=(186, 188), gap=30):
    roles, Rm = mark(c)
    line, area = rrect_bitten(MOB, c, Rm + gap)
    icon(name, DV, tags, **merge(dict(line=[line], area=[area], detail=[SPEAKER]), roles))


def phone(name, tags, detail=(), dotcut=()):
    icon(name, DV, tags, line=mob['line'], detail=mob['detail'] + list(detail), area=mob['area'], dotcut=list(dotcut))


dev_badge('device-mobile-arrow-up', T('device mobile, increase, upload, phone, smartphone'), lambda c: m_arrow(c, True))
dev_badge('device-mobile-check', T('verified phone, mobile ok, phone check, done, device mobile'), m_check)
dev_badge('device-mobile-currency-dollar', T('device mobile, money, price, phone, smartphone'), m_dollar, c=(188, 186))
dev_badge('device-mobile-gear', T('phone settings, mobile settings, configure, phone, device mobile'), m_gear, c=(186, 186), gap=26)
dev_badge('device-mobile-heart', T('device mobile, favorite, like, phone, smartphone'), m_heart)
dev_badge('device-mobile-lightning', T('device mobile, fast, power, phone, smartphone'), m_lightning, c=(188, 185))
dev_badge('device-mobile-info', T('phone info, about device, mobile, phone'), m_info, c=(188, 186))
dev_badge('device-mobile-lock', T('locked phone, screen lock, rotation lock, phone'), m_lock, c=(186, 188), gap=26)

phone('device-mobile-arrow-down', T('mobile download, phone, download, app, download to phone'),
      detail=[L(128, 100, 128, 184), PL([(100, 156), (128, 184), (156, 156)])])
icon('device-mobile-camera', DV, T('phone camera, mobile, camera, smartphone, selfie'),
     line=mob['line'], detail=[C(128, 92, 28)], area=mob['area'])
phone('device-mobile-charging', T('charging phone, battery, power, phone, device mobile'),
      detail=[PL([(140, 104), (108, 148), (148, 140), (116, 184)])])
phone('device-mobile-chat', T('sms, text message, mobile chat, phone, device mobile'),
      detail=[P('M108 108 H148 A8 8 0 0 1 156 116 V148 A8 8 0 0 1 148 156 H120 L100 176 V116 A8 8 0 0 1 108 108 Z')])

# hand holding a phone: thumb in front of the left edge, fingertips peeking out on the right
HP = dict(x=88, y=32, w=96, h=160, r=16)
thumb = 'M72 224 V132 A18 18 0 0 1 108 132 V176'
fingers = 'M184 100 H196 A16 16 0 0 1 196 132 H184 M184 132 H196 A16 16 0 0 1 196 164 H184'
ph_d = 'M88 112 V48 A16 16 0 0 1 104 32 H168 A16 16 0 0 1 184 48 V176 A16 16 0 0 1 168 192 H120'
icon('device-mobile-hand', DV, T('holding phone, hand, mobile, phone'),
     line=[P(ph_d), P(thumb), P(fingers), P('M196 164 C204 188 192 208 176 224')],
     detail=[L(120, 64, 152, 64)],
     area=[P('M88 112 V48 A16 16 0 0 1 104 32 H168 A16 16 0 0 1 184 48 V176 A16 16 0 0 1 168 192 H108 V132 A18 18 0 0 0 88 114 Z')])

# ================================================================== battery
BAT = dict(x=32, y=72, w=168, h=112, r=16)
bat = load('battery')
BODY = R(32, 72, 168, 112, 16)
TERM = L(224, 108, 224, 148)
bars = lambda n: [L(64 + 32 * i, 104, 64 + 32 * i, 152) for i in range(n)]


def battery(name, tags, detail=(), dotcut=()):
    icon(name, DV, tags, line=[BODY, TERM], detail=list(detail), area=[BODY], dotcut=list(dotcut))


def bat_badge(name, tags, mark, c=(186, 188), gap=30):
    roles, Rm = mark(c)
    line, area = rrect_bitten(BAT, c, Rm + gap)
    rc = Rm + gap
    yt = c[1] - math.sqrt(max(rc * rc - (224 - c[0]) ** 2, 0))
    term = [L(224, 108, 224, min(148, yt))] if yt > 124 else []
    icon(name, DV, tags, **merge(dict(line=[line] + term, area=[area]), roles))


battery('battery-low', T('low battery, charge needed, power, battery, low charge'), detail=bars(1))
battery('battery-medium', T('battery, half charge, power, half, charge'), detail=bars(2))
battery('battery-high', T('battery, high charge, power, charge, mostly full'), detail=bars(3))
battery('battery-plus', T('battery saver, power, battery, charge, add power'),
        detail=[L(116, 104, 116, 152), L(92, 128, 140, 128)])
LEAF = 'M56 200 C48 112 104 48 216 40 C224 144 160 208 56 200 Z'
leaf = xf(LEAF, 0.34, (136, 120), (116, 128))
battery('battery-eco', T('eco, battery, green energy'), detail=[P(leaf)])
battery('battery-warning', T('battery alert, low power, battery problem, critical, low'),
        detail=[L(116, 102, 116, 124)], dotcut=[C(116, 152, 11)])
qc = (116, 114); qa = polar(qc, 14, 40)
battery('battery-question', T('battery unknown, status, power, battery'),
        detail=[P(f'M102 114 A14 14 0 1 1 {pt(qa)} L116 132')], dotcut=[C(116, 156, 10)])
battery('battery-share', T('reverse charging, share power, battery, transfer'),
        detail=[P('M86 152 C86 130 100 116 140 116'), PL([(122, 98), (140, 116), (122, 134)])])
bat_badge('battery-sparkle', T('battery, ai, magic, power, charge'), m_sparkle, c=(188, 189), gap=24)
icon('battery-slash', DV, T('battery, disabled, off, power, charge'), line=[BODY, TERM, SLASH])

# ================================================================== bluetooth
RUNE = 'M80 88 L176 168 L128 208 L128 48 L176 88 L80 168'
icon('bluetooth-connected', DV, T('bluetooth, paired, connected, wireless, bluetooth connected'),
     line=[P(RUNE)], dot=[C(42, 128, 14), C(214, 128, 14)])
icon('bluetooth-slash', DV, T('bluetooth off, disabled, wireless, disconnect, disconnected'), line=[P(RUNE), SLASH])

# ================================================================== cell signal
BX = [56, 104, 152, 200]; TOPS = [168, 128, 88, 48]


def signal(n, extra=()):
    line = [L(BX[i], 208, BX[i], TOPS[i]) for i in range(n)] + list(extra)
    dots = [C(BX[i], 208, 10.67) for i in range(n, 4)]
    return dict(line=line, dot=dots)


icon('cell-signal-high', DV, T('signal, reception, cellular, 3 bars, good signal'), **signal(3))
icon('cell-signal-medium', DV, T('signal, reception, cellular, 2 bars, fair signal'), **signal(2))
icon('cell-signal-low', DV, T('weak signal, reception, cellular, 1 bar, low signal'), **signal(1))
icon('cell-signal-none', DV, T('no signal, reception, cellular, 0 bars, empty signal'), **signal(0))
icon('cell-signal-slash', DV, T('no signal, cellular off, signal, slash, cell off'),
     line=[L(56, 208, 56, 168), L(104, 208, 104, 134), L(152, 208, 152, 182), L(152, 122, 152, 88), L(200, 170, 200, 48), SLASH])
icon('cell-signal-x', DV, T('no service, signal lost, cellular, no internet, no data'),
     **signal(2, [L(156, 56, 204, 104), L(204, 56, 156, 104)]))

# ================================================================== towers, antennas
def arc(cc, r, a0, a1):
    p, q = polar(cc, r, a0), polar(cc, r, a1)
    return P(f'M{pt(p)} A{f(r)} {f(r)} 0 0 1 {pt(q)}')


def waves(cc, radii, span):
    out = []
    for r in radii:
        out += [arc(cc, r, -span, span), arc(cc, r, 180 - span, 180 + span)]
    return out


tc = (128, 80)
legs = PL([(84, 224), (128, 104), (172, 224)])
yl = lambda y: (y - 104) * 44 / 120
icon('cell-tower', DV, T('base station, antenna, signal, tower, cell tower'),
     line=[legs, L(128 - yl(152), 152, 128 + yl(216), 216), L(128 + yl(152), 152, 128 - yl(216), 216)]
     + waves(tc, (40, 76), 34),
     dot=[C(128, 80, 16)])

ac = (128, 88)
icon('antenna-signal', DV, T('antenna, transmitter, mast'),
     line=[L(128, 116, 128, 224), L(96, 224, 160, 224)] + waves(ac, (44, 84), 34),
     dot=[C(128, 88, 16)])

DOME = 'M64 208 A64 64 0 0 1 192 208 Z'
RODS = [L(120, 144, 80, 52), L(136, 144, 176, 52)]
icon('antenna', DV, T('antenna, signal, radio, broadcast'),
     line=[P(DOME)] + RODS, area=[P(DOME)], dot=[C(78, 46, 16), C(178, 46, 16)], dotcut=[C(128, 180, 12)])
icon('antenna-slash', DV, T('no signal, antenna off, disconnected, radio'),
     line=[P(DOME)] + RODS + [SLASH], dot=[C(78, 46, 16), C(178, 46, 16)])

PUCK = R(40, 152, 176, 56, 28)
apc = (128, 144)
ap_waves = [arc(apc, 40, -140, -40), arc(apc, 80, -140, -40)]
icon('access-point', DV, T('access point, access, point, devices'),
     line=[PUCK] + ap_waves, area=[PUCK], dotcut=[C(128, 180, 12)])
icon('access-point-slash', DV, T('access point, disabled, off, devices'), line=[PUCK] + ap_waves + [SLASH])

# ================================================================== keys, pads
def rpoly(pts, r):
    """Closed polygon with every corner rounded by radius r (orthogonal polygons)."""
    n = len(pts)
    d = ''
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        a = (p1[0] - p0[0], p1[1] - p0[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        rr = r[i] if isinstance(r, (list, tuple)) else r
        s = (p1[0] - a[0] / la * rr, p1[1] - a[1] / la * rr)
        e = (p1[0] + b[0] / lb * rr, p1[1] + b[1] / lb * rr)
        sweep = 1 if a[0] * b[1] - a[1] * b[0] > 0 else 0
        d += (f'M{pt(s)}' if i == 0 else f' L{pt(s)}')
        if rr:
            d += f' A{f(rr)} {f(rr)} 0 0 {sweep} {pt(e)}'
    return d + ' Z'


DP = [(88, 32), (168, 32), (168, 88), (224, 88), (224, 168), (168, 168), (168, 224), (88, 224), (88, 168),
      (32, 168), (32, 88), (88, 88)]
dpad = rpoly(DP, [14, 14, 0, 14, 14, 0, 14, 14, 0, 14, 14, 0])
tri = lambda c, deg: PG(rot([(c[0], c[1] - 7), (c[0] + 8, c[1] + 5), (c[0] - 8, c[1] + 5)], deg, c))
icon('d-pad', DV, T('d-pad, directional pad, gaming, controller, gamepad'),
     line=[P(dpad)], area=[P(dpad)],
     detail=[tri((128, 62), 0), tri((194, 128), 90), tri((128, 194), 180), tri((62, 128), 270)])

TOPKEY = R(96, 48, 64, 64, 12); ROW = R(32, 144, 192, 64, 12)
icon('arrow-keys', DV, T('keyboard, arrows, navigation, keys'),
     line=[TOPKEY, ROW], area=[TOPKEY, ROW],
     detail=[L(96, 144, 96, 208), L(160, 144, 160, 208),
             tri((128, 80), 0), tri((64, 176), 270), tri((128, 176), 180), tri((192, 176), 90)])

# ================================================================== misc devices
CLOUD = 'M84 192 H180 A44 44 0 0 0 191.06 105.41 A60 60 0 0 0 72.04 113.83 A40 40 0 0 0 84 192 Z'
wc = (128, 166)
icon('cloud-wifi', DV, T('cloud, wifi, wireless, online'),
     line=[P(CLOUD)], area=[P(CLOUD)],
     detail=[arc(wc, 32, -128, -52), arc(wc, 62, -116, -64)], dotcut=[C(128, 166, 12)])

CPU = load('cpu')
icon('cpu-slash', DV, T('cpu, disabled, off, devices'), line=CPU['line'] + CPU['detail'] + [SLASH])
icon('cpu-warning', DV, T('overheating, processor error, chip warning'),
     line=CPU['line'], area=CPU['area'], detail=[L(128, 100, 128, 132)], dotcut=[C(128, 162, 14)])

ring_a, ring_b = polar((128, 128), 88, -66), polar((128, 128), 88, -114)
icon('data-saver', DV, T('data saver, save data, usage, mobile'),
     line=[P(f'M{pt(ring_a)} A88 88 0 1 1 {pt(ring_b)}'), L(128, 92, 128, 164), L(92, 128, 164, 128)])

FOLD = [(40, 64), (128, 40), (216, 64), (216, 192), (128, 216), (40, 192)]
icon('device-foldable', DV, T('foldable, phone, dual screen, fold'),
     line=[PG(FOLD)], area=[PG(FOLD)], detail=[L(128, 40, 128, 216)])

icon('charger', DV, T('charger, power adapter, plug, charging'),
     line=[R(56, 88, 144, 136, 24), L(100, 40, 100, 88), L(156, 40, 156, 88)], area=[R(56, 88, 144, 136, 24)],
     detail=[PL([(140, 124), (108, 160), (148, 152), (116, 188)])])

MON = R(32, 64, 104, 96, 12); TOWER = R(168, 40, 56, 176, 12)
icon('computer-tower', DV, T('desktop pc, tower, computer case, pc, desktop computer'),
     line=[MON, TOWER, L(84, 160, 84, 216), L(56, 216, 112, 216)], area=[MON, TOWER],
     detail=[L(188, 76, 204, 76)], dotcut=[C(196, 180, 12)])

icon('cable', DV, T('cable, cord, connector, wire'),
     line=[R(144, 72, 64, 56, 12), L(160, 32, 160, 72), L(192, 32, 192, 72),
           P('M176 128 V152 C176 196 136 212 104 188 C80 170 56 172 40 196')],
     area=[R(144, 72, 64, 56, 12)])

icon('cable-car', 'Transport', T('cable car, ropeway, gondola, aerial lift, ski lift'),
     line=[L(32, 72, 224, 40), L(128, 56, 128, 96), R(56, 96, 144, 112, 16)], area=[R(56, 96, 144, 112, 16)],
     detail=[R(84, 124, 88, 40, 8), L(128, 124, 128, 164)])

AVR = R(32, 64, 192, 112, 14)
icon('av-receiver', DV, T('amplifier, audio, stereo, hifi'),
     line=[AVR, L(64, 176, 64, 196), L(192, 176, 192, 196)], area=[AVR],
     detail=[C(88, 120, 24), L(136, 100, 188, 100)], dotcut=[C(144, 144, 12), C(180, 144, 12)])

CAM = R(36, 80, 184, 120, 18)
icon('action-camera', DV, T('action camera, gopro, sports cam, video'),
     line=[CAM, P('M164 80 V68 A4 4 0 0 1 168 64 H188 A4 4 0 0 1 192 68 V80')], area=[CAM],
     detail=[C(92, 140, 30), R(148, 116, 40, 28, 6)])

PHL = R(32, 64, 192, 128, 18)
cube = regular_polygon((128, 128), 36, 6)
icon('augmented-reality', DV, T('ar, 3d, virtual, overlay, augmented reality'),
     line=[PHL], area=[PHL],
     detail=[PG(cube), PL([cube[5], (128, 128), cube[1]]), L(128, 128, 128, 164)])
icon('augmented-reality-slash', DV, T('augmented reality, disabled, off, devices'),
     line=[PHL, PG(cube), PL([cube[5], (128, 128), cube[1]]), L(128, 128, 128, 164), SLASH])

# ------------------------------------------------------------------ bounds check
import xml.etree.ElementTree as ET
for ic in ICONS:
    ds = [B_.element_d(ET.fromstring(e)) for role in ('line', 'detail') for e in ic[role]]
    bx = B_.stroke(ds, 16).bounds
    if bx[0] < 23.9 or bx[1] < 23.9 or bx[2] > 232.1 or bx[3] > 232.1:
        print('OUT OF BOUNDS', ic['name'], [round(v, 1) for v in bx])

print(save(overwrite=True))
