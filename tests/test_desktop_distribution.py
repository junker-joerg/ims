from contextlib import closing
import json
from pathlib import Path
import socket
import sqlite3
import sys
from types import SimpleNamespace
import zipfile

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from ims.desktop.data import export_diagnostics, import_database
from ims.desktop.instance import InstanceLock
from ims.desktop.launcher import add_controls, bind_loopback
from ims.desktop.paths import resource_root, user_root


def test_frozen_resources_and_user_data_are_separate(monkeypatch, tmp_path):
    bundle = tmp_path / "Programm mit Räumen" / "_internal"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle), raising=False)
    monkeypatch.setattr(sys, "executable", str(bundle.parent / "IMS-Workbench.exe"))
    assert resource_root() == bundle / "resources"
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Nutzerdaten Ä"))
    assert user_root() == tmp_path / "Nutzerdaten Ä" / "IMS" / "Workbench"
    with pytest.raises(ValueError, match="außerhalb"):
        user_root(bundle / "resources" / "data")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows OS lock")
def test_second_start_and_crash_lock_semantics(tmp_path):
    first, second = InstanceLock(tmp_path), InstanceLock(tmp_path)
    assert first.acquire()
    try:
        assert not second.acquire()
    finally:
        first.release()
    assert second.acquire()
    second.release()


def test_port_conflict_and_loopback_binding():
    with socket.socket() as other:
        other.bind(("127.0.0.1", 0))
        other.listen()
        port = other.getsockname()[1]
        with pytest.raises(RuntimeError, match="bereits verwendet"):
            bind_loopback(port)
    with bind_loopback(port) as listener:
        assert listener.getsockname() == ("127.0.0.1", port)


def test_control_requires_instance_token_and_post(monkeypatch):
    app = Starlette()
    server = SimpleNamespace(should_exit=False)
    opened = []
    monkeypatch.setattr("ims.desktop.launcher.webbrowser.open", opened.append)
    add_controls(app, server, "secret", "http://127.0.0.1:8000/")
    client = TestClient(app)
    assert client.get("/_desktop/control").status_code == 405
    assert client.post("/_desktop/control", content="stop").status_code == 403
    assert not server.should_exit
    headers = {"X-IMS-Desktop-Token": "secret"}
    assert client.post("/_desktop/control", content="open", headers=headers).status_code == 200
    assert opened == ["http://127.0.0.1:8000/"]
    assert client.post("/_desktop/control", content="stop", headers=headers).status_code == 200
    assert server.should_exit


def test_explicit_import_includes_wal_and_preserves_previous_database(tmp_path):
    old = tmp_path / "Alte Daten Ä" / "metadata.sqlite"
    old.parent.mkdir()
    root = tmp_path / "new"
    root.mkdir()
    with closing(sqlite3.connect(root / "metadata.sqlite")) as db:
        with db:
            db.execute("CREATE TABLE scenarios(id TEXT)")
            db.execute("INSERT INTO scenarios VALUES ('previous')")
    source = sqlite3.connect(old)
    try:
        source.execute("PRAGMA journal_mode=WAL")
        source.execute("CREATE TABLE scenarios(id TEXT)")
        source.execute("INSERT INTO scenarios VALUES ('adopted')")
        source.commit()
        backup = import_database(old.parent, root)
        for path, expected in [(old, 'adopted'), (root / 'metadata.sqlite', 'adopted'),
                               (backup / 'imported.sqlite', 'adopted'),
                               (backup / 'previous.sqlite', 'previous')]:
            with closing(sqlite3.connect(path)) as db:
                assert db.execute("SELECT id FROM scenarios").fetchone() == (expected,)
    finally:
        source.close()


def test_invalid_import_does_not_replace_existing_data(tmp_path):
    old = tmp_path / "not-ims.sqlite"
    with closing(sqlite3.connect(old)) as db:
        db.execute("CREATE TABLE alien(id TEXT)")
    root = tmp_path / "data"
    root.mkdir()
    target = root / "metadata.sqlite"
    target.write_bytes(b"prior data")
    with pytest.raises(ValueError, match="keine bekannten"):
        import_database(old, root)
    assert target.read_bytes() == b"prior data"


def test_diagnostics_excludes_user_data_and_control_token(tmp_path):
    (tmp_path / 'logs').mkdir()
    (tmp_path / 'logs/desktop.log').write_text('ready')
    (tmp_path / 'metadata.sqlite').write_bytes(b'user data')
    (tmp_path / 'instance.json').write_text('{"token":"secret"}')
    path = export_diagnostics(tmp_path, tmp_path / 'diagnosis.zip', 'alpha')
    with zipfile.ZipFile(path) as archive:
        assert set(archive.namelist()) == {'diagnosis.json', 'logs/desktop.log'}
        assert json.loads(archive.read('diagnosis.json'))['user_data_included'] is False
