# Components

Element factory functions for the built-in PythonNative widgets. These
return immutable [`Element`][pythonnative.Element] descriptors; nothing
is mounted to a native view tree until the
[`Reconciler`][pythonnative.reconciler.Reconciler] processes them.

For the visual and layout properties accepted by each component's
`style` argument, see the
[Component Property Reference](component-properties.md).

::: pythonnative.components
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- Wire interactions with [Hooks](hooks.md).
- Compose styles with [`StyleSheet`][pythonnative.StyleSheet].
- Build navigation with [`NavigationContainer`][pythonnative.NavigationContainer].
