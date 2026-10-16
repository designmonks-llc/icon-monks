import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Editor'
SLASH = L(48, 48, 208, 208)


def tags(s):
    return [t.strip() for t in s.split(',')]


# ---------------------------------------------------------------- glyph helpers
def cap_a(apex, lx, rx, base, bar):
    """Capital A: apex point, feet at x=lx/rx on y=base, crossbar at y=bar."""
    ax, ay = apex
    t = (bar - ay) / (base - ay)
    bl = ax + (lx - ax) * t
    br = ax + (rx - ax) * t
    return [PL([(lx, base), apex, (rx, base)]), L(bl, bar, br, bar)]


def low_a(cx, cy, r):
    """Single-storey a: round bowl with a stem on the right."""
    return [C(cx, cy, r), L(cx + r, cy - r, cx + r, cy + r)]


def low_b(x, top, cy, r):
    """b: stem at x from top down to the bowl bottom, bowl to the right."""
    return [L(x, top, x, cy + r), C(x + r, cy, r)]


def low_c(cx, cy, r, open_deg=50):
    p = polar((cx, cy), r, -open_deg)
    q = polar((cx, cy), r, open_deg)
    return [P(f'M{pt(p)} A{f(r)} {f(r)} 0 1 0 {pt(q)}')]


def cap_b(x, y0, y1, ym, xr):
    """Capital B: stem at x, bowls reaching xr; upper bowl y0..ym, lower ym..y1."""
    r1 = (ym - y0) / 2
    r2 = (y1 - ym) / 2
    return [L(x, y0, x, y1),
            P(f'M{f(x)} {f(y0)} H{f(xr - r1)} A{f(r1)} {f(r1)} 0 0 1 {f(xr - r1)} {f(ym)} H{f(x)}'),
            P(f'M{f(x)} {f(ym)} H{f(xr - r2)} A{f(r2)} {f(r2)} 0 0 1 {f(xr - r2)} {f(y1)} H{f(x)}')]


def cap_c(x0, y0, x1, y1):
    """Capital C as a half stadium open to the right."""
    r = (x1 - x0) / 2
    ct = (x0 + r, y0 + r)
    cb = (x0 + r, y1 - r)
    p = polar(ct, r, -40)
    q = polar(cb, r, 40)
    return [P(f'M{pt(p)} A{f(r)} {f(r)} 0 0 0 {f(x0)} {f(ct[1])} V{f(cb[1])} A{f(r)} {f(r)} 0 0 0 {pt(q)}')]


def digit(n, x0, y0, k=1.0):
    """Digits drawn in a 48 x 72 box (scaled by k) with its top-left at (x0, y0)."""
    def T(x, y):
        return (x0 + x * k, y0 + y * k)
    def s(v):
        return f(v * k)
    if n == 1:
        return [PL([T(8, 16), T(28, 0), T(28, 72)])]
    if n == 2:
        a, b = T(2, 22), T(46, 22)
        c1, c2, e, h = T(46, 44), T(2, 60), T(2, 72), T(46, 72)
        return [P(f'M{pt(a)} A{s(22)} {s(22)} 0 0 1 {pt(b)} C{pt(c1)} {pt(c2)} {pt(e)} H{f(h[0])}')]
    if n == 3:
        cu, ru = (24, 17), 17
        cl, rl = (24, 53), 19
        st = polar(cu, ru, 205); mid = (24, 34); en = polar(cl, rl, 155)
        return [P(f'M{pt(T(*st))} A{s(ru)} {s(ru)} 0 1 1 {pt(T(*mid))} '
                  f'A{s(rl)} {s(rl)} 0 1 1 {pt(T(*en))}')]
    if n == 4:
        return [PL([T(36, 72), T(36, 0), T(0, 50), T(48, 50)])]
    if n == 5:
        cb, rb = (23, 50), 22
        st = polar(cb, rb, -128); en = polar(cb, rb, 152)
        return [P(f'M{pt(T(44, 0))} H{f(T(10, 0)[0])} L{pt(T(*st))} A{s(rb)} {s(rb)} 0 1 1 {pt(T(*en))}')]
    if n == 6:
        c = T(24, 50)
        return [C(c[0], c[1], 22 * k), P(f'M{pt(T(40, 3))} C{pt(T(20, -1))} {pt(T(2, 18))} {pt(T(2, 50))}')]
    if n == 9:
        c = T(24, 22)
        return [C(c[0], c[1], 22 * k), P(f'M{pt(T(8, 69))} C{pt(T(28, 73))} {pt(T(46, 54))} {pt(T(46, 22))}')]
    raise ValueError(n)


def sparkle(cx, cy, R):
    k = R / 96
    def q(dx, dy):
        return pt((cx + dx * k, cy + dy * k))
    return (f'M{q(0, -96)} C{q(8, -32)} {q(32, -8)} {q(96, 0)} C{q(32, 8)} {q(8, 32)} {q(0, 96)} '
            f'C{q(-8, 32)} {q(-32, 8)} {q(-96, 0)} C{q(-32, -8)} {q(-8, -32)} {q(0, -96)} Z')


def head(tip, deg, size=24):
    """Open chevron arrowhead at tip, arrow travelling in direction deg (screen degrees)."""
    a = polar(tip, size * math.sqrt(2), deg + 180 - 45)
    b = polar(tip, size * math.sqrt(2), deg + 180 + 45)
    return PL([a, tip, b])


# ---------------------------------------------------------------- Sorting
SORT_ARROW = [L(176, 48, 176, 208), head((176, 208), 90, 32)]
icon('sort-numerical-descending', CAT, tags('sort 9-1, numerical, descending, order, sort'),
     line=digit(9, 52, 40) + digit(1, 52, 144) + SORT_ARROW)

sq_big_top = R(40, 48, 72, 72, 14)
sq_big_bot = R(40, 136, 72, 72, 14)
icon('sort-shapes-ascending', CAT, tags('sort by size, ascending, shapes, order'),
     line=[C(76, 70, 22), sq_big_bot] + SORT_ARROW, area=[C(76, 70, 22), sq_big_bot])
icon('sort-shapes-descending', CAT, tags('sort by size, descending, shapes, order'),
     line=[sq_big_top, C(76, 186, 22)] + SORT_ARROW, area=[sq_big_top, C(76, 186, 22)])

# ---------------------------------------------------------------- Speech & spelling
mic = R(52, 40, 56, 96, 28)
icon('speech-to-text', CAT, tags('dictation, transcribe, voice typing, speech'),
     line=[mic, P('M36 120 A44 44 0 0 0 124 120'), L(80, 164, 80, 208), L(56, 208, 104, 208),
           L(160, 88, 216, 88), L(160, 128, 216, 128), L(160, 168, 196, 168)],
     area=[mic])

icon('spellcheck', CAT, tags('spell check, grammar, abc, check, spelling'),
     line=cap_a((60, 36), 32, 88, 120, 98) + cap_b(116, 36, 120, 74, 160) + cap_c(176, 36, 222, 120)
          + [PL([(76, 176), (108, 208), (180, 144)])])

# ---------------------------------------------------------------- Tables
TBL = R(32, 48, 192, 160, 14)
T3 = (48 + 160 / 3, 48 + 320 / 3)
grid_c = [L(32, 96, 224, 96), L(96, 48, 96, 208), L(160, 48, 160, 208)]
icon('table-column', CAT, tags('column, table, spreadsheet, select column'),
     line=[TBL] + grid_c, area=[R(96, 48, 64, 160)])
grid_r = [L(32, 96, 224, 96), L(32, 152, 224, 152), L(96, 96, 96, 208)]
icon('table-row', CAT, tags('row, table, spreadsheet, select row'),
     line=[TBL] + grid_r, area=[R(32, 96, 192, 56)])

# badge variants: table outline opened around a clear circle r=50 at (184, 184)
BC, BR = (184, 184), 50
bx = BC[0] - math.sqrt(BR ** 2 - (208 - BC[1]) ** 2)   # bottom edge exit
by = BC[1] - math.sqrt(BR ** 2 - (224 - BC[0]) ** 2)   # right edge exit
tbl_open = (f'M{f(bx)} 208 H46 A14 14 0 0 1 32 194 V62 A14 14 0 0 1 46 48 H210 A14 14 0 0 1 224 62 V{f(by)}')
near = lambda m: -dist(m, (128, 128))
tbl_area = tbl_open + ' ' + arc_to(BC, BR, (224, by), (bx, 208), near) + ' Z'


def cut_x(y):
    return BC[0] - math.sqrt(BR ** 2 - (y - BC[1]) ** 2)


def cut_y(x):
    return BC[1] - math.sqrt(BR ** 2 - (x - BC[0]) ** 2)


PLUS = [L(184, 158, 184, 210), L(158, 184, 210, 184)]
MINUS = [L(158, 184, 210, 184)]
base = load('table')
tbl_detail = [L(32, 96, 224, 96), L(32, 152, cut_x(152), 152), L(96, 96, 96, 208)]
icon('table-plus', CAT, tags('insert table, add table, grid, spreadsheet, table plus'),
     line=[P(tbl_open)] + PLUS, detail=tbl_detail, area=[P(tbl_area)])
icon('table-minus', CAT, tags('table minus, remove, subtract, table, grid'),
     line=[P(tbl_open)] + MINUS, detail=tbl_detail, area=[P(tbl_area)])
icon('table-column-plus', CAT, tags('add column, insert column, table, spreadsheet'),
     line=[P(tbl_open), L(32, 96, 224, 96), L(96, 48, 96, 208), L(160, 48, 160, cut_y(160))] + PLUS,
     area=[P('M46 48 H96 V208 H46 A14 14 0 0 1 32 194 V62 A14 14 0 0 1 46 48 Z')])
icon('table-row-plus', CAT, tags('add row, insert row, table, spreadsheet'),
     line=[P(tbl_open), L(32, 96, 224, 96), L(32, 152, cut_x(152), 152), L(96, 96, 96, 208)] + PLUS,
     area=[P('M46 48 H210 A14 14 0 0 1 224 62 V96 H32 V62 A14 14 0 0 1 46 48 Z')])

icon('table-split', CAT, tags('split cells, table, divide, spreadsheet'),
     line=[TBL], area=[TBL],
     detail=[L(128, 48, 128, 208), L(100, 128, 64, 128), head((64, 128), 180, 20),
             L(156, 128, 192, 128), head((192, 128), 0, 20)])

# ---------------------------------------------------------------- Letter pairs
AA = cap_a((76, 48), 32, 120, 208, 160) + low_a(184, 172, 32)
icon('text-aa', CAT, tags('font, typography, alphabet, letters, typeface'), line=AA)
icon('text-aa-slash', CAT, tags('ignore case, case insensitive, aa off, font'), line=AA + [SLASH])
icon('text-ab', CAT, tags('uppercase, alphabet, capitals, letters'),
     line=cap_a((72, 48), 32, 112, 208, 156) + cap_b(148, 48, 208, 120, 216))
icon('text-abc', CAT, tags('abc, alphabet, spelling, text'),
     line=low_a(54, 152, 22) + low_b(108, 72, 152, 22) + low_c(206, 152, 22) + [L(32, 208, 224, 208)])
icon('text-lowercase', CAT, tags('lowercase, small letters, case, text, typography'),
     line=low_a(72, 164, 36) + low_b(144, 48, 164, 36))
icon('text-titlecase', CAT, tags('title case, capitalize, case, text'),
     line=cap_a((72, 48), 32, 112, 208, 156) + low_b(144, 48, 172, 36))

# ---------------------------------------------------------------- Vertical alignment in a box
BOX = R(32, 32, 192, 192, 16)
for nm, y in (('top', 72), ('middle', 108), ('bottom', 144)):
    icon(f'text-align-{nm}', CAT, tags(f'text, vertical align, {nm}, typography'),
         line=[BOX], area=[BOX], detail=[L(72, y, 184, y), L(72, y + 40, 144, y + 40)])

# ---------------------------------------------------------------- Slashed letters
icon('text-b-slash', CAT, tags('text b, disabled, off, editor'), line=load('text-b')['line'] + [SLASH])
icon('text-h-slash', CAT, tags('text h, off, disabled, hidden, text'), line=load('text-h')['line'] + [SLASH])
icon('text-italic-slash', CAT, tags('text italic, off, disabled, hidden, text'),
     line=load('text-italic')['line'] + [SLASH])
icon('text-t-slash', CAT, tags('clear formatting, remove format, text, slash, remove style'),
     line=load('text-t')['line'] + [SLASH])

# ---------------------------------------------------------------- Caption, color, highlight
IMG = R(32, 40, 192, 120, 14)
icon('text-caption', CAT, tags('caption, image caption, text, figure'),
     line=[IMG, L(56, 204, 200, 204)], area=[IMG],
     detail=[PL([(48, 140), (92, 100), (132, 136), (156, 116), (196, 152)]), C(164, 80, 14)])

icon('text-case-toggle', CAT, tags('toggle case, change case, text, typography'),
     line=cap_a((76, 40), 40, 112, 136, 108) + low_a(176, 110, 26)
          + [L(48, 196, 208, 196), head((48, 196), 180, 20), head((208, 196), 0, 20)])

COLOR_BAR = R(40, 184, 176, 40, 10)
icon('text-color', CAT, tags('font color, text color, letter, highlight, a'),
     line=cap_a((128, 40), 76, 180, 152, 116) + [COLOR_BAR], area=[COLOR_BAR])
icon('text-highlight', CAT, tags('background color, fill, highlight, text'),
     line=[BOX], area=[BOX], detail=cap_a((128, 76), 80, 176, 180, 148))

icon('text-columns', CAT, tags('columns, multi-column text, layout, newspaper layout, text'),
     line=[L(32, y, 112, y) for y in (56, 104, 152, 200)]
          + [L(144, y, 224, y) for y in (56, 104, 152)] + [L(144, 200, 192, 200)])

# ---------------------------------------------------------------- Direction
pil = 'M196 40 H116 A40 40 0 0 0 116 120 H140'
pil_area = 'M140 40 H116 A40 40 0 0 0 116 120 H140 Z'
PIL = [P(pil), L(140, 40, 140, 144), L(180, 40, 180, 144)]
icon('text-direction-ltr', CAT, tags('left to right, text direction, ltr, paragraph, writing'),
     line=PIL + [L(48, 200, 208, 200), head((208, 200), 0, 20)], area=[P(pil_area)])
icon('text-direction-rtl', CAT, tags('right to left, text direction, rtl, paragraph, writing'),
     line=PIL + [L(48, 200, 208, 200), head((48, 200), 180, 20)], area=[P(pil_area)])

icon('text-grammar', CAT, tags('grammar, check, writing, proofread'),
     line=[L(40, 64, 216, 64), L(40, 112, 216, 112), L(40, 160, 96, 160),
           PL([(128, 176), (160, 208), (216, 148)])])

# ---------------------------------------------------------------- Headings
H_ = [L(40, 48, 40, 208), L(136, 48, 136, 208), L(40, 128, 136, 128)]
for n, word in ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four'), (5, 'five'), (6, 'six')):
    extra = 'title' if n == 1 else ('subtitle' if n == 2 else 'heading')
    tg = [f'heading {n}', f'h{n}', 'heading', 'text', 'title']
    if n == 1:
        tg = ['heading 1', 'h1', 'title', 'text', 'heading']
    if n == 2:
        tg = ['heading 2', 'h2', 'subtitle', 'text', 'title']
    icon(f'text-h-{word}', CAT, tg, line=H_ + digit(n, 168, 136))

# ---------------------------------------------------------------- Kerning, T variants
icon('text-kerning', CAT, tags('kerning, letter spacing, typography, text'),
     line=cap_a((68, 40), 32, 104, 144, 112) + [PL([(152, 40), (188, 144), (224, 40)])]
          + [L(64, 196, 192, 196), head((64, 196), 180, 20), head((192, 196), 0, 20)])

T_TOP = PL([(40, 68), (40, 48), (160, 48), (160, 68)])
icon('text-magnifying-glass', CAT, tags('find text, search font, text, lookup'),
     line=[T_TOP, L(100, 48, 100, 200), C(166, 166, 34), L(190, 190, 216, 216)],
     area=[C(166, 166, 34)])
icon('text-plus', CAT, tags('add text, insert text, text box, plus, new text'),
     line=[T_TOP, L(100, 48, 100, 208), L(72, 208, 128, 208)] + PLUS)
icon('text-sparkle', CAT, tags('ai writing, generate text, magic, sparkle'),
     line=[T_TOP, L(100, 48, 100, 208), L(72, 208, 128, 208), P(sparkle(176, 170, 46))],
     area=[P(sparkle(176, 170, 46))])

scan = load('scan')['line'][:4]
icon('text-scan', CAT, tags('ocr, recognize text, scan, character recognition, text recognition'),
     line=scan + [L(88, 92, 168, 92), L(128, 92, 128, 168)])

RS = R(48, 48, 160, 160)
icon('text-resize', CAT, tags('resize text, scale, text box, font size'),
     line=[L(48, 48, 208, 48), L(208, 48, 208, 208), L(208, 208, 48, 208), L(48, 208, 48, 48)],
     area=[RS], detail=[L(92, 92, 164, 92), L(128, 92, 128, 168)],
     dot=[C(48, 48, 20), C(208, 48, 20), C(208, 208, 20), C(48, 208, 20)])

# rotate: an A tipped 45 degrees with a curved arrow around it
rc = (104, 148)
ra = [(0, -56), (44, 56), (-44, 56)]
apex, rf, lf = rot([(rc[0] + x, rc[1] + y) for x, y in ra], 45, rc)
t = (20 + 56) / 112
bar_l = rot([(rc[0] - 44 * t, rc[1] + 20)], 45, rc)[0]
bar_r = rot([(rc[0] + 44 * t, rc[1] + 20)], 45, rc)[0]
ac, ar = rc, 100
s_pt, e_pt = polar(ac, ar, -118), polar(ac, ar, -8)
icon('text-rotate', CAT, tags('rotate text, vertical text, angle text, text, orientation'),
     line=[PL([lf, apex, rf]), L(*bar_l, *bar_r),
           P(f'M{pt(s_pt)} A{ar} {ar} 0 0 1 {pt(e_pt)}'), head(e_pt, -8 + 90 + 4, 22)])

icon('text-size', CAT, tags('font size, text size, typography, scale, aa'),
     line=cap_a((84, 48), 32, 136, 208, 160) + cap_a((196, 120), 168, 224, 208, 180))
A_SZ = cap_a((88, 48), 32, 144, 208, 160)
icon('text-size-decrease', CAT, tags('decrease font size, smaller text, typography, minus, decrease font'),
     line=A_SZ + [L(192, 56, 192, 136), head((192, 136), 90, 24)])
icon('text-size-increase', CAT, tags('increase font size, larger text, typography, plus, increase font'),
     line=A_SZ + [L(192, 136, 192, 56), head((192, 56), -90, 24)])

# ---------------------------------------------------------------- Sub / superscript, overline
icon('text-subscript', CAT, tags('subscript, formula, typography, text, lower'),
     line=[L(40, 48, 136, 176), L(136, 48, 40, 176)] + digit(2, 172, 156, 0.83))
icon('text-superscript', CAT, tags('superscript, exponent, typography, text, raise'),
     line=[L(40, 88, 136, 216), L(136, 88, 40, 216)] + digit(2, 172, 40, 0.83))
icon('text-overline', CAT, tags('overline, text, line above, typography'),
     line=[L(56, 48, 200, 48), P('M80 96 V168 A48 48 0 0 0 176 168 V96')])

print(save(overwrite=True))
