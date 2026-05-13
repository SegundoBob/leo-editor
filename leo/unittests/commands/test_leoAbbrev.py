# @+leo-ver=5-thin
# @+node:ekr.20260512145309.1: * @file ../unittests/commands/test_leoAbbrev.py
"""Tests of leoAbbrev.py"""
# pylint: disable=no-member

import re
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
        x = c.abbrevCommands

        # Set the ivars by hand insead of with settings.
        x.abbrevs = {}
        x.next_placeholder = ',,'
        c.abbrev_subst_end = '}|}'
        c.abbrev_subst_start = '{|{'
        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {}}
        c.abbrev_place_start = '<|'
        c.abbrev_place_end = '|>'

        definitions = (
            'ex;;=!',
            'fmt;;=  # fmt: skip',
        )  # fmt: skip\n'
        for definition in definitions:
            x.addAbbrevHelper(definition)

        table = (
            ('ex;',         '!'),
            ('whateverex;', 'whatever!'),
            ('fmt;',        '  # fmt: skip'),
            (')fmt;',       ')  # fmt: skip'),
        )  # fmt: skip

        def test(results, expected) -> None:
            assert results == expected, f"expected: {expected!r} got: {results!r}"

        # Test body.
        w = c.frame.body.wrapper
        for contents, expected in table:
            p.b = contents
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.b, expected)
            test(w.getAllText(), expected)

        # Test headlines.
        c.editHeadline()
        w = c.headline_wrapper(p)
        for contents, expected in table:
            p.h = contents
            w.setAllText(contents)
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.h, expected)
            test(w.getAllText(), expected)

    # @+node:ekr.20260512164351.1: *3* TestAbbrev.test_multiline_abbreviations
    def test_multiline_abbreviations(self):

        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        x = c.abbrevCommands
        x.abbrevs = {}
        x.next_placeholder = ',,'

        # These must be the definition munged by c.config.getData.
        definitions = (
            'details;;=<details><summary><b>Title</b></summary>\n<br>\n\n</details>',
        )  # fmt: skip

        for definition in definitions:
            x.addAbbrevHelper(definition)

        def test(results, expected) -> None:
            assert results == expected, f"\nexpected: {expected!r}\n     got: {results!r}"

        for definition in definitions:
            i = definition.find(';=')
            contents = definition[:i]
            expected = definition[i + 2 :]
            p.b = contents
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.b, expected)
            test(w.getAllText(), expected)

    # @+node:ekr.20260512173657.1: *3* TestAbbrev.test_scripting_abbreviations
    def test_scripting_abbreviations(self):

        import time

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}

        # Init the ivars.
        x.enable = True
        x.next_placeholder = ',,'
        c.abbrev_subst_end = '}|}'
        c.abbrev_subst_start = '{|{'
        c.abbrev_subst_env = {'c': c, 'g': g, 'time': time, '_values': {}}

        # These must be the definition munged by c.config.getData.
        definitions = (
            'date;;={|{x=time.strftime("%Y/%m/%d")}|}',
        )  # fmt: skip

        for definition in definitions:
            x.addAbbrevHelper(definition)

        pattern = r'[0-9]{4}/[0-9]{2}/[0-9]{2}'

        def test(results: str) -> None:
            assert re.match(pattern, results), f"\nresults: {results!r} regex: {pattern!r}"

        # Test the body.
        w = c.frame.body.wrapper
        for definition in definitions:
            i = definition.find(';=')
            p.b = contents = definition[:i]
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.b)
            test(w.getAllText())

        # Test headlines.
        c.editHeadline()
        w = c.headline_wrapper(p)
        for definition in definitions:
            i = definition.find(';=')
            p.h = contents = definition[:i]
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(p.h)
            test(w.getAllText())

    # @-others


# @-others
# @-leo
