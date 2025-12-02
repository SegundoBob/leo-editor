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
import ast
import glob
import os
import re
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
all = True
verbose = False

# Global stats.
chains_seen: set[str] = set()
errors: set[str] = set()
stats_attrs = 0
stats_contexts = 0
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
    #@+node:ekr.20251129080959.1: *3* CheckLeo.check
    def check(self, path: str) -> None:
        assert os.path.exists(path), repr(path)
        g = leoG
        contents = g.readFile(path)
        tree = ast.parse(contents, filename=path)
        visitor = Visitor()
        visitor.visit(tree)
    #@+node:ekr.20251201031243.1: *3* CheckLeo.report
    def report(self, t1: float, t2: float, t3: float) -> None:
        g = leoG
        print(
            f"check_leo.py: files: {len(self.files)} "
            f"contexts: {stats_contexts} "
            f"attrs: {stats_attrs} "
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
        if 0:
            if not any(z for z in (
                errors, unknown_bases, undefined_chains, unfinished_chains, verbose
            )):
                print('Done')
    #@+node:ekr.20251130081419.1: *3* CheckLeo.run
    def run(self) -> None:
        global leoC, leoG, leoP, leoV
        t1 = time.process_time()
        self.adjust_sys_path()
        c, g, p, v = self.create_live_objects()  # Takes about 0.9 sec.
        leoC, leoG, leoP, leoV = c, g, p, v
        self.files = self.compute_files()
        if 0:
            print('Live objects...')
            for obj in (g.app, g.app.gui, c.frame, c.frame.tree):
                print(obj)
        t2 = time.process_time()
        for path in self.files:
            self.check(path)
        t3 = time.process_time()
        self.report(t1, t2, t3)
    #@-others
#@+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):

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
        ignore_prefixes = (
            'c._bookmarks',
            'c.cleo',
            # 'c.opml',
            'c.quickMove',
        )
        part0, part1 = parts[0], parts[1]

        # Ignore some prefixes entirely.
        if f"{part0}.{part1}" in ignore_prefixes:  # Not worth checking.
            return None

        if 1:  # Only test what's in the table.
            return d.get(part0)  # Get the base, the first obj.

        # More ambitious...
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
        global stats_attrs
        stats_attrs += 1
        #@+<< define ignore dict >>
        #@+node:ekr.20251201051957.1: *4* << define ignore dict >>
        ignore = (
            # Obsolete ast Nodes in leoAst.py.
            'ast.Num',
            'ast.Str',
            # Injected by leoserver.py.
            'c.patched_quicksearch_controller',
            'g.in_leo_server',
            'g.leoServer',
            # Injected by plugins.
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
            # Injected into v...
            'v.archive_ua', 'v.undo_info', 'v.unknownAttributes',
            # Exists only io.StringIO objects.
            'sys.stdout.getvalue',
            # Minor mysteries.
            'c.config.exists',
            's.decode',
        )
        ignore_dict = {z: 1 for z in ignore}
        #@-<< define ignore dict >>
        parts = self.split_Attribute(node)
        assert len(parts) > 1, repr(parts)
        obj = self.get_obj(parts)  # Reports problems.
        i = 0
        while obj:
            try:
                attr = parts[i + 1]
            except IndexError:
                return
            if not hasattr(obj, attr):
                head = '.'.join(parts[: i + 1])
                if f"{head}.{attr}" not in ignore_dict:
                    undefined_chains.add('.'.join(parts))
                return
            # Move to the next obj.
            obj = getattr(obj, attr, None)
            i += 1
    #@-others
#@-others
CheckLeo().run()
#@-leo
