# @+leo-ver=5-thin
# @+node:ekr.20260512145309.1: * @file ../unittests/commands/test_leoAbbrev.py
"""Tests of leoAbbrev.py"""
# pylint: disable=no-member

import re
import time
from leo.core import leoGlobals as g
from leo.core.leoGui import LeoKeyEvent
from leo.core.leoTest2 import LeoUnitTest

assert g


# @+others
# @+node:ekr.20260512145550.104: ** class TestAbbrev (LeoUnitTest)
class TestAbbrev(LeoUnitTest):
    # @+others
    # @+node:ekr.20260513064130.1: *3* TestAbbrev.test_active_comma
    def test_active_comma(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}

        # The definition as munged by c.config.getData.
        definition = 'details;;=<details><summary><b>Title</b></summary>\n<br>\n\n</details>'
        x.addAbbrevHelper(definition)

        if 1:  # Test 1: Test active double comma in the body
            w = c.frame.body.wrapper

            # Expand the definition.
            p.b = 'details;'
            event = LeoKeyEvent(c, char=';', w=w)
            x.expandAbbrev(event=event, stroke=None)

            # Type two commas.
            event = LeoKeyEvent(c, char=',', w=w)
            x.expandAbbrev(event=event, stroke=None)
            x.expandAbbrev(event=event, stroke=None)

            # Check the expansion (no comma) and the selection.
            s = w.getAllText()
            i = definition.find(';=')
            expected = definition[i + 2 :].replace('', '').replace('', '')
            assert s == expected, repr(s)  # Test 2.1
            s2 = w.getSelectedText()
            assert s2 == 'Title', repr(s2)  # Test. 2.2.

        # Test 2: Test active double comma in a headline.
        c.editHeadline()
        w = c.headline_wrapper(p)

        # Expand the definition.
        p.h = 'details;'
        event = LeoKeyEvent(c, char=';', w=w)
        x.expandAbbrev(event=event, stroke=None)
        ### g.trace(w.getAllText())
        ### breakpoint()  ###

        # Type two commas.
        event = LeoKeyEvent(c, char=',', w=w)
        x.expandAbbrev(event=event, stroke=None)
        g.trace(w.getAllText())
        x.expandAbbrev(event=event, stroke=None)

        # Check the expansion (no comma) and the selection.
        s = w.getAllText()
        i = definition.find(';=')
        expected = definition[i + 2 :].replace('\n', '')
        assert s == expected, repr(s)  # Test 2.1
        s2 = w.getSelectedText()
        assert s2 == 'Title', repr(s2)  # Test 2.2.

    # @+node:ekr.20260513023424.1: *3* TestAbbrev.test_bare_comma
    def test_bare_comma(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}

        # The definition as munged by c.config.getData.
        definition = 'details;;=<details><summary><b><|Title|></b></summary>\n<br>\n\n</details>'
        x.addAbbrevHelper(definition)

        # Test 1: Test bare double commas in the body.
        w = c.frame.body.wrapper
        p.b = ','
        event = LeoKeyEvent(c, char=',', w=w)
        x.expandAbbrev(event=event, stroke=None)
        s = w.getAllText()
        assert s == ',', repr(s)  # Test 1.

        # Test 2: Test bare double commas in headlines
        c.editHeadline()
        w = c.headline_wrapper(p)
        p.h = ','
        w.setAllText(',')
        event = LeoKeyEvent(c, char=',', w=w)
        x.expandAbbrev(event=event, stroke=None)
        s = w.getAllText()
        assert s == ',', repr(s)  # Test 2

    # @+node:ekr.20260512164351.1: *3* TestAbbrev.test_multiline_abbreviations
    def test_multiline_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}

        # These must be the definition munged by c.config.getData.
        definitions = (
            'details;;=<details><summary><b><|Title|></b></summary>\n<br>\n\n</details>',
        )  # fmt: skip

        for definition in definitions:
            x.addAbbrevHelper(definition)

        def test(results, expected) -> None:
            assert results == expected, (
                '\n'
                f"expected: {expected!r}\n"
                f"     got: {results!r}"
            )  # fmt: skip

        # Test bodies.
        if 0:
            w = c.frame.body.wrapper
            for definition in definitions:
                i = definition.find(';=')
                contents = definition[:i]
                expected = definition[i + 2 :].replace('<|', '').replace('|>', '')
                p.b = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test(p.b, expected)
                test(w.getAllText(), expected)

        # Test headlines
        if 1:
            for definition in definitions:
                c.editHeadline()
                w = c.headline_wrapper(p)
                ### g.trace(w)  ###
                i = definition.find(';=')
                contents = definition[:i]
                expected = (
                    definition[i + 2 :].replace('\\n', '').replace('<|', '').replace('|>', '')
                )
                p.h = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test(w.getAllText(), expected)
                c.endEditing()
                test(p.h, expected)

    # @+node:ekr.20210905064816.2: *3* TestAbbrev.test_next_place
    def test_next_place(self):
        c = self.c
        ac = c.abbrevCommands
        assert ac
        c.abbrev_place_start = '<|'
        c.abbrev_place_end = '|>'
        s = '123<| sub |>456'
        ok, new_s, i, j = ac.next_place(s)
        assert new_s == s.replace('<|', '').replace('|>', ''), new_s
        assert new_s[i:j] == ' sub ', new_s[i:j]

    # @+node:ekr.20260512173657.1: *3* TestAbbrev.test_scripting_abbreviations
    def test_scripting_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}
        x.scripting_enabled = True
        c.abbrev_subst_env['time'] = time

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
        for definition in definitions:
            c.editHeadline()
            w = c.headline_wrapper(p)
            i = definition.find(';=')
            p.h = contents = definition[:i]
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(w.getAllText())
            c.endEditing()
            test(p.h)

    # @+node:ekr.20260512150121.1: *3* TestAbbrev.test_simple_abbreviations
    def test_simple_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands

        # Set the ivars by hand insead of with settings.
        x.abbrevs = {}
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
        if 1:
            w = c.frame.body.wrapper
            for contents, expected in table:
                p.b = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test(p.b, expected)
                test(w.getAllText(), expected)

        # Test headlines.
        for contents, expected in table:
            c.editHeadline()
            w = c.headline_wrapper(p)
            p.h = contents
            w.setAllText(contents)
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(w.getAllText(), expected)
            c.endEditing()
            test(p.h, expected)

    # @-others


# @-others
# @-leo
