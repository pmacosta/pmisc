# pkgdata.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Global variables
###
VERSION_INFO = (1, 5, 3, "final", 0)
SUPPORTED_INTERPS = ["2.7", "3.5", "3.6", "3.7"]


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
