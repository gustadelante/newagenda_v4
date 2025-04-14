from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton,
    QTabWidget, QWidget, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ...models.user import User
from ...utils.theme_manager import theme_manager


class UserSettingsDialog(QDialog):
    """Diálogo para gestionar las configuraciones del usuario"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.user_preferences = user.get_preferences()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Configuraciones de usuario")
        self.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout(self)
        
        # Pestañas para organizar la configuración
        tab_widget = QTabWidget()
        
        # Tab de información personal
        personal_tab = QWidget()
        self.setup_personal_tab(personal_tab)
        tab_widget.addTab(personal_tab, "Información personal")
        
        # Tab de apariencia
        appearance_tab = QWidget()
        self.setup_appearance_tab(appearance_tab)
        tab_widget.addTab(appearance_tab, "Apariencia")
        
        # Tab de notificaciones
        notifications_tab = QWidget()
        self.setup_notifications_tab(notifications_tab)
        tab_widget.addTab(notifications_tab, "Notificaciones")
        
        # Tab de seguridad
        security_tab = QWidget()
        self.setup_security_tab(security_tab)
        tab_widget.addTab(security_tab, "Seguridad")
        
        main_layout.addWidget(tab_widget)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_personal_tab(self, tab):
        """Configura la pestaña de información personal"""
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        
        # Nombre completo
        self.full_name_edit = QLineEdit(self.user.full_name)
        layout.addRow("Nombre completo:", self.full_name_edit)
        
        # Correo electrónico
        self.email_edit = QLineEdit(self.user.email)
        layout.addRow("Correo electrónico:", self.email_edit)
        
        # Departamento
        self.department_edit = QLineEdit(self.user.department or "")
        layout.addRow("Departamento:", self.department_edit)
        
        # Teléfono
        self.phone_edit = QLineEdit(self.user.phone or "")
        layout.addRow("Teléfono:", self.phone_edit)
    
    def setup_appearance_tab(self, tab):
        """Configura la pestaña de apariencia"""
        layout = QVBoxLayout(tab)
        
        # Grupo de tema
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        # Selector de tema
        self.dark_mode_check = QCheckBox("Usar tema oscuro")
        self.dark_mode_check.setChecked(theme_manager.darkMode)
        theme_layout.addWidget(self.dark_mode_check)
        
        # Vista por defecto
        default_view_layout = QFormLayout()
        self.default_view_combo = QComboBox()
        self.default_view_combo.addItem("Vista Genio", "genio")
        self.default_view_combo.addItem("Vista Alfombra", "alfombra")
        
        # Establecer vista por defecto
        default_dashboard = self.user_preferences.get("default_dashboard", "genio")
        index = self.default_view_combo.findData(default_dashboard)
        if index >= 0:
            self.default_view_combo.setCurrentIndex(index)
        
        default_view_layout.addRow("Vista predeterminada:", self.default_view_combo)
        theme_layout.addLayout(default_view_layout)
        
        layout.addWidget(theme_group)
        layout.addStretch()
    
    def setup_notifications_tab(self, tab):
        """Configura la pestaña de notificaciones"""
        layout = QVBoxLayout(tab)
        
        # Grupo de notificaciones
        notifications_group = QGroupBox("Preferencias de notificación")
        notifications_layout = QVBoxLayout(notifications_group)
        
        # Opciones de notificación
        self.email_notifications_check = QCheckBox("Recibir notificaciones por correo electrónico")
        self.email_notifications_check.setChecked(True)  # Por defecto activado
        
        self.push_notifications_check = QCheckBox("Recibir notificaciones push (dispositivos móviles)")
        self.push_notifications_check.setChecked(True)  # Por defecto activado
        
        self.desktop_notifications_check = QCheckBox("Mostrar notificaciones de escritorio")
        self.desktop_notifications_check.setChecked(True)  # Por defecto activado
        
        # Cargar preferencias guardadas
        notification_settings = self.user_preferences.get("notification_settings")
        if notification_settings:
            try:
                settings = notification_settings
                if isinstance(settings, str):
                    import json
                    settings = json.loads(settings)
                
                self.email_notifications_check.setChecked(settings.get("email", True))
                self.push_notifications_check.setChecked(settings.get("push", True))
                self.desktop_notifications_check.setChecked(settings.get("desktop", True))
            except:
                pass
        
        notifications_layout.addWidget(self.email_notifications_check)
        notifications_layout.addWidget(self.push_notifications_check)
        notifications_layout.addWidget(self.desktop_notifications_check)
        
        layout.addWidget(notifications_group)
        layout.addStretch()
    
    def setup_security_tab(self, tab):
        """Configura la pestaña de seguridad"""
        layout = QVBoxLayout(tab)
        
        # Grupo de contraseña
        password_group = QGroupBox("Cambiar contraseña")
        password_layout = QFormLayout(password_group)
        
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Contraseña actual:", self.current_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Nueva contraseña:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Confirmar contraseña:", self.confirm_password_edit)
        
        layout.addWidget(password_group)
        
        # Grupo de inicio de sesión
        login_group = QGroupBox("Opciones de inicio de sesión")
        login_layout = QVBoxLayout(login_group)
        
        self.remember_credentials_check = QCheckBox("Recordar credenciales")
        self.remember_credentials_check.setChecked(self.user_preferences.get("remember_credentials", False))
        login_layout.addWidget(self.remember_credentials_check)
        
        layout.addWidget(login_group)
        layout.addStretch()
    
    def save_settings(self):
        """Guarda las configuraciones del usuario"""
        try:
            # Actualizar información personal
            self.user.full_name = self.full_name_edit.text()
            self.user.email = self.email_edit.text()
            self.user.department = self.department_edit.text()
            self.user.phone = self.phone_edit.text()
            
            if not self.user.save():
                QMessageBox.warning(
                    self, "Error", 
                    "No se pudo guardar la información personal."
                )
                return
            
            # Actualizar tema
            theme_manager.darkMode = self.dark_mode_check.isChecked()
            
            # Actualizar preferencias
            preferences = {
                'theme_mode': 'dark' if theme_manager.darkMode else 'light',
                'remember_credentials': self.remember_credentials_check.isChecked(),
                'default_dashboard': self.default_view_combo.currentData(),
                'notification_settings': {
                    'email': self.email_notifications_check.isChecked(),
                    'push': self.push_notifications_check.isChecked(),
                    'desktop': self.desktop_notifications_check.isChecked()
                }
            }
            
            self.user.update_preferences(preferences)
            
            # Cambiar contraseña si se ha especificado
            if self.new_password_edit.text():
                if not self.current_password_edit.text():
                    QMessageBox.warning(
                        self, "Error", 
                        "Debe ingresar su contraseña actual para cambiarla."
                    )
                    return
                
                if self.new_password_edit.text() != self.confirm_password_edit.text():
                    QMessageBox.warning(
                        self, "Error", 
                        "La nueva contraseña y su confirmación no coinciden."
                    )
                    return
                
                # Verificar contraseña actual
                if not User.check_password(self.current_password_edit.text(), self.user.password):
                    QMessageBox.warning(
                        self, "Error", 
                        "La contraseña actual es incorrecta."
                    )
                    return
                
                # Actualizar contraseña
                self.user.password = self.new_password_edit.text()
                if not self.user.save():
                    QMessageBox.warning(
                        self, "Error", 
                        "No se pudo actualizar la contraseña."
                    )
                    return
            
            QMessageBox.information(
                self, "Éxito", 
                "Configuraciones guardadas correctamente."
            )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error al guardar configuraciones: {e}"
            )
