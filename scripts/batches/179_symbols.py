import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CC = (128, 128)
CIRCLE = C(128, 128, 96)
SQUARE = R(32, 32, 192, 192, 16)
SLASH = L(48, 48, 208, 208)
SY = 'Symbols'


# ---------------------------------------------------------------- helpers
def star_pts(c, r, ratio=0.44, n=5, start=-90):
    pts = []
    for i in range(2 * n):
        pts.append(polar(c, r if i % 2 == 0 else r * ratio, start + i * 180 / n))
    return pts


def densify(pts, closed=False, step=2.0):
    seq = list(pts) + ([pts[0]] if closed else [])
    out = [seq[0]]
    for a, b in zip(seq, seq[1:]):
        n = max(1, int(math.ceil(dist(a, b) / step)))
        for k in range(1, n + 1):
            out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    return out


def arc_pts(c, r, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0) / 3))
    return [polar(c, r, a0 + (a1 - a0) * k / n) for k in range(n + 1)]


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + t * dx, a[1] + t * dy))


def gap(pts, closed=False, g=30):
    """Split a polyline wherever it passes within g of the slash; returns path elements."""
    d = densify(pts, closed)
    runs, cur = [], []
    for p in d:
        if seg_dist(p) >= g:
            cur.append(p)
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
    if len(cur) > 1:
        runs.append(cur)
    if closed and len(runs) > 1 and seg_dist(d[0]) >= g:
        runs[0] = runs[-1] + runs[0][1:]
        runs.pop()
    out = []
    for r_ in runs:
        if dist(r_[0], r_[-1]) < 6 and len(r_) < 6:
            continue
        out.append(PL(simplify(r_)))
    return out


def simplify(pts, tol=0.25):
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        cross = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        if cross / max(dist(a, c), 1e-6) > tol:
            out.append(b)
    out.append(pts[-1])
    return out


def ellipse_arc_pts(c, rx, ry, a0, a1, n=48):
    out = []
    for k in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * k / n)
        out.append((c[0] + rx * math.cos(t), c[1] + ry * math.sin(t)))
    return out


# ---------------------------------------------------------------- comparison / sets
icon('less-than', SY, ['less than', 'compare', 'math', 'comparison', 'symbol'],
     line=[PL([(184, 60), (72, 128), (184, 196)])])
icon('less-than-or-equal', SY, ['less or equal', 'compare', 'math', 'less than or equal', 'comparison'],
     line=[PL([(184, 40), (72, 98), (184, 156)]), L(72, 208, 184, 208)])
icon('not-equals', SY, ['not equal', 'unequal', 'math'],
     line=[L(48, 100, 208, 100), L(48, 156, 208, 156), L(164, 44, 92, 212)])

ELEM = [P('M188 64 H140 A64 64 0 0 0 140 192 H188'), L(76, 128, 180, 128)]
icon('member-of', SY, ['element of', 'set', 'math'], line=ELEM)
icon('not-member-of', SY, ['not element of', 'set', 'math'], line=ELEM + [L(160, 36, 100, 220)])

SUBP = P('M196 56 H128 A72 72 0 0 0 128 200 H196')
SUBE = [P('M192 44 H124 A60 60 0 0 0 124 164 H192'), L(64, 212, 192, 212)]
SUPP = P('M60 56 H128 A72 72 0 0 1 128 200 H60')
SUPE = [P('M64 44 H132 A60 60 0 0 1 132 164 H64'), L(64, 212, 192, 212)]
icon('subset-of', SY, ['subset', 'set', 'math'], line=SUBE)
icon('subset-proper-of', SY, ['proper subset', 'set', 'math'], line=[SUBP])
icon('superset-of', SY, ['superset', 'set', 'math'], line=SUPE)
icon('superset-proper-of', SY, ['proper superset', 'set', 'math'], line=[SUPP])
icon('not-subset-of', SY, ['not subset', 'set', 'math'], line=[SUBP, L(164, 36, 92, 220)])
icon('not-superset-of', SY, ['not superset', 'set', 'math'], line=[SUPP, L(164, 36, 92, 220)])

icon('plus-minus', SY, ['plus minus', 'tolerance', 'math', 'approximately', 'increase decrease'],
     line=[L(128, 48, 128, 160), L(64, 104, 192, 104), L(64, 208, 192, 208)])
icon('plus-minus-circle', 'Interface', ['plus minus', 'tolerance', 'math'],
     line=[CIRCLE], area=[CIRCLE],
     detail=[L(128, 76, 128, 140), L(96, 108, 160, 108), L(96, 172, 160, 172)])
icon('square-root', SY, ['square root', 'radical', 'math', 'sqrt'],
     line=[PL([(32, 144), (60, 128), (100, 208), (148, 48), (224, 48)])])
icon('tilde', SY, ['tilde', 'approximately', 'wave', 'symbol'],
     line=[P('M40 160 C60 104 100 96 128 128 C156 160 196 152 216 96')])
icon('omega', SY, ['omega', 'greek', 'ohm', 'symbol'],
     line=[P('M44 204 H92 V187 A80 80 0 1 1 164 187 V204 H212')])
icon('tally-marks', SY, ['tally marks', 'count', 'five', 'score', 'tally'],
     line=[L(x, 52, x, 204) for x in (68, 108, 148, 188)] + [L(36, 180, 220, 76)])

# ---------------------------------------------------------------- percent / question
PCT = [L(168, 88, 88, 168), C(96, 96, 14), C(160, 160, 14)]
icon('percent-circle', SY, ['percent', 'discount', 'rate', 'percent circle', 'circle'],
     line=[CIRCLE], area=[CIRCLE], detail=PCT)
icon('percent-square', SY, ['percent', 'discount', 'square', 'rate'],
     line=[SQUARE], area=[SQUARE], detail=PCT)
icon('question-mark', SY, ['question', 'help', 'unknown', 'glyph', 'question mark'],
     line=[P('M86 84 A42 42 0 1 1 146 121.5 C134 127.5 128 135 128 147 V153')], dot=[C(128, 204, 16)])

# ---------------------------------------------------------------- legal marks
icon('registered', SY, ['registered', 'trademark', 'r', 'legal', 'r symbol'],
     line=[CIRCLE], area=[CIRCLE],
     detail=[P('M104 172 V84 H134 A24 24 0 0 1 134 132 H104'), L(130, 132, 156, 172)])
M_GLYPH = PL([(136, 152), (136, 104), (160, 136), (184, 104), (184, 152)])
icon('trademark', SY, ['trademark', 'tm', 'brand', 'legal'],
     line=[CIRCLE], area=[CIRCLE],
     detail=[L(68, 104, 108, 104), L(88, 104, 88, 152), M_GLYPH])
s_top = ellipse_arc_pts((90, 116), 18, 12, -30, -270)
s_bot = ellipse_arc_pts((90, 140), 18, 12, -90, 150)
icon('servicemark', SY, ['service mark', 'sm', 'legal', 'trademark'],
     line=[CIRCLE], area=[CIRCLE],
     detail=[PL(s_top + s_bot[1:]), M_GLYPH])

# ---------------------------------------------------------------- seals
SEAL_D = load('seal-check')['line'][0]
seal_pts = []
for i in range(240):
    t = i * 2 * math.pi / 240
    rr = 88 + 8 * math.cos(10 * t)
    seal_pts.append((128 + rr * math.cos(t), 128 + rr * math.sin(t)))
SEAL_STAR = star_pts((128, 134), 50)
QM = [P('M106 98 A22 22 0 1 1 137.4 117.6 C131 121 128 125 128 132 V136')]
SPCT = [L(160, 96, 96, 160), C(100, 100, 12), C(156, 156, 12)]
icon('seal', SY, ['seal', 'rosette', 'badge', 'award', 'certified'], line=[SEAL_D], area=[SEAL_D])
icon('seal-plus', 'Interface', ['badge', 'add', 'seal', 'plus'],
     line=[SEAL_D], area=[SEAL_D], detail=[L(128, 88, 128, 168), L(88, 128, 168, 128)])
icon('seal-minus', 'Interface', ['badge', 'remove', 'seal', 'minus'],
     line=[SEAL_D], area=[SEAL_D], detail=[L(88, 128, 168, 128)])
icon('seal-star', 'Business', ['badge', 'award', 'star', 'certified'],
     line=[SEAL_D], area=[SEAL_D], detail=[PG(SEAL_STAR)])
icon('seal-percent', 'Commerce', ['discount', 'sale', 'percent', 'badge', 'discount badge'],
     line=[SEAL_D], area=[SEAL_D], detail=SPCT)
icon('seal-question', 'Interface', ['badge', 'help', 'seal', 'question', 'faq'],
     line=[SEAL_D], area=[SEAL_D], detail=QM, dotcut=[C(128, 170, 16)])
# slash variant: the check stays whole and the slash passes behind it
CHK = [(88, 132), (116, 160), (172, 104)]
chk_d = densify(CHK)
runs = [[]]
for p_ in densify([(48, 48), (208, 208)]):
    if min(dist(p_, q) for q in chk_d) < 28:
        if runs[-1]:
            runs.append([])
        continue
    runs[-1].append(p_)
icon('seal-check-slash', 'Security', ['seal check', 'off', 'disabled', 'hidden', 'seal'],
     line=gap(seal_pts, True) + [PL(CHK)] + [L(*r_[0], *r_[-1]) for r_ in runs if len(r_) > 1])
# seal-percent-slash skipped: the percent's two circles sit on the slash diagonal, so it cannot read cleanly

# ---------------------------------------------------------------- sleep / sos
Z1 = [(36, 144), (108, 144), (36, 216), (108, 216)]
Z2 = [(156, 44), (212, 44), (156, 100), (212, 100)]
icon('sleep', SY, ['sleep', 'zzz', 'rest', 'snooze'], line=[PL(Z1), PL(Z2)])
icon('sleep-slash', SY, ['sleep', 'off', 'disabled', 'hidden'], line=[PL(Z1), PL(Z2), SLASH])

SOS_BOX = R(32, 56, 192, 144, 16)
def s_glyph(cx, cy, rx=15, ry=16):
    top = ellipse_arc_pts((cx, cy - ry), rx, ry, -20, -270)
    bot = ellipse_arc_pts((cx, cy + ry), rx, ry, -90, 160)
    return PL(top + bot[1:])
icon('sos', SY, ['sos', 'emergency', 'help', 'distress'],
     line=[SOS_BOX], area=[SOS_BOX],
     detail=[s_glyph(74, 128, 13), E(128, 128, 15, 32), s_glyph(182, 128, 13)])

# ---------------------------------------------------------------- stars
STAR_C = star_pts((128, 86), 54)
STAR_L = star_pts((68, 180), 36)
STAR_R = star_pts((188, 180), 36)
icon('stars', SY, ['rating', 'three stars', 'review', 'stars', 'magic'],
     line=[PG(STAR_C), PG(STAR_L), PG(STAR_R)], area=[PG(STAR_C), PG(STAR_L), PG(STAR_R)])
icon('stars-slash', SY, ['stars', 'off', 'disabled', 'hidden'],
     line=gap(STAR_C, True) + gap(STAR_L, True) + gap(STAR_R, True) + [SLASH])
icon('pentagram', SY, ['pentagram', 'star', 'five point', 'symbol'],
     line=[PG([polar((128, 136), 100, -90 + k * 144) for k in range(5)])])
hexa = star_pts(CC, 96, ratio=1 / math.sqrt(3), n=6)
icon('star-of-david', SY, ['star of david', 'judaism', 'hexagram', 'jewish', 'religion'],
     line=[PG(regular_polygon(CC, 96, 3)), PG(regular_polygon(CC, 96, 3, start=90))], area=[PG(hexa)])

# star and crescent
c1, r1, c2, r2 = (120, 128), 88, (152, 128), 72
p_top, p_bot = circle_x(c1, r1, c2, r2)
CRESC = P(f'M{pt(p_top)} A{r1} {r1} 0 1 0 {pt(p_bot)} A{r2} {r2} 0 1 1 {pt(p_top)} Z')
SC_STAR = PG(star_pts((176, 132), 36))
icon('star-and-crescent', SY, ['crescent', 'islam', 'star'], line=[CRESC, SC_STAR], area=[CRESC, SC_STAR])

# ---------------------------------------------------------------- religious / cultural
# peace: ring + spokes, fill weight keeps the sign by cutting the four sectors out
def sector(a0, a1, rr=84, d=12):
    half = math.radians((a1 - a0) / 2)
    mid = (a0 + a1) / 2
    v = polar(CC, d / math.sin(half), mid)
    da = math.degrees(math.asin(d / rr))
    pts = [v] + arc_pts(CC, rr, a0 + da, a1 - da)
    return PG(pts)
icon('peace', SY, ['peace', 'symbol', 'harmony', 'love'],
     line=[CIRCLE, L(128, 32, 128, 224), L(128, 128, *polar(CC, 96, 45)), L(128, 128, *polar(CC, 96, 135))],
     area=[CIRCLE], hole=[sector(-90, 45), sector(45, 90), sector(90, 135), sector(135, 270)])

YY_S = 'M128 32 A48 48 0 0 0 128 128 A48 48 0 0 1 128 224'
icon('yin-yang', SY, ['yin yang', 'balance', 'taoism', 'harmony'],
     line=[CIRCLE, P(YY_S)], area=[P(YY_S + ' A96 96 0 0 1 128 32 Z')],
     dot=[C(128, 80, 16)], dotcut=[C(128, 176, 16)])

icon('om', SY, ['om', 'aum', 'hindu', 'meditation'],
     line=[P('M52 88 A34 30 0 1 1 90 124 A42 42 0 1 1 52 184'),
           P('M120 156 C140 116 196 120 200 164 C204 200 168 212 148 192'),
           P('M144 80 A28 20 0 0 0 200 80')],
     dot=[C(172, 44, 14)])

icon('torii', SY, ['torii', 'shrine gate', 'japan', 'shinto'],
     line=[P('M32 48 Q128 80 224 48'), L(48, 108, 208, 108), L(80, 60, 80, 216), L(176, 60, 176, 216),
           L(128, 64, 128, 108)])

# menorah: seven branches on nested half circles
MC = (128, 92)
arms = [P(f'M{128 - r} 48 V92 A{r} {r} 0 0 0 {128 + r} 92 V48') for r in (32, 64, 96)]
icon('menorah', SY, ['menorah', 'hanukkah', 'jewish', 'candles'],
     line=arms + [L(128, 48, 128, 212), L(88, 212, 168, 212)])

icon('military-rank', SY, ['military rank', 'chevrons', 'insignia', 'sergeant'],
     line=[PL([(48, y + 48), (128, y), (208, y + 48)]) for y in (60, 104, 148)])

# ---------------------------------------------------------------- zodiac
ZT = ['zodiac', 'astrology', 'horoscope']
step = 176 / 6
wave = lambda y0: PL([(40 + k * step, y0 if k % 2 == 0 else y0 - 32) for k in range(7)])
icon('zodiac-aquarius', SY, ['aquarius'] + ZT, line=[wave(112), wave(176)])
icon('zodiac-aries', SY, ['aries'] + ZT,
     line=[P(f'M128 208 V88 A40 40 0 1 0 {pt(polar((88, 88), 40, 150))}'),
           P(f'M128 88 A40 40 0 1 1 {pt(polar((168, 88), 40, 30))}')])
icon('zodiac-cancer', SY, ['cancer'] + ZT,
     line=[C(80, 104, 24), P('M80 80 C124 68 180 72 212 108'),
           C(176, 152, 24), P('M176 176 C132 188 76 184 44 148')])
icon('zodiac-capricorn', SY, ['capricorn'] + ZT,
     line=[P('M36 64 L76 176 L112 64 V176 C112 206 148 214 168 198 C190 180 184 142 158 142 C132 142 126 178 140 210')])
icon('zodiac-gemini', SY, ['gemini'] + ZT,
     line=[P('M48 52 Q128 84 208 52'), P('M48 204 Q128 172 208 204'), L(96, 64, 96, 192), L(160, 64, 160, 192)])
icon('zodiac-leo', SY, ['leo'] + ZT,
     line=[C(76, 156, 32), P('M108 156 V96 A44 44 0 0 1 196 96 C196 140 164 160 172 196 Q178 216 208 204')])
icon('zodiac-libra', SY, ['libra'] + ZT,
     line=[L(40, 184, 216, 184), P('M40 144 H88 A48 48 0 1 1 168 144 H216')])

print(save(overwrite=True))
