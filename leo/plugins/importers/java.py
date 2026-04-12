# @+leo-ver=5-thin
# @+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
"""The @auto importer for the java language."""

from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

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
        # protected Autotest(InstallerCommandLine commandLine) throws IOException, DriverException {
        
        ('class',     re.compile(r'^.*?\bclass\s+(\w+)')),
        ('interface', re.compile(r'^\s*interface\s+(\w*)\s*{')),
        
        # private/protected/public classes...
        ('private',   re.compile(r'^\s*private\s+(\w+.*?)\(.*?\)\s*((throws|implements).*?)?{')),
        ('protected', re.compile(r'^\s*protected\s+(\w+.*?)\(.*?\)\s*((throws|implements).*?)?{')),
        ('public',    re.compile(r'^\s*public\s+(\w+.*?)\(.*?\)\s*(t(throws|implements).*?)?{')),
        
        # private/protected/public functions...
        ('private',   re.compile(r'^\s*private\s+(\w+.*?)\(.*?\)\s*{')),
        ('protected', re.compile(r'^\s*protected\s+(\w+.*?)\(.*?\)\s*{')),
        ('public',    re.compile(r'^\s*public\s+(\w+.*?)\(.*?\)\s*{')),
    )  # fmt: skip

    # @-<< Java_Importer: block_patterns >>


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
