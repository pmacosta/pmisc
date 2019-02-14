# pmisc_example_1.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,E1129,W0702

from __future__ import print_function
import os, pmisc


def ignored_example():
    fname = "somefile.tmp"
    open(fname, "w").close()
    print("File {0} exists? {1}".format(fname, os.path.isfile(fname)))
    with pmisc.ignored(OSError):
        os.remove(fname)
    print("File {0} exists? {1}".format(fname, os.path.isfile(fname)))
    with pmisc.ignored(OSError):
        os.remove(fname)
    print("No exception trying to remove a file that does not exists")
    try:
        with pmisc.ignored(RuntimeError):
            os.remove(fname)
    except:
        print("Got an exception")
