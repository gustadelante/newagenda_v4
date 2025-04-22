#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para migrar la estructura del proyecto a Screaming Architecture

Este script crea la nueva estructura de directorios y mueve los archivos
a sus nuevas ubicaciones, actualizando las importaciones según sea necesario.
"""

import os
import shutil
import re
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path("d:/desarrollo/newagenda_v4")
APP_DIR = BASE_DIR / "app"

# Definir la nueva estructura de directorios
new_structure = {
    "core": {
        "__init__.py": "# Módulo core\n# Contiene componentes centrales y compartidos de la aplicación",
        "database": {},
        "utils": {}
    },
    "authentication": {
        "__init__.py": "# Módulo de autenticación\n# Gestiona la autenticación y autorización de usuarios",
        "controllers": {},
        "models": {},
        "views": {}
    },
    "expirations": {
        "__init__.py": "# Módulo de vencimientos\n# Gestiona los vencimientos y alertas del sistema",
        "controllers": {},
        "models": {},
        "views": {
            "dashboards": {},
            "forms": {},
            "lists": {}
        }
    },
    "notifications": {
        "__init__.py": "# Módulo de notificaciones\n# Gestiona el envío de notificaciones por diferentes canales",
        "services": {}
    },
    "user_management": {
        "__init__.py": "# Módulo de gestión de usuarios\n# Gestiona la configuración y preferencias de usuarios",
        "views": {}
    }
}

# Mapeo de archivos: origen -> destino
file_mapping = {
    # Core
    "database/connection.py": "core/database/connection.py",
    "database/schema.py": "core/database/schema.py",
    "utils/theme_manager.py": "core/utils/theme_manager.py",
    
    # Authentication
    "controllers/auth_controller.py": "authentication/controllers/auth_controller.py",
    "models/user.py": "authentication/models/user.py",
    "views/login_window.py": "authentication/views/login_window.py",
    
    # Expirations
    "controllers/expiration_controller.py": "expirations/controllers/expiration_controller.py",
    "models/expiration.py": "expirations/models/expiration.py",
    "models/alert.py": "expirations/models/alert.py",
    "views/dashboards/integral_dashboard.py": "expirations/views/dashboards/integral_dashboard.py",
    "views/dashboards/sabana_dashboard.py": "expirations/views/dashboards/sabana_dashboard.py",
    "views/expiration_views/expiration_form.py": "expirations/views/forms/expiration_form.py",
    "views/expiration_views/expiration_list.py": "expirations/views/lists/expiration_list.py",
    
    # Notifications
    "services/notification_service.py": "notifications/services/notification_service.py",
    
    # User Management
    "views/user_views/user_settings.py": "user_management/views/user_settings.py",
    
    # Main window (se mantiene en la raíz de app)
    "views/main_window.py": "main_window.py"
}

# Patrones de importación a actualizar
import_patterns = {
    # Core
    r"from \.\.database\.connection": "from app.core.database.connection",
    r"from \.\.database\.schema": "from app.core.database.schema",
    r"from \.\.utils\.theme_manager": "from app.core.utils.theme_manager",
    
    # Authentication
    r"from \.\.controllers\.auth_controller": "from app.authentication.controllers.auth_controller",
    r"from \.\.models\.user": "from app.authentication.models.user",
    r"from \.\.views\.login_window": "from app.authentication.views.login_window",
    
    # Expirations
    r"from \.\.controllers\.expiration_controller": "from app.expirations.controllers.expiration_controller",
    r"from \.\.models\.expiration": "from app.expirations.models.expiration",
    r"from \.\.models\.alert": "from app.expirations.models.alert",
    r"from \.\.views\.dashboards\.integral_dashboard": "from app.expirations.views.dashboards.integral_dashboard",
    r"from \.\.views\.dashboards\.sabana_dashboard": "from app.expirations.views.dashboards.sabana_dashboard",
    r"from \.\.views\.expiration_views\.expiration_form": "from app.expirations.views.forms.expiration_form",
    r"from \.\.views\.expiration_views\.expiration_list": "from app.expirations.views.lists.expiration_list",
    
    # Notifications
    r"from \.\.services\.notification_service": "from app.notifications.services.notification_service",
    
    # User Management
    r"from \.\.views\.user_views\.user_settings": "from app.user_management.views.user_settings",
    
    # Main window
    r"from \.\.views\.main_window": "from app.main_window"
}

# Actualizar importaciones en main.py
main_imports = {
    r"from app\.database\.schema import initialize_database": "from app.core.database.schema import initialize_database",
    r"from app\.controllers\.auth_controller import AuthController": "from app.authentication.controllers.auth_controller import AuthController",
    r"from app\.views\.login_window import LoginWindow": "from app.authentication.views.login_window import LoginWindow",
    r"from app\.views\.main_window import MainWindow": "from app.main_window import MainWindow",
    r"from app\.utils\.theme_manager import theme_manager": "from app.core.utils.theme_manager import theme_manager"
}


def create_directory_structure():
    """Crea la estructura de directorios para la nueva arquitectura"""
    print("Creando estructura de directorios...")
    
    def create_nested_dirs(base_path, structure, current_path=""):
        for key, value in structure.items():
            path = os.path.join(current_path, key)
            full_path = os.path.join(base_path, path)
            
            if not os.path.exists(full_path):
                if key.endswith(".py"):
                    # Es un archivo
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(value)
                else:
                    # Es un directorio
                    os.makedirs(full_path, exist_ok=True)
                    if isinstance(value, dict):
                        create_nested_dirs(base_path, value, path)
    
    create_nested_dirs(APP_DIR, new_structure)
    print("Estructura de directorios creada correctamente.")


def update_imports_in_file(file_path, patterns):
    """Actualiza las importaciones en un archivo"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Aplicar patrones de reemplazo
        for pattern, replacement in patterns.items():
            content = re.sub(pattern, replacement, content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error al actualizar importaciones en {file_path}: {e}")
        return False


def move_files():
    """Mueve los archivos a sus nuevas ubicaciones y actualiza las importaciones"""
    print("Moviendo archivos y actualizando importaciones...")
    
    for src_rel, dst_rel in file_mapping.items():
        src_path = APP_DIR / src_rel
        dst_path = APP_DIR / dst_rel
        
        # Crear directorio destino si no existe
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        
        try:
            # Leer contenido del archivo
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Actualizar importaciones
            for pattern, replacement in import_patterns.items():
                content = re.sub(pattern, replacement, content)
            
            # Escribir archivo en nueva ubicación
            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Archivo movido y actualizado: {src_rel} -> {dst_rel}")
        except Exception as e:
            print(f"Error al mover archivo {src_rel}: {e}")
    
    # Actualizar importaciones en main.py
    main_py_path = BASE_DIR / "main.py"
    if main_py_path.exists():
        update_imports_in_file(main_py_path, main_imports)
        print("Importaciones actualizadas en main.py")
    
    print("Archivos movidos y actualizados correctamente.")


def update_app_init():
    """Actualiza el archivo __init__.py en la raíz de app"""
    init_path = APP_DIR / "__init__.py"
    
    content = """\
NewAgenda - Sistema de Gestión de Vencimientos

Esta aplicación sigue una arquitectura Screaming Architecture,
donde la estructura de directorios refleja los casos de uso del sistema.

# Importar componentes principales para facilitar su uso
from app.core.utils.theme_manager import theme_manager
from app.core.database.schema import initialize_database
"""
    
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Archivo __init__.py actualizado correctamente.")


def main():
    """Función principal"""
    print("Iniciando migración a Screaming Architecture...")
    
    # Crear estructura de directorios
    create_directory_structure()
    
    # Mover archivos y actualizar importaciones
    move_files()
    
    # Actualizar __init__.py
    update_app_init()
    
    print("\nMigración completada con éxito.")
    print("IMPORTANTE: Revise la aplicación para asegurarse de que todo funciona correctamente.")
    print("Es posible que necesite ajustar manualmente algunas importaciones.")


if __name__ == "__main__":
    main()