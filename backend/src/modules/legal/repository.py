import json
from pathlib import Path

from src.modules.legal.schemas import LegalDocument

DATA_FILE = Path(__file__).parent / "data" / "documents.json"


class LegalRepository:
    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path

    def list_documents(self) -> list[LegalDocument]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [LegalDocument.model_validate(item) for item in raw]
