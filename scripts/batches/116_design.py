import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from draw import *

# ================================================================ small outline engine
# Segments: ('L', p0, p1) | ('C', p0, c1, c2, p1) | ('A', centre, r, a0, a1)  (angles in radians, a1 may be < a0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    if s[0] == 'C':
        p0, c1, c2, p1 = s[1:]
        a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
        d, e = lerp(a, b, t), lerp(b, c, t)
        return lerp(d, e, t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def split_cubic(p0, c1, c2, p1, t):
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p1)


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    if s[0] == 'C':
        _, right = split_cubic(*s[1:], t0)
        if t1 >= 1:
            return ('C',) + right
        left, _ = split_cubic(*right, (t1 - t0) / (1 - t0))
        return ('C',) + left
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []  # (seg index, t0, t1)
    for i, s in enumerate(segs):
        ts = [k / steps for k in range(steps + 1)]
        ok = [keep(seg_point(s, t)) for t in ts]

        def edge(ta, tb, oa):
            for _ in range(40):
                tm = (ta + tb) / 2
                if keep(seg_point(s, tm)) == oa:
                    ta = tm
                else:
                    tb = tm
            return (ta + tb) / 2
        start = 0.0 if ok[0] else None
        for k in range(1, len(ts)):
            if ok[k] != ok[k - 1]:
                e = edge(ts[k - 1], ts[k], ok[k - 1])
                if ok[k]:
                    start = e
                else:
                    pieces.append((i, start, e))
                    start = None
        if start is not None:
            pieces.append((i, start, 1.0))
    if len(pieces) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in pieces):
        return [segs], True
    runs = []
    for i, t0, t1 in pieces:
        sub = seg_sub(segs[i], t0, t1)
        if runs and t0 == 0 and runs[-1][1] == (i - 1, 1.0):
            runs[-1][0].append(sub)
        else:
            runs.append([[sub], None])
        runs[-1][1] = (i, t1)
    if closed and len(runs) > 1 and pieces[0][1] == 0 and pieces[0][0] == 0 and pieces[-1][2] == 1.0 \
            and pieces[-1][0] == len(segs) - 1:
        last = runs.pop()
        runs[0][0] = last[0] + runs[0][0]
    return [r[0] for r in runs], False


def sample(segs, n=60):
    return [seg_point(s, k / n) for s in segs for k in range(n)]


def inside(poly_pts, p):
    x, y = p
    c = False
    for i in range(len(poly_pts)):
        x1, y1 = poly_pts[i]
        x2, y2 = poly_pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def carve(segs, cut_c, cut_r):
    """Open the closed outline segs around a circular badge. Returns (line d, area d)."""
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r)
    assert not whole and len(runs) == 1, (whole, len(runs))
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    poly_pts = sample(segs)
    arc = arc_to(cut_c, cut_r, e, s, lambda m: 1 if inside(poly_pts, m) else 0)
    return segs_d(run), segs_d(run) + ' ' + arc + ' Z'


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])




# ================================================================ batch 116: design
DS, CM, UI = 'Design', 'Communication', 'Interface'
SLASH = L(48, 48, 208, 208)


def rpath(points, r, closed=False):
    """Polyline with corners rounded to radius r."""
    n = len(points)

    def corner(i):
        a, p, b = points[i - 1], points[i], points[(i + 1) % n]
        v1 = (a[0] - p[0], a[1] - p[1]); v2 = (b[0] - p[0], b[1] - p[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1); u2 = (v2[0] / l2, v2[1] / l2)
        phi = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        d = min(r / math.tan(phi / 2), l1 / 2, l2 / 2)
        rr = d * math.tan(phi / 2)
        s = (p[0] + u1[0] * d, p[1] + u1[1] * d); e = (p[0] + u2[0] * d, p[1] + u2[1] * d)
        cross = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
        return s, f'A{f(rr)} {f(rr)} 0 0 {1 if cross > 0 else 0} {pt(e)}', e

    if closed:
        cs = [corner(i) for i in range(n)]
        d = f'M{pt(cs[0][2])}'
        for s, a, e in cs[1:] + cs[:1]:
            d += f' L{pt(s)} {a}'
        return P(d + ' Z')
    d = f'M{pt(points[0])}'
    for i in range(1, n - 1):
        s, a, e = corner(i)
        d += f' L{pt(s)} {a}'
    return P(d + f' L{pt(points[-1])}')


def seg_len_table(segs, steps=200):
    tab = []  # (cumulative length, seg index, t)
    s = 0.0
    for i, sg in enumerate(segs):
        prev = seg_point(sg, 0)
        if not tab:
            tab.append((0.0, i, 0.0))
        for k in range(1, steps + 1):
            q = seg_point(sg, k / steps)
            s += dist(prev, q); prev = q
            tab.append((s, i, k / steps))
    return tab


def locate(tab, s):
    for k in range(1, len(tab)):
        if tab[k][0] >= s:
            s0, i0, t0 = tab[k - 1]; s1, i1, t1 = tab[k]
            if i0 != i1:
                t0 = 0.0
            u = (s - s0) / (s1 - s0) if s1 > s0 else 0
            return i1, t0 + (t1 - t0) * u
    return tab[-1][1], 1.0


def dashes(segs, n, ratio, offset=0.0):
    """n dashes of length ratio*period along the closed outline segs."""
    tab = seg_len_table(segs)
    total = tab[-1][0]
    per = total / n
    out = []
    for k in range(n):
        a = (offset + k * per) % total
        b = a + per * ratio
        pieces = []
        for lo, hi in ([(a, b)] if b <= total else [(a, total), (0, b - total)]):
            i0, t0 = locate(tab, lo); i1, t1 = locate(tab, hi)
            if i0 == i1:
                pieces.append(seg_sub(segs[i0], t0, t1))
            else:
                pieces.append(seg_sub(segs[i0], t0, 1))
                pieces += [segs[j] for j in range(i0 + 1, i1)]
                pieces.append(seg_sub(segs[i1], 0, t1))
        out.append(P(segs_d(pieces)))
    return out


def closed_spline(pts):
    n = len(pts)
    segs = []
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append(('C', p1, c1, c2, p2))
    return segs


# ---------------------------------------------------------------- communication
HEAD = ('M60 216 V188 C42 172 32 150 32 122 C32 76 62 44 100 44 C130 44 144 66 144 92 L144 106 L156 132 '
        'L144 136 V156 C144 166 138 172 128 172 H112 V216')
VC = (144, 128)
icon('voice', CM, ['voice', 'speak', 'speaking', 'audio'],
     line=[P(HEAD)] + [P(f'M{pt(polar(VC, r, -40))} A{r} {r} 0 0 1 {pt(polar(VC, r, 40))}') for r in (44, 80)],
     area=[P(HEAD + ' Z')])

icon('voice-recognition', CM, ['voice recognition', 'speech', 'scan', 'voice'],
     line=[rpath([(40, 88), (40, 40), (88, 40)], 16), rpath([(168, 40), (216, 40), (216, 88)], 16),
           rpath([(216, 168), (216, 216), (168, 216)], 16), rpath([(88, 216), (40, 216), (40, 168)], 16),
           L(64, 116, 64, 140), L(96, 96, 96, 160), L(128, 76, 128, 180), L(160, 96, 160, 160), L(192, 116, 192, 140)])

# wifi-question: wifi's own arcs, opened around a question mark
WC = (128, 200)
QC, QR = (186, 134), 26
Q_END = polar(QC, QR, 50)
Q_SEGS = [('A', QC, QR, math.pi, math.radians(410)), ('C', Q_END, (188, 164), (186, 168), (186, 180))]
Q_D = segs_d(Q_SEGS)
q_pts = sample(Q_SEGS, 40) + [(186, 212)]
wl = []
for r in (44, 88, 132):
    runs, _ = trim([('A', WC, r, math.radians(225), math.radians(315))],
                   lambda p: min(dist(p, q) for q in q_pts) >= 40, closed=False)
    wl += [P(segs_d(run)) for run in runs]
icon('wifi-question', CM, ['wifi unknown', 'no internet', 'wifi', 'question'],
     line=wl + [P(Q_D)], dot=[C(128, 200, 16), C(186, 212, 14)])

# ---------------------------------------------------------------- align family
def tf(mode, r=None, l=None):
    """Map left-aligned layout coords: id, mx (mirror x), t (transpose), tmy (transpose + mirror y)."""
    if r:
        x, y, w, h = r
        if mode == 'mx':
            x = 256 - x - w
        elif mode in ('t', 'tmy'):
            x, y, w, h = y, x, h, w
            if mode == 'tmy':
                y = 256 - y - h
        return R(x, y, w, h, 12)
    x1, y1, x2, y2 = l
    if mode == 'mx':
        x1, x2 = 256 - x1, 256 - x2
    elif mode in ('t', 'tmy'):
        x1, y1, x2, y2 = y1, x1, y2, x2
        if mode == 'tmy':
            y1, y2 = 256 - y1, 256 - y2
    return L(x1, y1, x2, y2)


def align(name, tags, mode, rects, lines):
    rs = [tf(mode, r=r) for r in rects]
    icon(name, DS, tags, line=[tf(mode, l=l) for l in lines] + rs, area=rs)


EDGE_BARS = [(72, 52, 144, 56), (72, 148, 96, 56)]
EDGE_LINE = [(40, 32, 40, 224)]
EDGE_BOX = [(72, 68, 128, 120)]
align('align-left', ['align', 'left', 'objects', 'start', 'layout'], 'id', EDGE_BARS, EDGE_LINE)
align('align-right', ['align', 'right', 'objects', 'end', 'layout'], 'mx', EDGE_BARS, EDGE_LINE)
align('align-top', ['align', 'top', 'objects', 'layout', 'arrange'], 't', EDGE_BARS, EDGE_LINE)
align('align-bottom', ['align', 'bottom', 'objects', 'layout', 'arrange'], 'tmy', EDGE_BARS, EDGE_LINE)
align('align-left-simple', ['align left', 'layout', 'arrange'], 'id', EDGE_BOX, EDGE_LINE)
align('align-right-simple', ['align right', 'layout', 'arrange'], 'mx', EDGE_BOX, EDGE_LINE)
align('align-top-simple', ['align top', 'layout', 'arrange'], 't', EDGE_BOX, EDGE_LINE)
align('align-bottom-simple', ['align bottom', 'layout', 'arrange'], 'tmy', EDGE_BOX, EDGE_LINE)

MID_BARS = [(48, 52, 160, 56), (80, 148, 96, 56)]
MID_AXIS = [(128, 32, 128, 52), (128, 108, 128, 148), (128, 204, 128, 224)]
MID_BOX = [(56, 72, 144, 112)]
MID_BOX_AXIS = [(128, 32, 128, 72), (128, 184, 128, 224)]
align('align-center-horizontal', ['align', 'center', 'horizontal', 'objects', 'align center'], 'id', MID_BARS, MID_AXIS)
align('align-center-vertical', ['align', 'middle', 'vertical', 'objects', 'align middle'], 't', MID_BARS, MID_AXIS)
align('align-center-horizontal-simple', ['align center', 'layout', 'arrange'], 'id', MID_BOX, MID_BOX_AXIS)
align('align-center-vertical-simple', ['align middle', 'layout', 'arrange'], 't', MID_BOX, MID_BOX_AXIS)

SPACE_LINES = [(40, 40, 40, 216), (216, 40, 216, 216)]
align('align-horizontal-spacing', ['distribute horizontally', 'spacing', 'layout'], 'id', [(88, 64, 80, 128)], SPACE_LINES)
align('align-vertical-spacing', ['distribute vertically', 'spacing', 'layout'], 't', [(88, 64, 80, 128)], SPACE_LINES)
align('align-stretch', ['stretch', 'fill', 'flex', 'layout'], 'id', [(56, 72, 56, 112), (144, 72, 56, 112)],
      [(32, 40, 224, 40), (32, 216, 224, 216)])

grid_dots = [C(x, y, 18) for y in (56, 128, 200) for x in (56, 128, 200) if (x, y) != (56, 56)]
icon('align-grid', DS, ['alignment', 'anchor', 'position', 'grid'],
     line=[C(56, 56, 24)], area=[C(56, 56, 24)], dot=grid_dots)

# ---------------------------------------------------------------- geometry
V = (40, 208)
icon('angle', DS, ['angle', 'geometry', 'degrees', 'measure'],
     line=[PL([polar(V, 192, -56), V, (224, 208)]),
           P(f'M{pt(polar(V, 96, 0))} A96 96 0 0 0 {pt(polar(V, 96, -56))}')])

PC = (128, 172)
PROT = 'M32 172 A96 96 0 0 1 224 172 Z'
icon('angle-tool', DS, ['protractor', 'measure angle', 'geometry'],
     line=[P(PROT)], area=[P(PROT)],
     detail=[P('M92 172 A36 36 0 0 1 164 172')],
     dotcut=[C(*polar(PC, 66, a), 10) for a in (-135, -90, -45)])

AC = [(168, 128), (128, 128), (88, 128)]
icon('animation', DS, ['motion', 'movement', 'tween', 'keyframes'],
     line=[C(168, 128, 56),
           P(f'M{pt(polar(AC[1], 56, 125))} ' + arc_to(AC[1], 56, polar(AC[1], 56, 125), polar(AC[1], 56, 235), lambda m: -m[0])),
           P(f'M{pt(polar(AC[2], 56, 140))} ' + arc_to(AC[2], 56, polar(AC[2], 56, 140), polar(AC[2], 56, 220), lambda m: -m[0]))],
     area=[C(168, 128, 56)])

MARKS = {'tl': [L(72, 32, 72, 48), L(32, 72, 48, 72)], 'tr': [L(184, 32, 184, 48), L(208, 72, 224, 72)],
         'bl': [L(72, 208, 72, 224), L(32, 184, 48, 184)], 'br': [L(184, 208, 184, 224), L(208, 184, 224, 184)]}
ART = R(72, 72, 112, 112, 8)
icon('artboard', DS, ['artboard', 'canvas', 'frame', 'design'],
     line=[ART] + sum(MARKS.values(), []), area=[ART])
icon('artboard-slash', DS, ['artboard', 'disabled', 'off', 'design'],
     line=[ART] + MARKS['tr'] + MARKS['bl'] + [SLASH])

AR = R(32, 56, 192, 144, 16)
AR_BR = [rpath([(160, 88), (192, 88), (192, 120)], 8), rpath([(96, 168), (64, 168), (64, 136)], 8)]
icon('aspect-ratio', DS, ['ratio', 'aspect', 'dimensions', 'crop', 'resize'], line=[AR], detail=AR_BR, area=[AR])
icon('aspect-ratio-slash', DS, ['aspect ratio', 'disabled', 'off', 'design'], line=[AR] + AR_BR + [SLASH])

BG = R(40, 40, 176, 176, 16)
icon('background', DS, ['background', 'layer', 'canvas', 'fill'], line=[BG], area=[BG],
     detail=[L(68, 131, 131, 68), L(68, 188, 188, 68), L(125, 188, 188, 125)])

BZN = R(108, 82, 40, 40, 8)
icon('bezier-curve', DS, ['bezier', 'curve', 'vector', 'path', 'ease curve'],
     line=[P(segs_d(run)) for run in trim([('C', (56, 216), (72, 64), (184, 64), (200, 216))],
                                          lambda p: p[0] < 100 or p[0] > 156 or p[1] > 132, closed=False)[0]]
          + [L(64, 102, 108, 102), L(148, 102, 192, 102), C(48, 102, 16), C(208, 102, 16), BZN],
     area=[BZN])

BN = R(104, 104, 48, 48, 8)
icon('bezier-node', DS, ['anchor point', 'node', 'vector', 'path'],
     line=[BN, L(40, 128, 104, 128), L(152, 128, 216, 128)], area=[BN], dot=[C(40, 128, 16), C(216, 128, 16)])

c1, c2 = (96, 128), (160, 128)
up, dn = circle_x(c1, 64, c2, 64)
LENS = f'M{pt(up)} A64 64 0 0 1 {pt(dn)} A64 64 0 0 1 {pt(up)} Z'
icon('blend-mode', DS, ['blend', 'overlay', 'layers', 'mix'], line=[C(96, 128, 64), C(160, 128, 64)], area=[P(LENS)])

BLOB_PTS = [(116, 40), (178, 50), (214, 100), (192, 146), (208, 194), (150, 218), (80, 204), (40, 150), (62, 84)]
BLOB = closed_spline(BLOB_PTS)
BLOB_D = segs_d(BLOB, True)
icon('blob', DS, ['blob', 'shape', 'organic'], line=[P(BLOB_D)], area=[P(BLOB_D)])
icon('blob-dashed', DS, ['blob', 'shape', 'outline', 'dashed'], line=dashes(BLOB, 10, 0.45))

BP = 'M56 40 H208 A8 8 0 0 1 216 48 V208 A8 8 0 0 1 208 216 H56 A24 24 0 0 1 32 192 V64 A24 24 0 0 1 56 40 Z'
icon('blueprint', DS, ['plan', 'blueprint', 'architecture'], line=[P(BP)], area=[P(BP)],
     detail=[P(f'M{pt(polar((56, 64), 24, -40))} A24 24 0 0 1 80 64 V192 A24 24 0 0 1 {pt(polar((56, 192), 24, 40))}'),
             rpath([(112, 120), (112, 80), (184, 80), (184, 176), (112, 176), (112, 152)], 4)])

BG5 = [40, 84, 128, 172, 216]
BLUR_R = {0: 22, 1: 14, 2: 8}
blur_dots = {}
for j, y in enumerate(BG5):
    for i, x in enumerate(BG5):
        if abs(i - 2) == 2 and abs(j - 2) == 2:
            continue
        blur_dots[(i, j)] = C(x, y, BLUR_R[max(abs(i - 2), abs(j - 2))])
icon('blur', DS, ['blur', 'soften', 'dots', 'photo effect', 'lens blur'], dot=list(blur_dots.values()))
icon('blur-slash', DS, ['blur off', 'sharpen', 'photo effect', 'disable', 'no blur'],
     line=[SLASH], dot=[d for (i, j), d in blur_dots.items() if i != j])

icon('blur-motion', DS, ['motion blur', 'speed', 'movement', 'streak'],
     line=[C(168, 128, 56), L(48, 88, 96, 88), L(32, 128, 80, 128), L(48, 168, 96, 168)], area=[C(168, 128, 56)])

icon('border-dotted', DS, ['dotted', 'border', 'stroke', 'line style'],
     dot=[C(x, y, 14) for y in (40, 84, 128, 172, 216) for x in (40, 84, 128, 172, 216)
          if x in (40, 216) or y in (40, 216)])

BB = [(56, 56), (200, 56), (200, 200), (56, 200)]
icon('bounding-box', DS, ['bounding box', 'selection', 'transform', 'handles'],
     line=[L(76, 56, 180, 56), L(200, 76, 200, 180), L(180, 200, 76, 200), L(56, 180, 56, 76)] + [C(x, y, 20) for x, y in BB],
     area=[R(56, 56, 144, 144)], hole=[C(x, y, 12) for x, y in BB])

FRONT = R(32, 104, 120, 120, 14)
icon('box-multiple', DS, ['box multiple', 'box', 'multiple', 'design'],
     line=[FRONT, rpath([(68, 104), (68, 68), (188, 68), (188, 188), (152, 188)], 14),
           rpath([(104, 68), (104, 32), (224, 32), (224, 152), (188, 152)], 14)], area=[FRONT])

BF = R(88, 88, 128, 128, 14)
icon('bring-forward', DS, ['bring forward', 'layer', 'arrange', 'order', 'layers'],
     line=[rpath([(64, 152), (40, 152), (40, 40), (152, 40), (152, 64)], 12), BF], area=[BF],
     detail=[L(152, 184, 152, 120), PL([(124, 148), (152, 120), (180, 148)])])

BTF = R(76, 76, 104, 104, 12)
icon('bring-to-front', DS, ['arrange', 'layer', 'front', 'order', 'bring forward'],
     line=[rpath([(56, 128), (32, 128), (32, 32), (128, 32), (128, 56)], 12),
           rpath([(200, 128), (224, 128), (224, 224), (128, 224), (128, 200)], 12), BTF], area=[BTF])

CAP = capsule((128, 128), 48, 48, (1, 0))
icon('capsule', DS, ['capsule', 'pill shape', 'shape'], line=[P(CAP)], area=[P(CAP)])

CAT = [R(40, 40, 72, 72, 10), C(180, 76, 36), R(40, 144, 72, 72, 10)]
CAT_BR = R(144, 144, 72, 72, 10)
icon('category', DS, ['category', 'shapes', 'group', 'classify'], line=CAT + [CAT_BR], area=CAT + [CAT_BR])
icon('category-plus', DS, ['category', 'add', 'new', 'shapes', 'group'],
     line=CAT + [L(180, 148, 180, 212), L(148, 180, 212, 180)], area=CAT)
icon('category-minus', DS, ['category', 'remove', 'subtract', 'shapes', 'group'],
     line=CAT + [L(148, 180, 212, 180)], area=CAT)

CHK_FRAME = R(40, 40, 176, 176, 16)
CHK_DARK = [R(40, 40, 88, 88), R(128, 128, 88, 88)]
icon('checkerboard', DS, ['checkerboard', 'transparency', 'pattern', 'chess', 'opacity'],
     line=[CHK_FRAME, L(128, 40, 128, 216), L(40, 128, 216, 128),
           L(40, 100, 100, 40), L(68, 128, 128, 68), L(128, 188, 188, 128), L(156, 216, 216, 156)],
     area=[P('M128 40 V128 H40 V56 A16 16 0 0 1 56 40 Z'), P('M128 216 V128 H216 V200 A16 16 0 0 1 200 216 Z')])

CIRC = [('A', (128, 128), 96, -math.pi / 2, 1.5 * math.pi)]
icon('circle-dashed', DS, ['circle', 'dashed', 'dotted', 'draft', 'dashed circle'],
     line=dashes(CIRC, 10, 0.43, offset=-0.43 * 603.19 / 20))

icon('circle-half', DS, ['contrast', 'adjust', 'half', 'tone', 'half circle'],
     line=[C(128, 128, 96), L(128, 32, 128, 224)], area=[P('M128 32 A96 96 0 0 0 128 224 Z')])

icon('circles-four', DS, ['four circles', 'grid', 'dots'],
     line=[C(x, y, 36) for y in (76, 180) for x in (76, 180)], area=[C(x, y, 36) for y in (76, 180) for x in (76, 180)])

T3 = [(128, 94), (128 - 44 * math.cos(math.radians(30)), 160), (128 + 44 * math.cos(math.radians(30)), 160)]
CEN = (128, 138)
vx = []
for a, b, cc in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
    p1, p2 = circle_x(T3[a], 56, T3[b], 56)
    vx.append(p1 if dist(p1, T3[cc]) < 56 else p2)
# vx[0] on circles 0,1; vx[1] on 1,2; vx[2] on 2,0
near = lambda m: -dist(m, CEN)
TRI = (f'M{pt(vx[0])} ' + arc_to(T3[1], 56, vx[0], vx[1], near) + ' ' + arc_to(T3[2], 56, vx[1], vx[2], near)
       + ' ' + arc_to(T3[0], 56, vx[2], vx[0], near) + ' Z')
icon('circles-three', DS, ['three circles', 'venn', 'group', 'color filter', 'rgb'],
     line=[C(x, y, 56) for x, y in T3], area=[P(TRI)])

C3 = [C(76, 76, 36), C(180, 76, 36), C(76, 180, 36)]
icon('circles-three-plus', UI, ['add group', 'apps', 'more'],
     line=C3 + [L(180, 148, 180, 212), L(148, 180, 212, 180)], area=C3)

CW = (128, 128)
wedges = []
for k in range(0, 6, 2):
    a0, a1 = -90 + 60 * k, -30 + 60 * k
    wedges.append(P(f'M{pt(polar(CW, 32, a0))} L{pt(polar(CW, 96, a0))} A96 96 0 0 1 {pt(polar(CW, 96, a1))} '
                    f'L{pt(polar(CW, 32, a1))} A32 32 0 0 0 {pt(polar(CW, 32, a0))} Z'))
icon('color-wheel', DS, ['hue', 'color picker', 'spectrum'],
     line=[C(128, 128, 96), C(128, 128, 32)] + [L(*polar(CW, 32, -90 + 60 * k), *polar(CW, 96, -90 + 60 * k)) for k in range(6)],
     area=wedges)

print(save(overwrite=True))
