from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, Property, Slot, QSettings
from PySide6.QtGui import QColor, QPalette

class ThemeManager(QObject):
    """Clase para gestionar el tema de la aplicación (claro/oscuro)"""
    
    themeChanged = Signal()
    
    def __init__(self, parent=None):
        """Inicializa el gestor de temas"""
        super().__init__(parent)
        self._settings = QSettings("NewAgenda", "App")
        self._dark_mode = self._settings.value("theme/darkMode", False, bool)
        
        # Definir los colores para los temas
        self._themes = {
            "light": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "background": "#ffffff",
                "card": "#ffffff",
                "text": "#212529",
                "border": "#dee2e6",
                "shadow": "rgba(0, 0, 0, 0.1)",
                "hover": "#f8f9fa",
                "active": "#e9ecef"
            },
            "dark": {
                "primary": "#375a7f",
                "secondary": "#444444",
                "success": "#00bc8c",
                "danger": "#e74c3c",
                "warning": "#f39c12",
                "info": "#3498db",
                "light": "#adb5bd",
                "dark": "#303030",
                "background": "#222222",
                "card": "#303030",
                "text": "#ffffff",
                "border": "#444444",
                "shadow": "rgba(0, 0, 0, 0.3)",
                "hover": "#444444",
                "active": "#555555"
            }
        }
    
    @Property(bool, notify=themeChanged)
    def darkMode(self) -> bool:
        """Getter para el modo oscuro"""
        return self._dark_mode
    
    @darkMode.setter
    def darkMode(self, value: bool):
        """Setter para el modo oscuro"""
        if self._dark_mode != value:
            self._dark_mode = value
            self._settings.setValue("theme/darkMode", value)
            self.themeChanged.emit()
    
    @Slot()
    def toggleTheme(self):
        """Alterna entre tema claro y oscuro"""
        self.darkMode = not self._dark_mode
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Obtiene los colores del tema actual"""
        theme_name = "dark" if self._dark_mode else "light"
        return self._themes[theme_name]
    
    def get_stylesheet(self) -> str:
        """Obtiene la hoja de estilos para el tema actual"""
        colors = self.get_theme_colors()
        
        # Estilos base
        stylesheet = f"""
        /* Estilos globales */
        QWidget {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        /* Botones */
        QPushButton {{
            background-color: {colors["primary"]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors["primary"]}e0;
        }}
        
        QPushButton:pressed {{
            background-color: {colors["primary"]}c0;
        }}
        
        QPushButton:disabled {{
            background-color: {colors["secondary"]};
            color: {colors["light"]};
        }}
        
        QPushButton.secondary {{
            background-color: {colors["secondary"]};
        }}
        
        QPushButton.success {{
            background-color: {colors["success"]};
        }}
        
        QPushButton.danger {{
            background-color: {colors["danger"]};
        }}
        
        QPushButton.warning {{
            background-color: {colors["warning"]};
            color: {colors["dark"]};
        }}
        
        /* Campos de texto */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            padding: 8px;
            border-radius: 4px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {colors["primary"]};
        }}
        
        /* Combobox */
        QComboBox {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            padding: 8px;
            border-radius: 4px;
        }}
        
        QComboBox::drop-down {{
            border: 0px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            selection-background-color: {colors["primary"]};
            selection-color: white;
        }}
        
        /* Calendar */
        QCalendarWidget {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        QCalendarWidget QToolButton {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        QCalendarWidget QMenu {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        QCalendarWidget QSpinBox {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        /* Tabla */
        QTableView, QTableWidget {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            gridline-color: {colors["border"]};
            border: 1px solid {colors["border"]};
        }}
        
        QTableView::item, QTableWidget::item {{
            padding: 4px;
        }}
        
        QTableView::item:selected, QTableWidget::item:selected {{
            background-color: {colors["primary"]};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {colors["secondary"]};
            color: white;
            padding: 6px;
            border: 1px solid {colors["border"]};
            font-weight: bold;
        }}
        
        /* GroupBox */
        QGroupBox {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            margin-top: 20px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
        }}
        
        /* ScrollBar */
        QScrollBar:vertical {{
            border: none;
            background: {colors["background"]};
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors["secondary"]};
            min-height: 20px;
            border-radius: 5px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {colors["background"]};
            height: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {colors["secondary"]};
            min-width: 20px;
            border-radius: 5px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Menu */
        QMenuBar {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        QMenuBar::item {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            padding: 8px 16px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors["primary"]};
            color: white;
        }}
        
        QMenu {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
        }}
        
        QMenu::item {{
            padding: 8px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors["primary"]};
            color: white;
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors["border"]};
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            padding: 8px 16px;
            border: 1px solid {colors["border"]};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors["card"]};
            border-bottom: none;
        }}
        
        /* CheckBox */
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 1px solid {colors["border"]};
            background-color: {colors["card"]};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors["primary"]};
            border: 1px solid {colors["primary"]};
        }}
        
        /* RadioButton */
        QRadioButton {{
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
        }}
        
        QRadioButton::indicator:unchecked {{
            border: 1px solid {colors["border"]};
            background-color: {colors["card"]};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors["primary"]};
            border: 1px solid {colors["primary"]};
        }}
        
        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            text-align: center;
            background-color: {colors["card"]};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors["primary"]};
            width: 10px;
            margin: 0.5px;
        }}
        
        /* Slider */
        QSlider::groove:horizontal {{
            border: 1px solid {colors["border"]};
            height: 6px;
            background: {colors["card"]};
            margin: 0px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors["primary"]};
            border: none;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        
        /* DateEdit */
        QDateEdit {{
            background-color: {colors["card"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            padding: 8px;
            border-radius: 4px;
        }}
        
        QDateEdit::drop-down {{
            border: 0px;
        }}
        
        /* Ventanas y Diálogos */
        QMainWindow {{
            background-color: {colors["background"]};
        }}
        
        QDialog {{
            background-color: {colors["background"]};
        }}
        
        QStatusBar {{
            background-color: {colors["card"]};
            color: {colors["text"]};
        }}
        
        QToolBar {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
        }}
        
        /* Frame */
        QFrame {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
        }}
        
        QFrame.noFrame {{
            border: none;
            border-radius: 0px;
        }}
        
        /* Label */
        QLabel {{
            color: {colors["text"]};
        }}
        
        QLabel.title {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        QLabel.subtitle {{
            font-size: 14px;
            font-weight: bold;
        }}
        """
        
        return stylesheet
    
    def apply_theme(self, app):
        """Aplica el tema actual a la aplicación"""
        app.setStyleSheet(self.get_stylesheet())
        
        # Aplicar paleta de colores
        colors = self.get_theme_colors()
        palette = QPalette()
        
        # Colores base
        palette.setColor(QPalette.Window, QColor(colors["background"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text"]))
        palette.setColor(QPalette.Base, QColor(colors["card"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["hover"]))
        palette.setColor(QPalette.ToolTipBase, QColor(colors["card"]))
        palette.setColor(QPalette.ToolTipText, QColor(colors["text"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Button, QColor(colors["primary"]))
        palette.setColor(QPalette.ButtonText, QColor("white"))
        palette.setColor(QPalette.BrightText, QColor("white"))
        palette.setColor(QPalette.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        
        app.setPalette(palette)


# Instancia global del gestor de temas
theme_manager = ThemeManager()
