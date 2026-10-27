"""Focused tests for offline CSV parsing and atomic question import."""

import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from import_questions import (
    GEMINI_KEY_ERROR, commit_questions, get_gemini_api_key,
    parse_csv, parse_pdf_with_gemini,
)


def draft(question="Question 1"):
    return {
        "question": question,
        "option_a": "A text",
        "option_b": "B text",
        "option_c": "C text",
        "option_d": "D text",
        "correct_option": "B",
        "marks": "1.0",
        "negative_marks": "0.0",
    }


class QuestionImportTests(unittest.TestCase):

    def test_configured_key_prefers_environment(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "environment-test-key"}):
            self.assertEqual(get_gemini_api_key(), "environment-test-key")

    def test_missing_key_reports_configuration_error(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}), \
                mock.patch("import_questions.Path") as config_path:
            config_path.return_value.with_name.return_value.read_text.side_effect = FileNotFoundError()
            self.assertEqual(get_gemini_api_key(), "")
            with self.assertRaisesRegex(ValueError, "Gemini API key not found"):
                parse_pdf_with_gemini("unused.pdf", api_key="")

    def test_csv_aliases_and_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "questions.csv")
            with open(path, "w", encoding="utf-8", newline="") as output:
                output.write("Question Prompt,Opt A,Option B,Choice C,D,Correct Answer\n")
                output.write("What is 2+2?,3,4,5,6,Option B\n")
            rows = parse_csv(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["correct_option"], "B")
        self.assertEqual(rows[0]["marks"], "1.0")
        self.assertEqual(rows[0]["negative_marks"], "0.0")

    def test_csv_requires_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "questions.csv")
            with open(path, "w", encoding="utf-8", newline="") as output:
                output.write("question,answer\nWhat?,A\n")
            with self.assertRaisesRegex(ValueError, "Missing CSV columns"):
                parse_csv(path)

    def _database(self, path):
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        connection.execute("INSERT INTO categories VALUES (1, 'Physics')")
        connection.execute("""CREATE TABLE questions (
            category_id INTEGER NOT NULL, question_text TEXT NOT NULL
                CHECK (question_text <> 'BAD'), option_a TEXT NOT NULL,
            option_b TEXT NOT NULL, option_c TEXT NOT NULL, option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL, marks REAL NOT NULL,
            negative_marks REAL NOT NULL)""")
        connection.commit()
        connection.close()

    def test_atomic_commit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "exam.db")
            self._database(path)
            factory = lambda: sqlite3.connect(path)
            count, category = commit_questions(1, [(1, draft()), (2, draft("Question 2"))], factory)
            self.assertEqual((count, category), (2, "Physics"))
            connection = factory()
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0], 2)
            connection.close()

    def test_constraint_failure_rolls_back_every_row(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "exam.db")
            self._database(path)
            factory = lambda: sqlite3.connect(path)
            with self.assertRaises(sqlite3.IntegrityError):
                commit_questions(1, [(1, draft()), (2, draft("BAD"))], factory)
            connection = factory()
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0], 0)
            connection.close()

    def test_pdf_json_is_staged_without_a_database_write(self):
        try:
            import pypdf
            import google.generativeai as genai
        except ImportError:
            self.skipTest("PDF and Gemini dependencies are not installed")
        page = mock.Mock()
        page.extract_text.return_value = "1. What is 2 + 2? A. 3 B. 4 C. 5 D. 6 Answer: B"
        response = mock.Mock()
        response.text = ('[{"question":"What is 2 + 2?","option_a":"3",'
                         '"option_b":"4","option_c":"5","option_d":"6",'
                         '"correct_option":"B","marks":1.0,"negative_marks":0.0}]')
        model = mock.Mock()
        model.generate_content.return_value = response
        progress = []
        with mock.patch.object(pypdf, "PdfReader") as reader, \
                mock.patch.object(genai, "GenerativeModel", return_value=model), \
                mock.patch.object(genai, "configure"):
            reader.return_value.pages = [page]
            rows = parse_pdf_with_gemini("unused.pdf", "test-key", progress=lambda a, b: progress.append((a, b)))
        self.assertEqual(rows[0]["correct_option"], "B")
        self.assertEqual(progress[-1], (1, 1))
        self.assertEqual(model.generate_content.call_count, 1)


if __name__ == "__main__":
    unittest.main()
