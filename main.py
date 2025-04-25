#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication, QStyleFactory
from app.widgets.database_init_splash import DatabaseInitSplash
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QIcon

from app.core.database.schema import initialize_database
from app.authentication.controllers.auth_controller import AuthController
from app.authentication.views.login_window import LoginWindow
from app.views.main_window import MainWindow
from app.core.utils.theme_manager import theme_manager


class NewAgendaApp:
    """Clase principal de la aplicación NewAgenda"""
    
    def __init__(self):
        """Inicializa la aplicación"""
        # Crear la aplicación QT
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("NewAgenda")
        self.app.setApplicationVersion("4.0")
        self.app.setStyle(QStyleFactory.create("Fusion"))
        
        # Aplicar tema
        theme_manager.apply_theme(self.app)
        
        # Inicializar base de datos
        self.init_database()
        
        # Controlador de autenticación
        self.auth_controller = AuthController()
        
        # Ventanas
        self.login_window = None
        self.main_window = None
        
        # Iniciar la aplicación
        self.start()
    
    def init_database(self):
        """Inicializa la base de datos"""
        try:
            # Mostrar splash screen moderno durante la inicialización
            splash = DatabaseInitSplash()
            splash.show()
            self.app.processEvents()

            # Inicializar base de datos
            initialize_database()

            # Cerrar splash después de un breve retraso
            QTimer.singleShot(1000, splash.close)
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            sys.exit(1)
    
    def start(self):
        """Inicia la aplicación"""
        # Mostrar ventana de login
        self.show_login_window()
        
        # Ejecutar bucle de eventos
        sys.exit(self.app.exec())
    
    def show_login_window(self):
        """Muestra la ventana de inicio de sesión"""
        if not self.login_window:
            self.login_window = LoginWindow()
            self.login_window.loginSuccessful.connect(self.on_login_successful)
        
        if self.main_window:
            self.main_window.hide()
        
        self.login_window.show()
    
    def on_login_successful(self):
        """Maneja el evento de inicio de sesión exitoso"""
        # Ocultar ventana de login
        if self.login_window:
            self.login_window.hide()
        
        # Mostrar ventana principal
        self.show_main_window()
    
    def show_main_window(self):
        """Muestra la ventana principal"""
        if not self.main_window:
            current_user = self.login_window.auth_controller.get_current_user()
            self.main_window = MainWindow(current_user=current_user)
            self.main_window.logoutRequested.connect(self.show_login_window)
        
        self.main_window.show()
        # Forzar refresco de menú y toolbar de administración
        self.main_window.force_admin_ui_refresh()


if __name__ == "__main__":
    # Punto de entrada de la aplicación
    app = NewAgendaApp()
