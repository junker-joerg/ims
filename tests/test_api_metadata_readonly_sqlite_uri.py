import sqlite3
from pathlib import Path

from ims.api.metadata_import_cli import _readonly_sqlite_uri
from ims.api.metadata_repository import initialize_metadata_schema, seed_metadata
from ims.api.sqlite_readonly import _sqlite_file_uses_wal


def test_metadata_readonly_uri_keeps_rollback_database_mutable_safe(tmp_path):
    db_path = tmp_path / "workbench.sqlite"
    _create_seeded_sqlite_database(db_path)

    uri = _readonly_sqlite_uri(db_path)

    assert uri == f"{db_path.as_uri()}?mode=ro"
    assert "immutable=1" not in uri
    assert not Path(f"{db_path}-wal").exists()
    assert not Path(f"{db_path}-shm").exists()


def test_metadata_readonly_uri_uses_immutable_for_sidecar_free_wal_database(tmp_path):
    db_path = tmp_path / "workbench.sqlite"
    wal_path = Path(f"{db_path}-wal")
    shm_path = Path(f"{db_path}-shm")
    connection = _create_seeded_wal_database_with_open_writer(db_path)
    try:
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        connection.close()
    wal_path.unlink(missing_ok=True)
    shm_path.unlink(missing_ok=True)

    uri = _readonly_sqlite_uri(db_path)

    assert uri == f"{db_path.as_uri()}?mode=ro&immutable=1"
    assert not wal_path.exists()
    assert not shm_path.exists()


def test_metadata_wal_detection_reads_only_sqlite_header_bytes():
    db_path = _HeaderOnlyPath(b"SQLite format 3\x00\x00\x00\x02\x02" + (b"x" * 1024))

    assert _sqlite_file_uses_wal(db_path) is True
    assert db_path.read_sizes == [20]


class _HeaderOnlyPath:
    def __init__(self, payload):
        self.payload = payload
        self.read_sizes = []

    def open(self, mode):
        assert mode == "rb"
        return _HeaderOnlyFile(self)


class _HeaderOnlyFile:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size=-1):
        self.path.read_sizes.append(size)
        return self.path.payload[:size]


def _create_seeded_sqlite_database(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    connection.close()


def _create_seeded_wal_database_with_open_writer(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL").fetchone()
    initialize_metadata_schema(connection)
    seed_metadata(connection)
    connection.commit()
    return connection
