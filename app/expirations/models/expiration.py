from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from app.core.database.connection import DatabaseConnection
from app.models.user import User


class Expiration:
    """Modelo para representar un vencimiento en el sistema"""
    
    def __init__(self, id: Optional[int] = None, expiration_date: date = None, 
                 concept: str = "", responsible_id: int = None, priority_id: int = None, 
                 sector_id: int = None, status_id: int = None, notes: str = "", 
                 created_by: int = None):
        self.id = id
        self.expiration_date = expiration_date or date.today()
        self.concept = concept
        self.responsible_id = responsible_id
        self.priority_id = priority_id
        self.sector_id = sector_id
        self.status_id = status_id
        self.notes = notes
        self.created_by = created_by
        self.db = DatabaseConnection()
        
        # Propiedades calculadas
        self._responsible = None
        self._priority = None
        self._sector = None
        self._status = None
        self._created_by_user = None
    
    def save(self, user_id=None) -> bool:
        """Guarda el vencimiento en la base de datos
        
        Args:
            user_id: ID del usuario que realiza la operación (opcional)
        """
        try:
            if self.id:
                # Obtener los datos del vencimiento antes de actualizarlo
                original_expiration = None
                try:
                    original_query = "SELECT * FROM expirations WHERE id = %s"
                    result = self.db.execute_query(original_query, (self.id,))
                    if result:
                        original_expiration = result[0]
                except Exception as e:
                    print(f"Error al obtener datos originales del vencimiento: {e}")
                
                # Actualizar vencimiento existente
                query = """
                UPDATE expirations SET
                    expiration_date = %s,
                    concept = %s,
                    responsible_id = %s,
                    priority_id = %s,
                    sector_id = %s,
                    status_id = %s,
                    notes = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                params = (
                    self.expiration_date, self.concept, self.responsible_id,
                    self.priority_id, self.sector_id, self.status_id,
                    self.notes, self.id
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
                # Generar descripción detallada de los cambios
                if original_expiration:
                    changes = []
                    
                    # Verificar cambios en cada campo
                    if str(original_expiration.get('expiration_date')) != str(self.expiration_date):
                        changes.append(f"Fecha de vencimiento: {original_expiration.get('expiration_date')} → {self.expiration_date}")
                    
                    if original_expiration.get('concept') != self.concept:
                        changes.append(f"Concepto: {original_expiration.get('concept')} → {self.concept}")
                    
                    if str(original_expiration.get('responsible_id')) != str(self.responsible_id):
                        # Obtener nombres de responsables
                        old_responsible = self._get_responsible_name_by_id(original_expiration.get('responsible_id'))
                        new_responsible = self._get_responsible_name_by_id(self.responsible_id)
                        changes.append(f"Responsable: {old_responsible} → {new_responsible}")
                    
                    if str(original_expiration.get('priority_id')) != str(self.priority_id):
                        # Obtener nombres de prioridades
                        old_priority = self._get_priority_name_by_id(original_expiration.get('priority_id'))
                        new_priority = self._get_priority_name_by_id(self.priority_id)
                        changes.append(f"Prioridad: {old_priority} → {new_priority}")
                    
                    if str(original_expiration.get('sector_id')) != str(self.sector_id):
                        # Obtener nombres de sectores
                        old_sector = self._get_sector_name_by_id(original_expiration.get('sector_id'))
                        new_sector = self._get_sector_name_by_id(self.sector_id)
                        changes.append(f"Sector: {old_sector} → {new_sector}")
                    
                    if str(original_expiration.get('status_id')) != str(self.status_id):
                        # Obtener nombres de estados
                        old_status = self._get_status_name_by_id(original_expiration.get('status_id'))
                        new_status = self._get_status_name_by_id(self.status_id)
                        changes.append(f"Estado: {old_status} → {new_status}")
                    
                    if original_expiration.get('notes') != self.notes:
                        changes.append(f"Notas actualizadas")
                    
                    # Si hay cambios, registrarlos
                    if changes:
                        description = "Cambios en el vencimiento: " + ", ".join(changes)
                    else:
                        description = "Información del vencimiento actualizada (sin cambios detectados)"
                else:
                    description = "Información del vencimiento actualizada"
                
                # Registrar actualización en el historial
                self._add_history_record(
                    "Actualización", 
                    description, 
                    self.notes, 
                    user_id  # Usar el ID del usuario proporcionado
                )
            else:
                # Crear nuevo vencimiento
                query = """
                INSERT INTO expirations (
                    expiration_date, concept, responsible_id, priority_id,
                    sector_id, status_id, notes, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    self.expiration_date, self.concept, self.responsible_id,
                    self.priority_id, self.sector_id, self.status_id,
                    self.notes, self.created_by
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
                # Obtener el ID generado
                result = self.db.execute_query(
                    "SELECT LAST_INSERT_ID() as id"
                )
                if result:
                    self.id = result[0]['id']
                    
                    # Crear alerta por defecto (30 días antes)
                    self.create_default_alert()
                    
                    # Registrar creación en el historial con más detalle
                    description = f"Nuevo vencimiento creado: {self.concept} - Vence: {self.expiration_date}"
                    self._add_history_record(
                        "Creación", 
                        description, 
                        self.notes, 
                        user_id if user_id is not None else self.created_by
                    )
            
            return True
        except Exception as e:
            print(f"Error al guardar vencimiento: {e}")
            return False
    
    def create_default_alert(self) -> bool:
        """Crea una alerta por defecto para el vencimiento"""
        if not self.id:
            return False
            
        try:
            query = """
            INSERT INTO alerts (
                expiration_id, days_before, alert_count, max_alerts,
                email_alert, push_alert, desktop_alert, is_active
            ) VALUES (?, 30, 0, 3, TRUE, TRUE, TRUE, TRUE)
            """
            self.db.execute_query(query, (self.id,), fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al crear alerta por defecto: {e}")
            return False
    
    def delete(self) -> bool:
        """Elimina el vencimiento de la base de datos"""
        try:
            if self.id:
                # Las alertas se eliminarán automáticamente por la restricción ON DELETE CASCADE
                query = "DELETE FROM expirations WHERE id = ?"
                self.db.execute_query(query, (self.id,), fetch=False, commit=True)
                self.id = None
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar vencimiento: {e}")
            return False
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Obtiene las alertas configuradas para este vencimiento"""
        if not self.id:
            return []
            
        query = "SELECT * FROM alerts WHERE expiration_id = ?"
        return self.db.execute_query(query, (self.id,))
    
    def add_alert(self, days_before: int, max_alerts: int = 3, 
                 email_alert: bool = True, push_alert: bool = True,
                 desktop_alert: bool = True) -> bool:
        """Agrega una nueva alerta para el vencimiento"""
        if not self.id:
            return False
            
        try:
            query = """
            INSERT INTO alerts (
                expiration_id, days_before, max_alerts,
                email_alert, push_alert, desktop_alert, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, TRUE)
            """
            params = (self.id, days_before, max_alerts, email_alert, push_alert, desktop_alert)
            self.db.execute_query(query, params, fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al agregar alerta: {e}")
            return False
    
    def update_alert(self, alert_id: int, days_before: int = None, max_alerts: int = None,
                    email_alert: bool = None, push_alert: bool = None,
                    desktop_alert: bool = None, is_active: bool = None) -> bool:
        """Actualiza una alerta existente"""
        if not self.id:
            return False
            
        try:
            # Obtener valores actuales
            result = self.db.execute_query(
                "SELECT * FROM alerts WHERE id = ? AND expiration_id = ?",
                (alert_id, self.id)
            )
            
            if not result:
                return False
                
            current = result[0]
            
            # Preparar la consulta y parámetros
            query = """
            UPDATE alerts SET
                days_before = ?,
                max_alerts = ?,
                email_alert = ?,
                push_alert = ?,
                desktop_alert = ?,
                is_active = ?
            WHERE id = ? AND expiration_id = ?
            """
            params = (
                days_before if days_before is not None else current['days_before'],
                max_alerts if max_alerts is not None else current['max_alerts'],
                email_alert if email_alert is not None else current['email_alert'],
                push_alert if push_alert is not None else current['push_alert'],
                desktop_alert if desktop_alert is not None else current['desktop_alert'],
                is_active if is_active is not None else current['is_active'],
                alert_id, self.id
            )
            
            self.db.execute_query(query, params, fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al actualizar alerta: {e}")
            return False
    
    def delete_alert(self, alert_id: int) -> bool:
        """Elimina una alerta"""
        if not self.id:
            return False
            
        try:
            query = "DELETE FROM alerts WHERE id = ? AND expiration_id = ?"
            self.db.execute_query(query, (alert_id, self.id), fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al eliminar alerta: {e}")
            return False
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de alertas para este vencimiento"""
        if not self.id:
            return []
            
        query = """
        SELECT ah.* 
        FROM alert_history ah
        JOIN alerts a ON ah.alert_id = a.id
        WHERE a.expiration_id = %s
        ORDER BY ah.alert_date DESC
        """
        return self.db.execute_query(query, (self.id,))
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de cambios para este vencimiento"""
        if not self.id:
            return []
            
        query = """
        SELECT h.*, u.full_name as user_name
        FROM expiration_history h
        LEFT JOIN users u ON h.user_id = u.id
        WHERE h.expiration_id = %s
        ORDER BY h.created_at DESC
        """
        return self.db.execute_query(query, (self.id,))
    
    def renew(self, new_date: date, notes: str = "", user_id: int = None) -> bool:
        """
        Renueva el vencimiento, actualizando la fecha
        
        Args:
            new_date: Nueva fecha de vencimiento
            notes: Notas sobre la renovación
            user_id: ID del usuario que realiza la renovación
            
        Returns:
            True si se renovó correctamente, False en caso contrario
        """
        try:
            # Validar que la fecha sea posterior a la actual
            if new_date <= date.today():
                return False
                
            # Actualizar la fecha de vencimiento
            self.expiration_date = new_date
            
            # Cambiar estado a "Renovado"
            status_id = self._get_status_id_by_name("Renovado")
            if status_id:
                self.status_id = status_id
            
            # Registrar el cambio en el historial
            self._add_history_record(
                "Renovación", 
                f"Vencimiento renovado para el {new_date.strftime('%d/%m/%Y')}", 
                notes,
                user_id
            )
            
            # Guardar cambios
            return self.save()
        except Exception as e:
            print(f"Error al renovar vencimiento: {e}")
            return False
    
    def change_status(self, status_id: int, notes: str = "", user_id: int = None) -> bool:
        """
        Cambia el estado del vencimiento
        
        Args:
            status_id: ID del nuevo estado
            notes: Notas sobre el cambio
            user_id: ID del usuario que realiza el cambio
            
        Returns:
            True si se cambió correctamente, False en caso contrario
        """
        try:
            # Validar que el estado sea diferente al actual
            if self.status_id == status_id:
                return True
                
            # Si el estado es "Renovado", validar que la fecha sea posterior a la actual
            if self._get_status_name_by_id(status_id) == "Renovado" and self.expiration_date <= date.today():
                print("La fecha de vencimiento debe ser posterior a la fecha actual para cambiar a estado Renovado")
                return False
                
            # Obtener nombre del estado anterior y nuevo
            old_status = self._get_status_name_by_id(self.status_id)
            new_status = self._get_status_name_by_id(status_id)
            
            # Actualizar estado
            self.status_id = status_id
            
            # Registrar el cambio en el historial
            self._add_history_record(
                "Cambio de estado", 
                f"Estado cambiado de '{old_status}' a '{new_status}'", 
                notes,
                user_id
            )
            
            # Guardar cambios
            return self.save()
        except Exception as e:
            print(f"Error al cambiar estado: {e}")
            return False
    
    def _add_history_record(self, action_type: str, description: str, notes: str = "", user_id: int = None) -> bool:
        """
        Agrega un registro al historial de cambios
        
        Args:
            action_type: Tipo de acción (Creación, Modificación, etc.)
            description: Descripción del cambio
            notes: Notas adicionales
            user_id: ID del usuario que realizó el cambio
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        try:
            # Validar que el ID del vencimiento exista
            if not self.id:
                print("Error: No se puede registrar historial sin ID de vencimiento")
                return False
                
            # Corregir la ruta de importación para DBManager
            from app.core.database.db_manager import DBManager 
            
            # Obtener conexión a la base de datos
            db = DBManager().get_connection()
            cursor = db.cursor()
            
            # Preparar los valores para la consulta
            # MariaDB/MySQL usa %s como marcador de posición, no ?
            query = """
                INSERT INTO expiration_history 
                (expiration_id, action_type, description, notes, user_id, created_at) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # Mostrar la consulta y los parámetros para depuración
            print(f"Ejecutando consulta: {query}")
            print(f"Parámetros: ID={self.id}, Acción={action_type}, Desc={description}, Notas={notes}, User={user_id}")
            
            # Ejecutar la consulta
            cursor.execute(query, (self.id, action_type, description, notes, user_id))
            db.commit()
            
            print(f"Registro de historial agregado correctamente para el vencimiento {self.id}")
            return True
        except Exception as e:
            print(f"Error al agregar registro al historial: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_responsible(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos del responsable"""
        if not self.responsible_id:
            return None
            
        query = "SELECT id, username, email, full_name, department, phone FROM users WHERE id = ?"
        result = self.db.execute_query(query, (self.responsible_id,))
        
        if result:
            return result[0]
        return None
    
    def get_priority(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de la prioridad"""
        if not self.priority_id:
            return None
            
        query = "SELECT * FROM priorities WHERE id = ?"
        result = self.db.execute_query(query, (self.priority_id,))
        
        if result:
            return result[0]
        return None
    
    def get_sector(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos del sector"""
        if not self.sector_id:
            return None
            
        query = "SELECT * FROM sectors WHERE id = ?"
        result = self.db.execute_query(query, (self.sector_id,))
        
        if result:
            return result[0]
        return None
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos del estado"""
        if not self.status_id:
            return None
            
        query = "SELECT * FROM expiration_statuses WHERE id = ?"
        result = self.db.execute_query(query, (self.status_id,))
        
        if result:
            return result[0]
        return None
    
    def get_status_name(self) -> str:
        """Obtiene el nombre del estado"""
        status = self.get_status()
        if status:
            return status['name']
        return "Desconocido"
    
    def get_days_until_expiration(self) -> int:
        """Calcula los días restantes hasta el vencimiento"""
        today = date.today()
        delta = self.expiration_date - today
        return delta.days
    
    def is_expired(self) -> bool:
        """Verifica si el vencimiento ya pasó"""
        return self.get_days_until_expiration() < 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el vencimiento a un diccionario"""
        return {
            'id': self.id,
            'expiration_date': self.expiration_date,
            'concept': self.concept,
            'responsible_id': self.responsible_id,
            'priority_id': self.priority_id,
            'sector_id': self.sector_id,
            'status_id': self.status_id,
            'notes': self.notes,
            'created_by': self.created_by,
            'days_until': self.get_days_until_expiration(),
            'is_expired': self.is_expired(),
            'responsible': self.get_responsible(),
            'priority': self.get_priority(),
            'sector': self.get_sector(),
            'status': self.get_status()
        }
    
    @classmethod
    def get_by_id(cls, expiration_id: int) -> Optional['Expiration']:
        """Obtiene un vencimiento por su ID"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM expirations WHERE id = ?", (expiration_id,))
        
        if result:
            data = result[0]
            return cls(
                id=data['id'],
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data['status_id'],
                notes=data['notes'],
                created_by=data['created_by']
            )
        
        return None
    
    @classmethod
    def get_all(cls, limit: int = 100, offset: int = 0) -> List['Expiration']:
        """Obtiene todos los vencimientos con paginación"""
        db = DatabaseConnection()
        results = db.execute_query(
            "SELECT * FROM expirations ORDER BY expiration_date LIMIT ? OFFSET ?",
            (limit, offset)
        )
        
        expirations = []
        for data in results:
            exp = cls(
                id=data['id'],
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data['status_id'],
                notes=data['notes'],
                created_by=data['created_by']
            )
            expirations.append(exp)
        
        return expirations
    
    @classmethod
    def get_upcoming(cls, days: int = 30, limit: int = 100) -> List['Expiration']:
        """Obtiene los vencimientos próximos en los siguientes días"""
        db = DatabaseConnection()
        today = date.today()
        max_date = today + timedelta(days=days)
        
        results = db.execute_query(
            """
            SELECT * FROM expirations 
            WHERE expiration_date BETWEEN ? AND ?
            AND status_id IN (SELECT id FROM expiration_statuses WHERE name != 'Renovado')
            ORDER BY expiration_date
            LIMIT ?
            """,
            (today, max_date, limit)
        )
        
        expirations = []
        for data in results:
            exp = cls(
                id=data['id'],
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data['status_id'],
                notes=data['notes'],
                created_by=data['created_by']
            )
            expirations.append(exp)
        
        return expirations
    
    @classmethod
    def get_expired(cls, limit: int = 100) -> List['Expiration']:
        """Obtiene los vencimientos que ya pasaron"""
        db = DatabaseConnection()
        today = date.today()
        
        results = db.execute_query(
            """
            SELECT * FROM expirations 
            WHERE expiration_date < ?
            AND status_id IN (SELECT id FROM expiration_statuses WHERE name != 'Renovado')
            ORDER BY expiration_date DESC
            LIMIT ?
            """,
            (today, limit)
        )
        
        expirations = []
        for data in results:
            exp = cls(
                id=data['id'],
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data['status_id'],
                notes=data['notes'],
                created_by=data['created_by']
            )
            expirations.append(exp)
        
        return expirations
    
    @classmethod
    def search(cls, search_text: str = None, responsible_id: int = None, 
              priority_id: int = None, sector_id: int = None, status_id: int = None,
              start_date: date = None, end_date: date = None, limit: int = 100) -> List['Expiration']:
        """Busca vencimientos con diferentes criterios"""
        db = DatabaseConnection()
        
        # Construir consulta base
        query = "SELECT * FROM expirations WHERE 1=1"
        params = []
        
        # Agregar condiciones según los parámetros
        if search_text:
            query += " AND (concept LIKE %s OR notes LIKE %s)"
            params.extend([f'%{search_text}%', f'%{search_text}%'])
            
        if responsible_id:
            query += " AND responsible_id = %s"
            params.append(responsible_id)
            
        if priority_id:
            query += " AND priority_id = %s"
            params.append(priority_id)
            
        if sector_id:
            query += " AND sector_id = %s"
            params.append(sector_id)
            
        if status_id:
            query += " AND status_id = %s"
            params.append(status_id)
            
        if start_date:
            query += " AND expiration_date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND expiration_date <= %s"
            params.append(end_date)
            
        # Agregar límite
        query += " ORDER BY expiration_date LIMIT %s"
        params.append(limit)
        
        # Ejecutar consulta
        results = db.execute_query(query, tuple(params))
        
        expirations = []
        for data in results:
            exp = cls(
                id=data['id'],
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data['status_id'],
                notes=data['notes'],
                created_by=data['created_by']
            )
            expirations.append(exp)
        
        return expirations
    
    @classmethod
    def count_by_status(cls) -> List[Tuple[str, int, str]]:
        """Cuenta los vencimientos agrupados por estado"""
        db = DatabaseConnection()
        
        query = """
        SELECT s.name, COUNT(e.id) as count, s.color
        FROM expiration_statuses s
        LEFT JOIN expirations e ON s.id = e.status_id
        GROUP BY s.id
        ORDER BY count DESC
        """
        
        results = db.execute_query(query)
        return [(row['name'], row['count'], row['color']) for row in results]
    
    @classmethod
    def count_by_priority(cls) -> List[Tuple[str, int, str]]:
        """Cuenta los vencimientos agrupados por prioridad"""
        db = DatabaseConnection()
        
        query = """
        SELECT p.name, COUNT(e.id) as count, p.color
        FROM priorities p
        LEFT JOIN expirations e ON p.id = e.priority_id
        GROUP BY p.id
        ORDER BY count DESC
        """
        
        results = db.execute_query(query)
        return [(row['name'], row['count'], row['color']) for row in results]
    
    @classmethod
    def count_by_sector(cls) -> List[Tuple[str, int]]:
        """Cuenta los vencimientos agrupados por sector"""
        db = DatabaseConnection()
        
        query = """
        SELECT s.name, COUNT(e.id) as count
        FROM sectors s
        LEFT JOIN expirations e ON s.id = e.sector_id
        GROUP BY s.id
        ORDER BY count DESC
        """
        
        results = db.execute_query(query)
        return [(row['name'], row['count']) for row in results]
    
    @classmethod
    def count_by_responsible(cls, limit: int = 10) -> List[Tuple[str, int]]:
        """Cuenta los vencimientos agrupados por responsable"""
        db = DatabaseConnection()
        
        query = """
        SELECT u.full_name, COUNT(e.id) as count
        FROM users u
        LEFT JOIN expirations e ON u.id = e.responsible_id
        GROUP BY u.id
        ORDER BY count DESC
        LIMIT ?
        """
        
        results = db.execute_query(query, (limit,))
        return [(row['full_name'], row['count']) for row in results]

    def _get_status_id_by_name(self, status_name: str) -> Optional[int]:
        """
        Obtiene el ID de un estado a partir de su nombre
        
        Args:
            status_name: Nombre del estado
            
        Returns:
            ID del estado o None si no se encuentra
        """
        try:
            query = "SELECT id FROM expiration_statuses WHERE name = ?"
            result = self.db.execute_query(query, (status_name,))
            
            if result:
                return result[0]['id']
            return None
        except Exception as e:
            print(f"Error al obtener ID de estado: {e}")
            return None
    
    def _get_status_name_by_id(self, status_id: int) -> Optional[str]:
        """
        Obtiene el nombre de un estado a partir de su ID
        
        Args:
            status_id: ID del estado
            
        Returns:
            Nombre del estado o None si no se encuentra
        """
        try:
            if not status_id:
                return "No asignado"
                
            query = "SELECT name FROM expiration_statuses WHERE id = %s"
            result = self.db.execute_query(query, (status_id,))
            
            if result:
                return result[0]['name']
            return "Desconocido"
        except Exception as e:
            print(f"Error al obtener nombre de estado: {e}")
            return "Error"
            
    def _get_responsible_name_by_id(self, responsible_id: int) -> str:
        """
        Obtiene el nombre del responsable a partir de su ID
        
        Args:
            responsible_id: ID del responsable
            
        Returns:
            Nombre del responsable o un valor por defecto si no se encuentra
        """
        try:
            if not responsible_id:
                return "No asignado"
                
            query = "SELECT full_name FROM users WHERE id = %s"
            result = self.db.execute_query(query, (responsible_id,))
            
            if result:
                return result[0]['full_name']
            return "Desconocido"
        except Exception as e:
            print(f"Error al obtener nombre de responsable: {e}")
            return "Error"
            
    def _get_priority_name_by_id(self, priority_id: int) -> str:
        """
        Obtiene el nombre de una prioridad a partir de su ID
        
        Args:
            priority_id: ID de la prioridad
            
        Returns:
            Nombre de la prioridad o un valor por defecto si no se encuentra
        """
        try:
            if not priority_id:
                return "No asignada"
                
            query = "SELECT name FROM priorities WHERE id = %s"
            result = self.db.execute_query(query, (priority_id,))
            
            if result:
                return result[0]['name']
            return "Desconocida"
        except Exception as e:
            print(f"Error al obtener nombre de prioridad: {e}")
            return "Error"
            
    def _get_sector_name_by_id(self, sector_id: int) -> str:
        """
        Obtiene el nombre de un sector a partir de su ID
        
        Args:
            sector_id: ID del sector
            
        Returns:
            Nombre del sector o un valor por defecto si no se encuentra
        """
        try:
            if not sector_id:
                return "No asignado"
                
            query = "SELECT name FROM sectors WHERE id = %s"
            result = self.db.execute_query(query, (sector_id,))
            
            if result:
                return result[0]['name']
            return "Desconocido"
        except Exception as e:
            print(f"Error al obtener nombre de sector: {e}")
            return "Error"
