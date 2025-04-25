from app.core.database.connection import DatabaseConnection

class DBManager:
    """
    Clase para gestionar la conexión a la base de datos
    Proporciona una interfaz unificada para obtener la conexión
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.db_connection = DatabaseConnection()
        return cls._instance
    
    def get_connection(self):
        """
        Obtiene la conexión a la base de datos
        
        Returns:
            Objeto de conexión a la base de datos
        """
        return self.db_connection.get_connection()
