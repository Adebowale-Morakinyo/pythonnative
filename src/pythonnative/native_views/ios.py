"""iOS native view handlers (rubicon-objc).

Each handler class maps a PythonNative element type to a UIKit widget,
implementing view creation, property updates, and child management.

This module is only imported on iOS at runtime; desktop tests inject
a mock registry via :func:`~.set_registry` and never trigger this import.
"""

from typing import Any, Callable, Dict, Optional

from rubicon.objc import SEL, ObjCClass, objc_method

from .base import LAYOUT_KEYS, ViewHandler, parse_color_int, resolve_padding

NSObject = ObjCClass("NSObject")
UIColor = ObjCClass("UIColor")
UIFont = ObjCClass("UIFont")


# ======================================================================
# Shared helpers
# ======================================================================


def _uicolor(color: Any) -> Any:
    """Convert a color value to a ``UIColor`` instance."""
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


def _apply_stack_props(sv: Any, props: Dict[str, Any], *, vertical: bool) -> None:
    """Apply spacing, alignment, distribution, background, and padding to a UIStackView.

    Column and Row handlers share identical logic except for axis-dependent
    alignment constants.  This helper consolidates that logic.
    """
    if "spacing" in props and props["spacing"]:
        sv.setSpacing_(float(props["spacing"]))

    ai = props.get("align_items") or props.get("alignment")
    if ai:
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
        distribution_map = {
            "flex_start": 0,
            "center": 0,
            "flex_end": 0,
            "space_between": 3,
            "space_around": 4,
            "space_evenly": 4,
        }
        sv.setDistribution_(distribution_map.get(jc, 0))

    if "background_color" in props and props["background_color"] is not None:
        sv.setBackgroundColor_(_uicolor(props["background_color"]))

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
# Handlers
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


class ColumnHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sv = ObjCClass("UIStackView").alloc().initWithFrame_(((0, 0), (0, 0)))
        sv.setAxis_(1)  # vertical
        _apply_stack_props(sv, props, vertical=True)
        _apply_ios_layout(sv, props)
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        _apply_stack_props(native_view, changed, vertical=True)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addArrangedSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeArrangedSubview_(child)
        child.removeFromSuperview()

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        parent.insertArrangedSubview_atIndex_(child, index)


class RowHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sv = ObjCClass("UIStackView").alloc().initWithFrame_(((0, 0), (0, 0)))
        sv.setAxis_(0)  # horizontal
        _apply_stack_props(sv, props, vertical=False)
        _apply_ios_layout(sv, props)
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        _apply_stack_props(native_view, changed, vertical=False)
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addArrangedSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeArrangedSubview_(child)
        child.removeFromSuperview()

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        parent.insertArrangedSubview_atIndex_(child, index)


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


class GenericViewHandler(ViewHandler):
    """Handler for the ``View`` element (generic UIView container)."""

    def create(self, props: Dict[str, Any]) -> Any:
        v = ObjCClass("UIView").alloc().init()
        if "background_color" in props and props["background_color"] is not None:
            v.setBackgroundColor_(_uicolor(props["background_color"]))
        _apply_ios_layout(v, props)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor_(_uicolor(changed["background_color"]))
        if changed.keys() & LAYOUT_KEYS:
            _apply_ios_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addSubview_(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        child.removeFromSuperview()


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
    registry.register("Text", TextHandler())
    registry.register("Button", ButtonHandler())
    registry.register("Column", ColumnHandler())
    registry.register("Row", RowHandler())
    registry.register("ScrollView", ScrollViewHandler())
    registry.register("TextInput", TextInputHandler())
    registry.register("Image", ImageHandler())
    registry.register("Switch", SwitchHandler())
    registry.register("ProgressBar", ProgressBarHandler())
    registry.register("ActivityIndicator", ActivityIndicatorHandler())
    registry.register("WebView", WebViewHandler())
    registry.register("Spacer", SpacerHandler())
    registry.register("View", GenericViewHandler())
    registry.register("SafeAreaView", SafeAreaViewHandler())
    registry.register("Modal", ModalHandler())
    registry.register("Slider", SliderHandler())
    registry.register("Pressable", PressableHandler())
