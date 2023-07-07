import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def on_create(self):
        super().on_create()

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
