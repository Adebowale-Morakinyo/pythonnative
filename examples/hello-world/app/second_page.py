from typing import Any

import pythonnative as pn

try:
    # Optional: iOS styling support (safe if rubicon isn't available)
    from rubicon.objc import ObjCClass

    UIColor = ObjCClass("UIColor")
except Exception:  # pragma: no cover
    UIColor = None


class SecondPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)

    def on_create(self) -> None:
        super().on_create()
        stack_view = pn.StackView()
        # Read args passed from MainPage
        args = self.get_args()
        message = args.get("message", "Second page!")
        stack_view.add_view(pn.Label(message))
        # Navigate to Third Page
        to_third_btn = pn.Button("Go to Third Page")
        # Style button on iOS similar to MainPage
        try:
            if UIColor is not None:
                to_third_btn.native_instance.setBackgroundColor_(UIColor.systemBlueColor())
                to_third_btn.native_instance.setTitleColor_forState_(UIColor.whiteColor(), 0)
        except Exception:
            pass

        def on_next() -> None:
            # Visual confirmation that tap worked (iOS only)
            try:
                if UIColor is not None:
                    to_third_btn.native_instance.setBackgroundColor_(UIColor.systemGreenColor())
                    to_third_btn.native_instance.setTitleColor_forState_(UIColor.whiteColor(), 0)
            except Exception:
                pass
            self.push("app.third_page.ThirdPage", args={"from": "Second"})

        to_third_btn.set_on_click(on_next)
        stack_view.add_view(to_third_btn)
        back_btn = pn.Button("Back")
        back_btn.set_on_click(lambda: self.pop())
        stack_view.add_view(back_btn)
        self.set_root_view(stack_view)

    def on_start(self) -> None:
        super().on_start()

    def on_resume(self) -> None:
        super().on_resume()

    def on_pause(self) -> None:
        super().on_pause()

    def on_stop(self) -> None:
        super().on_stop()

    def on_destroy(self) -> None:
        super().on_destroy()

    def on_restart(self) -> None:
        super().on_restart()

    def on_save_instance_state(self) -> None:
        super().on_save_instance_state()

    def on_restore_instance_state(self) -> None:
        super().on_restore_instance_state()
