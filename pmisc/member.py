# member.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Functions
###
def isalpha(obj):
    """
    Tests if the argument is a string representing a number

    :param obj: Object
    :type  obj: any

    :rtype: boolean

    For example:

        >>> import pmisc
        >>> pmisc.isalpha('1.5')
        True
        >>> pmisc.isalpha('1E-20')
        True
        >>> pmisc.isalpha('1EA-20')
        False
    """
    # pylint: disable=W0702
    try:
        float(obj)
        return isinstance(obj, str)
    except:
        return False


def ishex(obj):
    """
    Tests if the argument is a string representing a valid hexadecimal digit

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (isinstance(obj, str) and
        (len(obj) == 1) and
        (obj.upper() in '0123456789ABCDEF'))
    )


def isiterable(obj):
    """
    Tests if the argument is an iterable

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def isnumber(obj):
    """
    Tests if the argument is a number (complex, float or integer)

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (((obj is not None) and
        (not isinstance(obj, bool)) and
        (isinstance(obj, int) or
        isinstance(obj, float) or
        isinstance(obj, complex))))
    )


def isreal(obj):
    """
    Tests if the argument is a real number (float or integer)

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        ((obj is not None) and
        (not isinstance(obj, bool)) and (
        isinstance(obj, int) or
        isinstance(obj, float)))
    )
