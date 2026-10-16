"""Batch 100: animals (and monkey bars)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build  # boolean helpers (skia-pathops)

A = 'Animals'


# ---------------------------------------------------------------- helpers
def circ(c, r):
    return (f'M{f(c[0] - r)} {f(c[1])} A{f(r)} {f(r)} 0 1 1 {f(c[0] + r)} {f(c[1])} '
            f'A{f(r)} {f(r)} 0 1 1 {f(c[0] - r)} {f(c[1])} Z')


def ell(cx, cy, rx, ry, deg=0):
    a = math.radians(deg)
    p1 = (cx + rx * math.cos(a), cy + rx * math.sin(a))
    p2 = (cx - rx * math.cos(a), cy - rx * math.sin(a))
    return f'M{pt(p1)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p2)} A{f(rx)} {f(ry)} {f(deg)} 1 1 {pt(p1)} Z'


def rrect(x, y, w, h, r):
    return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
            f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')


def _flip(p):
    """Reverse every contour so union output winds like the raw circle/ellipse sources (screen clockwise)."""
    import pathops
    out = pathops.Path()
    for c in p.contours:
        c.reverse()
        out.addPath(c)
    return out


def U(*ds):
    """Union of closed shapes as one path."""
    return build.to_d(_flip(SH(list(ds))))


def SH(ds):
    """Filled shape; each contour normalised first so mixed windings union correctly."""
    return build.union(*[build.filled([d]) for d in ds])


def DIFF(a, *subs):
    return build.to_d(_flip(build.difference(SH([a]), SH(list(subs)))))


def tube(d, w):
    """Closed outline of a centreline stroked at width w (round caps)."""
    return build.to_d(_flip(build.stroke([d], w)))


def _bez(p, t):
    n = len(p) - 1
    x = y = 0.0
    for i, q in enumerate(p):
        b = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
        x += b * q[0]; y += b * q[1]
    return (x, y)


def sample(d, step=1.5):
    """Flatten path data (or an element) into a list of (points, closed) contours."""
    from fontTools.pens.basePen import BasePen
    from fontTools.svgLib.path import parse_path
    if d.lstrip().startswith('<'):
        import xml.etree.ElementTree as ET
        d = build.element_d(ET.fromstring(d))

    class Pen(BasePen):
        def __init__(self):
            super().__init__(None)
            self.out, self.cur = [], []

        def _moveTo(self, p):
            if self.cur:
                self.out.append((self.cur, False))
            self.cur = [p]

        def _lineTo(self, p):
            a = self.cur[-1]
            n = max(1, int(dist(a, p) / step))
            self.cur += [(a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n) for i in range(1, n + 1)]

        def _curve(self, s):
            ln = sum(dist(s[i], s[i + 1]) for i in range(len(s) - 1))
            n = max(2, int(ln / step))
            self.cur += [_bez(s, i / n) for i in range(1, n + 1)]

        def _curveToOne(self, p1, p2, p3):
            self._curve([self.cur[-1], p1, p2, p3])

        def _qCurveToOne(self, p1, p2):
            self._curve([self.cur[-1], p1, p2])

        def _closePath(self):
            if self.cur:
                if dist(self.cur[-1], self.cur[0]) > 0.01:
                    self._lineTo(self.cur[0])
                self.out.append((self.cur, True))
            self.cur = []

        def _endPath(self):
            if self.cur:
                self.out.append((self.cur, False))
            self.cur = []

    pen = Pen()
    parse_path(d, pen)
    if pen.cur:
        pen.out.append((pen.cur, False))
    return pen.out


def runs(d, shapes, inside=False):
    """Parts of the outline d that lie outside (or inside) the filled shapes, as open/closed paths."""
    shp = SH(shapes if isinstance(shapes, list) else [shapes])
    res = []
    for pts, closed in sample(d):
        if closed and len(pts) > 1 and dist(pts[0], pts[-1]) < 0.01:
            pts = pts[:-1]
        keep = [bool(shp.contains(p)) == inside for p in pts]
        if all(keep):
            res.append(P(poly(pts, closed)))
            continue
        if not any(keep):
            continue
        groups, g = [], []
        for p, k in zip(pts, keep):
            if k:
                g.append(p)
            elif g:
                groups.append(g); g = []
        if g:
            groups.append(g)
        if closed and keep[0] and keep[-1] and len(groups) > 1:
            groups[0] = groups.pop() + groups[0]
        res += [P(poly(g)) for g in groups if len(g) > 1]
    return res


def layered(front, back):
    """front shape over back shape: (lines, details). Hidden edge of front inside back becomes a cut."""
    lines = runs(back, front) + [P(front)]
    details = runs(front, back, inside=True)
    return lines, details


def mx(p):
    return (256 - p[0], p[1])


def clip_in(d, shape):
    """Open stroke d clipped to the inside of shape."""
    return runs(d, shape, inside=True)


# ---------------------------------------------------------------- bat
bat = ('M128 100 L144 76 L150 102 C168 100 196 88 224 72 Q194 104 202 152 Q184 124 160 144 Q144 148 140 172 '
       'Q128 188 116 172 Q112 148 96 144 Q72 124 54 152 Q62 104 32 72 C60 88 88 100 106 102 L112 76 Z')
import re
bat = re.sub(r'(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)', lambda m: f'{m.group(1)} {f(128 + (float(m.group(2)) - 128) * 1.3)}', bat)
icon('bat', A, ['bat', 'halloween', 'night', 'animal'], line=[P(bat)], area=[P(bat)])

# ---------------------------------------------------------------- bear
bear = U(circ((128, 140), 80), circ((66, 72), 28), circ((190, 72), 28))
icon('bear', A, ['bear', 'teddy', 'animal', 'face', 'wildlife'],
     line=[P(bear)], detail=[E(128, 170, 36, 26)], area=[P(bear)],
     dotcut=[C(96, 122, 14), C(160, 122, 14), C(128, 160, 14)])

# ---------------------------------------------------------------- bee
bee_body = U('M128 92 C156 92 172 120 172 150 C172 180 150 202 128 220 C106 202 84 180 84 150 C84 120 100 92 128 92 Z',
             circ((128, 76), 22))
wings = U(ell(76, 100, 42, 24, 30), ell(180, 100, 42, 24, -30))
bl, bd = layered(bee_body, wings)
stripes = clip_in(L(60, 140, 196, 140), bee_body) + clip_in(L(60, 176, 196, 176), bee_body)
icon('bee', A, ['bee', 'insect', 'honey', 'nature'],
     line=bl + [P('M118 58 C112 46 104 40 94 38'), P('M138 58 C144 46 152 40 162 38')],
     detail=bd + stripes, area=[P(bee_body), P(wings)])

# ---------------------------------------------------------------- bone-slash
bone = load('bone')
icon('bone-slash', A, ['bone', 'disabled', 'off', 'animals'], line=bone['line'] + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- canary
canary = U(circ((150, 80), 36), ell(124, 140, 62, 46, -35), 'M90 166 L46 192 L80 200 L110 186 Z',
           'M180 70 L210 84 L180 98 Z')
icon('canary', A, ['bird', 'canary', 'testing', 'release'],
     line=[P(canary), L(124, 190, 124, 216), L(152, 180, 152, 216), L(104, 216, 192, 216)],
     detail=[P('M100 132 C112 160 144 166 168 146')], area=[P(canary)], dotcut=[C(158, 76, 12)])

# ---------------------------------------------------------------- cat
cat = 'M64 120 L56 40 L104 72 H152 L200 40 L192 120 C196 176 164 208 128 208 C92 208 60 176 64 120 Z'
icon('cat', A, ['cat', 'pet', 'kitten', 'animal'], line=[P(cat)],
     detail=[P('M108 164 C114 176 124 176 128 166 C132 176 142 176 148 164')], area=[P(cat)],
     dotcut=[C(100, 130, 14), C(156, 130, 14)])

# ---------------------------------------------------------------- chicken
chick = U(ell(140, 140, 72, 54), circ((88, 84), 32), 'M168 104 L204 48 L216 124 Z',
          circ((80, 52), 12), circ((102, 50), 12), 'M60 78 L36 92 L60 102 Z')
icon('chicken', A, ['chicken', 'hen', 'rooster', 'farm'],
     line=[P(chick), L(120, 194, 116, 220), L(156, 194, 160, 220)],
     detail=[P('M116 136 C132 166 172 166 192 136')], area=[P(chick)], dotcut=[C(92, 80, 12)])

# ---------------------------------------------------------------- cow
cow_head = U(rrect(76, 60, 104, 104, 36), ell(128, 172, 52, 40), ell(56, 100, 24, 12, 15), ell(200, 100, 24, 12, -15))
icon('cow', A, ['cattle', 'farm', 'dairy', 'cow', 'ox'],
     line=[P(cow_head), P('M96 62 C80 60 64 48 60 32'), P('M160 62 C176 60 192 48 196 32')],
     detail=clip_in(P('M60 160 C96 140 160 140 196 160'), cow_head), area=[P(cow_head)],
     dotcut=[C(104, 108, 12), C(152, 108, 12), C(108, 184, 12), C(148, 184, 12)])


# ---------------------------------------------------------------- crab
def pac(c, r, open_deg, half=32):
    a = polar(c, r, open_deg + half)
    b = polar(c, r, open_deg - half)
    return f'M{pt(c)} L{pt(a)} A{f(r)} {f(r)} 0 1 1 {pt(b)} Z'


crab_body = ell(128, 152, 64, 40)
cl, cr = pac((64, 76), 28, -60), pac((192, 76), 28, -120)
legs = [L(68, 164, 36, 184), L(92, 186, 68, 216), L(188, 164, 220, 184), L(164, 186, 188, 216)]
icon('crab', A, ['crab', 'seafood', 'sea', 'crustacean'],
     line=[P(crab_body), P(cl), P(cr), L(80, 100, 98, 118), L(176, 100, 158, 118)] + legs,
     area=[P(crab_body), P(cl), P(cr)], dotcut=[C(108, 144, 12), C(148, 144, 12)])

# ---------------------------------------------------------------- deer
deer_head = U('M84 112 C84 92 104 84 128 84 C152 84 172 92 172 112 C172 140 156 176 148 196 C144 206 136 212 128 212 '
              'C120 212 112 206 108 196 C100 176 84 140 84 112 Z', ell(62, 116, 28, 14, -15), ell(194, 116, 28, 14, 15))
icon('deer', A, ['deer', 'antlers', 'wildlife', 'forest'],
     line=[P(deer_head), P('M108 86 C100 64 84 52 56 48'), L(90, 60, 84, 32),
           P('M148 86 C156 64 172 52 200 48'), L(166, 60, 172, 32)],
     area=[P(deer_head)], dotcut=[C(108, 124, 12), C(148, 124, 12), C(128, 186, 14)])

# ---------------------------------------------------------------- dog
dog_face = U(circ((128, 116), 64), ell(128, 168, 42, 34))
dog_ears = U(ell(68, 112, 24, 50, 15), ell(188, 112, 24, 50, -15))
dl, dd = layered(dog_face, dog_ears)
icon('dog', A, ['dog', 'puppy', 'pet', 'canine', 'animal'], line=dl, detail=dd, area=[P(dog_face), P(dog_ears)],
     dotcut=[C(106, 118, 12), C(150, 118, 12), C(128, 160, 16)])

# ---------------------------------------------------------------- dog-bowl
bowl = 'M40 160 H216 L200 206 A14 14 0 0 1 186 216 H70 A14 14 0 0 1 56 206 Z'
dbone = U(circ((82, 66), 18), circ((82, 106), 18), circ((174, 66), 18), circ((174, 106), 18), "M82 74 H174 V98 H82 Z")
icon('dog-bowl', A, ['pet', 'dog', 'bowl', 'food'], line=[P(bowl), P(dbone)], area=[P(bowl), P(dbone)])

# ---------------------------------------------------------------- dolphin
dolphin = ('M46 140 C52 128 62 124 76 120 C82 100 102 84 128 80 L152 46 L160 82 C192 92 208 120 204 156 '
           'L224 172 L200 180 L196 212 L180 176 C176 144 152 126 120 130 L100 162 L90 138 C76 148 56 150 46 140 Z')
icon('dolphin', A, ['dolphin', 'sea', 'ocean', 'mammal'], line=[P(dolphin)], area=[P(dolphin)], dotcut=[C(92, 110, 12)])

# ---------------------------------------------------------------- dragon
dragon = ('M84 216 L76 182 L48 174 L78 156 L56 134 L88 124 L88 100 L44 44 L112 80 H148 L204 100 Q222 108 212 124 '
          'L152 134 L196 152 Q202 164 188 166 L140 166 L132 216 Z')
icon('dragon', A, ['dragon', 'mythical', 'fantasy', 'zodiac'], line=[P(dragon)], area=[P(dragon)],
     dotcut=[C(132, 106, 12)])

# ---------------------------------------------------------------- duck
duck = U(circ((96, 80), 40), 'M40 152 C40 128 64 120 96 124 H160 L216 96 C224 140 200 200 128 200 H88 C60 200 40 180 40 152 Z',
         'M60 76 L32 92 L60 104 Z')
icon('duck', A, ['duck', 'bird', 'pond', 'rubber duck'], line=[P(duck)],
     detail=[P('M104 152 C120 176 160 176 176 148')], area=[P(duck)], dotcut=[C(104, 72, 12)])

# ---------------------------------------------------------------- eagle
eagle = ('M200 216 L180 176 L212 168 L184 148 L216 132 L184 116 C188 84 164 60 132 60 C108 60 96 72 88 84 '
         'C64 88 44 104 40 128 C40 136 48 140 52 132 C56 124 64 120 76 124 L104 132 L112 152 L120 216 Z')
icon('eagle', A, ['eagle', 'bird of prey', 'hawk', 'freedom'], line=[P(eagle)],
     detail=[P('M96 84 C100 100 104 116 104 132')], area=[P(eagle)], dotcut=[C(132, 96, 12)])

# ---------------------------------------------------------------- elephant
el_head = U(circ((128, 100), 52), tube('M128 136 V176 C128 196 140 204 156 202', 36))
el_ears = U(ell(68, 108, 36, 52), ell(188, 108, 36, 52))
el, ed = layered(el_head, el_ears)
icon('elephant', A, ['elephant', 'animal', 'safari', 'trunk'], line=el, detail=ed, area=[P(el_head), P(el_ears)],
     dotcut=[C(106, 100, 12), C(150, 100, 12)])

# ---------------------------------------------------------------- fish-slash
fish = load('fish')
icon('fish-slash', A, ['fish', 'off', 'disabled', 'hidden'], line=fish['line'] + [L(48, 48, 208, 208)],
     dot=[C(80, 128, 12)])

# ---------------------------------------------------------------- frog
frog_head = ell(128, 148, 96, 62)
frog = U(frog_head, circ((80, 86), 36), circ((176, 86), 36))
icon('frog', A, ['frog', 'toad', 'amphibian', 'pond'], line=[P(frog)],
     detail=[P('M84 164 C108 184 148 184 172 164')], area=[P(frog)],
     dotcut=[C(80, 86, 16), C(176, 86, 16)])

# ---------------------------------------------------------------- hippo
hip_head = U(ell(128, 100, 64, 52), circ((84, 58), 14), circ((172, 58), 14))
hip_muz = ell(128, 164, 88, 50)
hl, hd = layered(hip_muz, hip_head)
icon('hippo', A, ['hippopotamus', 'hippo', 'animal', 'safari'], line=hl, detail=hd, area=[P(hip_head), P(hip_muz)],
     dotcut=[C(100, 84, 12), C(156, 84, 12), C(98, 160, 14), C(158, 160, 14)])

# ---------------------------------------------------------------- horse
horse = ('M184 216 C188 160 180 112 160 72 L160 32 L140 56 C112 60 84 96 60 136 C48 156 52 176 72 180 '
         'C92 184 108 176 120 168 C128 184 128 200 120 216 Z')
icon('horse', A, ['horse', 'pony', 'equine', 'farm', 'equestrian'], line=[P(horse)], area=[P(horse)],
     dotcut=[C(124, 96, 12), C(72, 160, 10)])

# ---------------------------------------------------------------- jellyfish
jelly = 'M48 120 A80 80 0 0 1 208 120 V128 A12 12 0 0 1 196 140 H60 A12 12 0 0 1 48 128 Z'
icon('jellyfish', A, ['sea creature', 'ocean', 'jelly'],
     line=[P(jelly), P('M88 160 C80 176 96 196 88 216'), P('M128 160 C120 176 136 196 128 216'),
           P('M168 160 C160 176 176 196 168 216')], area=[P(jelly)])

# ---------------------------------------------------------------- koala
ko_head = circ((128, 140), 72)
ko_ears = U(circ((68, 84), 34), circ((188, 84), 34))
kl, kd = layered(ko_head, ko_ears)
nose = E(128, 160, 20, 28)
icon('koala', A, ['koala', 'australia', 'animal', 'marsupial'], line=kl, detail=kd + [nose],
     area=[P(ko_head), P(ko_ears)], hole=[nose], dotcut=[C(94, 132, 12), C(162, 132, 12)])

# ---------------------------------------------------------------- monkey
mk_head = U(circ((128, 132), 68), circ((56, 132), 22), circ((200, 132), 22))
mask = ('M128 108 C116 92 88 96 88 124 C88 140 96 148 96 160 C96 184 112 194 128 194 C144 194 160 184 160 160 '
        'C160 148 168 140 168 124 C168 96 140 92 128 108 Z')
icon('monkey', A, ['monkey', 'ape', 'primate', 'animal'], line=[P(mk_head)],
     detail=[P(mask)], area=[P(mk_head)],
     dotcut=[C(112, 126, 12), C(144, 126, 12)])

# ---------------------------------------------------------------- monkey-bars
icon('monkey-bars', 'Sports', ['monkey bars', 'playground', 'climbing', 'kids'],
     line=[L(40, 56, 216, 56), L(40, 92, 216, 92), L(92, 56, 92, 92), L(128, 56, 128, 92), L(164, 56, 164, 92),
           PL([(32, 216), (56, 92), (80, 216)]), PL([(176, 216), (200, 92), (224, 216)])])

# ---------------------------------------------------------------- owl
owl = 'M40 56 L88 80 H168 L216 56 V160 C216 196 176 216 128 216 C80 216 40 196 40 160 Z'
icon('owl', A, ['owl', 'bird', 'night', 'wisdom'], line=[P(owl)],
     detail=[C(92, 124, 26), C(164, 124, 26), P('M118 158 L128 174 L138 158')], area=[P(owl)],
     dotcut=[C(92, 124, 10), C(164, 124, 10)])

# ---------------------------------------------------------------- panda
icon('panda', A, ['panda', 'bear', 'china', 'wildlife'], line=[C(128, 140, 76)], area=[C(128, 140, 76)],
     dot=[C(68, 76, 32), C(188, 76, 32)], dotcut=[C(96, 134, 30), C(160, 134, 30), C(128, 176, 14)])

# ---------------------------------------------------------------- pig
pig = U(circ((128, 136), 80), 'M64 96 L52 40 L112 68 Z', 'M192 96 L204 40 L144 68 Z')
snout = E(128, 160, 36, 26)
icon('pig', A, ['pig', 'swine', 'farm', 'piggy', 'animal'], line=[P(pig)], detail=[snout], area=[P(pig)],
     dotcut=[C(96, 116, 12), C(160, 116, 12), C(114, 160, 10), C(142, 160, 10)])
icon('pig-slash', A, ['pig', 'off', 'disabled', 'hidden'], line=[P(pig), snout, L(48, 48, 208, 208)],
     dot=[C(96, 116, 12), C(160, 116, 12), C(114, 160, 10), C(142, 160, 10)])

# ---------------------------------------------------------------- paw-print-slash
paw = load('paw-print')
icon('paw-print-slash', A, ['paw print', 'off', 'disabled', 'hidden', 'paw'], line=paw['line'] + [L(48, 48, 208, 208)])

# ---------------------------------------------------------------- rabbit
rab = U(ell(144, 172, 68, 44), circ((84, 124), 36), ell(116, 74, 44, 16, -62), circ((206, 160), 14))
icon('rabbit', A, ['rabbit', 'bunny', 'cruelty free', 'hare', 'easter'], line=[P(rab)],
     detail=clip_in(P('M148 216 C148 184 172 168 200 176'), rab), area=[P(rab)], dotcut=[C(80, 118, 12)])

# ---------------------------------------------------------------- rat
rat_body = 'M48 152 C48 116 80 96 116 96 C152 96 176 120 212 148 C220 154 216 164 206 164 H64 C54 164 48 160 48 152 Z'
rat_ear = circ((136, 92), 22)
rl, rd = layered(rat_ear, rat_body)
icon('rat', A, ['rodent', 'mouse', 'pest', 'rat', 'animal'], line=rl + [P('M48 156 C20 168 32 204 72 200 H128')],
     detail=rd, area=[P(rat_body), P(rat_ear)], dotcut=[C(176, 128, 12)])

# ---------------------------------------------------------------- sheep
wool = U(*[circ(polar((128, 116), 56, a), 26) for a in range(150, 391, 30)], circ((128, 116), 56))
face = ell(128, 150, 40, 58)
sl, sd = layered(face, wool)
s_ears = [ell(58, 136, 26, 13, 20), ell(198, 136, 26, 13, -20)]
icon('sheep', A, ['sheep', 'lamb', 'wool', 'farm'], line=sl + sum([runs(e, [wool, face]) for e in s_ears], []),
     detail=sd, area=[P(wool), P(face)] + [P(e) for e in s_ears], dotcut=[C(112, 144, 12), C(144, 144, 12)])

# ---------------------------------------------------------------- snail
shell = circ((148, 124), 60)
s_body = 'M48 128 A20 20 0 0 1 88 128 V176 H196 C212 176 224 192 224 208 H64 C52 208 48 200 48 192 Z'
spiral = []
for i in range(0, 361, 6):
    rr = 10 + 30 * i / 360
    spiral.append(polar((148, 124), rr, 180 + i))
nl, nd = layered(shell, s_body)
icon('snail', A, ['snail', 'slow', 'shell', 'mollusc'], line=nl + [L(60, 110, 48, 76), L(78, 110, 86, 76)],
     detail=nd + [PL(spiral)], area=[P(shell), P(s_body)], dot=[C(48, 72, 14), C(88, 72, 14)])

# ---------------------------------------------------------------- snake
snake = U(tube('M204 196 H96 A34 34 0 0 1 96 128 H152 A30 30 0 0 0 152 68', 36), ell(140, 64, 34, 24))
icon('snake', A, ['snake', 'serpent', 'reptile', 'zodiac'], line=[P(snake), PL([(106, 64), (84, 64), (72, 56)]), L(84, 64, 72, 72)],
     area=[P(snake)], dotcut=[C(142, 58, 10)])

# ---------------------------------------------------------------- spider
sp_body = U(ell(128, 150, 34, 42), circ((128, 96), 22))
legs = []
for side in (1, -1):
    for knee, tip in (((60, 64), (44, 96)), ((44, 112), (32, 140)), ((52, 168), (40, 200)), ((76, 200), (72, 224))):
        k = knee if side == 1 else mx(knee)
        t = tip if side == 1 else mx(tip)
        legs += runs(PL([(128, 128), k, t]), sp_body)
icon('spider', A, ['spider', 'bug', 'web', 'halloween'], line=[P(sp_body)] + legs, area=[P(sp_body)])

# ---------------------------------------------------------------- tiger
tiger = U(circ((128, 136), 80), circ((66, 70), 24), circ((190, 70), 24))
icon('tiger', A, ['tiger', 'big cat', 'wild', 'zodiac'], line=[P(tiger)],
     detail=[L(128, 56, 128, 84), L(104, 60, 108, 80), L(152, 60, 148, 80), L(48, 128, 72, 136), L(52, 160, 76, 160),
             L(208, 128, 184, 136), L(204, 160, 180, 160), P('M114 156 H142 L128 172 Z')], area=[P(tiger)],
     dotcut=[C(100, 120, 12), C(156, 120, 12)])

# ---------------------------------------------------------------- turkey
piv = (124, 144)
sector = poly([piv] + [polar(piv, 64, a) for a in range(165, 286, 5)], True)
fan = U(sector, *[circ(polar(piv, 62, a), 28) for a in (180, 222, 264)])
t_body = U(circ((136, 156), 50), circ((176, 100), 22), 'M192 90 L216 100 L194 112 Z')
tl, td = layered(t_body, fan)
rays = []
for a in (201, 243):
    rays += runs(L(*piv, *polar(piv, 66, a)), t_body)
icon('turkey', A, ['turkey', 'thanksgiving', 'bird', 'farm'], line=tl + [L(122, 204, 118, 224), L(150, 204, 154, 224)],
     detail=td + rays, area=[P(fan), P(t_body)], dotcut=[C(180, 96, 10)])

# ---------------------------------------------------------------- whale
whale = ('M32 144 C32 108 64 92 104 92 C148 92 168 120 184 144 L196 112 C200 100 212 96 224 104 L208 128 L216 160 '
         'C200 164 192 160 188 156 C176 184 148 200 104 200 C60 200 32 180 32 144 Z')
icon('whale', A, ['whale', 'ocean', 'sea', 'mammal'],
     line=[P(whale), L(88, 72, 88, 44), P('M88 56 C84 44 72 40 64 44'), P('M88 56 C92 44 104 40 112 44')],
     detail=[P('M48 160 C80 176 112 176 136 160')], area=[P(whale)], dotcut=[C(72, 132, 12)])

# ---------------------------------------------------------------- wolf
wolf = 'M60 36 L104 76 H152 L196 36 L200 112 L220 152 L172 168 L140 208 Q128 220 116 208 L84 168 L36 152 L56 112 Z'
icon('wolf', A, ['wild animal', 'wolf', 'canine'], line=[P(wolf)], detail=[P('M108 150 L128 172 L148 150')],
     area=[P(wolf)], dotcut=[C(100, 124, 12), C(156, 124, 12), C(128, 186, 12)])

print(save(overwrite=True))
