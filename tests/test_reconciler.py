"""Unit tests for the reconciler using a mock native backend."""

from typing import Any, Dict, List

from pythonnative.element import Element
from pythonnative.reconciler import Reconciler

# ======================================================================
# Mock backend
# ======================================================================


class MockView:
    """Simulates a native view for testing."""

    _next_id = 0

    def __init__(self, type_name: str, props: Dict[str, Any]) -> None:
        MockView._next_id += 1
        self.id = MockView._next_id
        self.type_name = type_name
        self.props = dict(props)
        self.children: List["MockView"] = []

    def __repr__(self) -> str:
        return f"MockView({self.type_name}#{self.id})"


class MockBackend:
    """Records operations for assertions."""

    def __init__(self) -> None:
        self.ops: List[Any] = []

    def create_view(self, type_name: str, props: Dict[str, Any]) -> MockView:
        view = MockView(type_name, props)
        self.ops.append(("create", type_name, view.id))
        return view

    def update_view(self, native_view: MockView, type_name: str, changed_props: Dict[str, Any]) -> None:
        native_view.props.update(changed_props)
        self.ops.append(("update", type_name, native_view.id, tuple(sorted(changed_props.keys()))))

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
# Tests: mount
# ======================================================================


def test_mount_single_element() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el = Element("Text", {"text": "hello"}, [])
    root = rec.mount(el)
    assert isinstance(root, MockView)
    assert root.type_name == "Text"
    assert root.props["text"] == "hello"


def test_mount_nested_elements() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "a"}, []),
            Element("Button", {"title": "b"}, []),
        ],
    )
    root = rec.mount(el)
    assert root.type_name == "Column"
    assert len(root.children) == 2
    assert root.children[0].type_name == "Text"
    assert root.children[1].type_name == "Button"


def test_mount_deeply_nested() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el = Element(
        "ScrollView",
        {},
        [
            Element(
                "Column",
                {},
                [
                    Element("Text", {"text": "deep"}, []),
                ],
            ),
        ],
    )
    root = rec.mount(el)
    assert root.children[0].children[0].props["text"] == "deep"


# ======================================================================
# Tests: reconcile (update props)
# ======================================================================


def test_reconcile_updates_props() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element("Text", {"text": "hello"}, [])
    rec.mount(el1)

    backend.ops.clear()
    el2 = Element("Text", {"text": "world"}, [])
    rec.reconcile(el2)

    update_ops = [op for op in backend.ops if op[0] == "update"]
    assert len(update_ops) == 1
    assert "text" in update_ops[0][3]


def test_reconcile_no_change_no_update() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el = Element("Text", {"text": "same"}, [])
    rec.mount(el)

    backend.ops.clear()
    rec.reconcile(Element("Text", {"text": "same"}, []))

    update_ops = [op for op in backend.ops if op[0] == "update"]
    assert len(update_ops) == 0


# ======================================================================
# Tests: reconcile children (add / remove)
# ======================================================================


def test_reconcile_add_child() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element("Column", {}, [Element("Text", {"text": "a"}, [])])
    root = rec.mount(el1)
    assert len(root.children) == 1

    backend.ops.clear()
    el2 = Element(
        "Column",
        {},
        [Element("Text", {"text": "a"}, []), Element("Text", {"text": "b"}, [])],
    )
    rec.reconcile(el2)

    assert len(root.children) == 2


def test_reconcile_remove_child() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element(
        "Column",
        {},
        [Element("Text", {"text": "a"}, []), Element("Text", {"text": "b"}, [])],
    )
    root = rec.mount(el1)
    assert len(root.children) == 2

    backend.ops.clear()
    el2 = Element("Column", {}, [Element("Text", {"text": "a"}, [])])
    rec.reconcile(el2)

    assert len(root.children) == 1


def test_reconcile_replace_child_type() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element("Column", {}, [Element("Text", {"text": "a"}, [])])
    root = rec.mount(el1)

    backend.ops.clear()
    el2 = Element("Column", {}, [Element("Button", {"title": "b"}, [])])
    rec.reconcile(el2)

    assert root.children[0].type_name == "Button"


# ======================================================================
# Tests: reconcile root type change
# ======================================================================


def test_reconcile_root_type_change() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element("Text", {"text": "a"}, [])
    root1 = rec.mount(el1)

    el2 = Element("Button", {"title": "b"}, [])
    root2 = rec.reconcile(el2)
    assert root2.type_name == "Button"
    assert root2 is not root1


# ======================================================================
# Tests: callback props always counted as changed
# ======================================================================


def test_reconcile_callback_always_updated() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    cb1 = lambda: None  # noqa: E731
    cb2 = lambda: None  # noqa: E731
    el1 = Element("Button", {"title": "x", "on_click": cb1}, [])
    rec.mount(el1)

    backend.ops.clear()
    el2 = Element("Button", {"title": "x", "on_click": cb2}, [])
    rec.reconcile(el2)

    update_ops = [op for op in backend.ops if op[0] == "update"]
    assert len(update_ops) == 1
    assert "on_click" in update_ops[0][3]


# ======================================================================
# Tests: removed props signalled as None
# ======================================================================


def test_reconcile_removed_prop_becomes_none() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)
    el1 = Element("Text", {"text": "hi", "color": "#FF0000"}, [])
    root = rec.mount(el1)

    backend.ops.clear()
    el2 = Element("Text", {"text": "hi"}, [])
    rec.reconcile(el2)

    update_ops = [op for op in backend.ops if op[0] == "update"]
    assert len(update_ops) == 1
    assert "color" in update_ops[0][3]
    assert root.props.get("color") is None


# ======================================================================
# Tests: complex multi-step reconciliation
# ======================================================================


def test_multiple_reconcile_cycles() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)

    rec.mount(Element("Column", {}, [Element("Text", {"text": "0"}, [])]))

    for i in range(1, 5):
        rec.reconcile(Element("Column", {}, [Element("Text", {"text": str(i)}, [])]))

    assert rec._tree is not None
    assert rec._tree.children[0].element.props["text"] == "4"


# ======================================================================
# Tests: key-based reconciliation
# ======================================================================


def test_keyed_children_preserve_identity() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)

    el1 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "B"}, [], key="b"),
            Element("Text", {"text": "C"}, [], key="c"),
        ],
    )
    rec.mount(el1)
    view_a = rec._tree.children[0].native_view
    view_b = rec._tree.children[1].native_view
    view_c = rec._tree.children[2].native_view

    backend.ops.clear()
    el2 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "C"}, [], key="c"),
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "B"}, [], key="b"),
        ],
    )
    rec.reconcile(el2)

    assert rec._tree.children[0].native_view is view_c
    assert rec._tree.children[1].native_view is view_a
    assert rec._tree.children[2].native_view is view_b


def test_keyed_children_remove_by_key() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)

    el1 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "B"}, [], key="b"),
            Element("Text", {"text": "C"}, [], key="c"),
        ],
    )
    rec.mount(el1)

    el2 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "C"}, [], key="c"),
        ],
    )
    rec.reconcile(el2)

    assert len(rec._tree.children) == 2
    assert rec._tree.children[0].element.key == "a"
    assert rec._tree.children[1].element.key == "c"


def test_keyed_children_insert_new() -> None:
    backend = MockBackend()
    rec = Reconciler(backend)

    el1 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "C"}, [], key="c"),
        ],
    )
    rec.mount(el1)

    el2 = Element(
        "Column",
        {},
        [
            Element("Text", {"text": "A"}, [], key="a"),
            Element("Text", {"text": "B"}, [], key="b"),
            Element("Text", {"text": "C"}, [], key="c"),
        ],
    )
    rec.reconcile(el2)

    assert len(rec._tree.children) == 3
    assert rec._tree.children[1].element.key == "b"
