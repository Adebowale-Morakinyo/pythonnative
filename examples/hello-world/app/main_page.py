from typing import Callable

import emoji

import pythonnative as pn
from pythonnative.navigation import NavigationContainer, create_tab_navigator

print("[hello-world] main_page module imported")

MEDALS = [":1st_place_medal:", ":2nd_place_medal:", ":3rd_place_medal:"]

Tab = create_tab_navigator()

styles = pn.StyleSheet.create(
    title={"font_size": 24, "bold": True},
    subtitle={"font_size": 16, "color": "#666666"},
    hint={"font_size": 14, "color": "#666666"},
    medal={"font_size": 32},
    card={
        "spacing": 12,
        "padding": 16,
        "background_color": "#F8F9FA",
        "align_items": "center",
    },
    section={"spacing": 16, "padding": 24, "align_items": "stretch"},
    button_row={"spacing": 8, "align_items": "center"},
    flex_demo={
        "flex_direction": "row",
        "spacing": 8,
        "padding": 16,
        "background_color": "#EDF2F7",
        "height": 80,
    },
    flex_box={"background_color": "#4299E1", "padding": 12},
    flex_box_alt={"background_color": "#48BB78", "padding": 12},
    flex_box_label={"color": "#FFFFFF", "bold": True, "text_align": "center"},
    abs_canvas={
        "background_color": "#1A202C",
        "height": 200,
        "padding": 0,
    },
    abs_pin={
        "position": "absolute",
        "background_color": "#F6AD55",
        "padding": 8,
    },
    abs_label={"color": "#1A202C", "bold": True},
)


@pn.component
def counter_badge(initial: int = 0) -> pn.Element:
    """Reusable counter component with its own hook-based state."""
    count, set_count = pn.use_state(initial)
    medal = emoji.emojize(MEDALS[count] if count < len(MEDALS) else ":star:")

    print(f"[counter_badge] render count={count}")

    def handle_tap() -> None:
        print(f"[counter_badge] Tap me clicked; {count} -> {count + 1}")
        set_count(count + 1)

    def handle_reset() -> None:
        print(f"[counter_badge] Reset clicked from count={count}")
        set_count(0)

    return pn.View(
        pn.Text(f"Tapped {count} times", style=styles["subtitle"]),
        pn.Text(medal, style=styles["medal"]),
        pn.Row(
            pn.Button("Tap me", on_click=handle_tap),
            pn.Button("Reset", on_click=handle_reset),
            style=styles["button_row"],
        ),
        style=styles["card"],
    )


@pn.component
def HomeTab() -> pn.Element:
    """Home tab — counter demo and push-navigation to other pages."""
    nav = pn.use_navigation()

    def _on_mount() -> Callable[[], None]:
        print("[HomeTab] mounted")
        return lambda: print("[HomeTab] unmounted")

    pn.use_effect(_on_mount, [])

    def go_to_second() -> None:
        print("[HomeTab] navigating to SecondPage")
        nav.navigate(
            "app.second_page.SecondPage",
            params={"message": "Greetings from MainPage"},
        )

    return pn.ScrollView(
        pn.Column(
            pn.Text("Hello from PythonNative Demo!", style=styles["title"]),
            pn.Text(
                "Try `pn run android --hot-reload`, edit this text, and save. "
                "The running app should update without a rebuild.",
                style=styles["hint"],
            ),
            counter_badge(),
            pn.Button("Go to Second Page", on_click=go_to_second),
            style=styles["section"],
        )
    )


@pn.component
def LayoutTab() -> pn.Element:
    """Demonstrates the pure-Python flex layout engine.

    Showcases features that only became possible after the layout
    rewrite: ``flex: 1`` distribution between siblings, fixed-aspect
    boxes, and ``position: "absolute"`` overlays anchored to all
    four edges.
    """
    return pn.ScrollView(
        pn.Column(
            pn.Text("Flex layout", style=styles["title"]),
            pn.Text(
                "Three siblings sharing a row; the middle one expands with `flex: 1`.",
                style=styles["hint"],
            ),
            pn.Row(
                pn.View(
                    pn.Text("80px", style=styles["flex_box_label"]),
                    style={**styles["flex_box"], "width": 80},
                ),
                pn.View(
                    pn.Text("flex: 1", style=styles["flex_box_label"]),
                    style={**styles["flex_box"], "flex": 1},
                ),
                pn.View(
                    pn.Text("60px", style=styles["flex_box_label"]),
                    style={**styles["flex_box_alt"], "width": 60},
                ),
                style=styles["flex_demo"],
            ),
            pn.Text("Aspect ratio", style=styles["title"]),
            pn.Text(
                "A square (1:1) and a 16:9 box, both sized purely by `aspect_ratio`.",
                style=styles["hint"],
            ),
            pn.Row(
                pn.View(
                    pn.Text("1:1", style=styles["flex_box_label"]),
                    style={**styles["flex_box"], "width": 80, "aspect_ratio": 1.0},
                ),
                pn.View(
                    pn.Text("16:9", style=styles["flex_box_label"]),
                    style={
                        **styles["flex_box_alt"],
                        "width": 144,
                        "aspect_ratio": 16 / 9,
                    },
                ),
                style={"flex_direction": "row", "spacing": 12, "padding": 16},
            ),
            pn.Text("Absolute positioning", style=styles["title"]),
            pn.Text(
                "The four pinned tags are positioned absolutely against this dark canvas.",
                style=styles["hint"],
            ),
            pn.View(
                pn.View(
                    pn.Text("top-left", style=styles["abs_label"]),
                    style={**styles["abs_pin"], "top": 8, "left": 8},
                ),
                pn.View(
                    pn.Text("top-right", style=styles["abs_label"]),
                    style={**styles["abs_pin"], "top": 8, "right": 8},
                ),
                pn.View(
                    pn.Text("bottom-left", style=styles["abs_label"]),
                    style={**styles["abs_pin"], "bottom": 8, "left": 8},
                ),
                pn.View(
                    pn.Text("bottom-right", style=styles["abs_label"]),
                    style={**styles["abs_pin"], "bottom": 8, "right": 8},
                ),
                pn.View(
                    pn.Text("centered", style=styles["abs_label"]),
                    style={
                        **styles["abs_pin"],
                        "background_color": "#FBD38D",
                        "left": "30%",
                        "right": "30%",
                        "top": "40%",
                    },
                ),
                style=styles["abs_canvas"],
            ),
            style=styles["section"],
        )
    )


@pn.component
def SettingsTab() -> pn.Element:
    """Settings tab — Platform info, alerts, and a virtualized FlatList."""
    nav = pn.use_navigation()
    dims = pn.use_window_dimensions()

    def _show_alert() -> None:
        pn.Alert.show(
            title="Hello!",
            message="This is a native alert dialog.",
            buttons=[
                {"label": "OK", "style": "default"},
            ],
        )

    def _confirm_destructive() -> None:
        pn.Alert.confirm(
            title="Delete item?",
            message="This action cannot be undone.",
            confirm_label="Delete",
            cancel_label="Keep",
            on_confirm=lambda: print("[SettingsTab] confirmed"),
            on_cancel=lambda: print("[SettingsTab] cancelled"),
        )

    def _go_to_showcase() -> None:
        nav.navigate("app.second_page.SecondPage", params={"message": "Visual showcase"})

    return pn.ScrollView(
        pn.Column(
            pn.StatusBar(style="dark"),
            pn.Text("Settings", style=styles["title"]),
            pn.Text(f"PythonNative v{pn.__version__}", style=styles["subtitle"]),
            pn.Text(
                f"Running on {pn.Platform.OS} {pn.Platform.Version}",
                style=styles["subtitle"],
            ),
            pn.Text(
                f"Window: {dims['width']:.0f} × {dims['height']:.0f}",
                style=styles["subtitle"],
            ),
            pn.Button("Show alert", on_click=_show_alert),
            pn.Button("Confirm destructive", on_click=_confirm_destructive),
            pn.Button("Visual showcase", on_click=_go_to_showcase),
            style=styles["section"],
        )
    )


@pn.component
def ListTab() -> pn.Element:
    """Demonstrates virtualized FlatList with native row recycling."""
    items = [{"id": i, "title": f"Row {i + 1}", "subtitle": f"Lorem ipsum #{i}"} for i in range(500)]

    def render_row(item: dict, index: int) -> pn.Element:
        return pn.View(
            pn.Text(item["title"], style={"font_size": 16, "font_weight": "600"}),
            pn.Text(item["subtitle"], style={"font_size": 13, "color": "#6B7280"}),
            style={
                "padding": 12,
                "spacing": 4,
                "background_color": "#FFFFFF",
                "border_radius": 8,
            },
        )

    return pn.Column(
        pn.View(
            pn.Text(
                "Virtualized FlatList — 500 rows backed by UITableView / RecyclerView",
                style={"font_size": 13, "color": "#6B7280"},
            ),
            style={"padding": 16, "background_color": "#F9FAFB"},
        ),
        pn.FlatList(
            data=items,
            item_height=64,
            separator_height=8,
            render_item=render_row,
            key_extractor=lambda item, _: str(item["id"]),
            on_item_press=lambda i: print(f"[ListTab] tapped row {i}"),
            style={"flex": 1, "background_color": "#F3F4F6"},
        ),
        style={"flex": 1},
    )


@pn.component
def MainPage() -> pn.Element:
    return NavigationContainer(
        Tab.Navigator(
            Tab.Screen("Home", component=HomeTab, options={"title": "Home"}),
            Tab.Screen("Layout", component=LayoutTab, options={"title": "Layout"}),
            Tab.Screen("List", component=ListTab, options={"title": "List"}),
            Tab.Screen("Settings", component=SettingsTab, options={"title": "Settings"}),
        )
    )
