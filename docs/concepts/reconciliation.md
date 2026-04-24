# Reconciliation

Reconciliation is the process that turns a freshly produced
[`Element`][pythonnative.Element] tree into the smallest set of native
view mutations that bring the on-screen tree into agreement with it.
PythonNative's reconciler is small (a few hundred lines) and intentional;
this page covers how to think about it and the rules that govern keyed
diffing, function components, providers, and error boundaries.

## Why we need a reconciler

Re-running a `@component` function returns a brand-new
[`Element`][pythonnative.Element] tree. Naively recreating native
widgets every render would be slow (Auto Layout passes, JNI roundtrips)
and would lose user state (text selections, scroll position, focus).

The reconciler instead asks: what is the *minimal* sequence of native
calls that turns the previous tree into the new one? It maintains a
parallel virtual tree of [`VNode`][pythonnative.reconciler.VNode]s, each
of which holds the native handle returned by a
[`ViewHandler`][pythonnative.native_views.base.ViewHandler] and the props
last applied.

## The diff algorithm in one paragraph

For each pair of (previous, next) elements at the same position in the
tree:

- If their `type` matches, **update**: hand the native view back to the
  handler with `update_view(view, prev_props, next_props)`.
- If their `type` differs, **replace**: ask the handler to remove the
  old view, mount a new one, and recurse into its children.
- For container elements, match children by `key` first and by
  position only if no key was provided. Reorder, mount, and unmount
  as needed using `insert_child` / `add_child` / `remove_child`.

That's it. There is no "fiber tree", no time slicing, and no priority
lanes. The reconciler runs synchronously to completion on the main
thread; if a render is heavy, you'll feel it as a frame drop, not a
deferred update.

## Keyed children

Without keys, children are matched by **index**. That's fine for static
lists but breaks down when items are inserted or reordered:

```python
@pn.component
def Inbox():
    msgs, set_msgs = pn.use_state([("a", "Hi"), ("b", "Hello")])
    return pn.Column(
        *[pn.Text(text, key=mid) for mid, text in msgs],
    )
```

Without `key=mid`, inserting a new message at index `0` would update
each existing `Text` in place rather than push them down, briefly
showing the wrong text in each row. With keys, the reconciler matches
"a" and "b" by identity, mounts the new row at index `0`, and shifts
the others without re-rendering them.

!!! tip "Choose keys from the data, not the position"
    `key=i` for `i in range(len(items))` is no better than no key at
    all. Use a stable identifier (database id, file path, etc.).

## Function components

A `@pn.component` function is treated as an element type just like
`"Text"` or `"Button"`. When the reconciler encounters one:

1. It looks up the function's hook state (or creates a fresh slot).
2. It calls the function with the current props inside an active hook
   context.
3. It recursively reconciles whatever
   [`Element`][pythonnative.Element] the function returned.

Hook slots are matched by their position in the function body, which is
why hooks must be called at the top level (not inside `if`/`for`).

## Context providers

[`Provider`][pythonnative.Provider] is itself an element type. When the
reconciler mounts one, it pushes a value onto a per-context stack;
descendants reading via [`use_context`][pythonnative.use_context]
observe the topmost value. On unmount or value change, the reconciler
re-renders descendants whose `use_context` hook subscribes to that
context.

```python
ThemeContext = pn.create_context({"primary": "#000"})

@pn.component
def Screen():
    return pn.Provider(
        ThemeContext,
        {"primary": "#222"},
        Header(),
    )

@pn.component
def Header():
    theme = pn.use_context(ThemeContext)
    return pn.Text("Hi", style={"color": theme["primary"]})
```

## Error boundaries

[`ErrorBoundary`][pythonnative.ErrorBoundary] is a special-cased
element. When the reconciler renders a subtree underneath one and an
exception escapes a child component or handler, the reconciler:

1. Catches the exception.
2. Tears down the partially-mounted subtree.
3. Renders the boundary's `fallback` (which may be a static
   [`Element`][pythonnative.Element] or a callable that receives the
   exception).
4. Continues reconciling the rest of the page.

This means a single misbehaving component can't bring down the whole
screen. See the [Error boundaries guide](../guides/error-boundaries.md)
for usage patterns.

## When to bypass the reconciler

For animation-driven values that change every frame (60+ Hz), going
through `set_state` is wasteful. Two ways to bypass:

- Use [`use_ref`][pythonnative.use_ref] to hold a reference to a
  native view and mutate it directly (`view.setText(...)` from inside
  an effect callback).
- Implement a custom widget that internally manages an animation; the
  reconciler only sees the static element wrapping it.

Reach for these only when profiling tells you that re-rendering is the
bottleneck.

## Next steps

- Browse the algorithm in code: [Reconciler API](../api/reconciler.md).
- Understand handlers underneath the diff: [Native views](native-views.md).
- See how mounting interacts with hooks: [Lifecycle](lifecycle.md).
