import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Editor'
SLASH = L(48, 48, 208, 208)
BADGE = (184, 184)
SG = 32  # clear distance (centerline) kept between the slash and the outline it crosses


# ---------------------------------------------------------------- outline segments & trimming
# segments: ('L', p, q) or ('A', c, r, a0, a1) with angles in radians (increasing = clockwise on screen)
def seg_pt(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    a = s[3] + (s[4] - s[3]) * t
    return (s[1][0] + s[2] * math.cos(a), s[1][1] + s[2] * math.sin(a))


def seg_len(s):
    return dist(s[1], s[2]) if s[0] == 'L' else abs(s[4] - s[3]) * s[2]


def sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', seg_pt(s, t0), seg_pt(s, t1))
    return ('A', s[1], s[2], s[3] + (s[4] - s[3]) * t0, s[3] + (s[4] - s[3]) * t1)


def trim(segs, keep, closed=True):
    """Runs (lists of segments) of an outline where keep(point) holds."""
    runs, cur = [], []
    for s in segs:
        n = max(16, int(seg_len(s) * 2))
        ts = [i / n for i in range(n + 1)]
        ok = [keep(seg_pt(s, t)) for t in ts]
        i = 0
        while i <= n:
            if ok[i]:
                j = i
                while j < n and ok[j + 1]:
                    j += 1
                if j > i:
                    cur.append(sub(s, ts[i], ts[j]))
                if j < n:
                    runs.append(cur); cur = []
                i = j + 1
            else:
                if cur:
                    runs.append(cur); cur = []
                i += 1
    if cur:
        runs.append(cur)
    runs = [r for r in runs if r]
    if closed and len(runs) > 1 and dist(seg_pt(runs[-1][-1], 1), seg_pt(runs[0][0], 0)) < 1e-6:
        runs[0] = runs.pop() + runs[0]
    return runs


def segs_d(run, close=False):
    d = 'M' + pt(seg_pt(run[0], 0))
    for s in run:
        e = seg_pt(s, 1)
        if s[0] == 'L':
            d += ' L' + pt(e)
        else:
            span = s[4] - s[3]
            d += f' A{f(s[2])} {f(s[2])} 0 {1 if abs(span) > math.pi else 0} {1 if span > 0 else 0} {pt(e)}'
    return d + (' Z' if close else '')


def run_len(run):
    return sum(seg_len(s) for s in run)


def rrect_segs(x, y, w, h, r):
    A = lambda c, a0, a1: ('A', c, r, math.radians(a0), math.radians(a1))
    return [('L', (x + r, y), (x + w - r, y)), A((x + w - r, y + r), -90, 0),
            ('L', (x + w, y + r), (x + w, y + h - r)), A((x + w - r, y + h - r), 0, 90),
            ('L', (x + w - r, y + h), (x + r, y + h)), A((x + r, y + h - r), 90, 180),
            ('L', (x, y + h - r), (x, y + r)), A((x + r, y + r), 180, 270)]


def poly_segs(points, closed=True):
    pts = list(points) + ([points[0]] if closed else [])
    return [('L', pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def circle_segs(c, r, start=-90):
    return [('A', c, r, math.radians(start), math.radians(start + 360))]


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(segs, closed=True, sg=SG, a=(48, 48), b=(208, 208), min_len=16):
    runs = trim(segs, lambda p: seg_dist(p, a, b) >= sg, closed)
    if len(runs) == 1 and closed and abs(run_len(runs[0]) - sum(seg_len(s) for s in segs)) < 1e-6:
        return [P(segs_d(runs[0], True))]
    return [P(segs_d(r)) for r in runs if run_len(r) >= min_len]


def badge_clear(segs, closed=True, c=BADGE, r=52, min_len=16):
    runs = trim(segs, lambda p: dist(p, c) >= r, closed)
    return [P(segs_d(x)) for x in runs if run_len(x) >= min_len]


def badge_area(segs, c=BADGE, r=52):
    """Closed silhouette with a concave notch around the badge."""
    runs = trim(segs, lambda p: dist(p, c) >= r, True)
    assert len(runs) == 1
    run = runs[0]
    s, e = seg_point0(run), seg_pt(run[-1], 1)
    cen = (128, 128)
    return P(segs_d(run) + ' ' + arc_to(c, r, e, s, lambda m: -dist(m, cen)) + ' Z')


def seg_point0(run):
    return seg_pt(run[0], 0)


def mark(kind, c=BADGE, a=26):
    x, y = c
    if kind == 'plus':
        return [L(x, y - a, x, y + a), L(x - a, y, x + a, y)]
    return [L(x - a, y, x + a, y)]


def rpoly(points, r, close=True):
    """Polygon path with rounded corners; r is a number or per-vertex list (0 = sharp)."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    segs = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        if (not close and (i == 0 or i == n - 1)) or rs[i] == 0:
            segs.append((p1, None))
            continue
        a = (p0[0] - p1[0], p0[1] - p1[1]); b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a = (a[0] / la, a[1] / la); b = (b[0] / lb, b[1] / lb)
        ang = math.acos(max(-1, min(1, a[0] * b[0] + a[1] * b[1])))
        t = rs[i] / math.tan(ang / 2)
        s = (p1[0] + a[0] * t, p1[1] + a[1] * t); e = (p1[0] + b[0] * t, p1[1] + b[1] * t)
        cross = a[0] * b[1] - a[1] * b[0]
        segs.append((s, f'A{f(rs[i])} {f(rs[i])} 0 0 {0 if cross > 0 else 1} {pt(e)}'))
    d = ''
    for i, (p, arc) in enumerate(segs):
        d += ('M' if i == 0 else ' L') + pt(p)
        if arc:
            d += ' ' + arc
    return d + (' Z' if close else '')


def head(tip, deg, arm=28, spread=45):
    """Open arrowhead at tip; deg is the direction the arrow points."""
    return PL([polar(tip, arm, deg + 180 - spread), tip, polar(tip, arm, deg + 180 + spread)])


def arrow(a, b, arm=28):
    deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return [L(a[0], a[1], b[0], b[1]), head(b, deg, arm)]


def T90(points):
    """Rotate points a quarter turn clockwise around the centre."""
    return rot(points, 90)


# ---------------------------------------------------------------- borders (dot grid 40..216, step 44)
G = (40, 84, 128, 172, 216)
DR = 14  # same dot size as border-dotted
ring = [(x, 40) for x in G] + [(x, 216) for x in G] + [(40, y) for y in G[1:-1]] + [(216, y) for y in G[1:-1]]


def dots(points):
    return [C(x, y, DR) for x, y in points]


def without(points, drop):
    return [p for p in points if p not in drop]


icon('border-right', CAT, ['border right', 'table', 'cell', 'edge'],
     line=[L(216, 40, 216, 216)], dot=dots([p for p in ring if p[0] != 216]))
icon('border-top', CAT, ['border top', 'table', 'cell', 'edge'],
     line=[L(40, 40, 216, 40)], dot=dots([p for p in ring if p[1] != 40]))
icon('border-sides', CAT, ['border sides', 'border', 'table', 'stroke', 'sides'],
     line=[L(40, 40, 40, 216), L(216, 40, 216, 216)], dot=dots([(x, y) for x, y in ring if x not in (40, 216)]))
icon('border-vertical', CAT, ['border', 'table', 'inner', 'vertical', 'cells'],
     line=[L(128, 40, 128, 216)], dot=dots(without(ring, [(128, 40), (128, 216)]) + [(84, 128), (172, 128)]))


def near_badge(p, r=56):
    return dist(p, BADGE) < r


icon('border-right-plus', CAT, ['border right', 'add', 'new', 'border', 'table'],
     line=[L(216, 40, 216, 120)] + mark('plus'),
     dot=dots([p for p in ring if p[0] != 216 and not near_badge(p)]))
icon('border-top-plus', CAT, ['border top', 'add', 'new', 'border', 'table'],
     line=[L(40, 40, 216, 40)] + mark('plus'),
     dot=dots([p for p in ring if p[1] != 40 and not near_badge(p)]))

# border-style: solid, long dashes, short dashes, dots
BS = (48, 101, 155, 208)
icon('border-style', CAT, ['border style', 'dashed', 'line style', 'stroke'],
     line=[L(40, BS[0], 216, BS[0]),
           L(40, BS[1], 104, BS[1]), L(152, BS[1], 216, BS[1]),
           L(40, BS[2], 72, BS[2]), L(112, BS[2], 144, BS[2]), L(184, BS[2], 216, BS[2])],
     dot=[C(x, BS[3], 16) for x in G])

# border-width: hairline, medium bar, heavy bar
bw_mid = R(40, 100, 176, 8, 4)
bw_big = R(40, 152, 176, 56, 28)
icon('border-width', CAT, ['stroke width', 'line weight', 'thickness', 'border'],
     line=[L(40, 56, 216, 56), bw_mid, bw_big], area=[bw_mid, bw_big])

# ---------------------------------------------------------------- box align: solid box in a dotted frame
def box_align(name, tags, x, y, w, h):
    box = R(x, y, w, h, 14)
    inside = lambda p: x - 1 <= p[0] <= x + w + 1 and y - 1 <= p[1] <= y + h + 1
    icon(name, CAT, tags, line=[box], area=[box], dot=dots([p for p in ring if not inside(p)]))


box_align('box-align-bottom', ['box align bottom', 'align', 'box', 'layout', 'bottom'], 40, 128, 176, 88)
box_align('box-align-top', ['box align top', 'align', 'box', 'layout', 'top'], 40, 40, 176, 88)
box_align('box-align-left', ['box align left', 'align', 'box', 'layout', 'left'], 40, 40, 88, 176)
box_align('box-align-right', ['box align right', 'align', 'box', 'layout', 'right'], 128, 40, 88, 176)
box_align('box-align-bottom-left', ['align', 'box', 'layout', 'bottom', 'left'], 40, 128, 88, 88)
box_align('box-align-bottom-right', ['align', 'box', 'layout', 'bottom', 'right'], 128, 128, 88, 88)
box_align('box-align-top-left', ['align', 'box', 'layout', 'top', 'left'], 40, 40, 88, 88)
box_align('box-align-top-right', ['align', 'box', 'layout', 'top', 'right'], 128, 40, 88, 88)

# ---------------------------------------------------------------- box model
BM_OUT = (32, 32, 192, 192, 16)
BM_IN = (88, 88, 80, 80, 10)
bm_diag = [((88, 88), (60, 60)), ((168, 88), (196, 60)), ((168, 168), (196, 196)), ((88, 168), (60, 196))]
icon('box-model', CAT, ['box model', 'box', 'model', 'editor'],
     line=[R(*BM_OUT)], detail=[R(*BM_IN)] + [L(*a, *b) for a, b in bm_diag], area=[R(*BM_OUT)])
icon('box-model-slash', CAT, ['box model', 'disabled', 'off', 'editor'],
     line=[R(*BM_OUT)] + gapped(rrect_segs(*BM_IN), sg=28)
          + [L(*a, *b) for a, b in (bm_diag[1], bm_diag[3])] + [SLASH])

# ---------------------------------------------------------------- cells merge / split
CELL_H = (32, 48, 192, 160)  # x, y, w, h  (side-by-side cells)


def cells_h(kind):
    x, y, w, h = CELL_H
    box = R(x, y, w, h, 14)
    if kind == 'merge':
        det = [L(128, 48, 128, 88), L(128, 168, 128, 208)] + arrow((60, 128), (108, 128)) + arrow((196, 128), (148, 128))
    else:
        det = [L(128, 48, 128, 208)] + arrow((100, 128), (60, 128)) + arrow((156, 128), (196, 128))
    return box, det


def rot_el(el):
    """Rotate a simple L/PL path element a quarter turn (parse the M/L points)."""
    import re
    nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', el)]
    pts = T90(list(zip(nums[::2], nums[1::2])))
    return PL(pts)


for kind, tags_h, tags_v in (
        ('merge', ['merge cells', 'table', 'combine', 'horizontal'], ['merge cells', 'table', 'combine', 'vertical']),
        ('split', ['split cells', 'table', 'divide', 'horizontal'], ['split cells', 'table', 'divide', 'vertical'])):
    box, det = cells_h(kind)
    x, y, w, h = CELL_H
    vbox = R(128 - h / 2, 128 - w / 2, h, w, 14)
    if kind == 'merge':
        icon('cells-merge-horizontal', CAT, tags_h, line=[box], detail=det, area=[box])
        icon('cells-merge-vertical', CAT, tags_v, line=[vbox], detail=[rot_el(d) for d in det], area=[vbox])
    else:
        icon('cells-split-horizontal', CAT, tags_h, line=[box], detail=det, area=[box])
        icon('cells-split-vertical', CAT, tags_v, line=[vbox], detail=[rot_el(d) for d in det], area=[vbox])

# cells-merge: a table whose header keeps two cells while the body row merges
TB = R(32, 40, 192, 176, 14)
icon('cells-merge', CAT, ['merge cells', 'table', 'combine', 'spreadsheet'],
     line=[TB], area=[TB],
     detail=[L(32, 96, 224, 96), L(128, 40, 128, 96)] + arrow((60, 156), (108, 156)) + arrow((196, 156), (148, 156)))

# ---------------------------------------------------------------- text formatting
icon('clear-formatting', CAT, ['clear formatting', 'remove style', 'text', 'remove format', 'eraser'],
     line=[PL([(48, 72), (48, 48), (176, 48), (176, 72)]), L(112, 48, 112, 208),
           L(164, 164, 204, 204), L(204, 164, 164, 204)])

# ---------------------------------------------------------------- columns
COL = (120, 40, 104, 176, 14)
icon('column-insert-left', CAT, ['column insert left', 'column', 'table', 'grid', 'insert'],
     line=[R(*COL), L(64, 104, 64, 152), L(40, 128, 88, 128)], detail=[L(172, 40, 172, 216)], area=[R(*COL)])
COLR = (32, 40, 104, 176, 14)
icon('column-insert-right', CAT, ['column insert right', 'column', 'table', 'grid', 'insert'],
     line=[R(*COLR), L(192, 104, 192, 152), L(168, 128, 216, 128)], detail=[L(84, 40, 84, 216)], area=[R(*COLR)])

TBL = rrect_segs(32, 40, 192, 176, 14)
icon('column-minus', CAT, ['column', 'remove', 'subtract', 'table', 'grid'],
     line=badge_clear(TBL) + mark('minus', a=24),
     detail=[L(96, 40, 96, 216)] + badge_clear([('L', (160, 40), (160, 216))], closed=False, r=56),
     area=[badge_area(TBL)])

cols = load('columns')
icon('columns-slash', CAT, ['columns', 'disabled', 'off', 'editor'],
     line=gapped(rrect_segs(40, 40, 72, 176, 12)) + gapped(rrect_segs(144, 40, 72, 176, 12)) + [SLASH])

CURSOR = [(48, 40), (208, 112), (136, 136), (112, 208)]
icon('cursor-slash', CAT, ['cursor', 'disabled', 'off', 'editor'],
     line=gapped(poly_segs(CURSOR), a=(192, 32), b=(32, 192)) + [L(192, 32, 32, 192)])

# ---------------------------------------------------------------- decimals
def zero(x, y, w, h):
    return R(x, y, w, h, w / 2)


icon('decimal', CAT, ['decimal', 'number format', 'point'],
     line=[zero(40, 56, 48, 144), zero(168, 56, 48, 144)], dot=[C(128, 188, 16)])
icon('decimal-decrease', CAT, ['decimal', 'fewer decimals', 'number format', 'spreadsheet'],
     line=[zero(132, 40, 48, 96)] + arrow((200, 192), (56, 192), 24), dot=[C(92, 124, 16)])
icon('decimal-increase', CAT, ['decimal', 'more decimals', 'number format', 'spreadsheet'],
     line=[zero(84, 40, 48, 96), zero(168, 40, 48, 96)] + arrow((56, 192), (200, 192), 24), dot=[C(44, 124, 16)])

# ---------------------------------------------------------------- eraser slash
er = load('eraser')
ER = [(34.66, 159.11), (159.11, 34.66), (221.34, 96.89), (96.89, 221.34)]
icon('eraser-slash', CAT, ['eraser', 'disabled', 'off', 'editor'],
     line=gapped(poly_segs(ER)) + gapped([('L', (120, 216), (216, 216))], closed=False) + [SLASH])

# ---------------------------------------------------------------- find & replace
LC, LR = (112, 112), 72
AR = 34


def swap_arrows(c=LC, r=AR, arm=18):
    out = []
    for a0, a1 in ((205, 335), (25, 155)):
        p0, p1 = polar(c, r, a0), polar(c, r, a1)
        out.append(P(f'M{pt(p0)} A{r} {r} 0 0 1 {pt(p1)}'))
        tang = a1 + 90  # direction of travel (clockwise) at the end
        out.append(head(p1, tang, arm))
    return out


SWAP_SEGS = [[('A', LC, AR, math.radians(205), math.radians(335))], [('A', LC, AR, math.radians(25), math.radians(155))]]
icon('find-replace', CAT, ['find', 'replace', 'search', 'substitute'],
     line=[C(*LC, LR), L(163, 163, 216, 216)], detail=swap_arrows(), area=[C(*LC, LR)])
icon('find-replace-slash', CAT, ['find replace', 'off', 'disabled', 'hidden', 'find'],
     line=gapped(circle_segs(LC, LR, 45), a=(208, 48), b=(48, 208)) + [L(163, 163, 216, 216), L(208, 48, 48, 208)]
          + [P(f'M{pt(polar(LC, AR, 150))} A{AR} {AR} 0 0 1 {pt(polar(LC, AR, 295))}'),
             head(polar(LC, AR, 295), 295 + 90, 18)])

# ---------------------------------------------------------------- folding
icon('fold', CAT, ['fold', 'collapse', 'code folding', 'compress'],
     line=[L(40, 128, 216, 128)] + arrow((128, 32), (128, 88)) + arrow((128, 224), (128, 168)))
icon('fold-up', CAT, ['fold up', 'collapse', 'arrow', 'line'],
     line=[L(40, 48, 216, 48)] + arrow((128, 216), (128, 96), 40))
icon('fold-down', CAT, ['fold down', 'collapse', 'arrow', 'line'],
     line=[L(40, 208, 216, 208)] + arrow((128, 40), (128, 160), 40))

# ---------------------------------------------------------------- freeze panes
WIN = R(32, 48, 192, 160, 14)
icon('freeze-row', CAT, ['freeze row', 'spreadsheet', 'pin row', 'table'],
     line=[WIN], area=[WIN],
     detail=[R(32, 92, 192, 8, 4), L(32, 152, 224, 152), L(96, 100, 96, 208), L(160, 100, 160, 208)])
icon('freeze-row-column', CAT, ['freeze panes', 'spreadsheet', 'table', 'pin'],
     line=[WIN], area=[WIN],
     detail=[R(32, 92, 192, 8, 4), R(92, 48, 8, 160, 4), L(100, 152, 224, 152), L(160, 100, 160, 208)])

# ---------------------------------------------------------------- highlighter
HL_LOCAL = [(-34, -96), (34, -96), (34, 8), (22, 36), (22, 52), (-22, 72), (-22, 36), (-34, 8)]
HL_C = (128, 124)


def hl_pts(points):
    return [(x + HL_C[0], y + HL_C[1]) for x, y in rot(points, 45, (0, 0))]


HL = hl_pts(HL_LOCAL)
HL_D = rpoly(HL, [12, 12, 4, 4, 4, 4, 4, 4])
HL_BAND = hl_pts([(-34, -36), (34, -36)])
icon('highlighter', CAT, ['marker', 'highlight', 'mark', 'pen', 'emphasis'],
     line=[P(HL_D), L(128, 216, 216, 216)], detail=[L(*HL_BAND[0], *HL_BAND[1])], area=[P(HL_D)])
icon('highlighter-slash', CAT, ['highlighter', 'off', 'disabled', 'hidden'],
     line=gapped(poly_segs(HL)) + gapped([('L', (128, 216), (216, 216))], closed=False) + [SLASH])

# ---------------------------------------------------------------- ink bottle
INK = [(104, 72), (152, 72), (152, 96), (208, 124), (208, 216), (48, 216), (48, 124), (104, 96)]
INK_D = rpoly(INK, [0, 0, 8, 14, 16, 16, 14, 8])
CAP = R(88, 32, 80, 40, 10)
dc, dr = (128, 176), 18
dtip = (128, 138)
drop = (f'M{pt(dtip)} L{pt(polar(dc, dr, -30))} ' + arc_to(dc, dr, polar(dc, dr, -30), polar(dc, dr, 210),
                                                          lambda m: m[1]) + ' Z')
icon('ink-bottle', CAT, ['ink', 'fountain pen', 'write', 'calligraphy'],
     line=[CAP, P(INK_D)], detail=[P(drop)], area=[CAP, P(INK_D)])

# ---------------------------------------------------------------- modifier keys
icon('key-control', CAT, ['control key', 'ctrl', 'modifier', 'keyboard', 'caret'],
     line=[PL([(40, 168), (128, 80), (216, 168)])])
icon('key-option', CAT, ['option key', 'alt', 'modifier', 'keyboard', 'mac'],
     line=[PL([(40, 64), (96, 64), (160, 192), (216, 192)]), L(152, 64, 216, 64)])
icon('key-return', CAT, ['enter', 'return', 'newline'],
     line=[P('M208 56 V136 A16 16 0 0 1 192 152 H56'), head((56, 152), 180, 48)])

# ---------------------------------------------------------------- typography spacing
icon('letter-spacing', CAT, ['letter spacing', 'tracking', 'kerning', 'text', 'typography'],
     line=[PL([(40, 128), (76, 40), (112, 128)]), L(52, 100, 100, 100), PL([(144, 40), (180, 128), (216, 40)]),
           L(48, 192, 208, 192), head((48, 192), 180, 34), head((208, 192), 0, 34)])
icon('line-height', CAT, ['line height', 'spacing', 'leading', 'typography', 'paragraph'],
     line=[L(64, 48, 64, 208), head((64, 48), -90, 34), head((64, 208), 90, 34),
           L(128, 64, 216, 64), L(128, 128, 216, 128), L(128, 192, 216, 192)])

# ---------------------------------------------------------------- lists
icon('list-arrow', CAT, ['move item', 'list', 'reorder', 'arrow'],
     line=[L(40, 64, 128, 64), L(40, 128, 128, 128), L(40, 192, 128, 192)] + arrow((192, 48), (192, 200), 36))
icon('list-collapse', CAT, ['collapse', 'fold', 'outline', 'list', 'less'],
     line=[L(144, 64, 216, 64), L(144, 128, 216, 128), L(144, 192, 216, 192), PL([(40, 146), (76, 110), (112, 146)])])
icon('list-expand', CAT, ['expand', 'unfold', 'outline', 'list', 'more'],
     line=[L(144, 64, 216, 64), L(144, 128, 216, 128), L(144, 192, 216, 192), PL([(40, 110), (76, 146), (112, 110)])])
th1, th2 = R(40, 40, 64, 64, 12), R(40, 152, 64, 64, 12)
icon('list-details', CAT, ['detail list', 'items', 'description', 'rows'],
     line=[th1, th2, L(136, 56, 216, 56), L(136, 88, 184, 88), L(136, 168, 216, 168), L(136, 200, 184, 200)],
     area=[th1, th2])

print(save(overwrite=True))
