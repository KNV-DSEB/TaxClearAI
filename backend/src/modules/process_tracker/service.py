from datetime import UTC, date, datetime, timedelta

from src.modules.process_tracker.repository import DeadlineRule, ProcessTrackerRepository
from src.modules.process_tracker.schemas import (
    DeadlineAlert,
    ProcessTrackerRequest,
    ProcessTrackerResponse,
    TrackedStep,
    UrgencyLevel,
)


class ProcessTrackerService:
    def __init__(self, repository: ProcessTrackerRepository) -> None:
        self._repository = repository

    def track(self, request: ProcessTrackerRequest) -> ProcessTrackerResponse:
        steps = sorted(request.steps, key=lambda step: step.step_order)
        completed_by_order = {item.step_order: item for item in request.completed_steps}
        done_steps = [step for step in steps if step.step_order in completed_by_order]
        pending_steps = [step for step in steps if step.step_order not in completed_by_order]
        progress = round(len(done_steps) * 100 / len(steps))
        last_completed = done_steps[-1].action if done_steps else None
        current = pending_steps[0] if pending_steps else None
        next_step = pending_steps[1] if len(pending_steps) > 1 else None
        current_stage = current.phase if current else "COMPLETED"
        next_action = (
            next_step.action
            if next_step
            else (
                "Quy trình đã hoàn thành."
                if current is None
                else "Không có bước kế tiếp trong bản đồ."
            )
        )
        reference_time = request.as_of or datetime.now(UTC)
        alerts = self._deadline_alerts(request, current, reference_time)

        return ProcessTrackerResponse(
            progress_percentage=progress,
            current_stage=current_stage,
            completed_steps=[step.action for step in done_steps],
            last_completed_step=last_completed,
            current_step=current.action if current else None,
            next_action=next_action,
            critical_deadlines=alerts,
            calculation_note=(
                "Tiến độ tính theo số bước đã đánh dấu hoàn tất / tổng số bước. Deadline được tính "
                "từ current_step_started_at; với mốc ngày làm việc, ngày nghỉ lễ chưa được "
                "đối chiếu với lịch nghỉ chính thức. Nếu ngày bắt đầu khác ngày sự kiện pháp lý, "
                "cập nhật lại "
                "mốc bắt đầu trước khi dùng ngày hạn ước tính."
            ),
        )

    def _deadline_alerts(
        self,
        request: ProcessTrackerRequest,
        current_step: TrackedStep | None,
        reference_time: datetime,
    ) -> list[DeadlineAlert]:
        if current_step is None:
            return []
        rules = self._repository.get_deadline_rules(request.procedure, current_step.phase)
        anchor_date = request.current_step_started_at.date()
        as_of_date = reference_time.date()
        return [self._make_alert(rule, anchor_date, as_of_date) for rule in rules]

    @classmethod
    def _make_alert(
        cls,
        rule: DeadlineRule,
        anchor_date: date,
        as_of_date: date,
    ) -> DeadlineAlert:
        if rule.duration is None:
            return DeadlineAlert(
                milestone=rule.milestone,
                deadline_rule="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                urgency_level=UrgencyLevel.NORMAL,
                deadline_date="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                days_remaining=None,
                legal_reference=rule.legal_reference,
            )
        due_date = cls._add_duration(anchor_date, rule.duration, rule.unit)
        days_remaining = (
            cls._business_days_between(as_of_date, due_date)
            if rule.unit == "business_days"
            else (due_date - as_of_date).days
        )
        overdue = as_of_date > due_date
        urgency = (
            UrgencyLevel.WARNING
            if overdue or days_remaining <= rule.warning_window
            else UrgencyLevel.NORMAL
        )
        rule_unit = "ngày làm việc" if rule.unit == "business_days" else "ngày"
        return DeadlineAlert(
            milestone=rule.milestone,
            deadline_rule=(
                f"Trong {rule.duration} {rule_unit} kể từ {rule.anchor_description}; "
                f"mốc bắt đầu theo dữ liệu tracker: {anchor_date.isoformat()}."
            ),
            urgency_level=urgency,
            deadline_date=due_date.isoformat(),
            days_remaining=days_remaining,
            legal_reference=rule.legal_reference,
        )

    @staticmethod
    def _add_duration(anchor: date, duration: int, unit: str) -> date:
        if unit == "calendar_days":
            return anchor + timedelta(days=duration)
        result = anchor
        counted = 0
        while counted < duration:
            result += timedelta(days=1)
            if result.weekday() < 5:
                counted += 1
        return result

    @staticmethod
    def _business_days_between(start: date, end: date) -> int:
        if end <= start:
            return (end - start).days
        current = start
        counted = 0
        while current < end:
            current += timedelta(days=1)
            if current.weekday() < 5:
                counted += 1
        return counted
