from typing import Optional, Dict, Any, Tuple
import json
import os
from ..models.user import User

class AuthController:
    """Controlador para manejar la autenticación y autorización de usuarios"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(AuthController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, session_file: Optional[str] = None):
        """
        Inicializa el controlador de autenticación
        
        Args:
            session_file: Ruta al archivo para almacenar la sesión (credentials)
        """
        if self._initialized:
            return
            
        # Configuración
        self._session_file = session_file or os.path.join(
            os.path.expanduser("~"), ".newagenda", "session.json"
        )
        self._current_user = None
        self._remember_credentials = False
        self._credentials = None
        
        # Cargar credenciales guardadas
        self._load_saved_credentials()
        
        self._initialized = True
    
    def _load_saved_credentials(self) -> bool:
        """Carga las credenciales guardadas si existen"""
        try:
            if os.path.exists(self._session_file):
                with open(self._session_file, 'r', encoding='utf-8') as f:
                    self._credentials = json.load(f)
                    self._remember_credentials = True
                return True
            return False
        except Exception as e:
            print(f"Error al cargar credenciales: {e}")
            return False
    
    def _save_credentials(self, username: str, password: str) -> bool:
        """Guarda las credenciales en el archivo de sesión"""
        try:
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(self._session_file), exist_ok=True)
            
            # Guardar credenciales
            with open(self._session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "username": username,
                    "password": password
                }, f)
            return True
        except Exception as e:
            print(f"Error al guardar credenciales: {e}")
            return False
    
    def _delete_saved_credentials(self) -> bool:
        """Elimina las credenciales guardadas"""
        try:
            if os.path.exists(self._session_file):
                os.remove(self._session_file)
            return True
        except Exception as e:
            print(f"Error al eliminar credenciales: {e}")
            return False
    
    def login(self, username: str, password: str, remember: bool = False) -> Tuple[bool, str]:
        """
        Inicia sesión con los datos proporcionados
        
        Args:
            username: Nombre de usuario o correo electrónico
            password: Contraseña
            remember: Si es True, guarda las credenciales para inicios de sesión futuros
            
        Returns:
            Tuple con éxito (bool) y mensaje de error si hubo fallo
        """
        try:
            user = User.authenticate(username, password)
            
            if user:
                self._current_user = user
                self._remember_credentials = remember
                
                # Guardar o eliminar credenciales según la opción remember
                if remember:
                    self._save_credentials(username, password)
                else:
                    self._delete_saved_credentials()
                
                return True, ""
            else:
                return False, "Credenciales inválidas. Por favor verifica tu usuario y contraseña."
        except Exception as e:
            return False, f"Error al iniciar sesión: {e}"
    
    def try_auto_login(self) -> bool:
        """
        Intenta iniciar sesión automáticamente con las credenciales guardadas
        
        Returns:
            bool: True si el inicio de sesión fue exitoso
        """
        if self._credentials:
            success, _ = self.login(
                self._credentials.get("username", ""),
                self._credentials.get("password", ""),
                True  # Mantener las credenciales guardadas
            )
            return success
        return False
    
    def logout(self) -> bool:
        """
        Cierra la sesión del usuario actual
        
        Returns:
            bool: True si el cierre de sesión fue exitoso
        """
        self._current_user = None
        
        # Mantener o eliminar las credenciales según la configuración
        if not self._remember_credentials:
            self._delete_saved_credentials()
            
        return True
    
    def is_authenticated(self) -> bool:
        """
        Verifica si hay un usuario autenticado
        
        Returns:
            bool: True si hay un usuario autenticado
        """
        return self._current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """
        Obtiene el usuario actualmente autenticado
        
        Returns:
            User: El usuario actual o None si no hay sesión
        """
        return self._current_user
    
    def check_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico
        
        Args:
            permission: El permiso a verificar
            
        Returns:
            bool: True si el usuario tiene el permiso
        """
        if not self._current_user:
            return False
            
        # En este sistema simple, usamos roles como permisos
        # Para un sistema más complejo, se debería implementar un sistema de permisos más granular
        return self._current_user.has_role(permission)
    
    def is_admin(self) -> bool:
        """
        Verifica si el usuario actual es administrador
        
        Returns:
            bool: True si el usuario es administrador
        """
        if not self._current_user:
            return False
            
        return self._current_user.has_role('admin')
    
    def update_remember_credentials(self, remember: bool) -> bool:
        """
        Actualiza la configuración de recordar credenciales
        
        Args:
            remember: Si es True, guarda las credenciales para inicios de sesión futuros
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        self._remember_credentials = remember
        
        # Actualizar preferencias del usuario
        if self._current_user:
            prefs = self._current_user.get_preferences()
            prefs['remember_credentials'] = remember
            self._current_user.update_preferences(prefs)
            
            # Guardar o eliminar credenciales según la nueva configuración
            if remember and self._credentials:
                return self._save_credentials(
                    self._credentials.get("username", ""),
                    self._credentials.get("password", "")
                )
            elif not remember:
                return self._delete_saved_credentials()
        
        return True
