# pmisc_example_2.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

from __future__ import print_function
import pmisc


def timer(num_tries, fpointer):
    with pmisc.Timer() as tobj:
        for _ in range(num_tries):
            fpointer()
    print("Time per call: {0} seconds".format(tobj.elapsed_time / (2.0 * num_tries)))


def sample_func():
    count = 0
    for num in range(0, count):
        count += num
