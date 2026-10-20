"""Brand logos: platforms, languages and everyday apps."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


# ---------------------------------------------------------------- platforms
# Apple: the bitten apple with its leaf.
apple_body = P('M128 88 C116 82 104 78 90 78 C64 78 48 104 48 136 C48 172 68 224 90 224 '
               'C104 224 114 216 128 216 C142 216 152 224 166 224 C182 224 200 196 208 172 '
               'C188 162 178 152 178 136 C178 120 188 106 202 98 C190 84 176 78 162 78 '
               'C150 78 140 82 128 88 Z')
apple_leaf = P('M124 64 C124 46 142 32 164 32 C164 50 146 64 124 64 Z')
brand('apple-logo', ['apple', 'mac', 'iphone', 'technology'],
      area=[apple_body, apple_leaf], line=[apple_body, apple_leaf])

# Docker: the whale carrying a stack of containers (5, 3 and 1). The container grid is a repeated
# simple pattern (9 strokes), checked at 16 px; its seams separate the boxes in the fill weight.
whale = P('M32 136 H188 C188 112 190 92 200 80 C212 88 218 98 224 108 C216 110 212 120 208 136 '
          'C192 184 160 220 112 220 C64 220 32 184 32 136 Z')
stack = 'M32 136 V106 H62 V76 H122 V46 H152 V106 H182 V136'
brand('docker-logo', ['docker', 'containers', 'devops', 'whale'],
      area=[whale, P(stack + ' Z')], line=[whale, P(stack)],
      detail=[L(32, 136, 182, 136), L(62, 106, 152, 106), L(122, 76, 152, 76),
              L(62, 106, 62, 136), L(92, 76, 92, 136), L(122, 76, 122, 136), L(152, 106, 152, 136)],
      reviewed=True)

# Linux: Tux the penguin.
tux_body = ('M68 196 C60 184 56 176 56 164 C56 144 62 126 70 110 C76 100 80 92 80 76 '
            'C80 48 100 32 128 32 C156 32 176 48 176 76 C176 92 180 100 186 110 '
            'C194 126 200 144 200 164 C200 176 196 184 188 196')
tux_feet = [E(92, 208, 36, 16), E(164, 208, 36, 16)]
brand('linux-logo', ['linux', 'tux', 'penguin', 'operating system', 'open source'],
      area=[P(tux_body + ' Z')] + tux_feet, line=[P(tux_body)] + tux_feet,
      detail=[P('M128 124 C150 124 164 144 164 164 C164 184 148 196 128 196 '
                'C108 196 92 184 92 164 C92 144 106 124 128 124 Z'),
              PG([(114, 92), (142, 92), (128, 106)])],
      dotcut=[C(110, 62, 14), C(146, 62, 14)])

# AWS: the lowercase wordmark over the smile arrow.
brand('aws-logo', ['aws', 'amazon web services', 'cloud', 'amazon'], outline=True,
      line=[P('M36 66 C42 60 50 56 58 56 C70 56 76 64 76 74 V116'),
            P('M76 90 H56 C44 90 36 96 36 104 C36 112 44 116 52 116 C66 116 76 108 76 96'),
            PL([(96, 56), (110, 116), (128, 76), (146, 116), (160, 56)]),
            P('M218 64 C212 58 206 56 200 56 C190 56 182 62 182 70 C182 88 220 82 220 102 '
              'C220 112 212 116 200 116 C190 116 184 114 178 108'),
            P('M36 148 C60 166 92 176 124 176 C152 176 180 168 204 152'),
            PL([(188, 140), (216, 140), (208, 168)])])

# ---------------------------------------------------------------- languages and tools
# Python: two interlocked snakes; outline of the pair, the split between them, mouths and eyes.
py = ('M104 40 H152 A20 20 0 0 1 172 60 V84 H196 A20 20 0 0 1 216 104 V152 A20 20 0 0 1 196 172 H172 V196 '
      'A20 20 0 0 1 152 216 H104 A20 20 0 0 1 84 196 V172 H60 A20 20 0 0 1 40 152 V104 A20 20 0 0 1 60 84 '
      'H84 V60 A20 20 0 0 1 104 40 Z')
brand('python-logo', ['python', 'programming language', 'code', 'snake'],
      area=[P(py)], line=[P(py)],
      detail=[P('M172 84 V104 A24 24 0 0 1 148 128 H108 A24 24 0 0 0 84 152 V172'),
              L(84, 84, 128, 84), L(128, 172, 172, 172)],
      dotcut=[C(106, 62, 14), C(150, 194, 14)])

brand('javascript-logo', ['javascript', 'js', 'programming language', 'web', 'code'],
      area=[SQ], line=[SQ],
      detail=[P('M120 108 V164 C120 180 110 188 98 188 C88 188 80 184 76 176'),
              P('M190 120 C184 112 178 108 170 108 C158 108 150 114 150 126 C150 148 192 140 192 166 '
                'C192 180 182 188 170 188 C160 188 152 184 146 176')])

brand('typescript-logo', ['typescript', 'ts', 'programming language', 'javascript', 'code'],
      area=[SQ], line=[SQ],
      detail=[L(72, 112, 128, 112), L(100, 112, 100, 188),
              P('M194 120 C188 112 182 108 174 108 C162 108 154 114 154 126 C154 148 196 140 196 166 '
                'C196 180 186 188 174 188 C164 188 156 184 150 176')])

# Git: the rounded diamond with a branching commit graph; nodes are small stroked circles so they hold at every weight.
git = 'M116 44 A17 17 0 0 1 140 44 L212 116 A17 17 0 0 1 212 140 L140 212 A17 17 0 0 1 116 212 L44 140 A17 17 0 0 1 44 116 Z'
brand('git-logo', ['git', 'version control', 'source control', 'branch'],
      area=[P(git)], line=[P(git)],
      detail=[L(96, 64, 121, 89), L(128, 106, 128, 158), L(135, 103, 161, 129),
              C(128, 96, 10), C(128, 168, 10), C(168, 136, 10)])

# ---------------------------------------------------------------- browsers
# Firefox: the fox wrapped round the globe, ear at the left and tail flaring over the top right.
ff_outer = 'M72 56 C52 76 40 104 40 136 A88 88 0 0 0 216 136 C216 96 196 56 152 32 C140 48 132 64 128 84'
brand('firefox-logo', ['firefox', 'mozilla', 'browser', 'web browser', 'fox'],
      area=[P(ff_outer + ' A44 44 0 0 0 100 94 L80 92 Z')],
      line=[P(ff_outer)],
      detail=[P('M100 94 A44 44 0 1 1 86 144'),
              P('M72 56 L80 92 C100 92 120 100 136 116 C112 116 96 128 86 144')])

# Edge: the wave curling round its hole.
edge = ('M208 182 A96 96 0 1 1 224 128 C224 144 210 156 192 156 H168 C160 156 152 146 152 134 '
        'A28 28 0 1 0 106 138 C116 168 148 182 176 182 Z')
brand('microsoft-edge-logo', ['microsoft edge', 'edge', 'microsoft', 'browser', 'web browser'],
      area=[P(edge)], line=[P(edge)], detail=[P('M34 104 C52 80 76 68 100 68 C120 68 134 80 142 96')])

# ---------------------------------------------------------------- email
gm = 'M32 200 V76 A20 20 0 0 1 64 60 L128 108 L192 60 A20 20 0 0 1 224 76 V200 H184 V112 L128 154 L72 112 V200 Z'
brand('gmail-logo', ['gmail', 'google', 'email', 'mail', 'inbox'],
      area=[P(gm)], line=[P(gm)], detail=[L(72, 66, 72, 112), L(184, 66, 184, 112)])

ol_tile = R(32, 72, 104, 112, 16)
ol_back = 'M88 72 V48 A16 16 0 0 1 104 32 H200 A16 16 0 0 1 216 48 V208 A16 16 0 0 1 200 224 H104 A16 16 0 0 1 88 208 V184'
brand('microsoft-outlook-logo', ['microsoft outlook', 'outlook', 'microsoft', 'email', 'calendar'],
      area=[R(88, 32, 128, 192, 16), ol_tile], line=[P(ol_back), ol_tile],
      detail=[E(84, 128, 24, 32), PL([(136, 124), (216, 124), (152, 172), (136, 160)])])

print(save(overwrite=True))
