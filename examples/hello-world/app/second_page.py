import pythonnative as pn


class SecondPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack_view = pn.StackView()
        # Read args passed from MainPage
        args = self.get_args()
        message = args.get("message", "Second page!")
        stack_view.add_view(pn.Label(message))
        back_btn = pn.Button("Back")
        back_btn.set_on_click(lambda: self.pop())
        stack_view.add_view(back_btn)
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
