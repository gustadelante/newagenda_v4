import os
from datetime import date, timedelta
from app.expirations.models.expiration import Expiration
from app.core.database.connection import DatabaseConnection

LAST_RUN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.status_job_date')

# Puedes cambiar estos nombres por los IDs si tu tabla de estados usa IDs
ESTADO_PENDIENTE = 'Pendiente'
ESTADO_VENCIDO = 'Vencido'


def job_update_expiration_status():
    today = date.today()
    """ 
    # Verifica si ya se ejecutó hoy
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            last_run = f.read().strip()
            if last_run == today.isoformat():
                return  # Ya se ejecutó hoy """
    
    db = DatabaseConnection()
    expirations = db.execute_query("SELECT id, expiration_date, status_id FROM expirations", fetch=True)
    
    # Obtener IDs de estados
    estados = db.execute_query("SELECT id, name FROM expiration_statuses", fetch=True)
    estado_ids = {e['name']: e['id'] for e in estados}
    
    print("Estado IDs:", estado_ids)
    for exp in expirations:
        exp_id = exp['id']
        fecha_venc = exp['expiration_date']
        status_actual = exp['status_id']
        # Si la fecha viene como string, convertirla a date
        if isinstance(fecha_venc, str):
            try:
                fecha_venc = datetime.strptime(fecha_venc, "%Y-%m-%d").date()
            except Exception as e:
                print(f"Error parseando fecha para ID {exp_id}: {fecha_venc} ({e})")
                continue
        dias = (fecha_venc - today).days
        print(f"ID {exp_id}: fecha_venc={fecha_venc}, dias={dias}, status_actual={status_actual}")
        nuevo_estado = None
        if dias <= 30 and dias >= 0:
            nuevo_estado = estado_ids.get(ESTADO_PENDIENTE)
            print(f"  Debe ser 'Pendiente' (ID {nuevo_estado})")
        elif dias < 0:
            nuevo_estado = estado_ids.get(ESTADO_VENCIDO)
            print(f"  Debe ser 'Vencido' (ID {nuevo_estado})")
        if nuevo_estado and nuevo_estado != status_actual:
            print(f"  Actualizando estado de {status_actual} a {nuevo_estado}")
            db.execute_query(
                "UPDATE expirations SET status_id = %s WHERE id = %s",
                (nuevo_estado, exp_id),
                fetch=False,
                commit=True
            )
        else:
            print(f"  No se actualiza estado para ID {exp_id}")
    # Registrar fecha de última ejecución
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(today.isoformat())
