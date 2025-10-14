# Architecture

PythonNative maps Python directly to native platform APIs. Conceptually, it is closer to NativeScript's dynamic bindings than to React Native's bridge-and-module approach.

## High-level model

- Direct bindings: call native APIs synchronously from Python.
  - iOS: rubicon-objc exposes Objective-C/Swift classes (e.g., UIViewController, UIButton, WKWebView) and lets you create dynamic Objective-C subclasses and selectors.
  - Android: Chaquopy exposes Java classes (e.g., android.widget.Button, android.webkit.WebView) via the java bridge so you can construct and call methods directly.
- Shared Python API: components like Page, StackView, Label, Button, and WebView have a small, consistent surface. Platform-specific behavior is chosen at import time using pythonnative.utils.IS_ANDROID.
- Thin native bootstrap: the host app remains native (Android Activity or iOS UIViewController). It passes a live instance/pointer into Python, and Python drives the UI from there.

## Comparison

- Versus React Native: RN typically exposes capabilities via native modules/TurboModules and a bridge. PythonNative does not require authoring such modules for most APIs; you can access platform classes directly from Python.
- Versus NativeScript: similar philosophy—dynamic, synchronous access to Obj-C/Java from the scripting runtime.

## iOS flow (Rubicon-ObjC)

- The iOS template (Swift + PythonKit) boots Python and calls your bootstrap(native_instance) with the UIViewController pointer.
- In Python, Rubicon wraps the pointer; you then interact with UIKit classes directly.

```python
from rubicon.objc import ObjCClass, ObjCInstance

UIButton = ObjCClass("UIButton")
vc = ObjCInstance(native_ptr)  # passed from Swift template
button = UIButton.alloc().init()
# Configure target/action via a dynamic Objective-C subclass (see Button implementation)
```

## Android flow (Chaquopy)

- The Android template (Kotlin + Chaquopy) initializes Python in MainActivity and provides the current Activity/Context to Python.
- Components acquire the Context implicitly and construct real Android views.

```python
from java import jclass
from pythonnative.utils import get_android_context

WebViewClass = jclass("android.webkit.WebView")
context = get_android_context()
webview = WebViewClass(context)
webview.loadUrl("https://example.com")
```

## Key implications

- Synchronous native calls: no JS bridge; Python calls are direct.
- Lifecycle rules remain native: Activities/ViewControllers are created by the OS. Python receives and controls them; it does not instantiate Android Activities directly.
- Small, growing surface: the shared Python API favors clarity and consistency, expanding progressively.

## Related docs

- Guides / Android: guides/android.md
- Guides / iOS: guides/ios.md
- Concepts / Components: concepts/components.md
