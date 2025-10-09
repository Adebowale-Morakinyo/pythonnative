---
title: Roadmap
---

# PythonNative Roadmap (v0.2.0 → v0.10.0)

This roadmap focuses on transforming PythonNative into a workable, React Native / Expo-like framework from a developer-experience and simplicity standpoint. Releases are incremental and designed to be shippable, with DX-first improvements balanced with platform capability.

Assumptions
- Current version: 0.1.0
- Scope: Android (Chaquopy/Java bridge) and iOS (Rubicon-ObjC), Python 3.9–3.12
- Goals: Zero-config templates, one CLI, fast iteration loop, portable component API, and a curated subset of native capabilities with room to expand.

Guiding Principles
- Single CLI for init/run/build/clean.
- Convention over configuration: opinionated project layout (`app/`, `pythonnative.json`, `requirements.txt`).
- Hot reload (where feasible) and rapid feedback.
- Stable component API; platform shims kept internal.
- Progressive enhancement: start with a minimal but complete loop, add breadth and depth over time.

Milestones

0.2.0 — Foundations: DX Baseline and Templates
- CLI
  - pn init: generate project with `app/`, `pythonnative.json`, `requirements.txt`, `.gitignore`.
  - pn run android|ios: scaffold template apps (from bundled zips), copy `app/`, install requirements, build+install/run.
  - pn clean: remove `build/` safely.
- Templates
  - Bundle `templates/android_template.zip` and `templates/ios_template.zip` into package to avoid network.
  - Ensure Android template uses Kotlin+Chaquopy; iOS template uses Swift+PythonKit+Rubicon.
- Core APIs
  - Stabilize `Page`, `StackView`, `Label`, `Button`, `ImageView`, `TextField`, `TextView`, `Switch`, `ProgressView`, `ActivityIndicatorView`, `WebView` with consistent ctor patterns.
  - Add `utils.IS_ANDROID` fallback detection improvements.
- Docs
  - Getting Started (one page), Hello World, Concepts: Components, Guides: Android/iOS quickstart.
  - Roadmap (this page). Contributing.

Success Criteria
- New user can: pn init → pn run android → sees Hello World UI; same for iOS.

0.3.0 — Navigation and Lifecycle
- API
  - Page navigation abstraction with push/pop (Android: Activity/Fragment shim, iOS: UINavigationController).
  - Lifecycle events stabilized and wired from host to Python (on_create/start/resume/pause/stop/destroy).
- Templates
  - Two-screen sample demonstrating navigation and parameter passing.
- Docs
  - Navigation guide with examples.

Success Criteria
- Sample app navigates between two pages on both platforms using the same Python API.

0.4.0 — Layout and Styling Pass
- API
  - Improve `StackView` configuration: axis, spacing, alignment; add `ScrollView` wrapping helpers.
  - Add lightweight style API (padding/margin where supported, background color, text color/size for text components).
- DX
  - Component property setters return self for fluent configuration where ergonomic.
- Docs
  - Styling guide and component property reference.

Success Criteria
- Build complex vertical forms and simple horizontal layouts with predictable results on both platforms.

0.5.0 — Developer Experience: Live Reload Loop
- DX
  - pn dev android|ios: dev server watching `app/` with file-sync into running app.
  - Implement soft-reload: trigger Python module reload and page re-render without full app restart where possible.
  - Fallback to fast reinstall when soft-reload not possible.
- Templates
  - Integrate dev menu gesture (e.g., triple-tap or shake) to trigger reload.
- Docs
  - Dev workflow: live reload expectations and caveats.

Success Criteria
- Edit Python in `app/`, trigger near-instant UI update on device/emulator.

0.6.0 — Forms and Lists
- API
  - `ListView` cross-platform wrapper with simple adapter API (Python callback to render rows, handle click).
  - Input controls: `DatePicker`, `TimePicker`, basic validation utilities.
  - Add `PickerView` parity or mark as experimental if iOS-first.
- Performance
  - Ensure cell reuse on Android/iOS to handle 1k-row lists smoothly.
- Docs
  - Lists guide, forms guide with validation patterns.

Success Criteria
- Build a basic todo app with a scrollable list and an add-item form.

0.7.0 — Networking, Storage, and Permissions Primitives
- API
  - Simple `fetch`-like helper (thin wrapper over requests/URLSession with threading off main UI thread).
  - Key-value storage abstraction (Android SharedPreferences / iOS UserDefaults).
  - Permission prompts helper (camera, location, notifications) with consistent API returning futures/promises.
- DX
  - Background threading utilities for long-running tasks with callback to main thread.
- Docs
  - Data fetching, local storage, permissions cookbook.

Success Criteria
- Build a data-driven screen that fetches remote JSON, caches a token, and requests permission.

0.8.0 — Theming and Material Components (Android parity), iOS polish
- API
  - Theme object for colors/typography; propagate defaults to components.
  - Material variants: MaterialButton, MaterialProgress, MaterialSearchBar, MaterialSwitch stabilized.
  - iOS polishing: ensure UIKit equivalents’ look-and-feel is sensible by default.
- DX
  - Dark/light theme toggling hook.
- Docs
  - Theming guide with examples.

Success Criteria
- Switch between light/dark themes and see consistent component styling across screens.

0.9.0 — Packaging, Testing, and CI
- CLI
  - pn build android|ios: produce signed (debug) APK/IPA or x archive guidance; integrate keystore setup helper for Android.
  - pn test: run Python unit tests; document UI test strategy (manual/host-level instrumentation later).
- Tooling
  - Add ruff/black/mypy default config and `pn fmt`, `pn lint` wrappers.
- Docs
  - Release checklist; testing guide.

Success Criteria
- Produce installable builds via pn build; run unit tests with a single command.

0.10.0 — Plugin System (Early) and Project Orchestration
- Plugins
  - Define `pythonnative.plugins` entry point allowing add-ons (e.g., Camera, Filesystem) to register platform shims.
  - pn plugin add <name>: scaffold plugin structure and install dependency.
- Orchestration
  - Config-driven `pythonnative.json`: targets, app id/name, icons/splash, permissions, minSDK/iOS version.
  - Asset pipeline: copy assets to correct platform locations.
- Docs
  - Plugin authoring guide; configuration reference.

Success Criteria
- Install a community plugin and use it from Python without touching native code.

Backlog and Stretch (post-0.10)
- Cross-platform navigation stack parity (Fragments vs Activities, or single-activity multi-fragment on Android).
- Advanced layout (ConstraintLayout/AutoLayout helpers) with declarative constraints.
- Gesture/touch handling unification, animations/transitions.
- Expo-like over-the-air updates pipeline.
- Desktop/web exploration via PyObjC/Qt bridges (research).

Breaking Changes Policy
- Pre-1.0: Minor versions may include breaking changes; provide migration notes and deprecation warnings one release ahead when possible.

Tracking and Releases
- Each milestone will have a GitHub project board and labeled issues.
- Changelogs maintained per release; upgrade guides in docs.
