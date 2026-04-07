"""Android native view handlers (Chaquopy / Java bridge).

Each handler class maps a PythonNative element type to an Android widget,
implementing view creation, property updates, and child management.

This module is only imported on Android at runtime; desktop tests inject
a mock registry via :func:`~.set_registry` and never trigger this import.
"""

from typing import Any, Callable, Dict

from java import dynamic_proxy, jclass

from ..utils import get_android_context
from .base import CONTAINER_KEYS, LAYOUT_KEYS, ViewHandler, is_vertical, parse_color_int, resolve_padding

# ======================================================================
# Shared helpers
# ======================================================================


def _ctx() -> Any:
    return get_android_context()


def _density() -> float:
    return float(_ctx().getResources().getDisplayMetrics().density)


def _dp(value: float) -> int:
    return int(value * _density())


def _apply_layout(view: Any, props: Dict[str, Any]) -> None:
    """Apply common layout properties (child-level flex props) to an Android view."""
    lp = view.getLayoutParams()
    LayoutParams = jclass("android.widget.LinearLayout$LayoutParams")
    ViewGroupLP = jclass("android.view.ViewGroup$LayoutParams")
    Gravity = jclass("android.view.Gravity")
    needs_set = False

    if lp is None:
        lp = LayoutParams(ViewGroupLP.WRAP_CONTENT, ViewGroupLP.WRAP_CONTENT)
        needs_set = True

    if "width" in props and props["width"] is not None:
        lp.width = _dp(float(props["width"]))
        needs_set = True
    if "height" in props and props["height"] is not None:
        lp.height = _dp(float(props["height"]))
        needs_set = True

    flex = props.get("flex")
    flex_grow = props.get("flex_grow")
    weight = None
    if flex is not None:
        weight = float(flex)
    elif flex_grow is not None:
        weight = float(flex_grow)
    if weight is not None:
        try:
            lp.weight = weight
            needs_set = True
        except Exception:
            pass

    if "margin" in props and props["margin"] is not None:
        left, top, right, bottom = resolve_padding(props["margin"])
        try:
            lp.setMargins(_dp(left), _dp(top), _dp(right), _dp(bottom))
            needs_set = True
        except Exception:
            pass

    if "align_self" in props and props["align_self"] is not None:
        align_map = {
            "flex_start": Gravity.START | Gravity.TOP,
            "leading": Gravity.START | Gravity.TOP,
            "center": Gravity.CENTER,
            "flex_end": Gravity.END | Gravity.BOTTOM,
            "trailing": Gravity.END | Gravity.BOTTOM,
            "stretch": Gravity.FILL,
        }
        g = align_map.get(props["align_self"])
        if g is not None:
            lp.gravity = g
            needs_set = True

    if needs_set:
        view.setLayoutParams(lp)

    if "min_width" in props and props["min_width"] is not None:
        view.setMinimumWidth(_dp(float(props["min_width"])))
    if "min_height" in props and props["min_height"] is not None:
        view.setMinimumHeight(_dp(float(props["min_height"])))


def _apply_common_visual(view: Any, props: Dict[str, Any]) -> None:
    """Apply visual properties shared across many handlers."""
    if "background_color" in props and props["background_color"] is not None:
        view.setBackgroundColor(parse_color_int(props["background_color"]))
    if "overflow" in props:
        clip = props["overflow"] == "hidden"
        try:
            view.setClipChildren(clip)
            view.setClipToPadding(clip)
        except Exception:
            pass


def _apply_flex_container(container: Any, props: Dict[str, Any]) -> None:
    """Apply flex container properties to a LinearLayout.

    Handles spacing, padding, alignment, justification, background, and overflow.
    """
    LinearLayout = jclass("android.widget.LinearLayout")
    Gravity = jclass("android.view.Gravity")

    if "flex_direction" in props:
        vertical = is_vertical(props["flex_direction"])
        container.setOrientation(LinearLayout.VERTICAL if vertical else LinearLayout.HORIZONTAL)

    direction = props.get("flex_direction", "column")
    vertical = is_vertical(direction)

    if "spacing" in props and props["spacing"]:
        px = _dp(float(props["spacing"]))
        GradientDrawable = jclass("android.graphics.drawable.GradientDrawable")
        d = GradientDrawable()
        d.setColor(0x00000000)
        d.setSize(1 if vertical else px, px if vertical else 1)
        container.setShowDividers(LinearLayout.SHOW_DIVIDER_MIDDLE)
        container.setDividerDrawable(d)

    if "padding" in props:
        left, top, right, bottom = resolve_padding(props["padding"])
        container.setPadding(_dp(left), _dp(top), _dp(right), _dp(bottom))

    gravity = 0
    ai = props.get("align_items") or props.get("alignment")
    if ai:
        if vertical:
            cross_map = {
                "stretch": Gravity.FILL_HORIZONTAL,
                "fill": Gravity.FILL_HORIZONTAL,
                "flex_start": Gravity.START,
                "leading": Gravity.START,
                "start": Gravity.START,
                "center": Gravity.CENTER_HORIZONTAL,
                "flex_end": Gravity.END,
                "trailing": Gravity.END,
                "end": Gravity.END,
            }
        else:
            cross_map = {
                "stretch": Gravity.FILL_VERTICAL,
                "fill": Gravity.FILL_VERTICAL,
                "flex_start": Gravity.TOP,
                "top": Gravity.TOP,
                "center": Gravity.CENTER_VERTICAL,
                "flex_end": Gravity.BOTTOM,
                "bottom": Gravity.BOTTOM,
            }
        gravity |= cross_map.get(ai, 0)

    jc = props.get("justify_content")
    if jc:
        if vertical:
            main_map = {
                "flex_start": Gravity.TOP,
                "center": Gravity.CENTER_VERTICAL,
                "flex_end": Gravity.BOTTOM,
            }
        else:
            main_map = {
                "flex_start": Gravity.START,
                "center": Gravity.CENTER_HORIZONTAL,
                "flex_end": Gravity.END,
            }
        gravity |= main_map.get(jc, 0)

    if gravity:
        container.setGravity(gravity)

    _apply_common_visual(container, props)


# ======================================================================
# Flex container handler (shared by Column, Row, View)
# ======================================================================


class FlexContainerHandler(ViewHandler):
    """Unified handler for flex layout containers (Column, Row, View).

    All three element types use ``LinearLayout`` with orientation
    determined by the ``flex_direction`` prop.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        ll = jclass("android.widget.LinearLayout")(_ctx())
        direction = props.get("flex_direction", "column")
        LinearLayout = jclass("android.widget.LinearLayout")
        ll.setOrientation(LinearLayout.VERTICAL if is_vertical(direction) else LinearLayout.HORIZONTAL)
        _apply_flex_container(ll, props)
        _apply_layout(ll, props)
        return ll

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if changed.keys() & CONTAINER_KEYS:
            _apply_flex_container(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        parent.addView(child, index)


# ======================================================================
# Leaf handlers
# ======================================================================


class TextHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        tv = jclass("android.widget.TextView")(_ctx())
        self._apply(tv, props)
        _apply_layout(tv, props)
        return tv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

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


class ButtonHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        btn = jclass("android.widget.Button")(_ctx())
        self._apply(btn, props)
        _apply_layout(btn, props)
        return btn

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

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


class ScrollViewHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sv = jclass("android.widget.ScrollView")(_ctx())
        if "background_color" in props and props["background_color"] is not None:
            sv.setBackgroundColor(parse_color_int(props["background_color"]))
        _apply_layout(sv, props)
        return sv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor(parse_color_int(changed["background_color"]))
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)


class TextInputHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        et = jclass("android.widget.EditText")(_ctx())
        self._apply(et, props)
        _apply_layout(et, props)
        return et

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

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
        if "on_change" in props:
            cb = props["on_change"]
            if cb is not None:
                TextWatcher = jclass("android.text.TextWatcher")

                class ChangeProxy(dynamic_proxy(TextWatcher)):
                    def __init__(self, callback: Callable[[str], None]) -> None:
                        super().__init__()
                        self.callback = callback

                    def afterTextChanged(self, s: Any) -> None:
                        self.callback(str(s))

                    def beforeTextChanged(self, s: Any, start: int, count: int, after: int) -> None:
                        pass

                    def onTextChanged(self, s: Any, start: int, before: int, count: int) -> None:
                        pass

                et.addTextChangedListener(ChangeProxy(cb))


class ImageHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        iv = jclass("android.widget.ImageView")(_ctx())
        self._apply(iv, props)
        _apply_layout(iv, props)
        return iv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)
        if changed.keys() & LAYOUT_KEYS:
            _apply_layout(native_view, changed)

    def _apply(self, iv: Any, props: Dict[str, Any]) -> None:
        if "background_color" in props and props["background_color"] is not None:
            iv.setBackgroundColor(parse_color_int(props["background_color"]))
        if "source" in props and props["source"]:
            self._load_source(iv, props["source"])
        if "scale_type" in props and props["scale_type"]:
            ScaleType = jclass("android.widget.ImageView$ScaleType")
            mapping = {
                "cover": ScaleType.CENTER_CROP,
                "contain": ScaleType.FIT_CENTER,
                "stretch": ScaleType.FIT_XY,
                "center": ScaleType.CENTER,
            }
            st = mapping.get(props["scale_type"])
            if st:
                iv.setScaleType(st)

    def _load_source(self, iv: Any, source: str) -> None:
        try:
            if source.startswith(("http://", "https://")):
                Thread = jclass("java.lang.Thread")
                Runnable = jclass("java.lang.Runnable")
                URL = jclass("java.net.URL")
                BitmapFactory = jclass("android.graphics.BitmapFactory")
                Handler = jclass("android.os.Handler")
                Looper = jclass("android.os.Looper")
                handler = Handler(Looper.getMainLooper())

                class LoadTask(dynamic_proxy(Runnable)):
                    def __init__(self, image_view: Any, url_str: str, main_handler: Any) -> None:
                        super().__init__()
                        self.image_view = image_view
                        self.url_str = url_str
                        self.main_handler = main_handler

                    def run(self) -> None:
                        try:
                            url = URL(self.url_str)
                            stream = url.openStream()
                            bitmap = BitmapFactory.decodeStream(stream)
                            stream.close()

                            class SetImage(dynamic_proxy(Runnable)):
                                def __init__(self, view: Any, bmp: Any) -> None:
                                    super().__init__()
                                    self.view = view
                                    self.bmp = bmp

                                def run(self) -> None:
                                    self.view.setImageBitmap(self.bmp)

                            self.main_handler.post(SetImage(self.image_view, bitmap))
                        except Exception:
                            pass

                Thread(LoadTask(iv, source, handler)).start()
            else:
                ctx = _ctx()
                res = ctx.getResources()
                pkg = ctx.getPackageName()
                res_name = source.rsplit(".", 1)[0] if "." in source else source
                res_id = res.getIdentifier(res_name, "drawable", pkg)
                if res_id != 0:
                    iv.setImageResource(res_id)
        except Exception:
            pass


class SwitchHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sw = jclass("android.widget.Switch")(_ctx())
        self._apply(sw, props)
        _apply_layout(sw, props)
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


class ProgressBarHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        style = jclass("android.R$attr").progressBarStyleHorizontal
        pb = jclass("android.widget.ProgressBar")(_ctx(), None, 0, style)
        pb.setMax(1000)
        self._apply(pb, props)
        _apply_layout(pb, props)
        return pb

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, pb: Any, props: Dict[str, Any]) -> None:
        if "value" in props:
            pb.setProgress(int(float(props["value"]) * 1000))


class ActivityIndicatorHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        pb = jclass("android.widget.ProgressBar")(_ctx())
        if not props.get("animating", True):
            pb.setVisibility(jclass("android.view.View").GONE)
        _apply_layout(pb, props)
        return pb

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        View = jclass("android.view.View")
        if "animating" in changed:
            native_view.setVisibility(View.VISIBLE if changed["animating"] else View.GONE)


class WebViewHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        wv = jclass("android.webkit.WebView")(_ctx())
        if "url" in props and props["url"]:
            wv.loadUrl(str(props["url"]))
        _apply_layout(wv, props)
        return wv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "url" in changed and changed["url"]:
            native_view.loadUrl(str(changed["url"]))


class SpacerHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        v = jclass("android.view.View")(_ctx())
        if "size" in props and props["size"] is not None:
            px = _dp(float(props["size"]))
            lp = jclass("android.widget.LinearLayout$LayoutParams")(px, px)
            v.setLayoutParams(lp)
        if "flex" in props and props["flex"] is not None:
            lp = v.getLayoutParams()
            if lp is None:
                lp = jclass("android.widget.LinearLayout$LayoutParams")(0, 0)
            lp.weight = float(props["flex"])
            v.setLayoutParams(lp)
        return v

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "size" in changed and changed["size"] is not None:
            px = _dp(float(changed["size"]))
            lp = jclass("android.widget.LinearLayout$LayoutParams")(px, px)
            native_view.setLayoutParams(lp)


class SafeAreaViewHandler(ViewHandler):
    """Safe-area container using FrameLayout with ``fitsSystemWindows``."""

    def create(self, props: Dict[str, Any]) -> Any:
        fl = jclass("android.widget.FrameLayout")(_ctx())
        fl.setFitsSystemWindows(True)
        if "background_color" in props and props["background_color"] is not None:
            fl.setBackgroundColor(parse_color_int(props["background_color"]))
        if "padding" in props:
            left, top, right, bottom = resolve_padding(props["padding"])
            fl.setPadding(_dp(left), _dp(top), _dp(right), _dp(bottom))
        return fl

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor(parse_color_int(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)


class ModalHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        placeholder = jclass("android.view.View")(_ctx())
        placeholder.setVisibility(jclass("android.view.View").GONE)
        return placeholder

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass

    def add_child(self, parent: Any, child: Any) -> None:
        pass


class SliderHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sb = jclass("android.widget.SeekBar")(_ctx())
        sb.setMax(1000)
        self._apply(sb, props)
        _apply_layout(sb, props)
        return sb

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, sb: Any, props: Dict[str, Any]) -> None:
        min_val = float(props.get("min_value", 0))
        max_val = float(props.get("max_value", 1))
        rng = max_val - min_val if max_val != min_val else 1
        if "value" in props:
            normalized = (float(props["value"]) - min_val) / rng
            sb.setProgress(int(normalized * 1000))
        if "on_change" in props and props["on_change"] is not None:
            cb = props["on_change"]

            class SeekProxy(dynamic_proxy(jclass("android.widget.SeekBar").OnSeekBarChangeListener)):
                def __init__(self, callback: Callable[[float], None], mn: float, rn: float) -> None:
                    super().__init__()
                    self.callback = callback
                    self.mn = mn
                    self.rn = rn

                def onProgressChanged(self, seekBar: Any, progress: int, fromUser: bool) -> None:
                    if fromUser:
                        self.callback(self.mn + (progress / 1000.0) * self.rn)

                def onStartTrackingTouch(self, seekBar: Any) -> None:
                    pass

                def onStopTrackingTouch(self, seekBar: Any) -> None:
                    pass

            sb.setOnSeekBarChangeListener(SeekProxy(cb, min_val, rng))


class PressableHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        fl = jclass("android.widget.FrameLayout")(_ctx())
        fl.setClickable(True)
        self._apply(fl, props)
        return fl

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, fl: Any, props: Dict[str, Any]) -> None:
        if "on_press" in props and props["on_press"] is not None:
            cb = props["on_press"]

            class PressProxy(dynamic_proxy(jclass("android.view.View").OnClickListener)):
                def __init__(self, callback: Callable[[], None]) -> None:
                    super().__init__()
                    self.callback = callback

                def onClick(self, view: Any) -> None:
                    self.callback()

            fl.setOnClickListener(PressProxy(cb))
        if "on_long_press" in props and props["on_long_press"] is not None:
            cb = props["on_long_press"]

            class LongPressProxy(dynamic_proxy(jclass("android.view.View").OnLongClickListener)):
                def __init__(self, callback: Callable[[], None]) -> None:
                    super().__init__()
                    self.callback = callback

                def onLongClick(self, view: Any) -> bool:
                    self.callback()
                    return True

            fl.setOnLongClickListener(LongPressProxy(cb))

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)


# ======================================================================
# Registration
# ======================================================================


def register_handlers(registry: Any) -> None:
    """Register all Android view handlers with the given registry."""
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
    registry.register("Pressable", PressableHandler())
