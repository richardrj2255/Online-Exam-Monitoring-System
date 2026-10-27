"""Isolated PDF/CSV question import UI for the existing Questions page."""

import os
import json
import subprocess
import sys
import threading
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from import_questions import (
    FIELDS, GEMINI_KEY_ERROR, commit_questions, get_gemini_api_key,
    parse_csv, parse_pdf_with_gemini,
)
from models.question_model import QuestionModel
from ui.theme_manager import get_theme_palette


class ImportDropZone(QFrame):
    """The PDF/CSV picker used by the separate card on QuestionsPage."""

    fileChosen = pyqtSignal(str)

    def __init__(self, suffix, parent=None):
        super().__init__(parent)
        self.suffix = suffix
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("bulkDropZone")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        icon = QLabel("☁")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 24px; color: #4F46E5; border: none;")
        label = QLabel(f"Drag & drop your {suffix.upper()} file here")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 11px; color: #475569; border: none;")
        button = QPushButton("Choose File")
        button.setObjectName("dropChooseFile")
        button.setFixedWidth(110)
        button.clicked.connect(self.choose_file)
        layout.addWidget(icon)
        layout.addWidget(label)
        layout.addWidget(button, alignment=Qt.AlignCenter)

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose question file", "",
            f"{self.suffix.upper()} files (*.{self.suffix})",
        )
        if path:
            self.fileChosen.emit(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.choose_file()
        else:
            super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile() and urls[0].toLocalFile().lower().endswith("." + self.suffix):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        self.fileChosen.emit(path)
        event.acceptProposedAction()


def _extract_in_process(path, api_key, send):
    """Run the blocking parser outside the Admin process so Cancel can stop it."""
    try:
        if path.lower().endswith(".csv"):
            rows = parse_csv(path)
        else:
            rows = parse_pdf_with_gemini(
                path, api_key,
                progress=lambda done, total: send("progress", int(done * 100 / total)),
                model_name=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            )
        send("result", rows)
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        send("error", str(exc))
    except Exception:
        send("error", "Unable to process this file. Check its format and try again.")


_active_workers = set()


def _retire_worker(worker):
    _active_workers.discard(worker)
    worker.deleteLater()


class ExtractionWorker(QThread):
    extracted = pyqtSignal(list)
    failed = pyqtSignal(str)
    progressChanged = pyqtSignal(int)

    def __init__(self, path, api_key):
        super().__init__()
        self.path = path
        self.api_key = api_key
        self._cancelled = threading.Event()
        self._process = None

    def cancel(self):
        self._cancelled.set()
        self.requestInterruption()
        process = self._process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass

    def run(self):
        process = None
        try:
            if self._cancelled.is_set():
                return
            process = subprocess.Popen(
                [sys.executable, "-m", "ui.pages.ai_importer", "--extract-worker"],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            self._process = process
            process.stdin.write(json.dumps({"path": self.path, "api_key": self.api_key}) + "\n")
            process.stdin.close()
            received_result = False
            for line in process.stdout:
                if self._cancelled.is_set():
                    break
                kind, value = json.loads(line)
                if kind == "progress":
                    self.progressChanged.emit(value)
                elif kind == "result":
                    self.progressChanged.emit(100)
                    self.extracted.emit(value)
                    received_result = True
                    break
                elif kind == "error":
                    self.failed.emit(value)
                    received_result = True
                    break
            if not self._cancelled.is_set() and not received_result:
                self.failed.emit("Extraction stopped unexpectedly. Please try again.")
        except Exception:
            if not self._cancelled.is_set():
                self.failed.emit("Unable to start extraction. Please try again.")
        finally:
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                if process.stdout is not None:
                    process.stdout.close()
            self._process = None


class AIQuestionImportDialog(QDialog):
    """Stages editable question drafts, then commits checked rows in one transaction."""

    COLUMNS = (
        "Select", "Question Prompt", "Option A", "Option B", "Option C",
        "Option D", "Correct Option (A/B/C/D)", "Marks (+)",
        "Negative Marks (-)", "Action",
    )
    FIELD_COLUMNS = dict(zip(FIELDS, range(1, 9)))

    def __init__(self, parent=None, initial_path=None, category_id=None):
        super().__init__(parent)
        self.setObjectName("dialog_ai_import")
        self.setWindowTitle("Import Questions from PDF or CSV")
        self.resize(1240, 780)
        self.setMinimumSize(950, 620)
        self.worker = None
        self.import_result = None
        self._cancelled = False
        self._build_ui()
        self._load_categories(category_id)
        if initial_path:
            self.set_file(initial_path)
        self._apply_style()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        heading = QHBoxLayout()
        heading_icon = QLabel("📁")
        heading_icon.setObjectName("importHeadingIcon")
        heading_icon.setFixedSize(42, 42)
        heading_icon.setAlignment(Qt.AlignCenter)
        heading_text = QVBoxLayout()
        title = QLabel("Import Questions from PDF or CSV")
        title.setObjectName("importTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Choose a category, extract questions, edit the preview, then approve the import.")
        subtitle.setObjectName("importMuted")
        heading_text.addWidget(title)
        heading_text.addWidget(subtitle)
        heading.addWidget(heading_icon)
        heading.addLayout(heading_text)
        heading.addStretch()
        close_button = QPushButton("✕")
        close_button.setObjectName("importClose")
        close_button.setFixedSize(34, 34)
        close_button.clicked.connect(self.on_cancel_clicked)
        heading.addWidget(close_button)
        outer.addLayout(heading)

        selection = QFrame()
        selection.setObjectName("importSection")
        form = QVBoxLayout(selection)
        form.setContentsMargins(18, 15, 18, 15)
        form.setSpacing(10)
        form.addWidget(self._section_label("1   File Selection & Target Category"))
        row = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(38)
        row.addWidget(QLabel("Category:"))
        row.addWidget(self.category_combo, 2)
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Choose a .pdf or .csv file")
        self.file_input.setMinimumHeight(38)
        row.addWidget(self.file_input, 4)
        browse = QPushButton("Browse…")
        browse.setObjectName("importOutline")
        browse.clicked.connect(self._browse)
        row.addWidget(browse)
        self.process_button = QPushButton("⚡ Process & Extract Questions")
        self.process_button.setObjectName("importPrimary")
        self.process_button.setMinimumHeight(38)
        self.process_button.clicked.connect(self._process)
        row.addWidget(self.process_button)
        form.addLayout(row)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.hide()
        form.addWidget(self.progress)
        self.status_label = QLabel("CSV import works offline. PDF extraction sends document text to Gemini.")
        self.status_label.setObjectName("importMuted")
        form.addWidget(self.status_label)
        outer.addWidget(selection)

        preview = QFrame()
        preview.setObjectName("importSection")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(18, 15, 18, 15)
        preview_layout.setSpacing(10)
        header = QHBoxLayout()
        header.addWidget(self._section_label("2   Interactive Staging & Preview"))
        header.addStretch()
        self.add_row_button = QPushButton("＋ Add New Blank Row")
        self.add_row_button.setObjectName("importOutline")
        self.add_row_button.clicked.connect(lambda: self.add_preview_row())
        header.addWidget(self.add_row_button)
        preview_layout.addLayout(header)
        self.preview_table = QTableWidget(0, len(self.COLUMNS))
        self.preview_table.setObjectName("importPreviewTable")
        self.preview_table.setHorizontalHeaderLabels(self.COLUMNS)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.verticalHeader().setDefaultSectionSize(38)
        self.preview_table.setWordWrap(False)
        self.preview_table.setMinimumHeight(270)
        header_view = self.preview_table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Interactive)
        self.preview_table.setColumnWidth(0, 65)
        self.preview_table.setColumnWidth(1, 260)
        for column in range(2, 6):
            self.preview_table.setColumnWidth(column, 135)
        self.preview_table.setColumnWidth(6, 165)
        self.preview_table.setColumnWidth(7, 100)
        self.preview_table.setColumnWidth(8, 145)
        self.preview_table.setColumnWidth(9, 105)
        self.preview_table.itemChanged.connect(self._update_summary)
        preview_layout.addWidget(self.preview_table)
        outer.addWidget(preview, 1)

        footer = QHBoxLayout()
        self.summary_badge = QLabel("0 Questions Selected for Import")
        self.summary_badge.setObjectName("importSummaryBadge")
        footer.addWidget(self.summary_badge)
        footer.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("importOutline")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        footer.addWidget(self.cancel_button)
        self.confirm_button = QPushButton("✅ Confirm & Import Selected Questions")
        self.confirm_button.setObjectName("importPrimary")
        self.confirm_button.setMinimumHeight(42)
        self.confirm_button.clicked.connect(self._commit)
        footer.addWidget(self.confirm_button)
        outer.addLayout(footer)

    @staticmethod
    def _section_label(text):
        label = QLabel(text)
        label.setObjectName("importSectionTitle")
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        return label

    def _load_categories(self, category_id):
        self.category_combo.addItem("Select Category", None)
        for category in QuestionModel.get_all_categories():
            self.category_combo.addItem(category["name"], category["id"])
        if category_id is not None:
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose question file", "", "Question files (*.pdf *.csv)"
        )
        if path:
            self.set_file(path)

    def set_file(self, path):
        if self.worker is not None and self.worker.isRunning():
            return
        if path != self.file_input.text():
            self.preview_table.setRowCount(0)
            self._update_summary()
        self.file_input.setText(path)

    def _process(self):
        if self.category_combo.currentData() is None:
            QMessageBox.warning(self, "Choose Category", "Select a target category first.")
            return
        path = self.file_input.text().strip()
        if not path or Path(path).suffix.lower() not in (".pdf", ".csv"):
            QMessageBox.warning(self, "Choose File", "Choose a PDF or CSV file first.")
            return
        if not Path(path).is_file():
            QMessageBox.warning(self, "File Missing", "The selected file no longer exists.")
            return
        limit = 10 * 1024 * 1024 if path.lower().endswith(".pdf") else 5 * 1024 * 1024
        if Path(path).stat().st_size > limit:
            QMessageBox.warning(self, "File Too Large", "PDF files must be at most 10 MB; CSV files at most 5 MB.")
            return
        api_key = get_gemini_api_key() if path.lower().endswith(".pdf") else ""
        if path.lower().endswith(".pdf") and not api_key:
            QMessageBox.critical(self, "Gemini API Key", GEMINI_KEY_ERROR)
            return
        self.preview_table.setRowCount(0)
        self._update_summary()
        self._cancelled = False
        self.process_button.setEnabled(False)
        self.confirm_button.setEnabled(False)
        self.cancel_button.setText("⏹ Cancel & Stop Extraction")
        self.progress.setValue(0)
        self.progress.show()
        self.status_label.setText("Processing file…")
        self.worker = ExtractionWorker(path, api_key)
        _active_workers.add(self.worker)
        self.worker.progressChanged.connect(self._progress_changed)
        self.worker.extracted.connect(self._extracted)
        self.worker.failed.connect(self._failed)
        self.worker.finished.connect(self._worker_finished)
        self.worker.finished.connect(lambda worker=self.worker: _retire_worker(worker))
        self.worker.start()

    def _progress_changed(self, value):
        if not self._cancelled:
            self.progress.setValue(value)

    def _extracted(self, rows):
        if self._cancelled:
            return
        self.preview_table.blockSignals(True)
        self.preview_table.setUpdatesEnabled(False)
        try:
            for row in rows:
                self.add_preview_row(row, update_summary=False)
        finally:
            self.preview_table.setUpdatesEnabled(True)
            self.preview_table.blockSignals(False)
        self._update_summary()
        self.status_label.setText(f"Extracted {len(rows)} question(s). Review every answer before importing.")
        self.confirm_button.setEnabled(True)

    def _failed(self, message):
        if self._cancelled:
            return
        self.status_label.setText("Processing failed. No questions were imported.")
        if message == GEMINI_KEY_ERROR:
            QMessageBox.critical(self, "Gemini API Key", message)
        else:
            QMessageBox.warning(self, "Import Processing", message)

    def _worker_finished(self):
        if self._cancelled:
            return
        self.process_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.progress.hide()
        self.worker = None

    def add_preview_row(self, data=None, update_summary=True):
        data = data or {}
        table = self.preview_table
        row = table.rowCount()
        table.insertRow(row)
        selected = QTableWidgetItem()
        selected.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        selected.setCheckState(Qt.Checked)
        table.setItem(row, 0, selected)
        for field, column in self.FIELD_COLUMNS.items():
            default = "1.0" if field == "marks" else "0.0" if field == "negative_marks" else ""
            value = data.get(field)
            table.setItem(row, column, QTableWidgetItem(str(value if value not in (None, "") else default)))
        delete = QPushButton("🗑 Delete Row")
        delete.setObjectName("importDeleteRow")
        delete.clicked.connect(lambda checked=False, button=delete: self._delete_row(button))
        table.setCellWidget(row, 9, delete)
        if update_summary:
            self._update_summary()

    def _delete_row(self, button):
        for row in range(self.preview_table.rowCount()):
            if self.preview_table.cellWidget(row, 9) is button:
                self.preview_table.removeRow(row)
                break
        self._update_summary()

    def _update_summary(self, *args):
        count = sum(
            self.preview_table.item(row, 0).checkState() == Qt.Checked
            for row in range(self.preview_table.rowCount())
            if self.preview_table.item(row, 0) is not None
        )
        self.summary_badge.setText(f"{count} Questions Selected for Import")

    def _commit(self):
        if self.category_combo.currentData() is None:
            QMessageBox.warning(self, "Choose Category", "Select a target category first.")
            return
        rows = []
        for row in range(self.preview_table.rowCount()):
            selected = self.preview_table.item(row, 0)
            if selected is None or selected.checkState() != Qt.Checked:
                continue
            values = {
                field: (self.preview_table.item(row, column).text()
                        if self.preview_table.item(row, column) else "")
                for field, column in self.FIELD_COLUMNS.items()
            }
            rows.append((row + 1, values))
        self.confirm_button.setEnabled(False)
        try:
            self.import_result = commit_questions(self.category_combo.currentData(), rows)
        except ValueError as exc:
            QMessageBox.warning(self, "Check Preview", str(exc))
            self.confirm_button.setEnabled(True)
        except Exception:
            QMessageBox.critical(self, "Import Failed", "Database import failed. No questions were saved.")
            self.confirm_button.setEnabled(True)
        else:
            self.accept()

    def _cancel_worker(self):
        self._cancelled = True
        worker = self.worker
        if worker is None:
            return
        for signal, slot in (
            (worker.progressChanged, self._progress_changed),
            (worker.extracted, self._extracted),
            (worker.failed, self._failed),
            (worker.finished, self._worker_finished),
        ):
            try:
                signal.disconnect(slot)
            except (TypeError, RuntimeError):
                pass
        worker.cancel()
        self.worker = None
        self.process_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.progress.hide()
        self.status_label.setText("Extraction cancelled.")

    def on_cancel_clicked(self):
        self._cancel_worker()
        super().reject()

    def reject(self):
        self.on_cancel_clicked()

    def closeEvent(self, event):
        self._cancel_worker()
        event.accept()
        super().closeEvent(event)

    def _apply_style(self):
        palette = get_theme_palette()
        dark = palette.get("name") == "dark"
        background = "#0F172A" if dark else "#F8FAFC"
        card = "#1E293B" if dark else "#FFFFFF"
        text = "#F8FAFC" if dark else "#0F172A"
        muted = "#94A3B8" if dark else "#64748B"
        border = "#334155" if dark else "#DBEAFE"
        input_bg = "#0F172A" if dark else "#FFFFFF"
        self.setStyleSheet(f"""
            QDialog#dialog_ai_import {{ background: {background}; color: {text}; }}
            QFrame#importSection {{ background: {card}; border: 1px solid {border}; border-radius: 12px; }}
            QLabel {{ color: {text}; border: none; background: transparent; }}
            QLabel#importTitle, QLabel#importSectionTitle {{ color: {text}; font-weight: 700; }}
            QLabel#importMuted {{ color: {muted}; font-size: 11px; }}
            QLabel#importHeadingIcon {{ background: #4F46E5; border-radius: 10px; font-size: 20px; }}
            QLabel#importSummaryBadge {{ background: #DCFCE7; color: #15803D;
                border: 1px solid #BBF7D0; border-radius: 9px; padding: 8px 12px; font-weight: 700; }}
            QLineEdit, QComboBox {{ background: {input_bg}; color: {text}; border: 1px solid {border};
                border-radius: 7px; padding: 7px 10px; }}
            QComboBox QAbstractItemView {{ background: {card}; color: {text}; }}
            QTableWidget#importPreviewTable {{ background: {card}; alternate-background-color: {background};
                color: {text}; gridline-color: {border}; border: 1px solid {border}; }}
            QTableWidget#importPreviewTable QHeaderView::section {{ background: {background}; color: {muted};
                border: 1px solid {border}; padding: 7px; font-weight: 700; }}
            QPushButton#importPrimary {{ background: #2563EB; color: white; border: none;
                border-radius: 8px; padding: 8px 16px; font-weight: 700; }}
            QPushButton#importPrimary:hover {{ background: #1D4ED8; }}
            QPushButton#importOutline, QPushButton#importClose {{ background: {card}; color: #4F46E5;
                border: 1px solid #A5B4FC; border-radius: 7px; padding: 7px 12px; font-weight: 600; }}
            QPushButton#importDeleteRow {{ background: #FFF1F2; color: #E11D48;
                border: 1px solid #FDA4AF; border-radius: 6px; padding: 5px; }}
            QPushButton:disabled {{ background: #94A3B8; color: white; }}
            QProgressBar {{ border: 1px solid {border}; border-radius: 5px; text-align: center; }}
            QProgressBar::chunk {{ background: #4F46E5; }}
        """)


def _run_extraction_cli():
    """Private subprocess entry point; input stays off the command line."""
    def send(kind, value):
        print(json.dumps([kind, value]), flush=True)

    try:
        request = json.loads(sys.stdin.readline())
        _extract_in_process(request["path"], request["api_key"], send)
    except Exception:
        send("error", "Unable to start extraction. Please try again.")


if __name__ == "__main__" and sys.argv[1:] == ["--extract-worker"]:
    _run_extraction_cli()
