"""Brand logos: banks, fintech, accounting and crypto."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


# Pointy-top hexagon on the circle keyline (r=96).
HEX = PG([(128, 32), (211, 80), (211, 176), (128, 224), (45, 176), (45, 80)])

# ---------------------------------------------------------------- banks
# Chase: the octagon around a square hole, split into four pieces by the pinwheel cuts.
OCT = PG([(88, 32), (168, 32), (224, 88), (224, 168), (168, 224), (88, 224), (32, 168), (32, 88)])
SQ_HOLE = R(104, 104, 48, 48)
brand('chase-logo', ['chase', 'jpmorgan chase', 'bank', 'banking', 'finance'],
      area=[OCT], line=[OCT], hole=[SQ_HOLE],
      detail=[SQ_HOLE, L(152, 104, 224, 104), L(152, 152, 152, 224), L(104, 152, 32, 152), L(104, 104, 104, 32)])

# Bank of America: the flag, three short stripes on the left and three long ones on the right.
brand('bank-of-america-logo', ['bank of america', 'bofa', 'bank', 'banking', 'flag', 'finance'],
      line=[L(32, 98 + 32 * i, 92, 122 + 32 * i) for i in range(3)]
      + [L(116, 70 + 32 * i, 224, 114 + 32 * i) for i in range(3)])

# HSBC: the hexagon, a square between two points, crossed by its diagonals.
HSBC = PG([(32, 128), (80, 80), (176, 80), (224, 128), (176, 176), (80, 176)])
brand('hsbc-logo', ['hsbc', 'bank', 'banking', 'hexagon', 'finance'],
      area=[HSBC], line=[HSBC],
      detail=[L(80, 80, 80, 176), L(176, 80, 176, 176), L(80, 80, 176, 176), L(176, 80, 80, 176)])

# Barclays is left out: the eagle reduces to a shield-like blob.

# Santander: the flame rising out of the dish.
DISH = ('M104 132 C68 136 40 152 40 176 C40 200 80 216 128 216 C176 216 216 200 216 176 '
        'C216 152 188 136 152 132 C144 140 136 144 128 144 C120 144 112 140 104 132 Z')
FLAME = 'M128 120 C104 108 92 96 92 80 C92 64 104 52 112 32 C140 48 164 68 164 92 C164 108 148 118 128 120 Z'
brand('santander-logo', ['santander', 'banco santander', 'bank', 'banking', 'flame', 'finance'],
      area=[P(DISH), P(FLAME)], line=[P(DISH), P(FLAME)])

# ---------------------------------------------------------------- fintech
# SoFi: the 3 x 3 grid of dots, the anti-diagonal left as rings.
SOFI = [(x, y) for y in (60, 128, 196) for x in (60, 128, 196)]
RINGS = {(196, 60), (128, 128), (60, 196)}
brand('sofi-logo', ['sofi', 'social finance', 'fintech', 'banking', 'loans', 'finance'],
      area=[C(x, y, 22) for x, y in SOFI if (x, y) not in RINGS], line=[C(x, y, 22) for x, y in SOFI],
      reviewed=True)

# Nubank: the lowercase nu, an arch followed by a cup.
brand('nubank-logo', ['nubank', 'nu', 'bank', 'fintech', 'brazil', 'finance'],
      line=[P('M40 192 V102 A38 38 0 0 1 116 102 V192'), P('M140 64 V154 A38 38 0 0 0 216 154 V64')])

# Plaid: the diagonal lattice inside its eight-sided frame.
PLAID = PG([(72, 40), (184, 40), (216, 72), (216, 184), (184, 216), (72, 216), (40, 184), (40, 72)])
brand('plaid-logo', ['plaid', 'fintech', 'banking api', 'payments', 'finance'],
      area=[PLAID], line=[PLAID],
      detail=[L(168, 40, 40, 168), L(200, 56, 56, 200), L(216, 88, 88, 216),
              L(88, 40, 216, 168), L(56, 56, 200, 200), L(40, 88, 168, 216)])

# Ramp: the curved ramp sweeping up to the right, over the small wedge.
RAMP = 'M32 184 C104 168 160 112 166 32 L198 62 C192 144 128 208 40 216 L32 208 Z'
WEDGE = 'M164 176 H196 L224 216 H140 C148 204 156 192 164 176 Z'
brand('ramp-logo', ['ramp', 'corporate card', 'expenses', 'fintech', 'finance'],
      area=[P(RAMP), P(WEDGE)], line=[P(RAMP), P(WEDGE)])

# ---------------------------------------------------------------- accounting and payroll
# QuickBooks: the q and b facing each other in the circle.
brand('quickbooks-logo', ['quickbooks', 'intuit', 'accounting', 'bookkeeping', 'qb', 'finance'],
      area=[RING], line=[RING],
      detail=[P('M100 160 A32 32 0 0 1 100 96 H116 V196'), P('M156 96 A32 32 0 0 1 156 160 H140 V60')])

# Deel: the lowercase d and its full stop in a circle.
brand('deel-logo', ['deel', 'payroll', 'hr', 'hiring', 'remote work'],
      area=[RING], line=[RING],
      detail=[C(108, 144, 32), L(140, 72, 140, 176)], dot=[C(168, 168, 16)])

# Rippling: three ribbon shapes in a row, each a lobe over a straight leg.
brand('rippling-logo', ['rippling', 'hr', 'payroll', 'workforce', 'it management'],
      line=[P(f'M{x} 64 C{x + 20} 64 {x + 32} 80 {x + 32} 96 C{x + 32} 112 {x + 20} 124 {x + 8} 128 '
              f'C{x + 20} 132 {x + 28} 144 {x + 28} 160 V192')
            for x in (48, 112, 176)])

# ---------------------------------------------------------------- crypto
# Crypto.com: the lion's face (crown, nose and jaw) in the hexagon.
brand('crypto-com-logo', ['crypto.com', 'crypto', 'cryptocurrency', 'exchange', 'lion'],
      area=[HEX], line=[HEX],
      detail=[PG([(92, 84), (164, 84), (156, 104), (100, 104)]),
              PL([(116, 128), (116, 148), (128, 156), (140, 148), (140, 128)]),
              PL([(84, 128), (100, 172), (128, 192), (156, 172), (172, 128)])])

# OKX: five squares set out as an X on a 3 x 3 grid.
OKX = [R(x, y, 44, 44, 4) for x, y in ((40, 40), (172, 40), (106, 106), (40, 172), (172, 172))]
brand('okx-logo', ['okx', 'crypto', 'exchange', 'trading', 'cryptocurrency'],
      area=OKX, line=OKX)

# KuCoin: the K, its arms bent into a diamond around the inner chevron and dot.
brand('kucoin-logo', ['kucoin', 'crypto', 'exchange', 'trading', 'cryptocurrency'],
      line=[L(60, 56, 60, 200), PL([(60, 118), (159, 36), (196, 66), (196, 104)]),
            PL([(60, 138), (159, 220), (196, 190), (196, 152)])],
      detail=[PL([(159, 73), (104, 128), (159, 183)])], dot=[C(159, 128, 16)])

# Uniswap is left out: the unicorn does not survive the reduction to a few strokes.

# Phantom: the leaning ghost with a wavy hem and two eyes.
GHOST = ('M40 200 C40 116 92 52 152 52 C192 52 216 84 216 124 C216 172 192 200 172 200 '
         'C156 200 152 180 140 180 C128 180 124 200 104 200 C92 200 88 184 76 184 C64 184 60 200 40 200 Z')
brand('phantom-logo', ['phantom', 'crypto wallet', 'wallet', 'solana', 'ghost', 'cryptocurrency'],
      area=[P(GHOST)], line=[P(GHOST)], dotcut=[C(144, 112, 14), C(188, 112, 14)])

# Polygon: two hexagons linked through a shared side, each left open by a short inner tick.
brand('polygon-logo', ['polygon', 'matic', 'pol', 'crypto', 'blockchain', 'cryptocurrency'],
      line=[P('M104 136 V114 L80 100 L32 128 V176 L80 204 L128 176 V80 L176 52 L224 80 V128 L176 156 '
              'L152 142 V120')])

# Avalanche: the split A, a tall triangle beside a small one, in the circle.
brand('avalanche-logo', ['avalanche', 'avax', 'crypto', 'blockchain', 'cryptocurrency'],
      area=[RING], line=[RING],
      detail=[PG([(128, 72), (148, 104), (110, 168), (72, 168)]), PG([(164, 128), (186, 168), (142, 168)])])

# Chainlink: the thick hexagon ring.
HEX_IN = PG([(128, 80), (170, 104), (170, 152), (128, 176), (86, 152), (86, 104)])
brand('chainlink-logo', ['chainlink', 'link', 'oracle', 'crypto', 'blockchain', 'cryptocurrency'],
      area=[HEX], line=[HEX, HEX_IN], hole=[HEX_IN])

# TRON: the faceted triangle with its facet lines meeting off centre.
TRON = PG([(36, 40), (176, 64), (220, 104), (112, 220)])
brand('tron-logo', ['tron', 'trx', 'crypto', 'blockchain', 'cryptocurrency'],
      area=[TRON], line=[TRON],
      detail=[PL([(36, 40), (132, 116), (112, 220)]), L(176, 64, 132, 116), L(220, 104, 132, 116)])

# TON: the downward triangle split down the middle, in the circle.
brand('ton-logo', ['ton', 'toncoin', 'the open network', 'telegram', 'crypto', 'blockchain'],
      area=[RING], line=[RING],
      detail=[PG([(76, 92), (180, 92), (128, 184)]), L(128, 92, 128, 184)])

# Shiba Inu is left out: the dog face reads as a generic dog at icon size.

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
