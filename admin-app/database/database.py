import sqlite3
import os


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "offline_exam.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Return a connection to the SQLite database.

    sqlite3.Row allows access like:

        row["name"]

    instead of:

        row[0]
    """

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    # Enable foreign-key support
    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ====================================================
        # STUDENTS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                register_no TEXT UNIQUE NOT NULL,

                name TEXT NOT NULL,

                department TEXT NOT NULL,

                semester TEXT NOT NULL,

                hall TEXT NOT NULL,

                seat TEXT NOT NULL,

                photo TEXT

            )
        """)


        # ====================================================
        # EXAMS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                exam_name TEXT NOT NULL,

                subject_code TEXT NOT NULL,

                subject_name TEXT NOT NULL,

                department TEXT NOT NULL,

                semester TEXT NOT NULL,

                hall TEXT NOT NULL,

                exam_date TEXT NOT NULL,

                start_time TEXT NOT NULL,

                end_time TEXT NOT NULL,

                duration TEXT NOT NULL,

                exam_status TEXT DEFAULT 'Scheduled'

            )
        """)


        # ====================================================
        # VIOLATIONS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                register_no TEXT,

                violation_type TEXT,

                screenshot TEXT,

                date_time TEXT

            )
        """)


        # ====================================================
        # STUDENT ASSIGNMENT
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_assignment(

                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id INTEGER NOT NULL,

                exam_id INTEGER NOT NULL,

                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(exam_id)
                    REFERENCES exams(id)
                    ON DELETE CASCADE,

                UNIQUE(student_id, exam_id)

            )
        """)


        # ====================================================
        # QUESTION CATEGORIES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT UNIQUE NOT NULL

            )
        """)


        # ====================================================
        # QUESTIONS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                question_text TEXT NOT NULL,

                option_a TEXT NOT NULL,

                option_b TEXT NOT NULL,

                option_c TEXT NOT NULL,

                option_d TEXT NOT NULL,

                correct_option TEXT NOT NULL,

                marks REAL NOT NULL DEFAULT 1,

                negative_marks REAL NOT NULL DEFAULT 0,

                category_id INTEGER,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(category_id)
                    REFERENCES categories(id)
                    ON DELETE SET NULL

            )
        """)


        # ====================================================
        # EXAM QUESTIONS
        #
        # Stores the questions selected for each examination.
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_questions(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                exam_id INTEGER NOT NULL,

                question_id INTEGER NOT NULL,

                display_order INTEGER NOT NULL,

                FOREIGN KEY(exam_id)
                    REFERENCES exams(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(question_id)
                    REFERENCES questions(id)
                    ON DELETE CASCADE,

                UNIQUE(exam_id, question_id),

                UNIQUE(exam_id, display_order)

            )
        """)


        # ====================================================
        # EXAM ATTEMPTS
        #
        # One record represents one student's attempt at
        # one examination.
        #
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_attempts(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id INTEGER NOT NULL,

                exam_id INTEGER NOT NULL,

                started_at TEXT,

                submitted_at TEXT,

                status TEXT DEFAULT 'Not Started',

                score REAL DEFAULT 0,

                total_marks REAL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(student_id, exam_id),

                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(exam_id)
                    REFERENCES exams(id)
                    ON DELETE CASCADE

            )
        """)


        # ====================================================
        # STUDENT ANSWERS
        #
        # Stores each answer selected by the student.
        #
        # One question can have only one answer per attempt.
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_answers(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                attempt_id INTEGER NOT NULL,

                question_id INTEGER NOT NULL,

                selected_option TEXT,

                is_correct INTEGER DEFAULT 0,

                marks_awarded REAL DEFAULT 0,

                answered_at TEXT,

                FOREIGN KEY(attempt_id)
                    REFERENCES exam_attempts(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(question_id)
                    REFERENCES questions(id)
                    ON DELETE CASCADE,

                UNIQUE(attempt_id, question_id)

            )
        """)


        # ====================================================
        # MIGRATION: EXAMS
        #
        # Add exam_status if an older database does not have
        # this column.
        # ====================================================

        cursor.execute("""
            PRAGMA table_info(exams)
        """)

        exam_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if "exam_status" not in exam_columns:

            cursor.execute("""
                ALTER TABLE exams

                ADD COLUMN exam_status
                TEXT DEFAULT 'Scheduled'
            """)

            print(
                ">>> Added exam_status to exams."
            )


        # ====================================================
        # MIGRATION: QUESTIONS
        #
        # Add category_id if an older database does not have
        # this column.
        # ====================================================

        cursor.execute("""
            PRAGMA table_info(questions)
        """)

        question_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if "category_id" not in question_columns:

            cursor.execute("""
                ALTER TABLE questions

                ADD COLUMN category_id INTEGER
            """)

            print(
                ">>> Added category_id to questions."
            )


        # ====================================================
        # MIGRATION: QUESTIONS
        #
        # Add created_at if an older questions table does not
        # contain it.
        # ====================================================

        if "created_at" not in question_columns:

            cursor.execute("""
                ALTER TABLE questions

                ADD COLUMN created_at
                TEXT DEFAULT CURRENT_TIMESTAMP
            """)

            print(
                ">>> Added created_at to questions."
            )


        # ====================================================
        # MIGRATION: EXAM ATTEMPTS
        #
        # Older databases may already have exam_attempts but
        # may not contain total_marks or created_at.
        # ====================================================

        cursor.execute("""
            PRAGMA table_info(exam_attempts)
        """)

        attempt_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]


        # ----------------------------------------------------
        # Add total_marks
        # ----------------------------------------------------

        if "total_marks" not in attempt_columns:

            cursor.execute("""
                ALTER TABLE exam_attempts

                ADD COLUMN total_marks
                REAL DEFAULT 0
            """)

            print(
                ">>> Added total_marks to exam_attempts."
            )


        # ----------------------------------------------------
        # Add created_at
        # ----------------------------------------------------

        if "created_at" not in attempt_columns:

            cursor.execute("""
                ALTER TABLE exam_attempts

                ADD COLUMN created_at
                TEXT DEFAULT CURRENT_TIMESTAMP
            """)

            print(
                ">>> Added created_at to exam_attempts."
            )
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_exam_attempts_student_exam
            ON exam_attempts(student_id, exam_id)
        """)


        # ====================================================
        # INDEXES
        # ====================================================

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_student_assignment_student

            ON student_assignment(student_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_student_assignment_exam

            ON student_assignment(exam_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_questions_category

            ON questions(category_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_exam_questions_exam

            ON exam_questions(exam_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_exam_questions_question

            ON exam_questions(question_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_exam_attempts_student

            ON exam_attempts(student_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_exam_attempts_exam

            ON exam_attempts(exam_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_student_answers_attempt

            ON student_answers(attempt_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_student_answers_question

            ON student_answers(question_id)
        """)


        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_violations_register

            ON violations(register_no)
        """)


        # ====================================================
        # COMMIT
        # ====================================================

        conn.commit()

        print(
            ">>> Database tables verified successfully."
        )


    except sqlite3.Error as e:

        conn.rollback()

        print(
            ">>> Database error:"
        )

        print(e)

        raise


    finally:

        conn.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

if __name__ == "__main__":

    create_tables()

    print(
        ">>> Database initialization completed."
    )