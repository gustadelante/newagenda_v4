from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class PermissionForm(QDialog):
    def __init__(self, permission=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Permiso" if permission is None else "Editar Permiso")
        self.permission = permission
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        if self.permission:
            self.name_edit.setText(self.permission.name)
            self.desc_edit.setText(self.permission.description)
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Descripción:"))
        layout.addWidget(self.desc_edit)
        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        cancel_btn = QPushButton("Cancelar")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'description': self.desc_edit.text()
        }
