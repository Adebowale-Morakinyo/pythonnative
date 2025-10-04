import pythonnative as pn


class Page:
    def __init__(self, context):
        self.context = context

    def on_create(self):
        print("on_create() called")
        stack_view = pn.StackView(self.context)
        material_button = pn.MaterialButton(self.context, "MaterialButton")
        stack_view.add_view(material_button)
        # Create and add other views to the stack_view here
        return stack_view.native_instance

    def on_start(self):
        print("on_start() called")

    def on_resume(self):
        print("on_resume() called")

    def on_pause(self):
        print("on_pause() called")

    def on_stop(self):
        print("on_stop() called")

    def on_destroy(self):
        print("on_destroy() called")

    def on_restart(self):
        print("on_restart() called")

    def on_save_instance_state(self):
        print("on_save_instance_state() called")

    def on_restore_instance_state(self):
        print("on_restore_instance_state() called")
