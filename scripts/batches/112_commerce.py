import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Commerce'
SLASH = L(48, 48, 208, 208)


# ------------------------------------------------------------------ helpers
def xf(d, s, src, dst):
    """Scale an absolute path string (M L H V C A Z) by s about src and move src to dst."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cmd = [], 0, None
    X = lambda v: dst[0] + (float(v) - src[0]) * s
    Y = lambda v: dst[1] + (float(v) - src[1]) * s
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCAZ':
            cmd = t; out.append(t); i += 1
            continue
        if cmd in 'ML':
            out.append(f'{f(X(toks[i]))} {f(Y(toks[i + 1]))}'); i += 2
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(toks[i + k]))} {f(Y(toks[i + k + 1]))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'H':
            out.append(f(X(toks[i]))); i += 1
        elif cmd == 'V':
            out.append(f(Y(toks[i]))); i += 1
        elif cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {a} {la} {sw} {f(X(x))} {f(Y(y))}'); i += 7
    return re.sub(r'([MLHVCAZ]) ', r'\1', ' '.join(out))


def seg_outside(p, q, B, rc):
    """Parameter intervals of segment p->q lying outside circle (B, rc)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    fx, fy = p[0] - B[0], p[1] - B[1]
    a = dx * dx + dy * dy; b = 2 * (fx * dx + fy * dy); c = fx * fx + fy * fy - rc * rc
    disc = b * b - 4 * a * c
    if disc <= 0:
        return [(0, 1)]
    t1 = (-b - math.sqrt(disc)) / (2 * a); t2 = (-b + math.sqrt(disc)) / (2 * a)
    iv = []
    if t1 > 0: iv.append((0, min(t1, 1)))
    if t2 < 1: iv.append((max(t2, 0), 1))
    return [v for v in iv if v[1] - v[0] > 1e-6]


def clip(points, B, rc, closed=False):
    """Split a straight polyline around a badge circle; returns the remaining polylines."""
    pts = list(points)
    if closed:
        k = max(range(len(pts)), key=lambda i: dist(pts[i], B))
        pts = pts[k:] + pts[:k] + [pts[k]]
    lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    pieces, cur = [], []
    for p, q in zip(pts, pts[1:]):
        for t0, t1 in seg_outside(p, q, B, rc):
            a, b = lerp(p, q, t0), lerp(p, q, t1)
            if cur and dist(cur[-1], a) < 1e-6:
                cur.append(b)
            else:
                if cur: pieces.append(cur)
                cur = [a, b]
    if cur: pieces.append(cur)
    if closed and len(pieces) > 1 and dist(pieces[-1][-1], pieces[0][0]) < 1e-6:
        pieces = [pieces[-1] + pieces[0][1:]] + pieces[1:-1]
    return pieces


def badge_shape(points, B, rc, closed, interior):
    """Line paths and (for closed shapes) the area path of a polygon bitten by the badge circle."""
    pieces = clip(points, B, rc, closed)
    lines = [PL(pc) for pc in pieces]
    area = None
    if closed:
        pc = pieces[0] if len(pieces) == 1 else None
        if pc is None:
            raise SystemExit('unexpected clip')
        area = P(poly(pc) + ' ' + arc_to(B, rc, pc[-1], pc[0], lambda m: -dist(m, interior)) + ' Z')
    return lines, area


# ------------------------------------------------------------------ badge marks
# each returns (roles dict, R) where R is the centreline radius used for clearance
def m_plus(c, h=26):
    return dict(line=[L(c[0] - h, c[1], c[0] + h, c[1]), L(c[0], c[1] - h, c[0], c[1] + h)]), h

def m_minus(c, h=26):
    return dict(line=[L(c[0] - h, c[1], c[0] + h, c[1])]), h

def m_x(c, h=21):
    return dict(line=[L(c[0] - h, c[1] - h, c[0] + h, c[1] + h), L(c[0] + h, c[1] - h, c[0] - h, c[1] + h)]), 28

def m_check(c):
    x, y = c
    return dict(line=[PL([(x - 28, y + 2), (x - 8, y + 22), (x + 28, y - 16)])]), 30

def m_arrow(c, up):
    x, y = c
    s = -1 if up else 1
    return dict(line=[L(x, y - 28 * s, x, y + 28 * s), PL([(x - 22, y + 6 * s), (x, y + 28 * s), (x + 22, y + 6 * s)])]), 30

def m_code(c):
    x, y = c
    return dict(line=[PL([(x - 14, y - 24), (x - 34, y), (x - 14, y + 24)]),
                      PL([(x + 14, y - 24), (x + 34, y), (x + 14, y + 24)])]), 34

def m_dollar(c):
    x, y = c
    return dict(line=[L(x, y - 38, x, y + 38),
                      P(f'M{f(x + 22)} {f(y - 28)} H{f(x - 6)} A14 14 0 0 0 {f(x - 6)} {f(y)} H{f(x + 6)} '
                        f'A14 14 0 0 1 {f(x + 6)} {f(y + 28)} H{f(x - 22)}')]), 34

def m_percent(c):
    x, y = c
    return dict(line=[L(x + 28, y - 28, x - 28, y + 28)], dot=[C(x - 24, y - 24, 12), C(x + 24, y + 24, 12)]), 34

def m_gear(c, n=6, rb=25, rt=37):
    pts = []
    for i in range(n):
        t = -90 + i * 360 / n
        pts += [polar(c, rb, t - 22), polar(c, rt, t - 12), polar(c, rt, t + 12), polar(c, rb, t + 22)]
    d = 'M' + pt(pts[0])
    for i in range(n):
        a, b, cc, dd = pts[i * 4:i * 4 + 4]
        if i:
            d += f' A{rb} {rb} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{rb} {rb} 0 0 1 {pt(pts[0])} Z'
    return dict(line=[P(d)], area=[P(d)], dotcut=[C(c[0], c[1], 9)]), 38

HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
def m_heart(c, s=0.36):
    d = xf(HEART, s, (128, 140), c)
    return dict(line=[P(d)], area=[P(d)]), 34

LIGHTNING = 'M144 32 L56 144 H120 L104 224 L200 108 H136 Z'
def m_lightning(c, s=0.4):
    d = xf(LIGHTNING, s, (128, 128), c)
    return dict(line=[P(d)], area=[P(d)]), 36

def m_magnifier(c):
    x, y = c
    k = (x - 8, y - 8)
    e = polar(k, 20, 45)
    return dict(line=[C(k[0], k[1], 20), L(e[0], e[1], x + 26, y + 26)], area=[C(k[0], k[1], 20)]), 36

def m_pause(c):
    x, y = c
    return dict(line=[L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)]), 30

PIN = 'M162.03 33.63 L210.94 74.67 L186.36 89.76 L157.05 124.7 L153.32 192.99 L55.51 110.92 L122.12 95.39 L151.43 60.45 Z'
def m_pin(c, s=0.42):
    d = xf(PIN, s, (132, 124), c)
    nx = lambda v: c[0] + (v - 132) * s
    ny = lambda v: c[1] + (v - 124) * s
    return dict(line=[P(d), L(nx(104.41), ny(151.96), nx(51.65), ny(214.84))], area=[P(d)]), 38

def m_question(c):
    x, y = c
    k = (x, y - 18)
    a = polar(k, 18, 50)
    return dict(line=[P(f'M{f(x - 18)} {f(y - 18)} A18 18 0 1 1 {pt(a)} C{f(x + 4)} {f(y)} {f(x)} {f(y + 2)} {f(x)} {f(y + 8)} V{f(y + 10)}')],
                dot=[C(x, y + 38, 13)]), 36

def m_warning(c):
    x, y = c
    return dict(line=[L(x, y - 36, x, y + 6)], dot=[C(x, y + 36, 13)]), 36

def m_share(c):
    x, y = c
    return dict(line=[P(f'M{f(x - 30)} {f(y + 28)} C{f(x - 30)} {f(y - 2)} {f(x - 10)} {f(y - 12)} {f(x + 26)} {f(y - 12)}'),
                      PL([(x + 6, y - 32), (x + 26, y - 12), (x + 6, y + 8)])]), 34

def m_star(c, ro=36, ri=16):
    pts = [polar((c[0], c[1] + 3), ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]
    return dict(line=[PG(pts)], area=[PG(pts)]), 36

def m_pencil(c):
    u = (math.sqrt(0.5), -math.sqrt(0.5)); n = (math.sqrt(0.5), math.sqrt(0.5))
    at = lambda a, b: (c[0] + u[0] * a + n[0] * b, c[1] + u[1] * a + n[1] * b)
    pts = [at(-38, 0), at(-18, -15), at(36, -15), at(36, 15), at(-18, 15)]
    return dict(line=[PG(pts)], area=[PG(pts)]), 40


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, []).extend(v)
    return out


# ------------------------------------------------------------------ shopping bag
BAG = [(48, 80), (208, 80), (200, 216), (56, 216)]
BAG_HANDLE = P('M96 112 V72 A32 32 0 0 1 160 72 V112')

def bag_badge(name, tags, mark, c=(186, 188), gap=30):
    roles, R = mark(c)
    lines, area = badge_shape(BAG, c, R + gap, True, (128, 148))
    base = dict(line=lines + [BAG_HANDLE], area=[area])
    icon(name, CM, tags, **merge(base, roles))

bag_badge('shopping-bag-minus', ['bag', 'remove item', 'minus', 'shopping', 'cart'], m_minus)
bag_badge('shopping-bag-plus', ['bag', 'add item', 'plus', 'shopping', 'buy'], m_plus)
bag_badge('shopping-bag-x', ['bag', 'remove', 'x', 'shopping', 'shopping bag x'], m_x)
bag_badge('shopping-bag-warning', ['shopping bag', 'warning', 'alert', 'error', 'shopping'], m_warning, c=(188, 182))
bag_badge('shopping-bag-pencil', ['shopping bag', 'edit', 'write', 'shopping', 'bag'], m_pencil, c=(184, 184), gap=26)

icon('shopping-bag-slash', CM, ['bag', 'unavailable', 'slash', 'shopping'],
     line=[PG(BAG), BAG_HANDLE, SLASH])

# open bag: front panel plus the open mouth seen in perspective
front = [(48, 112), (208, 112), (200, 216), (56, 216)]
mouth = PL([(48, 112), (80, 72), (176, 72), (208, 112)])
icon('shopping-bag-open', CM, ['open bag', 'shopping', 'purchase'],
     line=[PG(front), mouth, P('M96 72 V64 A32 32 0 0 1 160 64 V72')],
     area=[PG(front)])


# ------------------------------------------------------------------ shopping cart
CART = [(24, 40), (56, 40), (84, 160), (192, 160), (216, 80), (65, 80)]
CART_AREA = [(65, 80), (216, 80), (192, 160), (84, 160)]

def cart_badge(name, tags, mark, c=(188, 190), gap=30):
    roles, R = mark(c)
    rc = R + gap
    lines = [PL(pc) for pc in clip(CART, c, rc)]
    _, area = badge_shape(CART_AREA, c, rc, True, (130, 110))
    base = dict(line=lines + [C(96, 204, 16)], area=[area])
    icon(name, CM, tags, **merge(base, roles))

cart_badge('shopping-cart-arrow-down', ['shopping cart', 'download', 'down', 'decrease', 'shopping'], lambda c: m_arrow(c, False))
cart_badge('shopping-cart-arrow-up', ['shopping cart', 'upload', 'up', 'increase', 'shopping'], lambda c: m_arrow(c, True))
cart_badge('shopping-cart-check', ['cart', 'checkout', 'done', 'check', 'shopping cart check'], m_check)
cart_badge('shopping-cart-code', ['shopping cart', 'code', 'developer', 'embed', 'shopping'], m_code, c=(186, 192))
cart_badge('shopping-cart-currency-dollar', ['shopping cart', 'dollar', 'price', 'money', 'shopping'], m_dollar, c=(188, 186))
cart_badge('shopping-cart-discount', ['shopping cart', 'discount', 'sale', 'percent', 'shopping'], m_percent)
cart_badge('shopping-cart-gear', ['shopping cart', 'settings', 'configure', 'shopping', 'cart'], m_gear, c=(186, 186), gap=26)
cart_badge('shopping-cart-heart', ['shopping cart', 'favorite', 'like', 'love', 'shopping'], m_heart)
cart_badge('shopping-cart-lightning', ['shopping cart', 'fast', 'power', 'instant', 'shopping'], m_lightning, c=(188, 185))
cart_badge('shopping-cart-magnifying-glass', ['shopping cart', 'search', 'find', 'shopping', 'cart'], m_magnifier)
cart_badge('shopping-cart-minus', ['cart', 'remove item', 'minus', 'shopping', 'remove from cart'], m_minus)
cart_badge('shopping-cart-pause', ['shopping cart', 'paused', 'hold', 'shopping', 'cart'], m_pause)
cart_badge('shopping-cart-plus', ['add to cart', 'shopping', 'cart', 'buy', 'shopping cart'], m_plus)
cart_badge('shopping-cart-push-pin', ['shopping cart', 'pin', 'pinned', 'shopping', 'cart'], m_pin, c=(186, 185), gap=26)
cart_badge('shopping-cart-question', ['shopping cart', 'help', 'unknown', 'question', 'shopping'], m_question, c=(188, 182))
cart_badge('shopping-cart-share', ['shopping cart', 'share', 'send', 'shopping', 'cart'], m_share)
cart_badge('shopping-cart-star', ['shopping cart', 'favorite', 'starred', 'featured', 'shopping'], m_star, c=(186, 188))
cart_badge('shopping-cart-warning', ['shopping cart', 'warning', 'alert', 'error', 'shopping'], m_warning, c=(188, 182))
cart_badge('shopping-cart-x', ['cart', 'remove', 'clear', 'x', 'remove from cart'], m_x)

icon('shopping-cart-slash', CM, ['cart off', 'remove from cart', 'no shopping', 'cart'],
     line=[PL(CART), C(96, 204, 16), C(184, 204, 16), SLASH])


# ------------------------------------------------------------------ storefront
sf = load('storefront')
AWNING = sf['line'][0]
icon('storefront-plus', CM, ['add business', 'new store', 'shop', 'storefront'],
     line=sf['line'][:4] + [P('M48 112 V216 H208 V112')],
     detail=[L(128, 140, 128, 188), L(104, 164, 152, 164)],
     area=[sf['area'][0], P('M48 104 H208 V216 H48 Z')])
icon('storefront-slash', CM, ['store closed', 'shop', 'storefront', 'slash'],
     line=sf['line'] + [SLASH])


# ------------------------------------------------------------------ tags
tg = load('tag')
TAG = tg['line'][0]
TAG_HOLE = tg['detail'][0]
heart_d = xf(HEART, 0.36, (128, 140), (140, 140))
icon('tag-heart', CM, ['loyalty', 'favourite deal', 'rewards', 'tag'],
     line=[TAG], detail=[TAG_HOLE, P(heart_d)], area=tg['area'], hole=[P(heart_d)])
icon('tag-plus', CM, ['new label', 'add tag', 'label', 'tag', 'tag plus'],
     line=[TAG], detail=[TAG_HOLE, L(140, 116, 140, 164), L(116, 140, 164, 140)], area=tg['area'])
icon('tag-minus', CM, ['tag minus', 'remove', 'subtract', 'tag', 'label'],
     line=[TAG], detail=[TAG_HOLE, L(116, 140, 164, 140)], area=tg['area'])

# two tags: the base tag scaled down, with the back tag echoed along its tip edges
s, T0 = 0.8, (32, 52)
tp = lambda x, y: (T0[0] + (x - 40) * s, T0[1] + (y - 40) * s)
front = [tp(40, 40), tp(128, 40), tp(224, 136), tp(136, 224), tp(40, 128)]
d = 31.6
A, Tt, Bm = front[1], front[2], front[3]
echo = [(A[0] + d * math.sqrt(0.5) + 8, A[1] - d * math.sqrt(0.5) + 8), (Tt[0] + d * math.sqrt(2), Tt[1]),
        (Bm[0] + d * math.sqrt(0.5) + 8, Bm[1] + d * math.sqrt(0.5) - 8)]
hole_c = tp(88, 88)
icon('tags', CM, ['tags', 'labels', 'prices', 'sale'],
     line=[PG(front), PL(echo)], detail=[C(hole_c[0], hole_c[1], 14)], area=[PG(front)])
icon('tags-slash', CM, ['tags', 'off', 'disabled', 'hidden'],
     line=[PG(front), PL(echo), C(hole_c[0], hole_c[1], 14), SLASH])


# ------------------------------------------------------------------ tax: document with a percent sign
fl = load('file')
icon('tax', CM, ['tax', 'percent', 'document', 'finance'],
     line=fl['line'], detail=fl['detail'] + [L(154, 130, 102, 182)], area=fl['area'],
     dotcut=[C(104, 132, 13), C(152, 180, 13)])


# ------------------------------------------------------------------ ticket / wallet slash
tk = load('ticket')
icon('ticket-slash', CM, ['ticket', 'off', 'disabled', 'hidden'],
     line=tk['line'] + [L(168, 96, 168, 128), SLASH])
wl = load('wallet')
icon('wallet-slash', CM, ['wallet', 'off', 'disabled', 'hidden'],
     line=wl['line'][:2] + [P('M224 116 H180 ' + arc_to((180, 140), 24, (180, 116), polar((180, 140), 24, 208), lambda m: -m[0])),
                            L(196, 164, 224, 164), SLASH])


# ------------------------------------------------------------------ tip jar
LID = 'M104 84 H86 A10 10 0 0 0 76 94 V102 A10 10 0 0 0 86 112 H170 A10 10 0 0 0 180 102 V94 A10 10 0 0 0 170 84 H152'
LID_AREA = 'M86 84 H170 A10 10 0 0 1 180 94 V102 A10 10 0 0 1 170 112 H86 A10 10 0 0 1 76 102 V94 A10 10 0 0 1 86 84 Z'
BODY = 'M88 112 C64 120 56 136 56 160 V208 A16 16 0 0 0 72 224 H184 A16 16 0 0 0 200 208 V160 C200 136 192 120 168 112'
icon('tip-jar', CM, ['tip jar', 'gratuity', 'donation', 'tips', 'coins'],
     line=[P(LID), P(BODY), C(128, 50, 18)],
     area=[P(LID_AREA), P(BODY + ' Z'), C(128, 50, 18)],
     hole=[R(106, 74, 44, 20, 6)])


# ------------------------------------------------------------------ transaction: coin inside circular arrows
cc, ra = (128, 128), 90
arcs = []
for a0, a1 in ((200, 330), (20, 150)):
    p, q = polar(cc, ra, a0), polar(cc, ra, a1)
    t = (-math.sin(math.radians(a1)), math.cos(math.radians(a1)))  # clockwise tangent at the tip
    back = (-t[0], -t[1])
    w1 = rot([(q[0] + back[0] * 30, q[1] + back[1] * 30)], 42, q)[0]
    w2 = rot([(q[0] + back[0] * 30, q[1] + back[1] * 30)], -42, q)[0]
    arcs += [P(f'M{pt(p)} A{ra} {ra} 0 0 1 {pt(q)}'), PL([w1, q, w2])]
icon('transaction', CM, ['transaction', 'payment', 'transfer', 'money'],
     line=arcs + [C(128, 128, 46)], detail=[C(128, 128, 16)], area=[C(128, 128, 46)])

print(save(overwrite=True))
