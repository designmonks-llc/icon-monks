#!/usr/bin/env python3
"""Measure every icon for consistency and list the outliers. Standard library only.

  python3 scripts/audit.py              # summary
  python3 scripts/audit.py report.md    # summary plus every outlier by name

Checks:
  stroke   line/detail/slash/badge groups use stroke-width 16 with round caps and joins; no element overrides them
           and nothing carries a transform (a scaled shape would scale its stroke)
  size     objects whose larger side spans under 168 units look smaller than their neighbours (glyphs, symbols and
           level families excepted, see undersized())
  centre   the geometry box sits 6 or more units off the canvas centre (variants and aligned families excepted)
  corners  rounded corners off STYLE.md rule 8 (16 on shapes 64+ units on both sides, 8 on smaller parts)
  dots     dot radii other than 16 and dotcut radii other than 14 (reported only: small dots in grids and dashes
           are smaller on purpose)

scripts/batches/235_consistency.py fixes size, centre and corners.
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint

ROOT = lint.ROOT
ICONS = lint.SRC
SMALL = 168        # larger side below this is undersized
OFF_CENTRE = 6     # box centre this far off (128, 128) is off-centre

# Meant to sit smaller than an object: glyphs, maths, typography, carets, dot grids, levels, media transport.
SMALL_OK = re.compile(r'^(caret|equals|equal-|approximate|congruent|greater|less|subset|superset|plus-minus|percent|'
                      r'math-|tally|dots-|numpad|cell-signal|speaker-|text-|sigma|alpha|pi$|pi-|function|currency-|'
                      r'zodiac-|alphabet-|om$|at$|question-mark|regex|variable-|prescription|fahrenheit|celsius|'
                      r'speed-|exponent|average|line-|stroke-|key-return|u-turn|corner-|play|pause|skip-|eject|stop$|'
                      r'stop-|minus$|plus$|x$|check$|divide|asterisk|hash|infinity|dot$|dot-|braille)|-calligraphy$')
SMALL_OK_CATEGORIES = {'Letters & Numbers', 'Arrows'}
# Families whose members line up with each other on purpose, and optically centred triangles.
CENTRE_OK = re.compile(r'^(cell-signal|speaker-|wifi-(none|low|medium|high)$|line-cap|play$|play-reverse$)')
# Icons that are about corner shape.
CORNER_OK = re.compile(r'corner|radius|squircle|rounded|line-join|border-')


def svg_root(name):
    return lint.ET.parse(os.path.join(ICONS, name + '.svg')).getroot()


def bounds(root, skip=('slash', 'badge')):
    pts = []
    for g in root:
        if g.get('data-role') in skip:
            continue
        for el in g:
            pts += lint.role_shape(g.get('data-role'), el)[0]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def elements(name):
    src = open(os.path.join(ICONS, name + '.svg')).read()
    out = []
    for g in re.finditer(r'<g data-role="(\w+)"[^>]*>(.*?)</g>', src, re.S):
        if g.group(1) not in ('slash', 'badge'):
            out += [(g.group(1), e) for e in re.findall(r'<(?:path|circle|ellipse|rect)[^>]*/>', g.group(2))]
    return out


def rebuilt_variant(name):
    """A -slash or standard-badge icon: 194_slash.py / 200_badges.py rebuild it from its base."""
    src = open(os.path.join(ICONS, name + '.svg')).read()
    if 'data-role="badge"' in src:
        return True
    return name.endswith('-slash') and name not in lint.NO_BASE_SLASH and \
        os.path.exists(os.path.join(ICONS, name[:-6] + '.svg'))


_bases = {}


def custom_base(name):
    """The base of a custom variant (data-badge="custom", or most of the base's shapes repeated unchanged), else None."""
    if name in _bases:
        return _bases[name]
    found = None
    if not rebuilt_variant(name):
        parts = name.split('-')
        custom = 'data-badge="custom"' in open(os.path.join(ICONS, name + '.svg')).read(400)
        mine = None
        for k in range(len(parts) - 1, 0, -1):
            base = '-'.join(parts[:k])
            if not os.path.exists(os.path.join(ICONS, base + '.svg')):
                continue
            mine = mine or set(elements(name))
            theirs = elements(base)
            shared = sum(e in mine for e in theirs)
            if theirs and (shared >= 0.5 * len(theirs) or (custom and k == len(parts) - 1)):
                found = base
                break
    _bases[name] = found
    return found


# Suffixes that add a mark to a base icon (file-lock, chat-sparkle) rather than name a different thing (hand-pinky).
MODIFIER = re.compile(r'^(sparkle|currency-[a-z]+|bitcoin|lightning|pause|pencil|arrow-(up|down|left|right)|code|'
                      r'push-pin|lock|lock-open|share|magnifying-glass|shield|x|discount|percent|plus|minus|clock|'
                      r'check|prohibit|question|warning|info|microphone|arrow-clockwise|reply|star|wrench|bookmark|'
                      r'paperclip|gear|heart|wifi|wifi-slash|tap|hand|sync|map-pin|tilde|charging|eye|trash|user|'
                      r'gavel|stamp|phone|sad|smile|export|import|snooze|forward|cloud|electric|medical|image|bluetooth|usb|'
                      r'send|receive|refund)$')


BASE_OVERRIDE = {'heart-arrow-down': 'heart', 'heart-arrow-up': 'heart'}  # a heart with an arrow badge, not heart-arrow


def variant_base(name):
    """The base icon a variant is drawn from (it should sit where its base sits), else None."""
    if name in BASE_OVERRIDE:
        return BASE_OVERRIDE[name]
    b = custom_base(name)
    if b:
        return b
    parts = name.split('-')
    for k in range(len(parts) - 1, 0, -1):
        base = '-'.join(parts[:k])
        if os.path.exists(os.path.join(ICONS, base + '.svg')) and MODIFIER.match('-'.join(parts[k:])):
            return base
    return None


def undersized(name, root):
    if root.get('data-size') == 'symbol' or root.get('data-category') in SMALL_OK_CATEGORIES or SMALL_OK.search(name):
        return False
    x0, y0, x1, y1 = bounds(root)
    return max(x1 - x0, y1 - y0) < SMALL


def centre_exempt(name):
    return bool(CENTRE_OK.search(name))


def corner_exempt(name):
    return bool(CORNER_OK.search(name))


def bad_stroke(src):
    for g in re.finditer(r'<g data-role="(line|detail|slash|badge)"([^>]*)>(.*?)</g>', src, re.S):
        attrs = g.group(2)
        if 'stroke-width="16"' not in attrs or 'stroke-linecap="round"' not in attrs or \
                'stroke-linejoin="round"' not in attrs:
            return True
        if re.search(r'stroke|style=', g.group(3)):
            return True
    return bool(re.search(r'transform=|style=', src))


def off_corners(name):
    """Corner radii that differ from rule 8, as a list of (radius, wanted)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('c', os.path.join(ROOT, 'scripts', 'batches', '235_consistency.py'))
    global _cons
    if '_cons' not in globals():
        _cons = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_cons)
    src = open(os.path.join(ICONS, name + '.svg')).read()
    out = []
    for g in re.finditer(r'<g data-role="(\w+)"[^>]*>(.*?)</g>', src, re.S):
        if g.group(1) in ('slash', 'badge', 'dot', 'dotcut'):
            continue
        for m in re.finditer(r'<rect\s([^>]*?)/>', g.group(2)):
            a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
            if 'rx' in a:
                r = _cons.corner_radius(float(a['width']), float(a['height']), float(a['rx']))
                if r is not None and r != float(a['rx']):
                    out.append((float(a['rx']), r))
        for d in re.findall(r'<path d="([^"]*)"', g.group(2)):
            segs = _cons.parse(d)
            fixed, n = _cons.fix_corners_d(d)
            if n:
                after = _cons.parse(fixed)
                out += [(s['a'][0], t['a'][0]) for s, t in zip(segs, after) if s['cmd'] == 'A' and s['a'][0] != t['a'][0]]
    return out


def audit():
    names = sorted(n[:-4] for n in os.listdir(ICONS) if n.endswith('.svg'))
    found = {k: {} for k in ('stroke', 'size', 'centre', 'corners', 'dots')}
    for n in names:
        root = svg_root(n)
        src = open(os.path.join(ICONS, n + '.svg')).read()
        if bad_stroke(src):
            found['stroke'][n] = 'stroke attributes'
        if rebuilt_variant(n):
            continue
        x0, y0, x1, y1 = bounds(root)
        variant = variant_base(n) or root.get('data-badge') == 'custom'
        if not variant and undersized(n, root):
            found['size'][n] = f'{max(x1 - x0, y1 - y0):.0f}'
        ox, oy = (x0 + x1) / 2 - 128, (y0 + y1) / 2 - 128
        if not variant and not centre_exempt(n) and max(abs(ox), abs(oy)) >= OFF_CENTRE:
            found['centre'][n] = f'{ox:+.0f},{oy:+.0f}'
        if not corner_exempt(n):
            c = off_corners(n)
            if c:
                found['corners'][n] = ', '.join(f'{a:g}→{b:g}' for a, b in c)
        dots = []
        for g in root:
            if g.get('data-role') in ('dot', 'dotcut'):
                want = 16 if g.get('data-role') == 'dot' else 14
                dots += [float(e.get('r')) for e in g if float(e.get('r')) != want]
        if dots:
            found['dots'][n] = ', '.join(f'{r:g}' for r in dots)
    return names, found


def main(args):
    names, found = audit()
    print(f'{len(names)} icons audited')
    for k, v in found.items():
        print(f'  {k:8} {len(v)}')
    if args:
        with open(args[0], 'w') as fh:
            fh.write(f'# Icon consistency audit\n\n{len(names)} icons. See the docstring of scripts/audit.py for the '
                     'checks.\n')
            for k, v in found.items():
                fh.write(f'\n## {k} ({len(v)})\n\n')
                fh.write('\n'.join(f'- `{n}` {d}' for n, d in sorted(v.items())) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
