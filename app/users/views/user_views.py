from app.users.controllers.user_controller import UserController
from app.roles.controllers.role_controller import RoleController
from app.core.database.db_manager import DatabaseConnection
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog
from app.users.views.user_form import UserForm

class UserManagementView(QWidget):
    def __init__(self, db: DatabaseConnection, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.user_controller = UserController(db)
        self.role_controller = RoleController(db)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        if not self.is_admin():
            QMessageBox.warning(self, "Acceso denegado", "Solo el administrador puede gestionar usuarios.")
            self.setLayout(layout)
            return
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton('Crear usuario')
        self.create_btn.clicked.connect(self.create_user)
        btn_layout.addWidget(self.create_btn)
        self.refresh_btn = QPushButton('Refrescar')
        self.refresh_btn.clicked.connect(self.load_users)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Usuario', 'Email', 'Activo', 'Rol'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_user)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        users = self.user_controller.list_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem("Sí" if user.is_active else "No"))
            roles = self.user_controller.get_user_roles(user.id)
            role_names = ', '.join([self.role_controller.get_role(rid).name for rid in roles])
            self.table.setItem(row, 4, QTableWidgetItem(role_names))
        self.table.resizeColumnsToContents()

    def create_user(self):
        roles = [(r.id, r.name) for r in self.role_controller.list_roles()]
        form = UserForm(roles, parent=self)
        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            from app.models.user import User
            password_hash = User.hash_password(data['password'])
            user_id = self.user_controller.create_user(data['username'], data['full_name'], password_hash, data['email'])
            self.user_controller.assign_role(user_id, data['role_id'])
            self.load_users()
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")

    def edit_user(self, row, column):
        user_id = int(self.table.item(row, 0).text())
        user = self.user_controller.get_user(user_id)
        roles = [(r.id, r.name) for r in self.role_controller.list_roles()]
        user_roles = self.user_controller.get_user_roles(user_id)
        user.role_id = user_roles[0] if user_roles else None
        form = UserForm(roles, user, parent=self)
        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            update_data = {'username': data['username'], 'email': data['email']}
            if data['password']:
                update_data['password'] = data['password']
            self.user_controller.update_user(user_id, **update_data)
            self.user_controller.assign_role(user_id, data['role_id'])
            self.load_users()
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")

    def is_admin(self):
        roles = self.user_controller.get_user_roles(self.current_user.id)
        return 'admin' in [self.role_controller.get_role(rid).name for rid in roles]
