"""Needed classes to implement and serve the RSet type."""

import json
import os
from typing import Optional

import Ice
import RemoteTypes as rt  # noqa: F401; pylint: disable=import-error

from remotetypes.customset import StringSet


class RemoteSet(rt.RSet):
    """Implementation of the remote interface RSet."""


    def __init__(self, identifier, adapter: Ice.ObjectAdapter) -> None:
        self.id_ = identifier
        self.archivo = os.path.join("almacen", identifier + "_set.json")
        self._storage_ = StringSet()

        try:
            with open(self.archivo, "r") as file:
                contenido = file.read().strip()
                valores = json.loads(contenido)
                for valor in valores:
                    self.add(valor)

        except FileNotFoundError:
            self._storage_ = StringSet()
            self.escribir_set()

        except json.JSONDecodeError:
            self._storage_ = StringSet()
            self.escribir_set()

        identity = Ice.Identity(identifier, "RemoteSet")
        adapter.add(self, identity)

    def escribir_set(self):
        with open(self.archivo, "w") as file:
            json.dump(list(self._storage_), file, indent=4)

    def identifier(self, current: Optional[Ice.Current] = None) -> str:
        """Return the identifier of the object."""
        return self.id_

    def remove(self, item: str, current: Optional[Ice.Current] = None) -> None:
        """Remove an item from the StringSet if added. Else, raise a remote exception."""
        try:
            self._storage_.remove(item)
            self.escribir_set()
        except KeyError as error:
            raise rt.KeyError(item) from error

    def length(self, current: Optional[Ice.Current] = None) -> int:
        """Return the number of elements in the StringSet."""
        return len(self._storage_)

    def contains(self, item: str, current: Optional[Ice.Current] = None) -> bool:
        """Check the pertenence of an item to the StringSet."""
        return item in self._storage_

    def hash(self, current: Optional[Ice.Current] = None) -> int:
        """Calculate a hash from the content of the internal StringSet."""
        contents = list(self._storage_)
        contents.sort()
        return hash(repr(contents))

    def add(self, item: str, current: Optional[Ice.Current] = None) -> None:
        """Add a new string to the StringSet."""
        self._storage_.add(item)
        self.escribir_set()

    def pop(self, current: Optional[Ice.Current] = None) -> str:
        """Remove and return an element from the storage."""
        try:
            valor = self._storage_.pop()
            self.escribir_set()
            return valor

        except KeyError as exc:
            raise rt.KeyError() from exc
   
    def iter(self, current: Optional[Ice.Current] = None) -> rt.IterablePrx:
        from remotetypes.iterable import IterableSet

        iterator = IterableSet(self)      
        proxy = current.adapter.addWithUUID(iterator)
        return rt.IterablePrx.uncheckedCast(proxy)
