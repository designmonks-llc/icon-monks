import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DV, BZ = 'Devices', 'Business'
SLASH = L(48, 48, 208, 208)


# ======================================================================= stroke lettering (as batch 105)
def g_E(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b), (x + w, b)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_L(x, t, w, h):
    return [PL([(x, t), (x, t + h), (x + w, t + h)])]


def g_T(x, t, w, h):
    return [L(x, t, x + w, t), L(x + w / 2, t, x + w / 2, t + h)]


def g_G(x, t, w, h):
    r = w / 2
    ct = (x + r, t + r)
    s = polar(ct, r, -20)
    yb = t + h * 0.54
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 '
              f'{f(x + w)} {f(t + h - r)} V{f(yb)} H{f(x + w * 0.55)}')]


def g_2(x, t, w, h):
    r = w / 2
    c = (x + r, t + r)
    s, e = polar(c, r, 200), polar(c, r, 35)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 1 1 {pt(e)} L{f(x)} {f(t + h)} H{f(x + w)}')]


def bowl_low(x, t, w, h):
    Rb = h * 0.3
    c = (x + w - Rb, t + h - Rb)
    return Rb, c, polar(c, Rb, 150)


def g_3(x, t, w, h):
    Rb, c, e = bowl_low(x, t, w, h)
    return [P(f'M{f(x)} {f(t)} H{f(x + w)} L{f(c[0])} {f(c[1] - Rb)} A{f(Rb)} {f(Rb)} 0 1 1 {pt(e)}')]


def g_5(x, t, w, h):
    Rb, c, e = bowl_low(x, t, w, h)
    return [P(f'M{f(x + w)} {f(t)} H{f(x)} V{f(c[1] - Rb)} H{f(c[0])} A{f(Rb)} {f(Rb)} 0 1 1 {pt(e)}')]


def g_4(x, t, w, h):
    yb = t + h * 0.64
    return [PL([(x + w * 0.42, t), (x, yb), (x + w, yb)]), L(x + w * 0.74, t + h * 0.36, x + w * 0.74, t + h)]


GLYPH = {'E': g_E, 'L': g_L, 'T': g_T, 'G': g_G, '2': g_2, '3': g_3, '4': g_4, '5': g_5}


def text(s, widths, gap, h, cx=128, cy=128):
    total = sum(widths) + gap * (len(s) - 1)
    x = cx - total / 2
    out = []
    for ch, w in zip(s, widths):
        out += GLYPH[ch](x, cy - h / 2, w, h)
        x += w + gap
    return out


FRAME = R(32, 56, 192, 144, 20)  # lettered badge frame, as batch 105

# ======================================================================= projector
PJ_BODY = R(32, 72, 192, 112, 16)
icon('projector', DV, ['video projector', 'beamer', 'presentation', 'projector', 'beam'],
     line=[PJ_BODY, L(64, 184, 64, 208), L(192, 184, 192, 208)],
     detail=[C(164, 128, 28), L(64, 112, 96, 112), L(64, 144, 96, 144)],
     area=[PJ_BODY])

SCR = 'M48 48 V156 A12 12 0 0 0 60 168 H196 A12 12 0 0 0 208 156 V48'
SCR_LINE = [L(32, 48, 224, 48), P(SCR), L(128, 168, 128, 192), L(128, 32, 128, 48)]
icon('projector-screen', BZ, ['screen', 'presentation', 'projection'],
     line=SCR_LINE, area=[P(SCR + ' Z')], dot=[C(128, 208, 16)])
icon('projector-screen-chart', BZ, ['presentation', 'report', 'slides'],
     line=SCR_LINE, detail=[L(92, 136, 92, 112), L(128, 136, 128, 84), L(164, 136, 164, 100)],
     area=[P(SCR + ' Z')], dot=[C(128, 208, 16)])

# ======================================================================= circular arrow family
AC, AR = (128, 136), 84
a_end = polar(AC, AR, -45)
ARC = [P(f'M{pt(polar(AC, AR, 0))} A{AR} {AR} 0 1 1 {pt(a_end)}'),
       PL([(a_end[0] - 44, a_end[1]), a_end, (a_end[0], a_end[1] - 44)])]
bolt0 = [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]
bolt = [(AC[0] + (x - 128) * 0.44, AC[1] + (y - 128) * 0.44) for x, y in bolt0]
icon('recharging', DV, ['recharging', 'charging', 'battery cycle', 'power'],
     line=ARC + [PG(bolt)], area=[PG(bolt)])
LKB = R(100, 128, 56, 44, 8)
icon('rotate-lock', DV, ['rotation lock', 'screen lock', 'orientation', 'lock'],
     line=ARC + [LKB, P('M110 128 V116 A18 18 0 0 1 146 116 V128')], area=[LKB])

# ======================================================================= remote control
RC = R(80, 32, 96, 192, 24)
icon('remote-control', DV, ['remote', 'tv remote', 'control', 'buttons', 'controller'],
     line=[RC], detail=[C(128, 84, 20)], area=[RC],
     dotcut=[C(108, 140, 12), C(148, 140, 12), C(108, 180, 12), C(148, 180, 12)])

# ======================================================================= scanner / shredder
SC_BODY = R(32, 128, 192, 72, 14)
SC_PAPER = [(84, 128), (100, 40), (192, 56), (180, 128)]
icon('scanner', DV, ['scanner', 'document scanner', 'adf', 'office', 'flatbed'],
     line=[SC_BODY, PL(SC_PAPER)],
     detail=[L(118, 80, 162, 88), L(72, 164, 136, 164)], area=[SC_BODY, PG(SC_PAPER)], dotcut=[C(184, 164, 12)])

SH_BODY = R(32, 96, 192, 80, 14)
icon('shredder', DV, ['shredder', 'destroy paper', 'office', 'confidential'],
     line=[SH_BODY, PL([(72, 96), (72, 40), (184, 40), (184, 96)])] + [L(x, 204, x, 224) for x in (80, 112, 144, 176)],
     detail=[L(104, 68, 152, 68), L(72, 136, 136, 136)], area=[SH_BODY, R(72, 40, 112, 56)], dotcut=[C(184, 136, 12)])

# ======================================================================= screen share / screenshot
MON = load('monitor')
UP = [L(128, 148, 128, 84), PL([(100, 112), (128, 84), (156, 112)])]
icon('screen-share', DV, ['screen share', 'cast', 'present', 'monitor'],
     line=MON['line'], detail=UP, area=MON['area'])
def gap_pts(pts, g=22, step=0.5):
    """Split a polyline where it passes within g of the slash centreline."""
    out, cur = [], []
    dense = []
    for a, b_ in zip(pts, pts[1:]):
        k = max(1, int(dist(a, b_) / step))
        dense += [(a[0] + (b_[0] - a[0]) * i / k, a[1] + (b_[1] - a[1]) * i / k) for i in range(k)]
    dense.append(pts[-1])
    for q in dense:
        if abs(q[0] - q[1]) / math.sqrt(2) >= g:
            cur.append(q)
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = []
    for c_ in out:
        if dist(c_[0], c_[-1]) < 6:
            continue
        keep = [c_[0]] + [q for q in c_[1:-1] if q in pts] + [c_[-1]]
        res.append(PL(keep))
    return res


icon('screen-share-slash', DV, ['stop sharing', 'screen share off', 'present', 'monitor'],
     line=MON['line'] + UP + [SLASH])

CAM = ('M72 116 A16 16 0 0 1 88 100 H100 L112 84 H144 L156 100 H168 A16 16 0 0 1 184 116 V160 '
       'A16 16 0 0 1 168 176 H88 A16 16 0 0 1 72 160 Z')
icon('screenshot', DV, ['screenshot', 'capture', 'screen', 'snip', 'screen grab'],
     line=[P('M40 88 V56 A16 16 0 0 1 56 40 H88'), P('M168 40 H200 A16 16 0 0 1 216 56 V88'),
           P('M216 168 V200 A16 16 0 0 1 200 216 H168'), P('M88 216 H56 A16 16 0 0 1 40 200 V168'), P(CAM)],
     detail=[C(128, 138, 14)], area=[P(CAM)])

# ======================================================================= network badges
for nm, s, tags in [('signal-2g', '2G', ['2g', 'mobile network', 'signal', 'cellular']),
                    ('signal-3g', '3G', ['3g', 'mobile network', 'signal', 'cellular', 'mobile data']),
                    ('signal-4g', '4G', ['4g', 'mobile network', 'signal', 'cellular', 'lte']),
                    ('signal-5g', '5G', ['5g', 'mobile network', 'signal', 'cellular', 'mobile data'])]:
    icon(nm, DV, tags, line=[FRAME], detail=text(s, [40, 40], 28, 64), area=[FRAME])
icon('signal-lte', DV, ['lte', 'mobile network', 'signal', 'cellular'],
     line=[FRAME], detail=text('LTE', [28, 36, 28], 22, 64), area=[FRAME])

# ======================================================================= sim card slash
SIM = load('sim-card')
icon('sim-card-slash', DV, ['no sim', 'sim card', 'disabled', 'slash', 'sim missing'],
     line=SIM['line'] + SIM['detail'] + [SLASH])

# ======================================================================= speakers
SS = 'M72 68 V188 A56 28 0 0 0 184 188 V68'
icon('smart-speaker', DV, ['smart speaker', 'voice assistant', 'home speaker', 'speaker'],
     line=[P(SS), E(128, 68, 56, 28)], area=[P(SS + ' A56 28 0 0 0 72 68 Z')],
     dotcut=[C(102, 68, 9), C(128, 68, 9), C(154, 68, 9)])

BAR = R(68, 100, 120, 56, 18)
SWC = (128, 128)
waves = [P(f'M{pt(polar(SWC, 92, -24))} A92 92 0 0 1 {pt(polar(SWC, 92, 24))}'),
         P(f'M{pt(polar(SWC, 92, 156))} A92 92 0 0 1 {pt(polar(SWC, 92, 204))}')]
icon('soundbar', DV, ['soundbar', 'speaker bar', 'tv audio', 'home theater'],
     line=[BAR] + waves, area=[BAR], dotcut=[C(100, 128, 9), C(128, 128, 9), C(156, 128, 9)])

CAB = R(56, 32, 144, 192, 16)
icon('speaker-hifi', DV, ['hifi speaker', 'audio', 'sound system', 'hi-fi speaker', 'loudspeaker'],
     line=[CAB], detail=[C(128, 156, 36)], area=[CAB], dotcut=[C(128, 76, 16)])
icon('speaker-hifi-slash', DV, ['speaker hifi', 'disabled', 'off', 'speaker', 'audio'],
     line=[CAB, C(128, 156, 36), SLASH], dot=[C(128, 76, 16)])

# ======================================================================= ssd
SSD = ('M44 80 H212 A12 12 0 0 1 224 92 V108 A20 20 0 0 0 224 148 V164 A12 12 0 0 1 212 176 H44 '
       'A12 12 0 0 1 32 164 V92 A12 12 0 0 1 44 80 Z')
icon('ssd', DV, ['ssd', 'nvme', 'storage', 'drive', 'solid state drive'],
     line=[P(SSD)], detail=[R(64, 108, 40, 40, 8), R(136, 108, 40, 40, 8)], area=[P(SSD)])

# ======================================================================= stylus
u = (math.sqrt(.5), -math.sqrt(.5)); n = (math.sqrt(.5), math.sqrt(.5))
tip = (40, 216)
at = lambda a, w: (tip[0] + u[0] * a + n[0] * w, tip[1] + u[1] * a + n[1] * w)
hw, a1, a2 = 18, 44, 206
far_c = at(a2, 0)
sty = (f'M{pt(at(0, 0))} L{pt(at(a1, -hw))} L{pt(at(a2, -hw))} '
       f'A{hw} {hw} 0 0 1 {pt(at(a2, hw))} L{pt(at(a1, hw))} Z')
icon('stylus', DV, ['stylus', 'tablet pen', 'digital pen', 'pencil', 'pen'],
     line=[P(sty)], detail=[L(*at(150, -hw), *at(150, hw))], area=[P(sty)])

# ======================================================================= television
TVR = R(32, 72, 192, 144, 16)
icon('television-retro', DV, ['old tv', 'retro', 'television', 'antenna', 'crt'],
     line=[TVR, L(120, 60, 88, 32), L(136, 60, 168, 32), P('M108 72 A20 20 0 0 1 148 72')],
     detail=[R(60, 100, 104, 88, 20)], area=[TVR], dotcut=[C(196, 124, 12), C(196, 164, 12)])
TV = load('television')
icon('television-slash', DV, ['tv off', 'no signal', 'television', 'slash', 'disabled'],
     line=TV['line'] + [SLASH])

# ======================================================================= touchpad
TP = R(32, 40, 192, 176, 16)
icon('touchpad', DV, ['trackpad', 'touchpad', 'laptop', 'input', 'laptop mouse'],
     line=[TP], detail=[L(32, 168, 224, 168), L(128, 168, 128, 216)], area=[TP])

# ======================================================================= usb
UD_C = R(88, 32, 80, 56, 6)
UD_B = R(64, 88, 128, 136, 20)
icon('usb-drive', DV, ['flash drive', 'thumb drive', 'usb stick', 'storage', 'usb drive'],
     line=[UD_C, UD_B], area=[UD_C, UD_B], dotcut=[C(112, 60, 8), C(144, 60, 8)])
UP_T = R(88, 32, 80, 48, 6)
UP_H = R(72, 80, 112, 96, 16)
icon('usb-plug', DV, ['usb plug', 'cable', 'connector', 'usb'],
     line=[UP_T, UP_H, L(128, 176, 128, 224)], detail=[L(104, 128, 152, 128)], area=[UP_T, UP_H],
     dotcut=[C(112, 56, 8), C(144, 56, 8)])
PORT = [(32, 72), (224, 72), (224, 136), (184, 184), (72, 184), (32, 136)]
icon('usb-port', DV, ['usb port', 'micro usb', 'mini usb', 'connector'],
     line=[PG(PORT)], detail=[L(80, 116, 176, 116)], area=[PG(PORT)])

# ======================================================================= vibrate
PH = R(88, 48, 80, 160, 16)
zl = [(56 if i % 2 == 0 else 40, 88 + 16 * i) for i in range(6)]
zr = [(256 - x, y) for x, y in zl]
icon('vibrate', DV, ['vibrate', 'silent mode', 'phone', 'shake', 'vibration'],
     line=[PH, PL(zl), PL(zr)], area=[PH])

# ======================================================================= visor / vr
VIS = ('M32 112 C32 88 72 76 128 76 C184 76 224 88 224 112 V140 C224 164 208 176 184 176 H164 '
       'C150 176 144 156 128 156 C112 156 106 176 92 176 H72 C48 176 32 164 32 140 Z')
icon('visor', DV, ['ar visor', 'headset', 'smart glasses'],
     line=[P(VIS)], detail=[L(72, 116, 100, 116)], area=[P(VIS)])

VR = ('M76 80 H180 A28 28 0 0 1 208 108 V156 A20 20 0 0 1 188 176 H160 L146 152 H110 L96 176 H68 '
      'A20 20 0 0 1 48 156 V108 A28 28 0 0 1 76 80 Z')
VR_STRAP = [L(32, 124, 48, 124), L(208, 124, 224, 124)]
VR_LENS = []
icon('vr-headset', DV, ['vr', 'virtual reality', 'headset', 'goggles', 'vr headset'],
     line=[P(VR)] + VR_STRAP, area=[P(VR)])
icon('vr-headset-slash', DV, ['vr headset', 'disabled', 'off', 'vr', 'virtual reality'],
     line=[P(VR)] + VR_STRAP + [SLASH])

VRS = ('M76 136 H180 A20 20 0 0 1 200 156 V196 A20 20 0 0 1 180 216 H158 L146 196 H110 L98 216 H76 '
       'A20 20 0 0 1 56 196 V156 A20 20 0 0 1 76 136 Z')
cb = [polar((128, 68), 36, -90 + 60 * i) for i in range(6)]
icon('vr-space', DV, ['virtual space', 'vr', 'metaverse', '3d'],
     line=[P(VRS), PG(cb), L(40, 172, 56, 172), L(200, 172, 216, 172)], detail=[PL([cb[5], (128, 68), cb[1]]), L(128, 68, *cb[3])], area=[P(VRS), PG(cb)])

# ======================================================================= watch family
W = load('watch')
WX = -32  # badge variants shift the watch left to make room for the badge
WC, WR = (128 + WX, 128), 64


def shift(el, dx):
    return re.sub(r'(M|L|H|V|A|cx="|x=")([^A-Za-z"]*)', lambda m: m.group(1) + _sh(m.group(1), m.group(2), dx), el)


def _sh(cmd, args, dx):
    nums = [float(v) for v in re.findall(r'-?[\d.]+', args)]
    if cmd in ('M', 'L'):
        nums = [v + dx if i % 2 == 0 else v for i, v in enumerate(nums)]
    elif cmd == 'H' or cmd in ('cx="', 'x="'):
        nums = [v + dx for v in nums]
    elif cmd == 'A':
        nums[5] += dx
    out = ' '.join(f(v) for v in nums)
    return out + (' ' if cmd not in ('cx="', 'x="') else '')



B = (184, 184)
BX, BY = B


def T(pts):
    return [(x + BX, y + BY) for x, y in pts]


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def gear_path(c, r_root, r_tip, n, phase=0):
    step = 360 / n
    hr, ht = step * 0.3, step * 0.17
    pts = []
    for i in range(n):
        t = phase + i * step
        pts.append((polar(c, r_root, t - hr), polar(c, r_tip, t - ht), polar(c, r_tip, t + ht), polar(c, r_root, t + hr)))
    d = 'M' + pt(pts[0][0])
    for i, (a, b, cc, dd) in enumerate(pts):
        if i:
            d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(pts[0][0])} Z'
    return d


def badge(kind):
    """Badge marks around B, identical to the ones in batches 113/114. Returns (roles, clearance radius)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), PL(T([(-20, 8), (0, 28), (20, 8)]))]
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.34)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 58
    elif kind == 'lightning':
        bl = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bl)]
        b['area'] = [PG(bl)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(b_)) for a, b_ in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'question':
        qc = (BX, BY - 14)
        e = polar(qc, 16, 50)
        b['line'] = [P(f'M{BX - 16} {BY - 14} A16 16 0 1 1 {pt(e)} C{f(BX + 2)} {f(BY + 6)} {BX} {BY + 6} {BX} {BY + 12}')]
        b['dot'] = [C(BX, BY + 36, 14)]
        cr = 58
    elif kind == 'star':
        st = [polar((BX, BY + 2), 32 if i % 2 == 0 else 14, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 58
    else:
        raise ValueError(kind)
    return b, cr


def trim_poly(pts, c, r):
    """Pieces of the polyline that lie outside circle (c, r)."""
    pieces, cur = [], []
    for a, b_ in zip(pts, pts[1:]):
        dx, dy = b_[0] - a[0], b_[1] - a[1]
        fx, fy = a[0] - c[0], a[1] - c[1]
        A_, B_, C_ = dx * dx + dy * dy, 2 * (fx * dx + fy * dy), fx * fx + fy * fy - r * r
        disc = B_ * B_ - 4 * A_ * C_
        ts = []
        if disc > 0:
            sq = math.sqrt(disc)
            ts = sorted(t for t in ((-B_ - sq) / (2 * A_), (-B_ + sq) / (2 * A_)) if 0 < t < 1)
        bounds = [0] + ts + [1]
        for t0, t1 in zip(bounds, bounds[1:]):
            tm = (t0 + t1) / 2
            m = (a[0] + dx * tm, a[1] + dy * tm)
            p0 = (a[0] + dx * t0, a[1] + dy * t0); p1 = (a[0] + dx * t1, a[1] + dy * t1)
            if dist(m, c) >= r:
                if not cur:
                    cur = [p0]
                cur.append(p1)
            elif cur:
                pieces.append(cur); cur = []
    if cur:
        pieces.append(cur)
    return pieces


WTOP = [(96 + WX, 72.57), (104 + WX, 32), (152 + WX, 32), (160 + WX, 72.57)]
WBOT = [(96 + WX, 183.43), (104 + WX, 224), (152 + WX, 224), (160 + WX, 183.43)]
WHANDS = [shift(e, WX).replace(' "', '"') for e in W['detail']]


def watch_badge(kind):
    b, cr = badge(kind)
    p, q = circle_x(WC, WR, B, cr)
    ring = f'M{pt(p)} ' + arc_to(WC, WR, p, q, lambda m: dist(m, B))
    area = ring + ' ' + arc_to(B, cr, q, p, lambda m: -dist(m, WC)) + ' Z'
    line = [P(ring), PL(WTOP)] + [PL(pc) for pc in trim_poly(WBOT, B, cr)]
    out = dict(line=line + b['line'], detail=WHANDS + b['detail'], area=[P(area)] + b['area'],
               hole=b['hole'], dot=b['dot'], dotcut=b['dotcut'])
    return out


WT = ['smartwatch', 'wearable']
for nm, kind, tags in [
    ('watch-arrow-down', 'arrow-down', ['watch', 'decrease', 'download']),
    ('watch-arrow-up', 'arrow-up', ['watch', 'increase', 'upload']),
    ('watch-check', 'check', ['watch', 'done', 'approved']),
    ('watch-code', 'code', ['watch', 'developer', 'code']),
    ('watch-currency-dollar', 'dollar', ['watch', 'money', 'price']),
    ('watch-gear', 'gear', ['watch', 'settings', 'configure']),
    ('watch-heart', 'heart', ['watch', 'favorite', 'like']),
    ('watch-lightning', 'lightning', ['watch', 'fast', 'power']),
    ('watch-magnifying-glass', 'magnifying-glass', ['watch', 'search', 'find']),
    ('watch-minus', 'minus', ['watch', 'remove', 'subtract']),
    ('watch-pause', 'pause', ['watch', 'paused', 'hold']),
    ('watch-plus', 'plus', ['watch', 'add', 'new']),
    ('watch-push-pin', 'push-pin', ['watch', 'pinned', 'pin']),
    ('watch-question', 'question', ['watch', 'help', 'unknown']),
    ('watch-share', 'share', ['watch', 'share', 'send']),
    ('watch-star', 'star', ['watch', 'favorite', 'starred']),
]:
    icon(nm, DV, tags + WT, **watch_badge(kind))

icon('watch-slash', DV, ['watch', 'disabled', 'off', 'smartwatch', 'wearable'],
     line=W['line'] + [SLASH])

WD = R(64, 72, 128, 112, 24)
icon('watch-digital', DV, ['digital watch', 'smartwatch', 'time', 'wrist'],
     line=[WD, PL([(96, 72), (104, 32), (152, 32), (160, 72)]), PL([(96, 184), (104, 224), (152, 224), (160, 184)])],
     detail=[PL([(98, 114), (112, 104), (112, 152)])] + g_2(132, 104, 28, 48), area=[WD])

print(save(overwrite=True))
