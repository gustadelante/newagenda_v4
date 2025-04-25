from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QMessageBox, QTabWidget, QWidget,
    QSpinBox, QCheckBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal, Slot

from datetime import date, datetime
import json

from ...controllers.expiration_controller import ExpirationController
from ...authentication.controllers.auth_controller import AuthController
from ...models.user import User


class ExpirationForm(QDialog):
    """Formulario para crear o editar un vencimiento"""
    
    def __init__(self, expiration_controller, expiration_id=None, parent=None):
        super().__init__(parent)
        self.expiration_controller = expiration_controller
        self.expiration_id = expiration_id
        self.auth_controller = AuthController()
        self.current_user = self.auth_controller.get_current_user()
        
        # Verificar si el usuario está autenticado
        if not self.current_user:
            # Intentar obtener el usuario actual nuevamente
            # Esto puede resolver problemas de sincronización en la inicialización
            import time
            time.sleep(0.1)  # Pequeña pausa para asegurar que la autenticación esté completa
            self.current_user = self.auth_controller.get_current_user()
            
            if not self.current_user:
                QMessageBox.critical(self, "Error de autenticación", "No hay un usuario autenticado. Por favor, inicie sesión nuevamente.")
                self.reject()
        
        self.expiration_data = None
        if expiration_id:
            # Cargar datos del vencimiento si se está editando
            success, data, _ = self.expiration_controller.get_expiration(expiration_id)
            if success:
                self.expiration_data = data
        
        self.setup_ui()
        if self.expiration_data:
            self.load_expiration_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Vencimiento" if not self.expiration_id else "Editar vencimiento")
        self.setMinimumSize(700, 500)
        
        main_layout = QVBoxLayout(self)
        
        # Tabs para organizar la información
        self.tab_widget = QTabWidget()
        
        # Tab de información básica
        basic_info_tab = QWidget()
        self.setup_basic_info_tab(basic_info_tab)
        self.tab_widget.addTab(basic_info_tab, "Información básica")
        
        # Tab de configuración de alertas
        alerts_tab = QWidget()
        self.setup_alerts_tab(alerts_tab)
        self.tab_widget.addTab(alerts_tab, "Alertas")
        
        # Tab de notas y observaciones
        notes_tab = QWidget()
        self.setup_notes_tab(notes_tab)
        self.tab_widget.addTab(notes_tab, "Notas")
        
        main_layout.addWidget(self.tab_widget)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_expiration)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_basic_info_tab(self, tab):
        """Configura la pestaña de información básica"""
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        
        # Fecha de vencimiento
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha de vencimiento:", self.date_edit)
        
        # Concepto
        self.concept_edit = QLineEdit()
        self.concept_edit.setPlaceholderText("Ingrese el concepto o descripción del vencimiento")
        layout.addRow("Concepto:", self.concept_edit)
        
        # Responsable
        self.responsible_combo = QComboBox()
        self.load_users()
        layout.addRow("Responsable:", self.responsible_combo)
        
        # Prioridad
        self.priority_combo = QComboBox()
        self.load_priorities()
        layout.addRow("Prioridad:", self.priority_combo)
        
        # Sector
        self.sector_combo = QComboBox()
        self.load_sectors()
        layout.addRow("Sector:", self.sector_combo)
        
        # Estado
        self.status_combo = QComboBox()
        self.load_statuses()
        layout.addRow("Estado:", self.status_combo)
    
    def setup_alerts_tab(self, tab):
        """Configura la pestaña de alertas"""
        layout = QVBoxLayout(tab)
        
        # Sección para agregar/editar alertas
        group_box = QGroupBox("Configuración de alertas")
        group_layout = QFormLayout()
        
        # Días antes
        self.days_before_spin = QSpinBox()
        self.days_before_spin.setRange(1, 365)
        self.days_before_spin.setValue(30)
        group_layout.addRow("Días antes del vencimiento:", self.days_before_spin)
        
        # Número máximo de alertas
        self.max_alerts_spin = QSpinBox()
        self.max_alerts_spin.setRange(1, 10)
        self.max_alerts_spin.setValue(3)
        group_layout.addRow("Número máximo de alertas:", self.max_alerts_spin)
        
        # Tipos de alerta
        self.email_alert_check = QCheckBox("Enviar alerta por correo electrónico")
        self.email_alert_check.setChecked(True)
        group_layout.addRow("", self.email_alert_check)
        
        self.push_alert_check = QCheckBox("Enviar notificación push (dispositivos móviles)")
        self.push_alert_check.setChecked(True)
        group_layout.addRow("", self.push_alert_check)
        
        self.desktop_alert_check = QCheckBox("Mostrar alerta en escritorio")
        self.desktop_alert_check.setChecked(True)
        group_layout.addRow("", self.desktop_alert_check)
        
        # Botón para agregar alerta
        self.add_alert_button = QPushButton("Agregar alerta")
        self.add_alert_button.clicked.connect(self.add_alert)
        
        group_layout.addRow("", self.add_alert_button)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        # Tabla de alertas configuradas
        alerts_label = QLabel("Alertas configuradas:")
        alerts_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(alerts_label)
        
        self.alerts_table = QTableWidget(0, 5)  # 5 columnas
        self.alerts_table.setHorizontalHeaderLabels([
            "Días antes", "Máx. alertas", "Email", "Push", "Escritorio"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_table.setAlternatingRowColors(True)
        layout.addWidget(self.alerts_table)
        
        # Botón para eliminar alerta seleccionada
        self.remove_alert_button = QPushButton("Eliminar alerta seleccionada")
        self.remove_alert_button.clicked.connect(self.remove_alert)
        layout.addWidget(self.remove_alert_button)
        
        # Si es un vencimiento existente, cargar sus alertas
        if self.expiration_id:
            self.load_alerts()
    
    def setup_notes_tab(self, tab):
        """Configura la pestaña de notas"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        notes_label = QLabel("Notas:")
        notes_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(notes_label)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Ingrese notas adicionales sobre este vencimiento...")
        layout.addWidget(self.notes_edit)
        
        # Historial de cambios (solo para vencimientos existentes)
        if self.expiration_id:
            history_label = QLabel("Historial de cambios:")
            history_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
            layout.addWidget(history_label)
            
            self.history_text = QTextEdit()
            self.history_text.setReadOnly(True)
            layout.addWidget(self.history_text)
            
            # Cargar historial de cambios desde la base de datos
            self.load_history_records()
    
    def load_users(self):
        """Carga los usuarios para el combo de responsables"""
        # Obtener todos los usuarios
        users = User.get_all()
        
        for user in users:
            self.responsible_combo.addItem(
                f"{user.full_name} ({user.email})", user.id
            )
    
    def load_priorities(self):
        """Carga las prioridades para el combo"""
        # Obtener prioridades desde la base de datos
        from ...database.connection import DatabaseConnection
        db = DatabaseConnection()
        priorities = db.execute_query("SELECT id, name, color FROM priorities ORDER BY name")
        
        for priority in priorities:
            self.priority_combo.addItem(priority['name'], priority['id'])
    
    def load_sectors(self):
        """Carga los sectores para el combo"""
        # Obtener sectores desde la base de datos
        from ...database.connection import DatabaseConnection
        db = DatabaseConnection()
        sectors = db.execute_query("SELECT id, name FROM sectors ORDER BY name")
        
        for sector in sectors:
            self.sector_combo.addItem(sector['name'], sector['id'])
    
    def load_statuses(self):
        """Carga los estados para el combo"""
        # Obtener estados desde la base de datos
        from ...database.connection import DatabaseConnection
        db = DatabaseConnection()
        statuses = db.execute_query("SELECT id, name FROM expiration_statuses ORDER BY name")
        
        for status in statuses:
            self.status_combo.addItem(status['name'], status['id'])
    
    def load_expiration_data(self):
        """Carga los datos del vencimiento en el formulario"""
        if not self.expiration_data:
            return
        
        # Fecha
        qdate = QDate(
            self.expiration_data['expiration_date'].year,
            self.expiration_data['expiration_date'].month,
            self.expiration_data['expiration_date'].day
        )
        self.date_edit.setDate(qdate)
        
        # Concepto
        self.concept_edit.setText(self.expiration_data['concept'])
        
        # Responsable
        if self.expiration_data['responsible_id']:
            index = self.responsible_combo.findData(self.expiration_data['responsible_id'])
            if index >= 0:
                self.responsible_combo.setCurrentIndex(index)
        
        # Prioridad
        if self.expiration_data['priority_id']:
            index = self.priority_combo.findData(self.expiration_data['priority_id'])
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        
        # Sector
        if self.expiration_data['sector_id']:
            index = self.sector_combo.findData(self.expiration_data['sector_id'])
            if index >= 0:
                self.sector_combo.setCurrentIndex(index)
        
        # Estado
        if self.expiration_data['status_id']:
            index = self.status_combo.findData(self.expiration_data['status_id'])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Notas
        if self.expiration_data['notes']:
            self.notes_edit.setText(self.expiration_data['notes'])
    
    def load_alerts(self):
        """Carga las alertas del vencimiento en la tabla"""
        if not self.expiration_id:
            return
        
        # Obtener alertas
        success, alerts, _ = self.expiration_controller.get_alerts_by_expiration(self.expiration_id)
        
        if success and alerts:
            self.alerts_table.setRowCount(len(alerts))
            
            for i, alert in enumerate(alerts):
                # Días antes
                days_item = QTableWidgetItem(str(alert['days_before']))
                self.alerts_table.setItem(i, 0, days_item)
                
                # Máximo de alertas
                max_alerts_item = QTableWidgetItem(str(alert['max_alerts']))
                self.alerts_table.setItem(i, 1, max_alerts_item)
                
                # Email
                email_item = QTableWidgetItem("✓" if alert['email_alert'] else "✗")
                email_item.setTextAlignment(Qt.AlignCenter)
                self.alerts_table.setItem(i, 2, email_item)
                
                # Push
                push_item = QTableWidgetItem("✓" if alert['push_alert'] else "✗")
                push_item.setTextAlignment(Qt.AlignCenter)
                self.alerts_table.setItem(i, 3, push_item)
                
                # Escritorio
                desktop_item = QTableWidgetItem("✓" if alert['desktop_alert'] else "✗")
                desktop_item.setTextAlignment(Qt.AlignCenter)
                self.alerts_table.setItem(i, 4, desktop_item)
                
                # Guardar ID de alerta como datos del elemento
                days_item.setData(Qt.UserRole, alert['id'])
    
    def load_history_records(self):
        """Carga el historial de cambios desde la base de datos"""
        from datetime import datetime
        
        if not self.expiration_id:
            return
            
        # Obtener historial desde el controlador
        success, history_records, error = self.expiration_controller.get_expiration_history(self.expiration_id)
        
        if success and history_records:
            history_text = ""
            
            for record in history_records:
                # Formatear fecha/hora
                date_time = record['created_at']
                if isinstance(date_time, str):
                    # Convertir string a datetime si es necesario
                    try:
                        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Si hay un error, mostrar como texto original
                        date_str = date_time
                        
                if isinstance(date_time, datetime):
                    date_str = date_time.strftime('%d/%m/%Y %H:%M')
                
                # Determinar el usuario que realizó el cambio
                user_text = ""
                if record.get('user_name'):
                    user_text = f" por <b>{record['user_name']}</b>"
                
                # Agregar entrada al historial con formato HTML
                history_text += f"<p><b>{date_str}</b> - <span style='color: #0066cc;'>{record['action_type']}</span>{user_text}"  
                history_text += f"<br>{record['description']}"  
                
                # Agregar notas si existen
                if record.get('notes') and record['notes'].strip():
                    history_text += f"<br><i>Nota: {record['notes']}</i>"
                    
                history_text += "</p>\n"
            
            self.history_text.setHtml(history_text)
        else:
            self.history_text.setText("No hay historial de cambios disponible.")
    
    def parse_history_from_notes(self):
        """Parsea el historial de cambios desde las notas"""
        notes = self.expiration_data['notes']
        
        # Buscar entradas de historial con el formato [YYYY-MM-DD] texto
        import re
        history_entries = re.findall(r'\[([\d-]+)\]\s+(.+?)(?=\n\[|$)', notes, re.DOTALL)
        
        if history_entries:
            history_text = ""
            for date_str, entry in history_entries:
                history_text += f"<b>{date_str}</b>: {entry.strip()}\n\n"
            
            self.history_text.setHtml(history_text)
        else:
            self.history_text.setText("No hay historial de cambios disponible.")
    
    def add_alert(self):
        """Agrega una nueva alerta a la tabla"""
        days_before = self.days_before_spin.value()
        max_alerts = self.max_alerts_spin.value()
        email_alert = self.email_alert_check.isChecked()
        push_alert = self.push_alert_check.isChecked()
        desktop_alert = self.desktop_alert_check.isChecked()
        
        # Verificar si ya existe una alerta con los mismos días
        for row in range(self.alerts_table.rowCount()):
            if int(self.alerts_table.item(row, 0).text()) == days_before:
                QMessageBox.warning(
                    self, "Alerta duplicada",
                    f"Ya existe una alerta configurada para {days_before} días antes."
                )
                return
        
        # Agregar fila a la tabla
        row = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row)
        
        # Días antes
        days_item = QTableWidgetItem(str(days_before))
        self.alerts_table.setItem(row, 0, days_item)
        
        # Máximo de alertas
        max_alerts_item = QTableWidgetItem(str(max_alerts))
        self.alerts_table.setItem(row, 1, max_alerts_item)
        
        # Email
        email_item = QTableWidgetItem("✓" if email_alert else "✗")
        email_item.setTextAlignment(Qt.AlignCenter)
        self.alerts_table.setItem(row, 2, email_item)
        
        # Push
        push_item = QTableWidgetItem("✓" if push_alert else "✗")
        push_item.setTextAlignment(Qt.AlignCenter)
        self.alerts_table.setItem(row, 3, push_item)
        
        # Escritorio
        desktop_item = QTableWidgetItem("✓" if desktop_alert else "✗")
        desktop_item.setTextAlignment(Qt.AlignCenter)
        self.alerts_table.setItem(row, 4, desktop_item)
        
        # Marcar como nueva alerta (sin ID)
        days_item.setData(Qt.UserRole, None)
        days_item.setBackground(Qt.green)
    
    def remove_alert(self):
        """Elimina la alerta seleccionada"""
        selected_rows = self.alerts_table.selectedIndexes()
        
        if not selected_rows:
            QMessageBox.warning(
                self, "Sin selección",
                "Por favor, seleccione una alerta para eliminar."
            )
            return
        
        row = selected_rows[0].row()
        alert_id = self.alerts_table.item(row, 0).data(Qt.UserRole)
        
        # Eliminar fila de la tabla
        self.alerts_table.removeRow(row)
        
        # Si la alerta ya existe en la base de datos, marcarla para eliminación
        if alert_id:
            # Aquí podríamos mantener una lista de alertas a eliminar
            # para procesarlas al guardar el vencimiento
            pass
    
    def validate_form(self):
        """Valida que los datos del formulario sean correctos"""
        if not self.concept_edit.text().strip():
            QMessageBox.warning(
                self, "Validación",
                "Por favor, ingrese un concepto para el vencimiento."
            )
            return False
        
        if self.responsible_combo.currentIndex() < 0:
            QMessageBox.warning(
                self, "Validación",
                "Por favor, seleccione un responsable para el vencimiento."
            )
            return False
        
        if self.priority_combo.currentIndex() < 0:
            QMessageBox.warning(
                self, "Validación",
                "Por favor, seleccione una prioridad para el vencimiento."
            )
            return False
        
        if self.sector_combo.currentIndex() < 0:
            QMessageBox.warning(
                self, "Validación",
                "Por favor, seleccione un sector para el vencimiento."
            )
            return False
        
        if self.status_combo.currentIndex() < 0:
            QMessageBox.warning(
                self, "Validación",
                "Por favor, seleccione un estado para el vencimiento."
            )
            return False
        
        return True
    
    def save_expiration(self):
        """Guarda el vencimiento y sus alertas"""
        if not self.validate_form():
            return
        
        # Verificar que el usuario esté autenticado
        if not self.current_user:
            # Intentar obtener el usuario actual nuevamente con un pequeño retraso
            import time
            time.sleep(0.1)  # Pequeña pausa para asegurar que la autenticación esté completa
            self.current_user = self.auth_controller.get_current_user()
            if not self.current_user:
                QMessageBox.critical(self, "Error de autenticación", "No hay un usuario autenticado. Por favor, inicie sesión nuevamente.")
                self.reject()
                return
        
        # Recopilar datos del vencimiento
        expiration_date = self.date_edit.date().toPython()
        concept = self.concept_edit.text().strip()
        responsible_id = self.responsible_combo.currentData()
        priority_id = self.priority_combo.currentData()
        sector_id = self.sector_combo.currentData()
        status_id = self.status_combo.currentData()
        notes = self.notes_edit.toPlainText().strip()
        
        # Crear diccionario de datos básicos
        expiration_data = {
            'expiration_date': expiration_date,
            'concept': concept,
            'responsible_id': responsible_id,
            'priority_id': priority_id,
            'sector_id': sector_id,
            'status_id': status_id,
            'notes': notes
        }
        
        # Agregar el ID del creador solo si el usuario está autenticado
        if self.current_user:
            expiration_data['created_by'] = self.current_user.id
        
        if self.expiration_id:
            # Actualizar vencimiento existente
            success, message = self.expiration_controller.update_expiration(
                self.expiration_id, expiration_data
            )
            
            if not success:
                QMessageBox.critical(
                    self, "Error al actualizar",
                    f"No se pudo actualizar el vencimiento: {message}"
                )
                return
                
            expiration_id = self.expiration_id
        else:
            # Crear nuevo vencimiento
            success, expiration_id, message = self.expiration_controller.create_expiration(
                expiration_data
            )
            
            if not success or not expiration_id:
                QMessageBox.critical(
                    self, "Error al crear",
                    f"No se pudo crear el vencimiento: {message}"
                )
                return
        
        # Procesar alertas
        self.save_alerts(expiration_id)
        
        self.accept()
    
    def save_alerts(self, expiration_id):
        """Guarda las alertas configuradas para el vencimiento"""
        # Si es una edición, primero obtener las alertas existentes
        existing_alerts = {}
        if self.expiration_id:
            success, alerts, _ = self.expiration_controller.get_alerts_by_expiration(expiration_id)
            if success:
                for alert in alerts:
                    existing_alerts[alert['id']] = alert
        
        # Procesar alertas de la tabla
        for row in range(self.alerts_table.rowCount()):
            days_before = int(self.alerts_table.item(row, 0).text())
            max_alerts = int(self.alerts_table.item(row, 1).text())
            email_alert = self.alerts_table.item(row, 2).text() == "✓"
            push_alert = self.alerts_table.item(row, 3).text() == "✓"
            desktop_alert = self.alerts_table.item(row, 4).text() == "✓"
            
            alert_id = self.alerts_table.item(row, 0).data(Qt.UserRole)
            
            alert_data = {
                'days_before': days_before,
                'max_alerts': max_alerts,
                'email_alert': email_alert,
                'push_alert': push_alert,
                'desktop_alert': desktop_alert,
                'is_active': True
            }
            
            if alert_id:
                # Actualizar alerta existente
                if alert_id in existing_alerts:
                    self.expiration_controller.update_alert(alert_id, alert_data)
                    del existing_alerts[alert_id]
            else:
                # Crear nueva alerta
                self.expiration_controller.create_alert(expiration_id, alert_data)
        
        # Eliminar alertas que ya no están en la tabla
        for alert_id in existing_alerts:
            self.expiration_controller.delete_alert(alert_id)
