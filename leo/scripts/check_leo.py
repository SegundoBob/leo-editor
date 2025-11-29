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
import glob
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
g.cls()
all = True
seen: set[str] = set()
verbose = False
stats_attrs = 0
#@+<< check_leo: compute files >>
#@+node:ekr.20251129100138.1: ** << check_leo: compute files >>
files: list[str]
if all:
    files = glob.glob(f"{core_dir}{os.sep}*.py")
    files = [z for z in files if not z.startswith('_')]
else:
    files = 'leoApp.py'
    files = [os.path.normpath(os.path.join(core_dir, z)) for z in files]
for z in files:
    assert os.path.exists(z), repr(z)
#@-<< check_leo: compute files >>
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
#@+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):
    #@+others
    #@+node:ekr.20251129080749.7: *3* visitor.visit_Attribute
    def visit_Attribute(self, node) -> None:

        global seen, stats_attrs
        stats_attrs += 1

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
                    attr_s = f"{base}.{attr}"
                    if attr_s not in seen:
                        seen.add(attr_s)

        self.generic_visit(node)
    #@-others
#@+node:ekr.20251129080959.1: ** check
def check(path: str) -> None:
    assert os.path.exists(path), repr(path)
    global seen
    contents = g.readFile(path)
    tree = ast.parse(contents, filename=path)
    visitor = Visitor()
    visitor.visit(tree)
#@-others
t1 = time.process_time()
leoC, leoG, leoP = create_live_objects()  # Takes about 0.9 sec.
t2 = time.process_time()
for path in files:
    check(path)
t3 = time.process_time()
if verbose:
    print(
        f"{len(files)} file{g.plural(files)}\n"
        f"Setup: {t2-t1:.2f} sec.\n"
        f" Scan: {t3-t2:.2f} sec.\n"
        f"Total: {t3-t1:.2f} sec")
for z in sorted(list(seen)):
    print(f"Undefined: {z}")

#@-leo
