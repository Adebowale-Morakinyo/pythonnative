<p align="center">
  <img src="docs/assets/banner.jpg" alt="PythonNative" width="800" />
</p>

<p align="center">
  <em>Build native Android and iOS apps in Python.</em>
</p>

<p align="center">
  <a href="https://github.com/pythonnative/pythonnative/actions/workflows/ci.yml"><img src="https://github.com/pythonnative/pythonnative/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/pythonnative/pythonnative/actions/workflows/release.yml"><img src="https://github.com/pythonnative/pythonnative/actions/workflows/release.yml/badge.svg" alt="Release" /></a>
  <a href="https://pypi.org/project/pythonnative/"><img src="https://img.shields.io/pypi/v/pythonnative" alt="PyPI Version" /></a>
  <a href="https://pypi.org/project/pythonnative/"><img src="https://img.shields.io/pypi/pyversions/pythonnative" alt="Python Versions" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/pythonnative" alt="License: MIT" /></a>
  <a href="https://docs.pythonnative.com/"><img src="https://img.shields.io/website?url=https%3A%2F%2Fdocs.pythonnative.com&label=docs" alt="Docs" /></a>
</p>

<p align="center">
  <a href="https://docs.pythonnative.com/">Documentation</a> ·
  <a href="https://docs.pythonnative.com/getting-started/">Getting Started</a> ·
  <a href="https://docs.pythonnative.com/examples/">Examples</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

---

## Overview

PythonNative is a cross-platform toolkit for building native Android and iOS apps in Python. It provides a **declarative, React-like component model** with hooks and automatic reconciliation, powered by Chaquopy on Android and rubicon-objc on iOS. Write function components with `use_state`, `use_effect`, and friends, just like React, and let PythonNative handle creating and updating native views.

## Features

- **Declarative UI:** Describe *what* your UI should look like with element functions (`Text`, `Button`, `Column`, `Row`, etc.). PythonNative creates and updates native views automatically.
- **Hooks and function components:** Manage state with `use_state`, side effects with `use_effect`, and navigation with `use_navigation`, all through one consistent pattern.
- **`style` prop:** Pass all visual and layout properties through a single `style` dict, composable via `StyleSheet`.
- **Virtual view tree + reconciler:** Element trees are diffed and patched with minimal native mutations, similar to React's reconciliation.
- **Direct native bindings:** Python calls platform APIs directly through Chaquopy and rubicon-objc, with no JavaScript bridge.
- **CLI scaffolding:** `pn init` creates a ready-to-run project; `pn run android` and `pn run ios` build and launch your app.
- **Navigation:** Push and pop screens with argument passing via the `use_navigation()` hook.
- **Bundled templates:** Android Gradle and iOS Xcode templates are included, so scaffolding requires no network access.

## Quick Start

### Installation

```bash
pip install pythonnative
```

### Usage

```python
import pythonnative as pn


@pn.component
def MainPage():
    count, set_count = pn.use_state(0)
    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 24}),
        pn.Button(
            "Tap me",
            on_click=lambda: set_count(count + 1),
        ),
        style={"spacing": 12, "padding": 16},
    )
```

## Documentation

Visit [docs.pythonnative.com](https://docs.pythonnative.com/) for the full documentation, including getting started guides, platform-specific instructions for Android and iOS, API reference, and working examples.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding standards, and guidelines for submitting pull requests.

## License

[MIT](LICENSE)
