"""Mark the icons that pass a 16 px review although the lint flags them, so the lint can hard-fail everything else.

  data-detail="reviewed"  more than 8 strokes, but reads clearly at 16 px (dashed outlines, grids, sun rays)
  data-size="symbol"      meant to sit smaller than the keylines (carets, dot, x, operators)

Icons that failed the review are listed in REDRAW and stay in the lint baseline until they are redrawn.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import ROOT

REDRAW = {
    'bee', 'blockchain', 'bow', 'car-4wd', 'car-lifter', 'cheers', 'cloud-sun-hail', 'cloud-sun-rain', 'crab',
    'crossword', 'file-heic', 'file-html', 'file-key', 'file-tiff', 'go-game', 'hands-clapping', 'helicopter',
    'lighthouse', 'lockers', 'needle-thread', 'pagoda', 'skeleton', 'solar-panel', 'spider', 'sun-wind',
    'thermometer-hot', 'tiger', 'topology-star-ring', 'treadmill', 'treasure-map', 'uv-index', 'video-conference',
    'virus-magnifying-glass', 'voice-recognition', 'wall', 'wall-slash',
}
MARK = {'detail': 'data-detail="reviewed"', 'small': 'data-size="symbol"'}


def mark(name, attr):
    path = os.path.join(ROOT, 'icons', name + '.svg')
    src = open(path).read()
    if attr in src[:src.index('>')]:
        return False
    open(path, 'w').write(src.replace('<svg ', f'<svg {attr} ', 1))
    return True


if __name__ == '__main__':
    baseline = json.load(open(os.path.join(ROOT, 'scripts', 'lint-baseline.json')))
    n = sum(mark(name, MARK[rule]) for name, rules in sorted(baseline.items()) if name not in REDRAW
            for rule in rules if rule in MARK)
    print(n, 'marks added;', len(REDRAW), 'icons left to redraw')
