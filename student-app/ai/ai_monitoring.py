import os
import cv2
import threading
import subprocess
import platform
import queue
import time
from datetime import datetime

from database.database import get_connection

from ai.face_detection import FaceDetector
from ai.multi_face import MultiFaceDetector
from ai.eye_tracking import EyeTracker
from ai.mouth_detection import MouthMonitor
from ai.object_detection import ObjectDetector
from ai.audio_detection import AudioMonitor


# ============================================================
# ALERT LOGGER
# ============================================================

class AIAlertLogger:

    def __init__(
        self,
        register_no,
        screenshot_dir="captured/ai"
    ):

        self.register_no = str(register_no)
        self.screenshot_dir = os.path.abspath(screenshot_dir)

        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.latest_frame = None
        self.last_alert_times = {}
        self.cooldown_seconds = 5

        # Official violations only
        self.violation_count = 0

        # Warning counters only
        self.eye_warning_count = 0
        self.mouth_warning_count = 0

        self.warning_callback = None

        self.last_event_type = None
        self.last_event_message = ""
        self.last_event_time = None

        self.lock = threading.Lock()

    # --------------------------------------------------------
    # Store latest camera frame
    # --------------------------------------------------------

    def set_frame(self, frame):

        if frame is None:
            return

        with self.lock:
            self.latest_frame = frame.copy()

    # --------------------------------------------------------
    # Save screenshot
    # --------------------------------------------------------

    def save_screenshot(self, violation_type):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        safe_type = (
            str(violation_type)
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"{self.register_no}_"
            f"{safe_type}_"
            f"{timestamp}.jpg"
        )

        filepath = os.path.join(self.screenshot_dir, filename)

        with self.lock:
            frame = (
                self.latest_frame.copy()
                if self.latest_frame is not None
                else None
            )

        if frame is None:
            return None

        try:
            cv2.imwrite(filepath, frame)
            return filepath

        except Exception as e:
            print(">>> Screenshot error:", e)
            return None

    # --------------------------------------------------------
    # Trigger warning callback
    # --------------------------------------------------------

    def _send_warning(self, warning_type, message):

        with self.lock:
            self.last_event_type = warning_type
            self.last_event_message = message
            self.last_event_time = datetime.now()

        print(f">>> AI WARNING: {warning_type}")
        print(f">>> Warning details: {message}")

        if self.warning_callback:
            try:
                self.warning_callback(warning_type, message)

            except Exception as e:
                print(">>> Warning callback error:", e)

    # --------------------------------------------------------
    # Reset warning counters
    # --------------------------------------------------------

    def reset_warning_counters(self):

        with self.lock:
            self.eye_warning_count = 0
            self.mouth_warning_count = 0

    # --------------------------------------------------------
    # Log violation
    # --------------------------------------------------------

    def log_alert(self, violation_type, message=""):

        violation_type = str(violation_type)

        # ====================================================
        # EYE MOVEMENT ESCALATION
        # ====================================================

        if violation_type == "EYE_MOVEMENT":

            with self.lock:
                self.eye_warning_count += 1
                occurrence = self.eye_warning_count

            if occurrence <= 3:

                self._send_warning(
                    "EYE_MOVEMENT_WARNING",
                    f"Eye movement detected. Warning {occurrence}/3."
                )

                return False

            return self._save_official_violation(
                violation_type,
                message
            )

        # ====================================================
        # MOUTH MOVEMENT ESCALATION
        # ====================================================

        if violation_type == "MOUTH_MOVEMENT":

            with self.lock:
                self.mouth_warning_count += 1
                occurrence = self.mouth_warning_count

            if occurrence <= 3:

                self._send_warning(
                    "MOUTH_MOVEMENT_WARNING",
                    f"Mouth movement detected. Warning {occurrence}/3."
                )

                return False

            return self._save_official_violation(
                violation_type,
                message
            )

        return self._save_official_violation(
            violation_type,
            message
        )

    # --------------------------------------------------------
    # Save official violation
    # --------------------------------------------------------

    def _save_official_violation(
        self,
        violation_type,
        message=""
    ):

        now = datetime.now()

        with self.lock:

            last_time = self.last_alert_times.get(
                violation_type
            )

            if last_time is not None:

                elapsed = (
                    now - last_time
                ).total_seconds()

                if elapsed < self.cooldown_seconds:
                    return False

            self.last_alert_times[violation_type] = now

        screenshot_path = self.save_screenshot(
            violation_type
        )

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO violations
                (
                    register_no,
                    violation_type,
                    screenshot,
                    date_time
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    self.register_no,
                    violation_type,
                    screenshot_path,
                    now.strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            conn.commit()
            conn.close()

            with self.lock:
                self.violation_count += 1
                self.last_event_type = violation_type
                self.last_event_message = message
                self.last_event_time = now

            print(
                f">>> AI OFFICIAL VIOLATION: "
                f"{violation_type}"
            )

            if message:
                print(f">>> Details: {message}")

            return True

        except Exception as e:
            print(">>> AI violation database error:", e)
            return False


# ============================================================
# CONFIGURATION
# ============================================================

class ExamAIConfig:

    @staticmethod
    def get_config():

        return {

            "detection": {

                "face": {
                    "detection_interval": 5,
                    "min_confidence": 0.80
                },

                "eyes": {
                    "gaze_threshold": 2,
                    "blink_threshold": 0.3,
                    "gaze_sensitivity": 15,
                    "consecutive_frames": 3
                },

                "mouth": {
                    "movement_threshold": 3
                },

                "multi_face": {
                    "alert_threshold": 5
                },

                "objects": {
                    "min_confidence": 0.65,
                    "detection_interval": 5,
                    "max_fps": 2
                },

                "audio_monitoring": {
                    "enabled": True,
                    "sample_rate": 16000,
                    "energy_threshold": 0.001,
                    "zcr_threshold": 0.35,
                    "whisper_enabled": False,
                    "whisper_model": "tiny.en"
                }
            },

            "logging": {
                "alert_cooldown": 5
            }
        }


# ============================================================
# EXAM AI MONITOR
# ============================================================

class ExamAIMonitor:

    def __init__(
        self,
        register_no,
        screenshot_dir="captured/ai"
    ):

        self.register_no = str(register_no)

        self.config = ExamAIConfig.get_config()

        self.alert_logger = AIAlertLogger(
            self.register_no,
            screenshot_dir
        )

        self.alert_logger.warning_callback = (
            self._handle_warning
        )

        # ----------------------------------------------------
        # Detectors
        # ----------------------------------------------------

        self.face_detector = None
        self.multi_face_detector = None
        self.eye_tracker = None
        self.mouth_monitor = None
        self.object_detector = None
        self.audio_monitor = None

        # ----------------------------------------------------
        # State
        # ----------------------------------------------------

        self.running = False
        self.initialization_errors = []

        self.face_present = False
        self.multiple_faces = False
        self.gaze_direction = "center"
        self.eye_ratio = 0.3
        self.mouth_movement = False
        self.forbidden_object = False
        self.voice_detected = False

        # ----------------------------------------------------
        # Warning state
        # ----------------------------------------------------

        self.current_warning = None
        self.current_warning_message = ""
        self.warning_time = None

        # ----------------------------------------------------
        # Face absence tracking
        # ----------------------------------------------------

        self.face_absence_start = None
        self.face_warning_issued = False
        self.face_violation_issued = False
        self.face_grace_seconds = 3
        self.face_violation_seconds = 5

        # ----------------------------------------------------
        # Warning cooldown
        # ----------------------------------------------------

        self.warning_cooldown_seconds = 2
        self.last_warning_time = None

        # ====================================================
        # FAST AND RELIABLE SPEECH SYSTEM
        # ====================================================

        self.speech_queue = queue.Queue(maxsize=50)
        self.speech_running = True
        self._speech_process = None
        self._speech_lock = threading.Lock()

        # Prevent the same sentence being repeated rapidly.
        self._last_spoken_message = ""
        self._last_spoken_time = None
        self._speech_repeat_cooldown = 1.5

        self.speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True,
            name="ExamWarningSpeechWorker"
        )

        self.speech_thread.start()

        self._initialize_detectors()

    # ========================================================
    # INITIALIZE DETECTORS
    # ========================================================

    def _initialize_detectors(self):

        try:

            self.face_detector = FaceDetector(self.config)

            self.face_detector.set_alert_logger(
                self.alert_logger
            )

            print(">>> Face detector initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Face detector: {e}"
            )

            print(">>> Face detector error:", e)

        try:

            self.multi_face_detector = MultiFaceDetector(
                self.config
            )

            self.multi_face_detector.set_alert_logger(
                self.alert_logger
            )

            print(">>> Multiple-face detector initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Multi-face detector: {e}"
            )

            print(">>> Multi-face detector error:", e)

        try:

            self.eye_tracker = EyeTracker(self.config)

            self.eye_tracker.set_alert_logger(
                self.alert_logger
            )

            print(">>> Eye tracker initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Eye tracker: {e}"
            )

            print(">>> Eye tracker error:", e)

        try:

            self.mouth_monitor = MouthMonitor(
                self.config
            )

            self.mouth_monitor.set_alert_logger(
                self.alert_logger
            )

            print(">>> Mouth monitor initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Mouth monitor: {e}"
            )

            print(">>> Mouth monitor error:", e)

        try:

            self.object_detector = ObjectDetector(
                self.config
            )

            self.object_detector.set_alert_logger(
                self.alert_logger
            )

            print(">>> Object detector initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Object detector: {e}"
            )

            print(">>> Object detector error:", e)

        try:

            audio_config = self.config[
                "detection"
            ][
                "audio_monitoring"
            ]

            if audio_config.get("enabled", True):

                self.audio_monitor = AudioMonitor(
                    self.config
                )

                self.audio_monitor.alert_logger = (
                    self.alert_logger
                )

                print(">>> Audio monitor initialized.")

        except Exception as e:

            self.initialization_errors.append(
                f"Audio monitor: {e}"
            )

            print(">>> Audio monitor error:", e)

    # ========================================================
    # WARNING HANDLER
    # ========================================================

    def _handle_warning(
        self,
        warning_type,
        message
    ):

        now = datetime.now()

        if self.last_warning_time is not None:

            elapsed = (
                now - self.last_warning_time
            ).total_seconds()

            if elapsed < self.warning_cooldown_seconds:
                return

        self.last_warning_time = now
        self.current_warning = warning_type
        self.current_warning_message = message
        self.warning_time = now

        print(f">>> WARNING: {message}")

        self._speak_warning(message)

    # ========================================================
    # FAST NON-BLOCKING SPEECH QUEUE
    # ========================================================

    def _speak_warning(self, message):

        if not message:
            return

        message = str(message).strip()

        if not message:
            return

        now = datetime.now()

        # Do not add identical warnings repeatedly.
        if (
            message == self._last_spoken_message
            and self._last_spoken_time is not None
        ):

            elapsed = (
                now - self._last_spoken_time
            ).total_seconds()

            if elapsed < self._speech_repeat_cooldown:
                return

        self._last_spoken_message = message
        self._last_spoken_time = now

        try:

            # If queue is full, remove old message.
            # Recent warnings are more useful than old warnings.
            while self.speech_queue.full():

                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()

                except queue.Empty:
                    break

            self.speech_queue.put_nowait(message)

        except queue.Full:
            print(">>> Speech queue full. Warning skipped.")

        except Exception as e:
            print(">>> Speech queue error:", e)
            print(f">>> AUDIO WARNING: {message}")

    # ========================================================
    # CREATE PERSISTENT WINDOWS SPEECH PROCESS
    # ========================================================

    def _start_speech_process(self):

        if platform.system() != "Windows":
            return None

        powershell_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$speaker = New-Object "
            "System.Speech.Synthesis.SpeechSynthesizer; "
            "$speaker.Rate = 1; "
            "$speaker.Volume = 100; "
            "while ($true) { "
            "$line = [Console]::ReadLine(); "
            "if ($null -eq $line) { break }; "
            "if ($line -eq '__STOP__') { break }; "
            "$speaker.Speak($line); "
            "}"
        )

        try:

            process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    powershell_script
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                bufsize=1
            )

            self._speech_process = process

            print(">>> Persistent warning speech system started.")

            return process

        except Exception as e:

            self._speech_process = None

            print(">>> Speech process start error:", e)

            return None

    # ========================================================
    # PERSISTENT SPEECH WORKER
    # ========================================================

    def _speech_worker(self):

        # Non-Windows fallback: warnings remain visible in console.
        if platform.system() != "Windows":

            print(
                ">>> Persistent speech worker unavailable "
                "on this operating system."
            )

            while self.speech_running:

                try:

                    message = self.speech_queue.get(
                        timeout=0.5
                    )

                    if message != "__STOP__":
                        print(f">>> AUDIO WARNING: {message}")

                    self.speech_queue.task_done()

                except queue.Empty:
                    continue

            return

        process = None
        restart_delay = 1.0

        while self.speech_running:

            try:

                # Start only when required.
                if (
                    process is None
                    or process.poll() is not None
                ):

                    process = self._start_speech_process()

                    if process is None:
                        time.sleep(restart_delay)
                        continue

                try:

                    message = self.speech_queue.get(
                        timeout=0.5
                    )

                except queue.Empty:
                    continue

                try:

                    if message == "__STOP__":
                        break

                    if (
                        process.poll() is None
                        and process.stdin is not None
                    ):

                        process.stdin.write(
                            str(message) + "\n"
                        )

                        process.stdin.flush()

                    else:

                        # Re-add the message if process closed.
                        try:
                            self.speech_queue.put_nowait(
                                message
                            )
                        except queue.Full:
                            pass

                        process = None
                        self._speech_process = None

                except Exception as e:

                    print(">>> Speech playback error:", e)

                    # Re-add warning once for retry.
                    try:
                        self.speech_queue.put_nowait(message)
                    except queue.Full:
                        pass

                    process = None
                    self._speech_process = None

                finally:
                    self.speech_queue.task_done()

            except Exception as e:

                print(">>> Speech worker error:", e)

                process = None
                self._speech_process = None

                time.sleep(restart_delay)

        # Clean shutdown.
        self._close_speech_process(process)

    # ========================================================
    # CLOSE SPEECH PROCESS
    # ========================================================

    def _close_speech_process(self, process=None):

        if process is None:
            process = self._speech_process

        if process is None:
            return

        try:

            if (
                process.poll() is None
                and process.stdin is not None
            ):

                try:
                    process.stdin.write("__STOP__\n")
                    process.stdin.flush()
                except Exception:
                    pass

                try:
                    process.stdin.close()
                except Exception:
                    pass

                try:
                    process.wait(timeout=1)
                except Exception:
                    process.terminate()

        except Exception as e:
            print(">>> Speech process cleanup error:", e)

        finally:
            self._speech_process = None

    # ========================================================
    # STOP SPEECH WORKER
    # ========================================================

    def _stop_speech_worker(self):

        self.speech_running = False

        try:
            self.speech_queue.put_nowait("__STOP__")
        except queue.Full:
            pass

        self._close_speech_process()

        thread = getattr(self, "speech_thread", None)

        if thread is not None and thread.is_alive():

            try:
                thread.join(timeout=2)
            except Exception:
                pass

        self._speech_process = None

    # ========================================================
    # FACE ABSENCE HANDLING
    # ========================================================

    def _handle_face_absence(self):

        now = datetime.now()

        if self.face_absence_start is None:

            self.face_absence_start = now
            self.face_warning_issued = False
            self.face_violation_issued = False

            print(">>> Face absence timer started.")

            return

        elapsed = (
            now - self.face_absence_start
        ).total_seconds()

        if (
            elapsed >= self.face_grace_seconds
            and not self.face_warning_issued
        ):

            self.face_warning_issued = True

            self.current_warning = "FACE_ABSENCE_WARNING"

            self.current_warning_message = (
                "Face not detected. "
                "Please return to the camera."
            )

            self.warning_time = now

            print(">>> FACE WARNING: 3 seconds absence.")

            self._speak_warning(
                "Face not detected. "
                "Please return to the camera."
            )

        if (
            elapsed >= self.face_violation_seconds
            and not self.face_violation_issued
        ):

            self.face_violation_issued = True

            self.alert_logger.log_alert(
                "FACE_DISAPPEARED",
                "Face remained absent for 5 seconds."
            )

            print(">>> FACE OFFICIAL VIOLATION")

    # ========================================================
    # FACE RETURN HANDLING
    # ========================================================

    def _handle_face_return(self):

        if self.face_absence_start is not None:

            print(
                ">>> Face returned. "
                "Absence timer reset."
            )

        self.face_absence_start = None
        self.face_warning_issued = False
        self.face_violation_issued = False

    # ========================================================
    # START
    # ========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        print(">>> AI EXAM MONITORING STARTED")

        if self.audio_monitor is not None:

            try:

                self.audio_monitor.start()

                print(">>> Audio monitoring started.")

            except Exception as e:
                print(">>> Audio monitoring start error:", e)

    # ========================================================
    # PROCESS CAMERA FRAME
    # ========================================================

    def process_frame(self, frame):

        if not self.running:
            return

        if frame is None:
            return

        self.alert_logger.set_frame(frame)

        if self.face_detector is not None:

            try:

                self.face_present = (
                    self.face_detector.detect_face(frame)
                )

                if self.face_present:
                    self._handle_face_return()
                else:
                    self._handle_face_absence()

            except Exception as e:
                print(">>> Face processing error:", e)

        if self.multi_face_detector is not None:

            try:

                result = (
                    self.multi_face_detector
                    .detect_multiple_faces(frame)
                )

                self.multiple_faces = (
                    result
                    or getattr(
                        self.multi_face_detector,
                        "consecutive_frames",
                        0
                    ) > 0
                )

            except Exception as e:
                print(">>> Multi-face processing error:", e)

        if self.eye_tracker is not None:

            try:

                (
                    self.gaze_direction,
                    self.eye_ratio
                ) = self.eye_tracker.track_eyes(frame)

            except Exception as e:
                print(">>> Eye processing error:", e)

        if self.mouth_monitor is not None:

            try:

                self.mouth_movement = (
                    self.mouth_monitor.monitor_mouth(frame)
                )

            except Exception as e:
                print(">>> Mouth processing error:", e)

        if self.object_detector is not None:

            try:

                before = (
                    self.object_detector.last_detection_time
                )

                result = self.object_detector.detect_objects(
                    frame,
                    visualize=False
                )

                after = (
                    self.object_detector.last_detection_time
                )

                if after != before:
                    self.forbidden_object = bool(result)

            except Exception as e:
                print(">>> Object processing error:", e)

        # Update audio status if AudioMonitor provides it.
        if self.audio_monitor is not None:

            try:

                self.voice_detected = getattr(
                    self.audio_monitor,
                    "voice_detected",
                    getattr(
                        self.audio_monitor,
                        "speech_detected",
                        False
                    )
                )

            except Exception:
                self.voice_detected = False

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self):

        eye_movement = (
            self.gaze_direction
            not in (
                None,
                "",
                "center"
            )
        )

        warning_active = False

        if self.current_warning is not None:

            if self.warning_time is not None:

                elapsed = (
                    datetime.now()
                    - self.warning_time
                ).total_seconds()

                if elapsed <= 3:
                    warning_active = True

                else:
                    self.current_warning = None
                    self.current_warning_message = ""

        return {

            "face_present":
                self.face_present,

            "multiple_faces":
                self.multiple_faces,

            "gaze":
                self.gaze_direction,

            "eye_ratio":
                self.eye_ratio,

            "eye_movement":
                eye_movement,

            "mouth_movement":
                self.mouth_movement,

            "forbidden_object":
                self.forbidden_object,

            "voice_detected":
                self.voice_detected,

            "warning_active":
                warning_active,

            "warning_type":
                self.current_warning,

            "warning_message":
                self.current_warning_message,

            "eye_warnings":
                self.alert_logger.eye_warning_count,

            "mouth_warnings":
                self.alert_logger.mouth_warning_count,

            "face_absence_seconds":
                self._get_face_absence_seconds(),

            "violations":
                self.alert_logger.violation_count,

            "running":
                self.running
        }

    # ========================================================
    # FACE ABSENCE TIME
    # ========================================================

    def _get_face_absence_seconds(self):

        if self.face_absence_start is None:
            return 0

        return round(
            (
                datetime.now()
                - self.face_absence_start
            ).total_seconds(),
            1
        )

    # ========================================================
    # VIOLATION COUNT
    # ========================================================

    @property
    def violation_count(self):

        return self.alert_logger.violation_count

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        if not self.running:

            if getattr(self, "speech_running", False):
                self._stop_speech_worker()

            return

        self.running = False

        print(">>> STOPPING AI EXAM MONITORING")

        if self.audio_monitor is not None:

            try:

                self.audio_monitor.stop()

                print(">>> Audio monitoring stopped.")

            except Exception as e:
                print(">>> Audio stop error:", e)

        try:

            self._stop_speech_worker()

            print(">>> Warning speech system stopped.")

        except Exception as e:
            print(">>> Speech worker stop error:", e)

        print(">>> AI EXAM MONITORING STOPPED")
