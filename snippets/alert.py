"""Alert: a real native confirm dialog from Python.

Tweet options:
1. Trigger a real native confirmation dialog straight from Python—no custom UI needed. #PythonNative
2. A genuine platform alert, complete with confirm and cancel actions, called from Python. #iOS
3. Native confirm dialogs from one Python call—title, message, and buttons included. #PythonNative
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    def confirm_delete():
        pn.Alert.confirm(
            title="Delete item?",
            message="This action cannot be undone.",
            confirm_label="Delete",
            cancel_label="Keep",
            on_confirm=lambda: print("deleted"),
        )

    return pn.Column(
        pn.Button("Delete", on_click=confirm_delete),
        style=pn.style(flex=1, padding=24, justify_content="center"),
    )
