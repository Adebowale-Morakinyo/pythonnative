import pythonnative as pn


def main():
    # Create a screen
    screen = pn.Screen()

    # Create a layout
    layout = pn.LinearLayout()

    # Create a button and add it to layout
    button = pn.Button("Click Me")
    layout.add_view(button)

    # Create a label and add it to layout
    label = pn.Label("Hello, World!")
    layout.add_view(label)

    # Set layout to screen
    screen.set_layout(layout)

    # Display the screen
    screen.show()


if __name__ == "__main__":
    main()
