"""Gap fill from the 2026-10-20 library comparison: brand logos the other libraries carry and we did not."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from draw import *

B = 'Brands'
RING = C(128, 128, 96)

# AdGuard: the shield with a check mark
SHIELD = 'M128 32 C96 48 64 52 40 52 C40 140 72 196 128 224 C184 196 216 140 216 52 C192 52 160 48 128 32 Z'
icon('adguard-logo', B, ['adguard', 'ad blocker', 'privacy', 'security', 'logo', 'brand'],
     line=[P(SHIELD)], area=[P(SHIELD)], detail=[PL([(88, 128), (120, 160), (176, 100)])])

# McAfee: the shield with the M drawn as one stroke
MSHIELD = 'M48 48 H208 V128 C208 176 172 208 128 224 C84 208 48 176 48 128 Z'
icon('mcafee-logo', B, ['mcafee', 'antivirus', 'security', 'logo', 'brand'],
     line=[P(MSHIELD)], area=[P(MSHIELD)], detail=[PL([(88, 168), (88, 88), (128, 128), (168, 88), (168, 168)])])

# Alipay: the rounded tile with the character for "pay"
icon('alipay-logo', B, ['alipay', 'payment', 'ant group', 'wallet', 'logo', 'brand'],
     line=[R(40, 40, 176, 176, 32)], area=[R(40, 40, 176, 176, 32)],
     detail=[L(76, 88, 180, 88), L(128, 64, 128, 116), L(84, 128, 168, 128),
             P('M168 128 C152 168 116 188 76 196'), P('M108 152 C132 176 160 188 188 192')])

# BlackBerry: seven berries in three columns
BERRIES = [R(x - 22, y - 16, 44, 32, 16) for x, y in
           [(54, 72), (54, 128), (128, 72), (128, 128), (128, 184), (202, 128), (202, 184)]]
icon('blackberry-logo', B, ['blackberry', 'phone', 'smartphone', 'logo', 'brand'],
     line=BERRIES, area=BERRIES)

# Grammarly: the round badge with a G whose end turns into an arrow
icon('grammarly-logo', B, ['grammarly', 'writing', 'grammar', 'spelling', 'logo', 'brand'],
     line=[RING], area=[RING],
     detail=[P('M162 94 A48 48 0 1 0 176 128 H136'), PL([(140, 90), (162, 94), (166, 72)])])

# Polar: the disc with an inner meridian ellipse
icon('polar-logo', B, ['polar', 'polar.sh', 'open source', 'funding', 'logo', 'brand'],
     line=[RING], area=[RING], detail=[E(128, 128, 44, 96)])

# OpenVPN: a ring open at the bottom around a keyhole that runs down into the gap
KEY = 'M116 138 A28 28 0 1 1 140 138 L152 208 H104 Z'
icon('openvpn-logo', B, ['openvpn', 'vpn', 'tunnel', 'privacy', 'logo', 'brand'],
     line=[P('M95 218 A96 96 0 1 1 161 218'), P(KEY)], area=[P(KEY)])

# Adobe Creative Cloud: the cloud ribbon, a small and a large loop crossing over a flat base
icon('adobe-creative-cloud-logo', B, ['adobe creative cloud', 'creative cloud', 'adobe', 'cloud', 'logo', 'brand'],
     line=[P('M120 184 H80 A44 44 0 1 1 124 128 L148 164 C152 172 160 176 168 176 A52 52 0 1 0 128 96'),
           P('M152 184 H168')])

print(save(overwrite=True))
