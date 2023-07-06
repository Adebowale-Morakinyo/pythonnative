import pythonnative as pn


def main():
    # Create a full-screen page
    page = pn.Page()

    # Create a layout
    stack_view = pn.StackView()

    # Create a button and add it to the layout
    button = pn.Button("Click Me")
    stack_view.add_view(button)

    # Create a label and add it to the layout
    label = pn.Label("Hello, World!")
    stack_view.add_view(label)

    # Set the layout
    page.set_layout(stack_view)

    # Display the page
    page.show()


if __name__ == "__main__":
    main()
