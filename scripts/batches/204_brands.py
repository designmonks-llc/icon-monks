"""Brand logos: apps, payments and browsers."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def badge(name, tags, glyph, outline=False):
    icon(name, B, tags + ['logo', 'brand'], area=[SQ], line=[SQ], detail=glyph, outline=outline)


# ---------------------------------------------------------------- products
air_top = PG([(128, 44), (216, 80), (128, 116), (40, 80)])
air_right = PG([(144, 140), (216, 108), (216, 188), (144, 220)])
air_left = PG([(40, 112), (112, 144), (40, 184)])
icon('airtable-logo', B, ['airtable', 'database', 'spreadsheet', 'no code', 'logo', 'brand'],
     area=[air_top, air_right, air_left], line=[air_top, air_right, air_left])

asana = [C(128, 84, 36), C(76, 172, 36), C(180, 172, 36)]
icon('asana-logo', B, ['asana', 'project management', 'tasks', 'work management', 'logo', 'brand'],
     area=asana, line=asana)

icon('clickup-logo', B, ['clickup', 'project management', 'productivity', 'tasks', 'logo', 'brand'],
     line=[PL([(60, 120), (128, 56), (196, 120)]),
           P('M48 156 C68 184 96 200 128 200 C160 200 188 184 208 156')])

meet_body = P('M88 72 H156 A16 16 0 0 1 172 88 V168 A16 16 0 0 1 156 184 H56 A16 16 0 0 1 40 168 V120 Z')
icon('google-meet-logo', B, ['google meet', 'google', 'video call', 'meeting', 'logo', 'brand'],
     area=[meet_body, PG([(172, 112), (216, 80), (216, 176), (172, 144)])],
     line=[meet_body, PL([(172, 112), (216, 80), (216, 176), (172, 144)])])

wallet = R(40, 48, 176, 160, 16)
icon('google-wallet-logo', B, ['google wallet', 'google', 'wallet', 'payment', 'cards', 'logo', 'brand'],
     area=[wallet], line=[wallet],
     detail=[L(40, 84, 216, 84), L(40, 108, 216, 108),
             P('M40 132 H88 C104 132 108 160 128 160 C148 160 152 132 168 132 H216')])

# ---------------------------------------------------------------- payments
icon('diners-club-logo', B, ['diners club', 'credit card', 'payment', 'card network', 'logo', 'brand'],
     area=[RING], line=[RING],
     detail=[P('M116 68 A60 60 0 0 0 116 188 Z'), P('M140 68 A60 60 0 0 1 140 188 Z')])

badge('cash-app-logo', ['cash app', 'payment', 'money transfer', 'dollar', 'fintech'],
      [P('M160 96 C152 88 142 84 128 84 C108 84 96 94 96 108 C96 138 160 120 160 150 '
         'C160 164 148 172 128 172 C114 172 102 168 96 162'),
       L(132, 60, 132, 84), L(124, 172, 124, 196)])

# ---------------------------------------------------------------- communities and social
Y = [PL([(84, 72), (128, 136), (172, 72)]), L(128, 136, 128, 184)]
badge('ycombinator-logo', ['y combinator', 'hacker news', 'startup', 'accelerator', 'tech news', 'y'], Y)

icon('producthunt-logo', B, ['product hunt', 'producthunt', 'launch', 'products', 'p', 'logo', 'brand'],
     area=[RING], line=[RING], detail=[P('M96 184 V72 H140 A32 32 0 0 1 140 136 H96')])

pat_bar = R(40, 40, 32, 176, 8)
pat_dot = C(160, 100, 64)
icon('patreon-logo', B, ['patreon', 'creators', 'membership', 'crowdfunding', 'logo', 'brand'],
     area=[pat_bar, pat_dot], line=[pat_bar, pat_dot])

# Signal: speech bubble inside a broken ring, the ring left open where the tail points.
SC = (128, 128)
tail = (68, 188)
b1, b2 = ipt(polar(SC, 64, 112)), ipt(polar(SC, 64, 158))
bubble = P(f'M{pt(b1)} ' + arc_to(SC, 64, b1, b2, lambda m: dist(m, tail)) + f' L{pt(tail)} Z')
dashes = []
for k in range(1, 8):
    mid = 135 + 45 * k
    a, b = ipt(polar(SC, 96, mid - 14)), ipt(polar(SC, 96, mid + 14))
    dashes.append(P(f'M{pt(a)} A96 96 0 0 1 {pt(b)}'))
icon('signal-logo', B, ['signal', 'messaging', 'private messenger', 'encrypted chat', 'logo', 'brand'],
     area=[bubble], line=[bubble] + dashes)

teams_tile = R(40, 80, 112, 112, 16)
teams_body = 'M152 112 H208 V160 A32 32 0 0 1 176 192 H152'
icon('microsoft-teams-logo', B, ['microsoft teams', 'microsoft', 'meetings', 'team chat', 'logo', 'brand'],
     area=[P(teams_body + ' Z'), C(184, 60, 24), teams_tile],
     line=[P(teams_body), C(184, 60, 24), teams_tile],
     detail=[L(68, 112, 124, 112), L(96, 112, 96, 164)])

# ---------------------------------------------------------------- browsers
brave = PG([(92, 40), (164, 40), (180, 56), (204, 52), (216, 76), (204, 120), (184, 176), (128, 216),
            (72, 176), (52, 120), (40, 76), (52, 52), (76, 56)])
icon('brave-logo', B, ['brave', 'browser', 'web browser', 'privacy', 'lion', 'logo', 'brand'],
     area=[brave], line=[brave],
     detail=[PG([(108, 160), (128, 152), (148, 160), (128, 180)]), L(80, 100, 108, 116), L(176, 100, 148, 116)])

opera = E(128, 128, 88, 96)
icon('opera-logo', B, ['opera', 'browser', 'web browser', 'o', 'logo', 'brand'],
     area=[opera], line=[opera], detail=[E(128, 128, 36, 68)])

# ---------------------------------------------------------------- automation
spokes = []
for k in range(8):
    if k % 2 == 0:
        dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][k // 2]
        spokes.append(L(128 + 24 * dx, 128 + 24 * dy, 128 + 92 * dx, 128 + 92 * dy))
    else:
        dx, dy = [(1, 1), (-1, 1), (-1, -1), (1, -1)][k // 2]
        spokes.append(L(128 + 17 * dx, 128 + 17 * dy, 128 + 65 * dx, 128 + 64 * dy))
icon('zapier-logo', B, ['zapier', 'automation', 'workflow', 'integrations', 'logo', 'brand'], line=spokes)

print(save(overwrite=True))
