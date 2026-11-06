"""Regenerate the generated animation snippets in docs/snippets/animations/ from tools/animations/specs/.

    python tools/animations/build.py            # all specs
    python tools/animations/build.py backpressure

Each spec writes docs/snippets/animations/<spec-name>.html. transactional-proxy.html and bean-lifecycle.html
are hand-written and have no spec.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "docs", "snippets", "animations")

names = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "specs")) if f.endswith(".py"))
for name in names:
    target = os.path.normpath(os.path.join(OUT, name + ".html"))
    subprocess.run([sys.executable, os.path.join(HERE, "specs", name + ".py"), target],
                   check=True, env={**os.environ, "PYTHONPATH": HERE})
    print("wrote", os.path.relpath(target))
