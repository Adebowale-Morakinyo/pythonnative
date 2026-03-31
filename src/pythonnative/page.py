"""Page — the root component that bridges native lifecycle and declarative UI.

A ``Page`` subclass is the entry point for each screen.  It owns a
:class:`~pythonnative.reconciler.Reconciler` and automatically mounts /
re-renders the element tree returned by :meth:`render` whenever state
changes.

Usage::

    import pythonnative as pn

    class MainPage(pn.Page):
        def __init__(self, native_instance):
            super().__init__(native_instance)
            self.state = {"count": 0}

        def increment(self):
            self.set_state(count=self.state["count"] + 1)

        def render(self):
            return pn.Column(
                pn.Text(f"Count: {self.state['count']}", font_size=24),
                pn.Button("Increment", on_click=self.increment),
                spacing=12,
                padding=16,
            )
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from .utils import IS_ANDROID, set_android_context

# ======================================================================
# Base class (platform-independent)
# ======================================================================


class PageBase(ABC):
    """Abstract base defining the Page interface."""

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def render(self) -> Any:
        """Return an Element tree describing this page's UI."""

    def set_state(self, **updates: Any) -> None:
        """Merge *updates* into ``self.state`` and trigger a re-render."""

    def on_create(self) -> None:
        """Called when the page is first created. Triggers initial render."""

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

    @abstractmethod
    def set_args(self, args: Optional[dict]) -> None:
        pass

    @abstractmethod
    def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
        pass

    @abstractmethod
    def pop(self) -> None:
        pass

    def get_args(self) -> dict:
        """Return navigation arguments (empty dict if none)."""
        return getattr(self, "_args", {})

    def navigate_to(self, page: Any) -> None:
        self.push(page)


# ======================================================================
# Shared declarative rendering helpers
# ======================================================================


def _init_page_common(page: Any) -> None:
    """Common initialisation shared by both platform Page classes."""
    page.state = {}
    page._args = {}
    page._reconciler = None
    page._root_native_view = None


def _set_state(page: Any, **updates: Any) -> None:
    page.state.update(updates)
    if page._reconciler is not None:
        _re_render(page)


def _on_create(page: Any) -> None:
    from .native_views import get_registry
    from .reconciler import Reconciler

    page._reconciler = Reconciler(get_registry())
    element = page.render()
    page._root_native_view = page._reconciler.mount(element)
    page._attach_root(page._root_native_view)


def _re_render(page: Any) -> None:
    element = page.render()
    new_root = page._reconciler.reconcile(element)
    if new_root is not page._root_native_view:
        page._detach_root(page._root_native_view)
        page._root_native_view = new_root
        page._attach_root(new_root)


def _resolve_page_path(page_ref: Union[str, Any]) -> str:
    if isinstance(page_ref, str):
        return page_ref
    module = getattr(page_ref, "__module__", None)
    name = getattr(page_ref, "__name__", None)
    if module and name:
        return f"{module}.{name}"
    cls = page_ref.__class__
    return f"{cls.__module__}.{cls.__name__}"


def _set_args(page: Any, args: Optional[dict]) -> None:
    if isinstance(args, str):
        try:
            page._args = json.loads(args) or {}
        except Exception:
            page._args = {}
        return
    page._args = args or {}


# ======================================================================
# Platform implementations
# ======================================================================

if IS_ANDROID:
    from java import jclass

    class Page(PageBase):
        """Android Page backed by an Activity and Fragment navigation."""

        def __init__(self, native_instance: Any) -> None:
            super().__init__()
            self.native_class = jclass("android.app.Activity")
            self.native_instance = native_instance
            set_android_context(native_instance)
            _init_page_common(self)

        def render(self) -> Any:
            raise NotImplementedError("Page subclass must implement render()")

        def set_state(self, **updates: Any) -> None:
            _set_state(self, **updates)

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

        def set_args(self, args: Optional[dict]) -> None:
            _set_args(self, args)

        def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
            page_path = _resolve_page_path(page)
            Navigator = jclass(f"{self.native_instance.getPackageName()}.Navigator")
            args_json = json.dumps(args) if args else None
            Navigator.push(self.native_instance, page_path, args_json)

        def pop(self) -> None:
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

    def _ios_register_page(vc_instance: Any, page_obj: Any) -> None:
        try:
            ptr = int(vc_instance.ptr)
            _IOS_PAGE_REGISTRY[ptr] = page_obj
        except Exception:
            pass

    def _ios_unregister_page(vc_instance: Any) -> None:
        try:
            ptr = int(vc_instance.ptr)
            _IOS_PAGE_REGISTRY.pop(ptr, None)
        except Exception:
            pass

    def forward_lifecycle(native_addr: int, event: str) -> None:
        """Forward a lifecycle event from Swift ViewController to the registered Page."""
        page = _IOS_PAGE_REGISTRY.get(int(native_addr))
        if page is None:
            return
        handler = getattr(page, event, None)
        if handler:
            handler()

    if _rubicon_available:

        class Page(PageBase):
            """iOS Page backed by a UIViewController."""

            def __init__(self, native_instance: Any) -> None:
                super().__init__()
                self.native_class = ObjCClass("UIViewController")
                if isinstance(native_instance, int):
                    try:
                        native_instance = ObjCInstance(native_instance)
                    except Exception:
                        native_instance = None
                self.native_instance = native_instance
                _init_page_common(self)
                if self.native_instance is not None:
                    _ios_register_page(self.native_instance, self)

            def render(self) -> Any:
                raise NotImplementedError("Page subclass must implement render()")

            def set_state(self, **updates: Any) -> None:
                _set_state(self, **updates)

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

            def set_args(self, args: Optional[dict]) -> None:
                _set_args(self, args)

            def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
                page_path = _resolve_page_path(page)
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
                        "No UINavigationController available; ensure template embeds root in navigation controller"
                    )
                nav.pushViewController_animated_(next_vc, True)

            def pop(self) -> None:
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

        class Page(PageBase):
            """Desktop stub — no native runtime available.

            Fully functional for testing with a mock backend via
            ``native_views.set_registry()``.
            """

            def __init__(self, native_instance: Any = None) -> None:
                super().__init__()
                self.native_instance = native_instance
                _init_page_common(self)

            def render(self) -> Any:
                raise NotImplementedError("Page subclass must implement render()")

            def set_state(self, **updates: Any) -> None:
                _set_state(self, **updates)

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

            def set_args(self, args: Optional[dict]) -> None:
                _set_args(self, args)

            def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
                raise RuntimeError("push() requires a native runtime (iOS or Android)")

            def pop(self) -> None:
                raise RuntimeError("pop() requires a native runtime (iOS or Android)")

            def _attach_root(self, native_view: Any) -> None:
                pass

            def _detach_root(self, native_view: Any) -> None:
                pass
