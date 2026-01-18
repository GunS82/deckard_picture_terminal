import json
import socketserver
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from PIL import Image

# Mocking Qt components for headless run
class MockSignal:
    def __init__(self):
        self._slots = []
    def connect(self, func):
        self._slots.append(func)
    def emit(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)

@dataclass
class Camera:
    scale: float
    cx: float
    cy: float

class CommandBridge:
    command = MockSignal()

class HeadlessViewer:
    def __init__(self, pil_image: Image.Image):
        print("[Headless] Viewer initialized.")
        self._pil_original = pil_image.copy()
        w, h = self._pil_original.size
        print(f"[Headless] Image loaded: {w}x{h}")
        self.camera = Camera(scale=1.0, cx=w/2, cy=h/2)

    def log_state(self):
        print(f"[State] Scale: {self.camera.scale:.2f}, Center: ({self.camera.cx:.1f}, {self.camera.cy:.1f})")

    def cmd_zoom(self, factor: float, ms: int = 250):
        print(f"[CMD] ZOOM factor={factor} duration={ms}ms")
        self.camera.scale *= factor
        self.log_state()

    def cmd_pan(self, dx: float, dy: float, ms: int = 250):
        print(f"[CMD] PAN dx={dx} dy={dy} duration={ms}ms")
        self.camera.cx += dx
        self.camera.cy += dy
        self.log_state()

    def cmd_fit(self, ms: int = 300):
        print(f"[CMD] FIT duration={ms}ms")
        self.camera.scale = 1.0 # simplified fit
        self.log_state()

    def cmd_sharpen(self, amount: float = 1.0):
        print(f"[CMD] SHARPEN amount={amount}")
        print("[Effect] *Enhance noises*")

    def cmd_crop_view(self, out_path: str | None = None):
        print(f"[CMD] CROP out={out_path}")

    def cmd_reset_image(self):
        print("[CMD] RESET")
        self.camera.scale = 1.0

class JsonLineTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break
            try:
                obj = json.loads(line.decode("utf-8", errors="replace").strip())
                # Access bridge from server
                self.server.bridge.command.emit(obj)
            except Exception as e:
                print(f"Error handling cmd: {e}")
                continue

class CommandServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, host: str, port: int, bridge: CommandBridge):
        super().__init__((host, port), JsonLineTCPHandler)
        self.bridge = bridge

def main():
    import sys
    # Force unbuffered output so the user sees logs immediately
    sys.stdout.reconfigure(line_buffering=True)

    img_path = "sample.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]

    # Just verify we can open the image
    try:
        pil_img = Image.open(img_path)
    except Exception as e:
        print(f"Failed to open image: {e}")
        sys.exit(1)

    bridge = CommandBridge()
    view = HeadlessViewer(pil_img)

    def on_cmd(cmd: dict):
        name = cmd.get("cmd")
        ms = int(cmd.get("ms", 250))
        
        if name == "zoom":
            view.cmd_zoom(cmd.get("factor", 1.0), ms)
        elif name == "pan":
            view.cmd_pan(cmd.get("dx", 0), cmd.get("dy", 0), ms)
        elif name == "fit":
            view.cmd_fit(ms)
        elif name == "sharpen":
            view.cmd_sharpen(cmd.get("amount", 1.0))
        elif name == "crop_view":
            view.cmd_crop_view(cmd.get("out"))
        elif name == "reset_image":
            view.cmd_reset_image()

    bridge.command.connect(on_cmd)

    print(f"[Headless] TCP Server listening on 127.0.0.1:8765...")
    server = CommandServer("127.0.0.1", 8765, bridge)
    server.serve_forever()

if __name__ == "__main__":
    main()
