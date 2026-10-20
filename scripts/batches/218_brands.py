"""Brand logos: banking, payments, crypto, security and browsers."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


def flip(points):
    return [(x, 256 - y) for x, y in points]


# ---------------------------------------------------------------- banking
# Monzo: the M with rounded pillar tops and the chevron between them.
MONZO = ('M40 196 V80 A16 16 0 0 1 68 70 L128 132 L188 70 A16 16 0 0 1 216 80 V196 H176 V140 L128 188 '
         'L80 140 V196 Z')
brand('monzo-logo', ['monzo', 'bank', 'banking', 'fintech', 'finance'],
      area=[P(MONZO)], line=[P(MONZO)])

# N26: the N between its two bars.
brand('n26-logo', ['n26', 'bank', 'banking', 'fintech', 'finance'],
      line=[PL([(84, 188), (84, 76), (172, 180), (172, 68)]), L(84, 36, 172, 36), L(84, 220, 172, 220)],
      outline=True)

# Chime, Revolut: wordmark or a plain letter; no symbol to draw.

# ---------------------------------------------------------------- payments
# Venmo: the swung v on the app tile.
brand('venmo-logo', ['venmo', 'paypal', 'payments', 'money transfer', 'finance'],
      area=[SQ], line=[SQ],
      detail=[P('M84 80 L108 176 C140 144 172 112 172 80')])

# Zelle: the Z with the bar through it.
brand('zelle-logo', ['zelle', 'payments', 'money transfer', 'bank', 'finance'],
      area=[SQ], line=[SQ],
      detail=[PL([(84, 92), (172, 92), (84, 164), (172, 164)]), L(128, 64, 128, 92), L(128, 164, 128, 192)])

# SumUp: the S made of two half discs split along the diagonal.
far1 = lambda m: dist(m, (176, 176))
far2 = lambda m: dist(m, (80, 80))
SU1 = 'M152 80 ' + arc_to((116, 116), dist((152, 80), (80, 152)) / 2, (152, 80), (80, 152), far1) + ' Z'
SU2 = 'M104 176 ' + arc_to((140, 140), dist((176, 104), (104, 176)) / 2, (104, 176), (176, 104), far2) + ' Z'
brand('sumup-logo', ['sumup', 'payments', 'card reader', 'point of sale', 'finance'],
      area=[SQ], line=[SQ], detail=[P(SU1), P(SU2)])

# PhonePe: the Devanagari pe in a circle.
brand('phonepe-logo', ['phonepe', 'upi', 'payments', 'india', 'finance'],
      area=[RING], line=[RING],
      detail=[L(84, 100, 176, 100), L(152, 100, 152, 192), P('M100 100 V120 C100 140 112 148 128 148 H152'),
              L(116, 100, 92, 64)])

# Razorpay: the slanted blade with the small wedge at its foot.
RP_BLADE = [(128, 96), (216, 36), (168, 216), (124, 216), (152, 124)]
RP_WEDGE = [(40, 216), (60, 172), (112, 152), (92, 216)]
brand('razorpay-logo', ['razorpay', 'payments', 'payment gateway', 'india', 'finance'],
      area=[PG(RP_BLADE), PG(RP_WEDGE)], line=[PG(RP_BLADE), PG(RP_WEDGE)])

# ---------------------------------------------------------------- investing and crypto
# Robinhood: the feather.
FEATHER = 'M76 184 C76 136 104 84 160 56 L212 40 C208 76 196 108 176 136 C152 168 116 184 76 184 Z'
brand('robinhood-logo', ['robinhood', 'investing', 'stocks', 'trading', 'feather', 'finance'],
      area=[P(FEATHER)], line=[P(FEATHER), L(48, 216, 76, 184)],
      detail=[L(76, 184, 176, 84)])

# Binance: the centre diamond, the two side diamonds and the top and bottom chevrons.
BN_TOP = [(128, 32), (180, 84), (160, 104), (128, 72), (96, 104), (76, 84)]
BN = [PG([(128, 108), (148, 128), (128, 148), (108, 128)]),
      PG([(52, 108), (72, 128), (52, 148), (32, 128)]),
      PG([(204, 108), (224, 128), (204, 148), (184, 128)]),
      PG(BN_TOP), PG(flip(BN_TOP))]
brand('binance-logo', ['binance', 'crypto', 'exchange', 'bnb', 'trading'],
      area=BN, line=BN)

# Kraken: the dome on four legs.
KR = 'M48 196 V140 A80 80 0 0 1 208 140 V196'
brand('kraken-logo', ['kraken', 'crypto', 'exchange', 'bitcoin', 'trading'],
      area=[P(KR + ' Z')], line=[P(KR)],
      detail=[L(101, 140, 101, 196), L(155, 140, 155, 196)])

# MetaMask: the fox head.
FOX = [(32, 36), (100, 92), (156, 92), (224, 36), (212, 120), (224, 156), (172, 196), (148, 216), (108, 216),
       (84, 196), (32, 156), (44, 120)]
brand('metamask-logo', ['metamask', 'crypto', 'wallet', 'ethereum', 'fox', 'web3'],
      area=[PG(FOX)], line=[PG(FOX)],
      detail=[PL([(108, 184), (128, 196), (148, 184)]), PL([(44, 120), (100, 92)]), PL([(212, 120), (156, 92)])],
      dotcut=[C(96, 144, 14), C(160, 144, 14)])

# Solana: three slanted bars, the middle one leaning the other way.
SOL = [PG([(68, 56), (216, 56), (188, 84), (40, 84)]),
       PG([(40, 114), (188, 114), (216, 142), (68, 142)]),
       PG([(68, 172), (216, 172), (188, 200), (40, 200)])]
brand('solana-logo', ['solana', 'sol', 'crypto', 'cryptocurrency', 'blockchain'],
      area=SOL, line=SOL)

# Cardano: rings of dots around the centre.
CA = [polar((128, 128), 44, a) for a in range(-90, 270, 60)] + [polar((128, 128), 84, a) for a in range(-60, 300, 60)]
brand('cardano-logo', ['cardano', 'ada', 'crypto', 'cryptocurrency', 'blockchain'],
      dot=[C(round(x), round(y), 16) for x, y in CA])

# Dogecoin: the barred D on a coin.
brand('dogecoin-logo', ['dogecoin', 'doge', 'crypto', 'cryptocurrency', 'coin'],
      area=[RING], line=[RING],
      detail=[P('M96 76 H124 C160 76 180 100 180 128 C180 156 160 180 124 180 H96 Z'), L(72, 128, 144, 128)])

# OpenSea: the sailboat in a circle.
brand('opensea-logo', ['opensea', 'nft', 'marketplace', 'crypto', 'web3'],
      area=[RING], line=[RING],
      detail=[P('M124 52 V140 H72 C96 116 116 88 124 52 Z'),
              P('M64 164 H192 C184 180 172 188 156 188 H100 C84 188 72 180 64 164 Z')])

# ---------------------------------------------------------------- security
# 1Password: the notched key bar in a circle.
OP_BAR = [(112, 64), (144, 64), (144, 192), (112, 192), (112, 140), (124, 128), (112, 116)]
brand('one-password-logo', ['1password', 'password manager', 'security', 'passwords', 'vault'],
      area=[RING], line=[RING], detail=[PG(OP_BAR)])

# Bitwarden: the flat-topped shield with its inner half shield.
BW = 'M48 40 H208 V120 C208 168 176 200 128 224 C80 200 48 168 48 120 Z'
brand('bitwarden-logo', ['bitwarden', 'password manager', 'security', 'passwords', 'open source'],
      area=[P(BW)], line=[P(BW)],
      detail=[P('M128 72 H176 V120 C176 148 158 170 128 186 Z')])

# LastPass: three dots and the cursor bar.
brand('lastpass-logo', ['lastpass', 'password manager', 'security', 'passwords'],
      line=[L(200, 80, 200, 176)], dot=[C(52, 128, 16), C(100, 128, 16), C(148, 128, 16)])

# NordVPN: the dome with the mountain peaks along its foot.
NORD = 'M60 196 A96 96 0 1 1 196 196 L168 124 L152 140 L124 92 Z'
brand('nordvpn-logo', ['nordvpn', 'vpn', 'privacy', 'security', 'mountain'],
      area=[P(NORD)], line=[P(NORD)])

# ---------------------------------------------------------------- browsers and search
# Tor Browser: the onion rings on the right of the circle.
brand('tor-logo', ['tor', 'tor browser', 'onion', 'privacy', 'browser', 'anonymity'],
      area=[RING], line=[RING],
      detail=[P('M128 64 A64 64 0 0 1 128 192'), P('M128 96 A32 32 0 0 1 128 160 Z')])

# Opera GX: the ring with the crescent inside its right side.
brand('opera-gx-logo', ['opera gx', 'opera', 'gaming', 'browser', 'web browser'],
      area=[RING], line=[RING],
      detail=[P('M132 60 C168 72 184 100 184 128 C184 156 168 184 132 196')])

# Not drawn: Vivaldi (reads as a plain V in a circle), Adyen, Paytm and Alipay (wordmarks), Square (reads as square-nested), Ledger (corner brackets
# read as a scan frame), Trezor (a plain padlock), Proton VPN and Afterpay (no clear symbol at small sizes),
# ExpressVPN and DuckDuckGo (no reference mark found).

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
