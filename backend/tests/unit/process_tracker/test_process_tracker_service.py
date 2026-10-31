from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.modules.process_tracker.repository import ProcessTrackerRepository
from src.modules.process_tracker.schemas import ProcessTrackerRequest
from src.modules.process_tracker.service import ProcessTrackerService


def make_request(**overrides: object) -> ProcessTrackerRequest:
    data: dict[str, object] = {
        "procedure": "hkd_termination",
        "steps": [
            {"step_order": 1, "phase": "PREPARATION", "action": "Tra cứu nghĩa vụ"},
            {"step_order": 2, "phase": "TAX_SUBMISSION", "action": "Nộp hồ sơ thuế"},
            {"step_order": 3, "phase": "REGISTRATION_SUBMISSION", "action": "Nộp chấm dứt HKD"},
        ],
        "completed_steps": [{"step_order": 1, "completed_at": "2026-10-30T09:00:00Z"}],
        "current_step_started_at": "2026-10-30T09:00:00Z",
        "as_of": "2026-10-30T09:00:00Z",
    }
    data.update(overrides)
    return ProcessTrackerRequest.model_validate(data)


def test_track_reports_progress_current_and_next_step() -> None:
    response = ProcessTrackerService(ProcessTrackerRepository()).track(make_request())

    assert response.progress_percentage == 33
    assert response.completed_steps == ["Tra cứu nghĩa vụ"]
    assert response.last_completed_step == "Tra cứu nghĩa vụ"
    assert response.current_stage == "TAX_SUBMISSION"
    assert response.current_step == "Nộp hồ sơ thuế"
    assert response.next_action == "Nộp chấm dứt HKD"
    assert response.critical_deadlines[0].deadline_date == "2026-12-14"


def test_completed_process_has_no_current_step_or_deadline() -> None:
    request = make_request(
        completed_steps=[
            {"step_order": 1, "completed_at": "2026-10-30T09:00:00Z"},
            {"step_order": 2, "completed_at": "2026-10-30T10:00:00Z"},
            {"step_order": 3, "completed_at": "2026-10-30T11:00:00Z"},
        ]
    )

    response = ProcessTrackerService(ProcessTrackerRepository()).track(request)

    assert response.progress_percentage == 100
    assert response.current_stage == "COMPLETED"
    assert response.current_step is None
    assert response.critical_deadlines == []


def test_hkd_registration_deadline_is_five_weekdays() -> None:
    request = make_request(
        steps=[{"step_order": 1, "phase": "REGISTRATION_RESULT", "action": "Nhận kết quả"}],
        completed_steps=[],
        current_step_started_at="2026-11-02T09:00:00Z",  # Monday
        as_of="2026-11-02T09:00:00Z",
    )

    response = ProcessTrackerService(ProcessTrackerRepository()).track(request)

    assert response.critical_deadlines[0].deadline_date == "2026-11-09"
    assert "5 ngày làm việc" in response.critical_deadlines[0].deadline_rule
    assert "khoản 1 Điều 104" in response.critical_deadlines[0].legal_reference


def test_rejects_completed_order_that_is_not_in_roadmap() -> None:
    with pytest.raises(ValidationError):
        make_request(completed_steps=[{"step_order": 99, "completed_at": datetime.now(UTC)}])


@pytest.mark.parametrize("procedure", ["hkd_suspension", "company_suspension"])
def test_suspension_deadline_is_left_unverified(procedure: str) -> None:
    request = make_request(
        procedure=procedure,
        steps=[{"step_order": 1, "phase": "SUSPENSION_SUBMISSION", "action": "Nộp thông báo"}],
        completed_steps=[],
    )

    alert = ProcessTrackerService(ProcessTrackerRepository()).track(request).critical_deadlines[0]

    assert alert.deadline_rule == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert alert.deadline_date == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert alert.days_remaining is None
