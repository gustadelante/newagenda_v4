"""
Helper module that adds history loading capability to ExpirationForm
"""

from datetime import datetime

def load_history_records(self):
    """Carga el historial de cambios desde la base de datos"""
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
