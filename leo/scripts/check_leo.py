#@+leo-ver=5-thin
#@+node:ekr.20251129060454.1: * @file ../scripts/check_leo.py
#@@language python

"""
Check Leo's core files for attribute errors not found by mypy, pylint or
pyflakes.

This script should run about as fast as pyflakes_leo.py.
"""
#@+<< check_leo: imports >>
#@+node:ekr.20251129080328.1: ** << check_leo: imports >>
import ast
import os
import sys
import time
# import textwrap

assert ast and time  ###

# Add 'leo-editor' to sys.path
leo_editor_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
core_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'core'))
for z in (leo_editor_dir, core_dir):
    assert os.path.exists(z), repr(z)

if leo_editor_dir not in sys.path:
    # Caution: path[0] is reserved for script path (or '' in REPL)
    sys.path.insert(1, leo_editor_dir)

from leo.core import leoGlobals as g  # pylint: disable=wrong-import-position
#@-<< check_leo: imports >>
#@+others
#@+node:ekr.20251129080858.1: ** create_live_objects
def create_live_objects():

    import leo.core.leoBridge as leoBridge

    controller = leoBridge.controller(gui='nullGui',
        loadPlugins=False,  # True: attempt to load plugins.
        readSettings=False,  # True: read standard settings files.
        silent=False,  # True: don't print signon messages.
        verbose=False)  # True: print informational messages.

    g = controller.globals()
    c = controller.openLeoFile('dummy')
    p = c.p
    return c, g, p
#@+node:ekr.20251129080749.7: ** ATTRIBUTE
def ATTRIBUTE(self, node) -> None:

    if isinstance(node.value, ast.Name):
        base = node.value.id
        attr = node.attr
        table = (
            (leoC, ('c', 'c1', 'c2')),
            (leoG, ('g', 'leoGlobals')),
            (leoP, ('p', 'p1', 'p2')),
        )
        for obj, bases in table:
            if base in bases and not hasattr(obj, attr):
                # self.report(messages.UndefinedName, node, f"{base}.{attr}")
                g.trace(f"Undefined: {base}.{attr}")

    self.handleChildren(node)
#@+node:ekr.20251129080959.1: ** check
def check(path: str) -> None:
    assert os.path.exists(path), repr(path)
    contents = g.readFile(path)
    g.trace(len(contents), path)
#@-others
g.cls()

# Compute files.
files: list[str] = ['leoApp.py']
files = [os.path.normpath(os.path.join(core_dir, z)) for z in files]
for z in files:
    assert os.path.exists(z), repr(z)
t1 = time.process_time()
leoC, leoG, leoP = create_live_objects()  # Takes about 0.9 sec.
for path in files:
    check(path)
t2 = time.process_time()
print(f"Done: {len(files)} file{g.plural(files)} in {t2-t1:.2f} sec.")
#@-leo
