import math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

H = 'Health'
SLASH = L(48, 48, 208, 208)


def tf(d, s=1.0, ox=0.0, oy=0.0, mirror=False):
    """Scale/translate (and optionally mirror about x=128) an absolute path string (M L H V C A Z)."""
    toks = re.findall(r'[MLHVCAZ]|-?\d*\.?\d+', d)
    out, i, cmd = [], 0, None
    X = lambda x: ox + s * ((256 - x) if mirror else x)
    Y = lambda y: oy + s * y
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; out.append(t); i += 1
            if t == 'Z':
                continue
        if cmd in 'ML':
            out.append(f'{f(X(float(toks[i])))} {f(Y(float(toks[i + 1])))}'); i += 2
        elif cmd == 'H':
            out.append(f(X(float(toks[i])))); i += 1
        elif cmd == 'V':
            out.append(f(Y(float(toks[i])))); i += 1
        elif cmd == 'C':
            out.append(' '.join(f'{f(X(float(toks[i + k])))} {f(Y(float(toks[i + k + 1])))}' for k in (0, 2, 4))); i += 6
        elif cmd == 'A':
            rx, ry, rotn, la, sw, x, y = toks[i:i + 7]
            if mirror:
                sw = '1' if sw == '0' else '0'
            out.append(f'{f(float(rx) * s)} {f(float(ry) * s)} {rotn} {la} {sw} {f(X(float(x)))} {f(Y(float(y)))}'); i += 7
    return re.sub(r'([MLHVCAZ]) ', r'\1', ' '.join(out)).replace(' Z', ' Z')


def cross(cx, cy, w=16, l=40):
    w = max(w, 16)
    """Outlined medical cross (plus with arm half-width w, half-length l)."""
    return PG([(cx - w, cy - l), (cx + w, cy - l), (cx + w, cy - w), (cx + l, cy - w), (cx + l, cy + w), (cx + w, cy + w),
               (cx + w, cy + l), (cx - w, cy + l), (cx - w, cy + w), (cx - l, cy + w), (cx - l, cy - w), (cx - w, cy - w)])


def as_lines(name, drop_detail=False):
    g = load(name)
    return g['line'] + ([] if drop_detail else g['detail'])


def rrect(cx, cy, w, h, r, deg):
    """Rounded rectangle rotated by deg about its centre, as a path."""
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    T = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
    hw, hh = w / 2, h / 2
    pts = [T(-hw + r, -hh), T(hw - r, -hh), T(hw, -hh + r), T(hw, hh - r), T(hw - r, hh), T(-hw + r, hh), T(-hw, hh - r), T(-hw, -hh + r)]
    d = f'M{pt(pts[0])}'
    for i in range(4):
        d += f' L{pt(pts[2 * i + 1])} A{f(r)} {f(r)} 0 0 1 {pt(pts[(2 * i + 2) % 8])}'
    return d + ' Z'


HEART = 'M128 212 C128 212 32 160 32 98 A50 50 0 0 1 128 78 A50 50 0 0 1 224 98 C224 160 128 212 128 212 Z'

# ---------------------------------------------------------------- hearts
bolt = PL([(140, 100), (108, 140), (148, 140), (116, 180)])
icon('defibrillator', H, ['aed', 'defibrillator', 'heart', 'emergency'],
     line=[P(HEART)], detail=[bolt], area=[P(HEART)])
icon('heart-medical', H, ['health', 'cardiology', 'heart', 'medical'],
     line=[P(HEART)], detail=[cross(128, 140, 16, 38)], area=[P(HEART)])
hs = tf(HEART, 0.56, 128 - 0.56 * 128, 132 - 0.56 * 132)
icon('heart-scan', H, ['health scan', 'heart', 'recognition', 'vitals'],
     line=[PL([(40, 88), (40, 40), (88, 40)]), PL([(168, 40), (216, 40), (216, 88)]),
           PL([(216, 168), (216, 216), (168, 216)]), PL([(88, 216), (40, 216), (40, 168)]), P(hs)],
     area=[P(hs)])

# ---------------------------------------------------------------- defibrillator pads
p1 = rrect(76, 72, 72, 56, 14, -10)
p2 = rrect(180, 72, 72, 56, 14, 10)
icon('defibrillator-pads', H, ['aed pads', 'electrodes', 'defibrillator', 'emergency'],
     line=[P(p1), P(p2), P('M80 100 C80 152 112 148 116 184'), P('M176 100 C176 152 144 148 140 184'), R(108, 184, 40, 40, 10)],
     detail=[L(64, 74, 88, 70), L(168, 70, 192, 74)], area=[P(p1), P(p2), R(108, 184, 40, 40, 10)])

# ---------------------------------------------------------------- people
dbody = 'M40 224 C40 172 80 148 128 148 C176 148 216 172 216 224'
icon('doctor', H, ['doctor', 'physician', 'medical', 'person'],
     line=[C(128, 76, 44), P(dbody)],
     detail=[P('M100 152 V180 A28 28 0 0 0 156 180 V152')],
     area=[C(128, 76, 44), P(dbody + ' Z')])

nhead = 'M101.17 76 A36 36 0 1 0 154.83 76'
cap = [(88, 76), (100, 36), (156, 36), (168, 76)]
nbody = 'M48 216 C48 172 84 152 128 152 C172 152 208 172 208 216'
icon('nurse', H, ['nurse', 'medical', 'caregiver', 'person', 'healthcare'],
     line=[P(nhead), PG(cap), P(nbody)],
     area=[P(nhead + ' Z'), PG(cap), P(nbody + ' Z')])

ncap = 'M40 192 L60 72 C100 48 156 48 196 72 L216 192 C160 176 96 176 40 192 Z'
icon('nurse-cap', H, ['nurse', 'cap', 'medical', 'care'],
     line=[P(ncap)], detail=[cross(128, 118, 16, 36)], area=[P(ncap)])

# ---------------------------------------------------------------- ear
icon('ear-slash', H, ['deaf', 'hearing disabled', 'mute', 'ear', 'disabled'], line=as_lines('ear') + [SLASH])

# ---------------------------------------------------------------- face mask
mask = 'M64 80 C100 64 156 64 192 80 V160 C156 188 100 188 64 160 Z'
loops = [P('M64 100 H56 A24 24 0 0 0 56 148 H64'), P('M192 100 H200 A24 24 0 0 1 200 148 H192')]
pleats = [L(100, 108, 156, 108), L(100, 140, 156, 140)]
icon('face-mask', H, ['surgical mask', 'mask', 'medical', 'protection', 'medical mask'],
     line=[P(mask)] + loops, detail=pleats, area=[P(mask)])
icon('face-mask-slash', H, ['face mask', 'disabled', 'off', 'health'],
     line=[P(mask)] + loops + pleats + [SLASH])

# ---------------------------------------------------------------- files & folders
fl = load('file')
icon('file-medical', H, ['medical record', 'document', 'health', 'file', 'chart'],
     line=fl['line'], detail=fl['detail'] + [cross(128, 152, 16, 40)], area=fl['area'])
fo = load('folder')
icon('folder-medical', H, ['medical records', 'folder', 'health', 'directory'],
     line=fo['line'], detail=[cross(128, 144, 16, 38)], area=fo['area'])
nb = load('notebook')
icon('notebook-medical', H, ['medical journal', 'notebook', 'health', 'record'],
     line=nb['line'], detail=[nb['detail'][0], cross(156, 128, 16, 34)], area=nb['area'])
cb = load('clipboard')
icon('medical-report', H, ['medical report', 'health record', 'clipboard', 'chart'],
     line=cb['line'], detail=[cross(128, 128, 16, 36), L(96, 192, 160, 192)], area=cb['area'], hole=cb['hole'])
idc = R(32, 56, 192, 144, 14)
icon('medical-id', H, ['medical information', 'health card', 'patient id', 'badge'],
     line=[idc], detail=[L(88, 104, 88, 152), L(64, 128, 112, 128), L(148, 108, 188, 108), L(148, 148, 176, 148)], area=[idc])
fak = load('first-aid-kit')
icon('first-aid-kit-slash', H, ['first aid kit', 'off', 'disabled', 'hidden', 'first'],
     line=fak['line'] + fak['detail'] + [SLASH])

# ---------------------------------------------------------------- foot
sole = ('M84 124 C84 100 108 88 144 92 C176 96 192 116 186 146 C180 172 166 182 164 198 '
        'C162 216 144 225 122 224 C94 220 82 200 90 176 C96 158 84 146 84 124 Z')
icon('foot', H, ['podiatry', 'foot', 'feet', 'footprint'],
     line=[P(sole)], area=[P(sole)],
     dot=[C(76, 64, 20), C(118, 46, 15), C(156, 44, 14), C(190, 56, 13), C(212, 80, 11)])

# ---------------------------------------------------------------- head profiles
HEAD = 'M84 224 V172.6 A76 76 0 1 1 195.4 82 L218 136 L204 144 V170 A18 18 0 0 1 186 188 H160 V224'
icon('head-heart', H, ['mental health', 'therapy', 'wellbeing', 'mind'],
     line=[P(HEAD)], detail=[P(tf(HEART, 0.4, 122 - 0.4 * 128, 110 - 0.4 * 140))], area=[P(HEAD + ' Z')])
hc = tf(HEAD, 0.8, 36 - 0.8 * 48, 224 - 0.8 * 224)
icon('head-cough', H, ['cough', 'sick', 'cold', 'flu'],
     line=[P(hc), L(196, 140, 216, 128), L(200, 172, 224, 172), L(196, 204, 216, 216)], area=[P(hc + ' Z')])
hm = 'M84 224 V172.6 A76 76 0 1 1 195.4 82 L210 120'
mfront = 'M210 120 C228 144 226 176 202 198'
mhead_area = hm + ' C228 144 226 176 202 198 L168 200 V224 Z'
icon('head-mask', H, ['face mask', 'protection', 'covid', 'head'],
     line=[P(hm), P(mfront), L(168, 200, 168, 224)],
     detail=[PL([(210, 120), (148, 120), (156, 196), (202, 198)]), L(148, 124, 108, 104), L(154, 176, 112, 152)],
     area=[P(mhead_area)])

# ---------------------------------------------------------------- hearing aid
hc0 = (148, 132)
o1, o2 = polar(hc0, 96, 150), polar(hc0, 96, 230)
i1, i2 = polar(hc0, 56, 150), polar(hc0, 56, 230)
e1, e2 = polar(hc0, 76, 150), polar(hc0, 76, 230)
mid = polar(hc0, 76, 190)
haid = (f'M{pt(o1)} A96 96 0 0 1 {pt(o2)} ' + arc_to(e2, 20, o2, i2, lambda m: dist(m, mid)) +
        f' A56 56 0 0 0 {pt(i1)} ' + arc_to(e1, 20, i1, o1, lambda m: dist(m, mid)) + ' Z')
tip = (e2[0] + 20 * 0.766, e2[1] - 20 * 0.643)
dome = 'M172 132 A20 20 0 0 1 212 132 V144 A8 8 0 0 1 204 152 H180 A8 8 0 0 1 172 144 Z'
icon('hearing-aid', H, ['hearing aid', 'deaf', 'accessibility', 'ear'],
     line=[P(haid), P(f'M{pt(tip)} C132 32 192 40 192 112'), P(dome)], area=[P(haid), P(dome)])

# ---------------------------------------------------------------- hospital
icon('hospital-sign', H, ['hospital', 'h sign', 'medical', 'clinic'],
     line=[C(128, 128, 96)], detail=[L(96, 84, 96, 172), L(160, 84, 160, 172), L(96, 128, 160, 128)],
     area=[C(128, 128, 96)])
mat = 'M40 128 H208 A16 16 0 0 1 224 144 V152 A16 16 0 0 1 208 168 H40'
icon('hospital-bed', H, ['hospital bed', 'patient', 'ward', 'care'],
     line=[L(40, 64, 40, 188), P(mat), P('M104 128 V96 H200 V128'), L(200, 168, 200, 188)],
     area=[P(mat + ' Z')], dot=[C(200, 208, 16), C(40, 208, 16)])

# ---------------------------------------------------------------- organs
intest = 'M48 192 V80 A32 32 0 0 1 80 48 H176 A32 32 0 0 1 208 80 V176 A24 24 0 0 1 184 200 H140 V224'
icon('intestines', H, ['intestines', 'gut', 'digestive', 'colon'],
     line=[P(intest), P('M100 100 H156 A18 18 0 0 1 156 136 H100 A18 18 0 0 0 100 172 H48')])
kid = ('M88 56 C56 56 36 92 36 128 C36 168 56 200 88 200 C108 200 116 180 106 160 '
       'C98 146 98 110 106 96 C116 76 108 56 88 56 Z')
kid2 = tf(kid, mirror=True)
icon('kidneys', H, ['nephrology', 'kidney', 'organ', 'urology', 'renal'],
     line=[P(kid), P(kid2), P('M100 128 C116 132 112 176 112 224'), P('M156 128 C140 132 144 176 144 224')],
     area=[P(kid), P(kid2)])
lobe = 'M108 112 V196 A20 20 0 0 1 88 216 H60 A20 20 0 0 1 40 196 V152 C40 104 60 72 80 68 C96 64 108 80 108 112 Z'
lobe2 = tf(lobe, mirror=True)
tr = [L(128, 32, 128, 88), PL([(108, 112), (128, 88), (148, 112)])]
br = [L(108, 132, 80, 160), L(148, 132, 176, 160)]
icon('lungs', H, ['pulmonology', 'breathing', 'respiratory', 'lungs', 'organ'],
     line=[P(lobe), P(lobe2)] + tr, detail=br, area=[P(lobe), P(lobe2)])
icon('lungs-slash', H, ['lungs', 'off', 'disabled', 'hidden'],
     line=[P(lobe), P(lobe2)] + tr + [SLASH])

# ---------------------------------------------------------------- iv drip
bag = R(72, 72, 80, 88, 16)
icon('iv-drip', H, ['iv', 'drip', 'infusion', 'hospital', 'iv drip'],
     line=[L(184, 40, 184, 216), L(152, 216, 216, 216), L(112, 40, 184, 40), L(112, 40, 112, 72), bag,
           P('M112 160 V184 A24 24 0 0 0 136 208 H152')],
     detail=[L(96, 112, 128, 112)], area=[bag])

# ---------------------------------------------------------------- massage
def mitten(c, top, bot, thumb):
    d = f'M{f(c - 24)} {f(top)} V{f(bot - 24)} A24 24 0 0 0 {f(c + 24)} {f(bot - 24)} V{f(top)} Z'
    tx = c - 24 if thumb < 0 else c + 24
    return d, L(tx, top + 24, tx + thumb * 18, top + 48)
m1, t1 = mitten(88, 40, 128, -1)
m2, t2 = mitten(168, 40, 128, 1)
icon('massage', H, ['massage', 'spa', 'therapy', 'relax'],
     line=[P(m1), P(m2), t1, t2, P('M32 192 C80 160 176 160 224 192')], area=[P(m1), P(m2)])
table = [L(32, 168, 224, 168), L(56, 168, 56, 216), L(200, 168, 200, 216)]
body_lying = R(92, 112, 132, 32, 16)
icon('massage-table', H, ['massage', 'spa', 'therapy', 'table'],
     line=table + [C(56, 120, 24), body_lying], area=[C(56, 120, 24), body_lying])
def thickpath(pts, hw):
    """Closed outline of a polyline with half-width hw and round ends."""
    def off(a, b, k):
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy); nx, ny = -dy / l * k, dx / l * k
        return (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)
    def isect(p1, p2, p3, p4):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    sides = []
    for k in (hw, -hw):
        segs = [off(pts[i], pts[i + 1], k) for i in range(len(pts) - 1)]
        side = [segs[0][0]] + [isect(*segs[i], *segs[i + 1]) for i in range(len(segs) - 1)] + [segs[-1][1]]
        sides.append(side)
    a, b = sides
    d = 'M' + ' L'.join(pt(q) for q in a)
    d += f' A{f(hw)} {f(hw)} 0 0 1 {pt(b[-1])}' if True else ''
    d += ' L' + ' L'.join(pt(q) for q in reversed(b))
    d += f' A{f(hw)} {f(hw)} 0 0 1 {pt(a[0])} Z'
    return d
arm = thickpath([(124, 84), (168, 84), (196, 52)], 16)
icon('physiotherapy', H, ['physiotherapy', 'rehab', 'massage', 'therapist'],
     line=table + [C(56, 136, 20), R(92, 128, 132, 24, 12), P(arm)], area=[C(56, 136, 20), R(92, 128, 132, 24, 12), P(arm)])
chair = 'M48 64 A16 16 0 0 1 80 52 L104 128 H176 L212 184 A16 16 0 0 1 198 208 L160 160 H96 A24 24 0 0 1 72 144 Z'
icon('massage-chair', H, ['massage chair', 'recliner', 'relax', 'spa'],
     line=[P(chair), L(128, 160, 128, 216), L(96, 216, 160, 216)], area=[P(chair)])

# ---------------------------------------------------------------- measuring tape
sides = [P('M64 32 C88 88 88 112 76 136 C64 160 56 200 64 224'), P('M192 32 C168 88 168 112 180 136 C192 160 200 200 192 224')]
band = 'M40 112 C96 136 160 136 216 112 V144 C160 168 96 168 40 144 Z'
icon('measuring-tape-waist', H, ['waist', 'measure', 'diet', 'body'],
     line=sides + [P(band)], area=[P(band)])

# ---------------------------------------------------------------- medical cross (star of life)
star = []
for k in range(6):
    th = -90 + k * 60
    a = polar((128, 128), 96, th)
    n = (math.cos(math.radians(th + 90)), math.sin(math.radians(th + 90)))
    star += [(a[0] - n[0] * 20, a[1] - n[1] * 20), (a[0] + n[0] * 20, a[1] + n[1] * 20), polar((128, 128), 40, th + 30)]
icon('medical-cross', H, ['medical', 'asterisk', 'emergency', 'star of life'], line=[PG(star)], area=[PG(star)])
icon('medical-cross-slash', H, ['medical cross', 'off', 'disabled', 'hidden', 'medical'], line=[PG(star), SLASH])

# ---------------------------------------------------------------- bottles
cup_lid = PG([(100, 32), (156, 32), (164, 72), (92, 72)])
mb = 'M100 72 V84 C76 92 64 104 64 128 V208 A16 16 0 0 0 80 224 H176 A16 16 0 0 0 192 208 V128 C192 104 180 92 156 84 V72'
icon('medicine-bottle', H, ['syrup', 'medicine', 'bottle', 'pharmacy', 'pill bottle'],
     line=[cup_lid, P(mb)], detail=[cross(128, 160, 16, 36)], area=[cup_lid, P(mb + ' Z')])
lb = 'M64 64 V80 C44 88 36 100 36 120 V208 A16 16 0 0 0 52 224 H120 A16 16 0 0 0 136 208 V120 C136 100 128 88 108 80 V64'
lcap = R(56, 32, 60, 32, 8)
mcup = PG([(164, 136), (224, 136), (214, 216), (174, 216)])
icon('medicine-liquid', H, ['syrup', 'liquid medicine', 'dose', 'bottle'],
     line=[lcap, P(lb), mcup], detail=[L(64, 160, 108, 160), L(184, 168, 204, 168)], area=[lcap, P(lb + ' Z'), mcup])
pcap = R(56, 32, 144, 40, 12)
pb = 'M68 72 V208 A16 16 0 0 0 84 224 H172 A16 16 0 0 0 188 208 V72'
icon('pill-bottle', H, ['medication', 'medicine', 'prescription', 'pills', 'supplements'],
     line=[pcap, P(pb)], detail=[R(96, 112, 64, 72, 8)], area=[pcap, P(pb + ' Z')])

# ---------------------------------------------------------------- monitor heartbeat
mon = load('monitor')
icon('monitor-heartbeat', H, ['heart rate monitor', 'ecg', 'vitals', 'monitor', 'heart monitor'],
     line=mon['line'], detail=[PL([(64, 112), (92, 112), (108, 80), (132, 144), (148, 112), (192, 112)])], area=mon['area'])

# ---------------------------------------------------------------- mortar & pestle
mort = 'M40 120 H216 A88 72 0 0 1 40 120 Z'
u = (1 / math.sqrt(2), -1 / math.sqrt(2))
pest = capsule((162, 82), 40, 16, u)
icon('mortar-pestle', H, ['herbal medicine', 'mortar', 'pestle', 'pharmacy'],
     line=[P(mort), P('M100 188 L96 216 H160 L156 188'), P(pest)], area=[P(mort), P(pest)])

# ---------------------------------------------------------------- nose
icon('nose', H, ['nose', 'smell', 'nasal', 'face'],
     line=[P('M80 32 C88 88 120 124 172 156 C200 174 192 212 160 212 H136'), P('M136 212 C108 212 100 184 120 168')])

# ---------------------------------------------------------------- pharmacy
awn = PG([(40, 96), (60, 48), (196, 48), (216, 96)])
icon('pharmacy', H, ['drugstore', 'chemist', 'medicine', 'rx'],
     line=[awn, P('M56 96 V216 M200 96 V216'), L(32, 216, 224, 216)], detail=[cross(128, 156, 16, 36)],
     area=[awn, R(56, 96, 144, 120)])

# ---------------------------------------------------------------- pills
pill_c = (112, 112)
pillp = capsule(pill_c, 56, 40, u)
icon('pill-clock', H, ['medication reminder', 'dose', 'schedule', 'pill'],
     line=[P(pillp), C(184, 184, 36)], detail=[L(83.72, 83.72, 140.28, 140.28), PL([(184, 166), (184, 184), (196, 192)])],
     area=[P(pillp), C(184, 184, 36)])
icon('pill-slash', H, ['pill', 'off', 'disabled', 'hidden'], line=as_lines('pill', drop_detail=True) + [SLASH])

# ---------------------------------------------------------------- prescription
icon('prescription', H, ['rx', 'prescription', 'pharmacy', 'medicine'],
     line=[L(72, 48, 72, 208), P('M72 48 H124 A36 36 0 0 1 124 120 H72'), L(108, 120, 200, 212), L(200, 144, 136, 208)])

# ---------------------------------------------------------------- pulse warning
icon('pulse-warning', H, ['abnormal', 'vital signs', 'alert', 'irregular'],
     line=[PL([(32, 112), (64, 112), (96, 48), (136, 176), (160, 112), (224, 112)]), L(200, 152, 200, 184)],
     dot=[C(200, 216, 16)])

# ---------------------------------------------------------------- skeleton & ribs
ribs = [L(128, 40, 128, 216)]
for y in (64, 112, 160):
    ribs += [P(f'M128 {y} C96 {y - 12} 48 {y - 4} 48 {y + 32}'), P(f'M128 {y} C160 {y - 12} 208 {y - 4} 208 {y + 32}')]
icon('rib-cage', H, ['ribs', 'chest', 'skeleton', 'anatomy'], line=ribs)
icon('skeleton', H, ['skeleton', 'bones', 'anatomy', 'halloween'],
     line=[C(128, 56, 24), L(128, 88, 128, 152), L(100, 104, 156, 104), L(104, 136, 152, 136),
           PL([(84, 156), (100, 104)]), PL([(172, 156), (156, 104)]),
           L(112, 160, 96, 220), L(144, 160, 160, 220), L(104, 160, 152, 160)])

# ---------------------------------------------------------------- scale
sq = R(32, 32, 192, 192, 16)
dial = [P('M72 120 A56 56 0 0 1 184 120 Z'), L(128, 120, 144, 96)]
icon('scale-bathroom', H, ['weight', 'bathroom scale', 'body weight', 'fitness'], line=[sq], detail=dial, area=[sq])
icon('scale-bathroom-slash', H, ['scale bathroom', 'off', 'disabled', 'hidden', 'scale'], line=[sq] + dial + [SLASH])

# ---------------------------------------------------------------- social distancing
pbody = 'M32 152 C32 120 48 104 68 104 C88 104 104 120 104 152'
pbody2 = tf(pbody, ox=-8, mirror=True)
pbody2 = 'M152 152 C152 120 168 104 188 104 C208 104 224 120 224 152'
icon('social-distancing', H, ['distance', 'spacing', 'people', 'covid', 'social distancing'],
     line=[C(68, 64, 24), P(pbody), C(188, 64, 24), P(pbody2), L(48, 200, 208, 200),
           PL([(68, 180), (48, 200), (68, 220)]), PL([(188, 180), (208, 200), (188, 220)])],
     area=[C(68, 64, 24), P(pbody + ' Z'), C(188, 64, 24), P(pbody2 + ' Z')])

# ---------------------------------------------------------------- stethoscope slash
st = load('stethoscope')
icon('stethoscope-slash', H, ['stethoscope', 'off', 'disabled', 'hidden'], line=st['line'] + [SLASH], dot=st['dot'])

print(save(overwrite=True))
