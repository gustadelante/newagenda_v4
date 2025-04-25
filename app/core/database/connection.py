import mariadb
import sys
from typing import Optional, Dict, Any

class DatabaseConnection:
    """Clase para manejar la conexión a la base de datos MariaDB"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Implementación del patrón Singleton para asegurar una única conexión"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._conn = None
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            config: Diccionario con los parámetros de conexión.
                   Por defecto usa la configuración para desarrollo.
        """
        if self._initialized:
            return
            
        if config is None:
            self._config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': 'pepe01',
                'database': 'new_agenda',
                'port': 3306
            }
        else:
            self._config = config
            
        self._initialized = True
    
    def connect(self):
        """Establece la conexión a la base de datos"""
        try:
            if self._conn is None or not self._conn.open:
                self._conn = mariadb.connect(
                    host=self._config['host'],
                    user=self._config['user'],
                    password=self._config['password'],
                    database=self._config['database'],
                    port=self._config['port']
                )
                self._conn.autocommit = False
                print("Conexión a la base de datos establecida correctamente")
        except mariadb.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            sys.exit(1)
            
        return self._conn
    
    def get_connection(self):
        """Retorna la conexión actual o crea una nueva si no existe"""
        if self._conn is None or not self._conn.open:
            self.connect()
        return self._conn
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self._conn and self._conn.open:
            self._conn.close()
            self._conn = None
            print("Conexión a la base de datos cerrada")
    
    def execute_query(self, query, params=None, fetch=True, commit=False):
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
            fetch: Si es True, retorna los resultados.
            commit: Si es True, hace commit después de la ejecución.
            
        Returns:
            Resultados de la consulta si fetch es True, None en caso contrario.
        """
        cursor = None
        result = None
        conn = self.get_connection()
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Convertir los placeholders ? a %s si es necesario (para compatibilidad)
            # MariaDB usa %s para los parámetros, no ? como SQLite
            if '?' in query and params:
                # Contar cuántos ? hay en la consulta
                placeholders_count = query.count('?')
                # Reemplazar cada ? por %s
                query = query.replace('?', '%s')
                print(f"Consulta convertida: {query}")
            
            # Ejecutar la consulta con parámetros o sin ellos
            if params:
                try:
                    cursor.execute(query, params)
                except Exception as e:
                    print(f"Error al ejecutar consulta con parámetros: {e}")
                    print(f"Consulta: {query}")
                    print(f"Parámetros: {params}")
                    raise
            else:
                cursor.execute(query)
                
            if fetch:
                try:
                    result = cursor.fetchall()
                except mariadb.Error as e:
                    # Si no hay resultados para obtener, simplemente continuar
                    if "Cursor doesn't have a result set" in str(e):
                        result = []
                    else:
                        raise
                
            if commit:
                conn.commit()
                
            return result
        except mariadb.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            if commit:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def begin_transaction(self):
        """Inicia una transacción"""
        self.get_connection().autocommit = False
    
    def commit(self):
        """Confirma una transacción"""
        self.get_connection().commit()
        
    def rollback(self):
        """Revierte una transacción"""
        self.get_connection().rollback()
