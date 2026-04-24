"""iOS native-view handlers (rubicon-objc).

Each handler class maps a PythonNative element type to a UIKit view,
implementing view creation, property updates, and child management.
Handlers are registered with the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry] by
[`register_handlers`][pythonnative.native_views.ios.register_handlers].

This module is only imported on iOS at runtime. Desktop tests inject a
mock registry via
[`set_registry`][pythonnative.native_views.set_registry] and never
trigger this import path. Layout uses Auto Layout constraints
exclusively; props that map onto layout (`flex`, `padding`, etc.) are
translated into the corresponding `NSLayoutConstraint`s on update.
"""

import ctypes as _ct
from typing import Any, Callable, Dict, Optional

from rubicon.objc import SEL, ObjCClass, objc_method

from .base import CONTAINER_KEYS, LAYOUT_KEYS, ViewHandler, is_vertical, parse_color_int, resolve_padding

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


def _apply_ios_layout(view: Any, props: Dict[str, Any]) -> None:
    """Apply common layout constraints to an iOS view."""
    if "width" in props and props["width"] is not None:
        try:
            for c in list(view.constraints or []):
                if c.firstAttribute == 7:  # NSLayoutAttributeWidth
                    c.setActive_(False)
            view.widthAnchor.constraintEqualToConstant_(float(props["width"])).setActive_(True)
        except Exception:
            pass
    if "height" in props and props["height"] is not None:
        try:
            for c in list(view.constraints or []):
                if c.firstAttribute == 8:  # NSLayoutAttributeHeight
                    c.setActive_(False)
            view.heightAnchor.constraintEqualToConstant_(float(props["height"])).setActive_(True)
        except Exception:
            pass
    if "min_width" in props and props["min_width"] is not None:
        try:
            view.widthAnchor.constraintGreaterThanOrEqualToConstant_(float(props["min_width"])).setActive_(True)
        except Exception:
            pass
    if "min_height" in props and props["min_height"] is not None:
        try:
            view.heightAnchor.constraintGreaterThanOrEqualToConstant_(float(props["min_height"])).setActive_(True)
        except Exception:
            pass


def _apply_common_visual(view: Any, props: Dict[str, Any]) -> None:
    """Apply visual properties shared across many handlers."""
    if "background_color" in props and props["background_color"] is not None:
        view.setBackgroundColor_(_uicolor(props["background_color"]))
    if "overflow" in props:
        view.setClipsToBounds_(props["overflow"] == "hidden")


def _apply_flex_container(sv: Any, props: Dict[str, Any]) -> None:
    """Apply flex container properties to a UIStackView.

    Handles axis, spacing, alignment, distribution, background, padding, and overflow.
    """
    if "flex_direction" in props:
        vertical = is_vertical(props["flex_direction"])
        sv.setAxis_(1 if vertical else 0)

    if "spacing" in props and props["spacing"]:
        sv.setSpacing_(float(props["spacing"]))

    ai = props.get("align_items") or props.get("alignment")
    if ai:
        direction = props.get("flex_direction")
        vertical = is_vertical(direction) if direction else bool(sv.axis())
        if vertical:
            alignment_map = {
                "stretch": 0,
                "fill": 0,
                "flex_start": 1,
                "leading": 1,
                "center": 3,
                "flex_end": 4,
                "trailing": 4,
            }
        else:
            alignment_map = {
                "stretch": 0,
                "fill": 0,
                "flex_start": 1,
                "top": 1,
                "center": 3,
                "flex_end": 4,
                "bottom": 4,
            }
        sv.setAlignment_(alignment_map.get(ai, 0))

    jc = props.get("justify_content")
    if jc:
        # UIStackViewDistribution:
        #   0 = fill, 1 = fillEqually, 2 = fillProportionally,
        #   3 = equalSpacing (≈ space_between), 4 = equalCentering (≈ space_evenly)
        distribution_map = {
            "flex_start": 0,
            "center": 0,
            "flex_end": 0,
            "space_between": 3,
            "space_around": 4,
            "space_evenly": 4,
        }
        sv.setDistribution_(distribution_map.get(jc, 0))

    _apply_common_visual(sv, props)

    if "padding" in props:
        left, top, right, bottom = resolve_padding(props["padding"])
        sv.setLayoutMarginsRelativeArrangement_(True)
        try:
            sv.setDirectionalLayoutMargins_((top, left, bottom, right))
        except Exception:
            sv.setLayoutMargins_((top, left, bottom, right))


# ======================================================================
# ObjC callback targets (retained at module level)
# ======================================================================

_pn_btn_handler_map: dict = {}
_pn_retained_views: list = []


class _PNButtonTarget(NSObject):  # type: ignore[valid-type]
    _callback: Optional[Callable[[], None]] = None

    @objc_method
    def onTap_(self, sender: object) -> None:
        if self._callback is not None:
            self._callback()


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


class FlexContainerHandler(ViewHandler):
    """Unified handler for flex layout containers (Column, Row, View).

    All three element types use ``UIStackView`` with axis determined
    by the ``flex_direction`` prop.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        sv = ObjCClass("UIStackView").alloc().initWithFrame_(((0, 0), (0, 0)))
        direction = props.get("flex_direction", "column")
        sv.setAxis_(1 if is_vertical(direction) else 0)
        _apply_flex_container(sv, props)
        _apply_ios_layout(sv, props)
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if changed.keys() & CONTAINER_KEYS:
            _apply_flex_container(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addArrangedSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeArrangedSubview_(child)
        child.removeFromSuperview()

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        parent.insertArrangedSubview_atIndex_(child, index)


# ======================================================================
# Leaf handlers
# ======================================================================


class TextHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        label = ObjCClass("UILabel").alloc().init()
        self._apply(label, props)
        _apply_ios_layout(label, props)
        return label

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def _apply(self, label: Any, props: Dict[str, Any]) -> None:
        if "text" in props:
            label.setText_(str(props["text"]))
        if "font_size" in props and props["font_size"] is not None:
            if props.get("bold"):
                label.setFont_(UIFont.boldSystemFontOfSize_(float(props["font_size"])))
            else:
                label.setFont_(UIFont.systemFontOfSize_(float(props["font_size"])))
        elif "bold" in props and props["bold"]:
            size = label.font().pointSize() if label.font() else 17.0
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


class ButtonHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        btn = ObjCClass("UIButton").alloc().init()
        btn.retain()
        _pn_retained_views.append(btn)
        _ios_blue = UIColor.colorWithRed_green_blue_alpha_(0.0, 0.478, 1.0, 1.0)
        btn.setTitleColor_forState_(_ios_blue, 0)
        self._apply(btn, props)
        _apply_ios_layout(btn, props)
        return btn

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def _apply(self, btn: Any, props: Dict[str, Any]) -> None:
        if "title" in props:
            btn.setTitle_forState_(str(props["title"]), 0)
        if "font_size" in props and props["font_size"] is not None:
            btn.titleLabel().setFont_(UIFont.systemFontOfSize_(float(props["font_size"])))
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
                existing._callback = props["on_click"]
            else:
                handler = _PNButtonTarget.new()
                handler._callback = props["on_click"]
                _pn_btn_handler_map[id(btn)] = handler
                btn.addTarget_action_forControlEvents_(handler, SEL("onTap:"), 1 << 6)


class ScrollViewHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sv = ObjCClass("UIScrollView").alloc().init()
        if "background_color" in props and props["background_color"] is not None:
            sv.setBackgroundColor_(_uicolor(props["background_color"]))
        _apply_ios_layout(sv, props)
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor_(_uicolor(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        child.setTranslatesAutoresizingMaskIntoConstraints_(False)
        parent.addSubview_(child)
        content_guide = parent.contentLayoutGuide
        frame_guide = parent.frameLayoutGuide
        child.topAnchor.constraintEqualToAnchor_(content_guide.topAnchor).setActive_(True)
        child.leadingAnchor.constraintEqualToAnchor_(content_guide.leadingAnchor).setActive_(True)
        child.trailingAnchor.constraintEqualToAnchor_(content_guide.trailingAnchor).setActive_(True)
        child.bottomAnchor.constraintEqualToAnchor_(content_guide.bottomAnchor).setActive_(True)
        child.widthAnchor.constraintEqualToAnchor_(frame_guide.widthAnchor).setActive_(True)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


class TextInputHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        tf = ObjCClass("UITextField").alloc().init()
        tf.setBorderStyle_(2)  # RoundedRect
        self._apply(tf, props)
        _apply_ios_layout(tf, props)
        return tf

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def _apply(self, tf: Any, props: Dict[str, Any]) -> None:
        if "value" in props:
            tf.setText_(str(props["value"]))
        if "placeholder" in props:
            tf.setPlaceholder_(str(props["placeholder"]))
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


class ImageHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        iv = ObjCClass("UIImageView").alloc().init()
        self._apply(iv, props)
        _apply_ios_layout(iv, props)
        return iv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

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


class SwitchHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sw = ObjCClass("UISwitch").alloc().init()
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


class ProgressBarHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        pv = ObjCClass("UIProgressView").alloc().init()
        if "value" in props:
            pv.setProgress_(float(props["value"]))
        _apply_ios_layout(pv, props)
        return pv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "value" in changed:
            native_view.setProgress_(float(changed["value"]))


class ActivityIndicatorHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        ai = ObjCClass("UIActivityIndicatorView").alloc().init()
        if props.get("animating", True):
            ai.startAnimating()
        return ai

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "animating" in changed:
            if changed["animating"]:
                native_view.startAnimating()
            else:
                native_view.stopAnimating()


class WebViewHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        wv = ObjCClass("WKWebView").alloc().init()
        if "url" in props and props["url"]:
            NSURL = ObjCClass("NSURL")
            NSURLRequest = ObjCClass("NSURLRequest")
            url_obj = NSURL.URLWithString_(str(props["url"]))
            wv.loadRequest_(NSURLRequest.requestWithURL_(url_obj))
        _apply_ios_layout(wv, props)
        return wv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "url" in changed and changed["url"]:
            NSURL = ObjCClass("NSURL")
            NSURLRequest = ObjCClass("NSURLRequest")
            url_obj = NSURL.URLWithString_(str(changed["url"]))
            native_view.loadRequest_(NSURLRequest.requestWithURL_(url_obj))


class SpacerHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        if "size" in props and props["size"] is not None:
            size = float(props["size"])
            v.setFrame_(((0, 0), (size, size)))
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "size" in changed and changed["size"] is not None:
            size = float(changed["size"])
            native_view.setFrame_(((0, 0), (size, size)))


class SafeAreaViewHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        if "background_color" in props and props["background_color"] is not None:
            v.setBackgroundColor_(_uicolor(props["background_color"]))
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor_(_uicolor(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


class ModalHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setHidden_(True)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass


class SliderHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sl = ObjCClass("UISlider").alloc().init()
        self._apply(sl, props)
        _apply_ios_layout(sl, props)
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

# Pre-register selectors used in the raw delegate path
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


# prevent GC of the C callback
_tabbar_imp_ref = _DELEGATE_IMP_TYPE(_tabbar_did_select_imp)

# Create and register a minimal ObjC class for the delegate
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


class TabBarHandler(ViewHandler):
    """Native tab bar using ``UITabBar``.

    Each tab is a ``UITabBarItem`` with a ``tag`` matching its index
    in the items list.  A raw ctypes delegate forwards selection
    events back to the Python ``on_tab_select`` callback.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        tab_bar = ObjCClass("UITabBar").alloc().initWithFrame_(((0, 0), (0, 49)))
        tab_bar.retain()
        _pn_retained_views.append(tab_bar)
        self._apply_full(tab_bar, props)
        _apply_ios_layout(tab_bar, props)
        return tab_bar

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply_partial(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

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


class PressableHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        v.setUserInteractionEnabled_(True)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass

    def add_child(self, parent: Any, child: Any) -> None:
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
