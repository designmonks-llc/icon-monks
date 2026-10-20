"""Brand logos: productivity, Google, Microsoft and Apple apps."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)
APP = R(40, 40, 176, 176, 40)  # Apple app tile, as app-store-logo and apple-music-logo


def ipt(p):
    return (round(p[0]), round(p[1]))


def tags(*t):
    return list(t) + ['logo', 'brand']


def cap(a, b, r):
    """Closed pill from centre a to centre b, radius r, tangent points rounded to whole units."""
    u = ((b[0] - a[0]) / dist(a, b), (b[1] - a[1]) / dist(a, b))
    n = (-u[1] * r, u[0] * r)
    a1, b1 = ipt((a[0] + n[0], a[1] + n[1])), ipt((b[0] + n[0], b[1] + n[1]))
    b2, a2 = ipt((b[0] - n[0], b[1] - n[1])), ipt((a[0] - n[0], a[1] - n[1]))
    far_b = lambda m: dist(m, a)
    far_a = lambda m: dist(m, b)
    return (f'M{pt(a1)} L{pt(b1)} ' + arc_to(b, r, b1, b2, far_b) + f' L{pt(a2)} ' + arc_to(a, r, a2, a1, far_a)
            + ' Z')


def visible_arcs(circles, inside, step=0.25, layered=False):
    """Outer boundary of overlapping circles (cx, cy, r) with every part for which inside(x, y) holds removed.
    layered=True treats the list as front-to-back, so the edges of front circles show over the ones behind.
    Returns one open arc path per visible run, endpoints rounded to whole units."""
    out = []
    for i, (cx, cy, r) in enumerate(circles):
        others = [c for j, c in enumerate(circles) if j != i]
        n = int(360 / step)
        vis = []
        for k in range(n):
            a = math.radians(k * step)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            front = circles[:i] if layered else others
            hidden = inside(x, y) or any(dist((x, y), c[:2]) < c[2] - 0.01 for c in front)
            vis.append(not hidden)
        if all(vis):
            out.append(C(cx, cy, r)); continue
        k0 = vis.index(False)
        runs, cur = [], None
        for k in range(k0, k0 + n + 1):
            v = vis[k % n]
            if v and cur is None:
                cur = k
            if not v and cur is not None:
                runs.append((cur, k - 1)); cur = None
        for a0, a1 in runs:
            p = ipt(polar((cx, cy), r, a0 * step)); q = ipt(polar((cx, cy), r, a1 * step))
            span = (a1 - a0) * step
            out.append(P(f'M{pt(p)} A{f(r)} {f(r)} 0 {1 if span > 180 else 0} 1 {pt(q)}'))
    return out


# ================================================================ productivity
# monday.com: two slanted pills and a dot.
MD = [cap((52, 156), (84, 100), 20), cap((132, 156), (164, 100), 20)]
icon('monday-logo', B, tags('monday', 'monday.com', 'work management', 'project management', 'productivity'),
     area=[P(d) for d in MD] + [C(200, 148, 20)], line=[P(d) for d in MD] + [C(200, 148, 20)])

# Todoist: three stacked ticks on the app tile.
icon('todoist-logo', B, tags('todoist', 'to-do', 'tasks', 'checklist', 'productivity'),
     area=[APP], line=[APP],
     detail=[PL([(72, y), (100, y + 16), (184, y - 24)]) for y in (96, 136, 176)])

# Evernote: the elephant head with its folded ear corner, eye and curled trunk.
EV = ('M80 36 H160 C192 36 212 60 212 96 V168 C212 200 196 220 168 220 H124 C96 220 72 204 60 180 '
      'L44 144 V72 Z')
icon('evernote-logo', B, tags('evernote', 'notes', 'note-taking', 'elephant', 'productivity'),
     area=[P(EV)], line=[P(EV)],
     detail=[P('M80 36 V72 H44'), P('M212 148 H176 C162 148 152 158 152 172 C152 186 162 196 176 196')],
     dotcut=[C(164, 100, 14)])

# Coda: the square with a C-shaped slot cut in from the right.
CODA = ('M56 40 H200 A16 16 0 0 1 216 56 V96 H152 A32 32 0 0 0 152 160 H216 V200 A16 16 0 0 1 200 216 H56 '
        'A16 16 0 0 1 40 200 V56 A16 16 0 0 1 56 40 Z')
icon('coda-logo', B, tags('coda', 'documents', 'docs', 'collaboration', 'productivity'),
     area=[P(CODA)], line=[P(CODA)])

# ================================================================ microsoft
# Office apps: the letter tile in front of the app's back shape (as microsoft-word-logo).
TILE = R(32, 72, 112, 112, 16)
SHEET = R(72, 32, 152, 192, 16)
SHEET_EDGE = P('M72 72 V48 A16 16 0 0 1 88 32 H208 A16 16 0 0 1 224 48 V208 A16 16 0 0 1 208 224 H88 '
               'A16 16 0 0 1 72 208 V184')

# OneNote: the N tile on the notebook with its section tabs down the right.
icon('onenote-logo', B, tags('onenote', 'microsoft onenote', 'microsoft', 'notes', 'notebook', 'office'),
     area=[SHEET, TILE], line=[TILE, SHEET_EDGE],
     detail=[PL([(64, 156), (64, 100), (112, 156), (112, 100)]), L(184, 32, 184, 224), L(184, 96, 224, 96),
             L(184, 160, 224, 160)])

# SharePoint: the S tile in front of three overlapping circles.
SP_C = [(148, 188, 36), (188, 140, 36), (140, 92, 60)]  # front to back
in_tile = lambda x, y: 32 <= x <= 144 and 72 <= y <= 184
icon('sharepoint-logo', B, tags('sharepoint', 'microsoft sharepoint', 'microsoft', 'intranet', 'collaboration',
                                'office'),
     area=[C(*c) for c in SP_C] + [TILE], line=[TILE] + visible_arcs(SP_C, in_tile, layered=True),
     detail=[P('M108 104 C104 98 96 96 88 96 C76 96 68 102 68 112 C68 122 76 126 88 128 C100 130 108 134 108 144 '
               'C108 154 100 160 88 160 C78 160 70 156 66 150')])

# Microsoft 365: the looped hexagonal ribbon, with the two folds where it passes over itself.
def rounded(points, rc):
    """Closed polygon with every corner rounded by an arc of radius rc (tangent points rounded)."""
    n = len(points)
    cuts = []
    for i in range(n):
        p, a, b = points[i], points[i - 1], points[(i + 1) % n]
        ang = math.acos(((a[0] - p[0]) * (b[0] - p[0]) + (a[1] - p[1]) * (b[1] - p[1])) / (dist(a, p) * dist(b, p)))
        d = rc / math.tan(ang / 2)
        cuts.append((ipt((p[0] + (a[0] - p[0]) * d / dist(a, p), p[1] + (a[1] - p[1]) * d / dist(a, p))),
                     ipt((p[0] + (b[0] - p[0]) * d / dist(b, p), p[1] + (b[1] - p[1]) * d / dist(b, p)))))
    d = f'M{pt(cuts[0][1])}'
    for i in range(1, n + 1):
        c_in, c_out = cuts[i % n]
        d += f' L{pt(c_in)} A{f(rc)} {f(rc)} 0 0 1 {pt(c_out)}'
    return d + ' Z'


HEX_PTS = regular_polygon((128, 128), 96, 6)
HEX_I = [ipt(p) for p in regular_polygon((128, 128), 40, 6)]
HEX_O = rounded([ipt(p) for p in HEX_PTS], 28)
HEX_IN = rounded(HEX_I, 8)
TOP, BOT = ipt(polar((128, 128), 92, -90)), ipt(polar((128, 128), 92, 90))
icon('microsoft-365-logo', B, tags('microsoft 365', 'office 365', 'microsoft', 'office', 'productivity'),
     area=[P(HEX_O)], hole=[P(HEX_IN)], line=[P(HEX_O), P(HEX_IN)],
     detail=[L(*HEX_I[5], *TOP), L(*HEX_I[2], *BOT)])

# Power BI: three bars rising to the right.
PBI = ('M56 216 V136 A8 8 0 0 1 64 128 H104 V88 A8 8 0 0 1 112 80 H152 V40 A8 8 0 0 1 160 32 H192 '
       'A8 8 0 0 1 200 40 V216 A8 8 0 0 1 192 224 H64 A8 8 0 0 1 56 216 Z')
icon('power-bi-logo', B, tags('power bi', 'microsoft power bi', 'microsoft', 'analytics', 'business intelligence',
                              'dashboard'),
     area=[P(PBI)], line=[P(PBI)], detail=[L(104, 128, 104, 224), L(152, 80, 152, 224)])

# Microsoft Store: the shopping bag with the four Microsoft squares.
BAG = R(40, 80, 176, 136, 16)
icon('microsoft-store-logo', B, tags('microsoft store', 'microsoft', 'windows', 'app store', 'apps', 'shopping'),
     area=[BAG], line=[BAG, P('M92 80 V68 A36 36 0 0 1 164 68 V80')],
     detail=[R(92, 112, 72, 72, 4), L(128, 112, 128, 184), L(92, 148, 164, 148)])

# Azure DevOps: the two folded bands around the open window.
ADO = [(114, 33), (180, 73), (220, 68), (220, 180), (174, 218), (102, 192), (102, 218), (61, 165), (35, 154),
       (35, 101), (53, 77), (114, 59)]
ADO_IN = [(61, 97), (180, 73), (180, 174), (61, 165)]
icon('azure-devops-logo', B, tags('azure devops', 'azure', 'microsoft', 'devops', 'ci', 'development'),
     area=[PG(ADO)], hole=[PG(ADO_IN)], line=[PG(ADO), PG(ADO_IN)])

# ================================================================ google
# Docs-family apps: the folded page of google-docs-logo with the app's glyph.
PAGE = 'M56 32 H152 L200 80 V224 H56 Z'
FOLD = P('M152 32 V80 H200')

icon('google-slides-logo', B, tags('google slides', 'google', 'presentation', 'slides', 'productivity'),
     area=[P(PAGE)], line=[P(PAGE)], detail=[FOLD, R(84, 120, 88, 64, 8)])

icon('google-forms-logo', B, tags('google forms', 'google', 'forms', 'survey', 'productivity'),
     area=[P(PAGE)], line=[P(PAGE)], detail=[FOLD] + [L(124, y, 168, y) for y in (120, 156, 192)],
     dotcut=[C(92, y, 14) for y in (120, 156, 192)])

icon('google-keep-logo', B, tags('google keep', 'google', 'notes', 'note-taking', 'idea', 'productivity'),
     area=[P(PAGE)], line=[P(PAGE)],
     detail=[FOLD, P('M112 184 V164 A36 36 0 1 1 144 164 V184 Z')])

# Tasks: the check breaking out of its ring. The part inside is cut from the fill, the part outside drawn on it.
TK = (191, 85)  # where the long arm crosses the ring
icon('google-tasks-logo', B, tags('google tasks', 'google', 'tasks', 'to-do', 'checklist', 'productivity'),
     area=[C(120, 136, 88)], line=[C(120, 136, 88), L(TK[0], TK[1], 216, 60)],
     detail=[PL([(80, 132), (112, 164), TK])])

# Chat: the speech bubble in front of the back square (2020 icon).
CHAT = 'M56 80 H160 A16 16 0 0 1 176 96 V168 A16 16 0 0 1 160 184 H80 L40 224 V96 A16 16 0 0 1 56 80 Z'
icon('google-chat-logo', B, tags('google chat', 'google', 'chat', 'messaging', 'hangouts', 'team chat'),
     area=[P(CHAT), R(96, 40, 120, 120, 16)], line=[P(CHAT), P('M96 80 V56 A16 16 0 0 1 112 40 H200 '
                                                                 'A16 16 0 0 1 216 56 V144 A16 16 0 0 1 200 160 H176')])

# Earth: the globe crossed by its two swooping waves.
E1 = [ipt(polar((128, 128), 96, a)) for a in (168, -36)]
E2 = [ipt(polar((128, 128), 96, a)) for a in (128, 4)]
icon('google-earth-logo', B, tags('google earth', 'google', 'globe', 'maps', 'satellite'),
     area=[RING], line=[RING],
     detail=[P(f'M{pt(E1[0])} C76 148 104 124 128 104 C148 88 168 76 {pt(E1[1])}'),
             P(f'M{pt(E2[0])} C96 200 132 168 156 152 C176 140 196 134 {pt(E2[1])}')])

# Fit: the heart whose left lobe closes into a tick.
FIT = 'M128 212 L44 128 A39.6 39.6 0 0 1 100 72 L128 100 L156 72 A39.6 39.6 0 0 1 212 128 Z'
icon('google-fit-logo', B, tags('google fit', 'google', 'fitness', 'health', 'heart', 'activity'),
     area=[P(FIT)], line=[P(FIT)], detail=[L(72, 156, 128, 100)])

# Home: the thick-banded house.
GH_O = 'M128 40 L216 120 V200 A16 16 0 0 1 200 216 H56 A16 16 0 0 1 40 200 V120 Z'
GH_I = 'M128 112 L168 148 V176 H88 V148 Z'
icon('google-home-logo', B, tags('google home', 'google', 'smart home', 'nest', 'home automation'),
     area=[P(GH_O)], hole=[P(GH_I)], line=[P(GH_O), P(GH_I)])

# Assistant: one large dot and three small ones.
icon('google-assistant-logo', B, tags('google assistant', 'google', 'voice assistant', 'ai', 'assistant'),
     area=[C(88, 96, 52), C(172, 188, 22)], line=[C(88, 96, 52), C(172, 188, 22)],
     dot=[C(172, 132, 16), C(208, 84, 16)])

# News: the front card with its G and lines, the tilted cards fanning out behind.
icon('google-news-logo', B, tags('google news', 'google', 'news', 'headlines', 'newspaper'),
     area=[R(40, 96, 176, 112, 16)],
     line=[R(40, 96, 176, 112, 16), PL([(56, 96), (68, 56), (188, 56), (200, 96)])],
     detail=[P('M100 132 A24 24 0 1 0 108 152 H88'), L(136, 136, 184, 136), L(136, 168, 184, 168)])

# One: the rounded 1, its flag folding down from the top.
ONE = 'M176 56 V200 A24 24 0 0 1 128 200 V105 L95 131 A24 24 0 0 1 65 93 L137 37 A24 24 0 0 1 176 56 Z'
icon('google-one-logo', B, tags('google one', 'google', 'cloud storage', 'subscription', 'backup'),
     area=[P(ONE)], line=[P(ONE)])

# Ads: two slanted bars meeting at the top, the left one ending in a dot.
AD_R = 28
AD_TOP = (128, 64)
AD_BR, AD_BL = (184, 168), (72, 172)


def offset(a, b, r):
    u = ((b[0] - a[0]) / dist(a, b), (b[1] - a[1]) / dist(a, b))
    return (a[0] - u[1] * r, a[1] + u[0] * r), (b[0] - u[1] * r, b[1] + u[0] * r)


def cross(p1, p2, q1, q2):
    d = (p2[0] - p1[0]) * (q2[1] - q1[1]) - (p2[1] - p1[1]) * (q2[0] - q1[0])
    t = ((q1[0] - p1[0]) * (q2[1] - q1[1]) - (q1[1] - p1[1]) * (q2[0] - q1[0])) / d
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


YL = offset(AD_BL, AD_TOP, AD_R)    # yellow bar, outer (left) edge
YR = offset(AD_BL, AD_TOP, -AD_R)   # yellow bar, inner edge
BL = offset(AD_TOP, AD_BR, AD_R)    # blue bar, edge facing the yellow one
y_in = ipt(cross(YR[0], YR[1], BL[0], BL[1]))
icon('google-ads-logo', B, tags('google ads', 'adwords', 'google', 'advertising', 'marketing'),
     area=[P(cap(AD_TOP, AD_BR, AD_R)), P(cap(AD_BL, AD_TOP, AD_R)), C(*AD_BL, AD_R)],
     line=[P(cap(AD_TOP, AD_BR, AD_R)), C(*AD_BL, AD_R), L(*ipt(YL[0]), *ipt(YL[1])), L(*ipt(YR[0]), *y_in)])

# Translate: the G tile in front of the tile with 文.
TR_BACK = 'M136 64 H208 A16 16 0 0 1 224 80 V208 A16 16 0 0 1 208 224 H120 A16 16 0 0 1 104 208 V176'
icon('google-translate-logo', B, tags('google translate', 'google', 'translation', 'language', 'dictionary'),
     area=[R(32, 32, 104, 144, 16), R(104, 64, 120, 160, 16)],
     line=[R(32, 32, 104, 144, 16), P(TR_BACK)],
     detail=[P('M100 84 A28 28 0 1 0 112 108 H88'), L(148, 140, 208, 140),
             P('M196 140 C188 172 172 194 148 208'), P('M160 140 C168 172 184 194 208 208')],
     dotcut=[C(178, 104, 14)])

# ================================================================ apple
icon('facetime-logo', B, tags('facetime', 'apple', 'video call', 'ios'),
     area=[APP], line=[APP],
     detail=[R(64, 96, 92, 64, 16), P('M156 120 L192 96 V160 L156 136')])

IM = 'M106 169 A64 50 0 1 0 73 147 C74 160 72 172 66 180 C80 180 94 176 106 169 Z'
icon('imessage-logo', B, tags('imessage', 'messages', 'apple', 'chat', 'ios'),
     area=[APP], line=[APP], detail=[P(IM)])

icon('apple-wallet-logo', B, tags('apple wallet', 'wallet', 'apple', 'payments', 'cards', 'ios'),
     area=[APP], line=[APP],
     detail=[L(72, 80, 184, 80), L(64, 112, 192, 112),
             P('M40 144 H92 C104 144 108 168 128 168 C148 168 152 144 164 144 H216')])

BOOK = ('M128 92 C112 82 96 78 76 78 V170 C96 170 112 174 128 184 C144 174 160 170 180 170 V78 '
        'C160 78 144 82 128 92 Z')
icon('apple-books-logo', B, tags('apple books', 'ibooks', 'books', 'apple', 'reading', 'ebook'),
     area=[APP], line=[APP], detail=[P(BOOK), L(128, 92, 128, 184)])

HEART = ('M160 120 C144 110 128 98 128 82 A16 16 0 0 1 160 76 A16 16 0 0 1 192 82 C192 98 176 110 160 120 Z')
icon('apple-health-logo', B, tags('apple health', 'health', 'apple', 'fitness', 'heart', 'ios'),
     area=[APP], line=[APP], detail=[P(HEART)])

# ================================================================ alexa
AX_C, AX_R = (132, 124), 92
AX_A = ipt(polar(AX_C, AX_R, 125))
ALEXA = f'M{AX_C[0] - AX_R} {AX_C[1]} A{AX_R} {AX_R} 0 1 1 {pt(AX_A)} L{AX_C[0] - AX_R + 4} 212 Z'
icon('alexa-logo', B, tags('alexa', 'amazon alexa', 'amazon', 'voice assistant', 'echo', 'smart speaker'),
     area=[P(ALEXA)], hole=[C(132, 124, 48)], line=[P(ALEXA), C(132, 124, 48)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
