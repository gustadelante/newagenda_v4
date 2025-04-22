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
    
    def save(self) -> bool:
        """Guarda el vencimiento en la base de datos"""
        try:
            if self.id:
                # Actualizar vencimiento existente
                query = """
                UPDATE expirations SET
                    expiration_date = ?,
                    concept = ?,
                    responsible_id = ?,
                    priority_id = ?,
                    sector_id = ?,
                    status_id = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """
                params = (
                    self.expiration_date, self.concept, self.responsible_id,
                    self.priority_id, self.sector_id, self.status_id,
                    self.notes, self.id
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
            else:
                # Crear nuevo vencimiento
                query = """
                INSERT INTO expirations (
                    expiration_date, concept, responsible_id, priority_id,
                    sector_id, status_id, notes, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
        WHERE a.expiration_id = ?
        ORDER BY ah.alert_date DESC
        """
        return self.db.execute_query(query, (self.id,))
    
    def renew(self, new_expiration_date: date, notes: str = "") -> bool:
        """Renueva un vencimiento, marcándolo como renovado y creando uno nuevo"""
        if not self.id:
            return False
            
        try:
            # Iniciar transacción
            self.db.begin_transaction()
            
            # Marcar este vencimiento como renovado
            status_renovado = self.db.execute_query(
                "SELECT id FROM expiration_statuses WHERE name = 'Renovado'"
            )
            
            if status_renovado:
                status_id = status_renovado[0]['id']
                
                # Actualizar estado
                old_status = self.status_id
                self.status_id = status_id
                
                # Agregar nota de renovación
                if notes:
                    if self.notes:
                        self.notes += f"\n[{datetime.now().strftime('%Y-%m-%d')}] Renovado: {notes}"
                    else:
                        self.notes = f"[{datetime.now().strftime('%Y-%m-%d')}] Renovado: {notes}"
                
                # Guardar cambios
                self.save()
                
                # Crear nuevo vencimiento
                new_expiration = Expiration(
                    expiration_date=new_expiration_date,
                    concept=self.concept,
                    responsible_id=self.responsible_id,
                    priority_id=self.priority_id,
                    sector_id=self.sector_id,
                    status_id=old_status,  # Usar el estado original
                    notes=f"Continuación del vencimiento anterior (ID: {self.id})",
                    created_by=self.created_by
                )
                
                if new_expiration.save():
                    # Confirmar transacción
                    self.db.commit()
                    return True
                else:
                    # Revertir transacción
                    self.db.rollback()
                    return False
            else:
                self.db.rollback()
                return False
        except Exception as e:
            print(f"Error al renovar vencimiento: {e}")
            self.db.rollback()
            return False
    
    def change_status(self, new_status_id: int, notes: str = "") -> bool:
        """Cambia el estado del vencimiento"""
        if not self.id:
            return False
            
        try:
            old_status = self.status_id
            self.status_id = new_status_id
            
            # Agregar nota de cambio de estado
            if notes:
                status_name = self.get_status_name()
                if self.notes:
                    self.notes += f"\n[{datetime.now().strftime('%Y-%m-%d')}] Cambio a '{status_name}': {notes}"
                else:
                    self.notes = f"[{datetime.now().strftime('%Y-%m-%d')}] Cambio a '{status_name}': {notes}"
            
            return self.save()
        except Exception as e:
            print(f"Error al cambiar estado: {e}")
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
            query += " AND concept LIKE ?"
            params.append(f"%{search_text}%")
            
        if responsible_id is not None:
            query += " AND responsible_id = ?"
            params.append(responsible_id)
            
        if priority_id is not None:
            query += " AND priority_id = ?"
            params.append(priority_id)
            
        if sector_id is not None:
            query += " AND sector_id = ?"
            params.append(sector_id)
            
        if status_id is not None:
            query += " AND status_id = ?"
            params.append(status_id)
            
        if start_date:
            query += " AND expiration_date >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND expiration_date <= ?"
            params.append(end_date)
            
        # Agregar límite
        query += " ORDER BY expiration_date LIMIT ?"
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
