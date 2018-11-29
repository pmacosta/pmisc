# lintshell.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,E1129,R0201,R0903,R0914,W0611,W1113

# Standard library import
from __future__ import print_function
import abc
import os
import platform
import re
import subprocess
import sys
import tempfile
import textwrap
import types
import xml.etree.ElementTree as ET

# PyPI imports
import decorator
import docutils.nodes
import docutils.utils.error_reporting
import sphinx.errors
import sphinx.util.logging
from sphinx.builders import Builder
from sphinx.locale import __


###
# Global variables
###
LOGGER = sphinx.util.logging.getLogger(__name__)


###
# Functions
###
def _tostr(line):
    if isinstance(line, str):
        return line
    if sys.hexversion > 0x03000000:
        return line.decode()
    return line.encode()


def _which(name):
    """Search PATH for executable files with the given name."""
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    for pdir in os.environ.get("PATH", "").split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            return fname
    return ""


###
# Classes
###
class LintShellNotFound(sphinx.errors.SphinxError):  # noqa: D101
    category = __("LintShell failed")


class LintShellBuilder(abc.ABC, Builder):
    """Validate shell code in documents."""

    name = ""

    @property
    @abc.abstractmethod
    def dialects(self):
        """Return shell dialects supported."""
        pass

    @property
    @abc.abstractmethod
    def prompt(self):
        """Return prompt used to denote command line start."""
        pass

    def __init__(self, app):  # noqa
        super(LintShellBuilder, self).__init__(app)
        self.stderr = docutils.utils.error_reporting.ErrorOutput()
        self.srclines = None
        self.tabwidth = None
        self.source = None
        self.shell = None
        self.nodes = []

    def _get_block_indent(self, node):
        first_line = self.srclines[node.line + 1]
        return len(first_line) - len(first_line.lstrip())

    def _shell_nodes(self, doctree):
        regexp = re.compile("(.[^:]*)(?::docstring of (.*))*")
        for node in doctree.traverse(siblings=True, ascend=True):
            if (
                (node.tagname == "literal_block")
                and (node.attributes.get("language").lower() in self.dialects)
                and node.source
            ):
                self.shell = node.attributes.get("language").lower()
                self.source, func_abs_name = regexp.match(node.source).groups()
                self.source = os.path.abspath(self.source)
                if func_abs_name:
                    tokens = func_abs_name.split(".")
                    func_path, func_name = ".".join(tokens[:-1]), tokens[-1]
                    func_obj = __import__(func_path).__dict__[func_name]
                    node.line = func_obj.__code__.co_firstlineno + node.line + 1
                self._read_source_file()
                yield node

    def _read_source_file(self):
        self.srclines = []
        node = docutils.nodes.Node()
        with open(self.source, "r") as obj:
            for line in obj.readlines():
                node.rawsource = line
                self.srclines.append(_tostr(node.rawsource.expandtabs(self.tabwidth)))

    def get_target_uri(self, docname, typ=None):  # noqa
        # Abstract method that needs to be overridden, not germane to current builder
        return ""

    def get_outdated_docs(self):  # noqa
        # Abstract method that needs to be overridden, not germane to current builder
        return self.env.found_docs

    def prepare_writing(self, docnames):  # noqa
        # Abstract method that needs to be overridden, not germane to current builder
        return

    def write_doc(self, docname, doctree):
        """Check shell nodes."""
        exe = self.linter_cmd("")[0]
        if not _which(exe):
            raise LintShellNotFound("Shell linter executable not found: " + exe)
        self.tabwidth = doctree.settings.tab_width
        rc = 0
        header = None
        for node in self._shell_nodes(doctree):
            block_indent = self._get_block_indent(node)
            errors = self._is_valid_shell(node, block_indent)
            if errors:
                if (not header) or (header and (header != self.source)):
                    header = self.source
                    LOGGER.info(self.source)
                for error in errors:
                    LOGGER.info(error)
                rc = 1
        self.app.statuscode = rc

    def _is_valid_shell(self, node, block_indent):
        # Create a shell script with all output lines commented out to be able
        # to report line offsets correctly
        value = node.astext()
        lineno_offset = node.line
        lines = []
        cont = False
        lmin = 0
        value = _tostr(value)
        for line in value.split(os.linesep):
            if line.strip().startswith(self.prompt) or cont:
                lines.append(line[1:])
                lmin = len(line[1:]) - len(line[1:].lstrip())
            else:
                lines.append((" " * lmin) + "# Output line")
            cont = line.strip().endswith("\\")
        ilines = os.linesep.join(lines)
        olines = textwrap.dedent(ilines)
        colno_offset = (
            len(ilines.split(os.linesep)[0])
            - len(olines.split(os.linesep)[0])
            + block_indent
            + 2
        )
        lines = "#!/bin/" + self.shell + os.linesep + olines
        with TmpFile(lambda x: x.write(lines)) as fname:
            obj = subprocess.Popen(
                self.linter_cmd(fname), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            lines, _ = obj.communicate()
            lines = [line for line in _tostr(lines).split(os.linesep)]
        return self.parse_linter_output(fname, lines, lineno_offset, colno_offset)

    @abc.abstractmethod
    def linter_cmd(self, fname):
        """Return command that runs the linter."""
        return []

    @abc.abstractmethod
    def parse_linter_output(self, fname, lines, lineno_offset, colno_offset):
        """Extract linter error information from STDOUT."""
        return []


class TmpFile(object):
    """Create and manage temporary file."""

    def __init__(self, fpointer=None, *args, **kwargs):  # noqa
        if (
            fpointer
            and (not isinstance(fpointer, types.FunctionType))
            and (not isinstance(fpointer, types.LambdaType))
        ):
            raise RuntimeError("Argument `fpointer` is not valid")
        self._fname = None
        self._fpointer = fpointer
        self._args = args
        self._kwargs = kwargs

    def __enter__(self):  # noqa
        fdesc, fname = tempfile.mkstemp()
        # fdesc is an OS-level file descriptor, see problems if this
        # is not properly closed in this post:
        # https://www.logilab.org/blogentry/17873
        os.close(fdesc)
        if platform.system().lower() == "windows":  # pragma: no cover
            fname = fname.replace(os.sep, "/")
        self._fname = fname
        if self._fpointer:
            with open(self._fname, "w") as fobj:
                self._fpointer(fobj, *self._args, **self._kwargs)
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa
        with ignored(OSError):
            os.remove(self._fname)
        return not exc_type is not None


@decorator.contextmanager
def ignored(*exceptions):
    """Ignore given exceptions."""
    try:
        yield
    except exceptions:
        pass
