# Hooks

Hook primitives for `@component` functions: state, effects, memoization,
context, and refs. Hooks must be called at the top level of a component
(not inside conditionals or loops) so they can be matched to the same
slot across renders.

::: pythonnative.hooks
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- Compose hooks into a screen: [Components](components.md).
- Run side effects from
  [`use_effect`][pythonnative.use_effect] (after commit) and
  [`use_focus_effect`][pythonnative.use_focus_effect] (after focus).
- Share state across the tree with
  [`create_context`][pythonnative.create_context] and
  [`Provider`][pythonnative.Provider].
