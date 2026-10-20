"""Brand logos: servers, databases, hosting and SaaS APIs."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
SQ = R(40, 40, 176, 176, 16)
RING = C(128, 128, 96)


def brand(name, tags, **roles):
    icon(name, B, tags + ['logo', 'brand'], **roles)


def ipt(p):
    return (round(p[0]), round(p[1]))


def arc(c, r, a0, a1, move=True):
    """Arc on circle (c, r) from angle a0 to a1 in degrees (y down), anchored at every quarter it passes."""
    step = 1 if a1 > a0 else -1
    stops = [a0]
    q = (math.floor(a0 / 90) + 1) * 90 if step > 0 else (math.ceil(a0 / 90) - 1) * 90
    while (q < a1) if step > 0 else (q > a1):
        stops.append(q)
        q += 90 * step
    stops.append(a1)
    pts = [ipt(polar(c, r, a)) for a in stops]
    d = (f'M{pt(pts[0])}' if move else '')
    for p in pts[1:]:
        d += f' A{f(r)} {f(r)} 0 0 {1 if step > 0 else 0} {pt(p)}'
    return d.strip()


# ---------------------------------------------------------------- servers and data
# NGINX: the upright hexagon with the N.
HEX = [ipt(p) for p in regular_polygon((128, 128), 96, 6)]
brand('nginx-logo', ['nginx', 'web server', 'proxy', 'load balancer', 'server'],
      area=[PG(HEX)], line=[PG(HEX)],
      detail=[PL([(100, 168), (100, 88), (156, 168), (156, 88)])])

# Elasticsearch: the round mark split into a top cap, a middle bar and a bottom cap.
ES_TOP = 'M52 92 C64 56 92 36 128 36 C164 36 192 56 204 92 Z'
ES_BOT = 'M52 164 C64 200 92 220 128 220 C164 220 192 200 204 164 Z'
ES_MID = R(36, 116, 184, 24, 12)
brand('elasticsearch-logo', ['elasticsearch', 'elastic', 'search', 'database'],
      area=[P(ES_TOP), ES_MID, P(ES_BOT)], line=[P(ES_TOP), ES_MID, P(ES_BOT)])

# Kafka: the hub node joined to four outer nodes. Nine simple strokes, checked at 16 px.
K_HUB, K_R, K_N = (100, 128), 24, 20
K_NODES = [(100, 52), (100, 204), (172, 92), (172, 164)]


def k_link(a, b, ra, rb):
    d = dist(a, b)
    u = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    return L(*ipt((a[0] + u[0] * ra, a[1] + u[1] * ra)), *ipt((b[0] - u[0] * rb, b[1] - u[1] * rb)))


brand('kafka-logo', ['kafka', 'apache kafka', 'streaming', 'message queue', 'events'],
      area=[C(*K_HUB, K_R)] + [C(*n, K_N) for n in K_NODES],
      line=[C(*K_HUB, K_R)] + [C(*n, K_N) for n in K_NODES] + [k_link(K_HUB, n, K_R + 8, K_N + 8) for n in K_NODES],
      reviewed=True)

# RabbitMQ: the two ears on the block, with the small square window.
RMQ = 'M48 40 H68 A8 8 0 0 1 76 48 V104 H108 V48 A8 8 0 0 1 116 40 H132 A8 8 0 0 1 140 48 V116 H208 ' \
      'A8 8 0 0 1 216 124 V208 A8 8 0 0 1 208 216 H48 A8 8 0 0 1 40 208 V48 A8 8 0 0 1 48 40 Z'
brand('rabbitmq-logo', ['rabbitmq', 'message broker', 'message queue', 'amqp'],
      area=[P(RMQ)], line=[P(RMQ)], detail=[R(152, 144, 32, 32, 8)])

# ---------------------------------------------------------------- hosting
# Heroku: the hooked h with its accent, on the tile.
brand('heroku-logo', ['heroku', 'hosting', 'cloud', 'platform', 'deploy'],
      area=[SQ], line=[SQ],
      detail=[L(96, 72, 96, 184), P('M96 136 C112 124 128 116 144 116 C154 116 160 122 160 132 V184'),
              L(168, 72, 160, 92)])

# Render: the stem joined to the ball by a sweeping neck.
RENDER = 'M32 112 C72 112 100 108 116 84 C128 60 148 36 184 36 A40 40 0 0 1 224 76 A40 40 0 0 1 184 116 ' \
         'H152 C138 116 128 126 128 140 V224 H32 Z'
brand('render-logo', ['render', 'hosting', 'cloud', 'deploy'],
      area=[P(RENDER)], line=[P(RENDER)])

# Railway: the train nose speeding out of the disc.
brand('railway-logo', ['railway', 'hosting', 'cloud', 'deploy', 'train'],
      area=[RING], line=[RING],
      detail=[P('M36 100 H140 C164 100 180 116 184 140'), L(32, 124, 116, 124), L(39, 164, 217, 164)])

# ---------------------------------------------------------------- auth and messaging
# Clerk: the split ring around the solid dot.
brand('clerk-logo', ['clerk', 'authentication', 'auth', 'login', 'users'],
      line=[P(arc((128, 128), 88, -40, -255)), P(arc((128, 128), 88, 135, 40)), C(128, 128, 24)],
      area=[C(128, 128, 24)])

# Twilio: the ring with four dots.
brand('twilio-logo', ['twilio', 'sms', 'messaging', 'voice', 'api'],
      area=[RING], line=[RING],
      detail=[C(96, 96, 20), C(160, 96, 20), C(96, 160, 20), C(160, 160, 20)])

# SendGrid: two overlapping squares sharing the centre cell.
SG = [(96, 32), (224, 32), (224, 160), (160, 160), (160, 224), (32, 224), (32, 96), (96, 96)]
brand('sendgrid-logo', ['sendgrid', 'twilio', 'email', 'email api', 'transactional email'],
      area=[PG(SG)], line=[PG(SG)], detail=[R(96, 96, 64, 64)])

# ---------------------------------------------------------------- analytics
# Segment: two arcs and two offset bars, a dot inside each arc end.
SEG_C = (128, 128)
brand('segment-logo', ['segment', 'twilio', 'customer data', 'analytics', 'data pipeline'],
      line=[P(arc(SEG_C, 96, 195, 305)), P(arc(SEG_C, 96, 15, 125)), L(112, 116, 216, 116), L(40, 140, 144, 140)],
      dot=[C(172, 80, 16), C(84, 176, 16)])

# Amplitude: the A traced by a wave crossing its bar, in the circle.
brand('amplitude-logo', ['amplitude', 'analytics', 'product analytics', 'wave'],
      area=[RING], line=[RING],
      detail=[L(64, 136, 192, 136),
              P('M72 172 C84 132 96 72 112 72 C128 72 136 184 160 184 C176 184 184 160 188 136')])

# PostHog: the hedgehog, three striped spines and the head with its pointed nose.
PH = 'M32 184 V72 L72 112 V72 L112 112 V72 L156 116 C184 124 204 148 216 168 L224 176 V184 Z'
brand('posthog-logo', ['posthog', 'product analytics', 'analytics', 'hedgehog'],
      area=[P(PH)], line=[P(PH)],
      detail=[L(156, 116, 156, 184), L(72, 112, 144, 184), L(112, 112, 156, 156), L(32, 112, 104, 184),
              L(32, 152, 64, 184)])

# Hotjar: the two flame strokes on the tile.
brand('hotjar-logo', ['hotjar', 'heatmaps', 'analytics', 'user behavior'],
      area=[SQ], line=[SQ],
      detail=[P('M144 64 C144 104 92 96 92 140'), P('M164 116 C164 160 112 152 112 192')])

# Google Analytics: two rounded bars and a dot, rising to the right.
GA = [R(172, 32, 40, 192, 20), R(108, 104, 40, 120, 20), C(64, 204, 20)]
brand('google-analytics-logo', ['google analytics', 'google', 'analytics', 'statistics', 'web analytics'],
      area=GA, line=GA)

# Plausible: the solid P crossed by a rising chart line.
PLA = 'M64 32 H144 A64 64 0 0 1 208 96 A64 64 0 0 1 144 160 H112 V208 A16 16 0 0 1 96 224 H64 ' \
      'A16 16 0 0 1 48 208 V48 A16 16 0 0 1 64 32 Z'
brand('plausible-logo', ['plausible', 'analytics', 'web analytics', 'privacy'],
      area=[P(PLA)], line=[P(PLA)], detail=[PL([(48, 152), (96, 112), (128, 128), (203, 72)])])

# ---------------------------------------------------------------- content
# Strapi: the square with its folded tab and the corner below.
ST = [(104, 32), (224, 32), (224, 152), (152, 152), (104, 224), (104, 152), (80, 152), (32, 104), (104, 104)]
brand('strapi-logo', ['strapi', 'cms', 'headless cms', 'content', 'api'],
      area=[PG(ST)], line=[PG(ST)], detail=[PL([(104, 104), (104, 152), (152, 152)])])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
