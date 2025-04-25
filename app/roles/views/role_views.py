from app.roles.controllers.role_controller import RoleController
from app.core.database.db_manager import DatabaseConnection
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from app.roles.views.role_form import RoleForm

class RoleManagementView(QWidget):
    def __init__(self, db: DatabaseConnection, current_user, user_controller):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.user_controller = user_controller
        self.role_controller = RoleController(db)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        if not self.is_admin():
            QMessageBox.warning(self, "Acceso denegado", "Solo el administrador puede gestionar roles.")
            self.setLayout(layout)
            return
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton('Crear rol')
        self.create_btn.clicked.connect(self.create_role)
        btn_layout.addWidget(self.create_btn)
        self.refresh_btn = QPushButton('Refrescar')
        self.refresh_btn.clicked.connect(self.load_roles)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', 'Nombre', 'Descripción'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_role)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_roles()

    def load_roles(self):
        roles = self.role_controller.list_roles()
        self.table.setRowCount(len(roles))
        for row, role in enumerate(roles):
            self.table.setItem(row, 0, QTableWidgetItem(str(role.id)))
            self.table.setItem(row, 1, QTableWidgetItem(role.name))
            self.table.setItem(row, 2, QTableWidgetItem(role.description or ""))
        self.table.resizeColumnsToContents()

    def create_role(self):
        form = RoleForm(parent=self)
        if form.exec() == form.Accepted:
            data = form.get_data()
            self.role_controller.create_role(data['name'], data['description'])
            self.load_roles()
            QMessageBox.information(self, "Éxito", "Rol creado correctamente.")

    def edit_role(self, row, column):
        role_id = int(self.table.item(row, 0).text())
        role = self.role_controller.get_role(role_id)
        form = RoleForm(role, parent=self)
        if form.exec() == form.Accepted:
            data = form.get_data()
            self.role_controller.update_role(role_id, **data)
            self.load_roles()
            QMessageBox.information(self, "Éxito", "Rol actualizado correctamente.")

    def is_admin(self):
        roles = self.user_controller.get_user_roles(self.current_user.id)
        return 'admin' in [self.role_controller.get_role(rid).name for rid in roles]
