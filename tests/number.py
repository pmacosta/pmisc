# number.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,W0212

# Standard library imports
from fractions import Fraction
# PyPI imports
import pytest
# Intra-package imports
import pmisc
from pmisc import AE, AI


###
# Test functions
###
@pytest.mark.parametrize(
    'num, ref', [
    (0, '0'),
    (0.0, '0.0'),
    (4, '4'),
    (4.0, '4.0'),
    (45, '45'),
    (450, '450'),
    (1234567, '1234567'),
    (4.5, '4.5'),
    (4.1234, '4.1234'),
    (4123.4E4, '41234000'),
    (0.1, '0.1'),
    (1.43E-2, '0.0143'),
    (100000000.0, '100000000.0'),
    (1000000, '1000000'),
    (1e3, '1000.0'),
    ]
)
def test_no_exp(num, ref):
    """ Test _no_exp function behavior """
    assert pmisc.number._no_exp(num) == ref


def test_no_exp_exceptions():
    """ Test _no_exp function exceptions """
    AI(pmisc.number._no_exp, 'number', number='a')


def test_to_scientific_tuple_exceptions():
    """ Test _to_scientific_tuple function exceptions """
    AI(pmisc.number._to_scientific_tuple, 'number', number=5+3j)


def test_gcd():
    """ Test gcd function behavior """
    assert pmisc.gcd([]) is None
    assert pmisc.gcd([7]) == 7
    assert pmisc.gcd([48, 18]) == 6
    assert pmisc.gcd([20, 12, 16]) == 4
    ref = [Fraction(5, 3), Fraction(2, 3), Fraction(10, 3)]
    assert pmisc.gcd(ref) == Fraction(1, 3)


def test_normalize():
    """ Test normalize function behavior """
    obj = pmisc.normalize
    AI(obj, 'value', value='a', series=[2, 5], offset=10)
    AI(obj, 'offset', value=5, series=[2, 5], offset='a')
    AI(obj, 'series', value=5, series=['a', 'b'])
    exmsg = 'Argument `offset` has to be in the [0.0, 1.0] range'
    AE(obj, ValueError, exmsg, value=5, series=[2, 5], offset=10)
    exmsg = 'Argument `value` has to be within the bounds of argument `series`'
    AE(obj, ValueError, exmsg, value=0, series=[2, 5], offset=0)
    assert pmisc.normalize(15, [10, 20]) == 0.5
    assert pmisc.normalize(15, [10, 20], 0.5) == 0.75


def test_per():
    """ Test per function behavior """
    obj = pmisc.per
    AI(obj, 'prec', arga=5, argb=7, prec='Hello')
    AI(obj, 'arga', arga='Hello', argb=7, prec=1)
    AI(obj, 'arga', arga=[1, 'a', 3], argb=[4, 6, 7], prec=1)
    AI(obj, 'argb', arga=5, argb='Hello', prec=1)
    AI(obj, 'argb', arga=[1, 2, 3], argb=[4, 'a', 7], prec=1)
    exmsg = 'Arguments are not of the same type'
    AE(obj, TypeError, exmsg, arga=5, argb=[5, 7], prec=1)
    assert obj(3, 2, 1) == 0.5
    assert obj(3.1, 3.1, 1) == 0
    ttuple = zip(obj([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])
    assert all([test == ref for test, ref in ttuple])
    ttuple = zip(obj([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])
    assert all([test == ref for test, ref in ttuple])
    assert obj(4, 3, 3) == 0.333
    assert obj(4, 0, 3) == 1e20
    ttuple = zip(obj([3, 1.1, 5], [2, 0, 2], 1), [0.5, 1e20, 1.5])
    assert all([test == ref for test, ref in ttuple])


def test_pgcd():
    """ Test pgcd function behavior """
    assert pmisc.pgcd(48, 18) == 6
    assert pmisc.pgcd(3, 4) == 1
    assert pmisc.pgcd(0.05, 0.02) == 0.01
    assert pmisc.pgcd(5, 2) == 1
    assert pmisc.pgcd(Fraction(5, 3), Fraction(2, 3)) == Fraction(1, 3)
