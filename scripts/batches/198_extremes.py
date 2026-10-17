"""Anchors on curve extremes: a cubic or quadratic that bulges more than a unit past both of its ends (left, right,
up or down) is split at that extreme, so the anchor sits there with a flat handle, as in hand-drawn vector work.
The split is exact (de Casteljau); the new anchor is rounded to a whole unit and its handles move with it.

  python3 scripts/batches/198_extremes.py            # every icon
  python3 scripts/batches/198_extremes.py name ...   # these icons
"""
import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT, f

ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}
BULGE = 1.0   # how far past both ends a curve may go before its extreme needs an anchor


def extreme_ts(p):
    """Parameters in (0, 1) where cubic p (4 points) has an x or y extreme that bulges past both ends."""
    ts = []
    for k in (0, 1):
        a, b, c, d = (q[k] for q in p)
        # derivative / 3: (b-a)(1-t)^2 + 2(c-b)(1-t)t + (d-c)t^2
        A, B, C = (b - a) - 2 * (c - b) + (d - c), 2 * ((c - b) - (b - a)), b - a
        roots = []
        if abs(A) < 1e-9:
            if abs(B) > 1e-9:
                roots = [-C / B]
        else:
            disc = B * B - 4 * A * C
            if disc >= 0:
                roots = [(-B + math.sqrt(disc)) / (2 * A), (-B - math.sqrt(disc)) / (2 * A)]
        for t in roots:
            if 0.02 < t < 0.98:
                v = point(p, t)[k]
                if v > max(a, d) + BULGE or v < min(a, d) - BULGE:
                    ts.append(t)
    return sorted(set(round(t, 6) for t in ts))


def point(p, t):
    while len(p) > 1:
        p = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) for (x0, y0), (x1, y1) in zip(p, p[1:])]
    return p[0]


def split(p, t):
    """Two cubics: p on [0, t] and on [t, 1]."""
    left, right, cur = [p[0]], [p[-1]], p
    while len(cur) > 1:
        cur = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) for (x0, y0), (x1, y1) in zip(cur, cur[1:])]
        left.append(cur[0])
        right.append(cur[-1])
    return left, right[::-1]


def split_all(p, ts):
    out, done = [], 0.0
    for t in ts:
        a, p = split(p, (t - done) / (1 - done))
        out.append(a)
        done = t
    return out + [p]


def fix_d(d):
    if re.search(r'[ST]', d):  # smooth commands reflect the previous handle; splitting would bend them
        return d
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?', d)
    out, i, cmd = [], 0, 'M'
    x = y = sx = sy = 0.0
    changed = False
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == 'Z':
                out.append('Z')
                x, y = sx, sy
                continue
        a = [float(v) for v in toks[i:i + ARGS[cmd]]]
        i += ARGS[cmd]
        seg = None
        if cmd == 'C':
            seg = [(x, y), (a[0], a[1]), (a[2], a[3]), (a[4], a[5])]
        elif cmd == 'Q':  # degree-elevate so it splits like a cubic
            q = (a[0], a[1])
            seg = [(x, y), (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y)),
                   (a[2] + 2 / 3 * (q[0] - a[2]), a[3] + 2 / 3 * (q[1] - a[3])), (a[2], a[3])]
        ts = extreme_ts(seg) if seg else []
        if ts:
            changed = True
            pieces = split_all(seg, ts)
            for j, pc in enumerate(pieces):
                if j < len(pieces) - 1:  # round the new anchor; its two handles move with it
                    e = pc[3]
                    r = (round(e[0]), round(e[1]))
                    dx, dy = r[0] - e[0], r[1] - e[1]
                    pc[2] = (pc[2][0] + dx, pc[2][1] + dy)
                    pc[3] = r
                    nxt = pieces[j + 1]
                    nxt[0] = r
                    nxt[1] = (nxt[1][0] + dx, nxt[1][1] + dy)
                out.append('C' + ' '.join(f'{f(round(px, 2))} {f(round(py, 2))}' for px, py in pc[1:]))
        else:
            out.append(cmd + ' '.join(f(v) for v in a) if cmd not in 'A' else
                       'A' + ' '.join([f(a[0]), f(a[1]), f(a[2]), str(int(a[3])), str(int(a[4])), f(a[5]), f(a[6])]))
        if cmd == 'H':
            x = a[0]
        elif cmd == 'V':
            y = a[0]
        else:
            x, y = a[-2], a[-1]
        if cmd == 'M':
            sx, sy = x, y
            cmd = 'L'
    return ' '.join(out) if changed else d


def fix(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    new = re.sub(r' d="([^"]*)"', lambda m: f' d="{fix_d(m.group(1))}"', src)
    if new != src:
        open(path, 'w').write(new)
        return True
    return False


if __name__ == '__main__':
    icons = os.path.join(ROOT, 'icons')
    names = sys.argv[1:] or sorted(n[:-4] for n in os.listdir(icons) if n.endswith('.svg'))
    print(sum(fix(n) for n in names), 'icons given anchors on their curve extremes')
