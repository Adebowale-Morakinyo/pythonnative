"""Platform-specific native view creation and update logic.

This package provides the :class:`NativeViewRegistry` that maps element type
names to platform-specific :class:`~.base.ViewHandler` implementations.

Platform handlers live in dedicated submodules:

- :mod:`~.base` — shared :class:`~.base.ViewHandler` protocol and utilities
- :mod:`~.android` — Android handlers (Chaquopy / Java bridge)
- :mod:`~.ios` — iOS handlers (rubicon-objc)

All platform-branching is handled at registration time via lazy imports,
so the package can be imported on any platform for testing.
"""

from typing import Any, Dict, Optional

from .base import ViewHandler


class NativeViewRegistry:
    """Maps element type names to platform-specific :class:`ViewHandler` instances."""

    def __init__(self) -> None:
        self._handlers: Dict[str, ViewHandler] = {}

    def register(self, type_name: str, handler: ViewHandler) -> None:
        self._handlers[type_name] = handler

    def create_view(self, type_name: str, props: Dict[str, Any]) -> Any:
        handler = self._handlers.get(type_name)
        if handler is None:
            raise ValueError(f"Unknown element type: {type_name!r}")
        return handler.create(props)

    def update_view(self, native_view: Any, type_name: str, changed_props: Dict[str, Any]) -> None:
        handler = self._handlers.get(type_name)
        if handler is not None:
            handler.update(native_view, changed_props)

    def add_child(self, parent: Any, child: Any, parent_type: str) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.add_child(parent, child)

    def remove_child(self, parent: Any, child: Any, parent_type: str) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.remove_child(parent, child)

    def insert_child(self, parent: Any, child: Any, parent_type: str, index: int) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.insert_child(parent, child, index)


# ======================================================================
# Singleton registry
# ======================================================================

_registry: Optional[NativeViewRegistry] = None


def get_registry() -> NativeViewRegistry:
    """Return the singleton registry, lazily creating platform handlers."""
    global _registry
    if _registry is not None:
        return _registry
    _registry = NativeViewRegistry()

    from ..utils import IS_ANDROID

    if IS_ANDROID:
        from .android import register_handlers

        register_handlers(_registry)
    else:
        from .ios import register_handlers

        register_handlers(_registry)
    return _registry


def set_registry(registry: NativeViewRegistry) -> None:
    """Inject a custom or mock registry (primarily for testing)."""
    global _registry
    _registry = registry
