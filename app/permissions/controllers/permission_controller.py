from app.permissions.models.permission import Permission
from app.core.database.db_manager import DatabaseConnection
from typing import List, Optional

class PermissionController:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create_permission(self, name: str, description: str = "") -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO permissions (name, description) VALUES (%s, %s)",
            (name, description)
        )
        permission_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        return permission_id

    def get_permission(self, permission_id: int) -> Optional[Permission]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description FROM permissions WHERE id = %s",
            (permission_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Permission(*row)
        return None

    def update_permission(self, permission_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        conn = self.db.get_connection()
        cursor = conn.cursor()
        fields = ', '.join(f"{k} = %s" for k in kwargs.keys())
        values = list(kwargs.values())
        values.append(permission_id)
        cursor.execute(f"UPDATE permissions SET {fields} WHERE id = %s", values)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def delete_permission(self, permission_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM permissions WHERE id = %s", (permission_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def list_permissions(self) -> List[Permission]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM permissions")
        rows = cursor.fetchall()
        cursor.close()
        return [Permission(*row) for row in rows]
