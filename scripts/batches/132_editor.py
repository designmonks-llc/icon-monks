import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

ED = 'Editor'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- helpers
def tf(points, s, c_from, c_to):
    return [(c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s) for x, y in points]


def tf_path(d, fn, s=1.0):
    """Apply point function fn to every point of an absolute M/L/C/A/Z path (H/V not allowed); arcs radii scale by s."""
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
    """Badge marks (bare, radius ~32) centred at B."""
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
    return m


# ---------------------------------------------------------------- pencil family
PENCIL = [(40, 216), (56, 160), (168, 48), (208, 88), (96, 200)]
PENCIL_DET = [(140, 76), (180, 116)]


def pencil_geo(s=1.0, off=(0, 0), anchor=(40, 216)):
    T = lambda pts: [(anchor[0] + (x - anchor[0]) * s + off[0], anchor[1] + (y - anchor[1]) * s + off[1]) for x, y in pts]
    body = T(PENCIL)
    return PG(body), PL(T(PENCIL_DET))


B = (184, 184)
pb_body, pb_det = pencil_geo(0.92, (-6, -16))


def pencil_badge(name, tags, kind, Bc=B):
    mk = marks(kind, Bc)
    icon(name, ED, tags, line=[pb_body] + mk['line'], detail=[pb_det] + mk['detail'],
         area=[pb_body] + mk['area'], dot=mk['dot'], dotcut=mk['dotcut'], hole=mk['hole'])


for kind, suffix, tags in [
    ('arrow-down', 'arrow-down', ['pencil', 'download', 'down', 'decrease']),
    ('arrow-up', 'arrow-up', ['pencil', 'upload', 'up', 'increase']),
    ('check', 'check', ['pencil check', 'done', 'approved', 'edit', 'pencil']),
    ('code', 'code', ['pencil', 'code', 'developer', 'embed']),
    ('dollar', 'currency-dollar', ['pencil', 'dollar', 'price', 'money']),
    ('percent', 'discount', ['pencil', 'discount', 'sale', 'percent']),
    ('gear', 'gear', ['pencil', 'settings', 'configure']),
    ('heart', 'heart', ['pencil', 'favorite', 'like', 'love']),
    ('lightning', 'lightning', ['pencil', 'fast', 'power', 'instant']),
    ('magnifying-glass', 'magnifying-glass', ['pencil', 'search', 'find']),
    ('minus', 'minus', ['pencil minus', 'remove', 'subtract', 'edit', 'pencil']),
    ('pause', 'pause', ['pencil', 'paused', 'hold']),
    ('plus', 'plus', ['pencil plus', 'add', 'new', 'edit', 'pencil']),
    ('push-pin', 'push-pin', ['pencil', 'pin', 'pinned']),
    ('question', 'question', ['pencil', 'help', 'unknown', 'question']),
    ('share', 'share', ['pencil', 'share', 'send']),
    ('sparkle', 'sparkle', ['ai write', 'generate text', 'pencil', 'sparkle']),
    ('star', 'star', ['pencil', 'favorite', 'starred', 'featured']),
    ('warning', 'warning', ['pencil', 'warning', 'alert', 'error']),
    ('x', 'x', ['pencil x', 'remove', 'cancel', 'edit', 'pencil']),
]:
    pencil_badge('pencil-' + suffix, tags, kind)

pc = load('pencil')


pl_body, pl_det = pencil_geo(0.84, (0, -28))
icon('pencil-line', ED, ['edit line', 'draw', 'pencil', 'underline'],
     line=[pl_body, L(112, 216, 216, 216)], detail=[pl_det], area=[pl_body])

# ---------------------------------------------------------------- pen
def pen_parts(s=1.0, c_to=(128, 128), gap=False):
    """Ballpoint pen drawn upright (tip down) then turned 45 degrees so the tip points down-left.
    With gap, straight strokes are opened where the slash (y = x) crosses them."""
    fn = lambda p: tf(rot([p], 45)[0:1], s, (128, 128), c_to)[0]
    T = lambda d: P(tf_path(d, fn, s))
    if not gap:
        body = T('M104 168 L104 52 A24 24 0 0 1 152 52 L152 168 L128 224 Z')
        clip = T('M104 60 L72 60 L72 128')
        grip = T('M104 168 L152 168')
        return dict(line=[body, clip], detail=[grip], area=[body])
    g = 32
    def cut(p, q):
        dp, dq = (p[0] - p[1]) / math.sqrt(2), (q[0] - q[1]) / math.sqrt(2)
        t1, t2 = sorted([(-g - dp) / (dq - dp), (g - dp) / (dq - dp)])
        at = lambda t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        return at(t1), at(t2)
    R0, R1, tip, L1, L0 = [fn(q) for q in [(152, 52), (152, 168), (128, 224), (104, 168), (104, 52)]]
    ra, rb = cut(R0, R1)
    la, lb = cut(L0, L1)
    return dict(line=[T('M104 52 A24 24 0 0 1 152 52'), PL([R0, ra]), PL([L0, la]),
                      PG([R1, tip, L1]), PL([rb, R1]), PL([lb, L1])]
                + gap_segments([fn(q) for q in [(104, 60), (72, 60), (72, 128)]], False))


def gap_segments(points, closed=True, g=32):
    """Straight polygon edges with the part within g of the slash line (y = x) removed."""
    pts = list(points) + ([points[0]] if closed else [])
    out = []
    for p, q in zip(pts, pts[1:]):
        dp, dq = (p[0] - p[1]) / math.sqrt(2), (q[0] - q[1]) / math.sqrt(2)
        at = lambda t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        if abs(dq - dp) < 1e-9:
            if abs(dp) >= g:
                out.append((p, q))
            continue
        t1, t2 = sorted([(-g - dp) / (dq - dp), (g - dp) / (dq - dp)])
        if t1 > 0:
            out.append((p, at(min(t1, 1))))
        if t2 < 1:
            out.append((at(max(t2, 0)), q))
    return [L(a[0], a[1], b[0], b[1]) for a, b in out if dist(a, b) > 0.5]


icon('pencil-slash', ED, ['read only', 'no editing', 'locked edit', 'edit off', 'locked'],
     line=gap_segments(PENCIL) + pc['detail'] + [SLASH])

pn = pen_parts(1.15, (124, 138))
icon('pen', ED, ['ballpoint', 'write', 'sign', 'pen', 'ballpoint pen'], **pn)
icon('pen-slash', ED, ['pen', 'disabled', 'off', 'editor'], line=pen_parts(1.15, (124, 138), gap=True)['line'] + [SLASH])

SG_S, SG_C = 0.72, (158, 104)
sg = pen_parts(SG_S, SG_C)
sg_tip = tf(rot([(128, 224)], 45), SG_S, (128, 128), SG_C)[0]
sig_line = L(32, 208, 224, 208)
scrib = P(f'M36 172 C48 140 72 144 68 168 C64 192 88 184 {pt(sg_tip)}')
icon('signature', ED, ['sign', 'signature', 'contract', 'pen', 'autograph'],
     line=sg['line'] + [sig_line, scrib], detail=sg['detail'], area=sg['area'])
icon('signature-slash', ED, ['signature', 'off', 'disabled', 'hidden'],
     line=sg['line'] + sg['detail'] + [sig_line, scrib, SLASH])

# ---------------------------------------------------------------- lists
icon('list-letters', ED, ['alphabetical list', 'a b c', 'outline', 'list', 'letters'],
     line=[L(124, 64, 216, 64), L(124, 128, 216, 128), L(124, 192, 216, 192),
           C(62, 78, 22), L(84, 56, 84, 100),
           L(40, 136, 40, 212), C(62, 190, 22)])

icon('list-nested', ED, ['nested list', 'indent', 'tree', 'outline'],
     line=[L(96, 64, 216, 64), L(144, 128, 216, 128), L(144, 192, 216, 192)],
     dot=[C(48, 64, 16), C(96, 128, 16), C(96, 192, 16)])

icon('list-plus', ED, ['add to list', 'bullet list', 'new item', 'list', 'add'],
     line=[L(96, 64, 216, 64), L(96, 128, 216, 128), L(96, 192, 120, 192),
           L(156, 192, 212, 192), L(184, 164, 184, 220)],
     dot=[C(48, 64, 16), C(48, 128, 16), C(48, 192, 16)])

stars = []
for cy in (64, 128, 192):
    stars.append(PG([polar((60, cy + 2), 28 if i % 2 == 0 else 13, -90 + i * 36) for i in range(10)]))
icon('list-star', ED, ['favorites list', 'star', 'list', 'rating', 'starred list'],
     line=[L(120, 64, 216, 64), L(120, 128, 216, 128), L(120, 192, 216, 192)] + stars, area=stars)

icon('list-x', ED, ['list error', 'remove item', 'list', 'delete'],
     line=[L(40, 64, 216, 64), L(40, 128, 216, 128), L(40, 192, 120, 192),
           L(164, 172, 204, 212), L(204, 172, 164, 212)])

# ---------------------------------------------------------------- notes
nt = load('note')
note_body = nt['line'][0]
note_fold = nt['detail'][0]
icon('note-blank', ED, ['sticky note', 'blank note', 'memo'], line=[note_body], detail=[note_fold], area=[note_body])
icon('note-plus', ED, ['sticky note', 'add note', 'new note', 'memo', 'note'],
     line=[note_body], detail=[note_fold, L(84, 116, 152, 116), L(118, 82, 118, 150)], area=[note_body])

np_body, np_det = pencil_geo(0.72, (56, -56))
np_sq = 'M120 40 H54 A14 14 0 0 0 40 54 V202 A14 14 0 0 0 54 216 H202 A14 14 0 0 0 216 202 V136'
icon('note-pencil', ED, ['edit', 'compose', 'write', 'pencil square', 'note'],
     line=[P(np_sq), np_body], detail=[np_det], area=[np_body])

front = 'M94 80 H210 A14 14 0 0 1 224 94 V176 L176 224 H94 A14 14 0 0 1 80 210 V94 A14 14 0 0 1 94 80 Z'
back = 'M176 80 V46 A14 14 0 0 0 162 32 H46 A14 14 0 0 0 32 46 V162 A14 14 0 0 0 46 176 H80'
fold = 'M224 176 H176 V224'
icon('notes', ED, ['sticky notes', 'stickies', 'memo', 'notes', 'note stack'],
     line=[P(front), P(back)], detail=[P(fold)], area=[P(front)])
icon('notes-slash', ED, ['notes', 'off', 'disabled', 'hidden'],
     line=[R(80, 80, 144, 144, 14), P(back), SLASH])  # fold dropped: it would sit right on the slash

# ---------------------------------------------------------------- page break
top = 'M48 96 V46 A14 14 0 0 1 62 32 H194 A14 14 0 0 1 208 46 V96'
bot = 'M48 160 V210 A14 14 0 0 0 62 224 H194 A14 14 0 0 0 208 210 V160'
icon('page-break', ED, ['page break', 'separator', 'document', 'divider', 'split'],
     line=[P(top), P(bot), L(32, 128, 56, 128), L(116, 128, 140, 128), L(200, 128, 224, 128)],
     detail=[L(80, 64, 176, 64), L(80, 192, 144, 192)],
     area=[P(top + ' Z'), P(bot + ' Z')])

# ---------------------------------------------------------------- quotes
q = load('quotes')
cl, cr = (76, 148), (180, 108)
left = P(f'M44 148 V132 C44 96 64 72 100 64')
right = P(f'M212 108 V124 C212 160 192 184 156 192')
icon('quotes-single', ED, ['quote', 'single quote', 'apostrophe', 'citation'],
     line=[C(*cl, 32), left, C(*cr, 32), right], area=[C(*cl, 32), C(*cr, 32)])
icon('quotes-slash', ED, ['quotes', 'off', 'disabled', 'hidden'], line=q['line'] + [SLASH])

# ---------------------------------------------------------------- rename
lb = 'M128 80 H46 A14 14 0 0 0 32 94 V162 A14 14 0 0 0 46 176 H128'
rb = 'M208 80 H210 A14 14 0 0 1 224 94 V162 A14 14 0 0 1 210 176 H208'
icon('rename', ED, ['rename', 'text field', 'edit name', 'input'],
     line=[P(lb), P(rb), L(168, 52, 168, 204), L(148, 44, 188, 44), L(148, 212, 188, 212)],
     detail=[L(64, 128, 96, 128)],
     area=[P(lb + ' Z'), P(rb + ' Z')])

# ---------------------------------------------------------------- rows
def table(y0):
    r = R(32, y0, 192, 88, 14)
    return r, [L(32, y0 + 44, 224, y0 + 44), L(128, y0, 128, y0 + 88)]


t, td = table(32)
icon('row-insert-bottom', ED, ['insert row below', 'table', 'add row', 'spreadsheet', 'insert row'],
     line=[t, L(100, 184, 156, 184), L(128, 156, 128, 212)], detail=td, area=[t])
t2, td2 = table(136)
icon('row-insert-top', ED, ['insert row above', 'table', 'add row', 'spreadsheet', 'insert row'],
     line=[t2, L(100, 72, 156, 72), L(128, 44, 128, 100)], detail=td2, area=[t2])
icon('row-minus', ED, ['delete row', 'table', 'remove row', 'spreadsheet'],
     line=[t, L(96, 184, 160, 184)], detail=td, area=[t])

# ---------------------------------------------------------------- section
def dashed_square(a, b, r=14, leg=32):
    out = []
    out.append(P(f'M{a} {a + leg} V{a + r} A{r} {r} 0 0 1 {a + r} {a} H{a + leg}'))
    out.append(P(f'M{b - leg} {a} H{b - r} A{r} {r} 0 0 1 {b} {a + r} V{a + leg}'))
    out.append(P(f'M{b} {b - leg} V{b - r} A{r} {r} 0 0 1 {b - r} {b} H{b - leg}'))
    out.append(P(f'M{a + leg} {b} H{a + r} A{r} {r} 0 0 1 {a} {b - r} V{b - leg}'))
    m = (a + b) / 2
    out += [L(m - 16, a, m + 16, a), L(m - 16, b, m + 16, b), L(a, m - 16, a, m + 16), L(b, m - 16, b, m + 16)]
    return out


icon('section-plus', ED, ['new section', 'insert', 'divider', 'add'],
     line=dashed_square(40, 216) + [L(100, 128, 156, 128), L(128, 100, 128, 156)])

r = 30
ct, cm, cb = (128, 68), (128, 128), (128, 188)
s1 = polar(ct, r, -25)
s2 = polar(cb, r, 155)
sec1 = f'M{pt(s1)} A{r} {r} 0 1 0 {pt((128, 98))} A{r} {r} 0 0 1 {pt((128, 158))}'
sec2 = f'M{pt(s2)} A{r} {r} 0 1 0 {pt((128, 158))} A{r} {r} 0 0 1 {pt((128, 98))}'
icon('section-sign', ED, ['section sign', 'legal', 'paragraph', '§'], line=[P(sec1), P(sec2)])

# ---------------------------------------------------------------- separators
icon('separator', ED, ['separator', 'divider', 'horizontal rule', 'line', 'hr'],
     line=[R(48, 32, 160, 56, 14), L(32, 128, 224, 128), R(48, 168, 160, 56, 14)],
     area=[R(48, 32, 160, 56, 14), R(48, 168, 160, 56, 14)])
icon('separator-horizontal', ED, ['horizontal separator', 'divider', 'line', 'rule'],
     line=[L(32, 128, 224, 128), L(128, 32, 128, 88), PL([(100, 60), (128, 88), (156, 60)]),
           L(128, 224, 128, 168), PL([(100, 196), (128, 168), (156, 196)])])
icon('separator-vertical', ED, ['vertical separator', 'divider', 'line', 'rule'],
     line=[L(128, 32, 128, 224), L(32, 128, 88, 128), PL([(60, 100), (88, 128), (60, 156)]),
           L(224, 128, 168, 128), PL([(196, 100), (168, 128), (196, 156)])])

# ---------------------------------------------------------------- set square
def tri(off):
    # right triangle legs x=40, y=216, hypotenuse y=x; inset by off
    k = off * math.sqrt(2)
    x0, y0 = 32 + off, 224 - off
    return [(x0, x0 + k), (x0, y0), (y0 - k, y0)]


outer = [(32, 32), (32, 224), (224, 224)]
inner = tri(34)
hole = tri(42)
ticks = [L(40, y, 60, y) for y in ()]  # kept clean for legibility
icon('set-square', ED, ['right angle', 'set square', 'triangle ruler', 'geometry'],
     line=[PG(outer), PG(inner)], area=[PG(outer)], hole=[PG(hole)])

# ---------------------------------------------------------------- sort
A_top = [PL([(40, 112), (72, 40), (104, 112)]), L(54, 86, 90, 86)]
A_bot = [PL([(40, 216), (72, 144), (104, 216)]), L(54, 190, 90, 190)]
Z_top = [PL([(44, 40), (100, 40), (44, 112), (100, 112)])]
Z_bot = [PL([(44, 144), (100, 144), (44, 216), (100, 216)])]
ARR = [L(184, 40, 184, 216), PL([(152, 184), (184, 216), (216, 184)])]
icon('sort-alphabetical-ascending', ED, ['sort a-z', 'alphabetical', 'ascending', 'order', 'sort'],
     line=A_top + Z_bot + ARR)
icon('sort-alphabetical-descending', ED, ['sort z-a', 'alphabetical', 'descending', 'order', 'sort'],
     line=Z_top + A_bot + ARR)
one = [PL([(52, 56), (76, 40), (76, 112)])]
nine = [C(72, 166, 22), P('M94 166 V194 A22 22 0 0 1 72 216 H56')]
icon('sort-numerical-ascending', ED, ['sort 1-9', 'numerical', 'ascending', 'order', 'sort'],
     line=one + nine + ARR)

print(save(overwrite=True))
