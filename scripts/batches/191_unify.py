"""Batch 191: unify sibling families that parallel batches drew in different ways.

1. Labelled file types (file-aac ... file-yml): one page cut, one label row and one stroke alphabet.
2. sliders-* badges: the batch-153 layout (top knob right, bottom knob left, badge bottom right) for all.
3. watch-* badges: the batch-129 convention (watch shifted left 32, ring opened around the badge).
4. lock-warning, lock-x: rebuilt like the batch-174 lock badges.
5. sort-numerical-descending: mirror of sort-numerical-ascending (same glyphs, arrow and slots).
6. swipe-* = shared hand + arrow, hand-swipe-* = the same hand + motion trail.

Only the icons listed here are rewritten; each keeps its name, category and tags.
"""
import html
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *  # noqa: F401,F403
from draw import ROOT


def meta(name):
    """(category, tags) of the existing icon, so a rewrite keeps them unchanged."""
    src = open(os.path.join(ROOT, 'icons', name + '.svg')).read()
    cat = html.unescape(re.search(r'data-category="([^"]*)"', src).group(1))
    tags = html.unescape(re.search(r'data-tags="([^"]*)"', src).group(1))
    return cat, [t for t in tags.split(',') if t]


def redo(name, **roles):
    cat, tags = meta(name)
    icon(name, cat, tags, **roles)


# ============================================================================ 1. labelled file types
# Layout: the page keeps its top (fold included) and stops at y=128; the label sits on one row, letters
# 160..224 (h=64), centred on x=128 and never wider than the live area (32..224). Gaps between letters
# are 32 by default, never below 28 (centreline to centreline) so bold strokes keep a clear gap; long labels
# condense their letters toward each glyph's minimum width (every counter stays >= 28 wide too).
LT, LH = 160, 64
LB = LT + LH
PAGE_END = 128
PAGE = f'M56 {PAGE_END} V32 H152 L200 80 V{PAGE_END}'
PAGE_AREA = PAGE + ' Z'
FOLD = P('M152 32 V80 H200')


def g_A(x, t, w, h):
    b = t + h
    yb = t + h * 0.64
    k = (b - yb) / h * w / 2
    return [PL([(x, b), (x + w / 2, t), (x + w, b)]), L(x + k, yb, x + w - k, yb)]


def _bowls(x, t, w, h, stem=True, mid_from=None):
    """B (stem=True) or 3 (stem=False): two right bowls, top 28 tall, bottom 32 tall."""
    b = t + h
    m = t + h * 0.47
    r1, r2 = (m - t) / 2, (b - m) / 2
    rx1, rx2 = min(r1, x + w - 4 - x), min(r2, w)
    x1, x2 = x + w - 4 - rx1, x + w - rx2
    if stem:
        return [P(f'M{f(x)} {f(m)} H{f(x2)} A{f(rx2)} {f(r2)} 0 0 1 {f(x2)} {f(b)} H{f(x)} V{f(t)} '
                  f'H{f(x1)} A{f(rx1)} {f(r1)} 0 0 1 {f(x1)} {f(m)}')]
    xm = x + w * (0.3 if mid_from is None else mid_from)
    return [P(f'M{f(x)} {f(t)} H{f(x1)} A{f(rx1)} {f(r1)} 0 0 1 {f(x1)} {f(m)} H{f(xm)}'),
            P(f'M{f(x1)} {f(m)} H{f(x2)} A{f(rx2)} {f(r2)} 0 0 1 {f(x2)} {f(b)} H{f(x)}')]


def g_B(x, t, w, h):
    return _bowls(x, t, w, h)


def g_3(x, t, w, h):
    return _bowls(x, t, w, h, stem=False)


def g_C(x, t, w, h, end=30):
    r = w / 2
    ct, cb = (x + r, t + r), (x + r, t + h - r)
    s, e = polar(ct, r, -end), polar(cb, r, end)
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 {pt(e)}')]


def g_D(x, t, w, h):
    r = min(w * 0.6, h / 2)
    b = t + h
    return [P(f'M{f(x)} {f(t)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(t + r)} V{f(b - r)} '
              f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(b)} H{f(x)} Z')]


def g_E(x, t, w, h):
    b = t + h
    return [PL([(x + w, t), (x, t), (x, b), (x + w, b)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_F(x, t, w, h):
    return [PL([(x + w, t), (x, t), (x, t + h)]), L(x, t + h / 2, x + w * 0.8, t + h / 2)]


def g_G(x, t, w, h, end=30):
    r = w / 2
    ct = (x + r, t + r)
    s = polar(ct, r, -end)
    yb = t + h * 0.6
    return [P(f'M{pt(s)} A{f(r)} {f(r)} 0 0 0 {f(x)} {f(t + r)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 0 '
              f'{f(x + w)} {f(t + h - r)} V{f(yb)} H{f(x + w * 0.55)}')]


def g_H(x, t, w, h):
    return [L(x, t, x, t + h), L(x + w, t, x + w, t + h), L(x, t + h / 2, x + w, t + h / 2)]


def g_I(x, t, w, h):
    return [L(x + w / 2, t, x + w / 2, t + h)]


def g_J(x, t, w, h):
    r = w / 2
    return [P(f'M{f(x + w)} {f(t)} V{f(t + h - r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(t + h - r)}')]


def g_K(x, t, w, h):
    b = t + h
    a0, a1 = (x + w, t), (x, t + h * 0.62)
    m = (a0[0] + (a1[0] - a0[0]) * 0.5, a0[1] + (a1[1] - a0[1]) * 0.5)
    return [L(x, t, x, b), L(*a0, *a1), L(*m, x + w, b)]


def g_L(x, t, w, h):
    return [PL([(x, t), (x, t + h), (x + w, t + h)])]


def g_M(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w / 2, t + h * 0.6), (x + w, t), (x + w, t + h)])]


def g_N(x, t, w, h):
    return [PL([(x, t + h), (x, t), (x + w, t + h), (x + w, t)])]


def g_O(x, t, w, h):
    return [R(x, t, w, h, w / 2)]


def _bowl_top(x, t, w, h):
    r = h * 0.27
    rx = min(r, w)
    return r, rx, f'M{f(x)} {f(t + h)} V{f(t)} H{f(x + w - rx)} A{f(rx)} {f(r)} 0 0 1 {f(x + w - rx)} {f(t + 2 * r)} H{f(x)}'


def g_P(x, t, w, h):
    return [P(_bowl_top(x, t, w, h)[2])]


def g_Q(x, t, w, h):
    return [R(x, t, w, h, w / 2), L(x + w * 0.55, t + h * 0.72, x + w + 2, t + h)]


def g_R(x, t, w, h):
    r, rx, d = _bowl_top(x, t, w, h)
    return [P(d), L(x + w * 0.45, t + 2 * r, x + w, t + h)]


def g_S(x, t, w, h):
    ry = h / 4
    rx = min(ry, w / 2)
    return [P(f'M{f(x + w)} {f(t)} H{f(x + rx)} A{f(rx)} {f(ry)} 0 0 0 {f(x + rx)} {f(t + 2 * ry)} H{f(x + w - rx)} '
              f'A{f(rx)} {f(ry)} 0 0 1 {f(x + w - rx)} {f(t + h)} H{f(x)}')]


def g_T(x, t, w, h):
    return [L(x, t, x + w, t), L(x + w / 2, t, x + w / 2, t + h)]


def g_V(x, t, w, h):
    return [PL([(x, t), (x + w / 2, t + h), (x + w, t)])]


def g_W(x, t, w, h):
    return [PL([(x, t), (x + w * 0.25, t + h), (x + w / 2, t + h * 0.3), (x + w * 0.75, t + h), (x + w, t)])]


def g_X(x, t, w, h):
    return [L(x, t, x + w, t + h), L(x + w, t, x, t + h)]


def g_Y(x, t, w, h):
    m = (x + w / 2, t + h * 0.5)
    return [PL([(x, t), m, (x + w, t)]), L(*m, m[0], t + h)]


def g_4(x, t, w, h):
    yb = t + h * 0.66
    return [PL([(x + w * 0.42, t), (x, yb), (x + w, yb)]), L(x + w * 0.74, t + h * 0.36, x + w * 0.74, t + h)]


# glyph: (draw, natural width, minimum width)
ALPHABET = {
    'A': (g_A, 44, 30), 'B': (g_B, 36, 28), 'C': (g_C, 36, 28), 'D': (g_D, 38, 28), 'E': (g_E, 32, 24),
    'F': (g_F, 30, 20), 'G': (g_G, 38, 30), 'H': (g_H, 36, 28), 'I': (g_I, 0, 0), 'J': (g_J, 30, 22),
    'K': (g_K, 36, 28), 'L': (g_L, 30, 20), 'M': (g_M, 44, 32), 'N': (g_N, 38, 28), 'O': (g_O, 38, 28),
    'P': (g_P, 34, 26), 'Q': (g_Q, 38, 30), 'R': (g_R, 36, 28), 'S': (g_S, 36, 28), 'T': (g_T, 36, 28),
    'V': (g_V, 42, 30), 'W': (g_W, 56, 44), 'X': (g_X, 38, 30), 'Y': (g_Y, 40, 30),
    '3': (g_3, 34, 28), '4': (g_4, 38, 32),
}
RUN = 192          # label centrelines stay within x 32..224
GAP, GAP_MIN = 32, 28


def _arc_center(p, q, rx, ry, large, sweep):
    """Centre parametrisation of an SVG arc without rotation; returns (cx, cy, rx, ry, a0, span)."""
    x1, y1 = p
    x2, y2 = q
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    lam = (dx / rx) ** 2 + (dy / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = max(rx * rx * ry * ry - rx * rx * dy * dy - ry * ry * dx * dx, 0)
    den = rx * rx * dy * dy + ry * ry * dx * dx
    k = math.sqrt(num / den) if den else 0
    if large == sweep:
        k = -k
    cxp, cyp = k * rx * dy / ry, -k * ry * dx / rx
    cx, cy = cxp + (x1 + x2) / 2, cyp + (y1 + y2) / 2
    a0 = math.atan2((dy - cyp) / ry, (dx - cxp) / rx)
    a1 = math.atan2((-dy - cyp) / ry, (-dx - cxp) / rx)
    span = (a1 - a0) % (2 * math.pi)
    if not sweep:
        span -= 2 * math.pi
    return cx, cy, rx, ry, a0, span


def samples(el, step=2.0):
    """Points along an element's centreline (paths with M L H V A Z, rects, circles)."""
    if el.startswith('<rect'):
        g = {k: float(v) for k, v in re.findall(r'(\w+)="([-\d.]+)"', el)}
        x, y, w, h, r = g['x'], g['y'], g['width'], g['height'], g.get('rx', 0)
        d = (f'M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} A{r} {r} 0 0 1 {x + w - r} {y + h} '
             f'H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z')
    elif el.startswith('<circle'):
        g = {k: float(v) for k, v in re.findall(r'(\w+)="([-\d.]+)"', el)}
        return [polar((g['cx'], g['cy']), g['r'], a) for a in range(0, 360, 3)]
    else:
        d = re.search(r' d="([^"]+)"', el).group(1)
    toks = re.findall(r'[MLHVAZ]|-?\d*\.?\d+', d)
    pts, i, cmd, cur, start = [], 0, None, (0, 0), (0, 0)

    def line_to(q):
        n = max(1, int(dist(cur, q) / step))
        pts.extend((cur[0] + (q[0] - cur[0]) * k / n, cur[1] + (q[1] - cur[1]) * k / n) for k in range(1, n + 1))
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == 'Z':
                line_to(start)
                cur = start
            continue
        v = lambda k: float(toks[i + k])
        if cmd == 'M':
            cur = start = (v(0), v(1)); pts.append(cur); i += 2; cmd = 'L'
        elif cmd == 'L':
            q = (v(0), v(1)); line_to(q); cur = q; i += 2
        elif cmd == 'H':
            q = (v(0), cur[1]); line_to(q); cur = q; i += 1
        elif cmd == 'V':
            q = (cur[0], v(0)); line_to(q); cur = q; i += 1
        elif cmd == 'A':
            q = (v(5), v(6))
            if dist(cur, q) > 1e-6 and v(0) > 0 and v(1) > 0:
                cx, cy, rx, ry, a0, span = _arc_center(cur, q, v(0), v(1), int(v(3)), int(v(4)))
                n = max(2, int(abs(span) * max(rx, ry) / step))
                pts.extend((cx + rx * math.cos(a0 + span * k / n), cy + ry * math.sin(a0 + span * k / n))
                           for k in range(1, n + 1))
            cur = q; i += 7
    return pts


def _glyph_pts(c, w):
    out = []
    for el in ALPHABET[c][0](0, LT, w, LH):
        out += samples(el)
    return out


def _advance(pa, pb, target, lo):
    """Smallest x offset >= lo of glyph b (drawn at x=0) so every point stays >= target from glyph a."""
    hi = lo + 200.0
    for _ in range(30):
        mid = (lo + hi) / 2
        ok = all(math.hypot(qx + mid - px, qy - py) >= target for qx, qy in pb for px, py in pa
                 if abs(qy - py) < target)
        lo, hi = (lo, mid) if ok else (mid, hi)
    return hi


def _layout(s, ws, target):
    xs = [0.0]
    pa = _glyph_pts(s[0], ws[0])
    for c, w in zip(s[1:], ws[1:]):
        pb = _glyph_pts(c, w)
        off = _advance(pa, pb, target, xs[-1])
        xs.append(off)
        pa = [(x + off, y) for x, y in pb]
    lefts = xs
    total = xs[-1] + ws[-1]
    return lefts, total


def label(s):
    nat = [ALPHABET[c][1] for c in s]
    mn = [ALPHABET[c][2] for c in s]
    ws = list(nat)
    gap = GAP
    xs, total = _layout(s, ws, gap)
    if total > RUN:
        lo, hi = GAP_MIN, GAP
        for _ in range(12):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if _layout(s, ws, mid)[1] <= RUN else (lo, mid)
        gap = lo
        xs, total = _layout(s, ws, gap)
    if total > RUN + 0.01:  # condense letters toward their minimum widths
        lo, hi = 0.0, 1.0
        for _ in range(14):
            k = (lo + hi) / 2
            w2 = [a - (a - b) * k for a, b in zip(nat, mn)]
            lo, hi = (lo, k) if _layout(s, w2, gap)[1] <= RUN else (k, hi)
        ws = [a - (a - b) * hi for a, b in zip(nat, mn)]
        xs, total = _layout(s, ws, gap)
    if total > RUN + 0.01:  # last resort: tighten below the minimum gap
        lo, hi = 20.0, gap
        for _ in range(12):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if _layout(s, ws, mid)[1] <= RUN else (lo, mid)
        gap = lo
        xs, total = _layout(s, ws, gap)
    x0 = 128 - total / 2
    out = []
    for c, w, x in zip(s, ws, xs):
        out += ALPHABET[c][0](x0 + x, LT, w, LH)
    return out, gap, total


FILE_TYPES = ['AAC', 'AI', 'BMP', 'CS', 'CSS', 'CSV', 'CV', 'DOC', 'EXE', 'GIF', 'HEIC', 'HTML', 'JAVA', 'JPG',
              'JS', 'JSON', 'JSX', 'KEY', 'M4P', 'MD', 'MDX', 'MOV', 'MP3', 'MP4', 'OTF', 'PDF', 'PHP', 'PNG',
              'PPT', 'PSD', 'PY', 'RAW', 'RB', 'RS', 'SASS', 'SH', 'SQL', 'SVG', 'TIFF', 'TS', 'TSX', 'TTF',
              'TXT', 'WAV', 'WOFF', 'XLS', 'XML', 'YML']
for s in FILE_TYPES:
    els, gap, total = label(s)
    if os.environ.get('UNIFY_DEBUG'):
        print(f'{s:5} gap {gap:5.1f} run {total:5.1f}')
    redo('file-' + s.lower(), line=[P(PAGE)] + els, detail=[FOLD], area=[P(PAGE_AREA)])

print(save(overwrite=True))

# ============================================================================ 2. sliders badges
# Convention (batch 153): top knob at (160, 80), bottom knob at (80, 176), bottom track stops short of the
# badge at (184, 184); the same knob layout as sliders-slash. Marks are batch 153's badge set.
def tf(points, s, c_from, c_to):
    return [(c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s) for x, y in points]


def tf_path(d, fn, s=1.0):
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        if cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {a} {la} {sw} {pt(fn((float(x), float(y))))}')
            i += 7
        else:
            out.append(pt(fn((float(toks[i]), float(toks[i + 1])))))
            i += 2
    return re.sub(r'([MLCAZ]) ', r'\1', ' '.join(out))


def marks(kind, B):
    x, y = B
    m = {'line': [], 'area': [], 'dot': [], 'dotcut': [], 'detail': [], 'hole': []}
    if kind == 'plus':
        m['line'] += [L(x - 28, y, x + 28, y), L(x, y - 28, x, y + 28)]
    elif kind == 'minus':
        m['line'] += [L(x - 28, y, x + 28, y)]
    elif kind == 'x':
        m['line'] += [L(x - 22, y - 22, x + 22, y + 22), L(x + 22, y - 22, x - 22, y + 22)]
    elif kind == 'check':
        m['line'] += [PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 14)])]
    elif kind == 'warning':
        m['line'] += [L(x, y - 34, x, y - 2)]
        m['dot'] += [C(x, y + 26, 16)]
    elif kind == 'question':
        c = (x, y - 26)
        st = polar(c, 14, 180)
        en = polar(c, 14, 60)
        m['line'] += [P(f'M{pt(st)} A14 14 0 1 1 {pt(en)} C{f(x + 2)} {f(y - 11)} {f(x)} {f(y - 8)} {f(x)} {f(y - 2)}')]
        m['dot'] += [C(x, y + 26, 16)]
    elif kind == 'arrow-up':
        m['line'] += [L(x, y + 30, x, y - 30), PL([(x - 24, y - 6), (x, y - 30), (x + 24, y - 6)])]
    elif kind == 'arrow-down':
        m['line'] += [L(x, y - 30, x, y + 30), PL([(x - 24, y + 6), (x, y + 30), (x + 24, y + 6)])]
    elif kind == 'pause':
        m['line'] += [L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)]
    elif kind == 'code':
        m['line'] += [PL([(x - 12, y - 22), (x - 30, y), (x - 12, y + 22)]),
                      PL([(x + 12, y - 22), (x + 30, y), (x + 12, y + 22)])]
    elif kind == 'dollar':
        m['line'] += [L(x, y - 36, x, y + 36),
                      P(f'M{f(x + 18)} {f(y - 26)} H{f(x - 6)} A13 13 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A13 13 0 0 1 {f(x + 6)} {f(y + 26)} H{f(x - 18)}')]
    elif kind == 'percent':
        m['line'] += [L(x + 22, y - 22, x - 22, y + 22)]
        m['dot'] += [C(x - 20, y - 20, 14), C(x + 20, y + 20, 14)]
    elif kind == 'gear':
        g = []
        for i in range(6):
            t = i * 60 - 90
            g += [polar(B, 21, t - 22), polar(B, 31, t - 13), polar(B, 31, t + 13), polar(B, 21, t + 22)]
        d = 'M' + pt(g[0])
        for i in range(6):
            a, b, cc, dd = g[i * 4:i * 4 + 4]
            if i:
                d += f' A21 21 0 0 1 {pt(a)}'
            d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
        d += f' A21 21 0 0 1 {pt(g[0])} Z'
        m['line'] += [P(d)]
        m['area'] += [P(d)]
        m['hole'] = [C(x, y, 12)]
    elif kind == 'heart':
        s = 0.34
        T = lambda px, py: pt((x + (px - 128) * s, y + 4 + (py - 136) * s))
        r = f(50 * s)
        d = (f'M{T(128, 212)} C{T(128, 212)} {T(32, 160)} {T(32, 98)} A{r} {r} 0 0 1 {T(128, 78)} '
             f'A{r} {r} 0 0 1 {T(224, 98)} C{T(224, 160)} {T(128, 212)} {T(128, 212)} Z')
        m['line'] += [P(d)]
        m['area'] += [P(d)]
    elif kind == 'star':
        st = [polar((x, y + 3), 36 if i % 2 == 0 else 16, -90 + i * 36) for i in range(10)]
        m['line'] += [PG(st)]
        m['area'] += [PG(st)]
    elif kind == 'lightning':
        pts = [(144, 32), (56, 144), (120, 144), (104, 224), (200, 108), (136, 108)]
        pp = tf(pts, 0.36, (128, 128), B)
        m['line'] += [PG(pp)]
        m['area'] += [PG(pp)]
    elif kind == 'magnifying-glass':
        m['line'] += [C(x - 6, y - 6, 22), L(x + 11, y + 11, x + 28, y + 28)]
        m['area'] += [C(x - 6, y - 6, 22)]
    elif kind == 'push-pin':
        pts = [(162.03, 33.63), (210.94, 74.67), (186.36, 89.76), (157.05, 124.7), (153.32, 192.99),
               (55.51, 110.92), (122.12, 95.39), (151.43, 60.45)]
        pp = tf(pts, 0.36, (128, 128), (x + 4, y - 4))
        nd = tf([(104.41, 151.96), (51.65, 214.84)], 0.36, (128, 128), (x + 4, y - 4))
        m['line'] += [PG(pp), PL(nd)]
        m['area'] += [PG(pp)]
    elif kind == 'share':
        m['line'] += [P(f'M{f(x - 24)} {f(y + 26)} V{f(y + 14)} A24 24 0 0 1 {f(x)} {f(y - 10)} H{f(x + 26)}'),
                      PL([(x + 10, y - 26), (x + 26, y - 10), (x + 10, y + 6)])]
    elif kind == 'sparkle':
        sp = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
        d = tf_path(sp, lambda p: tf([p], 0.42, (128, 128), B)[0])
        m['line'] += [P(d)]
        m['area'] += [P(d)]
    elif kind == 'pencil':
        pg = PG([(x - 30, y + 30), (x - 24, y + 8), (x + 8, y - 24), (x + 22, y - 10), (x - 10, y + 22)])
        m['line'] += [pg]
        m['area'] += [pg]
    else:
        raise ValueError(kind)
    return m



SC = (184, 184)
SL_TOP = [L(40, 80, 136, 80), C(160, 80, 24), L(184, 80, 216, 80)]
SL_TOP_AREA = [C(160, 80, 24)]


def sliders_badge(kind, R):
    bottom = [L(40, 176, 56, 176), C(80, 176, 24)]
    xr = SC[0] - math.sqrt(R * R - 8 * 8)
    if xr - 104 >= 12:
        bottom.append(L(104, 176, xr, 176))
    mk = marks(kind, SC)
    return dict(line=SL_TOP + bottom + mk['line'], area=SL_TOP_AREA + [C(80, 176, 24)] + mk['area'],
                hole=mk['hole'], dot=mk['dot'], dotcut=mk['dotcut'], detail=mk['detail'])


# the eight batch-152 variants (152 kept the base knob layout and used the smaller cursor marks)
for kind, mk, R in [('arrow-down', 'arrow-down', 56), ('arrow-up', 'arrow-up', 56), ('check', 'check', 56),
                    ('code', 'code', 60), ('currency-dollar', 'dollar', 60), ('gear', 'gear', 60),
                    ('heart', 'heart', 60), ('lightning', 'lightning', 60)]:
    redo('sliders-' + kind, **sliders_badge(mk, R))


# ============================================================================ 3. watch badges
# Convention (batch 129, 16 of 19 icons): the watch shifts left 32, its ring and lower strap open around the
# badge circle at (184, 184). Rebuilds the three batch-130 variants (trimmed in place) the same way.
W = load('watch')
WX = -32  # badge variants shift the watch left to make room for the badge
WC, WR = (128 + WX, 128), 64


def shift(el, dx):
    return re.sub(r'(M|L|H|V|A|cx="|x=")([^A-Za-z"]*)', lambda m: m.group(1) + _sh(m.group(1), m.group(2), dx), el)


def _sh(cmd, args, dx):
    nums = [float(v) for v in re.findall(r'-?[\d.]+', args)]
    if cmd in ('M', 'L'):
        nums = [v + dx if i % 2 == 0 else v for i, v in enumerate(nums)]
    elif cmd == 'H' or cmd in ('cx="', 'x="'):
        nums = [v + dx for v in nums]
    elif cmd == 'A':
        nums[5] += dx
    out = ' '.join(f(v) for v in nums)
    return out + (' ' if cmd not in ('cx="', 'x="') else '')



B = (184, 184)
BX, BY = B


def T(pts):
    return [(x + BX, y + BY) for x, y in pts]


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def gear_path(c, r_root, r_tip, n, phase=0):
    step = 360 / n
    hr, ht = step * 0.3, step * 0.17
    pts = []
    for i in range(n):
        t = phase + i * step
        pts.append((polar(c, r_root, t - hr), polar(c, r_tip, t - ht), polar(c, r_tip, t + ht), polar(c, r_root, t + hr)))
    d = 'M' + pt(pts[0][0])
    for i, (a, b, cc, dd) in enumerate(pts):
        if i:
            d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(pts[0][0])} Z'
    return d


def wbadge(kind):
    """Badge marks around B, identical to the ones in batches 113/114. Returns (roles, clearance radius)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), PL(T([(-20, 8), (0, 28), (20, 8)]))]
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.34)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 58
    elif kind == 'lightning':
        bl = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bl)]
        b['area'] = [PG(bl)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(b_)) for a, b_ in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'question':
        qc = (BX, BY - 14)
        e = polar(qc, 16, 50)
        b['line'] = [P(f'M{BX - 16} {BY - 14} A16 16 0 1 1 {pt(e)} C{f(BX + 2)} {f(BY + 6)} {BX} {BY + 6} {BX} {BY + 12}')]
        b['dot'] = [C(BX, BY + 36, 14)]
        cr = 58
    elif kind == 'star':
        st = [polar((BX, BY + 2), 32 if i % 2 == 0 else 14, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 58
    elif kind == 'x':  # as the x badge of batches 113/114
        b['line'] = [L(BX - 20, BY - 20, BX + 20, BY + 20), L(BX + 20, BY - 20, BX - 20, BY + 20)]
        cr = 54
    elif kind == 'warning':  # as the warning badge of batches 113/114
        b['line'] = [L(BX, BY - 32, BX, BY)]
        b['dot'] = [C(BX, BY + 32, 16)]
        cr = 58
    elif kind == 'stats':  # three rising bars, 28 apart
        b['line'] = [L(BX - 28, BY + 28, BX - 28, BY + 8), L(BX, BY + 28, BX, BY - 10),
                     L(BX + 28, BY + 28, BX + 28, BY - 28)]
        cr = 58
    else:
        raise ValueError(kind)
    return b, cr


def trim_poly(pts, c, r):
    """Pieces of the polyline that lie outside circle (c, r)."""
    pieces, cur = [], []
    for a, b_ in zip(pts, pts[1:]):
        dx, dy = b_[0] - a[0], b_[1] - a[1]
        fx, fy = a[0] - c[0], a[1] - c[1]
        A_, B_, C_ = dx * dx + dy * dy, 2 * (fx * dx + fy * dy), fx * fx + fy * fy - r * r
        disc = B_ * B_ - 4 * A_ * C_
        ts = []
        if disc > 0:
            sq = math.sqrt(disc)
            ts = sorted(t for t in ((-B_ - sq) / (2 * A_), (-B_ + sq) / (2 * A_)) if 0 < t < 1)
        bounds = [0] + ts + [1]
        for t0, t1 in zip(bounds, bounds[1:]):
            tm = (t0 + t1) / 2
            m = (a[0] + dx * tm, a[1] + dy * tm)
            p0 = (a[0] + dx * t0, a[1] + dy * t0); p1 = (a[0] + dx * t1, a[1] + dy * t1)
            if dist(m, c) >= r:
                if not cur:
                    cur = [p0]
                cur.append(p1)
            elif cur:
                pieces.append(cur); cur = []
    if cur:
        pieces.append(cur)
    return pieces


WTOP = [(96 + WX, 72.57), (104 + WX, 32), (152 + WX, 32), (160 + WX, 72.57)]
WBOT = [(96 + WX, 183.43), (104 + WX, 224), (152 + WX, 224), (160 + WX, 183.43)]
WHANDS = [shift(e, WX).replace(' "', '"') for e in W['detail']]


def watch_badge(kind):
    b, cr = wbadge(kind)
    p, q = circle_x(WC, WR, B, cr)
    ring = f'M{pt(p)} ' + arc_to(WC, WR, p, q, lambda m: dist(m, B))
    area = ring + ' ' + arc_to(B, cr, q, p, lambda m: -dist(m, WC)) + ' Z'
    line = [P(ring), PL(WTOP)] + [PL(pc) for pc in trim_poly(WBOT, B, cr)]
    out = dict(line=line + b['line'], detail=WHANDS + b['detail'], area=[P(area)] + b['area'],
               hole=b['hole'], dot=b['dot'], dotcut=b['dotcut'])
    return out



for nm, kind in [('watch-stats', 'stats'), ('watch-warning', 'warning'), ('watch-x', 'x')]:
    redo(nm, **watch_badge(kind))


# ============================================================================ 4. lock-warning, lock-x
# Convention (batch 174): full-size lock body opened around the badge circle at (184, 184), keyhole slot at
# x=100, marks from the library's chat/bell badges. The body cut depends only on the badge radius, so it is
# taken from the 174 lock badge with the same radius (pause: 54 like x; question: 58 like warning).
def lock_base(src):
    d = load(src)
    return dict(line=d['line'][:2], area=d['area'][:1], detail=d['detail'][:1])


lx = lock_base('lock-pause')
redo('lock-x', line=lx['line'] + load('chat-x')['line'][1:], area=lx['area'], detail=lx['detail'])
lw = lock_base('lock-question')
bw = load('bell-warning')
redo('lock-warning', line=lw['line'] + bw['line'][2:], area=lw['area'], detail=lw['detail'], dot=bw['dot'])

# ============================================================================ 5. sort pairs
# sort-alphabetical-ascending/descending (batch 132) already mirror each other (A/Z swapped, same arrow).
# sort-numerical-descending is redrawn from sort-numerical-ascending's glyphs, slots and arrow, 9 over 1.
SORT_ARROW = [L(184, 40, 184, 216), PL([(152, 184), (184, 216), (216, 184)])]


def one(y0):
    return [PL([(52, y0 + 16), (76, y0), (76, y0 + 72)])]


def nine(y0):
    return [C(72, y0 + 22, 22), P(f'M94 {y0 + 22} V{y0 + 50} A22 22 0 0 1 72 {y0 + 72} H56')]


redo('sort-numerical-descending', line=nine(40) + one(144) + SORT_ARROW)

# ============================================================================ 6. swipe vs hand-swipe
# One shared hand: the library's hand-tap hand (hand-pointing lowered, cropped at the wrist).
# swipe-* = hand + arrow (straight shaft, open head); hand-swipe-* = hand + motion trail (dot, dash(es) and a
# touch-point ring at the leading end; no arrowhead). Both run in the same lanes above / beside the hand.
HT = load('hand-tap')
HAND = dict(line=HT['line'][:1], detail=HT['detail'], area=HT['area'])
HY, VX = 48, 184      # horizontal gestures run along y=48 above the hand; vertical ones along x=184 (ring/pinky valley)


def arrow(a, b, head=22):
    l = dist(a, b)
    u = ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
    n = (-u[1], u[0])
    back = (b[0] - u[0] * head, b[1] - u[1] * head)
    return [L(*a, *b), PL([(back[0] + n[0] * head, back[1] + n[1] * head), b,
                           (back[0] - n[0] * head, back[1] - n[1] * head)])]


def trail(a, b, short=True):
    """Motion trail from trailing end a to leading end b: a dot, an optional short dash and a long dash
    running into a ring (the touch point) at b. Pieces sit >= 30 apart so bold stays open."""
    l = dist(a, b)
    u = ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
    at = lambda t: (a[0] + u[0] * t, a[1] + u[1] * t)
    rr = 16
    line = [C(*b, rr)]
    t0 = 32
    if short:
        line.append(L(*at(t0), *at(t0 + 20)))
        t0 += 52
    line.append(L(*at(t0), *at(l - rr)))
    return dict(line=line, dot=[C(*a, 14)])


def gesture(name, extra_line=(), extra_dot=()):
    redo(name, line=HAND['line'] + list(extra_line), detail=HAND['detail'], area=HAND['area'], dot=list(extra_dot))


H_L, H_R = (56, HY), (200, HY)
V_T, V_B = (VX, 40), (VX, 124)
gesture('swipe', arrow(H_L, H_R) + arrow(H_R, H_L)[1:])
gesture('swipe-left', arrow(H_R, H_L))
gesture('swipe-right', arrow(H_L, H_R))
gesture('swipe-up', arrow(V_B, V_T))
gesture('swipe-down', arrow(V_T, V_B))
for nm, a, b, sh in [('hand-swipe-left', (204, HY), (60, HY), True), ('hand-swipe-right', (52, HY), (196, HY), True),
                     ('hand-swipe-up', (VX, 128), (VX, 48), False), ('hand-swipe-down', (VX, 40), (VX, 108), False)]:
    t = trail(a, b, sh)
    gesture(nm, t['line'], t['dot'])

print(save(overwrite=True))
