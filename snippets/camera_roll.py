"""Camera roll: pick a photo and render it natively.

Tweet options:
1. Tap once, pick a photo, and render it in a real native image view—straight from Python. #PythonNative
2. Pick a photo from the gallery and show it natively, with async/await in plain Python. #Python
3. The native camera roll, opened and rendered from Python in just a few lines. #iOS
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    photo, set_photo = pn.use_state("")

    async def choose_photo() -> None:
        picked = await pn.Camera.pick_from_gallery()
        if picked:
            set_photo(picked)

    def open_picker() -> None:
        pn.run_async(choose_photo())

    preview = (
        pn.Image(
            photo,
            scale_type="cover",
            style=pn.style(width=260, height=260, border_radius=24),
        )
        if photo
        else pn.Text(
            "Tap once. Native picker. Native image view.",
            style=pn.style(color="#64748B", font_size=16),
        )
    )

    return pn.Column(
        pn.Text(
            "Camera roll", style=pn.style(font_size=32, font_weight="700")
        ),
        preview,
        pn.Button("Pick a photo", on_click=open_picker),
        style=pn.style(spacing=18, padding=24, align_items="center"),
    )
