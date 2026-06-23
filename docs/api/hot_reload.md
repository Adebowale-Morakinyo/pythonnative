# Hot reload

Hot-reload comes in two cooperating pieces: a host-side file watcher
that detects changed `.py` files, and a device-side module reloader
that swaps the new code in and re-renders the active page. Both are
wired up automatically by the [`pn start`](../guides/dev-client.md) dev
loop (and by `pn preview` on the desktop).

::: pythonnative.hot_reload
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- See the workflow in [Hot reload guide](../guides/hot-reload.md).
