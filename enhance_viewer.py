import json
import socketserver
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageFilter

from PySide6.QtCore import QObject, Signal, QRectF, QVariantAnimation, QEasingCurve, Qt
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem


def pil_to_qimage(pil_img: Image.Image) -> QImage:
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
    return qimg.copy()


@dataclass
class Camera:
    scale: float
    cx: float
    cy: float


class CommandBridge(QObject):
    command = Signal(dict)


class EnhanceView(QGraphicsView):
    def __init__(self, pil_image: Image.Image):
        super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        self._pil_original = pil_image.copy()
        self._pil_current = pil_image.copy()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self._update_pixmap()

        w, h = self._pil_current.size
        self.scene.setSceneRect(QRectF(0, 0, w, h))

        self.camera = self._fit_camera()

        self._anim = None
        self._apply_camera(self.camera)

    def _update_pixmap(self):
        qimg = pil_to_qimage(self._pil_current)
        self.pixmap_item.setPixmap(QPixmap.fromImage(qimg))
        self.pixmap_item.setPos(0, 0)

    def _fit_camera(self) -> Camera:
        w, h = self._pil_current.size
        vw = max(1, self.viewport().width())
        vh = max(1, self.viewport().height())
        scale = min(vw / w, vh / h)
        return Camera(scale=scale, cx=w / 2, cy=h / 2)

    def _apply_camera(self, cam: Camera):
        self.resetTransform()
        self.scale(cam.scale, cam.scale)
        self.centerOn(cam.cx, cam.cy)

    def _animate_to(self, target: Camera, ms: int = 250):
        start = Camera(self.camera.scale, self.camera.cx, self.camera.cy)

        if self._anim is not None:
            self._anim.stop()

        anim = QVariantAnimation(self)
        anim.setDuration(max(1, ms))
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def lerp(a: float, b: float, t: float) -> float:
            return a + (b - a) * t

        def on_value(t):
            t = float(t)
            cam = Camera(
                scale=lerp(start.scale, target.scale, t),
                cx=lerp(start.cx, target.cx, t),
                cy=lerp(start.cy, target.cy, t),
            )
            self._apply_camera(cam)

        def on_finished():
            self.camera = target
            self._apply_camera(self.camera)

        anim.valueChanged.connect(on_value)
        anim.finished.connect(on_finished)
        self._anim = anim
        anim.start()

    def cmd_zoom(self, factor: float, ms: int = 250):
        factor = float(factor)
        target = Camera(
            scale=max(0.02, min(self.camera.scale * factor, 200.0)),
            cx=self.camera.cx,
            cy=self.camera.cy,
        )
        self._animate_to(target, ms)

    def cmd_set_zoom(self, scale: float, ms: int = 250):
        scale = float(scale)
        target = Camera(
            scale=max(0.02, min(scale, 200.0)),
            cx=self.camera.cx,
            cy=self.camera.cy,
        )
        self._animate_to(target, ms)

    def cmd_pan(self, dx_px: float, dy_px: float, ms: int = 250):
        # dx/dy задаются в экранных пикселях
        dx_scene = float(dx_px) / max(1e-9, self.camera.scale)
        dy_scene = float(dy_px) / max(1e-9, self.camera.scale)

        w, h = self._pil_current.size
        cx = self.camera.cx + dx_scene
        cy = self.camera.cy + dy_scene

        # легкий clamp, чтобы не улететь далеко
        cx = max(0, min(w, cx))
        cy = max(0, min(h, cy))

        target = Camera(scale=self.camera.scale, cx=cx, cy=cy)
        self._animate_to(target, ms)

    def cmd_fit(self, ms: int = 300):
        target = self._fit_camera()
        self._animate_to(target, ms)

    def cmd_reset_image(self):
        self._pil_current = self._pil_original.copy()
        self._update_pixmap()
        w, h = self._pil_current.size
        self.scene.setSceneRect(QRectF(0, 0, w, h))
        self.camera = self._fit_camera()
        self._apply_camera(self.camera)

    def cmd_sharpen(self, amount: float = 1.0):
        # amount: 0..3 разумно
        a = max(0.0, min(float(amount), 5.0))
        # Простая "киношная" резкость: UnsharpMask
        self._pil_current = self._pil_current.filter(
            ImageFilter.UnsharpMask(radius=2, percent=int(120 + 200 * a), threshold=3)
        )
        self._update_pixmap()

    def cmd_crop_view(self, out_path: str | None = None):
        # Вырезать текущий вид (то, что в окне)
        rect = self.mapToScene(self.viewport().rect()).boundingRect()
        w, h = self._pil_current.size
        left = int(max(0, min(w, rect.left())))
        top = int(max(0, min(h, rect.top())))
        right = int(max(0, min(w, rect.right())))
        bottom = int(max(0, min(h, rect.bottom())))

        if right <= left or bottom <= top:
            return

        crop = self._pil_current.crop((left, top, right, bottom))

        if out_path is None:
            ts = time.strftime("%Y%m%d_%H%M%S")
            out_path = f"crop_{ts}.png"

        crop.save(out_path)


class JsonLineTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break
            try:
                obj = json.loads(line.decode("utf-8", errors="replace").strip())
                self.server.bridge.command.emit(obj)
            except Exception:
                continue


class CommandServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host: str, port: int, bridge: CommandBridge):
        super().__init__((host, port), JsonLineTCPHandler)
        self.bridge = bridge


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhance_viewer.py <image_path>")
        sys.exit(1)

    img_path = Path(sys.argv[1]).expanduser().resolve()
    pil_img = Image.open(img_path).convert("RGBA")

    app = QApplication(sys.argv)

    bridge = CommandBridge()
    view = EnhanceView(pil_img)
    view.setWindowTitle("ENHANCE")
    view.resize(1100, 700)
    view.show()

    def on_cmd(cmd: dict):
        name = cmd.get("cmd")
        ms = int(cmd.get("ms", 250))

        if name == "zoom":
            view.cmd_zoom(cmd.get("factor", 1.0), ms)
        elif name == "set_zoom":
            view.cmd_set_zoom(cmd.get("scale", view.camera.scale), ms)
        elif name == "pan":
            view.cmd_pan(cmd.get("dx", 0), cmd.get("dy", 0), ms)
        elif name == "fit":
            view.cmd_fit(ms)
        elif name == "reset_image":
            view.cmd_reset_image()
        elif name == "sharpen":
            view.cmd_sharpen(cmd.get("amount", 1.0))
        elif name == "crop_view":
            view.cmd_crop_view(cmd.get("out"))
        # можно расширять дальше без усложнения

    bridge.command.connect(on_cmd)

    # TCP server in background thread
    server = CommandServer("127.0.0.1", 8765, bridge)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()