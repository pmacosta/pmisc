# pkgdata.py
# Copyright (c) 2013-2020 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os


###
# Global variables
###
VERSION_INFO = (1, 5, 11, "final", 0)
SUPPORTED_INTERPS = ["3.5", "3.6", "3.7", "3.8"]
COPYRIGHT_START = 2013
PKG_DESC = (
    "Miscellaneous utility functions that can be applied in a variety of circumstances"
)
PKG_LONG_DESC = (
    "This module contains miscellaneous utility functions that can be applied in a "
    + "variety of circumstances; there are context managers, membership functions "
    + "(test if an argument is of a given type), numerical functions, string "
    + "functions and functions to aid in the unit testing of modules "
    + ""
    + os.linesep
    + "`Pytest`_ is the supported test runner"
)
PKG_PIPELINE_ID = 3


###
# Functions
###
def _make_version(major, minor, micro, level, serial):
    """Generate version string from tuple (almost entirely from coveragepy)."""
    level_dict = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
    if level not in level_dict:
        raise RuntimeError("Invalid release level")
    version = "{0:d}.{1:d}".format(major, minor)
    if micro:
        version += ".{0:d}".format(micro)
    if level != "final":
        version += "{0}{1:d}".format(level_dict[level], serial)
    return version


__version__ = _make_version(*VERSION_INFO)
