from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QMenu, QToolBar, QStatusBar, QSizePolicy,
    QSplitter, QFrame, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QSize, Slot, Signal
from PySide6.QtGui import QIcon, QAction, QKeySequence, QColor, QPalette

from ..controllers.auth_controller import AuthController
from ..controllers.expiration_controller import ExpirationController
from ..utils.theme_manager import theme_manager
from .dashboards.integral_dashboard import IntegralDashboard
from .dashboards.sabana_dashboard import SabanaDashboard
from .expiration_views.expiration_list import ExpirationListView
from .expiration_views.expiration_form import ExpirationForm
from .user_views.user_settings import UserSettingsDialog



class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    logoutRequested = Signal()
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.auth_controller = AuthController()
        self.expiration_controller = ExpirationController()
        if current_user is not None:
            self.current_user = current_user
        else:
            if not self.auth_controller.is_authenticated():
                raise RuntimeError("El usuario debe estar autenticado para iniciar la ventana principal")
            self.current_user = self.auth_controller.get_current_user()
        self.admin_panel = None
        self.setup_ui()

    def show_admin_panel(self):
        """Muestra el panel de administración en un diálogo modal"""
        if not self.admin_panel:
            from .admin_views import AdminPanel
            self.admin_panel = AdminPanel(self.current_user)
        dialog = QDialog(self)
        dialog.setWindowTitle('Panel de Administración')
        layout = QVBoxLayout(dialog)
        layout.addWidget(self.admin_panel)
        dialog.setLayout(layout)
        dialog.setMinimumSize(900, 600)
        dialog.exec()

    """Ventana principal de la aplicación"""
    
    logoutRequested = Signal()
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.auth_controller = AuthController()
        self.expiration_controller = ExpirationController()
        if current_user is not None:
            self.current_user = current_user
        else:
            if not self.auth_controller.is_authenticated():
                raise RuntimeError("El usuario debe estar autenticado para iniciar la ventana principal")
            self.current_user = self.auth_controller.get_current_user()
        self.admin_panel = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("NewAgenda - Sistema de Gestión de Vencimientos")
        self.setMinimumSize(1200, 800)
        self.refresh_admin_ui()
        self.setup_central_widget()  # <-- ¡Esto asegura que las vistas principales se muestren!
        # Configurar tema - Conexiones robustas
        self.theme_connections = [
            theme_manager.themeChanged.connect(self.update_theme),
            theme_manager.themeChanged.connect(self.update_toolbar_style),
            theme_manager.themeChanged.connect(self.update_header_theme),
            theme_manager.themeChanged.connect(self.update_welcome_label_style)
        ]

    def refresh_admin_ui(self):
        """Reconstruye el menú y toolbar de administración forzando refresco de usuario actual"""
        # Limpiar menubar y toolbar
        self.menuBar().clear()
        for tb in self.findChildren(QToolBar):
            self.removeToolBar(tb)
        # Volver a crear menubar y toolbar
        self.setup_menubar()
        self.setup_toolbar()

    
    def setup_central_widget(self):
        """Configura el widget central con pestañas para los dashboards"""
        # Widget central principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabecera con información del usuario
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        self.welcome_label = QLabel(f"Bienvenido, {self.current_user.full_name}")
        self.update_welcome_label_style()
        
        # Eliminado el bloque try/except que causaba problemas
        theme_manager.themeChanged.connect(self.update_welcome_label_style)
        
        self.user_info = QLabel(f"Rol: {', '.join([r['name'] for r in self.current_user.get_roles()])}")
        self.user_info.setStyleSheet(f"font-size: 14px; color: {theme_manager.get_color('text_secondary')};")
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.user_info)
        
        self.header.setStyleSheet(f"background-color: {theme_manager.get_color('card')};")
        main_layout.addWidget(self.header)
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {theme_manager.get_color('border')}; height: 1px;")
        main_layout.addWidget(separator)
        
        # Widget de pestañas para los dashboards
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setStyleSheet(f"QTabBar::tab {{ background: {theme_manager.get_color('card')}; color: {theme_manager.get_color('text')}; padding: 10px 20px; border: 1px solid {theme_manager.get_color('border')}; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; font-size: 15px; }} QTabBar::tab:selected {{ background: {theme_manager.get_color('primary')}; color: white; }} QTabWidget::pane {{ border: 1px solid {theme_manager.get_color('border')}; top: -1px; background: {theme_manager.get_color('card')}; }}")
        
        # Crear los dashboards
        self.integral_dashboard = IntegralDashboard(self.expiration_controller)
        self.sabana_dashboard = SabanaDashboard(self.expiration_controller)
        self.sabana_dashboard.refresh_data(apply_filters=False)
        self.expiration_list = ExpirationListView(self.expiration_controller)
        self.tab_widget.addTab(self.integral_dashboard, "Vista Integral")
        self.tab_widget.addTab(self.sabana_dashboard, "Vista Sábana")
        # Pestaña para la lista de vencimientos
        self.tab_widget.addTab(self.expiration_list, "Vencimientos")
        # Conectar señal de cambios en vencimientos para refrescar dashboards
        self.expiration_list.expirationsChanged.connect(self.integral_dashboard.refresh_data)
        self.expiration_list.expirationsChanged.connect(self.sabana_dashboard.refresh_data)
        
        main_layout.addWidget(self.tab_widget, 1)  # El dashboard ocupa todo el espacio restante
        
        self.setCentralWidget(central_widget)
    
    def setup_menubar(self):
        """Configura la barra de menús"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Menú Administración (solo admin)
        # DEBUG: Mostrar el usuario actual antes de mostrar el menú Administración
        print(f"[DEBUG] Usuario actual en menú: {getattr(self.current_user, 'username', None)}")
        # Mostrar menú Administración SOLO si el usuario es 'admin' (username literal)
        if self.current_user and getattr(self.current_user, 'username', None) == 'admin':
            admin_menu = menubar.addMenu("&Administración")
            manage_users_action = QAction("Gestionar Usuarios/Roles/Permisos", self)
            manage_users_action.triggered.connect(self.show_admin_panel)
            admin_menu.addAction(manage_users_action)
        
        # Acción Nuevo Vencimiento
        new_expiration_action = QAction("&Nuevo Vencimiento", self)
        new_expiration_action.setShortcut(QKeySequence("Ctrl+N"))
        new_expiration_action.triggered.connect(self.create_new_expiration)
        file_menu.addAction(new_expiration_action)
        
        # Acción Importar
        import_menu = QMenu("&Importar", self)
        
        import_excel_action = QAction("Desde Excel", self)
        import_excel_action.triggered.connect(self.import_from_excel)
        import_menu.addAction(import_excel_action)
        
        import_google_action = QAction("Desde Google Calendar", self)
        import_google_action.triggered.connect(self.import_from_google)
        import_menu.addAction(import_google_action)
        
        import_outlook_action = QAction("Desde Outlook", self)
        import_outlook_action.triggered.connect(self.import_from_outlook)
        import_menu.addAction(import_outlook_action)
        
        file_menu.addMenu(import_menu)
        
        # Separador
        file_menu.addSeparator()
        
        # Acción Cerrar Sesión
        logout_action = QAction("Cerrar &Sesión", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        # Acción Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        # Acción Cambiar Tema
        toggle_theme_action = QAction("Cambiar &Tema", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.triggered.connect(theme_manager.toggleTheme)
        view_menu.addAction(toggle_theme_action)
        
        # Acción Vista Integral
        integral_view_action = QAction("Vista &Integral", self)
        integral_view_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(integral_view_action)
        
        # Acción Vista Alfombra
        sabana_view_action = QAction("Vista &Sábana", self)
        sabana_view_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(sabana_view_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("&Herramientas")
        
        # Acción Procesar Alertas
        process_alerts_action = QAction("Procesar &Alertas", self)
        process_alerts_action.triggered.connect(self.process_alerts)
        tools_menu.addAction(process_alerts_action)
        
        # Acción Configuraciones de Usuario
        user_settings_action = QAction("&Configuraciones", self)
        user_settings_action.triggered.connect(self.show_user_settings)
        tools_menu.addAction(user_settings_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("A&yuda")
        
        # Acción Acerca de
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configura la barra de herramientas"""
        toolbar = QToolBar("Barra de herramientas principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet(f"QToolBar {{ background-color: {theme_manager.get_color('card')}; border-bottom: 1px solid {theme_manager.get_color('border')}; spacing: 5px; }} QToolButton {{ background-color: {theme_manager.get_color('primary')}; color: white; border-radius: 4px; padding: 8px 16px; margin: 3px; font-weight: bold; min-height: 36px; }} QToolButton:hover {{ background-color: {theme_manager.get_color('primary_hover')}; border: 1px solid {theme_manager.get_color('border')}; }} QToolButton:pressed {{ background-color: {theme_manager.get_color('primary_active')}; }} QToolButton:disabled {{ background-color: {theme_manager.get_color('disabled')}; color: {theme_manager.get_color('text_secondary')}; }}")
        self.addToolBar(toolbar)
        
        # Botón de administración (solo admin)
        # DEBUG: Mostrar el usuario actual antes de mostrar el botón Admin
        print(f"[DEBUG] Usuario actual en toolbar: {getattr(self.current_user, 'username', None)}")
        # Mostrar botón Admin SOLO si el usuario es 'admin' (username literal)
        if self.current_user and getattr(self.current_user, 'username', None) == 'admin':
            admin_action = QAction("Admin", self)
            admin_action.setToolTip("Gestión de usuarios, roles y permisos")
            admin_action.triggered.connect(self.show_admin_panel)
            toolbar.addAction(admin_action)
        
        # Botón Nuevo Vencimiento
        new_expiration_action = QAction("Nuevo", self)
        new_expiration_action.setToolTip("Crear nuevo vencimiento")
        new_expiration_action.triggered.connect(self.create_new_expiration)
        toolbar.addAction(new_expiration_action)
        
        # Separador
        toolbar.addSeparator()
        
        # Botón Vista Integral
        integral_view_action = QAction("Integral", self)
        integral_view_action.setToolTip("Ver dashboard Integral")
        integral_view_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(integral_view_action)
        
        # Botón Vista Alfombra
        sabana_view_action = QAction("Sábana", self)
        sabana_view_action.setToolTip("Ver dashboard Sábana")
        sabana_view_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(sabana_view_action)
        
        # Separador
        toolbar.addSeparator()
        
        # Botón Procesar Alertas
        process_alerts_action = QAction("Alertas", self)
        process_alerts_action.setToolTip("Procesar alertas pendientes")
        process_alerts_action.triggered.connect(self.process_alerts)
        toolbar.addAction(process_alerts_action)
        
        # Separador y espaciador (para alinear a la derecha)
        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Botón Cambiar Tema (a la derecha)
        # Botón de cambio de tema (claro/oscuro)
        theme_button = QPushButton()
        theme_button.setFixedSize(30, 30)
        theme_button.setToolTip("Cambiar tema claro/oscuro")
        theme_button.clicked.connect(self.handle_theme_toggle)
        self.update_theme_button(theme_button)
        theme_manager.themeChanged.connect(lambda: self.update_theme_button(theme_button))
        theme_manager.themeChanged.connect(self.update_welcome_label_style)  # Refuerzo explícito
        theme_button.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {theme_manager.get_color('info')}; border: none; }} QPushButton:hover {{ color: {theme_manager.get_color('primary_hover')}; }}")
        toolbar.addWidget(theme_button)
    
    def setup_statusbar(self):
        """Configura la barra de estado"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Mensaje inicial
        self.statusBar.showMessage("Listo", 3000)
    
    def update_theme_button(self, button):
        """Actualiza el ícono del botón de tema según el modo actual"""
        # El ícono muestra a qué modo vas a cambiar:
        if theme_manager.darkMode:
            button.setText("☀️")  # Cambiar a claro
        else:
            button.setText("🌙")  # Cambiar a oscuro
        button.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {theme_manager.get_color('info')}; border: none; }} QPushButton:hover {{ color: {theme_manager.get_color('primary_hover')}; }}")

    def handle_theme_toggle(self):
        """Cambia el tema y actualiza explícitamente el label de bienvenida"""
        theme_manager.toggleTheme()
        self.update_welcome_label_style()  # Garantiza actualización inmediata
    
    def update_toolbar_style(self):
        """Actualiza los estilos de la barra de herramientas"""
        for toolbar in self.findChildren(QToolBar):
            toolbar.setStyleSheet(f"QToolBar {{ background-color: {theme_manager.get_color('card')}; border-bottom: 1px solid {theme_manager.get_color('border')}; spacing: 5px; }} QToolButton {{ background-color: {theme_manager.get_color('primary')}; color: white; border-radius: 4px; padding: 8px 16px; margin: 3px; font-weight: bold; min-height: 36px; }} QToolButton:hover {{ background-color: {theme_manager.get_color('primary_hover')}; border: 1px solid {theme_manager.get_color('border')}; }} QToolButton:pressed {{ background-color: {theme_manager.get_color('primary_active')}; }} QToolButton:disabled {{ background-color: {theme_manager.get_color('disabled')}; color: {theme_manager.get_color('text_secondary')}; }}")
    
    def update_theme(self):
        """Actualiza el tema de la aplicación"""
        # El tema se aplica automáticamente a través del ThemeManager
        self.update_header_theme()
        # Si se agregan más labels, actualizarlos aquí también
        # Llama a otros métodos de actualización si es necesario
        pass

    def update_header_theme(self):
        """Actualiza los estilos del header y sus labels según el tema actual"""
        if hasattr(self, 'header'):
            self.header.setStyleSheet(f"background-color: {theme_manager.get_color('card')} !important;")
        self.update_welcome_label_style()
        if hasattr(self, 'user_info'):
            self.user_info.setStyleSheet(f"font-size: 14px; color: {theme_manager.get_color('text_secondary')} !important;")

    def update_welcome_label_style(self):
        # Usar QPalette para establecer color de texto según theme manager, evitando sobrescritura QSS
        if hasattr(self, 'welcome_label'):
            color_qt = QColor(theme_manager.get_color('text'))
            pal = self.welcome_label.palette()
            pal.setColor(QPalette.WindowText, color_qt)
            self.welcome_label.setPalette(pal)
            # Aplicar sólo estilo de fuente (sin color)
            self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
            self.welcome_label.setAutoFillBackground(False)
            # Forzar repintado
            self.welcome_label.repaint()
            if hasattr(self, 'header'):
                self.header.repaint()
    
    def create_new_expiration(self):
        """Abre el formulario para crear un nuevo vencimiento"""
        form = ExpirationForm(self.expiration_controller, parent=self)
        if form.exec() == QDialog.Accepted:
            # Actualizar vistas
            self.refresh_views()
            QMessageBox.information(self, "Éxito", "Vencimiento creado correctamente.")
    
    def import_from_excel(self):
        """Importa vencimientos desde un archivo Excel"""
        # TODO: Implementar importación desde Excel
        QMessageBox.information(
            self, "Importación desde Excel",
            "Funcionalidad de importación desde Excel en desarrollo."
        )
    
    def import_from_google(self):
        """Importa vencimientos desde Google Calendar"""
        # TODO: Implementar importación desde Google Calendar
        QMessageBox.information(
            self, "Importación desde Google Calendar",
            "Funcionalidad de importación desde Google Calendar en desarrollo."
        )
    
    def import_from_outlook(self):
        """Importa vencimientos desde Outlook"""
        # TODO: Implementar importación desde Outlook
        QMessageBox.information(
            self, "Importación desde Outlook",
            "Funcionalidad de importación desde Outlook en desarrollo."
        )
    
    def process_alerts(self):
        """Procesa las alertas pendientes"""
        success, count, error = self.expiration_controller.process_due_alerts()
        
        if success:
            QMessageBox.information(
                self, "Procesamiento de alertas",
                f"Se procesaron {count} alertas correctamente."
            )
        else:
            QMessageBox.warning(
                self, "Error de procesamiento",
                f"Error al procesar alertas: {error}"
            )
    
    def show_user_settings(self):
        """Muestra el diálogo de configuraciones de usuario"""
        dialog = UserSettingsDialog(self.current_user, parent=self)
        dialog.exec()

    def force_admin_ui_refresh(self):
        """Método público para forzar refresco de menú y toolbar desde fuera de la clase"""
        self.refresh_admin_ui()

    
    def show_about_dialog(self):
        """Muestra el diálogo 'Acerca de'"""
        QMessageBox.about(
            self, "Acerca de NewAgenda",
            "<h3>NewAgenda v4.0</h3>"
            "<p>Sistema de Gestión de Vencimientos y Notificaciones</p>"
            "<p> 2025 - Todos los derechos reservados</p>"
        )
    
    def refresh_views(self):
        """Actualiza todas las vistas de la aplicación"""
        self.integral_dashboard.refresh_data()
        self.sabana_dashboard.refresh_data()
        self.expiration_list.refresh_data()
        if self.admin_panel:
            self.admin_panel.tabs.widget(0).update() # Usuarios
            self.admin_panel.tabs.widget(1).update() # Roles
            self.admin_panel.tabs.widget(2).update() # Permisos
    
    def logout(self):
        """Cierra la sesión actual"""
        confirm = QMessageBox.question(
            self, "Confirmar cierre de sesión",
            "¿Está seguro que desea cerrar la sesión?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.auth_controller.logout()
            self.logoutRequested.emit()
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        confirm = QMessageBox.question(
            self, "Confirmar salida",
            "¿Está seguro que desea salir de la aplicación?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
