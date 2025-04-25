from app.roles.models.role import Role, RolePermission
from app.core.database.db_manager import DatabaseConnection
from typing import List, Optional

class RoleController:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create_role(self, name: str, description: str = "") -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO roles (name, description) VALUES (%s, %s)",
            (name, description)
        )
        role_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        return role_id

    def get_role(self, role_id: int) -> Optional[Role]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description FROM roles WHERE id = %s",
            (role_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Role(*row)
        return None

    def update_role(self, role_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        conn = self.db.get_connection()
        cursor = conn.cursor()
        fields = ', '.join(f"{k} = %s" for k in kwargs.keys())
        values = list(kwargs.values())
        values.append(role_id)
        cursor.execute(f"UPDATE roles SET {fields} WHERE id = %s", values)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def delete_role(self, role_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def list_roles(self) -> List[Role]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM roles")
        rows = cursor.fetchall()
        cursor.close()
        return [Role(*row) for row in rows]

    def assign_permission(self, role_id: int, permission_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
            (role_id, permission_id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def get_role_permissions(self, role_id: int) -> List[int]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT permission_id FROM role_permissions WHERE role_id = %s", (role_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [row[0] for row in rows]
