import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *


def head(tip, direction, size):
    """Chevron arrowhead at tip pointing along direction (deg), 45 deg legs of axial depth size."""
    a = math.radians(direction)
    bx, by = -math.cos(a), -math.sin(a)
    nx, ny = -by, bx
    return [(tip[0] + (bx + nx) * size, tip[1] + (by + ny) * size), tip,
            (tip[0] + (bx - nx) * size, tip[1] + (by - ny) * size)]


def arrow(a, b, size):
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return [L(a[0], a[1], b[0], b[1]), PL(head(b, ang, size))]


SLASH = L(48, 48, 208, 208)

# ======================================================================= stroke lettering
# Each glyph draws centrelines in the box (x, t, w, h); 16-unit strokes like everything else.

def g_A(x, t, w, h):
    b = t + h
    yb = t + h * 0.66
    hw = (w / 2) * (yb - t) / h
    return [PL([(x, b), (x + w / 2, t), (x + w, b)]), L(x + w / 2 - hw, yb, x + w / 2 + hw, yb)]


def g_C(x, t, w, h, end=20):
    r = w / 2
    ct, cb = (x + r, t + r), (x + r, t + h - r)
    s, e = polar(ct, r, -end), polar(cb, r, end)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 {pt(e)}')]


def g_D(x, t, w, h):
    R_ = min(w * 0.6, h / 2)
    b = t + h
    return [P(f'M{f(x)} {f(t)} H{f(x + w - R_)} A{f(R_)} {f(R_)} 0 0 1 {f(x + w)} {f(t + R_)} V{f(b - R_)} '
              f'A{f(R_)} {f(R_)} 0 0 1 {f(x + w - R_)} {f(b)} H{f(x)} Z')]


def g_E(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b), (x + w, b)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_F(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b)]), L(x, t + h * 0.5, x + w * 0.8, t + h * 0.5)]


def g_G(x, t, w, h):
    r = w / 2
    ct, cb = (x + r, t + r), (x + r, t + h - r)
    s = polar(ct, r, -20)
    yb = t + h * 0.54
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 '
              f'{f(x + w)} {f(t + h - r)} V{f(yb)} H{f(x + w * 0.55)}')]


def g_H(x, t, w, h):
    return [L(x, t, x, t + h), L(x + w, t, x + w, t + h), L(x, t + h / 2, x + w, t + h / 2)]


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h)]


def g_K(x, t, w, h):
    b = t + h
    a0, a1 = (x + w, t), (x, t + h * 0.62)
    m = (a0[0] + (a1[0] - a0[0]) * 0.55, a0[1] + (a1[1] - a0[1]) * 0.55)
    return [L(x, t, x, b), L(*a0, *a1), L(*m, x + w, b)]


def bowl(x, t, w, h, k=0.56):
    r = h * k / 2
    return r, f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 2 * r)} H{f(x)}'


def g_P(x, t, w, h):
    return [P(bowl(x, t, w, h)[1])]


def g_R(x, t, w, h):
    r, d = bowl(x, t, w, h)
    return [P(d), L(x + w * 0.45, t + 2 * r, x + w, t + h)]


def g_O(x, t, w, h):
    return [R(x, t, w, h, w / 2)]


def g_Q(x, t, w, h):
    return [R(x, t, w, h, w / 2), L(x + w * 0.62, t + h * 0.7, x + w + 4, t + h + 6)]


def g_S(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x + w)} {f(t)} H{f(x + r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(t + 2 * r)} H{f(x + w - r)} '
              f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + h)} H{f(x)}')]


def g_U(x, t, w, h):
    r = w / 2
    return [P(f'M{f(x)} {f(t)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 {f(x + w)} {f(t + h - r)} V{f(t)}')]


def g_V(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h), (x + w, t)])]


def g_W(x, t, w, h):
    return [PL([(x, t), (x + w * 0.25, t + h), (x + w / 2, t + h * 0.3), (x + w * 0.75, t + h), (x + w, t)])]


def g_1(x, t, w, h):
    return [PL([(x, t + h * 0.26), (x + w, t), (x + w, t + h)])]


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


def g_6(x, t, w, h, flip=False):
    r = w / 2
    c = (x + r, t + h - r)
    p = (x + w * 0.74, t)
    d = dist(p, c)
    base = math.atan2(p[1] - c[1], p[0] - c[0])
    off = math.acos(r / d)
    tp = (c[0] + r * math.cos(base - off), c[1] + r * math.sin(base - off))  # left tangent point
    pts = [p, tp]
    cc = c
    if flip:
        k = lambda q: (2 * x + w - q[0], 2 * t + h - q[1])
        pts = [k(q) for q in pts]
        cc = k(c)
    return [L(*pts[0], *pts[1]), C(cc[0], cc[1], r)]


def g_9(x, t, w, h):
    return g_6(x, t, w, h, flip=True)


def g_7(x, t, w, h):
    return [PL([(x, t), (x + w, t), (x + w * 0.36, t + h)])]


def g_8(x, t, w, h):
    ry1, ry2 = h * 0.225, h * 0.275
    return [E(x + w / 2, t + ry1, w / 2 - 3, ry1), E(x + w / 2, t + h - ry2, w / 2, ry2)]


def g_plus(x, t, w, h):
    cy = t + h / 2
    s = w / 2
    return [L(x, cy, x + w, cy), L(x + s, cy - s, x + s, cy + s)]


GLYPH = {'A': g_A, 'C': g_C, 'D': g_D, 'E': g_E, 'F': g_F, 'G': g_G, 'H': g_H, 'I': g_I, 'K': g_K,
         'P': g_P, 'R': g_R, 'O': g_O, 'Q': g_Q, 'S': g_S, 'U': g_U, 'V': g_V, 'W': g_W,
         '0': g_O, '1': g_1, '2': g_2, '3': g_3, '4': g_4, '5': g_5, '6': g_6, '7': g_7, '8': g_8, '9': g_9,
         '+': g_plus}
WIDTH = {'A': 44, 'C': 38, 'D': 40, 'E': 34, 'F': 34, 'G': 40, 'H': 40, 'I': 0, 'K': 38, 'P': 38, 'R': 40,
         'O': 40, 'Q': 42, 'S': 40, 'U': 40, 'V': 44, 'W': 64, '1': 22, '+': 36}


def text(s, cx=128, cy=128, h=64, k=1.0, gap=30, plus=None):
    ws = []
    for ch in s:
        w = WIDTH.get(ch, 40) * k
        if ch == '+' and plus:
            w = plus
        ws.append(w)
    total = sum(ws) + gap * (len(s) - 1)
    x = cx - total / 2
    out = []
    for ch, w in zip(s, ws):
        if ch == '+':
            hh = w
            out += g_plus(x, cy - hh / 2, w, hh)
        else:
            out += GLYPH[ch](x, cy - h / 2, w, h)
        x += w + gap
    return out


# Badge frame shared by every lettered badge
FRAME = R(32, 56, 192, 144, 20)


def label(s):
    if len(s) <= 2:
        return text(s, h=64, k=1.0, gap=28)
    # three glyphs: fixed widths for the narrow ones, the wide ones share what is left of a 136-unit run
    gap, run, h = 26, 136, 56
    fixed = {'I': 0, '1': 18, '+': 28}
    wide = [ch for ch in s if ch not in fixed]
    ww = min(36, (run - 2 * gap - sum(fixed.get(ch, 0) for ch in s)) / len(wide))
    ws = [fixed.get(ch, ww) for ch in s]
    x = 128 - (sum(ws) + gap * 2) / 2
    out = []
    for ch, w in zip(s, ws):
        out += g_plus(x, 128 - w / 2, w, w) if ch == '+' else GLYPH[ch](x, 128 - h / 2, w, h)
        x += w + gap
    return out


def badge(name, cat, tags, s):
    icon(name, cat, tags, line=[FRAME], detail=label(s), area=[FRAME])


def badge_slash(name, cat, tags, s):
    icon(name, cat, tags, line=[FRAME] + label(s) + [SLASH])


# ======================================================================= Arrows
STEPS = 'M32 208 L32 168 L80 168 L80 128 L128 128 L128 88 L176 88 L176 48 L224 48 L224 208 Z'  # stairs.svg
icon('stairs-up', 'Arrows', ['upstairs', 'stairs', 'climb', 'up'],
     line=[P(STEPS)] + arrow((40, 116), (100, 56), 36), area=[P(STEPS)])

BR_R = 'M184 56 H204 A12 12 0 0 1 216 68 V188 A12 12 0 0 1 204 200 H184'
BR_L = 'M72 56 H52 A12 12 0 0 0 40 68 V188 A12 12 0 0 0 52 200 H72'
icon('transfer-in', 'Arrows', ['transfer in', 'receive', 'incoming', 'arrow'],
     line=[P(BR_R)] + arrow((40, 128), (176, 128), 40))
icon('transfer-out', 'Arrows', ['transfer out', 'send', 'outgoing', 'arrow'],
     line=[P(BR_L)] + arrow((80, 128), (216, 128), 40))

# ======================================================================= Business
AD_C = text('AD', h=60, gap=26)
icon('ad-circle', 'Business', ['advertisement', 'ad', 'marketing'],
     line=[C(128, 128, 96)], detail=AD_C, area=[C(128, 128, 96)])
icon('ad-circle-slash', 'Business', ['advertisement', 'no ads', 'ad blocker'],
     line=[C(128, 128, 96)] + AD_C + [SLASH])

# affiliate: hub with three satellites
hub, hr = (128, 136), 32
sats = [((128, 52), 20), ((52, 188), 20), ((204, 188), 20)]
def seg(a, b, ra, rb):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rb, b[1] - uy * rb)
icon('affiliate', 'Business', ['affiliate', 'network', 'referral', 'nodes'],
     line=[C(*hub, hr)] + [C(*c, r) for c, r in sats] + [seg(hub, c, hr, r) for c, r in sats],
     area=[C(*hub, hr)] + [C(*c, r) for c, r in sats])

# agile: lead-in line that loops back around on itself
ac, ar_ = (144, 112), 72
a_end = polar(ac, ar_, 165)
agile_d = (f'M32 {ac[1] + ar_} H{ac[0]} A{ar_} {ar_} 0 1 0 {pt(a_end)}')
icon('agile', 'Business', ['sprint', 'iteration', 'scrum'],
     line=[P(agile_d), PL(head(a_end, 165 - 90, 36))])

# badge: clip-on staff card
card = 'M104 72 H72 A16 16 0 0 0 56 88 V208 A16 16 0 0 0 72 224 H184 A16 16 0 0 0 200 208 V88 A16 16 0 0 0 184 72 H152'
card_area = 'M72 72 H184 A16 16 0 0 1 200 88 V208 A16 16 0 0 1 184 224 H72 A16 16 0 0 1 56 208 V88 A16 16 0 0 1 72 72 Z'
clip = R(104, 40, 48, 52, 12)
icon('badge', 'Business', ['badge', 'id', 'staff', 'employee', 'rank'],
     line=[P(card), clip], detail=[C(128, 144, 20), L(100, 192, 156, 192), L(120, 62, 136, 62)],
     area=[P(card_area), clip])

badge('badge-ad', 'Commerce', ['advertisement', 'ad', 'sponsored', 'promo', 'marketing'], 'AD')
badge_slash('badge-ad-slash', 'Business', ['advertisement', 'ad blocker', 'no ads'], 'AD')

# ballot box
box = R(40, 120, 176, 96, 16)
paper = 'M80 120 V44 A12 12 0 0 1 92 32 H164 A12 12 0 0 1 176 44 V120'
icon('ballot-box', 'Business', ['vote', 'election', 'poll', 'ballot'],
     line=[box, P(paper)], detail=[PL([(104, 80), (122, 98), (152, 68)]), L(96, 168, 160, 168)],
     area=[box, P(paper + ' Z')])

# briefcase-slash (from briefcase.svg, no area so the slash reads in fill)
icon('briefcase-slash', 'Business', ['briefcase', 'disabled', 'off', 'business'],
     line=[R(32, 72, 192, 136, 16), P('M88 72 V56 A16 16 0 0 1 104 40 H152 A16 16 0 0 1 168 56 V72'),
           L(32, 124, 224, 124), SLASH])

# government building: dome, beam, columns, base
dome = 'M84 96 A44 44 0 0 1 172 96'
icon('building-government', 'Business', ['government', 'capitol', 'civic', 'building'],
     line=[L(128, 32, 128, 52), P(dome), L(40, 96, 216, 96), L(72, 128, 72, 176), L(109, 128, 109, 176),
           L(147, 128, 147, 176), L(184, 128, 184, 176), L(32, 208, 224, 208)],
     area=[P(dome + ' Z')])

# ---- building-office variants (geometry from building-office.svg)
WINDOWS = [L(88, 72, 112, 72), L(144, 72, 168, 72), L(88, 108, 112, 108), L(144, 108, 168, 108), L(88, 144, 112, 144)]


def office_cut(B, rc):
    yr = B[1] - math.sqrt(rc * rc - (200 - B[0]) ** 2)
    xb = B[0] - math.sqrt(rc * rc - (216 - B[1]) ** 2)
    body = f'M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V{f(yr)}'
    area = body + f' A{f(rc)} {f(rc)} 0 0 0 {f(xb)} 216 Z'
    return [P(body), L(32, 216, xb, 216)], [P(area)]


def office(name, tags, marks, rc=54, B=(184, 184), mark_area=(), mark_hole=()):
    ln, ar = office_cut(B, rc)
    icon(name, 'Business', tags, line=ln + list(marks), detail=WINDOWS, area=ar + list(mark_area),
         hole=list(mark_hole))


B = (184, 184)
office('building-office-arrow-down', ['building', 'office', 'download', 'arrow'], arrow((184, 152), (184, 216), 28), rc=60)
office('building-office-arrow-up', ['building', 'office', 'upload', 'arrow'], arrow((184, 216), (184, 152), 28), rc=60)
office('building-office-check', ['building', 'office', 'verified', 'check'], [PL([(156, 186), (176, 206), (212, 166)])])
office('building-office-minus', ['building', 'office', 'remove', 'minus', 'subtract'], [L(156, 184, 212, 184)])
office('building-office-plus', ['building', 'office', 'add', 'plus', 'add building'],
       [L(156, 184, 212, 184), L(184, 156, 184, 212)])
lock_body = R(156, 180, 56, 40, 10)
office('building-office-lock', ['building', 'office', 'secure', 'lock'],
       [lock_body, P('M168 180 V168 A16 16 0 0 1 200 168 V180')], rc=60, mark_area=[lock_body])
# small six-tooth gear
gp = []
for i in range(6):
    t0 = i * 60
    gp += [polar(B, 22, t0 - 20), polar(B, 32, t0 - 11), polar(B, 32, t0 + 11), polar(B, 22, t0 + 20)]
gdd = 'M' + pt(gp[0])
for i in range(6):
    a, b, c_, d_ = gp[i * 4:i * 4 + 4]
    if i:
        gdd += f' A22 22 0 0 1 {pt(a)}'
    gdd += f' L{pt(b)} L{pt(c_)} L{pt(d_)}'
gdd += f' A22 22 0 0 1 {pt(gp[0])} Z'
office('building-office-gear', ['building', 'office', 'settings', 'gear', 'building settings'],
       [P(gdd)], rc=58, mark_area=[P(gdd)], mark_hole=[C(184, 184, 8)])
icon('building-office-slash', 'Business', ['building', 'office', 'closed', 'disabled', 'building closed'],
     line=[P('M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V216'), L(32, 216, 224, 216),
           P('M108 216 V180 H148 V216')] + WINDOWS + [L(144, 144, 168, 144), SLASH])

# ======================================================================= lettered badges
badge('badge-2k', 'Media', ['badge 2k', 'badge', 'label', 'resolution', '2k'], '2K')
badge('badge-3d', 'Media', ['3d', 'three dimensional', 'view', 'stereoscopic', 'format'], '3D')
badge('badge-3k', 'Media', ['badge 3k', 'badge', 'label', 'resolution', '3k'], '3K')
badge('badge-4k', 'Media', ['4k', 'ultra hd', 'resolution', 'video'], '4K')
badge('badge-5k', 'Media', ['badge 5k', 'badge', 'label', 'resolution', '5k'], '5K')
badge('badge-8k', 'Media', ['8k', 'resolution', 'video', 'ultra hd'], '8K')
badge('badge-ai', 'Interface', ['ai', 'artificial intelligence', 'machine learning', 'smart'], 'AI')
badge('badge-ar', 'Symbols', ['augmented reality', 'ar', 'label', 'badge'], 'AR')
badge('badge-hd', 'Media', ['hd', 'high definition', 'resolution', 'full hd', '1080p'], 'HD')
badge('badge-hq', 'Media', ['high quality', 'hq', 'video', 'badge'], 'HQ')
badge('badge-sd', 'Media', ['sd', 'standard definition', 'resolution', 'video'], 'SD')
badge('badge-vo', 'Media', ['voice over', 'vo', 'audio', 'narration'], 'VO')
badge('badge-vr', 'Symbols', ['virtual reality', 'vr', 'label', 'badge', 'headset'], 'VR')
badge('badge-wc', 'Maps', ['wc', 'restroom', 'toilet', 'bathroom'], 'WC')
badge('badge-gif', 'Media', ['gif', 'animation', 'image', 'badge', 'animated image'], 'GIF')
badge('badge-hdr', 'Media', ['hdr', 'high dynamic range', 'photo', 'video', 'badge'], 'HDR')
badge('badge-uhd', 'Media', ['uhd', '4k', 'ultra hd', 'video quality'], 'UHD')
badge('badge-vip', 'Commerce', ['vip', 'premium', 'exclusive', 'member'], 'VIP')
badge_slash('badge-vip-slash', 'Commerce', ['badge vip', 'off', 'disabled', 'hidden', 'badge'], 'VIP')
icon('badge-slash', 'Interface', ['badge', 'disabled', 'off', 'label', 'resolution'], line=[FRAME, SLASH])
for n in ('0', '3', '6', '10', '12', '13', '16', '17', '18', '21'):
    tags = ['age rating', n + '+', 'adult', 'restriction'] + (['adults only'] if n == '18' else [])
    badge(f'badge-{n}-plus', 'Letters &amp; Numbers', tags, n + '+')
EX = R(40, 40, 176, 176, 20)
icon('badge-explicit', 'Media', ['explicit', 'e', 'parental advisory', 'content'],
     line=[EX], detail=g_E(100, 84, 56, 88), area=[EX])

print(save(overwrite=True))
