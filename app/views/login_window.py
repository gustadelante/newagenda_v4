from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

from ..controllers.auth_controller import AuthController
from ..utils.theme_manager import theme_manager


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
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("NewAgenda - Inicio de sesión")
        self.setMinimumSize(400, 500)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Logo y título
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Aquí se agregaría un logo si estuviera disponible
        # Por ahora solo agregamos un título
        logo_label = QLabel("NewAgenda")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #007bff;")
        
        subtitle_label = QLabel("Sistema de Gestión de Vencimientos")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: #6c757d;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(subtitle_label)
        main_layout.addLayout(logo_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Formulario de inicio de sesión
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Campo de usuario
        username_label = QLabel("Usuario o email:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario o email")
        self.username_input.setMinimumHeight(40)
        
        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        
        # Checkbox "Recordarme"
        self.remember_checkbox = QCheckBox("Recordar credenciales")
        
        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.setMinimumHeight(45)
        self.login_button.clicked.connect(self.try_login)
        
        # Agregar los widgets al layout del formulario
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.login_button)
        
        main_layout.addLayout(form_layout)
        
        # Botón para alternar tema claro/oscuro
        theme_layout = QHBoxLayout()
        theme_layout.setAlignment(Qt.AlignRight)
        
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setFixedSize(QSize(30, 30))
        self.theme_toggle_button.setToolTip("Cambiar tema")
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.update_theme_button()
        
        theme_layout.addWidget(self.theme_toggle_button)
        main_layout.addLayout(theme_layout)
        
        # Ajustar el tamaño del layout principal para que ocupe todo el espacio
        main_layout.addStretch()
        
        # Conectar eventos
        self.password_input.returnPressed.connect(self.try_login)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
        # Aplicar tema
        theme_manager.themeChanged.connect(self.update_theme_button)
    
    def update_theme_button(self):
        """Actualiza el ícono del botón de tema según el modo actual"""
        if theme_manager.darkMode:
            # Ícono para modo oscuro (sol)
            self.theme_toggle_button.setText("☀️")
        else:
            # Ícono para modo claro (luna)
            self.theme_toggle_button.setText("🌙")
    
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
    
    def keyPressEvent(self, event):
        """Maneja eventos de teclado"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
