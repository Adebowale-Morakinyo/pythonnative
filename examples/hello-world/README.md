# Hello World

The smallest PythonNative app: a counter with navigation to a detail
screen.

## Preview it on your desktop (fastest)

From this directory, install the example's dependencies (the preview
imports your real app code), then launch it. This app declares `emoji`
in `[requirements].packages`, so install it locally for the preview:

```bash
pip install emoji
pn preview
```

A desktop window opens running `app/main.py`'s `App`. Edit any component
under `app/`, save, and the window Fast Refreshes in place (no
simulator or device needed). See the
[Desktop preview guide](../../docs/guides/desktop-preview.md).

## Develop on a device with live reload (fastest on hardware)

Install the PythonNative Go client once, then serve this app to it over
Wi-Fi with Fast Refresh on every save:

```bash
pn go install ios     # or: pn go install android
pn start              # prints a URL + QR code; connect from the client
```

See the [PythonNative Go guide](../../docs/guides/dev-client.md).

## Run a standalone build

```bash
pn run ios
# or
pn run android
```

This bakes the app into the native shell (no dev server). Use it to test
a real build before shipping.
