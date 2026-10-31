from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.core.ai_disclosure import AI_DISCLOSURE


class Segment(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"


class EffectivenessStatus(StrEnum):
    CURRENT = "con_hieu_luc"
    EXPIRED = "het_hieu_luc"
    NOT_YET_EFFECTIVE = "chua_co_hieu_luc"
    UNKNOWN = "khong_ro"


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    message: str = Field(alias="tin_nhan", min_length=1, max_length=1000)
    segment: Segment = Field(alias="nhom")
    current_step: str = Field(default="", alias="buoc", max_length=200)
    context_flags: dict[str, bool] = Field(default_factory=dict, alias="co")


class LawEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = ""
    document_number: str = ""
    article: str = ""
    clause: str = ""
    point: str | None = None
    noi_dung: str
    source_url: str = ""
    source_domain: str = ""
    fetched_at: datetime | None = None
    content_sha256: str = ""
    effectiveness_status: EffectivenessStatus = EffectivenessStatus.UNKNOWN
    effective_date: date | None = None
    amended_by: str | None = None
    ap_dung_cho: list[Segment] = Field(default_factory=list)
    van_ban: str = ""
    dieu_khoan: str = ""
    hieu_luc: str = ""
    tinh_trang: str = ""
    link: str = ""


class LLMAnswer(BaseModel):
    answer: str
    citations: list[str]
    needs_expert: bool


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    sources: list[LawEntry] = Field(serialization_alias="nguon")
    needs_expert: bool
    mode: int = Field(serialization_alias="che_do", ge=1, le=3)
    block_reason: str | None = Field(default=None, serialization_alias="ly_do_chan")
    data_note: str | None = None
    ai_disclosure: str = AI_DISCLOSURE
    scope_note: str = (
        "Chỉ giải thích tổng quát theo nguồn được cung cấp; trường hợp cụ thể cần chuyên gia."
    )
