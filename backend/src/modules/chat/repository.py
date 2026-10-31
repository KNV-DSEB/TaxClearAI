import json
from datetime import datetime
from pathlib import Path

import structlog
from pydantic import ValidationError

from src.core.schemas import ApiModel

DATA_FILE = Path(__file__).parent / "data" / "legal_sources_b2.json"


class LegalProvision(ApiModel):
    id: str
    document_number: str
    document_title: str
    article: str
    clause: str
    point: str
    text: str
    source_url: str
    fetched_at: datetime
    content_sha256: str
    amended_by: str | None


class LegalSourceFile(ApiModel):
    origin: str
    review_status: str
    provisions: list[LegalProvision]


class LegalSourceRepository:
    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path

    def list_provisions(self) -> list[LegalProvision]:
        try:
            raw = self.path.read_text(encoding="utf-8")
            return LegalSourceFile.model_validate(json.loads(raw)).provisions
        except (OSError, ValueError, ValidationError):
            # Thiếu hoặc hỏng dữ liệu thì chat trả "chưa đủ nguồn", không làm sập API
            structlog.get_logger().error("legal_sources_unreadable", path=self.path.name)
            return []
