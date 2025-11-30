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
#@-<< check_leo: imports >>
#@+<< check_leo: globals >>
#@+node:ekr.20251130105440.1: ** << check_leo: globals >>
# Global objects.
leoC, leoG, leoP = None, None, None

# Global switches.
all = True
verbose = False

# Global stats.
attrs_seen: set[str] = set()
attr_values_seen: set[str] = set()
chains_seen: set[str] = set()
stats_attrs = 0

# Global directories.
leo_editor_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
commands_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'commands'))
core_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'core'))
plugins_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'plugins'))
for z in (leo_editor_dir, commands_dir, core_dir):
    assert os.path.exists(z), repr(z)
#@-<< check_leo: globals >>
#@+others
#@+node:ekr.20251130081222.1: ** class CheckLeo
class CheckLeo:

    #@+others
    #@+node:ekr.20251129161138.1: *3* CheckLeo.adjust_sys_path
    def adjust_sys_path(self) -> None:
        """Add 'leo-editor' to sys.path"""
        if leo_editor_dir not in sys.path:
            # Caution: path[0] is reserved for script path (or '' in REPL)
            sys.path.insert(1, leo_editor_dir)
    #@+node:ekr.20251129161354.1: *3* CheckLeo.compute_files
    def compute_files(self) -> list[str]:
        files: list[str]
        if all:
            core_files = glob.glob(f"{core_dir}{os.sep}*.py")
            commands_files = glob.glob(f"{commands_dir}{os.sep}*.py")
            plugins_files = [
                z for z in glob.glob(f"{plugins_dir}{os.sep}*.py")
                if 'qt_' in z
            ]
            if 0:
                for z in plugins_files:
                    print(f"plugin: {z}")
            all_files = core_files + commands_files + plugins_files
            files = [z for z in all_files if not z.startswith('_')]
        else:
            files = 'leoApp.py'
            files = [os.path.normpath(os.path.join(core_dir, z)) for z in files]
        for z in files:
            assert os.path.exists(z), repr(z)
        return files
    #@+node:ekr.20251129080858.1: *3* CheckLeo.create_live_objects
    def create_live_objects(self):

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
    #@+node:ekr.20251129080959.1: *3* CheckLeo.check
    def check(self, path: str) -> None:
        assert os.path.exists(path), repr(path)
        global leoG
        g = leoG
        contents = g.readFile(path)
        tree = ast.parse(contents, filename=path)
        visitor = Visitor()
        visitor.visit(tree)
    #@+node:ekr.20251130081419.1: *3* CheckLeo.run
    def run(self) -> None:
        global leoC, leoG, leoP
        t1 = time.process_time()
        self.adjust_sys_path()
        c, g, p = self.create_live_objects()  # Takes about 0.9 sec.
        leoC, leoG, leoP = c, g, p
        files = self.compute_files()
        g.cls()
        g.cls()  # Appears to be necessary.
        t2 = time.process_time()
        for path in files:
            self.check(path)
        t3 = time.process_time()
        print(f"check_leo.py: attrs: {stats_attrs}, {len(files)} file{g.plural(files)} in {t3-t1:.2f} sec.")
        if verbose:
            print(
                f"Setup: {t2-t1:.2f} sec.\n"
                f" Scan: {t3-t2:.2f} sec.\n"
                f"Total: {t3-t1:.2f} sec.")
        for z in sorted(list(attrs_seen)):
            print(f"Undefined: {z}")
        if attr_values_seen:
            print(f"attr.values: {', '.join(sorted(list(attr_values_seen)))}")
    #@-others
#@+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):

    # def __init__(self, checker: CheckLeo) -> None:
        # self.checker = checker

    #@+others
    #@+node:ekr.20251129080749.7: *3* visitor.visit_Attribute
    def visit_Attribute(self, node) -> None:
        global attrs_seen, attr_values_seen, chains_seen, stats_attrs
        stats_attrs += 1
        ignore = (  # Ignore for now:
            # Injected by leoserver.py
            'c.patched_quicksearch_controller', 'g.in_leo_server', 'g.leoServer',
            # Injected by user plugins.
            'c.screenCastController',  # screencast.py
            'c.vr',  # viewrendered.py
            # Injected from Qt plugins...
            'c._style_deltas', 'c.active_stylesheet', 'c.ftm', 'c.zoom_delta', 'g.insqh',
            #### Mysteries: to do.
            # 'c.config.exists',  # 'p.v.gnx', 'p.v.h',
        )

        d = {
            'c': leoC, 'c1': leoC, 'c2': leoC,
            'g': leoG,
            'p': leoP, 'p1': leoP, 'p2': leoP,
        }

        def add(s: str, context: str) -> None:
            if s not in attrs_seen and s not in ignore:
                if context != s:
                    print(f"ADD {s} in {context}")
                attrs_seen.add(s)

        # Apply various hacks for now...
        s = ast.unparse(node)
        parts = s.split('.')
        if len(parts) < 2:
            return
        i = 0
        base, attr = parts[i], parts[i + 1]
        obj = d.get(base)
        while obj:
            if obj.__class__.__name__ in ('function', 'method', 'str'):  # Hack, especially str.
                return
            if attr[0].isupper() or any(z in attr for z in '()[]{}'):
                return  # Hack.
            if not hasattr(obj, attr):
                head = '.'.join(parts[: i + 1])
                add(f"{head}.{attr}", s)
                return
            # Check the next object.
            i += 1
            try:
                attr = parts[i + 1]
            except IndexError:
                return
            obj = getattr(obj, attr, None)
    #@-others
#@-others
CheckLeo().run()
#@-leo
