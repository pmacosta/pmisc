# rst.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0304,C0305,C0411,R0205,R0914,W0108,W0212

# Standard library imports
from __future__ import print_function
import contextlib
import os
import platform
import shutil
import stat
import sys
import uuid

# PyPI imports
import pytest

# Intra-package imports
import pmisc
from pmisc import AI


###
# Global variables
###
LSEP = os.linesep
LDELIM = "%" if platform.system().lower() == "windows" else "${"
RDELIM = "%" if platform.system().lower() == "windows" else "}"


###
# Helper functions
###
def incfile_data(fobj):  # noqa
    fobj.write(
        "\n".join(
            [
                "# This is a python file",
                "from __future__ import print_function",
                "print(str(100))",
                "print(str(2))",
            ]
        )
    )


def ste_data(fobj):  # noqa
    shebang = "@" if platform.system().lower() == "windows" else "#!/bin/bash" + LSEP
    fobj.write(shebang + "echo Hello!")


def te_data(fobj):  # noqa
    fobj.write(
        "\n".join(
            [
                "import argparse",
                "parser = argparse.ArgumentParser(",
                '             description="Test script"',
                ")",
                "parser.add_argument(",
                '    "-d", "--directory",',
                '    help="specify source file directory (default ../pmisc)",',
                "    nargs=1,",
                ")",
                "args = parser.parse_args()",
            ]
        )
    )


@contextlib.contextmanager
def temp_read(fname, fpointer):  # noqa
    fobj = open(fname, "w")
    fpointer(fobj)
    fobj.close()
    sobj = os.stat(fname)
    os.chmod(fname, sobj.st_mode | stat.S_IEXEC)
    try:
        yield fobj
    finally:
        os.remove(fname)


###
# Helper class
###
class Capture(object):  # noqa
    def __init__(self):  # noqa
        self._lines = []

    def prt(self, line):  # noqa
        self._lines.append(line)

    def lines(self):  # noqa
        return "".join(self._lines)


###
# Functions
###
@pytest.mark.parametrize(
    "item, mlines, ref",
    [
        ("1", 10, [1]),
        ("1, 3, 5", 10, [1, 3, 5]),
        ("1-3, 7, 9-11", 10, [1, 2, 3, 7, 9, 10, 11]),
        ("1-3, 9-", 11, [1, 2, 3, 9, 10, 11]),
    ],
)
def test_proc_token(item, mlines, ref):
    """Test _proc_token function behavior."""
    assert pmisc.rst._proc_token(item, mlines) == ref


@pytest.mark.parametrize(
    "item",
    [
        "12--34",
        "12.34",
        "12a34",
        "12-,",
        "12,-",
        "1,2-3-4,5",
        "12,,34,5",
        "1-20,10",
        "1-, 20-",
    ],
)
def test_proc_token_exceptions(item):
    """Test _proc_token function exceptions."""
    obj = pmisc.rst._proc_token
    AI(obj, "lrange", item, 30)


def test_incfile():  # noqa: D202
    """Test incfile function behavior."""

    def make_ref(rlist):
        return LSEP.join([".. code-block:: python", ""] + rlist + ["", ""])

    obj = pmisc.incfile
    fname = "incfile_{0}.py".format(uuid.uuid4())
    sdir = os.path.join(os.path.dirname(__file__), "trial")
    if not os.path.exists(sdir):
        os.makedirs(sdir)
    pmisc.make_dir("trial")
    with temp_read(os.path.join(sdir, fname), incfile_data):
        cap = Capture()
        obj(fname, cap.prt, "", sdir)
        ref = make_ref(
            [
                "    # This is a python file",
                "    from __future__ import print_function",
                "    print(str(100))",
                "    print(str(2))",
            ]
        )
        pmisc.compare_strings(cap.lines(), ref)
        cap = Capture()
        obj(fname, cap.prt, "1,3", sdir)
        ref = make_ref(["    # This is a python file", "    print(str(100))"])
        pmisc.compare_strings(cap.lines(), ref)
        cap = Capture()
        obj(fname, cap.prt, "1,3-", sdir)
        ref = make_ref(
            ["    # This is a python file", "    print(str(100))", "    print(str(2))"]
        )
        pmisc.compare_strings(cap.lines(), ref)
        cap = Capture()
        obj(fname, cap.prt, "3-", sdir)
        ref = make_ref(["    print(str(100))", "    print(str(2))"])
        pmisc.compare_strings(cap.lines(), ref)
        os.environ["PKG_DOC_DIR"] = sdir
        cap = Capture()
        obj(fname, cap.prt)
        ref = make_ref(
            [
                "    # This is a python file",
                "    from __future__ import print_function",
                "    print(str(100))",
                "    print(str(2))",
            ]
        )
        pmisc.compare_strings(cap.lines(), ref)
        del os.environ["PKG_DOC_DIR"]
    shutil.rmtree(sdir)
    sdir = os.path.dirname(sys.modules["pmisc"].__file__)
    with temp_read(os.path.join(sdir, fname), incfile_data):
        cap = Capture()
        obj(fname, cap.prt)
        ref = make_ref(
            [
                "    # This is a python file",
                "    from __future__ import print_function",
                "    print(str(100))",
                "    print(str(2))",
            ]
        )
        pmisc.compare_strings(cap.lines(), ref)


def test_ste():
    """Test ste function behavior."""
    # pylint: disable=W0702
    def make_ref(rlist, indent=0):
        return LSEP.join(
            ["", (indent * " ") + ".. code-block:: bash", ""] + rlist + ["", ""]
        )

    obj = pmisc.ste
    fname = "myscript_{0}{1}".format(
        uuid.uuid4(), ".bat" if platform.system().lower() == "windows" else ""
    )
    bdir = os.path.dirname(__file__)
    full_fname = os.path.join(bdir, fname)
    with temp_read(full_fname, ste_data):
        cmd = LDELIM + "PKG_BIN_DIR" + RDELIM + os.sep + fname
        cap = Capture()
        ref = make_ref(["    $ " + cmd, "    Hello!"])
        # Basic functionality
        obj(fname, nindent=0, mdir=bdir, fpointer=cap.prt)
        pmisc.compare_strings(cap.lines(), ref)
        # Indentation
        cap = Capture()
        ref = make_ref(["        $ " + cmd, "        Hello!"], 4)
        obj(fname, nindent=4, mdir=bdir, fpointer=cap.prt)
        pmisc.compare_strings(cap.lines(), ref)


def test_term_echo():  # noqa: D202
    """Test term_echo function behavior."""

    def make_ref(rlist, indent=0):
        return LSEP.join(
            ["", (indent * " ") + ".. code-block:: bash", ""] + rlist + ["", ""]
        )

    obj = pmisc.term_echo
    cap = Capture()
    ref = make_ref(["    $ echo Hello!", "    Hello!"])
    # Basic functionality
    obj("echo Hello!", fpointer=cap.prt)
    pmisc.compare_strings(cap.lines(), ref)
    # Environment variable substitution
    cap = Capture()
    ref = make_ref(["    $ " + LDELIM + "CMD" + RDELIM + " Hello!", "    Hello!"])
    obj(LDELIM + "CMD" + RDELIM + " Hello!", env={"CMD": "echo"}, fpointer=cap.prt)
    pmisc.compare_strings(cap.lines(), ref)
    # Indentation
    cap = Capture()
    ref = make_ref(["        $ echo Hello!", "        Hello!"], 4)
    obj("echo Hello!", nindent=4, fpointer=cap.prt)
    pmisc.compare_strings(cap.lines(), ref)
    # Columns
    cap = Capture()
    with pmisc.TmpFile(te_data) as fname:
        cmd = LDELIM + "PYTHON_CMD" + RDELIM + " " + fname
        header = [
            "",
            ".. code-block:: bash",
            "",
            "    $ " + cmd + " -h",
            "    usage: " + os.path.basename(fname) + " [-h] [-d DIRECTORY]",
            "",
            "    Test script",
            "",
            "    optional arguments:",
        ]
        footer1 = [
            "      -h, --help            show this help",
            "                            message and",
            "                            exit",
            "      -d DIRECTORY, --directory DIRECTORY",
            "                            specify source",
            "                            file directory",
            "                            (default",
            "                            ../pmisc)",
        ]
        footer2 = [
            "      -h, --help      show this help",
            "                      message and exit",
            "      -d DIRECTORY, --directory DIRECTORY",
            "                      specify source file",
            "                      directory (default",
            "                      ../pmisc)",
        ]
        footer3 = ["", ""]
        msgs = [
            LSEP.join(header + footer1 + footer3),
            LSEP.join(header + footer2 + footer3),
        ]
        obj(cmd + " -h", cols=40, fpointer=cap.prt, env={"PYTHON_CMD": sys.executable})
    exclude_line = (
        "Coverage.py warning: --include is ignored because --source "
        "is set (include-ignored)"
    )
    act = [item for item in cap.lines().split(LSEP) if item.strip() != exclude_line]
    act = LSEP.join(act)
    ret = any(act == item for item in msgs)
    pmisc.compare_strings(act, msgs[1])
    if not ret:
        for num, text in enumerate(msgs):
            print("Reference {0}".format(num))
            print(text)
            print(30 * "-")
        print(cap.lines())
        print(30 * "-")
    assert ret
