"""Lightweight element descriptors for the virtual view tree.

An Element is an immutable description of a UI node — analogous to a React
element.  It captures a type name, a props dictionary, and an ordered list
of children without creating any native platform objects.  The reconciler
consumes these trees to determine what native views must be created,
updated, or removed.
"""

from typing import Any, Dict, List, Optional


class Element:
    """Immutable description of a single UI node."""

    __slots__ = ("type", "props", "children", "key")

    def __init__(
        self,
        type_name: str,
        props: Dict[str, Any],
        children: List["Element"],
        key: Optional[str] = None,
    ) -> None:
        self.type = type_name
        self.props = props
        self.children = children
        self.key = key

    def __repr__(self) -> str:
        return f"Element({self.type!r}, props={set(self.props)}, children={len(self.children)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Element):
            return NotImplemented
        return (
            self.type == other.type
            and self.props == other.props
            and self.children == other.children
            and self.key == other.key
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
