"""Virtual-tree reconciler.

Maintains a tree of :class:`VNode` objects (each wrapping a native view)
and diffs incoming :class:`Element` trees to apply the minimal set of
native mutations.

Supports:

- **Native elements** (type is a string like ``"Text"``).
- **Function components** (type is a callable decorated with
  ``@component``).  Their hook state is preserved across renders.
- **Provider elements** (type ``"__Provider__"``), which push/pop
  context values during tree traversal.
- **Error boundary elements** (type ``"__ErrorBoundary__"``), which
  catch exceptions in child subtrees and render a fallback.
- **Key-based child reconciliation** for stable identity across
  re-renders.
- **Post-render effect flushing**: after each mount or reconcile pass,
  all queued effects are executed so they see the committed native tree.
"""

from typing import Any, List, Optional

from .element import Element


class VNode:
    """A mounted element paired with its native view and child VNodes."""

    __slots__ = ("element", "native_view", "children", "hook_state", "_rendered")

    def __init__(self, element: Element, native_view: Any, children: List["VNode"]) -> None:
        self.element = element
        self.native_view = native_view
        self.children = children
        self.hook_state: Any = None
        self._rendered: Optional[Element] = None


class Reconciler:
    """Create, diff, and patch native view trees from Element descriptors.

    After each ``mount`` or ``reconcile`` call the reconciler walks the
    committed tree and flushes all pending effects so that effect
    callbacks run **after** native mutations are applied.

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
        self._page_re_render: Optional[Any] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def mount(self, element: Element) -> Any:
        """Build native views from *element* and return the root native view."""
        self._tree = self._create_tree(element)
        self._flush_effects()
        return self._tree.native_view

    def reconcile(self, new_element: Element) -> Any:
        """Diff *new_element* against the current tree and patch native views.

        Returns the (possibly replaced) root native view.
        """
        if self._tree is None:
            self._tree = self._create_tree(new_element)
            self._flush_effects()
            return self._tree.native_view

        self._tree = self._reconcile_node(self._tree, new_element)
        self._flush_effects()
        return self._tree.native_view

    # ------------------------------------------------------------------
    # Effect flushing
    # ------------------------------------------------------------------

    def _flush_effects(self) -> None:
        """Walk the committed tree and flush pending effects (depth-first)."""
        if self._tree is not None:
            self._flush_tree_effects(self._tree)

    def _flush_tree_effects(self, node: VNode) -> None:
        for child in node.children:
            self._flush_tree_effects(child)
        if node.hook_state is not None:
            node.hook_state.flush_pending_effects()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_tree(self, element: Element) -> VNode:
        # Provider: push context, create child, pop context
        if element.type == "__Provider__":
            context = element.props["__context__"]
            context._stack.append(element.props["__value__"])
            try:
                child_node = self._create_tree(element.children[0]) if element.children else None
            finally:
                context._stack.pop()
            native_view = child_node.native_view if child_node else None
            children = [child_node] if child_node else []
            return VNode(element, native_view, children)

        # Error boundary: catch exceptions in the child subtree
        if element.type == "__ErrorBoundary__":
            return self._create_error_boundary(element)

        # Function component: call with hook context
        if callable(element.type):
            from .hooks import HookState, _set_hook_state

            hook_state = HookState()
            hook_state._trigger_render = self._page_re_render
            _set_hook_state(hook_state)
            try:
                rendered = element.type(**element.props)
            finally:
                _set_hook_state(None)

            child_node = self._create_tree(rendered)
            vnode = VNode(element, child_node.native_view, [child_node])
            vnode.hook_state = hook_state
            vnode._rendered = rendered
            return vnode

        # Native element
        native_view = self.backend.create_view(element.type, element.props)
        children: List[VNode] = []
        for child_el in element.children:
            child_node = self._create_tree(child_el)
            self.backend.add_child(native_view, child_node.native_view, element.type)
            children.append(child_node)
        return VNode(element, native_view, children)

    def _create_error_boundary(self, element: Element) -> VNode:
        fallback_fn = element.props.get("__fallback__")
        try:
            child_node = self._create_tree(element.children[0]) if element.children else None
        except Exception as exc:
            if fallback_fn is not None:
                fallback_el = fallback_fn(exc) if callable(fallback_fn) else fallback_fn
                child_node = self._create_tree(fallback_el)
            else:
                raise
        native_view = child_node.native_view if child_node else None
        children = [child_node] if child_node else []
        return VNode(element, native_view, children)

    def _reconcile_node(self, old: VNode, new_el: Element) -> VNode:
        if not self._same_type(old.element, new_el):
            new_node = self._create_tree(new_el)
            self._destroy_tree(old)
            return new_node

        # Provider
        if new_el.type == "__Provider__":
            context = new_el.props["__context__"]
            context._stack.append(new_el.props["__value__"])
            try:
                if old.children and new_el.children:
                    child = self._reconcile_node(old.children[0], new_el.children[0])
                    old.children = [child]
                    old.native_view = child.native_view
                elif new_el.children:
                    child = self._create_tree(new_el.children[0])
                    old.children = [child]
                    old.native_view = child.native_view
            finally:
                context._stack.pop()
            old.element = new_el
            return old

        # Error boundary
        if new_el.type == "__ErrorBoundary__":
            return self._reconcile_error_boundary(old, new_el)

        # Function component
        if callable(new_el.type):
            from .hooks import _set_hook_state

            hook_state = old.hook_state
            if hook_state is None:
                from .hooks import HookState

                hook_state = HookState()
            hook_state.reset_index()
            hook_state._trigger_render = self._page_re_render
            _set_hook_state(hook_state)
            try:
                rendered = new_el.type(**new_el.props)
            finally:
                _set_hook_state(None)

            if old.children:
                child = self._reconcile_node(old.children[0], rendered)
            else:
                child = self._create_tree(rendered)
            old.children = [child]
            old.native_view = child.native_view
            old.element = new_el
            old.hook_state = hook_state
            old._rendered = rendered
            return old

        # Native element
        changed = self._diff_props(old.element.props, new_el.props)
        if changed:
            self.backend.update_view(old.native_view, old.element.type, changed)

        self._reconcile_children(old, new_el.children)
        old.element = new_el
        return old

    def _reconcile_error_boundary(self, old: VNode, new_el: Element) -> VNode:
        fallback_fn = new_el.props.get("__fallback__")
        try:
            if old.children and new_el.children:
                child = self._reconcile_node(old.children[0], new_el.children[0])
                old.children = [child]
                old.native_view = child.native_view
            elif new_el.children:
                child = self._create_tree(new_el.children[0])
                old.children = [child]
                old.native_view = child.native_view
        except Exception as exc:
            for c in old.children:
                self._destroy_tree(c)
            if fallback_fn is not None:
                fallback_el = fallback_fn(exc) if callable(fallback_fn) else fallback_fn
                child = self._create_tree(fallback_el)
                old.children = [child]
                old.native_view = child.native_view
            else:
                raise
        old.element = new_el
        return old

    def _reconcile_children(self, parent: VNode, new_children: List[Element]) -> None:
        old_children = parent.children
        parent_type = parent.element.type
        is_native = isinstance(parent_type, str) and parent_type not in ("__Provider__", "__ErrorBoundary__")

        old_by_key: dict = {}
        old_unkeyed: list = []
        for child in old_children:
            if child.element.key is not None:
                old_by_key[child.element.key] = child
            else:
                old_unkeyed.append(child)

        new_child_nodes: List[VNode] = []
        used_keyed: set = set()
        unkeyed_iter = iter(old_unkeyed)

        for i, new_el in enumerate(new_children):
            matched: Optional[VNode] = None

            if new_el.key is not None and new_el.key in old_by_key:
                matched = old_by_key[new_el.key]
                used_keyed.add(new_el.key)
            elif new_el.key is None:
                matched = next(unkeyed_iter, None)

            if matched is None:
                node = self._create_tree(new_el)
                if is_native:
                    self.backend.add_child(parent.native_view, node.native_view, parent_type)
                new_child_nodes.append(node)
            elif not self._same_type(matched.element, new_el):
                if is_native:
                    self.backend.remove_child(parent.native_view, matched.native_view, parent_type)
                self._destroy_tree(matched)
                node = self._create_tree(new_el)
                if is_native:
                    self.backend.insert_child(parent.native_view, node.native_view, parent_type, i)
                new_child_nodes.append(node)
            else:
                updated = self._reconcile_node(matched, new_el)
                new_child_nodes.append(updated)

        # Destroy unused old nodes
        for key, node in old_by_key.items():
            if key not in used_keyed:
                if is_native:
                    self.backend.remove_child(parent.native_view, node.native_view, parent_type)
                self._destroy_tree(node)
        for node in unkeyed_iter:
            if is_native:
                self.backend.remove_child(parent.native_view, node.native_view, parent_type)
            self._destroy_tree(node)

        # Reorder native children when keyed children changed positions.
        # Without this, native sibling order drifts from the logical tree
        # when keyed children swap positions across reconcile passes.
        if is_native and used_keyed:
            old_key_order = [c.element.key for c in old_children if c.element.key in used_keyed]
            new_key_order = [n.element.key for n in new_child_nodes if n.element.key in used_keyed]
            if old_key_order != new_key_order:
                for node in new_child_nodes:
                    self.backend.remove_child(parent.native_view, node.native_view, parent_type)
                for node in new_child_nodes:
                    self.backend.add_child(parent.native_view, node.native_view, parent_type)

        parent.children = new_child_nodes

    def _destroy_tree(self, node: VNode) -> None:
        if node.hook_state is not None:
            node.hook_state.cleanup_all_effects()
        for child in node.children:
            self._destroy_tree(child)
        node.children = []

    @staticmethod
    def _same_type(old_el: Element, new_el: Element) -> bool:
        if isinstance(old_el.type, str):
            return old_el.type == new_el.type
        return old_el.type is new_el.type

    @staticmethod
    def _diff_props(old: dict, new: dict) -> dict:
        """Return props that changed (callables always count as changed)."""
        changed = {}
        for key, new_val in new.items():
            if key.startswith("__"):
                continue
            old_val = old.get(key)
            if callable(new_val) or old_val != new_val:
                changed[key] = new_val
        for key in old:
            if key.startswith("__"):
                continue
            if key not in new:
                changed[key] = None
        return changed
