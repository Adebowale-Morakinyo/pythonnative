"""Animation: parallel spring + timing on a single view.

Tweet options:
1. Run a spring and a timing animation in parallel on one view, all in Python. #PythonNative
2. A native entrance animation—opacity and scale springing in together, driven from Python. #PythonNative
3. Parallel spring and timing animations on a single view—no JavaScript required. #MobileDev
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    opacity = pn.use_memo(lambda: pn.Animated.Value(0.0), [])
    scale = pn.use_memo(lambda: pn.Animated.Value(0.5), [])

    def enter():
        pn.Animated.parallel(
            [
                pn.Animated.timing(opacity, to=1.0, duration=600),
                pn.Animated.spring(scale, to=1.0, stiffness=180, damping=12),
            ]
        ).start()

    pn.use_effect(enter, [])

    return pn.Animated.View(
        pn.Text("Hello.", style=pn.style(font_size=56, font_weight="700")),
        style=pn.style(
            opacity=opacity,
            scale=scale,
            padding=48,
            background_color="#FEF3C7",
            border_radius=24,
        ),
    )
