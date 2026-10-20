"""Brand logos: developer tools, languages and databases."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import importlib.util

_spec = importlib.util.spec_from_file_location('extremes', os.path.join(os.path.dirname(os.path.abspath(__file__)), '198_extremes.py'))
_ext = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ext)


def PX(d):
    """Path with anchors added on its curve extremes."""
    return P(_ext.fix_d(d))


B = 'Brands'


def ipt(p):
    return (round(p[0]), round(p[1]))


def gear(c, ro, ri, n, tip=0.3, base=0.5, start=-90):
    """Toothed ring: n teeth reaching ro, valleys along ri, arcs between teeth."""
    step = 360 / n
    d = ''
    for i in range(n):
        a = start + i * step
        p0 = ipt(polar(c, ri, a - base * step / 2))
        p1 = ipt(polar(c, ro, a - tip * step / 2))
        p2 = ipt(polar(c, ro, a + tip * step / 2))
        p3 = ipt(polar(c, ri, a + base * step / 2))
        q = ipt(polar(c, ri, a + step - base * step / 2))
        d += (f'M{pt(p0)} ' if i == 0 else f'L{pt(p0)} ') + f'L{pt(p1)} A{f(ro)} {f(ro)} 0 0 1 {pt(p2)} L{pt(p3)} '
        d += f'A{f(ri)} {f(ri)} 0 0 1 {pt(q)} '
    return d.strip() + ' Z'


# ---------------------------------------------------------------- postgresql: the elephant head with its trunk and ear
PG_HEAD = ('M108 42 C124 34 140 32 156 33 C176 34 196 36 208 44 C220 52 222 68 218 84 C214 104 208 124 204 140 '
           'C212 144 220 148 220 156 C218 164 200 168 184 168 C178 168 176 176 174 188 C172 204 168 216 152 220 '
           'C140 222 132 216 128 204 C124 192 120 180 116 168 C104 170 84 176 72 170 C60 164 54 148 48 128 '
           'C42 108 36 84 36 64 C36 48 44 38 56 36 C76 32 96 36 108 42 Z')
icon('postgresql-logo', B, ['postgresql', 'postgres', 'database', 'sql', 'elephant', 'logo', 'brand'],
     area=[PX(PG_HEAD)], line=[PX(PG_HEAD)],
     detail=[PX('M168 80 C164 104 172 128 184 148')],
     dotcut=[C(112, 96, 14)])

# ---------------------------------------------------------------- mysql: the leaping dolphin
icon('mysql-logo', B, ['mysql', 'database', 'sql', 'dolphin', 'oracle', 'logo', 'brand'],
     line=[PX('M40 48 C52 48 64 56 72 60 C104 64 136 88 156 128 C164 148 168 164 180 172 L216 196 L188 188'),
           PX('M40 48 C32 56 44 72 52 84 C58 96 60 108 68 120 C60 140 60 168 72 180 C80 188 84 176 84 164 '
              'L88 152 C96 168 108 188 120 200')])

# ---------------------------------------------------------------- redis: the script R on a rounded tile
icon('redis-logo', B, ['redis', 'database', 'cache', 'key value', 'in memory', 'logo', 'brand'],
     area=[R(40, 40, 176, 176, 16)], line=[R(40, 40, 176, 176, 16)],
     detail=[PX('M72 184 L124 100'),
             PX('M84 108 C108 88 140 80 156 88 C176 100 168 128 132 140 C120 160 124 184 144 180 C160 176 172 160 184 144')])

# ---------------------------------------------------------------- graphql: hexagon, inscribed triangle, six nodes
HEX = [(128, 44), (200, 86), (200, 170), (128, 212), (56, 170), (56, 86)]
icon('graphql-logo', B, ['graphql', 'api', 'query language', 'schema', 'logo', 'brand'],
     line=[PG(HEX), PG([(128, 44), (200, 170), (56, 170)])],
     dot=[C(x, y, 16) for x, y in HEX], outline=True)

# ---------------------------------------------------------------- rust: the toothed ring with the R
RG = gear((128, 128), 96, 84, 16)
icon('rust-logo', B, ['rust', 'programming language', 'rustlang', 'gear', 'logo', 'brand'],
     area=[P(RG)], line=[P(RG)],
     detail=[P('M100 168 V88 H136 A20 20 0 0 1 136 128 H100'), L(132, 128, 160, 168)])

# ---------------------------------------------------------------- go: the GO lettering with speed lines
icon('go-logo', B, ['go', 'golang', 'programming language', 'google', 'logo', 'brand'],
     line=[P('M136 108 A28 28 0 1 0 144 128 H120'), C(196, 128, 28),
           L(44, 100, 64, 100), L(32, 124, 60, 124), L(40, 148, 56, 148)], outline=True)

# ---------------------------------------------------------------- kotlin: the square with the notch
KT = [(40, 40), (216, 40), (128, 128), (216, 216), (40, 216)]
icon('kotlin-logo', B, ['kotlin', 'programming language', 'jetbrains', 'android', 'logo', 'brand'],
     area=[PG(KT)], line=[PG(KT)])

# ---------------------------------------------------------------- php: the lettering in the oval
icon('php-logo', B, ['php', 'programming language', 'web development', 'server', 'logo', 'brand'],
     area=[E(128, 128, 96, 64)], line=[E(128, 128, 96, 64)],
     detail=[P('M64 156 V108 H70 A20 20 0 0 1 70 148 H64'), L(114, 88, 114, 148),
             P('M114 124 A14 14 0 0 1 142 124 V148'), P('M166 156 V108 H172 A20 20 0 0 1 172 148 H166')])

# ---------------------------------------------------------------- html5: the shield with the 5
SHIELD = [(44, 32), (212, 32), (196, 204), (128, 224), (60, 204)]
icon('html5-logo', B, ['html5', 'html', 'markup', 'web development', 'logo', 'brand'],
     area=[PG(SHIELD)], line=[PG(SHIELD)],
     detail=[PL([(176, 76), (88, 76), (92, 120), (164, 120), (160, 160), (128, 172), (100, 162), (100, 148)])])

# ---------------------------------------------------------------- jira: three stacked corner arrows
icon('jira-logo', B, ['jira', 'atlassian', 'project management', 'issue tracker', 'agile', 'logo', 'brand'],
     line=[P('M132 48 H192 A16 16 0 0 1 208 64 V120'), P('M88 92 H148 A16 16 0 0 1 164 108 V164'),
           P('M44 136 H104 A16 16 0 0 1 120 152 V208')])

# ---------------------------------------------------------------- confluence: two mirrored waves
CF_LOW = 'M36 184 C64 140 96 128 128 140 L204 160 L186 202 L136 182 C112 172 96 180 84 202 Z'
CF_UP = 'M220 72 C192 116 160 128 128 116 L52 96 L70 54 L120 74 C144 84 160 76 172 54 Z'
icon('confluence-logo', B, ['confluence', 'atlassian', 'wiki', 'documentation', 'collaboration', 'logo', 'brand'],
     area=[PX(CF_LOW), PX(CF_UP)], line=[PX(CF_LOW), PX(CF_UP)])

# ---------------------------------------------------------------- hugging-face: the smiling face hugging with both hands
HF_L = 'M40 200 C30 184 36 160 56 150 C76 140 100 152 104 172 C108 196 84 212 64 210 C54 209 46 206 40 200 Z'
HF_R = 'M216 200 C226 184 220 160 200 150 C180 140 156 152 152 172 C148 196 172 212 192 210 C202 209 210 206 216 200 Z'
icon('hugging-face-logo', B, ['hugging face', 'huggingface', 'ai', 'machine learning', 'models', 'emoji', 'logo', 'brand'],
     area=[C(128, 120, 80), PX(HF_L), PX(HF_R)],
     line=[P('M59 160 A80 80 0 1 1 197 160'), PX(HF_L), PX(HF_R)],
     detail=[PX('M100 132 H156 C156 152 144 164 128 164 C112 164 100 152 100 132 Z')],
     dotcut=[C(100, 100, 14), C(156, 100, 14)])

# ---------------------------------------------------------------- linear: the disc with three stripes across its lower left
def chord(k):
    """Ends of the 45-degree chord y - x = k on the circle r=96 around the centre."""
    c = k / 2
    t = math.sqrt(96 * 96 - c * c * 2) / math.sqrt(2)
    return ipt((128 - c - t, 128 + c - t)), ipt((128 - c + t, 128 + c + t))


LIN = 'M56 64 A96 96 0 0 1 128 32 A96 96 0 0 1 224 128 A96 96 0 0 1 192 200 Z'
stripes = []
for k in (52, 84, 116):
    a, b = chord(k)
    stripes.append(L(*a, *b))
icon('linear-logo', B, ['linear', 'issue tracker', 'project management', 'productivity', 'logo', 'brand'],
     area=[P(LIN)], line=[P(LIN)] + stripes)

# ---------------------------------------------------------------- sentry: the open triangle with nested arcs
def sx(x, y):
    return f'{round(32 + (x - 10) * 0.384)} {round(44 + (y - 30) * 0.384)}'


ST_OUT = (f'M{sx(432, 450)} L{sx(470, 450)} C{sx(490, 450)} {sx(490, 430)} {sx(478, 428)} L{sx(268, 62)} '
          f'C{sx(262, 50)} {sx(248, 50)} {sx(242, 62)} L{sx(180, 165)} C{sx(260, 210)} {sx(345, 320)} {sx(348, 460)}')
ST_IN = (f'M{sx(265, 465)} C{sx(265, 350)} {sx(205, 262)} {sx(136, 224)} L{sx(86, 304)} '
         f'C{sx(150, 340)} {sx(182, 400)} {sx(182, 450)} L{sx(40, 450)} L{sx(62, 362)}')
icon('sentry-logo', B, ['sentry', 'error tracking', 'monitoring', 'debugging', 'logo', 'brand'],
     line=[PX(ST_OUT), PX(ST_IN)], outline=True)

# ---------------------------------------------------------------- grafana: the flame cog with the spiral
def lobes(c, rv, rt, n, start=-90):
    step = 360 / n
    ch = 2 * rv * math.sin(math.radians(step / 2))
    s = rt - rv * math.cos(math.radians(step / 2))
    rr = (ch * ch / 4 + s * s) / (2 * s)
    pts = [ipt(polar(c, rv, start + (i + 0.5) * step)) for i in range(n)]
    d = f'M{pt(pts[-1])}'
    for p in pts:
        d += f' A{f(round(rr, 1))} {f(round(rr, 1))} 0 0 1 {pt(p)}'
    return d + ' Z'


GF = lobes((128, 128), 76, 92, 8)
icon('grafana-logo', B, ['grafana', 'monitoring', 'dashboards', 'observability', 'metrics', 'logo', 'brand'],
     area=[P(GF)], line=[P(GF)],
     detail=[P('M142 128 A14 14 0 0 0 114 128 A28 28 0 0 0 170 128 A42 42 0 0 0 86 128 A56 56 0 0 0 198 128')])

# ---------------------------------------------------------------- netlify: the n with its four rays and two ticks
icon('netlify-logo', B, ['netlify', 'hosting', 'deployment', 'jamstack', 'web', 'logo', 'brand'],
     line=[P('M104 156 V104 H140 A12 12 0 0 1 152 116 V156'),
           L(128, 32, 128, 76), L(128, 184, 128, 224), L(32, 128, 76, 128), L(180, 128, 224, 128),
           L(72, 76, 84, 88), L(72, 180, 84, 168)])

print(save(overwrite=True))
