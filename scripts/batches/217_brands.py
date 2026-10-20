"""Brand logos: learning, fitness, dating, travel and food."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


# ---------------------------------------------------------------- learning
# Udemy: the lowercase u under its chevron cap.
brand('udemy-logo', ['udemy', 'online courses', 'learning', 'education', 'u'], outline=True,
      line=[P('M80 104 V168 A48 48 0 0 0 176 168 V104'), PL([(80, 72), (128, 44), (176, 72)])])

# Khan Academy: the hexagon with the sprouting figure, a head over two leaves.
HEX = PG([(128, 32), (212, 80), (212, 176), (128, 224), (44, 176), (44, 80)])
brand('khan-academy-logo', ['khan academy', 'learning', 'education', 'nonprofit', 'school'],
      area=[HEX], line=[HEX],
      detail=[C(128, 84, 16),
              P('M76 124 H104 C120 144 128 164 128 188 C96 188 76 160 76 124 Z'),
              P('M180 124 H152 C136 144 128 164 128 188 C160 188 180 160 180 124 Z')])

# ---------------------------------------------------------------- fitness
# Strava: the large peak and the small valley that continues its right arm.
brand('strava-logo', ['strava', 'running', 'cycling', 'fitness', 'workout tracker'],
      line=[PL([(36, 148), (96, 40), (150, 137)]), PL([(164, 162), (194, 216), (224, 162)])])

# ---------------------------------------------------------------- dating
# Tinder: the flame with the small lick on its left shoulder.
FLAME = ('M100 32 C156 60 200 100 200 152 C200 192 168 224 128 224 C88 224 56 192 56 152 '
         'C56 128 64 108 76 96 C80 108 88 116 96 116 C96 84 100 56 100 32 Z')
brand('tinder-logo', ['tinder', 'dating', 'match', 'flame', 'swipe'], area=[P(FLAME)], line=[P(FLAME)])

# Bumble: the hexagon with three bars, the middle one longest.
BHEX = PG([(32, 128), (80, 44), (176, 44), (224, 128), (176, 212), (80, 212)])
brand('bumble-logo', ['bumble', 'dating', 'bee', 'hive', 'social'],
      area=[BHEX], line=[BHEX],
      detail=[L(108, 92, 140, 92), L(84, 128, 172, 128), L(116, 164, 148, 164)])

# ---------------------------------------------------------------- travel and homes
# Zillow: the house with a Z swept across it.
HOUSE = PG([(40, 216), (40, 104), (128, 40), (216, 104), (216, 216)])
brand('zillow-logo', ['zillow', 'real estate', 'homes', 'house', 'property'],
      area=[HOUSE], line=[HOUSE],
      detail=[P('M76 124 C108 112 140 106 172 104 L84 180 C116 168 148 160 184 156')])

# Booking.com: the B and its dot on the app tile.
brand('booking-logo', ['booking.com', 'booking', 'hotels', 'travel', 'reservations'],
      area=[SQ], line=[SQ],
      detail=[P('M88 124 V72 H116 A26 26 0 0 1 116 124 H88 V184 H124 A30 30 0 0 0 124 124')],
      dotcut=[C(176, 176, 14)])

# Tripadvisor: the owl's two big eyes under the brow, with the beak between them.
EYES = [C(80, 136, 36), C(176, 136, 36)]
# Kept outlined in the fill weight: filled eyes would swallow the pupils.
brand('tripadvisor-logo', ['tripadvisor', 'travel', 'reviews', 'owl', 'hotels'], outline=True,
      line=EYES + [P('M36 100 C60 82 96 72 128 72 C160 72 196 82 220 100'), PL([(112, 172), (128, 192), (144, 172)])],
      dot=[C(80, 136, 16), C(176, 136, 16)])

# Skyscanner: five rays rising over the curved horizon with its dip.
O = (128, 180)
RAYS = [L(*map(round, polar(O, 64, a)), *map(round, polar(O, 108, a))) for a in (-150, -120, -90, -60, -30)]
brand('skyscanner-logo', ['skyscanner', 'flights', 'travel', 'sunrise', 'search'],
      line=[P('M36 184 C64 172 92 164 108 164 C116 164 120 170 128 178 C136 170 140 164 148 164 C164 164 192 172 220 184')] + RAYS)

# ---------------------------------------------------------------- food delivery and rides
# DoorDash: the dash, a band that runs right and wraps back under itself.
DASH = 'M40 72 H164 A56 56 0 0 1 164 184 H140 L108 152 H164 A24 24 0 0 0 164 104 H72 Z'
brand('doordash-logo', ['doordash', 'food delivery', 'delivery', 'restaurants', 'dash'],
      area=[P(DASH)], line=[P(DASH)])

# Deliveroo: the kangaroo head with its two ears and small eyes.
ROO = PG([(96, 56), (144, 44), (156, 116), (168, 32), (216, 36), (204, 164), (176, 224), (52, 196),
          (40, 140), (108, 128)])
brand('deliveroo-logo', ['deliveroo', 'food delivery', 'delivery', 'kangaroo', 'restaurants'],
      area=[ROO], line=[ROO], dotcut=[C(116, 156, 14), C(160, 160, 14)])

# Instacart: the carrot, its leaves over the half-round root.
ROOT = 'M48 216 C48 172 84 148 128 148 C172 148 208 172 208 216 Z'
brand('instacart-logo', ['instacart', 'grocery delivery', 'groceries', 'carrot', 'shopping'],
      area=[P(ROOT)], line=[P(ROOT), L(128, 40, 128, 120), P('M68 76 C84 100 104 116 128 120 C152 116 172 100 188 76')])

# Gojek: the open ring curling in at the bottom, around the centre dot.
brand('gojek-logo', ['gojek', 'ride hailing', 'delivery', 'super app', 'indonesia'],
      area=[C(128, 128, 32)],
      line=[P('M108 184 C108 198 100 204 92 208 A88 88 0 1 1 164 208 C156 204 148 198 148 184'),
            C(128, 128, 32)])

# Swiggy: the map pin with the S cut through it.
PIN = 'M128 224 C112 200 56 152 56 104 A72 72 0 0 1 200 104 C200 152 144 200 128 224 Z'
brand('swiggy-logo', ['swiggy', 'food delivery', 'delivery', 'restaurants', 'india'],
      area=[P(PIN)], line=[P(PIN)],
      detail=[PL([(128, 60), (128, 100), (172, 100)]), PL([(84, 128), (124, 128), (124, 168)])])

# Ola: the wordmark, an O, an L and the A without a crossbar.
brand('ola-logo', ['ola', 'ola cabs', 'ride hailing', 'taxi', 'india'], outline=True,
      line=[C(64, 128, 28), PL([(116, 100), (116, 156), (152, 156)]), PL([(168, 156), (196, 100), (224, 156)])])

# ---------------------------------------------------------------- food and drink
# McDonald's: the golden arches.
brand('mcdonalds-logo', ['mcdonalds', 'fast food', 'golden arches', 'burgers', 'restaurant'],
      line=[P('M32 216 C32 96 52 48 80 48 C108 48 124 120 128 168 C132 120 148 48 176 48 C204 48 224 96 224 216')])

# Pizza Hut: the red roof.
ROOF = 'M32 168 L48 152 C76 144 92 120 100 88 H156 C164 120 180 144 208 152 L224 168 Z'
brand('pizza-hut-logo', ['pizza hut', 'pizza', 'fast food', 'restaurant', 'roof'], area=[P(ROOF)], line=[P(ROOF)])

# Domino's: the tilted domino, one pip on the upper half and two on the lower.
TILE = PG([(156, 36), (220, 100), (100, 220), (36, 156)])
brand('dominos-logo', ['dominos', 'pizza', 'delivery', 'domino', 'restaurant'],
      area=[TILE], line=[TILE], detail=[L(96, 96, 160, 160)],
      dotcut=[C(158, 98, 14), C(80, 158, 14), C(116, 158, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
