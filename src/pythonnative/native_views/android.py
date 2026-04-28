"""Android native-view handlers (Chaquopy / Java bridge).

Each handler class maps a PythonNative element type to an Android
widget, implementing view creation, property updates, child management,
and frame application. Handlers are registered with the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry] by
[`register_handlers`][pythonnative.native_views.android.register_handlers].

Layout is owned by the pure-Python flex engine in
[`pythonnative.layout`][pythonnative.layout]: container handlers create
plain `FrameLayout`s, the engine computes per-child frames, and
[`set_frame`][pythonnative.native_views.android.AndroidViewHandler.set_frame]
applies those frames via per-child `MarginLayoutParams`. Handlers
therefore only deal with *visual* props — text, colors, callbacks — and
ignore everything in
[`pythonnative.layout.LAYOUT_STYLE_KEYS`][pythonnative.layout.LAYOUT_STYLE_KEYS].

This module is only imported on Android at runtime. Desktop tests
inject a mock registry via
[`set_registry`][pythonnative.native_views.set_registry] and never
trigger this import path.
"""

import math
from typing import Any, Callable, Dict, Tuple

from java import dynamic_proxy, jclass

from ..utils import get_android_context
from .base import ViewHandler, _safe_max, parse_color_int

# ======================================================================
# Shared helpers
# ======================================================================


def _ctx() -> Any:
    return get_android_context()


def _density() -> float:
    return float(_ctx().getResources().getDisplayMetrics().density)


def _dp(value: float) -> int:
    return int(round(value * _density()))


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


# ======================================================================
# Base class with shared frame/measure implementations
# ======================================================================


class AndroidViewHandler(ViewHandler):
    """Base class providing the shared `set_frame` / measure contract.

    All Android handlers go through `set_frame` to apply the layout
    engine's computed frames as `MarginLayoutParams` mutations.
    Container handlers inherit the default `add_child` /
    `remove_child` implementations; leaves leave them as no-ops.
    """

    def set_frame(self, native_view: Any, x: float, y: float, width: float, height: float) -> None:
        if native_view is None:
            return
        try:
            px_x = _dp(x)
            px_y = _dp(y)
            px_w = max(0, _dp(width))
            px_h = max(0, _dp(height))
            lp = native_view.getLayoutParams()
            if lp is None:
                FrameLP = jclass("android.widget.FrameLayout$LayoutParams")
                lp = FrameLP(px_w, px_h)
            else:
                try:
                    lp.width = px_w
                    lp.height = px_h
                except Exception:
                    pass
            try:
                lp.leftMargin = px_x
                lp.topMargin = px_y
                lp.rightMargin = 0
                lp.bottomMargin = 0
            except Exception:
                pass
            native_view.setLayoutParams(lp)
        except Exception:
            pass

    def measure_intrinsic(
        self,
        native_view: Any,
        max_width: float,
        max_height: float,
    ) -> Tuple[float, float]:
        try:
            density = _density()
            View = jclass("android.view.View")
            MeasureSpec = View.MeasureSpec
            w_spec = (
                MeasureSpec.makeMeasureSpec(int(_safe_max(max_width) * density), MeasureSpec.AT_MOST)
                if math.isfinite(max_width)
                else MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)
            )
            h_spec = (
                MeasureSpec.makeMeasureSpec(int(_safe_max(max_height) * density), MeasureSpec.AT_MOST)
                if math.isfinite(max_height)
                else MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)
            )
            native_view.measure(w_spec, h_spec)
            return (
                native_view.getMeasuredWidth() / density,
                native_view.getMeasuredHeight() / density,
            )
        except Exception:
            return (0.0, 0.0)


# ======================================================================
# Flex container handler (shared by Column, Row, View)
# ======================================================================


class FlexContainerHandler(AndroidViewHandler):
    """Container for flex layout — a bare `FrameLayout`.

    All flex semantics (direction, alignment, distribution, padding)
    are computed by the layout engine and applied via
    [`set_frame`][pythonnative.native_views.android.AndroidViewHandler.set_frame].
    The container itself is just a positioning surface.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        fl = jclass("android.widget.FrameLayout")(_ctx())
        _apply_common_visual(fl, props)
        return fl

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        _apply_common_visual(native_view, changed)

    def add_child(self, parent: Any, child: Any) -> None:
        FrameLP = jclass("android.widget.FrameLayout$LayoutParams")
        lp = child.getLayoutParams()
        if lp is None:
            lp = FrameLP(0, 0)
            child.setLayoutParams(lp)
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        FrameLP = jclass("android.widget.FrameLayout$LayoutParams")
        lp = child.getLayoutParams()
        if lp is None:
            lp = FrameLP(0, 0)
            child.setLayoutParams(lp)
        parent.addView(child, index)


# ======================================================================
# Leaf handlers
# ======================================================================


class TextHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        tv = jclass("android.widget.TextView")(_ctx())
        self._apply(tv, props)
        return tv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, tv: Any, props: Dict[str, Any]) -> None:
        if "text" in props:
            tv.setText(str(props["text"]) if props["text"] is not None else "")
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


class ButtonHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        btn = jclass("android.widget.Button")(_ctx())
        self._apply(btn, props)
        return btn

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, btn: Any, props: Dict[str, Any]) -> None:
        if "title" in props:
            btn.setText(str(props["title"]) if props["title"] is not None else "")
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


class ScrollViewHandler(AndroidViewHandler):
    """Scroll container — wraps a single child whose height is unbounded.

    Only the *outer* `ScrollView` is positioned by the layout engine;
    its child receives an unbounded main-axis available height during
    layout (see
    [`pythonnative.reconciler.Reconciler._build_layout_tree`][pythonnative.reconciler.Reconciler._build_layout_tree])
    so the child can be taller than the visible viewport.
    """

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


class TextInputHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        et = jclass("android.widget.EditText")(_ctx())
        self._apply(et, props)
        return et

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

    def _apply(self, et: Any, props: Dict[str, Any]) -> None:
        if "value" in props:
            et.setText(str(props["value"]) if props["value"] is not None else "")
        if "placeholder" in props:
            et.setHint(str(props["placeholder"]) if props["placeholder"] is not None else "")
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


class ImageHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        iv = jclass("android.widget.ImageView")(_ctx())
        self._apply(iv, props)
        return iv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        self._apply(native_view, changed)

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


class SwitchHandler(AndroidViewHandler):
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


class ProgressBarHandler(AndroidViewHandler):
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


class ActivityIndicatorHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        pb = jclass("android.widget.ProgressBar")(_ctx())
        if not props.get("animating", True):
            pb.setVisibility(jclass("android.view.View").GONE)
        return pb

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        View = jclass("android.view.View")
        if "animating" in changed:
            native_view.setVisibility(View.VISIBLE if changed["animating"] else View.GONE)


class WebViewHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        wv = jclass("android.webkit.WebView")(_ctx())
        if "url" in props and props["url"]:
            wv.loadUrl(str(props["url"]))
        return wv

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "url" in changed and changed["url"]:
            native_view.loadUrl(str(changed["url"]))


class SpacerHandler(AndroidViewHandler):
    """Empty layout placeholder used as a flexible gap.

    All sizing semantics now live in the layout engine — ``Spacer``
    behaves identically to a `View` with the same style props (e.g.,
    ``flex: 1`` for an expanding spacer, ``size`` for a fixed gap).
    """

    def create(self, props: Dict[str, Any]) -> Any:
        return jclass("android.view.View")(_ctx())

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass


class SafeAreaViewHandler(AndroidViewHandler):
    """Safe-area container using FrameLayout with ``fitsSystemWindows``."""

    def create(self, props: Dict[str, Any]) -> Any:
        fl = jclass("android.widget.FrameLayout")(_ctx())
        fl.setFitsSystemWindows(True)
        if "background_color" in props and props["background_color"] is not None:
            fl.setBackgroundColor(parse_color_int(props["background_color"]))
        return fl

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if "background_color" in changed and changed["background_color"] is not None:
            native_view.setBackgroundColor(parse_color_int(changed["background_color"]))

    def add_child(self, parent: Any, child: Any) -> None:
        parent.addView(child)

    def remove_child(self, parent: Any, child: Any) -> None:
        parent.removeView(child)


class ModalHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        placeholder = jclass("android.view.View")(_ctx())
        placeholder.setVisibility(jclass("android.view.View").GONE)
        return placeholder

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        pass

    def add_child(self, parent: Any, child: Any) -> None:
        pass

    def set_frame(self, native_view: Any, x: float, y: float, width: float, height: float) -> None:
        # Modal is a virtual placeholder; never gets a positioned frame.
        return


class SliderHandler(AndroidViewHandler):
    def create(self, props: Dict[str, Any]) -> Any:
        sb = jclass("android.widget.SeekBar")(_ctx())
        sb.setMax(1000)
        self._apply(sb, props)
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


_android_tabbar_state: dict = {"callback": None, "items": []}


class TabBarHandler(AndroidViewHandler):
    """Native tab bar using ``BottomNavigationView`` from Material Components.

    Falls back to a horizontal ``LinearLayout`` with ``Button`` children
    when Material Components is unavailable.

    The intrinsic height is left to ``BottomNavigationView.measure(…)``
    (inherited from
    [`AndroidViewHandler`][pythonnative.native_views.android.AndroidViewHandler]).
    Material 3 chooses the right height per item configuration —
    56 dp for label-only, 80 dp for icon+label, etc. — and positions
    the active-indicator pill against that height. Hard-coding our
    own height was found to throw off the pill's geometry and to
    interact badly with the late ``WindowInsets`` callback (the bar
    grew on first tab tap), so we now defer entirely to the system.
    """

    _is_material: bool = True

    def create(self, props: Dict[str, Any]) -> Any:
        try:
            bnv = jclass("com.google.android.material.bottomnavigation.BottomNavigationView")(_ctx())
            bnv.setBackgroundColor(parse_color_int("#FFFFFF"))
            self._is_material = True
            self._apply_full(bnv, props)
            return bnv
        except Exception:
            self._is_material = False
            return self._create_fallback(props)

    def _create_fallback(self, props: Dict[str, Any]) -> Any:
        """Horizontal LinearLayout with Button children as a tab-bar fallback."""
        LinearLayout = jclass("android.widget.LinearLayout")
        ll = LinearLayout(_ctx())
        ll.setOrientation(LinearLayout.HORIZONTAL)
        ll.setBackgroundColor(parse_color_int("#F8F8F8"))
        self._apply_fallback(ll, props)
        return ll

    def update(self, native_view: Any, changed: Dict[str, Any]) -> None:
        if self._is_material:
            self._apply_partial(native_view, changed)
        else:
            self._apply_fallback(native_view, changed)

    def _apply_full(self, bnv: Any, props: Dict[str, Any]) -> None:
        """Initial creation — all props are present."""
        items = props.get("items", [])
        self._set_menu(bnv, items)
        self._set_active(bnv, props.get("active_tab"), items)
        cb = props.get("on_tab_select")
        if cb is not None:
            self._set_listener(bnv, cb, items)

    def _apply_partial(self, bnv: Any, changed: Dict[str, Any]) -> None:
        """Reconciler update — only changed props are present."""
        prev_items = _android_tabbar_state["items"]

        if "items" in changed:
            items = changed["items"]
            self._set_menu(bnv, items)
        else:
            items = prev_items

        if "active_tab" in changed:
            self._set_active(bnv, changed["active_tab"], items)

        if "on_tab_select" in changed:
            cb = changed["on_tab_select"]
            if cb is not None:
                self._set_listener(bnv, cb, items)

    def _set_menu(self, bnv: Any, items: list) -> None:
        _android_tabbar_state["items"] = items
        try:
            menu = bnv.getMenu()
            menu.clear()
            for i, item in enumerate(items):
                title = item.get("title", item.get("name", ""))
                menu.add(0, i, i, str(title))
        except Exception:
            pass

    def _set_active(self, bnv: Any, active: Any, items: list) -> None:
        if active and items:
            for i, item in enumerate(items):
                if item.get("name") == active:
                    try:
                        bnv.setSelectedItemId(i)
                    except Exception:
                        pass
                    break

    def _set_listener(self, bnv: Any, cb: Callable, items: list) -> None:
        _android_tabbar_state["callback"] = cb
        _android_tabbar_state["items"] = items
        try:
            listener_cls = jclass("com.google.android.material.navigation.NavigationBarView$OnItemSelectedListener")

            class _TabSelectProxy(dynamic_proxy(listener_cls)):
                def __init__(self, callback: Callable, tab_items: list) -> None:
                    super().__init__()
                    self.callback = callback
                    self.tab_items = tab_items

                def onNavigationItemSelected(self, menu_item: Any) -> bool:
                    idx = menu_item.getItemId()
                    if 0 <= idx < len(self.tab_items):
                        self.callback(self.tab_items[idx].get("name", ""))
                    return True

            bnv.setOnItemSelectedListener(_TabSelectProxy(cb, items))
        except Exception:
            pass

    def _apply_fallback(self, ll: Any, props: Dict[str, Any]) -> None:
        items = props.get("items", [])
        active = props.get("active_tab")
        cb = props.get("on_tab_select")
        if "items" in props:
            ll.removeAllViews()
            for item in items:
                name = item.get("name", "")
                title = item.get("title", name)
                btn = jclass("android.widget.Button")(_ctx())
                btn.setText(str(title))
                btn.setEnabled(name != active)
                if cb is not None:
                    tab_name = name

                    def _make_click(n: str) -> Callable[[], None]:
                        return lambda: cb(n)

                    class _ClickProxy(dynamic_proxy(jclass("android.view.View").OnClickListener)):
                        def __init__(self, callback: Callable[[], None]) -> None:
                            super().__init__()
                            self.callback = callback

                        def onClick(self, view: Any) -> None:
                            self.callback()

                    btn.setOnClickListener(_ClickProxy(_make_click(tab_name)))
                ll.addView(btn)


class PressableHandler(AndroidViewHandler):
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
    registry.register("TabBar", TabBarHandler())
    registry.register("Pressable", PressableHandler())


__all__ = [
    "AndroidViewHandler",
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
