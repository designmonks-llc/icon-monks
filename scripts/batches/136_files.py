import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

EM, FI = 'Emoji', 'Files'
SLASH = L(48, 48, 208, 208)
K = (184, 184)  # badge centre
UL = lambda m: -m[0] - m[1]  # arc preference: the side toward the upper left


def head(tip, d, s):
    """Open arrowhead at tip pointing along unit vector d, arms of length s*sqrt2."""
    n = (-d[1], d[0])
    return PL([(tip[0] - s * (d[0] + n[0]), tip[1] - s * (d[1] + n[1])), tip,
               (tip[0] - s * (d[0] - n[0]), tip[1] - s * (d[1] - n[1]))])


# ======================================================================= Emoji (base: smiley)
FACE = C(128, 128, 96)
EYES = [C(96, 108, 16), C(160, 108, 16)]

icon('smiley-worried', EM, ['worried', 'stressed', 'anxious', 'emoji', 'nervous'],
     line=[FACE], area=[FACE],
     detail=[L(82, 76, 108, 62), L(148, 62, 174, 76), P('M100 182 A36 36 0 0 1 156 182')],
     dotcut=[C(96, 120, 16), C(160, 120, 16)])

# smiley-x: face features nudged up-left, outline opened around the badge (as smiley-currency-dollar)
fa, fb = (138.75, 223.4), (223.4, 138.75)
face_open = f'M{pt(fa)} A96 96 0 0 1 60.12 60.12 A96 96 0 0 1 {pt(fb)}'
icon('smiley-x', EM, ['smiley', 'remove', 'delete', 'cancel'],
     line=[P(face_open), L(166, 166, 202, 202), L(202, 166, 166, 202)],
     area=[P(face_open + f' A60 60 0 0 0 {pt(fa)} Z')],
     detail=[P('M80 136 A40 40 0 0 0 144 136')], dotcut=[C(84, 96, 16), C(140, 96, 16)])


def xeye(c, s=14):
    return [L(c[0] - s, c[1] - s, c[0] + s, c[1] + s), L(c[0] + s, c[1] - s, c[0] - s, c[1] + s)]


icon('smiley-x-eyes', EM, ['dead', 'knocked out', 'dizzy', 'x eyes', 'emoji'],
     line=[FACE], area=[FACE],
     detail=xeye((96, 104)) + xeye((160, 104)) + [L(100, 168, 156, 168)])

grin = 'M80 148 H176 A48 48 0 0 1 80 148 Z'
icon('smiley-x-eyes-happy', EM, ['crazy happy', 'laughing', 'face', 'emoji'],
     line=[FACE], area=[FACE],
     detail=[PL([(80, 82), (108, 98), (80, 114)]), PL([(176, 82), (148, 98), (176, 114)]), P(grin)],
     hole=[P(grin)])

icon('smiley-zipper', EM, ['silence', 'mute', 'zipped mouth', 'emoji', 'silent'],
     line=[FACE], area=[FACE], dotcut=EYES,
     detail=[L(80, 164, 176, 164), L(96, 152, 96, 176), L(128, 152, 128, 176), L(160, 152, 160, 176)])

stk = 'M48 32 H208 A16 16 0 0 1 224 48 V168 L168 224 H48 A16 16 0 0 1 32 208 V48 A16 16 0 0 1 48 32 Z'
icon('sticker', EM, ['sticker', 'emoji', 'peel', 'smiley', 'emoji sticker'],
     line=[P(stk)], area=[P(stk)],
     detail=[P('M224 168 H184 A16 16 0 0 0 168 184 V224'), P('M76 132 A44 44 0 0 0 156 132')],
     dotcut=[C(90, 92, 16), C(142, 92, 16)])

# ======================================================================= Slashed variants
AR = load('archive')
icon('archive-slash', FI, ['archive', 'disabled', 'off', 'files'], line=AR['line'] + AR['detail'] + [SLASH])
AT = load('article')
icon('article-slash', FI, ['article', 'disabled', 'off', 'files'], line=AT['line'] + AT['detail'] + [SLASH])

# ======================================================================= Box with arrow
box_walls = 'M48 128 V200 A16 16 0 0 0 64 216 H192 A16 16 0 0 0 208 200 V128'
box_flaps = [L(48, 128, 32, 92), L(208, 128, 224, 92)]
icon('box-arrow-down', FI, ['archive', 'store', 'box', 'put away'],
     line=[P(box_walls)] + box_flaps + [L(128, 32, 128, 120)],
     detail=[L(128, 128, 128, 176), PL([(100, 148), (128, 176), (156, 148)])],
     area=[P(box_walls + ' Z')])
icon('box-arrow-up', FI, ['unarchive', 'take out', 'box', 'restore'],
     line=[P(box_walls)] + box_flaps + [L(128, 40, 128, 120), PL([(100, 68), (128, 40), (156, 68)])],
     detail=[L(128, 128, 128, 176)],
     area=[P(box_walls + ' Z')])

# ======================================================================= Clipboard family (base: clipboard)
CB = load('clipboard')
cb_line, cb_area, cb_hole = CB['line'], CB['area'], CB['hole']
CLIP = R(88, 32, 80, 40, 10)


def clip(name, tags, **kw):
    icon(name, FI, tags, line=cb_line + kw.pop('line', []), area=cb_area + kw.pop('area', []), hole=cb_hole, **kw)


clip('clipboard-check', ['clipboard', 'done', 'checklist', 'approved', 'survey'],
     detail=[PL([(92, 150), (116, 174), (164, 126)])])
clip('clipboard-list', ['clipboard list', 'clipboard', 'paste', 'board', 'list'],
     detail=[L(124, 112, 172, 112), L(124, 148, 172, 148), L(124, 184, 172, 184)],
     dotcut=[C(86, 112, 16), C(86, 148, 16), C(86, 184, 16)])
clip('clipboard-minus', ['clipboard', 'remove', 'minus', 'list'], detail=[L(96, 148, 160, 148)])
clip('clipboard-plus', ['clipboard', 'add', 'new', 'plus', 'add task'],
     detail=[L(128, 116, 128, 180), L(96, 148, 160, 148)])
clip('clipboard-x', ['clipboard', 'remove', 'cancel', 'x', 'task failed'],
     detail=[L(104, 124, 152, 172), L(152, 124, 104, 172)])
icon('clipboard-slash', FI, ['clipboard', 'disabled', 'off', 'paste', 'board'], line=cb_line + [SLASH])

# clipboard-copy: a sheet in front of the clipboard's lower-right corner
sheet = R(120, 120, 104, 104, 14)
icon('clipboard-copy', FI, ['clipboard copy', 'clipboard', 'paste', 'board', 'copy'],
     line=[P('M84 224 H64 A16 16 0 0 1 48 208 V64 A16 16 0 0 1 64 48 H88'),
           P('M168 48 H192 A16 16 0 0 1 208 64 V84'), CLIP, sheet],
     detail=[L(152, 156, 192, 156), L(152, 188, 176, 188)],
     area=[P('M64 48 H192 A16 16 0 0 1 208 64 V92 H134 A42 42 0 0 0 92 134 V224 H64 A16 16 0 0 1 48 208 V64 '
             'A16 16 0 0 1 64 48 Z'), sheet],
     hole=cb_hole)


def clip_open(c, rc):
    """Clipboard outline and area opened around a badge circle (c, rc)."""
    ry = c[1] - math.sqrt(rc * rc - (208 - c[0]) ** 2)
    bx = c[0] - math.sqrt(rc * rc - (224 - c[1]) ** 2)
    a = arc_to(c, rc, (208, ry), (bx, 224), UL)
    line = [P(f'M{f(bx)} 224 H64 A16 16 0 0 1 48 208 V64 A16 16 0 0 1 64 48 H88'),
            P(f'M168 48 H192 A16 16 0 0 1 208 64 V{f(ry)}'), CLIP]
    area = [P(f'M64 48 H192 A16 16 0 0 1 208 64 V{f(ry)} {a} H64 A16 16 0 0 1 48 208 V64 A16 16 0 0 1 64 48 Z')]
    return line, area


SB = (180, 180)
l, a = clip_open(SB, 74)
icon('clipboard-smile', FI, ['clipboard', 'happy', 'positive', 'paste', 'board'],
     line=l + [C(*SB, 44)], area=a + [C(*SB, 44)], hole=cb_hole,
     detail=[P('M164 190 A24 24 0 0 0 196 190')], dotcut=[C(165, 164, 12), C(195, 164, 12)])

# ======================================================================= Copy family (base: copy)
CP = load('copy')
copy_back = CP['line'][1]


def copy_open(rc=56):
    e = K[0] - math.sqrt(rc * rc - 40 * 40)
    a = arc_to(K, rc, (224, e), (e, 224), UL)
    d = f'M{f(e)} 224 H94 A14 14 0 0 1 80 210 V94 A14 14 0 0 1 94 80 H210 A14 14 0 0 1 224 94 V{f(e)}'
    return [P(d), copy_back], [P(d + f' {a} Z')]


l, a = copy_open()
MARK_CHECK = [PL([(158, 186), (176, 204), (210, 168)])]
MARK_PLUS = [L(184, 160, 184, 208), L(160, 184, 208, 184)]
MARK_MINUS = [L(160, 184, 208, 184)]
MARK_X = [L(166, 166, 202, 202), L(202, 166, 166, 202)]
icon('copy-check', FI, ['copy', 'done', 'approved', 'duplicate', 'clone'], line=l + MARK_CHECK, area=a)
icon('copy-minus', FI, ['copy', 'remove', 'subtract', 'duplicate', 'clone'], line=l + MARK_MINUS, area=a)
icon('copy-plus', FI, ['copy', 'add', 'new', 'duplicate', 'clone'], line=l + MARK_PLUS, area=a)
icon('copy-x', FI, ['copy', 'remove', 'cancel', 'duplicate', 'clone'], line=l + MARK_X, area=a)
icon('copy-slash', FI, ['copy', 'disabled', 'off', 'duplicate', 'clone'], line=CP['line'] + [SLASH])

# ======================================================================= File family (base: file)
FILEP = 'M56 32 H152 L200 80 V224 H56 Z'
FOLD = P('M152 32 V80 H200')


def file(name, tags, **kw):
    icon(name, FI, tags, line=[P(FILEP)] + kw.pop('line', []), area=[P(FILEP)] + kw.pop('area', []),
         detail=[FOLD] + kw.pop('detail', []), **kw)


def file_open(c=K, rc=56):
    ry = c[1] - math.sqrt(rc * rc - (200 - c[0]) ** 2)
    bx = c[0] - math.sqrt(rc * rc - (224 - c[1]) ** 2)
    d = f'M{f(bx)} 224 H56 V32 H152 L200 80 V{f(ry)}'
    return [P(d)], [P(d + ' ' + arc_to(c, rc, (200, ry), (bx, 224), UL) + ' Z')]


# ---- lettering for type labels (stroke centrelines, as batch 105)
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


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h)]


def g_P(x, t, w, h):
    r = h * 0.29
    return [P(f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 2 * r)} H{f(x)}')]


def g_B(x, t, w, h):
    r1 = h * 0.23
    r2 = h / 2 - r1
    m = t + 2 * r1
    return [P(f'M{f(x)} {f(m)} H{f(x + w - r2 - 2)} A{f(r2)} {f(r2)} 0 0 1 {f(x + w - r2 - 2)} {f(t + h)} H{f(x)} V{f(t)} '
              f'H{f(x + w - r1 - 6)} A{f(r1)} {f(r1)} 0 0 1 {f(x + w - r1 - 6)} {f(m)}')]


def g_M(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w / 2, t + h * 0.62), (x + w, t), (x + w, t + h)])]


def g_S(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x + w)} {f(t)} H{f(x + r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(t + 2 * r)} H{f(x + w - r)} '
              f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + h)} H{f(x)}')]


def g_V(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h), (x + w, t)])]


GLYPH = {'A': g_A, 'B': g_B, 'C': g_C, 'I': g_I, 'M': g_M, 'P': g_P, 'S': g_S, 'V': g_V}
WIDTH = {'A': 44, 'B': 38, 'C': 36, 'I': 0, 'M': 48, 'P': 36, 'S': 38, 'V': 44}


def label(s, cy=188, h=56):
    gap = 28 if len(s) <= 2 else 20
    ws = [WIDTH[ch] for ch in s]
    x = 128 - (sum(ws) + gap * (len(s) - 1)) / 2
    out = []
    for ch, w in zip(s, ws):
        out += GLYPH[ch](x, cy - h / 2, w, h)
        x += w + gap
    return out


FILE_TOP = 'M56 120 V32 H152 L200 80 V120'


def file_type(name, tags, s):
    icon(name, FI, tags, line=[P(FILE_TOP)] + label(s), detail=[FOLD], area=[P(FILE_TOP + ' Z')])


file_type('file-aac', ['aac', 'audio', 'file type', 'extension'], 'AAC')
file_type('file-ai', ['ai', 'vector', 'file type', 'extension', 'ai file'], 'AI')
file_type('file-bmp', ['bmp', 'image', 'file type', 'extension', 'file bmp'], 'BMP')
file_type('file-cs', ['cs', 'csharp', 'code', 'file type'], 'CS')
file_type('file-css', ['css', 'stylesheet', 'code', 'file type', 'code file'], 'CSS')
file_type('file-csv', ['csv', 'data', 'spreadsheet', 'file type', 'data file'], 'CSV')
file_type('file-cv', ['file cv', 'document', 'page', 'file', 'cv'], 'CV')

# ---- inner details
cube = regular_polygon((128, 154), 44, 6)
file('file-3d', ['file 3d', 'document', 'page', 'file', '3d'],
     detail=[PG(cube), PL([cube[5], (128, 154), cube[1]]), L(128, 154, *cube[3])])

file('file-arrow-down', ['file download', 'document', 'save', 'arrow', 'download file'],
     detail=[L(128, 112, 128, 188), PL([(100, 160), (128, 188), (156, 160)])])
file('file-arrow-up', ['file upload', 'document', 'import', 'arrow', 'upload file'],
     detail=[L(128, 116, 128, 192), PL([(100, 144), (128, 116), (156, 144)])])
file('file-arrow-right', ['file arrow right', 'document', 'page', 'file', 'arrow'],
     detail=[L(88, 152, 168, 152), PL([(140, 124), (168, 152), (140, 180)])])
file('file-arrow-left', ['recall', 'withdraw', 'return file', 'document', 'file arrow left'],
     detail=[L(88, 152, 168, 152), PL([(116, 124), (88, 152), (116, 180)])])

ca, ra = (128, 152), 40
arrows = []
for a0, a1 in ((155, 285), (335, 465)):
    s, e = polar(ca, ra, a0), polar(ca, ra, a1)
    arrows.append(P(f'M{pt(s)} A{ra} {ra} 0 0 1 {pt(e)}'))
    t = math.radians(a1)
    arrows.append(head(e, (-math.sin(t), math.cos(t)), 15))
file('file-arrows', ['convert', 'file', 'transform', 'format'], detail=arrows)

file('file-barcode', ['file barcode', 'document', 'page', 'file', 'barcode'],
     detail=[L(92, 120, 92, 188), L(128, 120, 128, 188), L(164, 120, 164, 188)])

file('file-binary', ['binary', 'data', 'document', 'code'],
     detail=[R(84, 124, 36, 56, 18), PL([(144, 136), (164, 124), (164, 180)])])

l, a = file_open()
B_MARK = [P('M166 158 H186 A13 13 0 0 1 186 184 H166'), P('M166 184 H188 A13 13 0 0 1 188 210 H166'),
          L(166, 158, 166, 210), L(178, 146, 178, 158), L(178, 210, 178, 222)]
icon('file-bitcoin', FI, ['file', 'crypto', 'bitcoin', 'document', 'page'], line=l + B_MARK, area=a, detail=[FOLD])
D_MARK = [P('M200 160 H180 A12 12 0 0 0 180 184 H188 A12 12 0 0 1 188 208 H168'), L(184, 146, 184, 160), L(184, 208, 184, 222)]
icon('file-currency-dollar', FI, ['file', 'money', 'price', 'document', 'page'], line=l + D_MARK, area=a, detail=[FOLD])
l2, a2 = file_open(rc=62)
ec = (190, 184)
E_MARK = [P(f'M{pt(polar(ec, 34, -50))} A34 34 0 1 0 {pt(polar(ec, 34, 50))}'), L(150, 170, 186, 170), L(150, 198, 186, 198)]
icon('file-currency-euro', FI, ['file currency euro', 'document', 'page', 'file', 'currency'], line=l2 + E_MARK, area=a2,
     detail=[FOLD])

file('file-bookmark', ['document', 'saved', 'bookmark', 'file', 'bookmarked'],
     detail=[P('M88 32 V108 L106 94 L124 108 V32')])

icon('file-break', FI, ['page break', 'document', 'split', 'file'],
     line=[P('M56 100 V32 H152 L200 80 V100'), P('M56 172 V224 H200 V172'),
           L(32, 136, 56, 136), L(104, 136, 152, 136), L(200, 136, 224, 136)],
     detail=[FOLD], area=[P('M56 100 V32 H152 L200 80 V100 Z'), P('M56 172 V224 H200 V172 Z')])

file('file-broken', ['corrupted', 'damaged', 'file', 'broken', 'file broken'],
     detail=[PL([(56, 140), (92, 120), (116, 156), (152, 128), (176, 160), (200, 144)])])

file('file-calendar', ['schedule document', 'calendar file', 'agenda', 'ics'],
     detail=[R(88, 124, 80, 68, 10), L(88, 152, 168, 152), L(108, 112, 108, 132), L(148, 112, 148, 132)])

seal = (128, 136)
sx = math.sqrt(28 * 28 - 16 * 16)
file('file-certificate', ['file certificate', 'document', 'page', 'file', 'certificate'],
     detail=[C(*seal, 28), P(f'M112 {f(seal[1] + sx)} V196 L128 184 L144 196 V{f(seal[1] + sx)}')])

file('file-chart', ['report', 'document', 'chart', 'graph', 'file chart'],
     detail=[L(96, 188, 96, 156), L(128, 188, 128, 120), L(160, 188, 160, 140)])

file('file-check', ['document', 'approved', 'done', 'check', 'approved file'],
     detail=[PL([(92, 152), (116, 176), (164, 128)])])

CK = (180, 180)
l3, a3 = file_open(CK, 74)
icon('file-clock', FI, ['history', 'recent', 'file', 'version', 'time'],
     line=l3 + [C(*CK, 44)], area=a3 + [C(*CK, 44)], detail=[FOLD, PL([(180, 158), (180, 180), (196, 190)])])

# cloud: three lobes on a flat base
lc1, lr1 = (102, 166), 18
lc2, lr2 = (128, 146), 30
lc3, lr3 = (154, 164), 20
base = 184
p12 = circle_x(lc1, lr1, lc2, lr2)[0]
p23 = circle_x(lc2, lr2, lc3, lr3)[0]
cloud = (f'M{f(lc1[0])} {base} H{f(lc3[0])} ' + arc_to(lc3, lr3, (lc3[0], base), p23, lambda m: m[0])
         + ' ' + arc_to(lc2, lr2, p23, p12, lambda m: -m[1]) + ' ' + arc_to(lc1, lr1, p12, (lc1[0], base), lambda m: -m[0]) + ' Z')
file('file-cloud', ['cloud file', 'synced', 'document', 'online'], detail=[P(cloud)])

file('file-contract', ['contract', 'agreement', 'signature', 'document'],
     detail=[L(88, 112, 168, 112), L(88, 144, 136, 144),
             P('M88 196 C96 166 106 162 110 182 C114 200 122 200 130 178 C134 168 140 170 142 186 H168')])

# file-dashed: file outline broken into even dashes, corners kept
def dashed(points, dash, gap, start):
    segs, cur = [], []
    total = sum(dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    period = dash + gap
    def on(s):
        return ((s - start) % period) < dash
    step = 0.5
    s = 0.0
    pos = []
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        d = dist(a, b)
        n = max(1, int(d / step))
        for k in range(n):
            pos.append((s + d * k / n, (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n), k == 0))
        s += d
    pos.append((s, points[-1], True))
    for sv, p, corner in pos:
        if on(sv):
            if not cur or corner:
                cur.append(p)
            last = p
        else:
            if cur:
                cur.append(last)
                segs.append(cur)
                cur = []
    if cur:
        cur.append(pos[-1][1])
        segs.append(cur)
    out = []
    for sg in segs:
        clean = [sg[0]]
        for p in sg[1:]:
            if dist(p, clean[-1]) > 0.01:
                clean.append(p)
        out.append(clean)
    return out, total


pts = [(56, 128), (56, 32), (152, 32), (200, 80), (200, 224), (56, 224), (56, 128)]
segs, tot = dashed(pts, 40, 36, 0)
file_dash = [PL([(round(x, 2), round(y, 2)) for x, y in sg]) for sg in segs if len(sg) > 1]
icon('file-dashed', FI, ['draft file', 'placeholder', 'new file', 'focus', 'selection'], line=file_dash)

print(save(overwrite=True))
