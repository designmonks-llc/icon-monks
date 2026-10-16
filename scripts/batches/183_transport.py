import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

SLASH = L(48, 48, 208, 208)


def rpoly(points, r, close=True):
    """Polygon path with corners rounded (quadratic) by r; r may be a list per point."""
    n = len(points)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    d = ''
    idx = range(n) if close else range(1, n - 1)
    segs = []
    for i in idx:
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        ri = rs[i]
        if ri == 0:
            segs.append((p1, p1, p1))
            continue
        l1, l2 = dist(p0, p1), dist(p1, p2)
        k1, k2 = min(ri, l1 / 2) / l1, min(ri, l2 / 2) / l2
        a = (p1[0] + (p0[0] - p1[0]) * k1, p1[1] + (p0[1] - p1[1]) * k1)
        b = (p1[0] + (p2[0] - p1[0]) * k2, p1[1] + (p2[1] - p1[1]) * k2)
        segs.append((a, p1, b))
    if close:
        d = 'M' + pt(segs[0][2])
        for a, c, b in segs[1:] + segs[:1]:
            d += f' L{pt(a)}' + (f' Q{pt(c)} {pt(b)}' if a != b else '')
        return d + ' Z'
    d = 'M' + pt(points[0])
    for a, c, b in segs:
        d += f' L{pt(a)}' + (f' Q{pt(c)} {pt(b)}' if a != b else '')
    return d + f' L{pt(points[-1])}'


def ring(c, r1, r2):
    """Annulus between r1 (outer) and r2 (inner) as one area path (opposite windings)."""
    x, y = c
    return (f'M{f(x - r1)} {f(y)} A{f(r1)} {f(r1)} 0 1 1 {f(x + r1)} {f(y)} A{f(r1)} {f(r1)} 0 1 1 {f(x - r1)} {f(y)} Z '
            f'M{f(x - r2)} {f(y)} A{f(r2)} {f(r2)} 0 1 0 {f(x + r2)} {f(y)} A{f(r2)} {f(r2)} 0 1 0 {f(x - r2)} {f(y)} Z')


def slashed(roles):
    """Slash variant: everything stroked becomes line, dotcuts become dots, no area."""
    return dict(line=roles.get('line', []) + roles.get('detail', []) + [SLASH],
                dot=roles.get('dot', []) + roles.get('dotcut', []))


T = 'Transport'
ICON_ROLES = {}


def ic(name, cat, tags, **roles):
    ICON_ROLES[name] = roles
    icon(name, cat, tags, **roles)


# ---------------------------------------------------------------- boats
sail = 'M112 32 C160 64 196 112 200 144 H112 Z'
hull = 'M40 168 H216 L192 204 H64 Z'
ic('sailboat', T, ['sailboat', 'sailing', 'yacht', 'boat', 'sail'],
   line=[P(sail), P(hull), L(112, 144, 112, 168)], area=[P(sail), P(hull)])
ic('sailboat-slash', T, ['sailboat', 'off', 'disabled', 'hidden'], **slashed(ICON_ROLES['sailboat']))

ship_hull = 'M32 144 H224 L196 200 H60 Z'
ship_top = 'M56 144 V120 A8 8 0 0 1 64 112 H88 V88 A8 8 0 0 1 96 80 H112 V56 A8 8 0 0 1 120 48 H136 A8 8 0 0 1 144 56 V80 H160 A8 8 0 0 1 168 88 V112 H184 A8 8 0 0 1 192 120 V144'
ic('ship', T, ['cruise', 'ship', 'liner', 'ocean', 'cargo'],
   line=[P(ship_hull), P(ship_top)], area=[P(ship_hull), P(ship_top + ' Z')],
   dotcut=[C(88, 168, 16), C(128, 168, 16), C(168, 168, 16)])
ic('ship-slash', T, ['ship', 'off', 'disabled', 'hidden'], **slashed(ICON_ROLES['ship']))

sb_hull = 'M80 128 H224 C208 164 184 192 148 192 H96 A16 16 0 0 1 80 176 Z'
ic('speedboat', T, ['speedboat', 'motorboat', 'fast boat', 'water'],
   line=[P(sb_hull), PL([(184, 128), (148, 80), (112, 80)]), L(32, 144, 52, 144), L(40, 176, 52, 176)],
   area=[P(sb_hull)])

sub_body = capsule((136, 152), 48, 40, (1, 0))
sub_tower = 'M104 112 V88 A8 8 0 0 1 112 80 H152 A8 8 0 0 1 160 88 V112'
ic('submarine', T, ['submarine', 'underwater', 'navy', 'sub'],
   line=[P(sub_body), P(sub_tower), PL([(136, 80), (136, 48), (156, 48)]), L(32, 128, 32, 176), L(32, 152, 48, 152)],
   area=[P(sub_body), P(sub_tower + ' Z')],
   dotcut=[C(104, 152, 16), C(144, 152, 16), C(184, 152, 16)])

# ---------------------------------------------------------------- small vehicles
ic('scooter', T, ['scooter', 'kick scooter', 'moped', 'e-scooter', 'delivery scooter'],
   line=[C(56, 188, 24), C(200, 188, 24), L(56, 164, 196, 164), L(196, 164, 176, 48),
         L(152, 48, 200, 48)])

ic('unicycle', T, ['unicycle', 'circus', 'wheel', 'ride'],
   line=[C(128, 168, 56), L(128, 64, 128, 156), C(128, 168, 12), R(92, 40, 72, 24, 12), PL([(136, 176), (152, 192), (172, 192)])],
   area=[R(92, 40, 72, 24, 12)])

# ---------------------------------------------------------------- seats
seat_pts = [(56, 44), (100, 36), (120, 136), (200, 136), (200, 168), (76, 168)]
seat_d = rpoly(seat_pts, [12, 12, 12, 12, 12, 16])
ic('seat', T, ['seat', 'chair', 'booking', 'car seat'],
   line=[P(seat_d), L(136, 168, 136, 216), L(96, 216, 176, 216)], area=[P(seat_d)],
   detail=[L(88, 136, 120, 136)])

# reclined seat with a sitting person
back_a, back_b = (48, 60), (84, 184)
ic('seat-recline', T, ['airline seat', 'recline', 'legroom', 'economy'],
   line=[PL([back_a, back_b, (176, 184)]), C(104, 64, 20), PL([(116, 104), (132, 144), (184, 144), (208, 200)])])

ic('seat-flat', T, ['flat bed', 'first class', 'airline seat', 'sleep'],
   line=[PL([(32, 96), (32, 168), (224, 168)]), C(80, 124, 20), L(120, 128, 208, 128), L(128, 168, 128, 216),
         L(88, 216, 168, 216)])

torso = 'M48 216 V176 A48 48 0 0 1 96 128 H160 A48 48 0 0 1 208 176 V216'
ic('seatbelt', T, ['seatbelt', 'safety', 'car'],
   line=[C(128, 64, 32), P(torso)], area=[C(128, 64, 32), P(torso + ' Z')],
   detail=[L(104, 152, 168, 216)])

# ---------------------------------------------------------------- winter
body = 'M40 64 H64 Q72 64 72 72 V120 H160 Q200 120 216 96 Q216 168 160 168 H56 Q40 168 40 152 Z'
ic('sleigh', T, ['sleigh', 'sled', 'winter', 'christmas'],
   line=[P(body), P('M32 200 H184 A24 24 0 0 0 208 176'), L(80, 168, 80, 200), L(160, 168, 160, 200)],
   area=[P(body)])

track = R(32, 152, 120, 56, 28)
sm_body = rpoly([(48, 152), (60, 120), (112, 120), (128, 72), (216, 136), (216, 152)], [0, 8, 8, 10, 10, 0])
ic('snowmobile', T, ['snowmobile', 'snow', 'winter', 'vehicle'],
   line=[track, P(sm_body), L(188, 152, 188, 208), P('M168 208 H204 A16 16 0 0 0 220 192')],
   area=[track, P(sm_body)], dotcut=[C(64, 180, 16), C(120, 180, 16)])

# ---------------------------------------------------------------- driving
hub = C(128, 128, 28)
ic('steering-wheel', T, ['steering wheel', 'drive', 'car', 'wheel', 'steering'],
   line=[C(128, 128, 96), hub, L(32, 128, 100, 128), L(156, 128, 224, 128), L(128, 156, 128, 224)],
   area=[hub])
ic('steering-wheel-slash', T, ['steering wheel', 'off', 'disabled', 'hidden', 'steering'],
   line=[C(128, 128, 96), hub, L(32, 128, 100, 128), L(156, 128, 224, 128), L(128, 156, 128, 224), SLASH])

# ---------------------------------------------------------------- rail
ic('subway', T, ['subway', 'metro', 'underground', 'train'],
   line=[P('M32 224 V128 A96 96 0 0 1 224 128 V224'), R(72, 80, 112, 112, 20), L(96, 192, 84, 216),
         L(160, 192, 172, 216)],
   area=[R(72, 80, 112, 112, 20)], detail=[L(100, 116, 156, 116)],
   dotcut=[C(102, 160, 16), C(154, 160, 16)])

ic('tram', T, ['tram', 'light rail', 'streetcar', 'rail', 'trolley'],
   line=[R(56, 72, 144, 128, 24), L(92, 200, 80, 224), L(164, 200, 176, 224), L(48, 32, 208, 32),
         PL([(128, 72), (108, 52), (128, 32)])],
   area=[R(56, 72, 144, 128, 24)], detail=[R(84, 100, 88, 40, 8)],
   dotcut=[C(92, 168, 16), C(164, 168, 16)])

loco = rpoly([(144, 160), (144, 104), (176, 104), (176, 72), (224, 72), (224, 160)], [0, 8, 0, 8, 8, 0])
ic('train-freight', T, ['freight', 'cargo train', 'rail', 'locomotive'],
   line=[R(32, 80, 88, 80, 10), P(loco), L(120, 144, 144, 144)],
   area=[R(32, 80, 88, 80, 10), P(loco)], detail=[L(62, 108, 62, 132), L(90, 108, 90, 132)],
   dot=[C(56, 188, 16), C(96, 188, 16), C(168, 188, 16), C(208, 188, 16)])

reg = 'M48 64 H152 C184 64 224 120 224 144 V152 A8 8 0 0 1 216 160 H48 A16 16 0 0 1 32 144 V80 A16 16 0 0 1 48 64 Z'
ic('train-regional', T, ['regional train', 'commuter', 'rail'],
   line=[P(reg), L(32, 216, 224, 216)], area=[P(reg)], detail=[L(60, 104, 144, 104), L(172, 96, 192, 124)],
   dot=[C(72, 184, 16), C(184, 184, 16)])

# ---------------------------------------------------------------- road vehicles
suv_body = rpoly([(32, 160), (32, 56), (152, 56), (184, 104), (224, 112), (224, 160)], [0, 16, 8, 8, 12, 0])
ic('suv', T, ['suv', 'car', 'vehicle'],
   line=[P(suv_body), C(72, 188, 20), C(184, 188, 20)], area=[P(suv_body)],
   detail=[PG([(60, 116), (60, 84), (140, 84), (162, 116)]), L(104, 84, 104, 116)])

van_body = rpoly([(32, 160), (32, 64), (160, 64), (208, 112), (224, 120), (224, 160)], [0, 20, 20, 8, 10, 0])
ic('van', T, ['van', 'delivery', 'minibus', 'shuttle', 'airport shuttle'],
   line=[P(van_body), C(72, 188, 20), C(184, 188, 20)], area=[P(van_body)],
   detail=[L(60, 104, 168, 104)])

car = load('car')
taxi_roof = 'M56 112 L76 72 H180 L200 112'
sign = 'M104 72 V52 A8 8 0 0 1 112 44 H144 A8 8 0 0 1 152 52 V72'
ic('taxi', T, ['taxi', 'cab', 'car', 'ride'],
   line=[car['line'][0], P(taxi_roof), P(sign)] + car['line'][2:], area=car['area'] + [P(sign + ' Z')],
   detail=car['detail'], dotcut=car['dotcut'])

ic('tank', T, ['tank', 'military', 'armored vehicle', 'army'],
   line=[R(32, 152, 192, 56, 28), PL([(48, 152), (64, 120), (192, 120), (208, 152)]),
         P('M88 120 V92 A20 20 0 0 1 108 72 H148 A20 20 0 0 1 168 92 V120'), L(168, 88, 224, 88)],
   area=[R(32, 152, 192, 56, 28), PG([(48, 152), (64, 120), (192, 120), (208, 152)]),
         P('M88 120 V92 A20 20 0 0 1 108 72 H148 A20 20 0 0 1 168 92 V120 Z')],
   dotcut=[C(72, 180, 16), C(128, 180, 16), C(184, 180, 16)])

rear = C(80, 168, 48)
tr_body = 'M56 112 V48 A8 8 0 0 1 64 40 H120 A8 8 0 0 1 128 48 V112 H200 A16 16 0 0 1 216 128 V152 A8 8 0 0 1 208 160 H140'
ic('tractor', T, ['tractor', 'farm', 'agriculture', 'vehicle'],
   line=[rear, C(192, 196, 16), P(tr_body), L(176, 112, 176, 72)],
   area=[R(56, 40, 72, 72, 8), P('M128 112 H200 A16 16 0 0 1 216 128 V152 A8 8 0 0 1 208 160 H128 Z')],
   dot=[C(80, 168, 16)])

# trucks (truck base: box 24..152 x 56..160, cab 152..224, wheels at 72/184)
truck = load('truck')
cab = 'M152 160 V104 A8 8 0 0 1 160 96 H188 L224 136 V160 Z'
wheels = [C(72, 188, 20), C(184, 188, 20)]

ic('tow-truck', T, ['tow truck', 'towing', 'breakdown', 'roadside'],
   line=[P(cab), R(96, 128, 56, 32, 0), L(112, 128, 64, 64), P('M64 64 V116 A12 12 0 0 1 40 116'),
         C(120, 188, 20), C(192, 188, 20)],
   area=[P(cab), R(96, 128, 56, 32, 0)])

ic('truck-flatbed', T, ['flatbed', 'truck', 'haul', 'delivery'],
   line=[P(cab), R(32, 128, 120, 32, 8)] + wheels, area=[P(cab), R(32, 128, 120, 32, 8)])

box_d = 'M104 56 H136 A16 16 0 0 1 152 72 V160 H88 V72 A16 16 0 0 1 104 56 Z'
ic('truck-delivery', T, ['delivery truck', 'shipping', 'courier', 'fast'],
   line=[P(box_d), P('M152 96 H188 L224 136 V160 H152'), C(116, 188, 20), C(192, 188, 20),
         L(32, 96, 56, 96), L(40, 128, 56, 128)],
   area=[P(box_d), P('M152 96 H188 L224 136 V160 H152 Z')])

ic('truck-return', T, ['return shipment', 'truck', 'back', 'logistics'],
   line=truck['line'], area=truck['area'],
   detail=[P('M60 96 H96 A18 18 0 0 1 96 132 H76'), PL([(74, 82), (60, 96), (74, 110)])])

ic('truck-slash', T, ['truck', 'off', 'disabled', 'hidden'], **slashed(truck))

semi_cab = 'M172 160 V96 A8 8 0 0 1 180 88 H196 L224 124 V160 Z'
ic('truck-trailer', T, ['semi truck', 'lorry', 'freight'],
   line=[R(32, 64, 108, 96, 12), P(semi_cab), L(140, 152, 172, 152), C(72, 188, 16), C(136, 188, 16),
         C(200, 188, 16)],
   area=[R(32, 64, 108, 96, 12), P(semi_cab)])

# ---------------------------------------------------------------- traffic
ic('traffic-light', T, ['traffic light', 'signal', 'stop go', 'road', 'stop'],
   line=[R(80, 32, 96, 192, 24)], area=[R(80, 32, 96, 192, 24)],
   dotcut=[C(128, 76, 20), C(128, 128, 20), C(128, 180, 20)])
ic('traffic-light-slash', T, ['traffic light', 'off', 'disabled', 'hidden', 'traffic'],
   **slashed(ICON_ROLES['traffic-light']))

tri = rpoly([(128, 32), (216, 168), (40, 168)], 14)
ic('traffic-sign', T, ['road sign', 'warning sign', 'traffic'],
   line=[P(tri), L(128, 168, 128, 224)], area=[P(tri)], detail=[L(128, 88, 128, 112)], dotcut=[C(128, 140, 16)])

ic('tunnel', T, ['underpass', 'road tunnel', 'passage', 'tunnel', 'road'],
   line=[P('M32 216 V128 A96 96 0 0 1 224 128 V216'), P('M72 216 V136 A56 56 0 0 1 184 136 V216'),
         L(32, 216, 224, 216), L(128, 176, 128, 216)],
   area=[P('M32 216 V128 A96 96 0 0 1 224 128 V216 Z')],
   hole=[P('M80 208 V136 A48 48 0 0 1 176 136 V208 Z')])

ic('turnstile', T, ['turnstile', 'gate', 'subway', 'access'],
   line=[R(32, 56, 56, 160, 14), R(168, 56, 56, 160, 14), L(88, 136, 112, 136), L(144, 136, 168, 136)],
   area=[R(32, 56, 56, 160, 14), R(168, 56, 56, 160, 14)],
   dotcut=[C(60, 92, 16), C(196, 92, 16)])

# ---------------------------------------------------------------- objects
ic('shipping-container', T, ['cargo', 'freight', 'container'],
   line=[R(32, 64, 192, 128, 14)], area=[R(32, 64, 192, 128, 14)],
   detail=[L(x, 96, x, 160) for x in (70.4, 108.8, 147.2, 185.6)])

suit = R(64, 72, 128, 116, 16)
ic('suitcase-rolling', T, ['luggage', 'trolley', 'travel', 'carry on', 'checked bag'],
   line=[suit, P('M104 72 V40 A8 8 0 0 1 112 32 H144 A8 8 0 0 1 152 40 V72')], area=[suit],
   detail=[L(104, 100, 104, 160), L(152, 100, 152, 160)], dot=[C(96, 212, 16), C(160, 212, 16)])

ic('suitcase-slash', T, ['no luggage', 'no baggage', 'suitcase off', 'travel'], line=load('suitcase')['line'] + [SLASH])

case = R(112, 104, 88, 96, 14)
ic('trolley', T, ['luggage trolley', 'hand truck', 'airport', 'cart'],
   line=[P('M56 32 H80 V200 H216'), case, C(72, 208, 16)], area=[case],
   detail=[L(140, 132, 140, 172), L(172, 132, 172, 172)])

tank_top = 'M76 32 H108 C108 72 148 72 148 32 H180 C180 72 200 88 200 112 V208 A8 8 0 0 1 192 216 H64 A8 8 0 0 1 56 208 V112 C56 88 76 72 76 32 Z'
ic('tank-top', 'Objects', ['sleeveless', 'singlet', 'clothing'], line=[P(tank_top)], area=[P(tank_top)])

tc = (128, 128)
tread = [P(f'M{pt(polar(tc, 70, a))} A70 70 0 0 1 {pt(polar(tc, 70, a + 40))}') for a in range(-160, 200, 60)]
ic('tire', T, ['tyre', 'wheel', 'car', 'tire repair', 'puncture'],
   line=[C(128, 128, 96), C(128, 128, 44)], area=[P(ring((128, 128), 96, 44))], detail=tread)

spokes = [L(128, 128, *polar((128, 128), 64, -90 + i * 72)) for i in range(5)]
ic('wheel', T, ['wheel', 'tire', 'car', 'spokes'],
   line=[C(128, 128, 96), C(128, 128, 64)] + spokes, area=[P(ring((128, 128), 96, 64))], dot=[C(128, 128, 20)])

ws = rpoly([(40, 168), (68, 48), (188, 48), (216, 168)], 14)
ic('windshield-washer', T, ['washer fluid', 'windshield', 'car', 'spray'],
   line=[P(ws), L(112, 204, 144, 204)], area=[P(ws)],
   detail=[L(*polar((128, 196), r0, a), *polar((128, 196), r0 + 16, a)) for a in (-122, -90, -58) for r0 in (52, 84)])

pv = (128, 148)
wa = polar(pv, 60, 222); wb = polar(pv, 60, 318)
ic('windshield-wiper', T, ['wiper', 'windshield', 'car', 'rain'],
   line=[P(ws)], area=[P(ws)],
   detail=[L(*pv, *polar(pv, 68, 240)), P(f'M{pt(wa)} A64 64 0 0 1 {pt(wb)}')])

zep = E(136, 104, 88, 48)
fin_u = 'M72 72 L40 48 V96'
fin_l = 'M72 136 L40 160 V112'
gond = 'M112 152 V176 A8 8 0 0 0 120 184 H152 A8 8 0 0 0 160 176 V152'
ic('zeppelin', T, ['zeppelin', 'airship', 'blimp', 'dirigible'],
   line=[zep, P(fin_u), P(fin_l), P(gond)], area=[zep, P(gond + ' Z')])
ic('zeppelin-slash', T, ['zeppelin', 'off', 'disabled', 'hidden'], **slashed(ICON_ROLES['zeppelin']))

print(save(overwrite=True))
