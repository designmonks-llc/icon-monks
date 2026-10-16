import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM = 'Communication'

# ================================================================ outline engine (same as batch 113, so badges match)
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def seg_point(s, t):
    if s[0] == 'L':
        return lerp(s[1], s[2], t)
    if s[0] == 'C':
        p0, c1, c2, p1 = s[1:]
        a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
        d, e = lerp(a, b, t), lerp(b, c, t)
        return lerp(d, e, t)
    c, r, a0, a1 = s[1:]
    a = a0 + (a1 - a0) * t
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def split_cubic(p0, c1, c2, p1, t):
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p1)


def seg_sub(s, t0, t1):
    if s[0] == 'L':
        return ('L', lerp(s[1], s[2], t0), lerp(s[1], s[2], t1))
    if s[0] == 'C':
        _, right = split_cubic(*s[1:], t0)
        if t1 >= 1:
            return ('C',) + right
        left, _ = split_cubic(*right, (t1 - t0) / (1 - t0))
        return ('C',) + left
    c, r, a0, a1 = s[1:]
    return ('A', c, r, a0 + (a1 - a0) * t0, a0 + (a1 - a0) * t1)


def seg_end(s):
    return seg_point(s, 1)


def seg_cmd(s):
    if s[0] == 'L':
        return f'L{pt(s[2])}'
    if s[0] == 'C':
        return f'C{pt(s[2])} {pt(s[3])} {pt(s[4])}'
    c, r, a0, a1 = s[1:]
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(seg_end(s))}'


def segs_d(segs, close=False):
    d = f'M{pt(seg_point(segs[0], 0))} ' + ' '.join(seg_cmd(s) for s in segs)
    return d + (' Z' if close else '')


def trim(segs, keep, closed=True, steps=240):
    """Split an outline into runs of segments where keep(point) holds."""
    pieces = []  # (seg index, t0, t1)
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


def ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])




# ================================================================ bases (exact geometry of the existing icons)
CHAT = [('L', (80, 200), (40, 224)), ('L', (40, 224), (40, 72)),
        ('A', (56, 72), 16, math.pi, 1.5 * math.pi), ('L', (56, 56), (200, 56)),
        ('A', (200, 72), 16, 1.5 * math.pi, 2 * math.pi), ('L', (216, 72), (216, 184)),
        ('A', (200, 184), 16, 0, 0.5 * math.pi), ('L', (200, 200), (80, 200))]
CHAT_D = load('chat')['line'][0]
CHATS = load('chats')

CC_C, CC_R = (132, 124), 92  # chat-circle
CHATC_D = load('chat-circle')['line'][0]

H = math.pi / 2
ENV = [('L', (32, 186), (32, 70)), ('A', (46, 70), 14, 2 * H, 3 * H), ('L', (46, 56), (210, 56)),
       ('A', (210, 70), 14, 3 * H, 4 * H), ('L', (224, 70), (224, 186)), ('A', (210, 186), 14, 0, H),
       ('L', (210, 200), (46, 200)), ('A', (46, 186), 14, H, 2 * H)]
ENV_D = load('envelope')['line'][0]
ENV_FLAP = load('envelope')['detail']

B = (184, 184)
BX, BY = B
SLASH = L(48, 48, 208, 208)


def T(pts, dx=BX, dy=BY):
    return [(x + dx, y + dy) for x, y in pts]


def heart_path(c, s):
    def q(x, y):
        return pt((c[0] + (x - 128) * s, c[1] + (y - 140) * s))
    r = f(50 * s)
    return (f'M{q(128, 212)} C{q(128, 212)} {q(32, 160)} {q(32, 98)} A{r} {r} 0 0 1 {q(128, 78)} '
            f'A{r} {r} 0 0 1 {q(224, 98)} C{q(224, 160)} {q(128, 212)} {q(128, 212)} Z')


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


def badge(kind):
    """Small mark around B. Returns (roles, clearance radius). Marks shared with batch 113 are identical."""
    b = dict(line=[], area=[], hole=[], dot=[], detail=[])
    cr = 56
    if kind == 'check':
        b['line'] = [PL(T([(-26, 2), (-8, 20), (26, -16)]))]
    elif kind == 'x':
        b['line'] = [L(BX - 20, BY - 20, BX + 20, BY + 20), L(BX + 20, BY - 20, BX - 20, BY + 20)]
        cr = 54
    elif kind == 'plus':
        b['line'] = [L(BX, BY - 26, BX, BY + 26), L(BX - 26, BY, BX + 26, BY)]
    elif kind == 'minus':
        b['line'] = [L(BX - 26, BY, BX + 26, BY)]
        cr = 50
    elif kind == 'arrow-down':
        b['line'] = [L(BX, BY - 28, BX, BY + 28), PL(T([(-20, 8), (0, 28), (20, 8)]))]
    elif kind == 'arrow-up':
        b['line'] = [L(BX, BY + 28, BX, BY - 28), PL(T([(-20, -8), (0, -28), (20, -8)]))]
    elif kind == 'arrow-right':
        b['line'] = [L(BX - 28, BY, BX + 28, BY), PL(T([(8, -20), (28, 0), (8, 20)]))]
    elif kind == 'arrow-down-left':
        b['line'] = [L(BX + 22, BY - 22, BX - 22, BY + 22), PL(T([(-22, -6), (-22, 22), (6, 22)]))]
        cr = 58
    elif kind == 'arrow-clockwise':
        r_ = 26
        e_ = polar(B, r_, -45)
        b['line'] = [P(f'M{pt(polar(B, r_, 0))} A{r_} {r_} 0 1 1 {pt(e_)}'),
                     PL([(e_[0] - 20, e_[1]), e_, (e_[0], e_[1] - 20)])]
        cr = 62
    elif kind == 'code':
        b['line'] = [PL(T([(-14, -20), (-34, 0), (-14, 20)])), PL(T([(14, -20), (34, 0), (14, 20)]))]
        cr = 60
    elif kind == 'dollar':
        b['line'] = [P(f'M{BX + 16} {BY - 24} H{BX - 4} A12 12 0 0 0 {BX - 4} {BY} '
                       f'H{BX + 4} A12 12 0 0 1 {BX + 4} {BY + 24} H{BX - 16}'),
                     L(BX, BY - 38, BX, BY - 24), L(BX, BY + 24, BX, BY + 38)]
        cr = 60
    elif kind == 'bitcoin':
        x0 = BX - 14
        b['line'] = [P(f'M{x0 - 8} {BY - 26} H{BX + 2} A13 13 0 0 1 {BX + 2} {BY} H{x0}'),
                     P(f'M{x0} {BY} H{BX + 5} A13 13 0 0 1 {BX + 5} {BY + 26} H{x0 - 8}'),
                     L(x0, BY - 26, x0, BY + 26),
                     L(BX - 4, BY - 38, BX - 4, BY - 26), L(BX - 4, BY + 26, BX - 4, BY + 38)]
        cr = 62
    elif kind == 'at':
        ro = 40
        b['dot'] = [C(BX, BY, 15)]
        b['line'] = [P(f'M{BX + 17} {BY - 8} V{BY + 4} A11.5 11.5 0 0 0 {BX + ro} {BY + 4} V{BY} '
                       f'A{ro} {ro} 0 1 0 {pt(polar(B, ro, 64))}')]
        cr = 66
    elif kind == 'bookmark':
        bm = T([(-18, -30), (18, -30), (18, 30), (0, 16), (-18, 30)])
        b['line'] = [PG(bm)]
        b['area'] = [PG(bm)]
        cr = 60
    elif kind == 'info':
        b['line'] = [L(BX, BY - 4, BX, BY + 32)]
        b['dot'] = [C(BX, BY - 32, 16)]
        cr = 58
    elif kind == 'gear':
        g = gear_path(B, 20, 31, 6, -90)
        b['line'] = [P(g)]
        b['area'] = [P(g)]
        b['hole'] = [C(BX, BY, 7)]
        cr = 60
    elif kind == 'heart':
        h = heart_path((BX, BY + 2), 0.34)
        b['line'] = [P(h)]
        b['area'] = [P(h)]
        cr = 58
    elif kind == 'lightning':
        bolt = T([(6, -34), (-22, 6), (0, 6), (-6, 34), (22, -6), (0, -6)])
        b['line'] = [PG(bolt)]
        b['area'] = [PG(bolt)]
        cr = 58
    elif kind == 'magnifying-glass':
        b['line'] = [C(BX - 6, BY - 6, 18), L(BX + 8, BY + 8, BX + 26, BY + 26)]
        b['area'] = [C(BX - 6, BY - 6, 18)]
    elif kind == 'pause':
        b['line'] = [L(BX - 16, BY - 24, BX - 16, BY + 24), L(BX + 16, BY - 24, BX + 16, BY + 24)]
        cr = 54
    elif kind == 'push-pin':
        import re
        pp = load('push-pin')

        def pin_pts(d):
            return [(float(a), float(b_)) for a, b_ in re.findall(r'([-\d.]+) ([-\d.]+)', d)]
        body = pin_pts(re.search(r'd="([^"]+)"', pp['line'][0]).group(1))
        needle = pin_pts(re.search(r'd="([^"]+)"', pp['line'][1]).group(1))
        s_, cx0, cy0 = 0.34, 133, 124
        tf = lambda q: [(BX + (x - cx0) * s_, BY + (y - cy0) * s_) for x, y in q]
        b['line'] = [PG(tf(body)), PL(tf(needle))]
        b['area'] = [PG(tf(body))]
        cr = 58
    elif kind == 'share':
        b['line'] = [P(f'M{BX - 28} {BY + 28} V{BY + 16} A24 24 0 0 1 {BX - 4} {BY - 8} H{BX + 28}'),
                     PL(T([(8, -28), (28, -8), (8, 12)]))]
        cr = 60
    elif kind == 'reply':
        b['line'] = [P(f'M{BX + 28} {BY + 28} V{BY + 16} A24 24 0 0 0 {BX + 4} {BY - 8} H{BX - 28}'),
                     PL(T([(-8, -28), (-28, -8), (-8, 12)]))]
        cr = 60
    elif kind == 'pencil':
        u, n = (math.sqrt(.5), -math.sqrt(.5)), (math.sqrt(.5), math.sqrt(.5))
        at_ = lambda a, w: (BX + u[0] * a + n[0] * w, BY + u[1] * a + n[1] * w)
        pen = [at_(-32, 0), at_(-14, 12), at_(26, 12), at_(26, -12), at_(-14, -12)]
        b['line'] = [PG(pen)]
        b['area'] = [PG(pen)]
        cr = 58
    elif kind == 'letter-a':
        b['line'] = [PL(T([(-22, 28), (0, -28), (22, 28)])), L(BX - 14, BY + 12, BX + 14, BY + 12)]
        cr = 60
    else:
        raise ValueError(kind)
    return b, cr


def merge(*ds):
    out = dict(line=[], area=[], hole=[], dot=[], detail=[])
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, []) + list(v)
    return out


def chat_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(CHAT, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)]), b)


def env_badge(kind):
    b, cr = badge(kind)
    ln, ar = carve(ENV, B, cr)
    return merge(dict(line=[P(ln)], area=[P(ar)], detail=ENV_FLAP), b)


chat_full = dict(line=[CHAT_D], area=[CHAT_D])

# ================================================================ chat: badge variants (lower right)
for name, kind, tags in [
    ('chat-lightning', 'lightning', ['chat', 'fast', 'power', 'message', 'conversation']),
    ('chat-magnifying-glass', 'magnifying-glass', ['chat', 'search', 'find', 'message', 'search messages']),
    ('chat-minus', 'minus', ['remove message', 'delete comment', 'less', 'chat', 'remove']),
    ('chat-pause', 'pause', ['chat', 'paused', 'hold', 'message', 'conversation']),
    ('chat-pencil', 'pencil', ['chat', 'edit', 'write', 'message']),
    ('chat-plus', 'plus', ['chat', 'new message', 'add', 'compose', 'new chat']),
    ('chat-push-pin', 'push-pin', ['chat', 'pinned', 'pin', 'message', 'conversation']),
    ('chat-reply', 'reply', ['reply', 'respond', 'answer message', 'chat', 'answer']),
    ('chat-share', 'share', ['chat', 'share', 'forward', 'message', 'send']),
    ('chat-x', 'x', ['delete message', 'failed message', 'error', 'chat', 'remove']),
]:
    icon(name, CM, tags, **chat_badge(kind))

# chat-unread: dot at the top right, the bubble opened around it (like bell-dot)
DOT_C = (192, 60)
ln, ar = carve(CHAT, DOT_C, 54)
icon('chat-unread', CM, ['unread message', 'new chat', 'notification', 'badge', 'new'],
     line=[P(ln)], area=[P(ar)], dot=[C(DOT_C[0], DOT_C[1], 28)])

# chat-translate: an "A" badge, a simplified ideogram inside the bubble
tb, tcr = badge('letter-a')
ln, ar = carve(CHAT, B, tcr)
icon('chat-translate', CM, ['translate message', 'language', 'localization', 'chat', 'translation'],
     **merge(dict(line=[P(ln)], area=[P(ar)],
                  detail=[L(72, 92, 136, 92), L(104, 76, 104, 92),
                          P('M122 92 C116 116 102 134 78 146'), P('M88 112 C98 128 110 138 128 144')]), tb))

# ================================================================ chat: symbols inside the bubble (interior 40..216 x 56..200)
icon('chat-image', CM, ['chat', 'image', 'photo', 'message', 'mms'],
     detail=[PL([(76, 168), (112, 128), (144, 160), (164, 140), (184, 160)])],
     dotcut=[C(164, 100, 16)], **chat_full)
icon('chat-info', CM, ['chat', 'info', 'help', 'message'],
     detail=[L(128, 128, 128, 168)], dotcut=[C(128, 94, 16)], **chat_full)
icon('chat-warning', CM, ['chat', 'alert', 'exclamation', 'message', 'report message'],
     detail=[L(128, 88, 128, 132)], dotcut=[C(128, 164, 16)], **chat_full)
q_c, q_r = (128, 104), 24
q_e = polar(q_c, q_r, 64)
icon('chat-question', CM, ['chat', 'question', 'help', 'faq', 'questionnaire'],
     detail=[P(f'M{pt(polar(q_c, q_r, 180))} A{q_r} {q_r} 0 1 1 {pt(q_e)} C133 126 128 130 128 136 V138')],
     dotcut=[C(128, 172, 16)], **chat_full)
icon('chat-lock', CM, ['chat', 'private', 'secure', 'message', 'private chat'],
     detail=[R(96, 120, 64, 48, 10), P('M108 120 V108 A20 20 0 0 1 148 108 V120')], **chat_full)
cr_ = [(108, 84), (148, 84), (148, 108), (172, 108), (172, 148), (148, 148), (148, 172), (108, 172), (108, 148),
       (84, 148), (84, 108), (108, 108)]
icon('chat-medical', CM, ['chat', 'medical', 'health', 'consultation'], detail=[PG(cr_)], **chat_full)
icon('chat-microphone', CM, ['voice message', 'audio chat', 'voice note', 'chat'],
     detail=[R(114, 78, 28, 54, 14), P('M86 112 V120 A42 42 0 0 0 170 120 V112'), L(128, 162, 128, 174)],
     **chat_full)
icon('chat-poll', CM, ['poll', 'vote', 'chat', 'survey'],
     detail=[L(84, 92, 172, 92), L(84, 128, 124, 128), L(84, 164, 148, 164)], **chat_full)
pc, pr = (128, 128), 40
icon('chat-prohibit', CM, ['chat', 'blocked', 'message', 'prohibit'],
     detail=[C(128, 128, pr), L(*polar(pc, pr, 225), *polar(pc, pr, 45))], **chat_full)
icon('chat-quote', CM, ['chat', 'quote', 'testimonial', 'message', 'quote reply'],
     detail=[P('M94 150 V136 C94 116 102 104 118 98'), P('M146 150 V136 C146 116 154 104 170 98')],
     dotcut=[C(102, 150, 21.33), C(154, 150, 21.33)], **chat_full)
icon('chat-report', CM, ['chat report', 'message', 'conversation', 'comment', 'chat'],
     detail=[L(100, 84, 100, 172), PL([(100, 88), (160, 88), (144, 112), (160, 136), (100, 136)])], **chat_full)
SH = load('shield')['line'][0]
import re as _re


def scale_path(d, s, c_from, c_to):
    """Scale an absolute M/L/C/V/H/Z path (no arcs) by s about c_from, moved to c_to."""
    toks = _re.findall(r'[MLCVHZ]|-?[\d.]+', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t in 'MLCVHZ':
            cmd = t
            out.append(t)
            i += 1
            continue
        if cmd == 'V':
            out.append(f(c_to[1] + (float(t) - c_from[1]) * s)); i += 1
        elif cmd == 'H':
            out.append(f(c_to[0] + (float(t) - c_from[0]) * s)); i += 1
        else:
            x, y = float(t), float(toks[i + 1])
            out.append(pt((c_to[0] + (x - c_from[0]) * s, c_to[1] + (y - c_from[1]) * s))); i += 2
    return ' '.join(out)


icon('chat-shield', CM, ['chat', 'secure', 'protected', 'message'],
     detail=[P(scale_path(SH, 0.44, (128, 128), (128, 128)))], **chat_full)
icon('chat-smiley', CM, ['chat', 'emoji', 'friendly', 'message', 'reaction'],
     detail=[P('M98 142 A36 36 0 0 0 158 142')], dotcut=[C(104, 108, 16), C(152, 108, 16)], **chat_full)
SP = load('sparkle')['line'][0]
icon('chat-sparkle', CM, ['ai chat', 'assistant', 'chatbot', 'sparkle', 'chat'],
     detail=[P(scale_path(SP, 0.46, (128, 128), (128, 128)))], **chat_full)
ST = load('star')['line'][0]
icon('chat-star', CM, ['starred message', 'favorite', 'highlight', 'review', 'rating'],
     detail=[P(scale_path(ST, 0.46, (128, 132), (128, 130)))], **chat_full)
icon('chat-trash', CM, ['delete chat', 'remove conversation', 'chat', 'trash'],
     detail=[L(88, 92, 168, 92), L(116, 80, 140, 80),
             P('M104 92 L108 162 A10 10 0 0 0 118 172 H138 A10 10 0 0 0 148 162 L152 92')], **chat_full)
icon('chat-user', CM, ['chat', 'user', 'contact', 'message', 'third party'],
     detail=[C(128, 100, 18), P('M88 172 C88 152 104 142 128 142 C152 142 168 152 168 172')], **chat_full)
icon('chat-video', CM, ['video chat', 'video call', 'chat', 'camera'],
     detail=[R(78, 100, 68, 56, 10), PG([(146, 118), (178, 102), (178, 154), (146, 138)])], **chat_full)
icon('chat-voice', CM, ['voice message', 'audio message', 'chat', 'sound'],
     detail=[L(68, 120, 68, 136), L(98, 104, 98, 152), L(128, 88, 128, 168), L(158, 104, 158, 152),
             L(188, 120, 188, 136)], **chat_full)
icon('chatbot', CM, ['bot', 'assistant', 'support', 'ai'],
     line=[CHAT_D, L(128, 56, 128, 44)], area=[CHAT_D], dot=[C(128, 36, 16)],
     detail=[L(108, 160, 148, 160)], dotcut=[C(100, 118, 18), C(156, 118, 18)])

# chat-history: the round bubble's outline becomes a counter-clockwise arrow, clock hands inside
a_tail0 = ang(CC_C, (52.33, 170))  # 150 deg, where the tail meets the circle
E_ = polar(CC_C, CC_R, 200)
gap_end = polar(CC_C, CC_R, 172)
hist = (f'M{pt(E_)} A{CC_R} {CC_R} 0 1 1 97.54 209.3 L40 216 L52.33 170 '
        f'A{CC_R} {CC_R} 0 0 1 {pt(gap_end)}')
dmove = (math.sin(math.radians(200)), -math.cos(math.radians(200)))
bk = (-dmove[0], -dmove[1]); nn = (-bk[1], bk[0])
hs = 22
head_ = [(E_[0] + (bk[0] + nn[0]) * hs, E_[1] + (bk[1] + nn[1]) * hs), E_,
         (E_[0] + (bk[0] - nn[0]) * hs, E_[1] + (bk[1] - nn[1]) * hs)]
icon('chat-history', CM, ['chat history', 'conversation log', 'messages', 'past'],
     line=[P(hist), PL(head_)], detail=[PL([(132, 82), (132, 124), (162, 142)])], area=[CHATC_D])

# ================================================================ slashed
SG = 30  # clear gap (centreline) left in the base strokes on each side of the slash


def seg_dist(p, a=(48, 48), b=(208, 208)):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return dist(p, (a[0] + dx * t, a[1] + dy * t))


def gapped(outline, closed=True):
    runs, whole = trim(outline, lambda p: seg_dist(p) >= SG, closed)
    if whole:
        return [P(segs_d(outline, closed))]
    return [P(segs_d(r)) for r in runs if r]


icon('chat-slash', CM, ['chat off', 'mute', 'message', 'disabled', 'mute chat'], line=gapped(CHAT) + [SLASH])
CH_FRONT = [('L', (64, 192), (32, 216)), ('L', (32, 216), (32, 104)), ('A', (48, 104), 16, 2 * H, 3 * H),
            ('L', (48, 88), (152, 88)), ('A', (152, 104), 16, 3 * H, 4 * H), ('L', (168, 104), (168, 176)),
            ('A', (152, 176), 16, 0, H), ('L', (152, 192), (64, 192))]
CH_BACK = [('L', (88, 88), (88, 56)), ('A', (104, 56), 16, 2 * H, 3 * H), ('L', (104, 40), (208, 40)),
           ('A', (208, 56), 16, 3 * H, 4 * H), ('L', (224, 56), (224, 184)), ('L', (224, 184), (192, 152))]
icon('chats-slash', CM, ['chat disabled', 'messages off', 'mute', 'conversation'],
     line=gapped(CH_FRONT) + gapped(CH_BACK, False) + [SLASH])

# ================================================================ dialpad
PADS = [(x, y) for y in (44, 100, 156, 212) for x in (72, 128, 184)]
icon('dialpad', CM, ['dialpad', 'keypad', 'phone', 'numbers'], dot=[C(x, y, 18) for x, y in PADS])
icon('dialpad-slash', CM, ['dialpad', 'disabled', 'off', 'communication'],
     line=[SLASH], dot=[C(x, y, 18) for x, y in PADS if abs(x - y) / math.sqrt(2) > 40])

# ================================================================ envelope: badge variants
for name, kind, tags in [
    ('envelope-arrow-clockwise', 'arrow-clockwise', ['mail', 'resend', 'refresh', 'envelope']),
    ('envelope-arrow-down', 'arrow-down', ['mail', 'receive', 'inbox', 'download', 'receive mail']),
    ('envelope-arrow-up', 'arrow-up', ['mail', 'send', 'upload', 'outbox', 'send mail']),
    ('envelope-bitcoin', 'bitcoin', ['envelope', 'crypto', 'bitcoin', 'mail', 'email']),
    ('envelope-bookmark', 'bookmark', ['mail', 'saved', 'bookmark', 'envelope']),
    ('envelope-check', 'check', ['read mail', 'email read', 'sent', 'done', 'mail sent']),
    ('envelope-code', 'code', ['envelope', 'developer', 'code', 'mail', 'email']),
    ('envelope-currency-dollar', 'dollar', ['envelope', 'money', 'price', 'mail', 'email']),
    ('envelope-forward', 'arrow-right', ['forward email', 'send on', 'mail', 'share', 'arrow']),
    ('envelope-gear', 'gear', ['mail settings', 'envelope', 'preferences', 'gear']),
    ('envelope-heart', 'heart', ['love letter', 'mail', 'valentine', 'envelope', 'heart']),
    ('envelope-incoming', 'arrow-down-left', ['received mail', 'inbox', 'incoming']),
    ('envelope-info', 'info', ['mail', 'info', 'details', 'envelope']),
]:
    icon(name, CM, tags, **env_badge(kind))

# envelope-fast: the envelope (same proportions, slightly smaller) with speed lines trailing on the left
ex, ey, ew, eh = 92, 74, 132, 108
env_s = R(ex, ey, ew, eh, 14)
icon('envelope-fast', CM, ['express mail', 'fast', 'send', 'envelope', 'express'],
     line=[env_s, L(46, 96, 60, 96), L(32, 128, 60, 128), L(46, 160, 60, 160)],
     detail=[PL([(ex + 16, ey + 18), (ex + ew / 2, ey + 66), (ex + ew - 16, ey + 18)])], area=[env_s])

print(save(overwrite=True))
