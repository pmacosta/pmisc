# shellcheck.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0914

# Standard library import
import re

# PyPI imports
from lintshell import LintShellBuilder


###
# Classes
###
class ShellcheckBuilder(LintShellBuilder):
    """Validate shell code in documents using shellcheck."""

    name = "shellcheck"

    def __init__(self, app):  # noqa
        super(ShellcheckBuilder, self).__init__(app)
        self._exe = app.config.shellcheck_executable
        self._dialects = app.config.shellcheck_dialects
        self._prompt = app.config.shellcheck_prompt

    def _get_dialects(self):
        return self._dialects

    def _get_prompt(self):
        return self._prompt

    def linter_cmd(self, fname):
        """Return command that runs the linter."""
        return [self._exe, fname]

    def parse_linter_output(self, fname, lines, lineno_offset, colno_offset):
        """Extract shellcheck error information from STDOUT."""
        error_start = re.compile(r"In {0} line (\d+):\s*".format(fname))
        error_desc = re.compile(r"(\s*)\^--\s*(.*):\s*(.*)")
        in_error = False
        lines = [line for line in lines if line.strip()]
        ret = []
        error = bool(lines)
        for line in lines:
            if not in_error:
                match = (not in_error) and error_start.match(line)
                if match:
                    lineno = int(match.groups()[0]) + lineno_offset
                    in_error = True
            else:
                match = error_desc.match(line)
                if match:
                    error = False
                    indent, code, desc = match.groups()
                    code, desc = code.strip(), desc.strip()
                    colno = len(indent) + colno_offset
                    info = (self.source, lineno, colno, code, desc)
                    if info not in self.nodes:
                        self.nodes.append(info)
                        ret.append(
                            "Line {0}, column {1} [{2}]: {3}".format(
                                lineno, colno, code, desc
                            )
                        )
        if error:
            raise RuntimeError(self.name + " output could not be correctly parsed")
        return ret

    dialects = property(_get_dialects)
    prompt = property(_get_prompt)


def setup(app):
    """Register custom builder."""
    app.add_builder(ShellcheckBuilder)
    app.add_config_value("shellcheck_executable", "shellcheck", "env")
    app.add_config_value("shellcheck_dialects", ("sh", "bash", "dash", "ksh"), "env")
    app.add_config_value("shellcheck_prompt", "$", "env")
    return
