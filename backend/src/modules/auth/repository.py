from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import RefreshSession, User
from src.modules.auth.domain import UserRecord


def user_record(user: User) -> UserRecord:
    return UserRecord(user.id, user.username, user.password_hash, user.is_active)


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_user(self, username: str) -> UserRecord | None:
        row = await self.session.scalar(select(User).where(User.username == username))
        result = user_record(row) if row else None
        await self.session.rollback()
        return result

    async def find_by_id(self, user_id: UUID) -> UserRecord | None:
        row = await self.session.get(User, user_id)
        result = user_record(row) if row else None
        await self.session.rollback()
        return result

    async def bootstrap(self, username: str, password_hash: str) -> None:
        if await self.find_user(username) is not None:
            return
        self.session.add(User(username=username, password_hash=password_hash, is_active=True))
        await self.session.commit()

    async def add_refresh(self, user_id: UUID, token_hash: str, expires_at: datetime) -> None:
        self.session.add(
            RefreshSession(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        )
        await self.session.commit()

    async def rotate_refresh(self, old_hash: str, new_hash: str) -> UserRecord | None:
        row = await self.session.scalar(
            select(RefreshSession)
            .where(
                RefreshSession.token_hash == old_hash,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > datetime.now(UTC),
            )
            .with_for_update()
        )
        if row is None:
            return None
        user = await self.session.get(User, row.user_id)
        if user is None:
            return None
        row.revoked_at = datetime.now(UTC)
        self.session.add(
            RefreshSession(user_id=user.id, token_hash=new_hash, expires_at=row.expires_at)
        )
        await self.session.commit()
        return user_record(user)

    async def revoke_refresh(self, token_hash: str) -> None:
        await self.session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.token_hash == token_hash,
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.commit()
