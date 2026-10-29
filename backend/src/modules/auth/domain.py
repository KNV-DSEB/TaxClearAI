from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserRecord:
    id: UUID
    username: str
    password_hash: str
    is_active: bool
