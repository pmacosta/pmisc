# test.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0304,C0305,C0413,E0611,F0401
# pylint: disable=R0914,W0106,W0122,W0212,W0613,W0703

# Standard library imports
from __future__ import print_function
import copy
import os
import re
import sys
if sys.hexversion < 0x03000000: # pragma: no cover
    from itertools import izip_longest
else:    # pragma: no cover
    from itertools import zip_longest as izip_longest
try:    # pragma: no cover
    from inspect import signature
except ImportError: # pragma: no cover
    from funcsigs import signature
# PyPI imports
import pytest
from _pytest.main import Failed
# Intra-package imports
if sys.hexversion < 0x03000000: # pragma: no cover
    from .compat2 import _ex_type_str, _get_ex_msg
else:   # pragma: no cover
    from .compat3 import _ex_type_str, _get_ex_msg


###
# Functions
###
def _get_fargs(func, no_self=False, no_varargs=False): # pragma: no cover
    """
    Returns a tuple of the function argument names in the order they are
    specified in the function signature

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
    is_parg = lambda x: (len(x) > 1) and (x[0] == '*') and (x[1] != '*')
    is_kwarg = lambda x: (len(x) > 2) and (x[:2] == '**')

    par_dict = signature(func).parameters
    # Mark positional and/or keyword arguments (if any)
    args = [
        '{prefix}{arg}'.format(
            prefix=(
                '*'
                if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else
                (
                    '**'
                    if par_dict[par].kind == par_dict[par].VAR_KEYWORD else
                    ''
                )
            ),
            arg=par
        )
        for par in par_dict
    ]
    # Filter out 'self' from parameter list (optional)
    self_filtered_args = args if not args else (
        args[1 if (args[0] == 'self') and no_self else 0:]
    )
    # Filter out positional or keyword arguments (optional)
    varargs_filtered_args = tuple([
        arg
        for arg in self_filtered_args
        if ((not no_varargs) or
           (no_varargs and (not is_parg(arg)) and (not is_kwarg(arg))))
    ])
    return varargs_filtered_args


def _invalid_frame(fobj):
    """ Selects valid stack frame to process """
    fin = fobj.f_code.co_filename
    invalid_module = fin.endswith('test.py')
    return invalid_module or (not os.path.isfile(fin))


def _pcolor(text, color, indent=0): # pragma: no cover
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34,
         'magenta':35, 'cyan':36, 'white':37, 'none':-1
    }
    color = color.lower()
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color], indent=' '*indent, text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def _raise_exception_mismatch(excinfo, extype, exmsg):
    regexp = re.compile(exmsg) if isinstance(exmsg, str) else None
    actmsg = get_exmsg(excinfo)
    acttype = (
        exception_type_str(excinfo.type)
        if hasattr(excinfo, 'type') else
        repr(excinfo)[:repr(excinfo).find('(')]
    )
    if not ((acttype == exception_type_str(extype))
       and ((actmsg == exmsg) or (regexp and regexp.match(actmsg)))):
        assert False, (
            'Raised exception mismatch'
            '{0}Expected: {1} ({2}){0}Got: {3} ({4})'.format(
                os.linesep, exception_type_str(extype), exmsg, acttype, actmsg
            )
        )


def _raise_if_not_raised(eobj, exmsg=None):
    if get_exmsg(eobj).upper().startswith('DID NOT RAISE'):
        raise AssertionError(exmsg or 'Did not raise')


def assert_arg_invalid(fpointer, pname, *args, **kwargs):
    r"""
    Asserts whether a function raises a :code:`RuntimeError` exception with the
    message :code:`'Argument \`*pname*\` is not valid'`, where
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
        'Argument `{0}` is not valid'.format(pname),
        *args,
        **kwargs
    )


def assert_exception(fpointer, extype, exmsg, *args, **kwargs):
    """
    Asserts an exception type and message within the Py.test environment. If
    the actual exception message and the expected exception message do not
    literally match then the expected exception message is treated as a
    regular expression and a match is sought with the actual exception message

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
            raise RuntimeError('Illegal number of arguments')
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
    Asserts whether a class property raises a given exception when assigned
    a given value

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
    lvars.update({'____test_obj____':cobj})
    # Run method assignment
    cmd = '____test_obj____.'+prop_name+' = '+repr(value)
    try:
        with pytest.raises(extype) as excinfo:
            exec(cmd, fobj.f_globals, lvars)
    except (BaseException, Exception, Failed) as eobj:
        _raise_if_not_raised(eobj)
        _raise_exception_mismatch(eobj, extype, exmsg)
    _raise_exception_mismatch(excinfo, extype, exmsg)


def assert_ro_prop(cobj, prop_name):
    """
    Asserts that a class property cannot be deleted

    :param cobj: Class object
    :type  cobj: class object

    :param prop_name: Property name
    :type  prop_name: string
    """
    try:
        with pytest.raises(AttributeError) as excinfo:
            exec('del cobj.'+prop_name, None, locals())
    except (BaseException, Exception, Failed) as eobj:
        _raise_if_not_raised(eobj, 'Property can be deleted')
    extype = 'AttributeError'
    exmsg = "can't delete attribute"
    _raise_exception_mismatch(excinfo, extype, exmsg)


def compare_strings(actual, ref, diff_mode=False):
    r"""
    Compare two strings. Lines are numbered, differing characters are colored
    yellow and extra characters (characters present in one string but not in
    the other) are colored red

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
    pyellow = lambda x, y: x if x == y else _pcolor(x, 'yellow')
    def colorize_lines(list1, list2, template, mode=True):
        iobj = izip_longest(list1, list2, fillvalue='')
        for num, (line1, line2) in enumerate(iobj):
            if mode and (len(list2)-1 < num):
                break
            line = [pyellow(chr2, chr1) for chr1, chr2 in zip(line1, line2)]
            # Eliminate superfluous colorizing codes when next character has
            # the same color
            line = ''.join(line).replace('\033[0m\033[33m', '')
            if len(line2) > len(line1):
                line += _pcolor(line2[len(line1):], 'red')
            yield template.format(num+1, line)
    def print_non_diff(msg, list1, list2, template):
        ret = ''
        ret += _pcolor(msg, 'cyan')+os.linesep
        ret += _pcolor('-'*len(msg), 'cyan')+os.linesep
        for line in colorize_lines(list1, list2, template):
            ret += line+os.linesep
        return ret
    def print_diff(list1, list2, template1, template2, sep):
        iobj = zip(
            colorize_lines(list1, list2, template1, False),
            colorize_lines(list2, list1, template2, False)
        )
        ret = ''
        for rline, aline in iobj:
            ret += _pcolor(sep, 'cyan')+os.linesep
            ret += rline+os.linesep
            ret += aline+os.linesep
        return ret
    if not isinstance(actual, str):
        raise RuntimeError('Argument `actual` is not valid')
    if not isinstance(ref, str):
        raise RuntimeError('Argument `ref` is not valid')
    if not isinstance(diff_mode, bool):
        raise RuntimeError('Argument `diff_mode` is not valid')
    if actual != ref:
        actual = actual.split(os.linesep)
        ref = ref.split(os.linesep)
        length = len(str(max(len(actual), len(ref))))
        ret = _pcolor('<<<', 'cyan')+os.linesep
        ret += 'Matching character'+os.linesep
        ret += _pcolor('Mismatched character', 'yellow')+os.linesep
        ret += _pcolor('Extra character', 'red')+os.linesep
        if not diff_mode:
            template = _pcolor('{0:'+str(length)+'}:', 'cyan')+' {1}'
            ret += print_non_diff('Reference text', actual, ref, template)
            ret += print_non_diff('Actual text', ref, actual, template)
        else:
            mline = max(
                [
                    max(len(item1), len(item2))
                    for item1, item2 in izip_longest(actual, ref, fillvalue='')
                ]
            )
            sep = '-'*(mline+length+9)
            template1 = _pcolor('{0:'+str(length)+'} Ref.  :', 'cyan')+' {1}'
            template2 = _pcolor(' '*length+' Actual:', 'cyan')+' {1}'
            ret += print_diff(actual, ref, template1, template2, sep)
        ret += _pcolor('>>>', 'cyan')+os.linesep
        raise AssertionError('Strings do not match'+os.linesep+ret)


def comp_list_of_dicts(list1, list2):
    """ Compare list of dictionaries """
    for item in list1:
        if item not in list2:
            print('List1 item not in list2:')
            print(item)
            return False
    for item in list2:
        if item not in list1:
            print('List2 item not in list1:')
            print(item)
            return False
    return True


def exception_type_str(exobj):
    """
    Returns an exception type string

    :param exobj: Exception
    :type  exobj: type (Python 2) or class (Python 3)

    :rtype: string

    For example:

        >>> import pmisc
        >>> pmisc.exception_type_str(RuntimeError)
        'RuntimeError'
    """
    return _ex_type_str(exobj)


def get_exmsg(exobj): # pragma: no cover
    """
    Returns exception message (Python interpreter version independent)

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
