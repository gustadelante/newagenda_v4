from app.permissions.controllers.permission_controller import PermissionController
from app.core.database.db_manager import DatabaseConnection
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog
from app.permissions.views.permission_form import PermissionForm

class PermissionManagementView(QWidget):
    def __init__(self, db: DatabaseConnection, current_user, user_controller, role_controller):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.user_controller = user_controller
        self.role_controller = role_controller
        self.permission_controller = PermissionController(db)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        if not self.is_admin():
            QMessageBox.warning(self, "Acceso denegado", "Solo el administrador puede gestionar permisos.")
            self.setLayout(layout)
            return
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton('Crear permiso')
        self.create_btn.clicked.connect(self.create_permission)
        btn_layout.addWidget(self.create_btn)
        self.delete_btn = QPushButton('Eliminar permiso')
        self.delete_btn.clicked.connect(self.delete_permission)
        btn_layout.addWidget(self.delete_btn)
        self.refresh_btn = QPushButton('Refrescar')
        self.refresh_btn.clicked.connect(self.load_permissions)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', 'Nombre', 'Descripción'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_permission)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_permissions()

    def load_permissions(self):
        permissions = self.permission_controller.list_permissions()
        self.table.setRowCount(len(permissions))
        for row, perm in enumerate(permissions):
            self.table.setItem(row, 0, QTableWidgetItem(str(perm.id)))
            self.table.setItem(row, 1, QTableWidgetItem(perm.name))
            self.table.setItem(row, 2, QTableWidgetItem(perm.description or ""))
        self.table.resizeColumnsToContents()

    def create_permission(self):
        form = PermissionForm(parent=self)
        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            self.permission_controller.create_permission(data['name'], data['description'])
            self.load_permissions()
            QMessageBox.information(self, "Éxito", "Permiso creado correctamente.")

    def delete_permission(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Eliminar permiso", "Seleccione un permiso para eliminar.")
            return
        perm_id = int(self.table.item(selected, 0).text())
        nombre = self.table.item(selected, 1).text()
        confirm = QMessageBox.question(self, "Confirmar eliminación", f"¿Está seguro de eliminar el permiso '{nombre}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            if self.permission_controller.delete_permission(perm_id):
                self.load_permissions()
                QMessageBox.information(self, "Permiso eliminado", "El permiso fue eliminado correctamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el permiso.")

    def edit_permission(self, row, column):
        perm_id = int(self.table.item(row, 0).text())
        perm = self.permission_controller.get_permission(perm_id)
        form = PermissionForm(perm, parent=self)
        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            self.permission_controller.update_permission(perm_id, **data)
            self.load_permissions()
            QMessageBox.information(self, "Éxito", "Permiso actualizado correctamente.")

    def is_admin(self):
        roles = self.user_controller.get_user_roles(self.current_user.id)
        return 'admin' in [self.role_controller.get_role(rid).name for rid in roles]
