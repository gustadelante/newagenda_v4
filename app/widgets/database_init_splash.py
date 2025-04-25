from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from app.core.utils.theme_manager import theme_manager

class DatabaseInitSplash(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Mensaje
        self.label = QLabel("Inicializando base de datos...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {theme_manager.get_color('text')};")
        layout.addWidget(self.label)

        # Barra de progreso indeterminada
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # Indeterminado
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(24)
        self.progress.setStyleSheet(f"QProgressBar {{ background-color: {theme_manager.get_color('card')}; border-radius: 12px; border: 1px solid {theme_manager.get_color('border')}; }} QProgressBar::chunk {{ background-color: {theme_manager.get_color('primary')}; border-radius: 12px; }}")
        layout.addWidget(self.progress)

        # Fondo
        self.setStyleSheet(f"background-color: {theme_manager.get_color('card')}; border-radius: 16px; border: 2px solid {theme_manager.get_color('primary')};")

        # Centrar en pantalla
        screen = self.screen().geometry() if self.screen() else None
        if screen:
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )
