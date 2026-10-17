"""Snap anchors onto whole grid units: path endpoints, circle centres and rect corners.

Curve handles move with the anchor they belong to, so tangents keep their direction. Arc radii and curve handles
keep up to two decimals. Radii of circles and rects are rounded too when that changes them by less than half a unit.

  python3 scripts/batches/197_grid.py            # every icon
  python3 scripts/batches/197_grid.py name ...   # these icons
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT, f

ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


def snap_d(d):
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?', d)
    out, i, cmd = [], 0, 'M'
    dx = dy = 0.0         # how far the current point moved
    sdx = sdy = 0.0       # how far the subpath start moved (the current point after Z)
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == 'Z':
                out.append('Z')
                dx, dy = sdx, sdy
                continue
        a = [float(v) for v in toks[i:i + ARGS[cmd]]]
        i += ARGS[cmd]
        if cmd == 'H':
            nx = round(a[0])
            out.append(f'H{f(nx)}')
            dx = nx - a[0]
        elif cmd == 'V':
            ny = round(a[0])
            out.append(f'V{f(ny)}')
            dy = ny - a[0]
        else:
            ex, ey = a[-2], a[-1]
            nx, ny = round(ex), round(ey)
            mx, my = nx - ex, ny - ey
            if cmd in 'CS':
                ctl = [(a[j], a[j + 1]) for j in range(0, len(a) - 2, 2)]
                if cmd == 'C':  # first handle belongs to the start point, the last to the end point
                    ctl = [(ctl[0][0] + dx, ctl[0][1] + dy), (ctl[1][0] + mx, ctl[1][1] + my)]
                else:
                    ctl = [(ctl[0][0] + mx, ctl[0][1] + my)]
                v = [c for p in ctl for c in (round(p[0], 2), round(p[1], 2))] + [nx, ny]
            elif cmd == 'Q':
                v = [round(a[0] + (dx + mx) / 2, 2), round(a[1] + (dy + my) / 2, 2), nx, ny]
            elif cmd == 'A':
                v = a[:5] + [nx, ny]
                v[3], v[4] = int(v[3]), int(v[4])
            else:
                v = [nx, ny]
            out.append(cmd + ' '.join(f(c) if isinstance(c, float) else str(c) for c in v))
            dx, dy = mx, my
        if cmd == 'M':
            sdx, sdy = dx, dy
            cmd = 'L'
    return ' '.join(out)


def snap_el(m):
    tag, attrs = m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))
    near = lambda v: f(round(float(v))) if abs(float(v) - round(float(v))) < 0.5 else v
    if tag == 'path':
        attrs['d'] = snap_d(attrs['d'])
    elif tag in ('circle', 'ellipse'):
        for k in ('cx', 'cy'):
            attrs[k] = f(round(float(attrs[k])))
        for k in ('r', 'rx', 'ry'):
            if k in attrs:
                attrs[k] = near(attrs[k])
    elif tag == 'rect':
        x0, y0 = round(float(attrs['x'])), round(float(attrs['y']))
        x1 = round(float(attrs['x']) + float(attrs['width']))
        y1 = round(float(attrs['y']) + float(attrs['height']))
        attrs.update(x=f(x0), y=f(y0), width=f(x1 - x0), height=f(y1 - y0))
        for k in ('rx', 'ry'):
            if k in attrs:
                attrs[k] = near(attrs[k])
    return f'<{tag} ' + ' '.join(f'{k}="{v}"' for k, v in attrs.items()) + '/>'


def snap(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    head = src[:src.index('>') + 1]
    new = head + re.sub(r'<(path|circle|ellipse|rect)\s([^>]*?)/>', snap_el, src[len(head):])
    if new != src:
        open(path, 'w').write(new)
        return True
    return False


if __name__ == '__main__':
    icons = os.path.join(ROOT, 'icons')
    names = sys.argv[1:] or sorted(n[:-4] for n in os.listdir(icons) if n.endswith('.svg'))
    print(sum(snap(n) for n in names), 'icons snapped to the grid')
