from rubicon.java import JavaClass

Button = JavaClass("android/widget/Button")


def create_button(context):
    button = Button(context)
    button.setId(hash(button))
    button.setText("Button created in Python")
    return button.getId()
