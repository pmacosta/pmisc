# shellcheck.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0914

# Standard library import
import json

# Intra-package imports
from lintshell import LintShellBuilder


###
# Functions
###
def _errors(stdout):
    for error in json.loads(stdout):
        code = error["code"]
        desc = error["message"]
        line = error["line"]
        col = error["column"]
        yield line, col, code, desc


###
# Classes
###
class ShellcheckBuilder(LintShellBuilder):
    """Validate shell code in documents using shellcheck."""

    name = "shellcheck"

    def __init__(self, app):  # noqa
        super(ShellcheckBuilder, self).__init__(app)
        self._dialects = app.config.shellcheck_dialects
        self._exe = app.config.shellcheck_executable
        self._prompt = app.config.shellcheck_prompt
        self._nodes = []

    @property
    def dialects(self):
        """Return shell dialects supported by linter."""
        return self._dialects

    @property
    def prompt(self):
        """Return character used to denote shell command prompt."""
        return self._prompt

    def cmd(self, fname):
        """Return command that runs the linter."""
        return [
            self._exe,
            "--shell=" + self.dialect,
            "--color=never",
            "--format=json",
            fname,
        ]

    def parse_linter_output(self, stdout, line_offset, col_offset):
        """Extract shellcheck error information from STDOUT."""
        ret = []
        for line, col, code, desc in _errors(stdout):
            info = [self.source, line + line_offset, col + col_offset, code, desc]
            if info not in self._nodes:
                self._nodes.append(info)
                ret.append("Line {0}, column {1} [{2}]: {3}".format(*info[1:]))
        return ret


###
# Registration
###
def setup(app):
    """Register custom builder."""
    app.add_builder(ShellcheckBuilder)
    app.add_config_value("shellcheck_dialects", ("sh", "bash", "dash", "ksh"), "env")
    app.add_config_value("shellcheck_executable", "shellcheck", "env")
    app.add_config_value("shellcheck_prompt", "$", "env")