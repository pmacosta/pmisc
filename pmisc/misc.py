# misc.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Functions
###
def flatten_list(lobj):
    """
    Recursively flattens a list.

    :param lobj: List to flatten
    :type  lobj: list

    :rtype: list

    For example:

        >>> import pmisc
        >>> pmisc.flatten_list([1, [2, 3, [4, 5, 6]], 7])
        [1, 2, 3, 4, 5, 6, 7]
    """
    ret = []
    for item in lobj:
        if isinstance(item, list):
            for sub_item in flatten_list(item):
                ret.append(sub_item)
        else:
            ret.append(item)
    return ret
