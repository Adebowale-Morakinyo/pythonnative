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
        stack = pn.StackView()
        # Ensure vertical stacking
        try:
            stack.native_instance.setAxis_(1)  # 1 = vertical
        except Exception:
            pass
        stack.add_view(pn.Label("Hello from PythonNative Demo!"))
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Demo button clicked"))
        # Make the button visually obvious
        try:
            if UIColor is not None:
                button.native_instance.setBackgroundColor_(UIColor.systemBlueColor())
                button.native_instance.setTitleColor_forState_(UIColor.whiteColor(), 0)
        except Exception:
            pass
        stack.add_view(button)
        self.set_root_view(stack)

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


def bootstrap(native_instance):
    page = MainPage(native_instance)
    page.on_create()
    return page
