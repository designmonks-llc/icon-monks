"""Keylines: the same visual size for every icon, whatever its shape.

A square container drawn as big as a circle looks bigger than the circle, so containers get the keyline for their
shape (centrelines on the 256 grid; strokes and dot sizes don't scale):

  circle                       192 diameter
  square (aspect 0.9 to 1.1)   176 on each side
  wider or taller rectangle    192 on the long side
  anything else                the 32..224 live area

An icon over its keyline, or outside the live area, is scaled down about the centre of its geometry and then moved
the least amount that brings it inside the live area. Coordinates are rounded back onto whole units.

  python3 scripts/batches/196_keylines.py            # fix every icon
  python3 scripts/batches/196_keylines.py name ...   # fix these
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT, f
import lint

CIRCLE, SQUARE, RECT = 192, 176, 192
LIVE = (32, 224)
ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


container = lint.container


def bounds(root):
    pts = []
    for g in root:
        if g.get('data-role') == 'slash':
            continue
        for el in g:
            pts += lint.role_shape(g.get('data-role'), el)[0]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def plan(root):
    """(scale, dx, dy) to apply about the geometry centre, or None when the icon already fits."""
    x0, y0, x1, y1 = bounds(root)
    s = 1.0
    c = container(root)
    if c:
        kind, w, h = c
        limit = CIRCLE if kind == 'circle' else SQUARE if 0.9 <= w / h <= 1 / 0.9 else RECT
        if lint.over_keyline(root):
            s = min(s, limit / max(w, h))
    s = min(s, (LIVE[1] - LIVE[0] + 2 * lint.LIVE_TOL) / max(x1 - x0, y1 - y0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    nx0, nx1 = cx + (x0 - cx) * s, cx + (x1 - cx) * s
    ny0, ny1 = cy + (y0 - cy) * s, cy + (y1 - cy) * s
    lo, hi = LIVE[0] - lint.LIVE_TOL, LIVE[1] + lint.LIVE_TOL
    dx = max(0, lo - nx0) - max(0, nx1 - hi)
    dy = max(0, lo - ny0) - max(0, ny1 - hi)
    if s > 0.999 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return None
    return s, round(dx), round(dy), cx, cy


def transform_d(d, T, S):
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?', d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            out.append(cmd)
            if cmd == 'Z':
                continue
        a = [float(v) for v in toks[i:i + ARGS[cmd]]]
        i += ARGS[cmd]
        if cmd in 'MLT':
            v = T(a[0], a[1], True)
        elif cmd == 'H':
            v = [round(T(a[0], 0, True)[0])]
        elif cmd == 'V':
            v = [round(T(0, a[0], True)[1])]
        elif cmd == 'A':
            v = [S(a[0]), S(a[1]), a[2], int(a[3]), int(a[4])] + T(a[5], a[6], True)
        else:
            v = sum((T(a[j], a[j + 1], False) for j in range(0, len(a) - 2, 2)), []) + T(a[-2], a[-1], True)
        out.append(' '.join(f(x) for x in v))
        if cmd == 'M':
            cmd = 'L'
    return re.sub(r'([A-Za-z]) ', r'\1', ' '.join(out)).replace(' Z', ' Z')


def apply(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    root = lint.ET.parse(path).getroot()
    p = plan(root)
    if not p:
        return False
    s, dx, dy, cx, cy = p

    def T(x, y, anchor):
        nx, ny = cx + (x - cx) * s + dx, cy + (y - cy) * s + dy
        return [round(nx), round(ny)] if anchor else [round(nx, 2), round(ny, 2)]

    def S(r):
        return round(r * s) if abs(r * s - round(r * s)) < 0.25 else round(r * s, 2)

    src = open(path).read()
    head, body = src[:src.index('>') + 1], src[src.index('>') + 1:]
    groups = re.split(r'(<g data-role="\w+")', body)
    role = None
    parts = []
    for chunk in groups:
        m = re.match(r'<g data-role="(\w+)"', chunk)
        if m:
            role = m.group(1)
            parts.append(chunk)
            continue
        if role == 'slash':
            parts.append(chunk)
            continue

        def el(m):
            tag, attrs = m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))
            if tag == 'path':
                attrs['d'] = transform_d(attrs['d'], T, S)
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
    open(path, 'w').write(head + ''.join(parts))
    return True


if __name__ == '__main__':
    icons = os.path.join(ROOT, 'icons')
    names = sys.argv[1:] or sorted(n[:-4] for n in os.listdir(icons) if n.endswith('.svg') and
                                   not (n.endswith('-slash.svg') and os.path.exists(os.path.join(icons, n[:-10] + '.svg'))))
    changed = [n for n in names if apply(n)]
    print(len(changed), 'icons resized or moved onto their keyline')
