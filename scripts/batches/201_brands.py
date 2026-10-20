"""Brand logos: developer platforms, frameworks and cloud services."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'


def ipoly(points, close=True):
    return P(poly([(round(x), round(y)) for x, y in points], close))


# Angular: the shield with the A
SHIELD = 'M128 32 L216 64 L202 176 L128 224 L54 176 L40 64 Z'
icon('angular-logo', B, ['angular', 'framework', 'javascript', 'typescript', 'web development', 'logo', 'brand'],
     area=[P(SHIELD)], line=[P(SHIELD)],
     detail=[P('M88 180 L128 80 L168 180'), P('M104 148 H152')])

# Bitbucket: the bucket with its window
BUCKET = 'M40 52 H216 L188 212 H68 Z'
icon('bitbucket-logo', B, ['bitbucket', 'git', 'repository', 'code', 'atlassian', 'logo', 'brand'],
     area=[P(BUCKET)], line=[P(BUCKET)],
     detail=[P('M92 96 H164 L152 168 H104 Z')])

# Cloudflare: the flat-bottomed cloud with the swoosh
CF = ('M32 184 H208 A16 16 0 0 0 208 152 H196 '
      'C196 108 166 76 128 76 C98 76 78 96 72 120 C50 120 32 138 32 160 Z')
icon('cloudflare-logo', B, ['cloudflare', 'cdn', 'cloud', 'network', 'security', 'logo', 'brand'],
     area=[P(CF)], line=[P(CF)],
     detail=[P('M160 184 C164 160 176 152 196 152')])

# Drupal: the drop with the infinity eyes
DROP = 'M128 32 C152 68 200 100 200 152 A72 72 0 0 1 56 152 C56 100 104 68 128 32 Z'
icon('drupal-logo', B, ['drupal', 'cms', 'content management', 'drop', 'logo', 'brand'],
     area=[P(DROP)], line=[P(DROP)],
     detail=[P('M128 160 C120 148 108 140 96 140 C84 140 76 148 76 160 C76 172 84 180 96 180 C108 180 120 172 128 160 '
               'C136 148 148 140 160 140 C172 140 180 148 180 160 C180 172 172 180 160 180 C148 180 136 172 128 160 Z')])

# Firebase: the flame
FIRE = 'M64 188 L100 36 L132 100 L152 64 L192 188 L128 224 Z'
icon('firebase-logo', B, ['firebase', 'google', 'backend', 'database', 'flame', 'logo', 'brand'],
     area=[P(FIRE)], line=[P(FIRE)],
     detail=[P('M64 188 L152 64')])

# Flutter: the two chevron bars
TOP = [(144, 40), (196, 40), (84, 152), (58, 126)]
LOW = [(148, 124), (196, 124), (148, 172), (196, 220), (148, 220), (100, 172)]
icon('flutter-logo', B, ['flutter', 'dart', 'google', 'framework', 'mobile', 'cross platform', 'logo', 'brand'],
     area=[PG(TOP), PG(LOW)], line=[PG(TOP), PG(LOW)])

# Gatsby: the round G
icon('gatsby-logo', B, ['gatsby', 'gatsbyjs', 'framework', 'react', 'static site', 'logo', 'brand'],
     area=[C(128, 128, 96)],
     line=[P('M224 128 A96 96 0 1 1 196 60')],
     detail=[P('M224 128 H136'), P('M32 128 L128 224')])

# Google Cloud: the cloud ring
GC_OUT = 'M80 192 H176 A40 40 0 0 0 184 113 A60 60 0 0 0 72 113 A40 40 0 0 0 80 192 Z'
GC_IN = 'M92 168 H164 A18 18 0 0 0 166 132 A40 40 0 0 0 90 132 A18 18 0 0 0 92 168 Z'
icon('google-cloud-logo', B, ['google cloud', 'google', 'gcp', 'cloud', 'hosting', 'logo', 'brand'],
     area=[P(GC_OUT)], hole=[P(GC_IN)], line=[P(GC_OUT)], detail=[P(GC_IN)])

# Azure: the two-blade A
AZ_L = [(100, 40), (148, 40), (84, 216), (32, 216)]
AZ_R = [(160, 76), (224, 216), (108, 216), (176, 180)]
icon('azure-logo', B, ['azure', 'microsoft', 'cloud', 'hosting', 'logo', 'brand'],
     area=[PG(AZ_L), PG(AZ_R)], line=[PG(AZ_L), PG(AZ_R)])

# Kubernetes: the helm wheel in a heptagon
KC = (128, 130)
HEPT = ipoly(regular_polygon(KC, 96, 7))
spokes = []
for i in range(7):
    a = -90 + i * 360 / 7
    p, q = polar(KC, 24, a), polar(KC, 68, a)
    spokes.append(P(f'M{round(p[0])} {round(p[1])} L{round(q[0])} {round(q[1])}'))
icon('kubernetes-logo', B, ['kubernetes', 'k8s', 'containers', 'orchestration', 'cloud', 'logo', 'brand'],
     area=[HEPT], line=[HEPT], detail=[C(128, 130, 44)] + spokes, reviewed=True)

# MongoDB: the leaf
LEAF = 'M128 32 C160 60 180 100 180 136 C180 172 156 196 128 204 C100 196 76 172 76 136 C76 100 96 60 128 32 Z'
icon('mongodb-logo', B, ['mongodb', 'mongo', 'database', 'nosql', 'leaf', 'logo', 'brand'],
     area=[P(LEAF)], line=[P(LEAF)], detail=[P('M128 80 V224')])

print(save(overwrite=True))
