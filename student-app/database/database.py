import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "..",
        "Admin-App",
        "database",
        "offline_exam.db"
    )
)


def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn