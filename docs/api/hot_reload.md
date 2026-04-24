# Hot reload

Hot-reload comes in two cooperating pieces: a host-side file watcher
that pushes changed `.py` files to the device, and a device-side
module reloader that swaps the new code in and re-renders the active
page. Both are wired up automatically by `pn run --hot-reload`.

::: pythonnative.hot_reload
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- See the workflow in [Hot reload guide](../guides/hot-reload.md).
