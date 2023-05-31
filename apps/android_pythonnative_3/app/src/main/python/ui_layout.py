import json


def on_button_click():
    print("Button clicked!")


def generate_layout():
    layout = {
        "widgets": [
            {
                "type": "Button",
                "properties": {
                    "text": "Click me!",
                    "textColor": "#FFFFFF",
                    "backgroundColor": "#DB4437",
                },
                "eventHandlers": {
                    "onClick": "on_button_click",
                }
            },
        ]
    }
    return json.dumps(layout)
