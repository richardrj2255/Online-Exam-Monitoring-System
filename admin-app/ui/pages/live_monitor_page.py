"""Live proctoring dashboard. TCP camera transport is owned by CameraServer."""

from datetime import datetime, timedelta
from html import escape
import math
import re
import traceback

import cv2
from PyQt5.QtCore import QObject, QRectF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QImage, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)

from database.database import DB_PATH, get_connection
from models.exam_model import ExamModel
from streaming.camera_server import CameraServer
from ui.theme_manager import get_theme_palette, register_theme_listener


class CameraSignalBridge(QObject):
    frame_received = pyqtSignal(str, object)
    student_disconnected = pyqtSignal(str)


class CameraScreen(QLabel):
    """A 16:9 screen that clips incoming frames to rounded corners."""

    def __init__(self):
        super().__init__()
        self._source_pixmap = None
        self.setObjectName("cameraScreen")
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumHeight(145)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return max(145, int(width * 9 / 16))

    def show_frame(self, pixmap):
        self._source_pixmap = pixmap
        self.clear()
        self.update()

    def show_message(self, message):
        self._source_pixmap = None
        self.setTextFormat(Qt.RichText)
        self.setText(message)
        self.update()

    def paintEvent(self, event):
        if self._source_pixmap is None:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QColor(get_theme_palette()["camera_screen_bg"]))
        scaled = self._source_pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        painter.drawPixmap(
            (self.width() - scaled.width()) // 2,
            (self.height() - scaled.height()) // 2,
            scaled,
        )


class StudentCameraCard(QFrame):
    """A persistent camera slot whose video surface survives state changes."""

    def __init__(self, slot_id, register_no=None, student_name="", subject="", semester=""):
        super().__init__()
        self.slot_id = slot_id
        self.register_no = register_no
        self.student_name = student_name
        self.subject = subject
        self.semester = semester
        self.state = "waiting"
        self.is_disconnected = False
        self._flagged = False
        self.setObjectName(f"camera_card_{slot_id}")
        self.setProperty("monitorCard", True)
        self.setMinimumWidth(195)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        self.cameraTitle = QLabel(f"◉  Camera {slot_id}")
        self.cameraTitle.setObjectName("cameraTitle")
        self.statusLabel = QLabel()
        header.addWidget(self.cameraTitle)
        header.addStretch()
        header.addWidget(self.statusLabel)
        layout.addLayout(header)

        self.cameraLabel = CameraScreen()
        layout.addWidget(self.cameraLabel)
        footer = QHBoxLayout()
        footer.setSpacing(5)
        self.registerLabel = QLabel("Awaiting student")
        self.subjectLabel = QLabel("—")
        self.semesterLabel = QLabel("—")
        self.liveDot = QLabel("●")
        for label, stretch in (
            (self.registerLabel, 2), (self.subjectLabel, 3), (self.semesterLabel, 1)
        ):
            label.setObjectName("cameraMeta")
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            footer.addWidget(label, stretch)
        footer.addWidget(self.liveDot)
        layout.addLayout(footer)
        self.set_waiting()

    def set_student(self, register_no, student_name="", subject="", semester=""):
        self.register_no = str(register_no)
        self.student_name = student_name or "Unknown Student"
        self.subject = subject or "Unknown Subject"
        self.semester = str(semester or "—")
        self.registerLabel.setText(self.register_no)
        self.subjectLabel.setText(self.subject)
        self.semesterLabel.setText(
            f"Sem {self.semester}" if self.semester != "—" else "—"
        )
        self.setToolTip(f"{self.student_name} · {self.register_no} · {self.subject}")

    def _set_state(self, state, message=None):
        self.state = state
        self.is_disconnected = state == "offline"
        self.statusLabel.setText({
            "waiting": "● Waiting", "normal": "● Normal",
            "violation": "● Violation", "offline": "● Offline",
            "submitted": "● Completed",
        }[state])
        if message is not None:
            self.cameraLabel.show_message(message)
        self.apply_theme()

    def set_waiting(self):
        self._set_state("waiting")
        self.pulse_waiting(True)

    def pulse_waiting(self, on):
        if self.state == "waiting":
            self.cameraLabel.show_message(
                "<div align='center'><span style='font-size:28px'>"
                + ("◉" if on else "◎")
                + "</span><br><br><b>Waiting for Student to Join...</b>"
                  "<br><span style='font-size:11px'>"
                  "Waiting for incoming camera stream on TCP feed.</span></div>"
            )

    def set_submitted(self, register_no):
        self._set_state(
            "submitted",
            "<div align='center'><span style='font-size:30px'>✓</span>"
            "<br><br><b>Exam Submitted Successfully</b><br>"
            f"<span style='font-size:11px'>Student {escape(str(register_no))} "
            "has completed and submitted the examination.</span></div>",
        )

    def set_disconnected(self):
        self._set_state(
            "offline",
            "<div align='center'><span style='font-size:28px'>○</span>"
            "<br><br><b>Camera Offline</b><br>"
            "<span style='font-size:11px'>The student camera connection has ended."
            "</span></div>",
        )

    def set_flagged(self, flagged):
        self._flagged = bool(flagged)
        if self.state in ("normal", "violation"):
            self._set_state("violation" if flagged else "normal")

    def update_frame(self, frame):
        if frame is None or self.state == "submitted":
            return
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            image = QImage(
                rgb.data, width, height, channels * width, QImage.Format_RGB888
            )
            self.cameraLabel.show_frame(QPixmap.fromImage(image))
            self._set_state("violation" if self._flagged else "normal")
        except Exception as error:
            print(">>> Camera card frame error:", error)

    def apply_theme(self):
        p = get_theme_palette()
        kind = {
            "waiting": "neutral", "offline": "neutral", "normal": "success",
            "violation": "danger", "submitted": "success",
        }[self.state]
        self.statusLabel.setStyleSheet(
            f"background: {p[f'badge_{kind}_bg']}; color: {p[f'badge_{kind}_text']};"
            f"border: 1px solid {p[f'badge_{kind}_border']}; border-radius: 9px;"
            "padding: 3px 7px; font-size: 11px; font-weight: 700;"
        )
        screen_bg = (
            p["badge_success_bg"] if self.state == "submitted"
            else p["camera_screen_bg"]
        )
        self.cameraLabel.setStyleSheet(
            f"background: {screen_bg}; color: {p['camera_screen_text']};"
            f"border: 1px solid {p['camera_screen_border']}; border-radius: 8px;"
            "font-size: 12px; font-weight: 600; padding: 6px;"
        )
        dot = {
            "normal": p["badge_success_text"],
            "violation": p["badge_danger_text"],
            "submitted": p["badge_success_text"],
        }.get(self.state, p["text_muted"])
        self.liveDot.setStyleSheet(f"color: {dot}; font-size: 11px;")


class LiveMonitorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cameraServer = None
        self.studentCards = {}
        self.camera_slots = {}
        self.slot_by_student = {}
        self.signalBridge = CameraSignalBridge()
        self.active_exam_id = None
        self.active_exam = None
        self.students_list = []
        self.violation_counts = {}
        self.camera_threads = {}
        self.recent_violations = []
        self._paused = False
        self._server_failed = False
        self._pulse_on = False
        self._filter = "all"
        self._remaining_seconds = None
        self._countdown_deadline = None
        self._observed_exam_started_at = None
        self._exam_schedule_signature = None
        self._exam_ended = False
        self._data_error = False
        self._last_db_error = None
        self._violation_error = False
        self._last_violation_error = None
        self._last_started_count = None
        self._last_logged_exam_id = None
        self._unknown_streams_logged = set()
        self.signalBridge.frame_received.connect(self.handle_frame)
        self.signalBridge.student_disconnected.connect(self.handle_disconnect)
        self.setupUI()
        self.exam_countdown_timer = QTimer(self)
        self.exam_countdown_timer.setInterval(1000)
        self.exam_countdown_timer.timeout.connect(self._update_countdown_display)
        self.clockTimer = self.exam_countdown_timer
        self.refresh_students()
        self.start_camera_server()
        self.dataTimer = QTimer(self)
        self.dataTimer.timeout.connect(self.refresh_students)
        self.dataTimer.start(5000)
        self.pulseTimer = QTimer(self)
        self.pulseTimer.timeout.connect(self._pulse_status)
        self.pulseTimer.start(700)
        register_theme_listener(self._on_theme_changed)

    def setupUI(self):
        self.setObjectName("pageWidget")
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        top = QFrame()
        top.setObjectName("monitorTop")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(18, 12, 18, 12)
        top_layout.setSpacing(14)
        icon = QLabel("▣")
        icon.setObjectName("examIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(42, 42)
        top_layout.addWidget(icon)
        heading = QVBoxLayout()
        heading.setSpacing(3)
        self.examTitle = QLabel("Live Monitoring")
        self.examTitle.setObjectName("examTitle")
        self.examMeta = QLabel("Looking for an active examination")
        self.examMeta.setObjectName("examMeta")
        heading.addWidget(self.examTitle)
        heading.addWidget(self.examMeta)
        top_layout.addLayout(heading, 1)
        self.serverStatusLabel = QLabel("● LIVE MONITORING")
        top_layout.addWidget(self.serverStatusLabel)
        timer_box = QVBoxLayout()
        self.timerValue = QLabel("--:--:--")
        self.timerValue.setObjectName("timerValue")
        self.lbl_time_remaining = self.timerValue
        self.timerCaption = QLabel("Time Remaining")
        self.timerCaption.setObjectName("smallMuted")
        timer_box.addWidget(self.timerValue)
        timer_box.addWidget(self.timerCaption)
        top_layout.addLayout(timer_box)
        self.adminBadge = QLabel("AD   Admin")
        self.adminBadge.setObjectName("adminBadge")
        top_layout.addWidget(self.adminBadge)
        root.addWidget(top)

        body = QHBoxLayout()
        body.setSpacing(12)
        center = QVBoxLayout()
        center.setSpacing(10)
        filters = QFrame()
        filters.setObjectName("monitorToolbar")
        filters_layout = QHBoxLayout(filters)
        filters_layout.setContentsMargins(9, 8, 9, 8)
        filters_layout.setSpacing(5)
        self.filterButtons = {}
        for key, title in (
            ("all", "All Cameras"), ("normal", "Normal"),
            ("violation", "Violation"), ("offline", "Offline"),
        ):
            button = QPushButton(title)
            button.setObjectName("filterPill")
            button.setProperty("filterKind", key)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked, name=key: self._set_filter(name))
            self.filterButtons[key] = button
            filters_layout.addWidget(button)
        filters_layout.addStretch()
        self.viewSelect = QComboBox()
        self.viewSelect.addItems(["3×3 Grid", "2×2 Grid", "1×1 Grid"])
        self.viewSelect.setObjectName("viewSelect")
        self.viewSelect.setMinimumWidth(108)
        self.viewSelect.currentIndexChanged.connect(self._layout_grid)
        filters_layout.addWidget(self.viewSelect)
        self.refreshButton = QPushButton("↻ Refresh")
        self.refreshButton.setObjectName("outlineButton")
        self.refreshButton.clicked.connect(self.refresh_students)
        filters_layout.addWidget(self.refreshButton)
        center.addWidget(filters)

        self.gridStack = QStackedWidget()
        self.gridScroll = QScrollArea()
        self.scrollArea = self.gridScroll
        self.gridScroll.setWidgetResizable(True)
        self.gridScroll.setFrameShape(QFrame.NoFrame)
        self.scrollWidget = QWidget()
        self.gridLayout = QGridLayout(self.scrollWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(10)
        for slot_id in range(1, 10):
            self.camera_slots[slot_id] = StudentCameraCard(slot_id)
        self.filterEmpty = QLabel("No cameras match this filter.")
        self.emptyLabel = self.filterEmpty
        self.filterEmpty.setObjectName("filterEmpty")
        self.filterEmpty.setAlignment(Qt.AlignCenter)
        self.gridScroll.setWidget(self.scrollWidget)
        self.gridStack.addWidget(self.gridScroll)

        self.noExamCard = QFrame()
        self.noExamCard.setObjectName("noExamCard")
        empty_layout = QVBoxLayout(self.noExamCard)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)
        shield = QLabel("🛡️")
        shield.setAlignment(Qt.AlignCenter)
        shield.setStyleSheet("font-size: 34px;")
        self.noExamTitle = QLabel("No Active Examination in Progress")
        self.noExamTitle.setObjectName("emptyTitle")
        self.noExamTitle.setAlignment(Qt.AlignCenter)
        self.noExamText = QLabel(
            "Live monitoring will automatically initialize once an examination "
            "is launched by the administrator."
        )
        self.noExamText.setObjectName("emptyText")
        self.noExamText.setAlignment(Qt.AlignCenter)
        self.noExamText.setWordWrap(True)
        self.scheduleButton = QPushButton("+ Schedule or Start Exam")
        self.scheduleButton.setObjectName("scheduleButton")
        self.scheduleButton.clicked.connect(self._open_exams_page)
        empty_layout.addStretch()
        empty_layout.addWidget(shield)
        empty_layout.addWidget(self.noExamTitle)
        empty_layout.addWidget(self.noExamText)
        empty_layout.addWidget(self.scheduleButton, 0, Qt.AlignCenter)
        empty_layout.addStretch()
        self.gridStack.addWidget(self.noExamCard)
        center.addWidget(self.gridStack, 1)
        body.addLayout(center, 1)

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFixedWidth(266)
        sidebar_scroll.setFrameShape(QFrame.NoFrame)
        sidebar_widget = QWidget()
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(10)
        summary, summary_layout = self._sidebar_card("◫  Live Summary")
        metrics = QGridLayout()
        metrics.setSpacing(8)
        self.metricLabels = {}
        for index, (key, title) in enumerate((
            ("total", "Total Students"), ("normal", "Normal"),
            ("violation", "Violations"), ("offline", "Offline"),
        )):
            metric = QFrame()
            metric.setObjectName("metricCard")
            metric_layout = QVBoxLayout(metric)
            metric_layout.setContentsMargins(10, 7, 10, 7)
            value = QLabel("0")
            value.setObjectName("metricValue")
            caption = QLabel(title)
            caption.setObjectName("smallMuted")
            metric_layout.addWidget(value)
            metric_layout.addWidget(caption)
            metrics.addWidget(metric, index // 2, index % 2)
            self.metricLabels[key] = value
        summary_layout.addLayout(metrics)
        sidebar.addWidget(summary)
        recent, recent_layout = self._sidebar_card("⚠  Recent Violations")
        self.violationsBody = QVBoxLayout()
        self.violationsBody.setSpacing(6)
        recent_layout.addLayout(self.violationsBody)
        sidebar.addWidget(recent)
        controls, controls_layout = self._sidebar_card("▦  Quick Controls")
        self.pauseButton = QPushButton("Ⅱ  Pause Monitoring")
        self.pauseButton.setObjectName("pauseButton")
        self.pauseButton.setToolTip("Pause the camera display while streams continue to arrive.")
        self.pauseButton.clicked.connect(self._toggle_pause)
        self.endButton = QPushButton("■  End Exam")
        self.endButton.setObjectName("outlineButton")
        self.endButton.clicked.connect(self._end_exam)
        self.refreshCamerasButton = QPushButton("↻  Refresh Cameras")
        self.refreshCamerasButton.setObjectName("outlineButton")
        self.refreshCamerasButton.clicked.connect(self.refresh_students)
        for button in (self.pauseButton, self.endButton, self.refreshCamerasButton):
            controls_layout.addWidget(button)
        sidebar.addWidget(controls)
        notes, notes_layout = self._sidebar_card("▤  Guidelines / Notes")
        note = QLabel(
            "Normal head movements while writing are allowed. "
            "Review flagged activity before taking action."
        )
        note.setObjectName("noteText")
        note.setWordWrap(True)
        notes_layout.addWidget(note)
        sidebar.addWidget(notes)
        sidebar.addStretch()
        sidebar_scroll.setWidget(sidebar_widget)
        body.addWidget(sidebar_scroll)
        root.addLayout(body, 1)
        self._layout_grid()
        self._apply_theme_styles()

    @staticmethod
    def _sidebar_card(title):
        card = QFrame()
        card.setObjectName("utilityCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(9)
        heading = QLabel(title)
        heading.setObjectName("utilityTitle")
        layout.addWidget(heading)
        return card, layout

    def _on_theme_changed(self, theme_name):
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        p = get_theme_palette()
        primary = "#2563EB"
        canvas = "#F8FAFC" if p["name"] == "light" else "#0B132B"
        self.setStyleSheet(f"""
            QWidget#pageWidget {{ background: {canvas}; }}
            QFrame#monitorTop, QFrame#monitorToolbar, QFrame#utilityCard,
            QFrame#noExamCard, QFrame[monitorCard="true"] {{
                background: {p['bg_card']}; border: 1px solid {p['border_card']};
                border-radius: 11px;
            }}
            QFrame#metricCard {{ background: {p['bg_card_alt']};
                border: 1px solid {p['border_subtle']}; border-radius: 8px; }}
            QLabel#examTitle, QLabel#emptyTitle {{ color: {p['text_primary']};
                font-size: 18px; font-weight: 750; }}
            QLabel#examMeta, QLabel#smallMuted, QLabel#emptyText,
            QLabel#noteText, QLabel#cameraMeta {{
                color: {p['text_secondary']}; font-size: 11px; }}
            QLabel#cameraTitle, QLabel#utilityTitle {{
                color: {p['text_primary']}; font-size: 12px; font-weight: 700; }}
            QLabel#metricValue, QLabel#timerValue {{
                color: {p['text_primary']}; font-size: 18px; font-weight: 750; }}
            QLabel#filterEmpty {{ color: {p['text_secondary']}; font-size: 14px; }}
            QLabel#examIcon {{ background: {p['badge_info_bg']};
                color: {primary}; border-radius: 9px; font-size: 24px; }}
            QLabel#adminBadge {{ background: {p['badge_info_bg']};
                color: {p['badge_info_text']}; border-radius: 13px;
                padding: 7px 9px; font-weight: 700; }}
            QPushButton#filterPill {{
                background: transparent; color: {p['text_secondary']};
                border: 1px solid transparent; padding: 7px 9px; border-radius: 7px; }}
            QPushButton#filterPill:checked {{
                background: {primary}; color: white; }}
            QPushButton#filterPill[filterKind="normal"]:!checked {{
                color: {p['badge_success_text']}; }}
            QPushButton#filterPill[filterKind="violation"]:!checked {{
                color: {p['badge_danger_text']}; }}
            QPushButton#filterPill[filterKind="offline"]:!checked {{
                color: {p['text_muted']}; }}
            QPushButton#filterPill:hover {{
                border: 1px solid {primary}; }}
            QPushButton#scheduleButton, QPushButton#pauseButton {{
                background: {primary}; color: white; border: 1px solid {primary}; }}
            QPushButton#outlineButton {{ background: {p['bg_card']};
                color: {p['text_primary']}; border: 1px solid {p['border_subtle']}; }}
            QComboBox#viewSelect {{ background: {p['bg_card']};
                color: {p['text_primary']}; border: 1px solid {p['border_subtle']}; }}
        """)
        for card in self.camera_slots.values():
            card.apply_theme()
        self._pulse_status()

    def _pulse_status(self):
        self._pulse_on = not self._pulse_on
        for card in self.camera_slots.values():
            card.pulse_waiting(self._pulse_on)
        p = get_theme_palette()
        if self._server_failed:
            self.serverStatusLabel.setText("● SERVER ERROR")
            self.serverStatusLabel.setStyleSheet(
                f"background: {p['badge_danger_bg']}; color: {p['badge_danger_text']};"
                f"border: 1px solid {p['badge_danger_border']};"
                "border-radius: 9px; padding: 6px 9px; font-weight: 700;"
            )
            return
        if self._data_error or self._violation_error:
            self.serverStatusLabel.setText("● DATA UNAVAILABLE")
            self.serverStatusLabel.setStyleSheet(
                f"background: {p['badge_warning_bg']};"
                f"color: {p['badge_warning_text']};"
                f"border: 1px solid {p['badge_warning_border']};"
                "border-radius: 9px; padding: 6px 9px; font-weight: 700;"
            )
            return
        active = self.active_exam_id is not None
        ended = self._exam_ended and not active
        kind = "danger" if active else "neutral"
        self.serverStatusLabel.setText(
            ("●" if self._pulse_on or not active else "◦")
            + (" LIVE MONITORING" if active else
               " EXAM ENDED" if ended else " MONITORING IDLE")
        )
        self.serverStatusLabel.setStyleSheet(
            f"background: {p[f'badge_{kind}_bg']};"
            f"color: {p[f'badge_{kind}_text']};"
            f"border: 1px solid {p[f'badge_{kind}_border']};"
            "border-radius: 9px; padding: 6px 9px; font-size: 11px; font-weight: 700;"
        )

    def _show_no_exam_state(self):
        self.exam_countdown_timer.stop()
        self._countdown_deadline = None
        self._observed_exam_started_at = None
        self._exam_schedule_signature = None
        self.gridStack.setCurrentWidget(self.noExamCard)
        self.examTitle.setText("No Active Examination")
        self.examMeta.setText(
            "Start or select an examination to begin live proctoring."
        )
        self._remaining_seconds = 0 if self._exam_ended else None
        self.lbl_time_remaining.setText(
            "00:00:00" if self._exam_ended else "--:--:--"
        )
        for label in self.metricLabels.values():
            label.setText("0")
        self.pauseButton.setEnabled(False)
        self.endButton.setEnabled(False)
        self._render_violations([])
        self._update_counts()
        self._pulse_status()

    def _render_waiting_state(self, slot_id):
        self.camera_slots[slot_id].set_waiting()

    def _render_submitted_state(self, student_id):
        identifier = str(student_id)
        student = next(
            (row for row in self.students_list
             if str(row["id"]) == identifier or row["register_no"] == identifier),
            None,
        )
        if student is None:
            return
        register_no = student["register_no"]
        slot_id = self.slot_by_student.get(register_no)
        if slot_id is None:
            self.create_student_card(register_no)
            slot_id = self.slot_by_student.get(register_no)
            if slot_id is None:
                return
        card = self.camera_slots[slot_id]
        card.set_student(
            register_no, student["name"], self.active_exam["subject_name"],
            student["semester"],
        )
        card.set_submitted(register_no)

    def _update_active_stream(self, frame, slot_id=1):
        """Render a TCP 5001 frame in its assigned student's camera slot."""
        if not self._paused:
            self.camera_slots[slot_id].update_frame(frame)

    def _set_filter(self, name):
        self._filter = name
        self._layout_grid()

    def _layout_grid(self, *_):
        columns = (3, 2, 1)[self.viewSelect.currentIndex()]
        for button_name, button in self.filterButtons.items():
            button.setChecked(button_name == self._filter)
        while self.gridLayout.count():
            self.gridLayout.takeAt(0)
        visible = [
            card for card in self.camera_slots.values()
            if self._filter == "all" or card.state == self._filter
        ]
        for index, card in enumerate(visible):
            card.show()
            self.gridLayout.addWidget(card, index // columns, index % columns)
        for card in self.camera_slots.values():
            if card not in visible:
                card.hide()
        self.filterEmpty.setVisible(not visible)
        if not visible:
            self.gridLayout.addWidget(self.filterEmpty, 0, 0)
        for column in range(3):
            self.gridLayout.setColumnStretch(column, 1 if column < columns else 0)
        self.gridLayout.setRowStretch((len(visible) + columns - 1) // columns, 1)

    def _update_counts(self):
        counts = {
            state: sum(card.state == state for card in self.camera_slots.values())
            for state in ("normal", "violation", "offline")
        }
        counts["violation"] = sum(self.violation_counts.values())
        counts["total"] = len(self.students_list)
        for key, value in counts.items():
            self.metricLabels[key].setText(
                "—" if key == "violation" and self._violation_error else str(value)
            )
        for key, button in self.filterButtons.items():
            button.setText({
                "all": f"All Cameras ({len(self.students_list)})",
                "normal": f"● Normal ({counts['normal']})",
                "violation": (
                    "● Violation (—)" if self._violation_error
                    else f"● Violation ({counts['violation']})"
                ),
                "offline": f"● Offline ({counts['offline']})",
            }[key])

    def _render_violations(self, rows):
        while self.violationsBody.count():
            item = self.violationsBody.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self._violation_error:
            unavailable = QLabel("Violation data temporarily unavailable.")
            unavailable.setObjectName("smallMuted")
            self.violationsBody.addWidget(unavailable)
            return
        if not rows:
            empty = QLabel("No recent violations.")
            empty.setObjectName("smallMuted")
            self.violationsBody.addWidget(empty)
            return
        for row in rows[:5]:
            slot = self.slot_by_student.get(row["register_no"])
            source = f"Camera {slot}" if slot else row["register_no"]
            event_time = row["date_time"] or "Time unavailable"
            try:
                event_time = datetime.fromisoformat(event_time).strftime("%I:%M:%S %p")
            except (TypeError, ValueError):
                pass
            label = QLabel(
                f"●  {row['violation_type'] or 'Violation type unavailable'}\n"
                f"    {source}\n    {event_time}"
            )
            label.setObjectName("noteText")
            label.setWordWrap(True)
            self.violationsBody.addWidget(label)

    @staticmethod
    def _duration_minutes(exam):
        match = re.search(r"\d+", str(exam.get("duration") or ""))
        return int(match.group()) if match else None

    def _update_countdown_display(self):
        if self.active_exam_id is None or self._countdown_deadline is None:
            self.exam_countdown_timer.stop()
            self.lbl_time_remaining.setText("--:--:--")
            return
        seconds = max(
            0, math.ceil((self._countdown_deadline - datetime.now()).total_seconds())
        )
        self._remaining_seconds = seconds
        self.lbl_time_remaining.setText(
            f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
        )
        if seconds == 0:
            self.exam_countdown_timer.stop()
            if not self._finish_exam(self.active_exam_id):
                print(">>> Could not complete expired examination.")

    def _open_exams_page(self):
        window = self.window()
        if hasattr(window, "show_page") and hasattr(window, "examsPage"):
            window.show_page(window.examsPage, window.examsBtn)

    def _toggle_pause(self):
        self._paused = not self._paused
        self.pauseButton.setText(
            "▶  Resume Monitoring" if self._paused else "Ⅱ  Pause Monitoring"
        )

    def _end_exam(self):
        if self.active_exam_id is None:
            return
        answer = QMessageBox.question(
            self, "End Examination",
            "End this examination for all assigned students?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            if not self._finish_exam(self.active_exam_id):
                QMessageBox.warning(
                    self, "End Examination", "Unable to end the examination."
                )

    def _finish_exam(self, exam_id, show_ended=True):
        """Complete the exam through the existing model and clear only page state."""
        try:
            completed = ExamModel.complete_exam(exam_id)
        except Exception as error:
            print(f">>> Live monitoring could not complete exam {exam_id}: {error}")
            traceback.print_exc()
            return False
        if not completed:
            print(f">>> Live monitoring could not complete exam {exam_id}.")
            return False
        self.exam_countdown_timer.stop()
        self._exam_ended = show_ended
        self.active_exam = None
        self.active_exam_id = None
        self.students_list = []
        self.violation_counts = {}
        self.recent_violations = []
        self._paused = False
        self.pauseButton.setText("Ⅱ  Pause Monitoring")
        self._reset_camera_slots()
        self._show_no_exam_state()
        self.refresh_students()
        return True

    def get_student_exam_info(self, register_no):
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT s.name AS student_name, e.subject_code, e.subject_name
                FROM students s
                LEFT JOIN student_assignment sa ON s.id = sa.student_id
                LEFT JOIN exams e ON sa.exam_id = e.id
                WHERE s.register_no = ?
                ORDER BY e.exam_date DESC, e.id DESC LIMIT 1
            """, (register_no,))
            row = cursor.fetchone()
            if row is None:
                return "Unknown Student", "Unknown Subject"
            subject = " - ".join(
                part for part in (row["subject_code"], row["subject_name"]) if part
            )
            return row["student_name"] or "Unknown Student", subject or "Unknown Subject"
        except Exception as error:
            print(">>> Student database lookup error:", error)
            return "Unknown Student", "Unknown Subject"
        finally:
            if connection is not None:
                connection.close()

    def _reset_camera_slots(self):
        self.studentCards.clear()
        self.slot_by_student.clear()
        for slot_id in sorted(self.camera_slots, reverse=True):
            if slot_id > 9:
                card = self.camera_slots.pop(slot_id)
                self.gridLayout.removeWidget(card)
                card.setParent(None)
                card.deleteLater()
        for slot_id, card in self.camera_slots.items():
            card.register_no = None
            card.student_name = ""
            card.subject = ""
            card.semester = ""
            card._flagged = False
            card.setToolTip("")
            card.registerLabel.setText("Awaiting student")
            card.subjectLabel.setText("—")
            card.semesterLabel.setText("—")
            self._render_waiting_state(slot_id)

    def _ensure_camera_capacity(self, total_students):
        for slot_id in range(len(self.camera_slots) + 1, max(9, total_students) + 1):
            self.camera_slots[slot_id] = StudentCameraCard(slot_id)

    def _sync_assigned_cards(self):
        """Keep a stable card for every assigned register number."""
        assigned = {str(row["register_no"]): row for row in self.students_list}
        self._ensure_camera_capacity(len(assigned))
        for register_no, slot_id in list(self.slot_by_student.items()):
            if register_no in assigned:
                continue
            self.studentCards.pop(register_no, None)
            self.slot_by_student.pop(register_no, None)
            card = self.camera_slots[slot_id]
            card.register_no = None
            card.setToolTip("")
            card.registerLabel.setText("Awaiting student")
            card.subjectLabel.setText("—")
            card.semesterLabel.setText("—")
            self._render_waiting_state(slot_id)
        for student in self.students_list:
            register_no = str(student["register_no"])
            if register_no not in self.studentCards:
                self.create_student_card(register_no)
            card = self.studentCards.get(register_no)
            if card is None:
                continue
            card.set_student(
                register_no, student["name"],
                self.active_exam["subject_name"], student["semester"],
            )
            if str(student["attempt_status"]).upper() == "SUBMITTED":
                self._render_submitted_state(student["id"])
            elif card.state in ("normal", "violation"):
                card.set_flagged(self.violation_counts.get(register_no, 0) > 0)

    def refresh_students(self):
        """Refresh dashboard data without restarting sockets or recreating live cards."""
        connection = None
        stage = "opening the database"
        try:
            connection = get_connection()
            cursor = connection.cursor()
            stage = "querying Started examinations"
            cursor.execute("""
                SELECT * FROM exams WHERE exam_status = 'Started'
                ORDER BY exam_date DESC, start_time DESC, id DESC
            """)
            started_rows = cursor.fetchall()
            exam = dict(started_rows[0]) if started_rows else None
            students = []
            violation_counts = {}
            recent_violations = []
            violation_error = None
            if exam is not None:
                stage = f"loading assignments for exam {exam['id']}"
                cursor.execute("""
                    SELECT s.id, s.register_no, s.name, s.semester,
                           COALESCE(ea.status, '') AS attempt_status
                    FROM student_assignment sa
                    JOIN students s ON s.id = sa.student_id
                    LEFT JOIN exam_attempts ea
                        ON ea.student_id = s.id AND ea.exam_id = sa.exam_id
                    WHERE sa.exam_id = ? ORDER BY s.register_no
                """, (exam["id"],))
                students = [dict(row) for row in cursor.fetchall()]
                try:
                    stage = f"loading violation counts for exam {exam['id']}"
                    cursor.execute("""
                        SELECT v.register_no, COUNT(DISTINCT v.id) AS total
                        FROM violations v
                        JOIN students s ON s.register_no = v.register_no
                        JOIN student_assignment sa
                            ON sa.student_id = s.id AND sa.exam_id = ?
                        JOIN exam_attempts ea
                            ON ea.student_id = s.id AND ea.exam_id = sa.exam_id
                        WHERE v.date_time >= datetime(ea.started_at, 'localtime')
                        GROUP BY v.register_no
                    """, (exam["id"],))
                    violation_counts = {
                        row["register_no"]: row["total"] for row in cursor.fetchall()
                    }
                    stage = f"loading recent violations for exam {exam['id']}"
                    cursor.execute("""
                        SELECT DISTINCT v.id, v.register_no,
                               v.violation_type, v.date_time
                        FROM violations v
                        JOIN students s ON s.register_no = v.register_no
                        JOIN student_assignment sa
                            ON sa.student_id = s.id AND sa.exam_id = ?
                        JOIN exam_attempts ea
                            ON ea.student_id = s.id AND ea.exam_id = sa.exam_id
                        WHERE v.date_time >= datetime(ea.started_at, 'localtime')
                        ORDER BY v.date_time DESC, v.id DESC LIMIT 5
                    """, (exam["id"],))
                    recent_violations = [dict(row) for row in cursor.fetchall()]
                except Exception as error:
                    violation_error = error
                    signature = (stage, type(error).__name__, str(error))
                    if signature != self._last_violation_error:
                        print(
                            f">>> Live monitoring violation refresh error while "
                            f"{stage}: {type(error).__name__}: {error}"
                        )
                        traceback.print_exc()
                        self._last_violation_error = signature
                    if exam["id"] == self.active_exam_id:
                        violation_counts = self.violation_counts
                        recent_violations = self.recent_violations
        except Exception as error:
            self._data_error = True
            self._last_started_count = None
            error_signature = (stage, type(error).__name__, str(error))
            if error_signature != self._last_db_error:
                print(
                    f">>> Live monitoring database refresh error while {stage} "
                    f"({DB_PATH}): {type(error).__name__}: {error}"
                )
                traceback.print_exc()
                self._last_db_error = error_signature
            if self.active_exam_id is None:
                self.examTitle.setText("Monitoring Data Unavailable")
                self.examMeta.setText("Unable to read exam data. Retrying automatically.")
                self.noExamTitle.setText("Unable to Load Examination Status")
                self.noExamText.setText(
                    "The database could not be read. Monitoring will retry automatically."
                )
                self.gridStack.setCurrentWidget(self.noExamCard)
            self._pulse_status()
            return
        finally:
            if connection is not None:
                connection.close()

        if self._data_error:
            print(">>> Live monitoring database read recovered.")
        self._data_error = False
        self._last_db_error = None
        if violation_error is None:
            if self._violation_error:
                print(">>> Live monitoring violation read recovered.")
            self._last_violation_error = None
        self._violation_error = violation_error is not None
        self.noExamTitle.setText("No Active Examination in Progress")
        self.noExamText.setText(
            "Live monitoring will automatically initialize once an examination "
            "is launched by the administrator."
        )
        started_count = len(started_rows)
        detected_id = exam["id"] if exam is not None else None
        if (started_count != self._last_started_count
                or detected_id != self._last_logged_exam_id):
            print(f">>> Live monitoring Started exams found: {started_count}.")
            if exam is not None:
                print(
                    f">>> Live monitoring detected active exam "
                    f"ID={exam['id']}, name={exam['exam_name']!r}, "
                    f"status={exam['exam_status']!r}."
                )
        self._last_started_count = started_count
        self._last_logged_exam_id = detected_id
        if exam is None:
            if self.active_exam_id is not None:
                self._exam_ended = True
            self.active_exam = None
            self.active_exam_id = None
            self.students_list = []
            self.violation_counts = {}
            self.recent_violations = []
            self._reset_camera_slots()
            self._show_no_exam_state()
            return

        new_exam = exam["id"] != self.active_exam_id
        if new_exam:
            self._reset_camera_slots()
            self._unknown_streams_logged.clear()
            self._exam_ended = False
            self._observed_exam_started_at = datetime.now()
            print(
                f">>> Live monitoring countdown for exam {exam['id']} starts at "
                f"first Started detection: {self._observed_exam_started_at:%Y-%m-%d %H:%M:%S}."
            )
        self.active_exam_id = exam["id"]
        self.active_exam = exam
        self.students_list = students
        self.violation_counts = violation_counts
        self.recent_violations = recent_violations
        if new_exam or exam["duration"] != self._exam_schedule_signature:
            self._exam_schedule_signature = exam["duration"]
            minutes = self._duration_minutes(exam)
            if minutes is not None and minutes > 0:
                self._countdown_deadline = (
                    self._observed_exam_started_at + timedelta(minutes=minutes)
                )
            else:
                self._countdown_deadline = None
                print(
                    f">>> Live monitoring exam {exam['id']} has no valid duration; "
                    "automatic expiry is unavailable."
                )
        self.gridStack.setCurrentWidget(self.gridScroll)
        self.examTitle.setText(exam["exam_name"] or "Active Examination")
        duration = self._duration_minutes(exam)
        duration_text = str(duration) if duration is not None else str(exam["duration"])
        self.examMeta.setText(
            f"Date: {exam['exam_date']}  |  Start Time: {exam['start_time']}  |  "
            f"Duration: {duration_text} Mins  |  "
            f"Total Students: {len(self.students_list)}"
        )
        self.pauseButton.setEnabled(True)
        self.endButton.setEnabled(True)
        self._update_countdown_display()
        if self.active_exam_id != exam["id"]:
            return
        if self.active_exam_id is not None and self._countdown_deadline is not None:
            if not self.exam_countdown_timer.isActive():
                self.exam_countdown_timer.start()
        self._sync_assigned_cards()
        self._update_counts()
        self._render_violations(self.recent_violations)
        self._layout_grid()
        self._pulse_status()

    def start_camera_server(self):
        try:
            self.cameraServer = CameraServer(
                host="0.0.0.0", port=5001,
                on_frame=self.server_frame_received,
                on_disconnect=self.server_student_disconnected,
            )
            self.cameraServer.start()
            print(">>> Live Monitoring camera server started.")
        except Exception as error:
            print(">>> Live Monitoring server error:", error)
            self._server_failed = True
            self._pulse_status()

    def server_frame_received(self, register_no, frame):
        self.signalBridge.frame_received.emit(str(register_no), frame)

    def server_student_disconnected(self, register_no):
        if register_no is None:
            return
        self.signalBridge.student_disconnected.emit(str(register_no))

    def handle_frame(self, register_no, frame):
        register_no = str(register_no)
        if self.active_exam_id is None:
            return
        if register_no not in self.studentCards:
            self.create_student_card(register_no)
        card = self.studentCards.get(register_no)
        if card is not None:
            previous_state = card.state
            self._update_active_stream(frame, card.slot_id)
            if card.state != previous_state:
                self._update_counts()
                self._layout_grid()

    def create_student_card(self, register_no):
        register_no = str(register_no)
        if register_no in self.studentCards:
            return
        student = next(
            (row for row in self.students_list
             if str(row["register_no"]) == register_no), None,
        )
        if student is None:
            if register_no not in self._unknown_streams_logged:
                print(
                    f">>> Live monitoring ignored stream for unassigned "
                    f"register number {register_no}."
                )
                self._unknown_streams_logged.add(register_no)
            return
        self._ensure_camera_capacity(len(self.studentCards) + 1)
        available = next(
            (number for number, slot in self.camera_slots.items()
             if slot.register_no is None), None,
        )
        if available is None:
            return
        card = self.camera_slots[available]
        card.set_student(
            register_no, student["name"],
            self.active_exam["subject_name"], student["semester"],
        )
        self._render_waiting_state(available)
        card.set_flagged(self.violation_counts.get(register_no, 0) > 0)
        self.studentCards[register_no] = card
        self.slot_by_student[register_no] = available

    def handle_disconnect(self, register_no):
        register_no = str(register_no)
        card = self.studentCards.get(register_no)
        if card is None:
            return
        exam_id = self.active_exam_id
        self.refresh_students()
        if self.active_exam_id != exam_id:
            return
        if card.state != "submitted":
            card.set_disconnected()
        self._update_counts()
        self._layout_grid()

    def closeEvent(self, event):
        if self.cameraServer is not None:
            try:
                self.cameraServer.stop()
            except Exception as error:
                print(">>> Camera server stop error:", error)
            self.cameraServer = None
        event.accept()
