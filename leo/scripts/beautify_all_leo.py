# @+leo-ver=5-thin
# @+node:ekr.20240323050520.1: * @file ../scripts/beautify_all_leo.py
# @@language python

"""
beautify_all_leo.py: Beautify (almost) all of Leo's files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's beautify-all-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.beautify_all_leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = f"--config {leo_editor_dir}{os.sep}pyproject.toml"
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

# Use -m so that __name__ == '__main__'.
command_head = f"{python} -m ruff format {args}"
for command in [
    # f"{command_head} leo{os.sep}commands",
    f"{command_head} leo{os.sep}core",
    # f"{command_head} leo{os.sep}external",
    # f"{command_head} leo{os.sep}plugins",
    f"{command_head} leo{os.sep}scripts",
    # f"{command_head} leo{os.sep}modes",
    # f"{command_head} leo{os.sep}unittests{os.sep}commands",
    # f"{command_head} leo{os.sep}unittests{os.sep}plugins",
    # f"{command_head} leo{os.sep}unittests{os.sep}misc_tests",
]:
    subprocess.Popen(command, shell=True).communicate()
# @-leo
