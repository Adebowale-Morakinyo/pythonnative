"""Hook primitives for function components.

Provides React-like hooks for managing state, effects, memoisation,
context, and navigation within function components decorated with
:func:`component`.

Usage::

    import pythonnative as pn

    @pn.component
    def counter(initial=0):
        count, set_count = pn.use_state(initial)
        return pn.Column(
            pn.Text(f"Count: {count}"),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
        )
"""

import inspect
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, TypeVar

from .element import Element

T = TypeVar("T")

_SENTINEL = object()

_hook_context: threading.local = threading.local()

_batch_context: threading.local = threading.local()

# ======================================================================
# Hook state container
# ======================================================================


class HookState:
    """Stores all hook data for a single function component instance.

    Effects are **queued** during the render phase and **flushed** after
    the reconciler commits native-view mutations.  This guarantees that
    effect callbacks can safely interact with the committed native tree.
    """

    __slots__ = (
        "states",
        "effects",
        "memos",
        "refs",
        "hook_index",
        "_trigger_render",
        "_pending_effects",
    )

    def __init__(self) -> None:
        self.states: List[Any] = []
        self.effects: List[Tuple[Any, Any]] = []
        self.memos: List[Tuple[Any, Any]] = []
        self.refs: List[dict] = []
        self.hook_index: int = 0
        self._trigger_render: Optional[Callable[[], None]] = None
        self._pending_effects: List[Tuple[int, Callable, Any]] = []

    def reset_index(self) -> None:
        self.hook_index = 0

    def flush_pending_effects(self) -> None:
        """Execute effects queued during the render pass (called after commit)."""
        pending = self._pending_effects
        self._pending_effects = []
        for idx, effect_fn, deps in pending:
            _, prev_cleanup = self.effects[idx]
            if callable(prev_cleanup):
                try:
                    prev_cleanup()
                except Exception:
                    pass
            cleanup = effect_fn()
            self.effects[idx] = (list(deps) if deps is not None else None, cleanup)

    def cleanup_all_effects(self) -> None:
        """Run all outstanding cleanup functions (called on unmount)."""
        for i, (deps, cleanup) in enumerate(self.effects):
            if callable(cleanup):
                try:
                    cleanup()
                except Exception:
                    pass
            self.effects[i] = (_SENTINEL, None)
        self._pending_effects = []


# ======================================================================
# Thread-local context helpers
# ======================================================================


def _get_hook_state() -> Optional[HookState]:
    return getattr(_hook_context, "current", None)


def _set_hook_state(state: Optional[HookState]) -> None:
    _hook_context.current = state


def _deps_changed(prev: Any, current: Any) -> bool:
    if prev is _SENTINEL:
        return True
    if prev is None or current is None:
        return True
    if len(prev) != len(current):
        return True
    return any(p is not c and p != c for p, c in zip(prev, current))


# ======================================================================
# Batching helpers
# ======================================================================


def _schedule_trigger(trigger: Callable[[], None]) -> None:
    """Call *trigger* now, or defer it if inside :func:`batch_updates`."""
    if getattr(_batch_context, "depth", 0) > 0:
        _batch_context.pending_trigger = trigger
    else:
        trigger()


@contextmanager
def batch_updates() -> Generator[None, None, None]:
    """Batch multiple state updates so only one re-render occurs.

    Usage::

        with pn.batch_updates():
            set_count(1)
            set_name("hello")
        # single re-render happens here
    """
    depth = getattr(_batch_context, "depth", 0)
    _batch_context.depth = depth + 1
    if depth == 0:
        _batch_context.pending_trigger = None
    try:
        yield
    finally:
        _batch_context.depth -= 1
        if _batch_context.depth == 0:
            trigger = _batch_context.pending_trigger
            _batch_context.pending_trigger = None
            if trigger is not None:
                trigger()


# ======================================================================
# Public hooks
# ======================================================================


def use_state(initial: Any = None) -> Tuple[Any, Callable]:
    """Return ``(value, setter)`` for component-local state.

    If *initial* is callable it is invoked once (lazy initialisation).
    The setter accepts a value **or** a ``current -> new`` callable.
    """
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_state must be called inside a @component function")

    idx = ctx.hook_index
    ctx.hook_index += 1

    if idx >= len(ctx.states):
        val = initial() if callable(initial) else initial
        ctx.states.append(val)

    current = ctx.states[idx]

    def setter(new_value: Any) -> None:
        if callable(new_value):
            new_value = new_value(ctx.states[idx])
        if ctx.states[idx] is not new_value and ctx.states[idx] != new_value:
            ctx.states[idx] = new_value
            if ctx._trigger_render:
                _schedule_trigger(ctx._trigger_render)

    return current, setter


def use_reducer(reducer: Callable[[Any, Any], Any], initial_state: Any) -> Tuple[Any, Callable]:
    """Return ``(state, dispatch)`` for reducer-based state management.

    The *reducer* is called as ``reducer(current_state, action)`` and
    must return the new state.  If *initial_state* is callable it is
    invoked once (lazy initialisation).

    Usage::

        def reducer(state, action):
            if action == "increment":
                return state + 1
            if action == "reset":
                return 0
            return state

        count, dispatch = pn.use_reducer(reducer, 0)
        # dispatch("increment") -> re-render with count = 1
    """
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_reducer must be called inside a @component function")

    idx = ctx.hook_index
    ctx.hook_index += 1

    if idx >= len(ctx.states):
        val = initial_state() if callable(initial_state) else initial_state
        ctx.states.append(val)

    current = ctx.states[idx]

    def dispatch(action: Any) -> None:
        new_state = reducer(ctx.states[idx], action)
        if ctx.states[idx] is not new_state and ctx.states[idx] != new_state:
            ctx.states[idx] = new_state
            if ctx._trigger_render:
                _schedule_trigger(ctx._trigger_render)

    return current, dispatch


def use_effect(effect: Callable, deps: Optional[list] = None) -> None:
    """Schedule *effect* to run **after** the native tree is committed.

    Effects are queued during the render pass and flushed once the
    reconciler has finished applying all native-view mutations.  This
    means effects can safely measure layout or interact with committed
    native views.

    *deps* controls when the effect re-runs:

    - ``None``  -> every render
    - ``[]``    -> mount only
    - ``[a, b]``-> when *a* or *b* change

    *effect* may return a cleanup callable.
    """
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_effect must be called inside a @component function")

    idx = ctx.hook_index
    ctx.hook_index += 1

    if idx >= len(ctx.effects):
        ctx.effects.append((_SENTINEL, None))
        ctx._pending_effects.append((idx, effect, deps))
        return

    prev_deps, _prev_cleanup = ctx.effects[idx]
    if _deps_changed(prev_deps, deps):
        ctx._pending_effects.append((idx, effect, deps))


def use_memo(factory: Callable[[], T], deps: list) -> T:
    """Return a memoised value, recomputed only when *deps* change."""
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_memo must be called inside a @component function")

    idx = ctx.hook_index
    ctx.hook_index += 1

    if idx >= len(ctx.memos):
        value = factory()
        ctx.memos.append((list(deps), value))
        return value

    prev_deps, prev_value = ctx.memos[idx]
    if not _deps_changed(prev_deps, deps):
        return prev_value

    value = factory()
    ctx.memos[idx] = (list(deps), value)
    return value


def use_callback(callback: Callable, deps: list) -> Callable:
    """Return a stable reference to *callback*, updated only when *deps* change."""
    return use_memo(lambda: callback, deps)


def use_ref(initial: Any = None) -> dict:
    """Return a mutable ref dict ``{"current": initial}`` that persists across renders."""
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_ref must be called inside a @component function")

    idx = ctx.hook_index
    ctx.hook_index += 1

    if idx >= len(ctx.refs):
        ref: dict = {"current": initial}
        ctx.refs.append(ref)
        return ref

    return ctx.refs[idx]


# ======================================================================
# Context
# ======================================================================


class Context:
    """A context object created by :func:`create_context`."""

    def __init__(self, default: Any = None) -> None:
        self.default = default
        self._stack: List[Any] = []

    def _current(self) -> Any:
        return self._stack[-1] if self._stack else self.default


def create_context(default: Any = None) -> Context:
    """Create a new context with an optional default value."""
    return Context(default)


def use_context(context: Context) -> Any:
    """Read the current value of *context* from the nearest ``Provider`` ancestor."""
    ctx = _get_hook_state()
    if ctx is None:
        raise RuntimeError("use_context must be called inside a @component function")
    return context._current()


# ======================================================================
# Provider element helper
# ======================================================================


def Provider(context: Context, value: Any, child: Element) -> Element:
    """Create a context provider element.

    All descendants of *child* will read *value* via ``use_context(context)``.
    """
    return Element("__Provider__", {"__context__": context, "__value__": value}, [child])


# ======================================================================
# Navigation
# ======================================================================

_NavigationContext: Context = create_context(None)


class NavigationHandle:
    """Object returned by :func:`use_navigation` providing push/pop/get_args.

    Navigates by component reference rather than string path, e.g.::

        nav = pn.use_navigation()
        nav.push(DetailScreen, args={"id": 42})
    """

    def __init__(self, host: Any) -> None:
        self._host = host

    def push(self, page: Any, args: Optional[Dict[str, Any]] = None) -> None:
        """Navigate forward to *page* (a ``@component`` function or class)."""
        self._host._push(page, args)

    def pop(self) -> None:
        """Navigate back to the previous screen."""
        self._host._pop()

    def get_args(self) -> Dict[str, Any]:
        """Return arguments passed from the previous screen."""
        return self._host._get_nav_args()


def use_navigation() -> NavigationHandle:
    """Return a :class:`NavigationHandle` for the current screen.

    Must be called inside a ``@component`` function rendered by PythonNative.
    """
    handle = use_context(_NavigationContext)
    if handle is None:
        raise RuntimeError(
            "use_navigation() called outside a PythonNative page. "
            "Ensure your component is rendered via create_page()."
        )
    return handle


# ======================================================================
# @component decorator
# ======================================================================


def component(func: Callable) -> Callable[..., Element]:
    """Decorator that turns a Python function into a PythonNative component.

    The decorated function can use hooks (``use_state``, ``use_effect``, etc.)
    and returns an ``Element`` tree.  Each call site creates an independent
    component instance with its own hook state.
    """
    sig = inspect.signature(func)
    positional_params = [
        name
        for name, p in sig.parameters.items()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    has_var_positional = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values())

    def wrapper(*args: Any, **kwargs: Any) -> Element:
        props: dict = dict(kwargs)

        if args:
            if has_var_positional:
                props["children"] = list(args)
            else:
                for i, arg in enumerate(args):
                    if i < len(positional_params):
                        props[positional_params[i]] = arg

        key = props.pop("key", None)
        return Element(func, props, [], key=key)

    wrapper.__wrapped__ = func  # noqa: B010
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper._pn_component = True  # noqa: B010
    return wrapper
