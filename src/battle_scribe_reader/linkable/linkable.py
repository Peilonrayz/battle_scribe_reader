from __future__ import annotations
from typing import TypeVar, get_type_hints, Dict, Type, Any, Optional, Tuple
import importlib
import functools

from ..typed import typed, Typed

__all__ = [
    'Linkable'
]

T = TypeVar('T')


class Import:
    @classmethod
    @functools.lru_cache()
    def module_globals(cls, module: str) -> Dict[str, Any]:
        return vars(importlib.import_module(module))

    @classmethod
    def class_globals(cls, obj: Type) -> Dict[str, Any]:
        return cls.module_globals(obj.__module__)


class Linkable:
    __attrs: Optional[Dict[str, Tuple[Type, Typed, Optional[Type]]]] = None

    @staticmethod
    def _build_link(parent: Linkable, item: str, raw: Type[T], type: Typed, link: Type) -> T:
        return raw()

    def __build_attrs(self):
        # To prevent infinite recursion with __getattr__
        self.__attrs = ...
        globalns = Import.class_globals(type(self))
        self.__attrs: Dict[str, Tuple[Type, Typed, Optional[Type]]] = {}
        type_hints = get_type_hints(self, globalns=globalns)
        for k, v in type_hints.items():
            t = typed(v)
            l = next((i.type for i in [t] + t.arguments + t.parameters if issubclass(i.type, Linkable)), None)
            self.__attrs[k] = v, t, l

    def get_lists(self):
        if self.__attrs is None:
            self.__build_attrs()
        return {
            key: getattr(self, key)
            for key, (_, _, link) in self.__attrs.items()
            if link is not None
        }

    def __getattr__(self, item):
        if self.__attrs is None:
            self.__build_attrs()

        raw, t, link = self.__attrs.get(item, (None, None, None))
        if link is not None:
            setattr(self, item, link._build_link(self, item, raw, t, link))
        return super().__getattribute__(item)
