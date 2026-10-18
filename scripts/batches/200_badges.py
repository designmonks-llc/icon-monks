"""One badge pattern for <base>-<modifier> icons (plus, minus, x, check, warning, heart, ...; see lint.BADGES).

A variant whose modifier sits as a corner badge today is rebuilt as its base icon unchanged plus the standard badge
group; the build cuts BADGE_GAP of clear space around it. A variant that draws the modifier into the icon (a lock
inside a file, an arrow inside a cloud, a hand holding a heart) is marked data-badge="custom" and left as drawn.

Corner or not is read from the current regular outputs: the ink the variant adds to its base must sit mostly in the
bottom-right quarter. Run scripts/build.py first so svg/regular/ is current.

  python3 scripts/batches/200_badges.py            # every variant
  python3 scripts/batches/200_badges.py name ...   # these variants
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT
import lint

MARKS = ('data-fill="outline"', 'data-detail="reviewed"', 'data-size="symbol"')
GROUP = ('  <g data-role="badge" fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" '
         'stroke-linejoin="round">\n{}  </g>\n')
PX = 64


def ink(name, tmp):
    """Dark pixels of the regular output as a set of (x, y), rendered at PX."""
    from PIL import Image
    out = os.path.join(tmp, 'r.png')
    subprocess.run(['rsvg-convert', '-w', str(PX), '-h', str(PX), '-b', 'white',
                    os.path.join(ROOT, 'svg', 'regular', name + '.svg'), '-o', out], check=True)
    im = Image.open(out).convert('L')
    return {(x, y) for y in range(PX) for x in range(PX) if im.getpixel((x, y)) < 128}


def is_corner(name, base, tmp):
    added = ink(name, tmp) - ink(base, tmp)
    if len(added) < 12:
        return False
    corner = sum(1 for x, y in added if x >= PX * 0.55 and y >= PX * 0.55)
    return corner >= 0.7 * len(added)


def element(m):
    if isinstance(m, tuple):
        return f'<circle cx="{m[1]}" cy="{m[2]}" r="{m[3]}"/>'
    return f'<path d="{m}"/>'


def rebuild(name, mod):
    icons = os.path.join(ROOT, 'icons')
    src = open(os.path.join(icons, name + '.svg')).read()
    base = open(os.path.join(icons, name[:-len(mod) - 1] + '.svg')).read()
    head = re.match(r'<svg[^>]*>\n', src).group(0)  # keeps the variant's own category and tags
    head = head.replace('data-badge="custom" ', '')
    for mark in MARKS:  # marks follow the base icon
        head = head.replace(mark + ' ', '')
        if mark in base[:base.index('>')]:
            head = head.replace('<svg ', f'<svg {mark} ', 1)
    body = base[re.match(r'<svg[^>]*>\n', base).end():base.rindex('</svg>')]
    group = GROUP.format(''.join(f'    {element(m)}\n' for m in lint.BADGES[mod]))
    new = head + body + group + '</svg>\n'
    if new != src:
        open(os.path.join(icons, name + '.svg'), 'w').write(new)


def custom(name):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    if 'data-badge="custom"' not in src[:src.index('>')]:
        open(path, 'w').write(src.replace('<svg ', '<svg data-badge="custom" ', 1))


if __name__ == '__main__':
    icons = os.path.join(ROOT, 'icons')
    names = sys.argv[1:] or sorted(n[:-4] for n in os.listdir(icons) if n.endswith('.svg') and not n.endswith('-slash.svg'))
    corner, kept = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            mod = lint.badge_of(name, icons)
            if not mod:
                continue
            src = open(os.path.join(icons, name + '.svg')).read()
            if 'data-role="badge"' in src:  # already standard: rebuild from the current base
                rebuild(name, mod)
                corner.append(name)
            elif 'data-badge="custom"' in src[:src.index('>')]:
                kept.append(name)
            elif is_corner(name, name[:-len(mod) - 1], tmp):
                rebuild(name, mod)
                corner.append(name)
            else:
                custom(name)
                kept.append(name)
    print(len(corner), 'variants rebuilt with a standard corner badge;', len(kept), 'marked custom')
    with open(os.path.join(tempfile.gettempdir(), 'badges-corner.txt'), 'w') as fh:
        fh.write('\n'.join(corner))
