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
import re
import sys
import time
from typing import Any
#@-<< check_leo: imports >>
#@+<< check_leo: globals >>
#@+node:ekr.20251130105440.1: ** << check_leo: globals >>
# Global objects.
leoC, leoG, leoP, leoV = None, None, None, None

# Global switches.
all = True
verbose = False

# Global stats.
chains_seen: set[str] = set()
errors: set[str] = set()
stats_attrs = 0
unknown_bases: set[str] = set()
undefined_chains: set[str] = set()
unfinished_chains: set[str] = set()

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
    def create_live_objects(self) -> tuple[Any, Any, Any, Any]:

        import leo.core.leoBridge as leoBridge
        from leo.core.leoNodes import VNode

        controller = leoBridge.controller(gui='nullGui',
            loadPlugins=False,  # True: attempt to load plugins.
            readSettings=False,  # True: read standard settings files.
            silent=False,  # True: don't print signon messages.
            verbose=False)  # True: print informational messages.

        g = controller.globals()
        c = controller.openLeoFile('dummy')
        p = c.p
        v = VNode(c)
        return c, g, p, v
    #@+node:ekr.20251129080959.1: *3* CheckLeo.check
    def check(self, path: str) -> None:
        assert os.path.exists(path), repr(path)
        # global leoG
        g = leoG
        contents = g.readFile(path)
        tree = ast.parse(contents, filename=path)
        visitor = Visitor()
        visitor.visit(tree)
    #@+node:ekr.20251201031243.1: *3* CheckLeo.report
    def report(self, t1: float, t2: float, t3: float) -> None:
        # global leoG.
        g = leoG
        print(
            f"check_leo.py: attrs: {stats_attrs}, "
            f"{len(self.files)} file{g.plural(self.files)} "
            f"in {t3-t1:.2f} sec.")
        if verbose:
            print(
                f"Setup: {t2-t1:.2f} sec.\n"
                f" Scan: {t3-t2:.2f} sec.\n"
                f"Total: {t3-t1:.2f} sec.")
        if errors:
            print('Errors...')
            for z in sorted(list(errors)):
                print(f"  {z}")
        if unknown_bases:
            if verbose:
                print('Unknown bases...')
                for z in sorted(list(unknown_bases)):
                    print(f"  {z}")
            else:
                n = len(list(unknown_bases))
                print(f"{n} unknown base{g.plural(n)}")

        if undefined_chains:
            print('Undefined chains...')
            for z in sorted(list(undefined_chains)):
                print(f"  {z}")
        if unfinished_chains:
            print('')
            print('Unfinished chains...')
            for z in sorted(list(unfinished_chains)):
                print(f"  {z}")
    #@+node:ekr.20251130081419.1: *3* CheckLeo.run
    def run(self) -> None:
        global leoC, leoG, leoP, leoV
        t1 = time.process_time()
        self.adjust_sys_path()
        c, g, p, v = self.create_live_objects()  # Takes about 0.9 sec.
        leoC, leoG, leoP, leoV = c, g, p, v
        self.files = self.compute_files()
        g.cls()
        g.cls()  # Appears to be necessary.
        t2 = time.process_time()
        for path in self.files:
            self.check(path)
        t3 = time.process_time()
        self.report(t1, t2, t3)
    #@-others
#@+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):

    # def __init__(self, checker: CheckLeo) -> None:
        # self.checker = checker

    #@+others
    #@+node:ekr.20251201064630.1: *3* visitor.get_obj
    def get_obj(self, parts: list[str]) -> Any:

        d = {
            'c': leoC, 'c1': leoC, 'c2': leoC,
            'd': {},  # Dummy dict.
            'g': leoG,
            'p': leoP, 'p1': leoP, 'p2': leoP,
            's': ' ', 's1': ' ', 's2': ' ',  # Dummy strings.
            'v': leoV,
            # Library modules:
            'ast': ast,
            'glob': glob,
            'os': os,
            're': re,
            'sys': sys
        }
        part0, part1 = parts[0], parts[1]
        if f"{part0}.{part1}" in ('g.app', 'c.frame'):  # For later.
            return None
        if part0.startswith(('"', "'", 's[')):
            return ' '  # A dummy string.
        if part0.startswith('{'):
            return {}  # A dummy dict
        obj = d.get(part0)  # Get the base, the first obj.
        if obj:
            return obj
        if part0[0].isupper():
            i = part0.find('(')
            unknown_bases.add(part0 if i == -1 else part0[:i])
        elif part0 in (
            'app', 'at', 'k', 'w', 'self', 'super()', 'x', 'xdb', 'z',
            'wrapper', 'widget', 'window', 'word',
        ):  # For later.
            pass
        elif 0:  # Very verbose.
            unknown_bases.add(f"{part0} in {'.'.join(parts)}")
        return None
    #@+node:ekr.20251201064630.1: *3* visitor.get_obj
    def get_obj(self, parts: list[str]) -> Any:

        d = {
            'c': leoC, 'c1': leoC, 'c2': leoC,
            'd': {},  # Dummy dict.
            'g': leoG,
            'p': leoP, 'p1': leoP, 'p2': leoP,
            's': ' ', 's1': ' ', 's2': ' ',  # Dummy strings.
            'v': leoV,
            # Library modules:
            'ast': ast,
            'glob': glob,
            'os': os,
            're': re,
            'sys': sys
        }
        part0, part1 = parts[0], parts[1]
        if f"{part0}.{part1}" in ('g.app', 'c.frame'):  # For later.
            return None
        if part0.startswith(('"', "'", 's[')):
            return ' '  # A dummy string.
        if part0.startswith('{'):
            return {}  # A dummy dict
        obj = d.get(part0)  # Get the base, the first obj.
        if obj:
            return obj
        if part0[0].isupper():
            i = part0.find('(')
            unknown_bases.add(part0 if i == -1 else part0[:i])
        elif part0 in (
            'app', 'at', 'k', 'w', 'self', 'super()', 'x', 'xdb', 'z',
            'wrapper', 'widget', 'window', 'word',
        ):  # For later.
            pass
        elif 0:  # Very verbose.
            unknown_bases.add(f"{part0} in {'.'.join(parts)}")
        return None
    #@+node:ekr.20251201032057.1: *3* visitor.split_Attribute
    def split_Attribute(self, node: ast.AST) -> list[str]:
        """
        Return the components of an Attribute.

        The would be wrong: ast.unparse(node).split('.')
        """

        result: list[str] = []

        def _helper(node: ast.AST, result: list[str]) -> None:
            if isinstance(node, ast.Attribute):
                _helper(node.value, result)
                tail = node.attr
            elif isinstance(node, ast.Name):
                tail = node.id
            else:
                tail = ast.unparse(node)
            result.append(tail)

        _helper(node, result)
        return result
    #@+node:ekr.20251129080749.7: *3* visitor.visit_Attribute
    def visit_Attribute(self, node) -> None:
        # global chains_seen, errors, unfinished_chains, undefined_chains, unknown_bases.
        global stats_attrs
        stats_attrs += 1
        #@+<< define ignore dict >>
        #@+node:ekr.20251201051957.1: *4* << define ignore dict >>
        ignore = (
            # Injected by leoserver.py
            'c.patched_quicksearch_controller', 'g.in_leo_server', 'g.leoServer',
            # Injected by user plugins.
            'c.screenCastController',  # screencast.py
            'c.vr',  # viewrendered.py
            # Injected from Qt plugins...
            'c._style_deltas', 'c.active_stylesheet', 'c.ftm', 'c.zoom_delta', 'g.insqh',
            # Properties...
            'p.v.h', 'p.v.gnx', 'v.h', 'v.gnx',
            # Injected into v...
            'v.archive_ua', 'v.undo_info', 'v.unknownAttributes',
            # Mystery!
            'c.config.exists',
        )
        ignore_dict = {z: 1 for z in ignore}
        #@-<< define ignore dict >>
        parts = self.split_Attribute(node)
        assert len(parts) > 1, repr(parts)
        obj = self.get_obj(parts)
        if not obj:
            return

        def undefined(s: str) -> None:
            if s not in undefined_chains and s not in ignore_dict:
                context = '.'.join(parts)
                if context != s:
                    print(f"ADD {s} in {context}")
                undefined_chains.add(s)

        i = 0
        while obj:
            try:
                attr = parts[i + 1]
            except IndexError:
                return
            if not hasattr(obj, attr):
                head = '.'.join(parts[: i + 1])
                undefined(f"{head}.{attr}")
                return
            # Move to the next obj.
            obj = getattr(obj, attr, None)
            i += 1
    #@-others
#@-others
CheckLeo().run()
#@-leo
