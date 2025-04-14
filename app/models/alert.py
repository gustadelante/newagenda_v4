from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from ..database.connection import DatabaseConnection
from .expiration import Expiration


class Alert:
    """Modelo para representar una alerta de vencimiento en el sistema"""
    
    def __init__(self, id: Optional[int] = None, expiration_id: int = None,
                 days_before: int = 30, alert_count: int = 0, max_alerts: int = 3,
                 email_alert: bool = True, push_alert: bool = True, 
                 desktop_alert: bool = True, is_active: bool = True):
        self.id = id
        self.expiration_id = expiration_id
        self.days_before = days_before
        self.alert_count = alert_count
        self.max_alerts = max_alerts
        self.email_alert = email_alert
        self.push_alert = push_alert
        self.desktop_alert = desktop_alert
        self.is_active = is_active
        self.db = DatabaseConnection()
        
        # Propiedades calculadas
        self._expiration = None
    
    def save(self) -> bool:
        """Guarda la alerta en la base de datos"""
        try:
            if self.id:
                # Actualizar alerta existente
                query = """
                UPDATE alerts SET
                    days_before = ?,
                    max_alerts = ?,
                    email_alert = ?,
                    push_alert = ?,
                    desktop_alert = ?,
                    is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """
                params = (
                    self.days_before, self.max_alerts, self.email_alert,
                    self.push_alert, self.desktop_alert, self.is_active, self.id
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
            else:
                # Crear nueva alerta
                query = """
                INSERT INTO alerts (
                    expiration_id, days_before, alert_count, max_alerts,
                    email_alert, push_alert, desktop_alert, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.expiration_id, self.days_before, self.alert_count, self.max_alerts,
                    self.email_alert, self.push_alert, self.desktop_alert, self.is_active
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
                # Obtener el ID generado
                result = self.db.execute_query(
                    "SELECT LAST_INSERT_ID() as id"
                )
                if result:
                    self.id = result[0]['id']
            
            return True
        except Exception as e:
            print(f"Error al guardar alerta: {e}")
            return False
    
    def delete(self) -> bool:
        """Elimina la alerta de la base de datos"""
        try:
            if self.id:
                query = "DELETE FROM alerts WHERE id = ?"
                self.db.execute_query(query, (self.id,), fetch=False, commit=True)
                self.id = None
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar alerta: {e}")
            return False
    
    def get_expiration(self) -> Optional[Expiration]:
        """Obtiene el vencimiento asociado a esta alerta"""
        if not self.expiration_id:
            return None
            
        if self._expiration is None:
            self._expiration = Expiration.get_by_id(self.expiration_id)
            
        return self._expiration
    
    def increment_alert_count(self) -> bool:
        """Incrementa el contador de alertas enviadas"""
        if not self.id:
            return False
            
        try:
            self.alert_count += 1
            query = "UPDATE alerts SET alert_count = ? WHERE id = ?"
            self.db.execute_query(query, (self.alert_count, self.id), fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al incrementar contador de alertas: {e}")
            return False
    
    def can_send_more_alerts(self) -> bool:
        """Verifica si se pueden enviar más alertas"""
        return self.alert_count < self.max_alerts
    
    def log_alert_sent(self, alert_type: str, status: str = 'sent', error_message: str = None) -> bool:
        """Registra una alerta enviada en el historial"""
        if not self.id:
            return False
            
        try:
            query = """
            INSERT INTO alert_history (
                alert_id, alert_type, status, error_message
            ) VALUES (?, ?, ?, ?)
            """
            params = (self.id, alert_type, status, error_message)
            self.db.execute_query(query, params, fetch=False, commit=True)
            
            # Incrementar contador de alertas
            if status == 'sent':
                self.increment_alert_count()
                
            return True
        except Exception as e:
            print(f"Error al registrar alerta enviada: {e}")
            return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de alertas enviadas"""
        if not self.id:
            return []
            
        query = """
        SELECT * FROM alert_history
        WHERE alert_id = ?
        ORDER BY alert_date DESC
        """
        return self.db.execute_query(query, (self.id,))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la alerta a un diccionario"""
        return {
            'id': self.id,
            'expiration_id': self.expiration_id,
            'days_before': self.days_before,
            'alert_count': self.alert_count,
            'max_alerts': self.max_alerts,
            'email_alert': self.email_alert,
            'push_alert': self.push_alert,
            'desktop_alert': self.desktop_alert,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_by_id(cls, alert_id: int) -> Optional['Alert']:
        """Obtiene una alerta por su ID"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        
        if result:
            data = result[0]
            return cls(
                id=data['id'],
                expiration_id=data['expiration_id'],
                days_before=data['days_before'],
                alert_count=data['alert_count'],
                max_alerts=data['max_alerts'],
                email_alert=data['email_alert'],
                push_alert=data['push_alert'],
                desktop_alert=data['desktop_alert'],
                is_active=data['is_active']
            )
        
        return None
    
    @classmethod
    def get_by_expiration(cls, expiration_id: int) -> List['Alert']:
        """Obtiene todas las alertas para un vencimiento específico"""
        db = DatabaseConnection()
        results = db.execute_query(
            "SELECT * FROM alerts WHERE expiration_id = ?",
            (expiration_id,)
        )
        
        alerts = []
        for data in results:
            alert = cls(
                id=data['id'],
                expiration_id=data['expiration_id'],
                days_before=data['days_before'],
                alert_count=data['alert_count'],
                max_alerts=data['max_alerts'],
                email_alert=data['email_alert'],
                push_alert=data['push_alert'],
                desktop_alert=data['desktop_alert'],
                is_active=data['is_active']
            )
            alerts.append(alert)
        
        return alerts
    
    @classmethod
    def get_due_alerts(cls) -> List['Alert']:
        """Obtiene las alertas que deben enviarse hoy"""
        db = DatabaseConnection()
        today = date.today()
        
        query = """
        SELECT a.* 
        FROM alerts a
        JOIN expirations e ON a.expiration_id = e.id
        WHERE a.is_active = TRUE 
        AND a.alert_count < a.max_alerts
        AND e.status_id IN (SELECT id FROM expiration_statuses WHERE name != 'Renovado')
        AND DATEDIFF(e.expiration_date, ?) = a.days_before
        """
        
        results = db.execute_query(query, (today,))
        
        alerts = []
        for data in results:
            alert = cls(
                id=data['id'],
                expiration_id=data['expiration_id'],
                days_before=data['days_before'],
                alert_count=data['alert_count'],
                max_alerts=data['max_alerts'],
                email_alert=data['email_alert'],
                push_alert=data['push_alert'],
                desktop_alert=data['desktop_alert'],
                is_active=data['is_active']
            )
            alerts.append(alert)
        
        return alerts
