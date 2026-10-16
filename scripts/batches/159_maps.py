import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

BC = (184, 184)  # badge centre


# ---------------------------------------------------------------- clipping helpers
def _inside(p, c, r):
    return dist(p, c) < r - 1e-6


def _seg_circle(a, b, c, r):
    """Parameters t in (0,1) where segment a-b crosses circle (c, r), sorted."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy
    B = 2 * (fx * dx + fy * dy)
    Cc = fx * fx + fy * fy - r * r
    disc = B * B - 4 * A * Cc
    if disc <= 0:
        return []
    s = math.sqrt(disc)
    ts = [(-B - s) / (2 * A), (-B + s) / (2 * A)]
    return sorted(t for t in ts if 1e-6 < t < 1 - 1e-6)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def clip_open(points, c, r):
    """Pieces of an open polyline lying outside circle (c, r)."""
    pieces, cur = [], []
    if not _inside(points[0], c, r):
        cur = [points[0]]
    for a, b in zip(points, points[1:]):
        for t in _seg_circle(a, b, c, r):
            q = _lerp(a, b, t)
            if cur:
                cur.append(q)
                pieces.append(cur)
                cur = []
            else:
                cur = [q]
        if cur and not _inside(b, c, r):
            cur.append(b)
    if cur and len(cur) > 1:
        pieces.append(cur)
    return [p for p in pieces if len(p) > 1 and sum(dist(u, v) for u, v in zip(p, p[1:])) > 2]


def clip_closed(points, c, r):
    """Outside pieces of a closed polygon outline; starts at an outside vertex."""
    k = next(i for i, p in enumerate(points) if not _inside(p, c, r))
    ring = points[k:] + points[:k] + [points[k]]
    pieces = clip_open(ring, c, r)
    if len(pieces) == 1 and dist(pieces[0][0], pieces[0][-1]) < 1e-6:
        return [], True  # untouched
    if len(pieces) > 1 and dist(pieces[-1][-1], pieces[0][0]) < 1e-6:
        pieces = [pieces[-1] + pieces[0][1:]] + pieces[1:-1]
    return pieces, False


def _pip(p, poly):
    x, y = p
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def area_cut(points, c, r):
    """Closed polygon minus a circle (one excursion) as a path with an arc."""
    k = next(i for i, p in enumerate(points) if not _inside(p, c, r))
    ring = points[k:] + points[:k] + [points[k]]
    d = 'M' + pt(ring[0])
    entry = None
    for a, b in zip(ring, ring[1:]):
        for t in _seg_circle(a, b, c, r):
            q = _lerp(a, b, t)
            if _inside(_lerp(a, b, min(1, t + 1e-4)), c, r):
                entry = q
                d += ' L' + pt(q)
            else:
                d += ' ' + arc_to(c, r, entry, q, lambda m: 1 if _pip(m, points) else 0)
                entry = None
        if entry is None and not _inside(b, c, r):
            d += ' L' + pt(b)
    return d + ' Z'


def lines_of(pieces):
    return [PL(p) for p in pieces]


# ---------------------------------------------------------------- badges (bare marks around 184,184)
GEAR = ('M177.82 164.98 L178.51 153.49 L189.49 153.49 L190.18 164.98 A20 20 0 0 1 197.38 169.14 L207.68 163.99 '
        'L213.17 173.5 L203.56 179.84 A20 20 0 0 1 203.56 188.16 L213.17 194.5 L207.68 204.01 L197.38 198.86 '
        'A20 20 0 0 1 190.18 203.02 L189.49 214.51 L178.51 214.51 L177.82 203.02 A20 20 0 0 1 170.62 198.86 '
        'L160.32 204.01 L154.83 194.5 L164.44 188.16 A20 20 0 0 1 164.44 179.84 L154.83 173.5 L160.32 163.99 '
        'L170.62 169.14 A20 20 0 0 1 177.82 164.98 Z')
HEART = ('M184 210.48 C184 210.48 151.36 192.8 151.36 171.72 A17 17 0 0 1 184 164.92 '
         'A17 17 0 0 1 216.64 171.72 C216.64 192.8 184 210.48 184 210.48 Z')
BOLT = 'M190 150 L162 190 L184 190 L178 218 L206 178 L184 178 Z'
PIN = ('M193.87 153.27 L210.5 167.23 L202.14 172.36 L192.18 184.24 L190.91 207.46 L157.65 179.55 '
       'L180.3 174.27 L190.27 162.39 Z')
STAR = ('M184 153 L192.82 174.86 L216.34 176.49 L198.27 191.64 L203.98 214.51 L184 202 L164.02 214.51 '
        'L169.73 191.64 L151.66 176.49 L175.18 174.86 Z')

BADGES = {
    'check': dict(cut=56, line=[P('M158 186 L176 204 L210 168')]),
    'code': dict(cut=60, line=[P('M170 164 L150 184 L170 204'), P('M198 164 L218 184 L198 204')]),
    'currency-dollar': dict(cut=60, line=[P('M200 160 H180 A12 12 0 0 0 180 184 H188 A12 12 0 0 1 188 208 H168'),
                                          L(184, 146, 184, 160), L(184, 208, 184, 222)]),
    'discount': dict(cut=60, line=[L(206, 162, 162, 206)], dot=[C(164, 164, 14), C(204, 204, 14)]),
    'down': dict(cut=56, line=[L(184, 156, 184, 212), PL([(164, 192), (184, 212), (204, 192)])]),
    'up': dict(cut=56, line=[L(184, 212, 184, 156), PL([(164, 176), (184, 156), (204, 176)])]),
    'gear': dict(cut=60, line=[P(GEAR)], area=[P(GEAR)], hole=[C(184, 184, 7)]),
    'heart': dict(cut=58, line=[P(HEART)], area=[P(HEART)]),
    'lightning': dict(cut=58, line=[P(BOLT)], area=[P(BOLT)]),
    'magnifying-glass': dict(cut=56, line=[C(178, 178, 18), L(192, 192, 210, 210)], area=[C(178, 178, 18)]),
    'minus': dict(cut=50, line=[L(158, 184, 210, 184)]),
    'plus': dict(cut=56, line=[L(184, 158, 184, 210), L(158, 184, 210, 184)]),
    'pause': dict(cut=54, line=[L(168, 160, 168, 208), L(200, 160, 200, 208)]),
    'push-pin': dict(cut=58, line=[P(PIN), L(174.28, 193.51, 156.34, 214.89)], area=[P(PIN)]),
    'question': dict(cut=58, line=[P('M166 164 A18 18 0 1 1 190 181 C185 184 184 187 184 192')],
                     dot=[C(184, 216, 14)]),
    'share': dict(cut=60, line=[P('M156 212 V200 A24 24 0 0 1 180 176 H212'), PL([(192, 156), (212, 176), (192, 196)])]),
    'star': dict(cut=60, line=[P(STAR)], area=[P(STAR)]),
    'warning': dict(cut=58, line=[L(184, 152, 184, 184)], dot=[C(184, 216, 16)]),
    'x': dict(cut=54, line=[L(164, 164, 204, 204), L(204, 164, 164, 204)]),
}

SLASH = L(48, 48, 208, 208)

# ---------------------------------------------------------------- map trifold variants
MAP = [(32, 64), (96, 40), (160, 64), (224, 40), (224, 192), (160, 216), (96, 192), (32, 216)]
MAP_FOLDS = [[(96, 40), (96, 192)], [(160, 64), (160, 216)]]


def map_badge(name, tags, key):
    b = BADGES[key]
    r = b['cut']
    pieces, _ = clip_closed(MAP, BC, r)
    det = []
    for fo in MAP_FOLDS:
        det += clip_open(fo, BC, r)
    icon(name, 'Maps', tags,
         line=lines_of(pieces) + b['line'],
         detail=lines_of(det),
         area=[P(area_cut(MAP, BC, r))] + b.get('area', []),
         hole=b.get('hole', []), dot=b.get('dot', []))


map_badge('map-trifold-heart', ['map trifold', 'favorite', 'like', 'love', 'map'], 'heart')
map_badge('map-trifold-lightning', ['map trifold', 'fast', 'power', 'instant', 'map'], 'lightning')
map_badge('map-trifold-magnifying-glass', ['search map', 'find place', 'explore', 'map'], 'magnifying-glass')
map_badge('map-trifold-minus', ['map trifold minus', 'remove', 'subtract', 'map', 'location'], 'minus')
map_badge('map-trifold-pause', ['map trifold', 'paused', 'hold', 'map', 'trifold'], 'pause')
map_badge('map-trifold-plus', ['map trifold plus', 'add', 'new', 'map', 'location'], 'plus')
map_badge('map-trifold-question', ['map trifold', 'help', 'unknown', 'question', 'map'], 'question')
map_badge('map-trifold-share', ['map trifold', 'share', 'send', 'map', 'trifold'], 'share')
map_badge('map-trifold-star', ['map trifold', 'favorite', 'starred', 'featured', 'map'], 'star')
map_badge('map-trifold-warning', ['damage', 'disaster', 'map', 'hazard'], 'warning')
map_badge('map-trifold-x', ['map trifold x', 'remove', 'cancel', 'map', 'location'], 'x')

base = load('map-trifold')
icon('map-trifold-slash', 'Maps', ['map trifold slash', 'off', 'disabled', 'map', 'location'],
     line=base['line'] + base['detail'] + [SLASH])

# ---------------------------------------------------------------- navigation arrow variants
NAV = [(48, 116), (208, 48), (140, 208), (120, 136)]
NAV_S, NAV_A = 0.78, (32, 32)
NAVB = [(NAV_A[0] + (x - NAV_A[0]) * NAV_S, NAV_A[1] + (y - NAV_A[1]) * NAV_S) for x, y in NAV]


def nav_badge(name, tags, key):
    b = BADGES[key]
    pieces, whole = clip_closed(NAVB, BC, b['cut'])
    if whole:
        ln, ar = [PG(NAVB)], [PG(NAVB)]
    else:
        ln, ar = lines_of(pieces), [P(area_cut(NAVB, BC, b['cut']))]
    icon(name, 'Maps', tags, line=ln + b['line'], area=ar + b.get('area', []),
         hole=b.get('hole', []), dot=b.get('dot', []))


nav_badge('navigation-arrow-check', ['navigation arrow check', 'done', 'approved', 'navigation', 'gps'], 'check')
nav_badge('navigation-arrow-code', ['navigation arrow', 'code', 'developer', 'embed', 'navigation'], 'code')
nav_badge('navigation-arrow-currency-dollar', ['navigation arrow', 'dollar', 'price', 'money', 'navigation'], 'currency-dollar')
nav_badge('navigation-arrow-discount', ['navigation arrow', 'discount', 'sale', 'percent', 'navigation'], 'discount')
nav_badge('navigation-arrow-down', ['navigation arrow', 'download', 'down', 'decrease', 'navigation'], 'down')
nav_badge('navigation-arrow-gear', ['navigation arrow', 'settings', 'configure', 'navigation', 'arrow'], 'gear')
nav_badge('navigation-arrow-heart', ['navigation arrow', 'favorite', 'like', 'love', 'navigation'], 'heart')
nav_badge('navigation-arrow-lightning', ['navigation arrow', 'fast', 'power', 'instant', 'navigation'], 'lightning')
nav_badge('navigation-arrow-magnifying-glass', ['navigation arrow', 'search', 'find', 'navigation', 'arrow'], 'magnifying-glass')
nav_badge('navigation-arrow-minus', ['navigation arrow minus', 'remove', 'subtract', 'navigation', 'gps'], 'minus')
nav_badge('navigation-arrow-pause', ['navigation arrow', 'paused', 'hold', 'navigation', 'arrow'], 'pause')
nav_badge('navigation-arrow-plus', ['navigation arrow plus', 'add', 'new', 'navigation', 'gps'], 'plus')
nav_badge('navigation-arrow-push-pin', ['navigation arrow', 'pin', 'pinned', 'navigation', 'arrow'], 'push-pin')
nav_badge('navigation-arrow-question', ['navigation arrow', 'help', 'unknown', 'question', 'navigation'], 'question')
nav_badge('navigation-arrow-share', ['navigation arrow', 'share', 'send', 'navigation', 'arrow'], 'share')
nav_badge('navigation-arrow-star', ['navigation arrow', 'favorite', 'starred', 'featured', 'navigation'], 'star')
nav_badge('navigation-arrow-up', ['navigation arrow', 'upload', 'up', 'increase', 'navigation'], 'up')
nav_badge('navigation-arrow-warning', ['navigation arrow', 'warning', 'alert', 'error', 'navigation'], 'warning')
nav_badge('navigation-arrow-x', ['navigation arrow x', 'remove', 'cancel', 'navigation', 'gps'], 'x')

base = load('navigation-arrow')
icon('navigation-arrow-slash', 'Maps', ['navigation off', 'location off', 'gps off', 'arrow', 'navigation arrow slash'],
     line=base['line'] + [SLASH])

# ---------------------------------------------------------------- landmarks
# merry-go-round: canopy, two poles with horses, platform
canopy = PG([(40, 96), (128, 40), (216, 96)])
HL = [(56, 140), (96, 140), (106, 118), (118, 126), (104, 154), (56, 154)]
HR = [(x + 96, y + 24) for x, y in HL]
horse_l = PG(HL)
horse_r = PG(HR)
icon('merry-go-round', 'Maps', ['carousel', 'fair', 'amusement'],
     line=[canopy, L(80, 96, 80, 208), L(176, 96, 176, 208), horse_l, horse_r, L(40, 208, 216, 208)],
     area=[canopy, horse_l, horse_r])

# monument: obelisk on a base
obelisk = [(102, 176), (110, 64), (128, 36), (146, 64), (154, 176)]
icon('monument', 'Maps', ['monument', 'obelisk', 'memorial', 'landmark'],
     line=[PL(obelisk), R(64, 176, 128, 40, 8)],
     area=[PG(obelisk), R(64, 176, 128, 40, 8)])

# mosque: onion dome on a hall, two minarets, arched door
dome_hall = 'M72 216 V136 C72 100 112 92 128 64 C144 92 184 100 184 136 V216'
door = 'M108 216 V188 A20 20 0 0 1 148 188 V216'
spire_l = PG([(32, 104), (40, 76), (48, 104)])
spire_r = PG([(208, 104), (216, 76), (224, 104)])
icon('mosque', 'Maps', ['mosque', 'islam', 'religion', 'worship'],
     line=[P(dome_hall), L(128, 64, 128, 44), L(40, 104, 40, 216), L(216, 104, 216, 216), spire_l, spire_r,
           L(32, 216, 224, 216)],
     detail=[P(door)],
     area=[P(dome_hall + ' Z'), spire_l, spire_r])

# museum: pediment, four columns, two steps
ped = PG([(40, 88), (128, 40), (216, 88)])
icon('museum', 'Maps', ['museum', 'gallery', 'columns', 'culture'],
     line=[ped] + [L(x, 88, x, 184) for x in (64, 106, 150, 192)] + [L(48, 184, 208, 184), L(32, 216, 224, 216)],
     area=[ped])


# pagoda: three swept roofs
def roof(cx, yb, hw, rw, lift=8):
    return (f'M{f(cx - hw)} {f(yb - lift)} Q{f(cx - rw - 8)} {f(yb + 2)} {f(cx - rw)} {f(yb - 22)} '
            f'H{f(cx + rw)} Q{f(cx + rw + 8)} {f(yb + 2)} {f(cx + hw)} {f(yb - lift)}')


tiers = [(74, 56, 20), (128, 76, 40), (182, 96, 60)]
pl, pa = [], []
for yb, hw, rw in tiers:
    pl.append(P(roof(128, yb, hw, rw)))
    pa.append(P(roof(128, yb, hw, rw) + ' Z'))
pl += [L(128, 52, 128, 34)]
pl += [L(104, 74, 104, 106), L(152, 74, 152, 106), L(84, 128, 84, 160), L(172, 128, 172, 160)]
pl += [L(64, 182, 64, 216), L(192, 182, 192, 216), L(48, 216, 208, 216)]
icon('pagoda', 'Maps', ['pagoda', 'temple', 'asia', 'landmark'], line=pl, area=pa)


# palace: big central onion dome, two domed towers
def onion(x1, x2, yb, ytip):
    cx = (x1 + x2) / 2
    h = yb - ytip
    return (f'C{f(x1)} {f(yb - h * 0.55)} {f(cx)} {f(yb - h * 0.6)} {f(cx)} {f(ytip)} '
            f'C{f(cx)} {f(yb - h * 0.6)} {f(x2)} {f(yb - h * 0.55)} {f(x2)} {f(yb)}')


palace = ('M32 216 V128 ' + onion(32, 76, 128, 88) + ' V156 H88 ' + onion(88, 168, 156, 60) +
          ' H180 V128 ' + onion(180, 224, 128, 88) + ' V216 Z')
icon('palace', 'Maps', ['palace', 'castle', 'royal', 'landmark'],
     line=[P(palace), L(128, 60, 128, 36)],
     detail=[P('M108 216 V196 A20 20 0 0 1 148 196 V216')],
     area=[P(palace)])

# path-slash
base = load('path')
icon('path-slash', 'Maps', ['path', 'off', 'disabled', 'hidden'], line=base['line'] + [SLASH])

# pavilion: curved roof on pillars with a railing
proof = 'M32 84 Q68 104 92 56 H164 Q188 104 224 84 L204 104 H52 Z'
icon('pavilion', 'Maps', ['pavilion', 'gazebo', 'landmark', 'temple'],
     line=[P(proof), L(128, 56, 128, 36), L(72, 104, 72, 208), L(184, 104, 184, 208), L(72, 164, 184, 164),
           L(40, 208, 216, 208)],
     area=[P(proof)])

# phone booth
icon('phone-booth', 'Maps', ['phone booth', 'payphone', 'call box', 'telephone'],
     line=[R(64, 32, 128, 192, 16)],
     detail=[L(64, 72, 192, 72), R(96, 104, 64, 88, 8), L(128, 104, 128, 192), L(96, 148, 160, 148)],
     area=[R(64, 32, 128, 192, 16)])

# picnic table (side view)
icon('picnic-table', 'Maps', ['picnic', 'table', 'park', 'outdoors'],
     line=[L(40, 88, 216, 88), L(100, 88, 60, 208), L(156, 88, 196, 208), L(36, 152, 108, 152), L(148, 152, 220, 152)])

# playground: ladder and slide
icon('playground', 'Maps', ['playground', 'slide', 'swing', 'park'],
     line=[L(48, 56, 48, 216), L(88, 56, 88, 216), L(48, 96, 88, 96), L(48, 136, 88, 136), L(48, 176, 88, 176),
           P('M88 64 C152 64 144 208 216 208')])

# prison: barred window
icon('prison', 'Maps', ['prison', 'jail', 'bars', 'police'],
     line=[R(40, 40, 176, 176, 16)],
     detail=[L(88, 40, 88, 216), L(128, 40, 128, 216), L(168, 40, 168, 216)],
     area=[R(40, 40, 176, 176, 16)])

# restroom: man and woman
dress = PG([(180, 92), (148, 168), (212, 168)])
icon('restroom', 'Maps', ['wc', 'toilet', 'restroom', 'bathroom'],
     line=[C(76, 52, 18), L(76, 92, 76, 152), PL([(44, 132), (76, 104), (108, 132)]), PL([(52, 216), (76, 152), (100, 216)]),
           C(180, 52, 18), dress, L(164, 168, 164, 216), L(196, 168, 196, 216)],
     area=[C(76, 52, 18), C(180, 52, 18), dress])

# road in perspective
ROAD_L, ROAD_R = [(40, 216), (100, 40)], [(216, 216), (156, 40)]
ROAD_D = [L(128, 52, 128, 76), L(128, 108, 128, 140), L(128, 172, 128, 208)]
road_area = PG([(40, 216), (100, 40), (156, 40), (216, 216)])
icon('road', 'Maps', ['road', 'highway', 'street', 'route', 'lane'],
     line=[PL(ROAD_L), PL(ROAD_R)], detail=ROAD_D, area=[road_area])

icon('road-slash', 'Maps', ['road', 'off', 'disabled', 'hidden'],
     line=[PL(ROAD_L), PL(ROAD_R), ROAD_D[0], ROAD_D[2], SLASH])

# road lane (top-down)
icon('road-lane', 'Transport', ['lane', 'road', 'highway', 'lines'],
     line=[L(48, 32, 48, 224), L(208, 32, 208, 224)],
     detail=[L(128, 40, 128, 72), L(128, 112, 128, 144), L(128, 184, 128, 216)],
     area=[R(48, 32, 160, 192)])

# road to the horizon with a setting sun
hz_area = PG([(40, 216), (118, 96), (138, 96), (216, 216)])
sun = P('M160 96 A28 28 0 0 1 216 96')
icon('road-horizon', 'Maps', ['road', 'journey', 'horizon'],
     line=[L(32, 96, 224, 96), L(40, 216, 118, 96), L(216, 216, 138, 96), sun],
     detail=[L(128, 136, 128, 152), L(128, 180, 128, 208)],
     area=[hz_area, P('M160 96 A28 28 0 0 1 216 96 Z')])

# roundabout
icon('roundabout', 'Maps', ['roundabout', 'traffic circle', 'rotary', 'direction'],
     line=[C(128, 104, 40), L(128, 144, 128, 216), L(168, 104, 216, 104), PL([(196, 84), (216, 104), (196, 124)]),
           L(40, 104, 88, 104)])


# route left / right
def route(m):
    X = (lambda x: x) if m == 'left' else (lambda x: 256 - x)
    return [L(128, 224, 128, 148),
            P(f'M128 148 C128 100 {f(X(64))} 100 {f(X(64))} 40'),
            PL([(X(40), 64), (X(64), 40), (X(88), 64)]),
            P(f'M128 148 C128 108 {f(X(192))} 108 {f(X(192))} 64')]


icon('route-left', 'Maps', ['turn left', 'route', 'fork', 'direction'], line=route('left'))
icon('route-right', 'Maps', ['turn right', 'route', 'fork', 'direction'], line=route('right'))

print(save(overwrite=True))
