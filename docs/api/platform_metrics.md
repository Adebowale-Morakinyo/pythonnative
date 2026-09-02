# Platform metrics

A small process-wide store for values only the screen host can observe:
safe-area insets, viewport size, and keyboard height. The host publishes
them as the platform reports changes, and view handlers read them on
demand instead of receiving them through every measurement call.
Everything here is in layout units, points on iOS and
density-independent pixels on Android, so the values add directly to
other layout-unit values without conversion. Most app code reaches this
indirectly, through
[`use_safe_area_insets`][pythonnative.use_safe_area_insets] and
[`use_window_dimensions`][pythonnative.use_window_dimensions].

::: pythonnative.platform_metrics
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- See the handlers that read these values in
  [Native views](native_views.md).
- See the ops that position a view once it's measured in
  [Mutation ops](mutations.md).
- See the other Python-side registry the native layer talks to in
  [Events](events.md).
- Use the hooks that wrap these in [Hooks](hooks.md).
