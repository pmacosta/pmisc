# file.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,E0401,E0611,F0401

# Standard library imports
from __future__ import print_function
import os
import sys
import platform
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
if sys.hexversion < 0x03000000:
    import mock
# Intra-package imports
import pmisc
from pmisc import AE, AI
if sys.hexversion < 0x03000000:
    from pmisc.compat2 import _unicode_to_ascii
else:
    from pmisc.compat3 import _unicode_to_ascii


###
# Test functions
###
def test_make_dir(capsys):
    """ Test make_dir function behavior """
    def mock_os_makedir(file_path):
        print(file_path)
    home_dir = os.path.expanduser('~')
    with mock.patch('os.makedirs', side_effect=mock_os_makedir):
        fname = os.path.join(home_dir, 'some_dir', 'some_file.ext')
        pmisc.make_dir(fname)
        stdout, _ = capsys.readouterr()
        actual = repr(os.path.dirname(fname).rstrip())[1:-1]
        ref = repr(_unicode_to_ascii(stdout.rstrip()))[1:-1]
        assert actual == ref
        pmisc.make_dir(
            os.path.join(os.path.abspath(os.sep), 'some_file.ext')
        )
        stdout, _ = capsys.readouterr()
        assert stdout == ''


def test_normalize():
    """ Test normalize function behavior """
    obj = pmisc.normalize
    AI(obj, 'value', value='a', series=[2, 5], offset=10)
    AI(obj, 'offset', value=5, series=[2, 5], offset='a')
    AI(obj, 'series', value=5, series=['a', 'b'])
    exmsg = 'Argument `offset` has to be in the [0.0, 1.0] range'
    AE(obj, ValueError, exmsg, value=5, series=[2, 5], offset=10)
    exmsg = 'Argument `value` has to be within the bounds of argument `series`'
    AE(obj, ValueError, exmsg, value=0, series=[2, 5], offset=0)
    assert pmisc.normalize(15, [10, 20]) == 0.5
    assert pmisc.normalize(15, [10, 20], 0.5) == 0.75


def test_normalize_windows_fname():
    """ Test normalize_windows_fname behavior """
    obj = pmisc.normalize_windows_fname
    in_windows = platform.system().lower() == 'windows'
    ref = r'a\b\c' if in_windows else 'a/b/c//'
    assert obj('a/b/c//') == ref
    ref = r'a\b\c' if in_windows else 'a/b/c'
    assert obj('a/b/c//', True) == ref
    ref = r'\\a\b\c' if in_windows else r'\\a\\b\\c'
    assert obj(r'\\\\\\\\a\\\\b\\c', True) == ref
    ref = r'C:\a\b\c' if in_windows else r'C:\\a\\b\\c'
    assert obj(r'C:\\\\\\\\a\\\\b\\c', True) == ref
    ref = (
        '\\apps\\temp\\new\\file\\wire'
        if in_windows else
        r'\apps\temp\new\\file\\wire'
    )
    assert obj(r'\apps\temp\new\\\\file\\\\\\\\\\wire', True) == ref
