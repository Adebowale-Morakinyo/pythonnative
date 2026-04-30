# Animated

PythonNative's `Animated` API mirrors React Native's. Build performant
animations declaratively by binding [`AnimatedValue`][pythonnative.AnimatedValue]
instances to the `style` of an `Animated.View`, `Animated.Text`, or
`Animated.Image`. The reconciler holds a `ref` to the underlying
native view; the animation driver pushes value changes directly to
the native handler's `set_animated_property` hook so per-frame updates
bypass full reconciliation.

::: pythonnative.animated
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]
      show_if_no_docstring: true

## See also

- The [Animations guide](../guides/animations.md) walks through
  fade-ins, springs, sequences, and gesture-driven animations.
- [`use_ref`][pythonnative.use_ref] explains the `ref` semantics that
  back `Animated.View`.
