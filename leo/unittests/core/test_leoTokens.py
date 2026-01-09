# @+leo-ver=5-thin
# @+node:ekr.20240105151507.1: * @file ../unittests/core/test_leoTokens.py
"""Tests of leoTokens.py"""
# @+<< test_leoTokens imports >>
# @+node:ekr.20240105151507.2: ** << test_leoTokens imports >>
import os
import sys
import textwrap
import unittest

# import warnings
# warnings.simplefilter("ignore")
# try:
    # # Suppress a warning about imp being deprecated.
    # with warnings.catch_warnings():
        # import black
# except Exception:  # pragma: no cover
    # black = None

from leo.core import leoGlobals as g

# Classes to test.
from leo.core.leoTokens import InputToken, Tokenizer, TokenBasedOrange

# Utility functions.
from leo.core.leoTokens import dump_contents, dump_tokens, input_tokens_to_string
# @-<< test_leoTokens imports >>
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)

# @+others
# @+node:ekr.20240105153420.2: ** class BaseTest (TestCase)
# Do *not* use LeoUnitTest as the base class.
# Doing so slows downt testing considerably.

class BaseTest(unittest.TestCase):
    """
    The base class of all tests of leoTokens.py.

    This class contains only helpers.
    """
    debug_list: list[str] = []

    def setUp(self) -> None:
        g.unitTesting = True

    # @+others
    # @+node:ekr.20240105153420.13: *3* BaseTest.beautify
    def beautify(self,
        contents,
        tokens,
        filename=None,
        max_join_line_length=None,
        max_split_line_length=None,
    ):
        """BaseTest.beautify."""
        if not contents:
            return ''  # pragma: no cover
        if not filename:
            filename = g.callers(2).split(',')[0]

        orange = TokenBasedOrange()
        result_s = orange.beautify(contents, filename, tokens)
        self.output_list = orange.output_list
        return result_s
    # @+node:ekr.20240105153420.4: *3* BaseTest.check_roundtrip
    def check_roundtrip(self, contents, *, debug_list: list[str] = None):
        """Check that the tokenizer round-trips the given contents."""
        # Several unit tests call this method.

        contents, tokens = self.make_data(contents, debug_list=debug_list)
        results = input_tokens_to_string(tokens)
        self.assertEqual(contents, results)
    # @+node:ekr.20240105153425.44: *3* BaseTest.make_data (test_leoTokens.py)
    def make_data(self,
        contents: str,
        *,
        description: str = None,
        debug_list: str = None,
    ) -> tuple[str, list[InputToken]]:  # pragma: no cover
        """
        BaseTest.make_data. Prepare the data for one unit test:
        - Regularize the contents:
          contents = textwrap.dedent(contents).strip() + '\n'
        - Tokenize the contents using the Tokenizer class in leoTokens.py.
        - Dump the contents or tokens per the debug_list kwarg.
        - Return (contents, tokens)
        """
        assert contents.strip(), g.callers()

        # Set debug flags and counts.
        self.debug_list = debug_list or []
        self.trace_token_method = False

        # Check the debug_list.
        valid = ('contents', 'debug', 'tokens')
        for z in self.debug_list:
            if z not in valid:
                g.trace('Ignoring debug_list value:', z)

        # Ensure all tests start with a non-blank line and end in exactly one newline.
        contents = textwrap.dedent(contents).strip() + '\n'

        # Create the tokens.
        tokens = Tokenizer().make_input_tokens(contents)
        if not tokens:
            self.fail('BaseTest.make_data:Tokenizer().make_input_tokens failed')

        # Dumps.
        if 'contents' in self.debug_list:
            dump_contents(contents)
        if 'tokens' in self.debug_list:
            dump_tokens(tokens)
        return contents, tokens
    # @+node:ekr.20240105153420.6: *3* BaseTest.make_file_data
    def make_file_data(self, filename: str) -> tuple[str, list[InputToken]]:
        """Return (contents, tokens, tree) from the given file."""
        directory = os.path.dirname(__file__)
        filename = g.finalize_join(directory, '..', '..', 'core', filename)
        assert os.path.exists(filename), repr(filename)
        contents = g.readFileIntoUnicodeString(filename)
        contents, tokens = self.make_data(contents, description=filename)
        return contents, tokens
    # @+node:ekr.20240205025458.1: *3* BaseTest.prep
    def prep(self, s: str) -> str:
        """
        Return the "prepped" version of s.

        This should eliminate the need for backslashes in tests.
        """
        return textwrap.dedent(s).strip() + '\n'
    # @-others
# @+node:ekr.20240105153425.2: ** class Optional_TestFiles (BaseTest)
class Optional_TestFiles(BaseTest):
    """
    Tests for the TokenOrderGenerator class that act on files.

    These are optional tests. They take a long time and are not needed
    for 100% coverage.

    All of these tests failed at one time.
    """
    # @+others
    # @+node:ekr.20240105153425.3: *3* TestFiles.test_leoApp
    def test_leoApp(self):

        self.make_file_data('leoApp.py')
    # @+node:ekr.20240105153425.4: *3* TestFiles.test_leoAst
    def test_leoAst(self):

        self.make_file_data('leoAst.py')
    # @+node:ekr.20240105153425.5: *3* TestFiles.test_leoDebugger
    def test_leoDebugger(self):

        self.make_file_data('leoDebugger.py')
    # @+node:ekr.20240105153425.6: *3* TestFiles.test_leoFind
    def test_leoFind(self):

        self.make_file_data('leoFind.py')
    # @+node:ekr.20240105153425.7: *3* TestFiles.test_leoGlobals
    def test_leoGlobals(self):

        self.make_file_data('leoGlobals.py')
    # @+node:ekr.20240105153425.8: *3* TestFiles.test_leoTips
    def test_leoTips(self):

        self.make_file_data('leoTips.py')
    # @+node:ekr.20240105153425.9: *3* TestFiles.test_runLeo
    def test_runLeo(self):

        self.make_file_data('runLeo.py')
    # @-others
# @+node:ekr.20240105153425.85: ** class TestTokens (BaseTest)
class TestTokens(BaseTest):
    """Unit tests for tokenizing."""

    # @+others
    # @+node:ekr.20240105153425.93: *3* TT.show_example_dump
    def show_example_dump(self):  # pragma: no cover

        # Will only be run when enabled explicitly.

        contents = """
    print('line 1')
    print('line 2')
    print('line 3')
    """
        contents, tokens = self.make_data(contents)
        dump_contents(contents)
        dump_tokens(tokens)
    # @+node:ekr.20240105153425.94: *3* TT.test_bs_nl_tokens
    def test_bs_nl_tokens(self):
        # Test https://bugs.python.org/issue38663.

        contents = """
    print \
        ('abc')
    """
        self.check_roundtrip(contents)
    # @+node:ekr.20240105153425.95: *3* TT.test_continuation_1
    def test_continuation_1(self):

        contents = """
    a = (3,4,
        5,6)
    y = [3, 4,
        5]
    z = {'a': 5,
        'b':15, 'c':True}
    x = len(y) + 5 - a[
        3] - a[2] + len(z) - z[
        'b']
    """
        self.check_roundtrip(contents)
    # @+node:ekr.20240105153425.96: *3* TT.test_continuation_2
    def test_continuation_2(self):
        # Backslash means line continuation, except for comments
        contents = (
            'x=1+\\\n    2'
            '# This is a comment\\\n    # This also'
        )
        self.check_roundtrip(contents)
    # @+node:ekr.20240105153425.97: *3* TT.test_continuation_3
    def test_continuation_3(self):

        contents = """
    # Comment \\\n
    x = 0
    """
        self.check_roundtrip(contents)
    # @+node:ekr.20240105153425.98: *3* TT.test_string_concatenation_1
    def test_string_concatentation_1(self):
        # Two *plain* string literals on the same line
        self.check_roundtrip("""'abc' 'xyz'""")
    # @+node:ekr.20240105153425.99: *3* TT.test_string_concatenation_2
    def test_string_concatentation_2(self):
        # f-string followed by plain string on the same line
        self.check_roundtrip("""f'abc' 'xyz'""")
    # @+node:ekr.20240105153425.100: *3* TT.test_string_concatenation_3
    def test_string_concatentation_3(self):
        # plain string followed by f-string on the same line
        self.check_roundtrip("""'abc' f'xyz'""")
    # @-others
# @-others
# @-leo
