# compat3.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Functions
###
def _ex_type_str(exobj):
    """ Returns a string corresponding to the exception type """
    return str(exobj).split("'")[1].split('.')[-1]


def _get_ex_msg(obj):
    """ Get exception message """
    return obj.value.args[0] if hasattr(obj, 'value') else obj.args[0]


def _readlines(fname, fpointer1=open, fpointer2=open): # pragma: no cover
    """ Read all lines from file """
    # fpointer1, fpointer2 arguments to ease testing
    try:
        with fpointer1(fname, 'r') as fobj:
            return fobj.readlines()
    except UnicodeDecodeError: # pragma: no cover
        with fpointer2(fname, 'r', encoding='utf-8') as fobj:
            return fobj.readlines()
    except: # pragma: no cover
        raise


def _unicode_to_ascii(obj): # pragma: no cover
    # pylint: disable=E0602
    return obj


def _write(fobj, data): # pragma: no cover
    """ Write data to file """
    fobj.write(data)
