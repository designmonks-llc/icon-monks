"""Consistency pass: the same visual size, the same centre and the same corner radii across the set.

scripts/audit.py measures every icon; this applies its fixes. Three steps, in this order:

  size     Objects whose larger side spans less than 168 units grow to 176 about their centre (never past the live
           area or a container keyline). Glyphs, maths and typographic symbols, carets, dot grids, tally marks and
           signal or volume levels keep their size: they are meant to sit smaller.
  centre   An icon whose geometry box sits 6 or more units off the canvas centre moves back by an even number of
           units. Families that line up on purpose (signal bars, speaker levels, line caps) and optically centred
           triangles (play) stay put.
  corners  Rounded corners follow STYLE.md rule 8: radius 16 on shapes at least 64 units on both sides, 8 on smaller
           parts. Applies to rect rx and to quarter-arc corners between straight path segments. Radii of 24 and up,
           and soft shapes whose radius is 40% or more of their short side, are drawn round on purpose and stay.

A variant that repeats its base (`-slash`, standard badges) is rebuilt from the base afterwards by 194_slash.py and
200_badges.py. Any other variant (audit.variant_base(): a base icon plus a mark such as -sparkle, -lock or -currency-dollar, or
most of its base's shapes unchanged) gets the same move and scale as its base, so the pair stays aligned, unless
that would push it out of the live area: then the whole family goes as far as all its members can (3/4, 1/2 or
1/4 of the way), or stays as drawn (audit.py lists it).

  python3 scripts/batches/235_consistency.py            # every icon
  python3 scripts/batches/235_consistency.py name ...   # these icons (and their custom variants)
"""
import importlib.util
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT, f
import lint
import audit


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.abspath(__file__)), name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


keylines = _load('196_keylines')
ICONS = os.path.join(ROOT, 'icons')
TARGET = 176            # larger side an undersized object grows to
CORNER_MAX = 24         # radii from here up are a drawn roundness, not a corner


def transform(name, s, dx, dy, cx, cy):
    """Scale by s about (cx, cy), then move by (dx, dy). Anchors land on whole units; strokes and dots keep size."""
    path = os.path.join(ICONS, name + '.svg')

    def T(x, y, anchor):
        nx, ny = cx + (x - cx) * s + dx, cy + (y - cy) * s + dy
        return [round(nx), round(ny)] if anchor else [round(nx, 2), round(ny, 2)]

    def S(r):
        return round(r * s) if abs(r * s - round(r * s)) < 0.25 else round(r * s, 2)

    src = open(path).read()
    head, body = src[:src.index('>') + 1], src[src.index('>') + 1:]
    role, parts = None, []
    for chunk in re.split(r'(<g data-role="\w+")', body):
        m = re.match(r'<g data-role="(\w+)"', chunk)
        if m:
            role = m.group(1)
            parts.append(chunk)
            continue
        if role in ('slash', 'badge'):
            parts.append(chunk)
            continue

        def el(m):
            tag, attrs = m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))
            if tag == 'path':
                attrs['d'] = keylines.transform_d(attrs['d'], T, S)
            elif tag in ('circle', 'ellipse'):
                attrs['cx'], attrs['cy'] = (f(v) for v in T(float(attrs['cx']), float(attrs['cy']), True))
                for k in ('r', 'rx', 'ry'):
                    if k in attrs and role not in ('dot', 'dotcut'):
                        attrs[k] = f(S(float(attrs[k])))
            elif tag == 'rect':
                x0, y0 = T(float(attrs['x']), float(attrs['y']), True)
                x1, y1 = T(float(attrs['x']) + float(attrs['width']), float(attrs['y']) + float(attrs['height']), True)
                attrs.update(x=f(x0), y=f(y0), width=f(x1 - x0), height=f(y1 - y0))
                for k in ('rx', 'ry'):
                    if k in attrs:
                        attrs[k] = f(S(float(attrs[k])))
            return f'<{tag} ' + ' '.join(f'{k}="{v}"' for k, v in attrs.items()) + '/>'
        parts.append(re.sub(r'<(path|circle|ellipse|rect)\s([^>]*?)/>', el, chunk))
    new = head + ''.join(parts)
    if new != src:
        open(path, 'w').write(new)
        return True
    return False


def plan(name):
    """(scale, dx, dy, cx, cy) for an icon, or None. Scale first (about the box centre), then centre."""
    root = lint.ET.parse(os.path.join(ICONS, name + '.svg')).getroot()
    x0, y0, x1, y1 = audit.bounds(root)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = 1.0
    if audit.undersized(name, root):
        s = TARGET / max(x1 - x0, y1 - y0)
        c = lint.container(root)
        if c:
            kind, w, h = c
            limit = keylines.CIRCLE if kind == 'circle' else keylines.SQUARE if 0.9 <= w / h <= 1 / 0.9 else keylines.RECT
            s = min(s, limit / max(w, h))
        s = max(1.0, min(s, (lint.LIVE[1] - lint.LIVE[0]) / max(x1 - x0, y1 - y0)))
    dx = dy = 0
    if not audit.centre_exempt(name):
        ox, oy = cx - 128, cy - 128
        off = 2 if s > 1 else audit.OFF_CENTRE  # a resized icon is re-centred anyway
        dx = -2 * round(ox / 2) if abs(ox) >= off else 0
        dy = -2 * round(oy / 2) if abs(oy) >= off else 0
    if s == 1.0 and not dx and not dy:
        return None
    # keep the scaled box inside the live area
    w, h = (x1 - x0) * s, (y1 - y0) * s
    lo, hi = lint.LIVE
    dx = max(lo - (cx - w / 2), min(hi - (cx + w / 2), dx))
    dy = max(lo - (cy - h / 2), min(hi - (cy + h / 2), dy))
    return round(s, 4), round(dx), round(dy), cx, cy


# ---- corners -------------------------------------------------------------------------------------------------------

def corner_radius(w, h, r):
    """The radius a corner on a w x h shape should have, or None to keep r."""
    short = min(w, h)
    if r <= 0 or r >= CORNER_MAX or r >= 0.4 * short:
        return None
    return 16 if short >= 64 else 8


def parse(d):
    toks = lint.tokens(d)
    segs, i, cmd, x, y, sx, sy = [], 0, 'M', 0.0, 0.0, 0.0, 0.0
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
        if cmd == 'Z':
            segs.append({'cmd': 'Z', 'a': [], 'start': (x, y), 'end': (sx, sy)})
            x, y = sx, sy
            continue
        a = [float(v) for v in toks[i:i + lint.ARGS[cmd]]]
        i += lint.ARGS[cmd]
        end = (a[0], y) if cmd == 'H' else (x, a[0]) if cmd == 'V' else (a[-2], a[-1])
        segs.append({'cmd': cmd, 'a': a, 'start': (x, y), 'end': end})
        x, y = end
        if cmd == 'M':
            sx, sy = x, y
            cmd = 'L'
    return segs


def serial(segs):
    out = []
    for s in segs:
        a = list(s['a'])
        if s['cmd'] == 'A':
            a[3], a[4] = int(a[3]), int(a[4])
        out.append(s['cmd'] + ' '.join(str(v) if isinstance(v, int) else f(v) for v in a))
    return ' '.join(out)


def set_end(seg, p):
    seg['end'] = p
    if seg['cmd'] == 'H':
        seg['a'] = [p[0]]
    elif seg['cmd'] == 'V':
        seg['a'] = [p[1]]
    else:
        seg['a'][-2:] = [p[0], p[1]]


def axis(p, q):
    """'h' or 'v' for an axis-aligned segment p->q with length, else None."""
    if p[1] == q[1] and p[0] != q[0]:
        return 'h'
    if p[0] == q[0] and p[1] != q[1]:
        return 'v'
    return None


def same_way(a, b, c):
    """True when c lies on the ray a->b at or past a (the segment keeps its direction after moving its end)."""
    return (b[0] - a[0]) * (c[0] - a[0]) + (b[1] - a[1]) * (c[1] - a[1]) >= 0


def fix_subpath(sub):
    """Normalise the quarter-arc corners of one subpath (a list of segments starting with M) in place.
    Returns the number changed, or None when some corner can't be changed: then the caller keeps the subpath as it
    was, so a shape never ends up with mixed radii."""
    closed = sub[-1]['cmd'] == 'Z'
    pts = [s['end'] for s in sub]
    w = max(p[0] for p in pts) - min(p[0] for p in pts)
    h = max(p[1] for p in pts) - min(p[1] for p in pts)
    # the drawn segments, with a zero-length closing Z dropped so the first segment follows the last
    body = list(range(1, len(sub)))
    if closed and sub[-1]['start'] == sub[-1]['end']:
        body = body[:-1]

    def neighbour(k, step):
        j = body.index(k) + step
        if 0 <= j < len(body):
            return sub[body[j]]
        return sub[body[j % len(body)]] if closed else None

    changed = 0
    for k in body:
        s = sub[k]
        if s['cmd'] != 'A':
            continue
        rx, ry, rot, large = s['a'][:4]
        P, Q = s['start'], s['end']
        if rx != ry or rot or large or abs(abs(Q[0] - P[0]) - rx) > 0.01 or abs(abs(Q[1] - P[1]) - rx) > 0.01:
            continue
        r = corner_radius(w, h, rx)
        if r is None or r == rx:
            continue
        prev, nxt = neighbour(k, -1), neighbour(k, 1)
        if prev is None or nxt is None or prev['cmd'] not in 'LHVZ' or nxt['cmd'] not in 'LHVZ':
            return None
        a_in, a_out = axis(prev['start'], P), axis(Q, nxt['end'])
        if not a_in or not a_out or a_in == a_out:
            return None
        V = (Q[0], P[1]) if a_in == 'h' else (P[0], Q[1])
        k_ = r / rx
        P2 = (V[0] + (P[0] - V[0]) * k_, V[1] + (P[1] - V[1]) * k_)
        Q2 = (V[0] + (Q[0] - V[0]) * k_, V[1] + (Q[1] - V[1]) * k_)
        if not same_way(prev['start'], P, P2) or not same_way(nxt['end'], Q, Q2) or \
                any(v != round(v) for v in P2 + Q2):
            return None
        # the point P sits at prev's end; if prev is the closing Z, P is the subpath start (the M)
        if prev['cmd'] == 'Z':
            set_end(sub[0], P2)
            sub[1]['start'] = P2
            prev['end'] = P2
        else:
            set_end(prev, P2)
        s['start'] = P2
        s['a'][0] = s['a'][1] = r
        set_end(s, Q2)
        nxt['start'] = Q2
        if k == body[-1] and closed:     # the arc ends where the path started
            set_end(sub[0], Q2)
            sub[-1]['end'] = Q2
            sub[-1]['start'] = Q2 if sub[-1]['start'] == Q else sub[-1]['start']
        changed += 1
    return changed


def fix_corners_d(d):
    import copy
    segs = parse(d)
    subs, cur = [], []
    for s in segs:
        if s['cmd'] == 'M' and cur:
            subs.append(cur)
            cur = []
        cur.append(s)
    subs.append(cur)
    out, changed = [], 0
    for sub in subs:
        trial = copy.deepcopy(sub)
        n = fix_subpath(trial)
        if n:
            out += trial
            changed += n
        else:
            out += sub
    return (serial(out), changed) if changed else (d, 0)


def fix_corners(name):
    path = os.path.join(ICONS, name + '.svg')
    src = open(path).read()
    head, body = src[:src.index('>') + 1], src[src.index('>') + 1:]
    role, parts = None, []
    for chunk in re.split(r'(<g data-role="\w+")', body):
        m = re.match(r'<g data-role="(\w+)"', chunk)
        if m:
            role = m.group(1)
            parts.append(chunk)
            continue
        if role in ('slash', 'badge', 'dot', 'dotcut'):
            parts.append(chunk)
            continue

        def rect(m):
            attrs = m.group(1)
            w, h = (float(re.search(fr'\b{k}="([^"]*)"', attrs).group(1)) for k in ('width', 'height'))
            rx = re.search(r'\brx="([^"]*)"', attrs)
            r = corner_radius(w, h, float(rx.group(1))) if rx else None
            if r is None:
                return m.group(0)
            attrs = re.sub(r'\brx="[^"]*"', f'rx="{f(r)}"', attrs)
            attrs = re.sub(r'\bry="[^"]*"', f'ry="{f(r)}"', attrs)
            return f'<rect {attrs}/>'

        def path_el(m):
            return 'd="' + fix_corners_d(m.group(1))[0] + '"'
        chunk = re.sub(r'<rect\s([^>]*?)/>', rect, chunk)
        chunk = re.sub(r'(?<=<path )d="([^"]*)"', path_el, chunk)
        parts.append(chunk)
    new = head + ''.join(parts)
    if new != src:
        open(path, 'w').write(new)
        return True
    return False


def main(names):
    every = sorted(n[:-4] for n in os.listdir(ICONS) if n.endswith('.svg'))
    names = set(names or every)
    rebuilt = {n for n in every if audit.rebuilt_variant(n)}
    base = {n: audit.variant_base(n) for n in every if n not in rebuilt}

    def root(n):
        while base.get(n):
            n = base[n]
        return n
    # plan everything against the untouched sources first, then apply
    plans = {n: plan(n) for n in every if n not in rebuilt and not base[n] and n in names}
    followers = [n for n in every if n not in rebuilt and base[n] and (n in names or root(n) in names)]
    # A base stays as it is when one of its variants can't take the same change without leaving the live area:
    # a family that lines up beats one fixed member.
    def fits(n, p):
        before = open(os.path.join(ICONS, n + '.svg')).read()
        transform(n, *p)
        ok = not lint.check(os.path.join(ICONS, n + '.svg'))[1]
        open(os.path.join(ICONS, n + '.svg'), 'w').write(before)
        return ok

    family = {}
    for n in followers:
        family.setdefault(root(n), []).append(n)
    held, partial = set(), set()
    for b, members in family.items():
        p = plans.get(b)
        if not p or all(fits(n, p) for n in members):
            continue
        # go part of the way, as far as every member can follow
        s, dx, dy, cx, cy = p
        for t in (0.75, 0.5, 0.25):
            q = (round(1 + (s - 1) * t, 4), 2 * round(dx * t / 2), 2 * round(dy * t / 2), cx, cy)
            if (q[0] != 1 or q[1] or q[2]) and all(fits(n, q) for n in members):
                plans[b] = q
                partial.add(b)
                break
        else:
            plans[b] = None
            held.add(b)
    moved, scaled, followed, cornered = [], [], [], []
    for n, p in plans.items():
        if p:
            transform(n, *p)
            (scaled if p[0] != 1.0 else moved).append(n)
    for n in followers:
        p = plans.get(root(n))
        if p:
            transform(n, *p)
            followed.append(n)
    for t in sorted(set(plans) | set(followers)):
        if not audit.corner_exempt(t) and fix_corners(t):
            cornered.append(t)
    print(f'{len(scaled)} icons grown to size, {len(moved)} re-centred, {len(followed)} variants moved with their base, '
          f'{len(partial)} families moved part way and {len(held)} held because a variant would leave the live area '
          f'({", ".join(sorted(held)) or "none"}), '
          f'{len(cornered)} with corners normalised')


if __name__ == '__main__':
    main(sys.argv[1:])
