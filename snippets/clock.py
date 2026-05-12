"""Clock: a live timer driven by use_effect.

Tweet options:
1. A live clock that ticks every second, driven entirely by use_effect in Python. #PythonNative
2. A timer plus use_effect gives you a ticking native clock—no JavaScript in sight. #PythonNative
3. Build a ticking clock in PythonNative with one hook and one timer. #Python
"""

import threading
import time

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    now, set_now = pn.use_state(time.strftime("%H:%M:%S"))

    def schedule_tick():
        timer = threading.Timer(1.0, lambda: set_now(time.strftime("%H:%M:%S")))
        timer.start()
        return timer.cancel

    pn.use_effect(schedule_tick, [now])

    return pn.Column(
        pn.Text(now, style=pn.style(font_size=64, font_weight="300")),
        style=pn.style(flex=1, justify_content="center", align_items="center"),
    )
