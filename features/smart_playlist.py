import os
import random
from dataclasses import dataclass

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
)


@dataclass
class SmartPlaylistResult:
    name: str
    description: str
    songs: list[str]


class SmartPlaylistGenerator:
    """
    Generator playlist sederhana berbasis heuristik.
    Belum pakai AI API, jadi aman offline dan ringan.
    """

    MOOD_KEYWORDS = {
        "Chill": [
            "chill", "lofi", "lo-fi", "slow", "calm", "soft", "sleep",
            "acoustic", "piano", "rain", "sad", "relax"
        ],
        "Focus": [
            "focus", "study", "deep", "ambient", "instrumental", "coding",
            "work", "brain", "lofi", "piano"
        ],
        "Energy": [
            "rock", "edm", "party", "dance", "speed", "hard", "bass",
            "remix", "workout", "gym", "drum", "beat"
        ],
        "Night": [
            "night", "midnight", "moon", "dark", "blue", "late",
            "city", "rain", "dream"
        ],
        "Love": [
            "love", "heart", "romance", "romantic", "sayang", "cinta",
            "rindu", "miss", "beautiful"
        ],
    }

    def suggest(self, songs: list[str], mode: str = "Surprise", favorites=None, max_songs: int = 20) -> SmartPlaylistResult:
        favorites = favorites or set()
        clean_songs = [fp for fp in songs if os.path.exists(fp)]

        if not clean_songs:
            return SmartPlaylistResult(
                name="Smart Mix - Empty",
                description="Belum ada lagu yang bisa diproses.",
                songs=[]
            )

        if mode == "Favorites Boost":
            selected = list(favorites)[:max_songs]
            if len(selected) < 5:
                selected += random.sample(clean_songs, min(max_songs - len(selected), len(clean_songs)))
            return SmartPlaylistResult(
                name="Smart Mix - Favorites",
                description="Campuran lagu favorit dan beberapa lagu tambahan.",
                songs=self._unique(selected)[:max_songs],
            )

        if mode in self.MOOD_KEYWORDS:
            selected = self._by_keywords(clean_songs, self.MOOD_KEYWORDS[mode], max_songs)

            if len(selected) < 5:
                fallback = random.sample(clean_songs, min(max_songs, len(clean_songs)))
                selected = self._unique(selected + fallback)

            return SmartPlaylistResult(
                name=f"Smart Mix - {mode}",
                description=f"Playlist otomatis berdasarkan mood {mode}.",
                songs=selected[:max_songs],
            )

        shuffled = clean_songs[:]
        random.shuffle(shuffled)

        return SmartPlaylistResult(
            name="Smart Mix - Surprise",
            description="Campuran acak agar queue tidak monoton.",
            songs=shuffled[:max_songs],
        )

    def _by_keywords(self, songs: list[str], keywords: list[str], max_songs: int):
        scored = []

        for fp in songs:
            name = os.path.splitext(os.path.basename(fp))[0].lower()
            score = 0

            for keyword in keywords:
                if keyword in name:
                    score += 3

            if score > 0:
                scored.append((score, fp))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [fp for _, fp in scored[:max_songs]]

    def _unique(self, items: list[str]):
        seen = set()
        result = []

        for item in items:
            if item not in seen and os.path.exists(item):
                seen.add(item)
                result.append(item)

        return result


class SmartPlaylistDialog(QDialog):
    create_playlist = pyqtSignal(str, list)

    def __init__(self, generator: SmartPlaylistGenerator, songs: list[str], favorites=None, parent=None):
        super().__init__(parent)

        self.generator = generator
        self.songs = songs
        self.favorites = favorites or set()
        self.current_result = None

        self.setWindowTitle("Smart Playlist Generator")
        self.setMinimumSize(620, 520)
        self.setObjectName("smartPlaylistDialog")

        self._build_ui()
        self._apply_style()
        self._preview("Surprise")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("Smart Playlist Generator")
        title.setObjectName("smartTitle")

        subtitle = QLabel("Buat playlist otomatis berdasarkan mood, nama lagu, dan favorit.")
        subtitle.setObjectName("smartSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        mood_bar = QHBoxLayout()
        mood_bar.setSpacing(8)

        self.mood_buttons = []

        for mood in ["Surprise", "Chill", "Focus", "Energy", "Night", "Love", "Favorites Boost"]:
            btn = QPushButton(mood)
            btn.setObjectName("moodButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, m=mood: self._preview(m))
            mood_bar.addWidget(btn)
            self.mood_buttons.append(btn)

        root.addLayout(mood_bar)

        info_card = QFrame()
        info_card.setObjectName("smartInfoCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(4)

        self.lbl_result_name = QLabel("-")
        self.lbl_result_name.setObjectName("resultName")

        self.lbl_result_desc = QLabel("-")
        self.lbl_result_desc.setObjectName("resultDesc")
        self.lbl_result_desc.setWordWrap(True)

        info_layout.addWidget(self.lbl_result_name)
        info_layout.addWidget(self.lbl_result_desc)

        root.addWidget(info_card)

        self.preview_list = QListWidget()
        self.preview_list.setObjectName("smartPreviewList")
        root.addWidget(self.preview_list, 1)

        action_bar = QHBoxLayout()
        action_bar.addStretch(1)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("smartCancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_create = QPushButton("Create Playlist")
        self.btn_create.setObjectName("smartCreate")
        self.btn_create.clicked.connect(self._emit_create)

        action_bar.addWidget(self.btn_cancel)
        action_bar.addWidget(self.btn_create)

        root.addLayout(action_bar)

    def _preview(self, mood: str):
        for btn in self.mood_buttons:
            btn.setProperty("active", btn.text() == mood)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.current_result = self.generator.suggest(
            songs=self.songs,
            mode=mood,
            favorites=self.favorites,
            max_songs=20,
        )

        self.lbl_result_name.setText(self.current_result.name)
        self.lbl_result_desc.setText(self.current_result.description)

        self.preview_list.clear()

        if not self.current_result.songs:
            self.preview_list.addItem("Belum ada lagu. Tambahkan lagu dulu ke library/queue.")
            self.btn_create.setEnabled(False)
            return

        self.btn_create.setEnabled(True)

        for fp in self.current_result.songs:
            name = os.path.splitext(os.path.basename(fp))[0]
            item = QListWidgetItem(f"♪ {name}")
            item.setData(Qt.UserRole, fp)
            self.preview_list.addItem(item)

    def _emit_create(self):
        if not self.current_result or not self.current_result.songs:
            return

        self.create_playlist.emit(self.current_result.name, self.current_result.songs)
        self.accept()

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog#smartPlaylistDialog {
                background-color: #090914;
            }

            QLabel#smartTitle {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: 900;
                font-family: "Segoe UI";
            }

            QLabel#smartSubtitle {
                color: #8B8BA7;
                font-size: 12px;
                font-family: "Segoe UI";
            }

            QFrame#smartInfoCard {
                background-color: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 24);
                border-radius: 18px;
            }

            QLabel#resultName {
                color: #C4B5FD;
                font-size: 16px;
                font-weight: 800;
            }

            QLabel#resultDesc {
                color: #A1A1AA;
                font-size: 12px;
            }

            QPushButton#moodButton {
                background-color: rgba(255, 255, 255, 9);
                color: #A1A1AA;
                border: 1px solid rgba(255, 255, 255, 22);
                border-radius: 12px;
                padding: 9px 12px;
                font-size: 11px;
                font-weight: 700;
                text-align: center;
            }

            QPushButton#moodButton:hover {
                background-color: rgba(167, 139, 250, 28);
                color: #FFFFFF;
                border: 1px solid rgba(196, 181, 253, 82);
            }

            QPushButton#moodButton[active="true"] {
                background-color: rgba(167, 139, 250, 52);
                color: #FFFFFF;
                border: 1px solid rgba(196, 181, 253, 120);
            }

            QListWidget#smartPreviewList {
                background-color: rgba(255, 255, 255, 8);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 18px;
                color: #E5E7EB;
                padding: 8px;
                outline: none;
            }

            QListWidget#smartPreviewList::item {
                padding: 10px 12px;
                margin: 3px;
                border-radius: 12px;
                color: #CBD5E1;
            }

            QListWidget#smartPreviewList::item:hover {
                background-color: rgba(167, 139, 250, 30);
                color: #FFFFFF;
            }

            QPushButton#smartCancel,
            QPushButton#smartCreate {
                min-width: 130px;
                min-height: 38px;
                border-radius: 14px;
                font-size: 12px;
                font-weight: 800;
                text-align: center;
            }

            QPushButton#smartCancel {
                background-color: rgba(255, 255, 255, 8);
                color: #A1A1AA;
                border: 1px solid rgba(255, 255, 255, 22);
            }

            QPushButton#smartCancel:hover {
                background-color: rgba(255, 255, 255, 16);
                color: #FFFFFF;
            }

            QPushButton#smartCreate {
                background-color: #A78BFA;
                color: #0A0A0F;
                border: none;
            }

            QPushButton#smartCreate:hover {
                background-color: #C4B5FD;
            }

            QPushButton#smartCreate:disabled {
                background-color: #3F3F46;
                color: #71717A;
            }
        """)