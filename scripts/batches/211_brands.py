"""Brand logos: programming languages and frameworks."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)
SQ = R(40, 40, 176, 176, 16)


def tags(*t):
    return list(t) + ['logo', 'brand']


# ---------------------------------------------------------------- the C family
# C# and C++: the pointy-top hexagon around an open C, with the # or ++ in the C's mouth.
HEX = PG([(128, 32), (211, 80), (211, 176), (128, 224), (45, 176), (45, 80)])

icon('csharp-logo', B, tags('c#', 'csharp', 'c sharp', 'programming language', 'microsoft', 'dotnet'),
     area=[HEX], line=[HEX],
     detail=[P('M126 97 A40 40 0 1 0 126 159'),
             L(160, 100, 160, 156), L(184, 100, 184, 156), L(144, 116, 196, 116), L(144, 140, 196, 140)])

icon('cplusplus-logo', B, tags('c++', 'cplusplus', 'cpp', 'programming language', 'iso'),
     area=[HEX], line=[HEX],
     detail=[P('M123 91 A48 48 0 1 0 123 165'),
             L(138, 128, 158, 128), L(148, 118, 148, 138), L(182, 128, 202, 128), L(192, 118, 192, 138)])

# ---------------------------------------------------------------- apple and google languages
# Swift: the swift in flight, two wing feathers cut into its back.
SWIFT = ('M152 40 C168 60 176 80 176 100 C176 112 174 124 172 132 C136 112 100 84 76 56 L128 124 L48 72 '
         'C80 116 112 148 144 166 C128 172 112 176 96 176 C72 176 48 168 32 156 '
         'C52 188 88 212 128 212 C160 212 176 196 196 196 C208 196 220 204 224 212 '
         'C224 196 216 176 208 164 C212 152 216 140 216 124 C216 88 192 60 152 40 Z')
icon('swift-logo', B, tags('swift', 'apple', 'programming language', 'ios', 'bird'),
     area=[P(SWIFT)], line=[P(SWIFT)])

# Dart: the dart head, with the fold from the top corner to the inner step.
DART = PG([(32, 136), (68, 64), (136, 32), (220, 116), (220, 188), (188, 188), (188, 224), (112, 224)])
icon('dart-logo', B, tags('dart', 'google', 'flutter', 'programming language'),
     area=[DART], line=[DART], detail=[L(68, 64, 188, 188)])

# ---------------------------------------------------------------- ruby and python frameworks
# Ruby: the tilted gem with its rounded top-left facet edge.
GEM = ('M152 36 H208 A16 16 0 0 1 224 52 L216 204 L72 220 A32 32 0 0 1 36 196 V148 '
       'C52 100 96 56 152 36 Z')
icon('ruby-logo', B, tags('ruby', 'programming language', 'gem', 'rails'),
     area=[P(GEM)], line=[P(GEM)],
     detail=[P('M160 40 C140 92 92 136 40 152'), L(40, 152, 216, 204)])

# Django: the "dj" on the app tile.
icon('django-logo', B, tags('django', 'python', 'web framework', 'dj'),
     area=[SQ], line=[SQ],
     detail=[C(100, 136, 28), L(128, 68, 128, 164), P('M164 112 V168 A24 24 0 0 1 140 192')],
     dot=[C(164, 80, 16)])

# FastAPI: the lightning bolt in the circle.
BOLT = PG([(136, 64), (188, 64), (124, 112), (164, 112), (72, 188)])
icon('fastapi-logo', B, tags('fastapi', 'python', 'api', 'web framework', 'lightning'),
     area=[RING], line=[RING], hole=[BOLT], detail=[BOLT])

# ---------------------------------------------------------------- java frameworks
# Spring: the leaf in the circle, with its vein.
LEAF = ('M80 176 C68 160 64 144 64 128 C64 108 80 96 108 92 C136 88 160 84 176 72 C186 92 190 112 190 132 '
        'C190 148 180 162 164 172 C152 180 136 184 120 184 C104 184 92 182 80 176 Z')
icon('spring-logo', B, tags('spring', 'spring boot', 'java', 'framework', 'leaf'),
     area=[RING], line=[RING], detail=[P(LEAF), P('M164 104 C152 140 120 164 80 176')])

# ---------------------------------------------------------------- functional languages
# Elixir: the tilted drop with an inner fold.
DROP = ('M136 32 C100 72 68 120 68 160 C68 196 96 224 128 224 C164 224 188 196 188 164 '
        'C188 132 172 112 156 92 C144 76 136 56 136 32 Z')
icon('elixir-logo', B, tags('elixir', 'erlang', 'programming language', 'phoenix', 'drop'),
     area=[P(DROP)], line=[P(DROP)], detail=[P('M120 60 C112 80 108 100 108 120 C108 160 132 180 180 188')])

# Haskell: the > and lambda, followed by the = bars.
icon('haskell-logo', B, tags('haskell', 'programming language', 'functional', 'lambda'),
     line=[PL([(40, 64), (88, 128), (40, 192)]), L(88, 64, 184, 192), L(136, 128, 88, 192),
           L(160, 104, 216, 104), L(176, 144, 216, 144)])

# Scala: three twisted bands stacked into a spiral.
BANDS = [PG([(64, y + 16), (192, y), (192, y + 40), (64, y + 56)]) for y in (36, 100, 164)]
icon('scala-logo', B, tags('scala', 'programming language', 'jvm', 'functional'),
     area=BANDS, line=BANDS)

# Clojure: the inner circle with its lambda, inside the outer ring.
icon('clojure-logo', B, tags('clojure', 'lisp', 'programming language', 'jvm', 'lambda'),
     area=[RING], line=[RING],
     detail=[C(124, 128, 60), L(102, 72, 146, 184), L(124, 128, 94, 180)])

# Erlang: the e between its brackets.
icon('erlang-logo', B, tags('erlang', 'programming language', 'otp', 'functional'),
     line=[P('M60 56 C48 76 42 100 42 128 C42 156 48 180 60 200'),
           P('M196 56 C208 76 214 100 214 128 C214 156 208 180 196 200'),
           P('M92 128 H188 A48 48 0 1 0 174 162')])

# ---------------------------------------------------------------- data and scripting languages
# R: the R in front of the ring.
icon('r-logo', B, tags('r', 'rlang', 'programming language', 'statistics', 'data science'),
     line=[P('M88 170 A96 64 0 1 1 220 94'), P('M112 200 V96 H168 A28 28 0 0 1 168 152 H112'),
           L(160, 152, 196, 200)])

# Julia: the three dots in a triangle.
icon('julia-logo', B, tags('julia', 'programming language', 'scientific computing', 'dots'),
     area=[C(128, 82, 40), C(76, 174, 40), C(180, 174, 40)],
     line=[C(128, 82, 40), C(76, 174, 40), C(180, 174, 40)])

# Lua: the planet with its hole and the moon in orbit.
icon('lua-logo', B, tags('lua', 'programming language', 'scripting', 'moon'),
     area=[C(120, 136, 80)], line=[C(120, 136, 80)], detail=[C(144, 112, 20)], dot=[C(200, 56, 16)])

# PowerShell: the prompt on the slanted panel.
PANEL = PG([(64, 56), (224, 56), (192, 200), (32, 200)])
icon('powershell-logo', B, tags('powershell', 'microsoft', 'shell', 'terminal', 'scripting'),
     area=[PANEL], line=[PANEL], detail=[PL([(88, 88), (144, 128), (88, 168)]), L(128, 168, 160, 168)])

# ---------------------------------------------------------------- systems languages
# Zig: the Z between brackets, its diagonal running out past both corners.
icon('zig-logo', B, tags('zig', 'programming language', 'systems', 'compiler'),
     line=[PL([(72, 64), (40, 64), (40, 176), (56, 176)]), L(96, 64, 200, 64), L(224, 40, 40, 224),
           L(88, 176, 168, 176), PL([(216, 96), (216, 176), (192, 176)])])

# Nim: the crown over its lower jaw.
CROWN = ('M36 100 L60 92 L72 68 L100 84 L128 56 L156 84 L184 68 L196 92 L220 100 L204 124 '
         'C180 110 156 104 128 104 C100 104 76 110 52 124 Z')
JAW = 'M40 144 L92 168 L128 148 L164 168 L216 144 C204 188 172 212 128 212 C84 212 52 188 40 144 Z'
icon('nim-logo', B, tags('nim', 'nimlang', 'programming language', 'crown'),
     area=[P(CROWN), P(JAW)], line=[P(CROWN), P(JAW)])

# Crystal: the faceted crystal with its cut triangle.
CRYSTAL = PG([(32, 100), (100, 32), (200, 56), (224, 152), (156, 224), (56, 196)])
TRI = PG([(32, 100), (132, 76), (108, 168)])
icon('crystal-logo', B, tags('crystal', 'programming language', 'ruby', 'compiled'),
     area=[CRYSTAL], line=[CRYSTAL], hole=[TRI], detail=[TRI])

# WebAssembly: the notched tile with WA.
WA = 'M40 40 H100 A28 28 0 0 0 156 40 H216 V216 H40 Z'
icon('webassembly-logo', B, tags('webassembly', 'wasm', 'web', 'bytecode', 'wa'),
     area=[P(WA)], line=[P(WA)],
     detail=[PL([(56, 128), (74, 192), (96, 144), (118, 192), (136, 128)]),
             PL([(148, 192), (172, 128), (196, 192)]), L(158, 172, 186, 172)])

# ---------------------------------------------------------------- php frameworks
# Symfony: the script sf in the circle.
icon('symfony-logo', B, tags('symfony', 'php', 'web framework', 'sf'),
     area=[RING], line=[RING],
     detail=[P('M108 120 C104 114 98 112 92 112 C84 112 78 118 78 126 C78 142 108 138 108 154 '
               'C108 164 100 170 90 170 C84 170 78 166 74 160'),
             P('M188 80 C184 72 178 68 170 68 C162 68 156 72 152 80 C144 96 140 124 136 148 C130 180 120 196 100 196'),
             L(132, 108, 172, 108)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
