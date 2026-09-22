import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        # Database will be created in the project's database folder
        db_folder = os.path.join(os.getcwd(), "database")
        os.makedirs(db_folder, exist_ok=True)

        self.db_path = os.path.join(db_folder, "exam_monitor.db")

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        # ---------------- Students ----------------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            semester TEXT,
            exam_hall TEXT,
            seat_no TEXT,
            photo TEXT
        )
        """)

        # ---------------- Exams ----------------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT,
            subject TEXT,
            exam_date TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER
        )
        """)

        # ---------------- Attendance ----------------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            exam_id INTEGER,
            login_time TEXT,
            status TEXT
        )
        """)

        # ---------------- Violations ----------------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            violation_type TEXT,
            timestamp TEXT,
            screenshot TEXT,
            risk_score INTEGER
        )
        """)

        # ---------------- Reports ----------------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            exam_id INTEGER,
            total_violations INTEGER,
            final_score INTEGER,
            pdf_path TEXT
        )
        """)

        self.connection.commit()

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    db = DatabaseManager()
    print("Database Created Successfully!")
    db.close()