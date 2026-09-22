import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QGroupBox,
    QInputDialog,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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


class QuestionsPage(QWidget):

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):
        super().__init__()

        self.selected_question_id = None

        self.setup_ui()

        self.load_categories()
        self.load_questions()

    # ==========================================================
    # UI
    # ==========================================================

    def setup_ui(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # ------------------------------------------------------
        # HEADER CARD
        # ------------------------------------------------------

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

        title = QLabel("❓ Question Bank & Assessment Authoring")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Design, manage, and configure categorized multiple-choice questions with automated grading weights.")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        headerLayout.addWidget(title)
        headerLayout.addWidget(subtitle)
        main_layout.addWidget(headerCard)

        # ------------------------------------------------------
        # QUESTION FORM
        # ------------------------------------------------------

        form_group = QGroupBox("Question Details & Grading Config")
        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        # ------------------------------------------------------
        # QUESTION
        # ------------------------------------------------------

        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Enter the examination question prompt...")
        self.question_input.setMinimumHeight(80)

        form_layout.addRow("Question Prompt:", self.question_input)

        # ------------------------------------------------------
        # CATEGORY
        # ------------------------------------------------------

        category_layout = QHBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(260)
        self.category_combo.setMinimumHeight(38)
        self.category_combo.setPlaceholderText("Select category")

        self.add_category_button = QPushButton("➕ Add Category")
        self.add_category_button.setMinimumHeight(38)
        self.add_category_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)
        self.add_category_button.clicked.connect(self.add_category)

        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.add_category_button)
        category_layout.addStretch()

        form_layout.addRow("Category:", category_layout)

        # ------------------------------------------------------
        # OPTIONS
        # ------------------------------------------------------

        self.option_a = QLineEdit()
        self.option_a.setPlaceholderText("Option A text")
        self.option_a.setMinimumHeight(36)
        form_layout.addRow("Option A:", self.option_a)

        self.option_b = QLineEdit()
        self.option_b.setPlaceholderText("Option B text")
        self.option_b.setMinimumHeight(36)
        form_layout.addRow("Option B:", self.option_b)

        self.option_c = QLineEdit()
        self.option_c.setPlaceholderText("Option C text")
        self.option_c.setMinimumHeight(36)
        form_layout.addRow("Option C:", self.option_c)

        self.option_d = QLineEdit()
        self.option_d.setPlaceholderText("Option D text")
        self.option_d.setMinimumHeight(36)
        form_layout.addRow("Option D:", self.option_d)

        # ------------------------------------------------------
        # CORRECT ANSWER & MARKS ROW
        # ------------------------------------------------------

        scoring_layout = QHBoxLayout()

        self.correct_option = QComboBox()
        self.correct_option.addItems(["A", "B", "C", "D"])
        self.correct_option.setMinimumWidth(100)
        self.correct_option.setMinimumHeight(36)

        scoring_layout.addWidget(QLabel("Correct Option:"))
        scoring_layout.addWidget(self.correct_option)
        scoring_layout.addSpacing(20)

        self.marks = QDoubleSpinBox()
        self.marks.setMinimum(0)
        self.marks.setMaximum(100)
        self.marks.setValue(1)
        self.marks.setDecimals(2)
        self.marks.setMinimumWidth(100)
        self.marks.setMinimumHeight(36)

        scoring_layout.addWidget(QLabel("Marks (+):"))
        scoring_layout.addWidget(self.marks)
        scoring_layout.addSpacing(20)

        self.negative_marks = QDoubleSpinBox()
        self.negative_marks.setMinimum(0)
        self.negative_marks.setMaximum(100)
        self.negative_marks.setValue(0)
        self.negative_marks.setDecimals(2)
        self.negative_marks.setMinimumWidth(100)
        self.negative_marks.setMinimumHeight(36)

        scoring_layout.addWidget(QLabel("Negative Marks (-):"))
        scoring_layout.addWidget(self.negative_marks)
        scoring_layout.addStretch()

        form_layout.addRow("Grading Weights:", scoring_layout)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # ======================================================
        # ACTION BUTTONS
        # ======================================================

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.add_button = QPushButton("➕ Save Question")
        self.add_button.setMinimumHeight(38)
        self.add_button.setStyleSheet(f"""
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

        self.update_button = QPushButton("✏ Update Question")
        self.update_button.setMinimumHeight(38)
        self.update_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        self.delete_button = QPushButton("🗑 Delete Question")
        self.delete_button.setMinimumHeight(38)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BADGE_DANGER_BG};
                color: {BADGE_DANGER_TEXT};
                border: 1px solid {BADGE_DANGER_BORDER};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #9F1239;
                color: #FFFFFF;
            }}
        """)

        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setMinimumHeight(38)
        self.clear_button.setStyleSheet(f"""
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

        self.refresh_button = QPushButton("🔄 Refresh")
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

        self.add_button.clicked.connect(self.add_question)
        self.update_button.clicked.connect(self.update_question)
        self.delete_button.clicked.connect(self.delete_question)
        self.clear_button.clicked.connect(self.clear_form)
        self.refresh_button.clicked.connect(self.refresh_all)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

        # ======================================================
        # QUESTIONS TABLE
        # ======================================================

        tableCard = QWidget()
        tableCard.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
        tableLayout = QVBoxLayout(tableCard)
        tableLayout.setContentsMargins(16, 16, 16, 16)

        table_title = QLabel("📚 Question Repository")
        table_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        tableLayout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "CATEGORY",
            "QUESTION",
            "OPTION A",
            "OPTION B",
            "OPTION C",
            "OPTION D",
            "CORRECT",
            "MARKS"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        self.table.setStyleSheet(f"""
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

        self.table.cellClicked.connect(self.select_question)
        tableLayout.addWidget(self.table)
        main_layout.addWidget(tableCard)

        self.setLayout(main_layout)

    # ==========================================================
    # LOAD CATEGORIES
    # ==========================================================

    def load_categories(self):

        try:

            categories = (
                QuestionModel.get_all_categories()
            )

            current_category_id = (
                self.category_combo.currentData()
            )

            self.category_combo.blockSignals(
                True
            )

            self.category_combo.clear()

            self.category_combo.addItem(
                "Select Category",
                None
            )

            for category in categories:

                self.category_combo.addItem(
                    category["name"],
                    category["id"]
                )

            self.category_combo.blockSignals(
                False
            )

            # --------------------------------------------------
            # Restore previously selected category
            # --------------------------------------------------

            if current_category_id is not None:

                index = (
                    self.category_combo.findData(
                        current_category_id
                    )
                )

                if index >= 0:

                    self.category_combo.setCurrentIndex(
                        index
                    )

        except Exception as e:

            self.category_combo.blockSignals(
                False
            )

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load categories:\n\n{e}"
            )

    # ==========================================================
    # ADD CATEGORY
    # ==========================================================

    def add_category(self):

        name, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Enter category name:"
        )

        if not ok:
            return

        name = name.strip()

        if not name:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter a category name."
            )

            return

        # ------------------------------------------------------
        # Check duplicate category
        # ------------------------------------------------------

        categories = (
            QuestionModel.get_all_categories()
        )

        for category in categories:

            if category["name"].strip().lower() == name.lower():

                QMessageBox.warning(
                    self,
                    "Duplicate Category",
                    "This category already exists."
                )

                return

        # ------------------------------------------------------
        # Add category
        # ------------------------------------------------------

        category_id = (
            QuestionModel.add_category(
                name
            )
        )

        if category_id:

            QMessageBox.information(
                self,
                "Success",
                "Category added successfully."
            )

            self.load_categories()

            # --------------------------------------------------
            # Automatically select new category
            # --------------------------------------------------

            index = (
                self.category_combo.findData(
                    category_id
                )
            )

            if index >= 0:

                self.category_combo.setCurrentIndex(
                    index
                )

        else:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to add category."
            )

    # ==========================================================
    # REFRESH EVERYTHING
    # ==========================================================

    def refresh_all(self):

        self.load_categories()
        self.load_questions()

    # ==========================================================
    # LOAD QUESTIONS
    # ==========================================================

    def load_questions(self):

        try:

            questions = (
                QuestionModel.get_all_questions()
            )

            self.table.setRowCount(
                len(questions)
            )

            for row, question in enumerate(
                questions
            ):

                # ------------------------------------------------
                # ID
                # ------------------------------------------------

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(question["id"])
                    )
                )

                # ------------------------------------------------
                # CATEGORY
                # ------------------------------------------------

                category_name = (
                    question["category_name"]
                    if question["category_name"]
                    else "Uncategorized"
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        category_name
                    )
                )

                # ------------------------------------------------
                # QUESTION
                # ------------------------------------------------

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        question["question_text"]
                    )
                )

                # ------------------------------------------------
                # OPTIONS
                # ------------------------------------------------

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        question["option_a"]
                    )
                )

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        question["option_b"]
                    )
                )

                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        question["option_c"]
                    )
                )

                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(
                        question["option_d"]
                    )
                )

                # ------------------------------------------------
                # CORRECT
                # ------------------------------------------------

                self.table.setItem(
                    row,
                    7,
                    QTableWidgetItem(
                        question["correct_option"]
                    )
                )

                # ------------------------------------------------
                # MARKS
                # ------------------------------------------------

                self.table.setItem(
                    row,
                    8,
                    QTableWidgetItem(
                        str(question["marks"])
                    )
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load questions:\n\n{e}"
            )

    # ==========================================================
    # SELECT QUESTION
    # ==========================================================

    def select_question(
        self,
        row,
        column
    ):

        item = self.table.item(
            row,
            0
        )

        if item is None:
            return

        question_id = int(
            item.text()
        )

        question = (
            QuestionModel.get_question(
                question_id
            )
        )

        if question is None:
            return

        self.selected_question_id = (
            question_id
        )

        # ------------------------------------------------------
        # QUESTION
        # ------------------------------------------------------

        self.question_input.setPlainText(
            question["question_text"]
        )

        # ------------------------------------------------------
        # CATEGORY
        # ------------------------------------------------------

        category_id = (
            question["category_id"]
        )

        if category_id is None:

            self.category_combo.setCurrentIndex(
                0
            )

        else:

            index = (
                self.category_combo.findData(
                    category_id
                )
            )

            if index >= 0:

                self.category_combo.setCurrentIndex(
                    index
                )

            else:

                self.category_combo.setCurrentIndex(
                    0
                )

        # ------------------------------------------------------
        # OPTIONS
        # ------------------------------------------------------

        self.option_a.setText(
            question["option_a"]
        )

        self.option_b.setText(
            question["option_b"]
        )

        self.option_c.setText(
            question["option_c"]
        )

        self.option_d.setText(
            question["option_d"]
        )

        # ------------------------------------------------------
        # CORRECT OPTION
        # ------------------------------------------------------

        index = (
            self.correct_option.findText(
                question["correct_option"]
            )
        )

        if index >= 0:

            self.correct_option.setCurrentIndex(
                index
            )

        # ------------------------------------------------------
        # MARKS
        # ------------------------------------------------------

        self.marks.setValue(
            float(
                question["marks"]
            )
        )

        # ------------------------------------------------------
        # NEGATIVE MARKS
        # ------------------------------------------------------

        self.negative_marks.setValue(
            float(
                question["negative_marks"]
            )
        )

    # ==========================================================
    # VALIDATE FORM
    # ==========================================================

    def validate_form(self):

        question = (
            self.question_input
            .toPlainText()
            .strip()
        )

        option_a = (
            self.option_a
            .text()
            .strip()
        )

        option_b = (
            self.option_b
            .text()
            .strip()
        )

        option_c = (
            self.option_c
            .text()
            .strip()
        )

        option_d = (
            self.option_d
            .text()
            .strip()
        )

        category_id = (
            self.category_combo.currentData()
        )

        # ------------------------------------------------------
        # QUESTION
        # ------------------------------------------------------

        if not question:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter a question."
            )

            return None

        # ------------------------------------------------------
        # CATEGORY
        # ------------------------------------------------------

        if category_id is None:

            QMessageBox.warning(
                self,
                "Validation",
                "Please select a category."
            )

            return None

        # ------------------------------------------------------
        # OPTION A
        # ------------------------------------------------------

        if not option_a:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter Option A."
            )

            return None

        # ------------------------------------------------------
        # OPTION B
        # ------------------------------------------------------

        if not option_b:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter Option B."
            )

            return None

        # ------------------------------------------------------
        # OPTION C
        # ------------------------------------------------------

        if not option_c:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter Option C."
            )

            return None

        # ------------------------------------------------------
        # OPTION D
        # ------------------------------------------------------

        if not option_d:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter Option D."
            )

            return None

        # ------------------------------------------------------
        # RETURN DATA
        # ------------------------------------------------------

        return (
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            self.correct_option.currentText(),
            self.marks.value(),
            self.negative_marks.value(),
            category_id
        )

    # ==========================================================
    # ADD QUESTION
    # ==========================================================

    def add_question(self):

        data = self.validate_form()

        if data is None:
            return

        question_id = (
            QuestionModel.add_question(
                *data
            )
        )

        if question_id:

            QMessageBox.information(
                self,
                "Success",
                "Question added successfully."
            )

            self.clear_form()
            self.load_questions()

        else:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to add question."
            )

    # ==========================================================
    # UPDATE QUESTION
    # ==========================================================

    def update_question(self):

        if self.selected_question_id is None:

            QMessageBox.warning(
                self,
                "Update Question",
                "Please select a question first."
            )

            return

        data = self.validate_form()

        if data is None:
            return

        success = (
            QuestionModel.update_question(
                self.selected_question_id,
                *data
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Success",
                "Question updated successfully."
            )

            self.clear_form()
            self.load_questions()

        else:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to update question."
            )

    # ==========================================================
    # DELETE QUESTION
    # ==========================================================

    def delete_question(self):

        if self.selected_question_id is None:

            QMessageBox.warning(
                self,
                "Delete Question",
                "Please select a question first."
            )

            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this question?",
            QMessageBox.Yes |
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = (
            QuestionModel.delete_question(
                self.selected_question_id
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Success",
                "Question deleted successfully."
            )

            self.clear_form()
            self.load_questions()

        else:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to delete question."
            )

    # ==========================================================
    # CLEAR FORM
    # ==========================================================

    def clear_form(self):

        self.selected_question_id = None

        self.question_input.clear()

        self.option_a.clear()
        self.option_b.clear()
        self.option_c.clear()
        self.option_d.clear()

        self.category_combo.setCurrentIndex(
            0
        )

        self.correct_option.setCurrentIndex(
            0
        )

        self.marks.setValue(
            1
        )

        self.negative_marks.setValue(
            0
        )

        self.table.clearSelection()


# ==============================================================
# TEST PAGE DIRECTLY
# ==============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = QuestionsPage()

    window.setWindowTitle(
        "Question Management"
    )

    window.resize(
        1400,
        850
    )

    window.show()

    sys.exit(
        app.exec_()
    )