import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

CM, PE = 'Communication', 'People'


def bez_split(p0, p1, p2, p3, t):
    """First part of a cubic split at t: returns (p1', p2', end)."""
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = lerp(p0, p1), lerp(p1, p2), lerp(p2, p3)
    d, e = lerp(a, b), lerp(b, c)
    return a, d, lerp(d, e)


class Path:
    """Tiny path builder whose points can be rotated (circular arcs stay valid under rotation)."""
    def __init__(self):
        self.s = []

    def M(self, p): self.s.append(('M', p)); return self
    def L(self, p): self.s.append(('L', p)); return self
    def A(self, r, large, sweep, p): self.s.append(('A', r, large, sweep, p)); return self
    def C(self, a, b, p): self.s.append(('C', a, b, p)); return self
    def Z(self): self.s.append(('Z',)); return self

    def d(self, deg=0, c=(128, 128), dx=0, dy=0):
        R_ = lambda p: (lambda q: (q[0] + dx, q[1] + dy))(rot([p], deg, c)[0])
        out = []
        for seg in self.s:
            k = seg[0]
            if k in 'ML':
                out.append(f'{k}{pt(R_(seg[1]))}')
            elif k == 'A':
                out.append(f'A{f(seg[1])} {f(seg[1])} 0 {seg[2]} {seg[3]} {pt(R_(seg[4]))}')
            elif k == 'C':
                out.append(f'C{pt(R_(seg[1]))} {pt(R_(seg[2]))} {pt(R_(seg[3]))}')
            else:
                out.append('Z')
        return ' '.join(out)


# ---------------------------------------------------------------- Phones
hs = ('M64 40 H96 L112 92 L88 112 C108 132 124 148 144 168 L164 144 L216 160 V192 '
      'A24 24 0 0 1 192 216 C104 216 40 152 40 64 A24 24 0 0 1 64 40 Z')
icon('phone', CM, ['call', 'telephone', 'contact', 'dial', 'handset'], line=[P(hs)], area=[P(hs)])
icon('phone-call', CM, ['calling', 'ringing', 'telephone', 'contact'],
     line=[P(hs), P('M152 40 A64 64 0 0 1 216 104'), P('M152 76 A28 28 0 0 1 180 104')], area=[P(hs)])
icon('phone-incoming', CM, ['call', 'received', 'inbound', 'answer'],
     line=[P(hs), L(212, 44, 156, 100), PL([(156, 64), (156, 100), (192, 100)])], area=[P(hs)])
icon('phone-outgoing', CM, ['call', 'dial', 'outbound', 'calling'],
     line=[P(hs), L(156, 100, 212, 44), PL([(176, 44), (212, 44), (212, 80)])], area=[P(hs)])
icon('phone-x', CM, ['missed', 'hang up', 'declined', 'end call'],
     line=[P(hs), L(160, 48, 208, 96), L(208, 48, 160, 96)], area=[P(hs)])

# ---------------------------------------------------------------- Mail & inbox
env_open = 'M32 104 L128 40 L224 104 V198 A14 14 0 0 1 210 212 H46 A14 14 0 0 1 32 198 Z'
icon('envelope-open', CM, ['email', 'mail', 'read', 'opened', 'message'],
     line=[P(env_open)], detail=[PL([(52, 124), (128, 172), (204, 124)])], area=[P(env_open)])
icon('tray', CM, ['inbox', 'mailbox', 'messages', 'incoming'],
     line=[R(32, 48, 192, 160, 14)], detail=[P('M52 140 H84 L100 164 H156 L172 140 H204')],
     area=[R(32, 48, 192, 160, 14)])
arch_body = 'M48 96 V200 A16 16 0 0 0 64 216 H192 A16 16 0 0 0 208 200 V96'
icon('archive', CM, ['box', 'storage', 'store', 'save'],
     line=[R(32, 44, 192, 52, 12), P(arch_body)], detail=[L(104, 140, 152, 140)],
     area=[R(32, 44, 192, 52, 12), P(arch_body + ' Z')])

# ---------------------------------------------------------------- Chat
cc = (132, 124)
cp1, cp2 = polar(cc, 92, 150), polar(cc, 92, 112)
chat_c = f'M{pt(cp2)} L40 216 L{pt(cp1)} A92 92 0 1 1 {pt(cp2)} Z'
icon('chat-circle', CM, ['message', 'comment', 'bubble', 'talk'], line=[P(chat_c)], area=[P(chat_c)])
front = 'M64 192 L32 216 V104 A16 16 0 0 1 48 88 H152 A16 16 0 0 1 168 104 V176 A16 16 0 0 1 152 192 Z'
back = 'M88 88 V56 A16 16 0 0 1 104 40 H208 A16 16 0 0 1 224 56 V184 L192 152 H168'
icon('chats', CM, ['messages', 'conversation', 'discussion', 'chat', 'reply'],
     line=[P(front), P(back)], area=[P(front), P(back + ' V88 Z')])
bub = 'M80 200 L40 224 V72 A16 16 0 0 1 56 56 H200 A16 16 0 0 1 216 72 V184 A16 16 0 0 1 200 200 Z'
icon('chat-dots', CM, ['typing', 'message', 'comment', 'bubble', 'reply'],
     line=[P(bub)], area=[P(bub)], dotcut=[C(88, 128, 16), C(128, 128, 16), C(168, 128, 16)])

# ---------------------------------------------------------------- Broadcast
horn = 'M56 100 H104 L216 44 V212 L104 156 H56 A16 16 0 0 1 40 140 V116 A16 16 0 0 1 56 100 Z'
handle = [(72, 156), (88, 212), (116, 212), (110, 159)]
icon('megaphone', CM, ['announcement', 'loudspeaker', 'marketing', 'promote', 'bullhorn'],
     line=[P(horn), PL(handle)], area=[P(horn), PG(handle)])
bc = (128, 128)
waves = []
for rr in (56, 96):
    for a1, a2 in ((-42, 42), (138, 222)):
        p, q = polar(bc, rr, a1), polar(bc, rr, a2)
        waves.append(P(f'M{pt(p)} A{rr} {rr} 0 0 1 {pt(q)}'))
icon('broadcast', CM, ['radio', 'signal', 'stream', 'live', 'antenna'],
     line=[C(128, 128, 18)] + waves, area=[C(128, 128, 18)])
icon('rss', CM, ['feed', 'subscribe', 'news', 'blog', 'podcast'],
     line=[P('M48 120 A88 88 0 0 1 136 208'), P('M48 48 A160 160 0 0 1 208 208')], dot=[C(66, 190, 22)])
icon('voicemail', CM, ['voice message', 'recording', 'answering machine', 'tape'],
     line=[C(76, 128, 44), C(180, 128, 44), L(76, 172, 180, 172)], area=[C(76, 128, 44), C(180, 128, 44)])

# ---------------------------------------------------------------- Users with a badge
# Reduced user figure (head r=40, shoulders cut short before the lower-right badge).
B = (188, 184)
uh = C(104, 84, 40)
b0, b1, b2, b3 = (104, 148), (144, 148), (176, 172), (176, 216)
s1, s2, s_end = bez_split(b0, b1, b2, b3, 0.42)
ubody = f'M32 216 C32 172 64 148 104 148 C{pt(s1)} {pt(s2)} {pt(s_end)}'
rb = dist(s_end, B)
xb = B[0] - math.sqrt(max(rb * rb - (216 - B[1]) ** 2, 0))
ubody_area = ubody + f' A{f(rb)} {f(rb)} 0 0 0 {f(xb)} 216 Z'


def badge_user(name, tags, marks):
    icon(name, PE, tags, line=[uh, P(ubody)] + marks, area=[uh, P(ubody_area)])


badge_user('user-plus', ['add user', 'invite', 'new contact', 'follow', 'signup'],
           [L(B[0] - 28, B[1], B[0] + 28, B[1]), L(B[0], B[1] - 28, B[0], B[1] + 28)])
badge_user('user-minus', ['remove user', 'unfollow', 'delete contact', 'kick'],
           [L(B[0] - 28, B[1], B[0] + 28, B[1])])
badge_user('user-check', ['verified', 'approved', 'friend', 'confirmed', 'member'],
           [PL([(B[0] - 28, B[1] + 2), (B[0] - 8, B[1] + 22), (B[0] + 28, B[1] - 18)])])

uc = (128, 128)
q1, q2 = polar(uc, 96, 137), polar(uc, 96, 43)
uc_body = f'M{pt(q1)} C76 174 100 164 128 164 C156 164 180 174 {pt(q2)}'
icon('user-circle', PE, ['account', 'profile', 'avatar', 'person', 'login'],
     line=[C(128, 128, 96), C(128, 100, 32), P(uc_body)],
     area=[C(128, 100, 32), P(uc_body + f' A96 96 0 0 1 {pt(q1)} Z')])
us_body = 'M64 224 C64 184 92 164 128 164 C164 164 192 184 192 224'
icon('user-square', PE, ['account', 'profile', 'avatar', 'person', 'contact'],
     line=[R(32, 32, 192, 192, 16), C(128, 100, 32), P(us_body)],
     area=[C(128, 100, 32), P(us_body + ' Z')])

# ---------------------------------------------------------------- Cards & contacts
icon('identification-card', PE, ['id', 'badge', 'license', 'identity', 'passport'],
     line=[R(32, 56, 192, 144, 14)],
     detail=[C(90, 104, 18), P('M60 168 C60 152 72 144 90 144 C108 144 120 152 120 168 Z'),
             L(150, 108, 188, 108), L(150, 148, 176, 148)],
     area=[R(32, 56, 192, 144, 14)])
icon('address-book', PE, ['contacts', 'directory', 'phonebook', 'people'],
     line=[R(64, 32, 144, 192, 14), L(44, 72, 80, 72), L(44, 128, 80, 128), L(44, 184, 80, 184)],
     detail=[C(140, 96, 22), P('M104 180 C104 160 118 148 140 148 C162 148 176 160 176 180 Z')],
     area=[R(64, 32, 144, 192, 14)])

# ---------------------------------------------------------------- Gestures
hand_shape = ('M68 104 L112 76 H148 L188 100 V148 H180 V168 H156 V188 H132 V208 H116 L68 160 Z')
icon('handshake', PE, ['deal', 'agreement', 'partnership', 'welcome', 'trust'],
     line=[P(hand_shape), L(32, 100, 44, 172), L(224, 92, 212, 164)],
     detail=[L(180, 148, 156, 124), L(156, 168, 128, 140), L(132, 188, 104, 160)],
     area=[P(hand_shape)])

hw = (Path().M((72, 136)).L((72, 88)).A(16, 0, 1, (104, 88)).L((104, 64)).A(16, 0, 1, (136, 64))
      .L((136, 68)).A(16, 0, 1, (168, 68)).L((168, 96)).A(16, 0, 1, (200, 96)).L((200, 160))
      .C((200, 200), (176, 224), (136, 224)).C((112, 224), (96, 216), (84, 200)).L((48, 154))
      .A(16, 0, 1, (72, 136)).Z())
hwd = hw.d(18, (136, 160), -8, -2)
hw_sep = [rot([(104, 88), (104, 128)], 18, (136, 160)), rot([(136, 68), (136, 128)], 18, (136, 160)),
          rot([(168, 96), (168, 128)], 18, (136, 160))]
hw_sep = [L(a[0] - 8, a[1] - 2, b[0] - 8, b[1] - 2) for a, b in hw_sep]
icon('hand-waving', PE, ['hello', 'hi', 'wave', 'greeting', 'goodbye'],
     line=[P(hwd), P('M180 32 A44 44 0 0 1 224 76'), P('M32 180 A44 44 0 0 0 76 224')],
     detail=hw_sep, area=[P(hwd)])

# ---------------------------------------------------------------- Figures
icon('person', PE, ['human', 'man', 'woman', 'body', 'figure'],
     line=[C(128, 56, 24), L(128, 100, 128, 152), PL([(68, 148), (128, 108), (188, 148)]),
           PL([(84, 220), (128, 152), (172, 220)])],
     area=[C(128, 56, 24)])
icon('baby', PE, ['infant', 'child', 'newborn', 'kid', 'toddler'],
     line=[C(128, 140, 84), P('M128 56 C128 40 144 34 154 44')],
     detail=[P('M104 176 A28 28 0 0 0 152 176')], area=[C(128, 140, 84)],
     dotcut=[C(96, 140, 14), C(160, 140, 14)])
mc = (104, 152)
mp = polar(mc, 64, -45)
icon('gender-male', PE, ['male', 'man', 'boy', 'mars', 'sex'],
     line=[C(*mc, 64), L(mp[0], mp[1], 216, 40), PL([(160, 40), (216, 40), (216, 96)])], area=[C(*mc, 64)])
icon('gender-female', PE, ['female', 'woman', 'girl', 'venus', 'sex'],
     line=[C(128, 96, 64), L(128, 160, 128, 224), L(92, 196, 164, 196)], area=[C(128, 96, 64)])
crown = 'M56 184 L36 76 L88 120 L128 52 L168 120 L220 76 L200 184 Z'
icon('crown', PE, ['king', 'queen', 'royal', 'premium', 'winner'],
     line=[P(crown), L(56, 216, 200, 216)], area=[P(crown)])
board = [(128, 56), (224, 104), (128, 152), (32, 104)]
capb = 'M80 128 V176 C80 196 104 208 128 208 C152 208 176 196 176 176 V128'
icon('graduation-cap', PE, ['education', 'school', 'student', 'degree', 'university'],
     line=[PG(board), P(capb), L(208, 112, 208, 172)], area=[PG(board), P(capb + ' Z')])

# ---------------------------------------------------------------- Body & characters
ear = 'M76 100 A60 60 0 0 1 196 100 C196 140 168 148 160 172 C152 200 136 220 108 220 C92 220 80 212 72 200'
icon('ear', PE, ['hearing', 'listen', 'audio', 'sound', 'deaf'],
     line=[P(ear)], detail=[P('M112 112 A24 24 0 0 1 160 104 C160 124 140 132 136 152')],
     area=[P(ear + ' C64 180 76 140 76 100 Z')])

brain_l = 'M128 56 A32 32 0 0 0 72 64 A32 32 0 0 0 44 112 A32 32 0 0 0 52 164 A32 32 0 0 0 96 204 A32 32 0 0 0 128 200'
brain_r = 'M128 56 A32 32 0 0 1 184 64 A32 32 0 0 1 212 112 A32 32 0 0 1 204 164 A32 32 0 0 1 160 204 A32 32 0 0 1 128 200'
icon('brain', PE, ['mind', 'think', 'intelligence', 'smart', 'idea'],
     line=[P(brain_l), P(brain_r)],
     detail=[L(128, 72, 128, 188), P('M84 132 A28 28 0 0 1 100 104'), P('M172 132 A28 28 0 0 0 156 104')],
     area=[P(brain_l + ' Z'), P(brain_r + ' Z'), R(110, 60, 36, 140)])

sc = (128, 120)
k1, k2 = polar(sc, 88, 150), polar(sc, 88, 30)
skull = f'M{pt(k1)} A88 88 0 1 1 {pt(k2)} L176 180 V200 A16 16 0 0 1 160 216 H96 A16 16 0 0 1 80 200 V180 Z'
icon('skull', PE, ['death', 'danger', 'poison', 'halloween', 'pirate'],
     line=[P(skull)], detail=[L(112, 192, 112, 216), L(144, 192, 144, 216)], area=[P(skull)],
     dotcut=[C(92, 128, 20), C(164, 128, 20)])
ghost = 'M48 216 V112 A80 80 0 0 1 208 112 V216 L181.33 196 L154.67 216 L128 196 L101.33 216 L74.67 196 Z'
icon('ghost', PE, ['halloween', 'spooky', 'boo', 'spirit', 'phantom'],
     line=[P(ghost)], area=[P(ghost)], dotcut=[C(100, 112, 16), C(156, 112, 16)])
icon('robot', PE, ['bot', 'ai', 'android', 'machine', 'automation'],
     line=[R(48, 88, 160, 128, 24), L(128, 56, 128, 88)], detail=[L(104, 176, 152, 176)],
     area=[R(48, 88, 160, 128, 24)], dot=[C(128, 48, 16)], dotcut=[C(96, 140, 16), C(160, 140, 16)])
alien = 'M128 224 C84 224 44 168 44 116 A84 84 0 0 1 212 116 C212 168 172 224 128 224 Z'
eye_l = 'M68 124 C92 116 112 128 112 152 C88 160 68 148 68 124 Z'
eye_r = 'M188 124 C164 116 144 128 144 152 C168 160 188 148 188 124 Z'
icon('alien', PE, ['ufo', 'extraterrestrial', 'space', 'martian', 'et'],
     line=[P(alien)], detail=[P(eye_l), P(eye_r)], hole=[P(eye_l), P(eye_r)], area=[P(alien)])

print(save(overwrite=True))
