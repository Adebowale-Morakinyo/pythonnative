# Layout

The pure-Python flexbox engine that computes a frame
`(x, y, width, height)` for every node in the rendered tree. The
[`Reconciler`][pythonnative.reconciler.Reconciler] runs
[`calculate_layout`][pythonnative.layout.calculate_layout] after every
commit and forwards the resulting frames to the platform handlers via
`set_frame`.

For a conceptual overview, see [Layout engine](../concepts/layout.md).

::: pythonnative.layout
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- Browse the supported style keys:
  [Component properties](component-properties.md).
- See how leaf widgets contribute their intrinsic size:
  [Native views](native_views.md).
- Read the conceptual walkthrough:
  [Layout engine](../concepts/layout.md).
