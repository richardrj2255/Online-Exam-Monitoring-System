import sys
import random

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QGroupBox,
    QFrame,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.exam_model import ExamModel
from models.question_model import QuestionModel


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
    BADGE_DANGER_BG,
    BADGE_DANGER_TEXT,
    BADGE_DANGER_BORDER,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER,
)


class ExamQuestionsPage(QWidget):

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):
        super().__init__()

        self.selected_exam_id = None

        self.setup_ui()

        self.load_exams()
        self.load_categories()

    # ==========================================================
    # UI
    # ==========================================================

    def setup_ui(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # ======================================================
        # HEADER CARD
        # ======================================================

        headerCard = QWidget()
        headerCard.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
        headerLayout = QVBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(3)

        title = QLabel("🎯 Examination Question Assembly & Mapping")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Assign question sets to examinations manually or synthesize random balanced exams via automated selection.")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        headerLayout.addWidget(title)
        headerLayout.addWidget(subtitle)
        main_layout.addWidget(headerCard)

        # ======================================================
        # EXAM SELECTION CARD
        # ======================================================

        examCard = QFrame()
        examCard.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        exam_layout = QHBoxLayout(examCard)
        exam_layout.setContentsMargins(16, 12, 16, 12)
        exam_layout.setSpacing(12)

        exam_label = QLabel("Active Examination:")
        exam_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 13px; background: transparent;")

        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumHeight(38)
        self.exam_combo.currentIndexChanged.connect(self.exam_changed)

        exam_layout.addWidget(exam_label)
        exam_layout.addWidget(self.exam_combo, 1)

        main_layout.addWidget(examCard)

        # ======================================================
        # AUTO SELECTION CARD
        # ======================================================

        auto_group = QGroupBox("🎲 Automated Question Generation Engine")
        auto_layout = QHBoxLayout()
        auto_layout.setContentsMargins(16, 16, 16, 16)
        auto_layout.setSpacing(12)

        category_label = QLabel("Category:")
        category_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600; font-size: 12px;")

        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(36)
        self.category_combo.currentIndexChanged.connect(self.category_changed)

        number_label = QLabel("Questions Count:")
        number_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600; font-size: 12px;")

        self.number_spin = QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(1000)
        self.number_spin.setValue(10)
        self.number_spin.setMinimumHeight(36)

        self.available_label = QLabel("Available: 0")
        self.available_label.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 6px;
                padding: 4px 10px;
                font-weight: 700;
                font-size: 11px;
            }}
        """)

        self.auto_select_button = QPushButton("🎲 Auto Select Questions")
        self.auto_select_button.setMinimumHeight(36)
        self.auto_select_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        self.auto_select_button.clicked.connect(self.auto_select_questions)

        auto_layout.addWidget(category_label)
        auto_layout.addWidget(self.category_combo, 2)
        auto_layout.addWidget(number_label)
        auto_layout.addWidget(self.number_spin)
        auto_layout.addWidget(self.available_label)
        auto_layout.addWidget(self.auto_select_button)

        auto_group.setLayout(auto_layout)
        main_layout.addWidget(auto_group)

        # ======================================================
        # MANUAL ASSIGNMENT CARD
        # ======================================================

        manual_group = QGroupBox("Available Question Bank")
        manual_layout = QVBoxLayout()
        manual_layout.setContentsMargins(16, 16, 16, 16)
        manual_layout.setSpacing(12)

        self.available_table = QTableWidget()
        self.available_table.setColumnCount(5)
        self.available_table.setHorizontalHeaderLabels([
            "ID",
            "QUESTION",
            "CATEGORY",
            "MARKS",
            "NEGATIVE MARKS"
        ])

        self.available_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.available_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.available_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.available_table.setAlternatingRowColors(True)
        self.available_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.available_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.available_table.verticalHeader().setVisible(False)

        self.available_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                alternate-background-color: {BG_CARD_ALT};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                gridline-color: #243248;
                font-size: 13px;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {BG_CANVAS};
                color: {TEXT_SECONDARY};
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {BORDER_SUBTLE};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #1E293B;
            }}
            QTableWidget::item:selected {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        manual_layout.addWidget(self.available_table)

        assign_layout = QHBoxLayout()

        self.assign_button = QPushButton("➕ Assign Selected Questions")
        self.assign_button.setMinimumHeight(38)
        self.assign_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        self.assign_button.clicked.connect(self.assign_selected_questions)

        self.refresh_button = QPushButton("🔄 Refresh Bank")
        self.refresh_button.setMinimumHeight(38)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #243248;
            }}
        """)
        self.refresh_button.clicked.connect(self.refresh_page)

        assign_layout.addWidget(self.assign_button)
        assign_layout.addStretch()
        assign_layout.addWidget(self.refresh_button)

        manual_layout.addLayout(assign_layout)
        manual_group.setLayout(manual_layout)
        main_layout.addWidget(manual_group)

        # ======================================================
        # ASSIGNED QUESTIONS CARD
        # ======================================================

        assigned_group = QGroupBox("Assigned Examination Questions")
        assigned_layout = QVBoxLayout()
        assigned_layout.setContentsMargins(16, 16, 16, 16)
        assigned_layout.setSpacing(12)

        assigned_top = QHBoxLayout()
        assigned_top.addStretch()

        self.assigned_count_label = QLabel("Assigned Questions: 0")
        self.assigned_count_label.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 10px;
                padding: 4px 12px;
                font-weight: 700;
                font-size: 11px;
            }}
        """)
        assigned_top.addWidget(self.assigned_count_label)
        assigned_layout.addLayout(assigned_top)

        self.assigned_table = QTableWidget()
        self.assigned_table.setColumnCount(6)
        self.assigned_table.setHorizontalHeaderLabels([
            "ORDER",
            "QUESTION ID",
            "QUESTION",
            "CATEGORY",
            "MARKS",
            "ACTION"
        ])

        self.assigned_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.assigned_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.assigned_table.setAlternatingRowColors(True)
        self.assigned_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assigned_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.assigned_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.assigned_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.assigned_table.verticalHeader().setVisible(False)

        self.assigned_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                alternate-background-color: {BG_CARD_ALT};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                gridline-color: #243248;
                font-size: 13px;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {BG_CANVAS};
                color: {TEXT_SECONDARY};
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {BORDER_SUBTLE};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #1E293B;
            }}
            QTableWidget::item:selected {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        assigned_layout.addWidget(self.assigned_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.clear_all_button = QPushButton("🗑 Remove All Assigned Questions")
        self.clear_all_button.setMinimumHeight(38)
        self.clear_all_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BADGE_DANGER_BG};
                color: {BADGE_DANGER_TEXT};
                border: 1px solid {BADGE_DANGER_BORDER};
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #9F1239;
                color: #FFFFFF;
            }}
        """)
        self.clear_all_button.clicked.connect(self.remove_all_questions)
        bottom_layout.addWidget(self.clear_all_button)

        assigned_layout.addLayout(bottom_layout)
        assigned_group.setLayout(assigned_layout)
        main_layout.addWidget(assigned_group)

        self.setLayout(main_layout)

    # ==========================================================
    # LOAD EXAMS
    # ==========================================================

    def load_exams(self):

        self.exam_combo.blockSignals(
            True
        )

        self.exam_combo.clear()

        try:

            exams = (
                ExamModel.get_all_exams()
            )

            for exam in exams:

                self.exam_combo.addItem(
                    f"{exam['exam_name']} | "
                    f"{exam['subject_code']} | "
                    f"{exam['exam_date']}",
                    exam["id"]
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load examinations:\n\n{e}"
            )

        self.exam_combo.blockSignals(
            False
        )

        if self.exam_combo.count() > 0:

            self.exam_combo.setCurrentIndex(
                0
            )

            self.selected_exam_id = (
                self.exam_combo.currentData()
            )

            self.load_available_questions()
            self.load_assigned_questions()

        else:

            self.selected_exam_id = None

            self.clear_tables()

    # ==========================================================
    # LOAD CATEGORIES
    # ==========================================================

    def load_categories(self):

        self.category_combo.blockSignals(
            True
        )

        self.category_combo.clear()

        self.category_combo.addItem(
            "All Categories",
            None
        )

        try:

            categories = (
                QuestionModel.get_all_categories()
            )

            for category in categories:

                self.category_combo.addItem(
                    category["name"],
                    category["id"]
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load categories:\n\n{e}"
            )

        self.category_combo.blockSignals(
            False
        )

        self.update_available_count()

    # ==========================================================
    # EXAM CHANGED
    # ==========================================================

    def exam_changed(self):

        exam_id = (
            self.exam_combo.currentData()
        )

        self.selected_exam_id = exam_id

        self.load_available_questions()
        self.load_assigned_questions()

    # ==========================================================
    # CATEGORY CHANGED
    # ==========================================================

    def category_changed(self):

        self.load_available_questions()

    # ==========================================================
    # LOAD AVAILABLE QUESTIONS
    # ==========================================================

    def load_available_questions(self):

        self.available_table.setRowCount(
            0
        )

        if self.selected_exam_id is None:

            self.available_label.setText(
                "Available: 0"
            )

            return

        category_id = (
            self.category_combo.currentData()
        )

        try:

            questions = (
                QuestionModel.get_unassigned_questions(
                    self.selected_exam_id,
                    category_id
                )
            )

            self.available_table.setRowCount(
                len(questions)
            )

            for row, question in enumerate(
                questions
            ):

                self.available_table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(question["id"])
                    )
                )

                self.available_table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        question["question_text"]
                    )
                )

                self.available_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        question["category_name"]
                        or "Uncategorized"
                    )
                )

                self.available_table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        str(question["marks"])
                    )
                )

                self.available_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        str(question["negative_marks"])
                    )
                )

            self.available_label.setText(
                f"Available: {len(questions)}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load available questions:\n\n{e}"
            )

            self.available_label.setText(
                "Available: 0"
            )

    # ==========================================================
    # LOAD ASSIGNED QUESTIONS
    # ==========================================================

    def load_assigned_questions(self):

        self.assigned_table.setRowCount(
            0
        )

        if self.selected_exam_id is None:

            self.assigned_count_label.setText(
                "Assigned: 0"
            )

            return

        try:

            questions = (
                QuestionModel.get_questions_for_exam(
                    self.selected_exam_id
                )
            )

            self.assigned_table.setRowCount(
                len(questions)
            )

            for row, question in enumerate(
                questions
            ):

                self.assigned_table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(question["display_order"])
                    )
                )

                self.assigned_table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        str(question["question_id"])
                    )
                )

                self.assigned_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        question["question_text"]
                    )
                )

                self.assigned_table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        question["category_name"]
                        or "Uncategorized"
                    )
                )

                self.assigned_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        str(question["marks"])
                    )
                )

                remove_button = QPushButton(
                    "🗑 Remove"
                )

                remove_button.clicked.connect(
                    lambda checked,
                    eqid=question["exam_question_id"]:
                    self.remove_question(eqid)
                )

                self.assigned_table.setCellWidget(
                    row,
                    5,
                    remove_button
                )

            self.assigned_count_label.setText(
                f"Assigned: {len(questions)}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load assigned questions:\n\n{e}"
            )

    # ==========================================================
    # ASSIGN SELECTED QUESTIONS
    # ==========================================================

    def assign_selected_questions(self):

        if self.selected_exam_id is None:

            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )

            return

        selected_rows = (
            self.available_table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:

            QMessageBox.warning(
                self,
                "No Questions Selected",
                "Please select one or more questions."
            )

            return

        assigned_count = (
            QuestionModel.get_exam_question_count(
                self.selected_exam_id
            )
        )

        success_count = 0

        for row_index in selected_rows:

            row = row_index.row()

            question_item = (
                self.available_table.item(
                    row,
                    0
                )
            )

            if question_item is None:
                continue

            question_id = int(
                question_item.text()
            )

            display_order = (
                assigned_count
                + success_count
                + 1
            )

            success = (
                QuestionModel.assign_question_to_exam(
                    self.selected_exam_id,
                    question_id,
                    display_order
                )
            )

            if success:

                success_count += 1

        if success_count > 0:

            QMessageBox.information(
                self,
                "Questions Assigned",
                f"{success_count} question(s) "
                "assigned successfully."
            )

            self.load_available_questions()
            self.load_assigned_questions()

        else:

            QMessageBox.warning(
                self,
                "Assignment Failed",
                "No questions were assigned."
            )

    # ==========================================================
    # AUTO SELECT QUESTIONS
    # ==========================================================

    def auto_select_questions(self):

        if self.selected_exam_id is None:

            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )

            return

        category_id = (
            self.category_combo.currentData()
        )

        if category_id is None:

            QMessageBox.warning(
                self,
                "Select Category",
                "Please select a category before "
                "using automatic question selection."
            )

            return

        number_to_select = (
            self.number_spin.value()
        )

        try:

            available_questions = (
                QuestionModel.get_unassigned_questions(
                    self.selected_exam_id,
                    category_id
                )
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load questions:\n\n{e}"
            )

            return

        available_count = (
            len(available_questions)
        )

        if available_count == 0:

            QMessageBox.warning(
                self,
                "No Questions",
                "There are no unassigned questions "
                "in this category."
            )

            return

        if number_to_select > available_count:

            QMessageBox.warning(
                self,
                "Not Enough Questions",
                f"You requested {number_to_select} "
                f"question(s), but only "
                f"{available_count} question(s) "
                "are available in this category."
            )

            return

        selected_questions = random.sample(
            available_questions,
            number_to_select
        )

        assigned_count = (
            QuestionModel.get_exam_question_count(
                self.selected_exam_id
            )
        )

        success_count = 0

        for index, question in enumerate(
            selected_questions
        ):

            display_order = (
                assigned_count
                + index
                + 1
            )

            success = (
                QuestionModel.assign_question_to_exam(
                    self.selected_exam_id,
                    question["id"],
                    display_order
                )
            )

            if success:

                success_count += 1

        if success_count > 0:

            QMessageBox.information(
                self,
                "Automatic Selection Complete",
                f"{success_count} question(s) "
                "were randomly selected and "
                "assigned to the examination."
            )

            self.load_available_questions()
            self.load_assigned_questions()

        else:

            QMessageBox.warning(
                self,
                "Assignment Failed",
                "Unable to automatically assign questions."
            )

    # ==========================================================
    # REMOVE QUESTION
    # ==========================================================

    def remove_question(
        self,
        exam_question_id
    ):

        reply = QMessageBox.question(
            self,
            "Remove Question",
            "Remove this question from the examination?",
            QMessageBox.Yes |
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = (
            QuestionModel.remove_question_from_exam(
                exam_question_id
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Removed",
                "Question removed from the examination."
            )

            self.load_available_questions()
            self.load_assigned_questions()

        else:

            QMessageBox.warning(
                self,
                "Error",
                "Unable to remove question."
            )

    # ==========================================================
    # REMOVE ALL QUESTIONS
    # ==========================================================

    def remove_all_questions(self):

        if self.selected_exam_id is None:

            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )

            return

        count = (
            QuestionModel.get_exam_question_count(
                self.selected_exam_id
            )
        )

        if count == 0:

            QMessageBox.information(
                self,
                "No Questions",
                "There are no questions assigned "
                "to this examination."
            )

            return

        reply = QMessageBox.question(
            self,
            "Remove All Questions",
            f"This will remove all {count} assigned "
            "questions from this examination.\n\n"
            "Are you sure?",
            QMessageBox.Yes |
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = (
            QuestionModel.remove_all_questions_from_exam(
                self.selected_exam_id
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Questions Removed",
                "All questions have been removed "
                "from the examination."
            )

            self.load_available_questions()
            self.load_assigned_questions()

        else:

            QMessageBox.warning(
                self,
                "Error",
                "Unable to remove questions."
            )

    # ==========================================================
    # UPDATE AVAILABLE COUNT
    # ==========================================================

    def update_available_count(self):

        self.load_available_questions()

    # ==========================================================
    # REFRESH PAGE
    # ==========================================================

    def refresh_page(self):

        current_exam_id = (
            self.selected_exam_id
        )

        self.load_exams()
        self.load_categories()

        if current_exam_id is not None:

            index = (
                self.exam_combo.findData(
                    current_exam_id
                )
            )

            if index >= 0:

                self.exam_combo.setCurrentIndex(
                    index
                )

                self.selected_exam_id = (
                    current_exam_id
                )

        self.load_available_questions()
        self.load_assigned_questions()

    # ==========================================================
    # CLEAR TABLES
    # ==========================================================

    def clear_tables(self):

        self.available_table.setRowCount(
            0
        )

        self.assigned_table.setRowCount(
            0
        )

        self.available_label.setText(
            "Available: 0"
        )

        self.assigned_count_label.setText(
            "Assigned: 0"
        )


# ==============================================================
# DIRECT TEST
# ==============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ExamQuestionsPage()

    window.setWindowTitle(
        "Exam Question Management"
    )

    window.resize(
        1400,
        850
    )

    window.show()

    sys.exit(
        app.exec_()
    )

