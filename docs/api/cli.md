# CLI (`pn`)

Reference for the `pn` console script. The implementation lives in
`pythonnative.cli.pn`; this page renders its docstrings directly so
the documented behavior never drifts from the code.

## Subcommands

- `pn init [name]`: scaffold a new project (creates `app/`,
  `pythonnative.toml`, `.gitignore`). Flag: `--force` to overwrite
  existing files. See [Configuration](../guides/configuration.md).
- `pn doctor [android|ios]`: diagnose the local toolchain and validate
  `pythonnative.toml`. Exits non-zero when something will block a build.
- `pn preview [component]`: render the app in a desktop (Tkinter) window
  with Fast Refresh, the fastest way to iterate on UI. Flags:
  `--width`, `--height`, `--title`, `--no-hot-reload`. See the
  [Desktop preview guide](../guides/desktop-preview.md).
- `pn start`: run the dev server and serve your app to
  [PythonNative Go](../guides/dev-client.md) over Wi-Fi, with a QR code
  and live reload on save. Flags: `--port`, `--host`, `--no-qr`,
  `--no-requirements`.
- `pn go build|install android|ios`: build (and install) the
  PythonNative Go dev client, a generic shell that connects to
  `pn start`.
- `pn run android|ios`: build and run a standalone build (your app baked
  in) on a connected device or simulator. Flags: `--prepare-only`,
  `--no-logs`.
- `pn build android|ios`: build distributable artifacts (release by
  default). Flag: `--debug` for the debug variant. See
  [Building for release](../guides/building-for-release.md).
- `pn app-id android|ios`: print the resolved application id (Android)
  or bundle id (iOS), handy for scripts and CI.
- `pn clean`: remove the local `build/` directory.

::: pythonnative.cli.pn
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- See the [Getting started](../getting-started.md) walkthrough.
- Set up the fast dev loop with [PythonNative Go](../guides/dev-client.md).
- Read about [Hot reload](../guides/hot-reload.md) internals.
