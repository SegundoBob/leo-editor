#@+leo-ver=5-thin
#@+node:ekr.20251129060454.1: * @file ../scripts/check_leo.py
#@@language python

"""
Check Leo's core files for attribute errors not found by mypy, pylint or
pyflakes.

This script runs about as fast as pyflakes_leo.py.
"""
#@+<< check_leo: imports >>
#@+node:ekr.20251129080328.1: ** << check_leo: imports >>
# Required directly by script.
import ast
import glob
import os
import sys
import time
from typing import Any
#@-<< check_leo: imports >>

# Not needed: we always print a summary line.
# print(os.path.basename(__file__))

#@+<< check_leo: globals >>
#@+node:ekr.20251130105440.1: ** << check_leo: globals >>
# Global objects.
leoC, leoG, leoP, leoV = None, None, None, None

# Global switches.
all_files_flag = True

# Global stats.
all_attrs: set[str] = set()
chains_seen: set[str] = set()
errors: set[str] = set()
full_check = False  # True: report *all* unknown attrs.
module_name: str = None
report_all_attrs = False
report_all_unusual_attrs = False  # True: report only unused attrs containing '{}[]()'
report_unusual_attrs = True  # True: report only number of unusual attrs.
report_all_undefined_chains = True
report_all_unfinished_chains = True
report_all_unknown_bases = True
report_times = False
show_context_flag = False
show_all_context_flag = False
stats_attrs = 0
stats_contexts = 0
unknown_bases: set[str] = set()
undefined_chains: set[str] = set()

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
    #@+node:ekr.20251129080959.1: *3* CheckLeo.check
    def check(self, path: str) -> None:
        assert os.path.exists(path), repr(path)
        contents = leoG.readFile(path)
        tree = ast.parse(contents, filename=path)
        visitor = Visitor(self.known_objects)
        visitor.visit(tree)
    #@+node:ekr.20251129161354.1: *3* CheckLeo.compute_files
    def compute_files(self) -> list[str]:
        files: list[str]
        if all_files_flag:
            core_files = glob.glob(f"{core_dir}{os.sep}*.py")
            commands_files = glob.glob(f"{commands_dir}{os.sep}*.py")
            plugins_names = (
                # 'active_path.py',
                # 'add_directives.py',
                # 'anki.py',
                # 'attrib_edit.py',
                # 'at_folder.py',
                # 'at_produce.py',
                # 'at_view.py',
                # 'auto_colorize2_0.py',
                'backlink.py',
                # 'baseNativeTree.py',
                # 'bibtex.py',
                # 'bigdash.py',
                'bookmarks.py',
                # 'bzr_qcommands.py',
                # 'chapter_hoist.py',
                # 'colorize_headlines.py',
                'contextmenu.py',
                # 'ctagscompleter.py',
                # 'cursesGui.py',
                # 'cursesGui2.py',
                # 'datenodes.py',
                # 'debugger_pudb.py',
                # 'demo.py',
                # 'dragdropgoodies.py',
                # 'dtest.py',
                # 'dump_globals.py',
                # 'empty_leo_file.py',
                # 'enable_gc.py',
                # 'example_rst_filter.py',
                # 'expfolder.py',
                # 'FileActions.py',
                # 'freewin.py',
                # 'free_layout.py',
                # 'ftp.py',
                # 'geotag.py',
                # 'gitarchive.py',
                # 'graphcanvas.py',
                # 'history_tracer.py',
                # 'import_cisco_config.py',
                # 'indented_languages.py',
                # 'initinclass.py',
                # 'interact.py',
                # 'leocursor.py',
                # 'leofeeds.py',
                # 'leofts.py',
                # 'leomail.py',
                # 'leomylyn.py',
                # 'leoOPML.py',
                # 'leoremote.py',
                # 'leoscreen.py',
                # 'leo_cloud.py',
                # 'leo_cloud_server.py',
                # 'leo_interface.py',
                # 'leo_pdf.py',
                # 'leo_to_html.py',
                # 'leo_to_html_outline_viewer.py',
                # 'leo_to_rtf.py',
                # 'lineNumbers.py',
                # 'line_numbering.py',
                # 'livecode.py',
                # 'macros.py',
                # 'markup_inline.py',
                # 'maximizeNewWindows.py',
                # 'md_docer.py',
                # 'mime.py',
                # 'mnplugins.py',
                # 'mod_autosave.py',
                # 'mod_framesize.py',
                # 'mod_http.py',
                # 'mod_leo2ascd.py',
                # 'mod_read_dir_outline.py',
                'mod_scripting.py',
                # 'mod_speedups.py',
                # 'mod_timestamp.py',
                # 'multifile.py',
                'nav_qt.py',
                # 'nested_splitter.py',
                # 'niceNosent.py',
                # 'nodeActions.py',
                # 'nodediff.py',
                'nodetags.py',
                # 'nodewatch.py',
                # 'open_shell.py',
                # 'outline_export.py',
                # 'pane_commands.py',
                # 'paste_as_headlines.py',
                # 'patch_python_colorizer.py',
                'plugins_menu.py',
                # 'projectwizard.py',
                # 'pyplot_backend.py',
                # 'python_terminal.py',
                # 'QNCalendarWidget.py',
                'qtGui.py',
                'qt_commands.py',
                'qt_events.py',
                'qt_frame.py',
                'qt_gui.py',
                'qt_idle_time.py',
                'qt_layout.py',
                'qt_main.py',
                'qt_quickheadlines.py',
                'qt_quicksearch.py',
                'qt_quicksearch_sub.py',
                'qt_text.py',
                'qt_tree.py',
                'quickMove.py',
                'quicksearch.py',
                # 'quit_leo.py',
                # 'read_only_nodes.py',
                # 'redirect_to_log.py',
                # 'richtext.py',
                # 'rpcalc.py',
                # 'rss.py',
                # 'run_nodes.py',
                # 'screencast.py',
                # 'screenshots.py',
                # 'screen_capture.py',
                # 'script_io_to_body.py',
                # 'setHomeDirectory.py',
                # 'settings_finder.py',
                # 'sftp.py',
                'slideshow.py',
                # 'spydershell.py',
                # 'startfile.py',
                # 'stickynotes.py',
                # 'stickynotes_plus.py',
                # 'systray.py',
                # 'tables.py',
                # 'testRegisterCommand.py',
                # 'textnode.py',
                # 'threadutil.py',
                # 'timestamp.py',
                'todo.py',
                # 'tomboy_import.py',
                # 'trace_gc_plugin.py',
                # 'trace_tags.py',
                'viewrendered.py',
                'viewrendered3.py',
                # 'vim.py',
                # 'wikiview.py',
                # 'word_count.py',
                # 'word_export.py',
                # 'xdb_pane.py',
                # 'xemacs.py',
                # 'xml_edit.py',
                # 'xsltWithNodes.py',
                # 'zenity_file_dialogs.py',
            )
            plugins_files = [f"{plugins_dir}{os.sep}{z}" for z in plugins_names]
                # z for z in glob.glob(f"{plugins_dir}{os.sep}*.py")
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
    #@+node:ekr.20251202072018.1: *3* CheckLeo.compute_module_name
    def compute_module_name(self, file_name) -> str:

        for base in ('commands', 'core', 'plugins'):
            i = file_name.find(base)
            if i > -1:
                s = file_name[i:-3]
                break
        else:
            s = file_name  # Should not happen.
        return s.replace('/', '.').replace('\\', '.')
    #@+node:ekr.20251202174626.1: *3* CheckLeo.create_known_objects
    def create_known_objects(self) -> dict[str, Any]:
        assert leoC and leoG and leoP and leoV  # Must be run after create_live_objects.
        d = {
            # Python types
            'aList': [], 'aList1': [], 'aList2': [],
            's': ' ', 's1': ' ', 's2': ' ',

            # Leo objects.
            'c': leoC, 'c1': leoC, 'c2': leoC,
            'g': leoG,
            'p': leoP, 'p1': leoP, 'p2': leoP,
            'v': leoV,

            # 'd' can stand for dialog, dict, etc.
            # 'd': {},
        }
        if 0:
            leoG.printObj(d, tag='run:known_objects')
        if 0:
            print('Live objects...')
            for obj in (leoG.app, leoG.app.gui, leoC.frame, leoC.frame.tree):
                print(obj.__class__.__name__)
        return d
    #@+node:ekr.20251129080858.1: *3* CheckLeo.create_live_objects
    def create_live_objects(self) -> tuple[Any, Any, Any, Any]:

        import leo.core.leoBridge as leoBridge
        from leo.core.leoNodes import VNode
        from leo.plugins.qt_gui import LeoQtGui
        from leo.plugins.qt_frame import LeoQtFrame

        controller = leoBridge.controller(
            gui='nullGui',  # Only 'nullGui' is allowed!
            loadPlugins=False,  # True: attempt to load plugins.
            readSettings=False,  # True: read standard settings files.
            silent=False,  # True: don't print signon messages.
            verbose=False)  # True: print informational messages.

        g = controller.globals()
        c = controller.openLeoFile('dummy')
        p = c.p
        v = VNode(c)

        # Monkey-patch g.app.gui and c.frame.
        g.app.use_splash_screen = False
        g.app.gui = LeoQtGui()
        c.frame = LeoQtFrame(c, 'test-frame', g.app.gui)
        return c, g, p, v
    #@+node:ekr.20251201031243.1: *3* CheckLeo.report
    def report(self, t1: float, t2: float, t3: float) -> None:
        print(
            f"check_leo.py: files: {len(self.files)} "
            f"contexts: {stats_contexts} "
            f"attrs: {stats_attrs} "
            f"in {t3-t1:.2f} sec.")
        if report_times:
            print(
                f"Setup: {t2-t1:.2f} sec.\n"
                f" Scan: {t3-t2:.2f} sec.\n"
                f"Total: {t3-t1:.2f} sec.")
        if report_all_unusual_attrs or report_unusual_attrs:
            unusual_attrs = [
                z for z in all_attrs
                if not z.startswith(('"', "'")) and any(z2 in z for z2 in '()[]{}')
            ]
            if report_all_unusual_attrs:
                print(f"{len(unusual_attrs)} Unusual attrs..")
                for z in sorted(list(unusual_attrs)):
                    print(f"  {z}")
            else:
                print(f"{len(unusual_attrs)} Unusual attrs")
        elif report_all_attrs:
            print(f"{len(list(all_attrs))} attrs...")
            for z in sorted(list(all_attrs)):
                print(f"  {z}")
            print('')
        if errors:
            print('Errors...')
            for z in sorted(list(errors)):
                print(f"  {z}")
            print('')
        if unknown_bases:
            if report_all_unknown_bases:
                print(f"{len(list(unknown_bases))} Unknown bases...")
                for z in sorted(list(unknown_bases)):
                    print(f"  {z}")
                print('')
            else:
                n = len(list(unknown_bases))
                print(f"{n} unknown base{leoG.plural(n)}")
        if undefined_chains:
            print(f"Undefined chains: {len(list(undefined_chains))}")
            if report_all_undefined_chains:
                for z in sorted(list(undefined_chains)):
                    print(f"  {z}")
                print('')
        if 0:
            if not any(z for z in (
                all_attrs, errors, unknown_bases, undefined_chains, unfinished_chains
            )):
                print('Done')
    #@+node:ekr.20251130081419.1: *3* CheckLeo.run
    def run(self) -> None:
        global leoC, leoG, leoP, leoV
        global module_name
        t1 = time.process_time()
        self.adjust_sys_path()
        leoC, leoG, leoP, leoV = self.create_live_objects()  # Takes about 0.9 sec.
        self.files = self.compute_files()
        self.known_objects = self.create_known_objects()
        t2 = time.process_time()
        for path in self.files:
            module_name = self.compute_module_name(path)
            self.check(path)
        t3 = time.process_time()
        self.report(t1, t2, t3)
    #@-others
#@+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):

    context_stack: list[ast.AST] = []
    shown_contexts: list[ast.AST] = []  # Cumulative.
    shown_modules: list[ast.AST] = []  # Cumulative.

    def __init__(self, known_objects: dict[str, Any]) -> None:
        self.known_objects = known_objects

    #@+others
    #@+node:ekr.20251202084740.1: *3* Visitor.context_name
    def context_name(self) -> str:
        """Return the context's name"""
        node = self.context_stack[-1]
        return (
            node.name if isinstance(node, ((ast.ClassDef, ast.FunctionDef)))
            else module_name
        )

    #@+node:ekr.20251129080749.7: *3* Visitor.visit_Attribute & helpers
    def visit_Attribute(self, node: ast.AST) -> None:
        """
        Check the chain of attributes starting with this outer Attribute node.
        Only check attribute chains whose base (first) attr is known.
        """
        global stats_attrs
        stats_attrs += 1
        parts = self.split_Attribute(node)
        chain = '.'.join(parts)
        all_attrs.add(chain)
        obj = self.get_obj(parts)
        i = 0
        while obj is not None:
            try:
                attr = parts[i + 1]
            except IndexError:
                return
            if not hasattr(obj, attr):
                head = '.'.join(parts[: i + 1])
                checked = chain if full_check else f"{head}.{attr}"
                # Use full_check = True for testing.
                if not full_check and self.should_ignore(parts):
                    return
                if show_all_context_flag or (show_context_flag and checked not in undefined_chains):
                    self.show_context(node)
                    print(checked)
                undefined_chains.add(checked)
                # undefined_chains.add(chain)
                return
            # Move to the next obj.
            obj = getattr(obj, attr, None)
            i += 1

        # Do *not* call self.generic_visit here.
        # This visitor handles all its children.
    #@+node:ekr.20251201064630.1: *4* Visitor.get_obj
    required_prefixes = (
        'c', 'c1', 'c2',
        'g',
        'p', 'p1', 'p2',
        # These produce unknown bases.
        # 'w', 'widget', 'wrapper',
    )

    def get_obj(self, parts: list[str]) -> Any:
        """Return the live object corresonding to the base of the chain."""
        part0 = parts[0]
        # Return dummy objects.
        if part0.startswith(('"', "'", 's[')):
            return ' '  # A dummy string.
        if part0.startswith('['):
            return []
        if part0.startswith('{'):
            return {}  # A dummy dict

        # Is the base a known object?
        obj = self.known_objects.get(part0)
        if obj is not None:  # Careful: allow empty strings, lists, dicts.
            return obj  # Success.
        if part0 in self.required_prefixes:
            unknown_bases.add(f"{part0} in {'.'.join(parts)}")
        return None  # Failure.
    #@+node:ekr.20251203044755.1: *4* Visitor.should_ignore
    #@+<< define Attribute ignore_dict >>
    #@+node:ekr.20251201051957.1: *5* << define Attribute ignore_dict >>
    ignore_list = (
        # Obsolete ast Nodes in leoAst.py.
        'ast.Num',
        'ast.Str',
        # Injected by leoserver.py.
        'c.patched_quicksearch_controller',
        'g.in_leo_server',
        'g.leoServer',
        # Injected by plugins.
        'c._bookmarks',
        'c.cleo',
        'c.quickMove',
        'c.pluginsMenu',
        'c.screenCastController',
        'c.theScriptingController',
        'c.theTagController',
        'c.vr',  # viewrendered.py
        'g._bookmarks_target',
        'g._bookmarks_target_v',
        'g._quickmove_target_list',
        'g.app.xdb',  # leoDebugger.py
        'p.update_asciidoc',
        # Injected from Qt plugins.
        'c._style_deltas',
        'c.active_stylesheet',
        'c.frame.detached_body_info',
        'c.frame.nav',
        'c.ftm',
        'c.zoom_delta',
        'g.app.openWithTable',
        'g.insqh',
        # Not always present:
        'g.app.config.context_menus',
        'g.app.drag_source',
        'g.app.globalFindTabManager',
        'g.app.gui.log',
        'g.app.gui.set_minibuffer_label',
        'g.app.gui.show_find_success',
        'g.app.openWithTable',
        # p/v properties.
        'p.script',
        'p.v.h',
        'p.v.gnx',
        'p.v.script',
        'v.h',
        'v.gnx',
        # p/v injected attributes.
        'p.v.tempAttributes',
        'p.v.tempAttributes.get',
        # Injected into v...
        'v.archive_ua', 'v.undo_info', 'v.unknownAttributes',
        # Exists only io.StringIO objects.
        'sys.stdout.getvalue',
        # Minor mysteries.
        'c.config.exists',
        's.decode',
    )
    ignore_dict = {z: 1 for z in ignore_list}
    #@-<< define Attribute ignore_dict >>

    def should_ignore(self, parts: list[str]) -> bool:
        prefix = []
        for part in parts:
            prefix.append(part)
            if '.'.join(prefix) in self.ignore_dict:
                return True
        return False
    #@+node:ekr.20251203015013.1: *4* Visitor.show_context
    def show_context(self, node: ast.AST) -> None:
        """Print the context of the given node."""
        context = self.context_stack[-1]
        if context in self.shown_contexts:
            return
        self.shown_contexts.append(context)
        if module_name not in self.shown_modules:
            self.shown_modules.append(module_name)
            print(f"\nmodule {module_name}")
        if isinstance(context, ast.ClassDef):
            print(f"class {context.name}")
        elif isinstance(context, ast.FunctionDef):
            print(f"\nfunction {context.name}")
    #@+node:ekr.20251201032057.1: *4* Visitor.split_Attribute
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
    #@+node:ekr.20251202073629.1: *3* Visitor.visit_ClassDef
    def visit_ClassDef(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()
    #@+node:ekr.20251202073629.2: *3* Visitor.visit_FunctionDef
    def visit_FunctionDef(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()
    #@+node:ekr.20251202071202.1: *3* Visitor.visit_Module
    def visit_Module(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()
    #@-others
#@-others
CheckLeo().run()
#@-leo
