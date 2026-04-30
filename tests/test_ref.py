"""Tests for the reconciler's ``ref`` prop support."""

from __future__ import annotations

from typing import Any, Dict, List

from pythonnative.element import Element
from pythonnative.hooks import component, use_ref
from pythonnative.reconciler import Reconciler


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
        self.last_create_props: Dict[str, Any] = {}
        self.last_update_changes: Dict[str, Any] = {}

    def create_view(self, type_name: str, props: Dict[str, Any]) -> MockView:
        # Track props the backend was asked to apply on create — ref
        # must NOT appear here; it's reconciler-owned.
        self.last_create_props = dict(props)
        return MockView(type_name, props)

    def update_view(self, view: MockView, type_name: str, changed: Dict[str, Any]) -> None:
        self.last_update_changes = dict(changed)
        view.props.update(changed)

    def add_child(self, parent: MockView, child: MockView, parent_type: str) -> None:
        parent.children.append(child)

    def remove_child(self, parent: MockView, child: MockView, parent_type: str) -> None:
        parent.children = [c for c in parent.children if c.id != child.id]

    def insert_child(self, parent: MockView, child: MockView, parent_type: str, index: int) -> None:
        parent.children.insert(index, child)


def test_ref_populated_on_mount() -> None:
    ref: Dict[str, Any] = {"current": None}
    el = Element("Text", {"text": "hi", "ref": ref}, [])
    backend = MockBackend()
    Reconciler(backend).mount(el)
    assert ref["current"] is not None
    assert isinstance(ref["current"], MockView)
    assert ref["current"].type_name == "Text"


def test_ref_not_passed_to_backend() -> None:
    ref: Dict[str, Any] = {"current": None}
    el = Element("Text", {"text": "hi", "ref": ref}, [])
    backend = MockBackend()
    Reconciler(backend).mount(el)
    assert "ref" not in backend.last_create_props


def test_ref_cleared_on_unmount() -> None:
    ref: Dict[str, Any] = {"current": None}
    el = Element("Text", {"text": "hi", "ref": ref}, [])
    backend = MockBackend()
    rec = Reconciler(backend)
    rec.mount(el)
    assert ref["current"] is not None

    # Replace with a different element type — destroys the old tree.
    rec.reconcile(Element("Button", {"title": "ok"}, []))
    assert ref["current"] is None


def test_ref_repointed_when_ref_dict_swapped() -> None:
    """Swapping the ref dict on update should populate the new and clear the old."""
    old_ref: Dict[str, Any] = {"current": None}
    new_ref: Dict[str, Any] = {"current": None}

    backend = MockBackend()
    rec = Reconciler(backend)
    rec.mount(Element("Text", {"text": "a", "ref": old_ref}, []))
    assert old_ref["current"] is not None
    first_view = old_ref["current"]

    rec.reconcile(Element("Text", {"text": "a", "ref": new_ref}, []))
    assert old_ref["current"] is None
    assert new_ref["current"] is first_view


def test_ref_ignored_when_not_a_dict() -> None:
    """Non-dict ``ref`` values are silently ignored — no crashes."""
    el = Element("Text", {"text": "hi", "ref": "not-a-dict"}, [])
    backend = MockBackend()
    Reconciler(backend).mount(el)


def test_ref_diff_does_not_trigger_native_update() -> None:
    """Changing only the ref dict identity should NOT call update_view."""
    backend = MockBackend()
    rec = Reconciler(backend)
    ref_a: Dict[str, Any] = {"current": None}
    ref_b: Dict[str, Any] = {"current": None}

    rec.mount(Element("Text", {"text": "x", "ref": ref_a}, []))
    backend.last_update_changes = {}

    rec.reconcile(Element("Text", {"text": "x", "ref": ref_b}, []))
    assert backend.last_update_changes == {}
    assert ref_a["current"] is None
    assert ref_b["current"] is not None


def test_use_ref_in_component_populated_after_mount() -> None:
    captured: Dict[str, Any] = {}

    @component
    def Comp() -> Element:
        ref = use_ref(None)
        captured["ref"] = ref
        return Element("Text", {"text": "hi", "ref": ref}, [])

    Reconciler(MockBackend()).mount(Comp())
    ref = captured["ref"]
    assert ref["current"] is not None
    assert isinstance(ref["current"], MockView)
