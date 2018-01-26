# __init__.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,W0401

# Standard library imports
from __future__ import print_function
import os
import re
import sys
import traceback


###
# Constants
###
_ORIG_EXCEPTHOOK = sys.excepthook
_EXC_TRAPS = [
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        136,
        'assert_arg_invalid',
        '**kwargs'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        199,
        'assert_exception',
        "raise AssertionError('Did not raise')"
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        205,
        'assert_exception',
        "'\\nExpected: {0}\\nGot: {1}'.format(refstr, actstr)"
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        218,
        'assert_exception',
        'actmsg'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        278,
        'assert_ro_prop',
        "raise AssertionError('Property can be deleted')"
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        287,
        'assert_ro_prop',
        'extype, exmsg, exception_type_str(excinfo.type), actmsg'
    ),
    (
        2,
       'pmisc{0}test.py'.format(os.sep),
        381,
        'compare_strings',
        "raise AssertionError('Strings do not match'+'\\n'+ret)"
    )
]


###
# Functions
###
def eprint(msg):
    """
    Print passthough function, for ease of testing of
    custom excepthook function
    """
    print(msg, file=sys.stderr)


def excepthook(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler to remove unwanted traceback elements
    past a given specific module call
    """
    #pylint:disable=R0914
    def make_test_tuple(tbt, ntokens=1):
        """ Create exception comparison tuple """
        fname, line, func, exc = tbt
        fname = os.sep.join(fname.split(os.sep)[-ntokens:])
        return (fname, line, func, exc)
    tbs = traceback.extract_tb(exc_traceback)
    offset = 0
    for item in [-2, -1]:
        found = False
        for trap in _EXC_TRAPS:
            ntokens = trap[0]
            ref = make_test_tuple(trap[1:], ntokens)
            fname, line, func, exc = make_test_tuple(tbs[item], ntokens)
            #print((fname, line, func, exc))
            if ((len(tbs) > abs(item)-1) and
                ((fname, line, func, exc) == ref)):
                offset = item
                found = True
                break
        if found:
            break
    if not offset:
        _ORIG_EXCEPTHOOK(exc_type, exc_value, exc_traceback)
    else:
        tblines = ['Traceback (most recent call last):']
        tblines += traceback.format_list(tbs[:offset])
        tblines = [item.rstrip() for item in tblines if item.strip()]
        regexp = re.compile(r"<(?:\bclass\b|\btype\b)\s+'?([\w|\.]+)'?>")
        exc_type = regexp.match(str(exc_type)).groups()[0]
        exc_type = (
            exc_type[11:] if exc_type.startswith('exceptions.') else exc_type
        )
        tblines += ['{0}: {1}'.format(exc_type, exc_value)]
        lines = os.linesep.join(tblines)
        eprint(lines)
sys.excepthook = excepthook


# Intra-package imports
from .version import __version__
from .ctx import *
from .dicts import *
from .file import *
from .member import *
from .misc import *
from .number import *
from .rst import *
from .strings import *
from .test import *
