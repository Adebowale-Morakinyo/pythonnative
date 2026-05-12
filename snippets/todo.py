"""Todo: add, toggle complete, all in one tiny App component.

Tweet options:
1. Add items, toggle them complete, and clear the input—a whole todo app in one tiny component. #PythonNative
2. A working todo list with add and toggle, built from a single Python component. #PythonNative
3. Add, complete, and track todos in one small App component, all in Python. #Python
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    todos, set_todos = pn.use_state([])
    draft, set_draft = pn.use_state("")

    def add():
        if draft.strip():
            set_todos([*todos, {"text": draft, "done": False}])
            set_draft("")

    def toggle(i: int):
        set_todos([{**t, "done": not t["done"]} if j == i else t for j, t in enumerate(todos)])

    return pn.Column(
        pn.Text("Todos", style=pn.style(font_size=32, font_weight="700")),
        pn.Row(
            pn.TextInput(
                value=draft,
                placeholder="What needs doing?",
                on_change=set_draft,
                style=pn.style(flex=1, padding=10, border_width=1, border_radius=8),
            ),
            pn.Button("Add", on_click=add),
            style=pn.style(spacing=8, align_items="center"),
        ),
        *[
            pn.Pressable(
                pn.Text(
                    ("✓ " if t["done"] else "○ ") + t["text"],
                    style=pn.style(
                        font_size=16,
                        color="#94A3B8" if t["done"] else "#0F172A",
                        padding=8,
                    ),
                ),
                on_press=lambda i=i: toggle(i),
            )
            for i, t in enumerate(todos)
        ],
        style=pn.style(spacing=12, padding=24),
    )
