import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Communication'
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


def seg_circle_ts(a, b, c, r):
    dx, dy = b[0] - a[0], b[1] - a[1]
    fx, fy = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dy * dy; Bq = 2 * (fx * dx + fy * dy); Cq = fx * fx + fy * fy - r * r
    disc = Bq * Bq - 4 * A * Cq
    if disc <= 0:
        return []
    sq = math.sqrt(disc)
    return sorted(t for t in ((-Bq - sq) / (2 * A), (-Bq + sq) / (2 * A)) if 0 < t < 1)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def clip_polyline(pts, c, r):
    """Parts of an open polyline outside circle (c, r), as point lists."""
    out, cur = [], []
    inside = lambda p: dist(p, c) < r
    if not inside(pts[0]):
        cur = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        for t in seg_circle_ts(a, b, c, r):
            p = lerp(a, b, t)
            if cur:
                cur.append(p); out.append(cur); cur = []
            else:
                cur = [p]
        if not inside(b) and cur:
            cur.append(b)
    if len(cur) > 1:
        out.append(cur)
    return [PL(s) for s in out if len(s) > 1 and dist(s[0], s[-1]) > 4]


def poly_cut(pts, c, r):
    """Closed polygon with circle (c, r) bitten out. Returns (line paths, area path)."""
    n = len(pts)
    inside = lambda p: dist(p, c) < r
    seq = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if not inside(a):
            seq.append((a, 'v'))
        for t in seg_circle_ts(a, b, c, r):
            p = lerp(a, b, t)
            seq.append((p, 'exit' if inside(lerp(a, b, t + 1e-4)) else 'enter'))
    # 'exit' here means the boundary walks INTO the circle (visible part ends)
    k = next(i for i, s in enumerate(seq) if s[1] == 'enter')
    seq = seq[k:] + seq[:k]
    lines, cur = [], []
    cen = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    for p, kind in seq:
        if kind == 'enter':
            cur = [p]
        else:
            cur.append(p)
        if kind == 'exit':
            lines.append(cur)
    # area: walk visible runs joined by arcs bulging toward the polygon centroid
    d = ''
    for j, run in enumerate(lines):
        d += (f'M{pt(run[0])}' if j == 0 else '') + ''.join(f' L{pt(q)}' for q in run[1:])
        nxt = lines[(j + 1) % len(lines)][0]
        d += ' ' + arc_to(c, r, run[-1], nxt, lambda m: -dist(m, cen))
    return [PL(s) for s in lines], P(d + ' Z')


# ----------------------------------------------------------------------- envelope (from envelope.svg)
EX0, EY0, EX1, EY1, ER = 32, 56, 224, 200, 14
FLAP = [(48, 76), (128, 140), (208, 76)]
ENV = R(32, 56, 192, 144, 14)
ECEN = (128, 128)


def env_cut(B, rc, corner='br'):
    if corner == 'br':
        yr = B[1] - math.sqrt(rc * rc - (EX1 - B[0]) ** 2)
        xb = B[0] - math.sqrt(rc * rc - (EY1 - B[1]) ** 2)
        o = (f'M{f(EX1)} {f(yr)} V{EY0 + ER} A{ER} {ER} 0 0 0 {EX1 - ER} {EY0} H{EX0 + ER} '
             f'A{ER} {ER} 0 0 0 {EX0} {EY0 + ER} V{EY1 - ER} A{ER} {ER} 0 0 0 {EX0 + ER} {EY1} H{f(xb)}')
        a = o + ' ' + arc_to(B, rc, (xb, EY1), (EX1, yr), lambda m: -dist(m, ECEN)) + ' Z'
    else:  # top-right
        xt = B[0] - math.sqrt(rc * rc - (B[1] - EY0) ** 2)
        yr = B[1] + math.sqrt(rc * rc - (EX1 - B[0]) ** 2)
        o = (f'M{f(xt)} {EY0} H{EX0 + ER} A{ER} {ER} 0 0 0 {EX0} {EY0 + ER} V{EY1 - ER} '
             f'A{ER} {ER} 0 0 0 {EX0 + ER} {EY1} H{EX1 - ER} A{ER} {ER} 0 0 0 {EX1} {EY1 - ER} V{f(yr)}')
        a = o + ' ' + arc_to(B, rc, (EX1, yr), (xt, EY0), lambda m: -dist(m, ECEN)) + ' Z'
    return P(o), P(a)


def env_badge(name, tags, marks, rc, B=(184, 184), mark_area=(), mark_detail=(), mark_dot=(), mark_dotcut=(),
              corner='br', flap_rc=None):
    ln, ar = env_cut(B, rc, corner)
    flap = clip_polyline(FLAP, B, flap_rc or rc)
    icon(name, CAT, tags, line=[ln] + list(marks), detail=flap + list(mark_detail), area=[ar] + list(mark_area),
         dot=list(mark_dot), dotcut=list(mark_dotcut))


def arrowhead(tip, back_dir_deg, size=24, spread=45):
    a = polar(tip, size * math.sqrt(2), back_dir_deg - spread)
    b = polar(tip, size * math.sqrt(2), back_dir_deg + spread)
    return PL([a, tip, b])


# ---- marks
def bolt(c, s=1.0):
    pts = [(10, -36), (-20, 4), (4, 4), (-8, 36), (22, -6), (-2, -6)]
    return [(c[0] + x * s, c[1] + y * s) for x, y in pts]


def lock_mark(c):
    body = R(c[0] - 28, c[1] - 4, 56, 40, 10)
    shackle = P(f'M{f(c[0] - 16)} {f(c[1] - 4)} V{f(c[1] - 16)} A16 16 0 0 1 {f(c[0] + 16)} {f(c[1] - 16)} V{f(c[1] - 4)}')
    return body, shackle


def star_pts(c, ro, ri):
    return [polar(c, ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]


SPARK = 'M128 32 C136 96 160 120 224 128 C160 136 136 160 128 224 C120 160 96 136 32 128 C96 120 120 96 128 32 Z'


def stamp_path(x0, y0, x1, y1, nx, ny, r):
    """Rectangle with semicircular perforation bites along every edge (clockwise)."""
    cen = ((x0 + x1) / 2, (y0 + y1) / 2)
    near = lambda m: -dist(m, cen)
    d = f'M{f(x0)} {f(y0)}'
    edges = [((x0, y0), (x1, y0), nx), ((x1, y0), (x1, y1), ny), ((x1, y1), (x0, y1), nx), ((x0, y1), (x0, y0), ny)]
    for a, b, n in edges:
        ln = dist(a, b); u = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        for i in range(n):
            t = ln * (i + 0.5) / n
            m = (a[0] + u[0] * t, a[1] + u[1] * t)
            p = (m[0] - u[0] * r, m[1] - u[1] * r); q = (m[0] + u[0] * r, m[1] + u[1] * r)
            d += f' L{pt(p)} ' + arc_to(m, r, p, q, near)
        d += f' L{pt(b)}'
    return d + ' Z'


B = (184, 184)
env_badge('envelope-lightning', ['envelope', 'fast', 'power', 'mail', 'email'],
          [PG(bolt(B))], 64, mark_area=[PG(bolt(B))])
lb, ls = lock_mark((184, 186))
env_badge('envelope-lock', ['secure mail', 'encrypted email', 'private', 'lock', 'encrypted'],
          [lb, ls], 66, mark_area=[lb])
env_badge('envelope-magnifying-glass', ['review mail', 'search mail', 'envelope', 'email', 'find email'],
          [C(176, 176, 22), L(192, 192, 212, 212)], 64, mark_area=[C(176, 176, 22)])
env_badge('envelope-minus', ['mail', 'remove', 'minus', 'envelope', 'remove mail'], [L(156, 184, 212, 184)], 60)
env_badge('envelope-outgoing', ['sent mail', 'outbox', 'outgoing', 'outgoing mail', 'send email'],
          [L(160, 208, 208, 160), PL([(176, 160), (208, 160), (208, 192)])], 62)

# paperclip: three legs, rotated to lean right
def paperclip(c, deg, sp=28, top=-20, bot=24, inner_top=-6, left_end=26):
    r1, r2 = sp, sp / 2
    d = (f'M0 {inner_top} V{bot} A{r2} {r2} 0 0 0 {sp} {bot} V{top} A{r1} {r1} 0 0 0 {-sp} {top} V{left_end}')
    a = math.radians(deg)
    fn = lambda p: (c[0] + p[0] * math.cos(a) - p[1] * math.sin(a), c[1] + p[0] * math.sin(a) + p[1] * math.cos(a))
    return P(tf_path(d.replace('V', ' V '), fn))


env_badge('envelope-paperclip', ['attachment', 'email attachment', 'mail', 'clip', 'envelope'],
          [paperclip((178, 178), 45, sp=26, top=-18, bot=22, inner_top=-6, left_end=24)], 72)
env_badge('envelope-pause', ['envelope', 'paused', 'hold', 'mail', 'email'],
          [L(168, 162, 168, 206), L(200, 162, 200, 206)], 62)
u = (math.sqrt(.5), -math.sqrt(.5)); nn = (math.sqrt(.5), math.sqrt(.5))
T = (152, 216); Ep = (210, 158); hw = 16
mv = lambda p, v, k: (p[0] + v[0] * k, p[1] + v[1] * k)
nb = mv(T, u, 22)
pencil = [T, mv(nb, nn, hw), mv(Ep, nn, hw), mv(Ep, nn, -hw), mv(nb, nn, -hw)]
env_badge('envelope-pencil', ['compose', 'write email', 'edit', 'envelope'], [PG(pencil)], 70, B=(180, 186),
          mark_area=[PG(pencil)])
env_badge('envelope-plus', ['new email', 'add', 'envelope', 'plus'], [L(156, 184, 212, 184), L(184, 156, 184, 212)], 60)
env_badge('envelope-prohibit', ['blocked mail', 'spam', 'envelope', 'denied'],
          [C(184, 184, 32), L(*polar(B, 32, -135), *polar(B, 32, 45))], 66)
pin_body = [(172, 150), (196, 150), (196, 170), (208, 190), (160, 190), (172, 170)]
env_badge('envelope-push-pin', ['envelope', 'pinned', 'pin', 'mail', 'email'],
          [PG(pin_body), L(164, 150, 204, 150), L(184, 190, 184, 218)], 66, mark_area=[PG(pin_body)])
env_badge('envelope-question', ['mail help', 'unknown', 'envelope', 'question'],
          [P('M168 160 A18 18 0 1 1 196 175 C190 179 186 183 186 190')], 64, mark_dot=[C(186, 212, 16)])
env_badge('envelope-reply', ['reply', 'mail', 'respond', 'envelope'],
          [P('M212 216 V196 A24 24 0 0 0 188 172 H156'), PL([(176, 152), (156, 172), (176, 192)])], 66)
env_badge('envelope-send', ['send mail', 'outgoing', 'envelope', 'arrow'],
          [L(152, 184, 216, 184), PL([(192, 160), (216, 184), (192, 208)])], 62)
icon('envelope-slash', CAT, ['mail off', 'no email', 'unsubscribe', 'mute', 'blocked'],
     line=[ENV, PL(FLAP), L(40, 40, 216, 216)])
spk = tf_path(SPARK, scaler((128, 128), B, 0.36), 0.36)
env_badge('envelope-sparkle', ['envelope', 'ai', 'magic', 'mail', 'email'], [P(spk)], 64, mark_area=[P(spk)])
st = stamp_path(156, 152, 212, 216, 2, 2, 8)
env_badge('envelope-stamp', ['envelope', 'postage', 'stamp', 'mail', 'email'], [P(st)], 66, mark_area=[P(st)])
sp_ = star_pts((184, 188), 36, 16)
env_badge('envelope-star', ['starred mail', 'important', 'envelope', 'favourite'], [PG(sp_)], 64, mark_area=[PG(sp_)])
env_badge('envelope-unread', ['unread mail', 'new email', 'mark unread', 'notification', 'unread'],
          [], 56, mark_dot=[C(186, 186, 32)])
env_badge('envelope-warning', ['mail error', 'undelivered', 'envelope', 'email', 'important'],
          [L(184, 144, 184, 172)], 64, mark_dot=[C(184, 208, 16)])
env_badge('envelope-x', ['mail', 'delete', 'error', 'envelope', 'delete mail'],
          [L(162, 162, 206, 206), L(206, 162, 162, 206)], 60)

# envelopes: front envelope plus the top/left edges of one behind it
front = R(64, 100, 160, 120, 12)
icon('envelopes', CAT, ['emails', 'mail', 'multiple', 'inbox'],
     line=[front, P('M32 172 V74 A14 14 0 0 1 46 60 H190')],
     detail=[PL([(80, 118), (144, 166), (208, 118)])], area=[front])

# ----------------------------------------------------------------------- mailbox
MB = 'M32 176 V136 A40 40 0 0 1 72 96 H208 A16 16 0 0 1 224 112 V176 Z'
MB_DOOR = P('M72 96 A40 40 0 0 1 112 136 V176')
FLAG = PG([(176, 40), (216, 40), (216, 68), (176, 68)])
icon('mailbox', CAT, ['mailbox', 'letterbox', 'post', 'mail', 'delivery'],
     line=[P(MB), L(176, 68, 176, 96), FLAG, L(144, 176, 144, 224)], detail=[MB_DOOR], area=[P(MB), FLAG])
icon('mailbox-slash', CAT, ['mailbox', 'off', 'disabled', 'hidden'],
     line=[P(MB), MB_DOOR, L(176, 68, 176, 96), FLAG, L(144, 176, 144, 224), SLASH])

# ----------------------------------------------------------------------- newspaper
teeth = [(208, 196), (181.3, 220), (154.7, 196), (128, 220), (101.3, 196), (74.7, 220), (48, 196)]
clip = ('M48 48 A16 16 0 0 1 64 32 H192 A16 16 0 0 1 208 48 ' + ' '.join(f'L{pt(p)}' for p in teeth) + ' Z')
icon('newspaper-clipping', CAT, ['clipping', 'article', 'press'],
     line=[P(clip)], detail=[L(80, 72, 176, 72), L(80, 112, 176, 112), L(80, 152, 136, 152)], area=[P(clip)])
NEWS = 'M32 104 H64 V64 A16 16 0 0 1 80 48 H208 A16 16 0 0 1 224 64 V192 A16 16 0 0 1 208 208 H48 A16 16 0 0 1 32 192 Z'
icon('newspaper-slash', CAT, ['newspaper', 'off', 'disabled', 'hidden'],
     line=[P(NEWS), P('M64 104 V192 A16 16 0 0 1 48 208'), L(116, 88, 192, 88), L(154, 128, 192, 128),
           L(96, 168, 142, 168), SLASH])

# ----------------------------------------------------------------------- paper plane (from paper-plane.svg)
PLANE = [(224, 32), (32, 104), (112, 144), (152, 224)]
PS = 0.84
psc = scaler((32, 32), (32, 32), PS)
PLANE_S = [psc(p) for p in PLANE]
FOLD_S = [psc((112, 144)), psc((176, 80))]


def plane_badge(name, tags, marks, rc, Bp=(194, 194), mark_area=()):
    if any(seg_circle_ts(a, b, Bp, rc) for a, b in zip(PLANE_S, PLANE_S[1:] + PLANE_S[:1])):
        ln, ar = poly_cut(PLANE_S, Bp, rc)
    else:
        ln, ar = [PG(PLANE_S)], PG(PLANE_S)
    icon(name, CAT, tags, line=ln + list(marks), detail=clip_polyline(FOLD_S, Bp, rc), area=[ar] + list(mark_area))


Bp = (194, 194)
plane_badge('paper-plane-check', ['sent', 'delivered', 'send', 'check'], [PL([(170, 196), (188, 214), (220, 178)])], 52)
plane_badge('paper-plane-minus', ['send', 'remove', 'minus', 'paper plane'], [L(170, 194, 218, 194)], 52)
plane_badge('paper-plane-plus', ['send', 'add', 'new', 'paper plane'],
            [L(170, 194, 218, 194), L(194, 170, 194, 218)], 52)
icon('paper-plane-slash', CAT, ['unsent', 'send off', 'paper plane', 'slash'],
     line=[PG(PLANE), L(112, 144, 176, 80), SLASH])
plane_badge('paper-plane-warning', ['send failed', 'error', 'alert', 'paper plane'],
            [L(196, 160, 196, 184)], 52, mark_area=[])
ICONS[-1]['dot'] = [C(196, 212, 14)]
plane_badge('paper-plane-x', ['send cancelled', 'error', 'x', 'paper plane'],
            [L(174, 174, 214, 214), L(214, 174, 174, 214)], 52)

# ----------------------------------------------------------------------- phone (from phone.svg); marks sit in the free upper-right
PH = 'M64 40 H96 L112 92 L88 112 C108 132 124 148 144 168 L164 144 L216 160 V192 A24 24 0 0 1 192 216 C104 216 40 152 40 64 A24 24 0 0 1 64 40 Z'


def phone(name, tags, marks, mark_area=(), mark_dot=()):
    icon(name, CAT, tags, line=[P(PH)] + list(marks), area=[P(PH)] + list(mark_area), dot=list(mark_dot))


phone('phone-check', ['phone check', 'done', 'approved', 'phone', 'call'], [PL([(156, 74), (176, 94), (212, 54)])])
# hang-up: a horizontal handset with its ear and mouth pieces pointing down
hang = ('M32 148 C32 100 80 76 128 76 C176 76 224 100 224 148 L212 180 L170 170 L166 138 '
        'C142 128 114 128 90 138 L86 170 L44 180 Z')
icon('phone-disconnect', CAT, ['hang up', 'end call', 'disconnect', 'call end', 'phone'], line=[P(hang)], area=[P(hang)])
phone('phone-forward', ['call forward', 'redirect', 'phone', 'arrow'], [L(148, 72, 212, 72), PL([(188, 48), (212, 72), (188, 96)])])
phone('phone-list', ['call log', 'contacts', 'phone book'], [L(152, 44, 212, 44), L(152, 80, 212, 80), L(168, 116, 212, 116)])
lb2, ls2 = lock_mark((184, 76))
phone('phone-lock', ['locked phone', 'secure call', 'private', 'phone'], [lb2, ls2], mark_area=[lb2])
phone('phone-minus', ['phone', 'remove', 'call', 'minus', 'remove contact'], [L(160, 72, 208, 72)])
phone('phone-missed', ['missed call', 'phone', 'call', 'notification', 'unanswered'],
      [PL([(148, 48), (180, 80), (212, 48)]), PL([(188, 48), (212, 48), (212, 72)])])
phone('phone-pause', ['call on hold', 'hold', 'paused call', 'phone', 'hold call'], [L(168, 48, 168, 96), L(200, 48, 200, 96)])
phone('phone-plus', ['phone', 'add contact', 'call', 'plus', 'add call'], [L(160, 72, 208, 72), L(184, 48, 184, 96)])
# phone-slash: the handset itself runs top-left to bottom-right, parallel to the slash, so the slash
# variant mirrors the handset (same geometry) to let the slash cross it
PH_M = ('M192 40 H160 L144 92 L168 112 C148 132 132 148 112 168 L92 144 L40 160 V192 A24 24 0 0 0 64 216 '
        'C152 216 216 152 216 64 A24 24 0 0 0 192 40 Z')
icon('phone-slash', CAT, ['no calls', 'phone off', 'muted calls', 'phone disabled', 'calls off'],
     line=[P(PH_M), SLASH])
phone('phone-transfer', ['transfer call', 'forward call', 'redirect'],
      [L(152, 52, 212, 52), PL([(192, 32), (212, 52), (192, 72)]), L(212, 100, 152, 100), PL([(172, 80), (152, 100), (172, 120)])])
cam_b = R(144, 52, 44, 40, 8); cam_l = PG([(188, 64), (216, 50), (216, 94), (188, 80)])
phone('phone-video', ['video call', 'facetime', 'phone', 'camera'], [cam_b, cam_l], mark_area=[cam_b, cam_l])

# ----------------------------------------------------------------------- podcast
mc = (128, 104)
arcs = []
for rr in (56, 92):
    for a0, a1 in ((-40, 40), (140, 220)):
        arcs.append(P(f'M{pt(polar(mc, rr, a0))} A{rr} {rr} 0 0 1 {pt(polar(mc, rr, a1))}'))
head = R(108, 64, 40, 80, 20)
icon('podcast', CAT, ['podcast', 'broadcast', 'microphone', 'audio', 'audio show'],
     line=[head, L(128, 144, 128, 216), L(100, 216, 156, 216)] + arcs, area=[head])

# ----------------------------------------------------------------------- postage stamp
STAMP = stamp_path(48, 40, 208, 216, 4, 4, 10)
icon('postage-stamp', CAT, ['stamp', 'postage', 'mail', 'post'],
     line=[P(STAMP)], detail=[R(84, 76, 88, 104, 8)], area=[P(STAMP)])
HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'
hs = tf_path(HEART, scaler((128, 140), (128, 132), 0.42), 0.42)
icon('postage-stamp-heart', CAT, ['stamp', 'love', 'postage', 'mail'], line=[P(STAMP)], detail=[P(hs)], area=[P(STAMP)])

# ----------------------------------------------------------------------- postcard
hp = tf_path(HEART, scaler((128, 140), (84, 130), 0.27), 0.27)
icon('postcard', CAT, ['postcard', 'mail', 'card', 'greeting', 'travel'],
     line=[ENV], detail=[L(136, 88, 136, 168), P(hp), L(164, 112, 192, 112), L(164, 148, 192, 148)], area=[ENV])

# ----------------------------------------------------------------------- social network
SN = [(128, 64), (64, 180), (192, 180)]
def seg(a, b, ra, rb):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rb, b[1] - uy * rb)
sn_lines = [seg(SN[0], SN[1], 28, 28), seg(SN[0], SN[2], 28, 28), seg(SN[1], SN[2], 28, 28)]
icon('social-network', CAT, ['social', 'network', 'connections', 'nodes'],
     line=[C(*n, 28) for n in SN] + sn_lines, area=[C(*n, 28) for n in SN])
icon('social-network-slash', CAT, ['social network', 'off', 'disabled', 'hidden', 'social'],
     line=[C(*n, 28) for n in SN] + sn_lines + [SLASH])

# ----------------------------------------------------------------------- video people
vb = R(32, 72, 136, 112, 14); vl = P('M168 112 L224 84 L224 172 L168 144 Z')
icon('user-video', CAT, ['video call', 'webinar', 'person', 'camera'],
     line=[vb, vl], detail=[P('M64 184 C64 164 80 152 100 152 C120 152 136 164 136 184')],
     area=[vb, vl], dotcut=[C(100, 112, 20)])
scr = R(32, 32, 192, 160, 14)
faces, shoulders = [], []
for cx in (80, 176):
    for top, bot in ((40, 112), (112, 192)):
        faces.append(C(cx, top + 24, 13))
        shoulders.append(P(f'M{cx - 20} {bot} A20 20 0 0 1 {cx + 20} {bot}'))
icon('video-conference', CAT, ['video call', 'meeting', 'conference', 'webinar', 'people'],
     line=[scr, L(128, 192, 128, 216), L(92, 216, 164, 216)],
     detail=[L(128, 48, 128, 176), L(48, 112, 208, 112)] + shoulders, area=[scr], dotcut=faces)

print(save(overwrite=True))
