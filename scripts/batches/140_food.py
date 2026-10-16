import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

SLASH = L(48, 48, 208, 208)
B = {}  # base geometry for slash variants


def reg(name, cat, tags, **roles):
    B[name] = roles
    icon(name, cat, tags, **roles)


def slash(name, cat, tags, base, drop_detail=False, extra_drop=()):
    """Slash variant: base strokes (details as plain lines), no area, dots solid, plus the slash."""
    line = [e for e in base.get('line', []) if e not in extra_drop]
    if not drop_detail:
        line += [e for e in base.get('detail', []) if e not in extra_drop]
    dots = list(base.get('dot', [])) + list(base.get('dotcut', []))
    icon(name, cat, tags, line=line + [SLASH], dot=dots)


def hull2(c1, r1, c2, r2):
    """Outline of the convex hull of two circles (tangent lines plus outer arcs)."""
    d = dist(c1, c2)
    u = ((c2[0] - c1[0]) / d, (c2[1] - c1[1]) / d)
    n = (-u[1], u[0])
    k = (r1 - r2) / d
    s = math.sqrt(1 - k * k)
    v1 = (k * u[0] + s * n[0], k * u[1] + s * n[1])
    v2 = (k * u[0] - s * n[0], k * u[1] - s * n[1])
    a1 = (c1[0] + r1 * v1[0], c1[1] + r1 * v1[1]); b1 = (c2[0] + r2 * v1[0], c2[1] + r2 * v1[1])
    a2 = (c1[0] + r1 * v2[0], c1[1] + r1 * v2[1]); b2 = (c2[0] + r2 * v2[0], c2[1] + r2 * v2[1])
    return (f'M{pt(a1)} L{pt(b1)} ' + arc_to(c2, r2, b1, b2, lambda m: dist(m, c1)) +
            f' L{pt(a2)} ' + arc_to(c1, r1, a2, a1, lambda m: dist(m, c2)) + ' Z')


def tpath(segs, fn):
    """Build a path from segments with points mapped through fn (rotation/translation keep arcs circular)."""
    out = []
    for s in segs:
        op = s[0]
        if op in 'ML':
            out.append(f'{op}{pt(fn(s[1]))}')
        elif op == 'C':
            out.append('C' + ' '.join(pt(fn(p)) for p in s[1:]))
        elif op == 'A':
            r, large, sweep, p = s[1:]
            out.append(f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(fn(p))}')
        elif op == 'Z':
            out.append('Z')
    return ' '.join(out)


def xf(deg, pivot, move, scale=1.0):
    a = math.radians(deg)
    def fn(p):
        dx, dy = (p[0] - pivot[0]) * scale, (p[1] - pivot[1]) * scale
        return (pivot[0] + dx * math.cos(a) - dy * math.sin(a) + move[0],
                pivot[1] + dx * math.sin(a) + dy * math.cos(a) + move[1])
    return fn


# ---------------------------------------------------------------- apple-half
apple = load('apple')
apple_body = apple['area'][0]
apple_stem = apple['line'][1]
core = 'M128 112 C102 130 98 166 128 188 C158 166 154 130 128 112 Z'
icon('apple-half', 'Food', ['apple slice', 'fruit', 'cut apple'],
     line=[apple_body, apple_stem], detail=[P(core)], area=[apple_body])

# ---------------------------------------------------------------- avocado
tilt = lambda p: rot([p], 24)[0]
top_c, bot_c = tilt((128, 74)), tilt((128, 154))
av = hull2(top_c, 38, bot_c, 70)
pit_c = tilt((128, 160))
icon('avocado', 'Food', ['fruit', 'guacamole', 'healthy', 'pit', 'avocado'],
     line=[P(av)], detail=[C(*pit_c, 30)], area=[P(av)])

# ---------------------------------------------------------------- baby-food
jar = 'M56 112 V200 A24 24 0 0 0 80 224 H136 A24 24 0 0 0 160 200 V112'
jar_area = jar + ' Z'
icon('baby-food', 'Food', ['baby food', 'meal', 'jar', 'feeding'],
     line=[R(44, 80, 128, 32, 10), P(jar), E(204, 72, 20, 30), L(204, 102, 204, 216)],
     detail=[L(88, 164, 128, 164)],
     area=[R(44, 80, 128, 32, 10), P(jar_area), E(204, 72, 20, 30)])

# ---------------------------------------------------------------- baguette
u = (1 / math.sqrt(2), -1 / math.sqrt(2))
bag_d = capsule((128, 128), 76, 40, u)
cuts = []
for t in (-50, 0, 50):
    cx, cy = 128 + u[0] * t, 128 + u[1] * t
    a = math.atan2(u[1], u[0]) + math.radians(32)
    dx, dy = math.cos(a) * 22, math.sin(a) * 22
    cuts.append(L(cx - dx, cy - dy, cx + dx, cy + dy))
icon('baguette', 'Food', ['bread', 'bakery', 'french'], line=[P(bag_d)], detail=cuts, area=[P(bag_d)])

# ---------------------------------------------------------------- baking-tray
tray = 'M32 152 H224 L204 202 A12 12 0 0 1 193 210 H63 A12 12 0 0 1 52 202 Z'
bun1 = 'M44 152 A32 32 0 0 1 108 152'
bun2 = 'M148 152 A32 32 0 0 1 212 152'
icon('baking-tray', 'Food', ['baking tray', 'oven', 'sheet pan', 'bake'],
     line=[P(tray), P(bun1), P(bun2)], area=[P(tray), P(bun1 + ' Z'), P(bun2 + ' Z')])

# ---------------------------------------------------------------- banana
ban = 'M168 64 L204 64 C216 156 152 216 60 212 C44 211 42 196 54 192 C124 176 168 132 168 64 Z'
icon('banana', 'Food', ['banana', 'fruit', 'food', 'potassium'],
     line=[P(ban), L(188, 64, 192, 36)], area=[P(ban)])

# ---------------------------------------------------------------- beans
pa, pb = (52, 204), (204, 52)
chord = dist(pa, pb); sag = 50
pr = (chord ** 2 / 4 + sag ** 2) / (2 * sag)
pod = f'M{pt(pa)} A{f(pr)} {f(pr)} 0 0 1 {pt(pb)} A{f(pr)} {f(pr)} 0 0 1 {pt(pa)} Z'
icon('beans', 'Food', ['beans', 'fava', 'legume', 'pod'],
     line=[P(pod), L(204, 52, 220, 36)], area=[P(pod)],
     dotcut=[C(88, 168, 16), C(128, 128, 16), C(168, 88, 16)])

# ---------------------------------------------------------------- beer
foam = 'M48 104 A28 28 0 0 1 88 68 A32 32 0 0 1 144 64 A28 28 0 0 1 168 104 Z'
mug = 'M56 104 V196 A20 20 0 0 0 76 216 H140 A20 20 0 0 0 160 196 V104'
handle = 'M160 128 H184 A20 20 0 0 1 204 148 V168 A20 20 0 0 1 184 188 H160'
reg('beer', 'Food', ['beer mug', 'pint', 'drink', 'pub', 'sports bar'],
    line=[P(foam), P(mug), P(handle)], detail=[L(92, 140, 92, 184), L(124, 140, 124, 184)],
    area=[P(foam), P(mug + ' Z')])
slash('beer-slash', 'Food', ['beer', 'disabled', 'off', 'food'], B['beer'], drop_detail=True)

# ---------------------------------------------------------------- beer-bottle
bb = ('M108 32 H148 V80 C148 100 176 108 176 136 V208 A16 16 0 0 1 160 224 H96 A16 16 0 0 1 80 208 '
      'V136 C80 108 108 100 108 80 Z')
icon('beer-bottle', 'Food', ['beer', 'bottle', 'drink'],
     line=[P(bb)], detail=[R(108, 148, 40, 44, 8)], area=[P(bb)])

# ---------------------------------------------------------------- bottle
bt = ('M108 72 V84 C108 100 76 108 76 136 V204 A20 20 0 0 0 96 224 H160 A20 20 0 0 0 180 204 '
      'V136 C180 108 148 100 148 84 V72')
bcap = R(100, 32, 56, 40, 10)
reg('bottle', 'Food', ['bottle', 'drink', 'water', 'beverage', 'container'],
    line=[bcap, P(bt)], area=[bcap, P(bt + ' Z')])
slash('bottle-slash', 'Food', ['bottle', 'disabled', 'off', 'food'], B['bottle'])

# ---------------------------------------------------------------- bottle-liquor
bl = ('M112 40 V88 C112 104 72 108 72 132 V208 A16 16 0 0 0 88 224 H168 A16 16 0 0 0 184 208 '
      'V132 C184 108 144 104 144 88 V40')
icon('bottle-liquor', 'Food', ['liquor', 'spirits', 'alcohol', 'bottle'],
     line=[P(bl), L(108, 32, 148, 32)], detail=[R(104, 148, 48, 44, 6)], area=[P(bl + ' Z')])

# ---------------------------------------------------------------- bowls
def bowl(dy):
    y0 = 104 + dy
    d = f'M32 {f(y0)} A96 84 0 0 0 224 {f(y0)} Z'
    foot = PL([(104, y0 + 81), (100, y0 + 108), (156, y0 + 108), (152, y0 + 81)])
    return d, foot

bd, bf = bowl(-24)
icon('bowl', 'Food', ['bowl', 'dish', 'soup', 'kitchen'], line=[P(bd), bf], area=[P(bd)])
bd, bf = bowl(-4)
icon('bowl-spoon', 'Food', ['bowl spoon', 'bowl', 'spoon', 'food'],
     line=[P(bd), bf, L(140, 100, 192, 40)], area=[P(bd)])
bd, bf = bowl(4)
steam = [P(f'M{x} 80 C{x - 8} 68 {x + 8} 56 {x} 40') for x in (84, 128, 172)]
icon('bowl-steam', 'Food', ['soup', 'hot bowl', 'ramen'], line=[P(bd), bf] + steam, area=[P(bd)])

# ---------------------------------------------------------------- brandy
bc, brr = (128, 114), 70
hw = math.sqrt(brr ** 2 - (bc[1] - 64) ** 2)
snif = f'M{f(128 - hw)} 64 H{f(128 + hw)} A{brr} {brr} 0 1 1 {f(128 - hw)} 64 Z'
lw = math.sqrt(brr ** 2 - 26 ** 2)
icon('brandy', 'Food', ['snifter', 'cognac', 'drink'],
     line=[P(snif), L(128, 184, 128, 216), L(92, 216, 164, 216)],
     detail=[L(128 - lw, 140, 128 + lw, 140)], area=[P(snif)])

# ---------------------------------------------------------------- bread
br = ('M68 216 V132 C44 124 32 104 40 84 C48 56 84 40 128 40 C172 40 208 56 216 84 C224 104 212 124 188 132 '
      'V216 Z')
reg('bread', 'Food', ['toast', 'bakery', 'slice', 'bread', 'loaf'], line=[P(br)], area=[P(br)])
slash('bread-slash', 'Food', ['bread', 'disabled', 'off', 'food'], B['bread'])

# ---------------------------------------------------------------- bread-maker
icon('bread-maker', 'Home', ['bread maker', 'appliance', 'baking', 'kitchen'],
     line=[R(40, 48, 176, 168, 28)], detail=[R(76, 84, 104, 64, 10), L(140, 184, 168, 184)],
     area=[R(40, 48, 176, 168, 28)], dotcut=[C(96, 184, 16)])

# ---------------------------------------------------------------- bubble-tea
cupb = 'M56 104 H200 L186 204 A14 14 0 0 1 172 216 H84 A14 14 0 0 1 70 204 Z'
dome = 'M76 104 A52 52 0 0 1 180 104'
icon('bubble-tea', 'Food', ['bubble tea', 'boba', 'milk tea', 'drink', 'tapioca'],
     line=[P(cupb), P(dome), L(144, 56, 162, 34)], area=[P(cupb), P(dome + ' Z')],
     dotcut=[C(104, 180, 16), C(152, 180, 16), C(128, 144, 16)])

# ---------------------------------------------------------------- cake-slash
cake = load('cake')
slash('cake-slash', 'Food', ['cake', 'disabled', 'off', 'food'], cake, drop_detail=True)

# ---------------------------------------------------------------- can
can_side = 'M64 56 V200 A64 20 0 0 0 192 200 V56'
icon('can', 'Food', ['can', 'tin', 'canned', 'food'],
     line=[E(128, 56, 64, 20), P(can_side)],
     detail=[P('M64 104 A64 20 0 0 0 192 104'), P('M64 160 A64 20 0 0 0 192 160')],
     area=[P('M64 56 A64 20 0 0 1 192 56 V200 A64 20 0 0 1 64 200 Z')])

# ---------------------------------------------------------------- candy
cc = (128, 128)
wl = PG(rot([(90, 128), (40, 92), (40, 164)], -30))
wr = PG(rot([(166, 128), (216, 92), (216, 164)], -30))
reg('candy', 'Food', ['candy', 'sweet', 'wrapper', 'treat'],
    line=[C(128, 128, 40), wl, wr], area=[C(128, 128, 40), wl, wr])
slash('candy-slash', 'Food', ['candy', 'disabled', 'off', 'food'], B['candy'])

# ---------------------------------------------------------------- carrot
car_c, car_t = (156, 100), (52, 204)
carrot = hull2(car_c, 40, car_t, 4)
ax_u = (-(1 / math.sqrt(2)), 1 / math.sqrt(2))  # toward tip
nrm = (1 / math.sqrt(2), 1 / math.sqrt(2))       # lower-right side
cdet = []
for t, w in ((44, 32), (92, 20)):
    p = (car_c[0] + ax_u[0] * t, car_c[1] + ax_u[1] * t)
    half = 40 - (40 - 4) * t / dist(car_c, car_t)
    a = (p[0] + nrm[0] * half, p[1] + nrm[1] * half)
    b = (a[0] - nrm[0] * w, a[1] - nrm[1] * w)
    cdet.append(L(*a, *b))
top = (car_c[0] + 40 / math.sqrt(2) - 6, car_c[1] - 40 / math.sqrt(2) + 6)
leaves = [L(*top, 224, 76), L(*top, 180, 32), L(*top, 216, 40)]
reg('carrot', 'Food', ['vegetables', 'carrot', 'produce', 'healthy', 'vegetable'],
    line=[P(carrot)] + leaves, detail=cdet, area=[P(carrot)])
slash('carrot-slash', 'Food', ['carrot', 'disabled', 'off', 'food'], B['carrot'], drop_detail=True)

# ---------------------------------------------------------------- champagne
ch_fn = xf(30, (128, 128), (-10, 6), 0.88)
ch_body = [('M', (110, 40)), ('L', (146, 40)), ('L', (146, 84)), ('C', (146, 108), (180, 116), (180, 144)),
           ('L', (180, 208)), ('A', 16, 0, 1, (164, 224)), ('L', (92, 224)), ('A', 16, 0, 1, (76, 208)),
           ('L', (76, 144)), ('C', (76, 116), (110, 108), (110, 84)), ('Z',)]
chb = tpath(ch_body, ch_fn)
foil = tpath([('M', (110, 76)), ('L', (146, 76))], ch_fn)
labs = [tpath([('M', (76, y)), ('L', (180, y))], ch_fn) for y in (152, 192)]
spray = []
for ang, r0, r1 in ((-90, 26, 44), (-140, 26, 42), (-40, 26, 42)):
    a0 = polar((128, 40), r0, ang); a1 = polar((128, 40), r1, ang)
    spray.append(P(tpath([('M', a0), ('L', a1)], ch_fn)))
icon('champagne', 'Food', ['celebration', 'sparkling wine', 'party', 'champagne', 'toast'],
     line=[P(chb)] + spray, detail=[P(foil)] + [P(d) for d in labs], area=[P(chb)])

# ---------------------------------------------------------------- cheers
fl_bowl = [('M', (-30, 0)), ('L', (30, 0)), ('C', (30, 56), (18, 80), (0, 80)), ('C', (-18, 80), (-30, 56), (-30, 0)), ('Z',)]
def flute(sign, base_x):
    fn = xf(14 * sign, (0, 128), (base_x, 216 - 128))
    g = lambda p: fn((p[0] * sign, p[1]))
    return ([P(tpath(fl_bowl, g)), P(tpath([('M', (0, 80)), ('L', (0, 128))], g)),
             P(tpath([('M', (-24, 128)), ('L', (24, 128))], g))], P(tpath(fl_bowl, g)), g)
l1, a1, g1 = flute(1, 64)
l2, a2, g2 = flute(-1, 192)
tip = g1((30, 0))
sp = [L(tip[0], tip[1] - 28, tip[0], tip[1] - 52),
      L(*polar(tip, 30, -135), *polar(tip, 50, -135)), L(*polar(tip, 30, -45), *polar(tip, 50, -45))]
icon('cheers', 'Food', ['toast', 'clinking glasses', 'celebrate'], line=l1 + l2 + sp, area=[a1, a2])

# ---------------------------------------------------------------- bento-box
icon('bento-box', 'Food', ['bento', 'lunch box', 'japanese', 'meal'],
     line=[R(32, 56, 192, 144, 16)], detail=[L(112, 56, 112, 200), L(112, 128, 224, 128)],
     area=[R(32, 56, 192, 144, 16)], dotcut=[C(72, 128, 16)])

# ---------------------------------------------------------------- cheese
chz = 'M32 120 L148 56 L224 120 V192 A8 8 0 0 1 216 200 H40 A8 8 0 0 1 32 192 Z'
icon('cheese', 'Food', ['cheese', 'dairy', 'wedge', 'food'],
     line=[P(chz)], detail=[L(32, 120, 224, 120)], area=[P(chz)],
     dotcut=[C(80, 162, 16), C(144, 168, 14), C(192, 152, 10)])

# ---------------------------------------------------------------- chef-hat
lc, lr_, mc, mr, rc, rr_ = (86, 116), 46, (128, 84), 52, (170, 116), 46
p_lm = circle_x(lc, lr_, mc, mr)[0]
p_mr = circle_x(mc, mr, rc, rr_)[0]
yb = lc[1] + math.sqrt(lr_ ** 2 - (80 - lc[0]) ** 2)
hat = (f'M80 216 V{f(yb)} ' + arc_to(lc, lr_, (80, yb), p_lm, lambda m: -m[0] - m[1]) + ' ' +
       arc_to(mc, mr, p_lm, p_mr, lambda m: -m[1]) + ' ' +
       arc_to(rc, rr_, p_mr, (176, yb), lambda m: m[0] - m[1]) + ' V216 Z')
reg('chef-hat', 'Food', ['chef', 'cook', 'toque', 'kitchen', 'cooking'],
    line=[P(hat)], detail=[L(80, 172, 176, 172), L(112, 124, 112, 172), L(144, 124, 144, 172)], area=[P(hat)])
slash('chef-hat-slash', 'Food', ['chef hat', 'disabled', 'off', 'food'], B['chef-hat'],
      extra_drop=(L(112, 124, 112, 172), L(144, 124, 144, 172)))

# ---------------------------------------------------------------- cherries
leaf = 'M152 52 C164 32 196 28 216 40 C204 60 176 64 152 52 Z'
icon('cherries', 'Food', ['cherry', 'fruit', 'sweet', 'food'],
     line=[C(76, 180, 38), C(178, 172, 38), P('M76 142 C84 104 120 68 152 52'), P('M178 134 C168 104 158 76 152 52'), P(leaf)],
     area=[C(76, 180, 38), C(178, 172, 38), P(leaf)])

# ---------------------------------------------------------------- chips-bag
chips = 'M60 36 H196 C180 96 180 160 196 220 H60 C76 160 76 96 60 36 Z'
icon('chips-bag', 'Food', ['snacks', 'chips', 'crisps', 'bag'],
     line=[P(chips)], detail=[L(68, 68, 188, 68), L(68, 188, 188, 188), C(128, 128, 22)], area=[P(chips)])

# ---------------------------------------------------------------- chocolate
icon('chocolate', 'Food', ['chocolate', 'bar', 'sweet', 'candy'],
     line=[R(56, 32, 144, 192, 14)], detail=[L(128, 32, 128, 224), L(56, 96, 200, 96), L(56, 160, 200, 160)],
     area=[R(56, 32, 144, 192, 14)])

# ---------------------------------------------------------------- chopsticks
icon('chopsticks', 'Food', ['chopsticks', 'asian', 'eating', 'utensils'],
     line=[L(176, 32, 52, 196), L(220, 68, 84, 220)])

# ---------------------------------------------------------------- cloche
dome_c = 'M36 180 A92 92 0 0 1 220 180 Z'
hl = P(f'M{pt(polar((128, 180), 62, 200))} A62 62 0 0 1 {pt(polar((128, 180), 62, 240))}')
icon('cloche', 'Food', ['serving dish', 'cloche', 'catering', 'restaurant'],
     line=[P(dome_c), L(32, 180, 224, 180)], detail=[hl], area=[P(dome_c)], dot=[C(128, 80, 18)])

# ---------------------------------------------------------------- coffee-bean
bc_ = (128, 128); ang = -50
ua = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
na = (-ua[1], ua[0])
e1 = (bc_[0] + ua[0] * 92, bc_[1] + ua[1] * 92); e2 = (bc_[0] - ua[0] * 92, bc_[1] - ua[1] * 92)
bean = f'M{pt(e1)} A92 66 {ang} 0 1 {pt(e2)} A92 66 {ang} 0 1 {pt(e1)} Z'
k1 = (bc_[0] + ua[0] * 40 + na[0] * 30, bc_[1] + ua[1] * 40 + na[1] * 30)
k2 = (bc_[0] - ua[0] * 40 - na[0] * 30, bc_[1] - ua[1] * 40 - na[1] * 30)
crease = f'M{pt(e1)} C{pt(k1)} {pt(k2)} {pt(e2)}'
icon('coffee-bean', 'Food', ['coffee bean', 'roast', 'cafe'], line=[P(bean)], detail=[P(crease)], area=[P(bean)])

# ---------------------------------------------------------------- coffee / cookie slashes
slash('coffee-slash', 'Food', ['coffee', 'disabled', 'off', 'food'], load('coffee'))
slash('cookie-slash', 'Food', ['cookie', 'disabled', 'off', 'food'], load('cookie'))

# ---------------------------------------------------------------- cooking-pot
lid = 'M40 128 A88 34 0 0 1 216 128 Z'
pot = 'M56 128 V192 A24 24 0 0 0 80 216 H176 A24 24 0 0 0 200 192 V128'
psteam = [P(f'M{x} 68 C{x - 10} 58 {x + 10} 48 {x} 36') for x in (80, 176)]
icon('cooking-pot', 'Food', ['stockpot', 'soup', 'pot', 'cooking', 'cook'],
     line=[P(lid), P(pot), L(32, 160, 56, 160), L(200, 160, 224, 160)] + psteam,
     area=[P(lid), P(pot + ' Z')], dot=[C(128, 94, 16)])

# ---------------------------------------------------------------- crockery
cbowl = 'M52 64 A76 64 0 0 0 204 64 Z'
icon('crockery', 'Food', ['plates', 'dishes', 'tableware', 'kitchen'],
     line=[P(cbowl), L(48, 164, 208, 164), L(32, 200, 224, 200)], area=[P(cbowl)])

# ---------------------------------------------------------------- croissant
oc, orr, ic_, irr = (128, 150), 92, (128, 206), 84
tl, tr = sorted(circle_x(oc, orr, ic_, irr), key=lambda p: p[0])
cro = (f'M{pt(tl)} ' + arc_to(oc, orr, tl, tr, lambda m: -m[1]) + ' ' + arc_to(ic_, irr, tr, tl, lambda m: -m[1]) + ' Z')
def ray_hit(c, r, o, ang):
    """Point where the ray from o at angle ang meets circle (c, r) (outside-going hit)."""
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    fx, fy = o[0] - c[0], o[1] - c[1]
    bq = fx * dx + fy * dy
    t = -bq + math.sqrt(bq * bq - (fx * fx + fy * fy - r * r))
    return (o[0] + dx * t, o[1] + dy * t)
segs = []
for ang in (-90 - 26, -90 + 26):
    ro = (128, 214)
    segs.append(L(*ray_hit(ic_, irr, ro, ang), *ray_hit(oc, orr, ro, ang)))
icon('croissant', 'Food', ['croissant', 'bakery', 'pastry', 'breakfast'],
     line=[P(cro)], detail=segs, area=[P(cro)])

# ---------------------------------------------------------------- cup
cupd = 'M44 64 H172 V176 A24 24 0 0 1 148 200 H68 A24 24 0 0 1 44 176 Z'
cuph = 'M172 88 H188 A24 24 0 0 1 212 112 V128 A24 24 0 0 1 188 152 H172'
reg('cup', 'Food', ['cup', 'mug', 'drink', 'tea'], line=[P(cupd), P(cuph)], area=[P(cupd)])
slash('cup-slash', 'Food', ['cup', 'disabled', 'off', 'food'], B['cup'])

# ---------------------------------------------------------------- cup-straw
tc = 'M68 104 H188 L174 204 A14 14 0 0 1 160 216 H96 A14 14 0 0 1 82 204 Z'
tlid = 'M56 104 L62 76 A8 8 0 0 1 70 68 H186 A8 8 0 0 1 194 76 L200 104 Z'
icon('cup-straw', 'Food', ['drink', 'soda', 'cup', 'straw'],
     line=[P(tc), P(tlid), PL([(136, 68), (146, 36), (176, 36)])], area=[P(tc), P(tlid)])

# ---------------------------------------------------------------- cutting-board
board = ('M48 112 A24 24 0 0 1 72 88 H100 V64 A28 28 0 0 1 156 64 V88 H184 A24 24 0 0 1 208 112 '
         'V200 A24 24 0 0 1 184 224 H72 A24 24 0 0 1 48 200 Z')
icon('cutting-board', 'Food', ['cutting board', 'chopping', 'kitchen', 'prep'],
     line=[P(board)], detail=[L(88, 136, 168, 136), L(88, 176, 136, 176)], area=[P(board)], dotcut=[C(128, 62, 14)])

# ---------------------------------------------------------------- dango
du = (1 / math.sqrt(2), -1 / math.sqrt(2))
dc0 = (136, 120); ds, drr = 64, 38
dcs = [(dc0[0] + du[0] * ds * k, dc0[1] + du[1] * ds * k) for k in (-1, 0, 1)]
lo, mid, hi = dcs
x_lm = circle_x(lo, drr, mid, drr); x_mh = circle_x(mid, drr, hi, drr)
far = lambda c: (lambda m: dist(m, c))
dline = [
    P(f'M{pt(x_lm[0])} ' + arc_to(lo, drr, x_lm[0], x_lm[1], far(mid))),
    P(f'M{pt(x_mh[0])} ' + arc_to(hi, drr, x_mh[0], x_mh[1], far(mid))),
    P(f'M{pt(x_lm[0])} ' + arc_to(mid, drr, x_lm[0], x_mh[0], lambda m: -m[0] - m[1])),
    P(f'M{pt(x_lm[1])} ' + arc_to(mid, drr, x_lm[1], x_mh[1], lambda m: m[0] + m[1])),
]
ddet = [P(f'M{pt(x_lm[0])} ' + arc_to(mid, drr, x_lm[0], x_lm[1], lambda m: -dist(m, lo))),
        P(f'M{pt(x_mh[0])} ' + arc_to(hi, drr, x_mh[0], x_mh[1], lambda m: -dist(m, hi) * 0 - dist(m, lo)))]
stick_end = (lo[0] - du[0] * drr, lo[1] - du[1] * drr)
icon('dango', 'Food', ['dango', 'skewer', 'japanese sweet', 'mochi'],
     line=dline + [L(36, 220, *stick_end)], detail=ddet, area=[C(*c, drr) for c in dcs])

# ---------------------------------------------------------------- donut
spr = []
for i, (ang, rr0, rot_) in enumerate(((-60, 64, 30), (0, 66, -40), (60, 62, 50), (120, 66, -20), (180, 64, 60), (240, 62, -50))):
    cpt = polar((128, 128), rr0, ang)
    a = math.radians(ang + 90 + rot_)
    dx, dy = math.cos(a) * 9, math.sin(a) * 9
    spr.append(L(cpt[0] - dx, cpt[1] - dy, cpt[0] + dx, cpt[1] + dy))
icon('donut', 'Food', ['donut', 'doughnut', 'pastry', 'sweet'],
     line=[C(128, 128, 96), C(128, 128, 30)], detail=spr, area=[C(128, 128, 96)], hole=[C(128, 128, 22)])

# ---------------------------------------------------------------- drumstick
meat = hull2((152, 100), 68, (100, 156), 20)
ke = (62, 194)
kn = (1 / math.sqrt(2), 1 / math.sqrt(2))
k1c = (ke[0] + kn[0] * 16, ke[1] + kn[1] * 16); k2c = (ke[0] - kn[0] * 16, ke[1] - kn[1] * 16)
kx = circle_x(k1c, 18, k2c, 18)
knob = (f'M{pt(kx[0])} ' + arc_to(k1c, 18, kx[0], kx[1], far(k2c)) + ' ' + arc_to(k2c, 18, kx[1], kx[0], far(k1c)) + ' Z')
reg('drumstick', 'Food', ['drumstick', 'chicken leg', 'meat', 'food', 'steak'],
    line=[P(meat), L(86, 170, 70, 186), P(knob)], area=[P(meat), P(knob)])
slash('drumstick-slash', 'Food', ['drumstick', 'off', 'disabled', 'hidden'], B['drumstick'])

print(save(overwrite=True))
