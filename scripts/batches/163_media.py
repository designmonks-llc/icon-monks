import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build as _build

CAT = 'Media'
SLASH = L(48, 48, 208, 208)


# ----------------------------------------------------------------------- generic helpers
def tf_path(d, fn, s=1.0):
    """Transform an absolute path (M L H V C A Z) by point function fn; arc radii scale by s."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cur, cmd = [], 0, (0, 0), None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == 'Z':
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
            a = (float(toks[i]), float(toks[i + 1])); b = (float(toks[i + 2]), float(toks[i + 3]))
            cur = (float(toks[i + 4]), float(toks[i + 5])); i += 6
            out.append(f'C{pt(fn(a))} {pt(fn(b))} {pt(fn(cur))}')
        elif cmd == 'A':
            rx, ry, xr, la, sw = (float(v) for v in toks[i:i + 5])
            cur = (float(toks[i + 5]), float(toks[i + 6])); i += 7
            out.append(f'A{f(rx * s)} {f(ry * s)} {f(xr)} {int(la)} {int(sw)} {pt(fn(cur))}')
    return ' '.join(out)


def scaler(c_from, c_to, s):
    return lambda p: (c_to[0] + (p[0] - c_from[0]) * s, c_to[1] + (p[1] - c_from[1]) * s)


def rotator(deg, c=(128, 128), shift=(0, 0)):
    a = math.radians(deg)
    return lambda p: (c[0] + shift[0] + (p[0] - c[0]) * math.cos(a) - (p[1] - c[1]) * math.sin(a),
                      c[1] + shift[1] + (p[0] - c[0]) * math.sin(a) + (p[1] - c[1]) * math.cos(a))


def compose(*fns):
    def g(p):
        for fn in fns:
            p = fn(p)
        return p
    return g


def el_tf(el, fn, s=1.0):
    """Transform a source element string (path / circle / rect) into a path or circle."""
    m = re.match(r'<circle cx="([\d.-]+)" cy="([\d.-]+)" r="([\d.-]+)"/>', el)
    if m:
        cx, cy, r = map(float, m.groups())
        c = fn((cx, cy))
        return C(c[0], c[1], r * s)
    m = re.match(r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.-]+)" height="([\d.-]+)"(?: rx="([\d.-]+)")?/>', el)
    if m:
        x, y, w, h = map(float, m.groups()[:4]); r = float(m.group(5) or 0)
        d = (f'M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} A{r} {r} 0 0 1 {x + w - r} {y + h} '
             f'H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z')
        return P(tf_path(d, fn, s))
    m = re.match(r'<path d="([^"]+)"/>', el)
    return P(tf_path(m.group(1), fn, s))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def star_pts(c, ro, ri):
    return [polar(c, ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]


def bolt(c, s=1.0):
    pts = [(10, -36), (-20, 4), (4, 4), (-8, 36), (22, -6), (-2, -6)]
    return [(c[0] + x * s, c[1] + y * s) for x, y in pts]


def gear_path(c, r_in, r_out, n=6, half_base=18, half_top=11):
    pts = []
    for i in range(n):
        t = -90 + i * 360 / n
        pts += [polar(c, r_in, t - half_base), polar(c, r_out, t - half_top),
                polar(c, r_out, t + half_top), polar(c, r_in, t + half_base)]
    d = 'M' + pt(pts[0])
    for i in range(n):
        a, b, cc, dd = pts[i * 4:i * 4 + 4]
        if i:
            d += f' A{f(r_in)} {f(r_in)} 0 0 1 {pt(a)}'
        d += f' L{pt(b)} L{pt(cc)} L{pt(dd)}'
    return d + f' A{f(r_in)} {f(r_in)} 0 0 1 {pt(pts[0])} Z'


HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'


# ----------------------------------------------------------------------- badge marks (centred on B)
def mark(kind, B):
    x, y = B
    o = lambda dx, dy: (x + dx, y + dy)
    if kind == 'arrow-down':
        return dict(line=[L(x, y - 30, x, y + 28), PL([o(-24, 4), o(0, 28), o(24, 4)])])
    if kind == 'arrow-up':
        return dict(line=[L(x, y + 30, x, y - 28), PL([o(-24, -4), o(0, -28), o(24, -4)])])
    if kind == 'check':
        return dict(line=[PL([o(-26, 2), o(-8, 20), o(26, -16)])])
    if kind == 'code':
        return dict(line=[PL([o(-10, -22), o(-28, 0), o(-10, 22)]), PL([o(14, -22), o(32, 0), o(14, 22)])])
    if kind == 'dollar':
        return dict(line=[P(f'M{f(x + 16)} {f(y - 24)} H{f(x - 4)} A12 12 0 0 0 {f(x - 4)} {f(y)} H{f(x + 4)} '
                            f'A12 12 0 0 1 {f(x + 4)} {f(y + 24)} H{f(x - 16)}'),
                          L(x, y - 36, x, y - 24), L(x, y + 24, x, y + 36)])
    if kind == 'percent':
        return dict(line=[L(x - 26, y + 26, x + 26, y - 26)], dot=[C(x - 22, y - 22, 14), C(x + 22, y + 22, 14)])
    if kind == 'gear':
        gp = gear_path(B, 22, 34, 6, 20, 12)
        return dict(line=[P(gp)], area=[P(gp)], hole=[C(x, y, 8)])
    if kind == 'heart':
        hs = tf_path(HEART, scaler((128, 145), (x, y + 2), 0.32), 0.32)
        return dict(line=[P(hs)], area=[P(hs)])
    if kind == 'lightning':
        b = bolt(B, 0.8)
        return dict(line=[PG(b)], area=[PG(b)])
    if kind == 'search':
        return dict(line=[C(x - 6, y - 6, 20), L(x + 8, y + 8, x + 24, y + 24)], area=[C(x - 6, y - 6, 20)])
    if kind == 'minus':
        return dict(line=[L(x - 28, y, x + 28, y)])
    if kind == 'plus':
        return dict(line=[L(x - 28, y, x + 28, y), L(x, y - 28, x, y + 28)])
    if kind == 'pause':
        return dict(line=[L(x - 16, y - 24, x - 16, y + 24), L(x + 16, y - 24, x + 16, y + 24)])
    if kind == 'pin':
        body = [o(-12, -34), o(12, -34), o(12, -14), o(24, 6), o(-24, 6), o(-12, -14)]
        return dict(line=[PG(body), L(x - 20, y - 34, x + 20, y - 34), L(x, y + 6, x, y + 34)], area=[PG(body)])
    if kind == 'question':
        return dict(line=[P(f'M{pt(o(-16, -24))} A18 18 0 1 1 {pt(o(12, -9))} C{pt(o(6, -5))} {pt(o(2, -1))} {pt(o(2, 6))}')],
                    dot=[C(x + 2, y + 28, 16)])
    if kind == 'share':
        return dict(line=[P(f'M{pt(o(-24, 28))} V{f(y + 12)} A24 24 0 0 1 {pt(o(0, -12))} H{f(x + 24)}'),
                          PL([o(8, -28), o(24, -12), o(8, 4)])])
    if kind == 'star':
        st = star_pts((x, y + 2), 32, 14)
        return dict(line=[PG(st)], area=[PG(st)])
    if kind == 'warning':
        return dict(line=[L(x, y - 32, x, y - 2)], dot=[C(x, y + 26, 16)])
    if kind == 'x':
        return dict(line=[L(x - 20, y - 20, x + 20, y + 20), L(x + 20, y - 20, x - 20, y + 20)])
    raise KeyError(kind)


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, [])
            out[k] = out[k] + list(v)
    return out


# ----------------------------------------------------------------------- music note + badges
NOTE = load('music-note')
NB = (188, 188)
for kind, name, tags in [
    ('arrow-down', 'music-note-arrow-down', ['music note', 'download', 'down', 'decrease', 'music']),
    ('arrow-up', 'music-note-arrow-up', ['music note', 'upload', 'up', 'increase', 'music']),
    ('check', 'music-note-check', ['music note check', 'done', 'approved', 'music', 'note']),
    ('code', 'music-note-code', ['music note', 'code', 'developer', 'embed', 'music']),
    ('dollar', 'music-note-currency-dollar', ['music note', 'dollar', 'price', 'money', 'music']),
    ('percent', 'music-note-discount', ['music note', 'discount', 'sale', 'percent', 'music']),
    ('gear', 'music-note-gear', ['music note', 'settings', 'configure', 'music', 'note']),
    ('heart', 'music-note-heart', ['music note', 'favorite', 'like', 'love', 'music']),
    ('lightning', 'music-note-lightning', ['music note', 'fast', 'power', 'instant', 'music']),
    ('search', 'music-note-magnifying-glass', ['music note', 'search', 'find', 'music', 'note']),
    ('minus', 'music-note-minus', ['music note minus', 'remove', 'subtract', 'music', 'note']),
    ('pause', 'music-note-pause', ['music note', 'paused', 'hold', 'music', 'note']),
    ('plus', 'music-note-plus', ['add song', 'add to playlist', 'new track', 'add music', 'playlist add']),
    ('pin', 'music-note-push-pin', ['music note', 'pin', 'pinned', 'music', 'note']),
    ('question', 'music-note-question', ['music note', 'help', 'unknown', 'question', 'music']),
    ('share', 'music-note-share', ['music note', 'share', 'send', 'music', 'note']),
    ('star', 'music-note-star', ['music note', 'favorite', 'starred', 'featured', 'music']),
    ('warning', 'music-note-warning', ['music note', 'warning', 'alert', 'error', 'music']),
    ('x', 'music-note-x', ['music note x', 'remove', 'cancel', 'music', 'note']),
]:
    icon(name, CAT, tags, **merge(NOTE, mark(kind, NB)))

icon('music-note-slash', CAT, ['mute music', 'no music', 'note', 'slash', 'music off'],
     line=NOTE['line'] + [SLASH])

# ----------------------------------------------------------------------- microphone (from microphone.svg) + badges
MIC = load('microphone')
MB = (190, 190); MRC = 60


def arc_visible(c, r, a_from, a_to, B, rc, step=0.25):
    """Pieces of the arc from angle a_from to a_to (degrees, either direction) that stay outside circle (B, rc)."""
    n = int(abs(a_to - a_from) / step)
    angs = [a_from + (a_to - a_from) * i / n for i in range(n + 1)]
    runs, cur = [], []
    for a in angs:
        if dist(polar(c, r, a), B) >= rc:
            cur.append(a)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    out = []
    for run in runs:
        if abs(run[-1] - run[0]) < 20:
            continue
        a0, a1 = run[0], run[-1]
        sweep = 1 if a1 > a0 else 0
        large = 1 if abs(a1 - a0) > 180 else 0
        out.append(P(f'M{pt(polar(c, r, a0))} A{f(r)} {f(r)} 0 {large} {sweep} {pt(polar(c, r, a1))}'))
    return out


MIC_TRIM = [MIC['line'][0]] + arc_visible((128, 128), 64, 180, 0, MB, MRC) + [MIC['line'][2]]
for kind, name, tags in [
    ('check', 'microphone-check', ['mic ok', 'sound check', 'verified audio', 'microphone', 'check']),
    ('minus', 'microphone-minus', ['remove mic', 'lower input', 'less', 'microphone', 'minus']),
    ('plus', 'microphone-plus', ['add mic', 'add audio', 'record', 'microphone', 'plus']),
    ('warning', 'microphone-warning', ['mic problem', 'audio error', 'mic alert', 'microphone', 'warning']),
]:
    icon(name, CAT, tags, **merge(dict(line=MIC_TRIM, area=MIC['area']), mark(kind, MB)))

# ----------------------------------------------------------------------- stage microphone
HC, HR = (164, 92), 52
u = (-math.sqrt(.5), math.sqrt(.5)); n = (math.sqrt(.5), math.sqrt(.5))
ax = lambda s, w: (HC[0] + u[0] * s + n[0] * w, HC[1] + u[1] * s + n[1] * w)
s0 = math.sqrt(HR * HR - 22 * 22); s1 = 160
hb = ax(s1, 0)
handle_open = (f'M{pt(ax(s0, 22))} L{pt(ax(s1, 14))} ' + arc_to(hb, 14, ax(s1, 14), ax(s1, -14), lambda m: dist(m, HC))
               + f' L{pt(ax(s0, -22))}')
STAGE_LINE = [C(*HC, HR), P(handle_open)]
STAGE_DET = [L(*ax(0, -30), *ax(0, 30)), L(*ax(80, -19.5), *ax(80, 19.5))]
icon('microphone-stage', CAT, ['singing', 'karaoke', 'performance', 'handheld microphone', 'singer'],
     line=STAGE_LINE, detail=STAGE_DET, area=[C(*HC, HR), P(handle_open + ' Z')])
icon('microphone-stage-slash', CAT, ['mic off', 'handheld mic off', 'mute', 'karaoke', 'microphone'],
     line=STAGE_LINE + STAGE_DET + [SLASH])

# ----------------------------------------------------------------------- music notes (from music-notes.svg) +/-
NOTES = load('music-notes')
nfn = scaler((72, 184), (64, 158), 0.8)
NOTES_S = {k: [el_tf(e, nfn, 0.8) for e in v] for k, v in NOTES.items() if v}
NSB = (192, 194)
icon('music-notes-plus', CAT, ['add songs', 'add to playlist', 'new track', 'music', 'plus'],
     **merge(NOTES_S, mark('plus', NSB)))
icon('music-notes-minus', CAT, ['remove song', 'remove from playlist', 'delete track', 'music', 'minus'],
     **merge(NOTES_S, mark('minus', NSB)))

# ----------------------------------------------------------------------- playlist (from playlist.svg) variants
# note moves to the upper right so the badge gets the lower-right corner
PL_LINES = [L(40, 64, 136, 64), L(40, 120, 104, 120), L(40, 176, 120, 176)]
PL_NOTE = [C(168, 120, 24), L(192, 120, 192, 40), L(192, 40, 224, 56)]
PB = (188, 200)
icon('playlist-check', CAT, ['added to playlist', 'queue', 'done', 'music', 'playlist'],
     **merge(dict(line=PL_LINES + PL_NOTE, area=[C(168, 120, 24)]), mark('check', PB)))
icon('playlist-minus', CAT, ['remove from playlist', 'queue', 'delete', 'music', 'playlist'],
     **merge(dict(line=PL_LINES + PL_NOTE, area=[C(168, 120, 24)]), mark('minus', PB)))

# ----------------------------------------------------------------------- macro (tulip)
TULIP = 'M72 56 L100 84 L128 48 L156 84 L184 56 V104 A56 56 0 0 1 72 104 Z'
LEAF_L = 'M128 216 C120 192 104 180 76 180 C80 204 100 216 128 216 Z'
LEAF_R = 'M128 216 C136 192 152 180 180 180 C176 204 156 216 128 216 Z'
MACRO = [P(TULIP), L(128, 160, 128, 224), P(LEAF_L), P(LEAF_R)]
icon('macro', CAT, ['macro', 'close up', 'flower', 'camera mode', 'tulip'],
     line=MACRO, area=[P(TULIP), P(LEAF_L), P(LEAF_R)])
icon('macro-slash', CAT, ['macro', 'off', 'disabled', 'hidden', 'close up'], line=MACRO + [SLASH])


# ----------------------------------------------------------------------- masks theater
def sample_d(d, steps=24):
    """Sample an absolute M/L/C/Z path into a list of points (single subpath)."""
    toks = re.findall(r'[MLCZ]|-?\d*\.?\d+', d)
    pts, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == 'Z':
                pts.append(pts[0])
            continue
        if cmd in 'ML':
            p = (float(toks[i]), float(toks[i + 1])); i += 2
            if pts and cmd == 'L':
                a = pts[-1]
                k = max(1, int(dist(a, p) / 3))
                pts += [lerp(a, p, j / k) for j in range(1, k + 1)]
            else:
                pts.append(p)
        elif cmd == 'C':
            a = pts[-1]
            b, c2, e = [(float(toks[i + 2 * j]), float(toks[i + 2 * j + 1])) for j in range(3)]; i += 6
            for j in range(1, steps + 1):
                t_ = j / steps; m = 1 - t_
                pts.append((m ** 3 * a[0] + 3 * m * m * t_ * b[0] + 3 * m * t_ * t_ * c2[0] + t_ ** 3 * e[0],
                            m ** 3 * a[1] + 3 * m * m * t_ * b[1] + 3 * m * t_ * t_ * c2[1] + t_ ** 3 * e[1]))
    return pts


def arc_pts(c, r, a0, a1, step=3):
    n = max(2, int(abs(a1 - a0) / step))
    return [polar(c, r, a0 + (a1 - a0) * j / n) for j in range(n + 1)]


def inside_poly(p, poly):
    x, y = p; ins = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return dist(p, (a[0] + t * dx, a[1] + t * dy))


def poly_dist(p, poly):
    return min(seg_dist(p, a, b) for a, b in zip(poly, poly[1:]))


def rdp(pts, eps=0.35):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    idx, dm = 0, 0
    for i in range(1, len(pts) - 1):
        d = seg_dist(pts[i], a, b)
        if d > dm:
            idx, dm = i, d
    if dm > eps:
        return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [a, b]


def clip_outside(pts, poly, margin):
    """Runs of an open/closed polyline that stay outside poly by at least margin."""
    ok = [not inside_poly(p, poly) and poly_dist(p, poly) >= margin for p in pts]
    runs, cur = [], []
    for p, k in zip(pts, ok):
        if k:
            cur.append(p)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    if len(runs) > 1 and ok[0] and ok[-1] and dist(pts[0], pts[-1]) < 1e-6:
        runs = [runs[-1] + runs[0][1:]] + runs[1:-1]
    return [r for r in runs if len(r) > 1 and dist(r[0], r[-1]) > 6]


MASK = 'M48 60 C96 36 160 36 208 60 V120 C208 176 168 216 128 216 C88 216 48 176 48 120 Z'
FC, FS, FR = (91, 161), 0.62, -12
BC, BS, BR = (167, 91), 0.58, 14
fnF = compose(scaler((128, 128), FC, FS), rotator(FR, FC))
fnB = compose(scaler((128, 128), BC, BS), rotator(BR, BC))
front_d = tf_path(MASK, fnF, FS)
back_d = tf_path(MASK, fnB, BS)
front_poly = sample_d(front_d)
# comedy: smiling eyes and wide smile; tragedy: drooping eyes and frown
F_SMILE = P(tf_path('M88 148 A44 44 0 0 0 168 148', fnF, FS))
F_EYES = [fnF((92, 108)), fnF((164, 108))]
back_outline = sample_d(back_d)
MARGIN = 32
B_LINES = [PL([pt_ for pt_ in rdp(r)]) for r in clip_outside(back_outline, front_poly, MARGIN)]
frown = [fnB(p) for p in arc_pts((128, 204), 40, -135, -45)]
B_LINES += [PL(rdp(r)) for r in clip_outside(frown, front_poly, MARGIN)]
B_EYES = [e for e in (fnB((94, 112)), fnB((162, 112))) if not inside_poly(e, front_poly) and poly_dist(e, front_poly) >= MARGIN]
back_area = _build.to_d(_build.difference(_build.filled([back_d]), _build.filled([front_d]),
                                           _build.stroke([front_d], 2 * MARGIN)))
icon('masks-theater', CAT, ['theater', 'comedy', 'drama', 'masks', 'comedy tragedy'],
     line=[P(front_d)] + B_LINES[:1], detail=[F_SMILE] + B_LINES[1:], area=[P(front_d), P(back_area)],
     dotcut=[C(*e, 14) for e in F_EYES + B_EYES])
icon('masks-theater-slash', CAT, ['masks theater', 'off', 'disabled', 'hidden', 'masks'],
     line=[P(front_d), F_SMILE] + B_LINES + [SLASH], dot=[C(*e, 14) for e in F_EYES + B_EYES])

# ----------------------------------------------------------------------- metronome
METRO = [(100, 36), (156, 36), (212, 216), (44, 216)]
icon('metronome', CAT, ['metronome', 'tempo', 'music', 'rhythm', 'beat'],
     line=[PG(METRO)], detail=[L(84, 176, 172, 176), L(128, 176, 148, 92)], area=[PG(METRO)])

# ----------------------------------------------------------------------- monitor play
MON = load('monitor')
icon('monitor-play', CAT, ['video', 'watch', 'play on screen', 'featured video', 'screen'],
     line=MON['line'], detail=[PG([(110, 80), (158, 112), (110, 144)])], area=MON['area'])

# ----------------------------------------------------------------------- music library
FRONT = R(32, 96, 128, 128, 14)
icon('music-library', CAT, ['music collection', 'albums', 'playlist', 'songs', 'library'],
     line=[FRONT, P('M64 64 H176 A16 16 0 0 1 192 80 V192'), P('M96 32 H208 A16 16 0 0 1 224 48 V160')],
     detail=[C(84, 184, 14), L(98, 184, 98, 128), L(98, 128, 126, 142)], area=[FRONT])

# ----------------------------------------------------------------------- music staff
CLEF = ('M80 210 C80 228 108 228 108 206 V72 C108 36 140 28 140 60 C140 96 40 112 40 162 '
        'C40 184 56 198 74 198 C94 198 108 184 108 164 C108 146 92 134 74 140')
icon('music-staff', CAT, ['staff', 'music', 'notation', 'clef', 'treble clef'],
     line=[P(CLEF)] + [L(160, y, 224, y) for y in (64, 96, 128, 160, 192)])

# ----------------------------------------------------------------------- music video
SCR = R(32, 48, 192, 160, 14)
icon('music-video', CAT, ['music video', 'clip', 'video', 'song', 'music'],
     line=[SCR], detail=[C(112, 156, 20), L(132, 156, 132, 88), P('M132 88 C152 92 172 104 166 128')], area=[SCR])

# ----------------------------------------------------------------------- panorama
PAN = 'M32 64 C96 88 160 88 224 64 V192 C160 168 96 168 32 192 Z'
PAN_M = PL([(48, 180), (92, 124), (128, 160), (156, 132), (208, 182)])
icon('panorama', CAT, ['panorama', 'wide photo', 'landscape', 'picture', 'panoramic'],
     line=[P(PAN)], detail=[PAN_M], area=[P(PAN)], dotcut=[C(184, 112, 14)])
icon('panorama-slash', CAT, ['panorama', 'off', 'disabled', 'hidden', 'wide photo'],
     line=[P(PAN), PAN_M, SLASH])
PANV = 'M64 40 C104 56 152 56 192 40 V216 C152 200 104 200 64 216 Z'
PANV_M = PL([(76, 196), (112, 148), (140, 176), (156, 160), (180, 188)])
icon('panorama-vertical', CAT, ['vertical panorama', 'photo', 'tall', 'wide view', 'panorama'],
     line=[P(PANV)], detail=[PANV_M], area=[P(PANV)], dotcut=[C(148, 100, 14)])
icon('panorama-vertical-slash', CAT, ['panorama vertical', 'off', 'disabled', 'hidden', 'panorama'],
     line=[P(PANV), PANV_M, SLASH])

# ----------------------------------------------------------------------- photo album
BOOK = R(48, 32, 160, 192, 14)
icon('photo-album', CAT, ['album', 'photo book', 'gallery', 'memories', 'photos'],
     line=[BOOK], detail=[L(88, 32, 88, 224), PL([(112, 176), (140, 140), (164, 164), (176, 152), (192, 168)])],
     area=[BOOK], dotcut=[C(168, 92, 14)])

# ----------------------------------------------------------------------- piano
CASE = R(32, 112, 192, 48, 8)
icon('piano', CAT, ['grand piano', 'music', 'instrument', 'keys', 'piano'],
     line=[CASE, L(48, 112, 200, 44), L(148, 112, 164, 61), L(56, 160, 56, 216), L(200, 160, 200, 216),
           L(128, 160, 128, 200), L(112, 200, 144, 200)],
     area=[CASE])
KEYS = R(32, 48, 192, 160, 14)
BK = [R(68, 48, 24, 80, 6), R(164, 48, 24, 80, 6)]
icon('piano-keys', CAT, ['piano', 'keyboard instrument', 'music', 'keys', 'synth'],
     line=[KEYS, L(128, 48, 128, 208), L(80, 128, 80, 208), L(176, 128, 176, 208)] + BK, area=BK)

# ----------------------------------------------------------------------- picture in picture
OUT_R = R(32, 48, 192, 160, 14); IN_R = R(120, 120, 72, 56, 8)
icon('picture-in-picture', CAT, ['pip', 'mini player', 'overlay', 'video', 'float'], line=[OUT_R, IN_R], area=[IN_R])
icon('picture-in-picture-slash', CAT, ['picture in picture', 'off', 'disabled', 'hidden', 'picture'],
     line=[OUT_R, IN_R, SLASH])

# ----------------------------------------------------------------------- play variants
CORN = [PL([(40, 96), (40, 40), (96, 40)]), PL([(160, 40), (216, 40), (216, 96)]),
        PL([(216, 160), (216, 216), (160, 216)]), PL([(96, 216), (40, 216), (40, 160)])]
TRI = [(104, 84), (172, 128), (104, 172)]
icon('play-fullscreen', CAT, ['fullscreen video', 'play', 'expand', 'theater', 'video'],
     line=CORN + [PG(TRI)], area=[PG(TRI)])
PT = [(40, 64), (128, 128), (40, 192)]
icon('play-pause', CAT, ['play pause', 'toggle', 'media', 'control', 'toggle playback'],
     line=[PG(PT), L(168, 64, 168, 192), L(216, 64, 216, 192)], area=[PG(PT)])
RT = [(176, 48), (48, 128), (176, 208)]
icon('play-reverse', CAT, ['reverse', 'play backwards', 'rewind', 'media', 'back'], line=[PG(RT)], area=[PG(RT)])
XT = [(56, 32), (184, 112), (56, 192)]
icon('play-x', CAT, ['playback error', 'play', 'failed', 'media', 'error'],
     **merge(dict(line=[PG(XT)], area=[PG(XT)]), mark('x', (188, 188))))


print(save(overwrite=True))
