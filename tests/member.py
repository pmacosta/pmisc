# member.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Intra-package imports
import pmisc


###
# Test functions
###
def test_isalpha():
    """Test isalpha function behavior."""
    assert not pmisc.isalpha(3)
    assert not pmisc.isalpha(1.5)
    assert not pmisc.isalpha(1 + 2j)
    assert not pmisc.isalpha("1EA-20")
    assert pmisc.isalpha("1.5")
    assert pmisc.isalpha("1E-20")


def test_ishex():
    """Test ishex function behavior."""
    assert not pmisc.ishex(5)
    assert not pmisc.ishex("45")
    assert pmisc.ishex("F")
    assert pmisc.ishex("f")


def test_isiterable():
    """Test isiterable function behavior."""
    assert pmisc.isiterable([1, 2, 3])
    assert pmisc.isiterable({"a": 5})
    assert pmisc.isiterable(set([1, 2, 3]))
    assert not pmisc.isiterable(3)


def test_isnumber():
    """Test isnumber function behavior."""
    assert pmisc.isnumber(5)
    assert pmisc.isnumber(1.5)
    assert pmisc.isnumber(complex(3.2, 9.5))
    assert not pmisc.isnumber("a")
    assert not pmisc.isnumber(True)


def test_isreal():
    """Test isreal function behavior."""
    assert pmisc.isreal(5)
    assert pmisc.isreal(1.5)
    assert not pmisc.isreal(complex(3.2, 9.5))
    assert not pmisc.isreal("a")
    assert not pmisc.isreal(True)
