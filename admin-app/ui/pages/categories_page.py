import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.category_model import CategoryModel
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


class CategoriesPage(QWidget):

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):
        super().__init__()

        self.selected_category_id = None

        self.setup_ui()
        self.load_categories()

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

        title = QLabel("🏷 Question Bank Category Taxonomy")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Create, organize, and manage academic subject categories for modular exam generation.")
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
        # CATEGORY INPUT CARD
        # ------------------------------------------------------

        inputCard = QWidget()
        inputCard.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        input_layout = QHBoxLayout(inputCard)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(12)

        category_label = QLabel("Category Name:")
        category_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 13px; background: transparent;")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Enter category name (e.g. Computer Networks, Machine Learning)...")
        self.category_input.setMinimumHeight(38)

        input_layout.addWidget(category_label)
        input_layout.addWidget(self.category_input, 1)

        main_layout.addWidget(inputCard)

        # ------------------------------------------------------
        # ACTION BUTTONS
        # ------------------------------------------------------

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.add_button = QPushButton("➕ Save Category")
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

        self.update_button = QPushButton("✏ Update Category")
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

        self.delete_button = QPushButton("🗑 Delete Category")
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

        self.clear_button = QPushButton("Clear")
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

        self.add_button.clicked.connect(self.add_category)
        self.update_button.clicked.connect(self.update_category)
        self.delete_button.clicked.connect(self.delete_category)
        self.clear_button.clicked.connect(self.clear_form)
        self.refresh_button.clicked.connect(self.load_categories)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

        # ------------------------------------------------------
        # CATEGORY TABLE CARD
        # ------------------------------------------------------

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

        table_title = QLabel("Available Categories")
        table_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        tableLayout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([
            "CATEGORY ID",
            "CATEGORY NAME"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
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
                padding: 8px 12px;
                border-bottom: 1px solid #1E293B;
            }}
            QTableWidget::item:selected {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        self.table.cellClicked.connect(self.select_category)
        tableLayout.addWidget(self.table)
        main_layout.addWidget(tableCard)

        self.setLayout(main_layout)

    # ==========================================================
    # LOAD CATEGORIES
    # ==========================================================

    def load_categories(self):

        try:

            categories = (
                CategoryModel.get_all_categories()
            )

            self.table.setRowCount(
                len(categories)
            )

            for row, category in enumerate(
                categories
            ):

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(category["id"])
                    )
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        category["name"]
                    )
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load categories:\n\n{e}"
            )

    # ==========================================================
    # SELECT CATEGORY
    # ==========================================================

    def select_category(
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

        category_id = int(
            item.text()
        )

        category = (
            CategoryModel.get_category(
                category_id
            )
        )

        if category is None:
            return

        self.selected_category_id = (
            category_id
        )

        self.category_input.setText(
            category["name"]
        )

    # ==========================================================
    # VALIDATE FORM
    # ==========================================================

    def validate_form(self):

        name = (
            self.category_input
            .text()
            .strip()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Validation",
                "Please enter a category name."
            )

            return None

        return name

    # ==========================================================
    # ADD CATEGORY
    # ==========================================================

    def add_category(self):

        name = self.validate_form()

        if name is None:
            return

        category_id = (
            CategoryModel.add_category(
                name
            )
        )

        if category_id:

            QMessageBox.information(
                self,
                "Success",
                "Category added successfully."
            )

            self.clear_form()
            self.load_categories()

        else:

            QMessageBox.warning(
                self,
                "Category Exists",
                "Unable to add category.\n\n"
                "The category may already exist."
            )

    # ==========================================================
    # UPDATE CATEGORY
    # ==========================================================

    def update_category(self):

        if self.selected_category_id is None:

            QMessageBox.warning(
                self,
                "Update Category",
                "Please select a category first."
            )

            return

        name = self.validate_form()

        if name is None:
            return

        success = (
            CategoryModel.update_category(
                self.selected_category_id,
                name
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Success",
                "Category updated successfully."
            )

            self.clear_form()
            self.load_categories()

        else:

            QMessageBox.warning(
                self,
                "Update Failed",
                "Unable to update category.\n\n"
                "The category name may already exist."
            )

    # ==========================================================
    # DELETE CATEGORY
    # ==========================================================

    def delete_category(self):

        if self.selected_category_id is None:

            QMessageBox.warning(
                self,
                "Delete Category",
                "Please select a category first."
            )

            return

        category = (
            CategoryModel.get_category(
                self.selected_category_id
            )
        )

        if category is None:
            return

        category_name = category["name"]

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete "
            f"the category '{category_name}'?",
            QMessageBox.Yes |
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = (
            CategoryModel.delete_category(
                self.selected_category_id
            )
        )

        if success:

            QMessageBox.information(
                self,
                "Success",
                "Category deleted successfully."
            )

            self.clear_form()
            self.load_categories()

        else:

            QMessageBox.critical(
                self,
                "Error",
                "Unable to delete category."
            )

    # ==========================================================
    # CLEAR FORM
    # ==========================================================

    def clear_form(self):

        self.selected_category_id = None

        self.category_input.clear()

        self.table.clearSelection()


# ==============================================================
# TEST PAGE DIRECTLY
# ==============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CategoriesPage()

    window.setWindowTitle(
        "Category Management"
    )

    window.resize(
        900,
        650
    )

    window.show()

    sys.exit(
        app.exec_()
    )