import os

os.environ[
    "JAVA_HOME"
] = "/Library/Java/JavaVirtualMachines/jdk-12.0.2.jdk/Contents/Home"

from jnius import autoclass
import json

# Load the necessary Java classes using pyjnius
ContextClass = autoclass("android.widget.Button")
ModifierClass = autoclass("java.lang.reflect.Modifier")


def extract(java_class):
    # Get all the methods of the Android class
    methods = java_class.getMethods()
    # Extract metadata for each method
    data = []
    for method in methods:
        method_name = method.getName()
        method_return_type = method.getReturnType().getSimpleName()
        method_parameters = method.getParameterTypes()
        method_parameter_types = [param.getSimpleName() for param in method_parameters]
        method_modifiers = ModifierClass.toString(method.getModifiers())
        method_metadata = {
            "Name": method_name,
            "ReturnType": method_return_type,
            "ParameterTypes": method_parameter_types,
            "Modifiers": method_modifiers,
            "Type": "Method",  # since we're only dealing with methods here
        }
        data.append(method_metadata)
    return data


def main():
    metadata = extract(ContextClass)
    # Save the extracted metadata
    with open("android_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
