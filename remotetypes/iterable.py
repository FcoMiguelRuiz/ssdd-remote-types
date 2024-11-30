"""Needed classes for implementing the Iterable interface for different types of objects."""

from typing import Optional

import Ice
import RemoteTypes as rt


class IterableDict(rt.Iterable):
    def __init__(self, remote_dict):
        self._remote_dict = remote_dict
        self._iterator = iter(self._remote_dict._storage_.items())
        self._initial_hash = self._remote_dict.hash()

    def next(self, current: Optional[Ice.Current] = None):
        current_hash = self._remote_dict.hash()
        if current_hash != self._initial_hash:
            raise rt.CancelIteration()
        try:
            clave,valor = next(self._iterator)
            return clave
        except StopIteration as error:
            raise StopIteration("No more items in the RemoteDict.") from error

class IterableSet(rt.Iterable):
    def __init__(self, remote_set):
        self._remote_set = remote_set
        self._iterator = iter(remote_set._storage_)
        self._initial_hash = remote_set.hash()

    def next(self, current: Optional[Ice.Current] = None):
        current_hash = self._remote_set.hash()
        if current_hash != self._initial_hash:
            raise rt.CancelIteration()

        try:
            return next(self._iterator)
        except StopIteration as error:
            raise StopIteration("No more items in the RemoteSet.") from error

class IterableList(rt.Iterable):
    def __init__(self, remote_list):
        self._remote_list = remote_list
        self._iterator = iter(remote_list._storage_)
        self._initial_hash = remote_list.hash()

    def next(self, current: Optional[Ice.Current] = None):
        current_hash = self._remote_list.hash()
        if current_hash != self._initial_hash:
            raise rt.CancelIteration()

        try:
            return next(self._iterator)
        except StopIteration as error:
            raise StopIteration("No more items in the RemoteList.") from error
