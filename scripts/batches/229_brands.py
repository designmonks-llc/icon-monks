"""Brand logos: operating systems, desktops and open-source apps."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'


def tags(*t):
    return list(t) + ['logo', 'brand']


import importlib.util as _u
_s = _u.spec_from_file_location('_ext', os.path.join(os.path.dirname(os.path.abspath(__file__)), '198_extremes.py'))
_m = _u.module_from_spec(_s); _s.loader.exec_module(_m)
X = _m.fix_d  # anchors on curve extremes


def ip(p):
    return (round(p[0]), round(p[1]))


# ---------------------------------------------------------------- operating systems
# Debian: the swirl, with its tail leaving at the bottom left.
icon('debian-logo', B, tags('debian', 'linux', 'operating system', 'open source', 'swirl'),
     line=[P('M80 212 C60 192 48 160 48 124 C48 78 86 40 132 40 C178 40 216 78 216 124 '
             'C216 170 182 208 136 208 C110 208 88 180 88 148 C88 124 104 106 126 106 '
             'C148 106 164 122 164 144')])

# Fedora: the round bubble with a square bottom-left corner around the looped f.
FED = 'M40 128 A88 88 0 1 1 128 216 H56 A16 16 0 0 1 40 200 Z'
icon('fedora-logo', B, tags('fedora', 'linux', 'operating system', 'red hat', 'open source'),
     area=[P(FED)], line=[P(FED)],
     detail=[P('M184 96 A24 24 0 0 0 136 96 V160 A24 24 0 1 1 112 136 H176')])

# Arch Linux: the peak with the arch cut out of its base.
ARCH = ('M128 32 C112 76 76 152 32 224 C60 206 80 192 96 184 C96 164 110 150 128 150 '
        'C146 150 160 164 160 184 C176 192 196 206 224 224 C180 152 144 76 128 32 Z')
icon('arch-linux-logo', B, tags('arch linux', 'arch', 'linux', 'operating system', 'open source'),
     area=[P(ARCH)], line=[P(ARCH)])

# Linux Mint: the bubble with a square top-left corner around the joined l and m.
MINT = 'M40 56 A16 16 0 0 1 56 40 H128 A88 88 0 1 1 40 128 Z'
icon('linux-mint-logo', B, tags('linux mint', 'mint', 'linux', 'operating system', 'open source'),
     area=[P(MINT)], line=[P(MINT)],
     detail=[P('M68 84 V152 A24 24 0 0 0 92 176 H160 A24 24 0 0 0 184 152 V128 A19 19 0 0 0 146 128 V176'),
             P('M146 128 A19 19 0 0 0 108 128 V176')])

# Manjaro: the three blocks, the left one with its top bar.
MJ = [PG([(32, 32), (152, 32), (152, 88), (88, 88), (88, 224), (32, 224)]),
      R(112, 112, 40, 112), R(176, 32, 48, 192)]
icon('manjaro-logo', B, tags('manjaro', 'linux', 'operating system', 'arch', 'open source'),
     area=MJ, line=MJ)

# Red Hat: the hat with its band.
HAT = ('M64 128 C68 92 84 56 116 56 C136 56 140 64 156 64 C176 64 184 96 192 128 '
       'C212 136 224 144 224 156 C224 176 196 184 160 184 C112 184 32 160 32 136 C32 124 48 120 64 128 Z')
icon('red-hat-logo', B, tags('red hat', 'linux', 'enterprise', 'open source', 'hat'),
     area=[P(X(HAT))], line=[P(X(HAT))],
     detail=[P('M64 128 C88 140 108 144 128 144 C148 144 172 140 192 128')])

# CentOS: the square with an arrow on each side, split by the cross and the diagonals.
CENT = ('M56 56 H104 L128 32 L152 56 H200 V104 L224 128 L200 152 V200 H152 L128 224 L104 200 H56 V152 '
        'L32 128 L56 104 Z')
icon('centos-logo', B, tags('centos', 'linux', 'operating system', 'red hat', 'open source'),
     area=[P(CENT)], line=[P(CENT)],
     detail=[L(128, 56, 128, 200), L(56, 128, 200, 128), L(56, 56, 200, 200), L(200, 56, 56, 200)])

# FreeBSD: the round daemon head with two horns.
FB_C, FB_R = (128, 140), 80
fl1, fl2 = ip(polar(FB_C, FB_R, 215)), ip(polar(FB_C, FB_R, 245))
fr1, fr2 = ip(polar(FB_C, FB_R, 295)), ip(polar(FB_C, FB_R, 325))
HORN_L = f'M{pt(fl1)} C52 76 44 60 40 44 C56 52 76 60 {pt(fl2)}'
HORN_R = f'M{pt(fr2)} C204 76 212 60 216 44 C200 52 180 60 {pt(fr1)}'
icon('freebsd-logo', B, tags('freebsd', 'bsd', 'unix', 'operating system', 'daemon', 'open source'),
     area=[C(*FB_C, FB_R), P(HORN_L + ' Z'), P(HORN_R + ' Z')],
     line=[C(*FB_C, FB_R), P(HORN_L), P(HORN_R)])

# ---------------------------------------------------------------- desktops
# KDE: the K with its stem inside a gear that opens to the right.
KC, KR, KT = (132, 128), 68, 90
gear = []
a = 70
pts = [ip(polar(KC, KR, a))]
d = f'M{pt(pts[0])}'
seq = [(KR, 10)] + [(KT, 24), (KR, 20)] * 4 + [(KT, 24), (KR, 10)]
r_prev = KR
for r, span in seq:
    if r != r_prev:
        p = ip(polar(KC, r, a))
        d += f' L{pt(p)}'
        r_prev = r
    a += span
    p = ip(polar(KC, r, a))
    d += f' A{r} {r} 0 0 1 {pt(p)}'
KDE_GEAR = d
icon('kde-logo', B, tags('kde', 'plasma', 'desktop', 'linux', 'gear', 'open source'),
     line=[P(KDE_GEAR), L(112, 88, 112, 168), PL([(196, 72), (112, 128), (196, 184)])])

# GNOME: the foot with its four toes.
FOOT = ('M120 120 C160 120 184 140 184 168 C184 184 176 192 164 192 H148 C140 192 136 200 144 212 '
        'C148 220 142 224 128 224 C88 224 64 200 64 172 C64 140 88 120 120 120 Z')
icon('gnome-logo', B, tags('gnome', 'desktop', 'linux', 'foot', 'open source'),
     area=[P(X(FOOT))], line=[P(X(FOOT))],
     dot=[C(48, 124, 16), C(76, 80, 16), C(120, 56, 16), C(172, 60, 16)])

# ---------------------------------------------------------------- open-source apps
# GIMP: Wilber's head with tall ears, big eyes and the brush in his mouth.
WIL = ('M64 128 C72 104 80 84 88 60 C108 76 132 88 152 88 C172 88 192 68 208 48 '
       'C216 96 216 140 200 168 C184 196 140 204 100 196 C76 192 60 180 56 164')
icon('gimp-logo', B, tags('gimp', 'image editor', 'wilber', 'graphics', 'open source'),
     area=[P(X(WIL) + ' Z')], line=[P(X(WIL) + ' Z')],
     detail=[L(132, 172, 212, 216)],
     dot=[C(48, 148, 16)],
     dotcut=[C(112, 128, 14), C(156, 124, 14)])

# Inkscape: the mountain with its snowcap, standing in a pool of ink.
INK = ('M128 32 C134 32 138 36 142 40 L212 120 C224 134 216 152 196 152 H164 C152 152 152 164 164 168 '
       'C176 172 176 188 160 188 H100 C84 188 84 172 100 168 C112 164 108 152 96 152 H60 '
       'C40 152 32 134 44 120 L114 40 C118 36 122 32 128 32 Z')
icon('inkscape-logo', B, tags('inkscape', 'vector', 'graphics', 'illustration', 'open source'),
     area=[P(X(INK))], line=[P(X(INK))],
     detail=[PL([(88, 84), (108, 104), (128, 88), (148, 104), (168, 84)])],
     dot=[C(204, 200, 16)])

# Prometheus: the round mark with the flame on its torch.
FLAME = ('M88 136 C80 120 84 104 96 92 C96 104 104 112 108 112 C104 96 112 84 128 72 '
         'C144 84 152 96 148 112 C152 112 160 104 160 92 C172 104 176 120 168 136 Z')
icon('prometheus-logo', B, tags('prometheus', 'monitoring', 'metrics', 'observability', 'open source'),
     area=[C(128, 128, 96)], line=[C(128, 128, 96)],
     detail=[P(X(FLAME)), L(72, 136, 184, 136), L(96, 176, 160, 176)])

# Istio: the two sails above the hull.
SAILS = [PG([(144, 32), (200, 176), (144, 176)]), PG([(104, 88), (104, 176), (64, 176)])]
icon('istio-logo', B, tags('istio', 'service mesh', 'kubernetes', 'sail', 'open source'),
     area=SAILS, line=SAILS + [L(56, 216, 208, 216)])

# HashiCorp: the H inside the hexagon made of two matching halves.
icon('hashicorp-logo', B, tags('hashicorp', 'terraform', 'infrastructure', 'devops', 'cloud'),
     line=[PL([(112, 40), (48, 76), (48, 180)]), PL([(144, 216), (208, 180), (208, 76)]),
           PL([(124, 80), (88, 100), (88, 200)]), PL([(132, 176), (168, 156), (168, 56)]),
           L(88, 128, 168, 128)])

# Consul: the C around a centre dot, with dots in its opening.
CC = (104, 128)
c1, c2 = ip(polar(CC, 72, 45)), ip(polar(CC, 72, -45))
icon('consul-logo', B, tags('consul', 'hashicorp', 'service mesh', 'service discovery', 'devops'),
     line=[P(f'M{pt(c1)} A72 72 0 1 1 {pt(c2)}')],
     dot=[C(104, 128, 16), C(172, 128, 16), C(208, 96, 16), C(208, 160, 16)])

# Gitea: the teacup with its handle and the tag inside.
CUP = 'M88 56 H216 C216 140 196 208 152 208 H144 C108 208 92 168 88 136 Z'
icon('gitea-logo', B, tags('gitea', 'git', 'code hosting', 'repository', 'teacup', 'open source'),
     area=[P(CUP)], line=[P(CUP), P('M88 72 H64 A28 28 0 0 0 64 128 H90')],
     detail=[PG([(152, 104), (184, 136), (152, 168), (120, 136)])])

# Nextcloud: the large ring between two small ones.
NC = [C(48, 128, 16), C(128, 128, 28), C(208, 128, 16)]
icon('nextcloud-logo', B, tags('nextcloud', 'cloud storage', 'files', 'sync', 'self-hosted', 'open source'),
     area=NC, line=NC)

# Syncthing: the ring with three nodes joined to a centre node.
icon('syncthing-logo', B, tags('syncthing', 'file sync', 'peer to peer', 'sync', 'open source'),
     area=[C(128, 128, 88)], line=[C(128, 128, 88)],
     detail=[L(43, 149, 144, 136), L(144, 136, 202, 87), L(144, 136, 184, 196)],
     dotcut=[C(43, 149, 14), C(144, 136, 14), C(202, 87, 14), C(184, 196, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
