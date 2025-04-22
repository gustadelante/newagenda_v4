from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QMessageBox, QSizePolicy,
    QGraphicsDropShadowEffect, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap, QColor, QFont, QPainter, QPainterPath

from app.authentication.controllers.auth_controller import AuthController
from app.core.utils.theme_manager import theme_manager


class LoginWindow(QWidget):
    """Ventana de inicio de sesión"""
    
    # Señal emitida cuando el inicio de sesión es exitoso
    loginSuccessful = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_controller = AuthController()
        self.setup_ui()
        
        # Intentar inicio de sesión automático
        if self.auth_controller.try_auto_login():
            self.loginSuccessful.emit()
    
    # Clase para crear el ícono de agenda/calendario
    class CalendarIcon(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedSize(100, 100)
            self.color = QColor("#3a86ff")
            self.secondaryColor = QColor("#ffffff")
            
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Dibujar la base del calendario
            path = QPainterPath()
            # Dibujar un rectángulo redondeado para la base del calendario
            path.addRoundedRect(10, 20, 80, 70, 8, 8)
            painter.fillPath(path, self.color)
            
            # Dibujar la parte superior del calendario (donde están los anillos)
            topPath = QPainterPath()
            topPath.addRoundedRect(10, 10, 80, 15, 4, 4)
            painter.fillPath(topPath, QColor("#2563eb"))
            
            # Dibujar los anillos del calendario
            ringColor = QColor("#ffffff")
            painter.setPen(Qt.NoPen)
            painter.setBrush(ringColor)
            painter.drawEllipse(25, 5, 10, 10)
            painter.drawEllipse(65, 5, 10, 10)
            
            # Dibujar líneas horizontales para simular hojas del calendario
            painter.setPen(self.secondaryColor)
            painter.drawLine(20, 50, 80, 50)
            painter.drawLine(20, 65, 80, 65)
            
            # Dibujar líneas verticales para simular columnas del calendario
            painter.drawLine(35, 35, 35, 80)
            painter.drawLine(50, 35, 50, 80)
            painter.drawLine(65, 35, 65, 80)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Agenda Pepelera ER - Inicio de sesión")
        self.setMinimumSize(400, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor principal con fondo de color azul oscuro
        main_container = QFrame()
        main_container.setStyleSheet(f"background-color: {theme_manager.get_color('background')};")
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(30, 40, 30, 30)
        main_container_layout.setSpacing(20)
        
        # Ícono de agenda/calendario en la parte superior
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        
        self.calendar_icon = self.CalendarIcon()
        icon_layout.addWidget(self.calendar_icon)
        main_container_layout.addLayout(icon_layout)
        
        # Logo y título
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(5)
        
        self.logo_label = QLabel("Agenda Pepelera ER")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.logo_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; font-weight: bold; margin-bottom: 5px;")
        
        self.subtitle_label = QLabel("Sistema de Gestión de Vencimientos")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-weight: medium;")
        logo_layout.addWidget(self.logo_label)
        logo_layout.addWidget(self.subtitle_label)
        main_container_layout.addLayout(logo_layout)
        main_container_layout.addSpacing(40)
        
        # Formulario de inicio de sesión directamente en el contenedor principal
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Icono de usuario
        user_icon_layout = QHBoxLayout()
        user_icon_layout.setAlignment(Qt.AlignCenter)
        
        user_icon = QLabel()
        user_icon.setFixedSize(60, 60)
        user_icon.setStyleSheet(f"""
            background-color: {theme_manager.get_color('primary')};
            border-radius: 30px;
        """)
        
        # Dibujar icono de usuario
        user_icon_path = QPainterPath()
        user_icon_path.addEllipse(15, 15, 30, 30)
        
        user_icon_layout.addWidget(user_icon)
        form_layout.addLayout(user_icon_layout)
        form_layout.addSpacing(10)
        
        # Campo de usuario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("User Name")
        self.username_input.setMinimumHeight(40)
        self.username_input.setAlignment(Qt.AlignCenter)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                border-bottom: 1px solid {theme_manager.get_color('input_border')};
                background-color: {theme_manager.get_color('input_bg')};
                color: {theme_manager.get_color('text')};
                font-size: 14px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {theme_manager.get_color('primary')};
            }}
        """)
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(10)
        
        # Campo de contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                border-bottom: 1px solid {theme_manager.get_color('input_border')};
                background-color: {theme_manager.get_color('input_bg')};
                color: {theme_manager.get_color('text')};
                font-size: 14px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {theme_manager.get_color('primary')};
            }}
        """)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(30)
        
        # Botón de inicio de sesión con estilo moderno
        self.login_button = QPushButton("Log In")
        self.login_button.setMinimumHeight(45)
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary_hover')};
            }}
            QPushButton:pressed {{
                background-color: {theme_manager.get_color('primary_active')};
            }}
        """)
        self.login_button.clicked.connect(self.try_login)
        form_layout.addWidget(self.login_button)
        
        # Checkbox "Recordarme" (oculto en este diseño)
        self.remember_checkbox = QCheckBox("")
        self.remember_checkbox.setVisible(False)
        
        # Agregar el formulario al contenedor principal
        main_container_layout.addLayout(form_layout)
        main_container_layout.addStretch(1)
        
        # Triángulo decorativo en la esquina del botón de login
        triangle_frame = QFrame()
        triangle_frame.setFixedSize(30, 30)
        triangle_frame.setStyleSheet(f"""
            background-color: {theme_manager.get_color('warning')};
            border-radius: 0px;
        """)
        
        # Posicionar el triángulo en la esquina del botón de login
        triangle_pos = QHBoxLayout()
        triangle_pos.setAlignment(Qt.AlignRight)
        triangle_pos.addWidget(triangle_frame)
        triangle_pos.setContentsMargins(0, -45, 10, 0)
        # Posicionarlo sobre el botón de login
        form_layout.addLayout(triangle_pos)
        
        # Botón para alternar tema claro/oscuro (más discreto)
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setFixedSize(QSize(30, 30))
        self.theme_toggle_button.setToolTip("Cambiar entre tema claro y oscuro")
        self.theme_toggle_button.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.theme_toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme_manager.get_color('info')};
            }}
        """)
        
        # Añadir el botón de tema en una esquina discreta
        theme_layout = QHBoxLayout()
        theme_layout.setAlignment(Qt.AlignRight)
        theme_layout.addWidget(self.theme_toggle_button)
        main_container_layout.addLayout(theme_layout)
        
        # Agregar el contenedor principal al layout
        main_layout.addWidget(main_container)
        
        # Conectar eventos
        self.password_input.returnPressed.connect(self.try_login)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
        # Aplicar tema y conectar señales para actualizar la UI cuando cambie el tema
        theme_manager.themeChanged.connect(self.update_theme_button)
        theme_manager.themeChanged.connect(self.update_login_button_style)
        theme_manager.themeChanged.connect(self.update_main_style)
        theme_manager.themeChanged.connect(self.update_labels_style)

    def update_login_button_style(self):
        """Actualiza los estilos del botón según el tema actual"""
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary_hover')};
            }}
            QPushButton:pressed {{
                background-color: {theme_manager.get_color('primary_active')};
            }}
        """)

    def update_theme_button(self):
        """Actualiza el ícono del botón de tema según el modo actual"""
        if theme_manager.darkMode:
            self.theme_toggle_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme_manager.get_color('info')};
                    border: none;
                }}
                QPushButton:hover {{
                    color: {theme_manager.get_color('primary_hover')};
                }}
            """)
            self.theme_toggle_button.setText("☀️")
            self.theme_toggle_button.setToolTip("Cambiar a modo claro")
        else:
            self.theme_toggle_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme_manager.get_color('info')};
                    border: none;
                }}
                QPushButton:hover {{
                    color: {theme_manager.get_color('primary_hover')};
                }}
            """)
            self.theme_toggle_button.setText("🌙")
            self.theme_toggle_button.setToolTip("Cambiar a modo oscuro")
    
    def update_main_style(self):
        """Actualiza el estilo del widget principal según el tema actual"""
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: {theme_manager.get_color('background')};
                color: {theme_manager.get_color('text')};
            }}
        """)
        if hasattr(self, 'calendar_icon'):
            self.calendar_icon.color = QColor(theme_manager.get_color('primary'))
            self.calendar_icon.secondaryColor = QColor(theme_manager.get_color('text'))
    
    def update_labels_style(self):
        """Actualiza el estilo de las etiquetas de título y subtítulo"""
        # Para este diseño, mantenemos los colores consistentes
        self.logo_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            margin-bottom: 5px;
        """)
        self.subtitle_label.setStyleSheet("""
            color: #a0b4d9;
            font-weight: medium;
        """)
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        theme_manager.toggleTheme()
    
    def try_login(self):
        """Intenta iniciar sesión con las credenciales proporcionadas"""
        username = self.username_input.text()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()
        
        if not username or not password:
            QMessageBox.warning(
                self, "Error de inicio de sesión",
                "Por favor, ingrese su usuario y contraseña."
            )
            return
        
        # Intentar iniciar sesión
        success, error_message = self.auth_controller.login(username, password, remember)
        
        if success:
            self.loginSuccessful.emit()
        else:
            QMessageBox.warning(
                self, "Error de inicio de sesión",
                error_message or "Usuario o contraseña incorrectos."
            )
    
    def forgot_password(self):
        """Maneja la acción de olvidar contraseña"""
        email = self.username_input.text()
        
        if not email:
            QMessageBox.information(
                self,
                "Recuperar contraseña",
                "Por favor, ingrese su correo electrónico en el campo de usuario para recibir instrucciones de recuperación."
            )
            return
        
        # Aquí se implementaría la lógica real de recuperación de contraseña
        # Por ahora, solo mostramos un mensaje informativo
        QMessageBox.information(
            self,
            "Recuperar contraseña",
            f"Se han enviado instrucciones de recuperación a: {email}\n\n" +
            "Por favor, revise su bandeja de entrada y siga las instrucciones para restablecer su contraseña."
        )
    
    def keyPressEvent(self, event):
        """Maneja eventos de teclado"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
