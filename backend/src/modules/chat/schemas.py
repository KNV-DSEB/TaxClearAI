from datetime import date
from typing import Literal

from pydantic import ConfigDict, Field

from src.core.schemas import ApiModel


class ChatRequest(ApiModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=1500)
    disclosure_accepted: Literal[True]


class Citation(ApiModel):
    source_id: str
    title: str
    url: str
    reviewed_at: date
    kind: Literal["product", "legal"]


class ChatReply(ApiModel):
    reply: str
    disposition: Literal["answered", "insufficient_sources", "expert_review", "blocked_input"]
    citations: list[Citation] = Field(default_factory=list)
    provider_used: bool = False


class GeneratedAnswer(ApiModel):
    reply: str = Field(min_length=1, max_length=3000)
    source_ids: list[str] = Field(min_length=1, max_length=8)
