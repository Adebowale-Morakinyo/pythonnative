import pythonnative as pn


def main(context):
    layout = pn.LinearLayout(context)

    label = pn.Label(context, "This is a PythonNative label")
    layout.add_view(label)

    switch = pn.Switch(context)
    layout.add_view(switch)

    for i in range(100):
        button = pn.Button(context, "Click me")
        layout.add_view(button)

    return layout.native_instance
