# member.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import string


###
# Functions
###
def isalpha(obj):
    """
    Test if the argument is a string representing a number.

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
    Test if the argument is a string representing a valid hexadecimal digit.

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return isinstance(obj, str) and (len(obj) == 1) and (obj in string.hexdigits)


def isiterable(obj):
    """
    Test if the argument is an iterable.

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def isnumber(obj):
    """
    Test if the argument is a number (complex, float or integer).

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (obj is not None)
        and (not isinstance(obj, bool))
        and isinstance(obj, (int, float, complex))
    )


def isreal(obj):
    """
    Test if the argument is a real number (float or integer).

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (obj is not None)
        and (not isinstance(obj, bool))
        and isinstance(obj, (int, float))
    )
