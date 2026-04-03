"""Page host — the bridge between native lifecycle and function components.

Users no longer subclass ``Page``.  Instead they write ``@component``
functions and the native template calls :func:`create_page` to obtain
an :class:`_AppHost` that manages the reconciler and lifecycle.

Usage (user code)::

    import pythonnative as pn

    @pn.component
    def MainPage():
        count, set_count = pn.use_state(0)
        return pn.Column(
            pn.Text(f"Count: {count}", style={"font_size": 24}),
            pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
            style={"spacing": 12, "padding": 16},
        )

The native template calls::

    host = pythonnative.page.create_page("app.main_page.MainPage", native_instance)
    host.on_create()
"""

import importlib
import json
from typing import Any, Dict, Optional

from .utils import IS_ANDROID, set_android_context

# ======================================================================
# Component path resolution
# ======================================================================


def _resolve_component_path(page_ref: Any) -> str:
    """Resolve a component function to a ``module.name`` path string."""
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


def _init_host_common(host: Any) -> None:
    host._args = {}
    host._reconciler = None
    host._root_native_view = None


def _on_create(host: Any) -> None:
    from .hooks import NavigationHandle, Provider, _NavigationContext
    from .native_views import get_registry
    from .reconciler import Reconciler

    host._reconciler = Reconciler(get_registry())
    host._reconciler._page_re_render = lambda: _re_render(host)

    nav_handle = NavigationHandle(host)
    app_element = host._component()
    provider_element = Provider(_NavigationContext, nav_handle, app_element)

    host._root_native_view = host._reconciler.mount(provider_element)
    host._attach_root(host._root_native_view)


def _re_render(host: Any) -> None:
    from .hooks import NavigationHandle, Provider, _NavigationContext

    nav_handle = NavigationHandle(host)
    app_element = host._component()
    provider_element = Provider(_NavigationContext, nav_handle, app_element)

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


# ======================================================================
# Platform implementations
# ======================================================================

if IS_ANDROID:
    from java import jclass

    class _AppHost:
        """Android host backed by an Activity and Fragment navigation."""

        def __init__(self, native_instance: Any, component_func: Any) -> None:
            self.native_instance = native_instance
            self._component = component_func
            set_android_context(native_instance)
            _init_host_common(self)

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
        """Forward a lifecycle event from Swift ViewController to the registered host."""
        host = _IOS_PAGE_REGISTRY.get(int(native_addr))
        if host is None:
            return
        handler = getattr(host, event, None)
        if handler:
            handler()

    if _rubicon_available:

        class _AppHost:
            """iOS host backed by a UIViewController."""

            def __init__(self, native_instance: Any, component_func: Any) -> None:
                if isinstance(native_instance, int):
                    try:
                        native_instance = ObjCInstance(native_instance)
                    except Exception:
                        native_instance = None
                self.native_instance = native_instance
                self._component = component_func
                _init_host_common(self)
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
            """Desktop stub — no native runtime available.

            Fully functional for testing with a mock backend via
            ``native_views.set_registry()``.
            """

            def __init__(self, native_instance: Any = None, component_func: Any = None) -> None:
                self.native_instance = native_instance
                self._component = component_func
                _init_host_common(self)

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
                raise RuntimeError("push() requires a native runtime (iOS or Android)")

            def _pop(self) -> None:
                raise RuntimeError("pop() requires a native runtime (iOS or Android)")

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

    Called by native templates (PageFragment.kt / ViewController.swift)
    to bridge the native lifecycle to a ``@component`` function.

    Parameters
    ----------
    component_path:
        Dotted Python path to the component, e.g. ``"app.main_page.MainPage"``.
    native_instance:
        The native Activity (Android) or ViewController pointer (iOS).
    args_json:
        Optional JSON string of navigation arguments.
    """
    component_func = _import_component(component_path)
    host = _AppHost(native_instance, component_func)
    if args_json:
        _set_args(host, args_json)
    return host
