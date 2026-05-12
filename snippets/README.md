# Shareable snippets

A small collection of self-contained PythonNative snippets designed to be
screenshotted and posted on X. Each file is a complete `App` component you can
drop straight into `app/main.py` of a `pn init` project.

Each snippet's module docstring contains a suggested tweet caption.

## How to share

1. Open a snippet in your editor (or paste it into a screenshot tool like
   [Carbon](https://carbon.now.sh/) or [ray.so](https://ray.so/)).
2. Crop to the `import` line and below. Hide the docstring if you want a
   tighter screenshot — it exists mostly to hold the suggested caption.
3. Copy the tweet caption from the docstring as a starting point.

## How to verify a snippet still works

```bash
pn init demo
cd demo
cp ../snippets/counter.py app/main.py
pn run ios   # or: pn run android
```

## The snippets

| File | What it shows | Why it's shareable |
| --- | --- | --- |
| `counter.py` | `use_state` + a Button | The canonical "12 lines = native iOS + Android" hook. |
| `clock.py` | `use_state` + `use_effect` + `threading.Timer` | Live UI, no event loop boilerplate. |
| `animation.py` | `Animated.parallel`, spring + timing | "It actually animates natively" moment. |
| `navigation.py` | `create_stack_navigator`, `use_navigation` | Two screens, real native stack and back gesture. |
| `form.py` | `TextInput` with two-way binding | Type, see headline update — instantly understandable. |
| `flexbox.py` | `Row` with `flex: 1` middle child | The CSS flexbox audience instantly gets it. |
| `list.py` | `FlatList` with 1000 rows | "From Python" + virtualized native recycling. |
| `alert.py` | `Alert.confirm` | A real native dialog from three lines of Python. |
| `theme_toggle.py` | `use_state` driving a theme dict | Whole-tree restyle in one tap. |
| `todo.py` | List + `TextInput` + `Pressable` | The classic "is this framework real?" benchmark. |
| `plugin.py` | `@native_component` + `Props` + `element_factory` | Ship your own native widget as a typed PythonNative element. |
| `plugin_toggle.py` | The same SDK contract on a one-prop UISwitch | Smallest possible plugin — fits cleanly in a screenshot. |

## Suggested posting order

A rough order from "fastest to grok" to "most ambitious":

1. `counter.py` — start here, it's the strongest hook.
2. `form.py` — relatable, instantly satisfying.
3. `clock.py` — proves hooks compose properly.
4. `flexbox.py` — wins over the CSS / React Native crowd.
5. `alert.py` — short, tweet-sized "native, not webview" proof.
6. `theme_toggle.py` — viral with the design-systems crowd.
7. `animation.py` — pair with a screen recording for max impact.
8. `list.py` — pair with a scrolling video.
9. `navigation.py` — slightly longer, but a strong "it's real" beat.
10. `todo.py` — the closer; ties everything together.
11. `plugin_toggle.py` — the smallest "you can extend this yourself" beat.
12. `plugin.py` — same beat, longer real-world example with theming.
