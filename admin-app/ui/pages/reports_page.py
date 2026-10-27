"""Read-only exam analytics for the existing Admin dashboard."""

import csv
from datetime import datetime, timezone
from html import escape

from PyQt5.QtCore import QDate, QRectF, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QFileDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QMenu, QMessageBox,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from database.database import get_connection
from models.exam_model import ExamModel
from models.result_model import ResultModel


PASS_PERCENTAGE = 40.0  # Report-only threshold requested by the administrator.
COMPLETED = {"SUBMITTED", "AUTO_SUBMITTED"}
BLUE = "#3D4CFF"
INK = "#10245C"
MUTED = "#6980AF"


def report_icon(kind, size=29, color=BLUE, background="#EEF1FF"):
    """Small vector icons that do not depend on installed symbol fonts."""
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(size * 2 / 28, size * 2 / 28)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(background))
    painter.drawRoundedRect(QRectF(0, 0, 28, 28), 7, 7)
    painter.setPen(QPen(QColor(color), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)
    if kind == "users":
        painter.drawEllipse(QRectF(10, 6, 7, 7))
        painter.drawRoundedRect(QRectF(7, 15, 14, 7), 3, 3)
    elif kind == "check":
        painter.drawEllipse(QRectF(5, 5, 18, 18))
        painter.drawLine(9, 14, 13, 18)
        painter.drawLine(13, 18, 19, 10)
    elif kind == "pie":
        painter.drawArc(QRectF(5, 5, 18, 18), 100 * 16, 260 * 16)
        painter.drawLine(14, 5, 14, 14)
        painter.drawLine(14, 14, 23, 14)
    elif kind == "clock":
        painter.drawEllipse(QRectF(5, 5, 18, 18))
        painter.drawLine(14, 8, 14, 14)
        painter.drawLine(14, 14, 18, 17)
    elif kind == "document":
        painter.drawRoundedRect(QRectF(7, 4, 14, 20), 2, 2)
        for y in (10, 14, 18):
            painter.drawLine(10, y, 18, y)
    elif kind == "search":
        painter.drawEllipse(QRectF(5, 5, 12, 12))
        painter.drawLine(16, 16, 23, 23)
    elif kind == "reset":
        painter.drawArc(QRectF(6, 6, 16, 16), 40 * 16, 290 * 16)
        painter.drawLine(22, 5, 22, 11)
        painter.drawLine(22, 11, 16, 11)
    elif kind == "download":
        painter.drawLine(14, 5, 14, 18)
        painter.drawLine(9, 13, 14, 18)
        painter.drawLine(14, 18, 19, 13)
        painter.drawLine(6, 20, 6, 23)
        painter.drawLine(6, 23, 22, 23)
        painter.drawLine(22, 23, 22, 20)
    elif kind == "print":
        painter.drawRect(QRectF(8, 4, 12, 7))
        painter.drawRoundedRect(QRectF(4, 11, 20, 10), 2, 2)
        painter.drawRect(QRectF(8, 17, 12, 7))
    else:
        for x, height in ((6, 9), (12, 17), (18, 13)):
            painter.fillRect(QRectF(x, 23 - height, 4, height), QColor(color))
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


def number(value):
    return f"{float(value or 0):g}"


def local_timestamp(value):
    """Attempt timestamps are written by SQLite datetime('now') in UTC."""
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.astimezone()
    except (TypeError, ValueError):
        return None


class ScoreChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = [0] * 5
        self.setMinimumHeight(146)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setToolTip("Completed attempts by percentage: 0–<20, 20–<40, "
                        "40–<60, 60–<80, 80–100. Negative scores use the first band.")

    def set_scores(self, percentages):
        self.values = [0] * 5
        for value in percentages:
            self.values[min(4, max(0, int(value // 20)))] += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Segoe UI", 8))
        plot = QRectF(38, 12, max(50, self.width() - 49), max(40, self.height() - 48))
        highest = max(1, max(self.values))
        maximum = highest * 1.2
        for value in sorted({0, round(highest / 2), highest}):
            y = plot.bottom() - plot.height() * value / maximum
            painter.setPen(QColor("#E7EEFC"))
            painter.drawLine(int(plot.left()), int(y), int(plot.right()), int(y))
            painter.setPen(QColor(MUTED))
            painter.drawText(QRectF(0, y - 8, 29, 16), Qt.AlignRight, str(value))
        for index, count in enumerate(self.values):
            cell = plot.width() / 5
            x = plot.left() + index * cell
            height = plot.height() * count / maximum
            bar = QRectF(x + cell * .2, plot.bottom() - height, cell * .6, height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#4285FF"))
            if count:
                painter.drawRoundedRect(bar, 3, 3)
            painter.setPen(QColor(INK))
            painter.drawText(QRectF(x, bar.top() - 17, cell, 16), Qt.AlignCenter, str(count))
            painter.drawText(QRectF(x, plot.bottom() + 5, cell, 16), Qt.AlignCenter,
                             ("0–20", "20–40", "40–60", "60–80", "80–100")[index])
        painter.setPen(QColor(MUTED))
        painter.drawText(QRectF(0, self.height() - 16, self.width(), 16), Qt.AlignCenter,
                         "Score range (%) · completed attempts")


class PassChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.passed = self.failed = 0
        self.setMinimumHeight(146)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_counts(self, passed, failed):
        self.passed, self.failed = passed, failed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        diameter = min(self.height() - 22, self.width() * .48)
        rect = QRectF(10, (self.height() - diameter) / 2, diameter, diameter)
        total = self.passed + self.failed
        width = max(13, diameter * .14)
        painter.setPen(QPen(QColor("#EBF0FA"), width))
        painter.drawEllipse(rect.adjusted(width / 2, width / 2, -width / 2, -width / 2))
        ring = rect.adjusted(width / 2, width / 2, -width / 2, -width / 2)
        if total:
            painter.setPen(QPen(QColor("#FF6379"), width))
            painter.drawEllipse(ring)
            painter.setPen(QPen(QColor("#1CB87A"), width))
            painter.drawArc(ring, 90 * 16, -round(360 * 16 * self.passed / total))
        painter.setPen(QColor(INK))
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        percent = f"{self.passed / total * 100:.0f}%" if total else "—"
        painter.drawText(rect.adjusted(0, -9, 0, -9), Qt.AlignCenter, percent)
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(rect.adjusted(0, 27, 0, 27), Qt.AlignCenter,
                         "Passed" if total else "No results")
        x = diameter + 26
        for offset, title, count, color in (
            (-19, "Passed", self.passed, "#1CB87A"),
            (19, "Failed", self.failed, "#FF6379"),
        ):
            y = self.height() / 2 + offset
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x, y - 4, 8, 8))
            painter.setPen(QColor(INK))
            suffix = f"{count} ({count / total * 100:.0f}%)" if total else "0"
            painter.drawText(QRectF(x + 15, y - 9, self.width() - x - 17, 20),
                             Qt.AlignLeft, f"{title}  {suffix}")


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("reportsPage")
        self.exams = []
        self.snapshot = None
        self._build_ui()
        self._apply_style()
        self.refresh_data(reset=True)

    @staticmethod
    def _label(text, name="reportText"):
        label = QLabel(text)
        label.setObjectName(name)
        label.setWordWrap(True)
        return label

    def _card(self, title=None, icon="chart"):
        frame = QFrame()
        frame.setProperty("reportCard", True)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 13)
        layout.setSpacing(10)
        if title:
            row = QHBoxLayout()
            badge = self._label("", "reportIcon")
            badge.setPixmap(report_icon(icon))
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(29, 29)
            row.addWidget(badge)
            row.addWidget(self._label(title, "reportSection"), 1)
            layout.addLayout(row)
        return frame, layout

    @staticmethod
    def _table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setMinimumSectionSize(45)
        table.horizontalHeader().setFixedHeight(32)
        table.verticalHeader().setDefaultSectionSize(32)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFixedHeight(132)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return table

    def _button(self, text, callback, primary=False, icon=None):
        button = QPushButton(text)
        button.setObjectName("reportPrimary" if primary else "reportButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(36)
        if icon:
            button.setIcon(QIcon(report_icon(icon, 18, "#FFFFFF" if primary else MUTED, "transparent")))
            button.setIconSize(QSize(16, 16))
        button.clicked.connect(callback)
        return button

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(13)
        heading = QHBoxLayout()
        badge = self._label("", "reportHeroIcon")
        badge.setPixmap(report_icon("chart", 45))
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(45, 45)
        heading.addWidget(badge)
        titles = QVBoxLayout()
        titles.setSpacing(3)
        titles.addWidget(self._label("Reports & Analytics", "reportTitle"))
        titles.addWidget(self._label("Examination performance and system insights", "reportMuted"))
        heading.addLayout(titles, 1)
        self.load_status = self._label("", "reportMuted")
        heading.addWidget(self.load_status)
        root.addLayout(heading)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setMinimumWidth(1010)
        body = QVBoxLayout(content)
        body.setContentsMargins(0, 0, 2, 0)
        body.setSpacing(12)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        filters, filters_layout = self._card()
        row = QHBoxLayout()
        exam_box = QVBoxLayout()
        exam_box.addWidget(self._label("Exam", "reportField"))
        self.exam_select = QComboBox()
        self.exam_select.setMinimumWidth(225)
        exam_box.addWidget(self.exam_select)
        row.addLayout(exam_box, 3)
        dates = QVBoxLayout()
        dates.addWidget(self._label("Date Range", "reportField"))
        date_row = QHBoxLayout()
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to = QDateEdit(calendarPopup=True)
        for edit in (self.date_from, self.date_to):
            edit.setDisplayFormat("dd MMM yyyy")
            edit.setToolTip("Filter by the scheduled examination date")
            edit.setMinimumWidth(120)
        date_row.addWidget(self.date_from, 1)
        arrow = self._label("→", "reportMuted")
        arrow.setFixedWidth(18)
        arrow.setAlignment(Qt.AlignCenter)
        date_row.addWidget(arrow)
        date_row.addWidget(self.date_to, 1)
        dates.addLayout(date_row)
        row.addLayout(dates, 3)
        row.addWidget(self._button("Apply Filters", self.apply_filters, True, "search"), 0, Qt.AlignBottom)
        row.addWidget(self._button("Reset", lambda: self.refresh_data(reset=True), icon="reset"), 0, Qt.AlignBottom)
        row.addStretch(1)
        self.export_button = self._button("Export Report", self.export_pdf, True, "download")
        self.export_button.setMinimumWidth(152)
        menu = QMenu(self.export_button)
        menu.addAction("PDF document", self.export_pdf)
        menu.addAction("CSV spreadsheet", self.export_csv)
        menu.addAction("Print report", self.print_report)
        self.export_button.setMenu(menu)
        row.addWidget(self.export_button, 0, Qt.AlignBottom)
        filters_layout.addLayout(row)
        body.addWidget(filters)

        summary = QHBoxLayout()
        summary.setSpacing(12)
        overview, layout = self._card("Exam Overview", "document")
        overview.setMinimumWidth(330)
        self.exam_name = self._label("—", "reportMuted")
        layout.addWidget(self.exam_name)
        metadata = QHBoxLayout()
        self.overview_values = {}
        for key, title in (("date", "Date"), ("duration", "Duration"),
                           ("questions", "Total Questions"), ("marks", "Total Marks")):
            column = QVBoxLayout()
            column.addWidget(self._label(title, "reportSmall"))
            label = self._label("—")
            self.overview_values[key] = label
            column.addWidget(label)
            metadata.addLayout(column, 1)
        layout.addLayout(metadata)
        summary.addWidget(overview, 3)
        self.metric_values = {}
        for key, title, icon, tint, note in (
            ("students", "Total Students", "users", "blue", "Assigned / recorded participants"),
            ("completed", "Completed Attempts", "check", "green", "Includes auto-submitted attempts"),
            ("average", "Average Score", "chart", "purple", "Completed attempts only"),
            ("pass_rate", "Pass Rate", "pie", "green", "Pass threshold: 40%"),
        ):
            card, layout = self._card()
            card.setProperty("metricTint", tint)
            icon_label = self._label("", "reportMetricIcon")
            icon_label.setPixmap(report_icon(icon, 34, "#1CB87A" if tint == "green" else BLUE,
                                            "#DDF7EB" if tint == "green" else "#E7ECFF"))
            layout.addWidget(icon_label)
            layout.addWidget(self._label(title))
            value = self._label("—", "reportMetricValue")
            self.metric_values[key] = value
            layout.addWidget(value)
            layout.addWidget(self._label(note, "reportSmall"))
            summary.addWidget(card, 1)
        body.addLayout(summary)

        charts = QHBoxLayout()
        charts.setSpacing(12)
        card, layout = self._card("Score Distribution")
        self.score_chart = ScoreChart()
        layout.addWidget(self.score_chart, 1)
        charts.addWidget(card, 4)
        card, layout = self._card("Pass / Fail Analysis", "pie")
        self.pass_chart = PassChart()
        layout.addWidget(self.pass_chart, 1)
        charts.addWidget(card, 3)
        card, layout = self._card("Average Score by Subject")
        header = QHBoxLayout()
        header.addWidget(self._label("Subject", "reportSmall"), 1)
        header.addWidget(self._label("Average Score", "reportSmall"))
        layout.addLayout(header)
        self.subject_name = self._label("—")
        self.subject_average = self._label("—")
        subject_row = QHBoxLayout()
        subject_row.addWidget(self.subject_name, 1)
        subject_row.addWidget(self.subject_average)
        layout.addLayout(subject_row)
        self.subject_bar = QProgressBar()
        self.subject_bar.setRange(0, 1000)
        self.subject_bar.setTextVisible(False)
        self.subject_bar.setFixedHeight(7)
        layout.addWidget(self.subject_bar)
        layout.addStretch(1)
        layout.addWidget(self._label("Selected exam · completed attempts", "reportSmall"))
        charts.addWidget(card, 3)
        body.addLayout(charts)

        tables = QGridLayout()
        tables.setHorizontalSpacing(12)
        tables.setVerticalSpacing(12)
        student_card, layout = self._card("Student Performance", "users")
        self.student_table = self._table(
            ["#", "Student Name", "Register No.", "Exam", "Score", "%", "Status"]
        )
        self.student_table.setObjectName("studentPerformanceTable")
        self.student_table.setMinimumHeight(240)
        self.student_table.setMaximumHeight(16777215)
        self.student_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.student_table.horizontalHeader().setFixedHeight(44)
        self.student_table.verticalHeader().setDefaultSectionSize(46)
        self.student_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.student_table.setColumnWidth(0, 42)
        for column in (1, 2):
            self.student_table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)
        layout.addWidget(self.student_table, 1)
        self.student_note = self._label("", "reportSmall")
        layout.addWidget(self.student_note)
        tables.addWidget(student_card, 0, 0, 2, 1)
        question_card, layout = self._card("Question Performance", "document")
        self.question_table = self._table(["Question", "Correct %", "Total Students"])
        layout.addWidget(self.question_table)
        layout.addWidget(self._label("Unanswered questions count as incorrect; completed attempts only.", "reportSmall"))
        tables.addWidget(question_card, 0, 1)
        export_card, layout = self._card()
        export_row = QHBoxLayout()
        export_text = QVBoxLayout()
        export_text.addWidget(self._label("Generate Report", "reportSection"))
        export_text.addWidget(self._label("Download the selected examination report.", "reportSmall"))
        export_row.addLayout(export_text, 1)
        self.pdf_button = self._button("PDF", self.export_pdf, True, "document")
        self.csv_button = self._button("CSV", self.export_csv, icon="document")
        self.print_button = self._button("Print", self.print_report, icon="print")
        for button in (self.pdf_button, self.csv_button, self.print_button):
            export_row.addWidget(button)
        layout.addLayout(export_row)
        tables.addWidget(export_card, 1, 1)
        tables.setColumnStretch(0, 3)
        tables.setColumnStretch(1, 2)
        body.addLayout(tables)
        body.addStretch(1)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#reportsPage, QWidget#reportsPage QScrollArea,
            QWidget#reportsPage QScrollArea > QWidget > QWidget { background: #F8FAFF; }
            QWidget#reportsPage { font-family: 'Segoe UI'; font-size: 11px; color: #10245C; }
            QWidget#reportsPage QFrame[reportCard="true"] {
                background: #FFFFFF; border: 1px solid #DFE8FA; border-radius: 9px;
            }
            QWidget#reportsPage QFrame[metricTint="blue"] { background: #F1F7FF; }
            QWidget#reportsPage QFrame[metricTint="green"] { background: #F0FBF7; border-color: #D8F1E6; }
            QWidget#reportsPage QFrame[metricTint="purple"] { background: #F6F3FF; border-color: #E5DDFF; }
            QWidget#reportsPage QLabel { color: #10245C; border: none; background: transparent; }
            QWidget#reportsPage QLabel#reportTitle { font-size: 23px; font-weight: 700; }
            QWidget#reportsPage QLabel#reportSection { font-size: 12px; font-weight: 600; }
            QWidget#reportsPage QLabel#reportField { font-size: 11px; font-weight: 600; }
            QWidget#reportsPage QLabel#reportMuted { color: #6980AF; font-size: 11px; }
            QWidget#reportsPage QLabel#reportSmall { color: #6980AF; font-size: 9px; }
            QWidget#reportsPage QLabel#reportIcon, QWidget#reportsPage QLabel#reportHeroIcon {
                color: #3D4CFF; background: #EEF1FF; border-radius: 8px; font-size: 20px;
            }
            QWidget#reportsPage QLabel#reportHeroIcon { font-size: 28px; }
            QWidget#reportsPage QLabel#reportMetricIcon { color: #3D4CFF; font-size: 23px; }
            QWidget#reportsPage QLabel#reportMetricValue { font-size: 22px; font-weight: 600; }
            QWidget#reportsPage QPushButton { border: 1px solid #D9E3FA; border-radius: 7px;
                padding: 6px 13px; color: #173068; background: #FFFFFF; font-weight: 600; }
            QWidget#reportsPage QPushButton:hover { background: #EFF3FF; border-color: #A8B9F7; }
            QWidget#reportsPage QPushButton#reportPrimary { background: #3D4CFF; color: white; border-color: #3D4CFF; }
            QWidget#reportsPage QPushButton#reportPrimary:hover { background: #2E3BE0; }
            QWidget#reportsPage QPushButton::menu-indicator { subcontrol-position: right center; right: 5px; }
            QWidget#reportsPage QPushButton:disabled { background: #EEF1F7; color: #A1ABC0; border-color: #E4E9F2; }
            QWidget#reportsPage QComboBox, QWidget#reportsPage QDateEdit {
                background: white; color: #173068; border: 1px solid #D9E3FA;
                border-radius: 6px; padding: 7px; min-height: 20px;
            }
            QWidget#reportsPage QTableWidget { background: white; alternate-background-color: #FAFCFF;
                color: #10245C; border: 1px solid #EDF2FB; border-radius: 5px;
                gridline-color: #EDF2FB; selection-background-color: #EDF1FF; selection-color: #10245C; font-size: 10px; }
            QWidget#reportsPage QHeaderView::section { background: #F1F6FF; color: #173068;
                border: 0; padding: 7px 3px; font-size: 9px; font-weight: 600; }
            QWidget#reportsPage QTableWidget::item { padding: 4px; border-bottom: 1px solid #EDF2FB; }
            QWidget#reportsPage QTableWidget#studentPerformanceTable {
                font-size: 14px; color: #142B5F;
            }
            QWidget#reportsPage QTableWidget#studentPerformanceTable QHeaderView::section {
                font-size: 13px; font-weight: 700; color: #142B5F; padding: 8px 4px;
            }
            QWidget#reportsPage QTableWidget#studentPerformanceTable::item {
                padding: 7px 5px;
            }
            QWidget#reportsPage QProgressBar { background: #EDF2FC; border: 0; border-radius: 3px; }
            QWidget#reportsPage QProgressBar::chunk { background: #4A50FF; border-radius: 3px; }
            QWidget#reportsPage QScrollBar:vertical { background: #F5F7FC; width: 7px; margin: 0; }
            QWidget#reportsPage QScrollBar::handle:vertical { background: #DCE4F2; border-radius: 3px; min-height: 20px; }
            QWidget#reportsPage QScrollBar::add-line:vertical, QWidget#reportsPage QScrollBar::sub-line:vertical { height: 0; }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self, reset=False):
        previous = self.exam_select.currentData()
        try:
            self.exams = [dict(row) for row in ExamModel.get_all_exams()]
        except Exception as error:
            print(">>> Reports exam refresh error:", error)
            self._clear("Examination list unavailable. Use Reset to retry.")
            return
        self.exam_select.clear()
        for exam in self.exams:
            title = " · ".join(str(part) for part in
                               (exam.get("subject_name"), exam.get("exam_name")) if part)
            self.exam_select.addItem(title or f"Exam {exam['id']}", exam["id"])
        if self.exams:
            preferred = previous if not reset else None
            if preferred not in {exam["id"] for exam in self.exams}:
                demo = next((exam for exam in self.exams if
                             "computer networks" in str(exam.get("subject_name", "")).lower()), self.exams[-1])
                preferred = demo["id"]
            self.exam_select.setCurrentIndex(self.exam_select.findData(preferred))
        if reset or not hasattr(self, "_dates_initialized"):
            dates = [QDate.fromString(str(exam.get("exam_date", "")), "yyyy-MM-dd") for exam in self.exams]
            dates = [date for date in dates if date.isValid()]
            self.date_from.setDate(min(dates) if dates else QDate.currentDate())
            self.date_to.setDate(max(dates) if dates else QDate.currentDate())
            self._dates_initialized = True
        self.apply_filters()

    def apply_filters(self):
        if self.date_from.date() > self.date_to.date():
            self._clear("Choose a start date before the end date.")
            return
        exam_id = self.exam_select.currentData()
        exam = next((row for row in self.exams if row["id"] == exam_id), None)
        if exam is None:
            self._clear("No examinations available.")
            return
        date = QDate.fromString(str(exam.get("exam_date", "")), "yyyy-MM-dd")
        if not date.isValid() or not self.date_from.date() <= date <= self.date_to.date():
            self._clear("No examination matches the selected date range.")
            return
        connection = None
        try:
            connection = get_connection()
            roster = [dict(row) for row in connection.execute("""
                SELECT DISTINCT s.id, s.name, s.register_no
                FROM students s JOIN student_assignment sa ON sa.student_id = s.id
                WHERE sa.exam_id = ? ORDER BY s.register_no
            """, (exam_id,))]
            results = [dict(row) for row in ResultModel.get_exam_results(exam_id)]
            questions = [dict(row) for row in ExamModel.get_exam_questions(exam_id)]
            completed = [row for row in results if row["status"] in COMPLETED]
            answers = {row["attempt_id"]: [dict(answer) for answer in
                       ResultModel.get_result_answers(row["attempt_id"])] for row in completed}
            known = {row["id"] for row in roster}
            roster.extend({"id": row["student_id"], "name": row["student_name"],
                           "register_no": row["register_no"]} for row in results if row["student_id"] not in known)
            self.snapshot = {"exam": exam, "roster": roster, "results": results,
                             "questions": questions, "completed": completed, "answers": answers}
            self._render()
            self.load_status.setText("Updated from saved examination data")
        except Exception as error:
            print(">>> Reports data refresh error:", error)
            self._clear("Report data unavailable. Use Apply Filters to retry.")
        finally:
            if connection is not None:
                connection.close()

    def _clear(self, message):
        self.snapshot = None
        self.load_status.setText(message)
        self.exam_name.setText(message)
        for label in list(self.overview_values.values()) + list(self.metric_values.values()):
            label.setText("—")
        self.student_table.setRowCount(0)
        self.question_table.setRowCount(0)
        self.student_note.setText(message)
        self.score_chart.set_scores([])
        self.pass_chart.set_counts(0, 0)
        self.subject_name.setText("—")
        self.subject_average.setText("—")
        self.subject_bar.setValue(0)
        self._enable_exports(False)

    def _enable_exports(self, enabled):
        for button in (self.export_button, self.pdf_button, self.csv_button, self.print_button):
            button.setEnabled(enabled)

    @staticmethod
    def _percentage(row):
        total = float(row["total_marks"] or 0)
        return float(row["score"] or 0) / total * 100 if total > 0 else None

    def _render(self):
        data = self.snapshot
        exam, completed = data["exam"], data["completed"]
        self.exam_name.setText(" · ".join(str(value) for value in
                               (exam.get("subject_name"), exam.get("exam_name")) if value))
        date = QDate.fromString(str(exam["exam_date"]), "yyyy-MM-dd")
        meta = {"date": date.toString("dd MMM yyyy"), "duration": str(exam.get("duration") or "—"),
                "questions": str(len(data["questions"])),
                "marks": number(sum(float(q["marks"] or 0) for q in data["questions"]))}
        for key, value in meta.items():
            self.overview_values[key].setText(value)
        percentages = [self._percentage(row) for row in completed]
        percentages = [value for value in percentages if value is not None]
        passed = sum(value >= PASS_PERCENTAGE for value in percentages)
        average = sum(percentages) / len(percentages) if percentages else None
        values = {"students": str(len(data["roster"])), "completed": str(len(completed)),
                  "average": f"{average:.1f}%" if average is not None else "—",
                  "pass_rate": f"{passed / len(percentages) * 100:.0f}%" if percentages else "—"}
        for key, value in values.items():
            self.metric_values[key].setText(value)
        self.score_chart.set_scores(percentages)
        self.pass_chart.set_counts(passed, len(percentages) - passed)
        self.subject_name.setText(str(exam.get("subject_name") or "Unspecified subject"))
        self.subject_average.setText(values["average"])
        self.subject_bar.setValue(round(max(0, min(100, average or 0)) * 10))
        results = {row["student_id"]: row for row in data["results"]}
        student_rows = []
        for index, student in enumerate(data["roster"], 1):
            result = results.get(student["id"])
            percentage = self._percentage(result) if result else None
            status = (str(result["status"]).replace("_", " ").title() if result else "Not started")
            if result and result["status"] in COMPLETED:
                status = ("Passed" if percentage >= PASS_PERCENTAGE else "Failed") if percentage is not None else "Ungraded"
            student_rows.append([str(index), student["name"], student["register_no"],
                                 exam.get("subject_name") or exam["exam_name"],
                                 f"{number(result['score'])} / {number(result['total_marks'])}" if result else "—",
                                 f"{percentage:.1f}%" if percentage is not None else "—", status])
        data["student_rows"] = student_rows
        self._fill_table(self.student_table, student_rows)
        for row_index, row in enumerate(student_rows):
            status = row[-1]
            if status in ("Passed", "Failed"):
                badge = QLabel(status)
                badge.setAlignment(Qt.AlignCenter)
                badge.setStyleSheet(
                    "font-size: 13px; font-weight: 700; padding: 6px 12px; border-radius: 12px; "
                    + ("color: #08794F; background: #DDF7EB;" if status == "Passed"
                       else "color: #B6344C; background: #FDE7EC;")
                )
                badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                holder = QWidget()
                badge_layout = QHBoxLayout(holder)
                badge_layout.setContentsMargins(2, 2, 2, 2)
                badge_layout.addWidget(badge, 0, Qt.AlignCenter)
                self.student_table.item(row_index, 6).setForeground(QColor(0, 0, 0, 0))
                self.student_table.setCellWidget(row_index, 6, holder)
        self.student_note.setText(f"{len(student_rows)} student{'s' if len(student_rows) != 1 else ''} · Pass threshold: 40% · Saved results")
        question_rows = []
        for index, question in enumerate(data["questions"], 1):
            correct = sum(any(answer["question_id"] == question["question_id"] and answer["is_correct"] == 1
                              for answer in records) for records in data["answers"].values())
            question_rows.append([f"Q{index}", f"{correct / len(completed) * 100:.0f}%" if completed else "—", str(len(completed))])
        data["question_rows"] = question_rows
        self._fill_table(self.question_table, question_rows)
        for index, question in enumerate(data["questions"]):
            self.question_table.item(index, 0).setToolTip(str(question["question_text"]))
        started = [local_timestamp(row["started_at"]) for row in data["results"]]
        submitted = [local_timestamp(row["submitted_at"]) for row in completed]
        started, submitted = [v for v in started if v], [v for v in submitted if v]
        durations = []
        for row in completed:
            start, end = local_timestamp(row["started_at"]), local_timestamp(row["submitted_at"])
            if start and end and end >= start:
                durations.append((end - start).total_seconds() / 60)
        activity = {"started": min(started).strftime("%d %b %Y, %I:%M %p") if started else "—",
                    "submitted": max(submitted).strftime("%d %b %Y, %I:%M %p") if submitted else "—",
                    "used": f"{sum(durations) / len(durations):.1f} min" + (" avg." if len(durations) > 1 else "") if durations else "—",
                    "total": str(exam.get("duration") or "—")}
        data["activity"] = activity
        self._enable_exports(True)

    @staticmethod
    def _fill_table(table, rows):
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, value in enumerate(row):
                item = QTableWidgetItem(str(value or "—"))
                item.setToolTip(str(value or "—"))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                table.setItem(row_index, column, item)

    def _report_html(self):
        data = self.snapshot
        def table(headers, rows):
            return "<table width='100%' cellspacing='0' cellpadding='7'><tr>" + "".join(
                f"<th bgcolor='#EEF3FF'>{escape(str(value))}</th>" for value in headers
            ) + "</tr>" + "".join("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>" for row in rows) + "</table>"
        return (
            "<html><body style='font-family:Segoe UI;color:#10245C;font-size:10pt'>"
            "<h1>Reports &amp; Analytics</h1>"
            f"<h2>{escape(self.exam_name.text())}</h2>"
            f"<p>Scheduled date: {escape(self.overview_values['date'].text())} · "
            f"Duration: {escape(self.overview_values['duration'].text())} · "
            f"Questions: {self.overview_values['questions'].text()} · Marks: {self.overview_values['marks'].text()}</p>"
            f"<p>Students: {self.metric_values['students'].text()} · Completed: {self.metric_values['completed'].text()} · "
            f"Average: {self.metric_values['average'].text()} · Pass rate: {self.metric_values['pass_rate'].text()}</p>"
            "<p>Report pass threshold: 40%. Averages and pass rate use graded, completed attempts.</p>"
            "<h3>Student Performance</h3>" + table(
                ["#", "Student", "Register No.", "Exam", "Score", "%", "Status"], data["student_rows"])
            + "<h3>Question Performance</h3>" + table(
                ["Question", "Correct %", "Completed Students"], data["question_rows"])
            + "<h3>Exam Activity</h3>" + table(
                ["Started At", "Submitted At", "Duration Used", "Total Time"],
                [[data["activity"][key] for key in ("started", "submitted", "used", "total")]])
            + "</body></html>"
        )

    def export_csv(self):
        if not self.snapshot:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "exam-report.csv", "CSV files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                writer.writerow(["#", "Student Name", "Register No.", "Exam", "Score", "Percentage", "Status"])
                for row in self.snapshot["student_rows"]:
                    writer.writerow(["'" + str(value) if str(value).startswith(("=", "+", "-", "@")) else value for value in row])
            self.load_status.setText("CSV report exported.")
        except (OSError, csv.Error) as error:
            QMessageBox.warning(self, "Export Report", f"Unable to export report: {error}")

    def export_pdf(self):
        if not self.snapshot:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "exam-report.pdf", "PDF files (*.pdf)")
        if not path:
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Landscape)
        self._print_document(printer)

    def print_report(self):
        if not self.snapshot:
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOrientation(QPrinter.Landscape)
        if QPrintDialog(printer, self).exec_() == QPrintDialog.Accepted:
            self._print_document(printer)

    def _print_document(self, printer):
        try:
            document = QTextDocument()
            document.setHtml(self._report_html())
            document.print_(printer)
            if printer.printerState() == QPrinter.Error:
                raise OSError("The selected printer or output file is unavailable.")
            self.load_status.setText("Report sent to output.")
        except Exception as error:
            print(">>> Reports export error:", error)
            QMessageBox.warning(self, "Export Report", f"Unable to export report: {error}")
