import os
import sys
import ctypes

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

import logger
from app.player import MusicPlayer
from app.helpers import resource_path, _svg_icon


def exception_hook(exctype, value, traceback):
    import traceback as tb
    err_msg = "".join(tb.format_exception(exctype, value, traceback))
    logger.error(f"Unhandled Exception:\n{err_msg}")
    
    try:
        # Tampilkan messagebox jika QApplication sudah berjalan
        if QApplication.instance():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("SoundWave Error")
            msg.setText("Terjadi kesalahan tidak terduga pada SoundWave!")
            msg.setInformativeText(str(value))
            msg.setDetailedText(err_msg)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #0A0A0F;
                    color: #E2E8F0;
                    font-family: 'Segoe UI';
                }
                QLabel {
                    color: #E2E8F0;
                }
                QPushButton {
                    background-color: #8B5CF6;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #A78BFA;
                }
            """)
            msg.exec_()
    except Exception as e:
        logger.error(f"Error displaying exception dialog: {e}")
        
    sys.__excepthook__(exctype, value, traceback)


def main():
    # ── High DPI Scaling Configuration ──
    # Menjadikan font dan visual elements sangat tajam (crisp/gacor) di layar resolusi tinggi/Windows scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # ── Taskbar Grouping Fix for Windows ──
    # Memaksa Windows menggunakan icon custom aplikasi pada Taskbar (bukan icon default python/launcher)
    try:
        myappid = 'redsilence.soundwave.musicplayer.4.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    logger.boot()
    
    # Register global exception handler
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    app.setApplicationName("SoundWave")
    app.setOrganizationName("Redsilence")
    app.setApplicationVersion("4.0")
    
    # ── Application Icon Setup ──
    try:
        icon_path = resource_path("icons", "svg", "zap.svg")
        app_icon = _svg_icon(icon_path, "#A78BFA", 64)
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
    except Exception as e:
        logger.warn(f"Gagal memuat application icon: {e}")

    window = MusicPlayer()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
