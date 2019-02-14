# strings.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

# Standard library imports
from datetime import datetime
import inspect
import os
import struct
import sys

# Intra-package imports
import pmisc
from pmisc import AE, AI


###
# Test functions
###
def test_binary_string_to_octal_string():
    """Test binary_string_to_octal_string function behavior."""
    obj = pmisc.binary_string_to_octal_string
    if sys.hexversion < 0x03000000:
        ref = (
            "\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0"
            "\\b\\0\\t\\0\\n\\0\\v\\0\\f\\0\\r\\0\\16\\0"
        )
        actual = obj("".join([struct.pack("h", num) for num in range(1, 15)]))
        assert ref == actual
    else:
        ref = r"\o1\0\o2\0\o3\0\o4\0\o5\0\o6\0\a\0" r"\b\0\t\0\n\0\v\0\f\0\r\0\o16\0"
        code = lambda x: struct.pack("h", x).decode("ascii")
        actual = obj("".join([code(num) for num in range(1, 15)]))
        assert ref == actual


def test_char_string_to_decimal():
    """Test char_string_to_decimal_string function."""
    ref = "72 101 108 108 111 32 119 111 114 108 100 33"
    assert pmisc.char_to_decimal("Hello world!") == ref


def test_elapsed_time_string():
    """Test elapsed_time_string function behavior."""
    obj = pmisc.elapsed_time_string
    assert obj(datetime(2015, 1, 1), datetime(2015, 1, 1)) == "None"
    AE(
        obj,
        RuntimeError,
        "Invalid time delta specification",
        start_time=datetime(2015, 2, 1),
        stop_time=datetime(2015, 1, 1),
    )
    items = [
        ((2014, 1, 1), (2015, 1, 1), "1 year"),
        ((2014, 1, 1), (2016, 1, 1), "2 years"),
        ((2014, 1, 1), (2014, 1, 31), "1 month"),
        ((2014, 1, 1), (2014, 3, 2), "2 months"),
        ((2014, 1, 1, 10), (2014, 1, 1, 11), "1 hour"),
        ((2014, 1, 1, 10), (2014, 1, 1, 12), "2 hours"),
        ((2014, 1, 1, 1, 10), (2014, 1, 1, 1, 11), "1 minute"),
        ((2014, 1, 1, 1, 10), (2014, 1, 1, 1, 12), "2 minutes"),
        ((2014, 1, 1, 1, 10, 1), (2014, 1, 1, 1, 10, 2), "1 second"),
        ((2014, 1, 1, 1, 10, 1), (2014, 1, 1, 1, 10, 3), "2 seconds"),
        ((2014, 1, 1, 1, 10, 1), (2015, 1, 1, 1, 10, 2), "1 year and 1 second"),
        ((2014, 1, 1, 1, 10, 1), (2015, 1, 1, 1, 10, 3), "1 year and 2 seconds"),
        ((2014, 1, 1, 1, 10, 1), (2015, 1, 2, 1, 10, 3), "1 year, 1 day and 2 seconds"),
        (
            (2014, 1, 1, 1, 10, 1),
            (2015, 1, 3, 1, 10, 3),
            "1 year, 2 days and 2 seconds",
        ),
    ]
    for date1, date2, ref in items:
        assert obj(datetime(*date1), datetime(*date2)) == ref


def test_pcolor():
    """Test pcolor function behavior."""
    obj = pmisc.pcolor
    AI(obj, "text", text=5, color="red", indent=0)
    AI(obj, "color", text="hello", color=5, indent=0)
    AI(obj, "indent", text="hello", color="red", indent=5.1)
    exmsg = "Unknown color hello"
    AE(obj, ValueError, exmsg, text="hello", color="hello", indent=5)
    assert pmisc.pcolor("Text", "none", 5) == "     Text"
    assert pmisc.pcolor("Text", "blue", 2) == "\033[34m  Text\033[0m"
    # These statements should not raise any exception
    pmisc.pcolor("Text", "RED")
    pmisc.pcolor("Text", "NoNe")


def test_quote_str():
    """Test quote_str function behavior."""
    assert pmisc.quote_str(5) == 5
    assert pmisc.quote_str("Hello!") == '"Hello!"'
    assert pmisc.quote_str('He said "hello!"') == "'He said \"hello!\"'"


def test_strframe():
    """Test strframe function behavior."""
    obj = pmisc.strframe

    def check_basic_frame(lines):
        fname = pmisc.normalize_windows_fname(os.path.realpath(__file__))
        assert lines[0].startswith("\x1b[33mFrame object ID: 0x")
        assert lines[1].startswith(
            "File name......: {0}".format(fname.replace(".pyc", ".py"))
        )
        assert lines[2].startswith("Line number....: ")
        assert lines[3] == "Function name..: test_strframe"
        assert lines[4] == r"Context........: ['    fobj = inspect.stack()[0]\n']"
        assert lines[5] == "Index..........: 0"

    fobj = inspect.stack()[0]
    lines = obj(fobj).split("\n")
    check_basic_frame(lines)
    assert len(lines) == 6
    lines = [
        line
        for num, line in enumerate(obj(fobj, extended=True).split("\n"))
        if (num < 6) or line.startswith("f_")
    ]
    check_basic_frame(lines)
    assert lines[6].startswith("f_back ID......: 0x")
    assert lines[7].startswith("f_builtins.....: {")
    assert lines[8].startswith("f_code.........: " "<code object test_strframe at ")
    assert lines[9].startswith("f_globals......: {")
    assert lines[10].startswith("f_lasti........: ")
    assert lines[11].startswith("f_lineno.......: ")
    assert lines[12].startswith("f_locals.......: {")
    if sys.hexversion < 0x03000000:
        assert lines[13] == "f_restricted...: False"
        assert lines[14].startswith("f_trace........: ")
        assert len(lines) == 15
    else:
        assert lines[13].startswith("f_trace........: ")
        assert len(lines) == 14
