"""Platform-specific native-view creation and update logic.

This package provides the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry]
that maps element type names (e.g., `"Text"`, `"Button"`) to
platform-specific
[`ViewHandler`][pythonnative.native_views.base.ViewHandler]
implementations. The reconciler calls the registry to create, update,
and re-parent native views.

Platform handlers live in dedicated submodules:

- `pythonnative.native_views.base`: shared `ViewHandler` protocol and
  utilities.
- `pythonnative.native_views.android`: Android handlers
  (Chaquopy / Java bridge).
- `pythonnative.native_views.ios`: iOS handlers (rubicon-objc).

All platform-branching is handled at registration time via lazy
imports, so this package can be imported on any platform for testing.
A mock registry can be installed via
[`set_registry`][pythonnative.native_views.set_registry] to drive the
reconciler with no real native views.
"""

from typing import Any, Dict, Optional

from .base import ViewHandler


class NativeViewRegistry:
    """Map element type names to platform-specific view handlers.

    The reconciler depends only on this protocol:
    `create_view`, `update_view`, `add_child`, `remove_child`,
    `insert_child`. Implementations may be real (Android/iOS) or
    mocked for tests.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, ViewHandler] = {}

    def register(self, type_name: str, handler: ViewHandler) -> None:
        """Register `handler` to service elements of type `type_name`.

        Args:
            type_name: The element type name (e.g., `"Text"`).
            handler: A `ViewHandler` instance for the active platform.
        """
        self._handlers[type_name] = handler

    def create_view(self, type_name: str, props: Dict[str, Any]) -> Any:
        """Create a native view for `type_name` and apply initial props.

        Args:
            type_name: The element type name.
            props: Initial props dict.

        Returns:
            The platform-native view object.

        Raises:
            ValueError: If no handler is registered for `type_name`.
        """
        handler = self._handlers.get(type_name)
        if handler is None:
            raise ValueError(f"Unknown element type: {type_name!r}")
        return handler.create(props)

    def update_view(self, native_view: Any, type_name: str, changed_props: Dict[str, Any]) -> None:
        """Apply `changed_props` to an existing native view.

        Silently ignored if no handler is registered for `type_name`.

        Args:
            native_view: The platform-native view.
            type_name: The element type name.
            changed_props: A dict containing only props whose values
                changed since the previous render. Removed props are
                signaled with a value of `None`.
        """
        handler = self._handlers.get(type_name)
        if handler is not None:
            handler.update(native_view, changed_props)

    def add_child(self, parent: Any, child: Any, parent_type: str) -> None:
        """Append `child` to `parent`.

        Args:
            parent: Parent native view.
            child: Native view to append.
            parent_type: Element type of the parent (for handler lookup).
        """
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.add_child(parent, child)

    def remove_child(self, parent: Any, child: Any, parent_type: str) -> None:
        """Remove `child` from `parent`.

        Args:
            parent: Parent native view.
            child: Child native view to remove.
            parent_type: Element type of the parent.
        """
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.remove_child(parent, child)

    def insert_child(self, parent: Any, child: Any, parent_type: str, index: int) -> None:
        """Insert `child` into `parent` at `index`.

        Args:
            parent: Parent native view.
            child: Child native view to insert.
            parent_type: Element type of the parent.
            index: Zero-based insertion position among `parent`'s
                existing children.
        """
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.insert_child(parent, child, index)


# ======================================================================
# Singleton registry
# ======================================================================

_registry: Optional[NativeViewRegistry] = None


def get_registry() -> NativeViewRegistry:
    """Return the process-wide registry, lazily registering handlers.

    The first call instantiates the registry and registers either the
    Android or iOS handlers based on `IS_ANDROID`. Subsequent calls
    return the same instance.

    Returns:
        The active `NativeViewRegistry`.
    """
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
    """Install a custom registry (primarily for testing).

    Replaces the lazy singleton so subsequent
    [`get_registry`][pythonnative.native_views.get_registry] calls
    return `registry`. Pass a mock to drive the reconciler from
    unit tests without touching real native APIs.

    Args:
        registry: The replacement registry.
    """
    global _registry
    _registry = registry
