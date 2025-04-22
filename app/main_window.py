from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QMenu, QToolBar, QStatusBar, QSizePolicy,
    QSplitter, QFrame, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QSize, Slot, Signal
from PySide6.QtGui import QIcon, QAction, QKeySequence

from app.authentication.controllers.auth_controller import AuthController
from app.expirations.controllers.expiration_controller import ExpirationController
from app.core.utils.theme_manager import theme_manager
from app.views.dashboards.integral_dashboard import IntegralDashboard
from app.views.dashboards.sabana_dashboard import SabanaDashboard
from app.views.expiration_views.expiration_list import ExpirationListView
from app.views.expiration_views.expiration_form import ExpirationForm
from app.views.user_views.user_settings import UserSettingsDialog


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    logoutRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_controller = AuthController()
        self.expiration_controller = ExpirationController()
        
        # Verificar que el usuario esté autenticado
        if not self.auth_controller.is_authenticated():
            raise RuntimeError("El usuario debe estar autenticado para iniciar la ventana principal")
        
        self.current_user = self.auth_controller.get_current_user()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("NewAgenda - Sistema de Gestión de Vencimientos")
        self.setMinimumSize(1200, 800)
        
        # Crear widgets centrales
        self.setup_central_widget()
        
        # Crear barra de menús
        self.setup_menubar()
        
        # Crear barra de herramientas
        self.setup_toolbar()
        
        # Crear barra de estado
        self.setup_statusbar()
        
        # Configurar tema
        theme_manager.themeChanged.connect(self.update_theme)
        theme_manager.themeChanged.connect(self.update_toolbar_style)
    
    def setup_central_widget(self):
        """Configura el widget central con pestañas para los dashboards"""
        # Widget central principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabecera con información del usuario
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        welcome_label = QLabel(f"Bienvenido, {self.current_user.full_name}")
        welcome_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme_manager.get_color('text')};")
        
        user_info = QLabel(f"Rol: {', '.join([r['name'] for r in self.current_user.get_roles()])}")
        user_info.setStyleSheet(f"font-size: 14px; color: {theme_manager.get_color('text_secondary')};")
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        
        main_layout.addWidget(header)
        
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
        theme_button = QPushButton()
        theme_button.setFixedSize(30, 30)
        theme_button.setToolTip("Cambiar tema")
        theme_button.clicked.connect(theme_manager.toggleTheme)
        self.update_theme_button(theme_button)
        theme_manager.themeChanged.connect(lambda: self.update_theme_button(theme_button))
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
        if theme_manager.darkMode:
            button.setText("☀️")
        else:
            button.setText("🌙")
        button.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {theme_manager.get_color('info')}; border: none; }} QPushButton:hover {{ color: {theme_manager.get_color('primary_hover')}; }}")
    
    def update_toolbar_style(self):
        """Actualiza los estilos de la barra de herramientas"""
        for toolbar in self.findChildren(QToolBar):
            toolbar.setStyleSheet(f"QToolBar {{ background-color: {theme_manager.get_color('card')}; border-bottom: 1px solid {theme_manager.get_color('border')}; spacing: 5px; }} QToolButton {{ background-color: {theme_manager.get_color('primary')}; color: white; border-radius: 4px; padding: 8px 16px; margin: 3px; font-weight: bold; min-height: 36px; }} QToolButton:hover {{ background-color: {theme_manager.get_color('primary_hover')}; border: 1px solid {theme_manager.get_color('border')}; }} QToolButton:pressed {{ background-color: {theme_manager.get_color('primary_active')}; }} QToolButton:disabled {{ background-color: {theme_manager.get_color('disabled')}; color: {theme_manager.get_color('text_secondary')}; }}")
    
    def update_theme(self):
        """Actualiza el tema de la aplicación"""
        # El tema se aplica automáticamente a través del ThemeManager
        pass
    
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
    
    def show_about_dialog(self):
        """Muestra el diálogo 'Acerca de'"""
        QMessageBox.about(
            self, "Acerca de NewAgenda",
            "<h3>NewAgenda v4.0</h3>"
            "<p>Sistema de Gestión de Vencimientos y Notificaciones</p>"
            "<p>© 2025 - Todos los derechos reservados</p>"
        )
    
    def refresh_views(self):
        """Actualiza todas las vistas de la aplicación"""
        self.integral_dashboard.refresh_data()
        self.sabana_dashboard.refresh_data()
        self.expiration_list.refresh_data()
    
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
