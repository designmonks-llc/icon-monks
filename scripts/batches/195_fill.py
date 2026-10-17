"""Give a fill weight to icons that had none (their fill was just the regular outline).

Outer closed shapes in the line group are copied into 'area', so they fill. Closed shapes and open strokes that sit
inside an outer shape move to 'detail', so they cut out of the fill instead of disappearing into it.
Icons that read better as outlines in every weight (letters, numbers, typographic symbols) are marked
data-fill="outline" instead, which records the decision for the lint.

  python3 scripts/batches/195_fill.py name ...            # auto-fill these icons
  python3 scripts/batches/195_fill.py --outline name ...  # mark these as outline-only
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT
import lint

STROKE = ('fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"')
ELEMENT = re.compile(r'<(?:path|circle|rect|ellipse)\b[^>]*/>')


def outline_points(el):
    """Points along an element's outline, from the lint's path sampler."""
    import xml.etree.ElementTree as ET
    node = ET.fromstring(el.replace('/>', ' xmlns="http://www.w3.org/2000/svg"/>', 1))
    tag = node.tag.split('}')[1]
    if tag == 'path':
        pts, _, closed = lint.walk(node.get('d'))
        return pts, closed
    if tag == 'rect':
        x, y, w, h = (float(node.get(k)) for k in ('x', 'y', 'width', 'height'))
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True
    cx, cy = float(node.get('cx')), float(node.get('cy'))
    rx = float(node.get('r') or node.get('rx'))
    ry = float(node.get('r') or node.get('ry'))
    import math
    return [(cx + rx * math.cos(a / 32 * math.tau), cy + ry * math.sin(a / 32 * math.tau)) for a in range(32)], True


def inside(p, poly):
    x, y, hit = p[0], p[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def contained(pts, poly):
    return sum(inside(p, poly) for p in pts) >= 0.9 * len(pts)


def autofill(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    m = re.search(r'(  <g data-role="line"[^>]*>\n)(.*?)(  </g>\n)', src, re.S)
    els = ELEMENT.findall(m.group(2))
    shapes = [(e,) + outline_points(e) for e in els]
    outers = [(e, pts) for e, pts, closed in shapes if closed and len(pts) > 2 and
              not any(o is not e and oc and contained(pts, opts) for o, opts, oc in shapes)]
    detail = [e for e, pts, _ in shapes if any(o is not e and contained(pts, opts) for o, opts in outers)]
    if not outers:
        return False
    line = [e for e in els if e not in detail]
    groups = {'area': [e for e, _ in outers], 'line': line, 'detail': detail}
    old_detail = re.search(r'  <g data-role="detail"[^>]*>\n(.*?)  </g>\n', src, re.S)
    if old_detail:
        groups['detail'] = ELEMENT.findall(old_detail.group(1)) + groups['detail']
        src = src.replace(old_detail.group(0), '')
    head = src[:src.index('\n') + 1]
    rest = src[len(head):].replace(m.group(0), '')
    body = (f'  <g data-role="area" fill="currentColor" opacity="0.2">\n' +
            ''.join(f'    {e}\n' for e in groups['area']) + '  </g>\n' +
            f'  <g data-role="line" {STROKE}>\n' + ''.join(f'    {e}\n' for e in groups['line']) + '  </g>\n' +
            (f'  <g data-role="detail" {STROKE}>\n' + ''.join(f'    {e}\n' for e in groups['detail']) + '  </g>\n'
             if groups['detail'] else ''))
    open(path, 'w').write(head + body + rest)
    return True


def mark_outline(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    if 'data-fill="outline"' not in src:
        open(path, 'w').write(src.replace('<svg ', '<svg data-fill="outline" ', 1))


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--outline':
        for n in args[1:]:
            mark_outline(n)
    else:
        for n in args:
            print(n, 'filled' if autofill(n) else 'skipped: no outer closed shape')
