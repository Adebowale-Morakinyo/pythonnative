import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("Hello from PythonNative Demo!"))
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Demo button clicked"))
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
