#!/usr/bin/env python3
"""Check icons/ against the rules in STYLE.md. Standard library only, so it runs before pip install.

  python3 scripts/lint.py                    # fail on any problem not recorded in the baseline
  python3 scripts/lint.py house bell         # check named icons only
  python3 scripts/lint.py --all              # list every problem, baseline included
  python3 scripts/lint.py --update-baseline  # drop fixed icons from the baseline (it never grows)

scripts/lint-baseline.json lists the icons waiting to be redrawn; every other problem fails. Redrawing one and
re-running --update-baseline removes it from the file.
"""
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'icons')
BASELINE = os.path.join(ROOT, 'scripts', 'lint-baseline.json')
NS = '{http://www.w3.org/2000/svg}'

ROLES = ('line', 'detail', 'area', 'hole', 'dot', 'dotcut', 'slash', 'badge')
CATEGORIES = {
    'Animals', 'Arrows', 'Business', 'Charts', 'Commerce', 'Communication', 'Design', 'Development', 'Devices',
    'Editor', 'Education', 'Emoji', 'Files', 'Food', 'Health', 'Home', 'Interface', 'Letters & Numbers', 'Maps',
    'Media', 'Nature', 'Objects', 'People', 'Science', 'Security', 'Sports', 'Symbols', 'Time', 'Transport', 'Weather',
}
LIVE = (32, 224)        # geometry must stay inside; 16-unit strokes then reach 24..232
LIVE_TOL = 1            # curves bulge a little between whole-unit anchors
MIN_SIZE = 144          # an icon's larger side should span at least this much of the grid
MAX_STROKED = 8         # line + detail elements; more than this turns to mush at 16px
MAX_SEGMENTS = 40       # straight segments in one curve-free path; more means a curve saved as points
KEYLINES = {'circle': 192, 'square': 176, 'rect': 192}  # max centreline size of a container shape
SLASHES = ('M48 48 L208 208', 'M208 48 L48 208')
# Standard corner badges for <base>-<modifier> icons (STYLE.md rule 11): paths in a 'badge' group, circles of r<=12
# are solid dots. Every badge sits in the same 56-unit spot around (188, 188).
BADGES = {
    'plus': ['M188 160 V216', 'M160 188 H216'],
    'minus': ['M160 188 H216'],
    'x': ['M168 168 L208 208', 'M208 168 L168 208'],
    'check': ['M162 190 L180 208 L214 172'],
    'warning': ['M188 160 V186', ('circle', 188, 212, 12)],
    'question': ['M174 170 A14 14 0 1 1 192 183 C189 185 188 187 188 188', ('circle', 188, 212, 12)],
    'heart': ['M188 214 C174 206 160 194 160 180 A14 14 0 0 1 188 174 A14 14 0 0 1 216 180 C216 194 202 206 188 214 Z'],
    'star': ['M188 162 L196 181 L217 183 L200 196 L206 216 L188 205 L170 216 L176 196 L159 183 L180 181 Z'],
    'gear': ['M182 161 L194 161 L195 169 L201 173 L208 169 L215 180 L208 184 L208 192 L215 196 L208 207 L201 203 L195 207 L194 215 L182 215 L181 207 L175 203 L168 207 L161 196 L168 192 L168 184 L161 180 L168 169 L175 173 L181 169 Z'],
    'magnifying-glass': [('circle', 182, 182, 18), 'M196 196 L214 214'],
    'arrow-up': ['M188 214 V162', 'M166 184 L188 162 L210 184'],
    'arrow-down': ['M188 162 V214', 'M166 192 L188 214 L210 192'],
    'user': [('circle', 188, 172, 14), 'M162 214 A26 26 0 0 1 214 214'],
}
NO_BASE_SLASH = {'cell-signal-slash', 'file-eye-slash'}  # partial slash drawn as part of the glyph

RULES = {
    'stroke': 'line/detail groups must use stroke-width 16 with round caps and joins',
    'role': 'every shape sits in a <g data-role> group with a known role',
    'meta': 'data-category from the category list and at least 3 data-tags',
    'no-fill': 'has a closed shape but no area/detail/hole/dotcut, so the fill weight is just the outline '
               '(letters, numbers and symbols that should stay outlined say so with data-fill="outline")',
    'live-area': f'geometry leaves the {LIVE[0]}..{LIVE[1]} live area',
    'small': f'larger side spans less than {MIN_SIZE} units, so it looks smaller than its neighbours '
             '(symbols meant to sit small, such as carets, say so with data-size="symbol")',
    'off-grid': 'straight-segment endpoints, circle centres or rect corners are not whole numbers',
    'detail': f'more than {MAX_STROKED} stroked elements; simplify it, or check it at 16 px and mark it '
              'data-detail="reviewed" if it still reads clearly',
    'extremes': 'a curve bulges past its ends with no anchor at its top, bottom, left or right extreme',
    'tessellated': f'a path is more than {MAX_SEGMENTS} straight segments; draw curves with arcs and cubics',
    'keyline': 'a container is bigger than its keyline: circle 192, square 176, other rectangle 192 on the long side',
    'badge': 'a <base>-<modifier> icon (plus, minus, x, check, ...) is its base icon unchanged plus the standard '
             'badge group from BADGES, or is marked data-badge="custom" when the modifier is drawn into the icon',
    'slash': 'a -slash icon is its base icon unchanged plus one slash group with M48 48 L208 208 '
             '(or the mirrored M208 48 L48 208); no other icon has a slash group',
}

ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


def tokens(d):
    return re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?', d)


def arc_points(x0, y0, rx, ry, rot, large, sweep, x, y, steps=24):
    """Sample an SVG arc via the endpoint-to-centre conversion in the SVG spec (F.6.5)."""
    if not rx or not ry or (x0, y0) == (x, y):
        return [(x, y)]
    phi = math.radians(rot)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x0 - x) / 2, (y0 - y) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    k = math.sqrt(max(num, 0) / (rx * rx * y1 * y1 + ry * ry * x1 * x1))
    if large == sweep:
        k = -k
    cx1, cy1 = k * rx * y1 / ry, -k * ry * x1 / rx
    cx, cy = cp * cx1 - sp * cy1 + (x0 + x) / 2, sp * cx1 + cp * cy1 + (y0 + y) / 2
    a1 = math.atan2((y1 - cy1) / ry, (x1 - cx1) / rx)
    a2 = math.atan2((-y1 - cy1) / ry, (-x1 - cx1) / rx)
    span = a2 - a1
    if sweep and span < 0:
        span += 2 * math.pi
    elif not sweep and span > 0:
        span -= 2 * math.pi
    out = []
    for i in range(1, steps + 1):
        a = a1 + span * i / steps
        ex, ey = rx * math.cos(a), ry * math.sin(a)
        out.append((cp * ex - sp * ey + cx, sp * ex + cp * ey + cy))
    return out


def bezier(pts, steps=16):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        p = list(pts)
        while len(p) > 1:
            p = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(p, p[1:])]
        out.append(p[0])
    return out


def walk(d):
    """Return (points along the path, straight-segment endpoints, closed?). Absolute commands only."""
    t = tokens(d)
    i, cmd, x, y, sx, sy = 0, 'M', 0.0, 0.0, 0.0, 0.0
    ctrl = None
    points, anchors, closed = [], [], False
    while i < len(t):
        if t[i].isalpha():
            cmd = t[i]
            i += 1
            if cmd.islower():
                raise ValueError(f'relative command "{cmd}"; sources use absolute commands')
        if cmd == 'Z':
            closed = True
            x, y = sx, sy
            continue
        a = [float(v) for v in t[i:i + ARGS[cmd]]]
        i += ARGS[cmd]
        last = ctrl
        ctrl = None
        if cmd == 'M':
            x, y = sx, sy = a
            points.append((x, y))
            anchors.append((x, y))
            cmd = 'L'
            continue
        if cmd in 'LHV':
            x = a[0] if cmd in 'LH' else x
            y = a[1] if cmd == 'L' else a[0] if cmd == 'V' else y
            points.append((x, y))
            anchors.append((x, y))
            continue
        if cmd == 'A':
            points += arc_points(x, y, *a)
        elif cmd in 'CS':
            c1 = (a[0], a[1]) if cmd == 'C' else (2 * x - last[0], 2 * y - last[1]) if last else (x, y)
            rest = [(a[j], a[j + 1]) for j in range(0 if cmd == 'S' else 2, len(a), 2)]
            points += bezier([(x, y), c1] + rest)
            ctrl = rest[-2]
        else:  # Q, T
            c1 = (a[0], a[1]) if cmd == 'Q' else (2 * x - last[0], 2 * y - last[1]) if last else (x, y)
            points += bezier([(x, y), c1, (a[-2], a[-1])])
            ctrl = c1
        x, y = a[-2], a[-1]
    return points, anchors, closed


def role_shape(role, el):
    """shape(), with dots shrunk to the radius they render at in the regular weight (0.75 r) less half a stroke,
    so their extent compares with stroke centrelines."""
    if role in ('dot', 'dotcut'):
        cx, cy, r = (float(el.get(k)) for k in ('cx', 'cy', 'r'))
        r = max(0.0, 0.75 * r - 8)
        return [(cx - r, cy), (cx + r, cy), (cx, cy - r), (cx, cy + r)], [(cx, cy)], True
    return shape(el)


def shape(el):
    """Same contract as walk() for <path>, <circle>, <ellipse> and <rect>."""
    tag = el.tag.replace(NS, '')
    f = lambda k, default=0.0: float(el.get(k, default))
    if tag == 'path':
        return walk(el.get('d'))
    if tag in ('circle', 'ellipse'):
        cx, cy = f('cx'), f('cy')
        rx = f('r') if tag == 'circle' else f('rx')
        ry = f('r') if tag == 'circle' else f('ry')
        return [(cx - rx, cy), (cx + rx, cy), (cx, cy - ry), (cx, cy + ry)], [(cx, cy)], True
    if tag == 'rect':
        x, y, w, h = f('x'), f('y'), f('width'), f('height')
        return [(x, y), (x + w, y + h)], [(x, y), (x + w, y + h)], True
    raise ValueError(f'unsupported element <{tag}>')


def container(root):
    """(kind, w, h) of the closed line/area shape that spans the whole icon ('circle' or 'rect'), or None."""
    pts, closed = [], []
    for g in root:
        if g.get('data-role') in ('slash', 'badge'):
            continue
        for el in g:
            p, _, shut = role_shape(g.get('data-role'), el)
            pts += p
            if g.get('data-role') in ('line', 'area') and shut:
                closed.append((el, p))
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    W, H = max(xs) - min(xs), max(ys) - min(ys)
    for el, p in closed:
        ex, ey = [q[0] for q in p], [q[1] for q in p]
        w, h = max(ex) - min(ex), max(ey) - min(ey)
        if w >= 0.9 * W and h >= 0.9 * H:
            tag = el.tag.replace(NS, '')
            d = el.get('d') or ''
            if abs(w - h) < 2 and (tag in ('circle', 'ellipse') or (d and not re.search(r'[LHVCQST]', d))):
                return 'circle', w, h
            if tag == 'rect' or (d and not re.search(r'[LCQST]', d)):
                return 'rect', w, h
            return None
    return None


def over_keyline(root):
    c = container(root)
    if not c:
        return False
    kind, w, h = c
    limit = KEYLINES['circle'] if kind == 'circle' else \
        KEYLINES['square'] if 0.9 <= w / h <= 1 / 0.9 else KEYLINES['rect']
    return max(w, h) > limit + 1.5


def misses_extremes(d):
    """True when a cubic or quadratic bulges more than a unit past both of its ends without an anchor there."""
    if re.search(r'[ST]', d):
        return False
    t = tokens(d)
    i, cmd, x, y, sx, sy = 0, 'M', 0.0, 0.0, 0.0, 0.0
    while i < len(t):
        if t[i].isalpha():
            cmd = t[i]
            i += 1
            if cmd == 'Z':
                x, y = sx, sy
                continue
        a = [float(v) for v in t[i:i + ARGS[cmd]]]
        i += ARGS[cmd]
        if cmd in 'CQ':
            ctl = [(x, y)] + [(a[j], a[j + 1]) for j in range(0, len(a), 2)]
            for k in (0, 1):
                ends = (ctl[0][k], ctl[-1][k])
                vals = [p[k] for p in bezier(ctl, 32)]
                if max(vals) > max(ends) + 1.0 or min(vals) < min(ends) - 1.0:
                    return True
        if cmd == 'H':
            x = a[0]
        elif cmd == 'V':
            y = a[0]
        elif cmd != 'Z':
            x, y = a[-2], a[-1]
        if cmd == 'M':
            sx, sy = x, y
            cmd = 'L'
    return False


def bad_slash(path, name, roles):
    if not name.endswith('-slash') or name in NO_BASE_SLASH:
        return bool(roles['slash'])
    base = os.path.join(os.path.dirname(path), name[:-6] + '.svg')
    if not os.path.exists(base) or [el.get('d') for el in roles['slash']] not in ([d] for d in SLASHES):
        return True
    body = lambda s: s[s.index('>') + 1:s.rindex('</svg>')]
    src, ref = body(open(path).read()), body(open(base).read())
    return src[:src.index('  <g data-role="slash"')] != ref


def badge_of(name, folder):
    """The modifier of a <base>-<modifier> icon whose base exists, e.g. 'plus' for bell-plus, else None."""
    for mod in sorted(BADGES, key=len, reverse=True):
        if name.endswith('-' + mod) and os.path.exists(os.path.join(folder, name[:-len(mod) - 1] + '.svg')):
            return mod
    return None


def badge_elements(mod):
    return [('circle', m[1], m[2], m[3]) if isinstance(m, tuple) else ('path', m) for m in BADGES[mod]]


def bad_badge(path, name, roles, root):
    mod = None if name.endswith('-slash') else badge_of(name, os.path.dirname(path))
    if mod is None or root.get('data-badge') == 'custom':
        return bool(roles['badge'])
    els = [('circle', float(e.get('cx')), float(e.get('cy')), float(e.get('r'))) if e.tag == NS + 'circle'
           else ('path', e.get('d')) for e in roles['badge']]
    if els != badge_elements(mod):
        return True
    body = lambda s: s[s.index('>') + 1:s.rindex('</svg>')]
    src = body(open(path).read())
    ref = body(open(os.path.join(os.path.dirname(path), name[:-len(mod) - 1] + '.svg')).read())
    return src[:src.index('  <g data-role="badge"')] != ref


def check(path):
    name = os.path.basename(path)[:-4]
    root = ET.parse(path).getroot()
    found = set()
    roles = {r: [] for r in ROLES}
    for el in root:
        if el.tag != NS + 'g' or el.get('data-role') not in ROLES:
            found.add('role')
            continue
        role = el.get('data-role')
        if role in ('line', 'detail', 'slash', 'badge') and (el.get('stroke-width') != '16' or el.get('stroke-linecap') != 'round'
                                           or el.get('stroke-linejoin') != 'round'):
            found.add('stroke')
        roles[role] += list(el)

    tags = [t for t in root.get('data-tags', '').split(',') if t.strip()]
    if root.get('data-category') not in CATEGORIES or len(tags) < 3:
        found.add('meta')

    points, closed = [], False
    for role, els in roles.items():
        for el in els:
            p, anchors, shut = role_shape(role, el)
            d = el.get('d') or ''
            if not re.search(r'[ACQST]', d) and len(re.findall(r'[LHV]', d)) > MAX_SEGMENTS:
                found.add('tessellated')
            if d and misses_extremes(d):
                found.add('extremes')
            points += p
            if role in ('line', 'detail'):
                closed = closed or shut
            if any(v != round(v) for xy in anchors for v in xy):
                found.add('off-grid')

    if closed and root.get('data-fill') != 'outline' and \
            not (roles['area'] or roles['detail'] or roles['hole'] or roles['dotcut']):
        found.add('no-fill')
    if points:
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        if min(xs) < LIVE[0] - LIVE_TOL or min(ys) < LIVE[0] - LIVE_TOL or max(xs) > LIVE[1] + LIVE_TOL or \
                max(ys) > LIVE[1] + LIVE_TOL:
            found.add('live-area')
        if max(max(xs) - min(xs), max(ys) - min(ys)) < MIN_SIZE and root.get('data-size') != 'symbol':
            found.add('small')
    if len(roles['line']) + len(roles['detail']) > MAX_STROKED and root.get('data-detail') != 'reviewed':
        found.add('detail')
    if over_keyline(root):
        found.add('keyline')
    if bad_slash(path, name, roles):
        found.add('slash')
    if bad_badge(path, name, roles, root):
        found.add('badge')
    return name, sorted(found)


def main(args):
    update = '--update-baseline' in args
    show_all = '--all' in args
    names = [a for a in args if not a.startswith('--')]
    files = [os.path.join(SRC, n + '.svg') for n in names] if names else \
        [os.path.join(SRC, f) for f in sorted(os.listdir(SRC)) if f.endswith('.svg')]

    results = {}
    for path in files:
        try:
            name, found = check(path)
        except (ET.ParseError, ValueError, TypeError) as e:
            name, found = os.path.basename(path)[:-4], ['parse: ' + str(e)]
        if found:
            results[name] = found

    if update:
        if names:
            raise SystemExit('--update-baseline checks every icon; drop the icon names')
        # The baseline only shrinks: it holds the icons waiting for a redraw, never new problems.
        old = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
        grown = {n: [r for r in rs if r not in old.get(n, [])] for n, rs in results.items()}
        grown = {n: rs for n, rs in grown.items() if rs}
        if grown:
            raise SystemExit('--update-baseline would add problems; fix these icons instead:\n' +
                             '\n'.join(f'  {n}: {", ".join(rs)}' for n, rs in sorted(grown.items())))
        # One icon per line keeps baseline diffs readable in review.
        with open(BASELINE, 'w') as fh:
            fh.write('{\n' + ',\n'.join(f'{json.dumps(n)}: {json.dumps(rs)}' for n, rs in sorted(results.items()))
                     + '\n}\n')
        print(f'baseline: {len(results)} icons with known problems')
        return 0

    baseline = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    new = {n: [r for r in rs if show_all or r not in baseline.get(n, [])] for n, rs in results.items()}
    new = {n: rs for n, rs in new.items() if rs}
    for n, rs in sorted(new.items()):
        print(f'{n}: ' + '; '.join(f'{r} ({RULES.get(r, "")})' if r in RULES else r for r in rs))

    counts = {}
    for rs in new.values():
        for r in rs:
            counts[r] = counts.get(r, 0) + 1
    label = 'problems' if show_all else 'new problems'
    print(f'{len(files)} icons checked, {len(new)} with {label}' +
          (': ' + ', '.join(f'{r} {c}' for r, c in sorted(counts.items(), key=lambda x: -x[1])) if counts else ''))
    return 1 if new and not show_all else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
