"""Needed classes to implement the Factory interface."""

import logging

import Ice
import RemoteTypes   # noqa: F401; pylint: disable=import-error


from .remotelist import RemoteList
from .remotedict import RemoteDict
from .remoteset import RemoteSet


class Factory(RemoteTypes.Factory):
    """Factory implementation for creating or retrieving RDict, RList, and RSet instances."""

    def __init__(self):
        # Diccionarios para almacenar instancias existentes
        self.rdicts = {}
        self.rlists = {}
        self.rsets = {}

    def get(self, type_name, identifier=None, current=None):
        try:
            if type_name == RemoteTypes.TypeName.RDict:
                if identifier not in self.rdicts:
                    RemoteDict(identifier,current.adapter)
                    identity = Ice.Identity(identifier, "RemoteDict")
                    proxy = current.adapter.createProxy(identity)
                    self.rdicts[identifier] = RemoteTypes.RDictPrx.uncheckedCast(proxy)
                else:
                    identity = Ice.Identity(identifier, "RemoteDict")
                    proxy = current.adapter.createProxy(identity)
                    self.rdicts[identifier] = RemoteTypes.RDictPrx.uncheckedCast(proxy)
                return self.rdicts[identifier]
            elif type_name == RemoteTypes.TypeName.RList:
                if identifier not in self.rlists:
                    RemoteList(identifier,current.adapter)
                    identity = Ice.Identity(identifier, "RemoteList")
                    proxy = current.adapter.createProxy(identity)
                    self.rlists[identifier] = RemoteTypes.RListPrx.uncheckedCast(proxy)
                else:
                    identity = Ice.Identity(identifier, "RemoteList")
                    proxy = current.adapter.createProxy(identity)
                    self.rdicts[identifier] = RemoteTypes.RListPrx.uncheckedCast(proxy)
                return self.rlists[identifier]
            elif type_name == RemoteTypes.TypeName.RSet:
                if identifier not in self.rsets:
                    RemoteSet(identifier,current.adapter)
                    identity = Ice.Identity(identifier, "RemoteSet")
                    proxy = current.adapter.createProxy(identity)
                    self.rsets[identifier] = RemoteTypes.RSetPrx.uncheckedCast(proxy)
                else:
                    identity = Ice.Identity(identifier, "RemoteSet")
                    proxy = current.adapter.createProxy(identity)
                    self.rdicts[identifier] = RemoteTypes.RSetPrx.uncheckedCast(proxy)
                return self.rsets[identifier]
            else:
                raise ValueError(f"Unsupported typeName: {type_name}")
        except Exception as e:
            logging.error(f"Error in Factory.get: {e}")
            raise
