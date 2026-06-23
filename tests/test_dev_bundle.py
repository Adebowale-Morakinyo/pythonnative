"""Tests for the project bundler that feeds the dev server."""

import io
import zipfile
from pathlib import Path

from pythonnative.dev import bundle as bundle_mod
from pythonnative.dev.protocol import PROTOCOL_VERSION


def _make_project(root: Path) -> None:
    app = root / "app"
    app.mkdir()
    (app / "main.py").write_text("App = 1\n", encoding="utf-8")
    (app / "util.py").write_text("VALUE = 2\n", encoding="utf-8")
    # Things that must be ignored.
    (app / "main.pyc").write_text("junk", encoding="utf-8")
    cache = app / "__pycache__"
    cache.mkdir()
    (cache / "main.cpython-311.pyc").write_text("junk", encoding="utf-8")
    (app / ".DS_Store").write_text("junk", encoding="utf-8")


def test_build_bundle_collects_app_files_only(tmp_path: Path) -> None:
    _make_project(tmp_path)
    bundle = bundle_mod.build_bundle(
        tmp_path,
        app_name="Demo",
        entry_module="app.main",
        sdk_version="1.0.0",
        version="v1",
    )
    assert set(bundle.files) == {"app/main.py", "app/util.py"}
    assert bundle.read("app/main.py") == b"App = 1\n"


def test_manifest_has_hashes_sizes_and_metadata(tmp_path: Path) -> None:
    _make_project(tmp_path)
    bundle = bundle_mod.build_bundle(
        tmp_path,
        app_name="Demo",
        entry_module="app.main",
        sdk_version="9.9.9",
        version="v1",
    )
    manifest = bundle.manifest()
    assert manifest.protocol_version == PROTOCOL_VERSION
    assert manifest.sdk_version == "9.9.9"
    assert manifest.app_name == "Demo"
    assert manifest.entry_module == "app.main"
    assert manifest.version == "v1"
    by_path = manifest.by_path()
    assert by_path["app/main.py"].size == len(b"App = 1\n")
    assert len(by_path["app/main.py"].sha256) == 64


def test_site_packages_included_under_prefix(tmp_path: Path) -> None:
    _make_project(tmp_path)
    site = tmp_path / "site"
    (site / "humanize").mkdir(parents=True)
    (site / "humanize" / "__init__.py").write_text("# pkg\n", encoding="utf-8")
    bundle = bundle_mod.build_bundle(
        tmp_path,
        app_name="Demo",
        entry_module="app.main",
        sdk_version="1.0.0",
        site_packages=site,
    )
    assert "site-packages/humanize/__init__.py" in bundle.files


def test_zip_bytes_round_trips(tmp_path: Path) -> None:
    _make_project(tmp_path)
    bundle = bundle_mod.build_bundle(
        tmp_path,
        app_name="Demo",
        entry_module="app.main",
        sdk_version="1.0.0",
    )
    with zipfile.ZipFile(io.BytesIO(bundle.zip_bytes())) as archive:
        names = set(archive.namelist())
        assert names == {"app/main.py", "app/util.py"}
        assert archive.read("app/util.py") == b"VALUE = 2\n"


def test_new_version_is_monotonic() -> None:
    first = bundle_mod.new_version()
    second = bundle_mod.new_version()
    assert second >= first
    assert first.isdigit()
