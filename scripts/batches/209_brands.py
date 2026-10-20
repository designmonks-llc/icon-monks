"""Brand logos: payments, shopping, streaming and marketing."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)


def ipt(p):
    return (round(p[0]), round(p[1]))


def tile(name, tags, glyph, **kw):
    icon(name, B, tags + ['logo', 'brand'], area=[SQ], line=[SQ], detail=glyph, **kw)


# "Pay" set under a company mark, as in the Apple Pay and Google Pay marks: P, a, y on a 208 baseline.
PAY = [P('M44 208 V148 H64 A20 20 0 0 1 64 188 H44'),
       C(128, 188, 20), L(148, 168, 148, 208),
       L(172, 168, 192, 208), L(212, 168, 184, 224)]

# ---------------------------------------------------------------- payments

# Apple Pay: the bitten apple with its leaf, "Pay" beneath.
APPLE = ('M128 68 C122 64 114 62 108 62 C96 62 88 74 88 90 C88 106 98 120 108 120 C116 120 120 116 128 116 '
         'C136 116 140 120 148 120 C156 120 162 112 166 104 A16 16 0 0 1 162 74 C156 66 150 62 146 62 '
         'C140 62 134 64 128 68 Z')
LEAF = 'M132 44 C132 36 140 32 148 32 C148 40 140 44 132 44 Z'
icon('apple-pay-logo', B, ['apple pay', 'apple', 'payment', 'wallet', 'contactless', 'logo', 'brand'],
     area=[P(APPLE), P(LEAF)], line=[P(APPLE), P(LEAF)] + PAY)

# Google Pay: the G, "Pay" beneath.
icon('google-pay-logo', B, ['google pay', 'gpay', 'google', 'payment', 'wallet', 'logo', 'brand'],
     line=[P('M156 44 A40 40 0 1 0 168 72 H128')] + PAY, outline=True)

# ---------------------------------------------------------------- shopping

# Etsy: the serif E of the app tile.
tile('etsy-logo', ['etsy', 'handmade', 'marketplace', 'shopping', 'e'],
     [P('M168 92 V72 H84'), L(100, 72, 100, 184), P('M84 184 H172 V164'), L(100, 128, 148, 128),
      L(148, 116, 148, 140)])

# ---------------------------------------------------------------- streaming

# Disney+: the sweeping arc over the plus.
icon('disney-plus-logo', B, ['disney plus', 'disney+', 'disney', 'streaming', 'movies', 'logo', 'brand'],
     line=[P('M36 176 C52 104 88 64 128 64 C164 64 188 92 196 128'), L(196, 152, 196, 208), L(168, 180, 224, 180)])

# Prime Video: the app tile with a play mark over the smile arrow.
tile('prime-video-logo', ['prime video', 'amazon', 'prime', 'streaming', 'video', 'movies'],
     [PG([(108, 72), (156, 100), (108, 128)]), P('M68 156 C88 170 108 178 128 178 C152 178 172 172 184 164'),
      PL([(164, 156), (184, 164), (180, 184)])])

# ---------------------------------------------------------------- marketing

# Salesforce: the lumpy cloud, bumps on every side.
lobes = [((58, 139), 25), ((97, 102), 40), ((155, 102), 33), ((194, 131), 29), ((153, 157), 38), ((95, 160), 33)]
mid = (128, 130)
far = lambda m: dist(m, mid)
xs = []
for i in range(len(lobes)):
    (c1, r1), (c2, r2) = lobes[i], lobes[(i + 1) % len(lobes)]
    xs.append(ipt(max(circle_x(c1, r1, c2, r2), key=far)))
d = f'M{pt(xs[-1])}'
for i, (c, r) in enumerate(lobes):
    d += ' ' + arc_to(c, r, xs[i - 1], xs[i], far)
CLOUD = d + ' Z'
icon('salesforce-logo', B, ['salesforce', 'crm', 'cloud', 'sales', 'logo', 'brand'], area=[P(CLOUD)], line=[P(CLOUD)])

# HubSpot: the sprocket, a ring with three spokes ending in dots.
icon('hubspot-logo', B, ['hubspot', 'crm', 'marketing', 'sprocket', 'logo', 'brand'],
     area=[C(168, 144, 38)], hole=[C(168, 144, 22)],
     line=[C(168, 144, 38), L(168, 52, 168, 106), L(56, 48, 139, 119), L(104, 208, 141, 171)],
     dot=[C(168, 52, 16), C(56, 48, 16), C(104, 208, 16)])

# Mailchimp: Freddie's head in his cap, ear, winking eye and grin.
HEAD = ('M52 124 C56 72 92 34 128 34 C160 34 188 40 200 56 C204 64 196 70 172 80 '
        'C184 92 188 104 188 108 C204 116 212 128 212 140 V168 C212 200 184 220 148 220 '
        'C112 220 88 204 76 180 C60 168 52 148 52 124 Z')
icon('mailchimp-logo', B, ['mailchimp', 'email marketing', 'newsletter', 'freddie', 'chimp', 'logo', 'brand'],
     area=[P(HEAD), C(64, 152, 24)],
     line=[P(HEAD), C(64, 152, 24)],
     detail=[P('M172 80 C136 76 100 88 80 124'),
             P('M136 156 L212 148 C208 172 188 188 164 188 C148 188 138 176 136 156 Z')],
     dotcut=[C(148, 124, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
