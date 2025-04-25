from dataclasses import dataclass

@dataclass
class Role:
    id: int
    name: str
    description: str = ""

@dataclass
class RolePermission:
    role_id: int
    permission_id: int
