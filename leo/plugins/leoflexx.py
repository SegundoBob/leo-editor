# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
# pylint: disable=logging-not-lazy
#@+<< leoflexx imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx imports >>
import leo.core.leoBridge as leoBridge
import leo.core.leoNodes as leoNodes
from flexx import flx
import re
import time
assert re and time
    # Suppress pyflakes complaints
#@-<< leoflexx imports >>
#@+<< ace assets >>
#@+node:ekr.20181111074958.1: ** << ace assets >>
# Assets for ace, embedded in the LeoBody and LeoLog classes.
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')
#@-<< ace assets >>
debug = True
debug_tree = True
#@+others
#@+node:ekr.20181103151350.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181113041410.1: **  suppress_unwanted_log_messages
def suppress_unwanted_log_messages():
    '''
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    '''
    allowed = r'(Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181107052522.1: ** class LeoApp(PyComponent)
# pscript never converts flx.PyComponents to JS.

class LeoApp(flx.PyComponent):
    '''
    The Leo Application.
    This is self.root for all flx.Widget objects!
    '''
    # This may be optional, but it doesn't hurt.
    main_window = flx.ComponentProp(settable=True)
    
    def init(self):
        c, g = self.open_bridge()
        self.c, self.g = c, g
        # Create all data-related ivars.
        self.create_all_data()
        # Create the main window and all its components.
        signon = '%s\n%s' % (g.app.signon, g.app.signon2)
        body = c.rootPosition().b
        redraw_dict = self.make_redraw_dict()
        main_window = LeoMainWindow(body, redraw_dict, signon)
        self._mutate('main_window', main_window)

    #@+others
    #@+node:ekr.20181111152542.1: *3* app.actions
    #@+node:ekr.20181111142921.1: *4* app.action: do_command
    @flx.action
    def do_command(self, command):

        if command == 'redraw':
            d = self.make_redraw_dict()
            self.root.dump_redraw_dict(d)
        elif command == 'test':
            self.test_new_tree()
            self.run_all_unit_tests()
        else:
            self.root.info('app.do_command: unknown command: %r' % command)
            ### To do: pass the command on to Leo's core.
    #@+node:ekr.20181113053154.1: *4* app.action: dump_redraw_dict & helpers
    @flx.action
    def dump_redraw_dict(self, d):
        '''Pretty print the redraw dict.'''
        print('app.dump_redraw dict...')
        padding, tag = None, 'c.p'
        self.dump_ap(d ['c.p'], padding, tag)
        level = 0
        for i, item in enumerate(d ['items']):
            self.dump_redraw_item(i, item, level)
            print('')
    #@+node:ekr.20181113085722.1: *5* app.action: dump_ap
    def dump_ap (self, ap, padding, tag):
        '''Print an archived position fully.'''
        stack = ap ['stack']
        if not padding:
            padding = ''
        padding = padding + ' '*4 
        if stack:
            print('%s%s:...' % (padding, tag or 'ap'))
            padding = padding + ' '*4
            print('%schildIndex: %s v: %s %s stack...' % (
                padding,
                str(ap ['childIndex']),
                ap['v'], ### .ljust(25),
                ap['headline'],
            ))
            padding = padding + ' '*4
            for stack_item in ap ['stack']:
                gnx, childIndex, headline = stack_item
                print('%s%s %s %s' % (
                    padding,
                    str(childIndex).ljust(2),
                    gnx, ### .ljust(25),
                    headline,
                ))
        else:
            print('%s%s: childIndex: %s v: %s stack: [] %s' % (
                padding, tag or 'ap',
                str(ap ['childIndex']).ljust(2),
                ap['v'], ### .ljust(25),
                ap['headline'],
            ))
    #@+node:ekr.20181113091522.1: *4* app.action: redraw_item
    @flx.action
    def dump_redraw_item(self, i, item, level):
        '''Pretty print one item in the redraw dict.'''
        padding = ' '*4*level
        # Print most of the item.
        print('%s%s gnx: %s body: %s %s' % (
            padding,
            str(i).ljust(3),
            item ['gnx'].ljust(25),
            str(len(item ['body'])).ljust(4),
            item ['headline'],
        ))
        tag = None
        self.dump_ap(item ['ap'], padding, tag)
        # Print children...
        children = item ['children']
        if children:
            print('%sChildren...' % padding)
            print('%s[' % padding)
            padding = padding + ' '*4
            for j, child in enumerate(children):
                index = '%s.%s' % (i, j)
                self.dump_redraw_item(index, child, level+1)
            padding = padding[:-4]
            print('%s]' % padding)
    #@+node:ekr.20181112165240.1: *4* app.action: info
    @flx.action
    def info (self, s):
        '''Send the string s to the flex logger, at level info.'''
        if not isinstance(s, str):
            s = repr(s)
        flx.logger.info('Leo: ' + s)
            # A hack: automatically add the "Leo" prefix so
            # the top-level suppression logic will not delete this message.
    #@+node:ekr.20181113042549.1: *4* app.action: redraw
    def redraw (self):
        '''
        Send a **redraw list** to the tree.
        
        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.
        
        As a side effect, app.make_redraw_dict updates all internal dicts.
        '''
        print('app.redraw')
        w = self.main_window
        d = self.make_redraw_dict()
        w.tree.redraw(d)

        
    #@+node:ekr.20181111202747.1: *4* app.action: select_ap
    @flx.action
    def select_ap(self, ap):
        '''Select the position in Leo's core corresponding to the archived position.'''
        c = self.c
        p = self.ap_to_p(ap)
        c.frame.tree.select(p)
    #@+node:ekr.20181111095640.1: *4* app.action: send_children_to_tree (Test)
    @flx.action
    def send_children_to_tree(self, parent_ap):
        '''
        Call w.tree.receive_children(d), where d is:
        {
            'parent': parent_ap,
            'children': [ap1, ap2, ...],
        }
        '''
        w = self.main_window
        p = self.ap_to_p(parent_ap)
        if p.hasChildren():
            w.tree.receive_children({
                'parent': parent_ap,
                'children': [self.p_to_ap(z) for z in p.children()],
            })
        elif debug: ###
            # Not an error.
            print('app.send_children_to_tree: no children', p.h)
    #@+node:ekr.20181111095637.1: *4* app.action: set_body (Test)
    @flx.action
    def set_body(self, ap):
        '''Set the body text in LeoBody to the body text of indicated node.'''
        w = self.main_window
        gnx = ap ['gnx']
        v = self.gnx_to_vnode(gnx)
        assert v, repr(ap)
        w.body.set_body(v.b)
    #@+node:ekr.20181111095640.2: *4* app.action: set_status_to_unl (CHANGE)
    @flx.action
    def set_status_to_unl(self, ap, gnx):
        ### c, g, w = self.c, self.g, self.main_window
        ### unls = []
        print('===== app.set_status_to_unl: not ready yet:') ###, repr(ap))
        # for i in range(len(ap)):
            # ap_s = self.ap_to_string(ap[:i+1])
            # gnx = self.ap_to_gnx.get(ap_s)
            # data = self.gnx_to_node.get(gnx, [])
            # unls.append(data[2] if data else '<not found: %s>' % ap_s)
        # fn = g.shortFileName(c.fileName())
        # fn = fn + '#' if fn else ''
        # w.status_line.set_text(fn + '->'.join(unls))
    #@+node:ekr.20181114015356.1: *3* app.create_all_data
    def create_all_data(self):
        '''Compute the initial values all data structures.'''
        t1 = time.clock()
        # gnx_to_vnode must never be cleared.
        # app.p_to_ap adds missing entries as needed.
        self.gnx_to_vnode = { 'gnx': v.gnx for v in self.c.all_unique_nodes() }
        t2 = time.clock()
        self.info('app.create_all_data: %5.2f sec.' % (t2-t1))
    #@+node:ekr.20181111155525.1: *3* app.utils
    #@+node:ekr.20181110090611.1: *4* app.ap_to_string
    def ap_to_string(self, ap):
        '''
        Convert an archived position (list of ints) to a string if necessary.
        '''
        if isinstance(ap, (list, tuple)):
            return '.'.join([str(z) for z in ap])
        assert isinstance(ap, str), repr(ap)
        return ap
    #@+node:ekr.20181110101328.1: *4* app.node_tuple_to_string
    def node_tuple_to_string(self, aTuple, ljust=False):

        ap, gnx, headline = aTuple
        s = self.ap_to_string(ap)
        s = s.ljust(17) if ljust else s.rjust(17)
        return '%s %s %s' % (s, gnx.ljust(30), headline)
    #@+node:ekr.20181111204659.1: *4* app.p_to_ap
    def p_to_ap(self, p):
        '''Convert a true Leo position to a serializable archived position.'''
        return {
            'childIndex': p._childIndex,
            'gnx': p.v.gnx,
            'headline': p.h, # For dumps.
            'stack': [{
                'gnx': v.gnx,
                'childIndex': childIndex,
                'headline': v.h, # For dumps & debugging.
            } for (v, childIndex) in p.stack ],
        }
    #@+node:ekr.20181111203114.1: *4* app.ap_to_p (uses gnx_to_vnode)
    def ap_to_p (self, ap):
        '''Convert an archived position to a true Leo position.'''
        childIndex = ap ['childIndex']
        v = self.gnx_to_vnode [ap ['gnx']]
        stack = [
            (self.gnx_to_vnode [d ['gnx']], d ['childIndex'])
                for d in ap ['stack']
        ]
        return leoNodes.position(v, childIndex, stack)
    #@+node:ekr.20181113043539.1: *4* app.make_redraw_dict & helpers
    def make_redraw_dict(self):
        '''
        Return a recursive, archivable, list of lists describing all and only
        the visible nodes of the tree.
        
        As a side effect, all LeoApp data are recomputed.
        '''
        c = self.c
        t1 = time.clock()
        self.clear_data()
            # This is correct. We are about to fully redraw the screen.
        aList = []
        p = c.rootPosition()
        ### Testing: forcibly expand the first node.
        p.expand()
        while p:
            if p.level() == 0 or p.isVisible():
                aList.append(self.make_dict_for_position(p))
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        d = {
            'c.p': self.p_to_ap(c.p),
            'items': aList,
        }
        if debug_tree:
            t2 = time.clock()
            self.info('app.make_redraw_dict: %5.4f sec' % (t2-t1))
        return d
    #@+node:ekr.20181113044217.1: *5* app.clear_data
    def clear_data(self):
        '''Clear all the date describing the tree.'''
        print('===== tree.clear_data')
        # These *are* necessary.
        self.gnx_to_body = {}
        self.gnx_to_vnode = {}
        ###
            # self.ap_to_gnx = {}
            # self.gnx_to_children = {}
            # self.gnx_to_node = {}
            # self.gnx_to_parents = {}
            # self.outline = []
    #@+node:ekr.20181113044701.1: *5* app.make_dict_for_position (MAKES DATA)
    def make_dict_for_position(self, p):
        '''
        Recursively add a sublist for p and all its visible nodes.
        
        Update all data structures for p.
        '''
        c = self.c
        self.gnx_to_vnode[p.v.gnx] = p.v
        children = [
            self.make_dict_for_position(child)
                for child in p.children()
                    if child.isVisible(c)
        ]
        return {
            'ap': self.p_to_ap(p),
            'body': p.b,
            'children': children,
            'gnx': p.v.gnx,
            'headline': p.h,
        }
    #@+node:ekr.20181105091545.1: *3* app.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = False,
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            flx.logger.error('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'LeoPyRef.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        return c, g
    #@+node:ekr.20181112182636.1: *3* app.run_all_unit_tests
    def run_all_unit_tests (self):
        '''
        Run all unit tests from the bridge using the browser gui.
        '''
        self.info('app.test: not ready yet')
        ### runUnitTests(self.c, self.g)
    #@+node:ekr.20181113180246.1: *3* app.test_new_tree
    def test_new_tree(self):
        '''Test the round tripping of p_to_ap and ap_to_p.'''
        c = self.c
        old_d = self.gnx_to_vnode.copy()
        t1 = time.clock()
        # Create a full gnx_to_vnode.
        self.gnx_to_vnode = { p.v.gnx: p.v for p in c.all_positions() }
        for p in c.all_positions():
            ap = self.p_to_ap(p)
            p2 = self.ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        t2 = time.clock()
        if 1:
            print('app.test_new_tree: %5.3f sec' % (t2-t1))
        self.gnx_to_vnode = old_d
    #@-others
#@+node:ekr.20181113041113.1: ** class LeoGui(PyComponent)
class LeoGui(flx.PyComponent):
    '''
    Leo's Browser Gui.
    
    This should be a subclass of leo.core.leoGui.LeoGui, but pscript does
    not support multiple inheritance.
    '''
    pass
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoBody

class LeoBody(flx.Widget):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, body):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")
        self.set_body(body)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
        
    @flx.action
    def set_body(self, body):
        self.ace.setValue(body)
#@+node:ekr.20181104082149.1: *3* class LeoLog
class LeoLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, signon):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.setValue(signon)
        
    @flx.action
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082130.1: *3* class LeoMainWindow
class LeoMainWindow(flx.Widget):
    
    '''
    Leo's main window, that is, root.main_window.
    
    Each property x below is accessible as root.main_window.x.
    '''
    # All these properties *are* needed.
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self, body_s, data, signon):
        # pylint: disable=arguments-differ
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoTree(data, flex=1)
                log = LeoLog(signon, flex=1)
            body = LeoBody(body_s, flex=1)
            minibuffer = LeoMiniBuffer()
            status_line = LeoStatusLine()
        for name, prop in (
            ('body', body),
            ('log', log),
            ('minibuffer', minibuffer),
            ('status_line', status_line),
            ('tree', tree),
        ):
            self._mutate(name, prop)

    #@+others
    #@+node:ekr.20181111001813.1: *4* JS versions of LeoApp utils
    #@+node:ekr.20181111001833.1: *5* LeoMainWindow.ap_to_string
    def ap_to_string(self, ap):
        '''
        Convert an archived position (list of ints) to a string if necessary.
        '''
        if isinstance(ap, (list, tuple)):
            return '.'.join([str(z) for z in ap])
        assert isinstance(ap, str), repr(ap)
        return ap
    #@+node:ekr.20181110125347.1: *5* LeoMainWindow.format_node_tuple
    def format_node_tuple(self, node_tuple):
        assert isinstance(node_tuple, (list, tuple)), repr(node_tuple)
        ap, gnx, headline = node_tuple
        s = '.'.join([str(z) for z in ap])
        return 'p: %s %s %s' % (s.ljust(15), gnx.ljust(30), headline)
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoMiniBuffer
class LeoMiniBuffer(flx.Widget):

    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')
    
    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
        
    @flx.reaction('widget.user_done')
    def on_event(self, *events):
        for ev in events:
            command = self.widget.text
            if command.strip():
                self.widget.set_text('')
                self.root.do_command(command)
#@+node:ekr.20181104082201.1: *3* class LeoStatusLine
class LeoStatusLine(flx.Widget):
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status')
        self.widget.apply_style('background: green')

    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
#@+node:ekr.20181104082138.1: *3* class LeoTree
class LeoTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    
    def init(self, redraw_dict):
        # pylint: disable=arguments-differ
        self.leo_items = {}
            # Keys are gnx's, values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are gnx's, values are True.
        self.clear_tree()
        self.tree = flx.TreeWidget(flex=1, max_selected=1)
            # The gnx of the selected tree item.
        self.redraw_from_dict(redraw_dict)
        
    #@+others
    #@+node:ekr.20181112163222.1: *4* tree.actions
    #@+node:ekr.20181112163252.1: *5* tree.action: clear_tree
    @flx.action
    def clear_tree(self):
        '''
        Completely clear the tree, preparing to recreate it.
        
        Important: we do *not* clear self.tree itself!
        '''
        # pylint: disable=access-member-before-definition
        print('===== tree.clear_tree')
        for item in self.leo_items.values():
            if debug or debug_tree:
                self.root.info('clear_tree: dispose: %r' % item)
            item.dispose()
        self.leo_items = {}
            # Keys are gnx's, values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are gnx's, values are True.
    #@+node:ekr.20181110175222.1: *5* tree.action: receive_children (Test)
    @flx.action
    def receive_children(self, d):
        '''
        d has the form:
        {
            'parent': ap
            'children': a list
                NEW: [ap1, ap2, ...]
                OLD: [ (ap, gnx, headline), ...]
        }
        '''
        if 1: ###
            print('tree.receive_children')
            for key, value in d.items():
                print(key, repr(value))
        ### parent_ap, parent_gnx, parent_headline = d.get('parent')
        ### assert parent_gnx == d.get('gnx'), (repr(parent_gnx), repr(d.get('gnx')))
        parent_gnx = d ['parent'] ['gnx']
        children = d ['children']
        self.populate_children(children, parent_gnx)
    #@+node:ekr.20181113043004.1: *5* tree.action: redraw
    @flx.action
    def redraw(self, redraw_dict):
        '''
        Clear the present tree and redraw using the redraw_list.
        '''
        self.clear_tree()
        self.redraw_from_dict(redraw_dict)
    #@+node:ekr.20181112172518.1: *4* tree.reactions
    #@+node:ekr.20181109083659.1: *5* tree.reaction: on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        for ev in events:
            if ev.new_value:
                # We are selecting a node, not de-selecting it.
                ap = ev.source.leo_ap
                if debug: ###
                    print('----- tree.on_selected_event', repr(ap))
                self.leo_selected_ap = ap
                    # Track the change.
                self.root.set_body(ap)
                    # Set the body text directly.
                self.root.set_status_to_unl(ap)
                    # Set the status line directly.
                self.root.send_children_to_tree(ap)
                    # Send the children back to us.
    #@+node:ekr.20181104080854.3: *5* tree.reaction: on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            if 0:
                self.show_event(ev)
    #@+node:ekr.20181111011928.1: *4* tree.populate_children (Change)
    def populate_children(self, children, parent_gnx):
        '''Populate parent with the children if necessary.'''
        if debug:
            print('tree.populate_children...')
            if parent_gnx in self.leo_populated_dict:
                print('===== already populated', parent_gnx)
                return
            print('parent', repr(self.leo_items[parent_gnx]))
            for child in children:
                print('  child: %r' % child)
        self.leo_populated_dict [parent_gnx] = True
        assert parent_gnx in self.leo_items, (parent_gnx, repr(self.leo_items))
        with self.leo_items[parent_gnx]:
            ### for ap, gnx, headline in children:
            for ap in children:
                gnx = ap ['gnx']
                headline = ap ['headline']
                item = LeoTreeItem(ap, text=headline, checked=None, collapsed=True)
                self.leo_items [gnx] = item
    #@+node:ekr.20181113043131.1: *4* tree.redraw_from_dict & helper
    def redraw_from_dict(self, d):
        '''
        Create LeoTreeItems from all items in the redraw_dict.
        The tree has already been cleared.
        '''
        self.leo_selected_ap = d ['c.p']
        for item in d ['items']:
            self.create_item_with_parent(item, self.tree)
           
    def create_item_with_parent(self, item, parent):
        '''Create a tree item for item and all its visible children.'''
        with parent:
            ap = item ['ap']
            gnx = ap ['gnx']
            headline = ap ['headline']
            # Create the tree item.
            tree_item = LeoTreeItem(ap, text=headline, checked=None, collapsed=True)
            self.leo_items [gnx] = tree_item
            # Create the item's children...
            for child in item ['children']:
                self.create_item_with_parent(child, tree_item)
    #@+node:ekr.20181108232118.1: *4* tree.show_event
    def show_event(self, ev):
        '''Put a description of the event to the log.'''
        w = self.root.main_window
        id_ = ev.source.title or ev.source.text
        kind = '' if ev.new_value else 'un-'
        s = kind + ev.type
        message = '%s: %s' % (s.rjust(15), id_)
        w.log.put(message)
        if debug and debug_tree:
            self.root.info('tree.show_event: ' + message)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoTreeItem
class LeoTreeItem(flx.TreeItem):
    
    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap
#@-others
if __name__ == '__main__':
    flx.launch(LeoApp)
    flx.logger.info('LeoApp: after flx.launch')
    if not debug:
        suppress_unwanted_log_messages()
    flx.run()
#@-leo
