from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.modules.case_brief.schemas import CaseBriefRequest, CaseSegment


class ExpertType(StrEnum):
    LUAT_SU = "luat_su"
    KE_TOAN = "ke_toan"
    DAI_LY_THUE = "dai_ly_thue"


class PlatformFeeType(StrEnum):
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class PlatformFeeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: PlatformFeeType = PlatformFeeType.NONE
    value: float | None = Field(default=None, ge=0)


class ExpertServiceOffering(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    scope: str = Field(min_length=1, max_length=1000)
    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)
    price_unit: str = Field(min_length=1, max_length=120)
    exclusions: list[str] = Field(default_factory=list, max_length=30)


class ExpertProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=160)
    expert_type: ExpertType
    verified: bool
    verified_by: str
    verified_date: str
    regions: list[str]
    segments: list[CaseSegment]
    services: list[ExpertServiceOffering]
    platform_fee_note: str
    platform_fee_model: PlatformFeeModel = Field(default_factory=PlatformFeeModel)
    illustrative: bool = Field(serialization_alias="du_lieu_minh_hoa")


class ExpertRequestResponse(BaseModel):
    expert_id: str
    case_brief: CaseBriefRequest
    request_status: str
    message: str
    illustrative: bool = Field(serialization_alias="du_lieu_minh_hoa")
