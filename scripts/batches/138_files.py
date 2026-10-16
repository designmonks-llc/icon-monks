import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Files'
SLASH = L(48, 48, 208, 208)

# ---------------------------------------------------------------- base geometry (from file.svg / folder.svg)
FL = load('file')
FILE_D = 'M56 32 H152 L200 80 V224 H56 Z'
FILE_PTS = [(56, 32), (152, 32), (200, 80), (200, 224), (56, 224)]
FOLD = P('M152 32 V80 H200')
FD = load('folder')
FOLDER = FD['line']; FOLDER_A = FD['area']
FT = load('file-text')
FILES = load('files')
FLOP = load('floppy-disk')


# ---------------------------------------------------------------- helpers
def simplify(pts):
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) > 1e-3:
            out.append(b)
    out.append(pts[-1])
    return out


def gapped(pts, closed=False, g=30, step=0.5):
    """Split a polyline where it passes within g of the slash centreline (x = y, 48..208)."""
    pts = list(pts) + ([pts[0]] if closed else [])
    dense = []
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(dist(a, b) / step))
        dense += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(k)]
    dense.append(pts[-1])

    def near(q):
        # distance to the slash segment (48,48)-(208,208)
        t = max(48, min(208, (q[0] + q[1]) / 2))
        return dist(q, (t, t)) < g
    runs, cur = [], []
    for q in dense:
        if not near(q):
            cur.append(q)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    if closed and len(runs) > 1 and runs[0][0] == dense[0] and runs[-1][-1] == dense[-1]:
        runs[0] = runs.pop() + runs[0]
    return [PL(simplify(r)) for r in runs if dist(r[0], r[-1]) > 6 or len(r) > 40]


BADGE = (184, 184)


def badge_cut(points, B=BADGE, R=76):
    """Open outline of a closed polygon with the part near B removed, plus the area with a concave notch."""
    n = len(points)
    inside = lambda p: dist(p, B) < R
    hits = []
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        fx, fy = a[0] - B[0], a[1] - B[1]
        A = dx * dx + dy * dy; Bq = 2 * (fx * dx + fy * dy); Cq = fx * fx + fy * fy - R * R
        disc = Bq * Bq - 4 * A * Cq
        if disc <= 0:
            continue
        for t in sorted(((-Bq - math.sqrt(disc)) / (2 * A), (-Bq + math.sqrt(disc)) / (2 * A))):
            if 0 <= t <= 1:
                p = (a[0] + dx * t, a[1] + dy * t)
                q = (a[0] + dx * min(t + 1e-3, 1), a[1] + dy * min(t + 1e-3, 1))
                hits.append((i, t, p, inside(q)))
    enter = [h for h in hits if h[3]][0]
    leave = [h for h in hits if not h[3]][0]
    pts = [leave[2]]
    i = leave[0]
    while True:
        i = (i + 1) % n
        if i == (enter[0] + 1) % n:
            break
        pts.append(points[i])
    pts.append(enter[2])
    open_d = poly(pts)
    area_d = open_d + ' ' + arc_to(B, R, enter[2], leave[2], lambda m: -dist(m, (56, 32))) + ' Z'
    return open_d, area_d


def hline_cut(x1, y, x2, B=BADGE, R=76):
    dy = abs(y - B[1])
    if dy < R:
        x2 = min(x2, B[0] - math.sqrt(R * R - dy * dy))
    return L(x1, y, x2, y)


def badge_file(name, tags, mark_line=(), mark_detail=(), mark_area=(), mark_dotcut=(), text=False, R=76):
    o, a = badge_cut(FILE_PTS, R=R)
    det = [FOLD]
    if text:
        det += [hline_cut(88, 128, 168, R=R), hline_cut(88, 160, 168, R=R), hline_cut(88, 192, 136, R=R)]
    icon(name, CAT, tags, line=[P(o)] + list(mark_line), detail=det + list(mark_detail),
         area=[P(a)] + list(mark_area), dotcut=list(mark_dotcut))


def sparkle_d(c, s):
    cx, cy = c
    k1, k2 = s / 12, s / 3
    return (f'M{f(cx)} {f(cy - s)} C{f(cx + k1)} {f(cy - k2)} {f(cx + k2)} {f(cy - k1)} {f(cx + s)} {f(cy)} '
            f'C{f(cx + k2)} {f(cy + k1)} {f(cx + k1)} {f(cy + k2)} {f(cx)} {f(cy + s)} '
            f'C{f(cx - k1)} {f(cy + k2)} {f(cx - k2)} {f(cy + k1)} {f(cx - s)} {f(cy)} '
            f'C{f(cx - k2)} {f(cy - k1)} {f(cx - k1)} {f(cy - k2)} {f(cx)} {f(cy - s)} Z')


def head(tip, deg, arm=28):
    """Arrowhead polyline (two arms at 45 degrees) pointing along deg."""
    return PL([polar(tip, arm * math.sqrt(2), deg + 135), tip, polar(tip, arm * math.sqrt(2), deg - 135)])


# ---------------------------------------------------------------- glyphs for labelled file types
def g_A(x, t, w, h):
    yb = t + h * 0.66
    k = (t + h - yb) / h * w / 2
    return [PL([(x, t + h), (x + w / 2, t), (x + w, t + h)]), L(x + k, yb, x + w - k, yb)]


def g_B(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x)} {f(t + h / 2)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + h)} H{f(x)} V{f(t)} '
              f'H{f(x + w - r - 4)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r - 4)} {f(t + h / 2)}')]


def g_R(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 2 * r)} H{f(x)}'),
            L(x + w - r - 2, t + h / 2, x + w, t + h)]


def g_S(x, t, w, h):
    r = h / 4
    return [P(f'M{f(x + w)} {f(t)} H{f(x + r)} A{f(r)} {f(r)} 0 0 0 {f(x + r)} {f(t + 2 * r)} H{f(x + w - r)} '
              f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(t + 4 * r)} H{f(x)}')]


def g_H(x, t, w, h):
    return [L(x, t, x, t + h), L(x + w, t, x + w, t + h), L(x, t + h / 2, x + w, t + h / 2)]


def g_O(x, t, w, h):
    return [R(x, t, w, h, w / 2)]


def g_Q(x, t, w, h):
    return [R(x, t, w, h, w / 2), L(x + w * 0.62, t + h * 0.74, x + w + 4, t + h + 6)]


def g_L(x, t, w, h):
    return [PL([(x, t), (x, t + h), (x + w, t + h)])]


def g_V(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h), (x + w, t)])]


def g_G(x, t, w, h):
    r = w / 2
    return [P(f'M{f(x + w)} {f(t + r)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} '
              f'A{f(r)} {f(r)} 0 0 0 {f(x + w)} {f(t + h - r)} V{f(t + h / 2 + 4)} H{f(x + w / 2 + 2)}')]


def g_T(x, t, w, h):
    return [L(x, t, x + w, t), L(x + w / 2, t, x + w / 2, t + h)]


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h)]


def g_F(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w, t)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_X(x, t, w, h):
    return [L(x, t, x + w, t + h), L(x + w, t, x, t + h)]


def g_M(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w / 2, t + h * 0.6), (x + w, t), (x + w, t + h)])]


def g_Y(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h * 0.5), (x + w, t)]), L(x + w / 2, t + h * 0.5, x + w / 2, t + h)]


def g_W(x, t, w, h):
    return [PL([(x, t), (x + w * 0.25, t + h), (x + w / 2, t + h * 0.34), (x + w * 0.75, t + h), (x + w, t)])]


GLYPH = {'A': g_A, 'B': g_B, 'R': g_R, 'S': g_S, 'H': g_H, 'O': g_O, 'Q': g_Q, 'L': g_L, 'V': g_V, 'G': g_G,
         'T': g_T, 'I': g_I, 'F': g_F, 'X': g_X, 'M': g_M, 'Y': g_Y, 'W': g_W}
WIDTH = {'A': 44, 'B': 36, 'R': 38, 'S': 36, 'H': 38, 'O': 38, 'Q': 40, 'L': 32, 'V': 42, 'G': 38, 'T': 40,
         'I': 0, 'F': 34, 'X': 40, 'M': 48, 'Y': 42, 'W': 60}


def label(s, t=152, h=64, run=192):
    gap = 22
    ws = [WIDTH[c] for c in s]
    if sum(ws) + gap * (len(s) - 1) > run:
        gap = 18
        k = (run - gap * (len(s) - 1)) / sum(ws)
        ws = [w * k for w in ws]
    x = 128 - (sum(ws) + gap * (len(s) - 1)) / 2
    out = []
    for c, w in zip(s, ws):
        out += GLYPH[c](x, t, w, h)
        x += w + gap
    return out


DOC_TOP = 'M56 112 V32 H152 L200 80 V112'


def labelled(name, tags, s):
    icon(name, CAT, tags, line=[P(DOC_TOP)] + label(s), detail=[FOLD], area=[P(DOC_TOP + ' Z')])


# ================================================================ labelled file types
labelled('file-raw', ['raw', 'photo', 'camera', 'file type'], 'RAW')
labelled('file-rb', ['rb', 'ruby', 'code', 'file type'], 'RB')
labelled('file-rs', ['rust', 'rs', 'source', 'code'], 'RS')
labelled('file-sass', ['sass', 'scss', 'stylesheet', 'file type'], 'SASS')
labelled('file-sh', ['sh', 'shell', 'script', 'file type'], 'SH')
labelled('file-sql', ['sql', 'database', 'query', 'file type', 'query file'], 'SQL')
labelled('file-svg', ['svg', 'vector', 'graphic', 'file type', 'image file'], 'SVG')
labelled('file-tiff', ['tiff', 'image', 'print', 'file type'], 'TIFF')
labelled('file-ts', ['typescript', 'ts', 'script', 'code'], 'TS')
labelled('file-tsx', ['tsx', 'code', 'component', 'file type', 'typescript'], 'TSX')
labelled('file-ttf', ['ttf', 'font', 'typeface', 'file type'], 'TTF')
labelled('file-txt', ['txt', 'text', 'plain', 'file type', 'text file'], 'TXT')
labelled('file-wav', ['wav', 'audio', 'sound', 'file type'], 'WAV')
labelled('file-woff', ['woff', 'web font', 'typeface', 'file type'], 'WOFF')
labelled('file-xls', ['xls', 'excel', 'spreadsheet', 'file type', 'excel file'], 'XLS')
labelled('file-xml', ['xml', 'markup', 'data', 'file type', 'code'], 'XML')
labelled('file-yml', ['yml', 'yaml', 'config', 'file type'], 'YML')


# ================================================================ documents with an interior mark
def doc(name, tags, detail=(), dotcut=(), hole=()):
    icon(name, CAT, tags, line=FL['line'], detail=FL['detail'] + list(detail), area=FL['area'],
         dotcut=list(dotcut), hole=list(hole))


REPORT = [L(96, 192, 96, 160), L(128, 192, 128, 136), L(160, 192, 160, 112)]
doc('file-report', ['file report', 'document', 'page', 'file', 'report'], REPORT)

# rss: dot plus two quarter arcs
rc = (88, 192)
doc('file-rss', ['file rss', 'document', 'page', 'file', 'rss'],
    [P(f'M88 148 A44 44 0 0 1 132 192'), P(f'M88 112 A80 80 0 0 1 168 192')], dotcut=[C(94, 186, 14)])

# signal: dot with two concentric arcs above
sc = (128, 188)
sig = []
for r in (34, 66):
    a, b = polar(sc, r, -135), polar(sc, r, -45)
    sig.append(P(f'M{pt(a)} A{r} {r} 0 0 1 {pt(b)}'))
doc('file-signal', ['file signal', 'document', 'page', 'file', 'signal'], sig, dotcut=[C(128, 188, 14)])

# scissors
ring_l, ring_r, rr = (100, 184), (156, 184), 16
def blade(ring, tip):
    d = dist(ring, tip); u = ((tip[0] - ring[0]) / d, (tip[1] - ring[1]) / d)
    return L(ring[0] + u[0] * rr, ring[1] + u[1] * rr, tip[0], tip[1])
doc('file-scissors', ['file scissors', 'document', 'page', 'file', 'scissors'],
    [C(*ring_l, rr), C(*ring_r, rr), blade(ring_l, (164, 108)), blade(ring_r, (92, 108))])

# share: three nodes
n1, n2, n3 = (96, 152), (160, 120), (160, 184)
def link(a, b, ra=20, rb=20):
    d = dist(a, b); u = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    return L(a[0] + u[0] * ra, a[1] + u[1] * ra, b[0] - u[0] * rb, b[1] - u[1] * rb)
doc('file-share', ['share', 'document', 'send', 'file'], [link(n1, n2), link(n1, n3)],
    dotcut=[C(*n1, 16), C(*n2, 16), C(*n3, 16)])

# slides: easel screen
doc('file-slides', ['presentation file', 'slides', 'deck', 'document'],
    [R(84, 112, 88, 56, 8), L(112, 168, 100, 196), L(144, 168, 156, 196)])

# spreadsheet: table grid
doc('file-spreadsheet', ['spreadsheet', 'table', 'grid', 'document', 'xls'],
    [R(84, 112, 88, 84, 8), L(84, 154, 172, 154), L(120, 112, 120, 196)])

# star
STAR = regular_polygon((128, 154), 44, 5)
inner = regular_polygon((128, 154), 20, 5, -90 + 36)
star_pts = [p for pair in zip(STAR, inner) for p in pair]
doc('file-star', ['starred file', 'favorite document', 'important', 'favorite file', 'starred'], [PG(star_pts)])

# symlink: bent arrow
doc('file-symlink', ['file symlink', 'document', 'page', 'file', 'symlink'],
    [P('M92 196 V172 A36 36 0 0 1 128 136 H164'), head((164, 136), 0, 26)])

# transfer: two opposing arrows
doc('file-transfer', ['send file', 'transfer', 'exchange', 'file'],
    [L(88, 124, 164, 124), head((164, 124), 0, 18), L(168, 180, 92, 180), head((92, 180), 180, 18)])

# user
doc('file-user', ['contact page', 'profile', 'resume', 'file', 'user file'],
    [C(128, 128, 20), P('M88 196 C88 172 104 164 128 164 C152 164 168 172 168 196')])

# vector: bezier curve with nodes and a handle
doc('file-vector', ['vector file', 'bezier', 'graphic', 'design'],
    [P('M88 196 C90 168 98 150 112 140'), P('M144 140 C158 150 166 168 168 196'), R(118, 118, 20, 20, 4),
     L(104, 128, 96, 128), L(152, 128, 160, 128)],
    dotcut=[C(90, 128, 12), C(166, 128, 12)])

# warning / x
doc('file-warning', ['document', 'error', 'alert', 'exclamation', 'file warning'], [L(128, 116, 128, 152)],
    dotcut=[C(128, 188, 14)])
doc('file-x', ['document', 'delete', 'error', 'x', 'missing file'], [L(104, 128, 152, 176), L(152, 128, 104, 176)])

# thumbs
THUMB = [(84, 144), (104, 144), (122, 106), (140, 108), (136, 140), (164, 140), (172, 152), (164, 192), (84, 192)]
def thumb_path(flip=False):
    tf = (lambda p: (p[0], 302 - p[1])) if flip else (lambda p: p)
    q = [tf(p) for p in THUMB]
    return [P(rpath(q, [0, 6, 10, 8, 0, 8, 6, 6, 0])), L(*tf((106, 152)), *tf((106, 184)))]


def rpath(points, rs):
    n = len(points)
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        if rs[i] == 0:
            segs.append((p1, None)); continue
        a = (p0[0] - p1[0], p0[1] - p1[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        tt = rs[i] / math.tan(ang / 2)
        s_ = (p1[0] + a[0] * tt, p1[1] + a[1] * tt); e_ = (p1[0] + b[0] * tt, p1[1] + b[1] * tt)
        cross = a[0] * b[1] - a[1] * b[0]
        segs.append((s_, f'A{f(rs[i])} {f(rs[i])} 0 0 {0 if cross > 0 else 1} {pt(e_)}'))
    d = ''
    for i, (p, arc) in enumerate(segs):
        d += ('M' if i == 0 else ' L') + pt(p)
        if arc:
            d += ' ' + arc
    return d + ' Z'


doc('file-thumbs-up', ['file thumbs', 'increase', 'upload', 'document', 'page'], thumb_path())
doc('file-thumbs-down', ['file thumbs', 'decrease', 'download', 'document', 'page'], thumb_path(True))

# ================================================================ badge variants (lower right)
bx, by = BADGE
FACE = C(bx, by, 40)
badge_file('file-smile', ['file', 'happy', 'positive', 'document', 'page'], mark_line=[FACE], mark_area=[FACE],
           mark_detail=[P(f'M{bx - 16} {by + 10} A20 20 0 0 0 {bx + 16} {by + 10}')],
           mark_dotcut=[C(bx - 14, by - 12, 10), C(bx + 14, by - 12, 10)])
badge_file('file-sad', ['file', 'unhappy', 'negative', 'document', 'page'], mark_line=[FACE], mark_area=[FACE],
           mark_detail=[P(f'M{bx - 16} {by + 20} A20 20 0 0 1 {bx + 16} {by + 20}')],
           mark_dotcut=[C(bx - 13, by - 10, 9), C(bx + 13, by - 10, 9)])
SPK = P(sparkle_d(BADGE, 40))
badge_file('file-sparkle', ['file', 'ai', 'magic', 'document', 'page'], mark_line=[SPK], mark_area=[SPK], R=68)
badge_file('file-text-sparkle', ['file text', 'ai', 'magic', 'document', 'page'], mark_line=[SPK], mark_area=[SPK],
           text=True, R=68)
shield_pts = 'M128 32 L208 64 V120 C208 176 168 208 128 224 C88 208 48 176 48 120 V64 Z'
sk, scx, scy = 0.42, bx, by - 2
def sm(x, y):
    return f'{f(scx + (x - 128) * sk)} {f(scy + (y - 128) * sk)}'
SHIELD_S = P(f'M{sm(128, 32)} L{sm(208, 64)} L{sm(208, 120)} C{sm(208, 176)} {sm(168, 208)} {sm(128, 224)} '
             f'C{sm(88, 208)} {sm(48, 176)} {sm(48, 120)} L{sm(48, 64)} Z')
badge_file('file-text-shield', ['file text', 'secure', 'protected', 'document', 'page'], mark_line=[SHIELD_S],
           mark_area=[SHIELD_S], text=True)

# ================================================================ scan / shredder
SC_DOC = 'M84 64 H140 L172 96 V192 H84 Z'
brk = []
for (cx, cy), (sx, sy) in (((32, 32), (1, 1)), ((224, 32), (-1, 1)), ((224, 224), (-1, -1)), ((32, 224), (1, -1))):
    sweep = 1 if sx * sy > 0 else 0
    brk.append(P(f'M{cx} {cy + sy * 44} V{cy + sy * 14} A14 14 0 0 {sweep} {cx + sx * 14} {cy} H{cx + sx * 44}'))
icon('file-scan', CAT, ['scan document', 'scanner', 'file', 'capture'],
     line=[P(SC_DOC)] + brk, detail=[P('M140 64 V96 H172')], area=[P(SC_DOC)])

icon('file-shredder', CAT, ['file shredder', 'document', 'page', 'file', 'shredder'],
     line=[P('M56 104 V32 H152 L200 80 V104'), L(32, 136, 224, 136)]
     + [L(x, 168, x, y) for x, y in ((74, 212), (110, 224), (146, 200), (182, 220))],
     detail=[FOLD], area=[P('M56 136 V32 H152 L200 80 V136 Z')])

# ================================================================ slash variants (no area so the slash reads in fill)
slashed = gapped(FILE_PTS, closed=True)
icon('file-slash', CAT, ['file off', 'missing', 'no file', 'slash'], line=slashed + [FOLD, SLASH])
rep_g = []
for x, y0, y1 in ((96, 192, 160), (128, 192, 136), (160, 192, 112)):
    rep_g += gapped([(x, y0), (x, y1)])
icon('file-report-slash', CAT, ['file report', 'off', 'disabled', 'hidden', 'file'],
     line=slashed + [FOLD, SLASH] + rep_g)
fr = [(80, 72), (160, 72), (200, 112), (200, 224), (80, 224)]
icon('files-slash', CAT, ['files', 'off', 'disabled', 'hidden'],
     line=gapped(fr, closed=True) + gapped([(48, 192), (48, 32), (136, 32)]) + [P('M160 72 V112 H200'), SLASH])

# ================================================================ filing cabinet
CAB = R(48, 32, 160, 192, 16)
icon('filing-cabinet', CAT, ['cabinet', 'drawers', 'archive', 'storage', 'filing'],
     line=[CAB], detail=[L(48, 96, 208, 96), L(48, 160, 208, 160), L(108, 64, 148, 64), L(108, 128, 148, 128),
                         L(108, 192, 148, 192)], area=[CAB])

# ================================================================ floppy disk with arrow badge
FB = (184, 184)
fl_out = 'M224 100 V80 L176 32 H48 A16 16 0 0 0 32 48 V208 A16 16 0 0 0 48 224 H120'
fl_area = fl_out + ' ' + arc_to(FB, 76, (120, 224), (224, 100), lambda m: -dist(m, (32, 32))) + ' Z'
fl_det = [P('M80 32 V72 H152 V32'), P('M72 224 V152 A8 8 0 0 1 80 144 H116')]
icon('floppy-disk-arrow-down', CAT, ['save', 'store', 'write'],
     line=[P(fl_out), L(184, 140, 184, 216), head((184, 216), 90, 28)], detail=fl_det, area=[P(fl_area)])
icon('floppy-disk-arrow-up', CAT, ['load', 'open', 'read'],
     line=[P(fl_out), L(184, 216, 184, 140), head((184, 140), -90, 28)], detail=fl_det, area=[P(fl_area)])

# ================================================================ folder variants (interior marks, as folder-plus)
def fold(name, tags, detail):
    icon(name, CAT, tags, line=FOLDER, detail=detail, area=FOLDER_A)


fold('folder-arrow-down', ['received', 'downloads', 'folder', 'incoming', 'download folder'],
     [L(128, 112, 128, 176), head((128, 176), 90, 26)])
fold('folder-arrow-up', ['upload folder', 'directory', 'arrow up', 'send'],
     [L(128, 176, 128, 112), head((128, 112), -90, 26)])
fold('folder-arrow-left', ['folder', 'return', 'recall', 'move back'],
     [L(164, 144, 96, 144), head((96, 144), 180, 26)])
ac, ar = (128, 144), 40
arw = []
for a0, a1 in ((200, 320), (20, 140)):
    p, q = polar(ac, ar, a0), polar(ac, ar, a1)
    arw.append(P(f'M{pt(p)} A{ar} {ar} 0 0 1 {pt(q)}'))
    arw.append(head(q, a1 + 90 - 14, 20))
fold('folder-arrows', ['sync folder', 'convert', 'folder', 'transfer'], arw)
fold('folder-chart', ['reports', 'analytics', 'folder', 'chart'],
     [L(96, 176, 96, 152), L(128, 176, 128, 116), L(160, 176, 160, 136)])
fold('folder-check', ['folder done', 'approved', 'verified', 'folder', 'done'], [PL([(100, 144), (120, 164), (158, 126)])])

print(save(overwrite=True))
