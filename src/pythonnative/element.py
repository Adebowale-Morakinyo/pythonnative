"""Lightweight element descriptors for the virtual view tree.

An Element is an immutable description of a UI node — analogous to a React
element.  It captures a type (name string **or** component function), a props
dictionary, and an ordered list of children without creating any native
platform objects.  The reconciler consumes these trees to determine what
native views must be created, updated, or removed.
"""

from typing import Any, Dict, List, Optional, Union


class Element:
    """Immutable description of a single UI node.

    ``type_name`` may be a *string* (e.g. ``"Text"``) for built-in native
    elements or a *callable* for function components decorated with
    :func:`~pythonnative.hooks.component`.
    """

    __slots__ = ("type", "props", "children", "key")

    def __init__(
        self,
        type_name: Union[str, Any],
        props: Dict[str, Any],
        children: List["Element"],
        key: Optional[str] = None,
    ) -> None:
        self.type = type_name
        self.props = props
        self.children = children
        self.key = key

    def __repr__(self) -> str:
        t = self.type if isinstance(self.type, str) else getattr(self.type, "__name__", repr(self.type))
        return f"Element({t!r}, props={set(self.props)}, children={len(self.children)})"

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
