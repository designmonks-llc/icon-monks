"""Brand logos: notes and research tools, data science libraries, formats and organisations."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)


def ipt(p):
    return (round(p[0]), round(p[1]))


def star(c, r_out, r_in, start=-90):
    pts = []
    for i in range(10):
        pts.append(ipt(polar(c, r_out if i % 2 == 0 else r_in, start + i * 36)))
    return PG(pts)


# ---------------------------------------------------------------- notes and research
# Logseq: one large and two small blobs, as on the app tile.
LS = [E(60, 84, 26, 32), E(148, 56, 32, 20), E(148, 164, 68, 52)]
icon('logseq-logo', B, ['logseq', 'notes', 'knowledge base', 'outliner', 'logo', 'brand'],
     area=LS, line=LS)

# Joplin: the J with its flat top bar and the hook closed into a round bowl, on the app tile.
icon('joplin-logo', B, ['joplin', 'notes', 'note-taking', 'markdown', 'logo', 'brand'],
     area=[SQ], line=[SQ],
     detail=[L(124, 76, 180, 76), P('M152 76 V152 A28 28 0 0 1 96 152 A28 28 0 0 1 152 152')])

# Anki: a big and a small star on the flashcard tile.
CARD = R(48, 32, 160, 192, 16)
icon('anki-logo', B, ['anki', 'flashcards', 'spaced repetition', 'study', 'learning', 'logo', 'brand'],
     area=[CARD], line=[CARD],
     detail=[star((104, 156), 52, 22), star((160, 84), 32, 14, -80)])

# Overleaf: the ring of the seed with its stem rising into the leaf.
LEAF = 'M84 104 C112 64 160 40 220 36 C200 76 164 100 124 100 C108 100 96 102 84 104 Z'
icon('overleaf-logo', B, ['overleaf', 'latex', 'writing', 'research', 'documents', 'logo', 'brand'],
     area=[P(LEAF)], line=[C(112, 160, 52), P('M60 160 C60 132 68 116 84 104'), P(LEAF)])

# ---------------------------------------------------------------- data science
# pandas: the columns of bars with the two square points between them.
icon('pandas-logo', B, ['pandas', 'python', 'data analysis', 'dataframe', 'data science', 'logo', 'brand'],
     line=[L(68, 88, 68, 216), L(108, 48, 108, 76), L(108, 144, 108, 176), L(148, 88, 148, 108),
           L(148, 184, 148, 208), L(188, 40, 188, 168)],
     dot=[C(108, 110, 16), C(148, 146, 16)])

# OpenCV: three open rings in a triangle, each cut toward the middle.
def ring(c, r, gap_at, gap=70):
    a1, a2 = gap_at + gap / 2, gap_at - gap / 2 + 360
    p, q = ipt(polar(c, r, a1)), ipt(polar(c, r, a2))
    return P(f'M{pt(p)} A{r} {r} 0 1 1 {pt(q)}')

icon('opencv-logo', B, ['opencv', 'computer vision', 'image processing', 'library', 'logo', 'brand'],
     line=[ring((128, 78), 36, 90), ring((72, 178), 36, -30), ring((184, 178), 36, -90)])

# Streamlit: the folded paper boat of three sails.
BOAT = 'M32 92 L96 124 L128 76 L160 124 L224 92 L192 176 H64 Z'
icon('streamlit-logo', B, ['streamlit', 'python', 'data apps', 'dashboard', 'logo', 'brand'],
     area=[P(BOAT)], line=[P(BOAT)],
     detail=[L(96, 124, 192, 176), L(160, 124, 192, 176)])

# Plotly: the grid of dots turning into bars of two heights.
icon('plotly-logo', B, ['plotly', 'charts', 'data visualization', 'graphs', 'python', 'logo', 'brand'],
     line=[L(56, 152, 56, 200), L(104, 104, 104, 200), L(152, 152, 152, 200), L(200, 104, 200, 200)],
     dot=[C(56, 56, 16), C(104, 56, 16), C(152, 56, 16), C(200, 56, 16), C(56, 104, 16), C(152, 104, 16)])

# D3: the stemless D and the 3 side by side.
icon('d3-logo', B, ['d3', 'd3.js', 'data visualization', 'javascript', 'charts', 'logo', 'brand'],
     outline=True,
     line=[P('M40 64 H68 A64 64 0 0 1 68 192 H40'),
           P('M156 64 H184 A32 32 0 0 1 184 128 H172 M184 128 A32 32 0 0 1 184 192 H156')])

# three.js: the triangle cut into a mesh of smaller triangles (three per side, so the mesh stays open in bold).
TA, TB, TC = (32, 32), (224, 86), (81, 224)
def lerp(a, b, t):
    return ipt((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
MESH = []
for k in (1, 2):
    t = k / 3
    MESH.append(L(*lerp(TA, TB, t), *lerp(TA, TC, t)))
    MESH.append(L(*lerp(TB, TA, t), *lerp(TB, TC, t)))
    MESH.append(L(*lerp(TC, TA, t), *lerp(TC, TB, t)))
icon('three-js-logo', B, ['three.js', 'threejs', 'webgl', '3d', 'javascript', 'logo', 'brand'],
     area=[PG([TA, TB, TC])], line=[PG([TA, TB, TC])], detail=MESH)

# ---------------------------------------------------------------- formats
# JSON: the twisted ring, two hooked halves wrapped around an upright hole.
icon('json-logo', B, ['json', 'data format', 'javascript', 'code', 'logo', 'brand'],
     area=[C(128, 128, 96)], hole=[E(128, 128, 28, 48)], line=[C(128, 128, 96), E(128, 128, 28, 48)],
     detail=[P('M128 80 C148 60 170 52 190 54'), P('M128 176 C108 196 86 204 66 202')])

# ---------------------------------------------------------------- organisations
# Pepsi: the globe with its top cap and the wave across the lower half.
icon('pepsi-logo', B, ['pepsi', 'pepsico', 'soda', 'cola', 'drinks', 'logo', 'brand'],
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[P('M39 92 C68 84 96 80 128 80 C160 80 188 84 217 92'), P('M39 164 C56 156 72 152 88 152 C120 152 136 168 168 168 C188 168 204 162 217 156')])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
