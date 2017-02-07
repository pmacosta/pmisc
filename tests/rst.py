# rst.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,W0108,W0212

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
LDELIM = '%' if platform.system().lower() == 'windows' else '${'
RDELIM = '%' if platform.system().lower() == 'windows' else '}'


###
# Helper functions
###
def incfile_data(fobj):
    fobj.write(
        '# This is a python file\n'
        'from __future__ import print_function\n'
        'print(str(100))\n'
        'print(str(2))'
    )


def ste_data(fobj):
    shebang = (
        '@'
        if platform.system().lower() == 'windows' else
        '#!/bin/bash\n'
    )
    fobj.write(shebang+'echo Hello!')


def te_data(fobj):
    fobj.write(
        'import argparse\n'
        'parser = argparse.ArgumentParser(\n'
        '             description="Test script"\n'
        ')\n'
        'parser.add_argument(\n'
        '    "-d", "--directory",\n'
        '    help="specify source file directory (default ../pmisc)",\n'
        '    nargs=1,\n'
        ')\n'
        'args = parser.parse_args()'
    )


@contextlib.contextmanager
def temp_read(fname, fpointer):
    fobj = open(fname, 'w')
    fpointer(fobj)
    fobj.close()
    sobj = os.stat(fname)
    os.chmod(fname, sobj.st_mode | stat.S_IEXEC)
    try:
        yield fobj
    finally:
        try:
            os.remove(fname)
        except:
            raise


###
# Helper class
###
class Capture(object):
    def __init__(self):
        self._lines = []
    def prt(self, line):
        self._lines.append(line)
    def lines(self):
        return ''.join(self._lines)


###
# Functions
###
@pytest.mark.parametrize(
    'item, mlines, ref', [
        ('1', 10, [1]),
        ('1, 3, 5', 10, [1, 3, 5]),
        ('1-3, 7, 9-11', 10, [1, 2, 3, 7, 9, 10, 11]),
        ('1-3, 9-', 11, [1, 2, 3, 9, 10, 11]),
    ]
)
def test_proc_token(item, mlines, ref):
    """ Test _proc_token function behavior """
    assert pmisc.rst._proc_token(item, mlines) == ref


@pytest.mark.parametrize(
    'item', [
        '12--34', '12.34', '12a34', '12-,', '12,-', '1,2-3-4,5',
        '12,,34,5', '1-20,10', '1-, 20-'
    ]
)
def test_proc_token_exceptions(item):
    """ Test _proc_token function exceptions """
    obj = pmisc.rst._proc_token
    AI(obj, 'lrange', item, 30)


def test_incfile():
    """ Test incfile function behavior """
    obj = pmisc.incfile
    fname = 'incfile_{0}.py'.format(uuid.uuid4())
    sdir = os.path.join(os.path.dirname(__file__), 'trial')
    if not os.path.exists(sdir):
        os.makedirs(sdir)
    pmisc.make_dir('trial')
    with temp_read(os.path.join(sdir, fname), incfile_data):
        cap = Capture()
        obj(fname, cap.prt, '', sdir)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    # This is a python file\n'
            '    from __future__ import print_function\n'
            '    print(str(100))\n'
            '    print(str(2))'
            '\n'
        )
        assert cap.lines() == ref
        cap = Capture()
        obj(fname, cap.prt, '1,3', sdir)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    # This is a python file\n'
            '    print(str(100))\n'
            '\n'
        )
        assert cap.lines() == ref
        cap = Capture()
        obj(fname, cap.prt, '1,3-', sdir)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    # This is a python file\n'
            '    print(str(100))\n'
            '    print(str(2))'
            '\n'
        )
        assert cap.lines() == ref
        cap = Capture()
        obj(fname, cap.prt, '3-', sdir)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    print(str(100))\n'
            '    print(str(2))'
            '\n'
        )
        assert cap.lines() == ref
        os.environ['PKG_DOC_DIR'] = sdir
        cap = Capture()
        obj(fname, cap.prt)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    # This is a python file\n'
            '    from __future__ import print_function\n'
            '    print(str(100))\n'
            '    print(str(2))'
            '\n'
        )
        assert cap.lines() == ref
        del os.environ['PKG_DOC_DIR']
    shutil.rmtree(sdir)
    sdir = os.path.dirname(sys.modules['pmisc'].__file__)
    with temp_read(os.path.join(sdir, fname), incfile_data):
        cap = Capture()
        obj(fname, cap.prt)
        ref = (
            '.. code-block:: python\n'
            '\n'
            '    # This is a python file\n'
            '    from __future__ import print_function\n'
            '    print(str(100))\n'
            '    print(str(2))'
            '\n'
        )
        assert cap.lines() == ref


def test_ste():
    """ Test ste function behavior """
    # pylint: disable=W0702
    obj = pmisc.ste
    fname = 'myscript_{0}{1}'.format(
        uuid.uuid4(), '.bat' if platform.system().lower() == 'windows' else ''
    )
    bdir = os.path.dirname(__file__)
    full_fname = os.path.join(bdir, fname)
    with temp_read(full_fname, ste_data):
        cmd = LDELIM+'PKG_BIN_DIR'+RDELIM+os.sep+fname
        cap = Capture()
        ref = (
            '\n'
            '.. code-block:: bash\n'
            '\n'
            '    $ '+cmd+'\n'
            '    Hello!\n'
            '\n'
            '\n'
        )
        # Basic functionality
        obj(fname, nindent=0, mdir=bdir, fpointer=cap.prt)
        assert cap.lines() == ref
        # Indentation
        cap = Capture()
        ref = (
            '\n'
            '    .. code-block:: bash\n'
            '\n'
            '        $ '+cmd+'\n'
            '        Hello!\n'
            '\n'
            '\n'
        )
        obj(fname, nindent=4, mdir=bdir, fpointer=cap.prt)
        assert cap.lines() == ref


def test_term_echo():
    """ Test term_echo function behavior """
    obj = pmisc.term_echo
    cap = Capture()
    ref = (
        '\n'
        '.. code-block:: bash\n'
        '\n'
        '    $ echo Hello!\n'
        '    Hello!\n'
        '\n'
        '\n'
    )
    # Basic functionality
    obj('echo Hello!', fpointer=cap.prt)
    assert cap.lines() == ref
    # Environment variable substitution
    cap = Capture()
    ref = (
        '\n'
        '.. code-block:: bash\n'
        '\n'
        '    $ '+LDELIM+'CMD'+RDELIM+' Hello!\n'
        '    Hello!\n'
        '\n'
        '\n'
    )
    obj(LDELIM+'CMD'+RDELIM+' Hello!', env={'CMD':'echo'}, fpointer=cap.prt)
    assert cap.lines() == ref
    # Indentation
    cap = Capture()
    ref = (
        '\n'
        '    .. code-block:: bash\n'
        '\n'
        '        $ echo Hello!\n'
        '        Hello!\n'
        '\n'
        '\n'
    )
    obj('echo Hello!', nindent=4, fpointer=cap.prt)
    assert cap.lines() == ref
    # Columns
    cap = Capture()
    with pmisc.TmpFile(te_data) as fname:
        cmd = LDELIM+'PYTHON_CMD'+RDELIM+' '+fname
        ref1 = (
            '\n'
            '.. code-block:: bash\n'
            '\n'
            '    $ '+cmd+' -h\n'
            '    usage: '+os.path.basename(fname)+' [-h] [-d DIRECTORY]\n'
            '\n'
            '    Test script\n'
            '\n'
            '    optional arguments:\n'
            '      -h, --help            show this help\n'
            '                            message and\n'
            '                            exit\n'
            '      -d DIRECTORY, --directory DIRECTORY\n'
            '                            specify source\n'
            '                            file directory\n'
            '                            (default\n'
            '                            ../pmisc)\n'
            '\n'
            '\n'
        )
        ref2 = (
            '\n'
            '.. code-block:: bash\n'
            '\n'
            '    $ '+cmd+' -h\n'
            '    usage: '+os.path.basename(fname)+' [-h] [-d DIRECTORY]\n'
            '\n'
            '    Test script\n'
            '\n'
            '    optional arguments:\n'
            '      -h, --help      show this help\n'
            '                      message and exit\n'
            '      -d DIRECTORY, --directory DIRECTORY\n'
            '                      specify source file\n'
            '                      directory (default\n'
            '                      ../pmisc)\n'
            '\n'
            '\n'
        )
        obj(
            cmd+' -h',
            cols=40,
            fpointer=cap.prt,
            env={'PYTHON_CMD':sys.executable}
        )
    assert (cap.lines() == ref1) or (cap.lines() == ref2)
