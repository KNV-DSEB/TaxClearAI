from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BusinessModel(StrEnum):
    HKD = "HKD"
    COMPANY_LLC = "COMPANY_LLC"
    COMPANY_JSC = "COMPANY_JSC"


class ConversionKind(StrEnum):
    HKD_TO_HKD = "HKD_TO_HKD"
    HKD_TO_COMPANY = "HKD_TO_COMPANY"
    COMPANY_TYPE_CHANGE = "COMPANY_TYPE_CHANGE"


class TaskState(StrEnum):
    COMPLETED = "COMPLETED"
    READY = "READY"
    BLOCKED = "BLOCKED"


class TargetAction(StrEnum):
    TERMINATE = "terminate"
    CONVERT_TO_NEW_ENTITY = "convert_to_new_entity"
    SUSPEND = "suspend"


class ConversionPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_model: BusinessModel
    desired_model: BusinessModel
    old_tax_obligations_settled: bool = False
    old_tax_id_termination_confirmed: bool = False
    old_registration_termination_confirmed: bool = False
    conversion_legal_review_confirmed: bool = False
    has_multiple_members: bool = False
    has_large_capital_contribution: bool = False
    has_dispute: bool = False
    new_name_prepared: bool = False
    new_address_prepared: bool = False
    new_industry_prepared: bool = False
    completed_task_ids: list[str] = Field(default_factory=list, max_length=30)
    target_action: TargetAction | None = None

    @model_validator(mode="after")
    def validate_transition(self) -> "ConversionPlanRequest":
        if self.target_action == TargetAction.SUSPEND:
            raise ValueError("Tạm ngừng kinh doanh không thuộc phạm vi công cụ chuyển đổi.")
        company_models = {BusinessModel.COMPANY_LLC, BusinessModel.COMPANY_JSC}
        supported = (
            self.current_model == BusinessModel.HKD
            and self.desired_model in company_models | {BusinessModel.HKD}
        ) or (
            self.current_model in company_models
            and self.desired_model in company_models
            and self.current_model != self.desired_model
        )
        if not supported:
            raise ValueError("Unsupported business model conversion")
        return self


class WorkflowTask(BaseModel):
    task_id: str
    action: str
    status: TaskState
    depends_on: list[str] = Field(default_factory=list)
    responsible_party: str
    note: str | None = None


class WorkflowLane(BaseModel):
    lane_id: str
    title: str
    progress_percentage: int = Field(ge=0, le=100)
    tasks: list[WorkflowTask]


class HardStop(BaseModel):
    code: str
    active: bool
    blocks: str
    reason: str
    legal_basis: str
    legal_scope_note: str


class ConversionPlanResponse(BaseModel):
    current_model: BusinessModel
    desired_model: BusinessModel
    conversion_kind: ConversionKind
    lanes: list[WorkflowLane]
    hard_stops: list[HardStop]
    next_action: str
    legal_note: str
    needs_expert: bool
