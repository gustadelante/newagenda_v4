"""NewAgenda - Sistema de Gestión de Vencimientos

Esta aplicación sigue una arquitectura Screaming Architecture,
donde la estructura de directorios refleja los casos de uso del sistema.
"""

# Importar componentes principales para facilitar su uso
from app.core.utils.theme_manager import theme_manager
from app.core.database.schema import initialize_database
