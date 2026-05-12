"""Pull to refresh: native spinner, Python callback.

Tweet options:
1. Pull to refresh with a real native spinner, backed by a plain Python callback. #PythonNative
2. The native pull-to-refresh spinner, wired to your Python code—no JavaScript bridge. #PythonNative
3. Drag down, fire a Python callback, and prepend fresh posts to the feed. #Python
"""

import threading

import pythonnative as pn

FEED = [
    "Launch notes",
    "Design teardown",
    "Native modules",
    "Zero-JS bridge",
]


@pn.component
def App() -> pn.Element:
    items, set_items = pn.use_state(FEED)
    refreshing, set_refreshing = pn.use_state(False)

    def reload() -> None:
        set_refreshing(True)

        def finish() -> None:
            set_items([f"Fresh post #{len(items) + 1}", *items[:4]])
            set_refreshing(False)

        threading.Timer(0.7, finish).start()

    return pn.ScrollView(
        pn.Column(
            pn.Text(
                "Pull down", style=pn.style(font_size=32, font_weight="700")
            ),
            *[
                pn.View(
                    pn.Text(item, style=pn.style(font_size=17)),
                    style=pn.style(
                        padding=16,
                        border_radius=14,
                        background_color="#FFFFFF",
                    ),
                )
                for item in items
            ],
            style=pn.style(spacing=12, padding=20),
        ),
        refresh_control=pn.RefreshControl(
            refreshing=refreshing,
            on_refresh=reload,
            tint_color="#2563EB",
        ),
        style=pn.style(flex=1, background_color="#EEF2FF"),
    )
