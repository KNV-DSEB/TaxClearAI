import json
from pathlib import Path

from src.modules.expert_directory.schemas import ExpertProfile


class ExpertDirectoryRepository:
    def __init__(self, data_path: Path | None = None) -> None:
        self._data_path = data_path or Path(__file__).parent / "data" / "experts.json"

    def list_experts(self) -> list[ExpertProfile]:
        raw_experts = json.loads(self._data_path.read_text(encoding="utf-8"))
        if not isinstance(raw_experts, list):
            raise ValueError("Expert directory data must be a JSON list")
        return [ExpertProfile.model_validate(item) for item in raw_experts]
