from unittest import mock

from dns_api.db import Database
from tinydb import TinyDB


def test_setup_db_tinydb_when_init():
    db = Database()
    assert isinstance(db._db, TinyDB)


def test_called_method_in_db():
    db = Database()
    with mock.patch.object(db, "_db", new_callable=mock.MagicMock) as attr_mock:
        db.all()

        attr_mock.all.assert_called_once()