"""Tests for the dev-server/dev-client wire protocol."""

from pythonnative.dev import protocol


def test_hash_bytes_is_sha256_hex() -> None:
    # Known SHA-256 of b"abc".
    assert protocol.hash_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_is_compatible_matches_exact_version() -> None:
    assert protocol.is_compatible(protocol.PROTOCOL_VERSION) is True
    assert protocol.is_compatible(protocol.PROTOCOL_VERSION + 1) is False
    assert protocol.is_compatible(1, client_protocol=2) is False


def test_file_entry_round_trips() -> None:
    entry = protocol.FileEntry(path="app/main.py", sha256="deadbeef", size=42)
    assert protocol.FileEntry.from_dict(entry.to_dict()) == entry


def test_manifest_json_round_trip_and_index() -> None:
    manifest = protocol.Manifest(
        protocol_version=protocol.PROTOCOL_VERSION,
        sdk_version="1.2.3",
        app_name="Demo",
        entry_module="app.main",
        version="v1",
        files=[
            protocol.FileEntry("app/main.py", "aaa", 1),
            protocol.FileEntry("app/util.py", "bbb", 2),
        ],
    )
    restored = protocol.Manifest.from_json(manifest.to_json())
    assert restored == manifest
    index = restored.by_path()
    assert set(index) == {"app/main.py", "app/util.py"}
    assert index["app/util.py"].sha256 == "bbb"


def test_server_status_identifies_pythonnative() -> None:
    status = protocol.ServerStatus(
        server=protocol.SERVER_NAME,
        protocol_version=protocol.PROTOCOL_VERSION,
        sdk_version="1.0.0",
        app_name="Demo",
        entry_module="app.main",
        version="v1",
    )
    assert status.is_pythonnative() is True
    restored = protocol.ServerStatus.from_json(
        '{"server": "something-else", "protocol_version": 1, "sdk_version": "1.0.0",'
        ' "app_name": "X", "entry_module": "app.main", "version": "v1"}'
    )
    assert restored.is_pythonnative() is False


def test_poll_result_round_trip() -> None:
    import json

    result = protocol.PollResult(version="v9", changed=True)
    assert protocol.PollResult.from_json(json.dumps(result.to_dict())) == result
