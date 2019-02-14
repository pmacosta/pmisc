# dicts.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# PyPI imports
import pytest

# Intra-package imports
import pmisc
from pmisc import GET_EXMSG


###
# Functions
###
def test_cidict():
    """Test CiDict class."""
    assert pmisc.CiDict() == {}
    obj = pmisc.CiDict(one=1, TwO=2, tHrEe=3, FOUR=4)
    assert obj == {"one": 1, "two": 2, "three": 3, "four": 4}
    assert obj["four"] == 4
    obj["FIve"] = 5
    assert "four" in obj
    assert "FOUR" in obj
    assert len(obj) == 5
    assert obj == {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    assert obj["five"] == 5
    assert len(obj) == 5
    del obj["five"]
    assert obj == {"one": 1, "two": 2, "three": 3, "four": 4}
    obj = pmisc.CiDict(zip(["aa", "bb", "cc"], [10, 20, 30]))
    assert obj == {"aa": 10, "bb": 20, "cc": 30}
    with pytest.raises(TypeError) as excinfo:
        pmisc.CiDict(zip(["aa", "bb", [1, 2]], [10, 20, 30]))
    assert GET_EXMSG(excinfo) == "unhashable type: 'list'"
    with pytest.raises(ValueError) as excinfo:
        pmisc.CiDict(["Prop1", "Prop2", "Prop3", "Prop4"])
    msg = "dictionary update sequence element #0 has length 5; 2 is required"
    assert GET_EXMSG(excinfo) == msg
