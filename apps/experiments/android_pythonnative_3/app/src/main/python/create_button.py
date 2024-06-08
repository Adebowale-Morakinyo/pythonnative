from java import cast, chaquopy, dynamic_proxy, jarray, jclass


def create_button(context):
    Button = jclass("android.widget.Button")
    button = Button(context)
    button.setText("Button created in Python")
    return button
