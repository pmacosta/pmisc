# test.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0304,C0305,C0413,E0611,F0401
# pylint: disable=R0205,R0903,R0914,W0106,W0122,W0201,W0212,W0613,W0703

# Standard library imports
from __future__ import print_function
import copy
import os
import re
import sys
import traceback
import uuid

if sys.hexversion < 0x03000000:  # pragma: no cover
    from itertools import izip_longest
else:  # pragma: no cover
    from itertools import zip_longest as izip_longest
try:  # pragma: no cover
    from inspect import signature
except ImportError:  # pragma: no cover
    from funcsigs import signature
# PyPI imports
import pytest
from _pytest.main import Failed
from _pytest._code import Traceback
from _pytest._code.code import ExceptionInfo

# Intra-package imports
if sys.hexversion < 0x03000000:  # pragma: no cover
    from .compat2 import _ex_type_str, _get_ex_msg
else:  # pragma: no cover
    from .compat3 import _ex_type_str, _get_ex_msg


###
# Constants
###
def _get_trap(func, exc):  # pragma: no cover
    """Find a line in a function with a simple source file parser."""
    debug = False
    ntokens = 2
    fname = "pmisc{0}test.py".format(os.sep)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.py")
    with open(src) as fobj:
        lines = [line.rstrip() for line in fobj.readlines()]
    if debug:
        print(lines)
    in_func = False
    exc_lnum = None
    if debug:
        print("Function: {0}, trigger: {1}".format(func, exc))
    for lnum, line in enumerate(lines):
        if in_func:
            if debug:
                print("   {0}".format(line))
            if line.strip() == exc.strip():
                exc_lnum = lnum
                break
            if line.startswith("def "):
                break
        else:
            if debug:
                print(line)
            in_func = line.startswith("def {0}".format(func))
    if exc_lnum is None:
        raise RuntimeError(
            "Exception raising line could not be found ({0}, {1})".format(func, exc)
        )
    return (ntokens, fname, exc_lnum + 1, func, exc)


_ORIG_EXCEPTHOOK = sys.__excepthook__
_EXC_TRAPS_INFO = [
    ("_raise_if_not_raised", 'raise AssertionError(exmsg or "Did not raise")'),
    ("assert_arg_invalid", "**kwargs"),
    ("assert_exception", "_raise_if_not_raised(eobj)"),
    ("assert_exception", "_raise_exception_mismatch(eobj, extype, exmsg)"),
    ("assert_exception", "_raise_exception_mismatch(excinfo, extype, exmsg)"),
    ("assert_prop", "_raise_if_not_raised(eobj)"),
    ("assert_prop", "_raise_exception_mismatch(eobj, extype, exmsg)"),
    ("assert_prop", "_raise_exception_mismatch(excinfo, extype, exmsg)"),
    ("assert_ro_prop", '_raise_if_not_raised(eobj, "Property can be deleted")'),
    ("assert_ro_prop", "_raise_exception_mismatch(excinfo, extype, exmsg)"),
    (
        "compare_strings",
        'raise AssertionError("Strings do not match" + os.linesep + ret)',
    ),
]
_EXC_TRAPS = [_get_trap(*exc_def) for exc_def in _EXC_TRAPS_INFO]


###
# Helper functions
###
def _del_pmisc_test_frames(excinfo):
    """Remove the pmisc.test module frames from pytest excinfo structure."""
    # pylint: disable=W0231,W0702
    class PmiscExceptionInfo(ExceptionInfo):
        def __init__(self, excinfo, offset):
            new_tb = _process_tb(excinfo.tb, offset)
            self.new_tb = new_tb[0] if new_tb else None
            self.new_excinfo = (excinfo._excinfo[0], excinfo._excinfo[1], excinfo.tb)
            self.new_traceback = Traceback(excinfo.traceback[:offset])
            for num, _ in enumerate(new_tb):
                self.new_traceback[num]._rawentry = new_tb[num]

        @property
        def _excinfo(self):  # pragma: no cover
            return self.new_excinfo

        @property
        def traceback(self):  # pragma: no cover
            return self.new_traceback

        @property
        def tb(self):  # pragma: no cover
            return self.new_tb

    offset = _find_test_module_frame(traceback.extract_tb(excinfo._excinfo[2]))
    if offset:
        return PmiscExceptionInfo(excinfo, offset)
    return excinfo


def _eprint(msg):  # pragma: no cover
    """Print passthrough function, for ease of testing of custom excepthook function."""
    print(msg, file=sys.stderr)


def _excepthook(exc_type, exc_value, exc_traceback):
    """Remove unwanted traceback elements past a given specific module call."""
    tbs = traceback.extract_tb(exc_traceback)
    offset = _find_test_module_frame(tbs)
    if not offset:
        _ORIG_EXCEPTHOOK(exc_type, exc_value, exc_traceback)
    new_tb = _process_tb(exc_traceback, offset)
    if new_tb:
        exc_traceback = new_tb[0]
    tbs = traceback.extract_tb(exc_traceback)
    tblines = ["Traceback (most recent call last):"]
    tblines += traceback.format_list(tbs)
    tblines = [_homogenize_breaks(item) for item in tblines if item.strip()]
    regexp = re.compile(r"<(?:\bclass\b|\btype\b)\s+'?([\w|\.]+)'?>")
    exc_type = regexp.match(str(exc_type)).groups()[0]
    exc_type = exc_type[11:] if exc_type.startswith("exceptions.") else exc_type
    tblines += ["{0}: {1}".format(exc_type, exc_value)]
    lines = os.linesep.join(tblines)
    _eprint(lines)


def _find_test_module_frame(tbs):  # noqa: D202
    """Find the first pmisc.test module frame in Pytest excinfo structure."""

    def make_test_tuple(tbt, ntokens=1):
        """Create exception comparison tuple."""
        fname, line, func, exc = tbt
        fname = os.sep.join(fname.split(os.sep)[-ntokens:])
        return (fname, line, func, exc)

    offset = 0
    for num, item in enumerate(tbs):
        found = False
        for trap in _EXC_TRAPS:
            ntokens = trap[0]
            ref = make_test_tuple(trap[1:], ntokens)
            fname, line, func, exc = make_test_tuple(item, ntokens)
            if (fname, line, func, exc) == ref:
                offset = num
                found = True
                break
        if found:
            break
    return offset


def _get_fargs(func, no_self=False, no_varargs=False):  # pragma: no cover
    """
    Return function argument names.

    The names are returned in a tuple in the order they are specified in the
    function signature

    :param func: Function
    :type  func: function object

    :param no_self: Flag that indicates whether the function argument *self*,
                    if present, is included in the output (False) or not (True)
    :type  no_self: boolean

    :param no_varargs: Flag that indicates whether keyword arguments are
                       included in the output (True) or not (False)
    :type  no_varargs: boolean

    :rtype: tuple
    """
    is_parg = lambda x: (len(x) > 1) and (x[0] == "*") and (x[1] != "*")
    is_kwarg = lambda x: (len(x) > 2) and (x[:2] == "**")

    par_dict = signature(func).parameters
    # Mark positional and/or keyword arguments (if any)
    args = [
        "{prefix}{arg}".format(
            prefix=(
                "*"
                if par_dict[par].kind == par_dict[par].VAR_POSITIONAL
                else ("**" if par_dict[par].kind == par_dict[par].VAR_KEYWORD else "")
            ),
            arg=par,
        )
        for par in par_dict
    ]
    # Filter out 'self' from parameter list (optional)
    self_filtered_args = (
        args if not args else (args[1 if (args[0] == "self") and no_self else 0 :])
    )
    # Filter out positional or keyword arguments (optional)
    varargs_filtered_args = tuple(
        [
            arg
            for arg in self_filtered_args
            if (
                (not no_varargs)
                or (no_varargs and (not is_parg(arg)) and (not is_kwarg(arg)))
            )
        ]
    )
    return varargs_filtered_args


def _homogenize_breaks(msg):
    """Replace stray newline characters with platform-correct line separator."""
    token = "_{0}_".format(uuid.uuid4())
    msg = msg.replace(os.linesep, token)
    msg = msg.replace("\n", os.linesep)
    msg = msg.replace(token, os.linesep).rstrip()
    return msg


def _invalid_frame(fobj):
    """Select valid stack frame to process."""
    fin = fobj.f_code.co_filename
    invalid_module = fin.endswith("test.py")
    return invalid_module or (not os.path.isfile(fin))


def _pcolor(text, color, indent=0):  # pragma: no cover
    esc_dict = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "none": -1,
    }
    color = color.lower()
    if esc_dict[color] != -1:
        return "\033[{color_code}m{indent}{text}\033[0m".format(
            color_code=esc_dict[color], indent=" " * indent, text=text
        )
    return "{indent}{text}".format(indent=" " * indent, text=text)


def _process_tb(trbk, offset=-1):
    """Create a "copy" of the traceback chain and cut it at a predefined depth."""
    obj = trbk
    iret = []
    while obj:
        iret.append((obj.tb_frame, obj.tb_lasti, obj.tb_lineno, obj.tb_next))
        obj = obj.tb_next
    ret = [_CustomTraceback(*item) for item in iret[:offset]]
    if ret:
        ret[-1].tb_next = None
    return ret


def _raise_exception_mismatch(excinfo, extype, exmsg):
    """
    Create verbose message when expected exception does not match actual exception.

    The mismatch may be it due to a different exception type or a different
    exception message or both.
    """
    regexp = re.compile(exmsg) if isinstance(exmsg, str) else None
    actmsg = get_exmsg(excinfo)
    acttype = (
        exception_type_str(excinfo.type)
        if hasattr(excinfo, "type")
        else repr(excinfo)[: repr(excinfo).find("(")]
    )
    if not (
        (acttype == exception_type_str(extype))
        and ((actmsg == exmsg) or (regexp and regexp.match(actmsg)))
    ):
        assert False, (
            "Raised exception mismatch"
            "{0}Expected: {1} ({2}){0}Got: {3} ({4})".format(
                os.linesep, exception_type_str(extype), exmsg, acttype, actmsg
            )
        )


def _raise_if_not_raised(eobj, exmsg=None):
    """Raise an exception if there was no exception raised (and it should have been)."""
    if get_exmsg(eobj).upper().startswith("DID NOT RAISE"):
        raise AssertionError(exmsg or "Did not raise")


###
# Helper classes
###
class _CustomTraceback(object):
    """
    Mimic a traceback object to break the traceback chain.

    The break can be implemented by making tb_next None, as desired
    """

    def __init__(self, tb_frame, tb_lasti, tb_lineno, tb_next):
        self.tb_frame = tb_frame
        self.tb_lasti = tb_lasti
        self.tb_lineno = tb_lineno
        self.tb_next = tb_next


###
# Functions
###
def assert_arg_invalid(fpointer, pname, *args, **kwargs):
    r"""
    Test if function raises :code:`RuntimeError('Argument \`*pname*\` is not valid')`.

    :code:`*pname*` is the value of the **pname** argument, when called with
    given positional and/or keyword arguments

    :param fpointer: Object to evaluate
    :type  fpointer: callable

    :param pname: Parameter name
    :type  pname: string

    :param args: Positional arguments to pass to object
    :type  args: tuple

    :param kwargs: Keyword arguments to pass to object
    :type  kwargs: dictionary

    :raises:
     * AssertionError (Did not raise)

     * RuntimeError (Illegal number of arguments)
    """
    assert_exception(
        fpointer,
        RuntimeError,
        "Argument `{0}` is not valid".format(pname),
        *args,
        **kwargs
    )


def assert_exception(fpointer, extype, exmsg, *args, **kwargs):
    """
    Assert an exception type and message within the Py.test environment.

    If the actual exception message and the expected exception message do not
    literally match then the expected exception message is treated as a regular
    expression and a match is sought with the actual exception message

    :param fpointer: Object to evaluate
    :type  fpointer: callable

    :param extype: Expected exception type
    :type  extype: type

    :param exmsg: Expected exception message (can have regular expressions)
    :type  exmsg: any

    :param args: Positional arguments to pass to object
    :type  args: tuple

    :param kwargs: Keyword arguments to pass to object
    :type  kwargs: dictionary

    For example:

        >>> import pmisc
        >>> try:
        ...     pmisc.assert_exception(
        ...         pmisc.normalize,
        ...         RuntimeError,
        ...         'Argument `offset` is not valid',
        ...         15, [10, 20], 0
        ...     )   #doctest: +ELLIPSIS
        ... except:
        ...     raise RuntimeError('Exception not raised')
        Traceback (most recent call last):
            ...
        RuntimeError: Exception not raised

    :raises:
     * AssertionError (Did not raise)

     * RuntimeError (Illegal number of arguments)
    """
    # Collect function arguments
    arg_dict = {}
    if args:
        fargs = _get_fargs(fpointer, no_self=True)
        if len(args) > len(fargs):
            raise RuntimeError("Illegal number of arguments")
        arg_dict = dict(zip(fargs, args))
    arg_dict.update(kwargs)
    # Execute function and catch exception
    inner_ex = False
    eobj = None
    try:
        with pytest.raises(extype) as excinfo:
            fpointer(**arg_dict)
    except (BaseException, Exception, Failed) as tmp_eobj:
        eobj = tmp_eobj
        inner_ex = True
    if inner_ex:
        _raise_if_not_raised(eobj)
        _raise_exception_mismatch(eobj, extype, exmsg)
    else:
        _raise_exception_mismatch(excinfo, extype, exmsg)


def assert_prop(cobj, prop_name, value, extype, exmsg):
    """
    Assert whether a class property raises an exception when assigned a value.

    :param cobj: Class object
    :type  cobj: class object

    :param prop_name: Property name
    :type  prop_name: string

    :param extype: Exception type
    :type  extype: Exception type object, i.e. RuntimeError, TypeError, etc.

    :param exmsg: Exception message
    :type  exmsg: string
    """
    # Get locals of calling function
    fnum = 0
    fobj = sys._getframe(fnum)
    while _invalid_frame(fobj):
        fnum += 1
        fobj = sys._getframe(fnum)
    fobj = sys._getframe(fnum)
    # Add cobj to local variables dictionary of calling function, the
    # exec statement is going to be run in its environment
    lvars = copy.copy(fobj.f_locals)
    lvars.update({"____test_obj____": cobj})
    # Run method assignment
    cmd = "____test_obj____." + prop_name + " = " + repr(value)
    try:
        with pytest.raises(extype) as excinfo:
            exec(cmd, fobj.f_globals, lvars)
    except (BaseException, Exception, Failed) as eobj:
        _raise_if_not_raised(eobj)
        _raise_exception_mismatch(eobj, extype, exmsg)
    _raise_exception_mismatch(excinfo, extype, exmsg)


def assert_ro_prop(cobj, prop_name):
    """
    Assert that a class property cannot be deleted.

    :param cobj: Class object
    :type  cobj: class object

    :param prop_name: Property name
    :type  prop_name: string
    """
    try:
        with pytest.raises(AttributeError) as excinfo:
            exec("del cobj." + prop_name, None, locals())
    except (BaseException, Exception, Failed) as eobj:
        _raise_if_not_raised(eobj, "Property can be deleted")
    extype = "AttributeError"
    exmsg = "can't delete attribute"
    _raise_exception_mismatch(excinfo, extype, exmsg)


def compare_strings(actual, ref, diff_mode=False):
    r"""
    Compare two strings.

    Lines are numbered, differing characters are colored yellow and extra
    characters (characters present in one string but not in the other) are
    colored red

    :param actual: Text produced by software under test
    :type  actual: string

    :param ref: Reference text
    :type  ref: string

    :param diff_mode: Flag that indicates whether the line(s) of the actual
                      and reference strings are printed one right after
                      the other (True) of if the actual and reference
                      strings are printed separately (False)
    :type diff_mode: boolean

    :raises:
     * AssertionError(Strings do not match)

     * RuntimeError(Argument \`actual\` is not valid)

     * RuntimeError(Argument \`diff_mode\` is not valid)

     * RuntimeError(Argument \`ref\` is not valid)
    """
    # pylint: disable=R0912
    pyellow = lambda x, y: x if x == y else _pcolor(x, "yellow")

    def colorize_lines(list1, list2, template, mode=True):
        iobj = izip_longest(list1, list2, fillvalue="")
        for num, (line1, line2) in enumerate(iobj):
            if mode and (len(list2) - 1 < num):
                break
            line = [pyellow(chr2, chr1) for chr1, chr2 in zip(line1, line2)]
            # Eliminate superfluous colorizing codes when next character has
            # the same color
            line = "".join(line).replace("\033[0m\033[33m", "")
            if len(line2) > len(line1):
                line += _pcolor(line2[len(line1) :], "red")
            yield template.format(num + 1, line)

    def print_non_diff(msg, list1, list2, template):
        ret = ""
        ret += _pcolor(msg, "cyan") + os.linesep
        ret += _pcolor("-" * len(msg), "cyan") + os.linesep
        for line in colorize_lines(list1, list2, template):
            ret += line + os.linesep
        return ret

    def print_diff(list1, list2, template1, template2, sep):
        iobj = zip(
            colorize_lines(list1, list2, template1, False),
            colorize_lines(list2, list1, template2, False),
        )
        ret = ""
        for rline, aline in iobj:
            ret += _pcolor(sep, "cyan") + os.linesep
            ret += rline + os.linesep
            ret += aline + os.linesep
        return ret

    if not isinstance(actual, str):
        raise RuntimeError("Argument `actual` is not valid")
    if not isinstance(ref, str):
        raise RuntimeError("Argument `ref` is not valid")
    if not isinstance(diff_mode, bool):
        raise RuntimeError("Argument `diff_mode` is not valid")
    if actual != ref:
        actual = actual.split(os.linesep)
        ref = ref.split(os.linesep)
        length = len(str(max(len(actual), len(ref))))
        ret = _pcolor("<<<", "cyan") + os.linesep
        ret += "Matching character" + os.linesep
        ret += _pcolor("Mismatched character", "yellow") + os.linesep
        ret += _pcolor("Extra character", "red") + os.linesep
        if not diff_mode:
            template = _pcolor("{0:" + str(length) + "}:", "cyan") + " {1}"
            ret += print_non_diff("Reference text", actual, ref, template)
            ret += print_non_diff("Actual text", ref, actual, template)
        else:
            mline = max(
                [
                    max(len(item1), len(item2))
                    for item1, item2 in izip_longest(actual, ref, fillvalue="")
                ]
            )
            sep = "-" * (mline + length + 9)
            template1 = _pcolor("{0:" + str(length) + "} Ref.  :", "cyan") + " {1}"
            template2 = _pcolor(" " * length + " Actual:", "cyan") + " {1}"
            ret += print_diff(actual, ref, template1, template2, sep)
        ret += _pcolor(">>>", "cyan") + os.linesep
        raise AssertionError("Strings do not match" + os.linesep + ret)


def comp_list_of_dicts(list1, list2):
    """
    Compare list of dictionaries.

    :param list1: First list of dictionaries to compare
    :type  list1: list of dictionaries

    :param list2: Second list of dictionaries to compare
    :type  list2: list of dictionaries

    :rtype: boolean
    """
    for item in list1:
        if item not in list2:
            print("List1 item not in list2:")
            print(item)
            return False
    for item in list2:
        if item not in list1:
            print("List2 item not in list1:")
            print(item)
            return False
    return True


def exception_type_str(exobj):
    """
    Return an exception type string.

    :param exobj: Exception
    :type  exobj: type (Python 2) or class (Python 3)

    :rtype: string

    For example:

        >>> import pmisc
        >>> pmisc.exception_type_str(RuntimeError)
        'RuntimeError'
    """
    return _ex_type_str(exobj)


def get_exmsg(exobj):  # pragma: no cover
    """
    Return exception message (Python interpreter version independent).

    :param exobj: Exception object
    :type  exobj: exception object

    :rtype: string
    """
    return _get_ex_msg(exobj)


###
# Global variables (shortcuts)
###
AE = assert_exception
AI = assert_arg_invalid
APROP = assert_prop
AROPROP = assert_ro_prop
CLDICTS = comp_list_of_dicts
CS = compare_strings
GET_EXMSG = get_exmsg
RE = RuntimeError
