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
                "primary": "#0055cc",
                "secondary": "#5a6268",
                "success": "#107c41",
                "danger": "#c92a2a",
                "warning": "#e67700",
                "info": "#0277bd",
                "light": "#f8f9fa",
                "dark": "#212529",
                "background": "#f0f2f5",
                "card": "#ffffff",
                "text": "#1a1a1a",
                "text_secondary": "#495057",
                "border": "#b0b6be",
                "shadow": "rgba(0, 0, 0, 0.18)",
                "hover": "#e2e6ea",
                "active": "#c9cfd6",
                "focus": "#0055cc",
                "primary_hover": "#004099",
                "primary_active": "#003380",
                "hover_bg": "#e2e6ea",
                "input_bg": "#ffffff",
                "input_border": "#8a929a",
                "input_focus": "#0055cc",
                "table_header": "#e3e6ea",
                "table_hover": "#e9ecef",
                "table_border": "#b0b6be",
                "disabled": "#d9dde2"
            },
            "dark": {
                "primary": "#339cff",
                "secondary": "#8a929a",
                "success": "#3ecf8e",
                "danger": "#ff5c5c",
                "warning": "#ffd166",
                "info": "#66cfff",
                "light": "#f8f9fa",
                "dark": "#181c20",
                "background": "#181c20",
                "card": "#23272b",
                "text": "#f8f9fa",
                "text_secondary": "#bfc8d1",
                "border": "#353a40",
                "shadow": "rgba(0, 0, 0, 0.7)",
                "hover": "#23272b",
                "active": "#353a40",
                "focus": "#339cff",
                "primary_hover": "#1976d2",
                "primary_active": "#1565c0",
                "hover_bg": "#23272b",
                "input_bg": "#23272b",
                "input_border": "#353a40",
                "input_focus": "#339cff",
                "table_header": "#23272b",
                "table_hover": "#23272b",
                "table_border": "#353a40",
                "disabled": "#353a40"
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
            # Emitir señal para notificar el cambio de tema
            self.themeChanged.emit()
            
            # Aplicar el tema inmediatamente a la aplicación actual
            from PySide6.QtWidgets import QApplication
            if QApplication.instance():
                self.apply_theme(QApplication.instance())
    
    @Slot()
    def toggleTheme(self):
        """Alterna entre tema claro y oscuro"""
        self.darkMode = not self._dark_mode
        # La aplicación del tema se maneja automáticamente en el setter de darkMode
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Obtiene los colores del tema actual"""
        theme_name = "dark" if self._dark_mode else "light"
        return self._themes[theme_name]
    
    def get_color(self, color_name: str) -> str:
        """Obtiene un color específico del tema actual"""
        colors = self.get_theme_colors()
        
        # Manejar colores especiales que no están directamente en el diccionario
        if color_name == "text_primary":
            return colors.get("text", "#000000")
        elif color_name == "primary_pressed":
            return colors.get("primary_active", "#000000")
            
        return colors.get(color_name, "#000000")  # Devuelve negro como color por defecto si no existe
    
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
            min-height: 40px;
            padding: 8px 20px;
            border-radius: 5px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {colors['primary_hover']};
            border: 1px solid {colors['primary_active']};
        }}

        QPushButton:pressed {{
            background-color: {colors['primary_active']};
        }}
        
        QPushButton:focus {{
            outline: 2px solid {colors['focus']};
            outline-offset: 2px;
        }}
        
        QPushButton:disabled {{
            background-color: {colors["disabled"]};
            color: {colors["text_secondary"]};
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
            background-color: {colors["input_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["input_border"]};
            padding: 8px;
            border-radius: 4px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors["input_focus"]};
            background-color: {colors["input_bg"]};
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border: 1px solid {colors["primary"]};
            background-color: {colors["hover"]};
        }}
        
        /* Combobox */
        QComboBox {{
            background-color: {colors["input_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["input_border"]};
            padding: 8px;
            border-radius: 4px;
            min-height: 40px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors["primary"]};
            background-color: {colors["hover"]};
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors["input_focus"]};
            background-color: {colors["input_bg"]};
        }}
        
        QComboBox::drop-down {{
            border: 0px;
            width: 30px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors["input_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["input_border"]};
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
            gridline-color: {colors["table_border"]};
            border: 1px solid {colors["table_border"]};
            border-radius: 4px;
            alternate-background-color: {colors["table_hover"]};
        }}
        
        QTableView::item, QTableWidget::item {{
            padding: 8px;
        }}
        
        QTableView::item:alternate, QTableWidget::item:alternate {{
            background-color: {colors["table_hover"]};
            color: {colors["text"]};
        }}
        
        QTableView::item:hover, QTableWidget::item:hover {{
            background-color: {colors["table_hover"]};
            color: {colors["text"]};
        }}
        
        QTableView::item:selected, QTableWidget::item:selected {{
            background-color: {colors["primary"]};
            color: white;
        }}
        
        QTableView::item:selected:hover, QTableWidget::item:selected:hover {{
            background-color: {colors["primary_hover"]};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {colors["table_header"]};
            color: {colors["text"]};
            padding: 10px;
            border: 1px solid {colors["table_border"]};
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
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors["secondary"]};
            min-height: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {colors["primary"]};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background: {colors["primary_active"]};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {colors["background"]};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {colors["secondary"]};
            min-width: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {colors["primary"]};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background: {colors["primary_active"]};
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
            background-color: {colors["card"]};
        }}
        
        QTabBar::tab {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            padding: 10px 20px;
            border: 1px solid {colors["border"]};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors["hover"]};
            color: {colors["text"]};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors["primary"]};
            color: white;
            border-bottom: 2px solid {colors["primary"]};
        }}
        
        /* CheckBox */
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 2px solid {colors["input_border"]};
            background-color: {colors["input_bg"]};
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 2px solid {colors["primary"]};
            background-color: {colors["hover"]};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors["primary"]};
            border: 2px solid {colors["primary"]};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {colors["primary_hover"]};
            border: 2px solid {colors["primary_hover"]};
        }}
        
        /* RadioButton */
        QRadioButton {{
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 10px;
        }}
        
        QRadioButton::indicator:unchecked {{
            border: 2px solid {colors["input_border"]};
            background-color: {colors["input_bg"]};
        }}
        
        QRadioButton::indicator:unchecked:hover {{
            border: 2px solid {colors["primary"]};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors["primary"]};
            border: 2px solid {colors["primary"]};
        }}
        
        QRadioButton::indicator:checked:hover {{
            background-color: {colors["primary_hover"]};
            border: 2px solid {colors["primary_hover"]};
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
        
        QSlider::handle:horizontal:hover {{
            background: {colors["primary_hover"]};
        }}
        
        /* DateEdit */
        QDateEdit {{
            background-color: {colors["input_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["input_border"]};
            padding: 8px;
            border-radius: 4px;
            min-height: 40px;
        }}
        
        QDateEdit:hover {{
            border: 1px solid {colors["primary"]};
            background-color: {colors["hover"]};
        }}
        
        QDateEdit:focus {{
            border: 2px solid {colors["input_focus"]};
            background-color: {colors["input_bg"]};
        }}
        
        QDateEdit::drop-down {{
            border: 0px;
            width: 30px;
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
            border-top: 1px solid {colors["border"]};
        }}
        
        QToolBar {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
            spacing: 3px;
        }}
        
        QToolButton {{
            background-color: {colors["primary"]};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            margin: 2px;
        }}
        
        QToolButton:hover {{
            background-color: {colors["primary_hover"]};
            border: 1px solid {colors["border"]};
        }}
        
        QToolButton:pressed {{
            background-color: {colors["primary_active"]};
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
        """
        
        return stylesheet
    
    def apply_theme(self, app):
        """Aplica el tema a la aplicación"""
        # Aplicar hoja de estilos
        app.setStyleSheet(self.get_stylesheet())
        
        # Configurar paleta de colores
        palette = app.palette()
        colors = self.get_theme_colors()
        
        # Colores de la paleta
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
        
        # Aplicar paleta
        app.setPalette(palette)


# Instancia global del gestor de temas
theme_manager = ThemeManager()
