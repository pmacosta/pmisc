# dicts.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import collections


###
# Classes
###
# Inspired from https://stackoverflow.com/
# questions/3387691/python-how-to-perfectly-override-a-dict
class CiDict(collections.MutableMapping):
    """
    Dictionary class with case-insensitive keys.

    Inspired by `<https://stackoverflow.com/
    questions/3387691/python-how-to-perfectly-override-a-dict>`_
    """

    def __init__(self, *args, **kwargs): # noqa
        # pylint: disable=W0231
        self._store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key): # noqa
        return self._store[self.__keytransform__(key)]

    def __setitem__(self, key, value): # noqa
        self._store[self.__keytransform__(key)] = value

    def __delitem__(self, key): # noqa
        del self._store[self.__keytransform__(key)]

    def __iter__(self): # noqa
        return iter(self._store)

    def __len__(self): # noqa
        return len(self._store)

    def __keytransform__(self, key): # noqa
        # pylint: disable=R0201
        return key.lower() if isinstance(key, str) else key
