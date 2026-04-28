"""iOS native-view handlers (rubicon-objc).

Each handler class maps a PythonNative element type to a UIKit view,
implementing view creation, property updates, child management, and
frame application. Handlers are registered with the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry] by
[`register_handlers`][pythonnative.native_views.ios.register_handlers].

Layout is owned by the pure-Python flex engine in
[`pythonnative.layout`][pythonnative.layout]: container handlers create
plain `UIView`s, the engine computes per-child frames in points, and
[`set_frame`][pythonnative.native_views.ios.IOSViewHandler.set_frame]
applies those frames via UIKit's classic ``frame`` property (with Auto
Layout disabled). Handlers therefore only deal with *visual* props and
ignore everything in
[`pythonnative.layout.LAYOUT_STYLE_KEYS`][pythonnative.layout.LAYOUT_STYLE_KEYS].

This module is only imported on iOS at runtime. Desktop tests inject a
mock registry via
[`set_registry`][pythonnative.native_views.set_registry] and never
trigger this import path.
"""

import ctypes as _ct
import math
from typing import Any, Callable, Dict, Optional, Tuple

from rubicon.objc import SEL, ObjCClass, objc_method

from .base import ViewHandler, _safe_max, parse_color_int

NSObject = ObjCClass("NSObject")
UIColor = ObjCClass("UIColor")
UIFont = ObjCClass("UIFont")


# ======================================================================
# Shared helpers
# ======================================================================


def _uicolor(color: Any) -> Any:
    """Convert a color value to a `UIColor` instance."""
    argb = parse_color_int(color)
    if argb < 0:
        argb += 0x100000000
    a = ((argb >> 24) & 0xFF) / 255.0
    r = ((argb >> 16) & 0xFF) / 255.0
    g = ((argb >> 8) & 0xFF) / 255.0
    b = (argb & 0xFF) / 255.0
    return UIColor.colorWithRed_green_blue_alpha_(r, g, b, a)


def _apply_common_visual(view: Any, props: Dict[str, Any]) -> None:
    """Apply visual properties shared across many handlers."""
    if "background_color" in props and props["background_color"] is not None:
        view.setBackgroundColor_(_uicolor(props["background_color"]))
    if "overflow" in props:
        view.setClipsToBounds_(props["overflow"] == "hidden")


# ======================================================================
# Base class with shared frame/measure implementations
# ======================================================================


class IOSViewHandler(ViewHandler):
    """Base class providing the shared `set_frame` / measure contract.

    All iOS handlers go through `set_frame` to apply the layout
    engine's computed frames via classic ``CGRect`` positioning (Auto
    Layout off). Child management defaults to UIKit's
    `addSubview_:` / `removeFromSuperview` API.
    """

    def set_frame(self, native_view: Any, x: float, y: float, width: float, height: float) -> None:
        if native_view is None:
            return
        try:
            frame_x = float(x)
            frame_y = float(y)
            frame_w = float(max(0.0, width))
            frame_h = float(max(0.0, height))
            native_view.setTranslatesAutoresizingMaskIntoConstraints_(True)
            native_view.setFrame_(((frame_x, frame_y), (frame_w, frame_h)))
            try:
                parent = native_view.superview
                set_content_size = getattr(parent, "setContentSize_", None)
                if set_content_size is not None:
                    bounds = parent.bounds
                    content_w = max(float(bounds.size.width), frame_x + frame_w)
                    content_h = max(float(bounds.size.height), frame_y + frame_h)
                    set_content_size((content_w, content_h))
            except Exception:
                pass
        except Exception:
            pass

    def measure_intrinsic(
        self,
        native_view: Any,
        max_width: float,
        max_height: float,
    ) -> Tuple[float, float]:
        try:
            mw = _safe_max(max_width, fallback=10000.0)
            mh = _safe_max(max_height, fallback=10000.0)
            size = native_view.sizeThatFits_((mw, mh))
            w = float(size.width)
            h = float(size.height)
            if math.isfinite(max_width):
                w = min(w, max_width)
            return (w, h)
        except Exception:
            return (0.0, 0.0)


# ======================================================================
# ObjC callback targets (retained at module level)
# ======================================================================

_pn_btn_handler_map: dict = {}
_pn_btn_callback_map: dict = {}
_pn_retained_views: list = []


class _PNButtonTarget(NSObject):  # type: ignore[valid-type]
    @objc_method
    def onTap_(self, sender: object) -> None:
        # Do not introspect ``sender`` here. On rubicon-objc 0.5.x the
        # selector trampoline can hand this callback a raw ObjC pointer;
        # calling ``getattr(sender, "ptr", ...)`` has been observed to
        # segfault before the user's callback runs.
        cb = _pn_btn_callback_map.get(id(self))
        if cb is not None:
            cb()


_pn_tf_handler_map: dict = {}


class _PNTextFieldTarget(NSObject):  # type: ignore[valid-type]
    _callback: Optional[Callable[[str], None]] = None

    @objc_method
    def onEdit_(self, sender: object) -> None:
        if self._callback is not None:
            try:
                text = str(sender.text) if sender and hasattr(sender, "text") else ""
                self._callback(text)
            except Exception:
                pass


_pn_switch_handler_map: dict = {}


class _PNSwitchTarget(NSObject):  # type: ignore[valid-type]
    _callback: Optional[Callable[[bool], None]] = None

    @objc_method
    def onToggle_(self, sender: object) -> None:
        if self._callback is not None:
            try:
                self._callback(bool(sender.isOn()))
            except Exception:
                pass


_pn_slider_handler_map: dict = {}


class _PNSliderTarget(NSObject):  # type: ignore[valid-type]
    _callback: Optional[Callable[[float], None]] = None

    @objc_method
    def onSlide_(self, sender: object) -> None:
        if self._callback is not None:
            try:
                self._callback(float(sender.value))
            except Exception:
                pass


# ======================================================================
# Flex container handler (shared by Column, Row, View)
# ======================================================================


class FlexContainerHandler(IOSViewHandler):
    """Container for flex layout — a bare `UIView`.

    All flex semantics (direction, alignment, distribution, padding)
    are computed by the layout engine and applied via
    [`set_frame`][pythonnative.native_views.ios.IOSViewHandler.set_frame].
    """

    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setTranslatesAutoresizingMaskIntoConstraints_(True)
        _apply_common_visual(v, props)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        _apply_common_visual(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        try:
            child.setTranslatesAutoresizingMaskIntoConstraints_(True)
        except Exception:
            pass
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        try:
            child.setTranslatesAutoresizingMaskIntoConstraints_(True)
        except Exception:
            pass
        parent.insertSubview_atIndex_(child, index)


# ======================================================================
# Leaf handlers
# ======================================================================


class TextHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        label = ObjCClass("UILabel").alloc().init()
        label.setNumberOfLines_(0)
        label.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self._apply(label, props)
        return label

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, label: Any, props: Dict[str, Any]) -> None:
        if "text" in props:
            label.setText_(str(props["text"]) if props["text"] is not None else "")
        if "font_size" in props and props["font_size"] is not None:
            if props.get("bold"):
                label.setFont_(UIFont.boldSystemFontOfSize_(float(props["font_size"])))
            else:
                label.setFont_(UIFont.systemFontOfSize_(float(props["font_size"])))
        elif "bold" in props and props["bold"]:
            # ``UILabel.font`` is a property in rubicon-objc, so use attribute
            # access (no parens) — calling it as ``label.font()`` would try to
            # invoke the returned ``UIFont`` ObjCInstance and raise TypeError.
            current_font = label.font
            try:
                size = float(current_font.pointSize) if current_font is not None else 17.0
            except Exception:
                size = 17.0
            label.setFont_(UIFont.boldSystemFontOfSize_(size))
        if "color" in props and props["color"] is not None:
            label.setTextColor_(_uicolor(props["color"]))
        if "background_color" in props and props["background_color"] is not None:
            label.setBackgroundColor_(_uicolor(props["background_color"]))
        if "max_lines" in props and props["max_lines"] is not None:
            label.setNumberOfLines_(int(props["max_lines"]))
        if "text_align" in props:
            mapping = {"left": 0, "center": 1, "right": 2}
            label.setTextAlignment_(mapping.get(props["text_align"], 0))


class ButtonHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        # ``UIButtonTypeSystem`` (1) gives us a properly-sized button
        # with intrinsicContentSize derived from the title; the default
        # ``UIButtonTypeCustom`` returns CGSizeZero from sizeThatFits_,
        # which makes the button collapse to 0×0 under the layout engine.
        btn = ObjCClass("UIButton").buttonWithType_(1)
        btn.setTranslatesAutoresizingMaskIntoConstraints_(True)
        btn.retain()
        _pn_retained_views.append(btn)
        self._apply(btn, props)
        return btn

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def measure_intrinsic(
        self,
        native_view: Any,
        max_width: float,
        max_height: float,
    ) -> Tuple[float, float]:
        # ``intrinsicContentSize`` honours the button's content insets and
        # title font; ``sizeThatFits_`` historically returns 0×0 for many
        # UIButton subtypes. Padding is added so the button has real
        # tappable area even on iOS 15+ where the default insets are 0.
        try:
            size = native_view.intrinsicContentSize()
            w = float(size.width) + 24.0
            h = float(size.height) + 12.0
            if math.isfinite(max_width):
                w = min(w, max_width)
            if math.isfinite(max_height):
                h = min(h, max_height)
            return (max(w, 44.0), max(h, 32.0))
        except Exception:
            return (44.0, 32.0)

    def _apply(self, btn: Any, props: Dict[str, Any]) -> None:
        if "title" in props:
            btn.setTitle_forState_(str(props["title"]) if props["title"] is not None else "", 0)
        if "font_size" in props and props["font_size"] is not None:
            # ``UIButton.titleLabel`` is a property in rubicon-objc; access it
            # as an attribute (no parens) — calling it would try to invoke the
            # returned UILabel and raise ``TypeError``.
            btn.titleLabel.setFont_(UIFont.systemFontOfSize_(float(props["font_size"])))
        if "background_color" in props and props["background_color"] is not None:
            btn.setBackgroundColor_(_uicolor(props["background_color"]))
            if "color" not in props:
                _white = UIColor.colorWithRed_green_blue_alpha_(1.0, 1.0, 1.0, 1.0)
                btn.setTitleColor_forState_(_white, 0)
        if "color" in props and props["color"] is not None:
            btn.setTitleColor_forState_(_uicolor(props["color"]), 0)
        if "enabled" in props:
            btn.setEnabled_(bool(props["enabled"]))
        if "on_click" in props:
            existing = _pn_btn_handler_map.get(id(btn))
            if existing is not None:
                _pn_btn_callback_map[id(existing)] = props["on_click"]
            else:
                handler = _PNButtonTarget.new()
                _pn_btn_handler_map[id(btn)] = handler
                _pn_btn_callback_map[id(handler)] = props["on_click"]
                btn.addTarget_action_forControlEvents_(handler, SEL("onTap:"), 1 << 6)


class ScrollViewHandler(IOSViewHandler):
    """Scroll container — wraps a single child whose height is unbounded.

    The child is positioned by the layout engine using its natural
    content height. The shared frame applier expands the parent
    `UIScrollView.contentSize` whenever a child frame extends beyond
    the visible bounds.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        sv = ObjCClass("UIScrollView").alloc().init()
        sv.setTranslatesAutoresizingMaskIntoConstraints_(True)
        if "background_color" in props and props["background_color"] is not None:
            sv.setBackgroundColor_(_uicolor(props["background_color"]))
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor_(_uicolor(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        try:
            child.setTranslatesAutoresizingMaskIntoConstraints_(True)
        except Exception:
            pass
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


class TextInputHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        tf = ObjCClass("UITextField").alloc().init()
        tf.setBorderStyle_(2)  # RoundedRect
        tf.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self._apply(tf, props)
        return tf

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, tf: Any, props: Dict[str, Any]) -> None:
        if "value" in props:
            tf.setText_(str(props["value"]) if props["value"] is not None else "")
        if "placeholder" in props:
            tf.setPlaceholder_(str(props["placeholder"]) if props["placeholder"] is not None else "")
        if "font_size" in props and props["font_size"] is not None:
            tf.setFont_(UIFont.systemFontOfSize_(float(props["font_size"])))
        if "color" in props and props["color"] is not None:
            tf.setTextColor_(_uicolor(props["color"]))
        if "background_color" in props and props["background_color"] is not None:
            tf.setBackgroundColor_(_uicolor(props["background_color"]))
        if "secure" in props and props["secure"]:
            tf.setSecureTextEntry_(True)
        if "on_change" in props:
            existing = _pn_tf_handler_map.get(id(tf))
            if existing is not None:
                existing._callback = props["on_change"]
            else:
                handler = _PNTextFieldTarget.new()
                handler._callback = props["on_change"]
                _pn_tf_handler_map[id(tf)] = handler
                tf.addTarget_action_forControlEvents_(handler, SEL("onEdit:"), 1 << 17)


class ImageHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        iv = ObjCClass("UIImageView").alloc().init()
        iv.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self._apply(iv, props)
        return iv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, iv: Any, props: Dict[str, Any]) -> None:
        if "background_color" in props and props["background_color"] is not None:
            iv.setBackgroundColor_(_uicolor(props["background_color"]))
        if "source" in props and props["source"]:
            self._load_source(iv, props["source"])
        if "scale_type" in props and props["scale_type"]:
            mapping = {"cover": 2, "contain": 1, "stretch": 0, "center": 4}
            iv.setContentMode_(mapping.get(props["scale_type"], 1))

    def _load_source(self, iv: Any, source: str) -> None:
        try:
            if source.startswith(("http://", "https://")):
                NSURL = ObjCClass("NSURL")
                NSData = ObjCClass("NSData")
                UIImage = ObjCClass("UIImage")
                url = NSURL.URLWithString_(source)
                data = NSData.dataWithContentsOfURL_(url)
                if data:
                    image = UIImage.imageWithData_(data)
                    if image:
                        iv.setImage_(image)
            else:
                UIImage = ObjCClass("UIImage")
                image = UIImage.imageNamed_(source)
                if image:
                    iv.setImage_(image)
        except Exception:
            pass


class SwitchHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sw = ObjCClass("UISwitch").alloc().init()
        sw.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self._apply(sw, props)
        return sw

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, sw: Any, props: Dict[str, Any]) -> None:
        if "value" in props:
            sw.setOn_animated_(bool(props["value"]), False)
        if "on_change" in props:
            existing = _pn_switch_handler_map.get(id(sw))
            if existing is not None:
                existing._callback = props["on_change"]
            else:
                handler = _PNSwitchTarget.new()
                handler._callback = props["on_change"]
                _pn_switch_handler_map[id(sw)] = handler
                sw.addTarget_action_forControlEvents_(handler, SEL("onToggle:"), 1 << 12)


class ProgressBarHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        pv = ObjCClass("UIProgressView").alloc().init()
        pv.setTranslatesAutoresizingMaskIntoConstraints_(True)
        if "value" in props:
            pv.setProgress_(float(props["value"]))
        return pv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "value" in changed:
            native_view.setProgress_(float(changed["value"]))


class ActivityIndicatorHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        ai = ObjCClass("UIActivityIndicatorView").alloc().init()
        ai.setTranslatesAutoresizingMaskIntoConstraints_(True)
        if props.get("animating", True):
            ai.startAnimating()
        return ai

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "animating" in changed:
            if changed["animating"]:
                native_view.startAnimating()
            else:
                native_view.stopAnimating()


class WebViewHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        wv = ObjCClass("WKWebView").alloc().init()
        wv.setTranslatesAutoresizingMaskIntoConstraints_(True)
        if "url" in props and props["url"]:
            NSURL = ObjCClass("NSURL")
            NSURLRequest = ObjCClass("NSURLRequest")
            url_obj = NSURL.URLWithString_(str(props["url"]))
            wv.loadRequest_(NSURLRequest.requestWithURL_(url_obj))
        return wv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "url" in changed and changed["url"]:
            NSURL = ObjCClass("NSURL")
            NSURLRequest = ObjCClass("NSURLRequest")
            url_obj = NSURL.URLWithString_(str(changed["url"]))
            native_view.loadRequest_(NSURLRequest.requestWithURL_(url_obj))


class SpacerHandler(IOSViewHandler):
    """Empty layout placeholder used as a flexible gap.

    All sizing semantics live in the layout engine; ``Spacer``
    behaves identically to a `View` with the same style props.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setTranslatesAutoresizingMaskIntoConstraints_(True)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass


class SafeAreaViewHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setTranslatesAutoresizingMaskIntoConstraints_(True)
        if "background_color" in props and props["background_color"] is not None:
            v.setBackgroundColor_(_uicolor(props["background_color"]))
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor_(_uicolor(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        try:
            child.setTranslatesAutoresizingMaskIntoConstraints_(True)
        except Exception:
            pass
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


class ModalHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setHidden_(True)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass

    def set_frame(self, native_view: Any, x: float, y: float, width: float, height: float) -> None:
        # Modal is a virtual placeholder — not rendered inline.
        return


class SliderHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sl = ObjCClass("UISlider").alloc().init()
        sl.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self._apply(sl, props)
        return sl

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, sl: Any, props: Dict[str, Any]) -> None:
        if "min_value" in props:
            sl.setMinimumValue_(float(props["min_value"]))
        if "max_value" in props:
            sl.setMaximumValue_(float(props["max_value"]))
        if "value" in props:
            sl.setValue_(float(props["value"]))
        if "on_change" in props:
            existing = _pn_slider_handler_map.get(id(sl))
            if existing is not None:
                existing._callback = props["on_change"]
            else:
                handler = _PNSliderTarget.new()
                handler._callback = props["on_change"]
                _pn_slider_handler_map[id(sl)] = handler
                sl.addTarget_action_forControlEvents_(handler, SEL("onSlide:"), 1 << 12)


_pn_tabbar_state: dict = {"callback": None, "items": []}
_pn_tabbar_delegate_installed: bool = False
_pn_tabbar_delegate_ptr: Any = None

# ---------------------------------------------------------------------------
# UITabBar delegate via raw ctypes
#
# rubicon-objc's @objc_method crashes (SIGSEGV in PyObject_GetAttr) when
# UIKit invokes the delegate through the FFI closure — the reconstructed
# Python wrappers for ``self`` or ``item`` end up with ob_type == NULL.
#
# We sidestep rubicon-objc entirely: create a minimal ObjC class with
# libobjc, register a CFUNCTYPE IMP for tabBar:didSelectItem:, and use
# objc_msgSend to read ``item.tag`` from the raw pointer.
# ---------------------------------------------------------------------------

_libobjc = _ct.cdll.LoadLibrary("libobjc.A.dylib")

_sel_reg = _libobjc.sel_registerName
_sel_reg.restype = _ct.c_void_p
_sel_reg.argtypes = [_ct.c_char_p]

_get_cls = _libobjc.objc_getClass
_get_cls.restype = _ct.c_void_p
_get_cls.argtypes = [_ct.c_char_p]

_alloc_cls = _libobjc.objc_allocateClassPair
_alloc_cls.restype = _ct.c_void_p
_alloc_cls.argtypes = [_ct.c_void_p, _ct.c_char_p, _ct.c_size_t]

_reg_cls = _libobjc.objc_registerClassPair
_reg_cls.argtypes = [_ct.c_void_p]

_add_method = _libobjc.class_addMethod
_add_method.restype = _ct.c_bool
_add_method.argtypes = [_ct.c_void_p, _ct.c_void_p, _ct.c_void_p, _ct.c_char_p]

_objc_msgSend = _libobjc.objc_msgSend

_SEL_ALLOC = _sel_reg(b"alloc")
_SEL_INIT = _sel_reg(b"init")
_SEL_RETAIN = _sel_reg(b"retain")
_SEL_SET_DELEGATE = _sel_reg(b"setDelegate:")
_SEL_TAG = _sel_reg(b"tag")

# IMP type: void (id self, SEL _cmd, id tabBar, id item)
_DELEGATE_IMP_TYPE = _ct.CFUNCTYPE(None, _ct.c_void_p, _ct.c_void_p, _ct.c_void_p, _ct.c_void_p)


def _tabbar_did_select_imp(self_ptr: int, cmd_ptr: int, tabbar_ptr: int, item_ptr: int) -> None:
    """Raw C callback for ``tabBar:didSelectItem:``."""
    try:
        _objc_msgSend.restype = _ct.c_long
        _objc_msgSend.argtypes = [_ct.c_void_p, _ct.c_void_p]
        tag: int = _objc_msgSend(item_ptr, _SEL_TAG)

        cb = _pn_tabbar_state["callback"]
        tab_items = _pn_tabbar_state["items"]
        if cb is not None and tab_items and 0 <= tag < len(tab_items):
            cb(tab_items[tag].get("name", ""))
    except Exception:
        pass


_tabbar_imp_ref = _DELEGATE_IMP_TYPE(_tabbar_did_select_imp)

_NS_OBJECT_CLS = _get_cls(b"NSObject")
_PN_DELEGATE_CLS = _alloc_cls(_NS_OBJECT_CLS, b"_PNTabBarDelegateCTypes", 0)
if _PN_DELEGATE_CLS:
    _add_method(
        _PN_DELEGATE_CLS,
        _sel_reg(b"tabBar:didSelectItem:"),
        _ct.cast(_tabbar_imp_ref, _ct.c_void_p),
        b"v@:@@",
    )
    _reg_cls(_PN_DELEGATE_CLS)


def _ensure_tabbar_delegate(tab_bar: Any) -> None:
    """Create the singleton delegate (if needed) and assign it to *tab_bar*."""
    global _pn_tabbar_delegate_ptr
    if _pn_tabbar_delegate_ptr is None and _PN_DELEGATE_CLS:
        _objc_msgSend.restype = _ct.c_void_p
        _objc_msgSend.argtypes = [_ct.c_void_p, _ct.c_void_p]
        raw = _objc_msgSend(_PN_DELEGATE_CLS, _SEL_ALLOC)
        raw = _objc_msgSend(raw, _SEL_INIT)
        raw = _objc_msgSend(raw, _SEL_RETAIN)
        _pn_tabbar_delegate_ptr = raw

    if _pn_tabbar_delegate_ptr is not None:
        _objc_msgSend.restype = None
        _objc_msgSend.argtypes = [_ct.c_void_p, _ct.c_void_p, _ct.c_void_p]
        tab_bar_ptr = tab_bar.ptr if hasattr(tab_bar, "ptr") else tab_bar
        _objc_msgSend(tab_bar_ptr, _SEL_SET_DELEGATE, _pn_tabbar_delegate_ptr)


class TabBarHandler(IOSViewHandler):
    """Native tab bar using ``UITabBar``.

    Each tab is a ``UITabBarItem`` with a ``tag`` matching its index
    in the items list. A raw ctypes delegate forwards selection
    events back to the Python ``on_tab_select`` callback.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        from .. import platform_metrics

        initial_h = platform_metrics.ios_tab_bar_height()
        tab_bar = ObjCClass("UITabBar").alloc().initWithFrame_(((0, 0), (0, initial_h)))
        tab_bar.setTranslatesAutoresizingMaskIntoConstraints_(True)
        tab_bar.retain()
        _pn_retained_views.append(tab_bar)
        self._apply_full(tab_bar, props)
        return tab_bar

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply_partial(native_view, changed)

    def measure_intrinsic(
        self,
        native_view: Any,
        max_width: float,
        max_height: float,
    ) -> Tuple[float, float]:
        # ``UITabBar.sizeThatFits_`` is platform-version dependent and
        # has historically returned 0 in some configurations. A
        # constant matches the standard UIKit tab-bar height and keeps
        # the layout deterministic at first paint. The bottom
        # safe-area inset is added on top so the bar can reach the
        # screen edge — without it the pill bar floats with an empty
        # 34 pt gap below it on devices with a home indicator.
        from .. import platform_metrics

        w = max_width if math.isfinite(max_width) else 320.0
        h = platform_metrics.ios_tab_bar_height()
        return (w, h)

    def _apply_full(self, tab_bar: Any, props: Dict[str, Any]) -> None:
        items = props.get("items", [])
        self._set_bar_items(tab_bar, items)
        self._set_active(tab_bar, props.get("active_tab"), items)
        self._set_callback(tab_bar, props.get("on_tab_select"), items)

    def _apply_partial(self, tab_bar: Any, changed: Dict[str, Any]) -> None:
        prev_items = _pn_tabbar_state["items"]

        if "items" in changed:
            items = changed["items"]
            self._set_bar_items(tab_bar, items)
        else:
            items = prev_items

        if "active_tab" in changed:
            self._set_active(tab_bar, changed["active_tab"], items)

        if "on_tab_select" in changed:
            self._set_callback(tab_bar, changed["on_tab_select"], items)

    def _set_bar_items(self, tab_bar: Any, items: list) -> None:
        UITabBarItem = ObjCClass("UITabBarItem")
        bar_items = []
        for i, item in enumerate(items):
            title = item.get("title", item.get("name", ""))
            bar_item = UITabBarItem.alloc().initWithTitle_image_tag_(str(title), None, i)
            bar_items.append(bar_item)
        tab_bar.setItems_animated_(bar_items, False)

    def _set_active(self, tab_bar: Any, active: Any, items: list) -> None:
        if not active or not items:
            return
        for i, item in enumerate(items):
            if item.get("name") == active:
                try:
                    all_items = list(tab_bar.items or [])
                    if i < len(all_items):
                        tab_bar.setSelectedItem_(all_items[i])
                except Exception:
                    pass
                break

    def _set_callback(self, tab_bar: Any, cb: Any, items: list) -> None:
        _pn_tabbar_state["callback"] = cb
        _pn_tabbar_state["items"] = items
        _ensure_tabbar_delegate(tab_bar)


class PressableHandler(IOSViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setTranslatesAutoresizingMaskIntoConstraints_(True)
        v.setUserInteractionEnabled_(True)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass

    def add_child(self, parent: Any, child: Any) -> None:
        try:
            child.setTranslatesAutoresizingMaskIntoConstraints_(True)
        except Exception:
            pass
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


# ======================================================================
# Registration
# ======================================================================


def register_handlers(registry: Any) -> None:
    """Register all iOS view handlers with the given registry."""
    flex = FlexContainerHandler()
    registry.register("Text", TextHandler())
    registry.register("Button", ButtonHandler())
    registry.register("Column", flex)
    registry.register("Row", flex)
    registry.register("View", flex)
    registry.register("ScrollView", ScrollViewHandler())
    registry.register("TextInput", TextInputHandler())
    registry.register("Image", ImageHandler())
    registry.register("Switch", SwitchHandler())
    registry.register("ProgressBar", ProgressBarHandler())
    registry.register("ActivityIndicator", ActivityIndicatorHandler())
    registry.register("WebView", WebViewHandler())
    registry.register("Spacer", SpacerHandler())
    registry.register("SafeAreaView", SafeAreaViewHandler())
    registry.register("Modal", ModalHandler())
    registry.register("Slider", SliderHandler())
    registry.register("TabBar", TabBarHandler())
    registry.register("Pressable", PressableHandler())


__all__ = [
    "IOSViewHandler",
    "FlexContainerHandler",
    "TextHandler",
    "ButtonHandler",
    "ScrollViewHandler",
    "TextInputHandler",
    "ImageHandler",
    "SwitchHandler",
    "ProgressBarHandler",
    "ActivityIndicatorHandler",
    "WebViewHandler",
    "SpacerHandler",
    "SafeAreaViewHandler",
    "ModalHandler",
    "SliderHandler",
    "TabBarHandler",
    "PressableHandler",
    "register_handlers",
]
