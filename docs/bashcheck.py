# bashcheck.py
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

# PyPI imports
import decorator
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
class BashCheckBuilder(Builder):
    """Validate bash code in documents using shellcheck."""

    name = "bashcheck"

    def __init__(self, app):  # noqa
        super(BashCheckBuilder, self).__init__(app)
        self.srclines = None
        self.tabwidth = None
        self.source = None

    def _get_file_name(self, doctree):
        regexp = re.compile(r"<document source=\"(.*)\">")
        match = regexp.match(doctree.pformat())
        if match:
            return match.groups()[0]
        raise RuntimeError("Source file could not be extracted")

    def _get_block_indent(self, node):
        first_line = self.srclines[node.line]
        return len(first_line)-len(first_line.lstrip())

    def _read_source_file(self, node):
        self.srclines = []
        tmp = node.rawsource
        with open(self.source, 'r') as obj:
            for line in obj.readlines():
                node.rawsource = line
                self.srclines.append(
                    _tostr(node.rawsource.expandtabs(self.tabwidth))
                )
        node.rawsource = tmp

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
        """Check bash nodes."""
        if not _which("shellcheck"):
            self.app.statuscode = 0
            return
        nodes = doctree.traverse()
        self.tabwidth = doctree.settings.tab_width
        self._get_file_name(doctree)
        self._read_source_file(nodes[0])
        rc = 0
        for node in nodes:
            if self._is_bash_literal_block(node):
                block_indent = self._get_block_indent(node)
                if not self._is_valid_bash(node.astext(), node.line, block_indent):
                    rc = 1
                    self._print_error(docname, node)
        self.app.statuscode = rc

    def _is_bash_literal_block(self, node):
        return (
            node.tagname == "literal_block"
            and node.attributes.get("language") == "bash"
        )

    def _is_valid_bash(self, value, lineno_offset, block_indent):
        # Create a shell script with all output lines commented out to be able
        # to report line offsets correctly
        prompt = "$"
        lines = []
        cont = False
        lmin = 0
        value = _tostr(value)
        for line in value.split(os.linesep):
            if line.strip().startswith(prompt) or cont:
                lines.append(line[1:])
                lmin = len(line[1:])-len(line[1:].lstrip())
            else:
                lines.append((" "*lmin)+"# Output line")
            cont = line.strip().endswith("\\")
        ilines = os.linesep.join(lines)
        olines = textwrap.dedent(ilines)
        colno_offset = len(ilines.split(os.linesep)[0])-len(olines.split(os.linesep)[0])
        lines = "#!/bin/bash"+os.linesep+olines
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
        if not lines:
            return True
        for line in lines:
            if not in_error:
                match = (not in_error) and error_start.match(line)
                if match:
                    lineno = int(match.groups()[0])+lineno_offset
                    in_error = True
            else:
                match = error_desc.match(line)
                if match:
                    indent, code, desc = match.groups()
                    code, desc = code.strip(), desc.strip()
                    colno = len(indent)+colno_offset+block_indent+2
                    print(
                        "Line {0}, column {1} [{2}]: {3}".format(
                            lineno, colno, code, desc
                        )
                    )
                    break
        else:
            raise RuntimeError("shellcheck output could not be correctly parsed")
        return False

    def _print_error(self, docname, node):
        LOGGER.warning("{0}, line {1}, {2}".format(docname, node.line, ""))


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
    LOGGER.info("Initializing Bash shell checker")
    app.add_builder(BashCheckBuilder)
    return
