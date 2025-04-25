from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    is_active: bool
    email: Optional[str]

@dataclass
class UserRole:
    user_id: int
    role_id: int
