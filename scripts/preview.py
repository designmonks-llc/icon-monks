#!/usr/bin/env python3
"""Render a contact sheet for some icons without touching build outputs.

  python3 scripts/preview.py out.png house gear bell        # named icons
  python3 scripts/preview.py out.png --category Weather     # every icon in a category
  python3 scripts/preview.py out.png --all

Each row shows thin, light, regular, bold, fill, duotone at 48px, then regular at 24px and 16px.
A few reference icons (house, gear, envelope) are always included at the top for style matching.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

args = sys.argv[1:]
if len(args) < 2:
    raise SystemExit(__doc__)
out, rest = os.path.abspath(args[0]), args[1:]
names = sorted(f[:-4] for f in os.listdir(build.SRC) if f.endswith('.svg'))
if rest[0] == '--all':
    chosen = names
elif rest[0] == '--category':
    chosen = [n for n in names if build.load(os.path.join(build.SRC, n + '.svg'))[1] == rest[1]]
else:
    chosen = rest
icons = []
for n in ['house', 'gear', 'envelope'] + [c for c in chosen if c not in ('house', 'gear', 'envelope')]:
    roles, category, tags = build.load(os.path.join(build.SRC, n + '.svg'))
    icons.append({'name': n, 'paths': build.outline(roles)})
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
    json.dump({'weights': build.WEIGHTS, 'icons': icons}, fh)
subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preview_sheet.cjs'), fh.name, out], check=True)
os.unlink(fh.name)
print(out)
