# ctx.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0105

# Standard library imports
from __future__ import print_function
import os
import platform
import tempfile
import time
import types
# PyPI imports
import decorator

if os.environ.get('APPVEYOR', None):    # pragma: no cover
    tempfile.tempdir = os.environ['CITMP']


"""
=[=cog
import os, sys, docs.support
fname = sys.modules['docs.support'].__file__
mdir = os.path.realpath(os.path.dirname(fname))
=]=
=[=end=]=
"""

###
# Context managers
###
@decorator.contextmanager
def ignored(*exceptions):
    """
    Executes commands and selectively ignores exceptions
    (Inspired by `"Transforming Code into Beautiful, Idiomatic Python"
    <http://pyvideo.org/video/1780/
    transforming-code-into-beautiful-idiomatic-pytho>`_ talk at PyCon US
    2013 by Raymond Hettinger)

    :param exceptions: Exception type(s) to ignore
    :type  exceptions: Exception object, i.e. RuntimeError, OSError, etc.

    For example:

    .. =[=cog
    .. import pmisc
    .. pmisc.incfile('pmisc_example_1.py', cog.out, '1, 6-', mdir)
    .. =]=
    .. code-block:: python

        # pmisc_example_1.py
        from __future__ import print_function
        import os, pmisc

        def ignored_example():
            fname = 'somefile.tmp'
            open(fname, 'w').close()
            print('File {0} exists? {1}'.format(
                fname, os.path.isfile(fname)
            ))
            with pmisc.ignored(OSError):
                os.remove(fname)
            print('File {0} exists? {1}'.format(
                fname, os.path.isfile(fname)
            ))
            with pmisc.ignored(OSError):
                os.remove(fname)
            print('No exception trying to remove a file that does not exists')
            try:
                with pmisc.ignored(RuntimeError):
                    os.remove(fname)
            except:
                print('Got an exception')

    .. =[=end=]=

    .. code-block:: python

        >>> import docs.support.pmisc_example_1
        >>> docs.support.pmisc_example_1.ignored_example()
        File somefile.tmp exists? True
        File somefile.tmp exists? False
        No exception trying to remove a file that does not exists
        Got an exception
    """
    try:
        yield
    except exceptions:
        pass


class Timer(object):
    r"""
    Profiles blocks of code by calculating elapsed time between the context
    manager entry and exit time points. Inspired by `Huy Nguyen's blog
    <http://www.huyng.com/posts/python-performance-analysis/>`_

    :param verbose: Flag that indicates whether the elapsed time is printed
                    upon exit (True) or not (False)
    :type  verbose: boolean

    :returns: :py:class:`pmisc.Timer`

    :raises: RuntimeError (Argument \`verbose\` is not valid)

    For example:

    .. =[=cog
    .. import pmisc
    .. pmisc.incfile('pmisc_example_2.py', cog.out, '1, 6-', mdir)
    .. =]=
    .. code-block:: python

        # pmisc_example_2.py
        from __future__ import print_function
        import pmisc

        def timer(num_tries, fpointer):
            with pmisc.Timer() as tobj:
                for _ in range(num_tries):
                    fpointer()
            print('Time per call: {0} seconds'.format(
                tobj.elapsed_time/(2.0*num_tries)
            ))

        def sample_func():
            count = 0
            for num in range(0, count):
                count += num

    .. =[=end=]=

    .. code-block:: python

        >>> from docs.support.pmisc_example_2 import *
        >>> timer(100, sample_func) #doctest: +ELLIPSIS
        Time per call: ... seconds
    """
    def __init__(self, verbose=False):
        if not isinstance(verbose, bool):
            raise RuntimeError('Argument `verbose` is not valid')
        self._tstart = None
        self._tstop = None
        self._elapsed_time = None
        self._verbose = verbose

    def __enter__(self):
        self._tstart = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._tstop = time.time()
        # time.time() returns time in seconds since the epoch
        self._elapsed_time = 1000.0*(self._tstop-self._tstart)
        if self._verbose:
            print('Elapsed time: {time}[msec]'.format(time=self._elapsed_time))
        if exc_type is not None:
            return False

    def _get_elapsed_time(self):
        return self._elapsed_time

    elapsed_time = property(_get_elapsed_time, doc='Elapsed time')
    """
    Returns elapsed time (in seconds) between context manager entry and exit
    time points

    :rtype: float
    """


class TmpFile(object):
    r"""
    Creates a temporary file and optionally sets up hooks for a function to
    write data to it

    :param fpointer: Pointer to a function that writes data to file.
                     If the argument is not None the function pointed to
                     receives exactly one argument, a file-like object
    :type  fpointer: function object or None

    :returns:   temporary file name

    :raises:    RuntimeError (Argument \`fpointer\` is not valid)

    .. warning:: The file name returned uses the forward slash (``/``) as
       the path separator regardless of the platform. This avoids
       `problems <https://pythonconquerstheuniverse.wordpress.com/2008/06/04/
       gotcha-%E2%80%94-backslashes-in-windows-filenames/>`_ with
       escape sequences or mistaken Unicode character encodings (``\\user``
       for example). Many functions in the os module of the standard library (
       `os.path.normpath()
       <https://docs.python.org/2/library/os.path.html#os.path.normpath>`_ and
       others) can change this path separator to the operating system path
       separator if needed

    For example:

    .. =[=cog
    .. import pmisc
    .. pmisc.incfile('pmisc_example_3.py', cog.out, '1, 6-', mdir)
    .. =]=
    .. code-block:: python

        # pmisc_example_3.py
        from __future__ import print_function
        import pmisc

        def write_data(file_handle):
            file_handle.write('Hello world!')

        def show_tmpfile():
            with pmisc.TmpFile(write_data) as fname:
                with open(fname, 'r') as fobj:
                    lines = fobj.readlines()
            print('\n'.join(lines))

    .. =[=end=]=

    .. code-block:: python

        >>> from docs.support.pmisc_example_3 import *
        >>> show_tmpfile()
        Hello world!
    """
    # pylint: disable=E1129
    def __init__(self, fpointer=None):
        if (fpointer and
           (not isinstance(fpointer, types.FunctionType)) and
           (not isinstance(fpointer, types.LambdaType))):
            raise RuntimeError('Argument `fpointer` is not valid')
        self._fname = None
        self._fpointer = fpointer

    def __enter__(self):
        fdesc, fname = tempfile.mkstemp()
        # fdesc is an OS-level file descriptor, see problems if this
        # is not properly closed in this post:
        # https://www.logilab.org/blogentry/17873
        os.close(fdesc)
        if platform.system().lower() == 'windows':  # pragma: no cover
            fname = fname.replace(os.sep, '/')
        self._fname = fname
        if self._fpointer:
            with open(self._fname, 'w') as fobj:
                self._fpointer(fobj)
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):
        with ignored(OSError):
            os.remove(self._fname)
        if exc_type is not None:
            return False
