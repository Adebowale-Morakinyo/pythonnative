"""Platform-specific native view creation and update logic.

This module replaces the old per-widget files.  All platform-branching
lives here, guarded behind lazy imports so the module can be imported
on desktop for testing.
"""

from typing import Any, Callable, Dict, Optional, Union

from .utils import IS_ANDROID

# ======================================================================
# Abstract handler protocol
# ======================================================================


class ViewHandler:
    """Protocol for creating, updating, and managing children of a native view type."""

    def create(self, props: Dict[str, Any]) -> Any:
        raise NotImplementedError

    def update(self, native_view: Any, changed_props: Dict[str, Any]) -> None:
        raise NotImplementedError

    def add_child(self, parent: Any, child: Any) -> None:
        pass

    def remove_child(self, parent: Any, child: Any) -> None:
        pass

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        self.add_child(parent, child)


# ======================================================================
# Registry
# ======================================================================


class NativeViewRegistry:
    """Maps element type names to platform-specific :class:`ViewHandler` instances."""

    def __init__(self) -> None:
        self._handlers: Dict[str, ViewHandler] = {}

    def register(self, type_name: str, handler: ViewHandler) -> None:
        self._handlers[type_name] = handler

    def create_view(self, type_name: str, props: Dict[str, Any]) -> Any:
        handler = self._handlers.get(type_name)
        if handler is None:
            raise ValueError(f"Unknown element type: {type_name!r}")
        return handler.create(props)

    def update_view(self, native_view: Any, type_name: str, changed_props: Dict[str, Any]) -> None:
        handler = self._handlers.get(type_name)
        if handler is not None:
            handler.update(native_view, changed_props)

    def add_child(self, parent: Any, child: Any, parent_type: str) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.add_child(parent, child)

    def remove_child(self, parent: Any, child: Any, parent_type: str) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.remove_child(parent, child)

    def insert_child(self, parent: Any, child: Any, parent_type: str, index: int) -> None:
        handler = self._handlers.get(parent_type)
        if handler is not None:
            handler.insert_child(parent, child, index)


# ======================================================================
# Shared helpers
# ======================================================================


def parse_color_int(color: Union[str, int]) -> int:
    """Parse ``#RRGGBB`` / ``#AARRGGBB`` hex string or raw int to a *signed* ARGB int.

    Java's ``setBackgroundColor`` et al. expect a signed 32-bit int, so values
    with a high alpha byte (e.g. 0xFF…) must be converted to negative ints.
    """
    if isinstance(color, int):
        val = color
    else:
        c = color.strip().lstrip("#")
        if len(c) == 6:
            c = "FF" + c
        val = int(c, 16)
    if val > 0x7FFFFFFF:
        val -= 0x100000000
    return val


def _resolve_padding(
    padding: Any,
) -> tuple:
    """Normalise various padding representations to ``(left, top, right, bottom)``."""
    if padding is None:
        return (0, 0, 0, 0)
    if isinstance(padding, (int, float)):
        v = int(padding)
        return (v, v, v, v)
    if isinstance(padding, dict):
        h = int(padding.get("horizontal", 0))
        v = int(padding.get("vertical", 0))
        left = int(padding.get("left", h))
        right = int(padding.get("right", h))
        top = int(padding.get("top", v))
        bottom = int(padding.get("bottom", v))
        a = int(padding.get("all", 0))
        if a:
            left = left or a
            right = right or a
            top = top or a
            bottom = bottom or a
        return (left, top, right, bottom)
    return (0, 0, 0, 0)


# ======================================================================
# Platform handler registration (lazy imports inside functions)
# ======================================================================


def _register_android_handlers(registry: NativeViewRegistry) -> None:  # noqa: C901
    from java import dynamic_proxy, jclass

    from .utils import get_android_context

    def _ctx() -> Any:
        return get_android_context()

    def _density() -> float:
        return float(_ctx().getResources().getDisplayMetrics().density)

    def _dp(value: float) -> int:
        return int(value * _density())

    # ---- Text -----------------------------------------------------------
    class AndroidTextHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            tv = jclass("android.widget.TextView")(_ctx())
            self._apply(tv, props)
            return tv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, tv: Any, props: Dict[str, Any]) -> None:
            if "text" in props:
                tv.setText(str(props["text"]))
            if "font_size" in props and props["font_size"] is not None:
                tv.setTextSize(float(props["font_size"]))
            if "color" in props and props["color"] is not None:
                tv.setTextColor(parse_color_int(props["color"]))
            if "background_color" in props and props["background_color"] is not None:
                tv.setBackgroundColor(parse_color_int(props["background_color"]))
            if "bold" in props and props["bold"]:
                tv.setTypeface(tv.getTypeface(), 1)  # Typeface.BOLD = 1
            if "max_lines" in props and props["max_lines"] is not None:
                tv.setMaxLines(int(props["max_lines"]))
            if "text_align" in props:
                Gravity = jclass("android.view.Gravity")
                mapping = {"left": Gravity.START, "center": Gravity.CENTER, "right": Gravity.END}
                tv.setGravity(mapping.get(props["text_align"], Gravity.START))

    # ---- Button ---------------------------------------------------------
    class AndroidButtonHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            btn = jclass("android.widget.Button")(_ctx())
            self._apply(btn, props)
            return btn

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, btn: Any, props: Dict[str, Any]) -> None:
            if "title" in props:
                btn.setText(str(props["title"]))
            if "font_size" in props and props["font_size"] is not None:
                btn.setTextSize(float(props["font_size"]))
            if "color" in props and props["color"] is not None:
                btn.setTextColor(parse_color_int(props["color"]))
            if "background_color" in props and props["background_color"] is not None:
                btn.setBackgroundColor(parse_color_int(props["background_color"]))
            if "enabled" in props:
                btn.setEnabled(bool(props["enabled"]))
            if "on_click" in props:
                cb = props["on_click"]
                if cb is not None:

                    class ClickProxy(dynamic_proxy(jclass("android.view.View").OnClickListener)):
                        def __init__(self, callback: Callable[[], None]) -> None:
                            super().__init__()
                            self.callback = callback

                        def onClick(self, view: Any) -> None:
                            self.callback()

                    btn.setOnClickListener(ClickProxy(cb))
                else:
                    btn.setOnClickListener(None)

    # ---- Column (vertical LinearLayout) ---------------------------------
    class AndroidColumnHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            ll = jclass("android.widget.LinearLayout")(_ctx())
            ll.setOrientation(jclass("android.widget.LinearLayout").VERTICAL)
            self._apply(ll, props)
            return ll

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, ll: Any, props: Dict[str, Any]) -> None:
            if "spacing" in props and props["spacing"]:
                px = _dp(float(props["spacing"]))
                GradientDrawable = jclass("android.graphics.drawable.GradientDrawable")
                d = GradientDrawable()
                d.setColor(0x00000000)
                d.setSize(1, px)
                ll.setShowDividers(jclass("android.widget.LinearLayout").SHOW_DIVIDER_MIDDLE)
                ll.setDividerDrawable(d)
            if "padding" in props:
                left, top, right, bottom = _resolve_padding(props["padding"])
                ll.setPadding(_dp(left), _dp(top), _dp(right), _dp(bottom))
            if "alignment" in props and props["alignment"]:
                Gravity = jclass("android.view.Gravity")
                mapping = {
                    "fill": Gravity.FILL_HORIZONTAL,
                    "center": Gravity.CENTER_HORIZONTAL,
                    "leading": Gravity.START,
                    "start": Gravity.START,
                    "trailing": Gravity.END,
                    "end": Gravity.END,
                }
                ll.setGravity(mapping.get(props["alignment"], Gravity.FILL_HORIZONTAL))
            if "background_color" in props and props["background_color"] is not None:
                ll.setBackgroundColor(parse_color_int(props["background_color"]))

        def add_child(self, parent: Any, child: Any) -> None:
            parent.addView(child)

        def remove_child(self, parent: Any, child: Any) -> None:
            parent.removeView(child)

        def insert_child(self, parent: Any, child: Any, index: int) -> None:
            parent.addView(child, index)

    # ---- Row (horizontal LinearLayout) ----------------------------------
    class AndroidRowHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            ll = jclass("android.widget.LinearLayout")(_ctx())
            ll.setOrientation(jclass("android.widget.LinearLayout").HORIZONTAL)
            self._apply(ll, props)
            return ll

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, ll: Any, props: Dict[str, Any]) -> None:
            if "spacing" in props and props["spacing"]:
                px = _dp(float(props["spacing"]))
                GradientDrawable = jclass("android.graphics.drawable.GradientDrawable")
                d = GradientDrawable()
                d.setColor(0x00000000)
                d.setSize(px, 1)
                ll.setShowDividers(jclass("android.widget.LinearLayout").SHOW_DIVIDER_MIDDLE)
                ll.setDividerDrawable(d)
            if "padding" in props:
                left, top, right, bottom = _resolve_padding(props["padding"])
                ll.setPadding(_dp(left), _dp(top), _dp(right), _dp(bottom))
            if "alignment" in props and props["alignment"]:
                Gravity = jclass("android.view.Gravity")
                mapping = {
                    "fill": Gravity.FILL_VERTICAL,
                    "center": Gravity.CENTER_VERTICAL,
                    "top": Gravity.TOP,
                    "bottom": Gravity.BOTTOM,
                }
                ll.setGravity(mapping.get(props["alignment"], Gravity.FILL_VERTICAL))
            if "background_color" in props and props["background_color"] is not None:
                ll.setBackgroundColor(parse_color_int(props["background_color"]))

        def add_child(self, parent: Any, child: Any) -> None:
            parent.addView(child)

        def remove_child(self, parent: Any, child: Any) -> None:
            parent.removeView(child)

        def insert_child(self, parent: Any, child: Any, index: int) -> None:
            parent.addView(child, index)

    # ---- ScrollView -----------------------------------------------------
    class AndroidScrollViewHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sv = jclass("android.widget.ScrollView")(_ctx())
            if "background_color" in props and props["background_color"] is not None:
                sv.setBackgroundColor(parse_color_int(props["background_color"]))
            return sv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            if "background_color" in changed and changed["background_color"] is not None:
                native_view.setBackgroundColor(parse_color_int(changed["background_color"]))

        def add_child(self, parent: Any, child: Any) -> None:
            parent.addView(child)

        def remove_child(self, parent: Any, child: Any) -> None:
            parent.removeView(child)

    # ---- TextInput (EditText) -------------------------------------------
    class AndroidTextInputHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            et = jclass("android.widget.EditText")(_ctx())
            self._apply(et, props)
            return et

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, et: Any, props: Dict[str, Any]) -> None:
            if "value" in props:
                et.setText(str(props["value"]))
            if "placeholder" in props:
                et.setHint(str(props["placeholder"]))
            if "font_size" in props and props["font_size"] is not None:
                et.setTextSize(float(props["font_size"]))
            if "color" in props and props["color"] is not None:
                et.setTextColor(parse_color_int(props["color"]))
            if "background_color" in props and props["background_color"] is not None:
                et.setBackgroundColor(parse_color_int(props["background_color"]))
            if "secure" in props and props["secure"]:
                InputType = jclass("android.text.InputType")
                et.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD)

    # ---- Image ----------------------------------------------------------
    class AndroidImageHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            iv = jclass("android.widget.ImageView")(_ctx())
            self._apply(iv, props)
            return iv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, iv: Any, props: Dict[str, Any]) -> None:
            if "background_color" in props and props["background_color"] is not None:
                iv.setBackgroundColor(parse_color_int(props["background_color"]))

    # ---- Switch ---------------------------------------------------------
    class AndroidSwitchHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sw = jclass("android.widget.Switch")(_ctx())
            self._apply(sw, props)
            return sw

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, sw: Any, props: Dict[str, Any]) -> None:
            if "value" in props:
                sw.setChecked(bool(props["value"]))
            if "on_change" in props and props["on_change"] is not None:
                cb = props["on_change"]

                class CheckedProxy(dynamic_proxy(jclass("android.widget.CompoundButton").OnCheckedChangeListener)):
                    def __init__(self, callback: Callable[[bool], None]) -> None:
                        super().__init__()
                        self.callback = callback

                    def onCheckedChanged(self, button: Any, checked: bool) -> None:
                        self.callback(checked)

                sw.setOnCheckedChangeListener(CheckedProxy(cb))

    # ---- ProgressBar ----------------------------------------------------
    class AndroidProgressBarHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            style = jclass("android.R$attr").progressBarStyleHorizontal
            pb = jclass("android.widget.ProgressBar")(_ctx(), None, 0, style)
            pb.setMax(1000)
            self._apply(pb, props)
            return pb

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, pb: Any, props: Dict[str, Any]) -> None:
            if "value" in props:
                pb.setProgress(int(float(props["value"]) * 1000))

    # ---- ActivityIndicator (circular ProgressBar) -----------------------
    class AndroidActivityIndicatorHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            pb = jclass("android.widget.ProgressBar")(_ctx())
            if not props.get("animating", True):
                pb.setVisibility(jclass("android.view.View").GONE)
            return pb

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            View = jclass("android.view.View")
            if "animating" in changed:
                native_view.setVisibility(View.VISIBLE if changed["animating"] else View.GONE)

    # ---- WebView --------------------------------------------------------
    class AndroidWebViewHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            wv = jclass("android.webkit.WebView")(_ctx())
            if "url" in props and props["url"]:
                wv.loadUrl(str(props["url"]))
            return wv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            if "url" in changed and changed["url"]:
                native_view.loadUrl(str(changed["url"]))

    # ---- Spacer ---------------------------------------------------------
    class AndroidSpacerHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            v = jclass("android.view.View")(_ctx())
            if "size" in props and props["size"] is not None:
                px = _dp(float(props["size"]))
                lp = jclass("android.widget.LinearLayout$LayoutParams")(px, px)
                v.setLayoutParams(lp)
            return v

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            if "size" in changed and changed["size"] is not None:
                px = _dp(float(changed["size"]))
                lp = jclass("android.widget.LinearLayout$LayoutParams")(px, px)
                native_view.setLayoutParams(lp)

    registry.register("Text", AndroidTextHandler())
    registry.register("Button", AndroidButtonHandler())
    registry.register("Column", AndroidColumnHandler())
    registry.register("Row", AndroidRowHandler())
    registry.register("ScrollView", AndroidScrollViewHandler())
    registry.register("TextInput", AndroidTextInputHandler())
    registry.register("Image", AndroidImageHandler())
    registry.register("Switch", AndroidSwitchHandler())
    registry.register("ProgressBar", AndroidProgressBarHandler())
    registry.register("ActivityIndicator", AndroidActivityIndicatorHandler())
    registry.register("WebView", AndroidWebViewHandler())
    registry.register("Spacer", AndroidSpacerHandler())


def _register_ios_handlers(registry: NativeViewRegistry) -> None:  # noqa: C901
    from rubicon.objc import SEL, ObjCClass, objc_method

    NSObject = ObjCClass("NSObject")
    UIColor = ObjCClass("UIColor")
    UIFont = ObjCClass("UIFont")

    def _uicolor(color: Any) -> Any:
        argb = parse_color_int(color)
        if argb < 0:
            argb += 0x100000000
        a = ((argb >> 24) & 0xFF) / 255.0
        r = ((argb >> 16) & 0xFF) / 255.0
        g = ((argb >> 8) & 0xFF) / 255.0
        b = (argb & 0xFF) / 255.0
        return UIColor.colorWithRed_green_blue_alpha_(r, g, b, a)

    # ---- Text -----------------------------------------------------------
    class IOSTextHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            label = ObjCClass("UILabel").alloc().init()
            self._apply(label, props)
            return label

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

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

    # ---- Button ---------------------------------------------------------

    # btn id(ObjCInstance) -> _PNButtonTarget.  Keeps a strong ref to
    # each handler (preventing GC) and lets us swap the callback on
    # re-render without calling removeTarget/addTarget (which crashes
    # due to rubicon-objc wrapper lifecycle issues).
    _pn_btn_handler_map: dict = {}

    class _PNButtonTarget(NSObject):  # type: ignore[valid-type]
        _callback: Optional[Callable[[], None]] = None

        @objc_method
        def onTap_(self, sender: object) -> None:
            if self._callback is not None:
                self._callback()

    # Strong refs to retained UIButton wrappers so the ObjCInstance
    # (and its prevent-deallocation retain) stays alive for the
    # lifetime of the app.
    _pn_retained_views: list = []

    class IOSButtonHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            btn = ObjCClass("UIButton").alloc().init()
            btn.retain()
            _pn_retained_views.append(btn)
            _ios_blue = UIColor.colorWithRed_green_blue_alpha_(0.0, 0.478, 1.0, 1.0)
            btn.setTitleColor_forState_(_ios_blue, 0)
            self._apply(btn, props)
            return btn

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

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

    # ---- Column (vertical UIStackView) ----------------------------------
    class IOSColumnHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sv = ObjCClass("UIStackView").alloc().initWithFrame_(((0, 0), (0, 0)))
            sv.setAxis_(1)  # vertical
            self._apply(sv, props)
            return sv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, sv: Any, props: Dict[str, Any]) -> None:
            if "spacing" in props and props["spacing"]:
                sv.setSpacing_(float(props["spacing"]))
            if "alignment" in props and props["alignment"]:
                mapping = {"fill": 0, "leading": 1, "top": 1, "center": 3, "trailing": 4, "bottom": 4}
                sv.setAlignment_(mapping.get(props["alignment"], 0))
            if "background_color" in props and props["background_color"] is not None:
                sv.setBackgroundColor_(_uicolor(props["background_color"]))
            if "padding" in props:
                left, top, right, bottom = _resolve_padding(props["padding"])
                sv.setLayoutMarginsRelativeArrangement_(True)
                try:
                    sv.setDirectionalLayoutMargins_((top, left, bottom, right))
                except Exception:
                    sv.setLayoutMargins_((top, left, bottom, right))

        def add_child(self, parent: Any, child: Any) -> None:
            parent.addArrangedSubview_(child)

        def remove_child(self, parent: Any, child: Any) -> None:
            parent.removeArrangedSubview_(child)
            child.removeFromSuperview()

        def insert_child(self, parent: Any, child: Any, index: int) -> None:
            parent.insertArrangedSubview_atIndex_(child, index)

    # ---- Row (horizontal UIStackView) -----------------------------------
    class IOSRowHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sv = ObjCClass("UIStackView").alloc().initWithFrame_(((0, 0), (0, 0)))
            sv.setAxis_(0)  # horizontal
            self._apply(sv, props)
            return sv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, sv: Any, props: Dict[str, Any]) -> None:
            if "spacing" in props and props["spacing"]:
                sv.setSpacing_(float(props["spacing"]))
            if "alignment" in props and props["alignment"]:
                mapping = {"fill": 0, "leading": 1, "top": 1, "center": 3, "trailing": 4, "bottom": 4}
                sv.setAlignment_(mapping.get(props["alignment"], 0))
            if "background_color" in props and props["background_color"] is not None:
                sv.setBackgroundColor_(_uicolor(props["background_color"]))

        def add_child(self, parent: Any, child: Any) -> None:
            parent.addArrangedSubview_(child)

        def remove_child(self, parent: Any, child: Any) -> None:
            parent.removeArrangedSubview_(child)
            child.removeFromSuperview()

        def insert_child(self, parent: Any, child: Any, index: int) -> None:
            parent.insertArrangedSubview_atIndex_(child, index)

    # ---- ScrollView -----------------------------------------------------
    class IOSScrollViewHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sv = ObjCClass("UIScrollView").alloc().init()
            if "background_color" in props and props["background_color"] is not None:
                sv.setBackgroundColor_(_uicolor(props["background_color"]))
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

    # ---- TextInput (UITextField) ----------------------------------------
    class IOSTextInputHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            tf = ObjCClass("UITextField").alloc().init()
            tf.setBorderStyle_(2)  # RoundedRect
            self._apply(tf, props)
            return tf

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

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

    # ---- Image ----------------------------------------------------------
    class IOSImageHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            iv = ObjCClass("UIImageView").alloc().init()
            if "background_color" in props and props["background_color"] is not None:
                iv.setBackgroundColor_(_uicolor(props["background_color"]))
            return iv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            if "background_color" in changed and changed["background_color"] is not None:
                native_view.setBackgroundColor_(_uicolor(changed["background_color"]))

    # ---- Switch ---------------------------------------------------------
    class IOSSwitchHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            sw = ObjCClass("UISwitch").alloc().init()
            self._apply(sw, props)
            return sw

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            self._apply(native_view, changed)

        def _apply(self, sw: Any, props: Dict[str, Any]) -> None:
            if "value" in props:
                sw.setOn_animated_(bool(props["value"]), False)

    # ---- ProgressBar (UIProgressView) -----------------------------------
    class IOSProgressBarHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            pv = ObjCClass("UIProgressView").alloc().init()
            if "value" in props:
                pv.setProgress_(float(props["value"]))
            return pv

        def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
            if "value" in changed:
                native_view.setProgress_(float(changed["value"]))

    # ---- ActivityIndicator ----------------------------------------------
    class IOSActivityIndicatorHandler(ViewHandler):
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

    # ---- WebView (WKWebView) --------------------------------------------
    class IOSWebViewHandler(ViewHandler):
        def create(self, props: Dict[str, Any]) -> Any:
            wv = ObjCClass("WKWebView").alloc().init()
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

    # ---- Spacer ---------------------------------------------------------
    class IOSSpacerHandler(ViewHandler):
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

    registry.register("Text", IOSTextHandler())
    registry.register("Button", IOSButtonHandler())
    registry.register("Column", IOSColumnHandler())
    registry.register("Row", IOSRowHandler())
    registry.register("ScrollView", IOSScrollViewHandler())
    registry.register("TextInput", IOSTextInputHandler())
    registry.register("Image", IOSImageHandler())
    registry.register("Switch", IOSSwitchHandler())
    registry.register("ProgressBar", IOSProgressBarHandler())
    registry.register("ActivityIndicator", IOSActivityIndicatorHandler())
    registry.register("WebView", IOSWebViewHandler())
    registry.register("Spacer", IOSSpacerHandler())


# ======================================================================
# Factory
# ======================================================================

_registry: Optional[NativeViewRegistry] = None


def get_registry() -> NativeViewRegistry:
    """Return the singleton registry, lazily creating platform handlers."""
    global _registry
    if _registry is not None:
        return _registry
    _registry = NativeViewRegistry()
    if IS_ANDROID:
        _register_android_handlers(_registry)
    else:
        _register_ios_handlers(_registry)
    return _registry


def set_registry(registry: NativeViewRegistry) -> None:
    """Inject a custom or mock registry (primarily for testing)."""
    global _registry
    _registry = registry
