import bcrypt
from typing import List, Dict, Any, Optional
from ..database.connection import DatabaseConnection


class User:
    """Modelo para representar un usuario en el sistema"""
    
    def __init__(self, id: Optional[int] = None, username: str = "", password: str = "", 
                 email: str = "", full_name: str = "", department: str = "", phone: str = "",
                 is_active: bool = True):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.full_name = full_name
        self.department = department
        self.phone = phone
        self.is_active = is_active
        self.roles = []
        self.db = DatabaseConnection()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash para la contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña corresponde al hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def save(self) -> bool:
        """Guarda el usuario en la base de datos"""
        try:
            if self.id:
                # Actualizar usuario existente
                query = """
                UPDATE users SET
                    username = ?,
                    email = ?,
                    full_name = ?,
                    department = ?,
                    phone = ?,
                    is_active = ?
                WHERE id = ?
                """
                params = (
                    self.username, self.email, self.full_name,
                    self.department, self.phone, self.is_active, self.id
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
                # Si hay una nueva contraseña, actualizarla
                if self.password:
                    query = "UPDATE users SET password = ? WHERE id = ?"
                    params = (self.hash_password(self.password), self.id)
                    self.db.execute_query(query, params, fetch=False, commit=True)
            else:
                # Crear nuevo usuario
                hashed_password = self.hash_password(self.password)
                query = """
                INSERT INTO users (username, password, email, full_name, department, phone, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.username, hashed_password, self.email, self.full_name,
                    self.department, self.phone, self.is_active
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
                # Obtener el ID generado
                result = self.db.execute_query(
                    "SELECT id FROM users WHERE username = ?", (self.username,)
                )
                if result:
                    self.id = result[0]['id']
            
            return True
        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return False
    
    def delete(self) -> bool:
        """Elimina el usuario de la base de datos"""
        try:
            if self.id:
                query = "DELETE FROM users WHERE id = ?"
                self.db.execute_query(query, (self.id,), fetch=False, commit=True)
                self.id = None
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """Obtiene los roles asignados al usuario"""
        if hasattr(self, 'roles') and self.roles:
            return self.roles
        if not self.id:
            return []
        query = """
        SELECT r.id, r.name, r.description
        FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = ?
        """
        self.roles = self.db.execute_query(query, (self.id,))
        return self.roles
    
    def has_role(self, role_name: str) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        roles = self.get_roles()
        return any(role['name'] == role_name for role in roles)
    
    def assign_role(self, role_id: int) -> bool:
        """Asigna un rol al usuario"""
        if not self.id:
            return False
        
        try:
            query = "INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)"
            self.db.execute_query(query, (self.id, role_id), fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al asignar rol: {e}")
            return False
    
    def remove_role(self, role_id: int) -> bool:
        """Elimina un rol asignado al usuario"""
        if not self.id:
            return False
        
        try:
            query = "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?"
            self.db.execute_query(query, (self.id, role_id), fetch=False, commit=True)
            return True
        except Exception as e:
            print(f"Error al eliminar rol: {e}")
            return False
    
    def get_preferences(self) -> Dict[str, Any]:
        """Obtiene las preferencias del usuario"""
        if not self.id:
            return {}
        
        query = "SELECT * FROM user_preferences WHERE user_id = ?"
        result = self.db.execute_query(query, (self.id,))
        
        if result:
            return result[0]
        else:
            # Crear preferencias por defecto si no existen
            query = """
            INSERT INTO user_preferences (user_id, theme_mode, remember_credentials)
            VALUES (?, 'light', FALSE)
            """
            self.db.execute_query(query, (self.id,), fetch=False, commit=True)
            
            # Retornar las preferencias por defecto
            return {
                'user_id': self.id,
                'theme_mode': 'light',
                'remember_credentials': False,
                'default_dashboard': 'integral',
                'notification_settings': None
            }
    
    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Actualiza las preferencias del usuario"""
        if not self.id:
            return False
        
        try:
            # Verificar si ya existen preferencias
            current_prefs = self.get_preferences()
            
            if current_prefs:
                # Actualizar preferencias existentes
                query = """
                UPDATE user_preferences SET
                    theme_mode = ?,
                    remember_credentials = ?,
                    default_dashboard = ?,
                    notification_settings = ?
                WHERE user_id = ?
                """
                params = (
                    preferences.get('theme_mode', current_prefs.get('theme_mode')),
                    preferences.get('remember_credentials', current_prefs.get('remember_credentials')),
                    preferences.get('default_dashboard', current_prefs.get('default_dashboard')),
                    preferences.get('notification_settings', current_prefs.get('notification_settings')),
                    self.id
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
            else:
                # Crear preferencias
                query = """
                INSERT INTO user_preferences 
                (user_id, theme_mode, remember_credentials, default_dashboard, notification_settings)
                VALUES (?, ?, ?, ?, ?)
                """
                params = (
                    self.id,
                    preferences.get('theme_mode', 'light'),
                    preferences.get('remember_credentials', False),
                    preferences.get('default_dashboard', 'integral'),
                    preferences.get('notification_settings', None)
                )
                self.db.execute_query(query, params, fetch=False, commit=True)
                
            return True
        except Exception as e:
            print(f"Error al actualizar preferencias: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Obtiene un usuario por su ID"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        
        if result:
            user_data = result[0]
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                department=user_data['department'],
                phone=user_data['phone'],
                is_active=user_data['is_active']
            )
            return user
        
        return None
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Obtiene un usuario por su nombre de usuario"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM users WHERE username = ?", (username,))
        
        if result:
            user_data = result[0]
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                department=user_data['department'],
                phone=user_data['phone'],
                is_active=user_data['is_active']
            )
            return user
        
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Obtiene un usuario por su correo electrónico"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM users WHERE email = ?", (email,))
        
        if result:
            user_data = result[0]
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                department=user_data['department'],
                phone=user_data['phone'],
                is_active=user_data['is_active']
            )
            return user
        
        return None
    
    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional['User']:
        """Autentica un usuario con su nombre de usuario y contraseña"""
        db = DatabaseConnection()
        result = db.execute_query(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = TRUE",
            (username, username)
        )
        
        if result:
            user_data = result[0]
            # Verificar contraseña
            if cls.check_password(password, user_data['password']):
                user = cls(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    department=user_data['department'],
                    phone=user_data['phone'],
                    is_active=user_data['is_active']
                )
                # Cargar roles inmediatamente
                user.roles = user.get_roles()
                return user
        
        return None
    
    @classmethod
    def get_all(cls) -> List['User']:
        """Obtiene todos los usuarios"""
        db = DatabaseConnection()
        results = db.execute_query("SELECT * FROM users")
        
        users = []
        for user_data in results:
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                department=user_data['department'],
                phone=user_data['phone'],
                is_active=user_data['is_active']
            )
            users.append(user)
        
        return users
