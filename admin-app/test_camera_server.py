from streaming.camera_server import CameraServer
import time

def on_frame(register_no, frame):
    print(
        f">>> FRAME RECEIVED from {register_no} "
        f"size={frame.shape}"
    )


def on_disconnect(register_no):
    print(
        f">>> STUDENT DISCONNECTED: {register_no}"
    )


server = CameraServer(
    host="0.0.0.0",
    port=5001,
    on_frame=on_frame,
    on_disconnect=on_disconnect
)

server.start()

print("======================================")
print(" CAMERA SERVER TEST")
print(" Listening on port 5001")
print(" Waiting for Student-App...")
print(" Press Ctrl+C to stop")
print("======================================")

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("\n>>> Stopping server...")
    server.stop()