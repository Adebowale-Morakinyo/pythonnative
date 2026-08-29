import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

import pytest

import pythonnative.cli.pn as pn_cli
import pythonnative.hot_reload as hot_reload_module


def run_pn(args: List[str], cwd: str) -> "subprocess.CompletedProcess[str]":
    cmd = [sys.executable, "-m", "pythonnative.cli.pn"] + args
    return subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)


def test_cli_version(tmp_path: Path) -> None:
    result = run_pn(["--version"], str(tmp_path))

    assert result.returncode == 0
    assert result.stdout.strip().startswith("pn ")


def test_cli_short_version_flag(tmp_path: Path) -> None:
    result = run_pn(["-V"], str(tmp_path))

    assert result.returncode == 0
    assert result.stdout.strip().startswith("pn ")


def test_cli_init_and_clean() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["init", "MyApp"], tmpdir)
        assert result.returncode == 0, result.stderr
        project_dir = os.path.join(tmpdir, "MyApp")
        assert os.path.isdir(os.path.join(project_dir, "app"))

        main_path = os.path.join(project_dir, "app", "main.py")
        assert os.path.isfile(main_path)
        content = Path(main_path).read_text(encoding="utf-8")
        assert "def App(" in content
        assert "Stack.Navigator" in content

        config_path = os.path.join(project_dir, "pythonnative.toml")
        assert os.path.isfile(config_path)
        toml_text = Path(config_path).read_text(encoding="utf-8")
        assert 'id = "com.example.myapp"' in toml_text
        assert os.path.isfile(os.path.join(project_dir, ".gitignore"))
        # The legacy JSON config and requirements.txt are no longer scaffolded.
        assert not os.path.exists(os.path.join(project_dir, "pythonnative.json"))

        # clean on empty build is a no-op
        result = run_pn(["clean"], tmpdir)
        assert result.returncode == 0, result.stderr

        os.makedirs(os.path.join(tmpdir, "build", "android"), exist_ok=True)
        result = run_pn(["clean"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert not os.path.exists(os.path.join(tmpdir, "build"))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_init_refuses_overwrite() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        assert run_pn(["init", "MyApp"], tmpdir).returncode == 0
        result = run_pn(["init", "MyApp"], tmpdir)
        assert result.returncode != 0
        assert "Refusing to overwrite" in result.stdout
        assert run_pn(["init", "MyApp", "--force"], tmpdir).returncode == 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_init_creates_named_directory(tmp_path: Path) -> None:
    result = run_pn(["init", "my_app"], str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "cd my_app" in result.stdout

    project_dir = os.path.join(str(tmp_path), "my_app")
    assert os.path.isfile(os.path.join(project_dir, "app", "main.py"))
    assert os.path.isfile(os.path.join(project_dir, "pythonnative.toml"))
    assert os.path.isfile(os.path.join(project_dir, ".gitignore"))
    toml_text = Path(os.path.join(project_dir, "pythonnative.toml")).read_text(encoding="utf-8")
    assert 'id = "com.example.my_app"' in toml_text
    # Nothing is scaffolded beside the project directory.
    assert os.listdir(str(tmp_path)) == ["my_app"]


def test_cli_init_without_name_uses_cwd(tmp_path: Path) -> None:
    project_dir = tmp_path / "widgets"
    project_dir.mkdir()

    result = run_pn(["init"], str(project_dir))
    assert result.returncode == 0, result.stderr
    assert "cd " not in result.stdout

    assert os.path.isfile(os.path.join(str(project_dir), "app", "main.py"))
    assert os.path.isfile(os.path.join(str(project_dir), ".gitignore"))
    toml_text = Path(os.path.join(str(project_dir), "pythonnative.toml")).read_text(encoding="utf-8")
    assert 'id = "com.example.widgets"' in toml_text
    assert 'name = "widgets"' in toml_text


def test_cli_init_refuses_non_empty_directory(tmp_path: Path) -> None:
    project_dir = tmp_path / "my_app"
    project_dir.mkdir()
    keeper = project_dir / "README.md"
    keeper.write_text("keep me\n", encoding="utf-8")

    result = run_pn(["init", "my_app"], str(tmp_path))
    assert result.returncode != 0
    assert "Refusing to overwrite" in result.stdout
    assert "non-empty directory" in result.stdout
    assert not os.path.exists(os.path.join(str(project_dir), "app"))
    assert keeper.read_text(encoding="utf-8") == "keep me\n"

    result = run_pn(["init", "my_app", "--force"], str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert os.path.isfile(os.path.join(str(project_dir), "app", "main.py"))
    # --force scaffolds over the directory; it doesn't empty it first.
    assert keeper.read_text(encoding="utf-8") == "keep me\n"


def test_cli_init_accepts_existing_empty_directory(tmp_path: Path) -> None:
    project_dir = tmp_path / "my_app"
    project_dir.mkdir()

    result = run_pn(["init", "my_app"], str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert os.path.isfile(os.path.join(str(project_dir), "app", "main.py"))
    assert os.path.isfile(os.path.join(str(project_dir), "pythonnative.toml"))


def test_cli_init_refuses_existing_file(tmp_path: Path) -> None:
    blocker = tmp_path / "my_app"
    blocker.write_text("not a project\n", encoding="utf-8")

    result = run_pn(["init", "my_app"], str(tmp_path))
    assert result.returncode != 0
    assert "Refusing to overwrite existing file" in result.stdout

    # --force can't turn a file into a directory, so it is refused too.
    result = run_pn(["init", "my_app", "--force"], str(tmp_path))
    assert result.returncode != 0
    assert "Refusing to overwrite existing file" in result.stdout
    assert blocker.read_text(encoding="utf-8") == "not a project\n"


@pytest.mark.parametrize("name", ["{absolute}", "nested/my_app", "my_app/", ".", "..", "../", "a/.."])
def test_cli_init_rejects_path_like_names(tmp_path: Path, name: str) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    result = run_pn(["init", name.format(absolute=str(tmp_path / "elsewhere"))], str(work_dir))
    assert result.returncode != 0
    assert "Refusing to" in result.stdout
    assert "project name" in result.stdout
    # Nothing was created in the working directory or anywhere above it.
    assert os.listdir(str(work_dir)) == []
    assert os.listdir(str(tmp_path)) == ["work"]


def test_cli_init_force_does_not_escape_to_parent(tmp_path: Path) -> None:
    parent_config = tmp_path / "pythonnative.toml"
    parent_config.write_text("# hand-written\n", encoding="utf-8")
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    result = run_pn(["init", "..", "--force"], str(work_dir))
    assert result.returncode != 0
    assert "Refusing to" in result.stdout
    # --force does not lift the single-name rule, so the parent is untouched.
    assert parent_config.read_text(encoding="utf-8") == "# hand-written\n"
    assert not os.path.exists(os.path.join(str(tmp_path), "app"))
    assert not os.path.exists(os.path.join(str(tmp_path), ".gitignore"))
    assert os.listdir(str(work_dir)) == []


@pytest.mark.parametrize("extra_args", [[], ["--force"]])
@pytest.mark.parametrize("populated", [True, False])
def test_cli_init_rejects_symlinked_target(tmp_path: Path, populated: bool, extra_args: List[str]) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_config = outside / "pythonnative.toml"
    if populated:
        outside_config.write_text("# hand-written\n", encoding="utf-8")
    before = sorted(os.listdir(str(outside)))

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    os.symlink(str(outside), os.path.join(str(work_dir), "link"))

    result = run_pn(["init", "link"] + extra_args, str(work_dir))
    assert result.returncode != 0
    assert "Refusing to" in result.stdout
    # exists() and is_dir() follow symlinks, so the destination must stay untouched:
    # no new entries, and no rewrite of a config that was already there.
    assert sorted(os.listdir(str(outside))) == before
    if populated:
        assert outside_config.read_text(encoding="utf-8") == "# hand-written\n"
    assert os.listdir(str(work_dir)) == ["link"]


def test_cli_run_help_lists_flags() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["run", "--help"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert "--no-logs" in result.stdout
        assert "--hot-reload" in result.stdout
        assert "--prepare-only" in result.stdout
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_build_help_lists_debug() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["build", "--help"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert "--debug" in result.stdout
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_run_rejects_unknown_flag() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["run", "android", "--does-not-exist"], tmpdir)
        assert result.returncode != 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_run_without_config_errors() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["run", "android"], tmpdir)
        assert result.returncode != 0
        assert "No pythonnative.toml" in (result.stdout + result.stderr)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_app_id_resolves(tmp_path: Path) -> None:
    assert run_pn(["init", "MyApp"], str(tmp_path)).returncode == 0
    project_dir = str(tmp_path / "MyApp")
    result = run_pn(["app-id", "android"], project_dir)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "com.example.myapp"
    assert run_pn(["app-id", "ios"], project_dir).stdout.strip() == "com.example.myapp"


def test_cli_doctor_runs(tmp_path: Path) -> None:
    assert run_pn(["init", "MyApp"], str(tmp_path)).returncode == 0
    result = run_pn(["doctor", "android"], str(tmp_path / "MyApp"))
    assert "PythonNative doctor" in result.stdout
    # android-only doctor on a CI box without adb still produces warnings, not errors.
    assert result.returncode in (0, 1)


def test_cli_run_prepare_only_android_and_ios() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        assert run_pn(["init", "MyApp"], tmpdir).returncode == 0
        project_dir = os.path.join(tmpdir, "MyApp")

        result = run_pn(["run", "android", "--prepare-only", "--no-logs"], project_dir)
        assert result.returncode == 0, result.stderr
        android_root = os.path.join(project_dir, "build", "android", "android_template")
        assert os.path.isdir(android_root)
        # Package relocated to the configured application id.
        relocated = os.path.join(
            android_root, "app", "src", "main", "java", "com", "example", "myapp", "ScreenFragment.kt"
        )
        assert os.path.isfile(relocated)
        assert not os.path.exists(
            os.path.join(android_root, "app", "src", "main", "java", "com", "pythonnative", "android_template")
        )
        # App identity written into the Gradle config.
        gradle = Path(os.path.join(android_root, "app", "build.gradle")).read_text(encoding="utf-8")
        assert "com.example.myapp" in gradle

        result = run_pn(["run", "ios", "--prepare-only", "--no-logs"], project_dir)
        assert result.returncode == 0, result.stderr
        ios_root = os.path.join(project_dir, "build", "ios", "ios_template")
        assert os.path.isdir(ios_root)
        info_plist = Path(os.path.join(ios_root, "ios_template", "Info.plist")).read_bytes()
        assert b"CFBundleDisplayName" in info_plist
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Pure helpers (no device required)
# ---------------------------------------------------------------------------


def test_booted_ios_udid_picks_first_booted_device(monkeypatch: pytest.MonkeyPatch) -> None:
    sample_json = (
        '{"devices": {'
        '"com.apple.CoreSimulator.SimRuntime.iOS-26-4": ['
        '{"name": "iPhone 17 Pro", "state": "Booted", "udid": "abc-123"}'
        "]}}"
    )

    class _StubResult:
        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    def _fake_run(cmd: List[str], **kwargs: object) -> _StubResult:
        assert cmd[:2] == ["xcrun", "simctl"]
        assert "booted" in cmd
        return _StubResult(sample_json)

    monkeypatch.setattr(pn_cli.subprocess, "run", _fake_run)
    assert pn_cli._booted_ios_udid() == "abc-123"


def test_booted_ios_udid_returns_none_when_no_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    class _StubResult:
        stdout = '{"devices": {}}'

    monkeypatch.setattr(pn_cli.subprocess, "run", lambda *a, **kw: _StubResult())
    assert pn_cli._booted_ios_udid() is None


def test_booted_ios_udid_handles_xcrun_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*args: object, **kwargs: object) -> None:
        raise FileNotFoundError("xcrun missing")

    monkeypatch.setattr(pn_cli.subprocess, "run", _raise)
    assert pn_cli._booted_ios_udid() is None


def test_hot_reload_manifest_payload_maps_files_to_modules(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    changed = app_dir / "main.py"
    changed.write_text("print('hi')\n", encoding="utf-8")

    payload = pn_cli._hot_reload_manifest_payload([os.fspath(changed)], os.fspath(tmp_path), version="v1")

    assert payload == {
        "version": "v1",
        "files": ["app/main.py"],
        "modules": ["app.main"],
    }


def test_android_hot_reload_dest_points_to_overlay() -> None:
    assert pn_cli._android_hot_reload_dest("app/main.py") == os.path.join(
        "files",
        "pythonnative_dev",
        "app/main.py",
    )


def test_clear_ios_hot_reload_overlay_removes_stale_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    overlay = tmp_path / "Documents" / "pythonnative_dev"
    overlay.mkdir(parents=True)
    (overlay / "reload.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(pn_cli, "_ios_data_container", lambda bundle_id: os.fspath(tmp_path))

    assert pn_cli._clear_ios_hot_reload_overlay("com.example.app") is True
    assert not overlay.exists()


def test_run_hot_reload_imports_top_level_watcher(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    build_dir = tmp_path / "build"
    events: list[str] = []

    class FakeWatcher:
        def __init__(self, watch_dir: str, on_change: object, interval: float = 1.0) -> None:
            assert watch_dir == os.fspath(app_dir)

        def start(self) -> None:
            events.append("start")

        def stop(self) -> None:
            events.append("stop")

    def stop_loop(_seconds: float) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(hot_reload_module, "FileWatcher", FakeWatcher)
    monkeypatch.setattr("time.sleep", stop_loop)

    pn_cli._run_hot_reload(
        "ios",
        os.fspath(tmp_path),
        os.fspath(build_dir),
        app_id="com.example.app",
        bundle_id="com.example.app",
        show_logs=False,
    )

    assert events == ["start", "stop"]
