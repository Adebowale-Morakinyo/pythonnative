# Alerts

The [`Alert`][pythonnative.Alert] class provides imperative access to
the host platform's alert dialogs and action sheets. Alerts are *not*
part of the element tree — they're fire-and-forget calls that present
a native dialog and dispatch button callbacks.

::: pythonnative.alerts
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members_order: source
      filters: ["!^_"]

## Patterns

- **Confirm before destructive actions**: pair a `"destructive"`
  button with a `"cancel"` button via
  [`Alert.confirm`][pythonnative.alerts.Alert.confirm].
- **Action sheets**: pass `style="action_sheet"` to render an iOS-style
  bottom sheet; on Android this falls back to a regular dialog.
- **Pickers**: the built-in [`Picker`][pythonnative.Picker] component
  is implemented on top of action sheets — use it for select/dropdown
  widgets.

## Testing

When running off-device (e.g., in unit tests), `Alert.show` records
each call to `Alert._test_log` instead of presenting a dialog. Reset
the log with `Alert._test_log.clear()` between cases.
