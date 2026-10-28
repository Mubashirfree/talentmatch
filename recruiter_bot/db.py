import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH=BASE_DIR/ "recruiter_bot.db"
SCHEMA_PATH =Path(__file__).resolve().parent / "schema.sql"

def get_db_path()->Path:
    """Use the RECRUITER_BOT_DB environment variable if set(
    test use this to point  at a throwaway database),otherwise the normal file."""
    return Path(os.environ.get("RECRUITER_BOT_DB",DEFAULT_DB_PATH))

def get_connection()->sqlite3.Connection:
    #Open  a connection whose rows behave like dicts (row["name"])
    conn=sqlite3.connect(get_db_path(),check_same_thread=False)
    conn.row_factory=sqlite3.Row
    #SQlite ignore foreign key unless you switch them on per connection.
    conn.execute("PRAGMA  foreign_keys=ON")
    return conn
