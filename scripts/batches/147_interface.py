import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

HOME, UI, PPL = 'Home', 'Interface', 'People'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def seg_circle(a, b, c, r):
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy
    B = 2 * (fx * dx + fy * dy)
    Cc = fx * fx + fy * fy - r * r
    disc = B * B - 4 * A * Cc
    if disc < 0:
        return []
    s = math.sqrt(disc)
    return sorted(t for t in ((-B - s) / (2 * A), (-B + s) / (2 * A)) if 0 <= t <= 1)


def cut_polygon(points, c, r):
    """Cut a closed polygon by a badge circle. Returns (open line path d, closed area path d)."""
    n = len(points)
    inside = lambda p: dist(p, c) < r
    k = next(i for i in range(n) if not inside(points[i]))
    pts = points[k:] + points[:k]
    seq = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        for t in seg_circle(a, b, c, r):
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            seq.append((q, 'x'))
        if i + 1 < n:
            seq.append((b, 'in' if inside(b) else 'out'))
    xs = [i for i, s in enumerate(seq) if s[1] == 'x']
    e_i, x_i = xs[0], xs[1]
    entry, exit_pt = seq[e_i][0], seq[x_i][0]
    after = [s[0] for s in seq[x_i + 1:] if s[1] == 'out']
    before = [s[0] for s in seq[:e_i] if s[1] == 'out']
    chain = [exit_pt] + after + [pts[0]] + before + [entry]
    d = poly(chain)
    area = d + ' ' + arc_to(c, r, entry, exit_pt, lambda m: -(m[0] + m[1])) + ' Z'
    return d, area


# ================================================================ HOME
# ---------------------------------------------------------------- smoke-detector
sd_body = 'M48 80 H208 V108 C208 164 172 200 128 200 C84 200 48 164 48 108 Z'
icon('smoke-detector', HOME, ['smoke alarm', 'detector', 'co alarm', 'safety', 'fire safety'],
     line=[L(32, 48, 224, 48), P(sd_body)],
     detail=[L(84, 120, 172, 120), L(104, 156, 152, 156)],
     area=[P(sd_body)])

# ---------------------------------------------------------------- soap
soap_bar = R(32, 128, 176, 88, 32)
icon('soap', HOME, ['soap', 'bubbles', 'wash', 'hygiene'],
     line=[soap_bar, C(176, 68, 28), C(104, 76, 16)],
     detail=[P('M68 172 A20 20 0 0 1 88 152')],
     area=[soap_bar, C(176, 68, 28)])

# ---------------------------------------------------------------- solar-roof
roof = [(32, 128), (76, 48), (180, 48), (224, 128)]
icon('solar-roof', HOME, ['solar panels', 'renewable', 'roof'],
     line=[PG(roof), P('M48 128 V208 H208 V128'), P('M108 208 V180 A20 20 0 0 1 148 180 V208')],
     detail=[L(54, 88, 202, 88), L(111, 48, 96, 128), L(145, 48, 160, 128)],
     area=[PG(roof), P('M48 128 V208 H208 V128 Z')],
     hole=[P('M116 208 V180 A12 12 0 0 1 140 180 V208 Z')])

# ---------------------------------------------------------------- spray-bottle
sb_body = R(56, 128, 96, 96, 16)
sb_head = 'M64 96 V64 A16 16 0 0 1 80 48 H168 A8 8 0 0 1 176 56 V72 A8 8 0 0 1 168 80 H136 V96 Z'
icon('spray-bottle', HOME, ['cleaning spray', 'spray', 'chores', 'cleaning', 'household'],
     line=[sb_body, P('M84 128 V96'), P('M124 128 V96'), P(sb_head), L(156, 80, 172, 120),
           L(208, 40, 220, 32), L(208, 64, 224, 64), L(208, 88, 220, 96)],
     area=[sb_body, R(84, 96, 40, 32), P(sb_head)])

# ---------------------------------------------------------------- sprinkler
sp_head = 'M108 216 V176 A20 20 0 0 1 148 176 V216'
jets = [P('M128 156 C120 96 80 64 40 80'), P('M128 156 C136 96 176 64 216 80')]
icon('sprinkler', HOME, ['sprinkler', 'watering', 'lawn', 'garden'],
     line=[L(48, 216, 208, 216), P(sp_head)] + jets,
     area=[P(sp_head + ' Z')],
     dot=[C(44, 128, 14), C(212, 128, 14), C(128, 48, 14)])

# ---------------------------------------------------------------- stool
seat = R(56, 40, 144, 40, 16)
icon('stool', HOME, ['stool', 'seat', 'bar stool', 'counter chair'],
     line=[seat, L(84, 80, 64, 224), L(172, 80, 192, 224), L(74, 168, 182, 168)],
     area=[seat])

# ---------------------------------------------------------------- stove
st_body = R(40, 32, 176, 192, 16)
icon('stove', HOME, ['cooker', 'stove', 'oven', 'kitchen'],
     line=[st_body],
     detail=[L(40, 96, 216, 96), R(80, 136, 96, 48, 8)],
     area=[st_body],
     dotcut=[C(84, 64, 14), C(128, 64, 14), C(172, 64, 14)])

# ---------------------------------------------------------------- swing
icon('swing', HOME, ['swing', 'playground', 'child', 'park'],
     line=[L(48, 40, 208, 40), L(64, 40, 32, 224), L(192, 40, 224, 224), L(100, 40, 100, 168), L(156, 40, 156, 168),
           L(84, 176, 172, 176)])

# ---------------------------------------------------------------- thermostat
icon('thermostat', HOME, ['thermostat', 'temperature', 'heating', 'climate'],
     line=[C(128, 128, 96)],
     detail=[L(128, 76, 128, 136), C(128, 160, 20)],
     area=[C(128, 128, 96)])

# ---------------------------------------------------------------- tiles
tiles_sq = R(32, 32, 192, 192, 16)
icon('tiles', HOME, ['tiles', 'floor', 'grid', 'pattern'],
     line=[tiles_sq],
     detail=[L(32, 96, 224, 96), L(32, 160, 224, 160),
             L(96, 32, 96, 96), L(160, 32, 160, 96),
             L(64, 96, 64, 160), L(128, 96, 128, 160), L(192, 96, 192, 160),
             L(96, 160, 96, 224), L(160, 160, 160, 224)],
     area=[tiles_sq])

# ---------------------------------------------------------------- toilet
tank = R(48, 32, 64, 96, 12)
bowl = 'M48 128 H216 C216 164 192 184 152 184 L160 224 H88 L96 178 C64 170 48 152 48 128 Z'
icon('toilet', HOME, ['toilet', 'bathroom', 'wc', 'restroom'],
     line=[tank, P(bowl)],
     area=[tank, P(bowl)])

# ---------------------------------------------------------------- toilet-paper
tp_c = (96, 100)
tp_line = [C(*tp_c, 56), P('M96 44 H208 V216 H152 V100')]
tp_detail = [C(*tp_c, 16), L(152, 176, 208, 176)]
icon('toilet-paper', HOME, ['toilet paper', 'roll', 'bathroom', 'tissue'],
     line=tp_line, detail=tp_detail,
     area=[C(*tp_c, 56), P('M96 44 H208 V216 H152 V100 H96 Z')])
icon('toilet-paper-slash', HOME, ['toilet paper', 'off', 'disabled', 'hidden', 'toilet'],
     line=tp_line + tp_detail + [SLASH])

# ---------------------------------------------------------------- towel
towel = 'M64 56 V200 A16 16 0 0 0 80 216 H176 A16 16 0 0 0 192 200 V56'
icon('towel', HOME, ['towel', 'bathroom', 'hanging', 'dry'],
     line=[L(32, 56, 224, 56), P(towel)],
     detail=[L(64, 168, 192, 168)],
     area=[P(towel + ' Z')])

# ---------------------------------------------------------------- utility-meter
um = R(40, 32, 176, 192, 16)
icon('utility-meter', HOME, ['electric meter', 'gas meter', 'meter', 'usage'],
     line=[um],
     detail=[R(72, 64, 112, 40, 8), L(109, 64, 109, 104), L(147, 64, 147, 104),
             P('M88 188 A40 40 0 0 1 168 188'), L(128, 188, 148, 160)],
     area=[um])

# ---------------------------------------------------------------- vacuum-cleaner
vc_body = R(112, 120, 108, 88, 32)
icon('vacuum-cleaner', HOME, ['vacuum', 'cleaner', 'cleaning', 'hoover', 'vacuum cleaner'],
     line=[vc_body, P('M136 120 C136 80 120 60 94 60'), L(100, 36, 60, 208), L(32, 212, 88, 212)],
     detail=[L(148, 164, 184, 164)],
     area=[vc_body])

# ---------------------------------------------------------------- wall
wall_r = R(32, 48, 192, 160, 12)
WALL_S = [((32, 88), (224, 88)), ((32, 128), (224, 128)), ((32, 168), (224, 168)),
          ((96, 48), (96, 88)), ((160, 48), (160, 88)),
          ((64, 88), (64, 128)), ((128, 88), (128, 128)), ((192, 88), (192, 128)),
          ((96, 128), (96, 168)), ((160, 128), (160, 168)),
          ((64, 168), (64, 208)), ((128, 168), (128, 208)), ((192, 168), (192, 208))]


def clear_of_slash(segs, gap=22):
    """Drop the part of each axis-aligned segment within `gap` of the slash line y = x."""
    out = []
    for (x1, y1), (x2, y2) in segs:
        if y1 == y2:  # horizontal: keep x outside (y-gap*sqrt2, y+gap*sqrt2)
            k, lo, hi, mk = y1, min(x1, x2), max(x1, x2), lambda v, k=y1: (v, k)
        else:
            k, lo, hi, mk = x1, min(y1, y2), max(y1, y2), lambda v, k=x1: (k, v)
        g = gap * math.sqrt(2)
        for a, b in ((lo, min(hi, k - g)), (max(lo, k + g), hi)):
            if b - a >= 20:
                out.append(L(*mk(a), *mk(b)))
    return out


WALL_D = [L(32, 88, 224, 88), L(32, 128, 224, 128), L(32, 168, 224, 168),
          L(96, 48, 96, 88), L(160, 48, 160, 88),
          L(64, 88, 64, 128), L(128, 88, 128, 128), L(192, 88, 192, 128),
          L(96, 128, 96, 168), L(160, 128, 160, 168),
          L(64, 168, 64, 208), L(128, 168, 128, 208), L(192, 168, 192, 208)]
icon('wall', HOME, ['wall', 'bricks', 'construction', 'firewall', 'masonry'],
     line=[wall_r], detail=WALL_D, area=[wall_r])
icon('wall-slash', HOME, ['wall', 'off', 'disabled', 'hidden'], line=[wall_r] + clear_of_slash(WALL_S) + [SLASH])

# ---------------------------------------------------------------- wardrobe
wr = R(48, 32, 160, 176, 14)
icon('wardrobe', HOME, ['closet', 'clothes storage', 'cabinet'],
     line=[wr, L(76, 208, 76, 224), L(180, 208, 180, 224)],
     detail=[L(128, 32, 128, 208), L(100, 104, 100, 136), L(156, 104, 156, 136)],
     area=[wr])

# ---------------------------------------------------------------- washing-machine
wm = R(40, 32, 176, 192, 16)
icon('washing-machine', HOME, ['washer', 'laundry', 'appliance', 'washing', 'clothes'],
     line=[wm],
     detail=[L(40, 88, 216, 88), L(132, 60, 180, 60), C(128, 156, 40)],
     area=[wm],
     dotcut=[C(80, 60, 14)])

# ---------------------------------------------------------------- water-heater
wh = R(56, 48, 144, 160, 36)
icon('water-heater', HOME, ['boiler', 'water heater', 'hot water', 'tank', 'heating'],
     line=[wh, L(100, 48, 100, 32), L(156, 48, 156, 32), L(88, 208, 88, 224), L(168, 208, 168, 224)],
     detail=[C(128, 104, 24), L(104, 168, 152, 168)],
     area=[wh])

# ---------------------------------------------------------------- water-meter
wdrop = 'M128 128 C118 142 106 154 106 168 A22 22 0 0 0 150 168 C150 154 138 142 128 128 Z'
icon('water-meter', HOME, ['water meter', 'utility', 'usage', 'bill'],
     line=[C(128, 128, 96)],
     detail=[R(96, 64, 64, 32, 8), P(wdrop)],
     area=[C(128, 128, 96)])

# ---------------------------------------------------------------- window
win_frame = 'M48 208 V52 A12 12 0 0 1 60 40 H196 A12 12 0 0 1 208 52 V208'
WIN_D = [L(128, 40, 128, 208), L(48, 124, 208, 124)]
icon('window', HOME, ['window', 'glass', 'frame', 'open window'],
     line=[P(win_frame), L(32, 208, 224, 208)], detail=WIN_D, area=[P(win_frame + ' Z')])
icon('window-slash', HOME, ['window', 'off', 'disabled', 'hidden'],
     line=[P(win_frame), L(32, 208, 224, 208)] + WIN_D + [SLASH])

# ================================================================ INTERFACE
aw = load('app-window')

icon('window-minimize', UI, ['minimize', 'window', 'hide', 'underscore'],
     line=aw['line'], detail=aw['detail'] + [L(88, 172, 168, 172)], area=aw['area'], dotcut=aw['dotcut'])

# ---------------------------------------------------------------- accessibility
ACC = [L(76, 108, 180, 108), L(128, 108, 128, 148), PL([(100, 188), (128, 148), (156, 188)])]
icon('accessibility', UI, ['accessibility', 'a11y', 'universal access', 'accessible', 'disability'],
     line=[C(128, 128, 96)], detail=ACC, area=[C(128, 128, 96)], dotcut=[C(128, 70, 16)])
icon('accessibility-slash', PPL, ['accessibility', 'a11y', 'disabled'],
     line=[C(128, 128, 96)] + ACC + [SLASH], dot=[C(128, 70, 16)])

# ---------------------------------------------------------------- ai-agent
ag_head = R(32, 88, 144, 128, 28)
sk_c, sk_r = (198, 58), 28
# sparkle: the core sparkle curve, scaled into the corner
s = sk_r / 96.0
def sp_pt(x, y):
    return (sk_c[0] + (x - 128) * s, sk_c[1] + (y - 128) * s)
core_sp = [((128, 32),), ((136, 96), (160, 120), (224, 128)), ((160, 136), (136, 160), (128, 224)),
           ((120, 160), (96, 136), (32, 128)), ((96, 120), (120, 96), (128, 32))]
sk = 'M' + pt(sp_pt(*core_sp[0][0]))
for seg_ in core_sp[1:]:
    sk += ' C' + ' '.join(pt(sp_pt(*p)) for p in seg_)
sk += ' Z'
icon('ai-agent', UI, ['ai agent', 'assistant', 'bot', 'automation', 'ai'],
     line=[ag_head, L(104, 88, 104, 68), P(sk)],
     detail=[L(84, 180, 124, 180)],
     area=[ag_head, P(sk)],
     dot=[C(104, 56, 16)],
     dotcut=[C(76, 140, 16), C(132, 140, 16)])

# ---------------------------------------------------------------- app-notification
bc, br = (188, 68), 62
an_p = (bc[0] - math.sqrt(br * br - 4 * 4), 72)
an_q = (184, bc[1] + math.sqrt(br * br - 4 * 4))
an_line = (f'M{pt(an_p)} H64 A32 32 0 0 0 32 104 V192 A32 32 0 0 0 64 224 H152 A32 32 0 0 0 184 192 V{f(an_q[1])}')
an_area = an_line + ' ' + arc_to(bc, br, an_q, an_p, lambda m: -dist(m, (96, 160))) + ' Z'
icon('app-notification', UI, ['app', 'badge', 'notification', 'indicator', 'app badge'],
     line=[P(an_line), C(*bc, 30)], area=[P(an_area), C(*bc, 30)])

# ---------------------------------------------------------------- app-switcher
front = R(88, 48, 128, 176, 20)
icon('app-switcher', UI, ['switch apps', 'multitask', 'windows', 'recent'],
     line=[front, P('M88 200 H52 A20 20 0 0 1 32 180 V92 A20 20 0 0 1 52 72 H88')],
     area=[front])

# ---------------------------------------------------------------- app-window layouts
for nm, tags, rect in [
    ('app-window-bottom', ['app window bottom', 'window', 'app', 'layout', 'bottom'], R(64, 144, 128, 40, 8)),
    ('app-window-bottom-left', ['window', 'app', 'layout', 'bottom', 'left'], R(64, 144, 64, 40, 8)),
    ('app-window-bottom-right', ['window', 'app', 'layout', 'bottom', 'right'], R(128, 144, 64, 40, 8)),
    ('app-window-center', ['app window center', 'window', 'app', 'layout', 'center'], R(88, 136, 80, 48, 8)),
]:
    icon(nm, UI, tags, line=aw['line'], detail=aw['detail'] + [rect], area=aw['area'], dotcut=aw['dotcut'])

for nm, tags, marks in [
    ('app-window-minus', ['window', 'minimize', 'remove', 'minus'], [L(100, 160, 156, 160)]),
    ('app-window-plus', ['new window', 'add', 'plus', 'window'], [L(128, 132, 128, 188), L(100, 160, 156, 160)]),
    ('app-window-x', ['close window', 'window', 'x', 'error'], [L(108, 140, 148, 180), L(148, 140, 108, 180)]),
]:
    icon(nm, UI, tags, line=aw['line'], detail=aw['detail'] + marks, area=aw['area'], dotcut=aw['dotcut'])

# ---------------------------------------------------------------- app-windows
fw = R(72, 80, 152, 136, 14)
icon('app-windows', UI, ['windows', 'multiple', 'restore', 'stack'],
     line=[fw, P('M72 176 H46 A14 14 0 0 1 32 162 V54 A14 14 0 0 1 46 40 H170 A14 14 0 0 1 184 54 V80')],
     detail=[L(72, 124, 224, 124)],
     area=[fw])

# ---------------------------------------------------------------- arrows-clockwise variants
ac = load('arrows-clockwise')
icon('arrows-clockwise-slash', UI, ['sync off', 'refresh off', 'no sync', 'paused'], line=ac['line'] + [SLASH])
ah1, ah2 = (184.57, 71.43), (71.43, 184.57)
acw = [ac['line'][0], ac['line'][2], PL([(ah1[0], ah1[1] - 28), ah1, (ah1[0] - 28, ah1[1])]),
       PL([(ah2[0], ah2[1] + 28), ah2, (ah2[0] + 28, ah2[1])])]
icon('arrows-clockwise-warning', UI, ['sync error', 'refresh', 'failed', 'exclamation', 'refresh failed'],
     line=acw + [L(128, 96, 128, 128)], dot=[C(128, 160, 14)])

# ---------------------------------------------------------------- asterisk-circle
ast = [L(*polar((128, 128), 52, a), *polar((128, 128), 52, a + 180)) for a in (-90, -30, 30)]
icon('asterisk-circle', UI, ['asterisk circle', 'asterisk', 'circle', 'interface'],
     line=[C(128, 128, 96)], detail=ast, area=[C(128, 128, 96)])

# ---------------------------------------------------------------- backspace
bs_d = 'M88 48 H208 A16 16 0 0 1 224 64 V192 A16 16 0 0 1 208 208 H88 L32 128 Z'
icon('backspace', UI, ['delete', 'erase', 'keyboard', 'back', 'delete key'],
     line=[P(bs_d)], detail=[L(124, 104, 172, 152), L(172, 104, 124, 152)], area=[P(bs_d)])
bsr_d = 'M168 48 H48 A16 16 0 0 0 32 64 V192 A16 16 0 0 0 48 208 H168 L224 128 Z'
icon('backspace-reverse', UI, ['delete forward', 'key', 'erase', 'keyboard'],
     line=[P(bsr_d)], detail=[L(84, 104, 132, 152), L(132, 104, 84, 152)], area=[P(bsr_d)])

# ---------------------------------------------------------------- badges (rank chevrons)
def chevron(top):
    return [(48, top + 40), (128, top), (208, top + 40), (208, top + 76), (128, top + 36), (48, top + 76)]
CH1, CH2 = chevron(52), chevron(132)
icon('badges', UI, ['badges', 'interface', 'symbol'], line=[PG(CH1), PG(CH2)], area=[PG(CH1), PG(CH2)])
icon('badges-slash', UI, ['badges', 'disabled', 'off', 'interface'], line=[PG(CH1), PG(CH2), SLASH])

# ---------------------------------------------------------------- bell-snooze
bck = load('bell-check')
icon('bell-snooze', UI, ['snooze', 'bell', 'notification', 'sleep', 'later'],
     line=bck['line'][:2] + [PL([(162, 164), (206, 164), (162, 206), (206, 206)])], area=bck['area'])

# ---------------------------------------------------------------- bookmark badges
BM = [(64, 32), (192, 32), (192, 224), (128, 184), (64, 224)]
BC = (184, 184)
d60, a60 = cut_polygon(BM, BC, 60)
d66, a66 = cut_polygon(BM, BC, 66)
icon('bookmark-check', UI, ['bookmark', 'saved', 'check', 'done', 'bookmarked'],
     line=[P(d60), PL([(158, 186), (176, 204), (210, 168)])], area=[P(a60)])
icon('bookmark-minus', UI, ['bookmark', 'remove', 'minus', 'unsave', 'remove bookmark'],
     line=[P(d60), L(158, 184, 210, 184)], area=[P(a60)])
icon('bookmark-plus', UI, ['add bookmark', 'save', 'bookmark', 'new', 'favourite'],
     line=[P(d60), L(184, 158, 184, 210), L(158, 184, 210, 184)], area=[P(a60)])
icon('bookmark-x', UI, ['bookmark', 'remove', 'delete', 'x'],
     line=[P(d60), L(166, 166, 202, 202), L(202, 166, 166, 202)], area=[P(a60)])

hs = 0.3
def hp(x, y):
    return (184 + (x - 128) * hs, 186 + (y - 132) * hs)
heart_s = (f'M{pt(hp(128, 212))} C{pt(hp(128, 212))} {pt(hp(32, 160))} {pt(hp(32, 98))} '
           f'A{f(50 * hs)} {f(50 * hs)} 0 0 1 {pt(hp(128, 78))} A{f(50 * hs)} {f(50 * hs)} 0 0 1 {pt(hp(224, 98))} '
           f'C{pt(hp(224, 160))} {pt(hp(128, 212))} {pt(hp(128, 212))} Z')
icon('bookmark-heart', UI, ['bookmark', 'favorite', 'heart', 'like'],
     line=[P(d66), P(heart_s)], area=[P(a66), P(heart_s)])
star_s = PG([polar((184, 188), 34 if i % 2 == 0 else 15, -90 + i * 36) for i in range(10)])
icon('bookmark-star', UI, ['bookmark', 'favorite', 'star', 'starred'],
     line=[P(d66), star_s], area=[P(a66), star_s])

print(save(overwrite=True))
