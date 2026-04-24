# Hot reload

Hot reload turns your edit-save-rebuild loop into edit-save-see. The
`pn` CLI watches `app/` for changes and pushes the modified files
straight to the running app, where a small device-side helper reloads
the affected modules and asks the page host to re-render.

## Turn it on

Add `--hot-reload` to your `pn run` invocation:

```bash
pn run android --hot-reload
# or
pn run ios --hot-reload
```

`pn` will:

1. Build and install the app once (the standard `run` flow).
2. Launch the app on a connected device or simulator.
3. Start a [`FileWatcher`][pythonnative.hot_reload.FileWatcher] over
   `app/`.
4. Tail logs (Android) or print hot-reload notifications (iOS) until
   you press `Ctrl+C`.

## What gets reloaded

PythonNative reloads any `.py` file under `app/`. The device-side
[`ModuleReloader`][pythonnative.hot_reload.ModuleReloader] resolves
the file to a dotted module name (e.g., `app/pages/home.py` becomes
`app.pages.home`) and calls `importlib.reload` on it.

After reloading, the page host is notified to re-render the active
page. Hook state for the affected component instances is **reset** on
reload (this matches React Native's "fast refresh" model and avoids
stale closures from older module versions).

## What doesn't reload

- Native template files (anything under `android_template/` or
  `ios_template/`). Changes there require a full rebuild because the
  Java/Swift code is compiled into the app binary.
- Files outside `app/`. If you have a shared library next to your
  project, copy or symlink it under `app/` to pick up changes.
- C extension modules. Hot reload only updates Python source files;
  recompiled `.so` / `.dylib` libraries are not re-loaded mid-session.

## Common pitfalls

!!! warning "Top-level side effects"
    Code that runs at import time (e.g., a global registry that
    registers itself when the module is imported) runs again on every
    reload. Idempotent registration is fine; non-idempotent setup
    (counters, network calls) needs guarding.

!!! warning "References across modules"
    If module `a` does `from b import Foo` and you reload `b`, module
    `a` still holds the *old* `Foo`. The reconciler sidesteps this
    for components by re-resolving the function on every render, but
    long-lived references (e.g., stashed in a global) can drift. When
    in doubt, restart the app.

!!! warning "Hook signature changes"
    Adding or removing a hook in a component changes the slot layout.
    The reload picks up the new code, but existing component instances
    can't safely keep their old state. Closing and reopening the
    affected screen (or restarting the app) clears the slate.

## Working without `--hot-reload`

Hot reload is opt-in. If you'd rather rebuild on every change (more
predictable, slower), use `pn run android` / `pn run ios` without the
flag, or split the loop:

```bash
pn run android --prepare-only   # stage files, skip the build
# ...edit...
pn run android                  # rebuild and re-install
```

`--prepare-only` is also useful for iterating on
`AndroidManifest.xml` or `Info.plist` because those changes never
hot-reload and you want the smallest possible cycle.

## Reading device logs

Hot reload streams logs by default so you can see exceptions from your
reloaded modules. Pass `--no-logs` to suppress the stream:

```bash
pn run android --hot-reload --no-logs
```

On iOS, the simulator attaches the launching terminal to the app's
stderr; PythonNative also rewires `sys.stdout` to that channel so
`print()` calls show up alongside `NSLog` output.

## Next steps

- Reference: [Hot reload API](../api/hot_reload.md).
- See where hot reload sits in the run loop: [`pn run`](../api/cli.md).
