# @+leo-ver=5-thin
# @+node:ekr.20260512145309.1: * @file ../unittests/commands/test_leoAbbrev.py
"""Tests of leoAbbrev.py"""

from leo.core import leoGlobals as g
from leo.core.leoGui import LeoKeyEvent
from leo.core.leoTest2 import LeoUnitTest

assert g


# @+others
# @+node:ekr.20260512145550.104: ** class TestAbbrev (LeoUnitTest)
class TestAbbrev(LeoUnitTest):
    # @+others
    # @+node:ekr.20260512150121.1: *3* TestAbbrev.test_simple_abbreviations
    def test_simple_abbreviations(self):

        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        x = c.abbrevCommands
        x.abbrevs = {}
        x.next_placeholder = ',,'
        definitions = (
            'ex;;=!',
            'fmt;;=  # fmt: skip',
        )  # fmt: skip\n'
        for definition in definitions:
            x.addAbbrevHelper(definition)
        # g.printObj(x.abbrevs)
        table = (
            ('ex;',         '!'),
            ('whateverex;', 'whatever!'),
            ('fmt;',        '  # fmt: skip'),
            (')fmt;',       ')  # fmt: skip'),  # rust format will alter this.
        )  # fmt: skip

        def test(results, expected) -> None:
            assert results == expected, f"expected: {expected!r} got: {results!r}"

        for contents, expected in table:
            p.b = contents
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.b, expected)
            test(w.getAllText(), expected)

    # @+node:ekr.20260512164351.1: *3* TestAbbrev.test_multiline_abbreviations
    def test_multiline_abbreviations(self):

        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        x = c.abbrevCommands
        x.abbrevs = {}
        x.next_placeholder = ',,'
        # details;;=<details><summary><b>Title</b></summary>
        # \:<br>
        # \:
        # \:</details>
        # This is the definition munged by c.config.getData.
        definition = 'details;;=<details><summary><b>Title</b></summary>\n<br>\n\n</details>'
        expected = (
            '<details><summary><b>Title</b></summary>\n'
            '<br>\n'
            '\n'
            '</details>'  # No trailing newline.
        )  # fmt: skip
        x.addAbbrevHelper(definition)
        table = (
            ('details;', expected),
        )  # fmt: skip

        def test(results, expected) -> None:
            assert results == expected, f"\nexpected: {expected!r}\n     got: {results!r}"

        for contents, expected in table:
            p.b = contents
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.b, expected)
            test(w.getAllText(), expected)

    # @-others


# @-others
# @-leo
