"""Page host: the bridge between native lifecycle and function components.

Users do not subclass `Page`. Instead they write `@component` functions
and the native template calls
[`create_page`][pythonnative.create_page] to obtain a host that manages
the reconciler and lifecycle.

The page host owns:

- A [`Reconciler`][pythonnative.reconciler.Reconciler] backed by the
  platform's native-view registry.
- A [`NavigationHandle`][pythonnative.hooks.NavigationHandle] (delivered to
  components via the navigation context) so screens can push and pop
  without holding a direct reference to native classes.
- Render scheduling. State changes during render are queued and drained
  in batches so the reconciler runs at most a bounded number of passes
  per user gesture.

Example:
    User code defines a top-level component:

    ```python
    import pythonnative as pn

    @pn.component
    def MainPage():
        count, set_count = pn.use_state(0)
        return pn.Column(
            pn.Text(f"Count: {count}", style={"font_size": 24}),
            pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
            style={"spacing": 12, "padding": 16},
        )
    ```

    The native template wires it in:

    ```python
    host = pythonnative.page.create_page(
        "app.main_page.MainPage",
        native_instance,
    )
    host.on_create()
    ```
"""

import importlib
import json
import sys
from typing import Any, Dict, Optional, Sequence

from .utils import IS_ANDROID, IS_IOS, set_android_context

_MAX_RENDER_PASSES = 25

# ======================================================================
# Component path resolution
# ======================================================================


def _resolve_component_path(page_ref: Any) -> str:
    """Resolve a component function or string into a `module.name` path."""
    if isinstance(page_ref, str):
        return page_ref
    func = getattr(page_ref, "__wrapped__", page_ref)
    module = getattr(func, "__module__", None)
    name = getattr(func, "__name__", None)
    if module and name:
        return f"{module}.{name}"
    raise ValueError(f"Cannot resolve component path for {page_ref!r}")


def _import_component(component_path: str) -> Any:
    """Import and return the component function from a dotted path."""
    module_path, component_name = component_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, component_name)


# ======================================================================
# Shared helpers
# ======================================================================


def _init_host_common(host: Any, component_path: str, component_func: Any) -> None:
    host._component_path = component_path
    host._component = component_func
    host._args = {}
    host._reconciler = None
    host._root_native_view = None
    host._nav_handle = None
    host._is_rendering = False
    host._render_queued = False
    host._hot_reload_manifest_path = None
    host._hot_reload_last_version = None


def _get_component(host: Any) -> Any:
    """Resolve the current component function from its dotted path."""
    host._component = _import_component(host._component_path)
    return host._component


def _render_app(host: Any) -> Any:
    """Call the current root component and return its element tree."""
    return _get_component(host)()


def _new_reconciler(host: Any) -> Any:
    from .native_views import get_registry
    from .reconciler import Reconciler

    reconciler = Reconciler(get_registry())
    reconciler._page_re_render = lambda: _request_render(host)
    return reconciler


def _on_create(host: Any) -> None:
    from .hooks import NavigationHandle, Provider, _NavigationContext

    host._nav_handle = NavigationHandle(host)
    host._reconciler = _new_reconciler(host)

    app_element = _render_app(host)
    provider_element = Provider(_NavigationContext, host._nav_handle, app_element)

    host._is_rendering = True
    try:
        host._root_native_view = host._reconciler.mount(provider_element)
        host._attach_root(host._root_native_view)
        _drain_renders(host)
    finally:
        host._is_rendering = False


def _request_render(host: Any) -> None:
    """Request a render pass.

    If a render is already in progress (state changed mid-render or
    inside an effect), the request is queued and drained at the end of
    the current pass so the reconciler is never re-entered.
    """
    if host._reconciler is None:
        return
    if host._is_rendering:
        host._render_queued = True
        return
    _re_render(host)


def _re_render(host: Any) -> None:
    """Run one render pass, then drain any renders queued during it."""
    from .hooks import Provider, _NavigationContext

    host._is_rendering = True
    try:
        host._render_queued = False

        app_element = _render_app(host)
        provider_element = Provider(_NavigationContext, host._nav_handle, app_element)

        new_root = host._reconciler.reconcile(provider_element)
        if new_root is not host._root_native_view:
            host._detach_root(host._root_native_view)
            host._root_native_view = new_root
            host._attach_root(new_root)

        _drain_renders(host)
    finally:
        host._is_rendering = False


def _drain_renders(host: Any) -> None:
    """Flush additional renders queued by effects that set state.

    Capped at `_MAX_RENDER_PASSES` to break runaway feedback loops
    (e.g., an effect that unconditionally calls a setter).
    """
    from .hooks import Provider, _NavigationContext

    for _ in range(_MAX_RENDER_PASSES):
        if not host._render_queued:
            break
        host._render_queued = False

        app_element = _render_app(host)
        provider_element = Provider(_NavigationContext, host._nav_handle, app_element)

        new_root = host._reconciler.reconcile(provider_element)
        if new_root is not host._root_native_view:
            host._detach_root(host._root_native_view)
            host._root_native_view = new_root
            host._attach_root(new_root)


def _set_args(host: Any, args: Any) -> None:
    if isinstance(args, str):
        try:
            host._args = json.loads(args) or {}
        except Exception:
            host._args = {}
        return
    host._args = args if isinstance(args, dict) else {}


def _enable_hot_reload(host: Any, manifest_path: str) -> None:
    host._hot_reload_manifest_path = manifest_path
    host._hot_reload_last_version = None


def _hot_reload_tick(host: Any) -> bool:
    manifest_path = getattr(host, "_hot_reload_manifest_path", None)
    if not manifest_path:
        return False

    from .hot_reload import ModuleReloader

    next_version = ModuleReloader.reload_from_manifest(
        host,
        manifest_path,
        last_version=getattr(host, "_hot_reload_last_version", None),
    )
    if next_version == getattr(host, "_hot_reload_last_version", None):
        return False
    host._hot_reload_last_version = next_version
    return True


def _reload_host(host: Any, changed_modules: Optional[Sequence[str]] = None) -> None:
    from .hooks import NavigationHandle, Provider, _NavigationContext
    from .hot_reload import ModuleReloader

    modules = list(changed_modules or [])
    root_module = host._component_path.rsplit(".", 1)[0]
    if root_module not in modules:
        modules.append(root_module)

    ModuleReloader.reload_modules(modules)
    host._component = _import_component(host._component_path)

    if host._reconciler is None:
        return

    old_reconciler = host._reconciler
    old_root = host._root_native_view
    old_nav = host._nav_handle

    new_reconciler = _new_reconciler(host)
    host._reconciler = new_reconciler
    host._nav_handle = NavigationHandle(host)
    host._is_rendering = True
    try:
        app_element = _render_app(host)
        provider_element = Provider(_NavigationContext, host._nav_handle, app_element)
        new_root = new_reconciler.mount(provider_element)
    except Exception:
        host._reconciler = old_reconciler
        host._nav_handle = old_nav
        raise
    finally:
        host._is_rendering = False

    if old_reconciler is not None and old_reconciler._tree is not None:
        old_reconciler._destroy_tree(old_reconciler._tree)
    if old_root is not None:
        host._detach_root(old_root)

    host._root_native_view = new_root
    host._attach_root(new_root)
    _drain_renders(host)
    print(f"[hot-reload] Reloaded {', '.join(modules)}", file=sys.stderr)


# ======================================================================
# Platform implementations
# ======================================================================

if IS_ANDROID:
    from java import jclass

    class _AppHost:
        """Android host backed by an `Activity` and fragment-based navigation.

        Owned by the page fragment template. Bridges Android lifecycle
        callbacks (`onCreate`, `onPause`, etc.) to the reconciler and
        the function component.
        """

        def __init__(self, native_instance: Any, component_path: str, component_func: Any) -> None:
            self.native_instance = native_instance
            set_android_context(native_instance)
            _init_host_common(self, component_path, component_func)

        def on_create(self) -> None:
            _on_create(self)

        def on_start(self) -> None:
            pass

        def on_resume(self) -> None:
            pass

        def on_pause(self) -> None:
            pass

        def on_stop(self) -> None:
            pass

        def on_destroy(self) -> None:
            pass

        def enable_hot_reload(self, manifest_path: str, source_root: Optional[str] = None) -> None:
            _enable_hot_reload(self, manifest_path)

        def hot_reload_tick(self) -> bool:
            return _hot_reload_tick(self)

        def reload(self, changed_modules: Optional[Sequence[str]] = None) -> None:
            _reload_host(self, changed_modules)

        def on_restart(self) -> None:
            pass

        def on_save_instance_state(self) -> None:
            pass

        def on_restore_instance_state(self) -> None:
            pass

        def set_args(self, args: Any) -> None:
            _set_args(self, args)

        def _get_nav_args(self) -> Dict[str, Any]:
            return self._args

        def _push(self, page: Any, args: Optional[Dict[str, Any]] = None) -> None:
            page_path = _resolve_component_path(page)
            Navigator = jclass(f"{self.native_instance.getPackageName()}.Navigator")
            args_json = json.dumps(args) if args else None
            Navigator.push(self.native_instance, page_path, args_json)

        def _pop(self) -> None:
            try:
                Navigator = jclass(f"{self.native_instance.getPackageName()}.Navigator")
                Navigator.pop(self.native_instance)
            except Exception:
                self.native_instance.finish()

        def _attach_root(self, native_view: Any) -> None:
            try:
                from .utils import get_android_fragment_container

                container = get_android_fragment_container()
                try:
                    container.removeAllViews()
                except Exception:
                    pass
                LayoutParams = jclass("android.view.ViewGroup$LayoutParams")
                lp = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
                container.addView(native_view, lp)
            except Exception:
                self.native_instance.setContentView(native_view)

        def _detach_root(self, native_view: Any) -> None:
            try:
                from .utils import get_android_fragment_container

                container = get_android_fragment_container()
                container.removeAllViews()
            except Exception:
                pass

else:
    from typing import Dict as _Dict

    _rubicon_available = False
    try:
        from rubicon.objc import ObjCClass, ObjCInstance

        _rubicon_available = True

        import gc as _gc

        _gc.disable()
    except ImportError:
        pass

    # Redirect Python's stdout/stderr through fd 2 so ``print()`` output is
    # visible via ``xcrun simctl launch --console-pty``. This runs at
    # ``pythonnative.page`` import time, i.e. before any user page module
    # (e.g. ``app.main_page``) is imported, so their top-level ``print()``
    # calls are captured too. Gated on ``IS_IOS`` rather than rubicon-objc
    # being importable, so installing the ``[ios]`` extra on macOS does
    # not silently swap ``sys.stdout`` on a dev machine.
    if IS_IOS:
        try:
            from . import _ios_log

            _ios_log.install()
        except Exception:
            pass

    _IOS_PAGE_REGISTRY: _Dict[int, Any] = {}

    def _ios_register_page(vc_instance: Any, host_obj: Any) -> None:
        try:
            ptr = int(vc_instance.ptr)
            _IOS_PAGE_REGISTRY[ptr] = host_obj
        except Exception:
            pass

    def _ios_unregister_page(vc_instance: Any) -> None:
        try:
            ptr = int(vc_instance.ptr)
            _IOS_PAGE_REGISTRY.pop(ptr, None)
        except Exception:
            pass

    def forward_lifecycle(native_addr: int, event: str) -> None:
        """Forward a Swift `UIViewController` lifecycle event to its host.

        Args:
            native_addr: Pointer (`int`) of the calling
                `UIViewController` instance, used to look up the
                registered host.
            event: Lifecycle method name (e.g., `"on_resume"`).
        """
        host = _IOS_PAGE_REGISTRY.get(int(native_addr))
        if host is None:
            return
        handler = getattr(host, event, None)
        if handler:
            handler()

    if _rubicon_available:

        class _AppHost:
            """iOS host backed by a `UIViewController`.

            Owned by the page view-controller template. Bridges iOS
            lifecycle callbacks (`viewDidLoad`, `viewWillDisappear`,
            etc.) to the reconciler and the function component.
            """

            def __init__(self, native_instance: Any, component_path: str, component_func: Any) -> None:
                if isinstance(native_instance, int):
                    try:
                        native_instance = ObjCInstance(native_instance)
                    except Exception:
                        native_instance = None
                self.native_instance = native_instance
                _init_host_common(self, component_path, component_func)
                if self.native_instance is not None:
                    _ios_register_page(self.native_instance, self)

            def on_create(self) -> None:
                _on_create(self)

            def on_start(self) -> None:
                pass

            def on_resume(self) -> None:
                pass

            def on_pause(self) -> None:
                pass

            def on_stop(self) -> None:
                pass

            def on_destroy(self) -> None:
                if self.native_instance is not None:
                    _ios_unregister_page(self.native_instance)

            def enable_hot_reload(self, manifest_path: str, source_root: Optional[str] = None) -> None:
                _enable_hot_reload(self, manifest_path)

            def hot_reload_tick(self) -> bool:
                return _hot_reload_tick(self)

            def reload(self, changed_modules: Optional[Sequence[str]] = None) -> None:
                _reload_host(self, changed_modules)

            def on_restart(self) -> None:
                pass

            def on_save_instance_state(self) -> None:
                pass

            def on_restore_instance_state(self) -> None:
                pass

            def set_args(self, args: Any) -> None:
                _set_args(self, args)

            def _get_nav_args(self) -> Dict[str, Any]:
                return self._args

            def _push(self, page: Any, args: Optional[Dict[str, Any]] = None) -> None:
                page_path = _resolve_component_path(page)
                ViewController = None
                try:
                    ViewController = ObjCClass("ViewController")
                except Exception:
                    try:
                        NSBundle = ObjCClass("NSBundle")
                        bundle = NSBundle.mainBundle
                        module_name = bundle.objectForInfoDictionaryKey_("CFBundleName")
                        if module_name is None:
                            module_name = bundle.objectForInfoDictionaryKey_("CFBundleExecutable")
                        if module_name:
                            ViewController = ObjCClass(f"{module_name}.ViewController")
                    except Exception:
                        pass

                if ViewController is None:
                    raise NameError("ViewController class not found; ensure Swift class is ObjC-visible")

                next_vc = ViewController.alloc().init()
                try:
                    next_vc.setValue_forKey_(page_path, "requestedPagePath")
                    if args:
                        next_vc.setValue_forKey_(json.dumps(args), "requestedPageArgsJSON")
                except Exception:
                    pass
                nav = getattr(self.native_instance, "navigationController", None)
                if nav is None:
                    raise RuntimeError(
                        "No UINavigationController available; " "ensure template embeds root in navigation controller"
                    )
                nav.pushViewController_animated_(next_vc, True)

            def _pop(self) -> None:
                nav = getattr(self.native_instance, "navigationController", None)
                if nav is not None:
                    nav.popViewControllerAnimated_(True)

            def _attach_root(self, native_view: Any) -> None:
                root_view = self.native_instance.view
                native_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
                root_view.addSubview_(native_view)
                try:
                    safe = root_view.safeAreaLayoutGuide
                    native_view.topAnchor.constraintEqualToAnchor_(safe.topAnchor).setActive_(True)
                    native_view.bottomAnchor.constraintEqualToAnchor_(safe.bottomAnchor).setActive_(True)
                    native_view.leadingAnchor.constraintEqualToAnchor_(safe.leadingAnchor).setActive_(True)
                    native_view.trailingAnchor.constraintEqualToAnchor_(safe.trailingAnchor).setActive_(True)
                except Exception:
                    native_view.setTranslatesAutoresizingMaskIntoConstraints_(True)
                    try:
                        native_view.setFrame_(root_view.bounds)
                        native_view.setAutoresizingMask_(2 | 16)
                    except Exception:
                        pass

            def _detach_root(self, native_view: Any) -> None:
                try:
                    native_view.removeFromSuperview()
                except Exception:
                    pass

    else:

        class _AppHost:
            """Desktop stub used when no native runtime is available.

            Fully functional for unit tests when a mock backend is
            installed via
            [`set_registry`][pythonnative.native_views.set_registry].
            Calls to navigation methods raise `RuntimeError` because
            there is no native navigation stack to push onto.
            """

            def __init__(
                self,
                native_instance: Any = None,
                component_path: str = "",
                component_func: Any = None,
            ) -> None:
                self.native_instance = native_instance
                _init_host_common(self, component_path, component_func)

            def on_create(self) -> None:
                _on_create(self)

            def on_start(self) -> None:
                pass

            def on_resume(self) -> None:
                pass

            def on_pause(self) -> None:
                pass

            def on_stop(self) -> None:
                pass

            def on_destroy(self) -> None:
                pass

            def enable_hot_reload(self, manifest_path: str, source_root: Optional[str] = None) -> None:
                _enable_hot_reload(self, manifest_path)

            def hot_reload_tick(self) -> bool:
                return _hot_reload_tick(self)

            def reload(self, changed_modules: Optional[Sequence[str]] = None) -> None:
                _reload_host(self, changed_modules)

            def on_restart(self) -> None:
                pass

            def on_save_instance_state(self) -> None:
                pass

            def on_restore_instance_state(self) -> None:
                pass

            def set_args(self, args: Any) -> None:
                _set_args(self, args)

            def _get_nav_args(self) -> Dict[str, Any]:
                return self._args

            def _push(self, page: Any, args: Optional[Dict[str, Any]] = None) -> None:
                raise RuntimeError("navigate() requires a native runtime (iOS or Android)")

            def _pop(self) -> None:
                raise RuntimeError("go_back() requires a native runtime (iOS or Android)")

            def _attach_root(self, native_view: Any) -> None:
                pass

            def _detach_root(self, native_view: Any) -> None:
                pass


# ======================================================================
# Public factory
# ======================================================================


def create_page(
    component_path: str,
    native_instance: Any = None,
    args_json: Optional[str] = None,
) -> _AppHost:
    """Create a page host for a function component.

    Called by native templates (`PageFragment.kt` on Android,
    `ViewController.swift` on iOS) to bridge the native lifecycle to a
    [`@component`][pythonnative.component] function.

    Args:
        component_path: Dotted Python path to the component, e.g.,
            `"app.main_page.MainPage"`. The function is imported lazily
            so user modules can be reloaded by the dev server.
        native_instance: The native `Activity` (Android) or
            `UIViewController` (iOS) pointer that owns this page.
        args_json: Optional JSON string of navigation arguments to pass
            to the component on first render.

    Returns:
        An `_AppHost` ready to receive lifecycle callbacks (`on_create`,
        `on_pause`, etc.) from the platform.

    Example:
        ```python
        host = pythonnative.page.create_page(
            "app.main_page.MainPage",
            native_instance,
            args_json='{"id": 42}',
        )
        host.on_create()
        ```
    """
    component_func = _import_component(component_path)
    host = _AppHost(native_instance, component_path, component_func)
    if args_json:
        _set_args(host, args_json)
    return host
