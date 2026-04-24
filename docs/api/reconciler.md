# Reconciler

Diffs successive virtual trees and applies the smallest set of native
mutations that bring the on-screen view tree in line with the new
description. The reconciler is platform-agnostic; it talks to native
widgets exclusively through the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry].

::: pythonnative.reconciler
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Next steps

- Read the high-level walkthrough in
  [Reconciliation](../concepts/reconciliation.md).
- See how native widgets are registered in [Native views](native_views.md).
