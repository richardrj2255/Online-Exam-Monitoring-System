import sqlite3

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QTextEdit,
    QFrame,
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from database.database import get_connection
from models.result_model import ResultModel

from ui.qss_theme import (
    BG_CANVAS,
    BG_CARD,
    BG_CARD_ALT,
    BORDER_SUBTLE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BADGE_SUCCESS_BG,
    BADGE_SUCCESS_TEXT,
    BADGE_SUCCESS_BORDER,
    BADGE_WARNING_BG,
    BADGE_WARNING_TEXT,
    BADGE_WARNING_BORDER,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER,
    create_badge_widget,
)


class AdminResultsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.all_results = []

        self.setupUI()
        self.load_exams()
        self.load_results()

    # ========================================================
    # STAT CARD BUILDER
    # ========================================================

    def _create_stat_card(self, title_text, label_widget, accent_color="#6366F1"):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        headerLbl = QLabel(title_text)
        headerLbl.setObjectName("kpiTitle")

        label_widget.setObjectName("kpiValue")
        label_widget.setFont(QFont("Segoe UI", 14, QFont.Bold))

        layout.addWidget(headerLbl)
        layout.addWidget(label_widget)
        return card

    # ========================================================
    # UI
    # ========================================================

    def setupUI(self):

        self.setObjectName("pageWidget")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # ====================================================
        # HEADER CARD
        # ====================================================

        headerCard = QFrame()
        headerCard.setObjectName("headerCard")
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("📊 Examination Performance & Results Analytics")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Analyze examinee scores, grading distributions, and submission audits.")
        subtitle.setObjectName("pageSubtitle")

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        main_layout.addWidget(headerCard)

        # ====================================================
        # STATISTICS CARDS
        # ====================================================

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.total_label = QLabel("Total: 0")
        self.submitted_label = QLabel("Submitted: 0")
        self.progress_label = QLabel("In Progress: 0")
        self.highest_label = QLabel("Highest: 0.00")
        self.lowest_label = QLabel("Lowest: 0.00")
        self.average_label = QLabel("Average: 0.00")

        card1 = self._create_stat_card("TOTAL ATTEMPTS", self.total_label, "#38BDF8")
        card2 = self._create_stat_card("SUBMITTED", self.submitted_label, "#34D399")
        card3 = self._create_stat_card("IN PROGRESS", self.progress_label, "#FBBF24")
        card4 = self._create_stat_card("HIGHEST SCORE", self.highest_label, "#A78BFA")
        card5 = self._create_stat_card("LOWEST SCORE", self.lowest_label, "#F87171")
        card6 = self._create_stat_card("AVERAGE SCORE", self.average_label, "#6366F1")

        for card in [card1, card2, card3, card4, card5, card6]:
            stats_layout.addWidget(card)

        main_layout.addLayout(stats_layout)

        # ====================================================
        # FILTER BAR
        # ====================================================

        filterCard = QFrame()
        filterCard.setObjectName("card")
        filter_layout = QHBoxLayout(filterCard)
        filter_layout.setContentsMargins(14, 10, 14, 10)
        filter_layout.setSpacing(12)

        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumHeight(40)
        self.exam_combo.currentIndexChanged.connect(self.exam_changed)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Filter by student name or register number...")
        self.search.setMinimumHeight(40)
        self.search.textChanged.connect(self.search_results)

        refresh_btn = QPushButton("⟳ Refresh Results")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.refresh_results)

        filter_layout.addWidget(self.exam_combo, 2)
        filter_layout.addWidget(self.search, 3)
        filter_layout.addWidget(refresh_btn)

        main_layout.addWidget(filterCard)

        # ====================================================
        # RESULT TABLE
        # ====================================================

        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        tableLayout = QVBoxLayout(tableCard)
        tableLayout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ATTEMPT ID",
            "REGISTER NO",
            "STUDENT NAME",
            "DEPARTMENT",
            "SEMESTER",
            "SCORE",
            "TOTAL MARKS",
            "PERCENTAGE",
            "STATUS",
            "ACTION",
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 130)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 140)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setShowGrid(False)

        tableLayout.addWidget(self.table)
        main_layout.addWidget(tableCard)

        self.setLayout(main_layout)

    # ========================================================
    # LOAD EXAMS
    # ========================================================

    def load_exams(self):

        self.exam_combo.blockSignals(True)
        self.exam_combo.clear()
        self.exam_combo.addItem("All Examinations", None)

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                SELECT
                    id,
                    exam_name,
                    subject_code,
                    subject_name,
                    exam_date
                FROM exams
                ORDER BY exam_date DESC, id DESC
            """)

            exams = cursor.fetchall()

            for exam in exams:
                display_text = (
                    f"{exam['exam_name']} - "
                    f"{exam['subject_code']} - "
                    f"{exam['exam_date']}"
                )
                self.exam_combo.addItem(display_text, exam["id"])

        except sqlite3.Error as e:
            print("Error loading exams:", e)
        finally:
            conn.close()
            self.exam_combo.blockSignals(False)

    # ========================================================
    # LOAD RESULTS
    # ========================================================

    def load_results(self):

        exam_id = self.exam_combo.currentData()

        if exam_id is None:
            results = ResultModel.get_all_results()
        else:
            results = ResultModel.get_exam_results(exam_id)

        self.all_results = results
        self.display_results(results)
        self.load_statistics(exam_id)

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    def display_results(self, results):

        self.table.setRowCount(len(results))

        for row, result in enumerate(results):

            attempt_id = result["attempt_id"]
            score = float(result["score"] or 0)
            total_marks = float(result["total_marks"] or 0)

            if total_marks > 0:
                percentage = (score / total_marks) * 100
            else:
                percentage = 0

            status_str = str(result["status"] or "PENDING")

            values = [
                str(attempt_id),
                str(result["register_no"] or ""),
                str(result["student_name"] or ""),
                str(result["department"] or ""),
                str(result["semester"] or ""),
                f"{score:.2f}",
                f"{total_marks:.2f}",
                f"{percentage:.2f}%",
                status_str
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)

                if column in [0, 5, 6, 7]:
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))

                self.table.setItem(row, column, item)

            # Status pill badge in column 8
            if status_str.upper() == "SUBMITTED":
                badge = create_badge_widget("SUBMITTED", "success")
            elif status_str.upper() == "IN_PROGRESS":
                badge = create_badge_widget("IN PROGRESS", "amber")
            else:
                badge = create_badge_widget(status_str, "neutral")

            self.table.setCellWidget(row, 8, badge)

            # ------------------------------------------------
            # VIEW BUTTON
            # ------------------------------------------------
            view_btn = QPushButton("👁 View Result")
            view_btn.setObjectName("secondaryBtn")
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setMinimumHeight(32)
            view_btn.clicked.connect(
                lambda checked, aid=attempt_id: self.view_result(aid)
            )

            btnContainer = QWidget()
            btnContainer.setStyleSheet("background: transparent;")
            btnLayout = QHBoxLayout(btnContainer)
            btnLayout.setContentsMargins(4, 2, 4, 2)
            btnLayout.setAlignment(Qt.AlignCenter)
            btnLayout.addWidget(view_btn)

            self.table.setCellWidget(row, 9, btnContainer)

    # ========================================================
    # LOAD STATISTICS
    # ========================================================

    def load_statistics(self, exam_id):

        if exam_id is None:
            self.calculate_all_statistics()
            return

        statistics = ResultModel.get_exam_result_statistics(exam_id)

        if not statistics:
            self.reset_statistics()
            return

        total = int(statistics["total_attempts"] or 0)
        submitted = int(statistics["submitted_attempts"] or 0)
        in_progress = int(statistics["in_progress_attempts"] or 0)
        highest = float(statistics["highest_score"] or 0)
        lowest = float(statistics["lowest_score"] or 0)
        average = float(statistics["average_score"] or 0)

        self.total_label.setText(f"Total: {total}")
        self.submitted_label.setText(f"Submitted: {submitted}")
        self.progress_label.setText(f"In Progress: {in_progress}")
        self.highest_label.setText(f"Highest: {highest:.2f}")
        self.lowest_label.setText(f"Lowest: {lowest:.2f}")
        self.average_label.setText(f"Average: {average:.2f}")

    # ========================================================
    # ALL RESULT STATISTICS
    # ========================================================

    def calculate_all_statistics(self):

        results = self.all_results
        total = len(results)
        submitted = sum(1 for result in results if result["status"] == "SUBMITTED")
        in_progress = sum(1 for result in results if result["status"] == "IN_PROGRESS")

        scores = [
            float(result["score"] or 0)
            for result in results
            if result["status"] == "SUBMITTED"
        ]

        if scores:
            highest = max(scores)
            lowest = min(scores)
            average = sum(scores) / len(scores)
        else:
            highest = 0
            lowest = 0
            average = 0

        self.total_label.setText(f"Total: {total}")
        self.submitted_label.setText(f"Submitted: {submitted}")
        self.progress_label.setText(f"In Progress: {in_progress}")
        self.highest_label.setText(f"Highest: {highest:.2f}")
        self.lowest_label.setText(f"Lowest: {lowest:.2f}")
        self.average_label.setText(f"Average: {average:.2f}")

    # ========================================================
    # RESET STATISTICS
    # ========================================================

    def reset_statistics(self):
        self.total_label.setText("Total: 0")
        self.submitted_label.setText("Submitted: 0")
        self.progress_label.setText("In Progress: 0")
        self.highest_label.setText("Highest: 0.00")
        self.lowest_label.setText("Lowest: 0.00")
        self.average_label.setText("Average: 0.00")

    # ========================================================
    # EXAM CHANGED
    # ========================================================

    def exam_changed(self):
        self.search.clear()
        self.load_results()

    # ========================================================
    # SEARCH
    # ========================================================

    def search_results(self):

        keyword = self.search.text().strip().lower()

        if not keyword:
            self.display_results(self.all_results)
            return

        filtered = []

        for result in self.all_results:
            name = str(result["student_name"] or "").lower()
            register_no = str(result["register_no"] or "").lower()

            if keyword in name or keyword in register_no:
                filtered.append(result)

        self.display_results(filtered)

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_results(self):
        self.load_exams()
        self.load_results()

    # ========================================================
    # VIEW RESULT DETAILS
    # ========================================================

    def view_result(self, attempt_id):

        result = ResultModel.get_attempt_result(attempt_id)

        if not result:
            QMessageBox.warning(self, "Error", "Result not found.")
            return

        answers = ResultModel.get_attempt_answers(attempt_id)
        summary = ResultModel.get_attempt_summary(attempt_id)

        dialog = ResultDetailDialog(result, answers, summary, self)
        dialog.exec_()


# ============================================================
# RESULT DETAIL DIALOG
# ============================================================

class ResultDetailDialog(QDialog):

    def __init__(self, result, answers, summary, parent=None):
        super().__init__(parent)

        self.result = result
        self.answers = answers
        self.summary = summary

        self.setWindowTitle(
            f"Result Details - {self.result['student_name']} ({self.result['register_no']})"
        )
        self.resize(760, 680)

        self.setupUI()

    # ========================================================
    # UI
    # ========================================================

    def setupUI(self):

        self.setObjectName("pageWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title
        title = QLabel("📄 Examination Result Details")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        infoRow = QHBoxLayout()
        infoRow.setSpacing(16)

        # Student Info Group
        student_group = QGroupBox("Student Details")
        student_layout = QFormLayout()
        student_layout.addRow("Register Number:", QLabel(str(self.result["register_no"])))
        student_layout.addRow("Name:", QLabel(str(self.result["student_name"])))
        student_layout.addRow("Department:", QLabel(str(self.result["department"])))
        student_layout.addRow("Semester:", QLabel(str(self.result["semester"])))
        student_group.setLayout(student_layout)
        infoRow.addWidget(student_group)

        # Exam Info Group
        exam_group = QGroupBox("Examination Details")
        exam_layout = QFormLayout()
        exam_layout.addRow("Exam Name:", QLabel(str(self.result["exam_name"])))
        exam_layout.addRow("Subject Code:", QLabel(str(self.result["subject_code"])))
        exam_layout.addRow("Subject:", QLabel(str(self.result["subject_name"])))
        exam_layout.addRow("Exam Date:", QLabel(str(self.result["exam_date"])))
        exam_group.setLayout(exam_layout)
        infoRow.addWidget(exam_group)

        layout.addLayout(infoRow)

        # Score Banner Card
        score_card = QFrame()
        score_card.setObjectName("card")
        score_layout = QVBoxLayout(score_card)

        score = float(self.result["score"] or 0)
        total_marks = float(self.result["total_marks"] or 0)

        if total_marks > 0:
            percentage = (score / total_marks) * 100
        else:
            percentage = 0

        score_label = QLabel(
            f"Score: {score:.2f} / {total_marks:.2f}    |    Percentage: {percentage:.2f}%"
        )
        score_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        score_label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(score_label)

        if self.summary:
            answered = int(self.summary["answered"] or 0)
            correct = int(self.summary["correct_answers"] or 0)
            wrong = int(self.summary["wrong_answers"] or 0)

            summary_label = QLabel(
                f"Answered: {answered}  •  Correct: {correct}  •  Wrong: {wrong}"
            )
            summary_label.setAlignment(Qt.AlignCenter)
            summary_label.setObjectName("pageSubtitle")
            score_layout.addWidget(summary_label)

        layout.addWidget(score_card)

        # Answers QTextEdit
        answers_text = QTextEdit()
        answers_text.setReadOnly(True)

        output = []
        for number, answer in enumerate(self.answers, start=1):
            question_text = answer["question_text"]
            selected = answer["selected_option"] or "Not Answered"
            correct_option = answer["correct_option"]
            marks_awarded = float(answer["marks_awarded"] or 0)
            result_tag = "✓ CORRECT" if answer["is_correct"] == 1 else "✗ WRONG"

            output.append(
                f"Question {number}: {question_text}\n"
                f"  Selected: {selected}  |  Correct: {correct_option}  |  Result: {result_tag}\n"
                f"  Marks: {marks_awarded:.2f}\n"
                f"{'-' * 60}\n"
            )

        if output:
            answers_text.setPlainText("\n".join(output))
        else:
            answers_text.setPlainText("No responses recorded for this attempt.")

        layout.addWidget(answers_text)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)