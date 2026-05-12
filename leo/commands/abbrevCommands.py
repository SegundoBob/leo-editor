# @+leo-ver=5-thin
# @+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
"""Leo's abbreviations commands."""

# @+<< abbrevCommands imports & abbreviations >>
# @+node:ekr.20150514045700.1: ** << abbrevCommands imports & abbreviations >>
from __future__ import annotations
from collections.abc import Callable
import functools
import re
import string
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextMixin

# @-<< abbrevCommands imports & abbreviations >>


def cmd(name: str) -> Callable:
    """Command decorator for the abbrevCommands class."""
    return g.new_cmd_decorator(name, ['c', 'abbrevCommands'])


# @+others
# @+node:ekr.20160514095531.1: ** class AbbrevCommands
class AbbrevCommandsClass(BaseEditCommandsClass):
    """
    A class to handle user-defined abbreviations.
    See apropos-abbreviations for details.
    """

    __slots__ = (
        'abbrevs',
        'c',
        'dynaregex',
        'enabled',
        'expanding',
        'last_hit',
        'number_regex',
        ### 'save_ins',
        ### 'save_sel',
        'tree_abbrevs_d',
        'w',
    )

    new = True  ###

    # @+others
    # @+node:ekr.20150514043850.3: *3* abbrev.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for AbbrevCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        # Set local ivars.
        self.abbrevs: dict[str, tuple[str, str]] = {}  # Keys are names, values are (abbrev,tag).
        self.dynaregex = re.compile(  # For dynamic abbreviations
            r'[%s%s\-_]+' % (string.ascii_letters, string.digits)
        )
        # Not a unicode problem.
        self.number_regex = re.compile(r'(?<!\\)\\n')  # to replace \\n but not \\\\n
        self.enabled = False
        self.expanding = False  # True: expanding abbreviations.
        self.last_hit = None  # Distinguish between text and tree abbreviations.
        ### self.save_ins = None  # Saved insert point.
        ### self.save_sel = None  # Saved selection range.
        self.subst_env: list[str] = []  # The scripting environment.
        self.tree_abbrevs_d: dict[str, str] = {}  # Keys are names, values are (tree,tag).
        self.w: QTextMixin = None

    # @+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev & helpers (entry point)
    def expandAbbrev(self, event: LeoKeyEvent, stroke: g.KeyStroke) -> bool:
        """
        Not a command.  Expand abbreviations..

        Words start with '@'.

        Return True if the abbreviation was expanded.
        """
        p = self.c.p
        w = event.w if event else None
        if not g.isTextWrapper(w):
            return False
        if self.expanding:
            return False
        ch = self.get_ch(event, stroke, w)
        if not ch:
            return False
        s, i, j, prefixes = self.get_prefixes(w)
        if not prefixes:
            return False
        # First, do we see the placeholder (,,)?
        if self.new:
            word = s[i:j] + ch
            if word.endswith(self.next_placeholder):
                self.do_placeholder(warn_flag=True)
                return True

        # Does the incoming string match any definition?
        # Handle headlines separately.
        w_name = g.app.gui.widget_name(w)
        if w_name.startswith('head'):
            for prefix in prefixes:
                _i, tag, word, val = self.match_prefix(ch, i, j, prefix, s)
                if word:
                    # #4462: Make only one substitution in headlines.
                    self.make_first_headline_substitution(ch, p, word, val)
                    return True  # Do not call c.endEditing.
            return False
        # General case.
        for prefix in prefixes:
            i, tag, word, val = self.match_prefix(ch, i, j, prefix, s)
            if word:
                self.make_general_replacements(i, j, w, word, val, tag)
                return True
        return False

    # @+node:ekr.20260512105951.1: *4* abbrev.do_placeholder
    def do_placeholder(self, warn_flag: bool) -> None:
        """
        Find the next place-holder string.

        By default this is <|...|>
        """
        c = self.c
        p = c.p.copy()
        if self.last_hit:
            # We are in a tree abbrev.
            while p:
                if self.find_place_holder(p):
                    return
                p.moveToThreadNext()
        elif self.find_place_holder(p):
            ###
            # Don't restore the insert point when selecting next placeholder.
            # self.save_ins = None
            # self.save_sel = None
            return
        if warn_flag:
            g.es_print(f"No next placeholder {c.abbrev_place_start}...{c.abbrev_place_end}")

    # @+node:ekr.20150514043850.12: *4* abbrev.expand_text
    def expand_text(self, w: QTextMixin, i: int, j: int, val: str, word: str) -> None:
        """Make a text expansion at location i,j of widget w."""
        c = self.c
        if self.new:
            warn_flag = self.last_hit and '__NEXT_PLACEHOLDER' in val
            val = self.make_script_substitutions(i, j, val)
            self.replace_selection(w, i, j, val)
            self.do_placeholder(warn_flag)
            return
        expand_search = bool('__NEXT_PLACEHOLDER' in val and self.last_hit)
        val = (
            '' if word == self.next_placeholder
            else self.make_script_substitutions(i, j, val)
        )  # fmt: skip
        self.replace_selection(w, i, j, val)
        # Search to the end.  We may have been called via a tree abbrev.
        p = c.p.copy()
        if expand_search:
            while p:
                if self.find_place_holder(p):
                    return
                p.moveToThreadNext()
        else:
            self.find_place_holder(p)
            # if self.find_place_holder(p):
            # Don't restore the insert point when selecting next placeholder.
            # self.save_ins = None
            # self.save_sel = None

    # @+node:ekr.20150514043850.13: *4* abbrev.expand_tree & helper
    def expand_tree(self, w: QTextMixin, i: int, j: int, tree_s: str, word: str) -> None:
        """
        Paste tree_s as children of c.p.
        This happens *before* any substitutions are made.
        """
        c = self.c
        if not c.canPasteOutline(tree_s):
            g.trace(f"bad copied outline: {tree_s}")
            return
        old_p = c.p.copy()
        self.replace_selection(w, i, j, None)
        self.paste_tree(old_p, tree_s)
        # Make all script substitutions first.
        for p in old_p.self_and_subtree():
            # Search for the next place-holder.
            p.b = self.make_script_substitutions(0, 0, p.b)
        # Now search for all place-holders.
        for p in old_p.subtree():
            if self.find_place_holder(p):
                break

    # @+node:ekr.20150514043850.17: *5* abbrev.paste_tree
    def paste_tree(self, old_p: Position, s: str) -> None:
        """Paste the tree corresponding to s (xml) into the tree."""
        c = self.c
        c.fileCommands.leo_file_encoding = 'utf-8'
        p = c.pasteOutline(s=s, undoFlag=False)
        if p:
            # Promote the name node, then delete it.
            p.moveToLastChildOf(old_p)
            c.selectPosition(p)
            c.promote(undoFlag=False)
            p.doDelete()
            c.redraw(old_p)  # 2017/02/27: required.
        else:
            g.trace('paste failed')

    # @+node:ekr.20150514043850.14: *4* abbrev.find_place_holder & helper
    def find_place_holder(self, p: Position) -> bool:
        """
        Search for the next place-holder.
        If found, select the place-holder (without the delims).
        """
        c = self.c
        # Do #438: Search for placeholder in headline.
        s = p.h
        if c.abbrev_place_start and c.abbrev_place_start in s:
            new_s, i, j = self.next_place(s, offset=0)
            if i is not None:
                p.h = new_s
                c.redraw(p)
                c.editHeadline()
                w = c.headline_wrapper(p)
                w.setSelectionRange(i, j, insert=j)
                return True
        s = p.b
        if c.abbrev_place_start and c.abbrev_place_start in s:
            new_s, i, j = self.next_place(s, offset=0)
            if i is None:
                return False
            w = c.frame.body.wrapper
            switch = p != c.p
            if switch:
                c.selectPosition(p)
            else:
                scroll = w.getYScrollPosition()
            w.setAllText(new_s)
            p.v.b = new_s
            if switch:
                c.redraw()
            w.setSelectionRange(i, j, insert=j)
            if switch:
                w.seeInsertPoint()
            else:
                # Keep the scroll point if possible.
                w.setYScrollPosition(scroll)
                w.seeInsertPoint()
            c.bodyWantsFocusNow()
            return True
        # #453: do nothing here.
        #   c.frame.body.forceFullRecolor()
        #   c.bodyWantsFocusNow()
        return False

    # @+node:ekr.20150514043850.16: *5* abbrev.next_place
    def next_place(self, s: str, offset: int = 0) -> tuple[str, int, int]:
        """
        Given string s containing a placeholder like <| block |>,
        return (s2,start,end) where s2 is s without the <| and |>,
        and start, end are the positions of the beginning and end of block.
        """
        c = self.c
        if c.abbrev_place_start is None or c.abbrev_place_end is None:
            return s, None, None  # #1345.
        new_pos = s.find(c.abbrev_place_start, offset)
        new_end = s.find(c.abbrev_place_end, offset)
        if (new_pos < 0 or new_end < 0) and offset:
            new_pos = s.find(c.abbrev_place_start)
            new_end = s.find(c.abbrev_place_end)
            if not (new_pos < 0 or new_end < 0):
                g.es("Found earlier placeholder")
        if new_pos < 0 or new_end < 0:
            return s, None, None
        start = new_pos
        place_holder_delim = s[new_pos : new_end + len(c.abbrev_place_end)]
        place_holder = place_holder_delim[len(c.abbrev_place_start) : -len(c.abbrev_place_end)]
        s2 = s[:start] + place_holder + s[start + len(place_holder_delim) :]
        end = start + len(place_holder)
        return s2, start, end

    # @+node:ekr.20161121111502.1: *4* abbrev.get_ch
    def get_ch(self, event: LeoKeyEvent, stroke: g.KeyStroke, w: QTextMixin) -> str:
        """Get the ch from the stroke."""
        ch = g.checkUnicode(event and event.char or '')
        if w.hasSelection():
            return None
        assert g.isStrokeOrNone(stroke), stroke
        if stroke in ('BackSpace', 'Delete'):
            return None
        d = {'Return': '\n', 'Tab': '\t', 'space': ' ', 'underscore': '_'}
        if stroke:
            ch = d.get(stroke.s, stroke.s)
            if len(ch) > 1:
                if (
                    stroke.find('Ctrl+') > -1 or
                    stroke.find('Alt+') > -1 or
                    stroke.find('Meta+') > -1
                ):  # fmt: skip
                    ch = ''
                else:
                    ch = event.char if event else ''
        else:
            ch = event.char
        return ch

    # @+node:ekr.20161121112346.1: *4* abbrev.get_prefixes
    def get_prefixes(self, w: QTextMixin) -> tuple[str, int, int, list[str]]:
        """Return the prefixes at the current insertion point of w."""
        # New code allows *any* sequence longer than 1 to be an abbreviation.
        # Any whitespace stops the search.
        s = w.getAllText()
        j = w.getInsertPoint()
        i, prefixes = j - 1, []
        while len(s) > i >= 0 and s[i] not in ' \t\n':
            prefixes.append(s[i:j])
            i -= 1
        prefixes = list(reversed(prefixes))
        if '' not in prefixes:
            prefixes.append('')
        return s, i, j, prefixes

    # @+node:ekr.20161121102113.1: *4* abbrev.make_first_headline_substitution
    def make_first_headline_substitution(self, ch: str, p: Position, word: str, val: str) -> None:
        """
        Make *only* the first scripting substitution in p.h.
        """
        c = self.c
        u = c.undoer

        # End editing, so we can get p.h before appending ch.
        c.endEditing()

        # Look for scripting substitutions.
        sub_start = re.escape(c.abbrev_subst_start)
        sub_end = re.escape(c.subst_end)
        pattern = re.compile(rf"^(.*?){sub_start}(.+){sub_end}(.*?)$")
        if m := pattern.match(val):
            content = m.group(2)
            c.abbrev_subst_env['x'] = ''
            try:
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
                x = c.abbrev_subst_env.get('x')
                if x:
                    val = f"{m.group(1)}{x}{m.group(3)}"
            except Exception:
                # Leave p.h alone.
                g.trace('scripting error in', p.h)
                g.es_exception()

        # Compute s, the final value of p.h..
        val = val.replace('\n', '').replace('\r', '')
        bunch = u.beforeChangeHeadline(p)
        p.h = s = f"{p.h}{ch}".replace(word, val)
        u.afterChangeHeadline(p, 'Expand Headline Abbreviation', bunch)

        # Select the placeholder if it exists. Otherwise, the last character.
        place_start, place_end = c.abbrev_place_start, c.abbrev_place_end
        i_start = s.find(place_start, 0)
        i_end = s.find(place_end, 0)
        if -1 < i_start < i_end:
            end = i_end + len(place_end)
            i, j, ins = i_start, end, end
        else:
            i = j = ins = len(s)

        # Continue editing the headline with the correct selection.
        c.frame.tree.editLabel(p, selection=(i, j, ins))

    # @+node:ekr.20260509051202.1: *4* abbrev.make_general_replacements
    def make_general_replacements(
        self, i: int, j: int, w: QTextMixin, word: str, val: str, tag: str
    ) -> None:
        c, p = self.c, self.c.p
        if val == '__NEXT_PLACEHOLDER':
            # Delete the last character.
            i = w.getInsertPoint()
            w.delete(i)

        # Handle a word that matches a prefix.
        c.abbrev_subst_env['_abr'] = word
        if tag == 'tree':
            self.last_hit = p.copy()
            self.expand_tree(w, i, j, val, word)
            c.undoer.clearAndWarn('tree-abbreviation')
            return
        # Expand, but never expand a search for text matches.
        if '__NEXT_PLACEHOLDER' not in val:
            self.last_hit = None
        self.expand_text(w, i, j, val, word)
        ###
        # # Restore the selection range.
        # if self.save_ins:
        #     ins = self.save_ins
        #     sel1, sel2 = self.save_sel
        #     w.setSelectionRange(sel1, sel2, insert=ins)

    # @+node:ekr.20150514043850.15: *4* abbrev.make_script_substitutions
    def make_script_substitutions(self, i: int, j: int, val: str) -> str:
        """Make scripting substitutions in node p."""
        c = self.c
        ### w = c.frame.body.wrapper
        if not c.abbrev_subst_start:
            return val
        if c.abbrev_subst_start not in val:
            return val

        # Perform all scripting substitutions.
        ###
        # self.save_ins = None
        # self.save_sel = None
        while c.abbrev_subst_start in val:
            prefix, rest = val.split(c.abbrev_subst_start, 1)
            content_list = rest.split(c.subst_end, 1)
            if len(content_list) != 2:
                break
            content: str
            content, rest = content_list
            try:
                self.expanding = True
                c.abbrev_subst_env['x'] = ''
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
            except Exception:
                g.es_print('exception evaluating', content)
                g.es_exception()
            finally:
                self.expanding = False
            x = c.abbrev_subst_env.get('x') or ''
            val = f"{prefix}{x}{rest}"
            ###
            # Save the selection range.
            # self.save_ins = w.getInsertPoint()
            # self.save_sel = w.getSelectionRange()
        return val

    # @+node:ekr.20161121112837.1: *4* abbrev.match_prefix
    def match_prefix(
        self, ch: str, i: int, j: int, prefix: str, s: str
    ) -> tuple[int, str, str, str]:
        """A match helper."""
        i = j - len(prefix)
        word = g.checkUnicode(prefix) + g.checkUnicode(ch)
        tag = 'tree'
        val = self.tree_abbrevs_d.get(word)
        if not val:
            val, tag = self.abbrevs.get(word, (None, None))
        fail = -1, tag, None, None
        if not val:
            return fail
        # Require a word match if the abbreviation is itself a word.
        if ch in ' \t\n':
            word = word.rstrip()
        if not word:
            return fail
        if word[0].isalpha() and i > 0 and s[i - 1].isalpha():
            return fail
        # We can assert word and val.
        return i, tag, word, val

    # @+node:ekr.20150514043850.18: *4* abbrev.replace_selection
    def replace_selection(self, w: QTextMixin, i: int, j: int, s: str) -> None:
        """Replace w[i:j] by s."""
        p, u = self.c.p, self.c.undoer
        w_name = g.app.gui.widget_name(w)
        bunch = u.beforeChangeBody(p)
        ###
        # if i == j:
        #     abbrev = ''
        # else:
        #     abbrev = w.get(i, j)
        #     w.delete(i, j)
        if i != j:
            w.delete(i, j)
        if s is None:
            ins = i
        else:
            w.insert(i, s)
            ins = i + len(s)
        w.setSelectionRange(ins, ins, ins)
        if w_name.startswith('head'):
            pass  # Don't set p.h here!
        else:
            # Fix part of #438. Don't leave the headline.
            p.v.b = w.getAllText()
            u.afterChangeBody(p, 'Abbreviation', bunch)
        ###
        # # Adjust self.save_sel & self.save_ins
        # if s is not None and self.save_sel is not None:
        #     i, j = self.save_sel
        #     ins = self.save_ins
        #     delta = len(s) - len(abbrev)
        #     self.save_sel = i + delta, j + delta
        #     self.save_ins = ins + delta

    # @+node:ekr.20150514043850.5: *3* abbrev.finishCreate
    def finishCreate(self) -> None:
        """AbbrevCommandsClass.finishCreate."""
        self.reload_settings()

    # @+node:ekr.20170221035644.1: *3* abbrev.reload_settings & helpers
    def reload_settings(self) -> None:
        """Reload all abbreviation settings."""
        self.abbrevs = {}
        self.init_settings()
        self.init_abbrev()
        self.init_tree_abbrev()
        self.init_env()

    reloadSettings = reload_settings

    # @+node:ekr.20150514043850.6: *4* abbrev.init_abbrev & helper
    def init_abbrev(self) -> None:
        """
        Init the user abbreviations from @data global-abbreviations
        and @data abbreviations nodes.
        """
        c = self.c
        table = (
            ('global-abbreviations', 'global'),
            ('abbreviations', 'local'),
        )
        for source, tag in table:
            aList = c.config.getData(source, strip_data=False) or []
            abbrev, result = [], []
            for s in aList:
                if s.startswith('\\:'):
                    # Continue the previous abbreviation.
                    abbrev.append(s[2:])
                else:
                    # End the previous abbreviation.
                    if abbrev:
                        result.append(''.join(abbrev))
                        abbrev = []
                    # Start the new abbreviation.
                    if s.strip():
                        abbrev.append(s)
            # End any remaining abbreviation.
            if abbrev:
                result.append(''.join(abbrev))
            for s in sorted(result):
                self.addAbbrevHelper(s, tag)

        # Define the expansion of the placeholder (usually ',,') to be '__NEXT_PLACEHOLDER'.
        if self.new:
            return  ###
        if self.next_placeholder:
            self.addAbbrevHelper(f"{self.next_placeholder}=__NEXT_PLACEHOLDER", 'global')

    # @+node:ekr.20150514043850.25: *5* abbrev.addAbbrevHelper
    def addAbbrevHelper(self, s: str, tag: str = '') -> None:
        """Enter the abbreviation 's' into the self.abbrevs dict."""
        if not s.strip():
            return
        try:
            d = self.abbrevs
            data = s.split('=')
            # Do *not* strip ws so the user can specify ws.
            name = data[0].replace('\\t', '\t').replace('\\n', '\n')
            val = '='.join(data[1:])
            if val.endswith('\n'):
                val = val[:-1]
            val = self.number_regex.sub('\n', val).replace('\\\\n', '\\n')
            old, tag = d.get(
                name,
                (None, None),
            )
            if old and old != val and not g.unitTesting:
                g.es_print(f"redefining abbreviation {name}\nfrom {old!r} to {val!r}")
            d[name] = val, tag
        except ValueError:
            g.es_print(f"bad abbreviation: {s}")

    # @+node:ekr.20150514043850.7: *4* abbrev.init_env
    def init_env(self) -> None:
        """
        Init c.abbrev_subst_env by executing the contents of the
        @data abbreviations-subst-env node.
        """
        c = self.c
        at = c.atFileCommands
        if c.abbrev_place_start and self.enabled:
            aList = self.subst_env
            script_list = []
            for z in aList:
                # Compatibility with original design.
                if z.startswith('\\:'):
                    script_list.append(z[2:])
                else:
                    script_list.append(z)
            script = ''.join(script_list)
            # Allow Leo directives in @data abbreviations-subst-env trees.
            # #1674: Avoid unnecessary entries in c.fileCommands.gnxDict.
            root = c.rootPosition()
            if root:
                v = root.v
            else:
                # Defensive programming. Probably will never happen.
                v = leoNodes.VNode(context=c)
                root = leoNodes.Position(v)
            # Similar to g.getScript.
            script = at.stringToString(
                root=root,
                s=script,
                forcePythonSentinels=True,
                sentinels=False,
            )
            script = script.replace("\r\n", "\n")
            try:
                exec(script, c.abbrev_subst_env, c.abbrev_subst_env)  # type:ignore
            except Exception:
                g.es('Error executing @data abbreviations-subst-env')
                g.es_exception()
        else:
            c.abbrev_subst_start = ''  # Was False.

    # @+node:ekr.20150514043850.8: *4* abbrev.init_settings (called from reload_settings)
    def init_settings(self) -> None:
        """Called from AbbrevCommands.reload_settings aka reloadSettings."""
        c = self.c
        if not c.config:
            return
        getBool, getString = c.config.getBool, c.config.getString

        # Local settings. Normally not accessed via c.abbrev_subst_env.
        self.enabled = getBool('scripting-at-script-nodes') or getBool('scripting-abbreviations')
        self.globalDynamicAbbrevs = getBool('globalDynamicAbbrevs')
        self.next_placeholder = getString("abbreviations-next-placeholder") or ''

        # Allow @data abbreviations-subst-env *only* in leoSettings.leo or myLeoSettings.leo!
        key = 'abbreviations-subst-env'
        if c.config.isLocalSetting(key, 'data'):
            g.issueSecurityWarning(f"@data {key}")
            self.subst_env = []
        else:
            self.subst_env = c.config.getData(key, strip_data=False)

        # Inject one ivar.
        c.k.abbrevOn = getBool('enable-abbreviations', default=False)

        # Commander ivars for scripting environments, unit tests, etc.
        c.abbrev_place_end = getString('abbreviations-place-end')
        c.abbrev_place_start = getString('abbreviations-place-start')
        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {}}  # May be augmented in init_env.
        c.abbrev_subst_start = getString('abbreviations-subst-start') or ''
        c.subst_end = getString('abbreviations-subst-end')

    # @+node:ekr.20150514043850.9: *4* abbrev.init_tree_abbrev
    def init_tree_abbrev(self) -> None:
        """Init tree_abbrevs_d from @data tree-abbreviations nodes."""
        c = self.c
        #
        # Careful. This happens early in startup.
        root = c.rootPosition()
        if not root:
            return
        if not c.p:
            c.selectPosition(root)
        if not c.p:
            return
        data = c.config.getOutlineData('tree-abbreviations')
        if data is None:
            return
        d: dict[str, str] = {}
        # #904: data may be a string or a list of two strings.
        aList = [data] if isinstance(data, str) else data
        for tree_s in aList:
            #
            # Expand the tree so we can traverse it.
            if not c.canPasteOutline(tree_s):
                return
            c.fileCommands.leo_file_encoding = 'utf-8'
            #
            # As part of #427, disable all redraws.
            old_disable = g.app.disable_redraw
            try:
                g.app.disable_redraw = True
                self.init_tree_abbrev_helper(d, tree_s)
            finally:
                g.app.disable_redraw = old_disable
        self.tree_abbrevs_d = d

    # @+node:ekr.20170227062001.1: *5* abbrev.init_tree_abbrev_helper
    def init_tree_abbrev_helper(self, d: dict[str, str], tree_s: str) -> None:
        """Init d from tree_s, the text of a copied outline."""
        c = self.c
        hidden_root = c.fileCommands.getPosFromClipboard(tree_s)
        if not hidden_root:
            g.trace('no pasted node')
            return
        for p in hidden_root.children():
            for s in g.splitLines(p.b):
                if s.strip() and not s.startswith('#'):
                    abbrev_name = s.strip()
                    # #926: Allow organizer nodes by searching all descendants.
                    for child in p.subtree():
                        if child.h.strip() == abbrev_name:
                            abbrev_s = c.fileCommands.outline_to_clipboard_string(child)
                            d[abbrev_name] = abbrev_s
                            break
                    else:
                        g.trace(f"no definition for {abbrev_name}")

    # @+node:ekr.20260511152312.1: *3* abbrev: Commands & helpers
    # @+node:ekr.20150514043850.23: *4* abbrev._getDynamicList (helper)
    def _getDynamicList(self, w: QTextMixin, s: str) -> list[str]:
        """Return a list of dynamic abbreviations."""
        if self.globalDynamicAbbrevs:
            # Look in all nodes.h
            items = []
            for p in self.c.all_unique_positions():
                items.extend(self.dynaregex.findall(p.b))
        else:
            # Just look in this node.
            items = self.dynaregex.findall(w.getAllText())
        items = sorted(set([z for z in items if z.startswith(s)]))
        return items

    # @+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
    @cmd('dabbrev-completion')
    def dynamicCompletion(self, event: LeoKeyEvent = None) -> None:
        """
        dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.
        """
        c, p = self.c, self.c.p
        w = event.w if event else None
        if not g.isTextWrapper(w):
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        word = w.get(i, j)
        aList = self._getDynamicList(w, word)
        if not aList:
            return
        # Bug fix: remove s itself, otherwise we can not extend beyond it.
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        if prefix.strip():
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p)
            s = s[:i] + prefix + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i + len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p, command='dabbrev-completion', bunch=b)
            c.recolor()

    # @+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ & helper
    @cmd('dabbrev-expands')
    def dynamicExpansion(self, event: LeoKeyEvent = None) -> None:
        """
        dabbrev-expands (M-/ in Emacs).

        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        """
        w = event.w if event else None
        if not g.isTextWrapper(w):
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        # This allows the cursor to be placed anywhere in the word.
        w.setInsertPoint(j)
        word = w.get(i, j)
        aList = self._getDynamicList(w, word)
        if not aList:
            return
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        prefix = prefix.strip()
        self.dynamicExpandHelper(event, prefix, aList, w)

    # @+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
    def dynamicExpandHelper(
        self,
        event: LeoKeyEvent,
        prefix: str = None,
        aList: list[str] = None,
        w: QTextMixin = None,
    ) -> None:
        """State handler for dabbrev-expands command."""
        c, k = self.c, self.c.k
        self.w = w
        if prefix is None:
            prefix = ''
        prefix2 = 'dabbrev-expand: '
        c.frame.log.deleteTab('Completion')
        g.es('', '\n'.join(aList or []), tabName='Completion')
        # Protect only prefix2 so tab completion and backspace to work properly.
        k.setLabelBlue(prefix2, protect=True)
        k.setLabelBlue(prefix2 + prefix, protect=False)
        k.get1Arg(event, handler=self.dynamicExpandHelper1, tabList=aList, prefix=prefix)

    def dynamicExpandHelper1(self, event: LeoKeyEvent) -> None:
        """Finisher for dabbrev-expands."""
        c, k = self.c, self.c.k
        p = c.p
        c.frame.log.deleteTab('Completion')
        k.clearState()
        k.resetLabel()
        if k.arg:
            w = self.w
            s = w.getAllText()
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p)
            ins = ins1 = w.getInsertPoint()
            if 0 < ins < len(s) and not g.isWordChar(s[ins]):
                ins1 -= 1
            i, j = g.getWord(s, ins1)
            # word = s[i: j]
            s = s[:i] + k.arg + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i + len(k.arg))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p, command='dabbrev-expand', bunch=b)
            c.recolor()

    # @+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
    @cmd('abbrev-kill-all')
    def killAllAbbrevs(self, event: LeoKeyEvent) -> None:
        """Delete all abbreviations."""
        self.abbrevs = {}

    # @+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
    @cmd('abbrev-list')
    def listAbbrevs(self, event: LeoKeyEvent = None) -> None:
        """List all abbreviations."""
        d = self.abbrevs
        if not d:
            return
        print('')
        g.es_print(f"Abbreviations for {self.c.shortFileName()}...")
        for name, value in sorted(d.items()):
            s, _tag = value
            s = s.replace('\n', '\\n')
            tail = s.removesuffix('\\n')
            print(f"{name:>15} {g.truncate(tail, 90)}")

    # @+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
    @cmd('toggle-abbrev-mode')
    def toggleAbbrevMode(self, event: LeoKeyEvent = None) -> None:
        """Toggle abbreviation mode."""
        k = self.c.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + ('on' if k.abbrevOn else 'off'))

    # @-others


# @-others
# @-leo
