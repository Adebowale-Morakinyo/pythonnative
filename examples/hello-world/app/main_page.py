import pythonnative as pn

try:
    # Optional: used for styling below; safe if rubicon isn't available
    from rubicon.objc import ObjCClass

    UIColor = ObjCClass("UIColor")
except Exception:  # pragma: no cover
    UIColor = None


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView().set_axis("vertical").set_spacing(12).set_alignment("fill").set_padding(all=16)
        stack.add_view(pn.Label("Hello from PythonNative Demo!").set_text_size(18))
        button = pn.Button("Go to Second Page").set_padding(vertical=10, horizontal=14)

        def on_next():
            # Visual confirmation that tap worked (iOS only)
            try:
                if UIColor is not None:
                    button.native_instance.setBackgroundColor_(UIColor.systemGreenColor())
                    button.native_instance.setTitleColor_forState_(UIColor.whiteColor(), 0)
            except Exception:
                pass
            # Demonstrate passing args
            self.push("app.second_page.SecondPage", args={"message": "Greetings from MainPage"})

        button.set_on_click(on_next)
        # Make the button visually obvious
        button.set_background_color("#FF1E88E5")
        stack.add_view(button)
        self.set_root_view(stack.wrap_in_scroll())

    def on_start(self):
        super().on_start()

    def on_resume(self):
        super().on_resume()

    def on_pause(self):
        super().on_pause()

    def on_stop(self):
        super().on_stop()

    def on_destroy(self):
        super().on_destroy()

    def on_restart(self):
        super().on_restart()

    def on_save_instance_state(self):
        super().on_save_instance_state()

    def on_restore_instance_state(self):
        super().on_restore_instance_state()
