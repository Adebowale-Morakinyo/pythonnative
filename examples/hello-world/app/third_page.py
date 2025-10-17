import pythonnative as pn

try:
    # Optional: iOS styling support (safe if rubicon isn't available)
    from rubicon.objc import ObjCClass

    UIColor = ObjCClass("UIColor")
except Exception:  # pragma: no cover
    UIColor = None


class ThirdPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("This is the Third Page"))
        back_btn = pn.Button("Back")
        # Style button on iOS similar to MainPage
        try:
            if UIColor is not None:
                back_btn.native_instance.setBackgroundColor_(UIColor.systemBlueColor())
                back_btn.native_instance.setTitleColor_forState_(UIColor.whiteColor(), 0)
        except Exception:
            pass
        back_btn.set_on_click(lambda: self.pop())
        stack.add_view(back_btn)
        self.set_root_view(stack)
