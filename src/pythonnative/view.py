from abc import ABC, abstractmethod

# ========================================
# Base class
# ========================================


class ViewBase(ABC):
    def __init__(self) -> None:
        self.native_instance = None
        self.native_class = None

    # @abstractmethod
    # def add_view(self, view):
    #     pass
    #
    # @abstractmethod
    # def set_layout(self, layout):
    #     pass
    #
    # @abstractmethod
    # def show(self):
    #     pass
