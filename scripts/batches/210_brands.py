"""Brand logos: AI, web frameworks and build tools."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *
import importlib.util

_spec = importlib.util.spec_from_file_location('extremes', os.path.join(os.path.dirname(os.path.abspath(__file__)), '198_extremes.py'))
_ext = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ext)
_P = P


def P(d):
    """Path with anchors added on its curve extremes."""
    return _P(_ext.fix_d(d))

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


def hexagon(r, start, c=(128, 128)):
    return [ipt(p) for p in regular_polygon(c, r, 6, start)]


def ell_pt(c, rx, ry, phi, t):
    a, b = math.radians(phi), math.radians(t)
    x, y = rx * math.cos(b), ry * math.sin(b)
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def ellipse(c, rx, ry, phi):
    """Closed rotated ellipse through its (rounded) major-axis ends."""
    p, q = ipt(ell_pt(c, rx, ry, phi, 0)), ipt(ell_pt(c, rx, ry, phi, 180))
    return P(f'M{pt(p)} A{f(rx)} {f(ry)} {f(phi)} 1 0 {pt(q)} A{f(rx)} {f(ry)} {f(phi)} 1 0 {pt(p)} Z')


# ---------------------------------------------------------------- AI
# Anthropic: the "A\" mark, a pointed A beside a backslash of the same slant.
brand('anthropic-logo', ['anthropic', 'ai', 'ai company', 'claude', 'a'],
      line=[PL([(32, 208), (92, 48), (152, 208)]), L(53, 152, 131, 152), L(164, 48, 224, 208)], outline=True)

# ---------------------------------------------------------------- runtimes and tools
# Bun: the round dumpling with two eyes and a small smile.
BUN = P('M40 152 C40 96 80 48 128 48 C176 48 216 96 216 152 C216 188 176 208 128 208 C80 208 40 188 40 152 Z')
brand('bun-logo', ['bun', 'javascript', 'runtime', 'bundler', 'dumpling'],
      area=[BUN], line=[BUN], detail=[P('M112 164 C120 176 136 176 144 164')],
      dotcut=[C(96, 136, 14), C(160, 136, 14)])

# Webpack: the cube inside the hexagonal box.
HEX_W = PG(hexagon(96, -90))
brand('webpack-logo', ['webpack', 'bundler', 'build tool', 'javascript', 'cube'],
      area=[HEX_W], line=[HEX_W],
      detail=[PG(hexagon(48, -90)), PL([(86, 104), (128, 128), (170, 104)]), L(128, 128, 128, 176)])

# Redux: three looping arcs, each starting from a dot, turned 120 degrees apart.
RC = (128, 134)
redux_lines, redux_dots = [], []
for a in (0, 120, 240):
    s, l1, l2, top, e = rot([(97, 167), (84, 108), (128, 42), (128, 42), (176, 92)], a, RC)
    c1, c2, c3, c4, c5, c6 = rot([(88, 148), (84, 128), (84, 70), (104, 42), (152, 42), (170, 60)], a, RC)
    s, l1, top, e = ipt(s), ipt(l1), ipt(top), ipt(e)
    redux_lines.append(P(f'M{pt(s)} C{pt(c1)} {pt(c2)} {pt(l1)} C{pt(c3)} {pt(c4)} {pt(top)} '
                         f'C{pt(c5)} {pt(c6)} {pt(e)}'))
    redux_dots.append(C(s[0], s[1], 16))
brand('redux-logo', ['redux', 'state management', 'javascript', 'react'],
      line=redux_lines, dot=redux_dots)

# Jest: the jester's hat, three bells and the curled shoe.
JEST_HAT = PG([(112, 32), (192, 32), (176, 104), (152, 66), (128, 104)])
JEST_SHOE = P('M68 172 H192 V184 C192 200 180 206 164 210 C140 216 128 224 104 224 '
              'C84 224 68 212 68 192 Z')
brand('jest-logo', ['jest', 'testing', 'test runner', 'javascript'],
      area=[JEST_HAT, JEST_SHOE], line=[JEST_HAT, JEST_SHOE],
      dot=[C(80, 138, 16), C(128, 138, 16), C(176, 138, 16)])

# Playwright: the two theatre masks, the smiling one in front.
PW_FRONT = P('M100 64 C140 60 184 48 220 36 C224 100 216 176 172 212 C148 232 116 220 104 188 '
             'C96 152 96 104 100 64 Z')
PW_BACK = 'M100 92 C80 88 56 80 32 72 C32 124 40 168 76 184 C84 188 92 188 100 186'
brand('playwright-logo', ['playwright', 'testing', 'browser automation', 'masks', 'microsoft'],
      area=[PW_FRONT, P(PW_BACK + ' Z')], line=[PW_FRONT, P(PW_BACK)],
      detail=[P('M128 156 C148 172 176 168 196 144'), P('M52 152 C60 140 72 136 84 140')],
      dotcut=[C(136, 108, 14), C(188, 96, 14), C(64, 108, 14)])

# Storybook: the book tile with its bookmark ribbon and S.
brand('storybook-logo', ['storybook', 'ui components', 'design system', 'frontend'],
      area=[SQ], line=[SQ],
      detail=[PL([(168, 40), (168, 76), (180, 66), (192, 76), (192, 40)]),
              P('M152 96 C146 86 138 80 126 80 C108 80 96 88 96 102 C96 132 160 120 160 156 '
                'C160 172 146 184 126 184 C110 184 98 178 92 168')])

# ESLint: the pointy-top hexagon inside the flat-top hexagon.
HEX_E = PG(hexagon(96, 0))
brand('eslint-logo', ['eslint', 'linter', 'javascript', 'code quality'],
      area=[HEX_E], line=[HEX_E], detail=[PG(hexagon(48, -90))])

# Deno: the dinosaur head in profile inside the circle.
brand('deno-logo', ['deno', 'javascript', 'typescript', 'runtime', 'dinosaur'],
      area=[RING], line=[RING],
      detail=[P('M60 196 C60 140 80 92 116 72 C148 56 184 80 200 112 C204 122 200 132 188 132 '
                'H140 C132 148 136 176 156 216')],
      dotcut=[C(124, 92, 14)])

# pnpm: the 3x3 grid of squares with the left middle square missing.
PN = [R(x, y, 32, 32) for x, y in [(40, 40), (112, 40), (184, 40), (112, 112), (184, 112),
                                    (40, 184), (112, 184), (184, 184)]]
brand('pnpm-logo', ['pnpm', 'package manager', 'npm', 'javascript'], area=PN, line=PN)

# Astro: the A-shaped rocket body over its flame.
ASTRO = P('M92 32 H164 L208 148 C192 140 172 136 156 136 L132 76 C130 72 126 72 124 76 L100 136 '
          'C84 136 64 140 48 148 Z')
FLAME = P('M100 180 C116 186 140 186 156 180 C160 200 148 212 128 224 C108 212 96 200 100 180 Z')
brand('astro-logo', ['astro', 'web framework', 'static site', 'rocket'],
      area=[ASTRO, FLAME], line=[ASTRO, FLAME])

# Laravel: the tall cube column and the small cube joined into an L.
LARA = PG([(39, 55), (74, 35), (110, 55), (110, 131), (147, 111), (147, 75), (183, 54), (217, 75),
           (217, 116), (183, 136), (183, 177), (109, 219), (39, 177)])
brand('laravel-logo', ['laravel', 'php', 'web framework', 'backend'],
      area=[LARA], line=[LARA],
      detail=[PL([(39, 55), (74, 76), (110, 55)]), PL([(74, 76), (74, 159), (109, 179), (183, 136)]),
              L(109, 179, 109, 219), PL([(147, 75), (183, 96), (217, 75)]), L(183, 96, 183, 136)])

# DigitalOcean: the open ring with the stepped squares at its foot.
DO_SQ = [R(108, 172, 24, 24), R(80, 204, 16, 16), R(64, 164, 16, 16)]
brand('digitalocean-logo', ['digitalocean', 'cloud', 'hosting', 'servers'],
      area=DO_SQ, line=[P('M68 112 A72 72 0 1 1 140 184')] + DO_SQ)

# Rollup: the R with the rolled sheet curling up inside it.
ROLL = P('M56 32 H144 C176 32 200 60 200 92 C200 116 188 136 168 148 L200 216 H56 Z')
brand('rollup-logo', ['rollup', 'bundler', 'build tool', 'javascript'],
      area=[ROLL], line=[ROLL],
      detail=[P('M64 208 C88 160 116 96 148 72 C164 60 180 76 168 96 C164 104 152 108 144 100')])

# esbuild: the double chevron in a circle.
brand('esbuild-logo', ['esbuild', 'bundler', 'build tool', 'fast', 'javascript'],
      area=[RING], line=[RING],
      detail=[PL([(80, 80), (124, 128), (80, 176)]), PL([(136, 80), (180, 128), (136, 176)])])

# Preact: the atom with two orbits in a hexagon.
HEX_P = PG(hexagon(96, -90))
brand('preact-logo', ['preact', 'javascript', 'ui library', 'react', 'web framework'],
      area=[HEX_P], line=[HEX_P],
      detail=[ellipse((128, 128), 64, 24, 40), ellipse((128, 128), 64, 24, -40)],
      dot=[C(128, 128, 16)])

# SolidJS: the two stacked slanted slabs.
SOLID_T = P('M92 72 C116 56 160 60 216 80 L196 116 C160 96 112 88 88 108 C80 96 82 80 92 72 Z')
SOLID_B = P('M164 184 C140 200 96 196 40 176 L60 140 C96 160 144 168 168 148 C176 160 174 176 164 184 Z')
brand('solidjs-logo', ['solidjs', 'solid', 'javascript', 'ui library', 'reactive'],
      area=[SOLID_T, SOLID_B], line=[SOLID_T, SOLID_B])

# Qwik: the hexagonal speech-bubble Q with the lightning bolt.
QWIK = PG([(76, 44), (184, 44), (224, 120), (188, 188), (204, 224), (148, 208), (80, 208), (32, 120)])
brand('qwik-logo', ['qwik', 'javascript', 'web framework', 'resumable'],
      area=[QWIK], line=[QWIK],
      detail=[PG([(96, 52), (172, 116), (156, 128), (184, 192), (80, 120), (104, 112)])])

# Alpine.js: the dark slanted block and the small diamond beside it.
ALP_A = PG([(32, 128), (72, 88), (160, 176), (80, 176)])
ALP_B = PG([(162, 128), (192, 98), (222, 128), (192, 158)])
brand('alpinejs-logo', ['alpine.js', 'alpinejs', 'alpine', 'javascript', 'web framework'],
      area=[ALP_A, ALP_B], line=[ALP_A, ALP_B])

# Lit: the flame of stacked chevron columns.
LIT = PG([(52, 108), (90, 146), (90, 70), (128, 32), (128, 108), (166, 70), (166, 146), (204, 108),
          (204, 186), (166, 224), (128, 186), (90, 224), (52, 186)])
brand('lit-logo', ['lit', 'web components', 'javascript', 'google', 'flame'],
      area=[LIT], line=[LIT], detail=[L(90, 146, 90, 224), L(128, 108, 128, 186), L(166, 146, 166, 224)])

# Ionic: the ring with its small satellite dot, around the solid centre.
IC = (128, 128)
io_p, io_q = ipt(polar(IC, 92, -17)), ipt(polar(IC, 92, -73))
brand('ionic-logo', ['ionic', 'mobile', 'hybrid app', 'framework'],
      area=[C(128, 128, 40), C(192, 64, 20)],
      line=[P(f'M{pt(io_p)} ' + arc_to(IC, 92, io_p, io_q, lambda m: dist(m, (192, 64)))),
            C(128, 128, 40), C(192, 64, 20)])

# Electron: three broken orbits, each ending in a small ball, around the nucleus.
EL = (128, 128)
el_lines, el_dots = [], []
for phi in (30, 90, 150):
    p, q = ipt(ell_pt(EL, 88, 34, phi, 30)), ipt(ell_pt(EL, 88, 34, phi, 320))
    el_lines.append(P(f'M{pt(p)} A88 34 {phi} 1 1 {pt(q)}'))
    d = q
    el_dots.append(C(d[0], d[1], 16))
brand('electron-logo', ['electron', 'desktop app', 'javascript', 'framework', 'atom'],
      line=el_lines, dot=el_dots + [C(128, 128, 16)])

# Tauri: two open rings turned against each other, each with a dot inside.
T1, T2 = (152, 100), (104, 156)
t1p, t1q = ipt(polar(T1, 64, 200)), ipt(polar(T1, 64, 40))
t2p, t2q = ipt(polar(T2, 64, 20)), ipt(polar(T2, 64, 220))
brand('tauri-logo', ['tauri', 'desktop app', 'rust', 'framework'],
      line=[P(f'M{pt(t1p)} ' + arc_to(T1, 64, t1p, t1q, lambda m: dist(m, T2))),
            P(f'M{pt(t2p)} ' + arc_to(T2, 64, t2p, t2q, lambda m: dist(m, T1)))],
      dot=[C(*T1, 16), C(*T2, 16)])

# Expo: the wide chevron with rounded feet.
EXPO = P('M112 44 H144 L220 196 C224 204 220 216 208 216 C200 216 196 212 192 208 L128 104 L64 208 '
         'C60 212 56 216 48 216 C36 216 32 204 36 196 Z')
brand('expo-logo', ['expo', 'react native', 'mobile', 'framework'], area=[EXPO], line=[EXPO])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
