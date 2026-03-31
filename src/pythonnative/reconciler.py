"""Virtual-tree reconciler.

Maintains a tree of :class:`VNode` objects (each wrapping a native view)
and diffs incoming :class:`Element` trees to apply the minimal set of
native mutations.
"""

from typing import Any, List, Optional

from .element import Element


class VNode:
    """A mounted element paired with its native view and child VNodes."""

    __slots__ = ("element", "native_view", "children")

    def __init__(self, element: Element, native_view: Any, children: List["VNode"]) -> None:
        self.element = element
        self.native_view = native_view
        self.children = children


class Reconciler:
    """Create, diff, and patch native view trees from Element descriptors.

    Parameters
    ----------
    backend:
        An object implementing the :class:`NativeViewRegistry` protocol
        (``create_view``, ``update_view``, ``add_child``, ``remove_child``,
        ``insert_child``).
    """

    def __init__(self, backend: Any) -> None:
        self.backend = backend
        self._tree: Optional[VNode] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def mount(self, element: Element) -> Any:
        """Build native views from *element* and return the root native view."""
        self._tree = self._create_tree(element)
        return self._tree.native_view

    def reconcile(self, new_element: Element) -> Any:
        """Diff *new_element* against the current tree and patch native views.

        Returns the (possibly replaced) root native view.
        """
        if self._tree is None:
            self._tree = self._create_tree(new_element)
            return self._tree.native_view

        self._tree = self._reconcile_node(self._tree, new_element)
        return self._tree.native_view

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_tree(self, element: Element) -> VNode:
        native_view = self.backend.create_view(element.type, element.props)
        children: List[VNode] = []
        for child_el in element.children:
            child_node = self._create_tree(child_el)
            self.backend.add_child(native_view, child_node.native_view, element.type)
            children.append(child_node)
        return VNode(element, native_view, children)

    def _reconcile_node(self, old: VNode, new_el: Element) -> VNode:
        if old.element.type != new_el.type:
            new_node = self._create_tree(new_el)
            self._destroy_tree(old)
            return new_node

        changed = self._diff_props(old.element.props, new_el.props)
        if changed:
            self.backend.update_view(old.native_view, old.element.type, changed)

        self._reconcile_children(old, new_el.children)
        old.element = new_el
        return old

    def _reconcile_children(self, parent: VNode, new_children: List[Element]) -> None:
        old_children = parent.children
        new_child_nodes: List[VNode] = []
        max_len = max(len(old_children), len(new_children))

        for i in range(max_len):
            if i >= len(new_children):
                self.backend.remove_child(parent.native_view, old_children[i].native_view, parent.element.type)
                self._destroy_tree(old_children[i])
            elif i >= len(old_children):
                node = self._create_tree(new_children[i])
                self.backend.add_child(parent.native_view, node.native_view, parent.element.type)
                new_child_nodes.append(node)
            else:
                if old_children[i].element.type != new_children[i].type:
                    self.backend.remove_child(parent.native_view, old_children[i].native_view, parent.element.type)
                    self._destroy_tree(old_children[i])
                    node = self._create_tree(new_children[i])
                    self.backend.insert_child(parent.native_view, node.native_view, parent.element.type, i)
                    new_child_nodes.append(node)
                else:
                    updated = self._reconcile_node(old_children[i], new_children[i])
                    new_child_nodes.append(updated)

        parent.children = new_child_nodes

    def _destroy_tree(self, node: VNode) -> None:
        for child in node.children:
            self._destroy_tree(child)
        node.children = []

    @staticmethod
    def _diff_props(old: dict, new: dict) -> dict:
        """Return props that changed (callables always count as changed)."""
        changed = {}
        for key, new_val in new.items():
            old_val = old.get(key)
            if callable(new_val) or old_val != new_val:
                changed[key] = new_val
        for key in old:
            if key not in new:
                changed[key] = None
        return changed
