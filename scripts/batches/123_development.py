import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Development'
TAU = 2 * math.pi

# ================================================================ carving machinery
# A segment is ('L', p0, p1) or ('E', c, rx, ry, a0, a1) (screen-angle parameter, a1 > a0 means clockwise).


def seg_at(s, t):
    if s[0] == 'L':
        (x0, y0), (x1, y1) = s[1], s[2]
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    _, c, rx, ry, a0, a1 = s
    a = a0 + (a1 - a0) * t
    return (c[0] + rx * math.cos(a), c[1] + ry * math.sin(a))


def sub_cmd(s, t0, t1):
    q = seg_at(s, t1)
    if s[0] == 'L':
        return f'L{pt(q)}'
    _, c, rx, ry, a0, a1 = s
    span = (a1 - a0) * (t1 - t0)
    return f'A{f(rx)} {f(ry)} 0 {1 if abs(span) > math.pi else 0} {1 if span > 0 else 0} {pt(q)}'


def runs(segs, B, cr, closed):
    """Pieces of the chain that stay outside the circle (B, cr), as lists of (seg, t0, t1)."""
    N = 400
    pieces = []  # list of runs, each a list of (si, t0, t1)
    cur = []
    for si, s in enumerate(segs):
        ins = [dist(seg_at(s, i / N), B) < cr for i in range(N + 1)]
        i = 0
        while i <= N:
            if ins[i]:
                if cur:
                    pieces.append(cur); cur = []
                i += 1
                continue
            j = i
            while j < N and not ins[j + 1]:
                j += 1
            t0, t1 = i / N, j / N
            # refine the boundaries by bisection
            if i > 0:
                lo, hi = (i - 1) / N, t0
                for _ in range(30):
                    m = (lo + hi) / 2
                    if dist(seg_at(s, m), B) < cr: lo = m
                    else: hi = m
                t0 = hi
                if cur:
                    pieces.append(cur); cur = []
            if j < N:
                lo, hi = t1, (j + 1) / N
                for _ in range(30):
                    m = (lo + hi) / 2
                    if dist(seg_at(s, m), B) < cr: hi = m
                    else: lo = m
                t1 = lo
            if t1 - t0 > 1e-6:
                cur.append((si, t0, t1))
            if j < N:
                pieces.append(cur); cur = []
            i = j + 1
    if cur:
        pieces.append(cur)
    pieces = [p for p in pieces if p]
    if closed and len(pieces) > 1:
        first, last = pieces[0], pieces[-1]
        if first[0][0] == 0 and first[0][1] == 0 and last[-1][0] == len(segs) - 1 and abs(last[-1][2] - 1) < 1e-9:
            pieces = [last + first] + pieces[1:-1]
    return pieces


def run_len(segs, run):
    return sum(dist(seg_at(segs[si], t0 + (t1 - t0) * k / 20), seg_at(segs[si], t0 + (t1 - t0) * (k + 1) / 20))
               for si, t0, t1 in run for k in range(20))


def run_d(segs, run):
    si, t0, _ = run[0]
    d = 'M' + pt(seg_at(segs[si], t0))
    for si, t0, t1 in run:
        d += ' ' + sub_cmd(segs[si], t0, t1)
    return d


def chain_d(segs, closed=False):
    d = 'M' + pt(seg_at(segs[0], 0)) + ''.join(' ' + sub_cmd(s, 0, 1) for s in segs)
    return d + (' Z' if closed else '')


def carve_closed(segs, B, cr, centroid=(128, 128)):
    """Line path and area path of a closed outline with a circular bite around B."""
    rs = runs(segs, B, cr, True)
    if len(rs) == 1 and len(rs[0]) == len(segs) and all(t0 == 0 and t1 == 1 for _, t0, t1 in rs[0]):
        return [P(chain_d(segs, True))], [P(chain_d(segs, True))]
    lines, areas = [], []
    for r in rs:
        d = run_d(segs, r)
        lines.append(P(d))
        p = seg_at(segs[r[-1][0]], r[-1][2]); q = seg_at(segs[r[0][0]], r[0][1])
        areas.append(P(d + ' ' + arc_to(B, cr, p, q, lambda m: -dist(m, centroid)) + ' Z'))
    return lines, areas


def carve_open(segs, B, cr):
    return [P(run_d(segs, r)) for r in runs(segs, B, cr, False) if run_len(segs, r) > 12]


# ================================================================ the database (library geometry)
DB = load('database')  # outline + two band details, rx 88, ry 32


def db_geo(cx=128, rx=88, ry=32, top=64, bot=192, mid=128):
    outline = [('E', (cx, top), rx, ry, math.pi, TAU), ('L', (cx + rx, top), (cx + rx, bot)),
               ('E', (cx, bot), rx, ry, 0, math.pi), ('L', (cx - rx, bot), (cx - rx, top))]
    bands = [[('E', (cx, top), rx, ry, math.pi, 0)], [('E', (cx, mid), rx, ry, math.pi, 0)]]
    return outline, bands


DB_OUT, DB_BANDS = db_geo()
assert chain_d(DB_OUT, True).replace(' ', '') != ''  # sanity


def db_badge(cr, B=(184, 184)):
    lines, areas = carve_closed(DB_OUT, B, cr)
    detail = []
    for b in DB_BANDS:
        detail += carve_open(b, B, cr)
    return dict(line=lines, area=areas, detail=detail, hole=[], dot=[], dotcut=[])


# ================================================================ badge marks around B
BX, BY = 184, 184
B = (BX, BY)


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


def drop_path(c, r, h):
    """Teardrop: circle (c, r) with a point h above the centre."""
    tip = (c[0], c[1] - h)
    a = math.degrees(math.acos(r / h))
    p1 = polar(c, r, -90 - a); p2 = polar(c, r, -90 + a)
    return f'M{pt(tip)} L{pt(p2)} A{f(r)} {f(r)} 0 1 1 {pt(p1)} Z'


def mark(kind):
    """Returns (roles, clearance radius between the badge centre and the cut database strokes)."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    cr = 64
    if kind == 'check':
        b['line'] = [PL(T([(-28, 2), (-8, 22), (28, -16)]))]
    elif kind == 'x':
        b['line'] = [L(BX - 22, BY - 22, BX + 22, BY + 22), L(BX + 22, BY - 22, BX - 22, BY + 22)]
        cr = 62
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), L(BX - 28, BY, BX + 28, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 28, BY, BX + 28, BY)]
        cr = 58
    elif kind == 'warning':
        b['line'] = [L(BX, BY - 36, BX, BY + 2)]
        b['dot'] = [C(BX, BY + 34, 16)]
        cr = 60
    elif kind == 'code':
        b['line'] = [PL(T([(-16, -24), (-40, 0), (-16, 24)])), PL(T([(16, -24), (40, 0), (16, 24)]))]
        cr = 70
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 18} {BY - 24} H{BX - 6} A12 12 0 0 0 {BX - 6} {BY} '
                       f'H{BX + 6} A12 12 0 0 1 {BX + 6} {BY + 24} H{BX - 18}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 62
    elif kind == 'gear':
        g = gear_path(B, 24, 38, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 9)]
        cr = 68
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.4)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 66
    elif kind == 'star':
        st = [polar((BX, BY + 4), 40 if i % 2 == 0 else 17, -90 + i * 36) for i in range(10)]
        b['line'] = [PG(st)]
        b['area'] = [PG(st)]
        cr = 66
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 8, BY - 8, 24), L(BX + 10, BY + 10, BX + 32, BY + 32)]
        b['area'] = [C(BX - 8, BY - 8, 24)]
        cr = 66
    elif kind == 'pencil':
        pc = [(BX - 34, BY + 34), (BX - 28, BY + 12), (BX + 14, BY - 30), (BX + 30, BY - 14), (BX - 12, BY + 28)]
        b['line'] = [PG(pc)]
        b['area'] = [PG(pc)]
        cr = 64
    elif kind == 'lock':
        b['line'] = [R(BX - 30, BY - 8, 60, 44, 8), P(f'M{BX - 16} {BY - 8} V{BY - 20} A16 16 0 0 1 {BX + 16} {BY - 20} V{BY - 8}')]
        b['area'] = [R(BX - 30, BY - 8, 60, 44, 8)]
        cr = 68
    elif kind == 'user':
        b['dot'] = [C(BX, BY - 18, 18)]
        b['line'] = [P(f'M{BX - 30} {BY + 36} A30 30 0 0 1 {BX + 30} {BY + 36}')]
        cr = 66
    elif kind == 'smile':
        b['line'] = [P(f'M{BX - 28} {BY + 4} A30 30 0 0 0 {BX + 28} {BY + 4}')]
        b['dot'] = [C(BX - 18, BY - 20, 14), C(BX + 18, BY - 20, 14)]
        cr = 66
    elif kind == 'clock':
        b['line'] = [C(BX, BY, 38)]
        b['area'] = [C(BX, BY, 38)]
        b['detail'] = [PL([(BX, BY - 14), (BX, BY), (BX + 10, BY + 8)])]
        cr = 72
    elif kind == 'power':
        b['line'] = [L(BX, BY - 36, BX, BY - 4), P(f'M{BX - 20} {BY - 24} A32 32 0 1 0 {BX + 20} {BY - 24}')]
        cr = 66
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 30} {BY + 30} V{BY + 18} A26 26 0 0 1 {BX - 4} {BY - 8} H{BX + 30}'),
                     PL(T([(8, -30), (30, -8), (8, 14)]))]
        cr = 64
    elif kind == 'export':
        b['line'] = [L(BX - 24, BY - 24, BX + 28, BY + 28), PL(T([(28, -4), (28, 28), (-4, 28)]))]
        cr = 64
    elif kind == 'import':
        b['line'] = [L(BX + 28, BY + 28, BX - 24, BY - 24), PL(T([(-24, 8), (-24, -24), (8, -24)]))]
        cr = 64
    elif kind == 'sync':
        r = 36
        a1 = P(f'M{pt(polar(B, r, 200))} A{r} {r} 0 0 1 {pt(polar(B, r, 320))}')
        e1 = polar(B, r, 320)
        a2 = P(f'M{pt(polar(B, r, 20))} A{r} {r} 0 0 1 {pt(polar(B, r, 140))}')
        e2 = polar(B, r, 140)
        b['line'] = [a1, a2,
                     PL([(e1[0], e1[1] - 16), e1, (e1[0] - 16, e1[1])]),
                     PL([(e2[0], e2[1] + 16), e2, (e2[0] + 16, e2[1])])]
        cr = 74
    elif kind == 'restore':
        r = 30
        st = polar(B, r, 200)
        b['line'] = [P(f'M{pt(st)} A{r} {r} 0 1 1 {pt(polar(B, r, 120))}'),
                     PL([(st[0] - 2, st[1] - 22), st, (st[0] + 20, st[1] - 8)])]
        cr = 66
    elif kind == 'leak':
        d1 = drop_path((BX - 10, BY + 12), 20, 42)
        d2 = drop_path((BX + 30, BY + 20), 8, 20)
        b['line'] = [P(d1), P(d2)]
        b['area'] = [P(d1), P(d2)]
        cr = 64
    elif kind == 'script':
        pg = f'M{BX - 26} {BY - 38} H{BX + 12} L{BX + 30} {BY - 20} V{BY + 38} H{BX - 26} Z'
        b['line'] = [P(pg)]
        b['area'] = [P(pg)]
        b['detail'] = [PL([(BX + 10, BY - 38), (BX + 10, BY - 18), (BX + 30, BY - 18)]), L(BX - 8, BY + 14, BX + 10, BY + 14)]
        cr = 70
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[], dotcut=[])
    for d in ds:
        for k, v in d.items():
            out[k] += list(v)
    return out


def db_with(kind):
    b, cr = mark(kind)
    return merge(db_badge(cr), b)


DB_VARIANTS = [
    ('database-check', ['database', 'verified', 'check', 'storage', 'success'], 'check'),
    ('database-clock', ['database', 'history', 'backup', 'schedule'], 'clock'),
    ('database-code', ['database', 'query', 'sql', 'code'], 'code'),
    ('database-currency-dollar', ['database', 'money', 'price', 'storage', 'data'], 'dollar'),
    ('database-export', ['export data', 'database', 'arrow out', 'backup'], 'export'),
    ('database-gear', ['database', 'settings', 'config', 'gear', 'admin'], 'gear'),
    ('database-heart', ['database', 'favorite', 'like', 'storage', 'data'], 'heart'),
    ('database-import', ['database', 'import', 'load', 'storage', 'data'], 'import'),
    ('database-leak', ['database', 'leak', 'breach', 'storage', 'data'], 'leak'),
    ('database-lock', ['database', 'secure', 'lock', 'storage', 'private'], 'lock'),
    ('database-magnifying-glass', ['query', 'search data', 'database', 'lookup'], 'magnifying-glass'),
    ('database-minus', ['database', 'remove', 'minus', 'storage', 'subtract'], 'minus'),
    ('database-pencil', ['database', 'edit', 'write', 'storage', 'data'], 'pencil'),
    ('database-plus', ['database', 'add', 'new', 'storage', 'add database'], 'plus'),
    ('database-power', ['database', 'power', 'on off', 'shutdown'], 'power'),
    ('database-restore', ['restore', 'recover data', 'rollback'], 'restore'),
    ('database-script', ['sql script', 'query', 'database code'], 'script'),
    ('database-share', ['database', 'share', 'send', 'storage', 'data'], 'share'),
    ('database-smile', ['database', 'happy', 'positive', 'storage', 'data'], 'smile'),
    ('database-star', ['favourite database', 'starred', 'data', 'star'], 'star'),
    ('database-sync', ['database', 'sync', 'refresh', 'backup'], 'sync'),
    ('database-user', ['user data', 'database', 'profile', 'records'], 'user'),
    ('database-warning', ['database', 'error', 'alert', 'exclamation', 'database error'], 'warning'),
    ('database-x', ['database', 'remove', 'delete', 'storage', 'database error'], 'x'),
]
for name, tags, kind in DB_VARIANTS:
    icon(name, CAT, tags, **db_with(kind))

# database-network: the database, shortened, on a network bus
n_out, n_bands = db_geo(cx=128, rx=80, ry=28, top=60, bot=136, mid=98)
icon('database-network', CAT, ['network database', 'distributed', 'server', 'cluster'],
     line=[P(chain_d(n_out, True)), L(128, 172, 128, 208), L(32, 208, 104, 208), L(152, 208, 224, 208)],
     detail=[P(chain_d(b)) for b in n_bands],
     area=[P(chain_d(n_out, True))],
     dot=[C(128, 208, 20)])

# database-slash: the database outline, no area, with the slash
icon('database-slash', CAT, ['database', 'offline', 'disabled', 'storage', 'database off'],
     line=DB['line'] + DB['detail'] + [L(48, 48, 208, 208)])

# ================================================================ devices with code
icon('device-mobile-code', CAT, ['mobile development', 'app code', 'phone coding', 'phone', 'developer'],
     line=load('device-mobile')['line'],
     detail=load('device-mobile')['detail'] + [PL([(112, 114), (96, 136), (112, 158)]), PL([(144, 114), (160, 136), (144, 158)])],
     area=load('device-mobile')['area'])

LAP = load('laptop')
icon('laptop-code', CAT, ['coding', 'developer', 'programming'],
     line=LAP['line'],
     detail=[PL([(108, 88), (84, 112), (108, 136)]), PL([(148, 88), (172, 112), (148, 136)])],
     area=LAP['area'])

# ================================================================ favicon
fst = [polar((128, 132), 56 if i % 2 == 0 else 24, -90 + i * 36) for i in range(10)]
icon('favicon', CAT, ['favicon', 'site icon', 'browser'],
     line=[R(40, 40, 176, 176, 36)], detail=[PG(fst)], area=[R(40, 40, 176, 176, 36)])

# ================================================================ flow-arrow
icon('flow-arrow', CAT, ['flow', 'workflow', 'process'],
     line=[C(60, 128, 28), L(88, 128, 112, 128), C(140, 128, 28), L(168, 128, 220, 128),
           PL([(188, 96), (220, 128), (188, 160)])],
     area=[C(60, 128, 28), C(140, 128, 28)])

# ================================================================ function-slash
icon('function-slash', CAT, ['function', 'off', 'disabled', 'hidden'],
     line=load('function')['line'] + [L(48, 48, 208, 208)])

# ================================================================ git
icon('git-cherry-pick', CAT, ['cherry pick', 'commit', 'version control', 'git'],
     line=[C(76, 180, 28), C(180, 180, 28), P('M76 152 C76 104 104 64 144 44'), P('M180 152 C180 112 168 76 144 44'),
           P('M144 44 C160 36 184 36 204 48')],
     area=[C(76, 180, 28), C(180, 180, 28)])

icon('git-compare', CAT, ['git compare', 'diff', 'branches', 'version control'],
     line=[C(64, 192, 24), C(192, 64, 24),
           P('M64 168 V96 A24 24 0 0 1 88 72 H136'), PL([(112, 48), (136, 72), (112, 96)]),
           P('M192 88 V160 A24 24 0 0 1 168 184 H120'), PL([(144, 160), (120, 184), (144, 208)])],
     area=[C(64, 192, 24), C(192, 64, 24)])

icon('git-diff', CAT, ['diff', 'compare', 'changes'],
     line=[R(32, 40, 192, 176, 14)],
     detail=[L(128, 40, 128, 216), L(80, 104, 80, 152), L(56, 128, 104, 128), L(152, 128, 200, 128)],
     area=[R(32, 40, 192, 176, 14)])

icon('git-merge-queue', CAT, ['merge queue', 'git', 'pipeline', 'version control'],
     line=[C(72, 200, 24), L(72, 40, 72, 176), C(184, 144, 24), P('M184 168 C184 192 160 200 96 200')],
     area=[C(72, 200, 24), C(184, 144, 24)],
     dot=[C(184, 48, 16), C(184, 92, 16)])

PR = load('git-pull-request')
PR_LEFT = [C(72, 56, 24), C(72, 200, 24), L(72, 80, 72, 176)]
icon('git-pull-request-closed', CAT, ['pull request closed', 'rejected', 'git', 'x', 'closed pr'],
     line=PR_LEFT + [C(184, 200, 24), L(184, 176, 184, 132), L(162, 46, 206, 90), L(206, 46, 162, 90)],
     area=[C(72, 56, 24), C(72, 200, 24), C(184, 200, 24)])
icon('git-pull-request-draft', CAT, ['draft', 'pull request', 'git', 'pr', 'draft pull request'],
     line=PR_LEFT + [C(184, 200, 24)],
     area=[C(72, 56, 24), C(72, 200, 24), C(184, 200, 24)],
     dot=[C(184, 132, 16), C(184, 72, 16)])

icon('git-rebase', CAT, ['rebase', 'branch', 'version control', 'history'],
     line=[C(72, 64, 24), L(72, 88, 72, 224), L(96, 64, 160, 64), C(184, 64, 24),
           L(184, 216, 184, 120), PL([(160, 144), (184, 120), (208, 144)])],
     area=[C(72, 64, 24), C(184, 64, 24)])

book_body = 'M48 184 V56 A24 24 0 0 1 72 32 H208 V208 H168'
icon('git-repository', CAT, ['repo', 'repository', 'git', 'source', 'git repository'],
     line=[P(book_body), P('M48 184 A24 24 0 0 0 72 208'), PL([(96, 160), (96, 224), (120, 206), (144, 224), (144, 160)])],
     detail=[P('M48 184 A24 24 0 0 1 72 160 H208')],
     area=[P('M48 184 V56 A24 24 0 0 1 72 32 H208 V208 H72 A24 24 0 0 1 48 184 Z')])

# ================================================================ hard drives slash
HD = load('hard-drives')
icon('hard-drives-slash', CAT, ['server down', 'offline', 'outage', 'disabled'],
     line=HD['line'] + HD['detail'] + [L(48, 48, 208, 208)], dot=HD['dotcut'])

# ================================================================ ip address
tag_ip = [(32, 128), (80, 64), (208, 64), (224, 80), (224, 176), (208, 192), (80, 192)]
tag_d = 'M32 128 L76 68 A10 10 0 0 1 84 64 H208 A16 16 0 0 1 224 80 V176 A16 16 0 0 1 208 192 H84 A10 10 0 0 1 76 188 Z'
icon('ip-address', CAT, ['network address', 'ip', 'internet protocol'],
     line=[P(tag_d)],
     detail=[L(120, 100, 120, 156), P('M156 156 V100 H172 A18 18 0 0 1 172 136 H156')],
     dotcut=[C(80, 128, 12)],
     area=[P(tag_d)])

# ================================================================ issues
icon('issue', CAT, ['issue', 'bug report', 'ticket', 'tracker'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)], dotcut=[C(128, 128, 24)])

rc = 88
s_ = polar((128, 128), rc, 165)
e_ = polar((128, 128), rc, 225)
icon('issue-reopen', CAT, ['reopen', 'issue', 'ticket', 'tracker'],
     line=[P(f'M{pt(s_)} A{rc} {rc} 0 1 0 {pt(e_)}'),
           PL([(e_[0] + 34, e_[1]), e_, (e_[0], e_[1] - 32)])],
     dot=[C(128, 128, 24)])

# ================================================================ list-gear
lg = gear_path((180, 180), 26, 38, 8, -90 + 22.5)
icon('list-gear', CAT, ['list settings', 'configure', 'preferences', 'list'],
     line=[L(40, 64, 216, 64), L(40, 128, 120, 128), L(40, 192, 104, 192), P(lg)],
     area=[P(lg)], hole=[C(180, 180, 10)])

# ================================================================ load balancer
kids = [(52, 196), (128, 196), (204, 196)]
icon('load-balancer', CAT, ['load balancer', 'network', 'distribute', 'server'],
     line=[R(64, 40, 128, 56, 14)] + [C(*k, 20) for k in kids]
     + [L(92, 96, 60.3, 177.6), L(128, 96, 128, 176), L(164, 96, 195.7, 177.6)],
     area=[R(64, 40, 128, 56, 14)] + [C(*k, 20) for k in kids])

# ================================================================ logs
icon('logs', CAT, ['logs', 'log file', 'lines', 'console'],
     line=[L(96, 56, 216, 56), L(96, 104, 184, 104), L(96, 152, 208, 152), L(96, 200, 160, 200)],
     dot=[C(48, 56, 16), C(48, 104, 16), C(48, 152, 16), C(48, 200, 16)])

# ================================================================ markdown
icon('markdown', CAT, ['markdown', 'md', 'text format', 'writing'],
     line=[R(28, 56, 200, 144, 16)],
     detail=[PL([(64, 160), (64, 96), (92, 128), (120, 96), (120, 160)]), L(172, 96, 172, 160),
             PL([(150, 138), (172, 160), (194, 138)])],
     area=[R(28, 56, 200, 144, 16)])

# ================================================================ microfrontends
BR = load('browser')
icon('microfrontends', CAT, ['micro frontends', 'modules', 'architecture', 'web'],
     line=BR['line'],
     detail=BR['detail'] + [L(112, 104, 112, 216), L(112, 160, 224, 160)],
     dotcut=BR['dotcut'], area=BR['area'])

# ================================================================ middleware
icon('middleware', CAT, ['middleware', 'layers', 'pipeline', 'server'],
     line=[R(96, 40, 64, 176, 14), L(32, 128, 96, 128), L(160, 128, 216, 128), PL([(188, 100), (216, 128), (188, 156)])],
     detail=[L(96, 84, 160, 84), L(96, 172, 160, 172), L(96, 128, 160, 128)],
     area=[R(96, 40, 64, 176, 14)])

# ================================================================ network
NET_KIDS = [(52, 200), (128, 200), (204, 200)]
NET_ROOT = [C(128, 56, 24), L(128, 80, 128, 128)]
icon('network', CAT, ['network', 'nodes', 'connection', 'topology'],
     line=NET_ROOT + [L(52, 128, 204, 128), L(52, 128, 52, 180), L(128, 128, 128, 180), L(204, 128, 204, 180)]
     + [C(*k, 20) for k in NET_KIDS],
     area=[C(128, 56, 24)] + [C(*k, 20) for k in NET_KIDS])
icon('network-x', 'Devices', ['network error', 'disconnected', 'network', 'offline', 'no network'],
     line=NET_ROOT + [L(52, 128, 204, 128), L(52, 128, 52, 180), L(128, 128, 128, 180), L(204, 128, 204, 144),
                      L(186, 180, 222, 216), L(222, 180, 186, 216)]
     + [C(*k, 20) for k in NET_KIDS[:2]],
     area=[C(128, 56, 24)] + [C(*k, 20) for k in NET_KIDS[:2]])
icon('network-slash', CAT, ['network off', 'disconnected', 'offline', 'slash'],
     line=NET_ROOT + [L(52, 128, 204, 128), L(52, 128, 52, 180), L(128, 128, 128, 180), L(204, 128, 204, 180)]
     + [C(*k, 20) for k in NET_KIDS] + [L(48, 48, 208, 208)])

print(save(overwrite=True))
