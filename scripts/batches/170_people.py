import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path

PE, HE = 'People', 'Health'
SLASH = L(48, 48, 208, 208)


# ---------------------------------------------------------------- local helpers
def _pp(ds):
    p = pathops.Path()
    pen = p.getPen()
    for d in ds:
        parse_path(d, pen)
    return p


def _d(p):
    p.convertConicsToQuads(0.05)
    pen = SVGPathPen(None, f)
    p.draw(pen)
    return pen.getCommands()


def union_d(ds):
    acc = None
    for d in ds:
        q = _pp([d])
        q.simplify()
        acc = q if acc is None else pathops.op(acc, q, pathops.PathOp.UNION)
    return _d(acc)


def diff_d(d, cut_ds, grow=0):
    a = _pp([d]); a.simplify()
    g = _pp(cut_ds); g.simplify()
    if grow:
        st = _pp(cut_ds)
        st.stroke(grow * 2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        st.convertConicsToQuads(0.05)
        st.simplify()
        g = pathops.op(g, st, pathops.PathOp.UNION)
    return _d(pathops.op(a, g, pathops.PathOp.DIFFERENCE))


class _Flat(BasePen):
    def __init__(self, step=3):
        super().__init__(None)
        self.subs, self.step = [], step

    def _moveTo(self, p):
        self.subs.append([p])

    def _lineTo(self, p):
        a = self.subs[-1][-1]
        n = max(1, int(dist(a, p) / self.step))
        self.subs[-1] += [(a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n) for i in range(1, n + 1)]

    def _curveToOne(self, p1, p2, p3):
        p0 = self.subs[-1][-1]
        n = max(2, int((dist(p0, p1) + dist(p1, p2) + dist(p2, p3)) / self.step))
        for i in range(1, n + 1):
            t = i / n; u = 1 - t
            self.subs[-1].append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                                  u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.subs[-1][-1]
        self._curveToOne((p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1])),
                         (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1])), p2)

    def _closePath(self):
        s = self.subs[-1]
        if dist(s[-1], s[0]) > 0.01:
            self._lineTo(s[0])
        self.subs[-1].append('closed')

    _endPath = lambda self: None


def flatten(d, step=3):
    pen = _Flat(step)
    parse_path(d, pen)
    out = []
    for s in pen.subs:
        closed = s[-1] == 'closed'
        out.append(([p for p in s if p != 'closed'], closed))
    return out


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def occlude_d(d, front, gap=20, step=2, keep_inside=False):
    """Pieces (as path data) of path d that stay `gap` clear of the closed shapes in front."""
    fp = _pp(front)
    edges = []
    for pts, _ in sum((flatten(x, 2) for x in front), []):
        edges += list(zip(pts, pts[1:]))

    def visible(p):
        if not keep_inside and fp.contains(p):
            return False
        return all(_seg_dist(p, a, b) >= gap for a, b in edges)

    out = []
    for pts, closed in flatten(d, step):
        runs, cur = [], []
        for p in pts:
            if visible(p):
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        if closed and len(runs) > 1 and runs[0][0] == pts[0] and runs[-1][-1] == pts[-1]:
            runs[0] = runs.pop() + runs[0][1:]
        if closed and len(runs) == 1 and len(runs[0]) == len(pts):
            out.append(d); continue
        for r in runs:
            if len(r) > 1:
                out.append('M' + ' L'.join(pt(q) for q in r))
    return out


def occlude(d, front, gap=20, **kw):
    return [P(x) for x in occlude_d(d, front, gap, **kw)]


SLASH_SHAPE = capsule((128, 128), 113.1, 1, (0.7071, 0.7071))


def el_d(e):
    m = re.search(r' d="([^"]+)"', e)
    if m:
        return m.group(1)
    g = lambda k: float(re.search(k + r'="([-\d.]+)"', e).group(1))
    if e.startswith('<circle'):
        cx, cy, r = g('cx'), g('cy'), g('r')
        return f'M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A{f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'
    if e.startswith('<rect'):
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        r = g('rx') if 'rx=' in e else 0
        return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
                f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
                f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')
    raise ValueError(e)


def slashed(elements, gap=22):
    out = []
    for e in elements:
        out += occlude(el_d(e), [SLASH_SHAPE], gap)
    return out + [SLASH]


def xform_d(d, fn, mirror=False, s=1.0, sy=None):
    """Apply point map fn to absolute path data (M L H V C Q A Z). mirror flips arc sweep, s scales radii."""
    toks = re.findall(r'[MLHVCQAZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    out, i, cmd, cur = [], 0, None, (0, 0)
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCQAZ':
            cmd = t; i += 1
            if t == 'Z':
                out.append('Z')
            continue
        if cmd in 'ML':
            cur = (float(toks[i]), float(toks[i + 1])); i += 2
            out.append(f'{cmd}{pt(fn(cur))}')
        elif cmd == 'H':
            cur = (float(toks[i]), cur[1]); i += 1
            out.append(f'L{pt(fn(cur))}')
        elif cmd == 'V':
            cur = (cur[0], float(toks[i])); i += 1
            out.append(f'L{pt(fn(cur))}')
        elif cmd == 'C':
            ps = [(float(toks[i + k]), float(toks[i + k + 1])) for k in (0, 2, 4)]; i += 6
            cur = ps[-1]
            out.append('C' + ' '.join(pt(fn(q)) for q in ps))
        elif cmd == 'Q':
            ps = [(float(toks[i + k]), float(toks[i + k + 1])) for k in (0, 2)]; i += 4
            cur = ps[-1]
            out.append('Q' + ' '.join(pt(fn(q)) for q in ps))
        elif cmd == 'A':
            rx, ry, a, la, sw, x, y = toks[i:i + 7]; i += 7
            cur = (float(x), float(y))
            sw = str(1 - int(sw)) if mirror else sw
            out.append(f'A{f(float(rx) * s)} {f(float(ry) * (s if sy is None else sy))} {a} {la} {sw} {pt(fn(cur))}')
    return ' '.join(out)


def xform(els, fn, mirror=False, s=1.0):
    return [P(xform_d(el_d(e), fn, mirror, s)) for e in els]


def rotf(deg, c=(128, 128)):
    return lambda p: rot([p], deg, c)[0]


def scalef(s, src=(128, 128), dst=None):
    dst = dst or src
    return lambda p: (dst[0] + (p[0] - src[0]) * s, dst[1] + (p[1] - src[1]) * s)


mirror_x = lambda p: (256 - p[0], p[1])


def lens(a, b, bulge):
    l = dist(a, b) / 2
    r = (l * l + bulge * bulge) / (2 * bulge)
    return f'M{pt(a)} A{f(r)} {f(r)} 0 0 1 {pt(b)} A{f(r)} {f(r)} 0 0 1 {pt(a)} Z'


def circ_d(cx, cy, r):
    return el_d(C(cx, cy, r))


def cap(a, b, r):
    """Capsule (stadium) between centre points a and b with radius r."""
    cn = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    l = dist(a, b)
    u = ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
    return capsule(cn, l / 2, r, u)


def heart_d(s=1.0, dst=(128, 145)):
    base = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
    return xform_d(base, scalef(s, (128, 145), dst), s=s)


# ---------------------------------------------------------------- hands (front view, the library's hand)
XS = (76, 112, 148, 184, 220)
THUMB_OUT = 'C108 224 92 214 78 196 L40 146 A18 18 0 0 1 68 124 L76 134 Z'
THUMB_IN = 'C100 224 76 204 76 172 Z'


def hand_d(tops, thumb=True):
    ti, tm, tr, tp = tops
    return (f'M76 134 V{f(ti)} A18 18 0 0 1 112 {f(ti)} V{f(tm)} A18 18 0 0 1 148 {f(tm)} '
            f'V{f(tr)} A18 18 0 0 1 184 {f(tr)} V{f(tp)} A18 18 0 0 1 220 {f(tp)} '
            f'V152 C220 196 192 224 152 224 H132 ' + (THUMB_OUT if thumb else THUMB_IN))


def seps(tops, skip=()):
    out = []
    for k in range(3):
        if k in skip:
            continue
        a, b = tops[k], tops[k + 1]
        top = max(a, b)
        end = 132 if top < 100 else top + 28
        out.append(L(XS[k + 1], top, XS[k + 1], end))
    return out


TUCK = P('M76 176 H124 A16 16 0 0 0 140 160')


def hand_icon(name, tags, tops, thumb=True, extra_detail=(), skip=(), cat=PE):
    d = hand_d(tops, thumb)
    det = seps(tops, skip) + ([] if thumb else [TUCK]) + list(extra_detail)
    icon(name, cat, tags, line=[P(d)], detail=det, area=[P(d)])


CURL = 118
hand_icon('hand-love-you', ['love you', 'sign language', 'hand', 'gesture'], (58, CURL, CURL + 4, 82))
hand_icon('hand-horns', ['rock on', 'horns', 'metal', 'gesture'], (58, CURL, CURL + 4, 82), thumb=False)
hand_icon('hand-pinky', ['pinky', 'little finger', 'promise', 'gesture'], (CURL, CURL - 4, CURL, 74), thumb=False)
hand_icon('hand-three-fingers', ['three', 'count', 'fingers', 'gesture'], (58, 50, 58, CURL + 4), thumb=False)
d_ring = hand_d((82, 58, 70, 98))
icon('hand-ring-finger', PE, ['ring finger', 'hand', 'wedding', 'gesture'], line=[P(d_ring), L(140, 104, 192, 104)],
     detail=seps((82, 58, 70, 98)) + [L(148, 104, 184, 104)], area=[P(d_ring)])

# peace: index and middle splayed into a V
peace = union_d([cap((86, 60), (98, 150), 18), cap((146, 54), (130, 150), 18),
                 cap((166, CURL), (166, 160), 18), cap((202, CURL + 4), (202, 160), 18),
                 'M76 120 H220 V152 C220 196 192 224 152 224 H132 C100 224 76 204 76 172 Z'])
icon('hand-peace', PE, ['peace', 'victory', 'v sign', 'two fingers', 'gesture'], line=[P(peace)],
     detail=[L(184, CURL + 4, 184, CURL + 32), TUCK], area=[P(peace)])

# vulcan: fingers split into two pairs
vul = union_d([cap((88, 66), (100, 150), 18), cap((122, 58), (132, 150), 18),
               cap((170, 58), (162, 150), 18), cap((206, 72), (196, 150), 18),
               'M78 120 H214 V152 C214 196 188 224 150 224 H132 ' + THUMB_OUT.replace('L76 134 Z', 'L78 120 Z')])
icon('hand-vulcan', PE, ['vulcan salute', 'live long', 'greeting'], line=[P(vul)],
     detail=[L(116, 92, 116, 132), L(180, 92, 180, 132)], area=[P(vul)])

# fist (front view)
fist = ('M64 92 A18 18 0 0 1 100 92 A18 18 0 0 1 136 92 A18 18 0 0 1 172 92 A18 18 0 0 1 208 92 '
        'V160 C208 196 184 220 148 220 H116 C84 220 64 200 64 168 Z')
icon('hand-fist', PE, ['fist', 'power', 'solidarity', 'punch'], line=[P(fist)],
     detail=[L(100, 92, 100, 120), L(136, 92, 136, 120), L(172, 92, 172, 120), P('M64 152 H128 A16 16 0 0 0 144 136')],
     area=[P(fist)])

# ok: index and thumb close a ring
okc, okr = (84, 138), 52
ok = union_d([circ_d(okc[0], okc[1], okr), cap((130, 58), (130, 150), 18), cap((166, 70), (166, 150), 18),
              cap((202, 96), (202, 150), 18),
              'M112 120 H220 V152 C220 196 192 224 152 224 H132 C112 224 100 214 92 200 L100 150 Z'])
ring_in = C(82, 136, 20)
icon('hand-ok', PE, ['ok', 'okay', 'gesture', 'fine'], line=[P(ok), ring_in],
     detail=[L(148, 82, 148, 132), L(184, 96, 184, 132)], area=[P(ok)], hole=[ring_in])

# hamsa
ham = union_d([cap((52, 108), (76, 170), 18), cap((92, 72), (92, 160), 18), cap((128, 54), (128, 160), 18),
               cap((164, 72), (164, 160), 18), cap((204, 108), (180, 170), 18),
               'M44 140 H212 V160 C212 200 176 224 128 224 C80 224 44 200 44 160 Z'])
eye = lens((88, 166), (168, 166), 28)
icon('hand-eye', PE, ['hamsa', 'protection', 'eye in hand'], line=[P(ham)],
     detail=[L(110, 72, 110, 110), L(146, 72, 146, 110), P(eye)], area=[P(ham)], dotcut=[C(128, 166, 13)])


# ---------------------------------------------------------------- pointing, slash and swipe variants
hp = load('hand-pointing')
for nm, fn, mir, tags in [('hand-pointing-right', rotf(90), False, ['point right', 'finger', 'next', 'gesture', 'hand']),
                          ('hand-pointing-left', lambda p: mirror_x(rot([p], 90)[0]), True,
                           ['point left', 'finger', 'back', 'gesture', 'hand']),
                          ('hand-pointing-down', rotf(180), False, ['point down', 'finger', 'below', 'gesture', 'hand'])]:
    icon(nm, PE, tags, line=xform(hp['line'], fn, mir), detail=xform(hp['detail'], fn, mir), area=xform(hp['area'], fn, mir))

icon('hand-pointing-slash', PE, ['hand pointing', 'off', 'disabled', 'hidden', 'hand'], line=slashed(hp['line'] + hp['detail']))
hb = load('hand')
icon('hand-slash', PE, ['hand', 'off', 'disabled', 'hidden'], line=slashed(hb['line'] + hb['detail']))

ht = load('hand-tap')
def arrow(a, b, head=22):
    l = dist(a, b); u = ((b[0] - a[0]) / l, (b[1] - a[1]) / l); n = (-u[1], u[0])
    back = (b[0] - u[0] * head, b[1] - u[1] * head)
    return [L(*a, *b), PL([(back[0] + n[0] * head, back[1] + n[1] * head), b, (back[0] - n[0] * head, back[1] - n[1] * head)])]
for nm, a, b, tags in [('hand-swipe-up', (180, 120), (180, 40), ['swipe up', 'gesture', 'scroll', 'touch']),
                       ('hand-swipe-down', (180, 40), (180, 120), ['swipe down', 'gesture', 'scroll', 'pull to refresh', 'touch']),
                       ('hand-swipe-left', (216, 64), (140, 64), ['swipe left', 'gesture', 'previous', 'touch', 'slide']),
                       ('hand-swipe-right', (140, 64), (216, 64), ['swipe right', 'gesture', 'next', 'touch', 'slide'])]:
    icon(nm, PE, tags, line=ht['line'][:1] + arrow(a, b), detail=ht['detail'], area=ht['area'])

# hand holding a heart (the library's offering hand)
hc = load('hand-coins')
hrt = heart_d(0.55, (144, 96))
icon('hand-heart', PE, ['service', 'care', 'charity', 'support', 'donate'],
     line=hc['line'][:2] + [P(hrt)], detail=hc['detail'][:1], area=hc['area'][:1] + [P(hrt)])

# two open palms side by side, thumbs out; the right one overlaps the left
HAND = hb['line'][0]
sx, sy = 0.6, 0.82
def hs(dst, mir):
    fn = lambda p: (dst[0] + (p[0] - 130) * sx, dst[1] + (p[1] - 132) * sy)
    return (lambda p: mirror_x(fn(p))) if mir else fn
bh = xform_d(el_d(HAND), hs((90, 132), False), s=sx, sy=sy)
fh = xform_d(el_d(HAND), hs((88, 132), True), True, s=sx, sy=sy)
icon('hands', PE, ['hands', 'open hands', 'help', 'support'],
     line=occlude(bh, [fh], 18) + [P(fh)], area=[P(diff_d(bh, [fh], 18)), P(fh)])

# praying hands, seen from the front: fingertips meet at the top, the two thumbs sit side by side
half = 'M128 32 C112 32 98 44 94 60 L64 148 C58 168 70 184 92 184 H128 Z'
whole = union_d([half, xform_d(half, mirror_x, True)])
cuff = R(60, 184, 136, 40, 12)
thumbs = [P('M96 184 V136 A16 16 0 0 1 128 136'), P('M160 184 V136 A16 16 0 0 0 128 136')]
icon('hands-praying', PE, ['pray', 'thanks', 'please', 'folded hands', 'bless'], line=[P(whole), cuff],
     detail=[L(128, 60, 128, 184)] + thumbs, area=[P(whole), cuff])

def drop_d(cx, cy, r):
    return (f'M{f(cx)} {f(cy - 1.9 * r)} C{f(cx + .4 * r)} {f(cy - 1.2 * r)} {f(cx + r)} {f(cy - .6 * r)} {f(cx + r)} {f(cy)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(cx - r)} {f(cy)} C{f(cx - r)} {f(cy - .6 * r)} {f(cx - .4 * r)} {f(cy - 1.2 * r)} {f(cx)} {f(cy - 1.9 * r)} Z')
sw = 0.84
wf = scalef(sw, (128, 224), (128, 224))
wh = xform_d(whole, wf, s=sw)
wc = xform_d('M60 196 A12 12 0 0 1 72 184 H184 A12 12 0 0 1 196 196 V212 A12 12 0 0 1 184 224 H72 A12 12 0 0 1 60 212 Z', wf, s=sw)
drops = [drop_d(56, 92, 16), drop_d(200, 92, 16)]
icon('hands-washing', HE, ['wash hands', 'hygiene', 'clean', 'soap'], line=[P(wh), P(wc)] + [P(d) for d in drops],
     detail=[P(xform_d('M128 60 L128 184', wf))] + xform(thumbs, wf, s=sw), area=[P(wh), P(wc)] + [P(d) for d in drops])

# clapping: two tilted palms meeting, with burst marks
s7 = 0.7
cb_fn = lambda p: rot([scalef(s7, (130, 132), (108, 140))(p)], -24, (108, 180))[0]
cf_fn = lambda p: rot([scalef(s7, (130, 132), (140, 156))(p)], -4, (140, 196))[0]
cbh = xform_d(el_d(HAND), cb_fn, s=s7)
cfh = xform_d(el_d(HAND), cf_fn, s=s7)
icon('hands-clapping', PE, ['applause', 'clap', 'bravo', 'hands'],
     line=occlude(cbh, [cfh], 18) + [P(cfh), L(184, 40, 172, 60), L(212, 72, 192, 80), L(156, 32, 154, 48)],
     detail=xform(hb['detail'], cf_fn, s=s7), area=[P(diff_d(cbh, [cfh], 18)), P(cfh)])

# ---------------------------------------------------------------- heads
HEAD = 'M84 224 V172.6 A76 76 0 1 1 195.4 82 L218 136 L204 144 V170 A18 18 0 0 1 186 188 H160 V224'
HC = (124, 108)
icon('head-profile', PE, ['head', 'profile', 'side view', 'person'], line=[P(HEAD)], area=[P(HEAD + ' Z')])


def gear_d(c, rr, rt, n, tw=11):
    pts = []
    for i in range(n):
        a = i * 360 / n - 90
        pts += [polar(c, rr, a - tw - 9), polar(c, rt, a - tw), polar(c, rt, a + tw), polar(c, rr, a + tw + 9)]
    return poly(pts, True)


icon('head-gear', PE, ['psychology', 'thinking', 'mind', 'mental'], line=[P(HEAD)],
     detail=[P(gear_d(HC, 30, 42, 7))], area=[P(HEAD + ' Z')], dotcut=[C(*HC, 11)])
qm = f'M{f(HC[0] - 22)} {f(HC[1] - 14)} A22 22 0 1 1 {f(HC[0] + 8)} {f(HC[1] + 6)} C{f(HC[0] + 2)} {f(HC[1] + 9)} {f(HC[0])} {f(HC[1] + 14)} {f(HC[0])} {f(HC[1] + 22)}'
icon('head-question', PE, ['thinking', 'question', 'confused', 'idea'], line=[P(HEAD)],
     detail=[P(qm)], area=[P(HEAD + ' Z')], dotcut=[C(HC[0], HC[1] + 52, 12)])

s8 = 0.7
spk = scalef(s8, (84, 224), (64, 224))
sh = xform_d(HEAD, spk, s=s8)
icon('person-speaking', PE, ['voice over', 'speaker', 'talk', 'narrator'],
     line=[P(sh), P('M' + pt(polar((162, 160), 30, -42)) + ' ' + arc_to((162, 160), 30, polar((162, 160), 30, -42), polar((162, 160), 30, 42), lambda m: m[0])),
           P('M' + pt(polar((162, 160), 62, -44)) + ' ' + arc_to((162, 160), 62, polar((162, 160), 62, -44), polar((162, 160), 62, 44), lambda m: m[0]))],
     area=[P(sh + ' Z')])

# ---------------------------------------------------------------- hearts and hands
HEART = heart_d(1.0, (128, 145))
icon('heart-handshake', PE, ['charity', 'support', 'care', 'handshake'], line=[P(HEART)],
     detail=[P('M64 124 L96 104 H128 L176 128'), L(120, 132, 152, 160), L(100, 148, 124, 172)], area=[P(HEART)])

# ---------------------------------------------------------------- badge
badge = R(52, 56, 152, 168, 16)
clip = PL([(108, 56), (108, 32), (148, 32), (148, 56)])
bperson = [C(128, 118, 22), P('M84 196 C84 176 102 166 128 166 C154 166 172 176 172 196 Z')]
icon('identification-badge', PE, ['badge', 'id', 'employee', 'lanyard', 'id badge'], line=[badge, clip],
     detail=bperson, area=[badge])
icon('identification-badge-slash', PE, ['identification badge', 'off', 'disabled', 'hidden', 'identification'],
     line=slashed([badge, clip] + bperson))

# ---------------------------------------------------------------- face parts
lips = ('M32 128 C60 92 84 76 104 78 C114 79 122 84 128 90 C134 84 142 79 152 78 C172 76 196 92 224 128 '
        'C196 170 164 188 128 188 C92 188 60 170 32 128 Z')
icon('lips', PE, ['mouth', 'kiss', 'lipstick', 'beauty', 'lips'], line=[P(lips)],
     detail=[P('M68 128 C100 136 156 136 188 128')], area=[P(lips)])

mh = ('M128 108 C112 88 84 88 68 106 C58 118 46 124 32 116 C34 146 58 162 86 158 C106 155 120 146 128 136 '
      'C136 146 150 155 170 158 C198 162 222 146 224 116 C210 124 198 118 188 106 C172 88 144 88 128 108 Z')
icon('mustache', PE, ['mustache', 'moustache', 'facial hair', 'gentleman', 'beard'], line=[P(mh)], area=[P(mh)])

# ---------------------------------------------------------------- baby
onesie = ('M104 40 C110 56 146 56 152 40 L184 52 L224 92 L196 120 L184 108 V168 C184 188 172 200 156 204 '
          'C150 206 148 212 148 220 H108 C108 212 106 206 100 204 C84 200 72 188 72 168 V108 L60 120 L32 92 L72 52 Z')
icon('onesie', PE, ['onesie', 'romper', 'baby clothes', 'infant'], line=[P(onesie)], area=[P(onesie)],
     dotcut=[C(116, 188, 9), C(140, 188, 9)])

paci = union_d([circ_d(128, 72, 36), 'M40 124 C40 104 84 96 128 96 C172 96 216 104 216 124 C216 144 172 152 128 152 C84 152 40 144 40 124 Z',
                'M106 140 V196 A22 22 0 0 0 150 196 V140 Z'])
icon('pacifier', PE, ['pacifier', 'dummy', 'baby', 'infant'], line=[P(paci), C(128, 72, 16)],
     area=[P(paci)], hole=[C(128, 72, 16)])

# ---------------------------------------------------------------- symbols
icon('gender-nonbinary', PE, ['nonbinary', 'gender', 'symbol'],
     line=[C(128, 164, 60), L(128, 104, 128, 32), L(106, 46, 150, 82), L(150, 46, 106, 82)], area=[C(128, 164, 60)])

# ---------------------------------------------------------------- figures (the library's person)
def stick(cx, sc=1.0, la=((68, 148),), ra=((188, 148),), legs=((84, 220), (172, 220)), feet=220, spine_end=152):
    T = lambda p: (cx + (p[0] - 128) * sc, feet + (p[1] - 220) * sc)
    head = C(*T((128, 56)), 24 * sc)
    line = [head, L(*T((128, 100)), *T((128, spine_end))),
            PL([T(q) for q in list(la)[::-1]] + [T((128, 108))] + [T(q) for q in ra]),
            PL([T(legs[0]), T((128, 152)), T(legs[1])])]
    return line, [head]


ln, ar = stick(128, la=((40, 92),), ra=((216, 92),), legs=((76, 220), (180, 220)))
icon('person-arms-spread', PE, ['open arms', 'welcome', 'freedom', 'person'], line=ln, area=ar)
ln, ar = stick(128, la=((72, 100), (60, 40)), ra=((184, 100), (196, 40)))
icon('person-arms-up', PE, ['celebrate', 'cheer', 'person', 'happy'], line=ln, area=ar)
ln, ar = stick(128, ra=((184, 100), (196, 40)))
icon('person-raised-hand', PE, ['raise hand', 'question', 'participant', 'person', 'volunteer'], line=ln, area=ar)

# parent and child holding hands
pa = [C(84, 56, 24), L(84, 100, 84, 152), PL([(40, 144), (84, 108)]), PL([(52, 220), (84, 152), (116, 220)])]
ch = [C(184, 124, 16), L(184, 154, 184, 184), PL([(84, 108), (140, 150), (184, 162), (212, 184)]),
      PL([(162, 220), (184, 184), (206, 220)])]
icon('parent', PE, ['parent', 'child', 'family', 'guardian'], line=pa + ch, area=[C(84, 56, 24), C(184, 124, 16)])

# two people holding hands
hh = [C(76, 64, 22), L(76, 104, 76, 156), PL([(36, 148), (76, 112), (128, 152), (180, 112), (220, 148)]),
      PL([(44, 220), (76, 156), (108, 220)]), C(180, 64, 22), L(180, 104, 180, 156), PL([(148, 220), (180, 156), (212, 220)])]
icon('holding-hands', PE, ['holding hands', 'couple', 'together', 'love'], line=hh, area=[C(76, 64, 22), C(180, 64, 22)])

# restroom-style figures
mhead = C(128, 52, 20)
torso = R(72, 92, 112, 72, 20)
icon('man', PE, ['male', 'restroom', 'man', 'person'], line=[mhead, torso, L(108, 164, 108, 216), L(148, 164, 148, 216)],
     detail=[L(104, 124, 104, 164), L(152, 124, 152, 164)], area=[mhead, torso])
dress = 'M104 92 H152 C160 92 166 97 168 104 L188 164 C190 172 186 176 178 176 H78 C70 176 66 172 68 164 L88 104 C90 97 96 92 104 92 Z'
icon('person-dress', PE, ['woman', 'person', 'dress', 'female'], line=[mhead, P(dress), L(108, 176, 108, 216), L(148, 176, 148, 216)],
     area=[mhead, P(dress)])

# kids (head and shoulders)
kh = C(128, 96, 44)
ksh = 'M56 220 C56 182 88 160 128 160 C168 160 200 182 200 220'
icon('person-boy', PE, ['boy', 'child', 'kid', 'son', 'male'], line=[kh, P(ksh)],
     detail=[P('M86 84 C108 88 128 80 142 64 C150 76 160 82 170 84')], area=[kh, P(ksh + ' Z')])
ghead = union_d([circ_d(128, 96, 44), circ_d(68, 116, 20), circ_d(188, 116, 20)])
icon('person-girl', PE, ['girl', 'child', 'kid', 'daughter', 'female'], line=[P(ghead), P(ksh)],
     detail=[P('M86 84 C108 84 124 74 128 62 C132 74 148 84 170 84')], area=[P(ghead), P(ksh + ' Z')])

# cane
icon('person-cane', PE, ['elderly', 'senior', 'cane', 'old'],
     line=[C(112, 56, 22), P('M112 96 L108 148'), PL([(80, 216), (108, 148), (140, 216)]), PL([(84, 140), (112, 104), (152, 132)]),
           P('M164 216 V132 A14 14 0 0 1 192 132')], area=[C(112, 56, 22)])
icon('person-elderly', PE, ['elderly', 'old person', 'senior', 'cane'],
     line=[C(128, 60, 22), P('M108 96 C96 112 92 132 92 152'), PL([(68, 216), (92, 152), (120, 216)]),
           PL([(104, 108), (148, 140)]), P('M160 216 V144 A14 14 0 0 0 132 144')], area=[C(128, 60, 22)])

# desk
icon('person-desk', PE, ['workspace', 'office', 'person', 'work'],
     line=[C(128, 64, 32), P('M64 152 C64 120 92 108 128 108 C164 108 192 120 192 152'), L(32, 176, 224, 176),
           L(56, 176, 56, 224), L(200, 176, 200, 224)], area=[C(128, 64, 32), P('M64 152 C64 120 92 108 128 108 C164 108 192 120 192 152 Z')])

# falling
fh_c = (80, 60)
icon('person-falling', PE, ['fall', 'falling', 'accident', 'safety', 'slip'],
     line=[C(*fh_c, 24), L(100, 96, 128, 152), PL([(44, 116), (106, 106), (164, 76)]),
           PL([(204, 124), (128, 152), (112, 216)]), L(152, 216, 216, 216)], area=[C(*fh_c, 24)])

# meditating
legs_m = 'M60 176 H196 A20 20 0 0 1 196 216 H60 A20 20 0 0 1 60 176 Z'
icon('person-meditating', PE, ['meditation', 'mindfulness', 'yoga', 'calm'],
     line=[C(128, 56, 24), L(128, 100, 128, 148), PL([(60, 160), (84, 120), (128, 104), (172, 120), (196, 160)]), P(legs_m)],
     area=[C(128, 56, 24), P(legs_m)])

# pregnant (side profile)
preg = ('M100 90 H126 C134 102 134 112 130 120 C162 128 180 156 168 180 C160 192 144 196 128 196 H104 '
        'C96 160 94 124 100 90 Z')
icon('person-pregnant', PE, ['pregnancy', 'expecting', 'maternity', 'mother', 'pregnant'],
     line=[C(114, 54, 20), P(preg), L(108, 196, 108, 220), L(140, 196, 140, 220)], area=[C(114, 54, 20), P(preg)])

# reading
book = 'M44 156 C76 150 104 154 128 168 C152 154 180 150 212 156 V212 C180 206 152 210 128 222 C104 210 76 206 44 212 Z'
rsh = 'M64 160 C64 132 92 116 128 116 C164 116 192 132 192 160'
icon('person-reading', PE, ['reader', 'reading', 'book', 'study'],
     line=[C(128, 64, 32)] + occlude(rsh, [book], 20) + [P(book)], detail=[L(128, 168, 128, 222)],
     area=[C(128, 64, 32), P(diff_d(rsh + ' Z', [book], 16)), P(book)])

print(save(overwrite=True))
