"""Brand logos: AI tools."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


def ipoly(points, close=True):
    return P(poly([ipt(p) for p in points], close))


# ---------------------------------------------------------------- labs and models
# Google DeepMind: the disc with two swirl cuts winding into the centre.
icon('deepmind-logo', B, ['deepmind', 'google deepmind', 'google', 'ai', 'research', 'logo', 'brand'],
     area=[RING], line=[RING],
     detail=[C(128, 128, 28),
             P('M72 50 C56 65 48 88 48 109 C48 124 52 138 60 148 C67 158 76 162 85 162 C91 162 98 160 104 156'),
             P('M184 206 C200 191 208 168 208 147 C208 132 204 118 196 108 C189 98 180 94 171 94 C165 94 158 96 152 100')])

# LlamaIndex: the standing llama in profile.
LLAMA = ('M76 32 L88 56 C96 60 100 68 100 80 V116 H180 C200 116 212 128 212 148 C212 160 208 168 200 172 V216 '
         'H184 V176 H116 V216 H100 V176 C92 168 88 156 88 140 V100 H64 C54 100 47 95 47 86 C47 84 47 82 48 80 L64 64 Z')
icon('llamaindex-logo', B, ['llamaindex', 'llama', 'rag', 'ai', 'llm', 'framework', 'logo', 'brand'],
     area=[P(LLAMA)], line=[P(LLAMA)])

# Model Context Protocol: three bent strands linked in a chain of loops.
S_MCP, R_MCP = 1.2, 24 * 1.2
def m(x, y):
    return (43 + (x - 18) * S_MCP, 32 + (y - 10) * S_MCP)
c1, c2, c3 = m(102.85, 33.94), m(136.79, 67.88), m(69.62, 101.12)
k = R_MCP / math.sqrt(2)
def off(c, s):
    return ipt((c[0] + s * k, c[1] + s * k))
r = f(R_MCP)
# strand 1: up-right into the loop around c1, back down-left to c3
MCP1 = f'M{pt(ipt(m(18, 84.85)))} L{pt(off(c1, -1))} A{r} {r} 0 0 1 {pt(off(c1, 1))} L{pt(ipt(c3))}'
# strand 3: from c1 down-left into the loop around c3, back up-right to c2
MCP3 = f'M{pt(ipt(c1))} L{pt(off(c3, -1))} A{r} {r} 0 0 0 {pt(off(c3, 1))} L{pt(ipt(c2))}'
# strand 2: on from strand 1 round the loop at c2, then down-left with a short kick down-right
MCP2 = (f'M{pt(off(c1, 1))} A{r} {r} 0 0 1 {pt(off(c2, 1))} L{pt(ipt(m(92.72, 146.6)))} '
        f'L{pt(ipt(m(105.33, 170.52)))}')
icon('mcp-logo', B, ['mcp', 'model context protocol', 'ai', 'agents', 'protocol', 'logo', 'brand'],
     line=[P(MCP1), P(MCP2), P(MCP3)])

# NotebookLM: three arches that share one left leg.
icon('notebooklm-logo', B, ['notebooklm', 'google', 'notebook', 'ai', 'research', 'notes', 'logo', 'brand'],
     line=[P('M41 196 V154 A87 87 0 0 1 215 154 V196'),
           P('M175 196 V160 C175 126 150 102 118 102 C84 102 56 122 41 154'),
           P('M41 196 V188 A44 44 0 0 1 129 188 V196')])

# ---------------------------------------------------------------- coding tools
# Windsurf: the wave stroke, two dips and a flag at the end.
icon('windsurf-logo', B, ['windsurf', 'codeium', 'code editor', 'ai', 'coding', 'ide', 'logo', 'brand'],
     line=[P('M36 80 L80 156 C84 164 92 168 99 168 C108 168 116 161 116 148 V100 C116 86 124 79 133 79 C139 79 146 82 150 90 '
             'L180 148 C185 160 193 165 201 165 C209 165 216 159 216 148 V76 H224')])

# Cursor: the cube with its dark front facet cut in.
HEX = ipoly(regular_polygon((128, 128), 96, 6))
icon('cursor-logo', B, ['cursor', 'cursor editor', 'code editor', 'ai', 'coding', 'ide', 'cube', 'logo', 'brand'],
     area=[HEX], line=[HEX], detail=[P('M45 80 H211 L128 224 V128 Z')])

# Tabnine: the hexagon with a play triangle inside.
icon('tabnine-logo', B, ['tabnine', 'code completion', 'ai', 'coding', 'assistant', 'logo', 'brand'],
     area=[HEX], line=[HEX], detail=[P('M96 50 V206 L211 128 Z')])

# Zed: the Z whose bars run on into nested corner brackets.
icon('zed-logo', B, ['zed', 'code editor', 'editor', 'ide', 'coding', 'logo', 'brand'],
     line=[P('M48 160 V48 H208 L48 208 H208 V96')],
     detail=[P('M88 144 V88 H168'), P('M168 112 V168 H88')])

# v0: the v and the squared 0 with its slash.
icon('v0-logo', B, ['v0', 'vercel', 'ai', 'app builder', 'ui generator', 'logo', 'brand'],
     line=[P('M32 96 L96 168 V96'), P('M144 88 H190 A24 24 0 0 1 214 112 V160'),
           P('M136 96 V144 A24 24 0 0 0 160 168 H206'), L(206, 98, 146, 158)],
     outline=True)

# ---------------------------------------------------------------- creative and media
# ComfyUI: the chunky slanted C with its stepped stem.
COMFY = 'M118 32 H207 A8 8 0 0 1 215 42 L203 86 L127 96 L106 163 H165 A8 8 0 0 1 173 173 L162 216 L80 224 L72 196 L41 172 L54 82 L100 76 Z'
icon('comfyui-logo', B, ['comfyui', 'comfy', 'stable diffusion', 'node editor', 'ai', 'image generation', 'logo',
                         'brand'],
     area=[P(COMFY)], line=[P(COMFY)])

# Suno: the tile with two half-ovals joined into an S.
TILE = R(40, 40, 176, 176, 40)
icon('suno-logo', B, ['suno', 'ai music', 'music', 'song generator', 'ai', 'logo', 'brand'],
     area=[TILE], line=[TILE],
     detail=[P('M128 128 A44 76 0 0 1 216 128 Z'), P('M40 128 A44 76 0 0 0 128 128 Z')])

# Luma: the open corner, a wall and a floor seen in perspective.
LUMA = 'M44 62 L130 32 V129 L211 177 L130 224 L44 177 Z'
icon('luma-logo', B, ['luma', 'luma ai', 'dream machine', 'video generation', 'ai', 'logo', 'brand'],
     area=[P(LUMA)], line=[P(LUMA)], detail=[L(44, 177, 130, 129)])

# HeyGen: the four-part gem, split from a point off its centre.
HG = 'M32 133 L123 32 L224 99 L147 221 Z'
icon('heygen-logo', B, ['heygen', 'ai video', 'avatar', 'video generation', 'ai', 'logo', 'brand'],
     area=[P(HG)], line=[P(HG)],
     detail=[PL([(32, 133), (143, 103), (147, 221)]), PL([(123, 32), (143, 103), (224, 99)])])

# Synthesia: two stepped bars that lock into a slanted frame.
def syn(x, y):
    return ipt((128 + (x - 129) * 0.923, 128 + (y - 130) * 0.923))
SYN_A = [syn(*p) for p in [(65, 60), (195, 60), (195, 100), (73, 100), (65, 161), (25, 161), (33, 80)]]
SYN_B = [syn(*p) for p in [(195, 100), (233, 100), (225, 167), (198, 200), (61, 200), (65, 161), (187, 161)]]
icon('synthesia-logo', B, ['synthesia', 'ai video', 'avatar', 'video generation', 'ai', 'logo', 'brand'],
     area=[PG(SYN_A), PG(SYN_B)], line=[PG(SYN_A), PG(SYN_B)])

# ---------------------------------------------------------------- assistants and meetings
# Poe: the chat-bubble face with a trailing echo stripe.
POE = ('M56 40 H168 A24 24 0 0 1 192 64 V120 A24 24 0 0 1 168 144 H88 L56 176 V144 A24 24 0 0 1 32 120 V64 '
       'A24 24 0 0 1 56 40 Z')
icon('poe-logo', B, ['poe', 'quora', 'chatbot', 'ai', 'chat', 'assistant', 'logo', 'brand'],
     area=[P(POE)], line=[P(POE), P('M80 216 L104 192 H200 A24 24 0 0 0 224 168 V96')],
     detail=[L(88, 84, 88, 100), L(136, 84, 136, 100)])

# Otter: the ring and the bars of a voice level.
icon('otter-logo', B, ['otter', 'otter.ai', 'transcription', 'meeting notes', 'ai', 'logo', 'brand'],
     line=[C(56, 128, 24), L(112, 100, 112, 156), L(148, 100, 148, 156), L(184, 124, 184, 132), L(216, 112, 216, 144)],
     outline=True)

# Fireflies: the F built from four blocks.
icon('fireflies-logo', B, ['fireflies', 'fireflies.ai', 'meeting notes', 'transcription', 'ai', 'logo', 'brand'],
     area=[R(40, 40, 64, 64), P('M144 40 H184 A32 32 0 0 1 216 72 V104 H144 Z'),
           P('M40 144 H104 V216 H72 A32 32 0 0 1 40 184 Z'), R(144, 144, 48, 48)],
     line=[R(40, 40, 64, 64), P('M144 40 H184 A32 32 0 0 1 216 72 V104 H144 Z'),
           P('M40 144 H104 V216 H72 A32 32 0 0 1 40 184 Z'), R(144, 144, 48, 48)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
