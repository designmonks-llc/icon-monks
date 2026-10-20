"""Brand logos: AI products and companies."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'

# Midjourney: a sailboat with a crescent main sail, a small jib and a bowl hull.
SAIL = 'M120 32 C176 64 196 112 196 160 C172 152 144 152 120 152 Z'
JIB = 'M96 80 L96 152 L52 152 Z'
HULL = 'M40 176 H216 C204 204 176 216 128 216 C80 216 52 204 40 176 Z'
icon('midjourney-logo', B, ['midjourney', 'ai', 'image generation', 'art', 'sailboat', 'logo', 'brand'],
     area=[P(SAIL), P(JIB), P(HULL)], line=[P(SAIL), P(JIB), P(HULL)])

# Ollama: the llama outline (tapered ears, wide crown, wavy cheeks, open neck); eyes beside an oval muzzle with a Y nose.
HEAD = ('M60 224 V212 C54 204 50 196 50 186 C50 174 54 166 60 160 C50 150 46 134 46 118 C46 98 54 84 66 74 '
        'L76 46 A12 12 0 0 1 100 48 L102 68 C110 62 118 60 128 60 C138 60 146 62 154 68 L156 48 A12 12 0 0 1 180 46 '
        'L190 74 C202 84 210 98 210 118 C210 134 206 150 196 160 C202 166 206 174 206 186 C206 196 202 204 196 212 V224')
icon('ollama-logo', B, ['ollama', 'llama', 'ai', 'llm', 'local models', 'logo', 'brand'],
     area=[P(HEAD + ' Z')], line=[P(HEAD)],
     detail=[E(128, 150, 36, 26), P('M121 146 L128 151 L135 146'), P('M128 151 V158')],
     dotcut=[C(78, 118, 14), C(178, 118, 14)])

# Replicate: three nested corner bars.
icon('replicate-logo', B, ['replicate', 'ai', 'machine learning', 'model hosting', 'api', 'logo', 'brand'],
     line=[P('M216 40 H40 V216'), P('M216 96 H96 V216'), P('M216 152 H152 V216')])

# ElevenLabs: two tall upright bars.
BARS = [R(72, 32, 32, 192, 8), R(152, 32, 32, 192, 8)]
icon('elevenlabs-logo', B, ['elevenlabs', 'eleven labs', 'ai', 'voice', 'text to speech', 'audio', 'logo', 'brand'],
     area=BARS, line=BARS)

print(save(overwrite=True))
