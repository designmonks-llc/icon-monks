"""Brand logos: messaging, meetings, creators, communities and media."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)


def ipt(p):
    return (round(p[0]), round(p[1]))


# ---------------------------------------------------------------- messaging
# Kik: the lowercase wordmark, k i k.
icon('kik-logo', B, ['kik', 'messenger', 'messaging', 'chat', 'logo', 'brand'],
     line=[L(40, 40, 40, 216), L(92, 112, 40, 164), L(62, 144, 96, 216),
           L(128, 120, 128, 216),
           L(168, 40, 168, 216), L(220, 112, 168, 164), L(190, 144, 224, 216)],
     dot=[C(128, 64, 16)], outline=True)

# Element: four quarter arcs turning around the centre, each offset so their ends never meet.
icon('element-logo', B, ['element', 'matrix', 'messenger', 'chat', 'encrypted', 'logo', 'brand'],
     line=[P('M108 40 A64 64 0 0 1 172 104'), P('M216 108 A64 64 0 0 1 152 172'),
           P('M148 216 A64 64 0 0 1 84 152'), P('M40 148 A64 64 0 0 1 104 84')])

# ---------------------------------------------------------------- meetings and scheduling
# Webex: two interlocking waves forming a looped W.
icon('webex-logo', B, ['webex', 'cisco', 'video call', 'meetings', 'conference', 'logo', 'brand'],
     line=[P('M40 92 C44 156 64 200 92 200 C116 200 124 164 132 128 C140 92 148 56 176 56 '
             'C196 56 208 72 212 96'),
           P('M48 100 C52 72 64 56 84 56 C108 56 116 92 124 128 C132 164 140 200 168 200 '
             'C196 200 212 156 216 96')])

# Calendly: the C inside its rounded-square ring.
CAL_SQ = R(40, 40, 176, 176, 56)
icon('calendly-logo', B, ['calendly', 'scheduling', 'calendar', 'meetings', 'booking', 'logo', 'brand'],
     area=[CAL_SQ], line=[CAL_SQ],
     detail=[P('M156 100 A40 40 0 1 0 156 156')])

# ---------------------------------------------------------------- forms
# Typeform: a narrow pill beside a wide rounded block.
TF_A, TF_B = R(32, 60, 40, 136, 20), R(112, 60, 112, 136, 32)
icon('typeform-logo', B, ['typeform', 'forms', 'surveys', 'questionnaire', 'logo', 'brand'],
     area=[TF_A, TF_B], line=[TF_A, TF_B])

# Jotform: three slanted bars and the corner triangle.
JF_T = PG([(52, 176), (52, 224), (100, 224)])
icon('jotform-logo', B, ['jotform', 'forms', 'surveys', 'form builder', 'logo', 'brand'],
     area=[JF_T], line=[L(68, 120, 140, 48), L(116, 160, 204, 72), L(164, 208, 204, 168), JF_T])

# ---------------------------------------------------------------- creators and communities
# Substack: two bars over the bookmark ribbon.
SS = PG([(48, 128), (208, 128), (208, 216), (128, 176), (48, 216)])
icon('substack-logo', B, ['substack', 'newsletter', 'publishing', 'writing', 'blog', 'logo', 'brand'],
     area=[SS], line=[L(48, 48, 208, 48), L(48, 88, 208, 88), SS])

# Hashnode: the rounded diamond with a round hole.
HN = ('M100 44 A40 40 0 0 1 128 32 A40 40 0 0 1 156 44 L212 100 A40 40 0 0 1 224 128 '
      'A40 40 0 0 1 212 156 L156 212 A40 40 0 0 1 128 224 A40 40 0 0 1 100 212 L44 156 '
      'A40 40 0 0 1 32 128 A40 40 0 0 1 44 100 Z')
icon('hashnode-logo', B, ['hashnode', 'blogging', 'developer', 'blog', 'community', 'logo', 'brand'],
     area=[P(HN)], line=[P(HN)], detail=[C(128, 128, 32)])

# Stack Exchange: the stacked bands, the bottom one with its speech tail.
SE = 'M40 160 H216 V176 A16 16 0 0 1 200 192 H160 L128 224 V192 H56 A16 16 0 0 1 40 176 Z'
icon('stack-exchange-logo', B, ['stack exchange', 'questions', 'answers', 'q&a', 'community', 'logo', 'brand'],
     area=[P(SE)], line=[L(40, 40, 216, 40), L(40, 80, 216, 80), L(40, 120, 216, 120), P(SE)])

# Discourse: the speech bubble with its square corner, holding a smaller bubble.
DC_C = (128, 128)
DC_A, DC_B, DC_TIP = ipt(polar(DC_C, 44, 165)), ipt(polar(DC_C, 44, 115)), (84, 180)
DC_IN = (f'M{pt(DC_A)} ' + arc_to(DC_C, 44, DC_A, DC_B, lambda m: dist(m, DC_TIP))
         + f' L{pt(DC_TIP)} Z')
DC_OUT = 'M40 216 V128 A88 88 0 1 1 128 216 Z'
icon('discourse-logo', B, ['discourse', 'forum', 'discussion', 'community', 'chat', 'logo', 'brand'],
     area=[P(DC_OUT)], line=[P(DC_OUT)], detail=[P(DC_IN)])

# Lemmy: the lemming's face, round ears over the head.
LM_H, LM_L, LM_R = ((128, 148), 68), ((72, 80), 32), ((184, 80), 32)
la_top, la_low = [ipt(p) for p in circle_x(LM_L[0], LM_L[1], LM_H[0], LM_H[1])]
ra_top, ra_low = [ipt(p) for p in circle_x(LM_R[0], LM_R[1], LM_H[0], LM_H[1])]
far = lambda c: (lambda m: dist(m, c))
LM = (f'M{pt(la_low)} ' + arc_to(LM_L[0], LM_L[1], la_low, la_top, far(LM_H[0]))
      + ' ' + arc_to(LM_H[0], LM_H[1], la_top, ra_top, lambda m: -m[1])
      + ' ' + arc_to(LM_R[0], LM_R[1], ra_top, ra_low, far(LM_H[0]))
      + ' ' + arc_to(LM_H[0], LM_H[1], ra_low, la_low, lambda m: m[1]) + ' Z')
icon('lemmy-logo', B, ['lemmy', 'lemming', 'fediverse', 'forum', 'community', 'logo', 'brand'],
     area=[P(LM)], line=[P(LM)], dotcut=[C(102, 150, 14), C(154, 150, 14), C(128, 188, 14)])

# ---------------------------------------------------------------- media
# VSCO: the outer ring divided into segments around an inner ring.
VS_SPOKES = [L(*ipt(polar((128, 128), 56, a)), *ipt(polar((128, 128), 96, a))) for a in range(0, 360, 45)]
icon('vsco-logo', B, ['vsco', 'photography', 'photo editing', 'camera', 'filters', 'logo', 'brand'],
     area=[RING], line=[RING], detail=[C(128, 128, 56)] + VS_SPOKES, reviewed=True)

# Letterboxd: three overlapping dots in a row.
LB = [C(72, 128, 40), C(128, 128, 40), C(184, 128, 40)]
icon('letterboxd-logo', B, ['letterboxd', 'films', 'movies', 'reviews', 'social', 'logo', 'brand'],
     area=LB, line=LB)

# Bandcamp: the slanted parallelogram in the circle.
icon('bandcamp-logo', B, ['bandcamp', 'music', 'artists', 'store', 'streaming', 'logo', 'brand'],
     area=[RING], line=[RING], detail=[PG([(104, 104), (176, 104), (152, 152), (80, 152)])])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
