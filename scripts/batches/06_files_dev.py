import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

F, D, CH = 'Files', 'Development', 'Charts'

# ---------------------------------------------------------------- shared geometry (from 00_core)
filep = 'M56 32 H152 L200 80 V224 H56 Z'
fold = P('M152 32 V80 H200')
folder = ('M32 72 A16 16 0 0 1 48 56 H96 L120 80 H208 A16 16 0 0 1 224 96 V192 '
          'A16 16 0 0 1 208 208 H48 A16 16 0 0 1 32 192 Z')
Lc, Lr, Mc, Mr, Rc, Rr = (84, 152), 40, (132, 116), 60, (180, 148), 44
irm = circle_x(Mc, Mr, Rc, Rr)[0]
iml = circle_x(Mc, Mr, Lc, Lr)[0]
cloud = (f'M84 192 H180 ' + arc_to(Rc, Rr, (180, 192), irm, lambda m: dist(m, Mc)) + ' ' +
         arc_to(Mc, Mr, irm, iml, lambda m: -m[1]) + ' ' + arc_to(Lc, Lr, iml, (84, 192), lambda m: dist(m, Mc)) + ' Z')


def file_icon(name, tags, det, dotcut=()):
    icon(name, F, tags, line=[P(filep)], detail=[fold] + det, area=[P(filep)], dotcut=list(dotcut))


# ---------------------------------------------------------------- files
file_icon('file-plus', ['new file', 'add', 'create', 'document'], [L(128, 120, 128, 184), L(96, 152, 160, 152)])
file_icon('file-minus', ['remove', 'delete', 'document', 'subtract'], [L(96, 152, 160, 152)])
file_icon('file-code', ['source', 'script', 'programming', 'document'],
          [PL([(108, 124), (84, 152), (108, 180)]), PL([(148, 124), (172, 152), (148, 180)])])
file_icon('file-zip', ['archive', 'compressed', 'zip', 'package'],
          [L(88, 56, 104, 56), L(104, 88, 120, 88), R(84, 120, 40, 60, 10)])
file_icon('file-image', ['photo', 'picture', 'jpg', 'png', 'document'],
          [PL([(84, 192), (116, 152), (140, 176), (152, 164), (172, 184)])], dotcut=[C(100, 116, 14)])
file_icon('file-audio', ['music', 'sound', 'mp3', 'document'],
          [C(108, 180, 16), PL([(124, 180), (124, 116), (156, 128)])])
file_icon('file-video', ['movie', 'film', 'mp4', 'document'], [PG([(108, 124), (156, 152), (108, 180)])])
file_icon('file-lock', ['secure', 'private', 'protected', 'document'],
          [R(92, 144, 72, 52, 8), P('M108 144 V132 A20 20 0 0 1 148 132 V144')])
file_icon('file-search', ['find', 'lookup', 'document', 'search'], [C(120, 148, 24), L(137, 165, 164, 192)])

front = 'M80 72 H160 L200 112 V224 H80 Z'
icon('files', F, ['documents', 'pages', 'copy', 'duplicate'],
     line=[P(front), PL([(48, 192), (48, 32), (136, 32)])], detail=[P('M160 72 V112 H200')], area=[P(front)])


def folder_icon(name, tags, det, **kw):
    icon(name, F, tags, line=[P(folder)], detail=det, area=[P(folder)], **kw)


folder_icon('folder-plus', ['new folder', 'add', 'create', 'directory'], [L(128, 116, 128, 172), L(100, 144, 156, 144)])
folder_icon('folder-minus', ['remove', 'delete', 'directory'], [L(100, 144, 156, 144)])
folder_icon('folder-lock', ['secure', 'private', 'protected', 'directory'],
            [R(100, 144, 56, 36, 8), P('M112 144 V132 A16 16 0 0 1 144 132 V144')])
back = 'M32 200 V72 A16 16 0 0 1 48 56 H96 L120 80 H192 A16 16 0 0 1 208 96 V112'
flap = [(32, 208), (64, 112), (224, 112), (192, 208)]
icon('folder-open', F, ['directory', 'browse', 'open', 'files'],
     line=[P(back), PG(flap)], detail=[PL([(42, 178), (64, 112), (200, 112)])], area=[P(back + ' H64 L32 208 Z'), PG(flap)])

board = 'M88 48 H64 A16 16 0 0 0 48 64 V208 A16 16 0 0 0 64 224 H192 A16 16 0 0 0 208 208 V64 A16 16 0 0 0 192 48 H168'
clip = R(88, 32, 80, 40, 10)
icon('clipboard', F, ['paste', 'copy', 'board', 'tasks'],
     line=[P(board), clip], area=[R(48, 48, 160, 176, 16)], hole=[R(96, 40, 64, 24, 4)])
icon('clipboard-text', F, ['paste', 'notes', 'list', 'report'],
     line=[P(board), clip], detail=[L(88, 120, 168, 120), L(88, 152, 168, 152), L(88, 184, 136, 184)],
     area=[R(48, 48, 160, 176, 16)], hole=[R(96, 40, 64, 24, 4)])

note = 'M56 40 H200 A16 16 0 0 1 216 56 V160 L160 216 H56 A16 16 0 0 1 40 200 V56 A16 16 0 0 1 56 40 Z'
icon('note', F, ['sticky', 'memo', 'post-it', 'reminder'],
     line=[P(note)], detail=[P('M216 160 H160 V216'), L(80, 96, 176, 96), L(80, 128, 136, 128)], area=[P(note)])

nb = R(56, 32, 160, 192, 14)
icon('notebook', F, ['journal', 'diary', 'notes', 'notepad'],
     line=[nb], detail=[L(96, 32, 96, 224), L(128, 88, 184, 88), L(128, 120, 184, 120)], area=[nb])

bookp = 'M48 200 V56 A24 24 0 0 1 72 32 H208 V224 H72 A24 24 0 0 1 48 200 Z'
icon('book', F, ['read', 'library', 'education', 'novel'],
     line=[P(bookp)], detail=[P('M48 200 A24 24 0 0 1 72 176 H208')], area=[P(bookp)])
bo = 'M128 72 C108 56 76 48 32 52 V196 C76 192 108 200 128 216 C148 200 180 192 224 196 V52 C180 48 148 56 128 72 Z'
icon('book-open', F, ['read', 'reading', 'learn', 'pages'], line=[P(bo)], detail=[L(128, 72, 128, 216)], area=[P(bo)])

b3 = rot([(148, 72), (188, 72), (188, 216), (148, 216)], 14, (188, 216))
books = [R(36, 48, 40, 168, 8), R(76, 32, 44, 184, 8)]
icon('books', F, ['library', 'shelf', 'reading', 'education'],
     line=books + [PG(b3)], detail=[L(36, 84, 76, 84), L(76, 68, 120, 68), L(76, 180, 120, 180)],
     area=books + [PG(b3)])

paper_area = ('M32 104 H64 V64 A16 16 0 0 1 80 48 H208 A16 16 0 0 1 224 64 V192 A16 16 0 0 1 208 208 '
              'H48 A16 16 0 0 1 32 192 Z')
icon('newspaper', F, ['news', 'article', 'press', 'blog'],
     line=[P(paper_area)], detail=[P('M64 104 V192 A16 16 0 0 1 48 208'), L(96, 88, 192, 88), L(96, 128, 192, 128),
                                    L(96, 168, 152, 168)],
     area=[P(paper_area)])

floppy = 'M48 32 H176 L224 80 V208 A16 16 0 0 1 208 224 H48 A16 16 0 0 1 32 208 V48 A16 16 0 0 1 48 32 Z'
icon('floppy-disk', F, ['save', 'disk', 'storage', 'diskette'],
     line=[P(floppy)], detail=[P('M80 32 V72 H152 V32'), P('M72 224 V152 A8 8 0 0 1 80 144 H176 A8 8 0 0 1 184 152 V224')],
     area=[P(floppy)])

icon('cloud-arrow-up', F, ['upload', 'sync', 'backup', 'storage'],
     line=[P(cloud)], detail=[L(128, 164, 128, 108), PL([(104, 132), (128, 108), (152, 132)])], area=[P(cloud)])
icon('cloud-arrow-down', F, ['download', 'sync', 'storage', 'save'],
     line=[P(cloud)], detail=[L(128, 108, 128, 164), PL([(104, 140), (128, 164), (152, 140)])], area=[P(cloud)])
icon('cloud-check', F, ['synced', 'saved', 'backup', 'done'],
     line=[P(cloud)], detail=[PL([(100, 140), (120, 160), (160, 120)])], area=[P(cloud)])
icon('cloud-slash', F, ['offline', 'disconnected', 'no sync', 'unavailable'],
     line=[P(cloud), L(48, 48, 208, 208)])

# ---------------------------------------------------------------- development
icon('git-branch', D, ['branch', 'version control', 'git', 'source'],
     line=[C(80, 56, 24), C(80, 200, 24), C(176, 72, 24), L(80, 80, 80, 176), P('M176 96 C176 144 80 128 80 176')],
     area=[C(80, 56, 24), C(80, 200, 24), C(176, 72, 24)])
icon('git-commit', D, ['commit', 'version control', 'git', 'history'],
     line=[C(128, 128, 40), L(32, 128, 88, 128), L(168, 128, 224, 128)], area=[C(128, 128, 40)])
icon('git-merge', D, ['merge', 'version control', 'git', 'combine'],
     line=[C(80, 56, 24), C(80, 200, 24), C(176, 152, 24), L(80, 80, 80, 176), P('M80 80 C80 136 112 152 152 152')],
     area=[C(80, 56, 24), C(80, 200, 24), C(176, 152, 24)])
icon('git-pull-request', D, ['pull request', 'review', 'git', 'merge request'],
     line=[C(72, 56, 24), C(72, 200, 24), C(184, 200, 24), L(72, 80, 72, 176),
           P('M184 176 V104 A24 24 0 0 0 160 80 H128'), PL([(152, 56), (128, 80), (152, 104)])],
     area=[C(72, 56, 24), C(72, 200, 24), C(184, 200, 24)])
icon('git-fork', D, ['fork', 'version control', 'git', 'split'],
     line=[C(72, 56, 24), C(184, 56, 24), C(128, 200, 24),
           P('M72 80 V104 A24 24 0 0 0 96 128 H160 A24 24 0 0 0 184 104 V80'), L(128, 128, 128, 176)],
     area=[C(72, 56, 24), C(184, 56, 24), C(128, 200, 24)])

bug = R(80, 80, 96, 136, 48)
icon('bug', D, ['debug', 'error', 'insect', 'issue'],
     line=[bug, L(108, 80, 92, 48), L(148, 80, 164, 48),
           L(40, 152, 80, 152), L(176, 152, 216, 152),
           L(48, 104, 84, 116), L(208, 104, 172, 116),
           L(48, 204, 84, 188), L(208, 204, 172, 188)],
     detail=[L(80, 128, 176, 128), L(128, 156, 128, 192)], area=[bug])

# puzzle piece: square with a knob on top and on the right
x0, y0, x1, y1, kr, cr = 36, 76, 188, 220, 22, 12
tk = ((x0 + x1) / 2, y0 - 10)
rk = (x1 + 10, (y0 + y1) / 2)
dk = math.sqrt(kr * kr - 100)
pz = (f'M{x0 + cr} {y0} H{f(tk[0] - dk)} A{kr} {kr} 0 1 1 {f(tk[0] + dk)} {y0} H{x1 - cr} '
      f'A{cr} {cr} 0 0 1 {x1} {y0 + cr} V{f(rk[1] - dk)} A{kr} {kr} 0 1 1 {x1} {f(rk[1] + dk)} V{y1 - cr} '
      f'A{cr} {cr} 0 0 1 {x1 - cr} {y1} H{x0 + cr} A{cr} {cr} 0 0 1 {x0} {y1 - cr} V{y0 + cr} '
      f'A{cr} {cr} 0 0 1 {x0 + cr} {y0} Z')
icon('puzzle-piece', D, ['plugin', 'extension', 'addon', 'integration'], line=[P(pz)], area=[P(pz)])

tb = [R(92, 32, 72, 56, 12), R(32, 168, 72, 56, 12), R(152, 168, 72, 56, 12)]
icon('tree-structure', D, ['hierarchy', 'sitemap', 'org chart', 'structure'],
     line=tb + [L(128, 88, 128, 128), PL([(68, 168), (68, 128), (188, 128), (188, 168)])], area=tb)

gn = [((68, 68), 24), ((188, 92), 20), ((96, 188), 24), ((196, 196), 16)]
gl = [C(*n, r) for n, r in gn]


def seg(a, b, ra, rb):
    d = dist(a, b); ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return L(a[0] + ux * ra, a[1] + uy * ra, b[0] - ux * rb, b[1] - uy * rb)


edges = [seg(gn[i][0], gn[j][0], gn[i][1], gn[j][1]) for i, j in ((0, 1), (0, 2), (1, 2), (1, 3))]
icon('graph', D, ['network', 'nodes', 'connections', 'diagram'], line=gl + edges, area=gl)

# ---------------------------------------------------------------- charts
icon('chart-line', CH, ['graph', 'analytics', 'statistics', 'trend'],
     line=[PL([(32, 40), (32, 216), (224, 216)]), PL([(72, 160), (112, 112), (152, 144), (208, 80)])])
pie_c = (128, 128)
icon('chart-pie', CH, ['graph', 'analytics', 'statistics', 'share'],
     line=[C(128, 128, 96)], detail=[PL([(128, 32), (128, 128), polar(pie_c, 96, 30)])], area=[C(128, 128, 96)])
ring = 'M32 128 A96 96 0 1 1 224 128 A96 96 0 1 1 32 128 Z M88 128 A40 40 0 1 0 168 128 A40 40 0 1 0 88 128 Z'
icon('chart-donut', CH, ['graph', 'analytics', 'statistics', 'ring'],
     line=[C(128, 128, 96), C(128, 128, 40)], detail=[L(128, 32, 128, 88), L(*polar(pie_c, 40, 30), *polar(pie_c, 96, 30))],
     area=[P(ring)], hole=[C(128, 128, 32)])
icon('presentation-chart', CH, ['presentation', 'slides', 'meeting', 'board'],
     line=[R(32, 40, 192, 136, 14), L(104, 176, 80, 224), L(152, 176, 176, 224)],
     detail=[L(88, 136, 88, 112), L(128, 136, 128, 80), L(168, 136, 168, 100)], area=[R(32, 40, 192, 136, 14)])
icon('pulse', CH, ['heartbeat', 'activity', 'health', 'monitor'],
     line=[PL([(32, 128), (72, 128), (100, 64), (148, 192), (176, 128), (224, 128)])])
g1, g2 = polar((128, 128), 96, 135), polar((128, 128), 96, 45)
gauge = f'M{pt(g1)} A96 96 0 1 1 {pt(g2)} Z'
icon('gauge', CH, ['speed', 'meter', 'performance', 'dashboard'],
     line=[P(gauge)], detail=[L(128, 148, 168, 96)], area=[P(gauge)], dotcut=[C(128, 148, 16)])

print(save(overwrite=True))
