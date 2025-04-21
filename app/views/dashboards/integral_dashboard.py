from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QComboBox, QCalendarWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QTextCharFormat
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from datetime import date, datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from ...controllers.expiration_controller import ExpirationController
from ...utils.theme_manager import theme_manager


class IntegralDashboard(QWidget):
    """
    Dashboard "Integral" que muestra las alertas de vencimiento en formato
    de cuadrícula, calendario y gráfico circular.
    """
    
    def __init__(self, expiration_controller: ExpirationController, parent=None):
        super().__init__(parent)
        self.expiration_controller = expiration_controller
        self.expirations = []
        self._loading_data = False  # Flag to prevent filter signals during data load
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard"""
        main_layout = QVBoxLayout(self)
        
        # Sección de filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Filtros comunes
        priority_label = QLabel("Prioridad:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("Todas", None)
        self.priority_combo.setCurrentIndex(0)
        self.priority_combo.currentIndexChanged.connect(self.apply_filters)
        
        responsible_label = QLabel("Responsable:")
        self.responsible_combo = QComboBox()
        self.responsible_combo.addItem("Todos", None)
        self.responsible_combo.setCurrentIndex(0)
        self.responsible_combo.currentIndexChanged.connect(self.apply_filters)
        
        sector_label = QLabel("Sector:")
        self.sector_combo = QComboBox()
        self.sector_combo.addItem("Todos", None)
        self.sector_combo.setCurrentIndex(0)
        self.sector_combo.currentIndexChanged.connect(self.apply_filters)
        
        days_label = QLabel("Período:")
        self.days_combo = QComboBox()
        self.days_combo.addItem("Todos", None)
        self.days_combo.addItem("7 días", 7)
        self.days_combo.addItem("15 días", 15)
        self.days_combo.addItem("30 días", 30)
        self.days_combo.addItem("60 días", 60)
        self.days_combo.addItem("90 días", 90)
        self.days_combo.setCurrentIndex(0)  # Mostrar todos por defecto
        # Connect refresh_data AFTER setting initial index to avoid premature trigger
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
        filter_layout.addWidget(priority_label)
        filter_layout.addWidget(self.priority_combo)
        filter_layout.addWidget(responsible_label)
        filter_layout.addWidget(self.responsible_combo)
        filter_layout.addWidget(sector_label)
        filter_layout.addWidget(self.sector_combo)
        filter_layout.addWidget(days_label)
        filter_layout.addWidget(self.days_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(save_view_button)
        filter_layout.addWidget(export_button)
        filter_layout.addWidget(print_button)
        
        main_layout.addWidget(filter_frame)
        
        # Contenedor principal para las tres vistas
        content_layout = QHBoxLayout()
        
        # 1. Sección de cuadrícula de vencimientos
        grid_frame = QFrame()
        grid_frame.setFrameShape(QFrame.StyledPanel)
        grid_layout = QVBoxLayout(grid_frame)
        
        grid_title = QLabel("Vencimientos por prioridad")
        grid_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(grid_title)
        
        # Crear área de desplazamiento para la cuadrícula
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid_scroll.setWidget(self.grid_container)
        grid_layout.addWidget(self.grid_scroll)
        
        content_layout.addWidget(grid_frame, 3)  # 30% del espacio
        
        # 2. Sección de calendario
        calendar_frame = QFrame()
        calendar_frame.setFrameShape(QFrame.StyledPanel)
        calendar_layout = QVBoxLayout(calendar_frame)
        
        calendar_title = QLabel("Calendario de vencimientos")
        calendar_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        calendar_layout.addWidget(calendar_title)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.clicked.connect(self.date_selected)
        calendar_layout.addWidget(self.calendar)
        
        content_layout.addWidget(calendar_frame, 4)  # 40% del espacio
        
        # 3. Sección de gráfico circular
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_title = QLabel("Distribución por estado")
        chart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        chart_layout.addWidget(chart_title)
        
        # Crear el gráfico circular
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        
        content_layout.addWidget(chart_frame, 3)  # 30% del espacio
        
        main_layout.addLayout(content_layout, 1)
        
        # Sección de detalles (vencimientos del día seleccionado)
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_layout = QVBoxLayout(details_frame)
        
        details_title = QLabel("Detalles del día seleccionado")
        details_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        details_layout.addWidget(details_title)
        
        # Tabla de vencimientos
        self.details_table = QTableWidget(0, 6)  # 6 columnas
        self.details_table.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Responsable", "Prioridad", "Sector", "Estado"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.details_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.details_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.details_table.setAlternatingRowColors(True)
        details_layout.addWidget(self.details_table)
        
        main_layout.addWidget(details_frame)
    
    def refresh_data(self):
        """Actualiza los datos del dashboard"""
        self._loading_data = True # Set flag before loading
        # Obtener el período seleccionado
        days = self.days_combo.currentData()
        if days is None:
            # Sin filtro de días, traer todos los vencimientos
            success, expirations, _ = self.expiration_controller.get_all_expirations()
        else:
            # Obtener vencimientos próximos
            success, expirations, _ = self.expiration_controller.get_upcoming_expirations(days)
        
        if success:
            self.expirations = expirations
            # Actualizar combos de filtro (esto puede disparar apply_filters si no se maneja)
            self.populate_filter_combos()
            self._loading_data = False # Unset flag after populating combos
            # Aplicar filtros y actualizar vistas explícitamente
            self.apply_filters()
            # Seleccionar la fecha actual en el calendario y actualizar detalles
            current_qdate = QDate.currentDate()
            self.calendar.setSelectedDate(current_qdate)
            # self.date_selected(current_qdate) # apply_filters ahora llama a date_selected
        else:
            self.expirations = []
            self.populate_filter_combos() # Clear combos even on error
            self._loading_data = False # Unset flag
            self.apply_filters() # Clear views
            QMessageBox.warning(self, "Error", "No se pudieron cargar los vencimientos.")

    def populate_filter_combos(self):
        """Popula los combos de filtros con datos únicos de los vencimientos cargados"""
        # Guardar selecciones actuales
        priority_id = self.priority_combo.currentData()
        responsible_id = self.responsible_combo.currentData()
        sector_id = self.sector_combo.currentData()

        # Desconectar señales temporalmente para evitar triggers
        try:
            self.priority_combo.currentIndexChanged.disconnect(self.apply_filters)
            self.responsible_combo.currentIndexChanged.disconnect(self.apply_filters)
            self.sector_combo.currentIndexChanged.disconnect(self.apply_filters)
        except RuntimeError: # Signals might not be connected yet
            pass

        # Limpiar y repopular
        self.priority_combo.clear()
        self.responsible_combo.clear()
        self.sector_combo.clear()

        self.priority_combo.addItem("Todas", None)
        self.responsible_combo.addItem("Todos", None)
        self.sector_combo.addItem("Todos", None)

        priorities = set()
        responsibles = set()
        sectors = set()

        for exp in self.expirations:
            if exp['priority'] and (exp['priority']['id'], exp['priority']['name']) not in priorities:
                priorities.add((exp['priority']['id'], exp['priority']['name']))
            if exp['responsible'] and (exp['responsible']['id'], exp['responsible']['full_name']) not in responsibles:
                responsibles.add((exp['responsible']['id'], exp['responsible']['full_name']))
            if exp['sector'] and (exp['sector']['id'], exp['sector']['name']) not in sectors:
                sectors.add((exp['sector']['id'], exp['sector']['name']))

        for pid, name in sorted(priorities, key=lambda x: x[1]):
            self.priority_combo.addItem(name, pid)
        for rid, name in sorted(responsibles, key=lambda x: x[1]):
            self.responsible_combo.addItem(name, rid)
        for sid, name in sorted(sectors, key=lambda x: x[1]):
            self.sector_combo.addItem(name, sid)

        # Restaurar selecciones
        priority_index = self.priority_combo.findData(priority_id)
        self.priority_combo.setCurrentIndex(priority_index if priority_index >= 0 else 0)

        responsible_index = self.responsible_combo.findData(responsible_id)
        self.responsible_combo.setCurrentIndex(responsible_index if responsible_index >= 0 else 0)

        sector_index = self.sector_combo.findData(sector_id)
        self.sector_combo.setCurrentIndex(sector_index if sector_index >= 0 else 0)

        # Reconectar señales
        self.priority_combo.currentIndexChanged.connect(self.apply_filters)
        self.responsible_combo.currentIndexChanged.connect(self.apply_filters)
        self.sector_combo.currentIndexChanged.connect(self.apply_filters)

    def apply_filters(self):
        """Aplica los filtros seleccionados y actualiza las vistas"""
        if self._loading_data:
            return # No aplicar filtros mientras se cargan datos
            
        filtered_expirations = self.get_filtered_expirations()
        
        self.update_grid(filtered_expirations)
        self.update_calendar(filtered_expirations)
        self.update_chart(filtered_expirations)
        # Actualizar detalles para la fecha seleccionada actualmente en el calendario
        self.date_selected(self.calendar.selectedDate())

    def get_filtered_expirations(self):
        """Filtra la lista self.expirations según los combos seleccionados"""
        priority_id = self.priority_combo.currentData()
        responsible_id = self.responsible_combo.currentData()
        sector_id = self.sector_combo.currentData()
        
        filtered = self.expirations
        
        if priority_id is not None:
            filtered = [exp for exp in filtered if exp['priority'] and exp['priority']['id'] == priority_id]
            
        if responsible_id is not None:
            filtered = [exp for exp in filtered if exp['responsible'] and exp['responsible']['id'] == responsible_id]
            
        if sector_id is not None:
            filtered = [exp for exp in filtered if exp['sector'] and exp['sector']['id'] == sector_id]
            
        return filtered

    def update_grid(self, expirations_to_display):
        """Actualiza la cuadrícula de vencimientos con los datos filtrados"""
        # Limpiar cuadrícula existente
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
        
        filtered_expirations = self.get_filtered_expirations()
        
        # Agrupar por prioridad
        exp_by_priority = {}
        for exp in expirations_to_display:
            priority_name = exp['priority']['name'] if exp['priority'] else "Sin prioridad"
            priority_color = exp['priority']['color'] if exp['priority'] else "#999999"
            
            if priority_name not in exp_by_priority:
                exp_by_priority[priority_name] = {
                    'color': priority_color,
                    'expirations': []
                }
            
            exp_by_priority[priority_name]['expirations'].append(exp)
        
        # Ordenar prioridades (Crítica, Alta, Media, Baja)
        priority_order = {"Crítica": 0, "Alta": 1, "Media": 2, "Baja": 3}
        sorted_priorities = sorted(
            exp_by_priority.keys(),
            key=lambda p: priority_order.get(p, 99)
        )
        
        # Crear widgets para cada prioridad
        row = 0
        for priority in sorted_priorities:
            priority_data = exp_by_priority[priority]
            
            # Encabezado de prioridad
            header = QLabel(f"{priority} ({len(priority_data['expirations'])})")
            header.setStyleSheet(f"font-weight: bold; color: {priority_data['color']};")
            self.grid.addWidget(header, row, 0, 1, 2)
            row += 1
            
            # Vencimientos de esta prioridad (mostrar hasta 5 por prioridad)
            for i, exp in enumerate(priority_data['expirations'][:5]):
                date_label = QLabel(exp['expiration_date'].strftime('%d/%m/%Y'))
                concept_label = QLabel(exp['concept'][:50] + ('...' if len(exp['concept']) > 50 else ''))
                
                days_until = exp['days_until']
                if days_until < 0:
                    date_label.setStyleSheet("color: #dc3545;")  # rojo para vencidos
                elif days_until < 7:
                    date_label.setStyleSheet("color: #ffc107;")  # amarillo para próximos
                
                self.grid.addWidget(date_label, row, 0)
                self.grid.addWidget(concept_label, row, 1)
                row += 1
            
            # Si hay más de 5, mostrar botón "Ver más"
            if len(priority_data['expirations']) > 5:
                more_button = QPushButton(f"Ver todos ({len(priority_data['expirations'])})")
                more_button.clicked.connect(
                    lambda checked, p=priority: self.show_priority_expirations(p)
                )
                self.grid.addWidget(more_button, row, 0, 1, 2)
                row += 1
            
            # Separador
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            self.grid.addWidget(separator, row, 0, 1, 2)
            row += 1
    
    def update_calendar(self, expirations_to_display):
        """Actualiza el calendario resaltando las fechas con vencimientos filtrados"""
        # Limpiar formatos existentes
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        filtered_expirations = self.get_filtered_expirations()
        
        # Marcar fechas con vencimientos
        format = self.calendar.dateTextFormat(QDate())
        for exp in filtered_expirations:
            qdate = QDate(
                exp['expiration_date'].year,
                exp['expiration_date'].month,
                exp['expiration_date'].day
            )
            
            # Formato según prioridad
            if exp['priority']:
                color = QColor(exp['priority']['color'])
            else:
                color = QColor("#999999")
            
            format.setBackground(color)
            format.setForeground(QColor("white"))
            self.calendar.setDateTextFormat(qdate, format)
    
    def update_chart(self, expirations_to_display):
        """Actualiza el gráfico circular con la distribución por estado de los datos filtrados"""
        # Crear un nuevo gráfico
        chart = QChart()
        chart.setTitle("Distribución por estado")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Crear la serie de tarta
        series = QPieSeries()

        # Agrupar por estado
        status_counts = {}
        for exp in expirations_to_display:
            status_name = exp['status']['name'] if exp['status'] else "Sin estado"
            status_color = exp['status']['color'] if exp['status'] else "#999999"
            if status_name not in status_counts:
                status_counts[status_name] = {'count': 0, 'color': status_color}
            status_counts[status_name]['count'] += 1

        # Añadir datos a la serie
        total_expirations = len(expirations_to_display)
        if total_expirations > 0:
            for status_name, data in status_counts.items():
                count = data['count']
                percentage = (count / total_expirations) * 100
                slice_label = f"{status_name}: {count} ({percentage:.1f}%)"
                pie_slice = QPieSlice(slice_label, count)
                pie_slice.setColor(QColor(data['color']))
                pie_slice.setLabelVisible(True)
                series.append(pie_slice)

        # Añadir serie al gráfico
        chart.addSeries(series)

        # Configurar leyenda
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # Limpiar series anteriores y establecer el nuevo gráfico
        self.chart_view.setChart(chart)

    def date_selected(self, date): # Parameter name is 'date'
        """Muestra los detalles de los vencimientos para la fecha seleccionada"""
        # Limpiar tabla de detalles
        self.details_table.setRowCount(0)
        
        # Obtener los vencimientos filtrados actualmente
        current_filtered_expirations = self.get_filtered_expirations()

        # Filtrar vencimientos para la fecha seleccionada
        selected_date_obj = date.toPython() # Use the parameter 'date'
        expirations_on_date = [
            exp for exp in current_filtered_expirations # Use the filtered list
            if exp['expiration_date'] == selected_date_obj
        ]
        
        # Poblar tabla de detalles
        self.details_table.setRowCount(len(expirations_on_date))
        for i, exp in enumerate(expirations_on_date): # Usar enumerate para obtener el índice i
            # Fecha
            date_item = QTableWidgetItem(exp['expiration_date'].strftime('%d/%m/%Y'))
            self.details_table.setItem(i, 0, date_item)
            
            # Concepto
            concept_item = QTableWidgetItem(exp['concept'])
            self.details_table.setItem(i, 1, concept_item)
            
            # Responsable
            responsible = exp['responsible']['full_name'] if exp['responsible'] else ""
            responsible_item = QTableWidgetItem(responsible)
            self.details_table.setItem(i, 2, responsible_item)
            
            # Prioridad
            priority = exp['priority']['name'] if exp['priority'] else ""
            priority_item = QTableWidgetItem(priority)
            if exp['priority']:
                priority_item.setBackground(QColor(exp['priority']['color']))
                priority_item.setForeground(QColor("white"))
            self.details_table.setItem(i, 3, priority_item)
            
            # Sector
            sector = exp['sector']['name'] if exp['sector'] else ""
            sector_item = QTableWidgetItem(sector)
            self.details_table.setItem(i, 4, sector_item)
            
            # Estado
            status = exp['status']['name'] if exp['status'] else ""
            status_item = QTableWidgetItem(status)
            if exp['status']:
                status_item.setBackground(QColor(exp['status']['color']))
                status_item.setForeground(QColor("white"))
            self.details_table.setItem(i, 5, status_item)
    
    def show_priority_expirations(self, priority):
        """Muestra todos los vencimientos de una prioridad específica"""
        # Esta función se llamaría desde el botón "Ver más"
        # TODO: Implementar ventana o diálogo para mostrar todos los vencimientos
        QMessageBox.information(
            self, f"Vencimientos de prioridad {priority}",
            f"Funcionalidad para ver todos los vencimientos de prioridad {priority} en desarrollo."
        )
    
    def save_current_view(self):
        """Guarda la configuración actual de filtros como una vista personalizada"""
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
