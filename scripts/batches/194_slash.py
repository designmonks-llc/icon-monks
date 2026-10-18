"""One slash pattern for every <name>-slash icon: the unchanged base icon <name> plus a 'slash' group holding one line.
The build cuts the gap around the slash (SLASH_GAP in build.py), so slash icons can no longer drift from their base.

The slash is M48 48 L208 208. Icons whose base already runs along that diagonal (a magnifier handle, corner arrows,
a cursor) take the mirrored M208 48 L48 208, so the slash doesn't lie on the icon's own stroke.
Slash icons without a base icon (file-eye-slash, cell-signal-slash) draw a partial slash as part of the glyph and
are left alone.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT

SLASH, MIRRORED = 'M48 48 L208 208', 'M208 48 L48 208'
MARKS = ('data-fill="outline"', 'data-detail="reviewed"', 'data-size="symbol"')
MIRROR = {'analyze-slash', 'corners-out-slash', 'cursor-slash', 'find-replace-slash', 'magnifying-glass-slash'}
GROUP = ('  <g data-role="slash" fill="none" stroke="currentColor" stroke-width="16" stroke-linecap="round" '
         'stroke-linejoin="round">\n    <path d="{}"/>\n  </g>\n')


def rebuild(name):
    icons = os.path.join(ROOT, 'icons')
    src = open(os.path.join(icons, name + '.svg')).read()
    base = open(os.path.join(icons, name[:-6] + '.svg')).read()
    head = re.match(r'<svg[^>]*>\n', src).group(0)          # keeps the slash icon's own category and tags
    for mark in MARKS:  # marks follow the base icon
        head = head.replace(mark + ' ', '')
        if mark in base[:base.index('>')]:
            head = head.replace('<svg ', f'<svg {mark} ', 1)
    body = base[re.match(r'<svg[^>]*>\n', base).end():base.rindex('</svg>')]
    slash = MIRRORED if name in MIRROR else SLASH
    new = head + body + GROUP.format(slash) + '</svg>\n'
    if new != src:
        open(os.path.join(icons, name + '.svg'), 'w').write(new)
        return True
    return False


if __name__ == '__main__':
    icons = os.path.join(ROOT, 'icons')
    import lint
    names = sorted(f[:-4] for f in os.listdir(icons)
                   if f.endswith('-slash.svg') and os.path.exists(os.path.join(icons, f[:-10] + '.svg'))
                   and f[:-4] not in lint.NO_BASE_SLASH)  # those draw their own partial slash
    print(sum(rebuild(n) for n in names), 'of', len(names), 'slash icons rebuilt from their base')
