from app.core.database.schema import DatabaseSchema

def update_database():
    """
    Actualiza la estructura de la base de datos para incluir la tabla 
    expiration_history que falta.
    """
    print("Iniciando actualización de la base de datos...")
    
    # Instanciar el gestor de schema
    schema = DatabaseSchema()
    
    # Crear la tabla de historial de vencimientos si no existe
    try:
        print("Creando tabla de historial de vencimientos...")
        schema._create_expiration_history_table()
        print("Tabla de historial de vencimientos creada correctamente.")
        return True
    except Exception as e:
        print(f"Error al crear la tabla expiration_history: {e}")
        return False

if __name__ == "__main__":
    if update_database():
        print("Base de datos actualizada correctamente.")
    else:
        print("Error al actualizar la base de datos.")
