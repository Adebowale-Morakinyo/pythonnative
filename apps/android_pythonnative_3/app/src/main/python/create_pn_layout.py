# pythonnative.py

import pythonnative as pn


def create_pn_layout():
    layout = pn.LinearLayout()

    label = pn.Label("This is a PythonNative label")
    layout.add_view(label)

    button = pn.Button("Click me")
    layout.add_view(button)

    return layout.native_instance
