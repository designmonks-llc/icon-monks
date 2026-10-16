import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

OBJ = 'Objects'
SLASH = L(48, 48, 208, 208)


def slashed(base, drop=()):
    """Slash variant from an existing icon: outline roles only, area dropped."""
    s = load(base) if isinstance(base, str) else base
    lines = [e for e in s['line'] + s['detail'] if e not in drop]
    return dict(line=lines + [SLASH], dot=[d for d in s['dot'] if d not in drop])


def path(cmds, tf=lambda p: p):
    """Build a path from commands with local points, mapped through tf (rotation/translation keep circular arcs valid)."""
    out = []
    for c in cmds:
        k = c[0]
        if k in 'ML':
            out.append(k + pt(tf(c[1])))
        elif k == 'C':
            out.append('C' + ' '.join(pt(tf(p)) for p in c[1:]))
        elif k == 'A':
            out.append(f'A{f(c[1])} {f(c[1])} 0 {c[2]} {c[3]} {pt(tf(c[4]))}')
        elif k == 'Z':
            out.append('Z')
    return P(' '.join(out))


def rt(deg, c=(128, 128), d=(0, 0)):
    return lambda p: (lambda q: (q[0] + d[0], q[1] + d[1]))(rot([p], deg, c)[0])


def mirror_x(el):
    """Mirror a <path> element horizontally (x -> 256 - x); supports M/L/A/Z with absolute coordinates."""
    d = re.search(r'd="([^"]+)"', el).group(1)
    toks = re.findall(r'[MLAZ]|-?[\d.]+', d)
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t in 'ML':
            out.append(f'{t}{f(256 - float(toks[i + 1]))} {toks[i + 2]}'); i += 3
        elif t == 'A':
            rx, ry, xr, la, sw, x, y = toks[i + 1:i + 8]
            out.append(f'A{rx} {ry} {xr} {la} {1 - int(sw)} {f(256 - float(x))} {y}'); i += 8
        else:
            out.append('Z'); i += 1
    return P(' '.join(out))


# ---------------------------------------------------------------- cowboy hat
brim = 'M32 124 C48 148 80 160 128 160 C176 160 208 148 224 124 C224 168 184 196 128 196 C72 196 32 168 32 124 Z'
crown_c = 'M80 158 L90 84 C92 68 106 62 118 70 L128 78 L138 70 C150 62 164 68 166 84 L176 158'
icon('cowboy-hat', OBJ, ['western', 'cowboy', 'hat'],
     line=[P(brim), P(crown_c)], detail=[L(84, 126, 172, 126)], area=[P(brim), P(crown_c + ' Z')])

icon('crown-slash', OBJ, ['crown', 'disabled', 'off', 'objects'], **slashed('crown'))

# ---------------------------------------------------------------- crystal ball
cb = (128, 108)
shine = P(f'M{pt(polar(cb, 48, 195))} A48 48 0 0 1 {pt(polar(cb, 48, 245))}')
base_cb = 'M87 172 L68 216 H188 L169 172'
icon('crystal-ball', OBJ, ['fortune', 'prediction', 'magic', 'future'],
     line=[C(*cb, 76), P(base_cb)], detail=[shine], area=[C(*cb, 76), P(base_cb + ' Z')])

icon('diamond-slash', OBJ, ['diamond', 'disabled', 'off', 'objects'], **slashed('diamond'))

# ---------------------------------------------------------------- disco ball
dc, dr = (120, 144), 80
chord = lambda y: L(dc[0] - math.sqrt(dr * dr - (y - dc[1]) ** 2), y, dc[0] + math.sqrt(dr * dr - (y - dc[1]) ** 2), y)
icon('disco-ball', OBJ, ['party', 'disco', 'dance'],
     line=[C(*dc, dr), L(120, 32, 120, 64),
           P('M196 36 C198 52 202 56 218 58 C202 60 198 64 196 80 C194 64 190 60 174 58 C190 56 194 52 196 36 Z')],
     detail=[E(120, 144, 40, 80), chord(112), chord(176)],
     area=[C(*dc, dr)])

# ---------------------------------------------------------------- domino mask
mask = ('M128 88 C160 64 204 60 220 88 C232 120 212 176 172 176 C150 176 144 156 128 156 '
        'C112 156 106 176 84 176 C44 176 24 120 36 88 C52 60 96 64 128 88 Z')
icon('domino-mask', OBJ, ['mask', 'masquerade', 'carnival', 'disguise'],
     line=[P(mask), E(84, 124, 26, 16), E(172, 124, 26, 16)], area=[P(mask)],
     hole=[E(84, 124, 18, 8), E(172, 124, 18, 8)])

# ---------------------------------------------------------------- dress
dress = 'M100 32 V72 C100 88 106 100 112 112 L52 212 Q128 228 204 212 L144 112 C150 100 156 88 156 72 V32 C146 52 110 52 100 32 Z'
icon('dress', OBJ, ['dress', 'clothing', 'fashion', 'gown'], line=[P(dress)], detail=[L(112, 112, 144, 112)], area=[P(dress)])

# ---------------------------------------------------------------- drill
drill_body = R(40, 56, 136, 56, 16)
drill_handle = PG([(72, 112), (120, 112), (112, 180), (64, 180)])
chuck = PG([(176, 68), (200, 76), (200, 92), (176, 100)])
battery = R(40, 180, 104, 44, 12)
icon('drill', OBJ, ['drill', 'power tool', 'diy', 'construction', 'power drill'],
     line=[drill_body, P('M72 112 L64 180'), P('M120 112 L112 180'), chuck, L(200, 84, 224, 84), battery],
     detail=[L(68, 84, 108, 84)],
     area=[drill_body, drill_handle, chuck, battery])

# ---------------------------------------------------------------- electric razor
rz_body = 'M80 88 L88 208 A16 16 0 0 0 104 224 H152 A16 16 0 0 0 168 208 L176 88'
icon('electric-razor', OBJ, ['electric razor', 'shaver', 'grooming', 'shave'],
     line=[R(56, 32, 144, 56, 16), P(rz_body)],
     detail=[L(104, 32, 104, 88), L(152, 32, 152, 88), L(128, 128, 128, 160)],
     area=[R(56, 32, 144, 56, 16), P(rz_body + ' Z')])

# ---------------------------------------------------------------- explosion
radii = [100, 50, 84, 48, 96, 52, 80, 46, 98, 50, 86, 48, 92, 52, 82, 46]
boom = [polar((128, 130), r * 0.96, -90 + i * 360 / len(radii) + (6 if i % 4 == 2 else 0)) for i, r in enumerate(radii)]
icon('explosion', OBJ, ['explosion', 'blast', 'boom', 'burst', 'bang'], line=[PG(boom)], area=[PG(boom)])

# ---------------------------------------------------------------- fidget spinner
sc, SR, lr, cr = (128, 144), 64, 40, 24
lobes = [polar(sc, SR, a) for a in (-90, 30, 150)]
conc = [polar(sc, SR, a) for a in (-30, 90, 210)]  # concave centres between lobes
d = 'M'
segs = []
for i in range(3):
    lc = lobes[i]; cprev = conc[(i - 1) % 3]; cnext = conc[i]
    t_in = (lc[0] + (cprev[0] - lc[0]) * lr / (lr + cr), lc[1] + (cprev[1] - lc[1]) * lr / (lr + cr))
    t_out = (lc[0] + (cnext[0] - lc[0]) * lr / (lr + cr), lc[1] + (cnext[1] - lc[1]) * lr / (lr + cr))
    segs.append((t_in, t_out, lc, cnext))
sp = f'M{pt(segs[0][0])}'
for i, (t_in, t_out, lc, cn) in enumerate(segs):
    sp += ' ' + arc_to(lc, lr, t_in, t_out, lambda m: dist(m, sc))
    nxt = segs[(i + 1) % 3][0]
    sp += ' ' + arc_to(cn, cr, t_out, nxt, lambda m: -dist(m, sc))
sp += ' Z'
icon('fidget-spinner', OBJ, ['fidget spinner', 'toy', 'spin', 'fidget'],
     line=[P(sp)], area=[P(sp)], dotcut=[C(*p, 16) for p in lobes] + [C(*sc, 16)])

# ---------------------------------------------------------------- fire extinguisher
icon('fire-extinguisher', OBJ, ['extinguisher', 'fire safety', 'emergency', 'safety', 'red'],
     line=[R(56, 100, 104, 124, 28), L(108, 100, 108, 68), L(108, 68, 64, 44),
           P('M108 68 H164 C192 68 208 84 208 112 V176')],
     detail=[L(56, 152, 160, 152)], area=[R(56, 100, 104, 124, 28)])

# ---------------------------------------------------------------- fire hydrant
hy_body = 'M88 96 V120 H64 V160 H88 V216 M168 216 V160 H192 V120 H168 V96'
hy_area = 'M88 96 V120 H64 V160 H88 V216 H168 V160 H192 V120 H168 V96 Z'
hy_dome = 'M80 96 A48 48 0 0 1 176 96'
hydrant = dict(line=[P(hy_dome), L(64, 96, 192, 96), P(hy_body), L(64, 216, 192, 216), L(128, 32, 128, 48)],
               area=[P(hy_dome + ' Z'), P(hy_area)], dotcut=[C(128, 140, 16)])
icon('fire-hydrant', OBJ, ['hydrant', 'firefighter', 'street', 'water', 'fire'], **hydrant)
icon('fire-hydrant-slash', OBJ, ['fire hydrant', 'off', 'disabled', 'hidden', 'fire'],
     line=hydrant['line'] + [SLASH])

# ---------------------------------------------------------------- flag banner
band = 'M60 64 H196 V144 H60 Z'
ltail = 'M60 104 H32 L52 140 L32 176 H92 V144'
rtail = 'M196 104 H224 L204 140 L224 176 H164 V144'
icon('flag-banner', OBJ, ['banner', 'ribbon', 'label', 'bunting', 'party'],
     line=[P(band), P(ltail), P(rtail)],
     area=[P(band), P(ltail + ' Z'), P(rtail + ' Z')])

# ---------------------------------------------------------------- flip-flops
def sole(cx):
    return [('M', (cx, 40)), ('C', (cx + 26, 40), (cx + 32, 64), (cx + 30, 96)),
            ('C', (cx + 28, 124), (cx + 32, 148), (cx + 32, 180)),
            ('C', (cx + 32, 206), (cx + 18, 224), (cx, 224)),
            ('C', (cx - 18, 224), (cx - 32, 206), (cx - 32, 180)),
            ('C', (cx - 32, 148), (cx - 28, 124), (cx - 30, 96)),
            ('C', (cx - 32, 64), (cx - 26, 40), (cx, 40)), ('Z',)]
ff_line, ff_det = [], []
for cx, deg in ((76, -8), (180, 8)):
    tf = rt(deg, (cx, 132))
    ff_line.append(path(sole(cx), tf))
    ff_det.append(path([('M', (cx - 29, 136)), ('L', (cx, 80)), ('L', (cx + 29, 136))], tf))
icon('flip-flops', OBJ, ['sandals', 'beach', 'summer', 'footwear'], line=ff_line, detail=ff_det, area=ff_line)

# ---------------------------------------------------------------- fountain
basin = 'M40 176 H216 V192 A24 24 0 0 1 192 216 H64 A24 24 0 0 1 40 192 Z'
bowl = 'M80 112 H176 C176 136 156 148 128 148 C100 148 80 136 80 112 Z'
fountain = dict(line=[P(basin), P(bowl), L(128, 148, 128, 176), L(128, 112, 128, 56),
                      P('M128 56 C80 48 52 80 48 140'), P('M128 56 C176 48 204 80 208 140')],
                area=[P(basin), P(bowl)])
icon('fountain', OBJ, ['fountain', 'water', 'park', 'plaza'], **fountain)
icon('fountain-slash', OBJ, ['fountain', 'off', 'disabled', 'hidden'], line=fountain['line'] + [SLASH])

# ---------------------------------------------------------------- gas cylinder
icon('gas-cylinder', OBJ, ['propane tank', 'gas bottle', 'lpg', 'fuel'],
     line=[R(56, 96, 144, 128, 36), L(128, 96, 128, 56), L(100, 56, 156, 56)],
     detail=[L(56, 140, 200, 140), L(56, 180, 200, 180)], area=[R(56, 96, 144, 128, 36)])

icon('glasses-slash', OBJ, ['glasses', 'disabled', 'off', 'objects'], **slashed('glasses'))

# ---------------------------------------------------------------- grave
stone = 'M56 224 V112 A72 72 0 0 1 200 112 V224'
icon('grave', OBJ, ['grave', 'tombstone', 'rip', 'cemetery'],
     line=[P(stone), L(32, 224, 224, 224)], detail=[L(128, 92, 128, 172), L(100, 120, 156, 120)],
     area=[P(stone + ' Z')])

# ---------------------------------------------------------------- hair clip (snap clip, tapered)
u = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))
A_ = (128 - u[0] * 60, 128 - u[1] * 60); B_ = (128 + u[0] * 72, 128 + u[1] * 72)
def taper(A, ra, B, rb):
    dd = dist(A, B); ux, uy = (B[0] - A[0]) / dd, (B[1] - A[1]) / dd
    s = (ra - rb) / dd; cth = math.sqrt(1 - s * s)
    # unit normals for external tangents
    n1 = (ux * s - uy * cth, uy * s + ux * cth); n2 = (ux * s + uy * cth, uy * s - ux * cth)
    a1 = (A[0] + n1[0] * ra, A[1] + n1[1] * ra); b1 = (B[0] + n1[0] * rb, B[1] + n1[1] * rb)
    a2 = (A[0] + n2[0] * ra, A[1] + n2[1] * ra); b2 = (B[0] + n2[0] * rb, B[1] + n2[1] * rb)
    far = lambda m: dist(m, ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2))
    return f'M{pt(a1)} L{pt(b1)} ' + arc_to(B, rb, b1, b2, far) + f' L{pt(a2)} ' + arc_to(A, ra, a2, a1, far) + ' Z'
outer_clip = taper(A_, 48, B_, 20)
tip = (A_[0] + u[0] * 84, A_[1] + u[1] * 84)
inner_clip = taper(A_, 16, tip, 2)
icon('hair-clip', OBJ, ['hair clip', 'barrette', 'accessory', 'hair'],
     line=[P(outer_clip), P(inner_clip)], area=[P(outer_clip)], hole=[P(taper(A_, 8, tip, 1))])

# ---------------------------------------------------------------- hair clippers
cl_body = 'M80 88 L88 200 A24 24 0 0 0 112 224 H144 A24 24 0 0 0 168 200 L176 88'
icon('hair-clippers', OBJ, ['clippers', 'barber', 'haircut', 'trimmer'],
     line=[R(72, 56, 112, 32, 8), P(cl_body), L(96, 40, 96, 56), L(128, 40, 128, 56), L(160, 40, 160, 56)],
     detail=[L(128, 124, 128, 160)], area=[R(72, 56, 112, 32, 8), P(cl_body + ' Z')])

# ---------------------------------------------------------------- hair dryer
barrel = 'M80 48 H176 L216 36 V156 L176 144 H80 A48 48 0 0 1 80 48 Z'
dry_handle = PG([(76, 144), (124, 144), (116, 216), (84, 216)])
icon('hair-dryer', OBJ, ['hair dryer', 'blow dryer', 'salon', 'styling', 'beauty'],
     line=[P(barrel), dry_handle], detail=[C(80, 96, 20), L(176, 48, 176, 144)],
     area=[P(barrel), dry_handle])

# ---------------------------------------------------------------- hairbrush (paddle, tilted)
hb = rt(45, (128, 128))
head = [('M', (128, 40)), ('A', 56, 0, 1, (184, 96)), ('L', (184, 120)), ('A', 56, 0, 1, (72, 120)),
        ('L', (72, 96)), ('A', 56, 0, 1, (128, 40)), ('Z',)]
handle = [('M', (108, 174)), ('L', (110, 220)), ('A', 18, 0, 0, (146, 220)), ('L', (148, 174))]
icon('hairbrush', OBJ, ['hairbrush', 'brush', 'grooming', 'hair'],
     line=[path(head, hb), path(handle, hb)],
     area=[path(head, hb), path(handle + [('Z',)], hb)],
     dotcut=[C(*hb(p), 12) for p in ((108, 84), (148, 84), (108, 124), (148, 124))])

# ---------------------------------------------------------------- hammer drill
hd_body = R(40, 56, 136, 56, 16)
hd_handle = PG([(64, 112), (108, 112), (100, 216), (56, 216)])
aux = P(capsule((176, 152), 28, 16, (0.34, 0.94)))
icon('hammer-drill', OBJ, ['hammer drill', 'power drill', 'tools', 'construction'],
     line=[hd_body, P('M64 112 L56 216 H100 L108 112'), chuck, L(200, 84, 224, 84), aux],
     detail=[L(68, 84, 108, 84), L(92, 84, 92, 84)],
     area=[hd_body, hd_handle, chuck, aux])

# ---------------------------------------------------------------- hammer slash (hammer mirrored so the handle crosses the slash)
hm = load('hammer')
icon('hammer-slash', OBJ, ['hammer', 'off', 'disabled', 'hidden'], line=[mirror_x(e) for e in hm['line']] + [SLASH])

# ---------------------------------------------------------------- hanger
hanger = dict(line=[P('M108 68 A20 20 0 1 1 128 88 V108'), PG([(128, 108), (224, 180), (32, 180)])],
              area=[PG([(128, 108), (224, 180), (32, 180)])])
icon('hanger', OBJ, ['hanger', 'clothes', 'closet', 'wardrobe', 'coat hanger'], **hanger)
icon('hanger-slash', OBJ, ['hanger', 'off', 'disabled', 'hidden'], line=hanger['line'] + [SLASH])

# ---------------------------------------------------------------- hat (fedora)
crown_f = 'M76 148 L84 96 C86 80 100 72 114 76 L128 82 L142 76 C156 72 170 80 172 96 L180 148'
icon('hat', OBJ, ['hat', 'fedora', 'clothing', 'fashion'],
     line=[P(crown_f), P('M76 148 A96 24 0 1 0 180 148')], detail=[L(80, 124, 176, 124)],
     area=[P(crown_f + ' Z'), E(128, 168, 96, 24)])

# ---------------------------------------------------------------- high heel
heel = ('M48 72 V140 L56 216 H72 L80 152 C108 156 128 180 152 200 H204 A20 20 0 0 0 220 172 '
        'C200 160 176 154 152 150 C112 142 84 108 72 72 Z')
icon('high-heel', OBJ, ['heels', 'shoe', 'fashion', 'high heels', 'stiletto'], line=[P(heel)], area=[P(heel)])

# ---------------------------------------------------------------- hoodie / jacket
top = ('M96 52 L60 68 C48 74 44 84 42 96 L32 172 L64 180 L80 116 V216 H176 V116 L192 180 L224 172 '
       'L214 96 C212 84 208 74 196 68 L160 52')
hood = 'M96 52 C92 38 108 32 128 32 C148 32 164 38 160 52'
icon('hoodie', OBJ, ['hoodie', 'sweatshirt', 'clothing', 'hood'],
     line=[P(top), P(hood), P('M96 52 C100 80 114 92 128 92 C142 92 156 80 160 52')],
     detail=[L(116, 108, 116, 128), L(140, 108, 140, 128)],
     area=[P(top + ' Z'), P(hood + ' Z')])
icon('jacket', OBJ, ['jacket', 'coat', 'clothing', 'outerwear'],
     line=[P(top), PL([(96, 52), (128, 100), (160, 52)]), P('M96 52 C112 44 144 44 160 52')],
     detail=[L(128, 100, 128, 216), PL([(96, 52), (104, 92), (124, 94)]), PL([(160, 52), (152, 92), (132, 94)])],
     area=[P(top + ' Z')])

# ---------------------------------------------------------------- jackhammer
jh_bit = PG([(112, 176), (144, 176), (144, 204), (128, 224), (112, 204)])
icon('jackhammer', OBJ, ['jackhammer', 'construction', 'drill', 'road work'],
     line=[PL([(40, 72), (40, 40), (216, 40), (216, 72)]), L(128, 40, 128, 72), R(72, 72, 112, 104, 20), jh_bit],
     detail=[L(104, 124, 152, 124)], area=[R(72, 72, 112, 104, 20), jh_bit])

# ---------------------------------------------------------------- joker (jester cap)
cap = ('M64 176 C60 140 56 116 44 100 C76 104 98 120 106 144 C106 108 114 80 128 56 C142 80 150 108 150 144 '
       'C158 120 180 104 212 100 C200 116 196 140 192 176 Z')
icon('joker', OBJ, ['joker', 'jester', 'playing card', 'clown'],
     line=[P(cap), R(56, 176, 144, 40, 12)], area=[P(cap), R(56, 176, 144, 40, 12)],
     dot=[C(44, 96, 16), C(128, 52, 16), C(212, 96, 16)])

# ---------------------------------------------------------------- kimono
kim = 'M96 40 L32 56 V120 H80 V224 H176 V120 H224 V56 L160 40 Z'
icon('kimono', OBJ, ['robe', 'kimono', 'hanfu', 'traditional'],
     line=[P(kim)],
     detail=[L(96, 40, 148, 148), L(160, 40, 123, 92), L(80, 148, 176, 148), L(80, 184, 176, 184)],
     area=[P(kim)])

# ---------------------------------------------------------------- knife
kn = rt(-45)
blade = [('M', (-16, -24)), ('L', (116, -24)), ('C', (108, 4), (92, 20), (60, 20)), ('L', (-16, 20)), ('Z',)]
kh = [('M', (-16, -16)), ('L', (-100, -16)), ('A', 16, 0, 0, (-100, 16)), ('L', (-16, 16)), ('Z',)]
tfk = lambda p: (lambda q: (q[0] + 6, q[1] + 6))(kn((p[0] + 128, p[1] + 128)))
icon('knife', OBJ, ['knife', 'blade', 'cut', 'kitchen', 'chef'],
     line=[path(blade, tfk), path(kh, tfk)], area=[path(blade, tfk), path(kh, tfk)])

# ---------------------------------------------------------------- ladder
lx = lambda y, a, b: a + (b - a) * (y - 32) / 192
ladder = [L(84, 32, 64, 224), L(172, 32, 192, 224)] + [L(lx(y, 84, 64), y, lx(y, 172, 192), y) for y in (72, 116, 160, 204)]
icon('ladder', OBJ, ['ladder', 'climb', 'steps', 'tools', 'diy'], line=ladder)
icon('ladder-slash', OBJ, ['ladder', 'off', 'disabled', 'hidden'], line=ladder + [SLASH])

lb = load('lifebuoy')
lb_drop = [e for e in lb['line'] + lb['detail'] if 'M159.11 159.11' in e or 'M96.89 96.89' in e]
icon('lifebuoy-slash', OBJ, ['lifebuoy', 'off', 'disabled', 'hidden'], **slashed('lifebuoy', lb_drop))
icon('lightbulb-slash', OBJ, ['light off', 'lightbulb', 'disabled', 'idea', 'lights off'], **slashed('lightbulb'))

# ---------------------------------------------------------------- lighter
flame = 'M108 32 C98 48 88 58 88 68 A20 20 0 0 0 128 68 C128 58 118 48 108 32 Z'
icon('lighter', OBJ, ['lighter', 'flame', 'fire', 'smoke'],
     line=[P(flame), P('M76 128 V112 H140 V128'), R(64, 128, 128, 96, 16)],
     area=[P(flame), R(64, 128, 128, 96, 16)], dot=[C(172, 108, 16)])

# ---------------------------------------------------------------- lipstick
icon('lipstick', OBJ, ['lipstick', 'makeup', 'cosmetics', 'beauty'],
     line=[R(72, 144, 112, 80, 14), R(88, 112, 80, 32, 8), P('M100 112 V72 L156 40 V112')],
     area=[R(72, 144, 112, 80, 14), R(88, 112, 80, 32, 8), P('M100 112 V72 L156 40 V112 Z')])

# ---------------------------------------------------------------- lockers
lk_det = [L(96, 32, 96, 224), L(160, 32, 160, 224)]
for cx in (64, 128, 192):
    lk_det += [L(cx - 8, 64, cx + 8, 64), L(cx - 8, 100, cx + 8, 100), L(cx + 8, 144, cx + 8, 168)]
icon('lockers', OBJ, ['lockers', 'gym', 'storage'], line=[R(32, 32, 192, 192, 14)], detail=lk_det,
     area=[R(32, 32, 192, 192, 14)])

mw = load('magic-wand')
icon('magic-wand-slash', OBJ, ['magic wand', 'off', 'disabled', 'hidden', 'magic'],
     line=mw['line'] + mw['detail'] + [SLASH], dot=[d for d in mw['dot'] if '"88"' not in d])

# ---------------------------------------------------------------- makeup brush + compact
mb = lambda p: rot([(p[0] + 176, p[1] + 36)], 12, (176, 36))[0]
bristle = [('M', (-24, 24)), ('L', (24, 0)), ('L', (20, 72)), ('L', (-20, 72)), ('Z',)]
ferrule = [('M', (-20, 72)), ('L', (20, 72)), ('L', (16, 104)), ('L', (-16, 104)), ('Z',)]
icon('makeup-brush', OBJ, ['makeup brush', 'powder', 'cosmetics', 'beauty'],
     line=[C(76, 172, 44), path(bristle, mb), path(ferrule, mb), path([('M', (0, 104)), ('L', (0, 184))], mb)],
     detail=[C(76, 172, 16)],
     area=[C(76, 172, 44), path(bristle, mb), path(ferrule, mb)])

# ---------------------------------------------------------------- mascara
icon('mascara', OBJ, ['mascara', 'makeup', 'lashes', 'cosmetics'],
     line=[R(56, 72, 56, 152, 20), R(148, 32, 40, 64, 12), L(168, 96, 168, 220),
           L(148, 160, 188, 160), L(148, 196, 188, 196)],
     detail=[L(56, 124, 112, 124)], area=[R(56, 72, 56, 152, 20), R(148, 32, 40, 64, 12)])

# ---------------------------------------------------------------- matchstick
mt = rt(40)
fl = [('M', (128, 14)), ('C', (118, 30), (110, 42), (110, 58)), ('A', 18, 0, 0, (146, 58)),
      ('C', (146, 42), (138, 30), (128, 14)), ('Z',)]
mh = P(capsule(mt((128, 128)), 12, 22, (math.cos(math.radians(130)), math.sin(math.radians(130)))))
icon('matchstick', OBJ, ['match', 'matchstick', 'fire', 'flame'],
     line=[path(fl, mt), mh, path([('M', (128, 162)), ('L', (128, 240))], mt)],
     area=[path(fl, mt), mh])

# ---------------------------------------------------------------- maze
icon('maze', OBJ, ['maze', 'labyrinth', 'puzzle', 'path'],
     line=[PL([(80, 32), (224, 32), (224, 224), (176, 224)]), PL([(128, 224), (32, 224), (32, 32)]),
           PL([(80, 80), (176, 80), (176, 176)]), PL([(80, 80), (80, 176), (128, 176)]),
           L(128, 128, 176, 128), L(80, 176, 80, 224)])

# ---------------------------------------------------------------- military medal
star = [polar((128, 168), 56 if i % 2 == 0 else 26, -90 + i * 36) for i in range(10)]
icon('medal-military', OBJ, ['military medal', 'honor', 'award', 'ribbon'],
     line=[R(80, 32, 96, 64, 8), L(128, 96, 128, 112), PG(star)],
     detail=[L(112, 32, 112, 96), L(144, 32, 144, 96)],
     area=[R(80, 32, 96, 64, 8), PG(star)])

icon('medal-slash', OBJ, ['award', 'medal', 'disabled'], **slashed('medal'))

print(save(overwrite=True))
