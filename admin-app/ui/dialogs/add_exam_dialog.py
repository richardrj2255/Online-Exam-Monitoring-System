from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTimeEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate, QTime

from models.exam_model import ExamModel


class AddExamDialog(QDialog):

    def __init__(self, exam=None):
        super().__init__()

        self.exam = exam
        self._calculated_minutes = 120

        if self.exam:
            self.setWindowTitle("Edit Examination Session")
        else:
            self.setWindowTitle("Schedule New Examination")

        self.setObjectName("addExamDialog")
        self.resize(550, 870)
        self.setMinimumSize(520, 700)

        self.setup_ui()

        if self.exam:
            self.load_exam()

    ######################################################

    def _create_field_label(self, text, icon="", required=True):
        lbl = QLabel()
        icon_part = f"<span style='font-size: 13px; font-weight: bold; color: #475569;'>{icon}</span>  " if icon else ""
        req_part = " <span style='color: #EF4444; font-weight: bold;'>*</span>" if required else ""
        lbl.setText(
            f"{icon_part}<span style='color: #1E293B; font-weight: 600; font-size: 13px;'>{text}</span>{req_part}"
        )
        return lbl

    ######################################################

    def setup_ui(self):
        # Dialog Base Stylesheet
        self.setStyleSheet("""
            QDialog#addExamDialog {
                background-color: #F8FAFC;
            }

            QFrame#mainCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#headerIconBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #4338CA);
                border-radius: 12px;
                font-size: 24px;
                color: #FFFFFF;
            }

            QLabel#dialogHeaderTitle {
                color: #0F172A;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 20px;
                font-weight: 700;
            }

            QLabel#dialogHeaderSubtitle {
                color: #64748B;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 12px;
            }

            QLineEdit, QComboBox {
                background-color: #FAFAFA;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                min-height: 42px;
                font-size: 13px;
                color: #1E293B;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4F46E5;
                background-color: #FFFFFF;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                selection-background-color: #EEF2FF;
                selection-color: #4338CA;
                padding: 4px;
                outline: none;
            }

            /* Exam Schedule Highlighted Card */
            QFrame#card_exam_schedule {
                background-color: #F0F7FF;
                border: 1px solid #D0E2FF;
                border-radius: 12px;
            }

            /* Embedded input boxes with icons */
            QFrame.scheduleInputBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                min-height: 42px;
            }

            QFrame.scheduleInputBox:focus-within {
                border: 2px solid #4F46E5;
            }

            QFrame#durationContainer {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                min-height: 42px;
            }

            QLineEdit#durationField {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #1E293B;
                font-weight: 500;
                padding: 0;
                min-height: 38px;
            }

            QPushButton#btnSaveExam {
                background-color: #4F46E5;
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 14px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
                min-height: 48px;
            }

            QPushButton#btnSaveExam:hover {
                background-color: #4338CA;
            }

            QPushButton#btnSaveExam:pressed {
                background-color: #3730A3;
            }

            /* Calendar Widget Popup Styling */
            QCalendarWidget {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #F8FAFC;
                border-bottom: 1px solid #E2E8F0;
                min-height: 36px;
            }

            QCalendarWidget QToolButton {
                color: #1E293B;
                background-color: transparent;
                font-size: 12px;
                font-weight: 600;
                border-radius: 4px;
                padding: 4px 8px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #EEF2FF;
                color: #4F46E5;
            }

            QCalendarWidget QTableView {
                background-color: #FFFFFF;
                selection-background-color: #4F46E5;
                selection-color: #FFFFFF;
                outline: none;
            }
        """)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(16, 16, 16, 16)
        dialog_layout.setSpacing(0)

        # Scroll Area for responsive screen adaptation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("dialogScrollArea")
        scroll.setStyleSheet("""
            QScrollArea#dialogScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 6px;
                margin: 0px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 24px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Main Card Container
        card = QFrame()
        card.setObjectName("mainCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 22)
        card_layout.setSpacing(10)

        # ----------------------------------------------------
        # Header Row
        # ----------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)
        header_layout.setContentsMargins(0, 0, 0, 6)

        icon_box = QLabel("📅")
        icon_box.setObjectName("headerIconBox")
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(50, 50)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        if self.exam:
            self.title_lbl = QLabel("Edit Examination Session")
        else:
            self.title_lbl = QLabel("Schedule New Examination")

        self.title_lbl.setObjectName("dialogHeaderTitle")
        subtitle_lbl = QLabel("Configure academic session attributes and scheduling timetable.")
        subtitle_lbl.setObjectName("dialogHeaderSubtitle")

        title_vbox.addWidget(self.title_lbl)
        title_vbox.addWidget(subtitle_lbl)

        header_layout.addWidget(icon_box)
        header_layout.addLayout(title_vbox, 1)
        card_layout.addLayout(header_layout)

        # ----------------------------------------------------
        # Form Fields
        # ----------------------------------------------------
        # 1. Exam Name
        card_layout.addWidget(self._create_field_label("Exam Name", icon="🎓", required=True))
        self.exam_name = QLineEdit()
        self.exam_name.setPlaceholderText("e.g. Midterm Assessment")
        self.exam_name.setMinimumHeight(42)
        card_layout.addWidget(self.exam_name)

        # 2. Subject Code
        card_layout.addWidget(self._create_field_label("Subject Code", icon="&lt;/&gt;", required=True))
        self.subject_code = QLineEdit()
        self.subject_code.setPlaceholderText("e.g. CS601")
        self.subject_code.setMinimumHeight(42)
        card_layout.addWidget(self.subject_code)

        # 3. Subject Name
        card_layout.addWidget(self._create_field_label("Subject Name", icon="📖", required=True))
        self.subject_name = QLineEdit()
        self.subject_name.setPlaceholderText("e.g. Computer Networks")
        self.subject_name.setMinimumHeight(42)
        card_layout.addWidget(self.subject_name)

        # 4. Department
        card_layout.addWidget(self._create_field_label("Department", icon="🏛", required=True))
        self.department = QLineEdit()
        self.department.setPlaceholderText("e.g. Computer Science")
        self.department.setMinimumHeight(42)
        card_layout.addWidget(self.department)

        # 5. Semester
        card_layout.addWidget(self._create_field_label("Semester", icon="📚", required=True))
        self.semester = QComboBox()
        self.semester.setMinimumHeight(42)
        self.semester.addItems([
            "Select Semester",
            "Semester 1",
            "Semester 2",
            "Semester 3",
            "Semester 4",
            "Semester 5",
            "Semester 6",
            "Semester 7",
            "Semester 8"
        ])
        # Compatibility wrappers so legacy callers can call .text() and .setText()
        self.semester.text = lambda: (
            "" if self.semester.currentText() == "Select Semester" else self.semester.currentText()
        )
        def _set_combo_text(val):
            val_str = str(val).strip()
            idx = self.semester.findText(val_str)
            if idx >= 0:
                self.semester.setCurrentIndex(idx)
                return
            idx = self.semester.findText(f"Semester {val_str}")
            if idx >= 0:
                self.semester.setCurrentIndex(idx)
                return
            if val_str:
                self.semester.addItem(val_str)
                self.semester.setCurrentText(val_str)
        self.semester.setText = _set_combo_text
        card_layout.addWidget(self.semester)

        # 6. Exam Hall / Laboratory
        card_layout.addWidget(self._create_field_label("Exam Hall / Laboratory", icon="⚗", required=True))
        self.hall = QLineEdit()
        self.hall.setPlaceholderText("e.g. Lab 3")
        self.hall.setMinimumHeight(42)
        card_layout.addWidget(self.hall)

        # ----------------------------------------------------
        # Exam Schedule Highlighted Section Card
        # ----------------------------------------------------
        schedule_card = QFrame()
        schedule_card.setObjectName("card_exam_schedule")
        schedule_layout = QVBoxLayout(schedule_card)
        schedule_layout.setContentsMargins(16, 14, 16, 16)
        schedule_layout.setSpacing(10)

        # Section Header: Calendar Icon + Bold Title "Exam Schedule" (#1E3A8A)
        sched_header = QLabel("📅  <b style='color: #1E3A8A; font-size: 14px;'>Exam Schedule</b>")
        schedule_layout.addWidget(sched_header)

        # 3-Column Grid Layout: Date, Start Time, End Time
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(10)

        # Column 1: Exam Date
        date_vbox = QVBoxLayout()
        date_vbox.setSpacing(4)
        date_lbl = QLabel("<span style='color: #1E293B; font-weight: 600; font-size: 12px;'>Exam Date</span> <span style='color: #EF4444; font-weight: bold;'>*</span>")
        
        date_container = QFrame()
        date_container.setProperty("class", "scheduleInputBox")
        date_hlayout = QHBoxLayout(date_container)
        date_hlayout.setContentsMargins(10, 0, 4, 0)
        date_hlayout.setSpacing(6)
        date_icon = QLabel("📅")
        date_icon.setStyleSheet("font-size: 13px; background: transparent; border: none;")
        
        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setObjectName("examDateEdit")
        self.exam_date_edit.setCalendarPopup(True)
        self.exam_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setMinimumHeight(38)
        self.exam_date_edit.setStyleSheet("""
            QDateEdit {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #1E293B;
                padding: 0;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border: none;
            }
        """)
        date_hlayout.addWidget(date_icon)
        date_hlayout.addWidget(self.exam_date_edit, 1)

        date_vbox.addWidget(date_lbl)
        date_vbox.addWidget(date_container)
        grid_layout.addLayout(date_vbox, 1)

        # Column 2: Start Time
        start_vbox = QVBoxLayout()
        start_vbox.setSpacing(4)
        start_lbl = QLabel("<span style='color: #1E293B; font-weight: 600; font-size: 12px;'>Start Time</span> <span style='color: #EF4444; font-weight: bold;'>*</span>")
        
        start_container = QFrame()
        start_container.setProperty("class", "scheduleInputBox")
        start_hlayout = QHBoxLayout(start_container)
        start_hlayout.setContentsMargins(10, 0, 4, 0)
        start_hlayout.setSpacing(6)
        start_icon = QLabel("🕒")
        start_icon.setStyleSheet("font-size: 13px; background: transparent; border: none;")

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setObjectName("startTimeEdit")
        self.start_time_edit.setDisplayFormat("hh:mm AP")
        self.start_time_edit.setTime(QTime(10, 0))
        self.start_time_edit.setMinimumHeight(38)
        self.start_time_edit.setStyleSheet("""
            QTimeEdit {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #1E293B;
                padding: 0;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 16px;
                background: transparent;
                border: none;
            }
        """)
        start_hlayout.addWidget(start_icon)
        start_hlayout.addWidget(self.start_time_edit, 1)

        start_vbox.addWidget(start_lbl)
        start_vbox.addWidget(start_container)
        grid_layout.addLayout(start_vbox, 1)

        # Column 3: End Time
        end_vbox = QVBoxLayout()
        end_vbox.setSpacing(4)
        end_lbl = QLabel("<span style='color: #1E293B; font-weight: 600; font-size: 12px;'>End Time</span> <span style='color: #EF4444; font-weight: bold;'>*</span>")
        
        end_container = QFrame()
        end_container.setProperty("class", "scheduleInputBox")
        end_hlayout = QHBoxLayout(end_container)
        end_hlayout.setContentsMargins(10, 0, 4, 0)
        end_hlayout.setSpacing(6)
        end_icon = QLabel("🕒")
        end_icon.setStyleSheet("font-size: 13px; background: transparent; border: none;")

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setObjectName("endTimeEdit")
        self.end_time_edit.setDisplayFormat("hh:mm AP")
        self.end_time_edit.setTime(QTime(12, 0))
        self.end_time_edit.setMinimumHeight(38)
        self.end_time_edit.setStyleSheet("""
            QTimeEdit {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #1E293B;
                padding: 0;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 16px;
                background: transparent;
                border: none;
            }
        """)
        end_hlayout.addWidget(end_icon)
        end_hlayout.addWidget(self.end_time_edit, 1)

        end_vbox.addWidget(end_lbl)
        end_vbox.addWidget(end_container)
        grid_layout.addLayout(end_vbox, 1)

        schedule_layout.addLayout(grid_layout)

        # Duration Row
        dur_vbox = QVBoxLayout()
        dur_vbox.setSpacing(4)
        dur_lbl = QLabel("🕒  <span style='color: #1E293B; font-weight: 600; font-size: 12px;'>Duration</span> <span style='color: #64748B; font-weight: normal; font-size: 11px;'>(Automatically calculated)</span>")

        self.duration_container = QFrame()
        self.duration_container.setObjectName("durationContainer")
        self.duration_container.setMinimumHeight(42)
        dur_hlayout = QHBoxLayout(self.duration_container)
        dur_hlayout.setContentsMargins(12, 0, 14, 0)
        dur_hlayout.setSpacing(8)

        self.duration_input = QLineEdit()
        self.duration_input.setObjectName("durationField")
        self.duration_input.setReadOnly(True)
        self.duration_input.setFrame(False)

        lock_icon = QLabel("🔒")
        lock_icon.setObjectName("durationLockIcon")
        lock_icon.setStyleSheet("font-size: 13px; color: #64748B; background: transparent; border: none;")

        dur_hlayout.addWidget(self.duration_input, 1)
        dur_hlayout.addWidget(lock_icon)

        dur_helper = QLabel("ℹ  Duration is calculated based on the selected start and end time.")
        dur_helper.setObjectName("durationHelper")
        dur_helper.setStyleSheet("color: #64748B; font-size: 11px; margin-top: 1px;")

        dur_vbox.addWidget(dur_lbl)
        dur_vbox.addWidget(self.duration_container)
        dur_vbox.addWidget(dur_helper)
        schedule_layout.addLayout(dur_vbox)

        card_layout.addWidget(schedule_card)

        # ----------------------------------------------------
        # Primary Action Button
        # ----------------------------------------------------
        if self.exam:
            self.saveBtn = QPushButton("✈  Update Examination Session")
        else:
            self.saveBtn = QPushButton("✈  Save Publish Examination")

        self.saveBtn.setObjectName("btnSaveExam")
        self.saveBtn.setCursor(Qt.PointingHandCursor)
        self.saveBtn.setMinimumHeight(48)
        self.saveBtn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.saveBtn.clicked.connect(self.save_exam)

        card_layout.addWidget(self.saveBtn)

        scroll.setWidget(card)
        dialog_layout.addWidget(scroll)

        # ----------------------------------------------------
        # Retain Legacy Variable Handles for Zero Breakage
        # ----------------------------------------------------
        self.exam_date = self.exam_date_edit
        self.start_time = self.start_time_edit
        self.end_time = self.end_time_edit
        self.duration = self.duration_input
        self.btn_save = self.saveBtn

        # Legacy setter helpers if external tests or scripts call setText
        self.exam_date_edit.setText = lambda val: self.exam_date_edit.setDate(self._parse_date(val))
        self.start_time_edit.setText = lambda val: self.start_time_edit.setTime(self._parse_time(val))
        self.end_time_edit.setText = lambda val: self.end_time_edit.setTime(self._parse_time(val))

        # Connect signals for real-time automatic duration calculation
        self.start_time_edit.timeChanged.connect(self._calculate_duration)
        self.end_time_edit.timeChanged.connect(self._calculate_duration)

        # Initial duration calculation
        self._calculate_duration()

    ######################################################

    def _parse_date(self, date_str):
        if not date_str:
            return QDate.currentDate()
        d = QDate.fromString(str(date_str).strip(), "yyyy-MM-dd")
        if not d.isValid():
            d = QDate.fromString(str(date_str).strip(), "dd/MM/yyyy")
        if not d.isValid():
            d = QDate.fromString(str(date_str).strip(), "yyyy/MM/dd")
        return d if d.isValid() else QDate.currentDate()

    ######################################################

    def _parse_time(self, time_str):
        if not time_str:
            return QTime(10, 0)
        s = str(time_str).strip()
        t = QTime.fromString(s, "HH:mm:ss")
        if not t.isValid():
            t = QTime.fromString(s, "HH:mm")
        if not t.isValid():
            t = QTime.fromString(s, "hh:mm AP")
        if not t.isValid():
            t = QTime.fromString(s, "h:mm AP")
        if not t.isValid():
            t = QTime.fromString(s, "hh:mm ap")
        return t if t.isValid() else QTime(10, 0)

    ######################################################

    def _calculate_duration(self):
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()

        diff_seconds = start_time.secsTo(end_time)

        if diff_seconds > 0:
            minutes = diff_seconds // 60
            self._calculated_minutes = minutes
            self.duration_input.setText(f"{minutes} minutes")
            self.duration_container.setStyleSheet("""
                QFrame#durationContainer {
                    background-color: #F1F5F9;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    min-height: 42px;
                }
            """)
            self.duration_input.setStyleSheet("""
                QLineEdit#durationField {
                    color: #1E293B;
                    font-weight: 500;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            self._calculated_minutes = 0
            self.duration_input.setText("Invalid Time Range")
            self.duration_container.setStyleSheet("""
                QFrame#durationContainer {
                    background-color: #FEF2F2;
                    border: 1.5px solid #EF4444;
                    border-radius: 8px;
                    min-height: 42px;
                }
            """)
            self.duration_input.setStyleSheet("""
                QLineEdit#durationField {
                    color: #DC2626;
                    font-weight: 600;
                    background: transparent;
                    border: none;
                }
            """)

    ######################################################

    def load_exam(self):
        if not self.exam:
            return

        self.exam_name.setText(str(self.exam.get("exam_name", "")))
        self.subject_code.setText(str(self.exam.get("subject_code", "")))
        self.subject_name.setText(str(self.exam.get("subject_name", "")))
        self.department.setText(str(self.exam.get("department", "")))

        sem_val = str(self.exam.get("semester", "")).strip()
        if sem_val:
            idx = self.semester.findText(sem_val)
            if idx >= 0:
                self.semester.setCurrentIndex(idx)
            else:
                idx = self.semester.findText(f"Semester {sem_val}")
                if idx >= 0:
                    self.semester.setCurrentIndex(idx)
                else:
                    self.semester.addItem(sem_val)
                    self.semester.setCurrentText(sem_val)

        self.hall.setText(str(self.exam.get("hall", "")))

        exam_date_str = self.exam.get("exam_date", "")
        if exam_date_str:
            self.exam_date_edit.setDate(self._parse_date(exam_date_str))

        start_time_str = self.exam.get("start_time", "")
        if start_time_str:
            self.start_time_edit.setTime(self._parse_time(start_time_str))

        end_time_str = self.exam.get("end_time", "")
        if end_time_str:
            self.end_time_edit.setTime(self._parse_time(end_time_str))

        self._calculate_duration()

    ######################################################

    def save_exam(self):
        exam_name = self.exam_name.text().strip()
        subject_code = self.subject_code.text().strip()
        subject_name = self.subject_name.text().strip()
        department = self.department.text().strip()

        sem_text = self.semester.currentText().strip()
        semester = "" if sem_text == "Select Semester" else sem_text

        hall = self.hall.text().strip()

        exam_date = self.exam_date_edit.date().toString("yyyy-MM-dd")
        start_time = self.start_time_edit.time().toString("HH:mm:ss")
        end_time = self.end_time_edit.time().toString("HH:mm:ss")
        duration = self.duration_input.text().strip()

        # Check for invalid time range
        if self.end_time_edit.time() <= self.start_time_edit.time() or duration == "Invalid Time Range":
            QMessageBox.warning(
                self,
                "Invalid Schedule",
                "End Time must be greater than Start Time. Please adjust the examination schedule."
            )
            return

        if (
            not exam_name or
            not subject_code or
            not subject_name or
            not department or
            not semester or
            not hall or
            not exam_date or
            not start_time or
            not end_time or
            not duration
        ):
            QMessageBox.warning(
                self,
                "Validation Error",
                "All examination attributes are mandatory."
            )
            return

        data = {
            "exam_name": exam_name,
            "subject_code": subject_code,
            "subject_name": subject_name,
            "department": department,
            "semester": semester,
            "hall": hall,
            "exam_date": exam_date,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
        }

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        if self.exam:

            success = ExamModel.update_exam(
                self.exam["id"],
                data["exam_name"],
                data["subject_code"],
                data["subject_name"],
                data["department"],
                data["semester"],
                data["hall"],
                data["exam_date"],
                data["start_time"],
                data["end_time"],
                data["duration"]
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Examination session updated successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update examination record."
                )

        # ----------------------------------------------------
        # ADD
        # ----------------------------------------------------

        else:

            success = ExamModel.add_exam(
                data["exam_name"],
                data["subject_code"],
                data["subject_name"],
                data["department"],
                data["semester"],
                data["hall"],
                data["exam_date"],
                data["start_time"],
                data["end_time"],
                data["duration"]
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Examination session scheduled successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to schedule examination."
                )