from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QColor


class Toast(QWidget):
    closed = pyqtSignal(object)

    COLORS = {
        "success": ("#22C55E", "✅"),
        "info": ("#A78BFA", "ℹ"),
        "warning": ("#F59E0B", "⚠"),
        "error": ("#EF4444", "✕"),
        "music": ("#C4B5FD", "♪"),
    }

    def __init__(self, parent, title: str, message: str = "", kind: str = "info", duration: int = 2600):
        super().__init__(parent)
        self.parent_ref = parent
        self.duration = duration
        self.kind = kind if kind in self.COLORS else "info"

        accent, icon = self.COLORS[self.kind]

        self.setObjectName("toast")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        self.lbl_title = QLabel(f"{icon}  {title}")
        self.lbl_title.setObjectName("toastTitle")

        self.lbl_msg = QLabel(message)
        self.lbl_msg.setObjectName("toastMessage")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setVisible(bool(message))

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_msg)

        self.setStyleSheet(f"""
            QWidget#toast {{
                background-color: rgba(17, 18, 30, 238);
                border: 1px solid rgba(255, 255, 255, 32);
                border-left: 4px solid {accent};
                border-radius: 16px;
            }}

            QLabel#toastTitle {{
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 800;
                font-family: "Segoe UI";
            }}

            QLabel#toastMessage {{
                color: #A1A1AA;
                font-size: 11px;
                font-family: "Segoe UI";
            }}
        """)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.move_anim = QPropertyAnimation(self, b"pos")
        self.move_anim.setDuration(260)
        self.move_anim.setEasingCurve(QEasingCurve.OutCubic)

    def show_at(self, x: int, y: int):
        self.adjustSize()

        start = QPoint(x + 24, y)
        end = QPoint(x, y)

        self.move(start)
        self.show()
        self.raise_()

        self.fade_anim.stop()
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()

        self.move_anim.stop()
        self.move_anim.setStartValue(start)
        self.move_anim.setEndValue(end)
        self.move_anim.start()

        QTimer.singleShot(self.duration, self.close_animated)

    def close_animated(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.finished.connect(self._finish_close)
        self.fade_anim.start()

    def _finish_close(self):
        try:
            self.closed.emit(self)
            self.deleteLater()
        except RuntimeError:
            pass


class ToastManager:
    def __init__(self, parent):
        self.parent = parent
        self.toasts = []

    def show(self, title: str, message: str = "", kind: str = "info", duration: int = 2600):
        toast = Toast(self.parent, title, message, kind, duration)
        toast.closed.connect(self._remove)

        self.toasts.append(toast)
        self._reflow()

    def _remove(self, toast):
        if toast in self.toasts:
            self.toasts.remove(toast)
        self._reflow(existing_only=True)

    def _reflow(self, existing_only=False):
        margin = 22
        gap = 12
        y = 76

        for toast in self.toasts:
            toast.adjustSize()
            x = self.parent.width() - toast.width() - margin

            if existing_only and toast.isVisible():
                toast.move(x, y)
            else:
                toast.show_at(x, y)

            y += toast.height() + gap