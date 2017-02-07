# number.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import copy
from decimal import Decimal
from fractions import Fraction
# Intra-package imports
from .member import isiterable, isreal


###
# Functions
###
def _no_exp(number):
    r"""
    Converts a number to a string guaranteeing that the result is not
    expressed in scientific notation

    :param number: Number to convert
    :type  number: integer or float

    :rtype: string

    :raises: RuntimeError (Argument \`number\` is not valid)
    """
    if not any([isinstance(number, item) for item in [int, float]]):
        raise RuntimeError('Argument `number` is not valid')
    mant, exp = _to_scientific_tuple(number)
    if not exp:
        return str(number)
    floating_mant = '.' in mant
    mant = mant.replace('.', '')
    if exp < 0:
        return '0.'+'0'*(-exp-1)+mant
    if not floating_mant:
        return mant+'0'*exp+('.0' if isinstance(number, float) else '')
    lfpart = len(mant)-1
    if lfpart < exp:
        return (mant+'0'*(exp-lfpart)).rstrip('.')
    return mant


def _to_scientific_tuple(number):
    """
    Returns mantissa and exponent of a number when expressed in
    scientific notation. Full precision is maintained if the number is
    represented as a string

    :param number: Number
    :type  number: integer, float or string

    :rtype: named tuple in which the first item is the mantissa (*string*)
            and the second item is the exponent (*integer*) of the number
            when expressed in scientific notation
    """
    # pylint: disable=W0632
    if not any([isinstance(number, item) for item in [int, float, str]]):
        raise RuntimeError('Argument `number` is not valid')
    convert = not isinstance(number, str)
    # Detect zero and return, simplifies subsequent algorithm
    if ((convert and (number == 0)) or
       ((not convert) and (not number.strip('0').strip('.')))):
        return ('0', 0)
    # Break down number into its components, use Decimal type to
    # preserve resolution:
    # sign  : 0 -> +, 1 -> -
    # digits: tuple with digits of number
    # exp   : exponent that gives null fractional part
    sign, digits, exp = Decimal(str(number) if convert else number).as_tuple()
    mant = '{sign}{itg}{frac}'.format(
        sign='-' if sign else '',
        itg=digits[0],
        frac=(
            '.{frac}'.format(frac=''.join([str(num) for num in digits[1:]]))
            if len(digits) > 1 else
            ''
        )
    ).rstrip('0').rstrip('.')
    exp += len(digits)-1
    return (mant, exp)


def gcd(vector):
    """
    Calculates the greatest common divisor (GCD) of a list of numbers or a
    Numpy vector of numbers. The computations are carried out with a precision
    of 1E-12 if the objects are not
    `fractions <https://docs.python.org/2/library/fractions.html>`_. When
    possible it is best to use the `fractions
    <https://docs.python.org/2/library/fractions.html>`_ data type with
    the numerator and denominator arguments when computing the GCD of
    floating point numbers.

    :param vector: Vector of numbers
    :type  vector: list of numbers or Numpy vector of numbers
    """
    if len(vector) == 0:
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
    Scales a value to the range defined by a series

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
    if not isreal(value):
        raise RuntimeError('Argument `value` is not valid')
    if not isreal(offset):
        raise RuntimeError('Argument `offset` is not valid')
    try:
        assert isreal(min(series))
        assert isreal(max(series))
    except AssertionError:
        raise RuntimeError('Argument `series` is not valid')
    if (offset < 0) or (offset > 1):
        raise ValueError('Argument `offset` has to be in the [0.0, 1.0] range')
    if (value < min(series)) or (value > max(series)):
        raise ValueError(
            'Argument `value` has to be within the bounds of argument `series`'
        )
    return (
        offset+((1.0-offset)*
        ((value-float(min(series)))/(float(max(series))-float(min(series)))))
    )


def per(arga, argb, prec=10):
    r"""
    Calculates the percentage difference between two numbers or the
    element-wise percentage difference between two lists of numbers or Numpy
    vectors. If any of the numbers in the arguments is zero the value returned
    is 1E+20

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
        raise RuntimeError('Argument `prec` is not valid')
    arga_type = (
        1
        if isreal(arga) else (
            2 if isiterable(arga) and not isinstance(arga, str) else 0
        )
    )
    argb_type = (
        1
        if isreal(argb) else (
            2 if isiterable(argb) and not isinstance(argb, str) else 0
        )
    )
    if not arga_type:
        raise RuntimeError('Argument `arga` is not valid')
    if not argb_type:
        raise RuntimeError('Argument `argb` is not valid')
    if arga_type != argb_type:
        raise TypeError('Arguments are not of the same type')
    if arga_type == 1:
        arga = float(arga)
        argb = float(argb)
        num_max = max(arga, argb)
        num_min = min(arga, argb)
        return (
            0
            if arga == argb else
            (1e20 if (not num_min) else round((num_max/num_min)-1, prec))
        )
    else:
        # Contortions to handle lists and Numpy arrays without explicitly
        # having to import numpy
        ret = copy.copy(arga)
        for num, (x, y) in enumerate(zip(arga, argb)):
            if not isreal(x):
                raise RuntimeError('Argument `arga` is not valid')
            if not isreal(y):
                raise RuntimeError('Argument `argb` is not valid')
            x = float(x)
            y = float(y)
            ret[num] = (
                0
                if x == y else (
                    1E20 if (x == 0) or (y == 0) else (
                        round((max(x, y)/min(x, y))-1, prec)
                    )
                )
            )
        return ret


def pgcd(numa, numb):
    """
    Calculate the greatest common divisor (GCD) of two numbers

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
    int_args = isinstance(numa, int) and isinstance(numb, int)
    fraction_args = isinstance(numa, Fraction) and isinstance(numb, Fraction)
    # Limit floating numbers to a "sane" fractional part resolution
    if (not int_args) and (not fraction_args):
        numa, numb = (
            Fraction(_no_exp(numa)).limit_denominator(),
            Fraction(_no_exp(numb)).limit_denominator()
        )
    while numb:
        numa, numb = (
            numb,
            (numa % numb if int_args else (numa % numb).limit_denominator())
        )
    return int(numa) if int_args else (numa if fraction_args else float(numa))
