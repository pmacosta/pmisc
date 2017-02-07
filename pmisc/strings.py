# strings.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Intra-package imports
from .file import normalize_windows_fname


###
# Global constants
###
_OCTAL_ALPHABET = [
    chr(_NUM)
    if (_NUM >= 32) and (_NUM <= 126) else
    '\\'+str(oct(_NUM)).lstrip('0')
    for _NUM in range(0, 256)
]
_OCTAL_ALPHABET[0] = '\\0'   # Null character
_OCTAL_ALPHABET[7] = '\\a'   # Bell/alarm
_OCTAL_ALPHABET[8] = '\\b'   # Back space
_OCTAL_ALPHABET[9] = '\\t'   # Horizontal tab
_OCTAL_ALPHABET[10] = '\\n'  # Line feed
_OCTAL_ALPHABET[11] = '\\v'  # Vertical tab
_OCTAL_ALPHABET[12] = '\\f'  # Form feed
_OCTAL_ALPHABET[13] = '\\r'  # Carriage return


###
# Functions
###
def binary_string_to_octal_string(text):
    r"""
    Returns a binary-packed string in octal representation aliasing typical
    codes to their escape sequences

    :param  text: Text to convert
    :type   text: string

    :rtype: string

    +------+-------+-----------------+
    | Code | Alias |   Description   |
    +======+=======+=================+
    |    0 |   \\0 | Null character  |
    +------+-------+-----------------+
    |    7 |   \\a | Bell / alarm    |
    +------+-------+-----------------+
    |    8 |   \\b | Backspace       |
    +------+-------+-----------------+
    |    9 |   \\t | Horizontal tab  |
    +------+-------+-----------------+
    |   10 |   \\n | Line feed       |
    +------+-------+-----------------+
    |   11 |   \\v | Vertical tab    |
    +------+-------+-----------------+
    |   12 |   \\f | Form feed       |
    +------+-------+-----------------+
    |   13 |   \\r | Carriage return |
    +------+-------+-----------------+

    For example:

        >>> import pmisc, struct, sys
        >>> def py23struct(num):
        ...    if sys.hexversion < 0x03000000:
        ...        return struct.pack('h', num)
        ...    else:
        ...        return struct.pack('h', num).decode('ascii')
        >>> nums = range(1, 15)
        >>> pmisc.binary_string_to_octal_string(
        ...     ''.join([py23struct(num) for num in nums])
        ... ).replace('o', '')  #doctest: +ELLIPSIS
        '\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0\\b\\0\\t\\0\\...
    """
    # pylint: disable=C0103
    return ''.join([_OCTAL_ALPHABET[ord(char)] for char in text])


def char_to_decimal(text):
    """
    Converts a string to its decimal ASCII representation, with spaces between
    characters

    :param text: Text to convert
    :type  text: string

    :rtype: string

    For example:

        >>> import pmisc
        >>> pmisc.char_to_decimal('Hello world!')
        '72 101 108 108 111 32 119 111 114 108 100 33'
    """
    return ' '.join([str(ord(char)) for char in text])


def elapsed_time_string(start_time, stop_time):
    r"""
    Returns a formatted string with the elapsed time between two time points.
    The string includes years (365 days), months (30 days), days (24 hours),
    hours (60 minutes), minutes (60 seconds) and seconds. If both arguments
    are equal, the string returned is :code:`'None'`; otherwise, the string
    returned is [YY year[s], [MM month[s], [DD day[s], [HH hour[s],
    [MM minute[s] [and SS second[s\]\]\]\]\]\]. Any part (year[s], month[s],
    etc.) is omitted if the value of that part is null/zero

    :param start_time: Starting time point
    :type  start_time: `datetime <https://docs.python.org/2/library/
                       datetime.html#datetime-objects>`_

    :param stop_time: Ending time point
    :type  stop_time: `datetime`

    :rtype: string

    :raises: RuntimeError (Invalid time delta specification)

    For example:

        >>> import datetime, pmisc
        >>> start_time = datetime.datetime(2014, 1, 1, 1, 10, 1)
        >>> stop_time = datetime.datetime(2015, 1, 3, 1, 10, 3)
        >>> pmisc.elapsed_time_string(start_time, stop_time)
        '1 year, 2 days and 2 seconds'
    """
    if start_time > stop_time:
        raise RuntimeError('Invalid time delta specification')
    delta_time = stop_time-start_time
    # Python 2.6 datetime objects do not have total_seconds() method
    tot_seconds = int(
        (
            delta_time.microseconds+
            (delta_time.seconds+delta_time.days*24*3600)*10**6
        )
        /
        10**6
    )
    years, remainder = divmod(tot_seconds, 365*24*60*60)
    months, remainder = divmod(remainder, 30*24*60*60)
    days, remainder = divmod(remainder, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)
    token_iter = zip(
        [years, months, days, hours, minutes, seconds],
        ['year', 'month', 'day', 'hour', 'minute', 'second']
    )
    ret_list = [
        '{token} {token_name}{plural}'.format(
            token=num, token_name=desc, plural='s' if num > 1 else ''
        ) for num, desc in token_iter if num > 0
    ]
    if len(ret_list) == 0:
        return 'None'
    elif len(ret_list) == 1:
        return ret_list[0]
    elif len(ret_list) == 2:
        return ret_list[0]+' and '+ret_list[1]
    else:
        return (', '.join(ret_list[0:-1]))+' and '+ret_list[-1]


def pcolor(text, color, indent=0):
    r"""
    Returns a string that once printed is colorized

    :param text: Text to colorize
    :type  text: string

    :param  color: Color to use, one of :code:`'black'`, :code:`'red'`,
                   :code:`'green'`, :code:`'yellow'`, :code:`'blue'`,
                   :code:`'magenta'`, :code:`'cyan'`, :code:`'white'` or
                   :code:`'none'` (case insensitive)
    :type   color: string

    :param indent: Number of spaces to prefix the output with
    :type  indent: integer

    :rtype: string

    :raises:
     * RuntimeError (Argument \`color\` is not valid)

     * RuntimeError (Argument \`indent\` is not valid)

     * RuntimeError (Argument \`text\` is not valid)

     * ValueError (Unknown color *[color]*)
    """
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35,
        'cyan':36, 'white':37, 'none':-1
    }
    if not isinstance(text, str):
        raise RuntimeError('Argument `text` is not valid')
    if not isinstance(color, str):
        raise RuntimeError('Argument `color` is not valid')
    if not isinstance(indent, int):
        raise RuntimeError('Argument `indent` is not valid')
    color = color.lower()
    if color not in esc_dict:
        raise ValueError('Unknown color {color}'.format(color=color))
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color], indent=' '*indent, text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def quote_str(obj):
    """
    Adds extra quotes to a string. If the argument is not a string it is
    returned unmodified

    :param obj: Object
    :type  obj: any

    :rtype: Same as argument

    For example:

        >>> import pmisc
        >>> pmisc.quote_str(5)
        5
        >>> pmisc.quote_str('Hello!')
        '"Hello!"'
        >>> pmisc.quote_str('He said "hello!"')
        '\\'He said "hello!"\\''
    """
    if not isinstance(obj, str):
        return obj
    else:
        return (
            "'{obj}'".format(obj=obj)
            if '"' in obj else
            '"{obj}"'.format(obj=obj)
        )


def strframe(obj, extended=False):
    """
    Returns a string with a frame record (typically an item in a list generated
    by `inspect.stack()
    <https://docs.python.org/2/library/inspect.html#inspect.stack>`_) pretty
    printed

    :param obj: Frame record
    :type  obj: tuple

    :param extended: Flag that indicates whether contents of the frame object
                     are printed (True) or not (False)
    :type  extended: boolean

    :rtype:     string
    """
    # Stack frame -> (frame object [0], filename [1], line number of current
    # line [2], function name [3], list of lines of context from source
    # code [4], index of current line within list [5])
    fname = normalize_windows_fname(obj[1])
    ret = list()
    ret.append(
        pcolor('Frame object ID: {0}'.format(hex(id(obj[0]))), 'yellow')
    )
    ret.append('File name......: {0}'.format(fname))
    ret.append('Line number....: {0}'.format(obj[2]))
    ret.append('Function name..: {0}'.format(obj[3]))
    ret.append('Context........: {0}'.format(obj[4]))
    ret.append('Index..........: {0}'.format(obj[5]))
    if extended:
        ret.append('f_back ID......: {0}'.format(hex(id(obj[0].f_back))))
        ret.append('f_builtins.....: {0}'.format(obj[0].f_builtins))
        ret.append('f_code.........: {0}'.format(obj[0].f_code))
        ret.append('f_globals......: {0}'.format(obj[0].f_globals))
        ret.append('f_lasti........: {0}'.format(obj[0].f_lasti))
        ret.append('f_lineno.......: {0}'.format(obj[0].f_lineno))
        ret.append('f_locals.......: {0}'.format(obj[0].f_locals))
        if hasattr(obj[0], 'f_restricted'): # pragma: no cover
            ret.append('f_restricted...: {0}'.format(obj[0].f_restricted))
        ret.append('f_trace........: {0}'.format(obj[0].f_trace))
    return '\n'.join(ret)
