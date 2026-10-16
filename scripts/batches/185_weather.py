import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

W = 'Weather'

# ---------------------------------------------------------------- wind-slash (wind geometry + slash, no area)
wind = load('wind')
# wind's own strokes with the slash laid over them (like wifi-slash); the middle stroke's curl would wrap
# around the slash and clog, so it is trimmed to a quarter hook that stays 34 units clear of the slash
icon('wind-slash', W, ['wind', 'off', 'disabled', 'hidden'],
     line=[wind['line'][0], P('M32 140 H188 A28 28 0 0 1 216 168'), wind['line'][2], L(48, 48, 208, 208)])

# ---------------------------------------------------------------- windsock
# pole on the left, tapered sock with three bands; outer bands are the area so the fill reads striped
def top(x):
    return 56 + (x - 48) * (84 - 56) / 168
def bot(x):
    return 136 + (x - 48) * (124 - 136) / 168
x1, x2 = 104, 160
sock = PG([(48, 56), (216, 84), (216, 124), (48, 136)])
icon('windsock', W, ['windsock', 'wind', 'direction', 'airport'],
     line=[L(48, 40, 48, 224), sock, L(x1, top(x1), x1, bot(x1)), L(x2, top(x2), x2, bot(x2))],
     area=[PG([(48, 56), (x1, top(x1)), (x1, bot(x1)), (48, 136)]),
           PG([(x2, top(x2)), (216, 84), (216, 124), (x2, bot(x2))])])

print(save(overwrite=True))
