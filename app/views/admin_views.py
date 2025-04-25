from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout
from app.users.views.user_views import UserManagementView
from app.roles.views.role_views import RoleManagementView
from app.permissions.views.permission_views import PermissionManagementView
from app.core.database.db_manager import DBManager
from app.users.controllers.user_controller import UserController
from app.roles.controllers.role_controller import RoleController

class AdminPanel(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.db = DBManager()
        self.user_controller = UserController(self.db)
        self.role_controller = RoleController(self.db)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(UserManagementView(self.db, self.current_user), 'Usuarios')
        self.tabs.addTab(RoleManagementView(self.db, self.current_user, self.user_controller), 'Roles')
        self.tabs.addTab(PermissionManagementView(self.db, self.current_user, self.user_controller, self.role_controller), 'Permisos')
        layout.addWidget(self.tabs)
        self.setLayout(layout)
