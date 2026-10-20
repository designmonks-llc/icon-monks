"""Brand logos: regional apps, shopping, fashion and social."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


# ---------------------------------------------------------------- search and social
# Yandex: the mirrored R (Я) in a circle.
brand('yandex-logo', ['yandex', 'search engine', 'search', 'russia'],
      area=[RING], line=[RING],
      detail=[P('M156 72 V184 M156 72 H128 A28 28 0 0 0 128 128 H156'), L(128, 128, 100, 184)])

# QQ: the round penguin with its scarf and the scarf's hanging end.
qq = ('M128 32 C164 32 188 60 188 96 V112 C204 136 216 160 216 180 C216 186 214 190 210 190 '
      'C204 190 200 186 196 170 C192 198 164 216 128 216 C92 216 64 198 60 170 '
      'C52 186 48 190 46 190 C42 190 40 186 40 180 C40 160 52 136 68 112 V96 C68 60 92 32 128 32 Z')
brand('qq-logo', ['qq', 'tencent', 'messaging', 'chat', 'penguin', 'china'],
      area=[P(qq)], line=[P(qq)],
      detail=[E(128, 100, 24, 8), P('M66 128 C80 134 104 138 128 138 C152 138 176 134 190 128'), L(108, 140, 108, 176)],
      dotcut=[C(108, 66, 14), C(148, 66, 14)])

# Weibo: the eye in its rounded blob, with two signal arcs at the top right.
wb = ('M32 156 C32 116 76 64 116 64 C128 64 130 78 128 92 C136 88 144 84 152 84 C166 84 178 92 178 104 '
      'C178 112 176 118 172 122 C196 128 208 142 208 160 C208 188 168 208 116 208 C64 208 32 188 32 156 Z')
brand('weibo-logo', ['weibo', 'sina weibo', 'social media', 'microblog', 'china'],
      area=[P(wb)], line=[P(wb), P('M176 44 A48 48 0 0 1 224 92'), P('M176 68 A24 24 0 0 1 200 92')],
      detail=[E(116, 156, 56, 28)], dotcut=[C(108, 160, 14)])

# Bilibili: the TV with two antennae and two eyes.
tv = R(32, 72, 192, 144, 32)
brand('bilibili-logo', ['bilibili', 'video', 'anime', 'streaming', 'china'],
      area=[tv], line=[tv, L(76, 36, 100, 72), L(180, 36, 156, 72)],
      detail=[L(92, 124, 92, 156), L(164, 124, 164, 156)])

# Jio: the wordmark in its circle.
brand('jio-logo', ['jio', 'reliance jio', 'telecom', 'mobile network', 'india'],
      area=[RING], line=[RING],
      detail=[P('M84 84 V148 C84 164 76 172 60 172'), L(116, 124, 116, 172), C(164, 148, 24)],
      dotcut=[C(116, 92, 14)])

# ---------------------------------------------------------------- shopping
# Flipkart: the shopping bag with its italic f.
bag = R(40, 80, 176, 144, 16)
brand('flipkart-logo', ['flipkart', 'shopping', 'ecommerce', 'store', 'india'],
      area=[bag], line=[bag, P('M92 80 V68 A36 36 0 0 1 164 68 V80')],
      detail=[P('M164 120 C160 112 152 108 144 108 C132 108 124 116 122 128 L112 192'), L(100, 148, 148, 148)])

# Shopee: the bag with the arched handle and the S.
sb = 'M44 88 H212 L200 208 A16 16 0 0 1 184 224 H72 A16 16 0 0 1 56 208 Z'
brand('shopee-logo', ['shopee', 'shopping', 'ecommerce', 'store', 'southeast asia'],
      area=[P(sb)], line=[P(sb), P('M92 88 C92 56 108 32 128 32 C148 32 164 56 164 88')],
      detail=[P('M156 124 C148 116 140 112 128 112 C114 112 104 120 104 132 C104 156 152 148 152 172 '
                'C152 186 140 192 128 192 C116 192 106 188 98 180')])

# Lazada: the heart-shaped box, its lid folded into a V.
lz = P('M36 72 L80 44 L128 72 L176 44 L220 72 V140 C220 164 172 192 128 212 C84 192 36 164 36 140 Z')
brand('lazada-logo', ['lazada', 'shopping', 'ecommerce', 'alibaba', 'southeast asia'],
      area=[lz], line=[lz], detail=[PL([(36, 72), (128, 120), (220, 72)]), L(128, 120, 128, 212)])


def teardrop(deg, r1=44, w1=4, r2=80, w2=14):
    """One Walmart spark ray: a small round end near the centre and a big one outside."""
    c1, c2 = polar((128, 128), r1, deg), polar((128, 128), r2, deg)
    a = math.radians(deg)
    # tangent angle between the two circles
    d = r2 - r1
    phi = math.asin((w2 - w1) / d)
    n1 = (math.cos(a + math.pi / 2 + phi), math.sin(a + math.pi / 2 + phi))
    n2 = (math.cos(a - math.pi / 2 - phi), math.sin(a - math.pi / 2 - phi))
    p1 = ipt((c1[0] + n1[0] * w1, c1[1] + n1[1] * w1)); q1 = ipt((c2[0] + n1[0] * w2, c2[1] + n1[1] * w2))
    q2 = ipt((c2[0] + n2[0] * w2, c2[1] + n2[1] * w2)); p2 = ipt((c1[0] + n2[0] * w1, c1[1] + n2[1] * w1))
    return P(f'M{pt(p1)} L{pt(q1)} A{w2} {w2} 0 0 0 {pt(q2)} L{pt(p2)} A{w1} {w1} 0 0 0 {pt(p1)} Z')


# Walmart: the spark, six rays swelling outwards.
rays = [teardrop(d) for d in (-90, -30, 30, 90, 150, 210)]
brand('walmart-logo', ['walmart', 'spark', 'retail', 'supermarket', 'store', 'shopping'],
      area=rays, line=rays)

# Target: the retailer's bullseye, a thick ring round a solid centre disc.
annulus = P('M32 128 A96 96 0 1 1 224 128 A96 96 0 1 1 32 128 Z M56 128 A72 72 0 1 0 200 128 A72 72 0 1 0 56 128 Z')
brand('target-logo', ['target', 'target corporation', 'bullseye', 'retail', 'store', 'shopping'],
      area=[annulus, C(128, 128, 36)], line=[RING, C(128, 128, 72), C(128, 128, 36)])

# ---------------------------------------------------------------- fashion
# H&M: the slanted script letters.
brand('h-and-m-logo', ['h&m', 'h and m', 'hennes mauritz', 'fashion', 'clothing', 'retail'], outline=True,
      line=[L(64, 56, 48, 192), L(100, 56, 84, 192), L(52, 128, 96, 124),
            P('M136 192 L114 160 C110 154 108 150 108 146 C108 140 114 136 120 136 C126 136 130 140 130 146 '
              'C130 150 128 154 122 158 L110 168 C104 174 102 178 102 182 C102 188 108 192 116 192 '
              'C124 192 130 188 134 180'),
            PL([(148, 192), (176, 56), (184, 160), (224, 56), (208, 192)])])

# adidas: the three slanted bars rising like a mountain.
def bar(x, h, w=36):
    u = (-0.5, -math.sqrt(3) / 2); p = (math.sqrt(3) / 2, -0.5)
    L_ = h / (math.sqrt(3) / 2)
    br = (x + w, 204); tr = (br[0] + u[0] * L_, br[1] + u[1] * L_)
    tl = (tr[0] - p[0] * w * math.sqrt(3) / 2, tr[1] - p[1] * w * math.sqrt(3) / 2)
    return PG([(x, 204), br, ipt(tr), ipt(tl)])


bars = [bar(56, 56), bar(120, 104), bar(184, 152)]
brand('adidas-logo', ['adidas', 'sportswear', 'fashion', 'three stripes', 'sport'],
      area=bars, line=bars)

# Puma: the leaping cat, tail and front leg as single strokes.
cat = ('M33 91 C36 84 40 78 46 74 L50 62 L60 74 C72 76 96 84 112 98 C128 112 140 130 156 138 '
       'C162 140 170 140 174 140 C178 150 182 166 182 190 H152 C146 172 132 156 116 152 '
       'C100 148 88 140 80 128 C68 116 52 108 40 102 C34 100 32 96 33 91 Z')
brand('puma-logo', ['puma', 'sportswear', 'fashion', 'cat', 'sport'],
      area=[P(cat)], line=[P(cat), P('M170 140 C196 132 192 96 220 72'), P('M84 128 C68 126 52 128 36 128')])

# Under Armour: the interlocked U and A, with the lens where they cross.
ua = ('M32 91 C48 81 68 75 84 72 V87 C84 94 92 97 104 97 C112 97 120 94 128 94 C136 94 144 97 152 97 '
      'C164 97 172 94 172 87 V72 C188 75 208 81 224 91 C224 106 204 122 188 128 C204 134 224 150 224 165 '
      'C208 175 188 181 172 184 V169 C172 162 164 159 152 159 C144 159 136 162 128 162 C120 162 112 159 104 159 '
      'C92 159 84 162 84 169 V184 C68 181 48 175 32 165 C32 150 52 134 68 128 C52 122 32 106 32 91 Z')
brand('under-armour-logo', ['under armour', 'sportswear', 'fashion', 'sport', 'athletic'],
      area=[P(ua)], line=[P(ua)], detail=[E(128, 128, 36, 10)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
