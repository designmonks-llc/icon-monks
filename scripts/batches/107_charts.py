import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CH = 'Charts'
SLASH = L(48, 48, 208, 208)


def head(tip, frm, a=28):
    """Chevron arrowhead at tip, pointing away from frm."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
    pts = []
    for s in (45, -45):
        r = math.radians(s)
        bx, by = -ux, -uy
        pts.append((tip[0] + a * (bx * math.cos(r) - by * math.sin(r)), tip[1] + a * (bx * math.sin(r) + by * math.cos(r))))
    return PL([pts[0], tip, pts[1]])


AXES = P('M32 40 L32 216 L224 216')  # same as chart-line

# ---------------------------------------------------------------- A/B test
def a_let(dx=0, dy=0):
    return [PL([(40 + dx, 116 + dy), (68 + dx, 40 + dy), (96 + dx, 116 + dy)]), L(48.8 + dx, 92 + dy, 87.2 + dx, 92 + dy)]


def b_let(dx=0, dy=0):
    return [P(f'M{160 + dx} {140 + dy} H{186 + dx} A18 18 0 0 1 {186 + dx} {176 + dy} H{160 + dx} Z'),
            P(f'M{160 + dx} {176 + dy} H{190 + dx} A20 20 0 0 1 {190 + dx} {216 + dy} H{160 + dx} Z')]


A_LET, B_LET = a_let(), b_let()
icon('a-b-test', CH, ['ab test', 'split test', 'experiment', 'compare'],
     line=A_LET + B_LET + [L(200, 56, 56, 200)])
icon('a-b-test-slash', 'Development', ['ab testing', 'experiment', 'disabled'],
     line=a_let(0, 100) + b_let(0, -100) + [SLASH])

# ---------------------------------------------------------------- analyze
ZIG = PL([(76, 132), (100, 108), (120, 124), (148, 92)])
icon('analyze', CH, ['analyze', 'analysis', 'insight', 'chart'],
     line=[C(112, 112, 72), L(163, 163, 216, 216)], detail=[ZIG], area=[C(112, 112, 72)])
icon('analyze-slash', CH, ['analysis off', 'disabled', 'chart'],
     line=[C(112, 112, 72), ZIG, L(48, 48, 216, 216)])

# ---------------------------------------------------------------- axes
O3 = (100, 156)
icon('axes', CH, ['xyz', 'coordinates', '3d axes', 'axes', 'graph'],
     line=[L(O3[0], O3[1], 100, 40), L(O3[0], O3[1], 220, 156), L(O3[0], O3[1], 44, 212),
           head((100, 40), O3, 24), head((220, 156), O3, 24), head((44, 212), O3, 24)])
icon('axis-x', CH, ['axis', 'remove', 'cancel', 'chart', 'graph'],
     line=[P('M48 40 L48 208 L216 208'), head((216, 208), (48, 208), 24),
           L(156, 136, 196, 176), L(196, 136, 156, 176)])
icon('axis-y', CH, ['axis y', 'axis', 'chart', 'graph', 'y'],
     line=[P('M48 40 L48 208 L216 208'), head((48, 40), (48, 208), 24),
           L(92, 48, 112, 78), L(132, 48, 100, 104)])

# ---------------------------------------------------------------- arcs / area / arrows
cA = (128, 128)
arcs = []
for r, span in ((96, 300), (56, 210)):
    a, b = polar(cA, r, -90), polar(cA, r, -90 + span)
    arcs.append(P(f'M{pt(a)} A{r} {r} 0 {1 if span > 180 else 0} 1 {pt(b)}'))
icon('chart-arcs', CH, ['chart arcs', 'chart', 'graph', 'analytics', 'arcs'], line=arcs, dot=[C(128, 128, 16)])

AREA = [(64, 184), (64, 152), (108, 108), (148, 140), (208, 80), (208, 184)]
icon('chart-area', CH, ['area chart', 'graph', 'analytics', 'trend', 'filled'],
     line=[AXES, PG(AREA)], area=[PG(AREA)])

arr = [L(40, 32, 40, 224)]
for y, x in ((72, 176), (128, 216), (184, 136)):
    arr += [L(40, y, x, y), head((x, y), (40, y), 24)]
icon('chart-arrows', CH, ['chart arrows', 'chart', 'graph', 'analytics', 'arrows'], line=arr)
arr = [L(32, 216, 224, 216)]
for x, y in ((72, 104), (128, 40), (184, 128)):
    arr += [L(x, 216, x, y), head((x, y), (x, 216), 24)]
icon('chart-arrows-vertical', CH, ['chart arrows vertical', 'chart', 'graph', 'analytics', 'arrows'], line=arr)

# ---------------------------------------------------------------- bars
grp = [R(36, 96, 36, 88, 8), R(72, 136, 36, 48, 8), R(148, 56, 36, 128, 8), R(184, 112, 36, 72, 8)]
icon('chart-bar-grouped', CH, ['grouped bars', 'comparison', 'bar chart', 'analytics'],
     line=grp + [L(32, 216, 224, 216)], area=grp)

hb = [R(72, 40, 96, 36, 8), R(72, 110, 144, 36, 8), R(72, 180, 112, 36, 8)]
icon('chart-bar-horizontal', CH, ['horizontal bar', 'bar chart', 'ranking', 'analytics', 'horizontal bars'],
     line=hb + [L(40, 32, 40, 224)], area=hb)

pop = [R(40, 128, 40, 56, 8), R(108, 88, 40, 96, 8), R(176, 40, 40, 144, 8)]
icon('chart-bar-popular', CH, ['chart bar popular', 'chart', 'graph', 'analytics', 'bar'],
     line=pop + [L(32, 216, 224, 216)], area=pop)

cb = load('chart-bar')
icon('chart-bar-slash', CH, ['chart bar', 'disabled', 'off', 'chart', 'graph'], line=cb['line'] + [SLASH])

icon('chart-bar-square', CH, ['bar chart', 'report', 'analytics', 'box'],
     line=[R(32, 32, 192, 192, 16)], detail=[L(80, 176, 80, 128), L(128, 176, 128, 80), L(176, 176, 176, 112)],
     area=[R(32, 32, 192, 192, 16)])

st = [R(40, 96, 40, 88, 8), R(108, 40, 40, 144, 8), R(176, 76, 40, 108, 8)]
icon('chart-bar-stacked', CH, ['stacked bars', 'bar chart', 'composition', 'analytics', 'stacked bar'],
     line=st + [L(32, 216, 224, 216)], area=st,
     detail=[L(40, 140, 80, 140), L(108, 88, 148, 88), L(108, 136, 148, 136), L(176, 132, 216, 132)])

bub = [C(88, 160, 28), C(164, 88, 44), C(192, 172, 16)]
icon('chart-bubble', CH, ['bubble chart', 'scatter', 'graph', 'circles', 'chart bubble'],
     line=[AXES] + bub, area=bub)

candle = []
cbody = []
for x, wt, bt, bb, wb in ((56, 72, 100, 164, 196), (128, 40, 64, 136, 168), (200, 92, 120, 188, 216)):
    cbody.append(R(x - 20, bt, 40, bb - bt, 8))
    candle += [L(x, wt, x, bt), L(x, bb, x, wb)]
icon('chart-candlestick', CH, ['stock', 'candlestick', 'trading', 'market', 'stocks'], line=cbody + candle, area=cbody)

# overlapping circles: inner arc of the second circle is a cut line in fill
c1, r1, c2, r2 = (104, 104), 72, (168, 168), 56
p, q = circle_x(c1, r1, c2, r2)
inner = f'M{pt(p)} ' + arc_to(c2, r2, p, q, lambda m: -dist(m, c1))
outer = f'M{pt(p)} ' + arc_to(c2, r2, p, q, lambda m: dist(m, c1))
icon('chart-circles', CH, ['chart circles', 'chart', 'graph', 'analytics', 'circles'],
     line=[C(*c1, r1), P(outer)], detail=[P(inner)], area=[C(*c1, r1), C(*c2, r2)])

coh = 'M32 32 H224 V80 H176 V128 H128 V176 H80 V224 H32 Z'
icon('chart-cohort', CH, ['chart cohort', 'chart', 'graph', 'analytics', 'cohort'],
     line=[P(coh)], area=[P(coh)],
     detail=[L(32, 80, 176, 80), L(32, 128, 128, 128), L(32, 176, 80, 176),
             L(80, 32, 80, 176), L(128, 32, 128, 128), L(176, 32, 176, 80)])

icon('chart-covariate', CH, ['chart covariate', 'chart', 'graph', 'analytics', 'covariate'],
     line=[AXES, L(72, 184, 216, 64)], dot=[C(100, 112, 16), C(144, 72, 16), C(180, 160, 16), C(136, 184, 16)])

fun = [(32, 48), (224, 48), (160, 208), (96, 208)]
fx = lambda y: 32 + 64 * (y - 48) / 160
icon('chart-funnel', CH, ['chart funnel', 'chart', 'graph', 'analytics', 'funnel'],
     line=[PG(fun)], area=[PG(fun)],
     detail=[L(fx(101.3), 101.3, 256 - fx(101.3), 101.3), L(fx(154.7), 154.7, 256 - fx(154.7), 154.7)])

gan = [R(32, 36, 104, 40, 10), R(76, 108, 104, 40, 10), R(120, 180, 104, 40, 10)]
icon('chart-gantt', CH, ['gantt', 'timeline', 'schedule', 'steps'], line=gan, area=gan)

hx = [40 + i * 35.2 for i in range(6)]
tops = [160, 112, 56, 96, 144]
sky = f'M{f(hx[0])} 208'
for i, t in enumerate(tops):
    sky += f' V{t} H{f(hx[i + 1])}'
sky_line = sky + ' V208'
icon('chart-histogram', CH, ['histogram', 'distribution', 'bars', 'statistics', 'frequency'],
     line=[P(sky_line), L(32, 208, 224, 208)], area=[P(sky_line + ' Z')],
     detail=[L(hx[i + 1], max(tops[i], tops[i + 1]), hx[i + 1], 192) for i in range(4)])

icon('chart-infographic', CH, ['chart infographic', 'chart', 'graph', 'analytics', 'infographic'],
     line=[C(84, 84, 52), L(180, 208, 180, 128), L(216, 208, 216, 72), L(40, 168, 120, 168), L(40, 208, 96, 208)],
     detail=[PL([(84, 32), (84, 84), (136, 84)])], area=[C(84, 84, 52)])

sw = [R(32, 40, 40, 40, 8), R(32, 108, 40, 40, 8), R(32, 176, 40, 40, 8)]
icon('chart-legend', CH, ['legend', 'key', 'chart', 'toggle legend'],
     line=sw + [L(104, 60, 216, 60), L(104, 128, 184, 128), L(104, 196, 200, 196)], area=sw)

up = [(72, 160), (112, 112), (152, 144), (208, 80)]
dn = [(72, 88), (112, 136), (152, 104), (208, 168)]
icon('chart-line-down', CH, ['decline', 'graph', 'decrease', 'trend', 'falling'],
     line=[AXES, PL(dn), head(dn[-1], dn[-2])])
icon('chart-line-up', CH, ['growth', 'graph', 'increase', 'trend', 'rising'],
     line=[AXES, PL(up), head(up[-1], up[-2])])

pie = load('chart-pie')
icon('chart-pie-slash', CH, ['chart pie', 'disabled', 'off', 'chart', 'graph'],
     line=pie['line'] + pie['detail'] + [SLASH])

pie_main = 'M112 144 L112 72 A72 72 0 1 0 184 144 Z'
pie_slice = 'M148 108 L220 108 A72 72 0 0 0 148 36 Z'
icon('chart-pie-slice', CH, ['pie slice', 'share', 'segment'],
     line=[P(pie_main), P(pie_slice)], area=[P(pie_main), P(pie_slice)])

pb = [R(40, 112, 36, 72, 8), R(96, 48, 36, 136, 8)]
icon('chart-plus', CH, ['add chart', 'new graph', 'chart', 'insert'],
     line=pb + [L(32, 216, 140, 216), L(172, 184, 220, 184), L(196, 160, 196, 208)], area=pb)

cP = (128, 128)
pol = (f'M128 32 A96 96 0 0 1 224 128 L192 128 A64 64 0 0 1 128 192 L128 212 A84 84 0 0 1 44 128 '
       f'L72 128 A56 56 0 0 1 128 72 Z')
icon('chart-polar', CH, ['radar chart', 'polar', 'spider chart'],
     line=[P(pol)], area=[P(pol)],
     detail=[L(128, 72, 128, 192), L(72, 128, 192, 128)])

cR = (128, 136)
outer5 = regular_polygon(cR, 96, 5)
inner5 = [polar(cR, r, -90 + i * 72) for i, r in enumerate((56, 40, 52, 34, 46))]
icon('chart-radar', CH, ['radar chart', 'spider chart', 'polar', 'comparison', 'chart radar'],
     line=[PG(outer5)], detail=[PG(inner5)], area=[PG(outer5)])

icon('chart-sankey', CH, ['chart sankey', 'chart', 'graph', 'analytics', 'sankey'],
     line=[L(40, 48, 40, 176), L(216, 40, 216, 72), L(216, 152, 216, 224),
           P('M40 64 C128 64 128 56 216 56'), P('M40 112 C128 112 128 168 216 168'),
           P('M40 160 C128 160 128 208 216 208')])

icon('chart-scatter', CH, ['scatter plot', 'dots', 'correlation', 'data', 'chart scatter'],
     line=[AXES], dot=[C(80, 160, 16), C(116, 104, 16), C(152, 152, 16), C(176, 72, 16), C(200, 124, 16)])

icon('chart-scatter-3d', CH, ['chart scatter 3d', 'chart', 'graph', 'analytics', 'scatter'],
     line=[L(O3[0], O3[1], 100, 40), L(O3[0], O3[1], 220, 156), L(O3[0], O3[1], 44, 212)],
     dot=[C(144, 108, 16), C(192, 72, 16), C(188, 120, 16), C(160, 200, 16)])

icon('chart-treemap', CH, ['chart treemap', 'chart', 'graph', 'analytics', 'treemap'],
     line=[R(32, 32, 192, 192, 16)], area=[R(32, 32, 192, 192, 16)],
     detail=[L(112, 32, 112, 224), L(112, 128, 224, 128), L(168, 128, 168, 224), L(32, 152, 112, 152)])

clip = load('clipboard')
icon('clipboard-data', CH, ['clipboard', 'report', 'data', 'chart', 'analytics'],
     line=clip['line'], hole=clip['hole'], area=clip['area'],
     detail=[L(96, 192, 96, 152), L(128, 192, 128, 112), L(160, 192, 160, 136)])

# ---------------------------------------------------------------- flowchart
fl_boxes = [R(92, 32, 72, 40, 10), R(32, 176, 64, 48, 12), R(160, 176, 64, 48, 12)]
dia = PG([(128, 100), (164, 136), (128, 172), (92, 136)])
fl_lines = [L(128, 72, 128, 100), PL([(92, 136), (64, 136), (64, 176)]), PL([(164, 136), (192, 136), (192, 176)])]
icon('flowchart', CH, ['flow chart', 'process', 'diagram', 'workflow', 'flowchart'],
     line=fl_boxes + [dia] + fl_lines, area=fl_boxes + [dia])
icon('flowchart-slash', CH, ['flowchart', 'off', 'disabled', 'hidden'], line=fl_boxes + [dia] + fl_lines + [SLASH])

gr = load('graph')
icon('graph-slash', CH, ['graph', 'off', 'disabled', 'hidden'], line=gr['line'] + [SLASH])

# ---------------------------------------------------------------- mind map
MM = R(84, 108, 88, 40, 20)
MN = [C(52, 56, 20), C(204, 56, 20), C(52, 200, 20), C(204, 200, 20)]
icon('mind-map', CH, ['mind map', 'brainstorm', 'diagram', 'nodes', 'ideas'],
     line=[MM] + MN + [P('M104 108 C104 80 96 56 72 56'), P('M152 108 C152 80 160 56 184 56'),
                       P('M104 148 C104 176 96 200 72 200'), P('M152 148 C152 176 160 200 184 200')],
     area=[MM] + MN)

mon = load('monitor')
icon('monitor-chart', CH, ['analytics', 'dashboard', 'desktop'],
     line=mon['line'], area=mon['area'], detail=[PL([(68, 136), (104, 100), (136, 124), (188, 80)])])

# ---------------------------------------------------------------- pyramids
tri = [(128, 40), (224, 208), (32, 208)]
icon('pyramid', CH, ['pyramid', 'hierarchy', 'levels', 'funnel', '3d'],
     line=[PG(tri)], area=[PG(tri)], detail=[L(96, 96, 160, 96), L(64, 152, 192, 152)])

pyr = [(128, 32), (224, 152), (136, 216), (32, 168)]
icon('pyramid-3d', 'Design', ['pyramid', '3d shape', 'solid', 'geometry'],
     line=[PG(pyr)], detail=[L(128, 32, 136, 216)], area=[PG(pyr)])
icon('pyramid-3d-slash', 'Design', ['pyramid 3d', 'off', 'disabled', 'hidden', 'pyramid'],
     line=[PG(pyr), L(128, 32, 136, 216), SLASH])

# ---------------------------------------------------------------- table pivot
hdr = 'M32 48 A16 16 0 0 1 48 32 H208 A16 16 0 0 1 224 48 V88 H88 V224 H48 A16 16 0 0 1 32 208 Z'
icon('table-pivot', CH, ['pivot table', 'crosstab', 'spreadsheet', 'data'],
     line=[R(32, 32, 192, 192, 16), L(32, 88, 224, 88), L(88, 32, 88, 224),
           P('M176 116 A60 60 0 0 1 116 176'), head((176, 116), (176, 160), 24), head((116, 176), (160, 176), 24)],
     area=[P(hdr)])

print(save(overwrite=True))
