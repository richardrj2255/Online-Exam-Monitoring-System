import cv2
import socket
import struct
import threading
import time


class CameraStreamer:

    def __init__(
        self,
        register_no,
        host="127.0.0.1",
        port=5001,
        quality=60,
        fps=8
    ):
        self.register_no = str(register_no)
        self.host = host
        self.port = port

        self.quality = quality
        self.fps = fps

        self.running = False
        self.thread = None
        self.socket = None

        self.current_frame = None
        self.frame_lock = threading.Lock()

    # =========================================================
    # START
    # =========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

        print(
            f">>> Camera streamer started for "
            f"{self.register_no}"
        )

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.running = False

        if self.socket is not None:

            try:
                self.socket.shutdown(
                    socket.SHUT_RDWR
                )
            except Exception:
                pass

            try:
                self.socket.close()
            except Exception:
                pass

            self.socket = None

        if self.thread is not None:

            self.thread.join(
                timeout=1
            )

        print(
            f">>> Camera streamer stopped for "
            f"{self.register_no}"
        )

    # =========================================================
    # UPDATE FRAME
    # =========================================================

    def update_frame(self, frame):

        if frame is None:
            return

        with self.frame_lock:

            self.current_frame = frame.copy()

    # =========================================================
    # MAIN STREAM THREAD
    # =========================================================

    def _run(self):

        while self.running:

            try:

                self._connect()

                self._stream_frames()

            except Exception as e:

                print(
                    ">>> Camera streaming error:",
                    e
                )

                self._close_socket()

                if self.running:

                    print(
                        ">>> Retrying connection..."
                    )

                    time.sleep(2)

    # =========================================================
    # CONNECT TO ADMIN
    # =========================================================

    def _connect(self):

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.socket.settimeout(5)

        self.socket.connect(
            (
                self.host,
                self.port
            )
        )

        self.socket.settimeout(None)

        # Send register number first
        register_bytes = (
            self.register_no.encode("utf-8")
        )

        header = struct.pack(
            "!I",
            len(register_bytes)
        )

        self.socket.sendall(
            header + register_bytes
        )

        print(
            f">>> Connected to Admin-App "
            f"({self.host}:{self.port})"
        )

    # =========================================================
    # STREAM FRAMES
    # =========================================================

    def _stream_frames(self):

        frame_interval = (
            1.0 / self.fps
        )

        while self.running:

            start_time = time.time()

            with self.frame_lock:

                if self.current_frame is None:

                    time.sleep(
                        frame_interval
                    )

                    continue

                frame = (
                    self.current_frame.copy()
                )

            # Resize for network transmission
            frame = cv2.resize(
                frame,
                (480, 360)
            )

            success, encoded = cv2.imencode(
                ".jpg",
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.quality
                ]
            )

            if not success:
                continue

            data = encoded.tobytes()

            # Send frame size followed by JPEG data
            header = struct.pack(
                "!I",
                len(data)
            )

            self.socket.sendall(
                header + data
            )

            elapsed = (
                time.time() - start_time
            )

            sleep_time = (
                frame_interval - elapsed
            )

            if sleep_time > 0:

                time.sleep(
                    sleep_time
                )

    # =========================================================
    # CLOSE SOCKET
    # =========================================================

    def _close_socket(self):

        if self.socket is not None:

            try:
                self.socket.close()
            except Exception:
                pass

            self.socket = None