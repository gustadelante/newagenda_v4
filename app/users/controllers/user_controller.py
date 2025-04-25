from app.users.models.user import User, UserRole
from app.core.database.db_manager import DatabaseConnection
from typing import List, Optional

class UserController:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create_user(self, username: str, full_name: str, password_hash: str, email: Optional[str], is_active: bool = True) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, full_name, password, email, is_active) VALUES (%s, %s, %s, %s, %s)",
            (username, full_name, password_hash, email, is_active)
        )
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        return user_id

    def get_user(self, user_id: int) -> Optional[User]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, is_active, email FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(*row)
        return None

    def update_user(self, user_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        conn = self.db.get_connection()
        cursor = conn.cursor()
        fields = ', '.join(f"{k} = %s" for k in kwargs.keys())
        values = list(kwargs.values())
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {fields} WHERE id = %s", values)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def delete_user(self, user_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def list_users(self) -> List[User]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, is_active, email FROM users")
        rows = cursor.fetchall()
        cursor.close()
        return [User(*row) for row in rows]

    def assign_role(self, user_id: int, role_id: int) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, role_id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def get_user_roles(self, user_id: int) -> List[int]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM user_roles WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [row[0] for row in rows]
