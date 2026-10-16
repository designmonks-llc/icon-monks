import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

M, D = 'Media', 'Devices'
CIRC = C(128, 128, 96)

# ---------------------------------------------------------------- Media: transport
icon('play-circle', M, ['start', 'video', 'music', 'resume'],
     line=[CIRC], detail=[PG([(108, 88), (172, 128), (108, 168)])], area=[CIRC])
icon('pause-circle', M, ['hold', 'video', 'music', 'break'],
     line=[CIRC], detail=[L(108, 92, 108, 164), L(148, 92, 148, 164)], area=[CIRC])
icon('stop', M, ['end', 'halt', 'square', 'video'],
     line=[R(56, 56, 144, 144, 16)], area=[R(56, 56, 144, 144, 16)])
icon('stop-circle', M, ['end', 'halt', 'video', 'music'],
     line=[CIRC], detail=[R(100, 100, 56, 56, 8)], area=[CIRC])
icon('record', M, ['rec', 'capture', 'live', 'recording'],
     line=[CIRC, C(128, 128, 44)], area=[C(128, 128, 44)])

SKIP_TRI = [(56, 48), (168, 128), (56, 208)]
icon('skip-forward', M, ['next', 'track', 'forward', 'music'],
     line=[PG(SKIP_TRI), L(208, 48, 208, 208)], area=[PG(SKIP_TRI)])
SKIP_TRI_B = [(256 - x, y) for x, y in SKIP_TRI]
icon('skip-back', M, ['previous', 'track', 'back', 'music'],
     line=[PG(SKIP_TRI_B), L(48, 48, 48, 208)], area=[PG(SKIP_TRI_B)])
FF = [[(32, 56), (128, 128), (32, 200)], [(128, 56), (224, 128), (128, 200)]]
icon('fast-forward', M, ['skip', 'forward', 'speed', 'seek'],
     line=[PG(t) for t in FF], area=[PG(t) for t in FF])
RW = [[(256 - x, y) for x, y in t] for t in FF]
icon('rewind', M, ['back', 'reverse', 'seek', 'replay'],
     line=[PG(t) for t in RW], area=[PG(t) for t in RW])
EJ = [(128, 48), (208, 144), (48, 144)]
icon('eject', M, ['remove', 'disc', 'open', 'unmount'],
     line=[PG(EJ), L(48, 200, 208, 200)], area=[PG(EJ)])

# ---------------------------------------------------------------- Media: audio
spk = 'M32 104 V152 H72 L128 200 V56 L72 104 Z'
icon('speaker-low', M, ['volume', 'sound', 'audio', 'quiet'],
     line=[P(spk), P('M164 96 A48 48 0 0 1 164 160')], area=[P(spk)])
icon('speaker-none', M, ['volume', 'sound', 'audio', 'silent'],
     line=[P(spk)], area=[P(spk)])
icon('speaker-x', M, ['mute', 'volume off', 'silent', 'sound off'],
     line=[P(spk), L(160, 100, 216, 156), L(216, 100, 160, 156)], area=[P(spk)])
icon('microphone-slash', M, ['mute', 'mic off', 'silent', 'voice'],
     line=[R(96, 32, 64, 120, 32), P('M64 128 A64 64 0 0 0 192 128'), L(128, 192, 128, 224), L(48, 48, 208, 208)])

cupL, cupR = R(40, 144, 48, 80, 16), R(168, 144, 48, 80, 16)
icon('headphones', M, ['audio', 'music', 'listen', 'earphones'],
     line=[P('M40 176 V136 A88 88 0 0 1 216 136 V176'), cupL, cupR], area=[cupL, cupR])
hcL, hcR = R(40, 128, 48, 72, 16), R(168, 128, 48, 72, 16)
icon('headset', M, ['support', 'call center', 'gaming', 'microphone'],
     line=[P('M40 160 V128 A88 88 0 0 1 216 128 V160'), hcL, hcR, P('M192 200 C192 216 176 216 152 216')],
     area=[hcL, hcR], dot=[C(136, 216, 16)])

radio = R(32, 88, 192, 128, 16)
icon('radio', M, ['fm', 'broadcast', 'music', 'tuner'],
     line=[radio, L(72, 88, 184, 40)], detail=[C(92, 152, 28), L(152, 136, 184, 136), L(152, 168, 184, 168)],
     area=[radio])
tv = R(32, 80, 192, 136, 16)
icon('television', M, ['tv', 'screen', 'watch', 'broadcast'],
     line=[tv, PL([(88, 32), (128, 80), (168, 32)])], area=[tv])

# ---------------------------------------------------------------- Media: video
film = R(32, 48, 192, 160, 14)
icon('film-strip', M, ['movie', 'video', 'cinema', 'reel'],
     line=[film],
     detail=[L(72, 48, 72, 208), L(184, 48, 184, 208)] +
            [L(32, y, 72, y) for y in (88, 128, 168)] + [L(184, y, 224, y) for y in (88, 128, 168)],
     area=[film])

slate = R(32, 120, 192, 96, 14)
hinge = (40, 112)
arm = rot([(40, 112), (216, 112), (216, 80), (40, 80)], -12, hinge)
along = lambda t, k: (arm[0][0] + (arm[1][0] - arm[0][0]) * t + (arm[3][0] - arm[0][0]) * k,
                      arm[0][1] + (arm[1][1] - arm[0][1]) * t + (arm[3][1] - arm[0][1]) * k)
stripes = [P(f'M{pt(along(t, 0))} L{pt(along(t + 0.12, 1))}') for t in (0.22, 0.48, 0.74)]
icon('film-slate', M, ['clapperboard', 'movie', 'action', 'cinema', 'production'],
     line=[slate, PG(arm)], detail=stripes, area=[slate, PG(arm)])

vbody = R(32, 72, 136, 112, 14)
lens = PG([(168, 112), (224, 84), (224, 172), (168, 144)])
icon('video-camera', M, ['video', 'record', 'camera', 'film', 'meeting'],
     line=[vbody, lens], area=[vbody, lens])
icon('webcam', M, ['camera', 'video call', 'meeting', 'stream'],
     line=[C(128, 104, 72), L(128, 176, 128, 216), L(72, 216, 184, 216)], detail=[C(128, 104, 28)],
     area=[C(128, 104, 72)])

icon('disc', M, ['cd', 'dvd', 'album', 'record', 'vinyl'],
     line=[CIRC, C(128, 128, 28)],
     detail=[P(f'M{pt(polar((128, 128), 60, 200))} A60 60 0 0 1 {pt(polar((128, 128), 60, 250))}')],
     area=[CIRC], hole=[C(128, 128, 20)])

icon('playlist', M, ['queue', 'music', 'list', 'songs'],
     line=[L(40, 64, 216, 64), L(40, 112, 144, 112), L(40, 160, 112, 160), C(160, 192, 24),
           L(184, 192, 184, 104), L(184, 104, 216, 120)],
     area=[C(160, 192, 24)])
icon('music-notes', M, ['music', 'song', 'audio', 'melody'],
     line=[C(72, 184, 28), C(176, 160, 28), L(100, 184, 100, 72), L(204, 160, 204, 48), L(100, 72, 204, 48)],
     area=[C(72, 184, 28), C(176, 160, 28)])

# ---------------------------------------------------------------- Devices: computers
kb = R(32, 64, 192, 128, 14)
icon('keyboard', D, ['typing', 'keys', 'input', 'type'],
     line=[kb], detail=[L(80, 152, 176, 152)], area=[kb],
     dotcut=[C(x, 108, 12) for x in (64, 96, 128, 160, 192)])
icon('mouse', D, ['click', 'pointer', 'input', 'scroll'],
     line=[R(72, 32, 112, 192, 56)], detail=[L(128, 72, 128, 104)], area=[R(72, 32, 112, 192, 56)])

pbody = ('M72 184 H48 A16 16 0 0 1 32 168 V104 A16 16 0 0 1 48 88 H208 A16 16 0 0 1 224 104 V168 '
         'A16 16 0 0 1 208 184 H184')
icon('printer', D, ['print', 'paper', 'document', 'office'],
     line=[P('M72 88 V40 H184 V88'), P(pbody), R(72, 144, 112, 72, 4)],
     area=[R(32, 88, 192, 96, 16), R(72, 40, 112, 48), R(72, 144, 112, 72, 4)],
     hole=[R(80, 152, 96, 56)], dotcut=[C(192, 116, 12)])

pins = []
for v in (92, 128, 164):
    pins += [L(v, 32, v, 64), L(v, 192, v, 224), L(32, v, 64, v), L(192, v, 224, v)]
icon('cpu', D, ['processor', 'chip', 'hardware', 'computer'],
     line=[R(64, 64, 128, 128, 14)] + pins, detail=[R(100, 100, 56, 56, 6)], area=[R(64, 64, 128, 128, 14)])

def drive(y, h):
    cy = y + h / 2
    return R(32, y, 192, h, 14), L(72, cy, 136, cy), C(184, cy, 12)
hd = drive(72, 112)
icon('hard-drive', D, ['storage', 'disk', 'hdd', 'ssd'], line=[hd[0]], detail=[hd[1]], area=[hd[0]], dotcut=[hd[2]])
d1, d2 = drive(32, 80), drive(144, 80)
icon('hard-drives', D, ['server', 'storage', 'rack', 'disks'],
     line=[d1[0], d2[0]], detail=[d1[1], d2[1]], area=[d1[0], d2[0]], dotcut=[d1[2], d2[2]])

db = 'M40 64 A88 32 0 0 1 216 64 V192 A88 32 0 0 1 40 192 Z'
icon('database', D, ['storage', 'data', 'sql', 'server'],
     line=[P(db)], detail=[P('M40 64 A88 32 0 0 0 216 64'), P('M40 128 A88 32 0 0 0 216 128')], area=[P(db)])

# ---------------------------------------------------------------- Devices: connectivity & power
usb_head = PG([(128, 32), (148, 64), (108, 64)])
icon('usb', D, ['port', 'cable', 'connector', 'flash drive'],
     line=[usb_head, L(128, 64, 128, 184), PL([(128, 176), (72, 144), (72, 120)]),
           PL([(128, 152), (184, 120), (184, 96)]), R(176, 80, 16, 16), C(128, 200, 16)],
     area=[usb_head, R(176, 80, 16, 16), C(128, 200, 16)], dot=[C(72, 108, 16)])
icon('bluetooth', D, ['wireless', 'pairing', 'connect', 'signal'],
     line=[PL([(80, 88), (176, 168), (128, 208), (128, 48), (176, 88), (80, 168)])])
plug = 'M64 72 H192 V120 A64 64 0 0 1 64 120 Z'
icon('plug', D, ['power', 'electricity', 'socket', 'connect'],
     line=[P(plug), L(104, 32, 104, 72), L(152, 32, 152, 72), L(128, 184, 128, 224)], area=[P(plug)])

bat = R(32, 72, 168, 112, 16)
icon('battery-charging', D, ['charge', 'power', 'energy', 'plugged in'],
     line=[bat, L(224, 108, 224, 148)], detail=[PL([(124, 100), (100, 132), (132, 124), (108, 156)])], area=[bat])
icon('battery-empty', D, ['low', 'power', 'dead', 'energy'], line=[bat, L(224, 108, 224, 148)], area=[bat])
icon('battery-full', D, ['charged', 'power', 'energy', 'level'],
     line=[bat, L(224, 108, 224, 148)], detail=[L(x, 104, x, 152) for x in (64, 96, 128, 160)], area=[bat])

sim = 'M72 32 H152 L200 80 V208 A16 16 0 0 1 184 224 H72 A16 16 0 0 1 56 208 V48 A16 16 0 0 1 72 32 Z'
icon('sim-card', D, ['mobile', 'carrier', 'chip', 'cellular'],
     line=[P(sim)], detail=[R(92, 116, 72, 76, 8), L(92, 154, 164, 154)], area=[P(sim)])
sd = 'M96 32 H184 A16 16 0 0 1 200 48 V208 A16 16 0 0 1 184 224 H72 A16 16 0 0 1 56 208 V72 Z'
icon('sd-card', D, ['memory', 'storage', 'camera', 'card'],
     line=[P(sd)], detail=[L(x, 72, x, 104) for x in (104, 136, 168)], area=[P(sd)])

wy = 128 - math.sqrt(64 ** 2 - 32 ** 2)
icon('watch', D, ['wristwatch', 'time', 'smartwatch', 'wearable'],
     line=[C(128, 128, 64), P(f'M96 {f(wy)} L104 32 H152 L160 {f(wy)}'), P(f'M96 {f(256 - wy)} L104 224 H152 L160 {f(256 - wy)}')],
     detail=[PL([(128, 100), (128, 128), (148, 140)])], area=[C(128, 128, 64)])
icon('device-tablet', D, ['ipad', 'tablet', 'screen', 'device'],
     line=[R(48, 32, 160, 192, 16)], detail=[L(112, 64, 144, 64)], area=[R(48, 32, 160, 192, 16)])

pad = ('M84 72 H172 C204 72 216 96 220 128 L224 168 C226 192 200 204 184 188 L160 164 H96 L72 188 '
       'C56 204 30 192 32 168 L36 128 C40 96 52 72 84 72 Z')
icon('game-controller', D, ['gaming', 'gamepad', 'console', 'play'],
     line=[P(pad)], detail=[L(68, 120, 100, 120), L(84, 104, 84, 136)], area=[P(pad)],
     dotcut=[C(164, 112, 12), C(188, 136, 12)])
jbase = R(48, 168, 160, 56, 14)
icon('joystick', D, ['gaming', 'arcade', 'controller', 'stick'],
     line=[jbase, L(128, 168, 128, 96), C(128, 64, 32)], area=[jbase, C(128, 64, 32)])

icon('screencast', D, ['cast', 'airplay', 'mirror', 'stream'],
     line=[P('M32 88 V64 A16 16 0 0 1 48 48 H208 A16 16 0 0 1 224 64 V192 A16 16 0 0 1 208 208 H152'),
           P('M40 160 A40 40 0 0 1 80 200'), P('M40 120 A80 80 0 0 1 120 200')],
     dot=[C(40, 200, 16)])
rbox = R(32, 120, 192, 88, 14)
icon('router', D, ['wifi', 'network', 'modem', 'internet'],
     line=[rbox, L(72, 120, 72, 56), L(184, 120, 184, 56)], area=[rbox],
     dotcut=[C(72, 164, 12), C(112, 164, 12)])
icon('cell-signal-full', D, ['signal', 'reception', 'bars', 'mobile', 'network'],
     line=[L(x, 208, x, top) for x, top in ((56, 168), (104, 128), (152, 88), (200, 48))])
wc = (128, 200)
wifi = []
for rr in (44, 88, 132):
    a = polar(wc, rr, -135); b = polar(wc, rr, -45)
    wifi.append(P(f'M{pt(a)} A{rr} {rr} 0 0 1 {pt(b)}'))
icon('wifi-slash', D, ['offline', 'no internet', 'disconnected', 'wireless off'],
     line=wifi + [L(48, 48, 208, 208)], dot=[C(128, 200, 16)])

# ---------------------------------------------------------------- Devices: scanning & identity
finders = [(32, 32), (152, 32), (32, 152)]
icon('qr-code', D, ['scan', 'code', 'link', 'barcode'],
     line=[R(x, y, 72, 72, 10) for x, y in finders],
     dot=[C(x + 36, y + 36, 16) for x, y in finders] + [C(164, 164, 16), C(212, 164, 16), C(188, 212, 16)])
BRK = [PL([(32, 80), (32, 48), (64, 48)]), PL([(192, 48), (224, 48), (224, 80)]),
       PL([(224, 176), (224, 208), (192, 208)]), PL([(64, 208), (32, 208), (32, 176)])]
icon('barcode', D, ['scan', 'product', 'price', 'upc'],
     line=BRK + [L(x, 88, x, 168) for x in (80, 112, 144, 176)])
icon('scan', D, ['scanner', 'capture', 'focus', 'frame'], line=BRK + [L(64, 128, 192, 128)])

fc = (128, 140)
icon('fingerprint', D, ['biometric', 'touch id', 'identity', 'security'],
     line=[P(f'M{pt(polar(fc, 96, 160))} A96 96 0 0 1 {pt(polar(fc, 96, 20))}'),
           P('M64 200 V140 A64 64 0 0 1 192 140 V168'),
           P('M96 176 V140 A32 32 0 0 1 160 140 V200'),
           L(128, 140, 128, 216)])

print(save(overwrite=True))
