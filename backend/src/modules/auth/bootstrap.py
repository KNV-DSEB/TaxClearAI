import asyncio

from src.core.database import _session_factory
from src.modules.auth.repository import AuthRepository
from src.modules.auth.service import AuthService


async def main() -> None:
    async with _session_factory() as session:
        await AuthService(AuthRepository(session)).bootstrap()


if __name__ == "__main__":
    asyncio.run(main())
