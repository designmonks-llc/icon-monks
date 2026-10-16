import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import build as _b

PE = 'People'
SLASH = L(48, 48, 208, 208)
SG = 32  # centerline clearance kept between the slash and the strokes it crosses

# ---------------------------------------------------------------- slash gapping (exact path splitting)
def _attrs(el):
    return {k: v for k, v in re.findall(r'([\w-]+)="([^"]*)"', el)}


def el_d(el):
    a = _attrs(el)
    g = lambda k, d=0: float(a.get(k, d))
    if el.startswith('<path'):
        return a['d']
    if el.startswith('<circle') or el.startswith('<ellipse'):
        cx, cy = g('cx'), g('cy')
        rx = g('r') if el.startswith('<circle') else g('rx')
        ry = g('r') if el.startswith('<circle') else g('ry')
        return f'M{f(cx - rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx + rx)} {f(cy)} A{f(rx)} {f(ry)} 0 1 1 {f(cx - rx)} {f(cy)} Z'
    if el.startswith('<rect'):
        x, y, w, h = g('x'), g('y'), g('width'), g('height')
        r = min(g('rx'), w / 2, h / 2)
        if not r:
            return f'M{f(x)} {f(y)} H{f(x + w)} V{f(y + h)} H{f(x)} Z'
        return (f'M{f(x + r)} {f(y)} H{f(x + w - r)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} V{f(y + h - r)} '
                f'A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} H{f(x + r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} '
                f'V{f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z')
    raise ValueError(el)


def _ang(u, v):
    a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    return a


def parse(d):
    """Absolute M L H V C A Z -> list of subpaths [(segments, closed)]."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cmd = None; cur = (0, 0); start = (0, 0); subs = []; segs = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd == 'Z':
                if dist(cur, start) > 1e-6:
                    segs.append(('L', cur, start))
                subs.append((segs, True)); segs = None; cur = start
                continue
        if cmd == 'M':
            if segs:
                subs.append((segs, False))
            cur = start = (num(), num()); segs = []; cmd = 'L'
        elif cmd == 'L':
            p = (num(), num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'H':
            p = (num(), cur[1]); segs.append(('L', cur, p)); cur = p
        elif cmd == 'V':
            p = (cur[0], num()); segs.append(('L', cur, p)); cur = p
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); p = (num(), num())
            segs.append(('C', cur, c1, c2, p)); cur = p
        elif cmd == 'A':
            rx, ry, _, fa, fs = num(), num(), num(), num(), num(); p = (num(), num())
            x1p, y1p = (cur[0] - p[0]) / 2, (cur[1] - p[1]) / 2
            lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
            if lam > 1:
                rx *= math.sqrt(lam); ry *= math.sqrt(lam)
            num_ = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
            den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
            co = math.sqrt(max(0, num_ / den)) * (-1 if fa == fs else 1)
            cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
            cx, cy = cxp + (cur[0] + p[0]) / 2, cyp + (cur[1] + p[1]) / 2
            u = ((x1p - cxp) / rx, (y1p - cyp) / ry); v = ((-x1p - cxp) / rx, (-y1p - cyp) / ry)
            t1 = math.atan2(u[1], u[0]); dt = _ang(u, v)
            if fs == 0 and dt > 0: dt -= 2 * math.pi
            if fs == 1 and dt < 0: dt += 2 * math.pi
            segs.append(('A', (cx, cy), rx, ry, t1, t1 + dt)); cur = p
    if segs:
        subs.append((segs, False))
    return subs


def at(s, t):
    if s[0] == 'L':
        return (s[1][0] + (s[2][0] - s[1][0]) * t, s[1][1] + (s[2][1] - s[1][1]) * t)
    if s[0] == 'C':
        p0, p1, p2, p3 = s[1:]
        m = 1 - t
        return tuple(m ** 3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t ** 3 * p3[k] for k in (0, 1))
    a = s[4] + (s[5] - s[4]) * t
    return (s[1][0] + s[2] * math.cos(a), s[1][1] + s[3] * math.sin(a))


def subseg(s, t0, t1):
    if s[0] == 'L':
        return ('L', at(s, t0), at(s, t1))
    if s[0] == 'A':
        return ('A', s[1], s[2], s[3], s[4] + (s[5] - s[4]) * t0, s[4] + (s[5] - s[4]) * t1)
    def split(p, t):
        p0, p1, p2, p3 = p
        l = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        a, b, c = l(p0, p1), l(p1, p2), l(p2, p3)
        d, e = l(a, b), l(b, c)
        g = l(d, e)
        return (p0, a, d, g), (g, e, c, p3)
    pts = s[1:]
    if t1 < 1:
        pts = split(pts, t1)[0]
    if t0 > 0:
        pts = split(pts, t0 / t1)[1]
    return ('C',) + tuple(pts)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    dt = s[5] - s[4]
    end = at(s, 1)
    if abs(s[2] - s[3]) < 1e-6:
        r = f(s[2]); rr = f'{r} {r}'
    else:
        rr = f'{f(s[2])} {f(s[3])}'
    return f'A{rr} 0 {1 if abs(dt) > math.pi else 0} {1 if dt > 0 else 0} {pt(end)}'


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gap(el, g=SG, keep=None):
    """Return path elements of el with everything within g of the slash removed."""
    keep = keep or (lambda p: seg_dist(p) >= g)
    out = []
    for segs, closed in parse(el_d(el)):
        pieces = []  # (seg index, t0, t1)
        for si, s in enumerate(segs):
            N = 240
            ks = [keep(at(s, j / N)) for j in range(N + 1)]
            j = 0
            while j <= N:
                if not ks[j]:
                    j += 1; continue
                k = j
                while k < N and ks[k + 1]:
                    k += 1
                def refine(lo, hi):  # lo kept, hi not
                    for _ in range(40):
                        m = (lo + hi) / 2
                        if keep(at(s, m)): lo = m
                        else: hi = m
                    return lo
                t0 = j / N if j == 0 else refine(j / N, (j - 1) / N)
                t1 = k / N if k == N else refine(k / N, (k + 1) / N)
                if t1 - t0 > 1e-4:
                    pieces.append((si, t0, t1))
                j = k + 1
        # join pieces into runs
        runs = []
        for pc in pieces:
            if runs and runs[-1][-1][0] == pc[0] - 1 and runs[-1][-1][2] > 1 - 1e-9 and pc[1] < 1e-9:
                runs[-1].append(pc)
            else:
                runs.append([pc])
        if not runs:
            continue
        full = len(runs) == 1 and len(runs[0]) == len(segs) and runs[0][0][1] < 1e-9 and runs[0][-1][2] > 1 - 1e-9
        if closed and not full and len(runs) > 1 and runs[0][0][0] == 0 and runs[0][0][1] < 1e-9 \
                and runs[-1][-1][0] == len(segs) - 1 and runs[-1][-1][2] > 1 - 1e-9:
            runs[0] = runs.pop() + runs[0]
        for run in runs:
            ss = [subseg(segs[si], t0, t1) for si, t0, t1 in run]
            if sum(dist(at(s, 0), at(s, 0.5)) + dist(at(s, 0.5), at(s, 1)) for s in ss) < 12:
                continue
            d = f'M{pt(at(ss[0], 0))} ' + ' '.join(seg_cmd(s) for s in ss)
            if full and closed:
                d += ' Z'
            out.append(P(d))
    return out


def slashed(src, g=SG, drop_dots=True):
    """Slash variant: area left out, details become lines, every stroke opened around the slash."""
    lines = []
    for el in src.get('line', []) + src.get('detail', []):
        lines += gap(el, g)
    dots = []
    for el in src.get('dot', []) + src.get('dotcut', []):
        a = _attrs(el)
        c, r = (float(a['cx']), float(a['cy'])), float(a['r'])
        if not drop_dots or seg_dist(c) >= g + r * 0.75:
            dots.append(el)
    return dict(line=lines + [SLASH], dot=dots)


def slashed1(src, lo=-30, hi=10):
    """Slash variant with a one-sided opening: strokes are removed in the band lo < sd < hi of the slash."""
    sd = lambda p: (p[0] - p[1]) / math.sqrt(2)
    keep = lambda p: not (lo < sd(p) < hi) or seg_dist(p) > 40 and not (48 <= (p[0] + p[1]) / 2 <= 208)
    lines = []
    for el in src.get('line', []) + src.get('detail', []):
        lines += gap(el, keep=keep)
    return dict(line=lines + [SLASH], dot=[e for e in src.get('dot', []) + src.get('dotcut', [])])


# ================================================================ transforms & badge helpers
def xf(el, s=1.0, deg=0.0, dx=0.0, dy=0.0, mirror=False, c=(128, 128)):
    """Mirror (about x=c.x), scale about c, rotate about c, then translate an element."""
    a = math.radians(deg)
    def M(p):
        x, y = p
        if mirror:
            x = 2 * c[0] - x
        x, y = c[0] + (x - c[0]) * s, c[1] + (y - c[1]) * s
        X = c[0] + (x - c[0]) * math.cos(a) - (y - c[1]) * math.sin(a)
        Y = c[1] + (x - c[0]) * math.sin(a) + (y - c[1]) * math.cos(a)
        return (X + dx, Y + dy)
    out = []
    for segs, closed in parse(el_d(el)):
        ss = []
        for sg in segs:
            if sg[0] == 'L':
                ss.append(('L', M(sg[1]), M(sg[2])))
            elif sg[0] == 'C':
                ss.append(('C',) + tuple(M(p) for p in sg[1:]))
            else:
                t1, t2 = sg[4], sg[5]
                if mirror:
                    t1, t2 = math.pi - t1, math.pi - t2
                ss.append(('A', M(sg[1]), sg[2] * s, sg[3] * s, t1 + a, t2 + a))
        out.append(f'M{pt(at(ss[0], 0))} ' + ' '.join(seg_cmd(x) for x in ss) + (' Z' if closed else ''))
    return P(' '.join(out))


def xd(dct, **kw):
    """Transform every element of a role dict (dots keep their radius, scaled)."""
    out = {}
    for role, els in dct.items():
        if role in ('dot', 'dotcut'):
            res = []
            for el in els:
                at_ = _attrs(el)
                p = (float(at_['cx']), float(at_['cy']))
                q = parse(el_d(xf(L(p[0], p[1], p[0] + 1, p[1]), **kw)))[0][0][0][1]
                res.append(C(q[0], q[1], float(at_['r']) * kw.get('s', 1)))
            out[role] = res
        else:
            out[role] = [xf(e, **kw) for e in els]
    return out


def samples(el, n=40):
    if el.startswith('<circle') and False:
        pass
    pts = []
    for segs, _ in parse(el_d(el)):
        for sg in segs:
            pts += [at(sg, j / n) for j in range(n + 1)]
    return pts


def dot_samples(el, off=8):
    a = _attrs(el)
    c, r = (float(a['cx']), float(a['cy'])), float(a['r']) * 0.75 - off
    if r <= 0.5:
        return [c]
    return [polar(c, r, k * 15) for k in range(24)]


def cut_area(els, c, r):
    if not els:
        return []
    res = _b.difference(_b.filled([el_d(e) for e in els]), _b.to_path([el_d(C(c[0], c[1], r))]))
    d = _b.to_d(res)
    return [P(d)] if d else []


def mark_pts(mk):
    pts = []
    for e in mk.get('line', []) + mk.get('detail', []):
        pts += samples(e)
    for e in mk.get('dot', []):
        pts += dot_samples(e)
    return pts


def badged(base, mk, B=(188, 184), rc=None, clear=30):
    """Open every base stroke around the badge at B; area minus circle; auto clearance radius."""
    mp = mark_pts(mk)
    bp = []
    for e in base.get('line', []) + base.get('detail', []):
        bp += samples(e, 120)
    if rc is None:
        rc = 46
        while rc < 90:
            kept = [p for p in bp if dist(p, B) >= rc]
            if not kept or min(dist(p, q) for p in kept for q in mp) >= clear:
                break
            rc += 1
    keep = lambda p: dist(p, B) >= rc
    out = dict(line=[], detail=[], area=[], hole=[], dot=[], dotcut=[])
    for role in ('line', 'detail'):
        for e in base.get(role, []):
            out[role] += gap(e, keep=keep)
    out['area'] = cut_area(base.get('area', []), B, rc)
    for role in ('dot', 'dotcut', 'hole'):
        for e in base.get(role, []):
            a = _attrs(e)
            if dist((float(a['cx']), float(a['cy'])), B) >= rc + float(a['r']):
                out[role].append(e)
    for role, els in mk.items():
        out[role] = out[role] + list(els)
    out['_rc'] = rc
    return out


def put(name, tags, d):
    d = {k: v for k, v in d.items() if not k.startswith('_')}
    icon(name, PE, tags, **d)


# ================================================================ bases
B = (188, 184)
UHEAD = C(104, 84, 40)
UBODY = 'M32 216 C32 172 64 148 104 148 C144 148 176 172 176 216'
UB = dict(line=[UHEAD, P(UBODY)], area=[UHEAD, P(UBODY + ' Z')])          # badge user (user-plus geometry)
USER = load('user')
UCIRC = load('user-circle')
USERS = load('users')

# ---------------------------------------------------------------- badge marks (centred on B)
MK = {}
MK['check'] = dict(line=[PL([(160, 186), (180, 206), (216, 166)])])
MK['plus'] = dict(line=[L(160, 184, 216, 184), L(188, 156, 188, 212)])
MK['minus'] = dict(line=[L(160, 184, 216, 184)])
MK['x'] = dict(line=[L(168, 164, 208, 204), L(208, 164, 168, 204)])
gear_d = ('M177.82 164.98 L178.51 153.49 L189.49 153.49 L190.18 164.98 A20 20 0 0 1 197.38 169.14 L207.68 163.99 '
          'L213.17 173.5 L203.56 179.84 A20 20 0 0 1 203.56 188.16 L213.17 194.5 L207.68 204.01 L197.38 198.86 '
          'A20 20 0 0 1 190.18 203.02 L189.49 214.51 L178.51 214.51 L177.82 203.02 A20 20 0 0 1 170.62 198.86 '
          'L160.32 204.01 L154.83 194.5 L164.44 188.16 A20 20 0 0 1 164.44 179.84 L154.83 173.5 L160.32 163.99 '
          'L170.62 169.14 A20 20 0 0 1 177.82 164.98 Z')
gear_el = xf(P(gear_d), dx=4)
MK['gear'] = dict(line=[gear_el], area=[gear_el], hole=[C(188, 184, 7)])
MK['warning'] = dict(line=[L(188, 152, 188, 184)], dot=[C(188, 216, 16)])
MK['question'] = dict(line=[xf(P('M166 164 A18 18 0 1 1 190 181 C185 184 184 187 184 192'), dx=4)], dot=[C(188, 216, 14)])
bolt = P('M194 150 L166 190 L188 190 L182 218 L210 178 L188 178 Z')
MK['lightning'] = dict(line=[bolt], area=[bolt])
MK['pause'] = dict(line=[L(172, 160, 172, 208), L(204, 160, 204, 208)])
MK['share'] = dict(line=[P('M160 212 V200 A24 24 0 0 1 184 176 H216'), PL([(196, 156), (216, 176), (196, 196)])])
star_b = xf(P('M184 153 L192.82 174.86 L216.34 176.49 L198.27 191.64 L203.98 214.51 L184 202 L164.02 214.51 '
              'L169.73 191.64 L151.66 176.49 L175.18 174.86 Z'), dx=4)
MK['star'] = dict(line=[star_b], area=[star_b])
heart_b = xf(P('M184 210.48 C184 210.48 151.36 192.8 151.36 171.72 A17 17 0 0 1 184 164.92 A17 17 0 0 1 216.64 171.72 '
               'C216.64 192.8 184 210.48 184 210.48 Z'), dx=4)
MK['heart'] = dict(line=[heart_b], area=[heart_b])
pin_b = xf(P('M193.87 153.27 L210.5 167.23 L202.14 172.36 L192.18 184.24 L190.91 207.46 L157.65 179.55 '
             'L180.3 174.27 L190.27 162.39 Z'), dx=4)
MK['push-pin'] = dict(line=[pin_b, xf(L(174.28, 193.51, 156.34, 214.89), dx=4)], area=[pin_b])
MK['dollar'] = dict(line=[P('M204 160 H184 A12 12 0 0 0 184 184 H192 A12 12 0 0 1 192 208 H172'),
                          L(188, 146, 188, 160), L(188, 208, 188, 222)])
MK['bitcoin'] = dict(line=[xf(P(d), dx=8) for d in ('M162 158 H186 A13 13 0 0 1 186 184 H170',
                                                     'M170 184 H189 A13 13 0 0 1 189 210 H162',
                                                     'M170 158 L170 210', 'M180 146 L180 158', 'M180 210 L180 222')])
MK['magnifier'] = dict(line=[C(182, 178, 18), L(196, 192, 214, 210)], area=[C(182, 178, 18)])
pen_b = PG([(163.37, 208.63), (184.59, 204.38), (212.87, 176.1), (195.9, 159.13), (167.62, 187.41)])
MK['pencil'] = dict(line=[pen_b], area=[pen_b])
lock_body = R(160, 182, 56, 40, 10)
MK['lock'] = dict(line=[lock_body, P('M172 182 V170 A16 16 0 0 1 204 170 V182')], area=[lock_body])
shield_b = P('M188 146 L218 158 V180 C218 204 204 216 188 222 C172 216 158 204 158 180 V158 Z')
MK['shield'] = dict(line=[shield_b], area=[shield_b])
mpin = P('M188 220 C188 220 160 196 160 174 A28 28 0 0 1 216 174 C216 196 188 220 188 220 Z')
MK['map-pin'] = dict(line=[mpin], area=[mpin], dotcut=[C(188, 174, 9)])
MK['music'] = dict(line=[L(190, 206, 190, 150), P('M190 150 C206 154 216 162 214 178')], dot=[C(178, 206, 18)])
crown_b = PG([(158, 210), (152, 160), (174, 180), (188, 150), (202, 180), (224, 160), (218, 210)])
MK['crown'] = dict(line=[crown_b], area=[crown_b])
MK['prohibit'] = dict(line=[C(188, 184, 28)], detail=[L(168.2, 164.2, 207.8, 203.8)], area=[C(188, 184, 28)])
MK['arrow-down'] = dict(line=[L(188, 150, 188, 214), PL([(164, 190), (188, 214), (212, 190)])])
MK['arrow-up'] = dict(line=[L(188, 214, 188, 150), PL([(164, 174), (188, 150), (212, 174)])])

RCS = {}
def ub(name, tags, mk, base=UB, B_=B, **kw):
    d = badged(base, MK[mk] if isinstance(mk, str) else mk, B=B_, **kw)
    RCS[name] = d['_rc']
    put(name, tags, d)
    return d

# ================================================================ user + badge
ub('user-arrow-down', ['download user', 'import contact', 'person', 'arrow', 'download'], 'arrow-down')
ub('user-arrow-up', ['upload user', 'export contact', 'person', 'arrow', 'upload'], 'arrow-up')
ub('user-bitcoin', ['user', 'bitcoin', 'crypto'], 'bitcoin')
ub('user-crown', ['admin', 'owner', 'vip'], 'crown')
ub('user-currency-dollar', ['user', 'dollar', 'price', 'money'], 'dollar')
ub('user-gear', ['admin', 'user settings', 'account settings', 'manage', 'manage account'], 'gear')
UHEART = ub('user-heart', ['favourite person', 'friend', 'care', 'user', 'love'], 'heart')
ub('user-lightning', ['user', 'fast', 'power', 'instant'], 'lightning')
ub('user-lock', ['privacy', 'private profile', 'lock', 'person', 'private'], 'lock')
ub('user-magnifying-glass', ['find user', 'search people', 'lookup', 'user', 'find people'], 'magnifier')
ub('user-map-pin', ['user location', 'person', 'map pin', 'where'], 'map-pin')
ub('user-music', ['artist', 'musician', 'singer', 'user'], 'music')
ub('user-pause', ['user', 'paused', 'hold'], 'pause')
ub('user-pencil', ['edit profile', 'edit user', 'account', 'user'], 'pencil')
ub('user-prohibit', ['block user', 'banned', 'forbidden', 'person'], 'prohibit')
ub('user-push-pin', ['user', 'pin', 'pinned'], 'push-pin')
ub('user-question', ['unknown user', 'anonymous', 'guest', 'person'], 'question')
ub('user-share', ['user', 'share', 'send'], 'share')
ub('user-shield', ['protected user', 'security', 'admin', 'person', 'user security'], 'shield')
ub('user-star', ['favourite user', 'vip', 'person', 'star'], 'star')
ub('user-warning', ['user alert', 'account warning', 'person', 'warning', 'alert'], 'warning')
ub('user-x', ['remove user', 'block', 'delete account', 'cancel user', 'user'], 'x')

# ================================================================ user-circle + badge
UB2 = (184, 184)
def shift(mk, dx, dy):
    return xd(mk, dx=dx, dy=dy)
ub('user-circle-check', ['verified user', 'approved', 'member'], shift(MK['check'], -4, 0), base=UCIRC, B_=UB2)
ub('user-circle-gear', ['account settings', 'profile settings', 'preferences'], shift(MK['gear'], -4, 0), base=UCIRC, B_=UB2)
ub('user-circle-minus', ['remove user', 'unfollow', 'leave'], shift(MK['minus'], -4, 0), base=UCIRC, B_=UB2)
ub('user-circle-plus', ['add user', 'follow', 'invite'], shift(MK['plus'], -4, 0), base=UCIRC, B_=UB2)

# ================================================================ users + badge
ub('users-minus', ['remove group member', 'group', 'users', 'minus', 'remove members'], 'minus', base=USERS)
ub('users-plus', ['add group member', 'invite', 'group', 'users', 'add members'], 'plus', base=USERS)

# ================================================================ slash variants
put('thumbs-up-slash', ['thumbs up', 'off', 'disabled', 'hidden', 'thumbs'], slashed(load('thumbs-up')))
put('thumbs-down-slash', ['thumbs down', 'off', 'disabled', 'hidden', 'thumbs'], slashed(load('thumbs-down')))
put('user-slash', ['no account', 'user off', 'blocked', 'disabled user', 'person'], slashed1(USER))
put('users-slash', ['group off', 'no users', 'disabled', 'group'], slashed1(USERS))
put('user-circle-slash', ['account off', 'no user', 'disabled', 'user'], slashed1(UCIRC))
put('user-heart-slash', ['empathy', 'care', 'disabled'],
    slashed1({k: v for k, v in xd({k: v for k, v in UHEART.items() if not k.startswith('_')}, mirror=True).items()}))


# ================================================================ people & figures
# ---------------------------------------------------------------- person-walking
pw = dict(line=[C(144, 52, 24), L(134, 98, 116, 152),
                PL([(132, 108), (102, 126), (86, 152)]), PL([(132, 108), (156, 134), (184, 138)]),
                PL([(116, 152), (94, 184), (70, 216)]), PL([(116, 152), (146, 180), (154, 216)])],
          area=[C(144, 52, 24)])
put('person-walking', ['walking', 'pedestrian', 'walk', 'person', 'directions'], xd(pw, dy=6))

# ---------------------------------------------------------------- rattle
rc_ = (152, 96)
u_ = (-math.sqrt(0.5), math.sqrt(0.5))
ring_c = (rc_[0] + u_[0] * 130, rc_[1] + u_[1] * 130)
h0 = polar(rc_, 64, 135)
h1 = (rc_[0] + u_[0] * 108, rc_[1] + u_[1] * 108)
icon('rattle', PE, ['rattle', 'baby toy', 'infant', 'toy'],
     line=[C(rc_[0], rc_[1], 64), L(h0[0], h0[1], h1[0], h1[1]), C(ring_c[0], ring_c[1], 22)],
     dotcut=[C(127, 71, 12), C(152, 96, 12), C(177, 121, 12)],
     area=[C(rc_[0], rc_[1], 64), C(ring_c[0], ring_c[1], 22)], hole=[C(ring_c[0], ring_c[1], 13)])

# ---------------------------------------------------------------- rocking-horse
horse = PG([(196, 112), (118, 112), (110, 56), (64, 64), (56, 96), (78, 100), (74, 152), (196, 152)])
rocker = 'M32 184 Q128 232 224 184'
def rock_y(x):
    t = (x - 32) / 192
    return 184 + 96 * t * (1 - t)
icon('rocking-horse', PE, ['rocking horse', 'toy', 'child', 'nursery', 'kids'],
     line=[horse, P('M32 184 C96 216 160 216 224 184'), L(92, 152, 92, rock_y(92) - 2), L(176, 152, 176, rock_y(176) - 2),
           PL([(196, 116), (216, 144)])],
     area=[horse], dotcut=[C(92, 78, 9)])

# sign-language: dropped (two hands could not be drawn legibly at 16px within the stroke rules).

# ---------------------------------------------------------------- sippy-cup
lid = R(64, 80, 128, 32, 12)
cup_b = 'M76 112 L86 202 A14 14 0 0 0 100 214 H156 A14 14 0 0 0 170 202 L180 112'
spout = 'M104 80 L110 48 A8 8 0 0 1 118 40 H138 A8 8 0 0 1 146 48 L152 80'
icon('sippy-cup', PE, ['sippy cup', 'toddler', 'baby', 'drink'],
     line=[lid, P(cup_b), P(spout), P('M79 128 H60 A16 16 0 0 0 44 144 V160 A16 16 0 0 0 60 176 H84'),
           P('M177 128 H196 A16 16 0 0 1 212 144 V160 A16 16 0 0 1 196 176 H172')],
     area=[lid, P(cup_b + ' Z'), P(spout + ' Z')])

# ---------------------------------------------------------------- thief
hc = (128, 88); hr = 44
ya, yb = 68, 108
xa = math.sqrt(hr * hr - (hc[1] - ya) ** 2); xb_ = math.sqrt(hr * hr - (yb - hc[1]) ** 2)
mask = P('M64 74 C64 70 68 68 72 68 H184 C188 68 192 70 192 74 L186 100 C185 105 182 108 176 108 H148 '
         'C140 108 136 100 128 100 C120 100 116 108 108 108 H80 C74 108 71 105 70 100 Z')
icon('thief', PE, ['criminal', 'burglar', 'masked', 'robber'],
     line=[P(f'M{f(hc[0] - xa)} {ya} A{hr} {hr} 0 0 1 {f(hc[0] + xa)} {ya}'),
           P(f'M{f(hc[0] - xb_)} {yb} A{hr} {hr} 0 0 0 {f(hc[0] + xb_)} {yb}'),
           mask, P('M48 216 C48 168 84 148 128 148 C172 148 208 168 208 216')],
     area=[C(hc[0], hc[1], hr), mask, P('M48 216 C48 168 84 148 128 148 C172 148 208 168 208 216 Z')],
     dotcut=[C(104, 86, 11), C(152, 86, 11)])

# ---------------------------------------------------------------- user-tie
tie = P('M120 166 H136 L133 178 L142 198 L128 212 L114 198 L123 178 Z')
icon('user-tie', PE, ['business person', 'professional', 'manager', 'tie'],
     line=USER['line'], area=USER['area'], detail=[tie])

# ---------------------------------------------------------------- user-child
achild = 'M32 216 C32 172 60 152 92 152 C112 152 128 157 140 166'
cbody = 'M140 216 C140 196 160 184 184 184 C208 184 224 196 224 216'
icon('user-child', PE, ['child account', 'kid', 'family', 'user'],
     line=[C(92, 84, 40), P(achild), C(184, 136, 24), P(cbody)],
     area=[C(92, 84, 40), P(achild + ' L132 216 Z'), C(184, 136, 24), P(cbody + ' Z')])

# ---------------------------------------------------------------- user-circle-dashed
dashes = []
n_d = 12
for k in range(n_d):
    a0 = -90 + k * 360 / n_d + 7; a1 = a0 + 360 / n_d - 14
    p, q = polar((128, 128), 96, a0), polar((128, 128), 96, a1)
    dashes.append(P(f'M{pt(p)} A96 96 0 0 1 {pt(q)}'))
icon('user-circle-dashed', PE, ['guest', 'placeholder user', 'anonymous'],
     line=dashes + UCIRC['line'][1:], area=UCIRC['area'])

# ---------------------------------------------------------------- user-focus / user-scan
bust_h = C(128, 100, 28)
bust_b = 'M76 180 C76 156 100 144 128 144 C156 144 180 156 180 180'
icon('user-focus', PE, ['face detection', 'portrait mode', 'focus user', 'frame person', 'focus'],
     line=load('focus')['line'][:4] + [bust_h, P(bust_b)], area=[bust_h, P(bust_b + ' Z')])
icon('user-scan', PE, ['person scan', 'body scan', 'face scan', 'recognition', 'person'],
     line=load('scan')['line'][:4] + [bust_h, P('M76 172 C76 152 100 144 128 144 C156 144 180 152 180 172'),
                                       L(56, 172, 200, 172)],
     area=[bust_h, P('M76 172 C76 152 100 144 128 144 C156 144 180 152 180 172 Z')])

# ---------------------------------------------------------------- user-headset
hh = (128, 104)
band = P(f'M60 104 A68 68 0 0 1 196 104')
hbody = 'M56 220 C56 194 88 180 128 180 C168 180 200 194 200 220'
icon('user-headset', PE, ['customer support', 'agent', 'help desk', 'service', 'customer service'],
     line=[C(128, 104, 36), band, R(48, 96, 24, 48, 12), R(184, 96, 24, 48, 12),
           P('M196 144 C196 156 188 162 172 164'), P(hbody)],
     area=[C(128, 104, 36), R(48, 96, 24, 48, 12), R(184, 96, 24, 48, 12), P(hbody + ' Z')])

# ---------------------------------------------------------------- user-list
icon('user-list', PE, ['contacts list', 'members', 'user', 'lines'],
     line=[C(88, 96, 36), P('M32 216 C32 180 56 160 88 160 C120 160 144 180 144 216'),
           L(176, 72, 224, 72), L(176, 120, 224, 120), L(184, 168, 224, 168)],
     area=[C(88, 96, 36), P('M32 216 C32 180 56 160 88 160 C120 160 144 180 144 216 Z')])

# ---------------------------------------------------------------- user-monitor
icon('user-monitor', PE, ['screen user', 'remote work', 'presenter', 'computer'],
     line=[R(32, 40, 192, 136, 14), L(128, 176, 128, 208), L(88, 208, 168, 208)],
     detail=[P('M88 176 C88 156 104 144 128 144 C152 144 168 156 168 176')],
     area=[R(32, 40, 192, 136, 14)], dotcut=[C(128, 100, 22)])

# ---------------------------------------------------------------- user-sound
sh = (96, 92)
waves = [P(f'M{pt(polar(sh, rr, a0))} A{rr} {rr} 0 0 1 {pt(polar(sh, rr, a1))}') for rr, a0, a1 in ((76, -40, 34), (114, -30, 26))]
sbody = 'M32 216 C32 176 60 156 96 156 C132 156 160 176 160 216'
icon('user-sound', PE, ['speaker', 'voice', 'talking', 'person', 'speaking'],
     line=[C(96, 92, 40), P(sbody)] + waves, area=[C(96, 92, 40), P(sbody + ' Z')])

# ---------------------------------------------------------------- user-switch
def mini(cx, hy, by):
    head = C(cx, hy, 20)
    body = f'M{cx - 36} {by + 24} C{cx - 36} {by + 8} {cx - 20} {by} {cx} {by} C{cx + 20} {by} {cx + 36} {by + 8} {cx + 36} {by + 24}'
    return head, body
ah = C(80, 68, 24); abody = 'M48 136 C48 118 62 108 80 108 C98 108 112 118 112 136'
bh = C(176, 148, 24); bbody = 'M144 216 C144 198 158 188 176 188 C194 188 208 198 208 216'
icon('user-switch', PE, ['switch account', 'change user', 'swap', 'swap profile', 'user'],
     line=[ah, P(abody), bh, P(bbody),
           P('M148 40 A52 52 0 0 1 200 92'), PL([(184, 76), (200, 92), (216, 76)]),
           P('M108 216 A52 52 0 0 1 56 164'), PL([(40, 180), (56, 164), (72, 180)])],
     area=[ah, P(abody + ' Z'), bh, P(bbody + ' Z')])

# ---------------------------------------------------------------- users-three
mh = C(128, 96, 32)
mbody = 'M68 208 C68 172 92 156 128 156 C164 156 188 172 188 208'
icon('users-three', PE, ['team', 'community', 'group', 'people', 'three people'],
     line=[mh, P(mbody),
           P(f'M{pt(polar((188, 84), 26, -130))} A26 26 0 1 1 {pt(polar((188, 84), 26, 110))}'),
           P('M204 136 C216 142 224 160 224 184'),
           P(f'M{pt(polar((68, 84), 26, -50))} A26 26 0 1 0 {pt(polar((68, 84), 26, 70))}'),
           P('M52 136 C40 142 32 160 32 184')],
     area=[mh, P(mbody + ' Z')])

# ---------------------------------------------------------------- users-four
f4 = []
f4a = []
for cx in (76, 180):
    for hy, by in ((52, 92), (148, 188)):
        h_, b_ = mini(cx, hy, by)
        f4 += [h_, P(b_)]; f4a += [h_, P(b_ + ' Z')]
icon('users-four', PE, ['team', 'group', 'four people'], line=f4, area=f4a)

print(save(overwrite=True))
