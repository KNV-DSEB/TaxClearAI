from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.community.repository import CommunityRepository
from src.modules.community.service import CommunityService


def get_community_service(
    session: AsyncSession = Depends(get_db, use_cache=False),
) -> CommunityService:
    return CommunityService(CommunityRepository(session))
