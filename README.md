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

PythonNative is a cross-platform toolkit for building native Android and iOS apps in Python. It provides a Pythonic API for native UI components, lifecycle events, and device capabilities, powered by Chaquopy on Android and rubicon-objc on iOS. Write your app once in Python and run it on both platforms with genuinely native interfaces.

## Features

- **Cross-platform native UI:** Build Android and iOS apps from a single Python codebase with truly native rendering.
- **Direct native bindings:** Python calls platform APIs directly through Chaquopy and rubicon-objc, with no JavaScript bridge.
- **Unified component API:** Components like `Page`, `StackView`, `Label`, `Button`, and `WebView` share a consistent interface across platforms.
- **CLI scaffolding:** `pn init` creates a ready-to-run project structure; `pn run android` and `pn run ios` build and launch your app.
- **Page lifecycle:** Hooks for `on_create`, `on_start`, `on_resume`, `on_pause`, `on_stop`, and `on_destroy`, with state save and restore.
- **Navigation:** Push and pop screens with argument passing for multi-page apps.
- **Rich component set:** Core views (Label, Button, TextField, ImageView, WebView, Switch, DatePicker, and more) plus Material Design variants.
- **Bundled templates:** Android Gradle and iOS Xcode templates are included, so scaffolding requires no network access.

## Quick Start

### Installation

```bash
pip install pythonnative
```

### Usage

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("Hello from PythonNative!"))
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Button tapped"))
        stack.add_view(button)
        self.set_root_view(stack)
```

## Documentation

Visit [docs.pythonnative.com](https://docs.pythonnative.com/) for the full documentation, including getting started guides, platform-specific instructions for Android and iOS, API reference, and working examples.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding standards, and guidelines for submitting pull requests.

## License

[MIT](LICENSE)
