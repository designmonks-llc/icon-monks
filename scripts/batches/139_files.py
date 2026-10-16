import math, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

FI = 'Files'

# ================================================================ small outline engine
# Segments: ('L', p0, p1) | ('A', centre, r, a0, a1)  (angles in radians, a1 may be < a0)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def seg_len(s):
    if s[0] == 'L':
        return dist(s[1], s[2])
    return abs(s[4] - s[3]) * s[2]


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []
    for i, s in enumerate(segs):
        ts = [k / steps for k in range(steps + 1)]
        ok = [keep(seg_point(s, t)) for t in ts]

        def edge(ta, tb, oa):
            for _ in range(40):
                tm = (ta + tb) / 2
                if keep(seg_point(s, tm)) == oa:
                    ta = tm
                else:
                    tb = tm
            return (ta + tb) / 2
        start = 0.0 if ok[0] else None
        for k in range(1, len(ts)):
            if ok[k] != ok[k - 1]:
                e = edge(ts[k - 1], ts[k], ok[k - 1])
                if ok[k]:
                    start = e
                else:
                    pieces.append((i, start, e))
                    start = None
        if start is not None:
            pieces.append((i, start, 1.0))
    if len(pieces) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in pieces):
        return [segs], True
    runs = []
    for i, t0, t1 in pieces:
        sub = seg_sub(segs[i], t0, t1)
        if runs and t0 == 0 and runs[-1][1] == (i - 1, 1.0):
            runs[-1][0].append(sub)
        else:
            runs.append([[sub], None])
        runs[-1][1] = (i, t1)
    if closed and len(runs) > 1 and pieces[0][1] == 0 and pieces[0][0] == 0 and pieces[-1][2] == 1.0 \
            and pieces[-1][0] == len(segs) - 1:
        last = runs.pop()
        runs[0][0] = last[0] + runs[0][0]
    return [r[0] for r in runs], False


def sample(segs, n=60):
    return [seg_point(s, k / n) for s in segs for k in range(n)]


def inside(poly_pts, p):
    x, y = p
    c = False
    for i in range(len(poly_pts)):
        x1, y1 = poly_pts[i]
        x2, y2 = poly_pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def carve(segs, cut_c, cut_r):
    """Open the closed outline segs around a circular badge. Returns (line d, area d)."""
    runs, whole = trim(segs, lambda p: dist(p, cut_c) >= cut_r)
    assert not whole and len(runs) == 1, (whole, len(runs))
    run = runs[0]
    s, e = seg_point(run[0], 0), seg_end(run[-1])
    poly_pts = sample(segs)
    arc = arc_to(cut_c, cut_r, e, s, lambda m: 1 if inside(poly_pts, m) else 0)
    return segs_d(run), segs_d(run) + ' ' + arc + ' Z'


def dashes(segs, n, ratio, offset=0.0):
    """n dashes of length ratio*period along the closed outline segs (arc-length based)."""
    lens = [seg_len(s) for s in segs]
    total = sum(lens)
    per = total / n
    out = []
    for k in range(n):
        a0 = (offset + k * per) % total
        a1 = a0 + ratio * per
        parts = []
        pos = 0
        for rep in range(2):
            for s, ln in zip(segs, lens):
                s0, s1 = pos, pos + ln
                lo, hi = max(a0, s0), min(a1, s1)
                if hi > lo + 1e-6:
                    parts.append(seg_sub(s, (lo - s0) / ln, (hi - s0) / ln))
                pos += ln
        out.append(P(segs_d(parts)))
    return out


# ================================================================ folder (exact geometry of the library folder)
H = math.pi / 2


def folder_segs(x0=32, x1=224, yt=56, yb=208, tab=64, r=16):
    ym = yt + 24
    return [('A', (x0 + r, yt + r), r, 2 * H, 3 * H), ('L', (x0 + r, yt), (x0 + tab, yt)),
            ('L', (x0 + tab, yt), (x0 + tab + 24, ym)), ('L', (x0 + tab + 24, ym), (x1 - r, ym)),
            ('A', (x1 - r, ym + r), r, -H, 0), ('L', (x1, ym + r), (x1, yb - r)),
            ('A', (x1 - r, yb - r), r, 0, H), ('L', (x1 - r, yb), (x0 + r, yb)),
            ('A', (x0 + r, yb - r), r, H, 2 * H), ('L', (x0, yb - r), (x0, yt + r))]


FOLDER = folder_segs()
FD = load('folder')
FOLDER_D = FD['line'][0]
full = dict(line=[FOLDER_D], area=[FOLDER_D])

# ---------------------------------------------------------------- badge marks around B
B = (184, 184)
BX, BY = B


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def gear_path(c, r_root, r_tip, n, phase=0):
    step = 360 / n
    hr, ht = step * 0.3, step * 0.17
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


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


def sparkle_path(c, r):
    k1, k2 = r / 12, r / 3  # same curvature as the library sparkle
    x, y = c
    return (f'M{f(x)} {f(y - r)} C{f(x + k1)} {f(y - k2)} {f(x + k2)} {f(y - k1)} {f(x + r)} {f(y)} '
            f'C{f(x + k2)} {f(y + k1)} {f(x + k1)} {f(y + k2)} {f(x)} {f(y + r)} '
            f'C{f(x - k1)} {f(y + k2)} {f(x - k2)} {f(y + k1)} {f(x - r)} {f(y)} '
            f'C{f(x - k2)} {f(y - k1)} {f(x - k1)} {f(y - k2)} {f(x)} {f(y - r)} Z')


def badge(kind):
    """Returns (roles dict, clearance radius)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    if kind == 'clock':
        b['line'] = [C(BX, BY, 36)]
        b['area'] = [C(BX, BY, 36)]
        b['detail'] = [PL([(BX, BY - 16), (BX, BY), (BX + 12, BY + 8)])]
        cr = 70
    elif kind == 'cloud':
        cl = (f'M{BX - 20} {BY + 18} H{BX + 20} A12 12 0 0 0 {BX + 20} {BY - 6} '
              f'A20 20 0 0 0 {BX - 20} {BY - 6} A12 12 0 0 0 {BX - 20} {BY + 18} Z')
        b['line'] = [P(cl)]
        b['area'] = [P(cl)]
        cr = 68
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 22} H{BX - 4} A11 11 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A11 11 0 0 1 {BX + 4} {BY + 22} H{BX - 16}'),
                     L(BX, BY - 34, BX, BY - 22), L(BX, BY + 22, BX, BY + 34)]
        cr = 66
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 64
    elif kind == 'lightning':
        bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bolt)]
        b['area'] = [PG(bolt)]
        cr = 64
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 62
    elif kind == 'prohibit':
        r = 30
        o = r / math.sqrt(2)
        b['line'] = [C(BX, BY, r), L(BX - o, BY - o, BX + o, BY + o)]
        cr = 66
    elif kind == 'push-pin':
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(c)) for a, c in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.36, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 64
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 66
    elif kind == 'shield':
        sh = (f'M{BX} {BY - 34} L{BX + 28} {BY - 23} V{BY - 2} C{BX + 28} {BY + 18} {BX + 14} {BY + 29} {BX} {BY + 34} '
              f'C{BX - 14} {BY + 29} {BX - 28} {BY + 18} {BX - 28} {BY - 2} V{BY - 23} Z')
        b['line'] = [P(sh)]
        b['area'] = [P(sh)]
        cr = 68
    elif kind == 'sparkle':
        sp = sparkle_path(B, 34)
        b['line'] = [P(sp)]
        b['area'] = [P(sp)]
        cr = 64
    elif kind == 'video':
        body = R(BX - 32, BY - 18, 40, 36, 8)
        lens = PG([(BX + 8, BY - 6), (BX + 30, BY - 18), (BX + 30, BY + 18), (BX + 8, BY + 6)])
        b['line'] = [body, lens]
        b['area'] = [body, lens]
        cr = 68
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return out


def folder_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(FOLDER, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)]), b)


# ================================================================ badge variants
for suffix, kind, tags in [
    ('clock', 'clock', ['history', 'recent', 'folder', 'time']),
    ('cloud', 'cloud', ['cloud folder', 'sync', 'folder', 'online']),
    ('currency-dollar', 'dollar', ['folder', 'dollar', 'price', 'money']),
    ('gear', 'gear', ['folder settings', 'config', 'folder', 'preferences', 'directory']),
    ('lightning', 'lightning', ['folder', 'fast', 'power', 'instant']),
    ('pause', 'pause', ['folder', 'paused', 'hold']),
    ('prohibit', 'prohibit', ['blocked', 'forbidden', 'folder', 'denied', 'blocked folder']),
    ('push-pin', 'push-pin', ['folder', 'pin', 'pinned']),
    ('share', 'share', ['folder', 'share', 'send']),
    ('shield', 'shield', ['protected', 'secure folder', 'folder', 'shield']),
    ('sparkle', 'sparkle', ['folder', 'ai', 'magic', 'smart']),
    ('video', 'video', ['videos', 'movies', 'folder', 'media']),
]:
    icon(f'folder-{suffix}', FI, tags, **folder_badge(kind))

# ================================================================ symbols inside the folder body (centre ~ (128,144))
icon('folder-code', FI, ['code folder', 'project', 'source', 'repository', 'project folder'],
     detail=[PL([(112, 116), (88, 144), (112, 172)]), PL([(144, 116), (168, 144), (144, 172)])], **full)

icon('folder-heart', FI, ['favourite folder', 'directory', 'love', 'heart'],
     detail=[P(heart_path((128, 150), 0.4))], **full)

icon('folder-image', FI, ['pictures', 'photos', 'folder', 'images', 'photo folder'],
     detail=[PL([(72, 176), (108, 132), (136, 164), (152, 148), (180, 176)])],
     dotcut=[C(160, 112, 14)], **full)

icon('folder-info', FI, ['folder info', 'details', 'directory', 'i'],
     detail=[L(128, 140, 128, 176)], dotcut=[C(128, 110, 14)], **full)

icon('folder-magnifying-glass', FI, ['search folder', 'find', 'folder', 'browse', 'directory'],
     detail=[C(120, 136, 24), L(137, 153, 156, 172)], **full)

icon('folder-music', FI, ['music folder', 'audio', 'library', 'folder', 'directory'],
     detail=[PL([(130, 166), (130, 110), (154, 122)])], dotcut=[C(116, 168, 20)], **full)

icon('folder-question', FI, ['unknown folder', 'folder', 'question', 'help', 'directory'],
     detail=[P('M110 118 A19 19 0 1 1 136 135.5 C130 138 128 142 128 150')], dotcut=[C(128, 178, 14)], **full)

st = [polar((128, 147), 40 if i % 2 == 0 else 19, -90 + i * 36) for i in range(10)]
icon('folder-star', FI, ['favorite folder', 'starred', 'important', 'special', 'folder'],
     detail=[PG(st)], **full)

icon('folder-symlink', FI, ['shortcut', 'alias', 'link', 'folder'],
     detail=[P('M92 176 V160 A28 28 0 0 1 120 132 H164'), PL([(140, 108), (164, 132), (140, 156)])], **full)

icon('folder-user', FI, ['personal folder', 'home folder', 'user files', 'shared folder', 'personal'],
     detail=[C(128, 116, 18), P('M84 182 C84 166 102 156 128 156 C154 156 172 166 172 182')], **full)

icon('folder-warning', FI, ['folder error', 'directory', 'warning', 'alert'],
     detail=[L(128, 108, 128, 146)], dotcut=[C(128, 176, 14)], **full)

icon('folder-x', FI, ['folder', 'delete', 'remove', 'x', 'folder error'],
     detail=[L(106, 122, 150, 166), L(150, 122, 106, 166)], **full)

# zip: a zipper track hanging from the top edge with a pull tab
icon('folder-zip', FI, ['archive', 'compressed', 'zip', 'folder'],
     detail=[L(152, 106, 152, 130), R(136, 130, 32, 48, 10)], **full)

# dashed
icon('folder-dashed', FI, ['draft folder', 'placeholder', 'new folder', 'folder', 'focus'],
     line=dashes(FOLDER, 12, 0.5, offset=-8))

# slash
SLASH = L(48, 48, 208, 208)
icon('folder-slash', FI, ['folder off', 'hidden', 'no folder', 'slash'], line=[FOLDER_D, SLASH])

# network: a smaller folder on a stem down to a network node and its bus line
NF = P(segs_d(folder_segs(48, 208, 32, 148, tab=56), True))
icon('folder-network', FI, ['shared folder', 'network', 'directory', 'server'],
     line=[NF, L(128, 148, 128, 188), C(128, 204, 16), L(32, 204, 112, 204), L(144, 204, 224, 204)],
     area=[NF, C(128, 204, 16)])

# ================================================================ folders: front folder, back folder peeking top-right
FRONT = P(segs_d(folder_segs(32, 192, 104, 224, tab=56), True))
BACK = 'M64 64 A16 16 0 0 1 80 48 H112 L136 72 H208 A16 16 0 0 1 224 88 V160'
BACK_AREA = 'M64 80 V64 A16 16 0 0 1 80 48 H112 L136 72 H208 A16 16 0 0 1 224 88 V160 H216 V104 H130 L106 80 Z'
icon('folders', FI, ['copy folder', 'folders', 'multiple', 'stack', 'directories'],
     line=[FRONT, P(BACK)], area=[FRONT, P(BACK_AREA)])
icon('folders-slash', FI, ['folders', 'off', 'disabled', 'hidden'], line=[FRONT, P(BACK), SLASH])

# ================================================================ note / notebook
note = load('note')
icon('note-slash', FI, ['note', 'off', 'disabled', 'hidden'], line=note['line'] + [SLASH])

nb = load('notebook')
NB = nb['line'][0]
SPINE = nb['detail'][0]
nbf = dict(line=[NB], area=[NB])
NC = (156, 128)
X, Y = NC
for suffix, tags, det in [
    ('arrow-down', ['notebook', 'download', 'journal', 'arrow'], [L(X, 92, X, 162), PL([(X - 24, 138), (X, 162), (X + 24, 138)])]),
    ('arrow-up', ['notebook', 'upload', 'journal', 'arrow'], [L(X, 164, X, 94), PL([(X - 24, 118), (X, 94), (X + 24, 118)])]),
    ('check', ['notebook', 'done', 'journal', 'check'], [PL([(X - 26, Y + 2), (X - 8, Y + 20), (X + 26, Y - 16)])]),
    ('minus', ['notebook', 'remove', 'journal', 'minus'], [L(X - 26, Y, X + 26, Y)]),
    ('plus', ['notebook', 'add', 'journal', 'plus'], [L(X, Y - 26, X, Y + 26), L(X - 26, Y, X + 26, Y)]),
    ('x', ['notebook', 'delete', 'journal', 'x'], [L(X - 20, Y - 20, X + 20, Y + 20), L(X + 20, Y - 20, X - 20, Y + 20)]),
]:
    icon(f'notebook-{suffix}', FI, tags, detail=[SPINE] + det, **nbf)

icon('notebook-image', FI, ['album', 'notebook', 'photos', 'journal'],
     detail=[SPINE, PL([(124, 168), (148, 132), (164, 152), (172, 144), (188, 164)])],
     dotcut=[C(172, 96, 14)], **nbf)

icon('notebook-bookmark', FI, ['notebook', 'bookmark', 'journal', 'saved'],
     line=[NB, PL([(140, 32), (140, 112), (164, 92), (188, 112), (188, 32)])], area=[NB],
     detail=[SPINE], hole=[PG([(148, 48), (180, 48), (180, 95), (164, 82), (148, 95)])])

icon('notebook-slash', FI, ['notebook', 'off', 'disabled', 'hidden'], line=[NB, SPINE, SLASH])

# notebooks: front notebook, back notebook peeking top-right
FNB = R(32, 72, 136, 152, 14)
BNB = 'M88 46 A14 14 0 0 1 102 32 H210 A14 14 0 0 1 224 46 V170 A14 14 0 0 1 210 184'
BNB_AREA = 'M88 48 V46 A14 14 0 0 1 102 32 H210 A14 14 0 0 1 224 46 V170 A14 14 0 0 1 210 184 H192 V48 Z'
icon('notebooks', FI, ['notebooks', 'journals', 'library', 'stack'],
     line=[FNB, P(BNB)], area=[FNB, P(BNB_AREA)], detail=[L(72, 72, 72, 224)])

print(save(overwrite=True))
