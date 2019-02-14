# rst.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0304,C0305

# Standard library imports
import os
import platform
import re
import subprocess
import sys
import uuid


###
# Global variables
###
LDELIM = "%" if platform.system().lower() == "windows" else "${"
RDELIM = "%" if platform.system().lower() == "windows" else "}"


###
# Functions
###
def _homogenize_linesep(line):
    """Enforce line separators to be the right one depending on platform."""
    token = str(uuid.uuid4())
    line = line.replace(os.linesep, token).replace("\n", "").replace("\r", "")
    return line.replace(token, os.linesep)


def _proc_token(spec, mlines):
    """Process line range tokens."""
    spec = spec.strip().replace(" ", "")
    regexp = re.compile(r".*[^0123456789\-,]+.*")
    tokens = spec.split(",")
    cond = any([not item for item in tokens])
    if ("--" in spec) or ("-," in spec) or (",-" in spec) or cond or regexp.match(spec):
        raise RuntimeError("Argument `lrange` is not valid")
    lines = []
    for token in tokens:
        if token.count("-") > 1:
            raise RuntimeError("Argument `lrange` is not valid")
        if "-" in token:
            subtokens = token.split("-")
            lmin, lmax = (
                int(subtokens[0]),
                int(subtokens[1]) if subtokens[1] else mlines,
            )
            for num in range(lmin, lmax + 1):
                lines.append(num)
        else:
            lines.append(int(token))
    if lines != sorted(lines):
        raise RuntimeError("Argument `lrange` is not valid")
    return lines


def incfile(fname, fpointer, lrange=None, sdir=None):
    r"""
    Return a Python source file formatted in reStructuredText.

    .. role:: bash(code)
        :language: bash

    :param fname: File name, relative to environment variable
                  :bash:`PKG_DOC_DIR`
    :type  fname: string

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                      other functions can be used for debugging
    :type  fpointer: function object

    :param lrange: Line range to include, similar to Sphinx
                   `literalinclude <http://www.sphinx-doc.org/en/master/usage
                   /restructuredtext/directives.html
                   #directive-literalinclude>`_ directive
    :type  lrange: string

    :param sdir: Source file directory. If None the :bash:`PKG_DOC_DIR`
                 environment variable is used if it is defined, otherwise
                 the directory where the module is located is used
    :type  sdir: string

    For example:

    .. code-block:: python

        def func():
            \"\"\"
            This is a docstring. This file shows how to use it:

            .. =[=cog
            .. import docs.support.incfile
            .. docs.support.incfile.incfile('func_example.py', cog.out)
            .. =]=
            .. code-block:: python

                # func_example.py
                if __name__ == '__main__':
                    func()

            .. =[=end=]=
            \"\"\"
            return 'This is func output'
    """
    # pylint: disable=R0914
    # Read file
    file_dir = (
        sdir
        if sdir
        else os.environ.get("PKG_DOC_DIR", os.path.abspath(os.path.dirname(__file__)))
    )
    fname = os.path.join(file_dir, fname)
    with open(fname, "r") as fobj:
        lines = fobj.readlines()
    # Eliminate spurious carriage returns in Microsoft Windows
    lines = [_homogenize_linesep(line) for line in lines]
    # Parse line specification
    inc_lines = (
        _proc_token(lrange, len(lines)) if lrange else list(range(1, len(lines) + 1))
    )
    # Produce output
    fpointer(".. code-block:: python" + os.linesep)
    fpointer(os.linesep)
    for num, line in enumerate(lines):
        if num + 1 in inc_lines:
            fpointer(
                "    " + line.replace("\t", "    ").rstrip() + os.linesep
                if line.strip()
                else os.linesep
            )
    fpointer(os.linesep)


def ste(command, nindent, mdir, fpointer):
    """
    Print STDOUT of a shell command formatted in reStructuredText.

    This is a simplified version of :py:func:`pmisc.term_echo`.

    :param command: Shell command, relative to **mdir**
    :type  command: string

    :param nindent: Indentation level
    :type  nindent: integer

    :param mdir: Module directory
    :type  mdir: string

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                     :code:`print` or other functions can be used for
                     debugging
    :type  fpointer: function object

    For example::

        .. This is a reStructuredText file snippet
        .. [[[cog
        .. import os, sys
        .. from docs.support.term_echo import term_echo
        .. file_name = sys.modules['docs.support.term_echo'].__file__
        .. mdir = os.path.realpath(
        ..     os.path.dirname(
        ..         os.path.dirname(os.path.dirname(file_name))
        ..     )
        .. )
        .. [[[cog ste('build_docs.py -h', 0, mdir, cog.out) ]]]

        .. code-block:: bash

        $ ${PKG_BIN_DIR}/build_docs.py -h
        usage: build_docs.py [-h] [-d DIRECTORY] [-n NUM_CPUS]
        ...

        .. ]]]

    """
    term_echo(
        LDELIM
        + "PKG_BIN_DIR"
        + RDELIM
        + "{sep}{cmd}".format(sep=os.path.sep, cmd=command),
        nindent,
        {"PKG_BIN_DIR": mdir},
        fpointer,
    )


def term_echo(command, nindent=0, env=None, fpointer=None, cols=60):
    """
    Print STDOUT of a shell command formatted in reStructuredText.

    .. role:: bash(code)
        :language: bash

    :param command: Shell command
    :type  command: string

    :param nindent: Indentation level
    :type  nindent: integer

    :param env: Environment variable replacement dictionary. The
                command is pre-processed and any environment variable
                represented in the full notation (:bash:`${...}` in Linux and
                OS X or :bash:`%...%` in Windows) is replaced. The dictionary
                key is the environment variable name and the dictionary value
                is the replacement value. For example, if **command** is
                :code:`'${PYTHON_CMD} -m "x=5"'` and **env** is
                :code:`{'PYTHON_CMD':'python3'}` the actual command issued
                is :code:`'python3 -m "x=5"'`
    :type  env: dictionary

    :param fpointer: Output function pointer. Normally is :code:`cog.out` but
                     :code:`print` or other functions can be used for
                     debugging
    :type  fpointer: function object

    :param cols: Number of columns of output
    :type  cols: integer
    """
    # pylint: disable=R0204
    # Set argparse width so that output does not need horizontal scroll
    # bar in narrow windows or displays
    os.environ["COLUMNS"] = str(cols)
    command_int = command
    if env:
        for var, repl in env.items():
            command_int = command_int.replace(LDELIM + var + RDELIM, repl)
    tokens = command_int.split(" ")
    # Add Python interpreter executable for Python scripts on Windows since
    # the shebang does not work
    if (platform.system().lower() == "windows") and (
        tokens[0].endswith(".py")
    ):  # pragma: no cover
        tokens = [sys.executable] + tokens
    proc = subprocess.Popen(tokens, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = proc.communicate()[0]
    if sys.hexversion >= 0x03000000:  # pragma: no cover
        stdout = stdout.decode("utf-8")
    stdout = stdout.split("\n")
    indent = nindent * " "
    fpointer(os.linesep)
    fpointer("{0}.. code-block:: bash{1}".format(indent, os.linesep))
    fpointer(os.linesep)
    fpointer("{0}    $ {1}{2}".format(indent, command, os.linesep))
    for line in stdout:
        line = _homogenize_linesep(line)
        if line.strip():
            fpointer(indent + "    " + line.replace("\t", "    ") + os.linesep)
        else:
            fpointer(os.linesep)
