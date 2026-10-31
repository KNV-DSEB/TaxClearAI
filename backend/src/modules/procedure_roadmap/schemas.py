from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Segment(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"


class TargetAction(StrEnum):
    TERMINATE = "terminate"
    SUSPEND = "suspend"
    CONVERT_TO_NEW_ENTITY = "convert_to_new_entity"


class RoadmapRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    segment: Segment
    target_action: TargetAction


class ProcedureStep(BaseModel):
    step_order: int
    phase: str
    action: str
    agency: str
    law_reference: str
    expected_duration: str
    can_self_do: bool


class RoadmapResponse(BaseModel):
    segment: Segment
    roadmap_title: str
    steps: list[ProcedureStep]
    needs_expert: bool = False


class CompanyCompareSegment(StrEnum):
    B1 = "B1"
    B2 = "B2"


class ProcedureCompareRequest(BaseModel):
    segment: CompanyCompareSegment
    has_multiple_members: bool = False
    has_large_capital_contribution: bool = False
    has_dispute: bool = False
    has_outstanding_items: bool = False


class ProcedureComparisonRow(BaseModel):
    criterion: str
    dissolution: str
    transfer_or_conversion: str
    legal_basis: str = "Chưa xác định căn cứ trong nguồn đã đồng bộ"


class ProcedureCompareResponse(BaseModel):
    segment: CompanyCompareSegment
    rows: list[ProcedureComparisonRow]
    recommendation_boundary: str
