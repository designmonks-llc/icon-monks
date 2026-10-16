import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

DV, ED = 'Devices', 'Editor'


# ---------------------------------------------------------------- trimming helpers
def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy
    t = 0 if l2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def clearance(p, keep):
    """keep: list of ('s', a, b, rad) segments or ('c', c, rad) discs. Returns min distance - rad."""
    m = 1e9
    for k in keep:
        if k[0] == 's':
            m = min(m, seg_dist(p, k[1], k[2]) - k[3])
        else:
            m = min(m, dist(p, k[1]) - k[2])
    return m


def runs(n, ok):
    out, start = [], None
    for i in range(n + 1):
        if ok(i):
            if start is None:
                start = i
        else:
            if start is not None:
                out.append((start, i - 1))
                start = None
    if start is not None:
        out.append((start, n))
    return out


def trim_arc(c, r, a0, a1, keep, step=0.25):
    """Sub-arcs of circle (c,r) from angle a0 to a1 (deg, increasing = clockwise) that clear keep."""
    n = max(1, int(abs(a1 - a0) / step))
    ang = lambda i: a0 + (a1 - a0) * i / n
    res = []
    for s, e in runs(n, lambda i: clearance(polar(c, r, ang(i)), keep) >= 0):
        if e - s < 2:
            continue
        sa, ea = ang(s), ang(e)
        res.append((sa, ea, polar(c, r, sa), polar(c, r, ea)))
    return res


def arc_path(c, r, sa, ea):
    p, q = polar(c, r, sa), polar(c, r, ea)
    span = ea - sa
    if abs(span) >= 359.9:
        return C(c[0], c[1], r)
    return P(f'M{pt(p)} A{f(r)} {f(r)} 0 {1 if abs(span) > 180 else 0} {1 if span > 0 else 0} {pt(q)}')


def trim_seg(a, b, keep, step=0.5):
    n = max(1, int(dist(a, b) / step))
    at = lambda i: (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
    return [(at(s), at(e)) for s, e in runs(n, lambda i: clearance(at(i), keep) >= 0) if e - s >= 2]


def keep_from(mark, gap=20, base=8):
    """Keep-out list from a mark spec: segments [(a,b)], dots [(c,r_render)]."""
    k = []
    for a, b in mark.get('segs', []):
        k.append(('s', a, b, 8 + gap + base))
    for c, rr in mark.get('dots', []):
        k.append(('c', c, rr + gap + base))
    return k


def mark_x(B, s=22):
    x, y = B
    return {'segs': [((x - s, y - s), (x + s, y + s)), ((x + s, y - s), (x - s, y + s))], 'dots': []}


def mark_plus(B, s=26):
    x, y = B
    return {'segs': [((x - s, y), (x + s, y)), ((x, y - s), (x, y + s))], 'dots': []}


def mark_warn(B):
    x, y = B
    return {'segs': [((x, y - 34), (x, y))], 'dots': [((x, y + 30), 12)], 'dotsrc': [C(x, y + 30, 16)]}


def mark_lines(m):
    out = [L(a[0], a[1], b[0], b[1]) for a, b in m['segs']]
    return out


# ---------------------------------------------------------------- watch variants
WC, WR = (128, 128), 64
W_STRAPS = [[(96, 72.57), (104, 32), (152, 32), (160, 72.57)],
            [(96, 183.43), (104, 224), (152, 224), (160, 183.43)]]


def watch_badge(name, tags, mark, extra_line=(), extra_dot=()):
    keep = keep_from(mark)
    line, area = [], []
    arcs = trim_arc(WC, WR, -90, 270, keep)
    # join wrap-around pieces
    if len(arcs) == 2 and abs(arcs[0][0] + 90) < 0.01 and abs(arcs[1][1] - 270) < 0.01:
        arcs = [(arcs[1][0], arcs[0][1] + 360)]
    else:
        arcs = [(a[0], a[1]) for a in arcs]
    for sa, ea in arcs:
        line.append(arc_path(WC, WR, sa, ea))
    # area: case minus badge cut
    if len(arcs) == 1:
        sa, ea = arcs[0]
        p, q = polar(WC, WR, sa), polar(WC, WR, ea)
        B = mark['B']
        rb = (dist(B, p) + dist(B, q)) / 2
        area.append(P(f'M{pt(p)} A{WR} {WR} 0 1 1 {pt(q)} A{f(rb)} {f(rb)} 0 0 0 {pt(p)} Z'))
    for strap in W_STRAPS:
        segs = []
        for a, b in zip(strap, strap[1:]):
            segs += trim_seg(a, b, keep)
        # merge consecutive segments into polylines
        polys = []
        for a, b in segs:
            if polys and dist(polys[-1][-1], a) < 0.6:
                polys[-1].append(b)
            else:
                polys.append([a, b])
        line += [PL(pp) for pp in polys]
    hands = [P('M128 100 L128 128 L148 140')]
    icon(name, DV, tags, line=line + list(extra_line), detail=hands, area=area,
         dot=list(extra_dot))


B = (184, 184)
mx = mark_x(B); mx['B'] = B
watch_badge('watch-x', ['watch', 'remove', 'cancel', 'smartwatch', 'wearable'], mx, extra_line=mark_lines(mx))

Bw = (192, 172)
mw = mark_warn(Bw); mw['B'] = (192, 186)
watch_badge('watch-warning', ['watch', 'warning', 'error', 'smartwatch', 'wearable'], mw,
            extra_line=mark_lines(mw), extra_dot=mw['dotsrc'])

bars = [((160, 216), (160, 196)), ((188, 216), (188, 178)), ((216, 216), (216, 160))]
ms = {'segs': bars, 'dots': [], 'B': (188, 188)}
watch_badge('watch-stats', ['watch', 'statistics', 'activity', 'smartwatch', 'wearable'], ms,
            extra_line=mark_lines(ms))


# ---------------------------------------------------------------- webcam slash
def band_arcs(c, r, g, a0=0, a1=360):
    """Arcs of circle outside a band of half-width g around the slash line y = x."""
    keep = [('s', (0, 0), (256, 256), g)]
    out = trim_arc(c, r, a0, a1, keep)
    return out


def circle_minus_band(c, r, g):
    arcs = band_arcs(c, r, g, -180, 180)
    res = [(a[0], a[1]) for a in arcs]
    if len(res) >= 2 and abs(res[0][0] + 180) < 0.01 and abs(res[-1][1] - 180) < 0.01:
        first = res.pop(0)
        last = res.pop(-1)
        res.append((last[0], first[1] + 360))
    return [arc_path(c, r, sa, ea) for sa, ea in res]


wc_line = circle_minus_band((128, 104), 72, 20) + circle_minus_band((128, 104), 28, 20)
icon('webcam-slash', DV, ['camera off', 'video off', 'privacy', 'webcam', 'disabled'],
     line=wc_line + [L(128, 176, 128, 216), L(72, 216, 168, 216), L(48, 48, 208, 208)])


# ---------------------------------------------------------------- wifi levels (four arcs, empty ones dotted)
WFC = (128, 204)
WF_R = [36, 72, 108, 144]
WF_HALF = 40


def wifi_level(name, tags, n):
    line, dots = [], [C(WFC[0], WFC[1], 16)]
    for i, r in enumerate(WF_R):
        if i < n:
            line.append(arc_path(WFC, r, -90 - WF_HALF, -90 + WF_HALF))
        else:
            # ghost arc: evenly spaced small dots
            length = r * math.radians(2 * WF_HALF)
            k = max(2, int(round(length / 44)) + 1)
            for j in range(k):
                a = -90 - WF_HALF + 2 * WF_HALF * j / (k - 1)
                p = polar(WFC, r, a)
                dots.append(C(p[0], p[1], 7))
    icon(name, DV, tags, line=line, dot=dots)


wifi_level('wifi-high', ['strong wifi', 'signal', 'wireless', 'wifi 3 bars', 'good signal'], 3)
wifi_level('wifi-medium', ['wifi', 'signal', 'wireless', 'weak signal', 'medium'], 2)
wifi_level('wifi-low', ['weak wifi', 'signal', 'wireless', 'weak signal', 'wifi 1 bar'], 1)
wifi_level('wifi-none', ['no wifi', 'disconnected', 'wireless', 'wifi 0 bars', 'no signal'], 0)


# ---------------------------------------------------------------- wifi badges (base wifi geometry)
WB_C, WB_R = (128, 200), [44, 88, 132]


def wifi_badge(name, tags, keep, extra_line=(), extra_dot=(), extra_area=(), extra_dotcut=()):
    line = []
    for r in WB_R:
        for sa, ea, p, q in trim_arc(WB_C, r, -135, -45, keep):
            line.append(arc_path(WB_C, r, sa, ea))
    icon(name, DV, tags, line=line + list(extra_line), dot=[C(128, 200, 16)] + list(extra_dot),
         area=list(extra_area), dotcut=list(extra_dotcut))


m = mark_x((192, 188), 20)
wifi_badge('wifi-x', ['wifi error', 'no connection', 'wifi', 'x', 'wireless'], keep_from(m), extra_line=mark_lines(m))

m = mark_warn((204, 150))
wifi_badge('wifi-warning', ['weak connection', 'network problem', 'wifi alert', 'connection problem', 'wifi'],
           keep_from(m), extra_line=mark_lines(m), extra_dot=m['dotsrc'])

lock_body = R(160, 176, 64, 48, 10)
shackle = 'M176 176 V164 A16 16 0 0 1 208 164 V176'
lk = [('s', (160, 176), (224, 176), 36), ('s', (160, 176), (160, 224), 36), ('s', (176, 176), (176, 164), 36),
      ('s', (208, 176), (208, 164), 36), ('c', (192, 164), 16 + 36)]
wifi_badge('wifi-lock', ['secured network', 'password wifi', 'private', 'secure wifi', 'password'], lk,
           extra_line=[lock_body, P(shackle)], extra_area=[lock_body], extra_dotcut=[C(192, 200, 9)])


# ---------------------------------------------------------------- wireless charging, workstation
phone = R(76, 32, 104, 132, 18)
pad = R(32, 196, 192, 28, 14)
icon('wireless-charging', DV, ['wireless charging', 'qi', 'charge', 'pad'],
     line=[phone, pad], detail=[PL([(140, 64), (112, 102), (144, 102), (116, 140)])], area=[phone, pad])

mon = R(32, 72, 108, 92, 12)
tower = R(168, 40, 56, 176, 14)
icon('workstation', DV, ['workstation', 'pc', 'desktop tower'],
     line=[mon, L(86, 164, 86, 208), L(56, 208, 116, 208), tower],
     detail=[L(188, 80, 204, 80)], dotcut=[C(196, 180, 12)], area=[mon, tower])


# ---------------------------------------------------------------- align box
BOX = R(32, 32, 192, 192, 16)
LENS = [112, 64, 88]
GROUP = {'start': [72, 108, 144], 'mid': [92, 128, 164], 'end': [112, 148, 184], 'stretch': [72, 128, 184]}


def hbars(anchor, group):
    out = []
    for y, l in zip(GROUP[group], LENS):
        if anchor == 'start':
            x0, x1 = 72, 72 + l
        elif anchor == 'end':
            x0, x1 = 184 - l, 184
        else:
            x0, x1 = 128 - l / 2, 128 + l / 2
        out.append(L(x0, y, x1, y))
    return out


def vbars(anchor, group):
    out = []
    for x, l in zip(GROUP[group], LENS):
        if anchor == 'start':
            y0, y1 = 72, 72 + l
        elif anchor == 'end':
            y0, y1 = 184 - l, 184
        else:
            y0, y1 = 128 - l / 2, 128 + l / 2
        out.append(L(x, y0, x, y1))
    return out


GP = {'left': 'start', 'top': 'start', 'center': 'mid', 'middle': 'mid', 'right': 'end', 'bottom': 'end',
      'stretch': 'stretch'}
AL = [('bottom', 'center'), ('bottom', 'left'), ('bottom', 'right'), ('center', 'bottom'), ('center', 'middle'),
      ('center', 'stretch'), ('center', 'top'), ('left', 'bottom'), ('left', 'middle'), ('left', 'stretch'),
      ('left', 'top'), ('right', 'bottom'), ('right', 'middle'), ('right', 'stretch'), ('right', 'top'),
      ('top', 'center'), ('top', 'left'), ('top', 'right')]
for a, b in AL:
    if a in ('top', 'bottom'):
        bars_ = vbars(GP[a], GP[b])
    else:
        bars_ = hbars(GP[a], GP[b])
    icon(f'align-box-{a}-{b}', ED, ['align', 'alignment', 'layout', 'box', a], line=[BOX], detail=bars_, area=[BOX])


# ---------------------------------------------------------------- baseline
A_LINES = [PL([(64, 184), (128, 40), (192, 184)]), L(86, 136, 170, 136)]
icon('baseline', ED, ['baseline', 'typography', 'text', 'line'], line=A_LINES + [L(32, 216, 224, 216)])


def density(name, n):
    ys = [48 + 160 * i / (n - 1) for i in range(n)]
    line = [L(104, y, 216, y) for y in ys]
    line += [L(56, 48, 56, 208), PL([(36, 68), (56, 48), (76, 68)]), PL([(36, 188), (56, 208), (76, 188)])]
    icon(name, ED, [name.replace('-', ' '), 'baseline', 'typography', 'text', 'density'], line=line)


density('baseline-density-large', 3)
density('baseline-density-medium', 4)
density('baseline-density-small', 5)

icon('blockquote', ED, ['quote', 'blockquote', 'text', 'indent', 'citation'],
     line=[L(48, 56, 48, 200), L(96, 56, 216, 56), L(96, 104, 176, 104), L(96, 152, 216, 152), L(96, 200, 152, 200)])


# ---------------------------------------------------------------- borders
G = [40, 84, 128, 172, 216]
EDGES = {
    'top': [(x, 40) for x in G], 'bottom': [(x, 216) for x in G], 'left': [(40, y) for y in G],
    'right': [(216, y) for y in G], 'h': [(x, 128) for x in G], 'v': [(128, y) for y in G]}
EDGE_LINE = {'top': (40, 40, 216, 40), 'bottom': (40, 216, 216, 216), 'left': (40, 40, 40, 216),
             'right': (216, 40, 216, 216), 'h': (40, 128, 216, 128), 'v': (128, 40, 128, 216)}


def border_parts(solid, inner=True):
    pts = []
    for e in ('top', 'bottom', 'left', 'right') + (('h', 'v') if inner else ()):
        for p in EDGES[e]:
            if p not in pts:
                pts.append(p)
    covered = set()
    for e in solid:
        covered |= set(EDGES[e])
    line = [L(*EDGE_LINE[e]) for e in solid]
    dots = [p for p in pts if p not in covered]
    return line, dots


def border(name, tags, solid, keep=(), extra_line=(), trim_lines=False):
    line, dots = border_parts(solid)
    if keep:
        dots = [p for p in dots if clearance(p, keep) >= 4]
        if trim_lines:
            nl = []
            for e in solid:
                x1, y1, x2, y2 = EDGE_LINE[e]
                for a, b in trim_seg((x1, y1), (x2, y2), keep):
                    nl.append(L(a[0], a[1], b[0], b[1]))
            line = nl
    icon(name, ED, tags, line=line + list(extra_line), dot=[C(x, y, 14) for x, y in dots])


icon('border-all', ED, ['borders', 'table', 'grid', 'cells', 'border all'],
     line=[R(40, 40, 176, 176), L(128, 40, 128, 216), L(40, 128, 216, 128)])
border('border-bottom', ['border', 'edge', 'table', 'cell', 'border bottom'], ['bottom'])
border('border-left', ['border left', 'table', 'cell', 'edge'], ['left'])
border('border-horizontal', ['border', 'table', 'inner', 'horizontal', 'cells'], ['h'])
border('border-inner', ['inner border', 'table', 'cells', 'grid', 'border inner'], ['h', 'v'])
border('border-none', ['border', 'clear', 'no border', 'table', 'clear borders'], [])
line_, dots_ = border_parts(['top', 'bottom', 'left', 'right'])
icon('border-outer', ED, ['outer border', 'table', 'frame', 'box', 'border outer'],
     line=[R(40, 40, 176, 176)], dot=[C(x, y, 14) for x, y in dots_])

mp = mark_plus((186, 186), 26)
border('border-bottom-plus', ['border bottom', 'add', 'new', 'border', 'table'], ['bottom'],
       keep=keep_from(mp, gap=18), extra_line=mark_lines(mp), trim_lines=True)
border('border-left-plus', ['border left', 'add', 'new', 'border', 'table'], ['left'],
       keep=keep_from(mp, gap=18), extra_line=mark_lines(mp), trim_lines=True)


# corners: solid top-left corner over 3/4 of each side, dots for the rest of the square
REST = [(216, 40), (216, 84), (216, 128), (216, 172), (216, 216), (172, 216), (128, 216), (84, 216), (40, 216)]
RD = [C(x, y, 14) for x, y in REST]
CT = ['border', 'table', 'stroke', 'corner']
icon('border-corner', ED, ['border corner'] + CT, line=[P('M40 172 V68 A28 28 0 0 1 68 40 H172')], dot=RD)
icon('border-corner-square', ED, ['border corner square'] + CT, line=[PL([(40, 172), (40, 40), (172, 40)])], dot=RD)
icon('border-corner-pill', ED, ['border corner pill'] + CT, line=[P('M40 172 A132 132 0 0 1 172 40')], dot=RD)
icon('border-corner-squircle', ED, ['border corner squircle'] + CT, line=[P('M40 172 C40 64 64 40 172 40')], dot=RD)

cp = 'M40 88 V64 A24 24 0 0 1 64 40 H88'
corners = [P(cp)]
for deg in (90, 180, 270):
    pts = rot([(40, 88), (40, 64), (64, 40), (88, 40)], deg)
    c2 = rot([(64, 64)], deg)[0]
    corners.append(P(f'M{pt(pts[0])} L{pt(pts[1])} A24 24 0 0 1 {pt(pts[2])} L{pt(pts[3])}'))
icon('border-corners', ED, ['border corners', 'border', 'table', 'stroke', 'corners'], line=corners,
     dot=[C(128, 40, 14), C(216, 128, 14), C(128, 216, 14), C(40, 128, 14)])

icon('border-radius', ED, ['border radius', 'border', 'table', 'stroke', 'radius'],
     line=[P('M40 216 V136 A96 96 0 0 1 136 40 H216'), L(136, 136, 96, 96)], dot=[C(136, 136, 18)])

print(save(overwrite=True))
