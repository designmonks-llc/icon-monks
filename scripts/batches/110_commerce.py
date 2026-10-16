import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Commerce'
CC = (128, 128)
SLASH = L(48, 48, 208, 208)

# Bare currency glyphs are pure-line icons (no area); the -circle variants are coins like
# currency-dollar / currency-euro (circle r=96 as line + area, the sign as a knocked-out detail).
G = {}


def glyph(name, tags, paths, dots=()):
    G[name] = list(paths)
    icon(name, CM, tags, line=paths, dot=list(dots))


def coin(name, tags, sign):
    icon(name, CM, tags, line=[C(128, 128, 96)], area=[C(128, 128, 96)], detail=sign)


# ---- currency: generic sign, a ring with four diagonal ticks
ring = C(128, 128, 52)
ticks = {a: L(*polar(CC, 52, a), *polar(CC, 100, a)) for a in (45, 135, 225, 315)}
glyph('currency', ['currency', 'money sign', 'generic', 'exchange'], [ring] + list(ticks.values()))

glyph('currency-kip', ['currency kip', 'currency', 'money', 'kip', 'commerce'],
      [L(96, 40, 96, 216), PL([(176, 40), (96, 128), (176, 216)]), L(48, 128, 208, 128)])

glyph('currency-leu', ['currency leu', 'currency', 'money', 'leu', 'commerce'],
      [P('M96 40 V216 H192'), L(52, 128, 140, 128)])

sc = (136, 112)
glyph('currency-som', ['currency som', 'currency', 'money', 'som', 'commerce'],
      [P(f'M{pt(polar(sc, 68, -40))} A68 68 0 1 0 {pt(polar(sc, 68, 40))}'), L(64, 216, 192, 216)])

glyph('currency-won', ['won', 'krw', 'korea money', 'currency won', 'currency'],
      [PL([(40, 56), (80, 200), (128, 80), (176, 200), (216, 56)]), L(40, 112, 216, 112), L(40, 148, 216, 148)])

YEN_Y = [PL([(64, 40), (128, 120), (192, 40)]), L(128, 120, 128, 216)]
glyph('currency-yen', ['yen', 'yuan', 'jpy', 'currency', 'money'],
      YEN_Y + [L(80, 152, 176, 152), L(80, 188, 176, 188)])

glyph('currency-baht', ['currency baht', 'currency', 'money', 'baht', 'commerce'],
      [P('M80 124 H144 A38 38 0 0 1 144 200 H80 V56 H136 A34 34 0 0 1 136 124'), L(120, 32, 120, 224)])

cc = (140, 128)
glyph('currency-cent', ['currency cent', 'currency', 'money', 'cent', 'commerce'],
      [P(f'M{pt(polar(cc, 64, -45))} A64 64 0 1 0 {pt(polar(cc, 64, 45))}'), L(140, 40, 140, 216)])

glyph('currency-dong', ['currency dong', 'currency', 'money', 'dong', 'commerce'],
      [C(112, 140, 44), L(156, 40, 156, 184), L(132, 68, 196, 68), L(68, 216, 192, 216)])

glyph('currency-dram', ['currency dram', 'currency', 'money', 'dram', 'commerce'],
      [P('M196 140 V100 A56 56 0 0 0 84 100 V216'), L(52, 152, 124, 152), L(52, 188, 124, 188)])

glyph('currency-lari', ['currency lari', 'currency', 'money', 'lari', 'commerce'],
      [P('M200 208 H128 A64 64 0 1 1 192 144'), L(108, 40, 108, 120), L(148, 40, 148, 120)])

glyph('currency-lira', ['lira', 'try', 'turkey', 'currency', 'money'],
      [P('M96 40 V208 H120 A72 72 0 0 0 192 136'), L(56, 140, 140, 104), L(56, 180, 140, 144)])

glyph('currency-peso', ['currency peso', 'currency', 'money', 'peso', 'commerce'],
      [P('M88 216 V40 H136 A48 48 0 0 1 136 136 H88'), L(48, 72, 208, 72), L(48, 104, 208, 104)])

glyph('currency-real', ['currency real', 'currency', 'money', 'real', 'commerce'],
      [P('M44 192 V64 H80 A32 32 0 0 1 80 128 H44'), L(76, 128, 112, 192),
       P('M208 88 H164 A20 20 0 0 0 164 128 H188 A20 20 0 0 1 188 168 H144'), L(176, 56, 176, 200)])

glyph('currency-taka', ['currency taka', 'currency', 'money', 'taka', 'commerce'],
      [P('M64 64 A24 24 0 0 1 112 64 V168 A40 40 0 0 0 192 168 V148'), L(64, 112, 176, 112)])

glyph('currency-yuan', ['yuan', 'cny', 'renminbi', 'currency', 'currency yuan'],
      YEN_Y + [L(80, 160, 176, 160)])

glyph('currency-dinar', ['currency dinar', 'currency', 'money', 'dinar', 'commerce'],
      [P('M96 48 C156 72 196 112 196 160 V176 A24 24 0 0 1 172 200 H100')], dots=[C(56, 200, 16)])

glyph('currency-franc', ['franc', 'chf', 'currency', 'money', 'currency franc'],
      [P('M184 48 H88 V216'), L(88, 120, 168, 120), L(48, 172, 136, 172)])

glyph('currency-krone', ['currency krone', 'currency', 'money', 'krone', 'commerce'],
      [L(56, 40, 56, 216), L(124, 108, 56, 164), L(84, 141, 128, 216),
       L(160, 112, 160, 216), P('M160 160 C160 128 180 112 208 112')])

glyph('currency-manat', ['currency manat', 'currency', 'money', 'manat', 'commerce'],
      [P('M56 216 V160 A72 72 0 0 1 200 160 V216'), L(128, 40, 128, 216)])

glyph('currency-naira', ['naira', 'ngn', 'nigeria money', 'currency naira', 'currency'],
      [P('M72 216 V40 L184 216 V40'), L(40, 112, 216, 112), L(40, 148, 216, 148)])

pc = (144, 88)
POUND = [P(f'M{pt(polar(pc, 40, -30))} A40 40 0 0 0 104 88 V168 C104 192 88 208 64 208 H192'),
         L(64, 136, 152, 136)]
glyph('currency-pound', ['pound sterling', 'gbp', 'uk money', 'pound', 'sterling'], POUND)

glyph('currency-ruble', ['ruble', 'rub', 'russia money', 'currency', 'money'],
      [P('M56 136 H144 A44 44 0 0 0 144 48 H96 V216'), L(56, 176, 152, 176)])

glyph('currency-rupee', ['rupee', 'inr', 'india money', 'currency', 'money'],
      [L(64, 48, 192, 48), L(64, 88, 192, 88), P('M144 48 A40 40 0 0 1 144 128 H72 L176 216')])

icon('currency-slash', CM, ['currency', 'disabled', 'off', 'money', 'commerce'],
     line=[ring, ticks[135], ticks[315], SLASH])

glyph('currency-tenge', ['tenge', 'kzt', 'kazakhstan money', 'currency tenge', 'currency'],
      [L(56, 48, 200, 48), L(56, 88, 200, 88), L(128, 88, 128, 216)])

glyph('currency-zloty', ['currency zloty', 'currency', 'money', 'zloty', 'commerce'],
      [PL([(56, 112), (120, 112), (56, 208), (120, 208)]), L(176, 40, 176, 208), L(152, 140, 200, 108)])

glyph('currency-dirham', ['currency dirham', 'currency', 'money', 'dirham', 'commerce'],
      [P('M80 48 H112 A80 80 0 0 1 112 208 H80 Z'), L(48, 108, 212, 108), L(48, 148, 212, 148)])

glyph('currency-florin', ['currency florin', 'currency', 'money', 'florin', 'commerce'],
      [P('M192 64 C176 40 144 40 136 72 L116 184 C108 216 76 216 64 196'), L(88, 120, 176, 120)])

glyph('currency-forint', ['currency forint', 'currency', 'money', 'forint', 'commerce'],
      [P('M128 48 H64 V208'), L(64, 124, 112, 124), P('M168 64 V180 A28 28 0 0 0 196 208 H204'), L(140, 112, 204, 112)])

glyph('currency-shekel', ['currency shekel', 'currency', 'money', 'shekel', 'commerce'],
      [P('M48 208 V88 A40 40 0 0 1 88 48 H108 A40 40 0 0 1 148 88 V160'),
       P('M208 48 V168 A40 40 0 0 1 168 208 H148 A40 40 0 0 1 108 168 V96')])

glyph('currency-tugrik', ['currency tugrik', 'currency', 'money', 'tugrik', 'commerce'],
      [L(56, 48, 200, 48), L(128, 48, 128, 216), L(88, 152, 168, 120), L(88, 192, 168, 160)])

glyph('currency-bitcoin', ['bitcoin', 'crypto', 'btc', 'currency', 'money'],
      [P('M64 64 H140 A30 30 0 0 1 140 124 H80'), P('M80 124 H148 A34 34 0 0 1 148 192 H64'), L(80, 64, 80, 192),
       L(104, 32, 104, 64), L(140, 32, 140, 64), L(104, 192, 104, 224), L(140, 192, 140, 224)])

gc = (128, 128)
glyph('currency-guarani', ['currency guarani', 'currency', 'money', 'guarani', 'commerce'],
      [P(f'M{pt(polar(gc, 76, -40))} A76 76 0 1 0 204 128 H160'), L(128, 32, 128, 224)])

glyph('currency-hryvnia', ['currency hryvnia', 'currency', 'money', 'hryvnia', 'commerce'],
      [P('M84 72 A44 36 0 0 1 172 72 C172 112 84 144 84 180 A44 36 0 0 0 172 184'),
       L(48, 112, 208, 112), L(48, 148, 208, 148)])

glyph('currency-quetzal', ['currency quetzal', 'currency', 'money', 'quetzal', 'commerce'],
      [C(128, 120, 76), L(148, 160, 200, 212)])

# ---- currency-exchange: two coins in opposite corners, swap arrows in the other two
c1, c2, cr = (80, 80), (176, 176), 44
def curved_arrow(a0, a1, r=90):
    p0, p1 = polar(CC, r, a0), polar(CC, r, a1)
    arc = f'M{pt(p0)} A{r} {r} 0 0 1 {pt(p1)}'
    t = math.radians(a1)
    d = (-math.sin(t), math.cos(t))           # travel direction at the end
    back = (-d[0], -d[1])
    heads = [rot([(p1[0] + back[0] * 28, p1[1] + back[1] * 28)], s, p1)[0] for s in (-45, 45)]
    return [P(arc), PL([heads[0], p1, heads[1]])]
icon('currency-exchange', CM, ['exchange', 'conversion', 'currency', 'forex', 'convert'],
     line=[C(*c1, cr), C(*c2, cr)] + curved_arrow(-76, -22) + curved_arrow(104, 158),
     area=[C(*c1, cr), C(*c2, cr)])

# ---- slash variants (no area so the slash reads in the fill weight)
icon('currency-yen-slash', CM, ['currency yen', 'disabled', 'off', 'currency', 'money'],
     line=G['currency-yen'] + [SLASH])
icon('currency-pound-slash', CM, ['currency pound', 'disabled', 'off', 'currency', 'money'],
     line=G['currency-pound'] + [SLASH])
# currency-dollar / currency-euro are coins; their slash variants use the bare sign (same construction
# as the coin's sign, enlarged) so every currency slash icon reads the same way.
ec2 = (152, 128)
EURO = [P(f'M{pt(polar(ec2, 72, -45))} ' + arc_to(ec2, 72, polar(ec2, 72, -45), polar(ec2, 72, 45), lambda m: -m[0])),
        L(48, 108, 136, 108), L(48, 148, 136, 148)]
DOLLAR = [L(128, 40, 128, 216), P('M176 76 H104 A26 26 0 0 0 104 128 H152 A26 26 0 0 1 152 180 H80')]
icon('currency-euro-slash', CM, ['currency euro', 'disabled', 'off', 'currency', 'money'], line=EURO + [SLASH])
icon('currency-dollar-slash', CM, ['currency dollar', 'disabled', 'off', 'currency', 'money'], line=DOLLAR + [SLASH])

# ---- coin variants
coin('currency-yen-circle', ['yen', 'jpy', 'coin', 'currency'],
     [PL([(92, 72), (128, 116), (164, 72)]), L(128, 116, 128, 192), L(96, 140, 160, 140), L(96, 172, 160, 172)])
coin('currency-yuan-circle', ['yuan', 'renminbi', 'money', 'coin'],
     [PL([(92, 72), (128, 116), (164, 72)]), L(128, 116, 128, 192), L(96, 152, 160, 152)])
pc2 = (140, 96)
coin('currency-pound-circle', ['pound', 'gbp', 'coin', 'currency', 'sterling'],
     [P(f'M{pt(polar(pc2, 28, -30))} A28 28 0 0 0 112 96 V160 C112 172 104 184 88 184 H168'), L(88, 136, 140, 136)])
coin('currency-rupee-circle', ['rupee', 'india', 'money', 'coin'],
     [L(88, 72, 168, 72), L(88, 104, 168, 104), P('M136 72 A32 32 0 0 1 136 136 H96 L156 188')])
src = load('currency-euro')
coin('currency-euro-circle', ['euro', 'coin', 'money', 'currency', 'eur'], src['detail'])
src = load('currency-dollar')
coin('currency-dollar-circle', ['dollar', 'usd', 'coin', 'currency', 'money'], src['detail'])
icon('currency-dollar-square', CM, ['dollar', 'usd', 'square', 'currency'],
     line=[R(32, 32, 192, 192, 16)], area=[R(32, 32, 192, 192, 16)], detail=src['detail'])

# ---- envelope-gift: portrait red envelope, flap meeting a coin seal
sc2, sr = (128, 116), 26
def toward(p, c, r):
    d = dist(p, c)
    return (c[0] + (p[0] - c[0]) * r / d, c[1] + (p[1] - c[1]) * r / d)
env = R(56, 32, 144, 192, 14)
icon('envelope-gift', CM, ['red envelope', 'hongbao', 'gift money', 'lucky money'],
     line=[env], area=[env],
     detail=[L(72, 76, *toward((72, 76), sc2, sr)), L(184, 76, *toward((184, 76), sc2, sr)), C(*sc2, sr)])

print(save(overwrite=True))
