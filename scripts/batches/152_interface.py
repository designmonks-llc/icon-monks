import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

UI = 'Interface'
SLASH = L(48, 48, 208, 208)


def scale_path(d, s, src=(128, 128), dst=(128, 128)):
    """Scale an absolute M/L/C/A/H/V/Z path about src and move it to dst."""
    import re
    toks = re.findall(r'[MLCAHVZ]|-?\d+(?:\.\d+)?', d)
    out, i, cmd = [], 0, None
    X = lambda v: dst[0] + (float(v) - src[0]) * s
    Y = lambda v: dst[1] + (float(v) - src[1]) * s
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; out.append(t); i += 1
            continue
        if cmd in ('M', 'L'):
            out.append(f'{f(X(toks[i]))} {f(Y(toks[i + 1]))}'); i += 2
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(toks[i + k]))} {f(Y(toks[i + k + 1]))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'A':
            rx, ry, rotx, la, sw, x, y = toks[i:i + 7]
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {rotx} {la} {sw} {f(X(x))} {f(Y(y))}'); i += 7
        elif cmd == 'H':
            out.append(f(X(toks[i]))); i += 1
        elif cmd == 'V':
            out.append(f(Y(toks[i]))); i += 1
    return ' '.join(out).replace('M ', 'M').replace(' L ', ' L').replace(' C ', ' C').replace(' A ', ' A')


HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'


def qmark(cx, cy, r=18):
    """Question mark: hook of radius r whose circle centre is (cx, cy); returns (path, dot centre)."""
    a = polar((cx, cy), r, 180)
    b = polar((cx, cy), r, 70)
    stem_top = cy + r + 10
    d = (f'M{pt(a)} A{f(r)} {f(r)} 0 1 1 {pt(b)} '
         f'C{f(b[0] - 5)} {f(b[1] + 3)} {f(cx)} {f(b[1] + 6)} {f(cx)} {f(stem_top)}')
    return d, (cx, stem_top + 26)


# ---------------------------------------------------------------- magnifying glass family
MG = load('magnifying-glass')
LENS, HANDLE = MG['line']
MC = (112, 112)

ht = scale_path(HEART, 0.42, (128, 132), MC)
icon('magnifying-glass-heart', UI, ['search favorites', 'find', 'love', 'magnifier'],
     line=[LENS, HANDLE, P(ht)], area=[P(ht)])

qd, qdot = qmark(112, 94, 17)
icon('magnifying-glass-question', UI, ['magnifying glass', 'help', 'unknown', 'question', 'magnifying'],
     line=[LENS, HANDLE], detail=[P(qd)], area=MG['area'], dotcut=[C(*qdot, 14)])

icon('magnifying-glass-slash', UI, ['no results', 'search off', 'not found', 'disabled'],
     line=[LENS, HANDLE, L(40, 184, 184, 40)])

sk = scale_path(SPARK, 0.44, (128, 128), MC)
icon('magnifying-glass-sparkle', UI, ['ai search', 'smart search', 'find', 'sparkle'],
     line=[LENS, HANDLE, P(sk)], area=[P(sk)])

icon('magnifying-glass-warning', UI, ['magnifying glass', 'warning', 'alert', 'error', 'magnifying'],
     line=[LENS, HANDLE], detail=[L(112, 80, 112, 116)], area=MG['area'], dotcut=[C(112, 146, 14)])

icon('magnifying-glass-x', UI, ['magnifying glass x', 'remove', 'cancel', 'search', 'zoom'],
     line=[LENS, HANDLE], detail=[L(92, 92, 132, 132), L(132, 92, 92, 132)], area=MG['area'])

# ---------------------------------------------------------------- menus
icon('menu-open', UI, ['open menu', 'expand menu', 'navigation', 'drawer'],
     line=[L(40, 64, 216, 64), L(120, 128, 216, 128), L(40, 192, 216, 192), PL([(80, 100), (52, 128), (80, 156)])])

# ---------------------------------------------------------------- dashed plus / minus
CD = load('check-circle-dashed')
icon('minus-circle-dashed', UI, ['remove', 'minus', 'dashed', 'circle', 'minus circle dashed'],
     line=CD['line'], detail=[L(84, 128, 172, 128)], area=CD['area'])
icon('plus-circle-dashed', UI, ['add', 'dashed', 'circle', 'placeholder', 'plus circle dashed'],
     line=CD['line'], detail=[L(128, 84, 128, 172), L(84, 128, 172, 128)], area=CD['area'])

SQD = [P('M32 56 V48 A16 16 0 0 1 48 32 H56'), P('M200 32 H208 A16 16 0 0 1 224 48 V56'),
       P('M224 200 V208 A16 16 0 0 1 208 224 H200'), P('M56 224 H48 A16 16 0 0 1 32 208 V200')]
for a, b in ((88, 112), (144, 168)):
    SQD += [L(a, 32, b, 32), L(a, 224, b, 224), L(32, a, 32, b), L(224, a, 224, b)]
SQ_AREA = [R(24, 24, 208, 208, 24)]
icon('minus-square-dashed', UI, ['remove', 'minus', 'dashed', 'square'],
     line=SQD, detail=[L(84, 128, 172, 128)], area=SQ_AREA)
icon('plus-square-dashed', UI, ['add', 'dashed', 'square', 'placeholder'],
     line=SQD, detail=[L(128, 84, 128, 172), L(84, 128, 172, 128)], area=SQ_AREA)

# ---------------------------------------------------------------- grips, scanning
icon('notches', UI, ['resize grip', 'corner handle', 'drag'],
     line=[L(216, 40, 40, 216), L(216, 104, 104, 216), L(216, 168, 168, 216)])

SCAN = load('scan')['line'][:4]
CUBE = load('cube-focus')
big = lambda e: P(scale_path(e.split('d="')[1].split('"')[0], 1.2))
icon('object-scan', UI, ['object scan', 'detect', 'ar', 'recognition'],
     line=SCAN + [big(CUBE['line'][4])], detail=[big(e) for e in CUBE['detail']], area=[big(e) for e in CUBE['area']])

QRB = CUBE['line'][:4]
qr = [R(72, 72, 36, 36, 8), R(148, 72, 36, 36, 8), R(72, 148, 36, 36, 8)]
icon('qr-code-scan', UI, ['scan qr', 'qr code', 'scanner', 'camera', 'barcode'],
     line=QRB + qr, dot=[C(152, 152, 14), C(184, 184, 14), C(184, 152, 14)])

icon('scan-position', UI, ['position', 'locate', 'scan', 'target'],
     line=QRB + [C(128, 128, 40), L(128, 60, 128, 88), L(128, 168, 128, 196), L(60, 128, 88, 128), L(168, 128, 196, 128)],
     dot=[C(128, 128, 14)])

# ---------------------------------------------------------------- panels and sidebars
WIN = R(32, 48, 192, 160, 14)
for nm, div, cx, d, tags in [
    ('panel-left-close', 96, 160, -1, ['collapse sidebar', 'hide panel', 'left panel']),
    ('panel-left-open', 96, 160, 1, ['expand sidebar', 'show panel', 'left panel']),
    ('panel-right-close', 160, 96, 1, ['collapse panel', 'hide panel', 'right panel']),
    ('panel-right-open', 160, 96, -1, ['expand panel', 'show panel', 'right panel']),
]:
    tip = cx + 14 * d
    icon(nm, UI, tags, line=[WIN],
         detail=[L(div, 48, div, 208), PL([(tip - 28 * d, 100), (tip, 128), (tip - 28 * d, 156)])], area=[WIN])

icon('sidebar-right', UI, ['sidebar', 'right panel', 'layout', 'drawer', 'panel'],
     line=[WIN], detail=[L(160, 48, 160, 208)], area=[WIN])
icon('sidebar-collapse', UI, ['sidebar', 'fold', 'close panel', 'collapse', 'collapse sidebar'],
     line=[WIN], detail=[L(96, 48, 96, 208), L(132, 128, 188, 128), PL([(156, 104), (132, 128), (156, 152)])], area=[WIN])
icon('sidebar-expand', UI, ['sidebar', 'unfold', 'open panel', 'expand', 'expand sidebar'],
     line=[WIN], detail=[L(96, 48, 96, 208), L(132, 128, 188, 128), PL([(164, 104), (188, 128), (164, 152)])], area=[WIN])

# ---------------------------------------------------------------- slashes
icon('paperclip-slash', UI, ['no attachment', 'detach', 'paperclip', 'remove'],
     line=[P('M136 176 A32 32 0 0 1 72 176 V106'), P('M85.5 51.5 A56 56 0 0 1 184 88 V150'), SLASH])
icon('push-pin-slash', UI, ['unpin', 'pin off', 'remove pin', 'detach', 'push pin'],
     line=load('push-pin')['line'] + [SLASH])
icon('share-network-slash', UI, ['share network', 'off', 'disabled', 'hidden', 'share'],
     line=load("share-network")["line"][:3] + [L(138.2, 88.4, 162.82, 75.29), load("share-network")["line"][4],
           L(64, 48, 160, 144)])

# ---------------------------------------------------------------- priority diamonds
DIA = load('diamond')['line']
icon('priority-high', UI, ['urgent', 'high priority', 'important'],
     line=DIA, detail=[L(128, 80, 128, 136)], area=DIA, dotcut=[C(128, 172, 16)])
icon('priority-medium', UI, ['normal priority', 'medium', 'moderate'],
     line=DIA, detail=[L(88, 128, 168, 128)], area=DIA)
icon('priority-up', UI, ['raise priority', 'increase', 'upgrade'],
     line=DIA, detail=[PL([(92, 146), (128, 110), (164, 146)])], area=DIA)
icon('priority-down', UI, ['low priority', 'decrease', 'downgrade'],
     line=DIA, detail=[PL([(92, 110), (128, 146), (164, 110)])], area=DIA)

# ---------------------------------------------------------------- progress
icon('progress-bar', UI, ['loading', 'progress', 'loader', 'bar', 'playback'],
     line=[R(32, 80, 192, 96, 48), L(72, 128, 136, 128)], area=[R(56, 112, 96, 32, 16)])

c0 = (128, 128)
half = 7.72
a0, a1 = -90 - half, -90 + 36 * 7 + half
solid = f'M{pt(polar(c0, 96, a0))} A96 96 0 1 1 {pt(polar(c0, 96, a1))}'
dashes = [P(f'M{pt(polar(c0, 96, t - half))} A96 96 0 0 1 {pt(polar(c0, 96, t + half))}') for t in (198, 234)]
icon('progress-check', UI, ['progress complete', 'done', 'circle', 'status'],
     line=[P(solid)] + dashes, detail=[PL([(88, 132), (116, 160), (172, 104)])], area=[C(128, 128, 104)])

wedge = f'M128 128 V60 A68 68 0 0 1 {pt(polar(c0, 68, 30))} Z'
icon('progress-circle', UI, ['progress', 'loading', 'incomplete', 'pie'],
     line=[C(128, 128, 96), P(wedge)], area=[P(wedge)])

# ---------------------------------------------------------------- question shapes
QB = load('question')
qpath, qdotc = QB['detail'], QB['dotcut']
icon('question-diamond', UI, ['question', 'help', 'diamond', 'unknown'],
     line=DIA, detail=[P(qmark(128, 102, 22)[0])], area=DIA, dotcut=[C(*qmark(128, 102, 22)[1], 14)])
OCT = load('octagon')['line']
icon('question-octagon', UI, ['question', 'help', 'octagon', 'unknown'],
     line=OCT, detail=qpath, area=OCT, dotcut=qdotc)
SQ = [R(32, 32, 192, 192, 16)]
icon('question-square', UI, ['question', 'help', 'square', 'faq'],
     line=SQ, detail=qpath, area=SQ, dotcut=qdotc)
icon('question-slash', UI, ['question', 'off', 'disabled', 'hidden'],
     line=[C(128, 128, 96)] + qpath + [SLASH], dot=qdotc)

# ---------------------------------------------------------------- misc controls
icon('reduce-motion', UI, ['reduce motion', 'accessibility', 'animation', 'settings'],
     line=[C(168, 128, 56), L(48, 128, 88, 128), L(80, 84, 104, 84), L(80, 172, 104, 172)],
     area=[C(168, 128, 56)])

icon('segmented-control', UI, ['segmented control', 'tabs', 'toggle', 'switcher'],
     line=[R(32, 72, 192, 112, 56), R(64, 104, 80, 48, 24), L(176, 128, 192, 128)], area=[R(64, 104, 80, 48, 24)])

SEL = [PL([(32, 56), (32, 32), (56, 32)]), PL([(200, 32), (224, 32), (224, 56)]),
       PL([(224, 200), (224, 224), (200, 224)]), PL([(56, 224), (32, 224), (32, 200)])]
for a, b in ((88, 112), (144, 168)):
    SEL += [L(a, 32, b, 32), L(a, 224, b, 224), L(32, a, 32, b), L(224, a, 224, b)]
icon('selection-magnifying-glass', UI, ['area search', 'scan region', 'find in selection'],
     line=SEL + [C(116, 116, 40), L(144.3, 144.3, 176, 176)], area=[C(116, 116, 40)])

fat = 'M224 112 L152 48 V80 C96 80 40 112 40 208 C72 160 104 144 152 144 V176 Z'
icon('share-fat', UI, ['share', 'forward', 'send', 'arrow'], line=[P(fat)], area=[P(fat)])

# ---------------------------------------------------------------- sliders
icon('slider-horizontal', UI, ['slider', 'range', 'scroll', 'horizontal'],
     line=[L(32, 128, 80, 128), L(144, 128, 224, 128), C(112, 128, 32)], area=[C(112, 128, 32)])
icon('slider-vertical', UI, ['slider', 'range', 'scroll', 'vertical'],
     line=[L(128, 224, 128, 176), L(128, 112, 128, 32), C(128, 144, 32)], area=[C(128, 144, 32)])
icon('slider-range', UI, ['range', 'slider', 'min max', 'filter'],
     line=[L(32, 128, 56, 128), L(104, 128, 152, 128), L(200, 128, 224, 128), C(80, 128, 24), C(176, 128, 24)],
     area=[C(80, 128, 24), C(176, 128, 24)])
icon('sliders-horizontal', UI, ['filters', 'adjust', 'controls', 'sliders', 'settings'],
     line=[L(32, 64, 64, 64), L(112, 64, 224, 64), C(88, 64, 24),
           L(32, 128, 144, 128), L(192, 128, 224, 128), C(168, 128, 24),
           L(32, 192, 80, 192), L(128, 192, 224, 192), C(104, 192, 24)],
     area=[C(88, 64, 24), C(168, 128, 24), C(104, 192, 24)])

# Badge variants of `sliders`: keep its top track, shorten the bottom track so the badge has room.
SL = load('sliders')
SL_LINE = [SL['line'][0], SL['line'][1], L(40, 176, 64, 176), SL['line'][4], C(88, 176, 24)]
SL_AREA = [SL['area'][0], C(88, 176, 24)]


def badge(src, idx):
    return load(src)['line'][idx]


B = {
    'arrow-down': dict(line=load('cursor-arrow-down')['line'][1:]),
    'arrow-up': dict(line=load('cursor-arrow-up')['line'][1:]),
    'check': dict(line=load('cursor-check')['line'][1:]),
    'code': dict(line=load('cursor-code')['line'][1:]),
    'currency-dollar': dict(line=load('cursor-currency-dollar')['line'][1:]),
    'gear': dict(line=load('cursor-gear')['line'][1:], area=load('cursor-gear')['area'][1:], hole=load('cursor-gear')['hole']),
    'heart': dict(line=load('cursor-heart')['line'][1:], area=load('cursor-heart')['area'][1:]),
    'lightning': dict(line=load('cursor-lightning')['line'][1:], area=load('cursor-lightning')['area'][1:]),
}
for nm, tags in [
    ('arrow-down', ['sliders', 'decrease', 'download', 'adjustments', 'controls']),
    ('arrow-up', ['sliders', 'increase', 'upload', 'adjustments', 'controls']),
    ('check', ['sliders', 'done', 'approved', 'adjustments', 'controls']),
    ('code', ['sliders', 'developer', 'code', 'adjustments', 'controls']),
    ('currency-dollar', ['sliders', 'money', 'price', 'adjustments', 'controls']),
    ('gear', ['sliders', 'settings', 'configure', 'adjustments', 'controls']),
    ('heart', ['sliders', 'favorite', 'like', 'adjustments', 'controls']),
    ('lightning', ['sliders', 'fast', 'power', 'adjustments', 'controls']),
]:
    b = B[nm]
    icon(f'sliders-{nm}', UI, tags, line=SL_LINE + b['line'], area=SL_AREA + b.get('area', []), hole=b.get('hole', []))

print(save(overwrite=True))
