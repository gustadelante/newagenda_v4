from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox

class UserForm(QDialog):
    def __init__(self, roles, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Usuario" if user is None else "Editar Usuario")
        self.roles = roles
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.fullname_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        for rid, rname in self.roles:
            self.role_combo.addItem(rname, rid)
        if self.user:
            self.username_edit.setText(self.user.username)
            self.fullname_edit.setText(getattr(self.user, 'full_name', ''))
            self.email_edit.setText(self.user.email)
            self.role_combo.setCurrentIndex(self.role_combo.findData(self.user.role_id))
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Nombre completo:"))
        layout.addWidget(self.fullname_edit)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Contraseña:" if self.user is None else "Nueva contraseña (opcional):"))
        layout.addWidget(self.password_edit)
        layout.addWidget(QLabel("Rol:"))
        layout.addWidget(self.role_combo)
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
            'username': self.username_edit.text(),
            'full_name': self.fullname_edit.text(),
            'email': self.email_edit.text(),
            'password': self.password_edit.text(),
            'role_id': self.role_combo.currentData()
        }
