import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *


def T(cmds, deg=0, c=(128, 128), dx=0, dy=0):
    """Path from command tuples, rotated by deg about c then shifted.
    ('M',p) ('L',p) ('A',r,large,sweep,p) ('C',p1,p2,p) ('Z',)"""
    def tp(p):
        q = rot([p], deg, c)[0]
        return (q[0] + dx, q[1] + dy)
    out = []
    for cm in cmds:
        k = cm[0]
        if k in 'ML':
            out.append(k + pt(tp(cm[1])))
        elif k == 'A':
            out.append(f'A{f(cm[1])} {f(cm[1])} 0 {cm[2]} {cm[3]} {pt(tp(cm[4]))}')
        elif k == 'C':
            out.append('C' + ' '.join(pt(tp(p)) for p in cm[1:]))
        else:
            out.append('Z')
    return ' '.join(out)


def TP(points, deg, c=(128, 128), dx=0, dy=0):
    return [(x + dx, y + dy) for x, y in rot(points, deg, c)]


def drop_path(cx, cy, r):
    """Water drop whose round part is centred at (cx, cy) with radius r (scaled from the core drop)."""
    k = r / 64
    s = lambda x, y: pt((cx + (x - 128) * k, cy + (y - 152) * k))
    return (f'M{s(128, 32)} C{s(104, 64)} {s(64, 112)} {s(64, 152)} A{f(r)} {f(r)} 0 0 0 {s(192, 152)} '
            f'C{s(192, 112)} {s(152, 64)} {s(128, 32)} Z')


def sparkle_path(cx, cy, R):
    k = R / 96
    s = lambda x, y: pt((cx + x * k, cy + y * k))
    return (f'M{s(0, -96)} C{s(8, -32)} {s(32, -8)} {s(96, 0)} C{s(32, 8)} {s(8, 32)} {s(0, 96)} '
            f'C{s(-8, 32)} {s(-32, 8)} {s(-96, 0)} C{s(-32, -8)} {s(-8, -32)} {s(0, -96)} Z')


D, O, TM, FD, SP = 'Design', 'Objects', 'Time', 'Food', 'Sports'

# ================================================================ Design
# paint-brush: drawn upright, rotated 45deg so the handle points up-right
handle = T([('M', (112, 28)), ('A', 16, 0, 1, (144, 28)), ('L', (144, 100)), ('L', (112, 100)), ('Z',)], 45)
brush_head = T([('M', (100, 100)), ('L', (156, 100)), ('L', (156, 176)),
                ('C', (156, 208), (144, 224), (124, 236)), ('C', (104, 220), (100, 200), (100, 176)), ('Z',)], 45)
icon('paint-brush', D, ['brush', 'paint', 'art', 'draw', 'style'],
     line=[P(handle), P(brush_head)], detail=[P(T([('M', (100, 140)), ('L', (156, 140))], 45))], area=[P(brush_head)])

pal = ('M128 32 A96 96 0 0 0 128 224 C152 224 160 208 152 192 C144 176 152 160 172 160 H192 '
       'A32 32 0 0 0 224 128 A96 96 0 0 0 128 32 Z')
icon('palette', D, ['colors', 'paint', 'art', 'theme', 'design'],
     line=[P(pal)], area=[P(pal)], dotcut=[C(84, 112, 16), C(124, 76, 16), C(172, 100, 16), C(88, 164, 16)])

nib = [(128, 216), (68, 140), (96, 88), (160, 88), (188, 140)]
icon('pen-nib', D, ['pen', 'vector', 'bezier', 'write', 'design'],
     line=[PG(nib), R(96, 40, 64, 48, 10)], detail=[L(128, 152, 128, 180)],
     area=[PG(nib), R(96, 40, 64, 48, 10)], dotcut=[C(128, 132, 14)])

er = rot([(40, 84), (216, 84), (216, 172), (40, 172)], -45)
icon('eraser', D, ['erase', 'delete', 'remove', 'clear', 'rubber'],
     line=[PG(er), L(120, 216, 216, 216)], detail=[PL(rot([(104, 84), (104, 172)], -45))], area=[PG(er)])

EDC = dict(deg=45, c=(128, 128), dx=0, dy=0)
dropper_body = T([('M', (108, 84)), ('L', (148, 84)), ('L', (148, 204)), ('L', (128, 240)),
                  ('L', (108, 204)), ('Z',)], **EDC)
dropper_bulb = T([('M', (104, 76)), ('L', (104, 44)), ('A', 24, 0, 1, (152, 44)), ('L', (152, 76))], **EDC)
collar = T([('M', (84, 80)), ('L', (172, 80))], **EDC)
icon('eyedropper', D, ['color picker', 'pipette', 'sample', 'dropper'],
     line=[P(dropper_body), P(dropper_bulb), P(collar)], area=[P(dropper_body)])

u = (1 / math.sqrt(2), -1 / math.sqrt(2))
wand = capsule((96, 160), 56, 16, u)
icon('magic-wand', D, ['magic', 'wizard', 'auto', 'enhance', 'ai'],
     line=[P(wand), P(sparkle_path(180, 76, 40))], detail=[L(104.5, 128.9, 127.1, 151.5)], area=[P(wand), P(sparkle_path(180, 76, 40))], dot=[C(88, 56, 12), C(208, 168, 12)])

bucket = T([('M', (48, 72)), ('L', (176, 72)), ('L', (162, 176)), ('A', 16, 0, 1, (146, 192)), ('L', (78, 192)),
            ('A', 16, 0, 1, (62, 176)), ('Z',)], 45, c=(112, 136), dx=-8, dy=-8)
bail = T([('M', (48, 72)), ('A', 72, 0, 1, (176, 72))], 45, c=(112, 136), dx=-8, dy=-8)
icon('paint-bucket', D, ['fill', 'bucket', 'paint', 'color'],
     line=[P(bucket), P(bail), P(drop_path(196, 196, 20))], area=[P(bucket), P(drop_path(196, 196, 20))])

icon('crop', D, ['crop', 'trim', 'cut', 'resize', 'frame'],
     line=[PL([(72, 32), (72, 184), (224, 184)]), PL([(32, 72), (184, 72), (184, 224)])])

rl = rot([(28, 92), (228, 92), (228, 164), (28, 164)], -45)
ticks = []
for i, x in enumerate((68, 108, 148, 188)):
    ticks.append(PL(rot([(x, 92), (x, 92 + (36 if i % 2 else 24))], -45)))
icon('ruler', D, ['measure', 'length', 'scale', 'size'], line=[PG(rl)], detail=ticks, area=[PG(rl)])

def towards(a, b, ra):
    d = dist(a, b)
    return (a[0] + (b[0] - a[0]) * ra / d, a[1] + (b[1] - a[1]) * ra / d)
lc, rc = (76, 184), (180, 184)
icon('scissors', D, ['cut', 'snip', 'trim', 'clip'],
     line=[C(*lc, 32), C(*rc, 32), PL([towards(lc, (184, 40), 32), (184, 40)]), PL([towards(rc, (72, 40), 32), (72, 40)])],
     area=[C(*lc, 32), C(*rc, 32)])

# ================================================================ Objects
y1 = 72 - math.sqrt(48 ** 2 - 16 ** 2); y2 = 72 + math.sqrt(48 ** 2 - 20 ** 2)
wr = T([('M', (112, y1)), ('L', (112, 80)), ('L', (144, 80)), ('L', (144, y1)), ('A', 48, 0, 1, (148, y2)),
        ('L', (148, 204)), ('A', 20, 0, 1, (108, 204)), ('L', (108, y2)), ('A', 48, 0, 1, (112, y1)), ('Z',)], 45)
icon('wrench', O, ['tool', 'settings', 'repair', 'fix', 'spanner'], line=[P(wr)], area=[P(wr)])

HMC = dict(deg=-45, c=(128, 128), dx=10, dy=18)
hh = T([('M', (104, 36)), ('L', (196, 36)), ('L', (196, 92)), ('L', (104, 92)), ('L', (60, 76)), ('L', (60, 52)), ('Z',)], **HMC)
hd = T([('M', (108, 92)), ('L', (148, 92)), ('L', (148, 200)), ('A', 20, 0, 1, (108, 200)), ('Z',)], **HMC)
icon('hammer', O, ['tool', 'build', 'construction', 'repair'], line=[P(hh), P(hd)], area=[P(hh), P(hd)])

SDC = dict(deg=45, c=(128, 128), dx=-6, dy=6)
sh = T([('M', (92, 36)), ('A', 28, 0, 1, (120, 8)), ('L', (136, 8)), ('A', 28, 0, 1, (164, 36)), ('L', (164, 124)),
        ('L', (92, 124)), ('Z',)], **SDC)
icon('screwdriver', O, ['tool', 'repair', 'fix', 'settings'],
     line=[P(sh), P(T([('M', (128, 124)), ('L', (128, 240))], **SDC))], detail=[P(T([('M', (128, 44)), ('L', (128, 92))], **SDC))],
     area=[P(sh)])

icon('toolbox', O, ['tools', 'kit', 'repair', 'box', 'case'],
     line=[R(32, 88, 192, 128, 14), P('M88 88 V64 A16 16 0 0 1 104 48 H152 A16 16 0 0 1 168 64 V88')],
     detail=[L(32, 136, 104, 136), L(152, 136, 224, 136), R(104, 124, 48, 32, 8)], area=[R(32, 88, 192, 128, 14)])

mag = 'M48 48 V136 A80 80 0 0 0 208 136 V48 H160 V136 A32 32 0 0 1 96 136 V48 Z'
icon('magnet', O, ['magnetic', 'attract', 'pull', 'physics'],
     line=[P(mag)], detail=[L(48, 88, 96, 88), L(160, 88, 208, 88)], area=[P(mag)])

fl = T([('M', (84, 32)), ('L', (172, 32)), ('A', 12, 0, 1, (184, 44)), ('L', (184, 64)), ('L', (152, 104)), ('L', (152, 212)),
        ('A', 12, 0, 1, (140, 224)), ('L', (116, 224)), ('A', 12, 0, 1, (104, 212)), ('L', (104, 104)), ('L', (72, 64)),
        ('L', (72, 44)), ('A', 12, 0, 1, (84, 32)), ('Z',)], 45, dx=-7, dy=7)
icon('flashlight', O, ['torch', 'light', 'beam', 'lamp'],
     line=[P(fl)], detail=[P(T([('M', (72, 64)), ('L', (184, 64))], 45, dx=-7, dy=7))], area=[P(fl)],
     dotcut=[C(*TP([(128, 152)], 45, dx=-7, dy=7)[0], 12)])

shade = [(88, 40), (168, 40), (208, 128), (48, 128)]
icon('lamp', O, ['light', 'desk lamp', 'home', 'furniture'],
     line=[PG(shade), L(128, 128, 128, 216), L(80, 216, 176, 216)], area=[PG(shade)])

icon('lifebuoy', O, ['help', 'support', 'rescue', 'lifesaver', 'ring'],
     line=[C(128, 128, 96), C(128, 128, 44)],
     detail=[L(*polar((128, 128), 44, a), *polar((128, 128), 96, a)) for a in (45, 135, 225, 315)],
     area=[C(128, 128, 96)], hole=[C(128, 128, 36)])

bl = 'M32 168 L52 72 A16 16 0 0 1 68 56 H96 A16 16 0 0 1 112 72 V168'
br = 'M144 168 V72 A16 16 0 0 1 160 56 H188 A16 16 0 0 1 204 72 L224 168'
icon('binoculars', O, ['search', 'explore', 'view', 'discover', 'zoom'],
     line=[C(72, 168, 40), C(184, 168, 40), P(bl), P(br), L(112, 112, 144, 112)],
     area=[P(bl + ' Z'), P(br + ' Z'), C(72, 168, 40), C(184, 168, 40)])

icon('glasses', O, ['eyeglasses', 'spectacles', 'reading', 'vision'],
     line=[C(72, 152, 40), C(184, 152, 40), P('M112 152 A16 16 0 0 1 144 152'),
           PL([(32, 152), (56, 80), (76, 72)]), PL([(224, 152), (200, 80), (180, 72)])],
     area=[C(72, 152, 40), C(184, 152, 40)])

icon('balloon', O, ['party', 'birthday', 'celebrate', 'event'],
     line=[E(128, 104, 68, 72), PG([(128, 176), (114, 192), (142, 192)]), P('M128 192 C128 204 116 212 124 224')],
     detail=[P('M100 96 A32 32 0 0 1 120 68')], area=[E(128, 104, 68, 72)])

cone = [(32, 224), (80, 100), (156, 176)]
icon('confetti', O, ['party', 'celebrate', 'popper', 'congrats', 'tada'],
     line=[PG(cone), P('M144 104 C152 80 176 80 184 56'), L(112, 64, 120, 40), L(176, 128, 208, 120)],
     area=[PG(cone)], dot=[C(160, 40, 12), C(216, 72, 12), C(208, 176, 12)])

back = 'M64 120 V72 A24 24 0 0 1 88 48 H168 A24 24 0 0 1 192 72 V120'
frame = 'M80 160 V144 A24 24 0 0 0 32 144 V200 H224 V144 A24 24 0 0 0 176 144 V160 Z'
icon('armchair', O, ['chair', 'seat', 'furniture', 'sofa', 'lounge'],
     line=[P(back), P(frame), L(56, 200, 56, 224), L(200, 200, 200, 224)],
     area=[P('M64 120 V72 A24 24 0 0 1 88 48 H168 A24 24 0 0 1 192 72 V120 V160 H64 Z'), P(frame)])

cback = 'M56 128 V96 A24 24 0 0 1 80 72 H176 A24 24 0 0 1 200 96 V128'
cframe = 'M72 168 V148 A20 20 0 0 0 32 148 V200 H224 V148 A20 20 0 0 0 184 148 V168 Z'
icon('couch', O, ['sofa', 'furniture', 'living room', 'seat', 'home'],
     line=[P(cback), P(cframe), L(48, 200, 48, 216), L(208, 200, 208, 216)],
     detail=[L(128, 104, 128, 168)],
     area=[P('M56 128 V96 A24 24 0 0 1 80 72 H176 A24 24 0 0 1 200 96 V168 H56 Z'), P(cframe)])

shirt = 'M96 40 A32 32 0 0 0 160 40 L204 56 L224 104 L184 116 V216 H72 V116 L32 104 L52 56 Z'
icon('t-shirt', O, ['clothing', 'shirt', 'apparel', 'fashion', 'merch'], line=[P(shirt)], area=[P(shirt)])

shoe = ('M32 176 V88 A16 16 0 0 1 48 72 H72 C76 92 92 104 116 100 L176 128 C208 132 224 148 224 168 V176 '
        'A16 16 0 0 1 208 192 H48 A16 16 0 0 1 32 176 Z')
icon('sneaker', O, ['shoe', 'running', 'footwear', 'sport', 'fitness'],
     line=[P(shoe)], detail=[L(32, 156, 224, 156), L(128, 106, 118, 126), L(156, 119, 146, 139)], area=[P(shoe)])

# ================================================================ Time
hg = ('M72 32 H184 V64 C184 100 136 112 136 128 C136 144 184 156 184 192 V224 H72 V192 C72 156 120 144 120 128 '
      'C120 112 72 100 72 64 Z')
icon('hourglass', TM, ['time', 'wait', 'loading', 'sand', 'timer'],
     line=[P(hg), L(48, 32, 208, 32), L(48, 224, 208, 224)], area=[P(hg)])

wc = (128, 140)
icon('timer', TM, ['countdown', 'time', 'clock', 'duration'],
     line=[C(*wc, 84), L(128, 56, 128, 32), L(104, 32, 152, 32)],
     detail=[P(f'M128 140 V92 {arc_to(wc, 48, (128, 92), polar(wc, 48, 30), lambda m: m[0])} Z')],
     area=[C(*wc, 84)])
icon('stopwatch', TM, ['timer', 'time', 'lap', 'speed', 'race'],
     line=[C(*wc, 84), L(128, 56, 128, 32), L(104, 32, 152, 32), L(*polar(wc, 84, -45), *polar(wc, 104, -45))],
     detail=[L(128, 140, 160, 108)], area=[C(*wc, 84)])

ac = (128, 136)
icon('alarm', TM, ['alarm clock', 'wake', 'time', 'reminder', 'clock'],
     line=[C(*ac, 80), P('M36 84 A48 48 0 0 1 84 36'), P('M220 84 A48 48 0 0 0 172 36'),
           L(*polar(ac, 80, 125), *polar(ac, 104, 125)), L(*polar(ac, 80, 55), *polar(ac, 104, 55))],
     detail=[PL([(128, 96), (128, 136), (156, 152)])], area=[C(*ac, 80)])

cal_line = [R(40, 48, 176, 168, 14), L(88, 32, 88, 72), L(168, 32, 168, 72)]
for nm, tags, det in [
    ('calendar-check', ['date', 'scheduled', 'done', 'event', 'confirmed'], [PL([(100, 160), (120, 180), (160, 140)])]),
    ('calendar-plus', ['add event', 'new', 'schedule', 'date'], [L(128, 132, 128, 188), L(100, 160, 156, 160)]),
    ('calendar-x', ['cancel', 'remove event', 'date', 'unavailable'], [L(108, 140, 148, 180), L(148, 140, 108, 180)]),
]:
    icon(nm, TM, tags, line=cal_line, detail=[L(40, 104, 216, 104)] + det, area=[R(40, 48, 176, 168, 14)])

# ================================================================ Food
cc, cr, bc, brr = (128, 128), 96, (204, 52), 44
bp, bq = circle_x(cc, cr, bc, brr)
cookie = (f'M{pt(bp)} ' + arc_to(cc, cr, bp, bq, lambda m: dist(m, bc)) + ' ' +
          arc_to(bc, brr, bq, bp, lambda m: -dist(m, cc)) + ' Z')
icon('cookie', FD, ['biscuit', 'snack', 'cookies', 'privacy', 'sweet'],
     line=[P(cookie)], area=[P(cookie)], dotcut=[C(92, 108, 14), C(140, 132, 14), C(100, 168, 14), C(160, 176, 14), C(124, 76, 14)])

wave = 'M40 156 C56 168 70 168 84 156 C98 144 114 144 128 156 C142 168 158 168 172 156 C186 144 200 144 216 156'
icon('cake', FD, ['birthday', 'celebration', 'party', 'dessert'],
     line=[R(40, 112, 176, 104, 14), L(88, 80, 88, 112), L(128, 80, 128, 112), L(168, 80, 168, 112)],
     detail=[P(wave)], area=[R(40, 112, 176, 104, 14)], dot=[C(88, 48, 12), C(128, 48, 12), C(168, 48, 12)])

pz = 'M128 224 L40 64 A184 184 0 0 1 216 64 Z'
def edge_x(y, side):
    return 128 + side * (224 - y) / 160 * 88
icon('pizza', FD, ['food', 'slice', 'fast food', 'italian'],
     line=[P(pz)], detail=[P(f'M{f(edge_x(96, -1))} 96 A184 184 0 0 1 {f(edge_x(96, 1))} 96')],
     area=[P(pz)], dotcut=[C(110, 138, 12), C(146, 138, 12)])

icon('fork-knife', FD, ['restaurant', 'dining', 'food', 'eat', 'cutlery'],
     line=[P('M52 32 V80 A32 32 0 0 0 116 80 V32'), L(84, 32, 84, 224),
           P('M204 140 H156 C156 88 168 52 204 32 V224')],
     area=[P('M204 140 H156 C156 88 168 52 204 32 Z')])

bowl = 'M80 32 H176 L184 80 A56 56 0 0 1 72 80 Z'
icon('wine', FD, ['glass', 'drink', 'alcohol', 'bar', 'celebrate'],
     line=[P(bowl), L(128, 136, 128, 216), L(88, 216, 168, 216)], detail=[L(74, 72, 182, 72)],
     area=[P(bowl)])

fbowl = 'M32 120 H224 A96 96 0 0 1 32 120 Z'
icon('bowl-food', FD, ['soup', 'meal', 'ramen', 'hot', 'food'],
     line=[P(fbowl)] + [P(f'M{x} 40 C{x - 16} 56 {x + 16} 72 {x} 88') for x in (88, 128, 168)],
     area=[P(fbowl)])

bun = 'M48 112 C48 64 88 40 128 40 C168 40 208 64 208 112 Z'
bot = 'M48 176 H208 V192 A24 24 0 0 1 184 216 H72 A24 24 0 0 1 48 192 Z'
icon('hamburger', FD, ['burger', 'fast food', 'food', 'sandwich'],
     line=[P(bun), L(32, 144, 224, 144), P(bot)], area=[P(bun), P(bot)], dotcut=[C(104, 80, 10), C(152, 80, 10)])

scoop = 'M72 128 A64 64 0 1 1 184 128 Z'
icon('ice-cream', FD, ['dessert', 'cone', 'sweet', 'summer', 'gelato'],
     line=[P(scoop), PL([(84, 128), (128, 224), (172, 128)])], area=[P(scoop), PG([(84, 128), (128, 224), (172, 128)])])

apple = ('M128 88 C104 72 48 72 48 136 C48 184 80 220 104 220 C116 220 120 212 128 212 C136 212 140 220 152 220 '
         'C176 220 208 184 208 136 C208 72 152 72 128 88 Z')
leaf = 'M136 60 C140 40 160 30 180 32 C176 52 160 62 136 60 Z'
icon('apple', FD, ['fruit', 'healthy', 'food', 'teacher', 'nutrition'],
     line=[P(apple), P('M128 88 C128 72 130 60 136 52'), P(leaf)], area=[P(apple), P(leaf)])

# ================================================================ Sports
icon('dice-five', SP, ['dice', 'game', 'random', 'luck', 'board game'],
     line=[R(40, 40, 176, 176, 20)], area=[R(40, 40, 176, 176, 20)],
     dotcut=[C(88, 88, 16), C(168, 88, 16), C(128, 128, 16), C(88, 168, 16), C(168, 168, 16)])

pent = regular_polygon((128, 128), 38, 5)
icon('soccer-ball', SP, ['football', 'sport', 'ball', 'game'],
     line=[C(128, 128, 96)],
     detail=[PG(pent)] + [L(*p, *polar((128, 128), 96, -90 + i * 72)) for i, p in enumerate(pent)],
     area=[C(128, 128, 96)])

def side_arc(sign):
    a = polar((128, 128), 96, 180 + 45) if sign < 0 else polar((128, 128), 96, -45)
    b = polar((128, 128), 96, 135) if sign < 0 else polar((128, 128), 96, 45)
    return P(f'M{pt(a)} ' + arc_to((128 + sign * 135.76, 128), 96, a, b, lambda m: -abs(m[0] - 128)))
icon('basketball', SP, ['ball', 'sport', 'nba', 'game', 'hoops'],
     line=[C(128, 128, 96)], detail=[L(128, 32, 128, 224), L(32, 128, 224, 128), side_arc(-1), side_arc(1)],
     area=[C(128, 128, 96)])

ta, tb = polar((128, 128), 96, -120), polar((128, 128), 96, 120)
icon('tennis-ball', SP, ['ball', 'sport', 'tennis', 'game'],
     line=[C(128, 128, 96)],
     detail=[P(f'M{pt(ta)} C{f(ta[0] + 40)} 90 {f(ta[0] + 40)} 166 {pt(tb)}'),
             P(f'M{f(256 - ta[0])} {f(ta[1])} C{f(256 - ta[0] - 40)} 90 {f(256 - ta[0] - 40)} 166 {f(256 - tb[0])} {f(tb[1])}')],
     area=[C(128, 128, 96)])

knight = ('M80 184 C76 160 96 148 112 136 L76 144 A18 18 0 0 1 56 116 L104 60 L116 32 L140 52 '
          'C184 64 200 104 200 144 V184 Z')
icon('chess-knight', SP, ['chess', 'strategy', 'game', 'horse', 'board game'],
     line=[P(knight), L(56, 216, 200, 216)], area=[P(knight)], dotcut=[C(124, 84, 12)])

icon('barbell', SP, ['gym', 'fitness', 'weights', 'workout', 'exercise'],
     line=[R(56, 64, 40, 128, 12), R(160, 64, 40, 128, 12), L(96, 128, 160, 128), L(32, 128, 56, 128), L(200, 128, 224, 128)],
     area=[R(56, 64, 40, 128, 12), R(160, 64, 40, 128, 12)])

print(save(overwrite=True))
