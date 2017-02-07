# misc.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Intra-package imports
import pmisc


###
# Test functions
###
def test_flatten_list():
    """ Test flatten_list function behavior """
    obj = pmisc.flatten_list
    assert obj([1, 2, 3]) == [1, 2, 3]
    assert obj([1, [2, 3, 4], 5]) == [1, 2, 3, 4, 5]
    assert obj([1, [2, 3, [4, 5, 6]], 7]) == [1, 2, 3, 4, 5, 6, 7]
    ref = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert obj([1, [2, 3, [4, [5, 6, 7], 8, 9]], [10, 11], 12]) == ref
