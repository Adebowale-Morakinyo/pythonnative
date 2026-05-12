"""Flexbox: the middle column stretches, the others stay fixed.

Tweet options:
1. Flexbox in PythonNative: the middle column stretches while the outer two stay fixed. #PythonNative
2. A pure-Python flexbox engine—fixed sides, a stretchy middle, and native layout. #PythonNative
3. Real flexbox in Python: fixed sides, a stretchy center, and no CSS in sight. #Python
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    return pn.Row(
        pn.View(style=pn.style(width=80, background_color="#0EA5E9", padding=16)),
        pn.View(style=pn.style(flex=1, background_color="#22C55E", padding=16)),
        pn.View(style=pn.style(width=60, background_color="#EF4444", padding=16)),
        style=pn.style(spacing=8, padding=16, height=120),
    )
