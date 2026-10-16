"""Drawing helpers for authoring Icon Monks sources (256-unit grid).

Write a batch script that imports these helpers, calls icon(...) for each new icon, then save().
Each call becomes icons/<name>.svg. Roles decide how every weight is generated:

  line    stroked in outline weights (8/12/16/24), merged into the fill weight
  detail  stroked in outline weights, knocked out of the fill weight (inner details of a filled shape)
  area    duotone tint (20%), merged into the fill weight; usually the closed silhouette
  hole    cut out of the fill weight only (e.g. the inside of a door)
  dot     solid dot whose radius scales with weight, merged into fill (source r=16 renders r=12 at regular)
  dotcut  solid dot in outline weights, knocked out of the fill weight

Rules: live area 32..224 (strokes reach 24..232 at regular), 16-unit strokes, round caps and joins.
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s

def pt(p):
    return f'{f(p[0])} {f(p[1])}'

def rot(points, deg, c=(128, 128)):
    a = math.radians(deg)
    out = []
    for x, y in points:
        dx, dy = x - c[0], y - c[1]
        out.append((c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a)))
    return out

def poly(points, close=False):
    d = 'M' + ' L'.join(pt(p) for p in points)
    return d + (' Z' if close else '')

def P(d):
    return f'<path d="{d}"/>'

def C(cx, cy, r):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>'

def R(x, y, w, h, rx=0):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"' + (f' rx="{f(rx)}"' if rx else '') + '/>'

def E(cx, cy, rx, ry):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"/>'

def L(x1, y1, x2, y2):
    return P(f'M{f(x1)} {f(y1)} L{f(x2)} {f(y2)}')

def PL(points):
    return P(poly(points))

def PG(points):
    return P(poly(points, True))

def polar(c, r, deg):
    a = math.radians(deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))

def arc_to(c, r, p, q, prefer):
    """SVG arc command from p to q on circle (c, r); prefer(mid) -> score, higher wins."""
    a1 = math.atan2(p[1] - c[1], p[0] - c[0])
    a2 = math.atan2(q[1] - c[1], q[0] - c[0])
    span1 = (a2 - a1) % (2 * math.pi)  # sweep=1 (increasing angle)
    cands = []
    for sweep, span in ((1, span1), (0, 2 * math.pi - span1)):
        mid = a1 + (span / 2 if sweep else -span / 2)
        m = (c[0] + r * math.cos(mid), c[1] + r * math.sin(mid))
        cands.append((prefer(m), sweep, span))
    _, sweep, span = max(cands)
    large = 1 if span > math.pi else 0
    return f'A{f(r)} {f(r)} 0 {large} {sweep} {pt(q)}'

def circle_x(c1, r1, c2, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    p1 = (mx + h * dy / d, my - h * dx / d)
    p2 = (mx - h * dy / d, my + h * dx / d)
    return sorted([p1, p2], key=lambda p: p[1])  # upper first

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def capsule(cn, h, r, u):
    """Closed pill outline centred at cn, axis unit vector u, half straight length h, radius r."""
    n = (-u[1], u[0])
    A = (cn[0] - u[0] * h, cn[1] - u[1] * h); B = (cn[0] + u[0] * h, cn[1] + u[1] * h)
    a1 = (A[0] + n[0] * r, A[1] + n[1] * r); b1 = (B[0] + n[0] * r, B[1] + n[1] * r)
    b2 = (B[0] - n[0] * r, B[1] - n[1] * r); a2 = (A[0] - n[0] * r, A[1] - n[1] * r)
    far = lambda m: dist(m, cn)
    return (f'M{pt(a1)} L{pt(b1)} ' + arc_to(B, r, b1, b2, far) + f' L{pt(a2)} ' + arc_to(A, r, a2, a1, far) + ' Z')


def regular_polygon(c, r, n, start=-90):
    return [polar(c, r, start + i * 360 / n) for i in range(n)]


ICONS = []


def icon(name, category, tags, line=(), detail=(), area=(), hole=(), dot=(), dotcut=()):
    ICONS.append(dict(name=name, category=category, tags=list(tags), line=list(line), detail=list(detail),
                      area=list(area), hole=list(hole), dot=list(dot), dotcut=list(dotcut)))


def _group(role, items, attrs):
    if not items:
        return ''
    return f'  <g data-role="{role}" {attrs}>\n' + ''.join(f'    {i}\n' for i in items) + '  </g>\n'


STROKE = 'fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"'


def load(name):
    """Return the source elements of an existing icon by role, e.g. load('bell')['line'], to build variants on it."""
    import re
    src = open(os.path.join(ROOT, 'icons', name + '.svg')).read()
    out = {r: [] for r in ('line', 'detail', 'area', 'hole', 'dot', 'dotcut')}
    for role, body in re.findall(r'<g data-role="(\w+)"[^>]*>(.*?)</g>', src, re.S):
        out[role] = [e.strip() for e in re.findall(r'<(?:path|circle|rect|ellipse)\b[^>]*/>', body)]
    return out


def _protected():
    # Optional list of names that batch scripts must never overwrite (written before parallel drawing runs).
    p = os.path.join(ROOT, '.protected-icons')
    return set(open(p).read().split()) if os.path.exists(p) else set()


def save(overwrite=False):
    """Write every icon() registered so far to icons/<name>.svg. Returns the list of names."""
    out = os.path.join(ROOT, 'icons')
    names = []
    protected = _protected()
    for ic in ICONS:
        path = os.path.join(out, ic['name'] + '.svg')
        if ic['name'] in protected:
            raise SystemExit(f'{ic["name"]} is an existing icon; pick another name')
        if os.path.exists(path) and not overwrite:
            raise SystemExit(f'{ic["name"]} already exists; pick another name or pass overwrite=True')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" '
               f'data-category="{ic["category"]}" data-tags="{",".join(ic["tags"])}">\n'
               + _group('area', ic['area'], 'fill="currentColor" opacity="0.2"')
               + _group('hole', ic['hole'], 'fill="none"')
               + _group('line', ic['line'], STROKE)
               + _group('detail', ic['detail'], STROKE)
               + _group('dot', ic['dot'], 'fill="currentColor"')
               + _group('dotcut', ic['dotcut'], 'fill="currentColor"')
               + '</svg>\n')
        with open(path, 'w') as fh:
            fh.write(svg)
        names.append(ic['name'])
    ICONS.clear()
    return names
