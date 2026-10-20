"""Gap fill from the 2026-10-20 library comparison: two-way elbow arrows, clock hours 10-12, 5 and 10 second
skips, and the AVI file type."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

# ---------------------------------------------------------------- arrow-elbow-<first>-<then>
# arrow-elbow-left runs down, then turns and points left; arrow-elbow-right, -down and -up cover down-right,
# right-down and right-up. These four add the turns that start by going up or left. The first word is the
# direction the arrow leaves in, the second the way it ends up pointing.
BASE = ([(196, 40), (196, 168), (40, 168)], [(88, 120), (40, 168), (88, 216)])
MX = lambda p: (256 - p[0], p[1])
MY = lambda p: (p[0], 256 - p[1])
TR = lambda p: (p[1], p[0])


def moved(*fs):
    out = []
    for pts in BASE:
        for fn in fs:
            pts = [fn(p) for p in pts]
        out.append(PL(pts))
    return out


ELBOWS = {
    'up-left': (MY,), 'up-right': (MX, MY), 'left-up': (MY, TR), 'left-down': (MX, MY, TR),
}
for name, fs in ELBOWS.items():
    first, then = name.split('-')
    icon(f'arrow-elbow-{name}', 'Arrows', ['elbow', 'turn', first, then, 'corner arrow', '90 degrees'],
         line=moved(*fs))

# ---------------------------------------------------------------- clock-hour-10..12
# clock-hour-9 with the hour hand (length 44) turned to the hour; at 12 both hands point up as one stroke
FACE = C(128, 128, 96)
for h in (10, 11):
    a = math.radians(h * 30)
    end = (round(128 + 44 * math.sin(a)), round(128 - 44 * math.cos(a)))
    icon(f'clock-hour-{h}', 'Time', [f'{h} oclock', ['ten', 'eleven'][h - 10], 'clock', 'time', 'hour', 'clock face'],
         line=[FACE], area=[FACE], detail=[P(f'M128 72 L128 128 L{pt(end)}')])
icon('clock-hour-12', 'Time', ['12 oclock', 'twelve', 'noon', 'midnight', 'clock', 'time', 'hour'],
     line=[FACE], area=[FACE], detail=[L(128, 72, 128, 128)])

# ---------------------------------------------------------------- skip-back / skip-forward 5 and 10
# skip-back-15 and skip-forward-15 with new numerals: the 5 is moved to the centre, the 10 keeps the 1 and adds
# a zero in the 5's place
BACK = [P('M128 56 A84 84 0 1 1 55 98'), P('M152 32 L128 56 L152 80')]
FWD = [P('M128 56 A84 84 0 1 0 201 98'), P('M104 32 L128 56 L104 80')]
ONE = P('M93 135 L112 119 L112 173')
ZERO = R(132, 119, 36, 54, 18)
FIVE = P('M143 119 H112 L110 144 A18.36 18.36 0 1 1 110 165')
for way, ring, words in (('back', BACK, ['rewind {n}', 'replay', 'back {n} seconds']),
                         ('forward', FWD, ['forward {n}', 'jump ahead', 'skip {n} seconds'])):
    icon(f'skip-{way}-10', 'Media', [w.format(n=10) for w in words], line=ring + [ONE, ZERO], outline=True)
    icon(f'skip-{way}-5', 'Media', [w.format(n=5) for w in words], line=ring + [FIVE])

# ---------------------------------------------------------------- file-avi
# the file-raw layout: page top above, three large letters below
icon('file-avi', 'Files', ['avi', 'video', 'movie', 'file type', 'video file'],
     line=[P('M56 128 V32 H152 L200 80 V128'), P('M41 224 L63 160 L85 224'), L(49, 201, 77, 201),
           P('M111 160 L133 224 L155 160'), L(196, 160, 196, 224)],
     area=[P('M56 128 V32 H152 L200 80 V128 Z')], detail=[P('M152 32 V80 H200')])

print(save(overwrite=True))
