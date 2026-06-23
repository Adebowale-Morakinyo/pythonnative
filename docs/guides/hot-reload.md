# Hot reload

Hot reload turns your edit-save-rebuild loop into edit-save-see. While
[PythonNative Go](dev-client.md) is connected to a `pn start` dev
server, every save streams the changed files to the device, where a
small device-side helper reloads the affected modules and asks the
screen host to re-render with state preserved.

This page covers the reload mechanics. For how to set up the dev server
and client, see the [PythonNative Go guide](dev-client.md).

## Turn it on

Hot reload is the default behavior of the dev loop. Install the client
once, then start the server:

```bash
pn go install android   # one time (or: pn go install ios)
pn start                # in your project; serves over Wi-Fi
```

Connect PythonNative Go to the printed URL and start editing. You can
also Fast-Refresh entirely on the desktop with
[`pn preview`](desktop-preview.md), which uses the same machinery.

## How the device sees changes

The native templates call
[`configure_dev_environment()`][pythonnative.hot_reload.configure_dev_environment]
before importing your app. That creates a `pythonnative_dev/` directory
in the app's writable sandbox and puts it before the bundled app code
on `sys.path`.

When you save, the dev server rebuilds the bundle and bumps a version
token. PythonNative Go is long-polling for that token; when it changes,
the client fetches only the files whose content hash differs and writes
them into the `pythonnative_dev/` overlay (the same directory the
templates already prioritize on `sys.path`).

After the files are in place, the client writes `reload.json` into the
overlay. The Android and iOS templates poll that manifest on the
platform main thread and call the screen host's reload hook. The host
re-imports the root component by dotted path, resets hook/navigation
state for the page, and mounts the refreshed tree.

## What gets reloaded

PythonNative reloads any `.py` file under `app/`. The device-side
[`ModuleReloader`][pythonnative.hot_reload.ModuleReloader] resolves
the file to a dotted module name (e.g., `app/pages/home.py` becomes
`app.pages.home`) and re-imports it from disk.

After reloading, every active screen host runs **Fast Refresh** in
place:

1. Walk the live VNode tree and collect every component function
   defined in a reloaded module.
2. Look up each function's replacement by `__module__` +
   `__qualname__` in the freshly reloaded module (unwrapping the
   `@pn.component` decorator).
3. Rewrite the `Element.type` references on every VNode in place;
   the next reconcile sees the new function with the same
   `HookState`, so state survives.

The next render runs through
[`Reconciler.reconcile`][pythonnative.reconciler.Reconciler.reconcile]
just like a normal re-render, so layout and native views are
updated incrementally. Component state (`use_state`, `use_reducer`,
refs) is preserved across the swap.

If Fast Refresh can't find a clean swap (for example, a
component's `__qualname__` changed, a new module was added that the
tree doesn't reference yet, or the swap raises), the host
**falls back** to a full remount of its root component so you never
get stuck with a stale tree. Hook state is reset in that case.

Per-screen scope: each native screen (UIViewController on iOS,
ScreenFragment on Android) runs its own host, so Fast Refresh
operates independently per host. Two pushed screens both running
Fast Refresh for the same changed module each swap their own
references.

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
    If module `a` does `from b import Foo` and only `b.py` changes,
    module `a` may still hold the *old* `Foo`. The screen host always
    reloads the root screen module after changed modules so common
    component imports update, but long-lived references (e.g., stashed
    in a global) can drift. When in doubt, restart the app.

!!! warning "Hook signature changes"
    Adding or removing a hook in a component changes the slot layout.
    Fast Refresh will swap the function in place but the next render
    can read the wrong slots, so the host falls back to a full
    remount when it detects the swap raises. If you see suspicious
    state after a hook-shape edit, close and reopen the affected
    screen (or restart the app) to clear the slate.

!!! info "Renaming a component"
    Fast Refresh keys on each function's `__qualname__`. Renaming a
    component changes the key, so the live VNode keeps its old
    function until the parent re-renders with the new name. In
    practice this means you may need to trigger one navigation or
    state change for the renamed component to take effect; closing
    and reopening the screen always works.

## Rebuilding from scratch

When you change native code (Kotlin, Swift, the manifest, or
`Info.plist`) or need a true standalone build, skip the dev server and
bake the app into the native shell:

```bash
pn run android   # build, install, and launch with your app baked in
# ...edit native files...
pn run android   # rebuild and re-install
```

You can stage the project without building (handy when iterating on
`AndroidManifest.xml` or `Info.plist`) with `pn run android
--prepare-only`, then open it in Android Studio or Xcode.

## Reading device logs

`pn start` prints reload activity in your terminal. For full app
stdout/stderr and tracebacks from a standalone build, `pn run` streams
device logs by default (pass `--no-logs` to suppress them); on iOS you
can also use Console.app or Xcode.

## Next steps

- Set up the dev loop: [PythonNative Go](dev-client.md).
- Reference: [Hot reload API](../api/hot_reload.md).
- See where the dev loop sits in the CLI: [`pn` CLI](../api/cli.md).
