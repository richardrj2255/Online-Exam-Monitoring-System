import socket
import struct
import threading
import cv2
import numpy as np


class CameraClient:

    def __init__(
        self,
        connection,
        address,
        on_frame,
        on_disconnect
    ):
        self.connection = connection
        self.address = address

        self.on_frame = on_frame
        self.on_disconnect = on_disconnect

        self.register_no = None
        self.running = True

        self.thread = threading.Thread(
            target=self._receive,
            daemon=True
        )

    def start(self):

        self.thread.start()

    # =========================================================
    # RECEIVE EXACT NUMBER OF BYTES
    # =========================================================

    def _receive_exact(self, size):

        data = b""

        while len(data) < size:

            packet = self.connection.recv(
                size - len(data)
            )

            if not packet:
                return None

            data += packet

        return data

    # =========================================================
    # RECEIVE DATA
    # =========================================================

    def _receive(self):

        try:

            # -------------------------------------------------
            # REGISTER NUMBER
            # -------------------------------------------------

            header = self._receive_exact(4)

            if header is None:
                return

            register_length = struct.unpack(
                "!I",
                header
            )[0]

            register_data = (
                self._receive_exact(
                    register_length
                )
            )

            if register_data is None:
                return

            self.register_no = (
                register_data
                .decode("utf-8")
            )

            print(
                f">>> Student connected: "
                f"{self.register_no}"
            )

            # -------------------------------------------------
            # CAMERA FRAMES
            # -------------------------------------------------

            while self.running:

                header = (
                    self._receive_exact(4)
                )

                if header is None:
                    break

                frame_size = struct.unpack(
                    "!I",
                    header
                )[0]

                # Safety check
                if frame_size <= 0 or frame_size > 5_000_000:
                    print(
                        ">>> Invalid frame size:",
                        frame_size
                    )
                    break

                frame_data = (
                    self._receive_exact(
                        frame_size
                    )
                )

                if frame_data is None:
                    break

                frame_array = np.frombuffer(
                    frame_data,
                    dtype=np.uint8
                )

                frame = cv2.imdecode(
                    frame_array,
                    cv2.IMREAD_COLOR
                )

                if frame is None:
                    continue

                self.on_frame(
                    self.register_no,
                    frame
                )

        except Exception as e:

            print(
                f">>> Client error "
                f"{self.address}:",
                e
            )

        finally:

            self.running = False

            try:
                self.connection.close()
            except Exception:
                pass

            self.on_disconnect(
                self.register_no
            )


# =============================================================
# CAMERA SERVER
# =============================================================

class CameraServer:

    def __init__(
        self,
        host="0.0.0.0",
        port=5001,
        on_frame=None,
        on_disconnect=None
    ):

        self.host = host
        self.port = port

        self.on_frame = (
            on_frame
            if on_frame
            else self._default_frame
        )

        self.on_disconnect = (
            on_disconnect
            if on_disconnect
            else self._default_disconnect
        )

        self.server_socket = None

        self.running = False

        self.clients = []

        self.server_thread = None

    # =========================================================
    # START SERVER
    # =========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.server_thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.server_thread.start()

        print(
            f">>> Camera server started "
            f"on port {self.port}"
        )

    # =========================================================
    # SERVER LOOP
    # =========================================================

    def _run(self):

        try:

            self.server_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            self.server_socket.bind(
                (
                    self.host,
                    self.port
                )
            )

            self.server_socket.listen(10)

            print(
                f">>> Waiting for Student-App "
                f"connections on "
                f"{self.host}:{self.port}"
            )

            while self.running:

                connection, address = (
                    self.server_socket.accept()
                )

                client = CameraClient(
                    connection,
                    address,
                    self.on_frame,
                    self.on_disconnect
                )

                self.clients.append(
                    client
                )

                client.start()

        except Exception as e:

            if self.running:

                print(
                    ">>> Camera server error:",
                    e
                )

        finally:

            self.stop()

    # =========================================================
    # STOP SERVER
    # =========================================================

    def stop(self):

        self.running = False

        if self.server_socket is not None:

            try:
                self.server_socket.close()
            except Exception:
                pass

            self.server_socket = None

        for client in self.clients:

            client.running = False

            try:
                client.connection.close()
            except Exception:
                pass

        self.clients.clear()

        print(
            ">>> Camera server stopped."
        )

    # =========================================================
    # DEFAULT CALLBACKS
    # =========================================================

    def _default_frame(
        self,
        register_no,
        frame
    ):

        print(
            f"Received frame from "
            f"{register_no}"
        )

    def _default_disconnect(
        self,
        register_no
    ):

        print(
            f">>> Student disconnected: "
            f"{register_no}"
        )