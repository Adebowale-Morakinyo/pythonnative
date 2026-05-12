"""List: 1000 virtualized rows backed by native recycling.

Tweet options:
1. One thousand virtualized rows, smooth scrolling, and native recycling—all from Python. #PythonNative
2. FlatList renders 1,000 rows with real native view recycling under the hood. #PythonNative
3. Scroll 1,000 rows at native speed, backed by Python and view recycling. #MobileDev
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    items = [{"id": i, "title": f"Row {i + 1}"} for i in range(1000)]
    return pn.FlatList(
        data=items,
        item_height=56,
        render_item=lambda item, _: pn.View(
            pn.Text(item["title"], style=pn.style(font_size=16)),
            style=pn.style(padding=16, background_color="#FFFFFF"),
        ),
        key_extractor=lambda item, _: str(item["id"]),
        style=pn.style(flex=1, background_color="#F3F4F6"),
    )
