import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack_view = pn.StackView(self.native_instance)
        # list_data = ["item_{}".format(i) for i in range(100)]
        # list_view = pn.ListView(self.native_instance, list_data)
        # stack_view.add_view(list_view)
        button = pn.Button(self.native_instance, "Button")
        button.set_on_click(lambda: print("Button was clicked!"))
        stack_view.add_view(button)
        self.set_root_view(stack_view)

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
