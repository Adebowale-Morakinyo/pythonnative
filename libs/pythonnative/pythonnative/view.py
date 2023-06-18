class View:
    def __init__(self) -> None:
        self.native_instance = None
        self.native_class = None

    def add_view(self, view):
        raise NotImplementedError("This method should be implemented in a subclass.")

    def set_layout(self, layout):
        raise NotImplementedError("This method should be implemented in a subclass.")

    def show(self):
        raise NotImplementedError("This method should be implemented in a subclass.")
