# ctx.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1129

# Standard library imports
import os
import platform
import re
import sys
import time
import uuid
# PyPI imports
import pytest
# Intra-package imports
import pmisc
from pmisc import GET_EXMSG
if sys.hexversion < 0x03000000:
    from pmisc.compat2 import _write
else:
    from pmisc.compat3 import _write


###
# Test functions
###
def test_ignored():
    """ Test ignored context manager behavior """
    with pmisc.TmpFile() as fname:
        with open(fname, 'w') as output_obj:
            output_obj.write('This is a test file')
        assert os.path.exists(fname)
        with pmisc.ignored(OSError):
            os.remove(fname)
        assert not os.path.exists(fname)
    with pmisc.ignored(OSError):
        os.remove('_some_file_')
    with pytest.raises(OSError) as excinfo:
        with pmisc.ignored(RuntimeError):
            os.remove('_some_file_')

    assert excinfo.value.strerror == (
        'The system cannot find the file specified'
        if platform.system().lower() == 'windows' else
        'No such file or directory'
    )
    assert excinfo.value.filename == '_some_file_'
    assert excinfo.value.errno == 2


def test_timer(capsys):
    """ Test Timer context manager behavior """
    # Test argument validation
    with pytest.raises(RuntimeError) as excinfo:
        with pmisc.Timer(5):
            pass
    assert GET_EXMSG(excinfo) == 'Argument `verbose` is not valid'
    # Test that exceptions within the with statement are re-raised
    with pytest.raises(RuntimeError) as excinfo:
        with pmisc.Timer():
            raise RuntimeError('Error in code')
    assert GET_EXMSG(excinfo) == 'Error in code'
    # Test normal operation
    with pmisc.Timer() as tobj:
        time.sleep(0.5)
    assert isinstance(tobj.elapsed_time, float) and (tobj.elapsed_time > 0)
    tregexp = re.compile(r'Elapsed time: [\d|\.]+\[msec\]')
    with pmisc.Timer(verbose=True) as tobj:
        time.sleep(0.5)
    out, _ = capsys.readouterr()
    assert tregexp.match(out.rstrip())

def test_tmp_dir():
    """ Test TmpDir context manager behavior """
    # Test argument validation
    with pytest.raises(RuntimeError) as excinfo:
        with pmisc.TmpDir(5) as dname:
            pass
    assert GET_EXMSG(excinfo) == 'Argument `dpath` is not valid'
    dname = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_dir_')
    with pytest.raises(RuntimeError) as excinfo:
        with pmisc.TmpDir(dname) as dname:
            pass
    assert GET_EXMSG(excinfo) == 'Argument `dpath` is not valid'
    # Test behavior when no function pointer is given
    with pmisc.TmpDir() as dname:
        assert os.path.isdir(dname)
    assert not os.path.isdir(dname)
    # Test that exceptions within the with statement are re-raised
    with pytest.raises(OSError) as excinfo:
        with pmisc.TmpDir() as dname:
            raise OSError('No data')
    assert GET_EXMSG(excinfo) == 'No data'
    assert not os.path.isdir(dname)
    # Test behaviour under "normal" circumstances
    with pmisc.TmpDir() as dname:
        fname = os.path.join(dname, 'file_{0}'.format(uuid.uuid4()))
        with open(fname, 'w') as fhandle:
            fhandle.write('pass')
        assert os.path.isdir(dname)
        assert os.path.exists(fname)
    assert not os.path.exists(dname)


def test_tmp_file():
    """ Test TmpFile context manager behavior """
    def write_data(file_handle):
        _write(file_handle, 'Hello world!')
    def write_data_with_args(file_handle, *args, **kwargs):
        _write(file_handle, str(args)+str(kwargs))
    # Test argument validation
    with pytest.raises(RuntimeError) as excinfo:
        with pmisc.TmpFile(5) as fname:
            pass
    assert GET_EXMSG(excinfo) == 'Argument `fpointer` is not valid'
    # Test behavior when no function pointer is given
    with pmisc.TmpFile() as fname:
        assert isinstance(fname, str) and (len(fname) > 0)
        assert os.path.exists(fname)
    assert not os.path.exists(fname)
    # Test that exceptions within the with statement are re-raised
    with pytest.raises(OSError) as excinfo:
        with pmisc.TmpFile(write_data) as fname:
            raise OSError('No data')
    assert GET_EXMSG(excinfo) == 'No data'
    assert not os.path.exists(fname)
    # Test behaviour under "normal" circumstances
    with pmisc.TmpFile(write_data) as fname:
        with open(fname, 'r') as fobj:
            line = fobj.readlines()
        assert line == ['Hello world!']
        assert os.path.exists(fname)
    assert not os.path.exists(fname)
    # Test behaviour under "normal" circumstances with arguments
    with pmisc.TmpFile(write_data_with_args, 3, data='foo') as fname:
        with open(fname, 'r') as fobj:
            line = fobj.readlines()
        assert line == ['(3,){\'data\': \'foo\'}']
        assert os.path.exists(fname)
    assert not os.path.exists(fname)
