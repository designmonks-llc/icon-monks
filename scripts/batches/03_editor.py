import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CAT = 'Editor'

def mx(points):
    return [(256 - x, y) for x, y in points]

# ---------------------------------------------------------------- Alignment (4 lines, 48 apart)
ROWS4 = (56, 104, 152, 200)
def align(spans):
    return [L(a, y, b, y) for (a, b), y in zip(spans, ROWS4)]
FULL = (40, 216)
icon('text-align-left', CAT, ['align', 'left', 'paragraph', 'format'],
     line=align([FULL, (40, 160), FULL, (40, 160)]))
icon('text-align-center', CAT, ['align', 'center', 'middle', 'paragraph', 'format'],
     line=align([FULL, (72, 184), FULL, (72, 184)]))
icon('text-align-right', CAT, ['align', 'right', 'paragraph', 'format'],
     line=align([FULL, (96, 216), FULL, (96, 216)]))
icon('text-align-justify', CAT, ['align', 'justify', 'paragraph', 'format', 'block'],
     line=align([FULL] * 4))

# ---------------------------------------------------------------- Letterforms (stroked geometry)
b_top = 'M76 40 H136 A44 44 0 0 1 136 128 H76'
b_bot = 'M76 128 H148 A44 44 0 0 1 148 216 H76'
b_area = 'M76 40 H136 A44 44 0 0 1 180 84 A44 44 0 0 1 166 116 A44 44 0 0 1 148 216 H76 Z'
icon('text-b', CAT, ['bold', 'strong', 'format', 'font', 'weight'],
     line=[L(76, 40, 76, 216), P(b_top), P(b_bot)],
     area=[P('M76 40 H136 A44 44 0 0 1 136 128 H148 A44 44 0 0 1 148 216 H76 Z')],
     hole=[P('M100 64 H136 A20 20 0 0 1 136 104 H100 Z'), P('M100 152 H148 A20 20 0 0 1 148 192 H100 Z')])
icon('text-italic', CAT, ['italic', 'emphasis', 'slant', 'format', 'font'],
     line=[L(152, 48, 104, 208), L(112, 48, 192, 48), L(64, 208, 144, 208)])
icon('text-underline', CAT, ['underline', 'format', 'font', 'style'],
     line=[P('M80 40 V112 A48 48 0 0 0 176 112 V40'), L(56, 208, 200, 208)])
s_path = ('M176 72 C168 52 150 44 128 44 C100 44 80 58 80 84 C80 108 100 118 128 128 '
          'C156 138 176 148 176 172 C176 198 156 212 128 212 C106 212 88 204 80 184')
icon('text-strikethrough', CAT, ['strikethrough', 'strike', 'format', 'delete', 'font'],
     line=[P(s_path), L(40, 128, 216, 128)])
icon('text-t', CAT, ['text', 'type', 'font', 'typography', 'letter'],
     line=[PL([(56, 72), (56, 48), (200, 48), (200, 72)]), L(128, 48, 128, 208), L(96, 208, 160, 208)])
icon('text-h', CAT, ['heading', 'header', 'title', 'format', 'h1'],
     line=[L(64, 48, 64, 208), L(192, 48, 192, 208), L(64, 128, 192, 128)])

# quotes: two round marks with curled tails
def quote(cx):
    body = C(cx, 152, 32)
    tail = P(f'M{f(cx - 32)} 152 V136 C{f(cx - 32)} 100 {f(cx - 12)} 76 {f(cx + 24)} 68')
    return body, tail
qa = quote(76); qb = quote(180)
icon('quotes', CAT, ['quote', 'quotation', 'blockquote', 'citation', 'testimonial'],
     line=[qa[0], qa[1], qb[0], qb[1]], area=[C(76, 152, 32), C(180, 152, 32)])

bowl = 'M136 40 H108 A44 44 0 0 0 108 128 H136'
icon('paragraph', CAT, ['pilcrow', 'paragraph', 'text', 'format', 'section'],
     line=[P('M200 40 H108 A44 44 0 0 0 108 128 H136'), L(136, 40, 136, 216), L(184, 40, 184, 216)],
     area=[P(bowl + ' Z')])

# ---------------------------------------------------------------- Lists (rows at 64 / 128 / 192, like list-bullets)
icon('list-numbers', CAT, ['ordered', 'numbered', 'list', 'steps', 'ol'],
     line=[L(112, 64, 216, 64), L(112, 128, 216, 128), L(112, 192, 216, 192),
           PL([(40, 52), (60, 40), (60, 104)]),
           P('M40 156 A20 20 0 0 1 80 156 C80 176 40 196 40 208 H80')])
icon('list-checks', CAT, ['checklist', 'todo', 'tasks', 'list', 'done'],
     line=[L(120, 64, 216, 64), L(120, 128, 216, 128), L(120, 192, 216, 192)]
          + [PL([(36, y), (56, y + 18), (88, y - 18)]) for y in (64, 128, 192)])
icon('list-dashes', CAT, ['list', 'unordered', 'items', 'dashes'],
     line=[L(104, 64, 216, 64), L(104, 128, 216, 128), L(104, 192, 216, 192),
           L(40, 64, 64, 64), L(40, 128, 64, 128), L(40, 192, 64, 192)])

icon('text-indent', CAT, ['indent', 'increase', 'tab', 'format', 'paragraph'],
     line=[L(40, 56, 216, 56), L(120, 104, 216, 104), L(120, 152, 216, 152), L(40, 200, 216, 200),
           PL([(48, 96), (80, 128), (48, 160)])])
icon('text-outdent', CAT, ['outdent', 'decrease', 'unindent', 'format', 'paragraph'],
     line=[L(40, 56, 216, 56), L(120, 104, 216, 104), L(120, 152, 216, 152), L(40, 200, 216, 200),
           PL([(80, 96), (48, 128), (80, 160)])])

# ---------------------------------------------------------------- Layout & windows
WIN = R(32, 48, 192, 160, 14)
icon('table', CAT, ['grid', 'spreadsheet', 'data', 'cells', 'rows'],
     line=[WIN], detail=[L(32, 96, 224, 96), L(32, 152, 224, 152), L(96, 96, 96, 208)], area=[WIN])
icon('rows', CAT, ['rows', 'horizontal', 'stack', 'layout', 'split'],
     line=[R(40, 40, 176, 72, 12), R(40, 144, 176, 72, 12)], area=[R(40, 40, 176, 72, 12), R(40, 144, 176, 72, 12)])
icon('columns', CAT, ['columns', 'vertical', 'split', 'layout'],
     line=[R(40, 40, 72, 176, 12), R(144, 40, 72, 176, 12)], area=[R(40, 40, 72, 176, 12), R(144, 40, 72, 176, 12)])
icon('sidebar', CAT, ['panel', 'navigation', 'drawer', 'layout', 'menu'],
     line=[WIN], detail=[L(96, 48, 96, 208)], area=[WIN])
lay = [R(40, 40, 176, 56, 12), R(40, 128, 64, 88, 12), R(136, 128, 80, 88, 12)]
icon('layout', CAT, ['layout', 'wireframe', 'template', 'grid', 'blocks'], line=lay, area=lay)
kb = [R(32, 40, 40, 176, 10), R(108, 40, 40, 112, 10), R(184, 40, 40, 144, 10)]
icon('kanban', CAT, ['board', 'tasks', 'columns', 'project', 'trello'], line=kb, area=kb)
tab = ('M32 56 A16 16 0 0 1 48 40 H96 A16 16 0 0 1 112 56 V72 H208 A16 16 0 0 1 224 88 V200 '
       'A16 16 0 0 1 208 216 H48 A16 16 0 0 1 32 200 Z')
BWIN = R(32, 40, 192, 176, 14)
icon('browser', CAT, ['web', 'website', 'internet', 'url', 'page'],
     line=[BWIN], detail=[L(32, 104, 224, 104), L(104, 72, 192, 72)], area=[BWIN], dotcut=[C(64, 72, 10)])
icon('app-window', CAT, ['window', 'application', 'program', 'desktop'],
     line=[BWIN], detail=[L(32, 104, 224, 104)], area=[BWIN], dotcut=[C(68, 72, 13), C(108, 72, 13)])
icon('cards', CAT, ['cards', 'stack', 'deck', 'collection', 'carousel'],
     line=[R(32, 104, 192, 112, 14), L(56, 68, 200, 68), L(80, 32, 176, 32)],
     area=[R(32, 104, 192, 112, 14)])
fc = []
for (cx, cy), (sx, sy) in (((32, 32), (1, 1)), ((224, 32), (-1, 1)), ((224, 224), (-1, -1)), ((32, 224), (1, -1))):
    fc.append(P(f'M{f(cx)} {f(cy + sy * 56)} V{f(cy + sy * 16)} A16 16 0 0 {1 if sx * sy > 0 else 0} '
                f'{f(cx + sx * 16)} {f(cy)} H{f(cx + sx * 56)}'))
icon('frame-corners', CAT, ['frame', 'crop', 'focus', 'fit', 'artboard'],
     line=fc + [R(80, 80, 96, 96, 12)], area=[R(80, 80, 96, 96, 12)])

# ---------------------------------------------------------------- Language & code
icon('translate', CAT, ['translate', 'language', 'localization', 'i18n', 'international'],
     line=[L(32, 64, 136, 64), L(84, 40, 84, 64),
           P('M112 64 C104 104 80 136 40 156'), P('M60 96 C76 124 96 140 120 148'),
           PL([(128, 216), (172, 112), (216, 216)]), L(146, 176, 198, 176)])
icon('code-block', CAT, ['code', 'snippet', 'embed', 'developer', 'programming'],
     line=[WIN], detail=[PL([(100, 100), (72, 128), (100, 156)]), PL([(156, 100), (184, 128), (156, 156)])],
     area=[WIN])
lb = 'M108 40 H100 A20 20 0 0 0 80 60 V100 Q80 128 52 128 Q80 128 80 156 V196 A20 20 0 0 0 100 216 H108'
rb = 'M148 40 H156 A20 20 0 0 1 176 60 V100 Q176 128 204 128 Q176 128 176 156 V196 A20 20 0 0 1 156 216 H148'
icon('brackets-curly', CAT, ['braces', 'code', 'json', 'object', 'curly'], line=[P(lb), P(rb)])
icon('brackets-square', CAT, ['brackets', 'array', 'code', 'square'],
     line=[PL([(104, 40), (64, 40), (64, 216), (104, 216)]), PL([(152, 40), (192, 40), (192, 216), (152, 216)])])
icon('function', CAT, ['function', 'formula', 'math', 'fx', 'code'],
     line=[P('M188 60 C180 44 164 40 152 40 C136 40 128 52 124 68 L104 188 C100 204 92 216 76 216 C64 216 56 212 52 200'),
           L(88, 104, 172, 104)])

# ---------------------------------------------------------------- Cursors & hands
cur = [(96, 88), (216, 144), (160, 160), (144, 216)]
icon('cursor-click', CAT, ['click', 'tap', 'select', 'pointer', 'mouse'],
     line=[PG(cur), L(96, 32, 96, 56), L(32, 88, 56, 88), L(51, 43, 68, 60), L(141, 43, 124, 60), L(51, 133, 68, 116)],
     area=[PG(cur)])
icon('cursor-text', CAT, ['text cursor', 'i-beam', 'caret', 'type', 'input'],
     line=[P('M92 40 H108 A20 20 0 0 1 128 60 A20 20 0 0 1 148 40 H164'), L(128, 60, 128, 196),
           P('M92 216 H108 A20 20 0 0 0 128 196 A20 20 0 0 0 148 216 H164'), L(104, 128, 152, 128)])

def palm_end():
    # right side down to wrist, heel, and thumb back up to index base at (76, 136)
    return ('V152 C220 196 192 224 152 224 H132 C108 224 92 214 78 196 L40 146 '
            'A18 18 0 0 1 68 124 L76 134')
hand = ('M76 134 V82 A18 18 0 0 1 112 82 V58 A18 18 0 0 1 148 58 V70 A18 18 0 0 1 184 70 V98 '
        'A18 18 0 0 1 220 98 ' + palm_end() + ' Z')
icon('hand', CAT, ['palm', 'stop', 'wave', 'hello', 'pan'],
     line=[P(hand)], detail=[L(112, 82, 112, 132), L(148, 70, 148, 132), L(184, 98, 184, 132)], area=[P(hand)])
point = ('M76 134 V58 A18 18 0 0 1 112 58 V112 A18 18 0 0 1 148 112 V116 A18 18 0 0 1 184 116 V122 '
         'A18 18 0 0 1 220 122 ' + palm_end() + ' Z')
icon('hand-pointing', CAT, ['point', 'click', 'tap', 'finger', 'link'],
     line=[P(point)], detail=[L(148, 116, 148, 150), L(184, 122, 184, 150)], area=[P(point)])
fist = ('M76 134 V110 A18 18 0 0 1 112 110 V102 A18 18 0 0 1 148 102 V106 A18 18 0 0 1 184 106 V114 '
        'A18 18 0 0 1 220 114 ' + palm_end() + ' Z')
icon('hand-grabbing', CAT, ['grab', 'drag', 'fist', 'move', 'grip'],
     line=[P(fist)], detail=[L(112, 110, 112, 150), L(148, 106, 148, 150), L(184, 114, 184, 150)], area=[P(fist)])

# ---------------------------------------------------------------- Documents
icon('article', CAT, ['article', 'post', 'blog', 'document', 'news'],
     line=[R(48, 32, 160, 192, 14)],
     detail=[L(88, 76, 168, 76), L(88, 112, 168, 112), L(88, 148, 168, 148), L(88, 184, 136, 184)],
     area=[R(48, 32, 160, 192, 14)])
icon('notepad', CAT, ['notes', 'memo', 'notebook', 'jot', 'pad'],
     line=[R(48, 48, 160, 176, 14), L(88, 32, 88, 64), L(128, 32, 128, 64), L(168, 32, 168, 64)],
     detail=[L(88, 112, 168, 112), L(88, 148, 168, 148), L(88, 184, 136, 184)],
     area=[R(48, 48, 160, 176, 14)])

print(save(overwrite=True))
