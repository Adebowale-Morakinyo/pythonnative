import os
import shutil
import subprocess
import sys
import tempfile
from typing import List


def run_pn(args: List[str], cwd: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "pythonnative.cli.pn"] + args
    return subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)


def test_cli_init_and_clean() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        # init
        result = run_pn(["init", "MyApp"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert os.path.isdir(os.path.join(tmpdir, "app"))
        # scaffolded entrypoint
        main_page_path = os.path.join(tmpdir, "app", "main_page.py")
        assert os.path.isfile(main_page_path)
        with open(main_page_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def MainPage(" in content
        assert os.path.isfile(os.path.join(tmpdir, "pythonnative.json"))
        assert os.path.isfile(os.path.join(tmpdir, "requirements.txt"))
        assert os.path.isfile(os.path.join(tmpdir, ".gitignore"))

        # clean (on empty build should be no-op)
        result = run_pn(["clean"], tmpdir)
        assert result.returncode == 0, result.stderr

        # create build dir and ensure clean removes it
        os.makedirs(os.path.join(tmpdir, "build", "android"), exist_ok=True)
        result = run_pn(["clean"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert not os.path.exists(os.path.join(tmpdir, "build"))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_run_help_lists_logging_flags() -> None:
    """`pn run --help` should advertise both --no-logs and --hot-reload."""
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["run", "--help"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert "--no-logs" in result.stdout
        assert "--hot-reload" in result.stdout
        assert "--prepare-only" in result.stdout
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_run_rejects_unknown_flag() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        result = run_pn(["run", "android", "--does-not-exist"], tmpdir)
        assert result.returncode != 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_cli_run_prepare_only_android_and_ios() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pn_cli_test_")
    try:
        # init to create app scaffold
        result = run_pn(["init", "MyApp"], tmpdir)
        assert result.returncode == 0, result.stderr

        # prepare-only android, combined with --no-logs to verify both flags
        # coexist without launching any adb/simctl subprocess (prepare-only
        # returns before logcat would ever be spawned).
        result = run_pn(["run", "android", "--prepare-only", "--no-logs"], tmpdir)
        assert result.returncode == 0, result.stderr
        android_root = os.path.join(tmpdir, "build", "android", "android_template")
        assert os.path.isdir(android_root)
        # Ensure new Fragment-based navigation exists
        page_fragment = os.path.join(
            android_root,
            "app",
            "src",
            "main",
            "java",
            "com",
            "pythonnative",
            "android_template",
            "PageFragment.kt",
        )
        assert os.path.isfile(page_fragment)
        nav_graph = os.path.join(
            android_root,
            "app",
            "src",
            "main",
            "res",
            "navigation",
            "nav_graph.xml",
        )
        assert os.path.isfile(nav_graph)

        # prepare-only ios with --no-logs
        result = run_pn(["run", "ios", "--prepare-only", "--no-logs"], tmpdir)
        assert result.returncode == 0, result.stderr
        assert os.path.isdir(os.path.join(tmpdir, "build", "ios", "ios_template"))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
