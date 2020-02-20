from __future__ import annotations

from typing import Any, List, Type, TypeVar

__all__ = ["typed", "Typed"]


class Typed:
    raw: Type
    type: Type
    arguments: List[Typed]
    parameters: List[Typed]

    def __init__(
        self, raw: Type, type: Type, arguments: List[Typed], parameters: List[Typed]
    ) -> None:
        self.raw = raw
        self.type = type
        if arguments == parameters:
            arguments = []
        self.arguments = arguments
        self.parameters = parameters

    def __eq__(self, other: Typed) -> bool:
        return (
            self.raw == other.raw
            and self.type == other.type
            and self.arguments == other.arguments
            and self.parameters == other.parameters
        )

    def __ne__(self, other: Typed) -> bool:
        return (
            self.raw != other.raw
            or self.type != other.type
            or self.arguments != other.arguments
            or self.parameters != other.parameters
        )

    def __repr__(self) -> str:
        return f"Types.from_raw({self.raw})"

    @staticmethod
    def from_raw(t: Type) -> Typed:
        if t is Any:
            return Typed(t, t, [], [])

        type_ = getattr(t, "__origin__", None) or t
        if isinstance(type_, TypeVar):
            type_ = type(type_)

        return Typed(
            t,
            type_,
            [typed(i) for i in getattr(t, "__args__", None) or []],
            [typed(i) for i in getattr(t, "__parameters__", None) or []],
        )


typed = Typed.from_raw
