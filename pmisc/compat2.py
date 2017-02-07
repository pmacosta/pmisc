# compat2.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Functions
###
def _ex_type_str(exobj):
    """ Returns a string corresponding to the exception type """
    return str(exobj).split('.')[-1][:-2]


def _get_ex_msg(obj):
    """ Get exception message """
    return obj.value.message if hasattr(obj, 'value') else obj.message


def _readlines(fname): # pragma: no cover
    """ Read all lines from file """
    with open(fname, 'r') as fobj:
        return fobj.readlines()


# Largely from From https://stackoverflow.com/questions/956867/
# how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
# with Python 2.6 compatibility changes
def _unicode_to_ascii(obj): # pragma: no cover
    # pylint: disable=E0602
    if isinstance(obj, dict):
        return dict(
            [
                (_unicode_to_ascii(key), _unicode_to_ascii(value))
                for key, value in obj.items()
            ]
        )
    elif isinstance(obj, list):
        return [_unicode_to_ascii(element) for element in obj]
    elif isinstance(obj, unicode):
        return obj.encode('utf-8')
    else:
        return obj


def _write(fobj, data): # pragma: no cover
    """ Write data to file """
    fobj.write(data)
