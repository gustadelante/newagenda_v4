from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QComboBox, QDateEdit, QLineEdit, QFrame,
    QHeaderView, QMenu, QMessageBox, QDialog, QFormLayout
)
from PySide6.QtGui import QColor, QIcon, QAction
from PySide6.QtCore import Qt, QDate, Signal, Slot

from datetime import date, datetime, timedelta

from ...controllers.expiration_controller import ExpirationController
from ...controllers.auth_controller import AuthController
from .expiration_form import ExpirationForm


class ExpirationListView(QWidget):
    """Vista para listar y gestionar vencimientos"""
    expirationsChanged = Signal()
    
    def __init__(self, expiration_controller, parent=None):
        super().__init__(parent)
        self.expiration_controller = expiration_controller
        self.auth_controller = AuthController()
        self.current_user = self.auth_controller.get_current_user()
        self.expirations = []
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sección de filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Filtro de texto
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por concepto...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Filtros por categoría
        priority_label = QLabel("Prioridad:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("Todas", None)
        self.priority_combo.currentIndexChanged.connect(self.apply_filters)
        
        responsible_label = QLabel("Responsable:")
        self.responsible_combo = QComboBox()
        self.responsible_combo.addItem("Todos", None)
        self.responsible_combo.currentIndexChanged.connect(self.apply_filters)
        
        sector_label = QLabel("Sector:")
        self.sector_combo = QComboBox()
        self.sector_combo.addItem("Todos", None)
        self.sector_combo.currentIndexChanged.connect(self.apply_filters)
        
        status_label = QLabel("Estado:")
        self.status_combo = QComboBox()
        self.status_combo.addItem("Todos", None)
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Filtros de fecha
        date_from_label = QLabel("Desde:")
        self.date_from = QDateEdit()
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_from.dateChanged.connect(self.apply_filters)
        
        date_to_label = QLabel("Hasta:")
        self.date_to = QDateEdit()
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate().addMonths(3))
        self.date_to.dateChanged.connect(self.apply_filters)
        
        # Botón para limpiar filtros
        self.clear_filters_button = QPushButton("Limpiar filtros")
        self.clear_filters_button.clicked.connect(self.clear_filters)
        
        # Agregar widgets al layout de filtros
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(priority_label)
        filter_layout.addWidget(self.priority_combo)
        filter_layout.addWidget(responsible_label)
        filter_layout.addWidget(self.responsible_combo)
        filter_layout.addWidget(sector_label)
        filter_layout.addWidget(self.sector_combo)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(date_from_label)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(date_to_label)
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(self.clear_filters_button)
        
        main_layout.addWidget(filter_frame)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        self.new_button = QPushButton("Nuevo vencimiento")
        self.new_button.clicked.connect(self.create_new_expiration)
        
        self.edit_button = QPushButton("Editar vencimiento")
        self.edit_button.clicked.connect(self.edit_selected_expiration)
        self.edit_button.setEnabled(False)  # Inicialmente deshabilitado hasta que se seleccione una fila
        
        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.clicked.connect(self.refresh_data)
        
        actions_layout.addWidget(self.new_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.refresh_button)
        actions_layout.addStretch()
        
        main_layout.addLayout(actions_layout)
        
        # Tabla de vencimientos
        self.table = QTableWidget(0, 8)  # 8 columnas
        self.table.setHorizontalHeaderLabels([
            "ID", "Fecha", "Concepto", "Responsable", "Prioridad", 
            "Sector", "Estado", "Días"
        ])
        
        # Configurar tabla
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fecha
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Días
        self.table.setSortingEnabled(True) # Habilitar ordenamiento
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table) # Conectar señal de clic
        
        # Conectar eventos de tabla
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Configurar menú contextual
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.table, 1)  # 1 = stretch factor
        
        # Etiqueta de estado
        self.status_label = QLabel("Listo")
        main_layout.addWidget(self.status_label)
    
    def populate_filter_combos(self):
        """Popula los combos de filtros con datos únicos de los vencimientos"""
        # Guardar las selecciones actuales
        priority_id = self.priority_combo.currentData()
        responsible_id = self.responsible_combo.currentData()
        sector_id = self.sector_combo.currentData()
        status_id = self.status_combo.currentData()
        
        # Limpiar y repopular
        self.priority_combo.clear()
        self.responsible_combo.clear()
        self.sector_combo.clear()
        self.status_combo.clear()
        
        # Agregar opción "Todos"
        self.priority_combo.addItem("Todas", None)
        self.responsible_combo.addItem("Todos", None)
        self.sector_combo.addItem("Todos", None)
        self.status_combo.addItem("Todos", None)
        
        # Conjuntos para valores únicos
        priorities = set()
        responsibles = set()
        sectors = set()
        statuses = set()
        
        # Recolectar valores únicos
        for exp in self.expirations:
            if exp['priority'] and (exp['priority']['id'], exp['priority']['name']) not in priorities:
                priorities.add((exp['priority']['id'], exp['priority']['name']))
            
            if exp['responsible'] and (exp['responsible']['id'], exp['responsible']['full_name']) not in responsibles:
                responsibles.add((exp['responsible']['id'], exp['responsible']['full_name']))
            
            if exp['sector'] and (exp['sector']['id'], exp['sector']['name']) not in sectors:
                sectors.add((exp['sector']['id'], exp['sector']['name']))
            
            if exp['status'] and (exp['status']['id'], exp['status']['name']) not in statuses:
                statuses.add((exp['status']['id'], exp['status']['name']))
        
        # Agregar opciones a los combos
        for priority_id, priority_name in sorted(priorities, key=lambda x: x[1]):
            self.priority_combo.addItem(priority_name, priority_id)
        
        for responsible_id, responsible_name in sorted(responsibles, key=lambda x: x[1]):
            self.responsible_combo.addItem(responsible_name, responsible_id)
        
        for sector_id, sector_name in sorted(sectors, key=lambda x: x[1]):
            self.sector_combo.addItem(sector_name, sector_id)
        
        for status_id, status_name in sorted(statuses, key=lambda x: x[1]):
            self.status_combo.addItem(status_name, status_id)
        
        # Restaurar selecciones anteriores si es posible
        if priority_id is not None:
            index = self.priority_combo.findData(priority_id)
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        
        if responsible_id is not None:
            index = self.responsible_combo.findData(responsible_id)
            if index >= 0:
                self.responsible_combo.setCurrentIndex(index)
        
        if sector_id is not None:
            index = self.sector_combo.findData(sector_id)
            if index >= 0:
                self.sector_combo.setCurrentIndex(index)
        
        if status_id is not None:
            index = self.status_combo.findData(status_id)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
    
    def refresh_data(self):
        """Actualiza los datos de la tabla de vencimientos"""
        # Obtener todos los vencimientos
        success, expirations, message = self.expiration_controller.get_all_expirations(limit=1000)
        
        if success:
            self.expirations = expirations
            self.populate_filter_combos()
            # Asegurar que los filtros por defecto sean 'Todos'
            self.priority_combo.setCurrentIndex(0)
            self.responsible_combo.setCurrentIndex(0)
            self.sector_combo.setCurrentIndex(0)
            self.status_combo.setCurrentIndex(0)
            # Aplicar filtros (que ahora serán 'Todos' por defecto)
            self.apply_filters()
            self.status_label.setText(f"Total: {len(expirations)} vencimientos")
        else:
            self.status_label.setText(f"Error: {message}")
    
    def apply_filters(self):
        """Aplica los filtros seleccionados a la tabla de vencimientos"""
        search_text = self.search_input.text().strip().lower()
        priority_id = self.priority_combo.currentData()
        responsible_id = self.responsible_combo.currentData()
        sector_id = self.sector_combo.currentData()
        status_id = self.status_combo.currentData()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        
        # Filtrar vencimientos
        filtered = self.expirations
        
        # Filtro de texto
        if search_text:
            filtered = [exp for exp in filtered if search_text in exp['concept'].lower()]
        
        # Filtros por categoría
        if priority_id is not None:
            filtered = [exp for exp in filtered if exp['priority'] and exp['priority']['id'] == priority_id]
        
        if responsible_id is not None:
            filtered = [exp for exp in filtered if exp['responsible'] and exp['responsible']['id'] == responsible_id]
        
        if sector_id is not None:
            filtered = [exp for exp in filtered if exp['sector'] and exp['sector']['id'] == sector_id]
        
        if status_id is not None:
            filtered = [exp for exp in filtered if exp['status'] and exp['status']['id'] == status_id]
        
        # Filtros de fecha
        filtered = [
            exp for exp in filtered 
            if date_from <= exp['expiration_date'] <= date_to
        ]
        
        # Actualizar tabla
        self.update_table(filtered)
    
    def clear_filters(self):
        """Limpia los filtros aplicados"""
        self.search_input.clear()
        self.priority_combo.setCurrentIndex(0)
        self.responsible_combo.setCurrentIndex(0)
        self.sector_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        
        # Restablecer fechas
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_to.setDate(QDate.currentDate().addMonths(3))
        
        # Aplicar filtros (todos los vencimientos)
        self.apply_filters()
    
    def update_table(self, expirations):
        """Actualiza la tabla con los vencimientos filtrados"""
        # Desactivar temporalmente el ordenamiento para evitar problemas durante la actualización
        sorting_enabled = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)
        
        # Limpiar y establecer el número de filas
        self.table.clearContents()
        self.table.setRowCount(len(expirations))
        
        # Actualizar la etiqueta de estado para mostrar cuántos vencimientos se están mostrando
        self.status_label.setText(f"Mostrando: {len(expirations)} vencimientos")
        
        # Llenar la tabla con los datos
        for i, exp in enumerate(expirations):
            # ID
            id_item = QTableWidgetItem(str(exp['id']))
            self.table.setItem(i, 0, id_item)
            
            # Fecha
            date_item = QTableWidgetItem(exp['expiration_date'].strftime('%d/%m/%Y'))
            self.table.setItem(i, 1, date_item)
            
            # Concepto
            concept_item = QTableWidgetItem(exp['concept'])
            self.table.setItem(i, 2, concept_item)
            
            # Responsable
            responsible = ""
            if 'responsible' in exp and exp['responsible']:
                responsible = exp['responsible']['full_name']
            responsible_item = QTableWidgetItem(responsible)
            self.table.setItem(i, 3, responsible_item)
            
            # Prioridad
            priority = ""
            priority_item = QTableWidgetItem(priority)
            if 'priority' in exp and exp['priority']:
                priority = exp['priority']['name']
                priority_item.setText(priority)
                priority_item.setBackground(QColor(exp['priority']['color']))
                priority_item.setForeground(QColor("white"))
            self.table.setItem(i, 4, priority_item)
            
            # Sector
            sector = ""
            if 'sector' in exp and exp['sector']:
                sector = exp['sector']['name']
            sector_item = QTableWidgetItem(sector)
            self.table.setItem(i, 5, sector_item)
            
            # Estado
            status = ""
            status_item = QTableWidgetItem(status)
            if 'status' in exp and exp['status']:
                status = exp['status']['name']
                status_item.setText(status)
                status_item.setBackground(QColor(exp['status']['color']))
                # Verificar si es el estado "En proceso" para asegurar contraste adecuado
                if exp['status']['name'] == "En proceso":
                    status_item.setForeground(QColor("black"))
                else:
                    status_item.setForeground(QColor("white"))
            self.table.setItem(i, 6, status_item)
            
            # Días hasta vencimiento
            days_until = exp['days_until']
            days_item = QTableWidgetItem(str(days_until))
            
            if days_until < 0:
                days_item.setForeground(QColor("#dc3545"))  # Rojo
            elif days_until < 7:
                days_item.setForeground(QColor("#ffc107"))  # Amarillo
            else:
                days_item.setForeground(QColor("#28a745"))  # Verde
                
            self.table.setItem(i, 7, days_item)
        
        # Restaurar el ordenamiento si estaba habilitado
        self.table.setSortingEnabled(sorting_enabled)
        
        # Asegurar que la tabla se actualice visualmente
        # No llamar a update() sin argumentos ya que requiere un QRect
        self.table.viewport().update()
    
    def on_row_double_clicked(self, index):
        """Maneja el evento de doble clic en una fila"""
        row = index.row()
        expiration_id = int(self.table.item(row, 0).text())
        self.edit_expiration(expiration_id)
    
    def on_selection_changed(self):
        """Actualiza los botones según la selección actual"""
        selected_rows = self.table.selectionModel().selectedRows()
        self.edit_button.setEnabled(len(selected_rows) > 0)
    
    def edit_selected_expiration(self):
        """Edita el vencimiento seleccionado actualmente"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            expiration_id = int(self.table.item(row, 0).text())
            self.edit_expiration(expiration_id)
    
    def show_context_menu(self, position):
        """Muestra el menú contextual para la fila seleccionada"""
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            return
        
        row = selected_indexes[0].row()
        expiration_id = int(self.table.item(row, 0).text())
        
        menu = QMenu(self)
        
        view_action = QAction("Ver detalles", self)
        view_action.triggered.connect(lambda: self.view_expiration_details(expiration_id))
        menu.addAction(view_action)
        
        edit_action = QAction("Editar", self)
        edit_action.triggered.connect(lambda: self.edit_expiration(expiration_id))
        menu.addAction(edit_action)
        
        renew_action = QAction("Renovar", self)
        renew_action.triggered.connect(lambda: self.renew_expiration(expiration_id))
        menu.addAction(renew_action)
        
        # Menú para cambiar estado
        status_menu = QMenu("Cambiar estado", self)
        
        # Obtener estados posibles
        from ...database.connection import DatabaseConnection
        db = DatabaseConnection()
        statuses = db.execute_query("SELECT id, name FROM expiration_statuses ORDER BY name")
        
        for status in statuses:
            status_action = QAction(status['name'], self)
            status_action.triggered.connect(
                lambda checked, s_id=status['id']: self.change_expiration_status(expiration_id, s_id)
            )
            status_menu.addAction(status_action)
        
        menu.addMenu(status_menu)
        
        menu.addSeparator()
        
        delete_action = QAction("Eliminar", self)
        delete_action.triggered.connect(lambda: self.delete_expiration(expiration_id))
        menu.addAction(delete_action)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def create_new_expiration(self):
        """Abre el formulario para crear un nuevo vencimiento"""
        form = ExpirationForm(self.expiration_controller, parent=self)
        if form.exec() == QDialog.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Éxito", "Vencimiento creado correctamente.")
            self.expirationsChanged.emit()
    
    def view_expiration_details(self, expiration_id):
        """Muestra los detalles de un vencimiento en modo solo lectura"""
        dialog = ExpirationForm(self.expiration_controller, expiration_id=expiration_id)
        dialog.setWindowTitle("Detalles del vencimiento")
        
        # Deshabilitar edición
        for tab_index in range(dialog.tab_widget.count()):
            tab = dialog.tab_widget.widget(tab_index)
            for child in tab.findChildren(QWidget):
                if not isinstance(child, QLabel):
                    child.setEnabled(False)
        
        # Ocultar botón de guardar, cambiar cancelar por cerrar
        dialog.save_button.setVisible(False)
        dialog.cancel_button.setText("Cerrar")
        
        dialog.exec()
    
    def edit_expiration(self, expiration_id):
        """Abre el formulario para editar un vencimiento"""
        dialog = ExpirationForm(self.expiration_controller, expiration_id=expiration_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Éxito", "Vencimiento actualizado correctamente.")
            self.expirationsChanged.emit()
    
    def renew_expiration(self, expiration_id):
        """Abre un diálogo para renovar un vencimiento"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Renovar vencimiento")
        dialog.setMinimumWidth(300)
        
        layout = QFormLayout(dialog)
        
        # Fecha de nuevo vencimiento
        date_edit = QDateEdit()
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate().addMonths(1))  # Por defecto, un mes después
        layout.addRow("Nueva fecha:", date_edit)
        
        # Notas
        notes_edit = QLineEdit()
        notes_edit.setPlaceholderText("Notas sobre la renovación...")
        layout.addRow("Notas:", notes_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        accept_button = QPushButton("Renovar")
        cancel_button = QPushButton("Cancelar")
        
        button_layout.addWidget(accept_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
        # Conectar eventos
        accept_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            new_date = date_edit.date().toPython()
            notes = notes_edit.text()
            
            success, updated_id, message = self.expiration_controller.renew_expiration(
                expiration_id, new_date, notes
            )
            
            if success:
                self.refresh_data()
                QMessageBox.information(
                    self, "Éxito", 
                    f"Vencimiento renovado correctamente."
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al renovar vencimiento: {message}"
                )
    
    def change_expiration_status(self, expiration_id, status_id):
        """Cambia el estado de un vencimiento"""
        # Solicitar notas
        notes, ok = QInputDialog.getText(
            self, "Cambiar estado", 
            "Notas sobre el cambio de estado (opcional):"
        )
        
        if ok:
            success, message = self.expiration_controller.change_expiration_status(
                expiration_id, status_id, notes
            )
            
            if success:
                self.refresh_data()
                QMessageBox.information(self, "Éxito", "Estado de vencimiento actualizado correctamente.")
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al cambiar estado del vencimiento: {message}"
                )
    
    def delete_expiration(self, expiration_id):
        """Elimina un vencimiento"""
        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Está seguro que desea eliminar este vencimiento? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.expiration_controller.delete_expiration(expiration_id)
            
            if success:
                self.refresh_data()
                QMessageBox.information(self, "Éxito", "Vencimiento eliminado correctamente.")
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al eliminar vencimiento: {message}"
                )


    @Slot(int)
    def sort_table(self, logical_index):
        """Ordena la tabla por la columna clickeada"""
        # Determinar el orden
        if self.current_sort_column == logical_index:
            self.current_sort_order = Qt.DescendingOrder if self.current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_order = Qt.AscendingOrder
        
        self.current_sort_column = logical_index
        
        # Ordenar los datos en self.expirations basándose en la columna y orden
        # Nota: Esto requiere que los datos relevantes estén en self.expirations
        # o que se obtengan de la tabla antes de ordenar.
        # Por simplicidad, usaremos el ordenamiento incorporado de QTableWidget.
        self.table.sortByColumn(self.current_sort_column, self.current_sort_order)
