import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Commerce'
# Base credit-card geometry (from icons/credit-card.svg): rect 24,56 208x144 rx14,
# stripe y=104, signature line 56..96 at y=160.
X0, Y0, X1, Y1, RX = 24, 56, 232, 200, 14
STRIPE = L(24, 104, 232, 104)
SIGN = L(56, 160, 96, 160)


def card_cut(B, rc):
    """Card outline opened around a lower-right badge centred at B, clearance radius rc.
    Returns (line path, area path)."""
    yr = B[1] - math.sqrt(rc * rc - (X1 - B[0]) ** 2)      # where the right edge stops
    xb = B[0] - math.sqrt(rc * rc - (Y1 - B[1]) ** 2)      # where the bottom edge stops
    outline = (f'M{f(X1)} {f(yr)} V{Y0 + RX} A{RX} {RX} 0 0 0 {X1 - RX} {Y0} H{X0 + RX} '
               f'A{RX} {RX} 0 0 0 {X0} {Y0 + RX} V{Y1 - RX} A{RX} {RX} 0 0 0 {X0 + RX} {Y1} H{f(xb)}')
    area = outline + f' A{f(rc)} {f(rc)} 0 0 1 {f(X1)} {f(yr)} Z'
    return P(outline), P(area)


def card_badge(name, tags, B, rc, marks, mark_area=(), mark_detail=()):
    ln, ar = card_cut(B, rc)
    icon(name, CM, tags, line=[ln] + list(marks), detail=[STRIPE, SIGN] + list(mark_detail),
         area=[ar] + list(mark_area))


# ---- credit-card-pay: contactless waves in the corner
Cw = (158, 190)
waves = []
for r in (20, 54):
    a, b = polar(Cw, r, -38), polar(Cw, r, 38)
    waves.append(P(f'M{pt(a)} A{r} {r} 0 0 1 {pt(b)}'))
card_badge('credit-card-pay', ['credit card pay', 'payment', 'card', 'pay', 'credit'],
           (178, 190), 70, waves)

# ---- credit-card-plus
B = (188, 188)
card_badge('credit-card-plus', ['add card', 'new payment', 'credit card', 'add'],
           B, 62, [L(B[0] - 28, B[1], B[0] + 28, B[1]), L(B[0], B[1] - 28, B[0], B[1] + 28)])

# ---- credit-card-refund: small u-turn arrow pointing back
B = (188, 184)
ref = [P('M160 168 L196 168 A20 20 0 0 1 196 208 L172 208'), PL([(180, 148), (160, 168), (180, 188)])]
card_badge('credit-card-refund', ['credit card refund', 'payment', 'card', 'pay', 'credit'],
           B, 64, ref)

# ---- credit-card-shield: small shield (shield.svg scaled 0.4)
def sp(x, y, c=(184, 184), s=0.4):
    return (c[0] + (x - 128) * s, c[1] + (y - 128) * s)
def shield_path(c, s):
    q = lambda x, y: pt(sp(x, y, c, s))
    return (f'M{q(128,32)} L{q(208,64)} L{q(208,120)} C{q(208,176)} {q(168,208)} {q(128,224)} '
            f'C{q(88,208)} {q(48,176)} {q(48,120)} L{q(48,64)} Z')
sh = P(shield_path((184, 180), 0.42))
card_badge('credit-card-shield', ['secure payment', 'protected', 'card', 'shield', 'payment protection'],
           (184, 180), 68, [sh], mark_area=[sh])

# ---- credit-card-slash (no area so the slash reads in the fill weight)
icon('credit-card-slash', CM, ['no card', 'card declined', 'payment', 'slash', 'declined'],
     line=[R(24, 56, 208, 144, 14), STRIPE, SIGN, L(48, 48, 208, 208)])

# ---- credits: two short coin stacks, the front one hiding the back one
RXc, RYc, T = 60, 18, 32
fc, ft = 164, 140          # front stack: 2 coins
bc, bt = 96, 64            # back stack: 3 coins
fb, bb = ft + 2 * T, bt + 3 * T
def stack_path(cx, top, yb):
    return (f'M{cx - RXc} {top} A{RXc} {RYc} 0 0 1 {cx + RXc} {top} V{yb} '
            f'A{RXc} {RYc} 0 0 1 {cx - RXc} {yb} Z')
def seam(cx, y):
    return f'M{cx - RXc} {y} A{RXc} {RYc} 0 0 0 {cx + RXc} {y}'
def hidden(p, d):
    """Inside the front stack grown by about d (top face as an enlarged ellipse, left side as x = fc-RXc-d)."""
    x, y = p
    return ((x - fc) / (RXc + d)) ** 2 + ((y - ft) / (RYc + d)) ** 2 <= 1 or (x >= fc - RXc - d and y >= ft)
def seam_cut(cy, d):
    """Lower half of the back coin ellipse at height cy, from its left end to where it meets the hidden zone."""
    ell = lambda a: (bc + RXc * math.cos(a), cy + RYc * math.sin(a))
    lo, hi = math.pi, 0.0      # angle pi = left end (visible), decreasing towards the right end
    if not hidden(ell(hi), d):
        return ell(hi)
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if not hidden(ell(m), d) else (lo, m)
    return ell(lo)
DL, DA = 28, 20            # line ends and area edge clearance from the front stack's centreline
def side_end(d):
    return ft - (RYc + d) * math.sqrt(1 - ((bc + RXc - fc) / (RXc + d)) ** 2)
back_line = (f'M{bc - RXc} {bb} V{bt} A{RXc} {RYc} 0 0 1 {bc + RXc} {bt} V{f(side_end(DL))}')
e = seam_cut(bb, DL)
back_bottom = f'M{bc - RXc} {bb} A{RXc} {RYc} 0 0 0 {pt(e)}'
back_details = [P(seam(bc, bt))]
for k in (1, 2):
    e2 = seam_cut(bt + k * T, DL)
    back_details.append(P(f'M{bc - RXc} {bt + k * T} A{RXc} {RYc} 0 0 0 {pt(e2)}'))
ea = seam_cut(bb, DA)
xa = fc - RXc - DA
ya = ft  # offset ellipse meets the vertical at its widest point
back_area = (f'M{bc - RXc} {bb} V{bt} A{RXc} {RYc} 0 0 1 {bc + RXc} {bt} V{f(side_end(DA))} '
             f'A{RXc + DA} {RYc + DA} 0 0 0 {f(xa)} {ya} V{f(ea[1])} '
             f'A{RXc} {RYc} 0 0 1 {bc - RXc} {bb} Z')
front = stack_path(fc, ft, fb)
icon('credits', CM, ['credits', 'tokens', 'balance', 'points'],
     line=[P(front), P(back_line), P(back_bottom)],
     detail=[P(seam(fc, ft)), P(seam(fc, ft + T))] + back_details,
     area=[P(front), P(back_area)])

print(save(overwrite=True))
