import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

M = 'Media'
SLASH = L(48, 48, 208, 208)


def gapped(x1, y1, x2, y2, g=36, minlen=12):
    """Straight line with the part near the 48,48-208,208 slash removed (g = gap along the line's axis)."""
    n = 400; keep = []; cur = None
    for i in range(n + 1):
        t = i / n; x = x1 + (x2 - x1) * t; y = y1 + (y2 - y1) * t
        near = abs(x - y) / math.sqrt(2) < g / math.sqrt(2) and 30 < (x + y) / 2 < 226
        if not near:
            cur = cur or [(x, y)]
            cur.append((x, y)) if len(cur) == 1 else cur.__setitem__(1, (x, y))
        elif cur:
            keep.append(cur); cur = None
    if cur:
        keep.append(cur)
    return [L(a[0], a[1], b[0], b[1]) for a, *rest in keep for b in [rest[-1] if rest else a]
            if math.hypot(b[0] - a[0], b[1] - a[1]) >= minlen]


def no_area(src, *extra):
    """Slash variant: base lines + details as lines, no area."""
    return dict(line=src['line'] + src['detail'] + list(extra), dot=src['dot'] + src['dotcut'])


# ---------------------------------------------------------------- tiny glyph set for numbers
def glyph(ch, x, y, h):
    """Return (lines, dots, width) for a glyph with top-left (x, y) and cap height h."""
    if ch == '0':
        w = 0.66 * h
        return [R(x, y, w, h, w / 2)], [], w
    if ch == '1':
        w = 0.36 * h
        return [PL([(x, y + 0.3 * h), (x + w, y), (x + w, y + h)])], [], w
    if ch == '2':
        w = 0.66 * h; rt = w / 2; tc = (x + rt, y + rt)
        p0 = polar(tc, rt, -165); p1 = polar(tc, rt, 40)
        return [P(f'M{pt(p0)} A{f(rt)} {f(rt)} 0 0 1 {pt(p1)} L{pt((x, y + h))} H{f(x + w)}')], [], w
    if ch == '3':
        w = 0.62 * h; rb = 0.33 * h; bc = (x + w - rb, y + h - rb)
        p0 = polar(bc, rb, -118); p1 = polar(bc, rb, 145)
        return [P(f'M{pt((x + 0.04 * h, y))} H{f(x + w)} L{pt(p0)} A{f(rb)} {f(rb)} 0 1 1 {pt(p1)}')], [], w
    if ch == '5':
        w = 0.64 * h; rb = 0.34 * h; bc = (x + w - rb, y + h - rb)
        p0 = polar(bc, rb, -145); p1 = polar(bc, rb, 145)
        return [P(f'M{pt((x + w, y))} H{f(p0[0] + 2)} L{pt(p0)} A{f(rb)} {f(rb)} 0 1 1 {pt(p1)}')], [], w
    if ch == '6':
        w = 0.64 * h; rb = w / 2; bc = (x + rb, y + h - rb)
        p0 = polar(bc, rb, 200)
        return [C(*bc, rb), P(f'M{pt(p0)} L{pt((x + 0.72 * w, y))}')], [], w
    if ch == 'x':
        w = 0.5 * h
        return [L(x, y + 0.42 * h, x + w, y + h), L(x + w, y + 0.42 * h, x, y + h)], [], w
    if ch == '.':
        r = 12
        return [], [C(x + 4, y + h - 4, r)], 8
    raise ValueError(ch)


def text(s, cx, cy, h, gap):
    widths = [glyph(ch, 0, 0, h)[2] for ch in s]
    gaps = []
    for i in range(len(s) - 1):
        g = gap
        if '.' in (s[i], s[i + 1]):
            g = gap * 0.9
        gaps.append(g)
    total = sum(widths) + sum(gaps)
    x = cx - total / 2; y = cy - h / 2
    lines, dots = [], []
    for i, ch in enumerate(s):
        l, d, w = glyph(ch, x, y, h)
        lines += l; dots += d
        x += w + (gaps[i] if i < len(gaps) else 0)
    return lines, dots


# ---------------------------------------------------------------- playlists
pl = load('playlist')
L1, L2, L3 = L(40, 64, 216, 64), L(40, 112, 144, 112), L(40, 160, 112, 160)
tri = PG([(156, 128), (220, 172), (156, 216)])
icon('playlist-play', M, ['play queue', 'play list', 'start playlist'],
     line=[L1, L(40, 112, 128, 112), L3, tri], area=[tri])
icon('playlist-plus', M, ['add to playlist', 'queue', 'add', 'music', 'plus'],
     line=[L1, L2, L3, L(180, 136, 180, 208), L(144, 172, 216, 172)])
icon('playlist-x', M, ['remove from playlist', 'playlist', 'music', 'delete'],
     line=[L1, L2, L3, L(152, 144, 208, 200), L(208, 144, 152, 200)])
icon('playlist-slash', M, ['playlist', 'off', 'disabled', 'hidden'],
     line=gapped(40, 64, 216, 64) + gapped(40, 112, 144, 112) + gapped(40, 160, 112, 160) + pl['line'][3:] + [SLASH])

qtri = PG([(40, 48), (96, 80), (40, 112)])
icon('queue', M, ['queue', 'up next', 'playlist'],
     line=[qtri, L(136, 80, 216, 80), L(40, 152, 216, 152), L(40, 208, 216, 208)], area=[qtri])

# ---------------------------------------------------------------- slashes of existing icons
for nm, base, tags in [
    ('radio-slash', 'radio', ['radio', 'off', 'disabled', 'hidden']),
    ('repeat-slash', 'repeat', ['repeat off', 'no loop', 'playback', 'disabled']),
    ('screencast-slash', 'screencast', ['screencast', 'disabled', 'off', 'media']),
    ('voicemail-slash', 'voicemail', ['voicemail', 'off', 'disabled', 'hidden']),
]:
    icon(nm, M, tags, **no_area(load(base), SLASH))

# ---------------------------------------------------------------- record player & vinyl
vin_grooves = [P(f'M{pt(polar((128, 128), 64, -160))} A64 64 0 0 1 {pt(polar((128, 128), 64, -110))}'),
               P(f'M{pt(polar((128, 128), 64, 20))} A64 64 0 0 1 {pt(polar((128, 128), 64, 70))}')]
icon('vinyl-record', M, ['vinyl', 'record', 'lp', 'music', 'turntable'],
     line=[C(128, 128, 96)], detail=[C(128, 128, 32)] + vin_grooves, area=[C(128, 128, 96)],
     dotcut=[C(128, 128, 10)])

base_rp = R(32, 48, 192, 160, 14)
icon('record-player', M, ['record player', 'turntable', 'vinyl', 'music'],
     line=[base_rp], detail=[C(112, 128, 48), PL([(184, 80), (184, 152), (156, 176)])],
     area=[base_rp], dotcut=[C(112, 128, 12), C(184, 80, 16)])

# ---------------------------------------------------------------- replay / seek
RC = (128, 140); RR = 84


def ring_arrow(ccw=True):
    top = (128, RC[1] - RR)
    if ccw:
        end = polar(RC, RR, -150)
        return [P(f'M{pt(top)} A{RR} {RR} 0 1 1 {pt(end)}'), PL([(152, top[1] - 24), top, (152, top[1] + 24)])]
    end = polar(RC, RR, -30)
    return [P(f'M{pt(top)} A{RR} {RR} 0 1 0 {pt(end)}'), PL([(104, top[1] - 24), top, (104, top[1] + 24)])]


def counter(s, ccw, nm, tags):
    h = 64 if len(s) == 1 else 54
    tl, td = text(s, 128, 146, h, 16)
    icon(nm, M, tags, line=ring_arrow(ccw) + tl, dot=td)


counter('10', True, 'replay-10', ['rewind 10', 'back 10 seconds', 'replay', 'skip back', 'rewind 10 seconds'])
counter('30', True, 'replay-30', ['rewind 30', 'back 30 seconds', 'replay', 'skip back'])
counter('5', True, 'replay-5', ['rewind 5', 'back 5 seconds', 'replay', 'skip back', 'replay 5 seconds'])
counter('15', True, 'skip-back-15', ['rewind 15', 'replay', 'back 15 seconds'])
counter('10', False, 'seek-forward', ['forward 10', 'skip ahead', 'seek', 'jump'])
counter('15', False, 'skip-forward-15', ['forward 15', 'jump ahead', 'skip 15 seconds'])

# ---------------------------------------------------------------- circle transport
CIR = C(128, 128, 96)
icon('rewind-circle', M, ['rewind', 'back', 'media', 'circle'], line=[CIR], area=[CIR],
     detail=[PG([(176, 96), (128, 128), (176, 160)]), PG([(128, 96), (80, 128), (128, 160)])])
icon('skip-back-circle', M, ['previous', 'skip back', 'circle', 'media', 'previous track'], line=[CIR], area=[CIR],
     detail=[L(92, 92, 92, 164), PG([(164, 92), (116, 128), (164, 164)])])
icon('skip-forward-circle', M, ['next', 'skip forward', 'circle', 'media'], line=[CIR], area=[CIR],
     detail=[L(164, 92, 164, 164), PG([(92, 92), (140, 128), (92, 164)])])

# ---------------------------------------------------------------- speed
for s, nm, tags, h in [
    ('0.5x', 'speed-0-5x', ['0.5x', 'half speed', 'playback', 'slow'], 72),
    ('1.5x', 'speed-1-5x', ['1.5x', 'playback speed', 'faster', 'video'], 76),
    ('1x', 'speed-1x', ['1x', 'normal speed', 'playback', 'video'], 104),
    ('2x', 'speed-2x', ['2x', 'double speed', 'playback', 'fast'], 104),
]:
    tl, td = text(s, 128, 128, h, 28)
    icon(nm, M, tags, line=tl, dot=td)

# ---------------------------------------------------------------- stack-play, subtitles
front = R(32, 88, 192, 136, 14)
icon('stack-play', M, ['collection', 'playlist', 'videos', 'library'],
     line=[front, L(64, 48, 192, 48)],
     detail=[PG([(110, 126), (160, 156), (110, 186)])], area=[front])
sub = R(32, 48, 192, 160, 14)
sub_lines = [L(64, 136, 128, 136), L(160, 136, 192, 136), L(64, 172, 96, 172), L(128, 172, 192, 172)]
icon('subtitles', M, ['subtitles', 'captions', 'text', 'video'], line=[sub], detail=sub_lines, area=[sub])
icon('subtitles-slash', M, ['subtitles off', 'captions off', 'no text', 'slash'], line=[sub] + gapped(64, 136, 128, 136) + gapped(160, 136, 192, 136) + gapped(64, 172, 96, 172)
     + gapped(128, 172, 192, 172) + [SLASH])

# ---------------------------------------------------------------- surround sound
box = R(100, 72, 56, 112, 14)
arcs = []
for rr, sp in ((64, 32), (96, 36)):
    arcs.append(P(f'M{pt(polar((128, 128), rr, -sp))} A{rr} {rr} 0 0 1 {pt(polar((128, 128), rr, sp))}'))
    arcs.append(P(f'M{pt(polar((128, 128), rr, 180 - sp))} A{rr} {rr} 0 0 1 {pt(polar((128, 128), rr, 180 + sp))}'))
icon('surround-sound', M, ['surround', 'speakers', 'audio', '5.1'], line=[box] + arcs, area=[box],
     dotcut=[C(128, 148, 12)])

# ---------------------------------------------------------------- tilt shift
dashes = []
for i in range(8):
    a = -90 + i * 45
    dashes.append(P(f'M{pt(polar((128, 128), 96, a - 11))} A96 96 0 0 1 {pt(polar((128, 128), 96, a + 11))}'))
icon('tilt-shift', M, ['tilt shift', 'lens', 'focus', 'photography'], line=[C(128, 128, 48)] + dashes,
     area=[C(128, 128, 48)])
icon('tilt-shift-slash', M, ['tilt shift', 'off', 'disabled', 'hidden', 'tilt'],
     line=[C(128, 128, 48)] + dashes + [SLASH])

# ---------------------------------------------------------------- timelapse
icon('timelapse', M, ['timelapse', 'time', 'video', 'camera'], line=[CIR], area=[CIR],
     detail=[P('M128 128 V72 A56 56 0 1 1 72 128 Z')])

# ---------------------------------------------------------------- treble clef
clef = ('M112 200 C112 224 148 228 148 200 L132 56 C128 24 172 28 164 64 '
        'C156 100 84 112 84 156 C84 196 172 200 172 160 C172 124 120 120 116 152')
icon('treble-clef', M, ['clef', 'music', 'notation'], line=[P(clef)])

# ---------------------------------------------------------------- trumpet
bell_t = PG([(172, 108), (224, 68), (224, 172), (172, 132)])
icon('trumpet', M, ['trumpet', 'brass', 'horn', 'music'],
     line=[L(32, 104, 32, 136), L(32, 120, 172, 120), bell_t,
           P('M72 120 V156 A28 28 0 0 0 100 184 H116 A28 28 0 0 0 144 156 V120'),
           L(72, 64, 72, 120), L(108, 64, 108, 120), L(144, 64, 144, 120)],
     area=[bell_t])

# ---------------------------------------------------------------- video camera variants
vc = load('video-camera')
body = R(32, 72, 136, 112, 14); lens = P('M168 112 L224 84 L224 172 L168 144 Z')
icon('video-camera-plus', M, ['new video', 'add recording', 'start meeting', 'record', 'camera'],
     line=vc['line'], area=vc['area'], detail=[L(100, 102, 100, 154), L(74, 128, 126, 128)])
icon('video-camera-minus', M, ['remove video', 'video', 'camera', 'minus'],
     line=vc['line'], area=vc['area'], detail=[L(74, 128, 126, 128)])
icon('video-camera-x', M, ['delete video', 'recording error', 'camera error'],
     line=vc['line'], area=vc['area'], detail=[L(80, 108, 120, 148), L(120, 108, 80, 148)])
icon('video-camera-slash', M, ['camera off', 'video off', 'disabled', 'mute', 'no video'],
     line=vc['line'] + [L(40, 40, 216, 216)])

# pencil variant: camera moved up 24, body corner opened for a small pencil
bp = 'M132 160 H46 A14 14 0 0 1 32 146 V62 A14 14 0 0 1 46 48 H154 A14 14 0 0 1 168 62 V124'
lens_u = PG([(168, 88), (224, 60), (224, 148), (168, 120)])
u = (math.sqrt(.5), -math.sqrt(.5)); n = (math.sqrt(.5), math.sqrt(.5))
T = (136, 224)
def ax(d, s):
    return (T[0] + u[0] * d + n[0] * s, T[1] + u[1] * d + n[1] * s)
pen = PG([T, ax(32, -20), ax(88, -20), ax(88, 20), ax(32, 20)])
icon('video-camera-pencil', M, ['video editor', 'edit video', 'media', 'clip'],
     line=[P(bp), lens_u, pen], area=[P(bp + ' L132 160 Z'), lens_u, pen])

# ---------------------------------------------------------------- 360
hc = (128, 120); hrx, hry = 96, 92
a0, a1 = 155, 28
def ep(a):
    return (hc[0] + hrx * math.cos(math.radians(a)), hc[1] + hry * math.sin(math.radians(a)))
p0, p1 = ep(a0), ep(a1)
orbit = P(f'M{pt(p0)} A{hrx} {hry} 0 0 0 {pt(p1)}')
t = math.radians(a1); d = (hrx * math.sin(t), -hry * math.cos(t)); dl = math.hypot(*d); d = (d[0] / dl, d[1] / dl)
arms = [rot([(p1[0] - d[0] * 36, p1[1] - d[1] * 32)], s_, p1)[0] for s_ in (45, -45)]
head = PL([arms[0], p1, arms[1]])
n360, _ = text('360', 128, 100, 60, 18)
v_ell = None
icon('view-360', M, ['360 view', 'panorama', 'rotate', 'vr', '360'], line=n360 + [orbit, head])
icon('view-360-slash', M, ['view 360', 'off', 'disabled', 'hidden', 'view'], line=n360 + [orbit, head, SLASH])

# ---------------------------------------------------------------- viewfinder
corners = [P('M40 88 V56 A16 16 0 0 1 56 40 H88'), P('M168 40 H200 A16 16 0 0 1 216 56 V88'),
           P('M216 168 V200 A16 16 0 0 1 200 216 H168'), P('M88 216 H56 A16 16 0 0 1 40 200 V168')]
icon('viewfinder', M, ['viewfinder', 'focus', 'frame', 'camera'], line=corners, dot=[C(128, 128, 24)])
icon('viewfinder-slash', M, ['viewfinder', 'off', 'disabled', 'hidden'], line=corners + [L(72, 72, 184, 184)])

# ---------------------------------------------------------------- vignette
vr = R(32, 48, 192, 160, 14)
icon('vignette', M, ['vignette', 'photo effect', 'edge', 'filter'],
     line=[vr, E(128, 128, 64, 48)], area=[vr], hole=[E(128, 128, 56, 40)])

# ---------------------------------------------------------------- waveform
bars = []; gbars = []
for x, hh in zip((48, 80, 112, 144, 176, 208), (24, 60, 92, 56, 76, 28)):
    bars.append(L(x, 128 - hh, x, 128 + hh)); gbars += gapped(x, 128 - hh, x, 128 + hh)
icon('waveform', M, ['soundwave', 'audio', 'waveform', 'sound', 'voiceprint'], line=bars)
icon('waveform-slash', M, ['no audio', 'muted', 'silence'], line=gbars + [SLASH])

print(save(overwrite=True))
