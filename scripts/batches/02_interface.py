import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Interface'
CC = (128, 128)


def ring(c, r_out, r_in):
    """Annulus as one path (outer clockwise, inner counter-clockwise)."""
    cx, cy = c
    return (f'M{f(cx - r_out)} {f(cy)} A{f(r_out)} {f(r_out)} 0 1 1 {f(cx + r_out)} {f(cy)} '
            f'A{f(r_out)} {f(r_out)} 0 1 1 {f(cx - r_out)} {f(cy)} Z '
            f'M{f(cx - r_in)} {f(cy)} A{f(r_in)} {f(r_in)} 0 1 0 {f(cx + r_in)} {f(cy)} '
            f'A{f(r_in)} {f(r_in)} 0 1 0 {f(cx - r_in)} {f(cy)} Z')


# ---------------------------------------------------------------- status circles & squares
CIRCLE = C(128, 128, 96)
SQ = R(32, 32, 192, 192, 16)
CHECK = [PL([(88, 132), (116, 160), (172, 104)])]
XMARK = [L(96, 96, 160, 160), L(160, 96, 96, 160)]
PLUS = [L(128, 84, 128, 172), L(84, 128, 172, 128)]
MINUS = [L(84, 128, 172, 128)]
EXCL = [L(128, 76, 128, 136)]
EXCL_DOT = [C(128, 176, 16)]

icon('minus-circle', CAT, ['remove', 'subtract', 'delete', 'collapse'], line=[CIRCLE], detail=MINUS, area=[CIRCLE])
icon('x-square', CAT, ['close', 'cancel', 'dismiss', 'error'], line=[SQ], detail=XMARK, area=[SQ])
icon('check-square', CAT, ['checkbox', 'done', 'complete', 'checked', 'task'], line=[SQ], detail=CHECK, area=[SQ])
icon('plus-square', CAT, ['add', 'create', 'new', 'expand'], line=[SQ], detail=PLUS, area=[SQ])
icon('minus-square', CAT, ['remove', 'subtract', 'collapse', 'delete'], line=[SQ], detail=MINUS, area=[SQ])
icon('warning-circle', CAT, ['alert', 'error', 'exclamation', 'attention'],
     line=[CIRCLE], detail=EXCL, area=[CIRCLE], dotcut=EXCL_DOT)

# ---------------------------------------------------------------- shapes
icon('square', CAT, ['shape', 'box', 'checkbox', 'stop'], line=[SQ], area=[SQ])
icon('circle', CAT, ['shape', 'round', 'dot', 'ring'], line=[CIRCLE], area=[CIRCLE])
TRI = PG([(128, 40), (224, 208), (32, 208)])
icon('triangle', CAT, ['shape', 'delta', 'pyramid', 'geometry'], line=[TRI], area=[TRI])
HEX = PG(regular_polygon(CC, 96, 6))
icon('hexagon', CAT, ['shape', 'polygon', 'honeycomb', 'geometry'], line=[HEX], area=[HEX])
OCT_PTS = regular_polygon(CC, 96 / math.cos(math.radians(22.5)), 8, start=-90 + 22.5)
OCT = PG(OCT_PTS)
icon('octagon', CAT, ['shape', 'polygon', 'stop', 'geometry'], line=[OCT], area=[OCT])
icon('warning-octagon', CAT, ['alert', 'stop', 'error', 'danger', 'exclamation'],
     line=[OCT], detail=EXCL, area=[OCT], dotcut=EXCL_DOT)
DIA = PG([(128, 32), (224, 128), (128, 224), (32, 128)])
icon('diamond', CAT, ['shape', 'rhombus', 'gem', 'geometry'], line=[DIA], area=[DIA])

# star-half: core star geometry, left half tinted/filled
star = [polar((128, 136), 100 if i % 2 == 0 else 44, -90 + i * 36) for i in range(10)]
left = star[5:] + [star[0]]
icon('star-half', CAT, ['rating', 'review', 'half', 'score'],
     line=[PG(star), L(128, 36, 128, 180)], area=[PG(left)])

# heart-break: core heart with a zigzag crack
HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
icon('heart-break', CAT, ['heartbreak', 'broken', 'sad', 'breakup', 'dislike'],
     line=[P(HEART)], detail=[PL([(128, 80), (108, 118), (146, 150), (128, 210)])], area=[P(HEART)])

# prohibit: ring + slash, fill weight = bold sign
u = (1 / math.sqrt(2), 1 / math.sqrt(2)); n = (1 / math.sqrt(2), -1 / math.sqrt(2))
s1 = polar(CC, 96, -135); s2 = polar(CC, 96, 45)
holes = []
for sgn in (1, -1):
    off = 14; rin = 78
    h = math.sqrt(rin * rin - off * off)
    base = (128 + n[0] * off * sgn, 128 + n[1] * off * sgn)
    a = (base[0] - u[0] * h, base[1] - u[1] * h); b = (base[0] + u[0] * h, base[1] + u[1] * h)
    far = (128 + n[0] * 100 * sgn, 128 + n[1] * 100 * sgn)
    holes.append(P(f'M{pt(a)} L{pt(b)} ' + arc_to(CC, rin, b, a, lambda m: -dist(m, far)) + ' Z'))
icon('prohibit', CAT, ['forbidden', 'blocked', 'ban', 'not allowed', 'no'],
     line=[CIRCLE, L(*s1, *s2)], area=[CIRCLE], hole=holes)

# ---------------------------------------------------------------- dots & loaders
icon('dots-three-vertical', CAT, ['more', 'menu', 'kebab', 'options', 'overflow'],
     dot=[C(128, 56, 16), C(128, 128, 16), C(128, 200, 16)])
icon('dots-nine', CAT, ['grid', 'apps', 'launcher', 'menu'],
     dot=[C(x, y, 16) for y in (56, 128, 200) for x in (56, 128, 200)])
icon('spinner', CAT, ['loading', 'progress', 'wait', 'busy'],
     line=[L(*polar(CC, 52, a), *polar(CC, 96, a)) for a in range(-90, 270, 45)])
cn_a = polar(CC, 96, -90); cn_b = polar(CC, 96, 180 + 30)
icon('circle-notch', CAT, ['loading', 'progress', 'spinner', 'wait'],
     line=[P(f'M{pt(cn_a)} A96 96 0 1 1 {pt(cn_b)}')])

# ---------------------------------------------------------------- controls
icon('radio-button', CAT, ['radio', 'option', 'select', 'choice', 'form'],
     line=[CIRCLE], area=[CIRCLE], dot=[C(128, 128, 48)], hole=[P(ring(CC, 76, 36))])
PILL = R(32, 64, 192, 128, 64)
icon('toggle-left', CAT, ['switch', 'off', 'disabled', 'setting'],
     line=[PILL], detail=[C(96, 128, 32)], area=[PILL])
icon('toggle-right', CAT, ['switch', 'on', 'enabled', 'setting'],
     line=[PILL], detail=[C(160, 128, 32)], area=[PILL])
sel = []
for x0, y0, dx, dy in ((40, 40, 1, 1), (216, 40, -1, 1), (216, 216, -1, -1), (40, 216, 1, -1)):
    sel.append(PL([(x0, y0 + dy * 24), (x0, y0), (x0 + dx * 24, y0)]))
sel += [L(104, 40, 152, 40), L(104, 216, 152, 216), L(40, 104, 40, 152), L(216, 104, 216, 152)]
icon('selection', CAT, ['select', 'marquee', 'dashed', 'area', 'crop'], line=sel)

# push-pin: upright tack, tilted
pin_body = [(100, 40), (156, 40), (148, 64), (148, 104), (184, 152), (72, 152), (108, 104), (108, 64)]
pin_body = rot(pin_body, 40, (128, 128))
needle = rot([(128, 152), (128, 224)], 40, (128, 128))
sc = lambda pts, k=1.14: [(122 + (x - 128) * k, 131 + (y - 128) * k) for x, y in pts]
pin_body = sc(pin_body); needle = sc(needle)
icon('push-pin', CAT, ['pin', 'tack', 'attach', 'sticky', 'keep'],
     line=[PG(pin_body), PL(needle)], area=[PG(pin_body)])

clip = 'M136 104 V176 A32 32 0 0 1 72 176 V88 A56 56 0 0 1 184 88 V168'
icon('paperclip', CAT, ['attachment', 'attach', 'clip', 'file'], line=[P(clip)])

# link-break: core link capsules, opened at the inner ends and pulled apart
ul = (1 / math.sqrt(2), -1 / math.sqrt(2)); nl = (1 / math.sqrt(2), 1 / math.sqrt(2))
def half_link(cn, h, r, s, sgn):
    """U-shaped half of the core link capsule: outer end arc plus sides reaching s past the centre."""
    A = (cn[0] - sgn * ul[0] * h, cn[1] - sgn * ul[1] * h)
    e1 = (A[0] + nl[0] * r, A[1] + nl[1] * r); e2 = (A[0] - nl[0] * r, A[1] - nl[1] * r)
    t = (cn[0] + sgn * ul[0] * s, cn[1] + sgn * ul[1] * s)
    t1 = (t[0] + nl[0] * r, t[1] + nl[1] * r); t2 = (t[0] - nl[0] * r, t[1] - nl[1] * r)
    return P(f'M{pt(t1)} L{pt(e1)} ' + arc_to(A, r, e1, e2, lambda m: dist(m, cn)) + f' L{pt(t2)}')
lb = [half_link((92, 164), 30, 30, 8, 1), half_link((164, 92), 30, 30, 8, -1)]
for sgn in (1, -1):
    a = (128 + nl[0] * 56 * sgn, 128 + nl[1] * 56 * sgn)
    b = (128 + nl[0] * 80 * sgn, 128 + nl[1] * 80 * sgn)
    lb.append(L(*a, *b))
icon('link-break', CAT, ['unlink', 'broken link', 'disconnect', 'detach'], line=lb)

# ---------------------------------------------------------------- feedback
def thumb(flip):
    fy = (lambda y: 256 - y) if flip else (lambda y: y)
    hand = (f'M80 {f(fy(112))} L108 {f(fy(48))} C112 {f(fy(38))} 120 {f(fy(34))} 128 {f(fy(34))} '
            f'C144 {f(fy(34))} 156 {f(fy(46))} 152 {f(fy(64))} L144 {f(fy(104))} H196 '
            f'C212 {f(fy(104))} 224 {f(fy(118))} 220 {f(fy(134))} L208 {f(fy(192))} '
            f'C206 {f(fy(204))} 196 {f(fy(212))} 184 {f(fy(212))} H80 Z')
    y0 = min(fy(112), fy(212))
    cuff = R(32, y0, 48, 100, 8)
    return dict(line=[P(hand), cuff], detail=[L(80, fy(120), 80, fy(204))], area=[P(hand), cuff])
icon('thumbs-up', CAT, ['like', 'approve', 'agree', 'good', 'upvote'], **thumb(False))
icon('thumbs-down', CAT, ['dislike', 'disapprove', 'bad', 'downvote'], **thumb(True))

EYES = [C(96, 108, 16), C(160, 108, 16)]
icon('smiley-sad', 'People', ['face', 'emoji', 'sad', 'unhappy', 'frown'],
     line=[CIRCLE], detail=[P('M88 176 A48 48 0 0 1 168 176')], area=[CIRCLE], dotcut=EYES)
icon('smiley-meh', 'People', ['face', 'emoji', 'neutral', 'indifferent'],
     line=[CIRCLE], detail=[L(92, 164, 164, 164)], area=[CIRCLE], dotcut=EYES)
icon('smiley-wink', 'People', ['face', 'emoji', 'wink', 'playful'],
     line=[CIRCLE], detail=[P('M88 152 A48 48 0 0 0 168 152'), P('M144 112 A16 16 0 0 1 176 112')],
     area=[CIRCLE], dotcut=[C(96, 108, 16)])

# seal: scalloped badge, 12 bumps
seal_pts = []
for i in range(240):
    t = i * 2 * math.pi / 240
    rr = 88 + 8 * math.cos(10 * t)
    seal_pts.append((128 + rr * math.cos(t), 128 + rr * math.sin(t)))
SEAL = PG(seal_pts)
icon('seal-check', CAT, ['verified', 'badge', 'certified', 'approved', 'official'],
     line=[SEAL], detail=CHECK, area=[SEAL])
icon('seal-warning', CAT, ['badge', 'alert', 'unverified', 'warning'],
     line=[SEAL], detail=EXCL, area=[SEAL], dotcut=EXCL_DOT)

# ---------------------------------------------------------------- symbols
icon('asterisk', CAT, ['required', 'star', 'wildcard', 'footnote'],
     line=[L(*polar(CC, 88, a), *polar(CC, 88, a + 180)) for a in (-90, -30, 30)])
inf = []
for i in range(160):
    t = i * 2 * math.pi / 160
    d = 1 + math.sin(t) ** 2
    inf.append((128 + 92 * math.cos(t) / d, 128 + 132 * math.sin(t) * math.cos(t) / d))
icon('infinity', CAT, ['forever', 'loop', 'unlimited', 'endless'], line=[PG(inf)])
icon('equals', CAT, ['equal', 'math', 'same', 'calculator'], line=[L(48, 100, 208, 100), L(48, 156, 208, 156)])
icon('divide', CAT, ['division', 'math', 'calculator', 'split'],
     line=[L(40, 128, 216, 128)], dot=[C(128, 64, 16), C(128, 192, 16)])
icon('percent', CAT, ['percentage', 'discount', 'math', 'sale'],
     line=[L(196, 60, 60, 196), C(76, 76, 28), C(180, 180, 28)])
at_end = polar(CC, 84, 60)
icon('at', CAT, ['email', 'mention', 'address', 'handle'],
     line=[C(128, 128, 36),
           P(f'M164 92 V144 A24 24 0 0 0 212 144 V128 A84 84 0 1 0 {pt(at_end)}')])
icon('command', CAT, ['cmd', 'mac', 'keyboard', 'shortcut', 'key'],
     line=[P('M96 96 V64 A32 32 0 1 0 64 96 H192 A32 32 0 1 0 160 64 V192 A32 32 0 1 0 192 160 '
             'H64 A32 32 0 1 0 96 192 Z')])

# ---------------------------------------------------------------- slashed / zoom variants
BELL = 'M48 184 C64 168 72 144 72 112 A56 56 0 0 1 184 112 C184 144 192 168 208 184 Z'
icon('bell-slash', CAT, ['notification', 'mute', 'silent', 'off', 'disabled'],
     line=[P(BELL), P('M108 200 A20 20 0 0 0 148 200'), L(128, 40, 128, 56), L(40, 40, 216, 216)])
EYE = 'M24 128 C56 72 96 56 128 56 C160 56 200 72 232 128 C200 184 160 200 128 200 C96 200 56 184 24 128 Z'
icon('eye-slash', CAT, ['hide', 'hidden', 'invisible', 'private', 'password'],
     line=[P(EYE), C(128, 128, 36), L(48, 48, 208, 208)])
icon('magnifying-glass-plus', CAT, ['zoom in', 'magnify', 'enlarge', 'search'],
     line=[C(112, 112, 72), L(163, 163, 216, 216)], detail=[L(112, 84, 112, 140), L(84, 112, 140, 112)],
     area=[C(112, 112, 72)])
icon('magnifying-glass-minus', CAT, ['zoom out', 'reduce', 'shrink', 'search'],
     line=[C(112, 112, 72), L(163, 163, 216, 216)], detail=[L(84, 112, 140, 112)], area=[C(112, 112, 72)])

print(save(overwrite=True))
