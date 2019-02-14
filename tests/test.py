# test.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,C0414,E0401,E0611,R0201,R0205,R0903,R0915,W0212

# Standard library imports
from __future__ import print_function
import os
import sys

if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import pytest

if sys.hexversion < 0x03000000:
    import mock
# Intra-package imports
from pmisc import AI
from pmisc.test import _EXC_TRAPS
import pmisc


###
# Test functions
###
def test_assert_arg_invalid():  # noqa: D202
    """Test assert_arg_invalid function behavior."""

    def func1(par):
        if par == 1:
            raise RuntimeError("Argument `par` is not valid")

    pmisc.assert_arg_invalid(func1, "par", 1)
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_arg_invalid(func1, "par", 2)
    assert pmisc.get_exmsg(excinfo) == "Did not raise"


def test_assert_exception():  # noqa: D202
    """Test assert_exception function behavior."""

    class MyClass0(object):
        def meth1(self, par):
            if par:
                raise TypeError("meth1 exception")

        def meth2(self, par1, par2=0, par3=1):
            ttuple = (par1, par2, par3)
            if ttuple == (0, 1, 2):
                raise IOError("meth2 exception")
            return ttuple

    def func1(par1):
        if par1 == 1:
            raise RuntimeError("Exception 1")
        elif par1 == 2:
            raise ValueError("The number 1234 is invalid")

    pmisc.assert_exception(func1, RuntimeError, "Exception 1", par1=1)
    with pytest.raises(AssertionError):
        pmisc.assert_exception(func1, RuntimeError, "Exception 1", par1=0)
    pmisc.assert_exception(func1, ValueError, r"The number \d+ is invalid", par1=2)
    with pytest.raises(AssertionError):
        pmisc.assert_exception(func1, OSError, "Exception 5", par1=1)
    with pytest.raises(AssertionError):
        pmisc.assert_exception(func1, ValueError, "Exception message is wrong", par1=2)
    # Test passing of positional and/or keyword arguments
    cobj = MyClass0()
    pmisc.assert_exception(cobj.meth1, TypeError, "meth1 exception", True)
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_exception(cobj.meth1, TypeError, "meth1 exception", False)
    assert pmisc.get_exmsg(excinfo) == "Did not raise"
    pmisc.assert_exception(cobj.meth2, IOError, "meth2 exception", 0, 1, 2)
    pmisc.assert_exception(cobj.meth2, IOError, "meth2 exception", 0, par3=2, par2=1)
    pmisc.assert_exception(
        cobj.meth2, IOError, "meth2 exception", par3=2, par2=1, par1=0
    )
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_exception(cobj.meth2, IOError, "meth2 exception", 3)
    assert pmisc.get_exmsg(excinfo) == "Did not raise"
    with pytest.raises(RuntimeError) as excinfo:
        pmisc.assert_exception(cobj.meth1, TypeError, "meth1 exception", 0, 1, 2, 3, 4)
    assert pmisc.get_exmsg(excinfo) == "Illegal number of arguments"


def test_assert_prop():  # noqa: D202
    """Test assert_ro_prop function behavior."""

    class MyClass1(object):
        def __init__(self):
            self._value = 1

        def getter(self):
            return self._value

        def setter(self, value):
            self._value = int(value)

        value = property(getter, setter)

    # Test case that raises exception
    obj1 = MyClass1()
    msg = "invalid literal for int() with base 10: 'a'"
    pmisc.assert_prop(obj1, "value", "a", ValueError, msg)
    # Test case that does not raise exception
    try:
        pmisc.assert_prop(obj1, "value", 5.2, ValueError, msg)
    except AssertionError as eobj:
        actmsg = pmisc.get_exmsg(eobj)
        assert actmsg == "Did not raise"
    # Test case where unexpected exception is raised during evaluation
    try:
        pmisc.assert_prop("a", "value", 5.2, ValueError, msg)
    except AssertionError as eobj:
        pass


def test_assert_ro_prop():  # noqa: D202
    """Test assert_ro_prop function behavior."""

    class MyClass1(object):
        def __init__(self):
            self._value = 1

        def getter(self):
            return self._value

        value = property(getter)

    class MyClass2(object):
        def __init__(self):
            self._value = 1

        def getter(self):
            return self._value

        def deleter(self):
            del self._value

        value = property(getter, None, deleter)
        value = property(getter, None, deleter)

    # Test case where attribute cannot be deleted
    obj1 = MyClass1()
    pmisc.assert_ro_prop(obj1, "value")
    # Test case where attribute can be deleted
    obj2 = MyClass2()
    try:
        pmisc.assert_ro_prop(obj2, "value")
    except AssertionError as eobj:
        actmsg = pmisc.get_exmsg(eobj)
        assert actmsg == "Property can be deleted"
    # Test case where unexpected exception is raised during evaluation
    try:
        pmisc.assert_ro_prop("a", "")
    except AssertionError as eobj:
        actmsg = pmisc.get_exmsg(eobj)
        base = (
            "Raised exception mismatch"
            + os.linesep
            + "Expected: AttributeError (can't delete attribute)"
            + os.linesep
        )
        ref1 = base + "Got: SyntaxError ()"
        ref2 = base + "Got: SyntaxError (invalid syntax)"
        if actmsg not in (ref1, ref2):
            print(
                "Expected:"
                + os.linesep
                + ref1
                + os.linesep
                + "Or"
                + os.linesep
                + ref2
                + os.linesep
                + "Got:"
                + os.linesep
                + actmsg
            )
        assert actmsg in (ref1, ref2)


def test_comp_list_of_dicts():
    """Test comp_list_of_dicts function behavior."""
    list1 = []
    list2 = [{"a": 5, "b": 6}]
    assert not pmisc.comp_list_of_dicts(list1, list2)
    list1 = [{"a": 5}]
    list2 = [{"a": 5, "b": 6}]
    assert not pmisc.comp_list_of_dicts(list1, list2)
    list1 = [{"a": 5, "b": 6}]
    list2 = [{"a": 5, "b": 6}]
    assert pmisc.comp_list_of_dicts(list1, list2)


def test_compare_strings():
    """Test compare_string function behavior."""
    obj = pmisc.compare_strings
    AI(obj, "actual", 5, "a")
    AI(obj, "ref", "a", 5)
    AI(obj, "diff_mode", "a", "b", 2)
    obj("a", "a")
    actual = "Hello{0}world!{0}".format(os.linesep)
    ref = (
        "Hello{0}cruel{0}world{0}this{0}is{0}a{0}test{0}" "of{0}the{0}function"
    ).format(os.linesep)
    pcol = pmisc.pcolor
    cyan = lambda x: pcol(x, "cyan")
    red = lambda x: pcol(x, "red")
    yellow = lambda x: pcol(x, "yellow")
    output_ref_list = (
        cyan("<<<"),
        "Matching character",
        yellow("Mismatched character"),
        red("Extra character"),
        cyan("Reference text"),
        cyan("--------------"),
        cyan(" 1:") + " Hello",
        cyan(" 2:") + " " + yellow("cruel"),
        cyan(" 3:") + " " + red("world"),
        cyan(" 4:") + " " + red("this"),
        cyan(" 5:") + " " + red("is"),
        cyan(" 6:") + " " + red("a"),
        cyan(" 7:") + " " + red("test"),
        cyan(" 8:") + " " + red("of"),
        cyan(" 9:") + " " + red("the"),
        cyan("10:") + " " + red("function"),
        cyan("Actual text"),
        cyan("-----------"),
        cyan(" 1:") + " Hello",
        cyan(" 2:") + " " + yellow("world") + red("!"),
        cyan(" 3:") + " ",
        cyan(">>>"),
    )
    output_ref = os.linesep.join(output_ref_list)
    msg = "Strings do not match" + os.linesep + output_ref + os.linesep
    with pytest.raises(AssertionError) as excinfo:
        obj(actual, ref)
    actmsg = pmisc.get_exmsg(excinfo)
    if msg != actmsg:
        print(os.linesep + "Reference:")
        print(msg)
        print("Actual:")
        print(actmsg)
        print("----------")
    assert actmsg == msg
    output_ref_list = (
        cyan("<<<"),
        "Matching character",
        yellow("Mismatched character"),
        red("Extra character"),
        cyan("-------------------"),
        cyan(" 1 Ref.  :") + " Hello",
        cyan("   Actual:") + " Hello",
        cyan("-------------------"),
        cyan(" 2 Ref.  :") + " " + yellow("cruel"),
        cyan("   Actual:") + " " + yellow("world") + red("!"),
        cyan("-------------------"),
        cyan(" 3 Ref.  :") + " " + red("world"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 4 Ref.  :") + " " + red("this"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 5 Ref.  :") + " " + red("is"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 6 Ref.  :") + " " + red("a"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 7 Ref.  :") + " " + red("test"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 8 Ref.  :") + " " + red("of"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan(" 9 Ref.  :") + " " + red("the"),
        cyan("   Actual:") + " ",
        cyan("-------------------"),
        cyan("10 Ref.  :") + " " + red("function"),
        cyan("   Actual:") + " ",
        cyan(">>>"),
    )
    output_ref = os.linesep.join(output_ref_list)
    msg = "Strings do not match" + os.linesep + output_ref + os.linesep
    with pytest.raises(AssertionError) as excinfo:
        obj(actual, ref, True)
    actmsg = pmisc.get_exmsg(excinfo)
    if msg != actmsg:
        print(os.linesep + "Reference:")
        print(msg)
        print("Actual:")
        print(actmsg)
        print("----------")
    assert actmsg == msg


def test_exception_type_str():  # noqa: D202
    """Test exception_type_str function behavior."""

    class MyException(Exception):
        pass

    assert pmisc.exception_type_str(RuntimeError) == "RuntimeError"
    assert pmisc.exception_type_str(Exception) == "Exception"
    pmisc.compare_strings(pmisc.exception_type_str(MyException), "MyException")


def test_excepthook():
    """Test _excepthook function behavior."""
    test_path = os.path.dirname(os.path.abspath(__file__))
    test_fname = os.path.join(test_path, "test.py")

    def comp_output(act, ref, lineno=0):
        ref = [
            "Traceback (most recent call last):",
            '  File "{0}", line {1}, in test_excepthook'.format(test_fname, lineno),
        ] + ref
        tokens = act.split(os.linesep)
        pmisc.compare_strings(os.linesep.join(tokens), os.linesep.join(ref))

    class TmpMock(object):
        def __init__(self):
            self.msg = ""

        def _eprint(self, msg):
            self.msg = msg

        def _excepthook(self, exc_type, exc_value, exc_traceback):
            # pylint: disable=W0613
            self.msg = str(exc_type) + "|" + str(exc_value)

    class Class1(object):
        def __init__(self):
            self._value = None

        def _get_value(self):
            return self._value

        def _set_value(self, value):
            if value == 100:
                raise RuntimeError("Value is too big")
            self._value = value

        def _del_value(self):
            raise ValueError("An exception")

        value = property(_get_value, _set_value, _del_value)

    def func1(arg):
        if arg:
            raise RuntimeError("Custom exception")

    obj = TmpMock()
    exmsg = "My exception"
    ###
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_arg_invalid(func1, "arg", 1)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.assert_arg_invalid(func1, "arg", 1)',
        "AssertionError: Raised exception mismatch",
        "Expected: RuntimeError (Argument `arg` is not valid)",
        "Got: RuntimeError (Custom exception)",
    ]
    comp_output(obj.msg, ref, 359)
    ###
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_exception(func1, ValueError, exmsg, 0)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        "    pmisc.assert_exception(func1, ValueError, exmsg, 0)",
        "AssertionError: Did not raise",
    ]
    comp_output(obj.msg, ref, 371)
    ###
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_exception(func1, ValueError, exmsg, 1)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        "    pmisc.assert_exception(func1, ValueError, exmsg, 1)",
        "AssertionError: Raised exception mismatch",
        "Expected: ValueError (My exception)",
        "Got: RuntimeError (Custom exception)",
    ]
    comp_output(obj.msg, ref, 381)
    ###
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_exception(func1, RuntimeError, exmsg, 1)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        "    pmisc.assert_exception(func1, RuntimeError, exmsg, 1)",
        "AssertionError: Raised exception mismatch",
        "Expected: RuntimeError (My exception)",
        "Got: RuntimeError (Custom exception)",
    ]
    comp_output(obj.msg, ref, 393)
    ###
    obj2 = TmpMock()
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_ro_prop(obj2, "msg")
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.assert_ro_prop(obj2, "msg")',
        "AssertionError: Property can be deleted",
    ]
    comp_output(obj.msg, ref, 406)
    ###
    obj2 = Class1()
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_ro_prop(obj2, "value")
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.assert_ro_prop(obj2, "value")',
        "AssertionError: Raised exception mismatch",
        "Expected: AttributeError (can't delete attribute)",
        "Got: ValueError (An exception)",
    ]
    comp_output(obj.msg, ref, 417)
    ###
    with pytest.raises(AssertionError) as excinfo:
        pmisc.compare_strings("hello", "hello!")
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.compare_strings("hello", "hello!")',
        "AssertionError: Strings do not match",
        pmisc.pcolor("<<<", "cyan"),
        "Matching character",
        pmisc.pcolor("Mismatched character", "yellow"),
        pmisc.pcolor("Extra character", "red"),
        pmisc.pcolor("Reference text", "cyan"),
        pmisc.pcolor("--------------", "cyan"),
        pmisc.pcolor("1:", "cyan") + " hello" + pmisc.pcolor("!", "red"),
        pmisc.pcolor("Actual text", "cyan"),
        pmisc.pcolor("-----------", "cyan"),
        pmisc.pcolor("1:", "cyan") + " hello",
        pmisc.pcolor(">>>", "cyan"),
        "",
    ]
    comp_output(obj.msg, ref, 429)
    ### Test handling of an exception not in the pmisc.test module
    with pytest.raises(RuntimeError) as excinfo:
        func1(1)
    with mock.patch("pmisc.test._ORIG_EXCEPTHOOK", side_effect=obj._excepthook):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref1 = "<type 'exceptions.RuntimeError'>|Custom exception"
    ref2 = "<class 'RuntimeError'>|Custom exception"
    assert (obj.msg == ref1) or (obj.msg == ref2)
    ###
    test_obj = Class1()
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_prop(test_obj, "value", 1, RuntimeError, exmsg)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.assert_prop(test_obj, "value", 1, RuntimeError, exmsg)',
        "AssertionError: Did not raise",
    ]
    comp_output(obj.msg, ref, 460)
    ###
    test_obj = Class1()
    with pytest.raises(AssertionError) as excinfo:
        pmisc.assert_prop(test_obj, "value", 100, RuntimeError, exmsg)
    with mock.patch("pmisc.test._eprint", side_effect=obj._eprint):
        pmisc._excepthook(excinfo.type, excinfo.value, excinfo.tb)
    ref = [
        '    pmisc.assert_prop(test_obj, "value", 100, RuntimeError, exmsg)',
        "AssertionError: Raised exception mismatch",
        "Expected: RuntimeError (My exception)",
        "Got: RuntimeError (Value is too big)",
    ]
    comp_output(obj.msg, ref, 471)


def test_del_pmisc_test_frames():
    """Test _remove_test_module_frame function behavior."""
    obj = pmisc.test._del_pmisc_test_frames
    line1 = 491
    line2 = _EXC_TRAPS[0][2]
    line3 = 507

    def func1():
        raise RuntimeError("Sample exception")  # <-- line1

    def get_last_tb(tbk):
        item = tbk
        while item:
            if not item.tb_next:
                break
            item = item.tb_next
        return item

    with pytest.raises(RuntimeError) as excinfo:
        func1()
    obj(excinfo)
    assert get_last_tb(excinfo.tb).tb_lineno == line1
    eobj = RuntimeError("DID NOT RAISE")
    with pytest.raises(AssertionError) as excinfo:
        pmisc.test._raise_if_not_raised(eobj)  # <-- line3
    assert get_last_tb(excinfo.tb).tb_lineno == line2
    assert get_last_tb(excinfo.traceback[-1]._rawentry).tb_lineno == line2
    assert "{0} in _raise_if_not_raised".format(line2) in str(excinfo.traceback[-1])
    excinfo = obj(excinfo)
    assert get_last_tb(excinfo.tb).tb_lineno == line3
    assert "{0} in test_del_pmisc_test_frames".format(line3) in str(
        excinfo.traceback[-1]
    )
    assert get_last_tb(excinfo.traceback[-1]._rawentry).tb_lineno == line3
