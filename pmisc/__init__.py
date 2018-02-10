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
import uuid


###
# Constants
###
_ORIG_EXCEPTHOOK = sys.excepthook
_EXC_TRAPS = [
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        128,
        '_raise_if_not_raised',
        "raise AssertionError(exmsg or 'Did not raise')"
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        160,
        'assert_arg_invalid',
        '**kwargs'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        225,
        'assert_exception',
        '_raise_if_not_raised(eobj)'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        226,
        'assert_exception',
        '_raise_exception_mismatch(eobj, extype, exmsg)'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        228,
        'assert_exception',
        '_raise_exception_mismatch(excinfo, extype, exmsg)'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        265,
        'assert_prop',
        '_raise_if_not_raised(eobj)'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        267,
        'assert_prop',
        '_raise_exception_mismatch(excinfo, extype, exmsg)'
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        284,
        'assert_ro_prop',
        "_raise_if_not_raised(eobj, 'Property can be deleted')"
    ),
    (
        2,
        'pmisc{0}test.py'.format(os.sep),
        287,
        'assert_ro_prop',
        '_raise_exception_mismatch(excinfo, extype, exmsg)'
    ),
    (
       2,
       'pmisc{0}test.py'.format(os.sep),
        379,
        'compare_strings',
        "raise AssertionError('Strings do not match'+os.linesep+ret)"
    ),
]


###
# Functions
###
def eprint(msg): # pragma: no cover
    """
    Print passthrough function, for ease of testing of
    custom excepthook function
    """
    print(msg, file=sys.stderr)


def excepthook(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler to remove unwanted traceback elements
    past a given specific module call
    """
    # pylint: disable=R0914
    def make_test_tuple(tbt, ntokens=1):
        """ Create exception comparison tuple """
        fname, line, func, exc = tbt
        fname = os.sep.join(fname.split(os.sep)[-ntokens:])
        return (fname, line, func, exc)
    def homogenize_breaks(msg):
        token = '_{0}_'.format(uuid.uuid4())
        msg = msg.replace(os.linesep, token)
        msg = msg.replace('\n', os.linesep)
        msg = msg.replace(token, os.linesep).rstrip()
        return msg
    tbs = traceback.extract_tb(exc_traceback)
    offset = 0
    for num, item in enumerate((tbs)):
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
    if not offset:
        _ORIG_EXCEPTHOOK(exc_type, exc_value, exc_traceback)
    else:
        tblines = ['Traceback (most recent call last):']
        tblines += traceback.format_list(tbs[:offset])
        tblines = [homogenize_breaks(item) for item in tblines if item.strip()]
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
