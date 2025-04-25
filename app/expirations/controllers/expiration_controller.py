from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
from app.expirations.models.expiration import Expiration
from app.expirations.models.alert import Alert
from app.notifications.services.notification_service import NotificationService


class ExpirationController:
    """Controlador para gestionar los vencimientos en el sistema"""
    
    def __init__(self):
        """Inicializa el controlador de vencimientos"""
        self.notification_service = NotificationService()
    
    def create_expiration(self, data: Dict[str, Any]) -> Tuple[bool, Optional[int], str]:
        """
        Crea un nuevo vencimiento
        
        Args:
            data: Diccionario con los datos del vencimiento
            
        Returns:
            Tuple con éxito (bool), ID del vencimiento creado y mensaje de error si hubo fallo
        """
        try:
            # Validar datos obligatorios
            required_fields = ['expiration_date', 'concept', 'responsible_id', 
                              'priority_id', 'sector_id', 'created_by']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return False, None, f"El campo '{field}' es obligatorio"
            
            # Convertir fecha si es string
            if isinstance(data['expiration_date'], str):
                try:
                    data['expiration_date'] = datetime.strptime(
                        data['expiration_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    return False, None, "Formato de fecha inválido. Use YYYY-MM-DD"
            
            # Crear el vencimiento
            expiration = Expiration(
                expiration_date=data['expiration_date'],
                concept=data['concept'],
                responsible_id=data['responsible_id'],
                priority_id=data['priority_id'],
                sector_id=data['sector_id'],
                status_id=data.get('status_id', 1),  # Por defecto, estado "Pendiente"
                notes=data.get('notes', ''),
                created_by=data['created_by']
            )
            
            if expiration.save():
                return True, expiration.id, ""
            else:
                return False, None, "Error al guardar el vencimiento"
        except Exception as e:
            return False, None, f"Error al crear vencimiento: {e}"
    
    def update_expiration(self, expiration_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Actualiza un vencimiento existente
        
        Args:
            expiration_id: ID del vencimiento a actualizar
            data: Diccionario con los datos a actualizar
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            # Obtener el vencimiento
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, "Vencimiento no encontrado"
            
            # Actualizar campos si están presentes en los datos
            if 'expiration_date' in data:
                if isinstance(data['expiration_date'], str):
                    try:
                        expiration.expiration_date = datetime.strptime(
                            data['expiration_date'], '%Y-%m-%d'
                        ).date()
                    except ValueError:
                        return False, "Formato de fecha inválido. Use YYYY-MM-DD"
                else:
                    expiration.expiration_date = data['expiration_date']
            
            if 'concept' in data:
                expiration.concept = data['concept']
                
            if 'responsible_id' in data:
                expiration.responsible_id = data['responsible_id']
                
            if 'priority_id' in data:
                expiration.priority_id = data['priority_id']
                
            if 'sector_id' in data:
                expiration.sector_id = data['sector_id']
                
            if 'status_id' in data:
                expiration.status_id = data['status_id']
                
            if 'notes' in data:
                expiration.notes = data['notes']
            
            # Obtener el ID del usuario que realiza la actualización
            user_id = data.get('created_by', None)
            
            # Guardar cambios
            if expiration.save(user_id):
                return True, ""
            else:
                return False, "Error al guardar los cambios"
        except Exception as e:
            return False, f"Error al actualizar vencimiento: {e}"
    
    def delete_expiration(self, expiration_id: int) -> Tuple[bool, str]:
        """
        Elimina un vencimiento
        
        Args:
            expiration_id: ID del vencimiento a eliminar
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, "Vencimiento no encontrado"
                
            if expiration.delete():
                return True, ""
            else:
                return False, "Error al eliminar el vencimiento"
        except Exception as e:
            return False, f"Error al eliminar vencimiento: {e}"
    
    def renew_expiration(self, expiration_id: int, new_date: date, user_id: int, notes: str = "") -> Tuple[bool, Optional[int], str]:
        """
        Renueva un vencimiento, actualizando la fecha de vencimiento
        
        Args:
            expiration_id: ID del vencimiento a renovar
            new_date: Nueva fecha de vencimiento
            user_id: ID del usuario que realiza la renovación
            notes: Notas sobre la renovación
            
        Returns:
            Tuple con éxito (bool), ID del vencimiento renovado y mensaje de error si hubo fallo
        """
        try:
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, None, "Vencimiento no encontrado"
        
            # Validar que la fecha de renovación sea posterior a la fecha actual
            if new_date <= date.today():
                return False, None, f"La fecha de renovación debe ser posterior a la fecha actual del sistema ({date.today().strftime('%d/%m/%Y')})"
                
            if expiration.renew(new_date, notes, user_id):
                # Devolver el mismo ID ya que solo se actualizó el registro
                return True, expiration_id, ""
            else:
                return False, None, "Error al renovar el vencimiento"
        except Exception as e:
            return False, None, f"Error al renovar vencimiento: {e}"
    
    def change_expiration_status(self, expiration_id: int, status_id: int, user_id: int, notes: str = "") -> Tuple[bool, str]:
        """
        Cambia el estado de un vencimiento
        
        Args:
            expiration_id: ID del vencimiento
            status_id: ID del nuevo estado
            user_id: ID del usuario que realiza el cambio
            notes: Notas sobre el cambio de estado
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, "Vencimiento no encontrado"
                
            if expiration.change_status(status_id, notes, user_id):
                return True, ""
            else:
                return False, "Error al cambiar el estado del vencimiento"
        except Exception as e:
            return False, f"Error al cambiar estado: {e}"
    
    def get_expiration(self, expiration_id: int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Obtiene un vencimiento por su ID
        
        Args:
            expiration_id: ID del vencimiento
            
        Returns:
            Tuple con éxito (bool), datos del vencimiento y mensaje de error si hubo fallo
        """
        try:
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, None, "Vencimiento no encontrado"
                
            return True, expiration.to_dict(), ""
        except Exception as e:
            return False, None, f"Error al obtener vencimiento: {e}"
    
    def get_all_expirations(self, limit: int = 100, offset: int = 0) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Obtiene todos los vencimientos con paginación
        
        Args:
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            Tuple con éxito (bool), lista de vencimientos y mensaje de error si hubo fallo
        """
        try:
            expirations = Expiration.get_all(limit, offset)
            return True, [exp.to_dict() for exp in expirations], ""
        except Exception as e:
            return False, [], f"Error al obtener vencimientos: {e}"
    
    def get_upcoming_expirations(self, days: int = 30, limit: int = 100) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Obtiene los vencimientos próximos en los siguientes días
        
        Args:
            days: Días a considerar
            limit: Límite de resultados
            
        Returns:
            Tuple con éxito (bool), lista de vencimientos y mensaje de error si hubo fallo
        """
        try:
            expirations = Expiration.get_upcoming(days, limit)
            return True, [exp.to_dict() for exp in expirations], ""
        except Exception as e:
            return False, [], f"Error al obtener vencimientos próximos: {e}"
    
    def get_expired(self, limit: int = 100) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Obtiene los vencimientos que ya pasaron
        
        Args:
            limit: Límite de resultados
            
        Returns:
            Tuple con éxito (bool), lista de vencimientos y mensaje de error si hubo fallo
        """
        try:
            expirations = Expiration.get_expired(limit)
            return True, [exp.to_dict() for exp in expirations], ""
        except Exception as e:
            return False, [], f"Error al obtener vencimientos vencidos: {e}"
    
    def search_expirations(self, search_params: Dict[str, Any], limit: int = 100) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Busca vencimientos con diferentes criterios
        
        Args:
            search_params: Parámetros de búsqueda
            limit: Límite de resultados
            
        Returns:
            Tuple con éxito (bool), lista de vencimientos y mensaje de error si hubo fallo
        """
        try:
            # Extraer parámetros de búsqueda
            search_text = search_params.get('search_text')
            responsible_id = search_params.get('responsible_id')
            priority_id = search_params.get('priority_id')
            sector_id = search_params.get('sector_id')
            status_id = search_params.get('status_id')
            start_date = search_params.get('start_date')
            end_date = search_params.get('end_date')
            
            # Convertir fechas si son strings
            if isinstance(start_date, str) and start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    return False, [], "Formato de fecha inicial inválido. Use YYYY-MM-DD"
                    
            if isinstance(end_date, str) and end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    return False, [], "Formato de fecha final inválido. Use YYYY-MM-DD"
            
            # Realizar búsqueda
            expirations = Expiration.search(
                search_text, responsible_id, priority_id, sector_id, 
                status_id, start_date, end_date, limit
            )
            
            return True, [exp.to_dict() for exp in expirations], ""
        except Exception as e:
            return False, [], f"Error al buscar vencimientos: {e}"
    
    def get_stats(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Obtiene estadísticas sobre los vencimientos
        
        Returns:
            Tuple con éxito (bool), estadísticas y mensaje de error si hubo fallo
        """
        try:
            stats = {
                'by_status': Expiration.count_by_status(),
                'by_priority': Expiration.count_by_priority(),
                'by_sector': Expiration.count_by_sector(),
                'by_responsible': Expiration.count_by_responsible(10)
            }
            
            return True, stats, ""
        except Exception as e:
            return False, {}, f"Error al obtener estadísticas: {e}"
    
    def create_alert(self, expiration_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[int], str]:
        """
        Crea una nueva alerta para un vencimiento
        
        Args:
            expiration_id: ID del vencimiento
            data: Datos de la alerta
            
        Returns:
            Tuple con éxito (bool), ID de la alerta creada y mensaje de error si hubo fallo
        """
        try:
            # Verificar que el vencimiento existe
            expiration = Expiration.get_by_id(expiration_id)
            if not expiration:
                return False, None, "Vencimiento no encontrado"
            
            # Validar datos obligatorios
            if 'days_before' not in data:
                return False, None, "El campo 'days_before' es obligatorio"
            
            # Crear la alerta
            alert = Alert(
                expiration_id=expiration_id,
                days_before=data['days_before'],
                max_alerts=data.get('max_alerts', 3),
                email_alert=data.get('email_alert', True),
                push_alert=data.get('push_alert', True),
                desktop_alert=data.get('desktop_alert', True),
                is_active=data.get('is_active', True)
            )
            
            if alert.save():
                return True, alert.id, ""
            else:
                return False, None, "Error al guardar la alerta"
        except Exception as e:
            return False, None, f"Error al crear alerta: {e}"
    
    def update_alert(self, alert_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Actualiza una alerta existente
        
        Args:
            alert_id: ID de la alerta
            data: Datos a actualizar
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            # Obtener la alerta
            alert = Alert.get_by_id(alert_id)
            if not alert:
                return False, "Alerta no encontrada"
            
            # Actualizar campos si están presentes en los datos
            if 'days_before' in data:
                alert.days_before = data['days_before']
                
            if 'max_alerts' in data:
                alert.max_alerts = data['max_alerts']
                
            if 'email_alert' in data:
                alert.email_alert = data['email_alert']
                
            if 'push_alert' in data:
                alert.push_alert = data['push_alert']
                
            if 'desktop_alert' in data:
                alert.desktop_alert = data['desktop_alert']
                
            if 'is_active' in data:
                alert.is_active = data['is_active']
            
            # Guardar cambios
            if alert.save():
                return True, ""
            else:
                return False, "Error al guardar los cambios"
        except Exception as e:
            return False, f"Error al actualizar alerta: {e}"
    
    def delete_alert(self, alert_id: int) -> Tuple[bool, str]:
        """
        Elimina una alerta
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            alert = Alert.get_by_id(alert_id)
            if not alert:
                return False, "Alerta no encontrada"
                
            if alert.delete():
                return True, ""
            else:
                return False, "Error al eliminar la alerta"
        except Exception as e:
            return False, f"Error al eliminar alerta: {e}"
    
    def get_alerts_by_expiration(self, expiration_id: int) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Obtiene todas las alertas para un vencimiento
        
        Args:
            expiration_id: ID del vencimiento
            
        Returns:
            Tuple con éxito (bool), lista de alertas y mensaje de error si hubo fallo
        """
        try:
            alerts = Alert.get_by_expiration(expiration_id)
            return True, [alert.to_dict() for alert in alerts], ""
        except Exception as e:
            return False, [], f"Error al obtener alertas: {e}"
    
    def get_expiration_history(self, expiration_id: int) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Obtiene el historial de cambios para un vencimiento
        
        Args:
            expiration_id: ID del vencimiento
            
        Returns:
            Tuple con éxito (bool), lista de registros históricos y mensaje de error si hubo fallo
        """
        try:
            expiration = Expiration(id=expiration_id)
            history = expiration.get_history()
            return True, history, ""
        except Exception as e:
            return False, [], f"Error al obtener historial: {e}"
    
    def process_due_alerts(self) -> Tuple[bool, int, str]:
        """
        Procesa todas las alertas que deben enviarse hoy
        
        Returns:
            Tuple con éxito (bool), número de alertas procesadas y mensaje de error si hubo fallo
        """
        try:
            count = self.notification_service.process_due_alerts()
            return True, count, ""
        except Exception as e:
            return False, 0, f"Error al procesar alertas: {e}"
