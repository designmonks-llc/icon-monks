import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

ED, EDU, UI = 'Editor', 'Education', 'Interface'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def seg_circle(a, b, c, r):
    """Parameters t in [0,1] where segment a-b crosses circle (c, r)."""
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
    # rotate so we start at a vertex outside the circle
    k = next(i for i in range(n) if not inside(points[i]))
    pts = points[k:] + points[:k]
    seq = []  # sequence of (point, kind)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        for t in seg_circle(a, b, c, r):
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            seq.append((q, 'x'))
        if i + 1 < n:
            seq.append((b, 'in' if inside(b) else 'out'))
    # seq: points after pts[0]; first 'x' is entry, second is exit
    xs = [i for i, s in enumerate(seq) if s[1] == 'x']
    e_i, x_i = xs[0], xs[1]
    entry, exit_pt = seq[e_i][0], seq[x_i][0]
    after = [s[0] for s in seq[x_i + 1:] if s[1] == 'out']
    before = [s[0] for s in seq[:e_i] if s[1] == 'out']
    chain = [exit_pt] + after + [pts[0]] + before + [entry]
    d = poly(chain)
    area = d + ' ' + arc_to(c, r, entry, exit_pt, lambda m: -(m[0] + m[1])) + ' Z'
    return d, area


# ---------------------------------------------------------------- text-to-speech
wc = (116, 128)
waves = []
for rr in (56, 96):
    p, q = polar(wc, rr, -40), polar(wc, rr, 40)
    waves.append(P(f'M{pt(p)} A{rr} {rr} 0 0 1 {pt(q)}'))
icon('text-to-speech', ED, ['read aloud', 'speech', 'audio', 'tts'],
     line=[L(40, 64, 128, 64), L(40, 128, 108, 128), L(40, 192, 128, 192)] + waves)

# ---------------------------------------------------------------- text-underline-slash
icon('text-underline-slash', ED, ['text underline', 'off', 'disabled', 'hidden', 'text'],
     line=[P('M80 40 V112 A48 48 0 0 0 176 112 V40'), L(56, 208, 160, 208), SLASH])

# ---------------------------------------------------------------- text-uppercase
def letter_a(ax, ay, w, base, bar_y):
    lx, rx = ax - w / 2, ax + w / 2
    t = (base - bar_y) / (base - ay)
    return [PL([(lx, base), (ax, ay), (rx, base)]),
            L(lx + (ax - lx) * t, bar_y, rx - (rx - ax) * t, bar_y)]

icon('text-uppercase', ED, ['uppercase', 'caps', 'case', 'typography', 'capitals'],
     line=letter_a(78, 48, 92, 208, 156) + letter_a(190, 96, 68, 208, 172))

# ---------------------------------------------------------------- text-width
icon('text-width', ED, ['width', 'letter spacing', 'tracking', 'typography'],
     line=[L(64, 40, 192, 40), L(128, 40, 128, 136),
           L(40, 192, 216, 192), PL([(68, 164), (40, 192), (68, 220)]), PL([(188, 164), (216, 192), (188, 220)])])

# ---------------------------------------------------------------- text-wrap
icon('text-wrap', ED, ['text wrap', 'overflow', 'word wrap', 'lines', 'wrap text'],
     line=[L(40, 56, 216, 56), P('M40 120 H172 A36 36 0 0 1 172 192 H128'), PL([(152, 168), (128, 192), (152, 216)]),
           L(40, 192, 88, 192)])

# ---------------------------------------------------------------- image wrap layouts
def img(x, y, w, h):
    return R(x, y, w, h, 12)

def mxr(x, w):  # mirror a rect x
    return 256 - x - w

IMG_L = (32, 40, 96, 80)
icon('text-wrap-left', ED, ['float left', 'image wrap', 'layout', 'align'],
     line=[img(*IMG_L), L(160, 56, 224, 56), L(160, 104, 224, 104), L(32, 160, 224, 160), L(32, 208, 224, 208)],
     area=[img(*IMG_L)])
IMG_R = (mxr(32, 96), 40, 96, 80)
icon('text-wrap-right', ED, ['float right', 'image wrap', 'layout', 'align'],
     line=[img(*IMG_R), L(32, 56, 96, 56), L(32, 104, 96, 104), L(32, 160, 224, 160), L(32, 208, 224, 208)],
     area=[img(*IMG_R)])
IMG_N = (32, 84, 96, 88)
icon('text-wrap-none', ED, ['no float', 'inline image', 'layout', 'block', 'no wrap'],
     line=[L(32, 48, 224, 48), img(*IMG_N), L(32, 208, 224, 208)], area=[img(*IMG_N)])
IMG_C = (80, 84, 96, 88)
icon('text-wrap-center', ED, ['float center', 'image wrap', 'layout', 'align'],
     line=[L(32, 48, 224, 48), img(*IMG_C), L(32, 208, 224, 208)], area=[img(*IMG_C)])

# ---------------------------------------------------------------- textbox
TB = R(32, 72, 192, 112, 14)
icon('textbox', ED, ['input', 'text field', 'cursor', 'form', 'input field'],
     line=[TB], detail=[L(76, 104, 76, 152)], area=[TB])
TBS = R(32, 64, 192, 128, 40)
mg = (96, 120)
icon('textbox-magnifying-glass', UI, ['search field', 'search bar', 'input', 'find'],
     line=[TBS], detail=[C(*mg, 24), L(*polar(mg, 24, 45), *polar(mg, 54, 45))], area=[TBS])

# ---------------------------------------------------------------- translate-slash
tr = load('translate')
icon('translate-slash', ED, ['translate', 'off', 'disabled', 'hidden'], line=tr['line'] + [SLASH])

# ---------------------------------------------------------------- writing
tip = (96, 168)
off = [(0, 0), (12, -42), (96, -126), (126, -96), (42, -12)]
pen = [(tip[0] + a, tip[1] + b) for a, b in off]
band = [(pen[2][0] - 21.2, pen[2][1] + 21.2), (pen[3][0] - 21.2, pen[3][1] + 21.2)]
WR_LINES = [L(32, 208, 224, 208), L(32, 168, 64, 168)]
icon('writing', ED, ['writing', 'pen', 'notes', 'write'],
     line=[PG(pen)] + WR_LINES, detail=[L(*band[0], *band[1])], area=[PG(pen)])
icon('writing-slash', ED, ['writing', 'off', 'disabled', 'hidden'],
     line=[PG(pen), L(*band[0], *band[1])] + WR_LINES + [SLASH])

# ---------------------------------------------------------------- abacus
AB = R(32, 40, 192, 176, 14)
rods = [L(32, 96, 224, 96), L(32, 160, 224, 160)]
beads = [C(x, y, 24) for x, y in ((76, 96), (120, 96), (180, 96), (76, 160), (136, 160), (180, 160))]
icon('abacus', EDU, ['abacus', 'counting', 'math', 'beads'], line=[AB], detail=rods, area=[AB], dotcut=beads)
icon('abacus-slash', EDU, ['abacus', 'disabled', 'off', 'education'], line=[AB] + rods + [SLASH], dot=beads)

# ---------------------------------------------------------------- books
book = load('book')
BOOK = 'M48 200 V56 A24 24 0 0 1 72 32 H208 V224 H72 A24 24 0 0 1 48 200 Z'
PAGE = 'M48 200 A24 24 0 0 1 72 176 H208'
icon('bible', EDU, ['bible', 'scripture', 'holy book', 'religion'],
     line=book['line'], detail=book['detail'] + [L(128, 64, 128, 144), L(100, 92, 156, 92)], area=book['area'])
icon('book-arrow-down', EDU, ['book download', 'book', 'read', 'library', 'download'],
     line=book['line'], detail=book['detail'] + [L(128, 64, 128, 140), PL([(100, 112), (128, 140), (156, 112)])],
     area=book['area'])
icon('book-arrow-up', EDU, ['book upload', 'book', 'read', 'library', 'upload'],
     line=book['line'], detail=book['detail'] + [L(128, 140, 128, 64), PL([(100, 92), (128, 64), (156, 92)])],
     area=book['area'])
icon('book-bookmark', EDU, ['bookmarked book', 'reading', 'book', 'saved', 'bookmark'],
     line=book['line'] + [P('M136 32 V112 L156 96 L176 112 V32')], detail=book['detail'], area=book['area'],
     hole=[P('M136 40 V112 L156 96 L176 112 V40 Z')])
bh = 'M128 148 C128 148 84 124 84 96 A22 22 0 0 1 128 88 A22 22 0 0 1 172 96 C172 124 128 148 128 148 Z'
icon('book-heart', EDU, ['favorite book', 'loved', 'reading list'],
     line=book['line'], detail=book['detail'] + [P(bh)], area=book['area'])
icon('book-lock', EDU, ['locked book', 'private', 'diary'],
     line=book['line'], detail=book['detail'] + [R(96, 100, 64, 48, 10), P('M108 100 V88 A20 20 0 0 1 148 88 V100')],
     area=book['area'])
icon('book-slash', EDU, ['book', 'disabled', 'off', 'read', 'library'], line=book['line'] + book['detail'] + [SLASH])
bks = load('books')
icon('books-slash', EDU, ['books', 'disabled', 'off', 'education'], line=bks['line'] + bks['detail'] + [SLASH])

bo = load('book-open')
icon('book-open-text', EDU, ['reading', 'text', 'literature', 'manual', 'instructions'],
     line=bo['line'], detail=bo['detail'] + [L(64, 104, 100, 104), L(64, 144, 100, 144), L(156, 104, 192, 104), L(156, 144, 192, 144)],
     area=bo['area'])
BO_LOW = 'M128 136 C108 120 76 112 32 116 V196 C76 192 108 200 128 216 C148 200 180 192 224 196 V116 C180 112 148 120 128 136 Z'
icon('book-open-user', EDU, ['reader', 'reading', 'student'],
     line=[P(BO_LOW), C(128, 64, 28)], detail=[L(128, 136, 128, 216)], area=[P(BO_LOW), C(128, 64, 28)])
VOC = letter_a(80, 92, 44, 160, 140)
VOC_L = [L(156, 104, 192, 104), L(156, 144, 192, 144)]
icon('vocabulary', EDU, ['vocabulary', 'dictionary', 'words', 'language'],
     line=bo['line'], detail=bo['detail'] + VOC + VOC_L, area=bo['area'])
icon('vocabulary-slash', EDU, ['vocabulary', 'off', 'disabled', 'hidden'],
     line=bo['line'] + bo['detail'] + VOC + VOC_L + [SLASH])

# ---------------------------------------------------------------- bookmark badges
BM = [(64, 32), (192, 32), (192, 224), (128, 184), (64, 224)]
BC = (184, 184)
d, a = cut_polygon(BM, BC, 58)
pencil_b = 'M161.37 206.63 L182.59 202.38 L210.87 174.1 L193.9 157.13 L165.62 185.41 Z'
icon('bookmark-pencil', EDU, ['bookmark', 'edit', 'write', 'save', 'mark'],
     line=[P(d), P(pencil_b)], area=[P(a), P(pencil_b)])
icon('bookmark-question', EDU, ['bookmark', 'help', 'unknown', 'save', 'mark'],
     line=[P(d), P('M166 164 A18 18 0 1 1 190 181 C185 184 184 187 184 192')], area=[P(a)], dot=[C(184, 216, 14)])
d6, a6 = cut_polygon(BM, BC, 66)
spk = ('M184 151.36 C186.72 173.12 194.88 181.28 216.64 184 C194.88 186.72 186.72 194.88 184 216.64 '
       'C181.28 194.88 173.12 186.72 151.36 184 C173.12 181.28 181.28 173.12 184 151.36 Z')
icon('bookmark-sparkle', EDU, ['bookmark', 'ai', 'magic', 'save', 'mark'],
     line=[P(d6), P(spk)], area=[P(a6), P(spk)])
icon('bookmark-slash', EDU, ['bookmark', 'disabled', 'off', 'save', 'mark'], line=[PG(BM), SLASH])

# ---------------------------------------------------------------- chalkboard
CB = R(32, 40, 192, 128, 14)
CB_LEGS = [L(88, 168, 64, 224), L(168, 168, 192, 224)]
CB_CHALK = [P('M68 128 C80 96 92 88 100 104 C108 120 120 120 136 84'), L(164, 96, 188, 96), L(164, 128, 188, 128)]
icon('chalkboard', EDU, ['blackboard', 'classroom', 'teaching', 'chalkboard', 'class'],
     line=[CB] + CB_LEGS, detail=CB_CHALK, area=[CB])
icon('chalkboard-slash', EDU, ['chalkboard', 'disabled', 'off', 'education'], line=[CB] + CB_LEGS + CB_CHALK + [SLASH])

CT_B = R(120, 32, 104, 96, 12)
CT_BODY = 'M32 216 C32 176 44 156 64 156 C84 156 96 176 96 216'
icon('chalkboard-teacher', EDU, ['teacher', 'lecture', 'class', 'presenter'],
     line=[CT_B, C(64, 108, 24), P(CT_BODY), L(92, 180, 140, 152)],
     detail=[L(148, 64, 196, 64), L(148, 96, 180, 96)],
     area=[CT_B, C(64, 108, 24), P(CT_BODY + ' Z')])

CL_B = R(112, 32, 112, 88, 12)
CL_T = 'M32 132 C32 110 42 98 58 98 C74 98 84 110 84 132 Z'
icon('classroom', EDU, ['classroom', 'teacher', 'lesson', 'school'],
     line=[CL_B, C(58, 58, 18), P(CL_T), C(56, 196, 20), C(128, 196, 20), C(200, 196, 20)],
     detail=[L(140, 64, 196, 64), L(140, 92, 172, 92)],
     area=[CL_B, C(58, 58, 18), P(CL_T), C(56, 196, 20), C(128, 196, 20), C(200, 196, 20)])

# ---------------------------------------------------------------- exam
EX = R(48, 32, 160, 192, 14)
icon('exam', EDU, ['test', 'exam paper', 'grade'],
     line=[EX], detail=letter_a(100, 64, 48, 128, 108) + [L(148, 96, 180, 96), L(164, 80, 164, 112),
                                                          L(80, 164, 176, 164), L(80, 196, 144, 196)],
     area=[EX])

# ---------------------------------------------------------------- math symbols
icon('exponent', EDU, ['exponent', 'power', 'superscript', 'math'],
     line=[L(36, 96, 140, 200), L(140, 96, 36, 200), L(168, 40, 196, 84), L(220, 40, 176, 128)])
icon('integral', EDU, ['integral', 'calculus', 'math', 'symbol'],
     line=[P('M184 60 C182 42 170 32 156 32 C140 32 134 46 132 64 L124 192 C122 210 116 224 100 224 C86 224 74 214 72 196')])
icon('math-not', EDU, ['logical not', 'negation', 'logic', 'math'], line=[PL([(48, 100), (208, 100), (208, 164)])])
icon('matrix', EDU, ['matrix', 'brackets', 'math', 'grid'],
     line=[PL([(72, 40), (40, 40), (40, 216), (72, 216)]), PL([(184, 40), (216, 40), (216, 216), (184, 216)])],
     dot=[C(x, y, 16) for y in (88, 128, 168) for x in (88, 128, 168)])
icon('math-book', EDU, ['algebra', 'textbook', 'mathematics'],
     line=book['line'], detail=book['detail'] + [L(76, 104, 116, 104), L(96, 84, 96, 124), L(148, 88, 180, 88), L(148, 120, 180, 120)],
     area=book['area'])

# ---------------------------------------------------------------- geometry
hc = (128, 60)
lg, rg = (56, 216), (200, 216)
def from_circle(c, r, p):
    d_ = dist(c, p)
    return (c[0] + (p[0] - c[0]) * r / d_, c[1] + (p[1] - c[1]) * r / d_)
tri = [(128, 148), (154, 200), (102, 200)]
icon('geometry', EDU, ['geometry', 'compass', 'math', 'drawing'],
     line=[C(*hc, 20), L(128, 32, 128, 40), L(*from_circle(hc, 20, lg), *lg), L(*from_circle(hc, 20, rg), *rg), PG(tri)],
     area=[PG(tri)])

# ---------------------------------------------------------------- globe-stand
gc, gr, ar = (120, 100), 60, 92
a0, a1 = polar(gc, ar, -40), polar(gc, ar, 140)
icon('globe-stand', EDU, ['desk globe', 'geography', 'school'],
     line=[C(*gc, gr), P(f'M{pt(a0)} A{ar} {ar} 0 0 1 {pt(a1)}'), L(120, 192, 120, 216), L(84, 216, 156, 216)],
     detail=[E(*gc, 26, gr), L(gc[0] - gr, gc[1], gc[0] + gr, gc[1])], area=[C(*gc, gr)])

# ---------------------------------------------------------------- lectern
LT = 'M40 56 H216 L200 96 H56 Z'
LB = 'M84 96 L96 216 H160 L172 96'
LEC = [P(LT), P(LB), L(64, 216, 192, 216)]
icon('lectern', EDU, ['podium', 'speech', 'lecture'], line=LEC, area=[P(LT), P(LB + ' Z')])
icon('lectern-slash', EDU, ['lectern', 'off', 'disabled', 'hidden'], line=LEC + [SLASH])

# ---------------------------------------------------------------- notebook-pencil
nb = load('notebook')
NBL = 'M142 224 H70 A14 14 0 0 1 56 210 V46 A14 14 0 0 1 70 32 H202 A14 14 0 0 1 216 46 V135.6'
icon('notebook-pencil', EDU, ['notes', 'journal', 'writing', 'study'],
     line=[P(NBL), P(pencil_b)], detail=nb['detail'],
     area=[P(NBL + ' A58 58 0 0 0 142 224 Z'), P(pencil_b)])

# ---------------------------------------------------------------- school
ry = lambda x: 80 + (128 - x) / 88 * 56 if x < 128 else 80 + (x - 128) / 88 * 56
SCH = f'M40 216 V136 L108 {f(ry(108))} V60 L128 40 L148 60 V{f(ry(108))} L216 136 V216 Z'
DOOR = 'M108 216 V180 A20 20 0 0 1 148 180 V216'
icon('school', EDU, ['school', 'preschool', 'kindergarten', 'building', 'education'],
     line=[P(SCH), P(DOOR)], area=[P(SCH)], hole=[P('M116 216 V180 A12 12 0 0 1 140 180 V216 Z')])
icon('school-slash', EDU, ['school', 'off', 'disabled', 'hidden'], line=[P(SCH), P(DOOR), SLASH])

# ---------------------------------------------------------------- school-bell
BC2, BDEG = (128, 132), -18
def bp(x, y):
    return pt(rot([(x, y)], BDEG, BC2)[0])
SB = (f'M{bp(60, 184)} C{bp(76, 168)} {bp(84, 144)} {bp(84, 124)} A44 44 0 0 1 {bp(172, 124)} '
      f'C{bp(172, 144)} {bp(180, 168)} {bp(196, 184)} Z')
SBH = f'M{bp(112, 84)} L{bp(112, 50)} A16 16 0 0 1 {bp(144, 50)} L{bp(144, 84)}'
SBC = f'M{bp(110, 200)} A18 18 0 0 0 {bp(146, 200)}'
MC = (144, 112)
icon('school-bell', EDU, ['school bell', 'ring', 'class', 'alarm', 'hand bell'],
     line=[P(SB), P(SBH), P(SBC), P(f'M{pt(polar(MC, 56, -75))} A56 56 0 0 1 {pt(polar(MC, 56, -20))}'),
           P(f'M{pt(polar(MC, 88, -65))} A88 88 0 0 1 {pt(polar(MC, 88, -28))}')],
     area=[P(SB), P(SBH + ' Z')])

# ---------------------------------------------------------------- scroll
SC = [R(40, 32, 176, 40, 20), R(40, 184, 176, 40, 20)]
icon('scroll', EDU, ['scroll', 'history', 'parchment', 'document', 'ancient'],
     line=SC + [L(64, 72, 64, 184), L(192, 72, 192, 184)],
     detail=[L(96, 112, 160, 112), L(96, 144, 144, 144)],
     area=SC + [R(64, 52, 128, 152)])

# ---------------------------------------------------------------- student
hc2, hr2 = (128, 112), 32
capL, capM, capR = (52, 64), (128, 92), (204, 64)
def first_hit(a, b):
    ts = seg_circle(a, b, hc2, hr2)
    return (a[0] + (b[0] - a[0]) * ts[0], a[1] + (b[1] - a[1]) * ts[0])
hl = first_hit(capL, capM)
hrp = first_hit(capR, capM)
head = f'M{pt(hl)} ' + arc_to(hc2, hr2, hl, hrp, lambda m: m[1])
CAP = PG([(128, 36), capR, capM, capL])
SBODY = 'M56 216 C56 180 88 164 128 164 C168 164 200 180 200 216'
icon('student', EDU, ['student', 'learner', 'graduate'],
     line=[CAP, P(head), L(204, 64, 204, 108), P(SBODY)],
     area=[CAP, C(*hc2, hr2), P(SBODY + ' Z')])

print(save(overwrite=True))
