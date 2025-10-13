import argparse
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from importlib import resources
from typing import Any, Dict, List, Optional


def init_project(args: argparse.Namespace) -> None:
    """
    Initialize a new PythonNative project.
    Creates `app/`, `pythonnative.json`, `requirements.txt`, `.gitignore`.
    """
    project_name: str = getattr(args, "name", None) or os.path.basename(os.getcwd())
    cwd: str = os.getcwd()

    app_dir = os.path.join(cwd, "app")
    config_path = os.path.join(cwd, "pythonnative.json")
    requirements_path = os.path.join(cwd, "requirements.txt")
    gitignore_path = os.path.join(cwd, ".gitignore")

    # Prevent accidental overwrite unless --force is provided
    if not getattr(args, "force", False):
        exists = []
        if os.path.exists(app_dir):
            exists.append("app/")
        if os.path.exists(config_path):
            exists.append("pythonnative.json")
        if os.path.exists(requirements_path):
            exists.append("requirements.txt")
        if os.path.exists(gitignore_path):
            exists.append(".gitignore")
        if exists:
            print(f"Refusing to overwrite existing: {', '.join(exists)}. Use --force to overwrite.")
            sys.exit(1)

    os.makedirs(app_dir, exist_ok=True)

    # Minimal hello world app scaffold
    main_page_py = os.path.join(app_dir, "main_page.py")
    if not os.path.exists(main_page_py) or args.force:
        with open(main_page_py, "w", encoding="utf-8") as f:
            f.write(
                """import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("Hello from PythonNative!"))
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Button clicked"))
        stack.add_view(button)
        self.set_root_view(stack)


def bootstrap(native_instance):
    '''Entry point called by the host app (Android Activity or iOS ViewController).'''
    page = MainPage(native_instance)
    page.on_create()
    return page
"""
            )

    # Create config
    config = {
        "name": project_name,
        "appId": "com.example." + project_name.replace(" ", "").lower(),
        "entryPoint": "app/main_page.py",
        "ios": {},
        "android": {},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # Requirements
    if not os.path.exists(requirements_path) or args.force:
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write("pythonnative\n")

    # .gitignore
    default_gitignore = "# PythonNative\n" "__pycache__/\n" "*.pyc\n" ".venv/\n" "build/\n" ".DS_Store\n"
    if not os.path.exists(gitignore_path) or args.force:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(default_gitignore)

    print("Initialized PythonNative project.")


def _extract_zip_to_destination(zip_path: str, destination: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destination)


def _extract_bundled_template(zip_name: str, destination: str) -> None:
    """
    Extract a bundled template zip into the destination directory.
    Tries package resources first; falls back to repo root `templates/` at dev time.
    """
    # Dev-first: prefer repository templates if running from a checkout (avoid stale packaged zips)
    try:
        # __file__ -> src/pythonnative/cli/pn.py, so go up to src/, then to repo root
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        repo_root = os.path.abspath(os.path.join(src_dir, ".."))
        repo_templates = os.path.join(repo_root, "templates")
        candidate = os.path.join(repo_templates, zip_name)
        if os.path.exists(candidate):
            _extract_zip_to_destination(candidate, destination)
            return
    except Exception:
        pass

    # Try to load from installed package resources next (if templates are packaged inside the module)
    try:
        cand = resources.files("pythonnative").joinpath("templates").joinpath(zip_name)
        with resources.as_file(cand) as p:
            resource_path = str(p)
            if os.path.exists(resource_path):
                _extract_zip_to_destination(resource_path, destination)
                return
    except Exception:
        # Not packaged inside the module; try data-files installation locations next
        pass

    # Try sysconfig data dir (where data-files are typically installed)
    try:
        data_dir = sysconfig.get_paths().get("data")
        if data_dir:
            candidate = os.path.join(data_dir, "pythonnative", "templates", zip_name)
            if os.path.exists(candidate):
                _extract_zip_to_destination(candidate, destination)
                return
    except Exception:
        pass

    # Try site-packages purelib/platlib (some environments place data files here)
    try:
        purelib = sysconfig.get_paths().get("purelib")
        platlib = sysconfig.get_paths().get("platlib")
        for base in filter(None, [purelib, platlib]):
            candidate = os.path.join(base, "pythonnative", "templates", zip_name)
            if os.path.exists(candidate):
                _extract_zip_to_destination(candidate, destination)
                return
    except Exception:
        pass

    raise FileNotFoundError(f"Could not find bundled template {zip_name}. Ensure templates are packaged.")


def create_android_project(project_name: str, destination: str) -> None:
    """
    Create a new Android project using a template.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    """
    # Extract the Android template project from bundled zip
    _extract_bundled_template("android_template.zip", destination)


def create_ios_project(project_name: str, destination: str) -> None:
    """
    Create a new iOS project using a template.

    :param project_name: The name of the project.
    :param destination: The directory where the project will be created.
    """
    # Extract the iOS template project from bundled zip
    _extract_bundled_template("ios_template.zip", destination)


def run_project(args: argparse.Namespace) -> None:
    """
    Run the specified project.
    """
    # Determine the platform
    platform: str = args.platform
    prepare_only: bool = getattr(args, "prepare_only", False)

    # Define the build directory
    build_dir: str = os.path.join(os.getcwd(), "build", platform)

    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)

    # Generate the required project files
    if platform == "android":
        create_android_project("MyApp", build_dir)
    elif platform == "ios":
        create_ios_project("MyApp", build_dir)

    # Copy the user's Python code into the project
    src_dir: str = os.path.join(os.getcwd(), "app")

    # Adjust the destination directory for Android project
    if platform == "android":
        dest_dir: str = os.path.join(build_dir, "android_template", "app", "src", "main", "python", "app")
    else:
        # For iOS, stage the Python app in a top-level folder for later integration scripts
        dest_dir = os.path.join(build_dir, "app")

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)

    # During local development (running from repository), also bundle the
    # local library sources so the app uses the in-repo version instead of
    # the PyPI package. This provides faster inner-loop iteration and avoids
    # version skew during development.
    try:
        # __file__ -> src/pythonnative/cli/pn.py, so repo root is one up from src/
        src_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".."))
        local_lib = os.path.join(src_root, "pythonnative")
        if os.path.isdir(local_lib):
            if platform == "android":
                python_root = os.path.join(build_dir, "android_template", "app", "src", "main", "python")
            else:
                python_root = os.path.join(build_dir)  # staged at build/ios/app for iOS below
            os.makedirs(python_root, exist_ok=True)
            shutil.copytree(local_lib, os.path.join(python_root, "pythonnative"), dirs_exist_ok=True)
    except Exception:
        # Non-fatal; fallback to the packaged PyPI dependency if present
        pass

    # Install any necessary Python packages into the project environment
    # Skip installation during prepare-only to avoid network access and speed up scaffolding
    if not prepare_only:
        requirements_path = os.path.join(os.getcwd(), "requirements.txt")
        if os.path.exists(requirements_path):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=False)

    # Run the project
    if prepare_only:
        print("Prepared project in build/ without building (prepare-only).")
        return

    if platform == "android":
        # Change to the Android project directory
        android_project_dir: str = os.path.join(build_dir, "android_template")
        os.chdir(android_project_dir)

        # Add executable permissions to the gradlew script
        gradlew_path: str = os.path.join(android_project_dir, "gradlew")
        os.chmod(gradlew_path, 0o755)  # this makes the file executable for the user

        # Build the Android project and install it on the device
        env: dict[str, str] = os.environ.copy()
        # Respect JAVA_HOME if set; otherwise, attempt a best-effort on macOS via Homebrew
        if sys.platform == "darwin" and not env.get("JAVA_HOME"):
            try:
                jdk_path: str = subprocess.check_output(["brew", "--prefix", "openjdk@17"]).decode().strip()
                env["JAVA_HOME"] = jdk_path
            except Exception:
                pass
        subprocess.run(["./gradlew", "installDebug"], check=True, env=env)

        # Run the Android app
        # Assumes that the package name of your app is "com.example.myapp" and the main activity is "MainActivity"
        # Replace "com.example.myapp" and ".MainActivity" with your actual package name and main activity
        subprocess.run(
            [
                "adb",
                "shell",
                "am",
                "start",
                "-n",
                "com.pythonnative.android_template/.MainActivity",
            ],
            check=True,
        )
    elif platform == "ios":
        # Attempt to build and run on iOS Simulator (best-effort)
        ios_project_dir: str = os.path.join(build_dir, "ios_template")
        if os.path.isdir(ios_project_dir):
            os.chdir(ios_project_dir)
            derived_data = os.path.join(ios_project_dir, "build")
            try:
                # Detect a simulator UDID to target: prefer Booted; else any iPhone
                sim_udid: Optional[str] = None
                try:
                    import json as _json

                    devices_out = subprocess.run(
                        ["xcrun", "simctl", "list", "devices", "available", "--json"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    devs = _json.loads(devices_out.stdout or "{}").get("devices") or {}
                    all_devs = [d for lst in devs.values() for d in (lst or [])]
                    for d in all_devs:
                        if d.get("state") == "Booted":
                            sim_udid = d.get("udid")
                            break
                    if not sim_udid:
                        for d in all_devs:
                            if (d.get("isAvailable") or d.get("availability")) and (
                                d.get("name") or ""
                            ).lower().startswith("iphone"):
                                sim_udid = d.get("udid")
                                break
                except Exception:
                    pass

                xcode_dest = (
                    ["-destination", f"id={sim_udid}"] if sim_udid else ["-destination", "platform=iOS Simulator"]
                )

                subprocess.run(
                    [
                        "xcodebuild",
                        "-project",
                        "ios_template.xcodeproj",
                        "-scheme",
                        "ios_template",
                        "-configuration",
                        "Debug",
                        *xcode_dest,
                        "-derivedDataPath",
                        derived_data,
                        "build",
                    ],
                    check=False,
                )
            except FileNotFoundError:
                print("xcodebuild not found. Skipping iOS build step.")
                return

            # Locate built app
            app_path = os.path.join(derived_data, "Build", "Products", "Debug-iphonesimulator", "ios_template.app")
            if not os.path.isdir(app_path):
                print("Could not locate built .app; open the project in Xcode to run.")
                return

            # Copy staged Python app into the .app bundle so PythonKit can import it
            try:
                staged_app_src = os.path.join(build_dir, "app")
                if os.path.isdir(staged_app_src):
                    shutil.copytree(staged_app_src, os.path.join(app_path, "app"), dirs_exist_ok=True)
                # Also copy local library sources if present for dev flow
                src_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".."))
                local_lib = os.path.join(src_root, "pythonnative")
                if os.path.isdir(local_lib):
                    shutil.copytree(local_lib, os.path.join(app_path, "pythonnative"), dirs_exist_ok=True)
            except Exception:
                # Non-fatal; fallback UI will appear if import fails
                pass

            # Find an available simulator and boot it
            try:
                import json as _json

                result = subprocess.run(
                    ["xcrun", "simctl", "list", "devices", "available", "--json"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                devices_json = _json.loads(result.stdout or "{}")
                all_devices: List[Dict[str, Any]] = []
                for _runtime, devices in (devices_json.get("devices") or {}).items():
                    all_devices.extend(devices or [])
                # Prefer iPhone 15/15 Pro names; else first available iPhone
                preferred = None
                for d in all_devices:
                    name = (d.get("name") or "").lower()
                    if "iphone 15" in name and d.get("isAvailable"):
                        preferred = d
                        break
                if not preferred:
                    for d in all_devices:
                        if d.get("isAvailable") and (d.get("name") or "").lower().startswith("iphone"):
                            preferred = d
                            break
                if not preferred:
                    print("No available iOS Simulators found; open the project in Xcode to run.")
                    return

                udid = preferred.get("udid")
                # Boot (no-op if already booted)
                subprocess.run(["xcrun", "simctl", "boot", udid], check=False)
                # Install and launch
                subprocess.run(["xcrun", "simctl", "install", udid, app_path], check=False)
                subprocess.run(["xcrun", "simctl", "launch", udid, "com.pythonnative.ios-template"], check=False)
                print("Launched iOS app on Simulator (best-effort).")
            except Exception:
                print("Failed to auto-run on Simulator; open the project in Xcode to run.")


def clean_project(args: argparse.Namespace) -> None:
    """
    Clean the specified project.
    """
    # Define the build directory
    build_dir: str = os.path.join(os.getcwd(), "build")

    # Check if the build directory exists
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("Removed build/ directory.")
    else:
        print("No build/ directory to remove.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="pn", description="PythonNative CLI")
    subparsers = parser.add_subparsers()

    # Create a new command 'init' that calls init_project
    parser_init = subparsers.add_parser("init")
    parser_init.add_argument("name", nargs="?", help="Project name (defaults to current directory name)")
    parser_init.add_argument("--force", action="store_true", help="Overwrite existing files if present")
    parser_init.set_defaults(func=init_project)

    # Create a new command 'run' that calls run_project
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("platform", choices=["android", "ios"])
    parser_run.add_argument(
        "--prepare-only",
        action="store_true",
        help="Extract templates and stage app without building",
    )
    parser_run.set_defaults(func=run_project)

    # Create a new command 'clean' that calls clean_project
    parser_clean = subparsers.add_parser("clean")
    parser_clean.set_defaults(func=clean_project)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
