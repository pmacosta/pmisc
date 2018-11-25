# shellcheck.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,E1129,R0201,R0903,R0914,W0611,W1113

# Standard library import
from __future__ import print_function
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
    if sys.hexversion > 0x03000000:
        if isinstance(line, str):
            return line
        return line.decode()
    return line.encode()


def _which(name):
    """Search PATH for executable files with the given name."""
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    result = []
    path = os.environ.get("PATH", None)
    if path is None:
        return []
    for pdir in os.environ.get("PATH", "").split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0] if result else None


###
# Classes
###
class ShellCheckNotFound(sphinx.errors.SphinxError):  # noqa: D101
    category = __("ShellCheck failed")


class ShellCheckBuilder(Builder):
    """Validate shell code in documents using shellcheck."""

    name = "shellcheck"
    dialects = ('sh', 'bash', 'dash', 'ksh')

    def __init__(self, app):  # noqa
        super(ShellCheckBuilder, self).__init__(app)
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
        if not _which("shellcheck"):
            raise ShellCheckNotFound("shellcheck not found")
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
        prompt = "$"
        lines = []
        cont = False
        lmin = 0
        value = _tostr(value)
        for line in value.split(os.linesep):
            if line.strip().startswith(prompt) or cont:
                lines.append(line[1:])
                lmin = len(line[1:]) - len(line[1:].lstrip())
            else:
                lines.append((" " * lmin) + "# Output line")
            cont = line.strip().endswith("\\")
        ilines = os.linesep.join(lines)
        olines = textwrap.dedent(ilines)
        colno_offset = len(ilines.split(os.linesep)[0]) - len(
            olines.split(os.linesep)[0]
        )
        lines = "#!/bin/" + self.shell + os.linesep + olines
        with TmpFile(lambda x: x.write(lines)) as fname:
            obj = subprocess.Popen(
                ["shellcheck", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            lines, _ = obj.communicate()
            lines = [line for line in _tostr(lines).split(os.linesep)]
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
                    colno = len(indent) + colno_offset + block_indent + 2
                    info = (self.source, lineno, colno, code, desc)
                    if info not in self.nodes:
                        self.nodes.append(info)
                        ret.append(
                            "Line {0}, column {1} [{2}]: {3}".format(
                                lineno, colno, code, desc
                            )
                        )
        if error:
            raise RuntimeError("shellcheck output could not be correctly parsed")
        return ret


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


def setup(app):
    LOGGER.info("Initializing Shell shell checker")
    app.add_builder(ShellCheckBuilder)
    return
