"""Xóa hồ sơ đã hết hạn. Mặc định chỉ đếm; cần --apply mới xóa thật."""

import argparse
import asyncio

from src.core.database import _session_factory
from src.modules.assessments.repository import AssessmentRepository
from src.modules.assessments.service import AssessmentService


async def main(apply: bool) -> None:
    async with _session_factory() as session:
        count = await AssessmentService(AssessmentRepository(session)).purge_expired(apply)
    action = "Đã xóa" if apply else "Sẽ xóa (chạy thử)"
    print(f"{action} {count} hồ sơ hết hạn.")  # noqa: T201 - lệnh vận hành chạy tay


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Xóa thật thay vì chỉ đếm")
    asyncio.run(main(parser.parse_args().apply))
