"""Brand logos: editors, ML tools and DevOps."""
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


# ---------------------------------------------------------------- editors and IDEs
# Vim: the V standing in the diamond.
DIAMOND = PG([(128, 32), (224, 128), (128, 224), (32, 128)])
brand('vim-logo', ['vim', 'text editor', 'editor', 'terminal'],
      area=[DIAMOND], line=[DIAMOND],
      detail=[PL([(100, 100), (128, 164), (156, 100)])])

# Neovim: the N of two pillars with slanted ends joined by the diagonal band.
NV = PG([(44, 72), (92, 32), (164, 176), (164, 32), (212, 32), (212, 184), (164, 224), (92, 80), (92, 224),
         (44, 224)])
brand('neovim-logo', ['neovim', 'vim', 'text editor', 'editor', 'terminal'],
      area=[NV], line=[NV],
      detail=[L(92, 32, 92, 80), L(164, 176, 164, 224)])

# Emacs: the swirling E in a circle.
brand('emacs-logo', ['emacs', 'gnu', 'text editor', 'editor'],
      area=[RING], line=[RING],
      detail=[P('M160 68 C140 72 120 72 100 72 A18 18 0 0 0 100 108 H152 A18 18 0 0 1 152 144 H104 '
                'A18 18 0 0 0 104 180 H164')])

# IntelliJ IDEA: the JetBrains black tile with IJ over the underscore.
brand('intellij-logo', ['intellij', 'intellij idea', 'jetbrains', 'ide', 'java'],
      area=[SQ], line=[SQ],
      detail=[L(80, 72, 80, 136), P('M160 72 V116 A20 20 0 0 1 120 116'), L(80, 176, 128, 176)])

# Android Studio: the drafting compass A with the Android head peeking out behind it.
brand('android-studio-logo', ['android studio', 'android', 'google', 'ide', 'mobile'],
      area=[P('M164 192 A30 30 0 0 1 224 192 Z')],
      line=[C(108, 64, 20), L(108, 32, 108, 44), L(98, 82, 48, 216), L(118, 82, 168, 216),
            P('M164 192 A30 30 0 0 1 224 192 Z'), L(176, 160, 168, 144), L(212, 160, 220, 144)],
      detail=[L(76, 152, 140, 152)])

# Sublime Text: the three folded bands of the S.
ST = PG([(60, 84), (196, 40), (196, 84), (130, 104), (196, 124), (196, 172), (60, 216), (60, 168), (128, 148),
         (60, 124)])
brand('sublime-text-logo', ['sublime text', 'sublime', 'text editor', 'editor', 'code'],
      area=[ST], line=[ST], detail=[L(128, 148, 196, 172)])

# Visual Studio: the bow tie, a short bar crossed over to the tall right panel.
VS = R(168, 32, 48, 192, 16)
VS_L, VS_R = PG([(40, 92), (90, 128), (40, 164)]), PG([(90, 128), (168, 72), (168, 184)])
brand('visual-studio-logo', ['visual studio', 'microsoft', 'ide', 'code', 'dotnet'],
      area=[VS, VS_L, VS_R], line=[VS, VS_L, VS_R])

# ---------------------------------------------------------------- data and ML
# Jupyter: the two orange crescents with three moons around them.
TOPC = 'M56 108 A76 76 0 0 1 200 108 A88 56 0 0 0 56 108 Z'
BOTC = 'M56 148 A76 76 0 0 0 200 148 A88 56 0 0 1 56 148 Z'
brand('jupyter-logo', ['jupyter', 'notebook', 'python', 'data science'],
      area=[P(TOPC), P(BOTC)], line=[P(TOPC), P(BOTC)],
      dot=[C(204, 48, 16), C(52, 56, 16), C(52, 204, 16)])

# TensorFlow: the T and F block in isometric view, with the edge of its top faces.
TF_A, TF_B = 23.4, 13.5
def tf(x, y):
    return ipt((128 + (x + 0.5) * TF_A, 40 + y * TF_B))
TF = PG([tf(*p) for p in [(0, 0), (3, 3), (3, 5), (2, 6), (0, 4), (0, 6), (1, 7), (1, 9), (0, 10), (-1, 9),
                          (-1, 13), (-2, 12), (-2, 6), (-3, 7), (-4, 6), (-4, 4)]])
brand('tensorflow-logo', ['tensorflow', 'google', 'machine learning', 'ai', 'deep learning'],
      area=[TF], line=[TF],
      detail=[PL([tf(-4, 4), tf(-3, 5), tf(0, 2), tf(2, 4), tf(3, 3)]), L(*tf(0, 2), *tf(0, 4))])

# PyTorch: the flame ring rising to a point, with the spark beside its open end.
PT_C, PT_R = (128, 140), 76
pt_l = ipt(polar(PT_C, PT_R, 220))
pt_r = ipt(polar(PT_C, PT_R, -20))
brand('pytorch-logo', ['pytorch', 'meta', 'machine learning', 'ai', 'deep learning'],
      line=[P(f'M124 32 L{pt(pt_l)} A{PT_R} {PT_R} 0 1 0 {pt(pt_r)}')],
      dot=[C(164, 76, 16)])

# ---------------------------------------------------------------- git and API tools
# GitKraken: the kraken's head with its tentacles curling out into a ring.
GK_A, GK_B = ipt(polar((128, 128), 96, -115)), ipt(polar((128, 128), 96, -65))
brand('gitkraken-logo', ['gitkraken', 'git', 'git client', 'kraken', 'octopus'],
      area=[P('M84 120 C84 76 104 56 128 56 C152 56 172 76 172 120 Z')],
      line=[P('M84 120 C84 76 104 56 128 56 C152 56 172 76 172 120 Z'), L(128, 120, 128, 192),
            P(f'M{pt(GK_A)} A96 96 0 1 0 {pt(GK_B)}'),
            P('M84 120 C84 156 60 168 41 168'), P('M172 120 C172 156 196 168 215 168')])

# Swagger: the braces with an ellipsis, in a circle.
brand('swagger-logo', ['swagger', 'openapi', 'api', 'documentation'],
      area=[RING], line=[RING],
      detail=[P('M88 72 C72 72 72 80 72 96 V108 C72 120 68 128 56 128 C68 128 72 136 72 148 V160 '
                'C72 176 72 184 88 184'),
              P('M168 72 C184 72 184 80 184 96 V108 C184 120 188 128 200 128 C188 128 184 136 184 148 V160 '
                'C184 176 184 184 168 184'),
              L(100, 128, 100, 128), L(128, 128, 128, 128), L(156, 128, 156, 128)])

# Insomnia: the moon disc with a bite out of its upper left, inside a ring.
IN_C, IN_R, BITE_C, BITE_R = (128, 128), 56, (92, 92), 28
in_a, in_b = (ipt(p) for p in circle_x(IN_C, IN_R, BITE_C, BITE_R))
far_bite = lambda m: dist(m, BITE_C)
near_bite = lambda m: -dist(m, IN_C)
MOON = (f'M{pt(in_a)} ' + arc_to(IN_C, IN_R, in_a, in_b, far_bite) + ' '
        + arc_to(BITE_C, BITE_R, in_b, in_a, near_bite) + ' Z')
brand('insomnia-logo', ['insomnia', 'kong', 'api', 'rest client', 'http'],
      area=[P(MOON)], line=[RING, P(MOON)])

# ---------------------------------------------------------------- devops
# OpenShift: the ring broken by two slanted bands.
OS_C, OS_R = (128, 136), 80
def os_pt(deg):
    return ipt(polar(OS_C, OS_R, deg))
brand('openshift-logo', ['openshift', 'red hat', 'kubernetes', 'containers', 'cloud'],
      line=[P(f'M{pt(os_pt(-55))} A{OS_R} {OS_R} 0 0 0 {pt(os_pt(-190))}'),
            P(f'M{pt(os_pt(-10))} A{OS_R} {OS_R} 0 0 1 {pt(os_pt(155))}'),
            L(172, 104, 220, 88), L(40, 160, 88, 144)])

# Terraform: the four slanted blocks.
def block(x, y, rise):
    return PG([(x, y), (x + 32, y + rise), (x + 32, y + rise + 48), (x, y + 48)])
TFM = [block(56, 34, 18), block(112, 66, 18), block(112, 158, 18), block(168, 84, -18)]
brand('terraform-logo', ['terraform', 'hashicorp', 'infrastructure as code', 'devops', 'cloud'],
      area=TFM, line=TFM)

# Ansible: the A with its crossbar slanting down to the right foot, in a circle.
brand('ansible-logo', ['ansible', 'red hat', 'automation', 'devops', 'configuration'],
      area=[RING], line=[RING],
      detail=[PL([(80, 184), (128, 68), (176, 184)]), L(98, 140, 176, 184)])

# CircleCI: the ring open on the left around the solid centre.
CC_A, CC_B = ipt(polar((128, 128), 96, 204)), ipt(polar((128, 128), 96, 156))
brand('circleci-logo', ['circleci', 'ci', 'continuous integration', 'devops', 'pipeline'],
      area=[C(128, 128, 32)],
      line=[P(f'M{pt(CC_A)} A96 96 0 1 1 {pt(CC_B)}'), C(128, 128, 32)])

# Argo: the octopus in its space helmet.
ARGO_HEAD = 'M76 144 V112 C76 80 100 64 128 64 C156 64 180 80 180 112 V144 Z'
brand('argo-logo', ['argo', 'argo cd', 'gitops', 'kubernetes', 'octopus', 'devops'],
      area=[P(ARGO_HEAD)],
      line=[P(ARGO_HEAD), P('M52 168 A88 88 0 1 1 204 168'),
            L(96, 144, 72, 208), L(128, 144, 128, 216), L(160, 144, 184, 208)],
      dotcut=[C(108, 108, 14), C(148, 108, 14)])

if __name__ == '__main__':
    print(save(overwrite='--overwrite' in sys.argv))
