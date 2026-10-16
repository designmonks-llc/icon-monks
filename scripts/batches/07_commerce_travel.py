import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM, BZ, MP = 'Commerce', 'Business', 'Maps'

# ---------------------------------------------------------------- Commerce
wallet = R(32, 72, 192, 136, 16)
pocket = 'M224 116 H180 A24 24 0 0 0 180 164 H224'
icon('wallet', CM, ['money', 'purse', 'payment', 'cash', 'finance'],
     line=[wallet, P('M56 72 V56 A16 16 0 0 1 72 40 H168 A16 16 0 0 1 184 56 V72'), P(pocket)],
     area=[wallet], hole=[P('M216 124 H180 A16 16 0 0 0 180 156 H216 Z')])

icon('money', CM, ['cash', 'banknote', 'bill', 'payment', 'currency'],
     line=[R(24, 64, 208, 128, 14)], detail=[C(128, 128, 28)],
     area=[R(24, 64, 208, 128, 14)], dotcut=[C(64, 128, 16), C(192, 128, 16)])

fc, bc, cr = (100, 156), (156, 100), 68
gap = cr + 24
p, q = circle_x(bc, cr, fc, gap)
back_arc = f'M{pt(p)} ' + arc_to(bc, cr, p, q, lambda m: dist(m, fc))
back_area = back_arc + ' ' + arc_to(fc, gap, q, p, lambda m: -dist(m, bc)) + ' Z'
icon('coins', CM, ['money', 'cash', 'change', 'currency', 'savings'],
     line=[C(*fc, cr), P(back_arc)], detail=[C(*fc, 32)], area=[C(*fc, cr), P(back_area)])

icon('currency-dollar', CM, ['dollar', 'money', 'usd', 'price', 'cost'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[L(128, 64, 128, 192), P('M160 92 H110 A18 18 0 0 0 110 128 H146 A18 18 0 0 1 146 164 H96')])

ec = (148, 128)
icon('currency-euro', CM, ['euro', 'money', 'eur', 'price', 'europe'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[P(f'M{pt(polar(ec, 44, -45))} ' + arc_to(ec, 44, polar(ec, 44, -45), polar(ec, 44, 45), lambda m: -m[0])),
             L(80, 112, 136, 112), L(80, 144, 136, 144)])

roof = [(32, 88), (128, 36), (224, 88)]
icon('bank', CM, ['finance', 'institution', 'building', 'money', 'savings'],
     line=[PG(roof)] + [L(x, 120, x, 180) for x in (64, 106, 150, 192)] + [L(32, 212, 224, 212)],
     area=[PG(roof)])

rec = 'M56 32 H200 V224 L176 208 L152 224 L128 208 L104 224 L80 208 L56 224 Z'
icon('receipt', CM, ['invoice', 'bill', 'purchase', 'transaction'],
     line=[P(rec)], detail=[L(88, 80, 168, 80), L(88, 120, 168, 120), L(88, 160, 136, 160)], area=[P(rec)])

icon('calculator', CM, ['math', 'accounting', 'numbers', 'calculate'],
     line=[R(56, 32, 144, 192, 16)], detail=[R(88, 64, 80, 32, 6)], area=[R(56, 32, 144, 192, 16)],
     dotcut=[C(x, y, 16) for y in (140, 184) for x in (92, 128, 164)])

awning = ('M48 40 H208 L224 88 A24 24 0 0 1 176 88 A24 24 0 0 1 128 88 A24 24 0 0 1 80 88 '
          'A24 24 0 0 1 32 88 Z')
shop = 'M48 112 V216 H104 V160 H152 V216 H208 V112'
icon('storefront', CM, ['shop', 'store', 'market', 'retail', 'business'],
     line=[P(awning), L(88, 40, 80, 88), L(128, 40, 128, 88), L(168, 40, 176, 88), P(shop)],
     area=[P(awning), P('M48 104 H208 V216 H152 V160 H104 V216 H48 Z')])

bask = [(48, 104), (208, 104), (188, 208), (68, 208)]
icon('basket', CM, ['shopping', 'groceries', 'buy', 'cart', 'store'],
     line=[PL([(48, 104), (68, 208), (188, 208), (208, 104)]), L(32, 104, 224, 104), P('M72 104 A56 56 0 0 1 184 104')],
     detail=[L(104, 136, 108, 176), L(152, 136, 148, 176)], area=[PG(bask)])

cube = [(128, 32), (216, 80), (216, 176), (128, 224), (40, 176), (40, 80)]
icon('package', CM, ['box', 'parcel', 'shipping', 'delivery', 'order'],
     line=[PG(cube)], detail=[PL([(40, 80), (128, 128), (216, 80)]), L(128, 128, 128, 224), PL([(172, 56), (84, 104), (84, 144)])],
     area=[PG(cube)])

cargo = 'M40 56 H136 A16 16 0 0 1 152 72 V160 H24 V72 A16 16 0 0 1 40 56 Z'
cab = 'M152 96 H188 L224 136 V160 H152'
icon('truck', CM, ['delivery', 'shipping', 'transport', 'lorry', 'vehicle'],
     line=[P(cargo), P(cab), C(72, 188, 20), C(184, 188, 20)],
     area=[P(cargo), P(cab + ' Z')])

tick = ('M44 64 H212 A12 12 0 0 1 224 76 V104 A24 24 0 0 0 224 152 V180 A12 12 0 0 1 212 192 H44 '
        'A12 12 0 0 1 32 180 V152 A24 24 0 0 0 32 104 V76 A12 12 0 0 1 44 64 Z')
icon('ticket', CM, ['event', 'admission', 'pass', 'coupon', 'movie'],
     line=[P(tick)], detail=[L(168, 96, 168, 160)], area=[P(tick)])

pig = E(124, 140, 84, 60)
ear = [(92, 90), (100, 56), (132, 82)]
icon('piggy-bank', CM, ['savings', 'money', 'piggy', 'deposit', 'budget'],
     line=[pig, R(196, 120, 28, 40, 10), PL(ear), L(88, 192, 88, 216), L(164, 192, 164, 216)],
     detail=[L(108, 108, 148, 108)], area=[pig, R(196, 120, 28, 40, 10), PG(ear)], dotcut=[C(172, 124, 12)])

hand = 'M64 152 H108 C120 152 126 160 132 168 H160 L194 146 A15 15 0 0 1 212 168 L168 212 H64 Z'
icon('hand-coins', CM, ['payment', 'donate', 'pay', 'salary', 'tip'],
     line=[R(32, 144, 32, 72, 8), P(hand), C(144, 76, 44)], detail=[L(96, 184, 140, 184), L(144, 56, 144, 96)],
     area=[P(hand), C(144, 76, 44)])

icon('vault', CM, ['safe', 'secure', 'bank', 'storage', 'lock'],
     line=[R(32, 32, 192, 168, 16), L(72, 200, 72, 216), L(184, 200, 184, 216)],
     detail=[C(112, 116, 36), L(184, 88, 184, 144)], area=[R(32, 32, 192, 168, 16)], dotcut=[C(112, 116, 16)])

reg = [(56, 96), (200, 96), (216, 168), (40, 168)]
icon('cash-register', CM, ['checkout', 'pos', 'till', 'sale', 'store'],
     line=[PG(reg), R(32, 168, 192, 48, 10), R(80, 40, 96, 36, 8), L(128, 76, 128, 96)],
     detail=[L(104, 192, 152, 192)], area=[PG(reg), R(32, 168, 192, 48, 10), R(80, 40, 96, 36, 8)],
     dotcut=[C(x, 132, 16) for x in (96, 128, 160)])

# ---------------------------------------------------------------- Business
cup = 'M72 40 H184 V96 A56 56 0 0 1 72 96 Z'
icon('trophy', BZ, ['award', 'winner', 'prize', 'champion', 'achievement'],
     line=[P(cup), P('M72 64 H40 V80 C40 104 56 124 82 128'), P('M184 64 H216 V80 C216 104 200 124 174 128'),
           L(128, 152, 128, 216), L(88, 216, 168, 216)],
     area=[P(cup)])

mc = (128, 160)
icon('medal', BZ, ['award', 'prize', 'winner', 'badge', 'achievement'],
     line=[C(*mc, 56), PL([(92, 117), (64, 40), (108, 40), (128, 84), (148, 40), (192, 40), (164, 117)])],
     detail=[C(*mc, 24)], area=[C(*mc, 56), PG([(92, 117), (64, 40), (108, 40), (128, 84), (148, 40), (192, 40), (164, 117)])])

icon('certificate', BZ, ['diploma', 'award', 'document', 'credential', 'license'],
     line=[R(32, 40, 192, 160, 14)], detail=[L(64, 80, 192, 80), L(64, 120, 124, 120), L(64, 160, 108, 160), C(172, 148, 24)],
     area=[R(32, 40, 192, 160, 14)])

icon('briefcase', BZ, ['work', 'business', 'job', 'office', 'portfolio'],
     line=[R(32, 72, 192, 136, 16), P('M88 72 V56 A16 16 0 0 1 104 40 H152 A16 16 0 0 1 168 56 V72')],
     detail=[L(32, 124, 224, 124)], area=[R(32, 72, 192, 136, 16)])

hb = 'M64 96 H192 L216 200 A12 12 0 0 1 204 216 H52 A12 12 0 0 1 40 200 Z'
icon('handbag', BZ, ['purse', 'bag', 'fashion', 'accessory'],
     line=[P(hb), P('M80 96 A48 48 0 0 1 176 96')], area=[P(hb)], dotcut=[C(128, 140, 16)])

icon('suitcase', BZ, ['luggage', 'travel', 'trip', 'baggage'],
     line=[R(56, 64, 144, 152, 16), P('M96 64 V48 A16 16 0 0 1 112 32 H144 A16 16 0 0 1 160 48 V64')],
     detail=[L(96, 100, 96, 180), L(160, 100, 160, 180)], area=[R(56, 64, 144, 152, 16)])

bp = 'M56 112 A48 48 0 0 1 104 64 H152 A48 48 0 0 1 200 112 V200 A16 16 0 0 1 184 216 H72 A16 16 0 0 1 56 200 Z'
icon('backpack', BZ, ['bag', 'school', 'hiking', 'travel', 'rucksack'],
     line=[P(bp), P('M104 64 V48 A16 16 0 0 1 120 32 H136 A16 16 0 0 1 152 48 V64')],
     detail=[R(88, 140, 80, 44, 12)], area=[P(bp)])

lp = 'M32 144 H80 A24 24 0 0 1 32 144 Z'
rp = 'M176 144 H224 A24 24 0 0 1 176 144 Z'
icon('scales', BZ, ['justice', 'law', 'balance', 'legal', 'weigh'],
     line=[L(128, 40, 128, 208), L(88, 208, 168, 208), L(56, 64, 200, 64),
           PL([(32, 144), (56, 64), (80, 144)]), PL([(176, 144), (200, 64), (224, 144)]), P(lp), P(rp)],
     area=[P(lp), P(rp)])

gc = (104, 96)
gu = (math.sqrt(.5), -math.sqrt(.5)); gn = (math.sqrt(.5), math.sqrt(.5))
head = [(gc[0] + gu[0] * a + gn[0] * b, gc[1] + gu[1] * a + gn[1] * b) for a, b in ((-56, -24), (56, -24), (56, 24), (-56, 24))]
icon('gavel', BZ, ['law', 'judge', 'auction', 'court', 'legal'],
     line=[PG(head), L(gc[0] + gn[0] * 24, gc[1] + gn[1] * 24, gc[0] + gn[0] * 140, gc[1] + gn[1] * 140), R(32, 192, 104, 24, 8)],
     area=[PG(head), R(32, 192, 104, 24, 8)])

icon('buildings', BZ, ['city', 'office', 'company', 'urban', 'apartment'],
     line=[P('M40 216 V56 A16 16 0 0 1 56 40 H120 A16 16 0 0 1 136 56 V216'),
           P('M136 104 H200 A16 16 0 0 1 216 120 V216'), L(24, 216, 232, 216)],
     detail=[L(72, 88, 104, 88), L(72, 128, 104, 128), L(72, 168, 104, 168), L(160, 144, 192, 144), L(160, 180, 192, 180)],
     area=[P('M40 216 V56 A16 16 0 0 1 56 40 H120 A16 16 0 0 1 136 56 V104 H200 A16 16 0 0 1 216 120 V216 Z')])

icon('building-office', BZ, ['office', 'company', 'workplace', 'corporate', 'tower'],
     line=[P('M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V216'), L(32, 216, 224, 216),
           P('M108 216 V180 H148 V216')],
     detail=[L(x, y, x + 24, y) for y in (72, 108, 144) for x in (88, 144)],
     area=[P('M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V216 H148 V180 H108 V216 Z')])

fac = 'M32 216 V112 L80 140 V112 L128 140 V112 L176 140 V40 H216 V216 Z'
icon('factory', BZ, ['industry', 'manufacturing', 'plant', 'production'],
     line=[P(fac)], detail=[L(60, 180, 84, 180), L(108, 180, 132, 180)], area=[P(fac)])

# ---------------------------------------------------------------- Maps & travel
tri = [(32, 64), (96, 40), (160, 64), (224, 40), (224, 192), (160, 216), (96, 192), (32, 216)]
icon('map-trifold', MP, ['map', 'navigation', 'directions', 'atlas', 'travel'],
     line=[PG(tri)], detail=[L(96, 40, 96, 192), L(160, 64, 160, 216)], area=[PG(tri)])

s1 = [(64, 40), (184, 40), (208, 64), (184, 88), (64, 88)]
s2 = [(192, 120), (72, 120), (48, 144), (72, 168), (192, 168)]
icon('signpost', MP, ['direction', 'sign', 'way', 'navigation', 'crossroads'],
     line=[PG(s1), PG(s2), L(128, 88, 128, 120), L(128, 168, 128, 224)], area=[PG(s1), PG(s2)])

icon('path', MP, ['route', 'journey', 'road', 'trail', 'directions'],
     line=[C(56, 200, 24), C(200, 56, 24), P('M80 200 H156 A36 36 0 0 0 156 128 H100 A36 36 0 0 1 100 56 H176')],
     area=[C(56, 200, 24), C(200, 56, 24)])

cabin = [(56, 112), (80, 56), (176, 56), (200, 112)]
tire = lambda x: P(f'M{x} 184 V200 A8 8 0 0 0 {x + 8} 208 H{x + 24} A8 8 0 0 0 {x + 32} 200 V184')
icon('car', MP, ['vehicle', 'auto', 'drive', 'transport', 'automobile'],
     line=[R(32, 112, 192, 72, 16), PL(cabin), tire(56), tire(168)],
     detail=[L(112, 152, 144, 152)], area=[R(32, 112, 192, 72, 16)], dotcut=[C(72, 148, 16), C(184, 148, 16)])

tire2 = lambda x: P(f'M{x} 192 V208 A8 8 0 0 0 {x + 8} 216 H{x + 24} A8 8 0 0 0 {x + 32} 208 V192')
icon('bus', MP, ['transport', 'transit', 'public', 'vehicle', 'school'],
     line=[R(48, 32, 160, 160, 20), tire2(72), tire2(152)], detail=[R(72, 64, 112, 56, 8)],
     area=[R(48, 32, 160, 160, 20)], dotcut=[C(88, 156, 16), C(168, 156, 16)])

trn = 'M56 168 V72 A40 40 0 0 1 96 32 H160 A40 40 0 0 1 200 72 V168 A16 16 0 0 1 184 184 H72 A16 16 0 0 1 56 168 Z'
icon('train', MP, ['railway', 'transit', 'subway', 'metro', 'transport'],
     line=[P(trn), L(88, 184, 64, 224), L(168, 184, 192, 224)], detail=[R(84, 64, 88, 48, 8)],
     area=[P(trn)], dotcut=[C(92, 148, 16), C(164, 148, 16)])

rhalf = [(144, 64), (144, 104), (224, 152), (224, 176), (144, 152), (144, 184), (176, 204), (176, 216), (128, 204)]
lhalf = [(256 - x, y) for x, y in reversed(rhalf[:-1])]
plane = 'M112 64 A16 16 0 0 1 144 64 ' + ' '.join('L' + pt(p) for p in rhalf[1:] + lhalf) + ' Z'
icon('airplane', MP, ['flight', 'travel', 'plane', 'airport', 'trip'], line=[P(plane)], area=[P(plane)])

icon('bicycle', MP, ['bike', 'cycling', 'ride', 'transport', 'sport'],
     line=[C(68, 152, 34), C(188, 152, 34), PL([(68, 152), (108, 96), (128, 152), (68, 152)]),
           PL([(108, 96), (168, 96), (128, 152)]), PL([(188, 152), (160, 72), (184, 72)]),
           L(108, 96, 100, 76), L(88, 76, 116, 76)])

moto = [(76, 112), (164, 112), (140, 164), (112, 164)]
icon('motorcycle', MP, ['motorbike', 'bike', 'ride', 'vehicle', 'scooter'],
     line=[C(62, 164, 30), C(194, 164, 30), L(62, 164, 90, 130), PG(moto), PL([(194, 164), (164, 80), (140, 80)])],
     area=[PG(moto)])

hull = 'M32 168 H224 L196 208 H60 Z'
icon('boat', MP, ['sailboat', 'ship', 'sea', 'sailing', 'marine'],
     line=[P(hull), PG([(108, 56), (108, 136), (48, 136)]), PG([(140, 40), (140, 136), (212, 136)]), L(140, 136, 140, 168)],
     area=[P(hull), PG([(108, 56), (108, 136), (48, 136)]), PG([(140, 40), (140, 136), (212, 136)])])

rb = 'M128 32 C168 60 176 104 176 144 V176 H80 V144 C80 104 88 60 128 32 Z'
icon('rocket', MP, ['launch', 'space', 'startup', 'spaceship', 'boost'],
     line=[P(rb), PL([(80, 136), (48, 168), (48, 200), (80, 184)]), PL([(176, 136), (208, 168), (208, 200), (176, 184)]),
           L(128, 200, 128, 224)],
     detail=[C(128, 108, 22)], area=[P(rb)])

icon('gas-pump', MP, ['fuel', 'petrol', 'gas station', 'gasoline', 'diesel'],
     line=[P('M48 216 V56 A16 16 0 0 1 64 40 H128 A16 16 0 0 1 144 56 V216'), L(32, 216, 160, 216),
           P('M144 104 H160 A16 16 0 0 1 176 120 V176 A16 16 0 0 0 208 176 V96 L184 72')],
     detail=[R(76, 72, 40, 40, 6)], area=[P('M48 216 V56 A16 16 0 0 1 64 40 H128 A16 16 0 0 1 144 56 V216 Z')])

icon('anchor', MP, ['marine', 'ship', 'harbor', 'sea', 'nautical'],
     line=[C(128, 56, 20), L(128, 76, 128, 216), L(88, 104, 168, 104), P('M48 152 A82 82 0 0 0 208 152'),
           L(32, 152, 64, 152), L(192, 152, 224, 152)])

icon('tent', MP, ['camping', 'outdoors', 'camp', 'shelter'],
     line=[PG([(32, 208), (128, 48), (224, 208)]), PL([(96, 208), (128, 152), (160, 208)])],
     area=[PG([(32, 208), (128, 48), (224, 208), (160, 208), (128, 152), (96, 208)])])

mnt = 'M32 200 L88 112 L115.7 155.6 L160 56 L224 200 Z'
icon('mountains', MP, ['landscape', 'hiking', 'peak', 'nature', 'outdoors'],
     line=[P(mnt)], detail=[PL([(138.7, 104), (152, 116), (166, 104), (181.3, 104)])], area=[P(mnt)])

icon('hospital', MP, ['medical', 'clinic', 'health', 'emergency', 'building'],
     line=[P('M48 216 V64 A16 16 0 0 1 64 48 H192 A16 16 0 0 1 208 64 V216'), L(32, 216, 224, 216), P('M108 216 V184 H148 V216')],
     detail=[L(128, 88, 128, 152), L(96, 120, 160, 120)],
     area=[P('M48 216 V64 A16 16 0 0 1 64 48 H192 A16 16 0 0 1 208 64 V216 H148 V184 H108 V216 Z')])

mat = 'M32 120 H184 A40 40 0 0 1 224 160 V176 H32 Z'
icon('bed', MP, ['sleep', 'hotel', 'bedroom', 'rest', 'accommodation'],
     line=[L(32, 56, 32, 208), P('M32 120 H184 A40 40 0 0 1 224 160 V208'), L(32, 176, 224, 176), R(64, 88, 56, 32, 16)],
     area=[P(mat), R(64, 88, 56, 32, 16)])

door = 'M64 216 V48 A16 16 0 0 1 80 32 H176 A16 16 0 0 1 192 48 V216'
icon('door', MP, ['entrance', 'exit', 'room', 'closed'],
     line=[P(door), L(32, 216, 224, 216)], area=[P(door + ' Z')], dotcut=[C(156, 128, 16)])

panel = [(64, 40), (144, 56), (144, 224), (64, 216)]
icon('door-open', MP, ['entrance', 'exit', 'enter', 'leave', 'open'],
     line=[P('M64 216 V56 A16 16 0 0 1 80 40 H176 A16 16 0 0 1 192 56 V216'), L(32, 216, 224, 216), PG(panel)],
     area=[PG(panel)])

st = [(32, 208), (32, 168), (80, 168), (80, 128), (128, 128), (128, 88), (176, 88), (176, 48), (224, 48), (224, 208)]
icon('stairs', MP, ['steps', 'staircase', 'upstairs', 'floor', 'climb'], line=[PG(st)], area=[PG(st)])

icon('elevator', MP, ['lift', 'floor', 'up', 'down', 'building'],
     line=[R(48, 32, 160, 192, 16)], detail=[PL([(100, 108), (128, 80), (156, 108)]), PL([(100, 148), (128, 176), (156, 148)])],
     area=[R(48, 32, 160, 192, 16)])

wc = (108, 164)
a0, a1 = polar(wc, 56, -110), polar(wc, 56, 30)
icon('wheelchair', MP, ['accessibility', 'disabled', 'handicap', 'accessible', 'mobility'],
     line=[P(f'M{pt(a0)} ' + arc_to(wc, 56, a0, a1, lambda m: -m[0] + m[1])),
           PL([(124, 84), (124, 140), (176, 140), (200, 208), (216, 208)])],
     dot=[C(124, 48, 16)])

print(save(overwrite=True))
