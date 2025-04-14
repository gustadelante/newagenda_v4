import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import date

from ..models.alert import Alert
from ..models.expiration import Expiration
from ..models.user import User


class NotificationService:
    """Servicio para el envío de notificaciones por diferentes canales"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa el servicio de notificaciones
        
        Args:
            config_file: Ruta al archivo de configuración JSON de los servicios de notificación
        """
        if self._initialized:
            return
            
        # Cargar configuración
        self.config = self._load_config(config_file)
        self._initialized = True
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Carga la configuración desde un archivo JSON"""
        default_config = {
            "email": {
                "server": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "username": "",
                "password": "",
                "from_name": "Sistema de Vencimientos",
                "from_email": ""
            },
            "push": {
                "enabled": False,
                "service": "firebase",
                "api_key": ""
            },
            "desktop": {
                "enabled": True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Combinar con la configuración por defecto
                    self._merge_config(default_config, loaded_config)
            except Exception as e:
                print(f"Error al cargar la configuración: {e}")
        
        return default_config
    
    def _merge_config(self, default_config: Dict[str, Any], loaded_config: Dict[str, Any]):
        """Combina la configuración cargada con la configuración por defecto"""
        for key, value in loaded_config.items():
            if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                self._merge_config(default_config[key], value)
            else:
                default_config[key] = value
    
    def save_config(self, config_file: str):
        """Guarda la configuración en un archivo JSON"""
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")
            return False
    
    def send_notification(self, alert: Alert) -> bool:
        """
        Envía una notificación para una alerta
        
        Args:
            alert: Alerta a procesar
            
        Returns:
            bool: True si al menos una notificación fue enviada con éxito
        """
        success = False
        expiration = alert.get_expiration()
        
        if not expiration:
            return False
        
        # Enviar alertas según la configuración
        if alert.email_alert:
            success = self.send_email_notification(alert, expiration) or success
            
        if alert.push_alert:
            success = self.send_push_notification(alert, expiration) or success
            
        if alert.desktop_alert:
            success = self.send_desktop_notification(alert, expiration) or success
        
        return success
    
    def send_email_notification(self, alert: Alert, expiration: Expiration) -> bool:
        """
        Envía una notificación por correo electrónico
        
        Args:
            alert: La alerta a enviar
            expiration: El vencimiento asociado
            
        Returns:
            bool: True si el correo se envió correctamente
        """
        try:
            # Verificar configuración
            email_config = self.config.get("email", {})
            if not email_config.get("username") or not email_config.get("password"):
                print("Configuración de correo electrónico incompleta")
                alert.log_alert_sent("email", "failed", "Configuración de correo electrónico incompleta")
                return False
            
            # Obtener datos del responsable
            responsible = User.get_by_id(expiration.responsible_id)
            if not responsible or not responsible.email:
                print(f"No se encontró el correo electrónico del responsable: {expiration.responsible_id}")
                alert.log_alert_sent("email", "failed", "No se encontró el correo electrónico del responsable")
                return False
            
            # Crear mensaje
            msg = MIMEMultipart()
            
            # Encabezados
            from_name = email_config.get("from_name", "Sistema de Vencimientos")
            from_email = email_config.get("from_email", email_config.get("username"))
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = responsible.email
            
            # Determinar el asunto basado en los días restantes
            days_until = expiration.get_days_until_expiration()
            if days_until < 0:
                msg['Subject'] = f"VENCIDO: {expiration.concept}"
            else:
                msg['Subject'] = f"Recordatorio: {expiration.concept} vence en {days_until} días"
            
            # Construir el cuerpo del mensaje
            priority = expiration.get_priority()
            sector = expiration.get_sector()
            status = expiration.get_status()
            
            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ padding: 20px; }}
                    .header {{ font-size: 24px; margin-bottom: 20px; color: #333; }}
                    .info {{ margin-bottom: 10px; }}
                    .label {{ font-weight: bold; }}
                    .priority {{ font-weight: bold; color: {priority['color'] if priority else '#000'}; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">Recordatorio de Vencimiento</div>
                    
                    <div class="info">
                        <span class="label">Concepto:</span> {expiration.concept}
                    </div>
                    
                    <div class="info">
                        <span class="label">Fecha de vencimiento:</span> {expiration.expiration_date.strftime('%d/%m/%Y')}
                    </div>
                    
                    <div class="info">
                        <span class="label">Días restantes:</span> {days_until}
                    </div>
                    
                    <div class="info">
                        <span class="label">Prioridad:</span> 
                        <span class="priority">{priority['name'] if priority else 'No especificada'}</span>
                    </div>
                    
                    <div class="info">
                        <span class="label">Sector:</span> {sector['name'] if sector else 'No especificado'}
                    </div>
                    
                    <div class="info">
                        <span class="label">Estado:</span> {status['name'] if status else 'No especificado'}
                    </div>
                    
                    <div class="footer">
                        Este es un mensaje automático del Sistema de Gestión de Vencimientos.
                        Por favor, no responda a este correo.
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Conectar al servidor SMTP y enviar
            with smtplib.SMTP(email_config.get("server", "smtp.gmail.com"), email_config.get("port", 587)) as server:
                if email_config.get("use_tls", True):
                    server.starttls()
                
                server.login(email_config.get("username"), email_config.get("password"))
                server.send_message(msg)
            
            # Registrar alerta enviada
            alert.log_alert_sent("email", "sent")
            return True
        except Exception as e:
            print(f"Error al enviar notificación por correo electrónico: {e}")
            alert.log_alert_sent("email", "failed", str(e))
            return False
    
    def send_push_notification(self, alert: Alert, expiration: Expiration) -> bool:
        """
        Envía una notificación push (implementación para múltiples plataformas)
        
        Args:
            alert: La alerta a enviar
            expiration: El vencimiento asociado
            
        Returns:
            bool: True si la notificación se envió correctamente
        """
        try:
            # Verificar configuración
            push_config = self.config.get("push", {})
            if not push_config.get("enabled"):
                print("Las notificaciones push están deshabilitadas")
                return False
            
            # Determinar el servicio a utilizar
            service = push_config.get("service", "firebase")
            
            if service == "firebase":
                return self._send_firebase_notification(alert, expiration, push_config)
            else:
                print(f"Servicio de notificaciones push no soportado: {service}")
                alert.log_alert_sent("push", "failed", f"Servicio no soportado: {service}")
                return False
        except Exception as e:
            print(f"Error al enviar notificación push: {e}")
            alert.log_alert_sent("push", "failed", str(e))
            return False
    
    def _send_firebase_notification(self, alert: Alert, expiration: Expiration, config: Dict[str, Any]) -> bool:
        """
        Envía una notificación mediante Firebase Cloud Messaging
        
        Nota: Esta es una implementación ficticia. Para una implementación real,
        se debería usar la API de Firebase y mantener un registro de tokens de dispositivos.
        """
        # En una implementación real, aquí se enviaría la notificación usando la API de Firebase
        # y se obtendría el token del dispositivo del usuario desde la base de datos
        
        # Simulamos que la notificación se envía correctamente
        alert.log_alert_sent("push", "sent")
        return True
    
    def send_desktop_notification(self, alert: Alert, expiration: Expiration) -> bool:
        """
        Registra una notificación de escritorio para ser mostrada cuando el usuario inicie sesión
        
        Args:
            alert: La alerta a enviar
            expiration: El vencimiento asociado
            
        Returns:
            bool: True si la notificación se registró correctamente
        """
        # En una implementación real, aquí se registraría la notificación en la base de datos
        # para ser mostrada al usuario cuando inicie sesión en la aplicación de escritorio
        
        # Registrar alerta enviada
        alert.log_alert_sent("desktop", "sent")
        return True
    
    def process_due_alerts(self) -> int:
        """
        Procesa todas las alertas que deben enviarse hoy
        
        Returns:
            int: Número de alertas procesadas exitosamente
        """
        alerts = Alert.get_due_alerts()
        successful_alerts = 0
        
        for alert in alerts:
            if self.send_notification(alert):
                successful_alerts += 1
        
        return successful_alerts
