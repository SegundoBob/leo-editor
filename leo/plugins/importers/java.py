# @+leo-ver=5-thin
# @+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
"""The @auto importer for the java language."""

from __future__ import annotations
import re
from typing import TYPE_CHECKING
import leo.core.leoGlobals as g
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position


# @+others
# @+node:ekr.20161126161824.2: ** class Java_Importer(Importer)
class Java_Importer(Importer):
    """The importer for the java language."""

    language = 'java'

    # @+<< Java_Importer: block_patterns >>
    # @+node:ekr.20260412045240.1: *3* << Java_Importer: block_patterns >>
    block_patterns: tuple = (

        # #4471: Patterns must include a known prefix to avoid matching compound statements.
        # ('interface', re.compile(r'^\s*interface\s+(\w+.*?)\s*((implements|throws).*?)?{')),
        # ('private',   re.compile(r'^\s*private\s+(\w+.*?)\(.*?\)\s*((implements|throws).*?)?{')),
        # ('protected', re.compile(r'^\s*protected\s+(\w+.*?)\s*\(.*?\)\s*((implements|throws).*?)?{')),
        # ('public',    re.compile(r'^\s*public\s+(\w+.*?)\(.*?\)\s*((implements|throws).*?)?{')),
        # ('static',    re.compile(r'^\s*static\s+(\w+.*?)\(.*?\)\s*((implements|throws).*?)?{')),
        
        ('',          re.compile(r'^\s*(.*?\bclass\s+\w+)')),
        ('',          re.compile(r'^\s*(\w+.*?)\(.*?\)\s*((implements|throws).*?)?{')),

    )  # fmt: skip
    # @-<< Java_Importer: block_patterns >>

    # @+others
    # @+node:ekr.20260415021624.1: *3* java_i.postprocess
    def postprocess(self, parent: Position) -> None:
        """Python_Importer.postprocess."""

        # Base-class method.
        self.move_blank_lines(parent)

        # Subclass methods...
        self.move_module_preamble(parent)

    # @+node:ekr.20260415021537.1: *3* java_i.move_module_preamble
    def move_module_preamble(self, parent: Position) -> None:
        """Move the preamble lines from the parent's first child to the start of parent.b."""

        child1 = parent.firstChild()
        if not child1:
            return

        def match(s: str) -> bool:
            for kind, pattern in self.block_patterns:
                if pattern.match(s):
                    return True
            return False

        # The preamble is everything up to the line that first matches a block
        lines = g.splitLines(child1.b)
        for i, line in enumerate(lines):
            if match(line):
                # Adjust the bodies.
                preamble_s = ''.join(lines[:i])
                parent.b = preamble_s + parent.b
                child1.b = child1.b.replace(preamble_s, '')
                return

    # @+node:ekr.20260415023102.1: *3* java_i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Java_Importer.find_blocks.

        Same as Importer.find_blocks, but disallows matches of compound statements.

        Using self.block_patterns and self.guide_lines, return a list of all
        blocks in the given range of *guide* lines.

        **Important**: An @others directive will refer to the returned blocks,
                       so there must be *no gaps* between blocks!
        """
        min_size = self.minimum_block_size
        i, prev_i, results = i1, i1, []
        while i < i2:
            progress = i
            s = self.guide_lines[i]
            i += 1
            # Assume that no pattern matches a compound statement.
            for kind, pattern in self.block_patterns:
                if m := pattern.match(s):
                    # cython may include trailing whitespace.
                    name = m.group(1).strip()
                    if name in ('else', 'for', 'if', 'switch', 'while'):
                        continue
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    # Don't generate small blocks.
                    if min_size == 0 or end - prev_i > min_size:
                        block = Block(
                            kind, name, start=prev_i, start_body=i, end=end, lines=self.lines
                        )
                        results.append(block)
                        i = prev_i = end
                    else:
                        i = end
                    break
            assert i > progress, g.callers()
        # g.printObj(results, tag=f"{g.my_name()} {i1} {i2}")
        return results

    # @-others


# @-others


def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for java."""
    Java_Importer(c).import_from_string(parent, s)


importer_dict = {
    'extensions': ['.java'],
    'func': do_import,
}
# @@language python
# @@tabwidth -4
# @-leo
