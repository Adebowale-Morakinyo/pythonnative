"""`pn` CLI: scaffold, diagnose, preview, run, and build PythonNative apps.

The console script `pn` (declared in `pyproject.toml`) dispatches to:

- `pn init [name]`: scaffold a new project (``pythonnative.toml`` + ``app/``).
- `pn doctor [platform]`: diagnose the local toolchain and config.
- `pn preview [component]`: render the app in a desktop (Tkinter) window
  with Fast Refresh, the fast inner dev loop, no device required.
- `pn start`: run the dev server and serve the app to PythonNative Go
  over Wi-Fi, with a scannable QR code and live reload on every save.
- `pn go build|install android|ios`: build (and install) the PythonNative
  Go dev client, a generic shell that connects to `pn start`.
- `pn run android|ios`: stage + build + install + launch a standalone
  build on a device or simulator.
- `pn build android|ios`: produce standalone artifacts (signed APK/AAB,
  or an iOS archive/IPA).
- `pn app-id android|ios`: print the resolved application/bundle id
  (handy for scripts and CI).
- `pn clean`: remove the local `build/` directory.

The heavy lifting lives in the ``pythonnative.project`` and
``pythonnative.dev`` packages; this module is a thin, side-effect-y shell
that wires arguments to them and handles the device-facing steps
(simulator boot, log streaming) that can't be unit tested.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..dev import protocol as dev_protocol
from ..project import builder as builder_mod
from ..project import doctor as doctor_mod
from ..project.android import collect_logcat_filters
from ..project.config import CONFIG_FILENAME, AppConfig, ConfigError, render_default_toml

HOT_RELOAD_DEV_ROOT = "pythonnative_dev"
"""Subdirectory (under the app's writable storage) for hot-reload overlays."""


# ======================================================================
# init
# ======================================================================

_MAIN_TEMPLATE = """import pythonnative as pn

Stack = pn.create_stack_navigator()


@pn.component
def HomeScreen():
    count, set_count = pn.use_state(0)
    nav = pn.use_navigation()
    return pn.ScrollView(
        pn.Column(
            pn.Text("Hello from PythonNative!", style={"font_size": 24, "bold": True}),
            pn.Text(f"Tapped {count} times"),
            pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
            pn.Button("Open detail", on_click=lambda: nav.navigate("Detail", {"count": count})),
            style={"spacing": 12, "padding": 16, "align_items": "stretch"},
        )
    )


@pn.component
def DetailScreen():
    nav = pn.use_navigation()
    params = pn.use_route()
    return pn.Column(
        pn.Text(f"Detail: count was {params.get('count', 0)}", style={"font_size": 20}),
        pn.Button("Back", on_click=nav.go_back),
        style={"spacing": 12, "padding": 16},
    )


@pn.component
def App():
    return pn.NavigationContainer(
        Stack.Navigator(
            Stack.Screen("Home", component=HomeScreen, options={"title": "Home"}),
            Stack.Screen("Detail", component=DetailScreen, options={"title": "Detail"}),
        )
    )
"""

_GITIGNORE = "# PythonNative\n__pycache__/\n*.pyc\n.venv/\nbuild/\n.DS_Store\n"


def _app_id_from_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_]", "", name.lower())
    if not slug or not slug[0].isalpha():
        slug = "app" + slug
    return f"com.example.{slug}"


def init_project(args: argparse.Namespace) -> None:
    """Scaffold a new PythonNative project in the current directory.

    Creates ``app/main.py``, ``pythonnative.toml``, and ``.gitignore``.
    Refuses to overwrite existing files unless ``--force`` is passed.

    Args:
        args: Parsed namespace with ``name`` (optional) and ``force``.
    """
    cwd = Path.cwd()
    project_name: str = getattr(args, "name", None) or cwd.name
    force: bool = getattr(args, "force", False)

    app_dir = cwd / "app"
    config_path = cwd / CONFIG_FILENAME
    gitignore_path = cwd / ".gitignore"

    if not force:
        existing = [
            label
            for label, path in (("app/", app_dir), (CONFIG_FILENAME, config_path), (".gitignore", gitignore_path))
            if path.exists()
        ]
        if existing:
            print(f"Refusing to overwrite existing: {', '.join(existing)}. Use --force to overwrite.")
            sys.exit(1)

    app_dir.mkdir(parents=True, exist_ok=True)
    main_py = app_dir / "main.py"
    if force or not main_py.exists():
        main_py.write_text(_MAIN_TEMPLATE, encoding="utf-8")

    config_path.write_text(
        render_default_toml(name=project_name, app_id=_app_id_from_name(project_name)),
        encoding="utf-8",
    )
    if force or not gitignore_path.exists():
        gitignore_path.write_text(_GITIGNORE, encoding="utf-8")

    print(f"Initialized PythonNative project in {cwd}.")
    print("Next: pn preview   (desktop)   |   pn run android   |   pn run ios")


# ======================================================================
# doctor / app-id
# ======================================================================


def doctor_command(args: argparse.Namespace) -> None:
    """Run toolchain/config diagnostics and exit non-zero on errors.

    Args:
        args: Parsed namespace with optional ``platform``.
    """
    platform: Optional[str] = getattr(args, "platform", None)
    results = doctor_mod.run_doctor(Path.cwd(), platform=platform)
    print("PythonNative doctor\n")
    for result in results:
        print(result.format())
    level = doctor_mod.worst_level(results)
    print()
    if level == doctor_mod.ERROR:
        print("Found problems that will block builds. Address the [x] items above.")
        sys.exit(1)
    if level == doctor_mod.WARN:
        print("Ready, with warnings. Review the [!] items above.")
    else:
        print("Everything looks good.")


def app_id_command(args: argparse.Namespace) -> None:
    """Print the resolved application id (Android) or bundle id (iOS).

    Args:
        args: Parsed namespace with ``platform``.
    """
    config = _load_config_or_exit()
    print(config.application_id if args.platform == "android" else config.bundle_id)


# ======================================================================
# preview
# ======================================================================


def preview_project(args: argparse.Namespace) -> None:
    """Render the project in a desktop preview window (Tkinter).

    Re-execs under ``PN_PLATFORM=desktop`` so every module binds to the
    Tkinter backend, then hands off to ``pythonnative.preview.run_preview``.

    Args:
        args: Parsed namespace (``component``, ``width``, ``height``,
            ``title``, ``no_hot_reload``).
    """
    if os.environ.get("PN_PLATFORM") != "desktop":
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pythonnative.cli.pn", *sys.argv[1:]],
                env={**os.environ, "PN_PLATFORM": "desktop"},
            )
        except KeyboardInterrupt:
            sys.exit(130)
        sys.exit(completed.returncode)

    project_dir = Path.cwd()
    component: Optional[str] = getattr(args, "component", None)
    if not component:
        component = _preview_entry(project_dir)

    try:
        from pythonnative.preview import run_preview
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"Error: could not start the desktop preview: {exc}")
        print(
            "The desktop preview needs Tkinter (Python's standard GUI toolkit).\n"
            "On macOS:        brew install python-tk\n"
            "On Debian/Ubuntu: sudo apt-get install python3-tk\n"
            "On Windows:      reinstall Python with the 'tcl/tk' option checked."
        )
        sys.exit(1)

    print(f"Starting PythonNative preview for {component} (Ctrl+C or close the window to stop).")
    try:
        run_preview(
            component,
            project_root=str(project_dir),
            width=getattr(args, "width", 390),
            height=getattr(args, "height", 844),
            title=getattr(args, "title", "PythonNative Preview"),
            hot_reload=not getattr(args, "no_hot_reload", False),
        )
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def _preview_entry(project_dir: Path) -> str:
    try:
        return AppConfig.load(project_dir).entry_module
    except ConfigError:
        return "app.main"


# ======================================================================
# run
# ======================================================================


def run_project(args: argparse.Namespace) -> None:
    """Stage, build, install, and launch the app on a device/simulator.

    This produces a standalone build with the app baked in. For the fast,
    Expo-style inner loop (edit + live reload over Wi-Fi), use ``pn start``
    together with the PythonNative Go client (``pn go install``).

    Args:
        args: Parsed namespace (``platform``, ``prepare_only``, ``no_logs``).
    """
    platform: str = args.platform
    prepare_only: bool = getattr(args, "prepare_only", False)
    show_logs: bool = not getattr(args, "no_logs", False)

    config = _load_config_or_exit()
    builder = builder_mod.Builder(config, log=print)

    try:
        prepared = builder.prepare(platform)
    except builder_mod.BuildError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if prepare_only:
        print(f"Prepared {platform} project in {prepared.project_dir} (prepare-only).")
        return

    try:
        if platform == "android":
            _run_android(builder, prepared, show_logs=show_logs)
        else:
            _run_ios(builder, prepared, show_logs=show_logs)
    except builder_mod.BuildError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def _run_android(
    builder: builder_mod.Builder,
    prepared: builder_mod.PreparedProject,
    *,
    show_logs: bool,
) -> None:
    builder.install_android_debug(prepared)
    _clear_android_hot_reload_overlay(prepared.app_id)
    subprocess.run(
        ["adb", "shell", "am", "start", "-n", f"{prepared.app_id}/.MainActivity"],
        check=True,
    )
    if show_logs:
        proc = _start_android_log_stream()
        if proc is not None:
            try:
                proc.wait()
            except KeyboardInterrupt:
                print()
                _terminate_subprocess(proc)
                print("Stopped log streaming.")


def _run_ios(
    builder: builder_mod.Builder,
    prepared: builder_mod.PreparedProject,
    *,
    show_logs: bool,
) -> None:
    app_path = builder.build_ios_simulator(prepared)
    udid = _select_ios_simulator()
    if udid is None:
        print("No available iOS Simulators found; open the project in Xcode to run.")
        return
    subprocess.run(["xcrun", "simctl", "boot", udid], check=False, capture_output=True)
    subprocess.run(["xcrun", "simctl", "install", udid, str(app_path)], check=False)
    _clear_ios_hot_reload_overlay(prepared.app_id)

    if show_logs:
        env = {**os.environ, "SIMCTL_CHILD_PYTHONUNBUFFERED": "1"}
        print("Launched iOS app on Simulator. Streaming logs (Ctrl+C to stop)...")
        try:
            subprocess.run(
                ["xcrun", "simctl", "launch", "--console-pty", "--terminate-running-process", udid, prepared.app_id],
                env=env,
                check=False,
            )
        except KeyboardInterrupt:
            print()
            subprocess.run(["xcrun", "simctl", "terminate", udid, prepared.app_id], check=False, capture_output=True)
            print("Stopped log streaming.")
    else:
        subprocess.run(["xcrun", "simctl", "launch", udid, prepared.app_id], check=False)
        print("Launched iOS app on Simulator.")


# ======================================================================
# build
# ======================================================================


def build_project(args: argparse.Namespace) -> None:
    """Build standalone, distributable artifacts for ``platform``.

    Args:
        args: Parsed namespace (``platform``, ``debug``).
    """
    platform: str = args.platform
    debug: bool = getattr(args, "debug", False)

    config = _load_config_or_exit()
    builder = builder_mod.Builder(config, log=print)

    try:
        prepared = builder.prepare(platform)
        if platform == "android":
            artifacts = builder.build_android(prepared, debug=debug)
        else:
            if debug:
                app_path = builder.build_ios_simulator(prepared)
                artifacts = builder_mod.BuildArtifacts(paths=[app_path])
            else:
                artifacts = builder.build_ios_archive(prepared)
    except builder_mod.BuildError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if not artifacts.paths:
        print("Build completed, but no artifacts were found. Check the build output above.")
        return
    print("\nBuilt artifacts:")
    for path in artifacts.paths:
        print(f"  {path}")


# ======================================================================
# clean
# ======================================================================


def clean_project(args: argparse.Namespace) -> None:
    """Remove the local ``build/`` directory.

    Args:
        args: Parsed namespace (unused).
    """
    build_dir = Path.cwd() / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("Removed build/ directory.")
    else:
        print("No build/ directory to remove.")


# ======================================================================
# Config helpers
# ======================================================================


def _load_config_or_exit(project_dir: Optional[Path] = None) -> AppConfig:
    try:
        return AppConfig.load(project_dir or Path.cwd())
    except ConfigError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


# ======================================================================
# Device log streaming
# ======================================================================


def _start_android_log_stream() -> Optional[subprocess.Popen]:
    """Clear logcat and stream Python-relevant tags to the terminal.

    Returns:
        The ``adb logcat`` process, or ``None`` if ``adb`` is missing.
    """
    try:
        subprocess.run(["adb", "logcat", "-c"], check=False, capture_output=True)
    except FileNotFoundError:
        print("Note: 'adb' not found on PATH; skipping log streaming.")
        return None
    try:
        proc = subprocess.Popen(["adb", "logcat", *collect_logcat_filters()])
    except FileNotFoundError:
        return None
    print("Streaming Python logs from device (Ctrl+C to stop)...")
    return proc


def _booted_ios_udid() -> Optional[str]:
    """Return a booted iOS Simulator's UDID, or ``None`` if none is booted."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None
    for _runtime, devices in (data.get("devices") or {}).items():
        for device in devices or []:
            if device.get("state") == "Booted" and device.get("udid"):
                return str(device["udid"])
    return None


def _select_ios_simulator() -> Optional[str]:
    """Return a simulator UDID to target (booted first, else an iPhone)."""
    booted = _booted_ios_udid()
    if booted:
        return booted
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None
    devices: List[Dict[str, Any]] = [d for lst in (data.get("devices") or {}).values() for d in (lst or [])]
    for device in devices:
        if "iphone 15" in (device.get("name") or "").lower() and device.get("isAvailable"):
            return device.get("udid")
    for device in devices:
        if device.get("isAvailable") and (device.get("name") or "").lower().startswith("iphone"):
            return device.get("udid")
    return None


def _start_ios_log_stream(bundle_id: str) -> Optional[subprocess.Popen]:
    """Re-launch the iOS app with a console PTY so its stdio streams here.

    Args:
        bundle_id: The app's bundle identifier.

    Returns:
        The launched process, or ``None`` when no simulator is booted.
    """
    udid = _booted_ios_udid()
    if udid is None:
        print("Note: no booted iOS Simulator found; skipping log streaming.")
        return None
    env = {**os.environ, "SIMCTL_CHILD_PYTHONUNBUFFERED": "1"}
    try:
        proc = subprocess.Popen(
            ["xcrun", "simctl", "launch", "--console-pty", "--terminate-running-process", udid, bundle_id],
            env=env,
        )
    except FileNotFoundError:
        print("Note: 'xcrun' not found on PATH; skipping iOS log streaming.")
        return None
    print("Streaming iOS app logs from the simulator (Ctrl+C to stop)...")
    return proc


def _terminate_subprocess(proc: Optional[subprocess.Popen]) -> None:
    """Politely stop a subprocess, escalating to ``SIGKILL`` if needed."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()


# ======================================================================
# Hot-reload overlay cleanup (clears stale dev files before launch)
# ======================================================================


def _ios_data_container(bundle_id: str) -> Optional[str]:
    """Return the booted simulator's app data container, if available."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "get_app_container", "booted", bundle_id, "data"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _clear_android_hot_reload_overlay(app_id: str) -> bool:
    """Remove stale Android hot-reload files before launching."""
    result = subprocess.run(
        ["adb", "shell", "run-as", app_id, "rm", "-rf", f"files/{HOT_RELOAD_DEV_ROOT}"],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def _clear_ios_hot_reload_overlay(bundle_id: str) -> bool:
    """Remove stale iOS Simulator hot-reload files before launching."""
    container = _ios_data_container(bundle_id)
    if container is None:
        return False
    shutil.rmtree(os.path.join(container, "Documents", HOT_RELOAD_DEV_ROOT), ignore_errors=True)
    return True


# ======================================================================
# start (dev server)
# ======================================================================


def start_project(args: argparse.Namespace) -> None:
    """Run the dev server: serve the app over the LAN with live reload.

    Bundles ``app/`` (plus pure-Python requirements), serves it over HTTP,
    prints a scannable QR code, and pushes updates to connected PythonNative
    Go clients on every save. This is the fast inner loop, the Python answer
    to ``expo start``.

    Args:
        args: Parsed namespace (``host``, ``port``, ``no_qr``,
            ``no_requirements``).
    """
    config = _load_config_or_exit()
    host: str = getattr(args, "host", None) or "0.0.0.0"
    port: int = getattr(args, "port", None) or dev_protocol.DEFAULT_PORT

    site_packages: Optional[Path] = None
    if config.requirements and not getattr(args, "no_requirements", False):
        site_packages = _install_dev_requirements(config)

    from ..dev.discovery import lan_ip, server_url
    from ..dev.server import DevServer

    try:
        server = DevServer(
            config.project_root,
            app_name=config.name,
            entry_module=config.entry_module,
            host=host,
            port=port,
            site_packages=site_packages,
            log=print,
        )
    except OSError as exc:
        print(f"Error: couldn't start the dev server on {host}:{port} ({exc}).")
        print("Another `pn start` may already be running; try --port to pick a different port.")
        sys.exit(1)

    url = server_url(lan_ip(), server.port)
    _print_start_banner(url, config.name, qr=not getattr(args, "no_qr", False))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        print("\nStopped dev server.")


def _print_start_banner(url: str, app_name: str, *, qr: bool) -> None:
    print()
    print(f"  PythonNative dev server  -  {app_name}")
    print(f"  {url}")
    print()
    if qr:
        from ..dev.qr import render_qr

        rendered = render_qr(url)
        if rendered:
            print(rendered)
            print()
    print("  Open PythonNative Go on your device and scan the QR code above,")
    print("  or type the URL in by hand. Install the client with `pn go install`.")
    print("  Edit a file under app/ and the device refreshes. Ctrl+C to stop.")
    print()


def _install_dev_requirements(config: AppConfig) -> Optional[Path]:
    """Best-effort: pip-install ``[requirements].packages`` for the bundle.

    Returns the site-packages directory to include in the served bundle, or
    ``None`` if there's nothing to install or the install failed (in which
    case the app is served without its third-party deps and the device shows
    an import error the developer can act on).
    """
    site_dir = config.project_root / "build" / "devserver" / "site-packages"
    try:
        if site_dir.exists():
            shutil.rmtree(site_dir)
        site_dir.mkdir(parents=True, exist_ok=True)
        print(f"Installing requirements for the bundle: {', '.join(config.requirements)}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-t", str(site_dir), *config.requirements],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Note: couldn't install some requirements; serving app sources only.")
            return None
    except OSError:
        return None
    return site_dir


# ======================================================================
# go (PythonNative Go dev client)
# ======================================================================


def _go_client_config(project_root: Path) -> AppConfig:
    """Return the built-in config for the PythonNative Go client app."""
    try:
        from .. import __version__

        version = __version__ if re.match(r"^\d+(\.\d+){0,3}$", __version__) else "1.0.0"
    except Exception:
        version = "1.0.0"
    return AppConfig.from_dict(
        {
            "app": {
                "id": "com.pythonnative.go",
                "name": "PythonNativeGo",
                "display_name": "PythonNative Go",
                "version": version,
                "python_version": "3.11",
                "orientation": "portrait",
            },
        },
        project_root=project_root,
    )


def go_command(args: argparse.Namespace) -> None:
    """Build (and optionally install) the PythonNative Go dev client.

    PythonNative Go is a generic client app that bakes in the framework but no
    user code; it connects to ``pn start`` to download and run any project.
    Build it once per device, then iterate with ``pn start`` alone.

    Args:
        args: Parsed namespace (``action`` of ``build``/``install``,
            ``platform``).
    """
    action: str = args.action
    platform: str = args.platform
    project_root = Path.cwd()
    config = _go_client_config(project_root)
    builder = builder_mod.Builder(config, log=print, build_root=project_root / "build" / "pythonnative-go")

    try:
        prepared = builder.prepare(platform, dev_client=True)
        if platform == "android":
            artifacts = builder.build_android(prepared, debug=True)
        else:
            app_path = builder.build_ios_simulator(prepared)
            artifacts = builder_mod.BuildArtifacts(paths=[app_path])
    except builder_mod.BuildError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if not artifacts.paths:
        print("Build completed, but no PythonNative Go artifact was found. Check the output above.")
        sys.exit(1)

    if action == "build":
        print("\nBuilt PythonNative Go:")
        for path in artifacts.paths:
            print(f"  {path}")
        print("\nInstall it with: pn go install " + platform)
        return

    _go_install(platform, prepared, artifacts)


def _go_install(platform: str, prepared: builder_mod.PreparedProject, artifacts: builder_mod.BuildArtifacts) -> None:
    """Install and launch the freshly built PythonNative Go client."""
    if platform == "android":
        apk = next((p for p in artifacts.paths if p.suffix == ".apk"), None)
        if apk is None:
            print("No APK found to install.")
            sys.exit(1)
        subprocess.run(["adb", "install", "-r", str(apk)], check=False)
        subprocess.run(
            ["adb", "shell", "am", "start", "-n", f"{prepared.app_id}/.MainActivity"],
            check=False,
        )
        print("Installed and launched PythonNative Go. Now run `pn start` in your project.")
        return

    app_path = artifacts.paths[0]
    udid = _select_ios_simulator()
    if udid is None:
        print("No available iOS Simulators found; open the project in Xcode to run.")
        return
    subprocess.run(["xcrun", "simctl", "boot", udid], check=False, capture_output=True)
    subprocess.run(["xcrun", "simctl", "install", udid, str(app_path)], check=False)
    subprocess.run(["xcrun", "simctl", "launch", udid, prepared.app_id], check=False)
    print("Installed and launched PythonNative Go. Now run `pn start` in your project.")


# ======================================================================
# Argument parsing
# ======================================================================


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pn", description="PythonNative CLI")
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser("init", help="Scaffold a new project")
    parser_init.add_argument("name", nargs="?", help="Project name (defaults to current directory name)")
    parser_init.add_argument("--force", action="store_true", help="Overwrite existing files if present")
    parser_init.set_defaults(func=init_project)

    parser_doctor = subparsers.add_parser("doctor", help="Diagnose the local toolchain and config")
    parser_doctor.add_argument("platform", nargs="?", choices=["android", "ios"], help="Restrict checks to a platform")
    parser_doctor.set_defaults(func=doctor_command)

    parser_preview = subparsers.add_parser("preview", help="Render the app in a desktop window")
    parser_preview.add_argument(
        "component",
        nargs="?",
        help="Module path (e.g. app.main) or dotted component path; defaults to the project entry point",
    )
    parser_preview.add_argument("--width", type=int, default=390, help="Initial window width in points (default: 390)")
    parser_preview.add_argument(
        "--height", type=int, default=844, help="Initial window height in points (default: 844)"
    )
    parser_preview.add_argument("--title", default="PythonNative Preview", help="Preview window title")
    parser_preview.add_argument("--no-hot-reload", action="store_true", help="Disable file watching / Fast Refresh")
    parser_preview.set_defaults(func=preview_project)

    parser_start = subparsers.add_parser(
        "start", help="Run the dev server for PythonNative Go (live reload over Wi-Fi)"
    )
    parser_start.add_argument(
        "--port", type=int, default=None, help=f"Port to serve on (default: {dev_protocol.DEFAULT_PORT})"
    )
    parser_start.add_argument("--host", default=None, help="Interface to bind (default: 0.0.0.0, all interfaces)")
    parser_start.add_argument("--no-qr", action="store_true", help="Don't print a QR code, just the URL")
    parser_start.add_argument(
        "--no-requirements", action="store_true", help="Don't bundle [requirements].packages into the served app"
    )
    parser_start.set_defaults(func=start_project)

    parser_go = subparsers.add_parser("go", help="Build/install the PythonNative Go dev client")
    parser_go.add_argument("action", choices=["build", "install"], help="Build the client, or build and install it")
    parser_go.add_argument("platform", choices=["android", "ios"])
    parser_go.set_defaults(func=go_command)

    parser_run = subparsers.add_parser("run", help="Build, install, and launch a standalone build on a device")
    parser_run.add_argument("platform", choices=["android", "ios"])
    parser_run.add_argument("--prepare-only", action="store_true", help="Stage + configure without building")
    parser_run.add_argument("--no-logs", action="store_true", help="Don't stream device logs after launch")
    parser_run.set_defaults(func=run_project)

    parser_build = subparsers.add_parser("build", help="Build distributable artifacts")
    parser_build.add_argument("platform", choices=["android", "ios"])
    parser_build.add_argument("--debug", action="store_true", help="Build the debug variant instead of release")
    parser_build.set_defaults(func=build_project)

    parser_app_id = subparsers.add_parser("app-id", help="Print the resolved application/bundle id")
    parser_app_id.add_argument("platform", choices=["android", "ios"])
    parser_app_id.set_defaults(func=app_id_command)

    parser_clean = subparsers.add_parser("clean", help="Remove the local build/ directory")
    parser_clean.set_defaults(func=clean_project)

    return parser


def main() -> None:
    """Entry point for the ``pn`` console script."""
    parser = _build_parser()
    args = parser.parse_args()
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        sys.exit(1)
    func(args)


if __name__ == "__main__":
    main()
