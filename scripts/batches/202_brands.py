"""Brand logos: developer platforms, frameworks and tools."""
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


def ring_arc(c, r, a0, a1):
    """Arc on circle (c, r) from angle a0 to a1 (degrees, clockwise on screen), with anchors at the extremes."""
    stops = [a0] + [a for a in range(-720, 721, 90) if a0 < a < a1] + [a1]
    pts = [ipt(polar(c, r, a)) for a in stops]
    d = f'M{pt(pts[0])}'
    for p in pts[1:]:
        d += f' A{f(r)} {f(r)} 0 0 1 {pt(p)}'
    return P(d)


BADGE = R(40, 40, 176, 176, 16)

# ---------------------------------------------------------------- nextjs: N in a circle, the diagonal runs past the stem
icon('nextjs-logo', B, ['nextjs', 'next.js', 'next', 'react', 'framework', 'vercel', 'logo', 'brand'],
     line=[C(128, 128, 96)], area=[C(128, 128, 96)],
     detail=[P('M92 168 V88 L180 200'), L(164, 88, 164, 136)])

# ---------------------------------------------------------------- nodejs: pointed-top hexagon with js
hexagon = PG([(128, 32), (212, 80), (212, 176), (128, 224), (44, 176), (44, 80)])
icon('nodejs-logo', B, ['nodejs', 'node.js', 'node', 'javascript', 'runtime', 'server', 'logo', 'brand'],
     line=[hexagon], area=[hexagon],
     detail=[P('M108 96 V148 A20 20 0 0 1 72 160'),
             P('M180 104 C172 96 164 96 156 96 C144 96 136 104 136 114 C136 134 180 126 180 148 '
               'C180 160 172 168 158 168 C148 168 140 164 134 158')])

# ---------------------------------------------------------------- nuxt: a large peak with a small peak behind it
big = PG([(32, 192), (104, 64), (176, 192)])
icon('nuxt-logo', B, ['nuxt', 'nuxtjs', 'vue', 'framework', 'web development', 'logo', 'brand'],
     line=[big, PL([(165, 124), (172, 112), (216, 192), (200, 192)])], area=[big])

# ---------------------------------------------------------------- prisma: a leaning prism with one inner edge
prism = PG([(136, 32), (44, 180), (152, 224), (212, 196)])
icon('prisma-logo', B, ['prisma', 'orm', 'database', 'typescript', 'logo', 'brand'],
     line=[prism], area=[prism], detail=[L(136, 32, 152, 224)])

# ---------------------------------------------------------------- remix: the stemless R with a foot bar
icon('remix-logo', B, ['remix', 'react', 'framework', 'web development', 'r', 'logo', 'brand'],
     line=[P('M48 64 H148 C180 64 200 84 200 108 C200 132 180 148 148 148 H48'),
           P('M148 148 C176 148 188 164 188 188 V200'), L(48, 200, 124, 200)], outline=True)

# ---------------------------------------------------------------- supabase: the split bolt with two straight edges
bolt = PG([(140, 32), (44, 148), (120, 148), (120, 224), (212, 108), (140, 108)])
icon('supabase-logo', B, ['supabase', 'database', 'postgres', 'backend', 'logo', 'brand'],
     line=[bolt], area=[bolt])

# ---------------------------------------------------------------- turborepo: inner ring, outer ring broken into dashes
icon('turborepo-logo', B, ['turborepo', 'turbo', 'monorepo', 'build system', 'vercel', 'logo', 'brand'],
     area=[C(128, 128, 44)],
     line=[C(128, 128, 44), ring_arc((128, 128), 92, -90, 160),
           ring_arc((128, 128), 92, 176, 200), ring_arc((128, 128), 92, 216, 236), ring_arc((128, 128), 92, 252, 262)])

# ---------------------------------------------------------------- ubuntu: circle of friends
heads = [180, -60, 60]
icon('ubuntu-logo', B, ['ubuntu', 'linux', 'operating system', 'canonical', 'logo', 'brand'],
     line=[ring_arc((128, 128), 60, a + 26, a + 94) for a in heads],
     dot=[C(*ipt(polar((128, 128), 80, a)), 16) for a in heads])

# ---------------------------------------------------------------- vercel: the triangle
tri = PG([(128, 44), (224, 208), (32, 208)])
icon('vercel-logo', B, ['vercel', 'hosting', 'deployment', 'cloud', 'triangle', 'logo', 'brand'],
     line=[tri], area=[tri])

# ---------------------------------------------------------------- vite: downward shield with a lightning bolt
shield = PG([(32, 48), (224, 48), (128, 216)])
icon('vite-logo', B, ['vite', 'vitejs', 'build tool', 'bundler', 'lightning', 'logo', 'brand'],
     line=[shield], area=[shield], detail=[PL([(148, 72), (104, 124), (152, 124), (124, 164)])])

# ---------------------------------------------------------------- vuejs: outer V band with the inner chevron
vee = PG([(32, 48), (128, 216), (224, 48), (176, 48), (128, 132), (80, 48)])
icon('vuejs-logo', B, ['vuejs', 'vue.js', 'vue', 'javascript', 'framework', 'logo', 'brand'],
     line=[vee], area=[vee], detail=[PL([(104, 48), (128, 88), (152, 48)])])

# ---------------------------------------------------------------- stackoverflow: tray with a fanned stack of bars
bars = []
for deg, c in ((0, (112, 184)), (-15, (118, 154)), (-32, (130, 124)), (-52, (150, 98))):
    a, b = rot([(c[0] - 40, c[1]), (c[0] + 40, c[1])], deg, c)
    bars.append(L(*ipt(a), *ipt(b)))
icon('stackoverflow-logo', B, ['stackoverflow', 'stack overflow', 'questions', 'developer', 'community', 'logo', 'brand'],
     line=[PL([(48, 140), (48, 216), (184, 216), (184, 140)])] + bars)

# ---------------------------------------------------------------- svelte: two interlocked tilted loops forming an S
icon('svelte-logo', B, ['svelte', 'sveltejs', 'framework', 'javascript', 'logo', 'brand'],
     line=[PX('M168 52 C148 36 120 40 104 56 L68 92 C52 108 52 132 68 148 C76 156 88 160 100 160'),
           PX('M88 204 C108 220 136 216 152 200 L188 164 C204 148 204 124 188 108 C180 100 168 96 156 96')],
     detail=[PX('M148 76 C140 68 128 68 120 76 L96 100 C88 108 92 120 104 124 L152 132 C164 136 168 148 160 156 '
               'L136 180 C128 188 116 188 108 180')])

print(save(overwrite=True))
