from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QComboBox, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QColor, QPainter
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from datetime import date, datetime, timedelta
import pandas as pd

from ...controllers.expiration_controller import ExpirationController
from ...utils.theme_manager import theme_manager


class ExpirationCard(QFrame):
    """Widget para mostrar un vencimiento como una tarjeta"""
    
    clicked = Signal(int)  # Señal que emite el ID del vencimiento
    
    def __init__(self, expiration, parent=None):
        super().__init__(parent)
        self.expiration = expiration
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la tarjeta"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(100)
        
        # Obtener datos relevantes
        exp_date = self.expiration['expiration_date']
        concept = self.expiration['concept']
        responsible = self.expiration['responsible']['full_name'] if self.expiration['responsible'] else "Sin asignar"
        priority = self.expiration['priority']['name'] if self.expiration['priority'] else "Sin prioridad"
        priority_color = self.expiration['priority']['color'] if self.expiration['priority'] else "#999999"
        days_until = self.expiration['days_until']
        
        # Definir el estilo de la tarjeta
        border_color = priority_color
        bg_color = f"{priority_color}22"  # Agregar transparencia
        
        if days_until < 0:
            # Vencido
            border_color = "#dc3545"
            bg_color = "#dc354522"
        elif days_until < 7:
            # Próximo a vencer
            border_color = "#ffc107"
            bg_color = "#ffc10722"
        
        self.setStyleSheet(f"""
            ExpirationCard {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: {bg_color};
                padding: 8px;
            }}
            ExpirationCard:hover {{
                border: 2px solid {border_color};
                background-color: {bg_color.replace('22', '44')};
            }}
        """)
        
        # Layout de la tarjeta
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Fecha y prioridad (primera fila)
        top_layout = QHBoxLayout()
        
        date_label = QLabel(exp_date.strftime('%d/%m/%Y'))
        date_label.setStyleSheet("font-weight: bold;")
        
        priority_label = QLabel(priority)
        priority_label.setStyleSheet(f"color: {priority_color}; font-weight: bold;")
        priority_label.setAlignment(Qt.AlignRight)
        
        top_layout.addWidget(date_label)
        top_layout.addWidget(priority_label)
        
        # Concepto
        concept_label = QLabel(concept)
        concept_label.setWordWrap(True)
        concept_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Responsable y días restantes
        bottom_layout = QHBoxLayout()
        
        responsible_label = QLabel(responsible)
        responsible_label.setStyleSheet("color: #6c757d;")
        
        days_label = QLabel(f"{abs(days_until)} {'días desde' if days_until < 0 else 'días para'} vencimiento")
        days_label.setAlignment(Qt.AlignRight)
        days_label.setStyleSheet(
            "color: #dc3545; font-weight: bold;" if days_until < 0 else
            "color: #ffc107; font-weight: bold;" if days_until < 7 else
            "color: #28a745; font-weight: bold;"
        )
        
        bottom_layout.addWidget(responsible_label)
        bottom_layout.addWidget(days_label)
        
        # Agregar todo al layout principal
        layout.addLayout(top_layout)
        layout.addWidget(concept_label, 1)  # 1 = stretch factor
        layout.addLayout(bottom_layout)
    
    def mousePressEvent(self, event):
        """Maneja el evento de clic en la tarjeta"""
        super().mousePressEvent(event)
        self.clicked.emit(self.expiration['id'])


class CategoryColumn(QWidget):
    """Widget para mostrar una columna de vencimientos por categoría"""
    
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la columna"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Título de la columna
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 16px;
            color: {self.color};
            border-bottom: 2px solid {self.color};
            padding-bottom: 5px;
        """)
        
        layout.addWidget(title_label)
        
        # Contenedor para las tarjetas
        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignTop)
        
        # Área de desplazamiento
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(scroll_area)
    
    def add_card(self, expiration):
        """Agrega una tarjeta de vencimiento a la columna"""
        card = ExpirationCard(expiration)
        self.cards_layout.addWidget(card)
        return card
    
    def clear(self):
        """Elimina todas las tarjetas de la columna"""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class AlfombraDashboard(QWidget):
    """
    Dashboard "Alfombra" que muestra los vencimientos organizados
    en columnas por categoría.
    """
    
    def __init__(self, expiration_controller: ExpirationController, parent=None):
        super().__init__(parent)
        self.expiration_controller = expiration_controller
        self.expirations = []
        self.category_columns = {}
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard"""
        main_layout = QVBoxLayout(self)
        
        # Sección de filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Selector de vista
        view_label = QLabel("Agrupar por:")
        self.view_combo = QComboBox()
        self.view_combo.addItem("Estado", "status")
        self.view_combo.addItem("Prioridad", "priority")
        self.view_combo.addItem("Sector", "sector")
        self.view_combo.addItem("Responsable", "responsible")
        self.view_combo.currentIndexChanged.connect(self.refresh_data)
        
        # Filtros adicionales
        self.filter_label = QLabel("Filtrar por:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Todos", None)
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)
        
        days_label = QLabel("Período:")
        self.days_combo = QComboBox()
        self.days_combo.addItem("7 días", 7)
        self.days_combo.addItem("15 días", 15)
        self.days_combo.addItem("30 días", 30)
        self.days_combo.addItem("60 días", 60)
        self.days_combo.addItem("90 días", 90)
        self.days_combo.setCurrentIndex(2)  # 30 días por defecto
        self.days_combo.currentIndexChanged.connect(self.refresh_data)
        
        # Botón para guardar la vista actual
        save_view_button = QPushButton("Guardar vista")
        save_view_button.clicked.connect(self.save_current_view)
        
        # Botón para exportar
        export_button = QPushButton("Exportar")
        export_button.clicked.connect(self.export_data)
        
        # Botón para imprimir
        print_button = QPushButton("Imprimir")
        print_button.clicked.connect(self.print_dashboard)
        
        # Agregar widgets al layout de filtros
        filter_layout.addWidget(view_label)
        filter_layout.addWidget(self.view_combo)
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(days_label)
        filter_layout.addWidget(self.days_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(save_view_button)
        filter_layout.addWidget(export_button)
        filter_layout.addWidget(print_button)
        
        main_layout.addWidget(filter_frame)
        
        # Contenedor para las columnas de categorías
        self.columns_container = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_container)
        self.columns_layout.setContentsMargins(0, 0, 0, 0)
        self.columns_layout.setSpacing(15)
        
        # Área de desplazamiento horizontal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.columns_container)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_layout.addWidget(scroll_area, 1)  # 1 = stretch factor
        
        # Tabla para ver los detalles de todos los vencimientos
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.StyledPanel)
        table_layout = QVBoxLayout(table_frame)
        
        table_label = QLabel("Todos los vencimientos")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        table_layout.addWidget(table_label)
        
        self.expirations_table = QTableWidget(0, 6)  # 6 columnas
        self.expirations_table.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Responsable", "Prioridad", "Sector", "Estado"
        ])
        self.expirations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expirations_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.expirations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expirations_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.expirations_table)
        
        main_layout.addWidget(table_frame)
    
    def refresh_data(self):
        """Actualiza los datos del dashboard"""
        # Obtener el período seleccionado
        days = self.days_combo.currentData()
        
        # Obtener vencimientos próximos
        success, expirations, _ = self.expiration_controller.get_upcoming_expirations(days)
        if success:
            self.expirations = expirations
            
            # Actualizar filtros
            self.update_filter_combo()
            
            # Actualizar vistas
            self.update_category_columns()
            self.update_expirations_table()
    
    def update_filter_combo(self):
        """Actualiza el combo de filtros según la vista seleccionada"""
        view_type = self.view_combo.currentData()
        
        # Guardar selección actual
        current_data = self.filter_combo.currentData()
        
        # Limpiar y configurar etiqueta
        self.filter_combo.clear()
        self.filter_combo.addItem("Todos", None)
        
        if view_type == "status":
            self.filter_label.setText("Filtrar por prioridad:")
            # Agregar prioridades únicas
            priorities = set()
            for exp in self.expirations:
                if exp['priority'] and (exp['priority']['id'], exp['priority']['name']) not in priorities:
                    priorities.add((exp['priority']['id'], exp['priority']['name']))
            
            for priority_id, priority_name in sorted(priorities, key=lambda x: x[1]):
                self.filter_combo.addItem(priority_name, priority_id)
        
        elif view_type == "priority":
            self.filter_label.setText("Filtrar por estado:")
            # Agregar estados únicos
            statuses = set()
            for exp in self.expirations:
                if exp['status'] and (exp['status']['id'], exp['status']['name']) not in statuses:
                    statuses.add((exp['status']['id'], exp['status']['name']))
            
            for status_id, status_name in sorted(statuses, key=lambda x: x[1]):
                self.filter_combo.addItem(status_name, status_id)
        
        elif view_type == "sector":
            self.filter_label.setText("Filtrar por prioridad:")
            # Agregar prioridades únicas
            priorities = set()
            for exp in self.expirations:
                if exp['priority'] and (exp['priority']['id'], exp['priority']['name']) not in priorities:
                    priorities.add((exp['priority']['id'], exp['priority']['name']))
            
            for priority_id, priority_name in sorted(priorities, key=lambda x: x[1]):
                self.filter_combo.addItem(priority_name, priority_id)
        
        elif view_type == "responsible":
            self.filter_label.setText("Filtrar por sector:")
            # Agregar sectores únicos
            sectors = set()
            for exp in self.expirations:
                if exp['sector'] and (exp['sector']['id'], exp['sector']['name']) not in sectors:
                    sectors.add((exp['sector']['id'], exp['sector']['name']))
            
            for sector_id, sector_name in sorted(sectors, key=lambda x: x[1]):
                self.filter_combo.addItem(sector_name, sector_id)
        
        # Restaurar selección anterior si es posible
        if current_data is not None:
            index = self.filter_combo.findData(current_data)
            if index >= 0:
                self.filter_combo.setCurrentIndex(index)
    
    def apply_filters(self):
        """Aplica los filtros seleccionados"""
        self.update_category_columns()
        self.update_expirations_table()
    
    def get_filtered_expirations(self):
        """Obtiene los vencimientos filtrados según los criterios seleccionados"""
        view_type = self.view_combo.currentData()
        filter_id = self.filter_combo.currentData()
        
        filtered = self.expirations
        
        if filter_id is not None:
            if view_type == "status" or view_type == "sector":
                # Filtrar por prioridad
                filtered = [exp for exp in filtered if exp['priority'] and exp['priority']['id'] == filter_id]
            elif view_type == "priority":
                # Filtrar por estado
                filtered = [exp for exp in filtered if exp['status'] and exp['status']['id'] == filter_id]
            elif view_type == "responsible":
                # Filtrar por sector
                filtered = [exp for exp in filtered if exp['sector'] and exp['sector']['id'] == filter_id]
        
        return filtered
    
    def update_category_columns(self):
        """Actualiza las columnas de categorías"""
        # Limpiar columnas existentes
        for column in self.category_columns.values():
            self.columns_layout.removeWidget(column)
            column.deleteLater()
        self.category_columns.clear()
        
        filtered_expirations = self.get_filtered_expirations()
        view_type = self.view_combo.currentData()
        
        # Agrupar vencimientos por categoría seleccionada
        categories = {}
        
        for exp in filtered_expirations:
            if view_type == "status":
                # Agrupar por estado
                if exp['status']:
                    category_id = exp['status']['id']
                    category_name = exp['status']['name']
                    category_color = exp['status']['color']
                else:
                    category_id = 0
                    category_name = "Sin estado"
                    category_color = "#999999"
            
            elif view_type == "priority":
                # Agrupar por prioridad
                if exp['priority']:
                    category_id = exp['priority']['id']
                    category_name = exp['priority']['name']
                    category_color = exp['priority']['color']
                else:
                    category_id = 0
                    category_name = "Sin prioridad"
                    category_color = "#999999"
            
            elif view_type == "sector":
                # Agrupar por sector
                if exp['sector']:
                    category_id = exp['sector']['id']
                    category_name = exp['sector']['name']
                    category_color = "#007bff"  # Color por defecto para sectores
                else:
                    category_id = 0
                    category_name = "Sin sector"
                    category_color = "#999999"
            
            elif view_type == "responsible":
                # Agrupar por responsable
                if exp['responsible']:
                    category_id = exp['responsible']['id']
                    category_name = exp['responsible']['full_name']
                    category_color = "#28a745"  # Color por defecto para responsables
                else:
                    category_id = 0
                    category_name = "Sin responsable"
                    category_color = "#999999"
            
            # Crear categoría si no existe
            if category_id not in categories:
                categories[category_id] = {
                    'name': category_name,
                    'color': category_color,
                    'expirations': []
                }
            
            # Agregar vencimiento a la categoría
            categories[category_id]['expirations'].append(exp)
        
        # Crear columnas para cada categoría
        for category_id, category_data in categories.items():
            column = CategoryColumn(
                f"{category_data['name']} ({len(category_data['expirations'])})", 
                category_data['color']
            )
            
            # Agregar tarjetas a la columna
            for exp in category_data['expirations']:
                card = column.add_card(exp)
                card.clicked.connect(self.on_expiration_card_clicked)
            
            # Agregar columna al layout
            self.columns_layout.addWidget(column)
            self.category_columns[category_id] = column
    
    def update_expirations_table(self):
        """Actualiza la tabla de vencimientos"""
        self.expirations_table.clearContents()
        
        filtered_expirations = self.get_filtered_expirations()
        self.expirations_table.setRowCount(len(filtered_expirations))
        
        for i, exp in enumerate(filtered_expirations):
            # Fecha
            date_item = QTableWidgetItem(exp['expiration_date'].strftime('%d/%m/%Y'))
            self.expirations_table.setItem(i, 0, date_item)
            
            # Concepto
            concept_item = QTableWidgetItem(exp['concept'])
            self.expirations_table.setItem(i, 1, concept_item)
            
            # Responsable
            responsible = exp['responsible']['full_name'] if exp['responsible'] else ""
            responsible_item = QTableWidgetItem(responsible)
            self.expirations_table.setItem(i, 2, responsible_item)
            
            # Prioridad
            priority = exp['priority']['name'] if exp['priority'] else ""
            priority_item = QTableWidgetItem(priority)
            if exp['priority']:
                priority_item.setBackground(QColor(exp['priority']['color']))
                priority_item.setForeground(QColor("white"))
            self.expirations_table.setItem(i, 3, priority_item)
            
            # Sector
            sector = exp['sector']['name'] if exp['sector'] else ""
            sector_item = QTableWidgetItem(sector)
            self.expirations_table.setItem(i, 4, sector_item)
            
            # Estado
            status = exp['status']['name'] if exp['status'] else ""
            status_item = QTableWidgetItem(status)
            if exp['status']:
                status_item.setBackground(QColor(exp['status']['color']))
                status_item.setForeground(QColor("white"))
            self.expirations_table.setItem(i, 5, status_item)
    
    def on_expiration_card_clicked(self, expiration_id):
        """Maneja el clic en una tarjeta de vencimiento"""
        # TODO: Implementar acción al hacer clic en una tarjeta
        QMessageBox.information(
            self, "Detalles del vencimiento",
            f"Funcionalidad para ver los detalles del vencimiento ID: {expiration_id} en desarrollo."
        )
    
    def save_current_view(self):
        """Guarda la configuración actual como una vista personalizada"""
        # TODO: Implementar guardado de vista personalizada
        QMessageBox.information(
            self, "Guardar vista",
            "Funcionalidad para guardar vista personalizada en desarrollo."
        )
    
    def export_data(self):
        """Exporta los datos del dashboard a un archivo Excel"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar datos", "", "Excel Files (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                filtered_expirations = self.get_filtered_expirations()
                
                # Convertir a DataFrame
                data = []
                for exp in filtered_expirations:
                    data.append({
                        'Fecha': exp['expiration_date'],
                        'Concepto': exp['concept'],
                        'Responsable': exp['responsible']['full_name'] if exp['responsible'] else "",
                        'Prioridad': exp['priority']['name'] if exp['priority'] else "",
                        'Sector': exp['sector']['name'] if exp['sector'] else "",
                        'Estado': exp['status']['name'] if exp['status'] else "",
                        'Días restantes': exp['days_until']
                    })
                
                df = pd.DataFrame(data)
                
                # Exportar a Excel
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Vencimientos', index=False)
                
                QMessageBox.information(
                    self, "Exportación exitosa",
                    f"Los datos se han exportado correctamente a:\n{file_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error de exportación",
                f"Error al exportar los datos: {e}"
            )
    
    def print_dashboard(self):
        """Imprime el dashboard actual"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.Accepted:
                # TODO: Implementar la impresión real del dashboard
                QMessageBox.information(
                    self, "Impresión",
                    "Funcionalidad de impresión en desarrollo."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error de impresión",
                f"Error al imprimir: {e}"
            )
