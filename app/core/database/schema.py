from .connection import DatabaseConnection
import sys

class DatabaseSchema:
    """Clase para crear y actualizar el esquema de la base de datos"""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        self.db = DatabaseConnection()
    
    def initialize_database(self):
        """Crea la base de datos si no existe"""
        try:
            # Conectar sin especificar una base de datos
            config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': 'pepe01',
                'port': 3306
            }
            self.db = DatabaseConnection(config)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Crear la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS new_agenda")
            cursor.execute("USE new_agenda")
            
            conn.commit()
            cursor.close()
            
            # Reiniciar la conexión para usar la base de datos recién creada
            self.db.close()
            self.db = DatabaseConnection()
            
            print("Base de datos inicializada correctamente")
            return True
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            return False
    
    def create_tables(self):
        """Crea las tablas necesarias para la aplicación"""
        try:
            # Conectar a la base de datos
            conn = self.db.get_connection()
            
            # Crear tablas en orden correcto para evitar problemas de dependencias
            self._create_users_table()
            self._create_roles_table()
            self._create_user_roles_table()
            self._create_sectors_table()
            self._create_priorities_table()
            self._create_expiration_statuses_table()
            self._create_expirations_table()
            self._create_expiration_history_table()  # Añadida la tabla de historial de vencimientos
            self._create_alerts_table()
            self._create_alert_history_table()
            self._create_document_categories_table()
            self._create_documents_table()
            self._create_document_tags_table()
            self._create_document_tag_mappings_table()
            self._create_user_preferences_table()
            self._create_dashboard_views_table()
            
            # Poblar con datos iniciales
            self._populate_initial_data()
            
            print("Tablas creadas correctamente")
            return True
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
            return False
    
    def _create_users_table(self):
        """Crea la tabla de usuarios"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            full_name VARCHAR(100) NOT NULL,
            department VARCHAR(100),
            phone VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_roles_table(self):
        """Crea la tabla de roles"""
        query = """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        self._create_permissions_table()
        self._create_role_permissions_table()
    
    def _create_permissions_table(self):
        """Crea la tabla de permisos"""
        query = """
        CREATE TABLE IF NOT EXISTS permissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
    
    def _create_role_permissions_table(self):
        """Crea la tabla de relación entre roles y permisos"""
        query = """
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INT NOT NULL,
            permission_id INT NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_user_roles_table(self):
        """Crea la tabla de relación entre usuarios y roles"""
        query = """
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INT NOT NULL,
            role_id INT NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_sectors_table(self):
        """Crea la tabla de sectores"""
        query = """
        CREATE TABLE IF NOT EXISTS sectors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_priorities_table(self):
        """Crea la tabla de prioridades"""
        query = """
        CREATE TABLE IF NOT EXISTS priorities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            color VARCHAR(7) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_expiration_statuses_table(self):
        """Crea la tabla de estados de vencimientos"""
        query = """
        CREATE TABLE IF NOT EXISTS expiration_statuses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            color VARCHAR(7) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_expirations_table(self):
        """Crea la tabla de vencimientos"""
        query = """
        CREATE TABLE IF NOT EXISTS expirations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            expiration_date DATE NOT NULL,
            concept TEXT NOT NULL,
            responsible_id INT NOT NULL,
            priority_id INT NOT NULL,
            sector_id INT NOT NULL,
            status_id INT NOT NULL,
            notes TEXT,
            created_by INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (responsible_id) REFERENCES users(id),
            FOREIGN KEY (priority_id) REFERENCES priorities(id),
            FOREIGN KEY (sector_id) REFERENCES sectors(id),
            FOREIGN KEY (status_id) REFERENCES expiration_statuses(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_alerts_table(self):
        """Crea la tabla de alertas"""
        query = """
        CREATE TABLE IF NOT EXISTS alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            expiration_id INT NOT NULL,
            days_before INT NOT NULL,
            alert_count INT DEFAULT 0,
            max_alerts INT DEFAULT 3,
            email_alert BOOLEAN DEFAULT TRUE,
            push_alert BOOLEAN DEFAULT TRUE,
            desktop_alert BOOLEAN DEFAULT TRUE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (expiration_id) REFERENCES expirations(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_alert_history_table(self):
        """Crea la tabla de historial de alertas"""
        query = """
        CREATE TABLE IF NOT EXISTS alert_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alert_id INT NOT NULL,
            alert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            alert_type ENUM('email', 'push', 'desktop') NOT NULL,
            status ENUM('sent', 'failed', 'pending') NOT NULL,
            error_message TEXT,
            FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    # El método _create_documents_table se ha movido después de _create_document_categories_table
        
    def _create_document_categories_table(self):
        """Crea la tabla de categorías de documentos"""
        query = """
        CREATE TABLE IF NOT EXISTS document_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_documents_table(self):
        """Crea la tabla de documentos (debe ejecutarse después de document_categories)"""
        query = """
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            reference_number VARCHAR(100),
            file_path VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_size INT,
            category_id INT,
            uploaded_by INT NOT NULL,
            is_personal BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES document_categories(id) ON DELETE SET NULL,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_document_tags_table(self):
        """Crea la tabla de etiquetas de documentos"""
        query = """
        CREATE TABLE IF NOT EXISTS document_tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_document_tag_mappings_table(self):
        """Crea la tabla de relación entre documentos y etiquetas"""
        query = """
        CREATE TABLE IF NOT EXISTS document_tag_mappings (
            document_id INT NOT NULL,
            tag_id INT NOT NULL,
            PRIMARY KEY (document_id, tag_id),
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES document_tags(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_user_preferences_table(self):
        """Crea la tabla de preferencias de usuario"""
        query = """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INT PRIMARY KEY,
            theme_mode ENUM('light', 'dark') DEFAULT 'light',
            remember_credentials BOOLEAN DEFAULT FALSE,
            default_dashboard VARCHAR(50) DEFAULT 'integral',
            notification_settings JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
        
    def _create_dashboard_views_table(self):
        """Crea la tabla de vistas personalizadas de dashboard"""
        query = """
        CREATE TABLE IF NOT EXISTS dashboard_views (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            view_type ENUM('integral', 'alfombra') NOT NULL,
            filter_config JSON,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_view_name_per_user (user_id, name),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db.execute_query(query, commit=True)
    
    def _create_expiration_history_table(self):
        """Crea la tabla de historial de vencimientos"""
        query = """
        CREATE TABLE IF NOT EXISTS expiration_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            expiration_id INT NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            description VARCHAR(255) NOT NULL,
            notes TEXT,
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (expiration_id) REFERENCES expirations(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
        self.db.execute_query(query, commit=True)
    
    def _populate_initial_data(self):
        """Pobla las tablas con datos iniciales"""
        # Roles
        roles = [
            ('admin', 'Administrador con acceso completo al sistema'),
            ('user', 'Usuario estándar con acceso limitado'),
            ('manager', 'Gerente con permisos extendidos de visualización')
        ]
        
        for role in roles:
            self.db.execute_query(
                "INSERT IGNORE INTO roles (name, description) VALUES (?, ?)",
                role, commit=True
            )
        # Permisos
        permissions = [
            ('manage_users', 'Gestionar usuarios'),
            ('manage_roles', 'Gestionar roles'),
            ('manage_permissions', 'Gestionar permisos'),
            ('view_dashboard', 'Ver dashboard'),
            ('edit_expirations', 'Editar vencimientos'),
            ('view_expirations', 'Ver vencimientos')
        ]
        for perm in permissions:
            self.db.execute_query(
                "INSERT IGNORE INTO permissions (name, description) VALUES (?, ?)",
                perm, commit=True
            )
        # Asignar todos los permisos al rol admin
        self.db.execute_query(
            "INSERT IGNORE INTO role_permissions (role_id, permission_id) SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'admin'",
            commit=True
        )
        
        # Sectores
        sectors = [
            ('Administración', 'Sector encargado de tareas administrativas'),
            ('Finanzas', 'Sector encargado de las finanzas'),
            ('IT', 'Sector de tecnología e informática'),
            ('RRHH', 'Recursos Humanos'),
            ('Operaciones', 'Sector de operaciones')
        ]
        
        for sector in sectors:
            self.db.execute_query(
                "INSERT IGNORE INTO sectors (name, description) VALUES (?, ?)",
                sector, commit=True
            )
        
        # Prioridades
        priorities = [
            ('Baja', 'Prioridad baja, puede esperar', '#28a745'),
            ('Media', 'Prioridad media, atención regular', '#ffc107'),
            ('Alta', 'Prioridad alta, requiere atención pronta', '#dc3545'),
            ('Crítica', 'Prioridad crítica, requiere atención inmediata', '#9c27b0')
        ]
        
        for priority in priorities:
            self.db.execute_query(
                "INSERT IGNORE INTO priorities (name, description, color) VALUES (?, ?, ?)",
                priority, commit=True
            )
        
        # Estados de vencimiento
        statuses = [
            ('Pendiente', 'Vencimiento pendiente de atención', '#ffc107'),
            ('Renovado', 'Vencimiento renovado o gestionado', '#28a745'),
            ('Vencido', 'Vencimiento pasado sin gestionar', '#dc3545'),
            ('En proceso', 'Vencimiento en proceso de gestión', '#17a2b8')
        ]
        
        for status in statuses:
            self.db.execute_query(
                "INSERT IGNORE INTO expiration_statuses (name, description, color) VALUES (?, ?, ?)",
                status, commit=True
            )
        
        # Usuario administrador por defecto
        admin_exists_result = self.db.execute_query(
            "SELECT id FROM users WHERE username = 'admin'"
        )
        
        # Verificar si el resultado existe y tiene elementos
        admin_exists = admin_exists_result and len(admin_exists_result) > 0
        
        if not admin_exists:
            import bcrypt
            # Generar hash para la contraseña 'admin123'
            password = 'admin123'
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Crear usuario admin
            self.db.execute_query(
                "INSERT INTO users (username, password, email, full_name, department) VALUES (?, ?, ?, ?, ?)",
                ('admin', hashed_password, 'admin@newagenda.com', 'Administrador del Sistema', 'IT'),
                commit=True
            )
            
            # Asignar rol de administrador
            admin_id_result = self.db.execute_query(
                "SELECT id FROM users WHERE username = 'admin'"
            )
            if admin_id_result and len(admin_id_result) > 0:
                admin_id = admin_id_result[0]['id']
                
                admin_role_id_result = self.db.execute_query(
                    "SELECT id FROM roles WHERE name = 'admin'"
                )
                if admin_role_id_result and len(admin_role_id_result) > 0:
                    admin_role_id = admin_role_id_result[0]['id']
                    
                    # Solo insertar si tenemos ambos IDs
                    self.db.execute_query(
                        "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
                        (admin_id, admin_role_id),
                        commit=True
                    )
                    
                    # Crear preferencias por defecto
                    self.db.execute_query(
                        "INSERT INTO user_preferences (user_id, theme_mode) VALUES (?, ?)",
                        (admin_id, 'light'),
                        commit=True
                    )


def initialize_database():
    """Función para inicializar la base de datos"""
    schema = DatabaseSchema()
    
    if not schema.initialize_database():
        print("Error al inicializar la base de datos")
        sys.exit(1)
        
    if not schema.create_tables():
        print("Error al crear las tablas")
        sys.exit(1)
        
    print("Base de datos creada correctamente")


if __name__ == "__main__":
    initialize_database()
