"""Needed classes to implement and serve the RDict type."""

import json
import os
from typing import Optional

import Ice
import RemoteTypes as rt # noqa: F401; pylint: disable=import-error


class RemoteDict(rt.RDict):

    def __init__(self, identifier, adapter: Ice.ObjectAdapter) -> None:

        self.id_ = identifier
        self.archivo = os.path.join("almacen", identifier + "_dict.json")
        self._storage_ = {}

        try:
            with open(self.archivo, "r") as file:
                #print(json.load(file))
                contenido = file.read().strip()
                valores = json.loads(contenido)
                for key,value in valores.items():
                    self.setItem(key,value)

        except FileNotFoundError:
            self._storage_ = {}
            self.escribir_diccionario()

        except json.JSONDecodeError:
            raise ValueError()

        identity = Ice.Identity(identifier, "RemoteDict")
        adapter.add(self, identity)

    def escribir_diccionario(self):
        os.makedirs(os.path.dirname(self.archivo), exist_ok=True)

        with open(self.archivo, "w") as file:
            json.dump(self._storage_, file)


    def remove(self, key: str, current: Optional[Ice.Current] = None) -> None:
        try:
            del self._storage_[key]
            self.escribir_diccionario()
        except KeyError as error:
            raise rt.KeyError() from error

    def length(self, current: Optional[Ice.Current] = None) -> int:
        return len(self._storage_)

    def contains(self, key: str, current: Optional[Ice.Current] = None) -> bool:
        return key in self._storage_

    def hash(self, current: Optional[Ice.Current] = None) -> int:
        return hash(frozenset(self._storage_.items()))

    def setItem(self, key: str, value: str, current: Optional[Ice.Current] = None) -> None:
        self._storage_[key] = value
        self.escribir_diccionario()

    def getItem(self, key: str, current: Optional[Ice.Current] = None) -> str:
        try:
            return self._storage_[key]
        except KeyError as error:
            raise KeyError() from error

    def pop(self, key: str, current: Optional[Ice.Current] = None) -> str:
        try:
            valor = self._storage_.pop(key)
            self.escribir_diccionario()
            return valor
        except KeyError as error:
            raise KeyError() from error

    def iter(self, current: Optional[Ice.Current] = None) -> rt.IterablePrx:
        from remotetypes.iterable import IterableDict

        iterator = IterableDict(self)
        proxy = current.adapter.addWithUUID(iterator)
        return rt.IterablePrx.uncheckedCast(proxy)
