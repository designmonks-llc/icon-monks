import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

BZ = 'Business'


def gear_path(c, r_root, r_tip, n, phase=0, half_root=None, half_tip=None):
    """Gear outline like the core gear: trapezoid teeth joined by root arcs."""
    step = 360 / n
    hr = half_root if half_root is not None else step * 0.36
    ht = half_tip if half_tip is not None else step * 0.2
    pts = []
    for i in range(n):
        t = phase + i * step
        pts.append((polar(c, r_root, t - hr), polar(c, r_tip, t - ht), polar(c, r_tip, t + ht), polar(c, r_root, t + hr)))
    d = 'M' + pt(pts[0][0])
    for i, (a, b, cc, dd) in enumerate(pts):
        if i:
            d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    d += f' A{f(r_root)} {f(r_root)} 0 0 1 {pt(pts[0][0])} Z'
    return d


# ================================================================ Building office variants
# Base: building-office. The lower-right corner is opened up for a bare badge mark.
BO = load('building-office')
bo_windows = ['M88 72 L112 72', 'M144 72 L168 72', 'M88 108 L112 108', 'M144 108 L168 108', 'M88 144 L112 144']
bo_body = 'M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V112'
bo_area = ('M56 216 V48 A16 16 0 0 1 72 32 H184 A16 16 0 0 1 200 48 V112 '
           'A28 28 0 0 1 172 140 H164 A8 8 0 0 0 156 148 V216 H148 V180 H108 V216 Z')
icon('building-office-warning', BZ, ['building', 'office', 'alert', 'exclamation'],
     line=[P(bo_body), L(32, 216, 156, 216), P('M108 216 V180 H148 V216'), L(200, 152, 200, 184)],
     detail=[P(d) for d in bo_windows], area=[P(bo_area)], dot=[C(200, 216, 16)])
icon('building-office-x', BZ, ['building', 'office', 'remove', 'x'],
     line=[P(bo_body), L(32, 216, 156, 216), P('M108 216 V180 H148 V216'), L(180, 164, 220, 204), L(220, 164, 180, 204)],
     detail=[P(d) for d in bo_windows], area=[P(bo_area)])

# ================================================================ Business plan: plan sheet behind a coin stack
sheet = 'M100 192 H56 A16 16 0 0 1 40 176 V48 A16 16 0 0 1 56 32 H136 A16 16 0 0 1 152 48 V96'
sheet_area = ('M40 176 V48 A16 16 0 0 1 56 32 H136 A16 16 0 0 1 152 48 V112 H112 V192 H56 A16 16 0 0 1 40 176 Z')
coins = R(128, 120, 96, 96, 16)
icon('business-plan', BZ, ['business plan', 'strategy', 'finance', 'growth'],
     line=[P(sheet), coins], detail=[L(72, 72, 120, 72), L(72, 104, 104, 104), L(72, 136, 88, 136), L(128, 152, 224, 152), L(128, 184, 224, 184)],
     area=[P(sheet_area), coins])

# ================================================================ Calculator / certificate slashed
calc = load('calculator')
icon('calculator-slash', BZ, ['calculator', 'disabled', 'off', 'business'],
     line=[R(56, 32, 144, 192, 16), R(88, 64, 80, 32, 6), L(48, 48, 208, 208)],
     dot=[C(92, 140, 16), C(92, 184, 16), C(128, 184, 16)])
icon('certificate-slash', BZ, ['certificate', 'disabled', 'off', 'business'],
     line=[R(32, 40, 192, 160, 14), L(64, 80, 192, 80), L(64, 120, 124, 120), L(64, 160, 108, 160), C(172, 148, 24),
           L(48, 48, 208, 208)])

# ================================================================ Clipboard family
CB = load('clipboard')
cb_line, cb_area, cb_hole = CB['line'], CB['area'], CB['hole']


def clip(name, tags, **kw):
    icon(name, BZ, tags, line=cb_line + kw.pop('line', []), area=cb_area + kw.pop('area', []), hole=cb_hole, **kw)


clip('clipboard-clock', ['pending tasks', 'deadline', 'scheduled', 'clipboard'],
     detail=[C(128, 148, 48), PL([(128, 120), (128, 148), (152, 162)])])
clip('clipboard-magnifying-glass', ['audit', 'review', 'inspect', 'check', 'clipboard'],
     detail=[C(120, 140, 32), L(143, 163, 168, 188)])
clip('clipboard-user', ['assignment', 'assignee', 'profile', 'clipboard'],
     detail=[C(128, 120, 20), P('M84 196 C84 180 100 172 128 172 C156 172 172 180 172 196')])
clip('clipboard-warning', ['late', 'overdue', 'alert', 'clipboard'],
     detail=[L(128, 108, 128, 152)], dotcut=[C(128, 188, 16)])
clip('financial-report', ['financial report', 'money', 'clipboard', 'accounting'],
     detail=[L(128, 102, 128, 198), P('M160 116 H112 A18 18 0 0 0 112 152 H144 A18 18 0 0 1 144 188 H96')])
clip('report-chart', ['analytics report', 'chart', 'document', 'statistics'],
     detail=[L(92, 188, 92, 156), L(128, 188, 128, 116), L(164, 188, 164, 140)])

# report-search: clipboard with text lines, magnifier overlapping the lower-right corner
MG = (172, 172)
rs_body = 'M88 48 H64 A16 16 0 0 0 48 64 V208 A16 16 0 0 0 64 224 H134'
rs_body2 = 'M168 48 H192 A16 16 0 0 1 208 64 V118'
rs_area = ('M48 64 A16 16 0 0 1 64 48 H192 A16 16 0 0 1 208 64 V118 A64 64 0 0 0 134 224 H64 A16 16 0 0 1 48 208 Z')
icon('report-search', BZ, ['search report', 'audit', 'review', 'clipboard'],
     line=[P(rs_body), P(rs_body2), R(88, 32, 80, 40, 10), C(*MG, 32), L(195, 195, 214, 214)],
     detail=[L(88, 112, 144, 112), L(88, 144, 112, 144)],
     area=[P(rs_area), C(*MG, 32)], hole=cb_hole)

# ================================================================ Contract / file signature
filep = 'M56 32 H152 L200 80 V224 H56 Z'
fold = 'M152 32 V80 H200'
icon('contract', BZ, ['contract', 'agreement', 'document', 'signature'],
     line=[P(filep)], detail=[P(fold), L(88, 120, 168, 120), L(88, 152, 168, 152), L(124, 192, 168, 192)], dotcut=[C(92, 192, 16)],
     area=[P(filep)])
icon('file-signature', BZ, ['contract', 'agreement', 'sign', 'document'],
     line=[P(filep)], detail=[P(fold), L(88, 192, 168, 192),
                              P('M84 152 C96 120 112 112 112 136 C112 160 124 164 136 140 C144 124 156 128 168 148')],
     area=[P(filep)])

# ================================================================ Conveyor belt
belt = 'M64 152 H192 A32 32 0 0 1 192 216 H64 A32 32 0 0 1 64 152 Z'
icon('conveyor-belt', BZ, ['conveyor', 'factory', 'logistics', 'belt'],
     line=[P(belt), R(48, 64, 64, 56, 8), R(136, 48, 72, 72, 8)],
     area=[P(belt), R(48, 64, 64, 56, 8), R(136, 48, 72, 72, 8)],
     dotcut=[C(68, 184, 16), C(128, 184, 16), C(188, 184, 16)])

# ================================================================ Easel / presentation
icon('easel', BZ, ['easel', 'presentation board', 'whiteboard', 'stand'],
     line=[R(40, 48, 176, 112, 14), L(128, 32, 128, 48), L(96, 160, 72, 224), L(160, 160, 184, 224), L(128, 160, 128, 208)],
     area=[R(40, 48, 176, 112, 14)])

board = R(32, 40, 192, 136, 14)
legs = [L(104, 176, 80, 224), L(152, 176, 176, 224)]


def pres(name, tags, **kw):
    icon(name, BZ, tags, line=[board] + legs + kw.pop('line', []), area=[board], **kw)


pres('presentation', ['presentation', 'board', 'easel', 'slides'])
pres('presentation-x', ['presentation', 'close', 'board', 'x'], detail=[L(108, 88, 148, 128), L(148, 88, 108, 128)])
pres('presentation-play', ['presentation', 'start', 'play', 'slideshow'], detail=[PG([(112, 80), (156, 108), (112, 136)])])
pres('presentation-plus', ['presentation', 'add', 'board', 'plus'], detail=[L(128, 80, 128, 136), L(100, 108, 156, 108)])
pres('presentation-check', ['presentation', 'approved', 'board', 'check'], detail=[PL([(100, 110), (120, 130), (156, 90)])])
pres('presentation-minus', ['presentation', 'remove', 'board', 'minus'], detail=[L(100, 108, 156, 108)])
u = (math.sqrt(0.5), -math.sqrt(0.5)); n = (math.sqrt(0.5), math.sqrt(0.5))
tip = (104, 140); back = (tip[0] + 80 * u[0], tip[1] + 80 * u[1]); sh = (tip[0] + 26 * u[0], tip[1] + 26 * u[1])
pw = 14
pen = [tip, (sh[0] + pw * n[0], sh[1] + pw * n[1]), (back[0] + pw * n[0], back[1] + pw * n[1]),
       (back[0] - pw * n[0], back[1] - pw * n[1]), (sh[0] - pw * n[0], sh[1] - pw * n[1])]
pres('presentation-pencil', ['presentation', 'edit', 'board', 'pencil'], detail=[PG(pen)])
icon('presentation-slash', BZ, ['presentation', 'off', 'disabled', 'hidden'],
     line=[board] + legs + [L(48, 48, 208, 208)])

icon('presenter', BZ, ['presentation', 'speaker', 'co-present', 'lecture'],
     line=[C(68, 80, 28), P('M32 216 V180 A36 36 0 0 1 104 180 V216'), R(120, 40, 104, 96, 12), L(172, 136, 172, 216)],
     detail=[L(148, 72, 196, 72), L(148, 104, 180, 104)],
     area=[C(68, 80, 28), P('M32 216 V180 A36 36 0 0 1 104 180 V216 Z'), R(120, 40, 104, 96, 12)])

# ================================================================ Gears
g1 = gear_path((88, 88), 40, 56, 7, phase=12, half_root=14, half_tip=8)
g2 = gear_path((178, 178), 32, 46, 6, phase=5, half_root=15, half_tip=8)
icon('gears', BZ, ['manufacturing', 'machinery', 'process', 'mechanism'],
     line=[P(g1), P(g2)], area=[P(g1), P(g2)], dotcut=[C(88, 88, 14), C(178, 178, 11)])

# ================================================================ Growth
leaf_l = 'M128 160 C128 120 104 104 64 104 C64 144 88 160 128 160 Z'
leaf_r = 'M128 128 C128 80 152 56 200 56 C200 104 176 128 128 128 Z'
icon('growth', BZ, ['growth', 'sprout', 'grow', 'progress'],
     line=[L(128, 216, 128, 128), P(leaf_l), P(leaf_r), L(72, 216, 184, 216)], area=[P(leaf_l), P(leaf_r)])

# ================================================================ Hard hat
dome = 'M56 168 V144 A72 72 0 0 1 200 144 V168'
brim = 'M32 168 H224 V184 A16 16 0 0 1 208 200 H48 A16 16 0 0 1 32 184 Z'
icon('hard-hat', BZ, ['worker', 'construction', 'hard hat', 'safety', 'helmet'],
     line=[P(dome), P(brim)], detail=[L(104, 112, 104, 168), L(152, 112, 152, 168)], area=[P(dome + ' Z'), P(brim)])

# ================================================================ Name tag
icon('name-tag', BZ, ['name tag', 'badge', 'hello', 'identity'],
     line=[R(32, 56, 192, 152, 16)], detail=[L(112, 92, 144, 92), L(72, 140, 184, 140), L(72, 172, 144, 172)],
     area=[R(32, 56, 192, 152, 16)])

# ================================================================ Oil pump
head = R(40, 64, 40, 72, 12)
icon('oil-pump', BZ, ['oil', 'pumpjack', 'petroleum', 'industry'],
     line=[head, L(80, 88, 208, 88), PL([(104, 216), (136, 88), (168, 216)]), L(60, 136, 60, 216), L(200, 88, 200, 144),
           C(200, 164, 20), L(32, 216, 224, 216)],
     area=[head, C(200, 164, 20)])

# ================================================================ Pallet
icon('pallet', BZ, ['pallet', 'warehouse', 'logistics', 'shipping'],
     line=[L(32, 168, 224, 168), L(32, 216, 224, 216), L(48, 168, 48, 216), L(128, 168, 128, 216), L(208, 168, 208, 216),
           R(48, 56, 80, 80, 8), R(144, 88, 64, 48, 8)],
     detail=[L(88, 56, 88, 84)],
     area=[R(48, 56, 80, 80, 8), R(144, 88, 64, 48, 8)])

# ================================================================ Punch clock
icon('punch-clock', BZ, ['time clock', 'clock in', 'attendance', 'timesheet'],
     line=[R(48, 32, 160, 192, 16)], detail=[C(128, 104, 44), PL([(128, 80), (128, 104), (148, 116)]), L(96, 184, 160, 184)],
     area=[R(48, 32, 160, 192, 16)])

# ================================================================ Scale platform
icon('scale-platform', BZ, ['industrial scale', 'weigh', 'platform', 'warehouse'],
     line=[R(32, 184, 192, 32, 12), L(184, 104, 184, 184), R(144, 40, 80, 64, 12), R(48, 120, 88, 64, 8)],
     detail=[L(168, 72, 200, 72)],
     area=[R(32, 184, 192, 32, 12), R(144, 40, 80, 64, 12), R(48, 120, 88, 64, 8)])

# ================================================================ Stamp
kc = (128, 68); kr = 32
k1 = (112, kc[1] + math.sqrt(kr * kr - 16 * 16)); k2 = (144, k1[1])
stamp_top = f'M92 144 C92 124 112 120 {pt(k1)} A{kr} {kr} 0 1 1 {pt(k2)} C144 120 164 124 164 144'
stamp_base = R(40, 144, 176, 40, 12)
icon('stamp', BZ, ['approval', 'stamp', 'approve', 'seal', 'rubber stamp'],
     line=[P(stamp_top), stamp_base, L(56, 216, 200, 216)], area=[P(stamp_top + ' Z'), stamp_base])
icon('stamp-slash', BZ, ['stamp', 'off', 'disabled', 'hidden'],
     line=[P(stamp_top), stamp_base, L(56, 216, 200, 216), L(40, 40, 216, 216)])

# ================================================================ Strategy
icon('strategy', BZ, ['strategy', 'playbook', 'tactics', 'plan'],
     line=[C(72, 72, 32), L(156, 160, 212, 216), L(212, 160, 156, 216), P('M120 72 C168 72 184 92 184 128'),
           PL([(156, 104), (184, 132), (212, 104)])])

# ================================================================ Subtask
icon('subtask', BZ, ['subtask', 'tasks', 'checklist', 'hierarchy'],
     line=[R(32, 40, 64, 64, 12), L(128, 72, 224, 72), P('M64 104 V176 H96'), R(96, 144, 64, 64, 12), L(192, 176, 224, 176)],
     detail=[PL([(50, 72), (60, 82), (78, 62)])],
     area=[R(32, 40, 64, 64, 12), R(96, 144, 64, 64, 12)])

# ================================================================ Target arrow
TC = (112, 144)
icon('target-arrow', BZ, ['goal', 'bullseye', 'arrow', 'aim'],
     line=[C(*TC, 80), L(169, 87, 192, 64), PL([(192, 32), (192, 64), (224, 64)])],
     detail=[C(*TC, 40), L(112, 144, 169, 87)],
     area=[C(*TC, 80)])

# ================================================================ Warehouse
wh = 'M32 216 V96 L128 40 L224 96 V216 Z'
icon('warehouse', BZ, ['warehouse', 'storage', 'inventory', 'logistics', 'depot'],
     line=[P(wh)], detail=[P('M64 216 V112 H192 V216'), L(64, 144, 192, 144), R(100, 176, 56, 40, 6)],
     area=[P(wh)])

print(save(overwrite=True))
