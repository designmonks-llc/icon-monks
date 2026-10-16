"""One-time authoring script: writes the original Monks icon sources (256 grid).

Roles:
  line    stroked in outline weights, merged into the fill weight
  detail  stroked in outline weights, knocked out of the fill weight
  area    duotone tint, merged into the fill weight
  hole    cut out of the fill weight only
  dot     solid dot (radius scales with weight), merged into fill
  dotcut  solid dot in outline weights, knocked out of the fill weight
"""
import math, os, sys, json

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s

def pt(p):
    return f'{f(p[0])} {f(p[1])}'

def rot(points, deg, c=(128, 128)):
    a = math.radians(deg)
    out = []
    for x, y in points:
        dx, dy = x - c[0], y - c[1]
        out.append((c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a)))
    return out

def poly(points, close=False):
    d = 'M' + ' L'.join(pt(p) for p in points)
    return d + (' Z' if close else '')

def P(d):
    return f'<path d="{d}"/>'

def C(cx, cy, r):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>'

def R(x, y, w, h, rx=0):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"' + (f' rx="{f(rx)}"' if rx else '') + '/>'

def E(cx, cy, rx, ry):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"/>'

def L(x1, y1, x2, y2):
    return P(f'M{f(x1)} {f(y1)} L{f(x2)} {f(y2)}')

def PL(points):
    return P(poly(points))

def PG(points):
    return P(poly(points, True))

def polar(c, r, deg):
    a = math.radians(deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))

def arc_to(c, r, p, q, prefer):
    """SVG arc command from p to q on circle (c, r); prefer(mid) -> score, higher wins."""
    a1 = math.atan2(p[1] - c[1], p[0] - c[0])
    a2 = math.atan2(q[1] - c[1], q[0] - c[0])
    span1 = (a2 - a1) % (2 * math.pi)  # sweep=1 (increasing angle)
    cands = []
    for sweep, span in ((1, span1), (0, 2 * math.pi - span1)):
        mid = a1 + (span / 2 if sweep else -span / 2)
        m = (c[0] + r * math.cos(mid), c[1] + r * math.sin(mid))
        cands.append((prefer(m), sweep, span))
    _, sweep, span = max(cands)
    large = 1 if span > math.pi else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(q)}'

def circle_x(c1, r1, c2, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    p1 = (mx + h * dy / d, my - h * dx / d)
    p2 = (mx - h * dy / d, my + h * dx / d)
    return sorted([p1, p2], key=lambda p: p[1])  # upper first

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

ICONS = []

def icon(name, category, tags, line=(), detail=(), area=(), hole=(), dot=(), dotcut=()):
    ICONS.append(dict(name=name, category=category, tags=tags, line=line, detail=detail,
                      area=area, hole=hole, dot=dot, dotcut=dotcut))

# ---------------------------------------------------------------- Arrows
icon('plus', 'Interface', ['add', 'new', 'create'], line=[L(128, 40, 128, 216), L(40, 128, 216, 128)])
icon('minus', 'Interface', ['subtract', 'remove'], line=[L(40, 128, 216, 128)])
icon('x', 'Interface', ['close', 'cancel', 'dismiss', 'times'], line=[L(60, 60, 196, 196), L(196, 60, 60, 196)])
icon('check', 'Interface', ['done', 'confirm', 'tick', 'ok'], line=[PL([(40, 136), (96, 192), (216, 72)])])

ARROW = [[(40, 128), (216, 128)], [(144, 56), (216, 128), (144, 200)]]
CARET = [(96, 48), (176, 128), (96, 208)]
for nm, deg in (('right', 0), ('down', 90), ('left', 180), ('up', 270)):
    icon(f'arrow-{nm}', 'Arrows', ['direction', nm, 'pointer'], line=[PL(rot(s, deg)) for s in ARROW])
    icon(f'caret-{nm}', 'Arrows', ['chevron', 'direction', nm], line=[PL(rot(CARET, deg))])

c = (128, 132); r = 76
end = polar(c, r, -45)
icon('arrow-clockwise', 'Arrows', ['refresh', 'reload', 'redo', 'rotate'],
     line=[P(f'M{pt(polar(c, r, 0))} A{r} {r} 0 1 1 {pt(end)}'),
           PL([(end[0] - 44, end[1]), end, (end[0], end[1] - 44)])])
end2 = (256 - end[0], end[1])
icon('arrow-counter-clockwise', 'Arrows', ['undo', 'back', 'rotate', 'reset'],
     line=[P(f'M{pt((256 - polar(c, r, 0)[0], c[1]))} A{r} {r} 0 1 0 {pt(end2)}'),
           PL([(end2[0] + 44, end2[1]), end2, (end2[0], end2[1] - 44)])])
icon('trend-up', 'Arrows', ['chart', 'growth', 'increase', 'stocks'],
     line=[PL([(32, 192), (96, 128), (136, 168), (216, 88)]), PL([(160, 88), (216, 88), (216, 144)])])
icon('corners-out', 'Arrows', ['fullscreen', 'expand', 'maximize'],
     line=[PL([(40, 96), (40, 40), (96, 40)]), PL([(160, 40), (216, 40), (216, 96)]),
           PL([(216, 160), (216, 216), (160, 216)]), PL([(96, 216), (40, 216), (40, 160)])])

# ---------------------------------------------------------------- Interface
icon('magnifying-glass', 'Interface', ['search', 'find', 'zoom', 'lookup'],
     line=[C(112, 112, 72), L(163, 163, 216, 216)], area=[C(112, 112, 72)])

gear = []
cg = (128, 128)
for i in range(8):
    t = i * 45
    gear += [polar(cg, 72, t - 16), polar(cg, 92, t - 9), polar(cg, 92, t + 9), polar(cg, 72, t + 16)]
gd = 'M' + pt(gear[0])
for i in range(8):
    a, b, cc, dd = gear[i * 4:i * 4 + 4]
    if i:
        gd += f' A72 72 0 0 1 {pt(a)}'
    gd += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
gd += f' A72 72 0 0 1 {pt(gear[0])} Z'
icon('gear', 'Interface', ['settings', 'preferences', 'cog', 'options'],
     line=[P(gd), C(128, 128, 28)], area=[P(gd)], hole=[C(128, 128, 20)])

icon('heart', 'Interface', ['like', 'love', 'favorite', 'health'],
     line=[P('M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z')],
     area=[P('M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z')])

star = []
for i in range(10):
    star.append(polar((128, 136), 100 if i % 2 == 0 else 44, -90 + i * 36))
icon('star', 'Interface', ['favorite', 'rating', 'bookmark', 'like'], line=[PG(star)], area=[PG(star)])

sp = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'
icon('sparkle', 'Interface', ['ai', 'magic', 'new', 'shine', 'star'], line=[P(sp)], area=[P(sp)])

bell = 'M48 184 C64 168 72 144 72 112 A56 56 0 0 1 184 112 C184 144 192 168 208 184 Z'
icon('bell', 'Interface', ['notification', 'alert', 'alarm', 'ring'],
     line=[P(bell), P('M108 200 A20 20 0 0 0 148 200'), L(128, 40, 128, 56)], area=[P(bell)])

icon('eye', 'Interface', ['view', 'visible', 'show', 'watch', 'see'],
     line=[P('M24 128 C56 72 96 56 128 56 C160 56 200 72 232 128 C200 184 160 200 128 200 C96 200 56 184 24 128 Z')],
     detail=[C(128, 128, 36)],
     area=[P('M24 128 C56 72 96 56 128 56 C160 56 200 72 232 128 C200 184 160 200 128 200 C96 200 56 184 24 128 Z')])

trash_body = 'M64 64 L72 208 A16 16 0 0 0 88 224 H168 A16 16 0 0 0 184 208 L192 64'
icon('trash', 'Interface', ['delete', 'remove', 'bin', 'garbage'],
     line=[L(40, 64, 216, 64), P('M96 64 V48 A16 16 0 0 1 112 32 H144 A16 16 0 0 1 160 48 V64'), P(trash_body)],
     detail=[L(108, 104, 108, 184), L(148, 104, 148, 184)], area=[P(trash_body + ' Z')])

pencil = [(40, 216), (56, 160), (168, 48), (208, 88), (96, 200)]
icon('pencil', 'Interface', ['edit', 'write', 'compose', 'draw'],
     line=[PG(pencil)], detail=[L(140, 76, 180, 116)], area=[PG(pencil)])

icon('bookmark', 'Interface', ['save', 'favorite', 'read later'],
     line=[P('M64 32 H192 V224 L128 184 L64 224 Z')], area=[P('M64 32 H192 V224 L128 184 L64 224 Z')])

icon('list', 'Interface', ['menu', 'hamburger', 'navigation', 'lines'],
     line=[L(40, 64, 216, 64), L(40, 128, 216, 128), L(40, 192, 216, 192)])
icon('list-bullets', 'Interface', ['list', 'items', 'todo', 'unordered'],
     line=[L(96, 64, 216, 64), L(96, 128, 216, 128), L(96, 192, 216, 192)],
     dot=[C(48, 64, 16), C(48, 128, 16), C(48, 192, 16)])
icon('dots-three', 'Interface', ['more', 'menu', 'ellipsis', 'overflow'],
     dot=[C(56, 128, 16), C(128, 128, 16), C(200, 128, 16)])
icon('squares-four', 'Interface', ['grid', 'apps', 'dashboard', 'layout'],
     line=[R(40, 40, 72, 72, 10), R(144, 40, 72, 72, 10), R(40, 144, 72, 72, 10), R(144, 144, 72, 72, 10)],
     area=[R(40, 40, 72, 72, 10), R(144, 40, 72, 72, 10), R(40, 144, 72, 72, 10), R(144, 144, 72, 72, 10)])
icon('funnel', 'Interface', ['filter', 'sort', 'refine'],
     line=[P('M32 48 H224 L152 136 V200 L104 224 V136 Z')], area=[P('M32 48 H224 L152 136 V200 L104 224 V136 Z')])
icon('sliders', 'Interface', ['settings', 'controls', 'adjust', 'equalizer'],
     line=[L(40, 80, 72, 80), L(120, 80, 216, 80), L(40, 176, 136, 176), L(184, 176, 216, 176),
           C(96, 80, 24), C(160, 176, 24)],
     area=[C(96, 80, 24), C(160, 176, 24)])
icon('copy', 'Interface', ['duplicate', 'clipboard', 'clone'],
     line=[R(80, 80, 144, 144, 14),
           P('M176 80 V48 A16 16 0 0 0 160 32 H48 A16 16 0 0 0 32 48 V160 A16 16 0 0 0 48 176 H80')],
     area=[R(80, 80, 144, 144, 14)])
icon('cursor', 'Interface', ['pointer', 'mouse', 'click', 'select'],
     line=[PG([(48, 40), (208, 112), (136, 136), (112, 208)])],
     area=[PG([(48, 40), (208, 112), (136, 136), (112, 208)])])
icon('power', 'Interface', ['on', 'off', 'shutdown', 'start'],
     line=[L(128, 40, 128, 120), P('M88 72 A80 80 0 1 0 168 72')])
icon('hash', 'Interface', ['hashtag', 'number', 'channel', 'tag'],
     line=[L(104, 40, 88, 216), L(168, 40, 152, 216), L(40, 96, 216, 96), L(40, 160, 216, 160)])

# Status circles
for nm, tags, det, dc in [
    ('check-circle', ['success', 'done', 'complete', 'verified'], [PL([(88, 132), (116, 160), (172, 104)])], []),
    ('x-circle', ['error', 'close', 'cancel', 'fail'], [L(96, 96, 160, 160), L(160, 96, 96, 160)], []),
    ('plus-circle', ['add', 'create', 'new'], [L(128, 84, 128, 172), L(84, 128, 172, 128)], []),
    ('info', ['information', 'help', 'about', 'details'], [L(128, 120, 128, 176)], [C(128, 84, 16)]),
    ('question', ['help', 'faq', 'support', 'unknown'],
     [P('M100 104 A28 28 0 1 1 140 129 C132 133 128 138 128 146 V150')], [C(128, 184, 16)]),
]:
    icon(nm, 'Interface', tags, line=[C(128, 128, 96)], detail=det, area=[C(128, 128, 96)], dotcut=dc)
icon('warning', 'Interface', ['alert', 'caution', 'danger', 'triangle'],
     line=[PG([(128, 40), (224, 208), (32, 208)])], detail=[L(128, 104, 128, 144)],
     area=[PG([(128, 40), (224, 208), (32, 208)])], dotcut=[C(128, 176, 16)])
icon('smiley', 'People', ['face', 'emoji', 'happy', 'smile'],
     line=[C(128, 128, 96)], detail=[P('M88 152 A48 48 0 0 0 168 152')], area=[C(128, 128, 96)],
     dotcut=[C(96, 108, 16), C(160, 108, 16)])

# ---------------------------------------------------------------- People
body = 'M48 216 C48 168 84 148 128 148 C172 148 208 168 208 216'
icon('user', 'People', ['person', 'account', 'profile', 'avatar'],
     line=[C(128, 88, 44), P(body)], area=[C(128, 88, 44), P(body + ' Z')])
fb = 'M32 208 C32 168 60 152 100 152 C140 152 168 168 168 208'
icon('users', 'People', ['people', 'team', 'group', 'community'],
     line=[C(100, 100, 36), P(fb), P('M152 56 A32 32 0 1 1 168 116'), P('M184 144 C212 148 228 168 228 200')],
     area=[C(100, 100, 36), P(fb + ' Z')])

# ---------------------------------------------------------------- Communication
icon('envelope', 'Communication', ['email', 'mail', 'message', 'inbox'],
     line=[R(32, 56, 192, 144, 14)], detail=[PL([(48, 76), (128, 140), (208, 76)])], area=[R(32, 56, 192, 144, 14)])
bub = 'M80 200 L40 224 V72 A16 16 0 0 1 56 56 H200 A16 16 0 0 1 216 72 V184 A16 16 0 0 1 200 200 Z'
icon('chat', 'Communication', ['message', 'comment', 'bubble', 'talk'], line=[P(bub)], area=[P(bub)])
icon('chat-text', 'Communication', ['message', 'comment', 'bubble', 'conversation'],
     line=[P(bub)], detail=[L(88, 108, 168, 108), L(88, 148, 144, 148)], area=[P(bub)])
plane = [(224, 32), (32, 104), (112, 144), (152, 224)]
icon('paper-plane', 'Communication', ['send', 'message', 'submit', 'share'],
     line=[PG(plane)], detail=[L(112, 144, 176, 80)], area=[PG(plane)])
share_nodes = [(64, 128), (184, 64), (184, 192)]
def seg(a, b, ra, rb):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rb, b[1] - uy * rb)
icon('share-network', 'Communication', ['share', 'connect', 'social', 'nodes'],
     line=[C(*n, 24) for n in share_nodes] + [seg(share_nodes[0], share_nodes[1], 24, 24), seg(share_nodes[0], share_nodes[2], 24, 24)],
     area=[C(*n, 24) for n in share_nodes])
spk = 'M32 104 V152 H72 L128 200 V56 L72 104 Z'
icon('speaker-high', 'Media', ['volume', 'sound', 'audio', 'loud'],
     line=[P(spk), P('M164 96 A48 48 0 0 1 164 160'), P('M192 64 A88 88 0 0 1 192 192')], area=[P(spk)])
icon('microphone', 'Media', ['record', 'voice', 'audio', 'mic'],
     line=[R(96, 32, 64, 120, 32), P('M64 128 A64 64 0 0 0 192 128'), L(128, 192, 128, 224)],
     area=[R(96, 32, 64, 120, 32)])
icon('bell-ringing', 'Communication', ['notification', 'alert', 'active', 'ring'],
     line=[P(bell), P('M108 200 A20 20 0 0 0 148 200'), L(128, 40, 128, 56), P('M32 104 A112 112 0 0 1 56 56'),
           P('M224 104 A112 112 0 0 0 200 56')], area=[P(bell)])

# ---------------------------------------------------------------- Media
icon('play', 'Media', ['start', 'video', 'music', 'resume'],
     line=[PG([(80, 48), (208, 128), (80, 208)])], area=[PG([(80, 48), (208, 128), (80, 208)])])
icon('pause', 'Media', ['stop', 'hold', 'video', 'music'],
     line=[R(64, 48, 40, 160, 10), R(152, 48, 40, 160, 10)], area=[R(64, 48, 40, 160, 10), R(152, 48, 40, 160, 10)])
icon('music-note', 'Media', ['music', 'song', 'audio', 'melody'],
     line=[C(88, 184, 32), L(120, 184, 120, 40), P('M120 40 C152 48 192 64 184 112')], area=[C(88, 184, 32)])
cam = ('M32 88 A16 16 0 0 1 48 72 H80 L96 48 H160 L176 72 H208 A16 16 0 0 1 224 88 V192 '
       'A16 16 0 0 1 208 208 H48 A16 16 0 0 1 32 192 Z')
icon('camera', 'Media', ['photo', 'picture', 'snapshot', 'lens'], line=[P(cam)], detail=[C(128, 140, 36)], area=[P(cam)])
icon('image', 'Media', ['photo', 'picture', 'gallery', 'landscape'],
     line=[R(32, 48, 192, 160, 14)], detail=[PL([(44, 188), (96, 136), (144, 184), (168, 160), (212, 204)]), C(168, 100, 16)],
     area=[R(32, 48, 192, 160, 14)])

# ---------------------------------------------------------------- Devices
icon('device-mobile', 'Devices', ['phone', 'smartphone', 'mobile', 'cell'],
     line=[R(72, 32, 112, 192, 20)], detail=[L(112, 64, 144, 64)], area=[R(72, 32, 112, 192, 20)])
icon('monitor', 'Devices', ['desktop', 'screen', 'display', 'computer'],
     line=[R(32, 48, 192, 128, 14), L(128, 176, 128, 208), L(88, 208, 168, 208)], area=[R(32, 48, 192, 128, 14)])
icon('laptop', 'Devices', ['computer', 'notebook', 'macbook', 'device'],
     line=[R(52, 56, 152, 112, 12), L(28, 196, 228, 196)], area=[R(52, 56, 152, 112, 12)])
icon('battery', 'Devices', ['power', 'charge', 'energy', 'level'],
     line=[R(32, 72, 168, 112, 16), L(224, 108, 224, 148)], detail=[L(64, 104, 64, 152), L(96, 104, 96, 152)],
     area=[R(32, 72, 168, 112, 16)])
wc = (128, 200)
wifi = []
for rr in (44, 88, 132):
    a = polar(wc, rr, -135); b = polar(wc, rr, -45)
    wifi.append(P(f'M{pt(a)} A{rr} {rr} 0 0 1 {pt(b)}'))
icon('wifi', 'Devices', ['wireless', 'internet', 'network', 'signal'], line=wifi, dot=[C(128, 200, 16)])
icon('lightbulb', 'Devices', ['idea', 'light', 'tip', 'innovation'],
     line=[P('M96 176 C96 152 64 136 64 96 A64 64 0 0 1 192 96 C192 136 160 152 160 176 Z'), L(104, 208, 152, 208)],
     area=[P('M96 176 C96 152 64 136 64 96 A64 64 0 0 1 192 96 C192 136 160 152 160 176 Z')])

# ---------------------------------------------------------------- Files
icon('folder', 'Files', ['directory', 'files', 'organize', 'archive'],
     line=[P('M32 72 A16 16 0 0 1 48 56 H96 L120 80 H208 A16 16 0 0 1 224 96 V192 A16 16 0 0 1 208 208 H48 A16 16 0 0 1 32 192 Z')],
     area=[P('M32 72 A16 16 0 0 1 48 56 H96 L120 80 H208 A16 16 0 0 1 224 96 V192 A16 16 0 0 1 208 208 H48 A16 16 0 0 1 32 192 Z')])
filep = 'M56 32 H152 L200 80 V224 H56 Z'
icon('file', 'Files', ['document', 'page', 'paper', 'blank'],
     line=[P(filep)], detail=[P('M152 32 V80 H200')], area=[P(filep)])
icon('file-text', 'Files', ['document', 'text', 'article', 'notes'],
     line=[P(filep)], detail=[P('M152 32 V80 H200'), L(88, 128, 168, 128), L(88, 160, 168, 160), L(88, 192, 136, 192)],
     area=[P(filep)])
tray = 'M40 168 V200 A16 16 0 0 0 56 216 H200 A16 16 0 0 0 216 200 V168'
icon('download', 'Files', ['save', 'import', 'get', 'arrow'],
     line=[L(128, 40, 128, 160), PL([(80, 112), (128, 160), (176, 112)]), P(tray)])
icon('upload', 'Files', ['export', 'send', 'publish', 'arrow'],
     line=[L(128, 160, 128, 40), PL([(80, 88), (128, 40), (176, 88)]), P(tray)])
icon('calendar', 'Files', ['date', 'schedule', 'event', 'month'],
     line=[R(40, 48, 176, 168, 14), L(88, 32, 88, 72), L(168, 32, 168, 72)], detail=[L(40, 104, 216, 104)],
     area=[R(40, 48, 176, 168, 14)])
icon('clock', 'Interface', ['time', 'watch', 'hour', 'schedule'],
     line=[C(128, 128, 96)], detail=[PL([(128, 72), (128, 128), (168, 152)])], area=[C(128, 128, 96)])
icon('chart-bar', 'Files', ['graph', 'analytics', 'statistics', 'data'],
     line=[R(48, 120, 40, 72, 8), R(108, 56, 40, 136, 8), R(168, 96, 40, 96, 8), L(32, 216, 224, 216)],
     area=[R(48, 120, 40, 72, 8), R(108, 56, 40, 136, 8), R(168, 96, 40, 96, 8)])
icon('stack', 'Files', ['layers', 'stacked', 'levels', 'depth'],
     line=[PG([(128, 40), (224, 92), (128, 144), (32, 92)]), PL([(32, 132), (128, 184), (224, 132)]),
           PL([(32, 172), (128, 224), (224, 172)])],
     area=[PG([(128, 40), (224, 92), (128, 144), (32, 92)])])
cube = [(128, 32), (216, 80), (216, 176), (128, 224), (40, 176), (40, 80)]
icon('cube', 'Files', ['box', '3d', 'package', 'product'],
     line=[PG(cube)], detail=[PL([(40, 80), (128, 128), (216, 80)]), L(128, 128, 128, 224)], area=[PG(cube)])

# ---------------------------------------------------------------- Security
icon('lock', 'Security', ['secure', 'private', 'password', 'locked'],
     line=[R(48, 104, 160, 112, 14), P('M88 104 V72 A40 40 0 0 1 168 72 V104')], detail=[L(128, 144, 128, 176)],
     area=[R(48, 104, 160, 112, 14)])
icon('lock-open', 'Security', ['unlocked', 'unsecure', 'open', 'access'],
     line=[R(48, 104, 160, 112, 14), P('M88 104 V72 A40 40 0 0 1 166 60')], detail=[L(128, 144, 128, 176)],
     area=[R(48, 104, 160, 112, 14)])
icon('key', 'Security', ['password', 'access', 'unlock', 'login'],
     line=[C(92, 164, 52), L(129, 127, 208, 48), L(192, 64, 216, 88), L(164, 92, 184, 112)],
     detail=[C(92, 164, 16)], area=[C(92, 164, 52)])
shield = 'M128 32 L208 64 V120 C208 176 168 208 128 224 C88 208 48 176 48 120 V64 Z'
icon('shield', 'Security', ['protection', 'security', 'safe', 'guard'], line=[P(shield)], area=[P(shield)])
icon('shield-check', 'Security', ['verified', 'secure', 'protected', 'trust'],
     line=[P(shield)], detail=[PL([(96, 128), (120, 152), (164, 108)])], area=[P(shield)])

# ---------------------------------------------------------------- Maps & places
house_area = 'M48 112 L128 44 L208 112 V208 H48 Z'
icon('house', 'Maps', ['home', 'building', 'residence', 'main'],
     line=[P('M48 112 V208 H208 V112'), PL([(32, 124), (128, 40), (224, 124)]), P('M108 208 V164 A20 20 0 0 1 148 164 V208')],
     area=[P(house_area)], hole=[P('M116 208 V164 A12 12 0 0 1 140 164 V208 Z')])
pin = 'M128 224 C128 224 56 160 56 104 A72 72 0 0 1 200 104 C200 160 128 224 128 224 Z'
icon('map-pin', 'Maps', ['location', 'place', 'marker', 'gps'], line=[P(pin)], detail=[C(128, 104, 24)], area=[P(pin)])
icon('globe', 'Maps', ['world', 'earth', 'internet', 'language', 'web'],
     line=[C(128, 128, 96)], detail=[E(128, 128, 40, 96), L(32, 128, 224, 128)], area=[C(128, 128, 96)])
flag = 'M56 48 C104 24 136 72 200 48 V160 C136 184 104 136 56 160 Z'
icon('flag', 'Maps', ['report', 'milestone', 'country', 'goal'], line=[L(56, 224, 56, 40), P(flag)], area=[P(flag)])

# ---------------------------------------------------------------- Weather
icon('sun', 'Weather', ['light', 'day', 'bright', 'weather'],
     line=[C(128, 128, 44)] + [L(*polar((128, 128), 68, a), *polar((128, 128), 92, a)) for a in range(0, 360, 45)],
     area=[C(128, 128, 44)])
c1, r1, c2, r2 = (120, 136), 88, (176, 84), 72
p, q = circle_x(c1, r1, c2, r2)
moon = (f'M{pt(p)} ' + arc_to(c1, r1, p, q, lambda m: dist(m, c2)) + ' ' +
        arc_to(c2, r2, q, p, lambda m: -dist(m, c1)) + ' Z')
icon('moon', 'Weather', ['night', 'dark mode', 'sleep', 'crescent'], line=[P(moon)], area=[P(moon)])
Lc, Lr, Mc, Mr, Rc, Rr = (84, 152), 40, (132, 116), 60, (180, 148), 44
irm = circle_x(Mc, Mr, Rc, Rr)[0]
iml = circle_x(Mc, Mr, Lc, Lr)[0]
cloud = (f'M84 192 H180 ' + arc_to(Rc, Rr, (180, 192), irm, lambda m: dist(m, Mc)) + ' ' +
         arc_to(Mc, Mr, irm, iml, lambda m: -m[1]) + ' ' + arc_to(Lc, Lr, iml, (84, 192), lambda m: dist(m, Mc)) + ' Z')
icon('cloud', 'Weather', ['weather', 'storage', 'sky', 'overcast'], line=[P(cloud)], area=[P(cloud)])
bolt = 'M144 32 L56 144 H120 L104 224 L200 108 H136 Z'
icon('lightning', 'Weather', ['flash', 'energy', 'power', 'fast', 'bolt'], line=[P(bolt)], area=[P(bolt)])
drop = 'M128 32 C104 64 64 112 64 152 A64 64 0 0 0 192 152 C192 112 152 64 128 32 Z'
icon('drop', 'Weather', ['water', 'rain', 'liquid', 'humidity'], line=[P(drop)], area=[P(drop)])

# ---------------------------------------------------------------- Commerce
cart = 'M65 80 H216 L192 160 H84 Z'
icon('shopping-cart', 'Commerce', ['cart', 'buy', 'checkout', 'ecommerce'],
     line=[PL([(24, 40), (56, 40), (84, 160), (192, 160), (216, 80), (65, 80)]), C(96, 204, 16), C(184, 204, 16)],
     area=[P(cart)])
bag = 'M48 80 H208 L200 216 H56 Z'
icon('shopping-bag', 'Commerce', ['bag', 'store', 'buy', 'shop'],
     line=[P(bag), P('M96 112 V72 A32 32 0 0 1 160 72 V112')], area=[P(bag)])
tag = 'M40 40 H128 L224 136 L136 224 L40 128 Z'
icon('tag', 'Commerce', ['label', 'price', 'sale', 'discount'], line=[P(tag)], detail=[C(88, 88, 14)], area=[P(tag)])
icon('credit-card', 'Commerce', ['payment', 'card', 'money', 'billing'],
     line=[R(24, 56, 208, 144, 14)], detail=[L(24, 104, 232, 104), L(56, 160, 96, 160)], area=[R(24, 56, 208, 144, 14)])
cup = 'M48 88 H176 V152 A56 56 0 0 1 120 208 H104 A56 56 0 0 1 48 152 Z'
icon('coffee', 'Commerce', ['cup', 'drink', 'cafe', 'break'],
     line=[P(cup), P('M176 104 H192 A24 24 0 0 1 192 152 H174'), L(88, 32, 88, 56), L(136, 32, 136, 56)], area=[P(cup)])
icon('gift', 'Commerce', ['present', 'reward', 'birthday', 'surprise'],
     line=[R(32, 80, 192, 48, 10), P('M48 128 V208 A8 8 0 0 0 56 216 H200 A8 8 0 0 0 208 208 V128'), L(128, 80, 128, 216),
           P('M128 80 C112 48 72 40 72 64 C72 80 104 80 128 80 C152 80 184 80 184 64 C184 40 144 48 128 80')],
     area=[R(32, 80, 192, 48, 10), P('M48 128 V208 H208 V128 Z')])

# ---------------------------------------------------------------- Development
icon('code', 'Development', ['programming', 'developer', 'html', 'brackets'],
     line=[PL([(72, 72), (32, 128), (72, 184)]), PL([(184, 72), (224, 128), (184, 184)]), L(148, 52, 108, 204)])
icon('terminal', 'Development', ['console', 'command line', 'shell', 'cli'],
     line=[R(32, 48, 192, 160, 14)], detail=[PL([(72, 104), (104, 128), (72, 152)]), L(120, 152, 168, 152)],
     area=[R(32, 48, 192, 160, 14)])

def capsule(cn, h, r, u):
    n = (-u[1], u[0])
    A = (cn[0] - u[0] * h, cn[1] - u[1] * h); B = (cn[0] + u[0] * h, cn[1] + u[1] * h)
    a1 = (A[0] + n[0] * r, A[1] + n[1] * r); b1 = (B[0] + n[0] * r, B[1] + n[1] * r)
    b2 = (B[0] - n[0] * r, B[1] - n[1] * r); a2 = (A[0] - n[0] * r, A[1] - n[1] * r)
    far = lambda m: dist(m, cn)
    return (f'M{pt(a1)} L{pt(b1)} ' + arc_to(B, r, b1, b2, far) + f' L{pt(a2)} ' + arc_to(A, r, a2, a1, far) + ' Z')
u = (1 / math.sqrt(2), -1 / math.sqrt(2))
icon('link', 'Development', ['chain', 'url', 'hyperlink', 'connect'],
     line=[P(capsule((102, 154), 34, 30, u)), P(capsule((154, 102), 34, 30, u))])

# ---------------------------------------------------------------- write
def group(role, items, attrs):
    if not items:
        return ''
    return f'  <g data-role="{role}" {attrs}>\n' + ''.join(f'    {i}\n' for i in items) + '  </g>\n'

STROKE = 'fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"'
for ic in ICONS:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" '
           f'data-category="{ic["category"]}" data-tags="{",".join(ic["tags"])}">\n'
           + group('area', ic['area'], 'fill="currentColor" opacity="0.2"')
           + group('hole', ic['hole'], 'fill="none"')
           + group('line', ic['line'], STROKE)
           + group('detail', ic['detail'], STROKE)
           + group('dot', ic['dot'], 'fill="currentColor"')
           + group('dotcut', ic['dotcut'], 'fill="currentColor"')
           + '</svg>\n')
    with open(os.path.join(OUT, ic['name'] + '.svg'), 'w') as fh:
        fh.write(svg)
print(len(ICONS), 'icons')
