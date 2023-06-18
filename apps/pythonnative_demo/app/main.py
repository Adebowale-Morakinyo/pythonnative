import pythonnative as pn


def main():
    # Create a main view
    main_view = pn.View()

    # Create a layout
    layout = pn.LinearLayout()

    # Create a button and add it to layout
    button = pn.Button("Click Me")
    layout.add_view(button)

    # Create a label and add it to layout
    label = pn.Label("Hello, World!")
    layout.add_view(label)

    # Add layout to main view
    main_view.add_view(layout)

    # Display the main view
    main_view.show()


if __name__ == "__main__":
    main()
