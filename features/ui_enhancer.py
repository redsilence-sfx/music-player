from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPainter, QPainterPath

import constants as C
from features.theme import MoodColorEngine


class UIEnhancer:
    """
    Glassmorphism + dynamic album gradient.
    Modul ini sengaja dipisah supaya app/player.py tidak makin numpuk.
    """

    def __init__(self, window):
        self.w = window

    def install(self):
        self.apply_base_glass()
        self.apply_compact_nav_polish()
        self.apply_album_gradient()

    def apply_base_glass(self):
        """
        Patch QSS global. Efek glass di Qt bukan real backdrop blur,
        tapi simulasi modern via rgba, border transparan, dan shadow.
        """
        glass_qss = """
        QWidget#nowPlayingCard,
        QWidget#queueArea,
        QWidget#devCard,
        QWidget#versionCard,
        QWidget#techCard,
        QWidget#licenseCard {
            background-color: rgba(20, 20, 32, 218);
            border: 1px solid rgba(255, 255, 255, 26);
            border-radius: 22px;
        }

        QListWidget#queueList::item,
        QListWidget#songList::item,
        QListWidget#libraryList::item,
        QListWidget#searchResultList::item,
        QListWidget#favList::item {
            background-color: rgba(255, 255, 255, 7);
            border: 1px solid rgba(255, 255, 255, 14);
            border-radius: 12px;
        }

        QListWidget#queueList::item:hover,
        QListWidget#songList::item:hover,
        QListWidget#libraryList::item:hover,
        QListWidget#searchResultList::item:hover,
        QListWidget#favList::item:hover {
            background-color: rgba(167, 139, 250, 24);
            border: 1px solid rgba(196, 181, 253, 72);
            color: #FFFFFF;
        }

        QLineEdit#searchInput {
            background-color: rgba(255, 255, 255, 10);
            border: 1px solid rgba(255, 255, 255, 28);
            border-radius: 16px;
            color: #E5E7EB;
        }

        QLineEdit#searchInput:focus {
            border: 1px solid rgba(196, 181, 253, 130);
            background-color: rgba(167, 139, 250, 16);
        }
        """

        self.w.setStyleSheet(self.w.styleSheet() + "\n" + glass_qss)

    def apply_compact_nav_polish(self):
        """
        Memperhalus top navigation yang sudah ada di player.py.
        Di repo kamu top nav sudah dibuat lewat _setup_top_navigation(),
        jadi di sini kita cuma poles styling-nya.
        """
        nav = getattr(self.w, "topNavBar", None)
        if not nav:
            return

        nav.setStyleSheet("""
            QFrame#topNavBar {
                background-color: rgba(10, 10, 15, 230);
                border-bottom: 1px solid rgba(255, 255, 255, 22);
            }

            QWidget#topBrand {
                background-color: transparent;
            }

            QPushButton#btnNavSwitch {
                background-color: rgba(255, 255, 255, 9);
                border: 1px solid rgba(255, 255, 255, 28);
                border-radius: 14px;
            }

            QPushButton#btnNavSwitch:hover {
                background-color: rgba(167, 139, 250, 30);
                border: 1px solid rgba(196, 181, 253, 90);
            }
        """)

    def apply_song_cover(self, filepath: str):
        """
        Ambil album art dari file audio lalu apply ke tombol album art.
        Jika tidak ada cover, app tetap jalan pakai cover default.
        """
        cover = self.extract_album_cover(filepath, C.ALBUM_ART_SIZE)
        if cover and not cover.isNull():
            self.w.albumArtBtn.setText("")
            self.w.albumArtBtn.setIcon(QIcon(cover))
            self.w.albumArtBtn.setIconSize(cover.size())

        self.apply_album_gradient()

    def apply_album_gradient(self):
        """
        Ambil warna dominan dari album art lalu jadikan gradient card.
        """
        if not hasattr(self.w, "albumArtBtn"):
            return

        icon = self.w.albumArtBtn.icon()
        if icon.isNull():
            accent = QColor("#A78BFA")
        else:
            px = icon.pixmap(220, 220)
            accent = MoodColorEngine.extract(px) if not px.isNull() else QColor("#A78BFA")

        palette = MoodColorEngine.make_palette(accent)
        rgb = f"{accent.red()}, {accent.green()}, {accent.blue()}"

        card_qss = f"""
            QWidget#nowPlayingCard {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba({rgb}, 74),
                    stop:0.42 rgba(20, 20, 32, 235),
                    stop:1 rgba(10, 10, 15, 245)
                );
                border: 1px solid rgba({rgb}, 92);
                border-radius: 26px;
            }}

            QWidget#queueArea {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 12),
                    stop:1 rgba({rgb}, 28)
                );
                border: 1px solid rgba({rgb}, 54);
                border-radius: 22px;
            }}
        """

        if hasattr(self.w, "nowPlayingCard"):
            self.w.nowPlayingCard.setStyleSheet(card_qss)

        if hasattr(self.w, "queueArea"):
            self.w.queueArea.setStyleSheet(card_qss)

        if hasattr(self.w, "progressSlider"):
            self.w.progressSlider.setStyleSheet(f"""
                QSlider#progressSlider::groove:horizontal {{
                    height: 4px;
                    background: rgba(255, 255, 255, 32);
                    border-radius: 2px;
                }}

                QSlider#progressSlider::handle:horizontal {{
                    background: #FFFFFF;
                    width: 14px;
                    height: 14px;
                    margin: -5px 0;
                    border-radius: 7px;
                }}

                QSlider#progressSlider::sub-page:horizontal {{
                    background: {palette["accent"]};
                    border-radius: 2px;
                }}
            """)

        if hasattr(self.w, "btnPlay"):
            self.w.btnPlay.setStyleSheet(f"""
                QPushButton#btnPlay {{
                    background-color: {palette["accent"]};
                    color: #0A0A0F;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 28px;
                    min-width: 56px;
                    max-width: 56px;
                    min-height: 56px;
                    max-height: 56px;
                    text-align: center;
                    padding: 0px;
                }}

                QPushButton#btnPlay:hover {{
                    background-color: {palette["hover"]};
                }}

                QPushButton#btnPlay:pressed {{
                    background-color: {palette["dark"]};
                    color: #E5E7EB;
                }}
            """)

    def extract_album_cover(self, filepath: str, size: int = 220) -> QPixmap:
        """
        Support utama: MP3 APIC, FLAC pictures, MP4/M4A covr.
        Kalau file tidak punya cover, return QPixmap kosong.
        """
        try:
            from mutagen import File as MutagenFile

            audio = MutagenFile(filepath)
            if not audio:
                return QPixmap()

            data = None

            if hasattr(audio, "tags") and audio.tags:
                for key, value in audio.tags.items():
                    if str(key).startswith("APIC"):
                        data = value.data
                        break

                if data is None and "covr" in audio.tags:
                    covers = audio.tags.get("covr")
                    if covers:
                        data = bytes(covers[0])

            if data is None and hasattr(audio, "pictures") and audio.pictures:
                data = audio.pictures[0].data

            if not data:
                return QPixmap()

            pix = QPixmap()
            pix.loadFromData(data)

            if pix.isNull():
                return QPixmap()

            return self._rounded_pixmap(pix, size)

        except Exception:
            return QPixmap()

    def _rounded_pixmap(self, pixmap: QPixmap, size: int) -> QPixmap:
        if pixmap.isNull():
            return QPixmap()
            
        raw = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        x = max(0, (raw.width() - size) // 2)
        y = max(0, (raw.height() - size) // 2)
        raw = raw.copy(x, y, size, size)

        result = QPixmap(size, size)
        result.fill(Qt.transparent)

        painter = QPainter()
        if not painter.begin(result):
            return raw
            
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, 18, 18)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, raw)
        painter.end()

        return result
