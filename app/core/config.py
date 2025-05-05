# Configuración centralizada: lee variables de entorno para DB y Email
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', ''),
}

EMAIL_CONFIG = {
    'host': os.getenv('EMAIL_HOST', ''),
    'port': int(os.getenv('EMAIL_PORT', 587)),
    'user': os.getenv('EMAIL_USER', ''),
    'password': os.getenv('EMAIL_PASSWORD', ''),
}
