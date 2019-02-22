# __init__.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,W0401
"""Miscellaneous functions."""
# Standard library imports
import sys

# Intra-package imports
from .pkgdata import __version__
from .ctx import *
from .dicts import *
from .file import *
from .member import *
from .misc import *
from .number import *
from .rst import *
from .strings import *
from .test import *
from .test import _excepthook

sys.excepthook = _excepthook
