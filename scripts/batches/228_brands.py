"""Brand logos: SaaS, monitoring, design tools, e-commerce and support."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)


def tags(*t):
    return list(t) + ['logo', 'brand']


# ---------------------------------------------------------------- SaaS and monitoring
# Atlassian: the small blade in front of the tall peak, both with one curved side.
AT_BIG = 'M136 32 L222 224 H156 C136 192 112 152 112 112 C112 80 120 56 136 32 Z'
AT_SMALL = 'M72 124 L32 224 H96 C99 212 100 196 100 184 C100 156 90 138 72 124 Z'
icon('atlassian-logo', B, tags('atlassian', 'jira', 'confluence', 'software', 'teamwork'),
     area=[P(AT_BIG), P(AT_SMALL)], line=[P(AT_BIG), P(AT_SMALL)])

# PagerDuty: the P on the app tile, its stem broken off below the bowl.
icon('pagerduty-logo', B, tags('pagerduty', 'incident', 'on-call', 'alerts', 'monitoring'),
     area=[SQ], line=[SQ],
     detail=[P('M88 140 V64 H124 A38 38 0 0 1 124 140 Z'), L(88, 172, 88, 192)])

# LogRocket: the rocket with a porthole and a flame on the app tile.
ROCKET = ('M128 52 C148 68 156 92 156 120 L172 140 V164 L156 156 H100 L84 164 V140 L100 120 '
          'C100 92 108 68 128 52 Z')
icon('logrocket-logo', B, tags('logrocket', 'session replay', 'frontend monitoring', 'analytics'),
     area=[SQ], line=[SQ],
     detail=[P(ROCKET), PL([(116, 180), (128, 198), (140, 180)])],
     dotcut=[C(128, 104, 14)])

# LaunchDarkly: the arrowhead with three streaks running into its tip.
icon('launchdarkly-logo', B, tags('launchdarkly', 'feature flags', 'release', 'devops'),
     line=[PL([(132, 40), (220, 128), (132, 216)]), L(36, 128, 220, 128),
           L(84, 72, 180, 112), L(84, 184, 180, 144)])

# ---------------------------------------------------------------- design tools
# Zeplin: the round mark crossed by a straight band and a curved one.
icon('zeplin-logo', B, tags('zeplin', 'design handoff', 'design', 'developers'),
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[L(38, 161, 218, 95), P('M38 161 C60 190 96 202 128 202 C170 202 206 172 222 134')])

# Balsamiq: the scribbled zigzag.
icon('balsamiq-logo', B, tags('balsamiq', 'wireframes', 'mockups', 'design'),
     line=[PL([(108, 40), (148, 32), (84, 84), (204, 48), (56, 148), (216, 104), (96, 196), (176, 180)])])

# Whimsical: a diamond in front of another, of which only the left corner shows.
W_FRONT = [(150, 64), (214, 128), (150, 192), (86, 128)]
icon('whimsical-logo', B, tags('whimsical', 'whiteboard', 'flowcharts', 'diagrams'),
     area=[PG(W_FRONT)], line=[PG(W_FRONT), PL([(106, 64), (42, 128), (106, 192)])])

# Excalidraw: the long pencil crossing a pen nib and its end block.
EX_BAR = 'M89 201 L201 89 A24 24 0 0 0 167 55 L55 167 A24 24 0 0 0 89 201 Z'
EX_NIB = [(40, 40), (108, 60), (60, 108)]
EX_END = [(148, 184), (184, 148), (216, 180), (180, 216)]
icon('excalidraw-logo', B, tags('excalidraw', 'whiteboard', 'sketch', 'drawing', 'diagrams'),
     area=[P(EX_BAR), PG(EX_NIB), PG(EX_END)], line=[P(EX_BAR), PG(EX_NIB), PG(EX_END)],
     dotcut=[C(172, 84, 14)])

# tldraw: the semicolon on the app tile.
icon('tldraw-logo', B, tags('tldraw', 'whiteboard', 'drawing', 'canvas'),
     area=[SQ], line=[SQ],
     detail=[P('M140 150 C140 172 132 188 114 198')],
     dotcut=[C(128, 96, 14), C(128, 150, 14)])

# Mural: the M of two arches, the inner legs joined at the foot.
MURAL = 'M40 208 V104 A36 36 0 0 1 112 104 V208 H144 V104 A36 36 0 0 1 216 104 V208'
icon('mural-logo', B, tags('mural', 'whiteboard', 'collaboration', 'workshops'),
     line=[P(MURAL)])

# draw.io: three boxes joined as a tree on the app tile.
icon('draw-io-logo', B, tags('draw.io', 'diagrams.net', 'diagrams', 'flowchart'),
     area=[SQ], line=[SQ],
     detail=[R(108, 64, 40, 36, 8), R(64, 148, 40, 36, 8), R(152, 148, 40, 36, 8),
             L(120, 100, 84, 148), L(136, 100, 172, 148)])

# ---------------------------------------------------------------- e-commerce and websites
# Wix: the wordmark, three letters.
icon('wix-logo', B, tags('wix', 'website builder', 'websites', 'hosting'), outline=True,
     line=[PL([(32, 80), (56, 176), (80, 104), (104, 176), (128, 80)]), L(152, 120, 152, 176),
           L(176, 80, 224, 176), L(224, 80, 176, 176)],
     dot=[C(152, 84, 16)])

# WooCommerce: the speech bubble with the W.
WOO = ('M64 56 H192 A32 32 0 0 1 224 88 V144 A32 32 0 0 1 192 176 H144 L156 208 L112 176 H64 '
       'A32 32 0 0 1 32 144 V88 A32 32 0 0 1 64 56 Z')
icon('woocommerce-logo', B, tags('woocommerce', 'woo', 'wordpress', 'e-commerce', 'shop'),
     area=[P(WOO)], line=[P(WOO)],
     detail=[PL([(64, 92), (88, 148), (128, 108), (168, 148), (192, 92)])])

# Magento: the folded hexagon, its roof over two inner pillars.
icon('magento-logo', B, tags('magento', 'adobe commerce', 'e-commerce', 'shop'),
     line=[PL([(36, 208), (36, 92), (128, 40), (220, 92), (220, 208)]),
           PL([(84, 208), (84, 124), (112, 108)]), PL([(172, 208), (172, 124), (144, 108)])])

# ---------------------------------------------------------------- customer support
# Zendesk: the Z of two half discs and two triangles.
ZD = ['M32 48 H112 A40 40 0 0 1 72 88 A40 40 0 0 1 32 48 Z',
      'M144 48 H224 L144 156 Z',
      'M112 208 H32 L112 100 Z',
      'M224 208 H144 A40 40 0 0 1 184 168 A40 40 0 0 1 224 208 Z']
icon('zendesk-logo', B, tags('zendesk', 'customer support', 'help desk', 'tickets'),
     area=[P(d) for d in ZD], line=[P(d) for d in ZD])

# Intercom: four bars over a smile on the app tile.
icon('intercom-logo', B, tags('intercom', 'customer support', 'chat', 'messaging'),
     area=[SQ], line=[SQ],
     detail=[L(80, 76, 80, 136), L(112, 68, 112, 148), L(144, 68, 144, 148), L(176, 76, 176, 136),
             P('M76 168 C92 180 110 186 128 186 C146 186 164 180 180 168')])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
