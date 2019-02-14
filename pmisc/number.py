# number.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import copy
from decimal import Decimal
from fractions import Fraction
import sys

# Intra-package imports
from .member import isiterable


###
# Functions
###
def _isclose(obja, objb, rtol=1e-05, atol=1e-08):
    """Return floating point equality."""
    return abs(obja - objb) <= (atol + rtol * abs(objb))


def _isreal(obj):
    """
    Determine if an object is a real number.

    Both Python standard data types and Numpy data types are supported.

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    # pylint: disable=W0702
    if (obj is None) or isinstance(obj, bool):
        return False
    try:
        cond = (int(obj) == obj) or (float(obj) == obj)
    except:
        return False
    return cond


def _no_exp(number):
    r"""
    Convert a number to a string without using scientific notation.

    :param number: Number to convert
    :type  number: integer or float

    :rtype: string

    :raises: RuntimeError (Argument \`number\` is not valid)
    """
    if isinstance(number, bool) or (not isinstance(number, (int, float))):
        raise RuntimeError("Argument `number` is not valid")
    mant, exp = _to_scientific_tuple(number)
    if not exp:
        return str(number)
    floating_mant = "." in mant
    mant = mant.replace(".", "")
    if exp < 0:
        return "0." + "0" * (-exp - 1) + mant
    if not floating_mant:
        return mant + "0" * exp + (".0" if isinstance(number, float) else "")
    lfpart = len(mant) - 1
    if lfpart < exp:
        return (mant + "0" * (exp - lfpart)).rstrip(".")
    return mant


def _to_scientific_tuple(number):
    r"""
    Return mantissa and exponent of a number expressed in scientific notation.

    Full precision is maintained if the number is represented as a string.

    :param number: Number
    :type  number: integer, float or string

    :rtype: Tuple whose first item is the mantissa (*string*) and the second
            item is the exponent (*integer*) of the number when expressed in
            scientific notation

    :raises: RuntimeError (Argument \`number\` is not valid)
    """
    # pylint: disable=W0632
    if isinstance(number, bool) or (not isinstance(number, (int, float, str))):
        raise RuntimeError("Argument `number` is not valid")
    convert = not isinstance(number, str)
    # Detect zero and return, simplifies subsequent algorithm
    if (convert and (not number)) or (
        (not convert) and (not number.strip("0").strip("."))
    ):
        return ("0", 0)
    # Break down number into its components, use Decimal type to
    # preserve resolution:
    # sign  : 0 -> +, 1 -> -
    # digits: tuple with digits of number
    # exp   : exponent that gives null fractional part
    sign, digits, exp = Decimal(str(number) if convert else number).as_tuple()
    mant = (
        "{sign}{itg}.{frac}".format(
            sign="-" if sign else "",
            itg=digits[0],
            frac="".join(str(item) for item in digits[1:]),
        )
        .rstrip("0")
        .rstrip(".")
    )
    exp += len(digits) - 1
    return (mant, exp)


def gcd(vector):
    """
    Calculate the greatest common divisor (GCD) of a sequence of numbers.

    The sequence can be a list of numbers or a Numpy vector of numbers. The
    computations are carried out with a precision of 1E-12 if the objects are
    not `fractions <https://docs.python.org/3/library/fractions.html>`_. When
    possible it is best to use the `fractions
    <https://docs.python.org/3/library/fractions.html>`_ data type with the
    numerator and denominator arguments when computing the GCD of floating
    point numbers.

    :param vector: Vector of numbers
    :type  vector: list of numbers or Numpy vector of numbers
    """
    # pylint: disable=C1801
    if not len(vector):
        return None
    if len(vector) == 1:
        return vector[0]
    if len(vector) == 2:
        return pgcd(vector[0], vector[1])
    current_gcd = pgcd(vector[0], vector[1])
    for element in vector[2:]:
        current_gcd = pgcd(current_gcd, element)
    return current_gcd


def normalize(value, series, offset=0):
    r"""
    Scale a value to the range defined by a series.

    :param value: Value to normalize
    :type  value: number

    :param series: List of numbers that defines the normalization range
    :type  series: list

    :param offset: Normalization offset, i.e. the returned value will be in
                   the range [**offset**, 1.0]
    :type  offset: number

    :rtype: number

    :raises:
     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Argument \`value\` is not valid)

     * ValueError (Argument \`offset\` has to be in the [0.0, 1.0] range)

     * ValueError (Argument \`value\` has to be within the bounds of the
       argument \`series\`)

    For example::

        >>> import pmisc
        >>> pmisc.normalize(15, [10, 20])
        0.5
        >>> pmisc.normalize(15, [10, 20], 0.5)
        0.75
    """
    if not _isreal(value):
        raise RuntimeError("Argument `value` is not valid")
    if not _isreal(offset):
        raise RuntimeError("Argument `offset` is not valid")
    try:
        smin = float(min(series))
        smax = float(max(series))
    except:
        raise RuntimeError("Argument `series` is not valid")
    value = float(value)
    offset = float(offset)
    if not 0 <= offset <= 1:
        raise ValueError("Argument `offset` has to be in the [0.0, 1.0] range")
    if not smin <= value <= smax:
        raise ValueError(
            "Argument `value` has to be within the bounds of argument `series`"
        )
    return offset + ((1.0 - offset) * (value - smin) / (smax - smin))


def per(arga, argb, prec=10):
    r"""
    Calculate percentage difference between numbers.

    If only two numbers are given, the percentage difference between them is
    computed. If two sequences of numbers are given (either two lists of
    numbers or Numpy vectors), the element-wise percentage difference is
    computed. If any of the numbers in the arguments is zero the value returned
    is the maximum floating-point number supported by the Python interpreter.

    :param arga: First number, list of numbers or Numpy vector
    :type  arga: float, integer, list of floats or integers, or Numpy vector
                 of floats or integers

    :param argb: Second number, list of numbers or or Numpy vector
    :type  argb: float, integer, list of floats or integers, or Numpy vector
                 of floats or integers

    :param prec: Maximum length of the fractional part of the result
    :type  prec: integer

    :rtype: Float, list of floats or Numpy vector, depending on the arguments
     type

    :raises:
     * RuntimeError (Argument \`arga\` is not valid)

     * RuntimeError (Argument \`argb\` is not valid)

     * RuntimeError (Argument \`prec\` is not valid)

     * TypeError (Arguments are not of the same type)
    """
    # pylint: disable=C0103,C0200,E1101,R0204
    if not isinstance(prec, int):
        raise RuntimeError("Argument `prec` is not valid")
    a_type = 1 * _isreal(arga) + 2 * (isiterable(arga) and not isinstance(arga, str))
    b_type = 1 * _isreal(argb) + 2 * (isiterable(argb) and not isinstance(argb, str))
    if not a_type:
        raise RuntimeError("Argument `arga` is not valid")
    if not b_type:
        raise RuntimeError("Argument `argb` is not valid")
    if a_type != b_type:
        raise TypeError("Arguments are not of the same type")
    if a_type == 1:
        arga, argb = float(arga), float(argb)
        num_min, num_max = min(arga, argb), max(arga, argb)
        return (
            0
            if _isclose(arga, argb)
            else (
                sys.float_info.max
                if _isclose(num_min, 0.0)
                else round((num_max / num_min) - 1, prec)
            )
        )
    # Contortions to handle lists and Numpy arrays without explicitly
    # having to import numpy
    ret = copy.copy(arga)
    for num, (x, y) in enumerate(zip(arga, argb)):
        if not _isreal(x):
            raise RuntimeError("Argument `arga` is not valid")
        if not _isreal(y):
            raise RuntimeError("Argument `argb` is not valid")
        x, y = float(x), float(y)
        ret[num] = (
            0
            if _isclose(x, y)
            else (
                sys.float_info.max
                if _isclose(x, 0.0) or _isclose(y, 0)
                else (round((max(x, y) / min(x, y)) - 1, prec))
            )
        )
    return ret


def pgcd(numa, numb):
    """
    Calculate the greatest common divisor (GCD) of two numbers.

    :param numa: First number
    :type  numa: number

    :param numb: Second number
    :type  numb: number

    :rtype: number

    For example:

        >>> import pmisc, fractions
        >>> pmisc.pgcd(10, 15)
        5
        >>> str(pmisc.pgcd(0.05, 0.02))
        '0.01'
        >>> str(pmisc.pgcd(5/3.0, 2/3.0))[:6]
        '0.3333'
        >>> pmisc.pgcd(
        ...     fractions.Fraction(str(5/3.0)),
        ...     fractions.Fraction(str(2/3.0))
        ... )
        Fraction(1, 3)
        >>> pmisc.pgcd(
        ...     fractions.Fraction(5, 3),
        ...     fractions.Fraction(2, 3)
        ... )
        Fraction(1, 3)
    """
    # Test for integers this way to be valid also for Numpy data types without
    # actually importing (and package depending on) Numpy
    int_args = (int(numa) == numa) and (int(numb) == numb)
    fraction_args = isinstance(numa, Fraction) and isinstance(numb, Fraction)
    # Force conversion for Numpy data types
    if int_args:
        numa, numb = int(numa), int(numb)
    elif not fraction_args:
        numa, numb = float(numa), float(numb)
    # Limit floating numbers to a "sane" fractional part resolution
    if (not int_args) and (not fraction_args):
        numa, numb = (
            Fraction(_no_exp(numa)).limit_denominator(),
            Fraction(_no_exp(numb)).limit_denominator(),
        )
    while numb:
        numa, numb = (
            numb,
            (numa % numb if int_args else (numa % numb).limit_denominator()),
        )
    return int(numa) if int_args else (numa if fraction_args else float(numa))
