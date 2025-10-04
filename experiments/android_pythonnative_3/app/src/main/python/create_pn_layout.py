import pythonnative as pn


def create_pn_layout(context):
    layout = pn.StackView(context)

    label = pn.Label(context, "This is a PythonNative label")
    layout.add_view(label)

    button = pn.Button(context, "Click me")
    layout.add_view(button)

    return layout.native_instance
