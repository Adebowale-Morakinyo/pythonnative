# PythonNative

PythonNative is a cross-platform Python tool kit for Android and iOS. It allows you to create native UI elements such as buttons and labels in a Pythonic way, regardless of whether you're running on iOS or Android.

## Installation

You can install PythonNative from PyPI:

```bash
pip install pythonnative
```

Please note that PythonNative requires Python 3.6 or higher.

## Usage

Here's a simple example of how to create a button and a label:

```python
import pythonnative as pn

# Create a button
button = pn.Button("Click Me")
print(button.get_title())  # Outputs: Click Me

# Create a label
label = pn.Label("Hello, World!")
print(label.get_text())  # Outputs: Hello, World!
```

## License

PythonNative is licensed under the MIT License. See `LICENSE` for more information.
