"""Brand logos: office apps, cloud storage, note-taking and games."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def cloud(circles, bottom):
    """Closed cloud outline: lobes (cx, cy, r) from left to right over a flat bottom at y=bottom.
    Lobe joins are rounded to whole units; the first and last lobes must touch the bottom line."""
    cn = (sum(c[0] for c in circles) / len(circles), bottom - 40)
    out = lambda m: dist(m, cn)
    first, last = circles[0], circles[-1]
    start = (first[0], bottom)
    left = (first[0] - first[2], first[1])
    d = f'M{pt(start)} ' + arc_to(first[:2], first[2], start, left, out) + ' '
    cur = left
    for a, b in zip(circles, circles[1:]):
        x = ipt(circle_x(a[:2], a[2], b[:2], b[2])[0])
        d += arc_to(a[:2], a[2], cur, x, out) + ' '
        cur = x
    right, end = (last[0] + last[2], last[1]), (last[0], bottom)
    d += arc_to(last[:2], last[2], cur, right, out) + ' ' + arc_to(last[:2], last[2], right, end, out) + ' Z'
    return d


# ---------------------------------------------------------------- office apps
# Excel, Word and PowerPoint: the letter tile in front of the app's back shape (as microsoft-teams-logo).
TILE = R(32, 72, 112, 112, 16)
SHEET = R(72, 32, 152, 192, 16)
SHEET_EDGE = P('M72 72 V48 A16 16 0 0 1 88 32 H208 A16 16 0 0 1 224 48 V208 A16 16 0 0 1 208 224 H88 '
               'A16 16 0 0 1 72 208 V184')
ROWS = [L(144, 80, 224, 80), L(144, 128, 224, 128), L(144, 176, 224, 176)]

icon('microsoft-excel-logo', B, ['microsoft excel', 'excel', 'microsoft', 'spreadsheet', 'office', 'logo', 'brand'],
     area=[SHEET, TILE], line=[TILE, SHEET_EDGE],
     detail=[L(68, 104, 108, 152), L(108, 104, 68, 152), L(184, 32, 184, 128)] + ROWS)

icon('microsoft-word-logo', B, ['microsoft word', 'word', 'microsoft', 'document', 'word processor', 'office',
                                'logo', 'brand'],
     area=[SHEET, TILE], line=[TILE, SHEET_EDGE],
     detail=[PL([(56, 100), (70, 156), (88, 116), (106, 156), (120, 100)])] + ROWS)

# PowerPoint: the pie with its right half split, behind the P tile.
PIE_R = math.hypot(57, 56)
icon('microsoft-powerpoint-logo', B, ['microsoft powerpoint', 'powerpoint', 'microsoft', 'presentation', 'slides',
                                      'office', 'logo', 'brand'],
     area=[C(144, 128, PIE_R), TILE],
     line=[TILE, P(f'M87 72 A{f(PIE_R)} {f(PIE_R)} 0 1 1 87 184')],
     detail=[L(144, 128, 224, 128), P('M68 160 V96 H92 A20 20 0 0 1 92 136 H68')])

# ---------------------------------------------------------------- google apps
# Sheets: the folded page of google-docs-logo with a table of cells.
PAGE = 'M56 32 H152 L200 80 V224 H56 Z'
icon('google-sheets-logo', B, ['google sheets', 'google', 'spreadsheet', 'table', 'productivity', 'logo', 'brand'],
     area=[P(PAGE)], line=[P(PAGE)],
     detail=[P('M152 32 V80 H200'), R(80, 112, 96, 80, 8), L(80, 152, 176, 152), L(120, 112, 120, 192)])

# Calendar: the square tile with its bottom-right corner cut off, showing the 31.
CAL = 'M56 40 H200 A16 16 0 0 1 216 56 V176 L176 216 H56 A16 16 0 0 1 40 200 V56 A16 16 0 0 1 56 40 Z'
icon('google-calendar-logo', B, ['google calendar', 'google', 'calendar', 'schedule', 'events', '31', 'logo', 'brand'],
     area=[P(CAL)], line=[P(CAL)],
     detail=[P('M76 92 C82 84 90 80 100 80 C114 80 124 88 124 102 C124 116 114 124 100 124 '
               'C116 124 128 132 128 148 C128 162 116 172 100 172 C90 172 80 168 72 160'),
             PL([(148, 96), (164, 80), (164, 168)])])

# ---------------------------------------------------------------- cloud storage
# OneDrive: three overlapping lobes; the shape edges cross in an X inside the cloud.
OD = [(80, 140, 48), (128, 130, 64), (184, 148, 40)]
OD_D = cloud(OD, 188)
od_r = ipt(circle_x(OD[1][:2], OD[1][2], OD[2][:2], OD[2][2])[0])
icon('onedrive-logo', B, ['onedrive', 'microsoft', 'cloud storage', 'files', 'sync', 'logo', 'brand'],
     area=[P(OD_D)], line=[P(OD_D)],
     detail=[L(100, 98, 216, 168), L(od_r[0], od_r[1], 40, 166)])

# iCloud: four lobes, a small one tucked between the left and the big centre lobe.
IC = [(72, 148, 40), (92, 116, 28), (142, 118, 52), (186, 150, 38)]
IC_D = cloud(IC, 188)
icon('icloud-logo', B, ['icloud', 'apple', 'cloud storage', 'backup', 'sync', 'logo', 'brand'],
     area=[P(IC_D)], line=[P(IC_D)])

# ---------------------------------------------------------------- note-taking and whiteboards
# Obsidian: the faceted gem, with its curved facet edges.
GEM = 'M132 32 L180 80 C182 104 186 128 200 152 L176 216 L96 208 L56 164 L76 112 L84 72 Z'
icon('obsidian-logo', B, ['obsidian', 'notes', 'markdown', 'knowledge base', 'note-taking', 'logo', 'brand'],
     area=[P(GEM)], line=[P(GEM)],
     detail=[P('M76 112 C96 124 108 144 108 168 C108 184 104 196 96 208'),
             P('M108 152 C132 148 168 156 186 184'),
             P('M144 44 C132 68 128 92 128 112 C130 128 134 140 136 148')])

# Miro: the three slanted strokes on the app tile.
icon('miro-logo', B, ['miro', 'whiteboard', 'collaboration', 'brainstorming', 'logo', 'brand'],
     area=[SQ], line=[SQ],
     detail=[PG([(x - 6, 72), (x + 6, 72), (x + 28, 100), (x + 12, 184), (x, 184), (x + 16, 100)]) for x in (72, 116, 160)])

# Canva: the script C with its ball terminal, in a circle.
icon('canva-logo', B, ['canva', 'design', 'graphic design', 'templates', 'logo', 'brand'],
     area=[RING], line=[RING],
     detail=[P('M152 112 C166 112 178 102 178 90 C178 76 166 66 148 66 C108 66 72 104 72 148 '
               'C72 174 88 190 110 190 C138 190 162 174 182 150')],
     dot=[C(152, 112, 16)])

# ---------------------------------------------------------------- games
# PlayStation: the upright P with the flat S passing behind it, both parts filled.
PS_P = 'M100 52 C148 60 184 72 184 100 C184 116 172 128 156 128 H140 V204 L100 192 Z'
PS_L = 'M100 140 L46 158 A14 14 0 0 0 46 186 H100'
PS_R = 'M140 156 L208 142 A16 16 0 0 1 216 172 L140 204'
icon('playstation-logo', B, ['playstation', 'sony', 'gaming', 'console', 'games', 'ps', 'logo', 'brand'],
     area=[P(PS_P), P(PS_L + ' Z'), P(PS_R + ' Z')],
     line=[P(PS_P), P(PS_L), P(PS_R)])

# Steam: the piston, a wheel joined by a rod to the small pivot, which the arm pulls from the edge.
icon('steam-logo', B, ['steam', 'valve', 'gaming', 'games', 'store', 'logo', 'brand'],
     area=[RING], line=[RING],
     detail=[C(156, 104, 32), C(96, 166, 20), L(134, 128, 110, 152), L(33, 140, 78, 158)],
     dotcut=[C(156, 104, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
