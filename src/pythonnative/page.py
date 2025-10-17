"""
Your current approach, which involves creating an Android Activity in Kotlin
and then passing it to Python, is necessary due to the restrictions inherent
in Android's lifecycle. You are correctly following the Android way of managing
Activities. In Android, the system is in control of when and how Activities are
created and destroyed. It is not possible to directly create an instance of an
Activity from Python because that would bypass Android's lifecycle management,
leading to unpredictable results.

Your Button example works because Button is a View, not an Activity. View
instances in Android can be created and managed directly by your code. This is
why you are able to create an instance of Button from Python.

Remember that Activities in Android are not just containers for your UI like a
ViewGroup, they are also the main entry points into your app and are closely
tied to the app's lifecycle. Therefore, Android needs to maintain tight control
over them. Activities aren't something you instantiate whenever you need them;
they are created in response to a specific intent and their lifecycle is
managed by Android.

So, to answer your question: Yes, you need to follow this approach for
Activities in Android. You cannot instantiate an Activity from Python like you
do for Views.

On the other hand, for iOS, you can instantiate a UIViewController directly
from Python. The example code you provided for this is correct.

Just ensure that your PythonNative UI framework is aware of these platform
differences and handles them appropriately.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from .utils import IS_ANDROID, set_android_context
from .view import ViewBase

# ========================================
# Base class
# ========================================


class PageBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_root_view(self, view) -> None:
        pass

    @abstractmethod
    def on_create(self) -> None:
        pass

    @abstractmethod
    def on_start(self) -> None:
        pass

    @abstractmethod
    def on_resume(self) -> None:
        pass

    @abstractmethod
    def on_pause(self) -> None:
        pass

    @abstractmethod
    def on_stop(self) -> None:
        pass

    @abstractmethod
    def on_destroy(self) -> None:
        pass

    @abstractmethod
    def on_restart(self) -> None:
        pass

    @abstractmethod
    def on_save_instance_state(self) -> None:
        pass

    @abstractmethod
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
        """Return arguments provided to this Page (empty dict if none)."""
        # Concrete classes should set self._args; default empty
        return getattr(self, "_args", {})

    # Back-compat: navigate_to delegates to push
    def navigate_to(self, page) -> None:
        self.push(page)
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/app/Activity
    # ========================================

    from java import jclass

    class Page(PageBase, ViewBase):
        def __init__(self, native_instance) -> None:
            super().__init__()
            self.native_class = jclass("android.app.Activity")
            self.native_instance = native_instance
            # self.native_instance = self.native_class()
            # Stash the Activity so child views can implicitly acquire a Context
            set_android_context(native_instance)
            self._args: dict = {}

        def set_root_view(self, view) -> None:
            # In fragment-based navigation, attach child view to the current fragment container.
            try:
                from .utils import get_android_fragment_container

                container = get_android_fragment_container()
                # Remove previous children if any, then add the new root
                try:
                    container.removeAllViews()
                except Exception:
                    pass
                container.addView(view.native_instance)
            except Exception:
                # Fallback to setting content view directly on the Activity
                self.native_instance.setContentView(view.native_instance)

        def on_create(self) -> None:
            print("Android on_create() called")

        def on_start(self) -> None:
            print("Android on_start() called")

        def on_resume(self) -> None:
            print("Android on_resume() called")

        def on_pause(self) -> None:
            print("Android on_pause() called")

        def on_stop(self) -> None:
            print("Android on_stop() called")

        def on_destroy(self) -> None:
            print("Android on_destroy() called")

        def on_restart(self) -> None:
            print("Android on_restart() called")

        def on_save_instance_state(self) -> None:
            print("Android on_save_instance_state() called")

        def on_restore_instance_state(self) -> None:
            print("Android on_restore_instance_state() called")

        def set_args(self, args: Optional[dict]) -> None:
            # Accept dict or JSON string for convenience when crossing language boundaries
            if isinstance(args, str):
                try:
                    self._args = json.loads(args) or {}
                    return
                except Exception:
                    self._args = {}
                    return
            self._args = args or {}

        def _resolve_page_path(self, page: Union[str, Any]) -> str:
            if isinstance(page, str):
                return page
            # If a class or instance is passed, derive dotted path
            try:
                module = getattr(page, "__module__", None)
                name = getattr(page, "__name__", None)
                if module and name:
                    return f"{module}.{name}"
                # Instance: use its class
                cls = page.__class__
                return f"{cls.__module__}.{cls.__name__}"
            except Exception:
                raise ValueError("Unsupported page reference; expected dotted string or class/instance")

        def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
            # Delegate to Navigator.push to navigate to PageFragment with arguments
            page_path = self._resolve_page_path(page)
            try:
                Navigator = jclass(f"{self.native_instance.getPackageName()}.Navigator")
                args_json = json.dumps(args) if args else None
                Navigator.push(self.native_instance, page_path, args_json)
            except Exception:
                # As a last resort, do nothing rather than crash
                pass

        def pop(self) -> None:
            # Delegate to Navigator.pop for back-stack pop
            try:
                Navigator = jclass(f"{self.native_instance.getPackageName()}.Navigator")
                Navigator.pop(self.native_instance)
            except Exception:
                try:
                    self.native_instance.finish()
                except Exception:
                    pass

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uiviewcontroller
    # ========================================

    from typing import Dict

    from rubicon.objc import ObjCClass, ObjCInstance

    # Global registry mapping native UIViewController pointer address to Page instances.
    _IOS_PAGE_REGISTRY: Dict[int, Any] = {}

    def _ios_register_page(vc_instance: Any, page_obj: Any) -> None:
        try:
            ptr = int(vc_instance.ptr)  # rubicon ObjCInstance -> c_void_p convertible to int
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
        """Forward a lifecycle event from Swift ViewController to the registered Page.

        :param native_addr: Integer pointer address of the UIViewController
        :param event: One of 'on_start', 'on_resume', 'on_pause', 'on_stop', 'on_destroy',
            'on_save_instance_state', 'on_restore_instance_state'.
        """
        page = _IOS_PAGE_REGISTRY.get(int(native_addr))
        if not page:
            return
        try:
            handler = getattr(page, event, None)
            if handler:
                handler()
        except Exception:
            # Avoid surfacing exceptions across the Swift/Python boundary in lifecycle
            pass

    class Page(PageBase, ViewBase):
        def __init__(self, native_instance) -> None:
            super().__init__()
            self.native_class = ObjCClass("UIViewController")
            # If Swift passed us an integer pointer, wrap it as an ObjCInstance.
            if isinstance(native_instance, int):
                try:
                    native_instance = ObjCInstance(native_instance)
                except Exception:
                    native_instance = None
            self.native_instance = native_instance
            # self.native_instance = self.native_class.alloc().init()
            self._args: dict = {}
            # Register for lifecycle forwarding
            if self.native_instance is not None:
                _ios_register_page(self.native_instance, self)

        def set_root_view(self, view) -> None:
            # UIViewController.view is a property; access without calling.
            root_view = self.native_instance.view
            # Size the root child to fill the controller's view and enable autoresizing
            try:
                bounds = root_view.bounds
                view.native_instance.setFrame_(bounds)
                # UIViewAutoresizingFlexibleWidth (2) | UIViewAutoresizingFlexibleHeight (16)
                view.native_instance.setAutoresizingMask_(2 | 16)
            except Exception:
                pass
            root_view.addSubview_(view.native_instance)

        def on_create(self) -> None:
            print("iOS on_create() called")

        def on_start(self) -> None:
            print("iOS on_start() called")

        def on_resume(self) -> None:
            print("iOS on_resume() called")

        def on_pause(self) -> None:
            print("iOS on_pause() called")

        def on_stop(self) -> None:
            print("iOS on_stop() called")

        def on_destroy(self) -> None:
            print("iOS on_destroy() called")
            if self.native_instance is not None:
                _ios_unregister_page(self.native_instance)

        def on_restart(self) -> None:
            print("iOS on_restart() called")

        def on_save_instance_state(self) -> None:
            print("iOS on_save_instance_state() called")

        def on_restore_instance_state(self) -> None:
            print("iOS on_restore_instance_state() called")

        def set_args(self, args: Optional[dict]) -> None:
            if isinstance(args, str):
                try:
                    self._args = json.loads(args) or {}
                    return
                except Exception:
                    self._args = {}
                    return
            self._args = args or {}

        def _resolve_page_path(self, page: Union[str, Any]) -> str:
            if isinstance(page, str):
                return page
            try:
                module = getattr(page, "__module__", None)
                name = getattr(page, "__name__", None)
                if module and name:
                    return f"{module}.{name}"
                cls = page.__class__
                return f"{cls.__module__}.{cls.__name__}"
            except Exception:
                raise ValueError("Unsupported page reference; expected dotted string or class/instance")

        def push(self, page: Union[str, Any], args: Optional[dict] = None) -> None:
            page_path = self._resolve_page_path(page)
            # Resolve the Swift ViewController class. Swift classes are namespaced by
            # the module name (CFBundleName). Try plain name first, then Module.Name.
            ViewController = None
            try:
                ViewController = ObjCClass("ViewController")
            except Exception:
                try:
                    NSBundle = ObjCClass("NSBundle")
                    bundle = NSBundle.mainBundle
                    module_name = None
                    try:
                        # Prefer CFBundleName; fallback to CFBundleExecutable
                        module_name = bundle.objectForInfoDictionaryKey_("CFBundleName")
                        if module_name is None:
                            module_name = bundle.objectForInfoDictionaryKey_("CFBundleExecutable")
                    except Exception:
                        module_name = None
                    if module_name:
                        ViewController = ObjCClass(f"{module_name}.ViewController")
                except Exception:
                    ViewController = None

            if ViewController is None:
                raise NameError("ViewController class not found; ensure Swift class is ObjC-visible")

            next_vc = ViewController.alloc().init()
            try:
                # Use KVC to pass metadata to Swift
                next_vc.setValue_forKey_(page_path, "requestedPagePath")
                if args:
                    next_vc.setValue_forKey_(json.dumps(args), "requestedPageArgsJSON")
            except Exception:
                pass
            # On iOS, `navigationController` is exposed as a property; treat it as such.
            nav = getattr(self.native_instance, "navigationController", None)
            if nav is None:
                # If no navigation controller, this push will be a no-op; rely on template to embed one.
                raise RuntimeError(
                    "No UINavigationController available; ensure template embeds root in navigation controller"
                )
            # Method name maps from pushViewController:animated:
            nav.pushViewController_animated_(next_vc, True)

        def pop(self) -> None:
            nav = getattr(self.native_instance, "navigationController", None)
            if nav is not None:
                nav.popViewControllerAnimated_(True)
