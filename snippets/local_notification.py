"""Local notification: request permission, schedule reminder.

Tweet options:
1. Request permission and schedule a local notification, all from a few lines of Python. #PythonNative
2. Fire a native local reminder five seconds from now, scheduled in pure Python. #iOS
3. Native notification permissions and scheduling, handled with async Python. #MobileDev
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    status, set_status = pn.use_state("Ready")

    async def remind() -> None:
        set_status("Asking permission...")
        if not await pn.Notifications.request_permission():
            set_status("Notifications are off")
            return

        ok = await pn.Notifications.schedule(
            "Time to ship",
            body="Your PythonNative reminder fired.",
            delay_seconds=5,
            identifier="viral-demo",
        )
        set_status("Reminder scheduled" if ok else "Could not schedule")

    def schedule() -> None:
        pn.run_async(remind())

    return pn.Column(
        pn.Text("Local push", style=pn.style(font_size=34, font_weight="700")),
        pn.Text(status, style=pn.style(font_size=16, color="#475569")),
        pn.Button("Remind me in 5s", on_click=schedule),
        style=pn.style(
            flex=1,
            spacing=16,
            padding=24,
            justify_content="center",
            align_items="center",
        ),
    )
