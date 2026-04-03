"""Unit tests for function components and hooks."""

from typing import Any, Dict, List

from pythonnative.element import Element
from pythonnative.hooks import (
    HookState,
    Provider,
    _set_hook_state,
    component,
    create_context,
    use_callback,
    use_context,
    use_effect,
    use_memo,
    use_ref,
    use_state,
)
from pythonnative.reconciler import Reconciler

# ======================================================================
# Mock backend (shared with test_reconciler)
# ======================================================================


class MockView:
    _next_id = 0

    def __init__(self, type_name: str, props: Dict[str, Any]) -> None:
        MockView._next_id += 1
        self.id = MockView._next_id
        self.type_name = type_name
        self.props = dict(props)
        self.children: List["MockView"] = []


class MockBackend:
    def __init__(self) -> None:
        self.ops: List[Any] = []

    def create_view(self, type_name: str, props: Dict[str, Any]) -> MockView:
        view = MockView(type_name, props)
        self.ops.append(("create", type_name, view.id))
        return view

    def update_view(self, view: MockView, type_name: str, changed: Dict[str, Any]) -> None:
        view.props.update(changed)
        self.ops.append(("update", type_name, view.id, tuple(sorted(changed.keys()))))

    def add_child(self, parent: MockView, child: MockView, parent_type: str) -> None:
        parent.children.append(child)
        self.ops.append(("add_child", parent.id, child.id))

    def remove_child(self, parent: MockView, child: MockView, parent_type: str) -> None:
        parent.children = [c for c in parent.children if c.id != child.id]
        self.ops.append(("remove_child", parent.id, child.id))

    def insert_child(self, parent: MockView, child: MockView, parent_type: str, index: int) -> None:
        parent.children.insert(index, child)
        self.ops.append(("insert_child", parent.id, child.id, index))


# ======================================================================
# use_state
# ======================================================================


def test_use_state_returns_initial_value() -> None:
    ctx = HookState()
    _set_hook_state(ctx)
    try:
        val, setter = use_state(42)
        assert val == 42
    finally:
        _set_hook_state(None)


def test_use_state_lazy_initialiser() -> None:
    ctx = HookState()
    _set_hook_state(ctx)
    try:
        val, _ = use_state(lambda: 99)
        assert val == 99
    finally:
        _set_hook_state(None)


def test_use_state_setter_triggers_render() -> None:
    renders = []
    ctx = HookState()
    ctx._trigger_render = lambda: renders.append(1)
    _set_hook_state(ctx)
    try:
        val, setter = use_state(0)
        setter(1)
        assert len(renders) == 1
        assert ctx.states[0] == 1
    finally:
        _set_hook_state(None)


def test_use_state_setter_functional_update() -> None:
    ctx = HookState()
    _set_hook_state(ctx)
    try:
        _, setter = use_state(10)
        _set_hook_state(None)
        setter(lambda prev: prev + 5)
        assert ctx.states[0] == 15
    finally:
        _set_hook_state(None)


# ======================================================================
# use_effect
# ======================================================================


def test_use_effect_runs_on_mount() -> None:
    calls: list = []
    ctx = HookState()
    _set_hook_state(ctx)
    try:
        use_effect(lambda: calls.append("mounted"), [])
        assert calls == ["mounted"]
    finally:
        _set_hook_state(None)


def test_use_effect_cleanup_on_rerun() -> None:
    cleanups: list = []
    ctx = HookState()

    _set_hook_state(ctx)
    try:
        use_effect(lambda: cleanups.append, None)
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        use_effect(lambda: cleanups.append, None)
    finally:
        _set_hook_state(None)


def test_use_effect_skips_with_same_deps() -> None:
    calls: list = []
    ctx = HookState()

    _set_hook_state(ctx)
    try:
        use_effect(lambda: calls.append("run"), [1, 2])
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        use_effect(lambda: calls.append("run"), [1, 2])
    finally:
        _set_hook_state(None)

    assert calls == ["run"]


# ======================================================================
# use_memo / use_callback
# ======================================================================


def test_use_memo_caches() -> None:
    calls: list = []
    ctx = HookState()

    def factory_a() -> int:
        calls.append(1)
        return 42

    def factory_b() -> int:
        calls.append(1)
        return 99

    _set_hook_state(ctx)
    try:
        val1 = use_memo(factory_a, [1])
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        val2 = use_memo(factory_b, [1])
    finally:
        _set_hook_state(None)

    assert val1 == 42
    assert val2 == 42
    assert len(calls) == 1


def test_use_memo_recomputes_on_dep_change() -> None:
    ctx = HookState()

    _set_hook_state(ctx)
    try:
        val1 = use_memo(lambda: "first", ["a"])
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        val2 = use_memo(lambda: "second", ["b"])
    finally:
        _set_hook_state(None)

    assert val1 == "first"
    assert val2 == "second"


def test_use_callback_returns_stable_reference() -> None:
    ctx = HookState()
    fn = lambda: None  # noqa: E731

    _set_hook_state(ctx)
    try:
        cb1 = use_callback(fn, [1])
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        cb2 = use_callback(lambda: None, [1])
    finally:
        _set_hook_state(None)

    assert cb1 is fn
    assert cb2 is fn


# ======================================================================
# use_ref
# ======================================================================


def test_use_ref_persists() -> None:
    ctx = HookState()
    _set_hook_state(ctx)
    try:
        ref = use_ref(0)
        assert ref["current"] == 0
        ref["current"] = 5
    finally:
        _set_hook_state(None)

    ctx.reset_index()
    _set_hook_state(ctx)
    try:
        ref2 = use_ref(0)
        assert ref2["current"] == 5
        assert ref2 is ref
    finally:
        _set_hook_state(None)


# ======================================================================
# Context
# ======================================================================


def test_create_context_default() -> None:
    ctx = create_context("default_val")
    assert ctx._current() == "default_val"


def test_context_stack() -> None:
    ctx = create_context("default")
    ctx._stack.append("override")
    assert ctx._current() == "override"
    ctx._stack.pop()
    assert ctx._current() == "default"


def test_use_context_reads_current() -> None:
    my_ctx = create_context("fallback")
    my_ctx._stack.append("active")
    hook_state = HookState()
    _set_hook_state(hook_state)
    try:
        val = use_context(my_ctx)
        assert val == "active"
    finally:
        _set_hook_state(None)
        my_ctx._stack.pop()


# ======================================================================
# @component decorator
# ======================================================================


def test_component_decorator_creates_element() -> None:
    @component
    def my_comp(label: str = "hello") -> Element:
        return Element("Text", {"text": label}, [])

    el = my_comp(label="world")
    assert isinstance(el, Element)
    assert el.type is getattr(my_comp, "__wrapped__")
    assert el.props == {"label": "world"}


def test_component_with_positional_args() -> None:
    @component
    def greeting(name: str, age: int = 0) -> Element:
        return Element("Text", {"text": f"{name}, {age}"}, [])

    el = greeting("Alice", age=30)
    assert el.props == {"name": "Alice", "age": 30}


def test_component_key_extraction() -> None:
    @component
    def widget(text: str = "") -> Element:
        return Element("Text", {"text": text}, [])

    el = widget(text="hi", key="k1")
    assert el.key == "k1"
    assert "key" not in el.props


# ======================================================================
# Function components in reconciler
# ======================================================================


def test_reconciler_mounts_function_component() -> None:
    @component
    def greeting(name: str = "World") -> Element:
        return Element("Text", {"text": f"Hello {name}"}, [])

    backend = MockBackend()
    rec = Reconciler(backend)
    root = rec.mount(greeting(name="Python"))
    assert root.type_name == "Text"
    assert root.props["text"] == "Hello Python"


def test_reconciler_reconciles_function_component() -> None:
    @component
    def display(value: int = 0) -> Element:
        return Element("Text", {"text": str(value)}, [])

    backend = MockBackend()
    rec = Reconciler(backend)
    rec.mount(display(value=1))

    backend.ops.clear()
    rec.reconcile(display(value=2))

    update_ops = [op for op in backend.ops if op[0] == "update"]
    assert len(update_ops) == 1
    assert "text" in update_ops[0][3]


def test_function_component_use_state() -> None:
    render_count = [0]
    captured_setter: list = [None]

    @component
    def counter() -> Element:
        count, set_count = use_state(0)
        render_count[0] += 1
        captured_setter[0] = set_count
        return Element("Text", {"text": str(count)}, [])

    backend = MockBackend()
    rec = Reconciler(backend)
    re_rendered: list = []
    rec._page_re_render = lambda: re_rendered.append(1)

    root = rec.mount(counter())
    assert root.props["text"] == "0"
    assert render_count[0] == 1

    setter_fn = captured_setter[0]
    assert setter_fn is not None
    setter_fn(5)
    assert len(re_rendered) == 1


def test_function_component_preserves_state_across_reconcile() -> None:
    @component
    def stateful(label: str = "") -> Element:
        count, set_count = use_state(0)
        return Element("Text", {"text": f"{label}:{count}"}, [])

    backend = MockBackend()
    rec = Reconciler(backend)
    rec.mount(stateful(label="A"))

    tree_node = rec._tree
    assert tree_node is not None
    assert tree_node.hook_state is not None
    tree_node.hook_state.states[0] = 42

    rec.reconcile(stateful(label="B"))
    assert rec._tree is not None
    assert rec._tree.hook_state is not None
    assert rec._tree.hook_state.states[0] == 42


# ======================================================================
# Provider in reconciler
# ======================================================================


def test_provider_in_reconciler() -> None:
    theme = create_context("light")

    @component
    def themed() -> Element:
        t = use_context(theme)
        return Element("Text", {"text": t}, [])

    backend = MockBackend()
    rec = Reconciler(backend)
    el = Provider(theme, "dark", themed())
    root = rec.mount(el)
    assert root.props["text"] == "dark"
