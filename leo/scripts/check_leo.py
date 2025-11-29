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

leo_editor_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
core_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'core'))
for z in (leo_editor_dir, core_dir):
    assert os.path.exists(z), repr(z)
#@-<< check_leo: imports >>
all = True
seen: set[str] = set()
verbose = False
stats_attrs = 0
#@+others
#@+node:ekr.20251129161138.1: ** adjust_sys_path
def adjust_sys_path() -> None:
    """Add 'leo-editor' to sys.path"""
    if leo_editor_dir not in sys.path:
        # Caution: path[0] is reserved for script path (or '' in REPL)
        sys.path.insert(1, leo_editor_dir)
#@+node:ekr.20251129161354.1: ** compute_files
def compute_files() -> list[str]:
    files: list[str]
    if all:
        files = glob.glob(f"{core_dir}{os.sep}*.py")
        files = [z for z in files if not z.startswith('_')]
    else:
        files = 'leoApp.py'
        files = [os.path.normpath(os.path.join(core_dir, z)) for z in files]
    for z in files:
        assert os.path.exists(z), repr(z)
    return files

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

        global stats_attrs
        stats_attrs += 1
        # Ignore for now?:
        ignore = (
            'c.patched_quicksearch_controller',  # Injected by server.finishCreate.
            'c.screenCastController',  # Injected by screencast plugin.
            'g.in_leo_server',  # Injected by server.__init__.
            'g.leoServer',  # Injected by server.__init__.
        )

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
                    if attr_s not in seen and attr_s not in ignore:
                        seen.add(attr_s)

        self.generic_visit(node)
    #@-others
#@+node:ekr.20251129080959.1: ** check
def check(path: str) -> None:
    assert os.path.exists(path), repr(path)
    contents = g.readFile(path)
    tree = ast.parse(contents, filename=path)
    visitor = Visitor()
    visitor.visit(tree)
#@-others
t1 = time.process_time()
adjust_sys_path()
c, g, p = create_live_objects()  # Takes about 0.9 sec.
leoC, leoG, leoP = c, g, p
files = compute_files()
g.cls()
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
