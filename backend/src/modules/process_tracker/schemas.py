from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrackedProcedure(StrEnum):
    HKD_TERMINATION = "hkd_termination"
    HKD_SUSPENSION = "hkd_suspension"
    HKD_NEW_REGISTRATION = "hkd_new_registration"
    TAX_ID_TERMINATION = "tax_id_termination"
    COMPANY_DISSOLUTION = "company_dissolution"
    COMPANY_SUSPENSION = "company_suspension"


class UrgencyLevel(StrEnum):
    WARNING = "WARNING"
    NORMAL = "NORMAL"


class TrackedStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    step_order: int = Field(ge=1)
    phase: str = Field(min_length=1)
    action: str = Field(min_length=1)


class CompletedStep(BaseModel):
    step_order: int = Field(ge=1)
    completed_at: datetime


class ProcessTrackerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    procedure: TrackedProcedure
    steps: list[TrackedStep] = Field(min_length=1, max_length=100)
    completed_steps: list[CompletedStep] = Field(default_factory=list, max_length=100)
    current_step_started_at: datetime
    as_of: datetime | None = None

    @model_validator(mode="after")
    def validate_step_history(self) -> "ProcessTrackerRequest":
        step_orders = [step.step_order for step in self.steps]
        if len(step_orders) != len(set(step_orders)):
            raise ValueError("steps must have unique step_order values")
        completed_orders = [item.step_order for item in self.completed_steps]
        if len(completed_orders) != len(set(completed_orders)):
            raise ValueError("completed_steps must not contain duplicate step_order values")
        unknown_orders = set(completed_orders) - set(step_orders)
        if unknown_orders:
            raise ValueError("completed_steps must refer to an order in steps")
        return self


class DeadlineAlert(BaseModel):
    milestone: str
    deadline_rule: str
    urgency_level: UrgencyLevel
    deadline_date: str
    days_remaining: int | None
    legal_reference: str


class ProcessTrackerResponse(BaseModel):
    progress_percentage: int = Field(ge=0, le=100)
    current_stage: str
    completed_steps: list[str]
    last_completed_step: str | None
    current_step: str | None
    next_action: str
    critical_deadlines: list[DeadlineAlert]
    calculation_note: str
