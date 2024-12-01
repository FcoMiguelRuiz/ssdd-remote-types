"""Needed classes to implement and serve the RList type."""

import json
import os
from typing import Optional

import Ice
import RemoteTypes as rt # noqa: F401; pylint: disable=import-error


class RemoteList(rt.RList):
    """Skelenton for the RList implementation."""

    def __init__(self, identifier, adapter: Ice.ObjectAdapter) -> None:
        self.id_ = identifier
        self.archivo = os.path.join("almacen", identifier + "_list.json")
        self._storage_ = []

        try:
            with open(self.archivo, "r") as file:
                self._storage_ = json.load(file)

        except FileNotFoundError:
            self._storage_ = []
            self.escribir_lista()

        except json.JSONDecodeError:
            self._storage_ = []
            self.escribir_lista()

        identity = Ice.Identity(identifier, "RemoteList")
        adapter.add(self, identity)

    def escribir_lista(self):
        with open(self.archivo, "w") as file:
            json.dump(self._storage_, file)

    def remove(self, item: str, current: Optional[Ice.Current] = None) -> None:
        try:
            self._storage_.remove(item)
            self.escribir_lista()
        except ValueError as error:
            raise rt.KeyError(item) from error

    def length(self, current: Optional[Ice.Current] = None) -> int:
        return len(self._storage_)

    def contains(self, item: str, current: Optional[Ice.Current] = None) -> bool:
        return item in self._storage_

    def hash(self, current: Optional[Ice.Current] = None) -> int:
        return hash(repr(self._storage_))

    def append(self, item: str, current: Optional[Ice.Current] = None) -> None:
        self._storage_.append(item)
        self.escribir_lista()

    def pop(self, index: Optional[int] = None, current: Optional[Ice.Current] = None) -> str:
        try:
            if index is None:
                item = self._storage_.pop()
            else:
                item = self._storage_.pop(index)

            self.escribir_lista()
            return item
        except IndexError as error:
            raise IndexError() from error

    def getItem(self, index: int, current: Optional[Ice.Current] = None) -> str:
        try:
            return self._storage_[index]
        except IndexError as error:
            raise IndexError() from error

    def iter(self, current: Optional[Ice.Current] = None) -> rt.IterablePrx:
        from remotetypes.iterable import IterableList

        iterator = IterableList(self)      
        proxy = current.adapter.addWithUUID(iterator)
        return rt.IterablePrx.uncheckedCast(proxy)
