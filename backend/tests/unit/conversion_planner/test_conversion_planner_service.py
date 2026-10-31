from datetime import date

from src.modules.conversion_planner.repository import ConversionPlannerRepository
from src.modules.conversion_planner.schemas import (
    ConversionKind,
    ConversionPlanRequest,
    TaskState,
)
from src.modules.conversion_planner.service import (
    LEGAL_BASIS_PLACEHOLDER,
    ConversionPlannerService,
)
from src.modules.legal_library.repository import LegalLibraryRepository
from src.modules.legal_library.schemas import ApplicableProvision, LegalReference


class _LegalLibraryWithMockTransition(LegalLibraryRepository):
    def get_references(self, procedure, query):
        del procedure, query
        return [
            LegalReference(
                document_name="[TEST ONLY]",
                document_number="MOCK-TEST-ONLY",
                issuing_authority="[TEST ONLY]",
                issued_date=date(2026, 1, 1),
                effective_date=date(2026, 1, 1),
                effectiveness_status="[TEST ONLY]",
                applicable_provisions=[
                    ApplicableProvision(
                        article="Điều mẫu",
                        clause="Khoản mẫu",
                        regulated_action="Chuyển đổi loại hình doanh nghiệp (dữ liệu test).",
                    )
                ],
                summary="Metadata giả chỉ dùng trong unit test.",
                source_url="https://example.invalid/test-only",
            )
        ]


def _service() -> ConversionPlannerService:
    return ConversionPlannerService(ConversionPlannerRepository())


def _task(plan, lane_id: str, task_id: str):
    lane = next(item for item in plan.lanes if item.lane_id == lane_id)
    return next(item for item in lane.tasks if item.task_id == task_id)


def test_hkd_to_hkd_keeps_existing_hard_stop_and_dependency_order() -> None:
    request = ConversionPlanRequest.model_validate(
        {"current_model": "HKD", "desired_model": "HKD", "new_name_prepared": True}
    )

    plan = _service().plan(request)

    assert plan.conversion_kind == ConversionKind.HKD_TO_HKD
    assert plan.hard_stops[0].code == "OLD_HKD_STATUS_NOT_CLOSED"
    assert plan.hard_stops[0].active is True
    assert _task(plan, "close_old", "old_tax_settlement").depends_on == ["old_tax_review"]
    assert _task(plan, "close_old", "old_tax_close").depends_on == ["old_tax_settlement"]
    assert _task(plan, "close_old", "old_registration_close").depends_on == ["old_tax_close"]
    assert "HKD cũ" in plan.next_action
    assert "HKD→HKD" in plan.legal_note


def test_hkd_to_company_has_separate_stop_and_parallel_company_preparation() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "HKD",
            "desired_model": "COMPANY_LLC",
            "new_name_prepared": True,
            "new_address_prepared": True,
            "new_industry_prepared": True,
        }
    )

    plan = _service().plan(request)

    assert plan.conversion_kind == ConversionKind.HKD_TO_COMPANY
    assert plan.hard_stops[0].code == "OLD_HKD_TO_COMPANY_STATUS_REQUIRES_REVIEW"
    assert plan.hard_stops[0].active is True
    assert plan.hard_stops[0].legal_basis == LEGAL_BASIS_PLACEHOLDER
    assert "chuyên gia xác minh" in plan.hard_stops[0].legal_scope_note
    assert _task(plan, "close_old", "old_registration_close").depends_on == ["old_tax_close"]
    assert _task(plan, "open_new", "new_file").depends_on == [
        "new_name",
        "new_address",
        "new_industry",
    ]
    assert "công ty" in plan.next_action
    assert "Không coi đây là kết luận" in plan.legal_note
    assert plan.needs_expert is True


def test_hkd_to_company_stop_releases_only_after_close_and_expert_review() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "HKD",
            "desired_model": "COMPANY_JSC",
            "old_tax_id_termination_confirmed": True,
            "old_registration_termination_confirmed": True,
            "conversion_legal_review_confirmed": True,
            "new_name_prepared": True,
            "new_address_prepared": True,
            "new_industry_prepared": True,
        }
    )

    plan = _service().plan(request)

    assert plan.hard_stops[0].active is False
    assert "nộp" in plan.next_action
    assert _task(plan, "open_new", "new_file").status == TaskState.READY


def test_company_type_change_has_sequential_change_tasks_without_old_model_closure() -> None:
    request = ConversionPlanRequest.model_validate(
        {"current_model": "COMPANY_LLC", "desired_model": "COMPANY_JSC"}
    )

    plan = _service().plan(request)
    tasks = plan.lanes[0].tasks

    assert plan.conversion_kind == ConversionKind.COMPANY_TYPE_CHANGE
    assert plan.hard_stops[0].code == "COMPANY_TYPE_CHANGE_REQUIRES_VERIFICATION"
    assert plan.hard_stops[0].active is True
    assert plan.hard_stops[0].legal_basis == LEGAL_BASIS_PLACEHOLDER
    assert [task.task_id for task in tasks] == [
        "change_review",
        "conversion_resolution",
        "conversion_documents",
        "submit_company_change",
        "update_company_records",
    ]
    assert tasks[1].depends_on == ["change_review"]
    assert tasks[2].depends_on == ["conversion_resolution"]
    assert tasks[3].depends_on == ["conversion_documents"]
    assert tasks[4].depends_on == ["submit_company_change"]
    assert all("old_tax" not in task.task_id for task in tasks)
    assert "Không thực hiện đóng MST/giải thể" in plan.next_action
    assert "không tạo bước đóng MST" in plan.legal_note
    assert plan.needs_expert is True


def test_company_type_change_review_flag_unblocks_first_dependent_task() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "COMPANY_JSC",
            "desired_model": "COMPANY_LLC",
            "conversion_legal_review_confirmed": True,
        }
    )

    plan = _service().plan(request)

    assert plan.hard_stops[0].active is False
    assert plan.lanes[0].tasks[0].status == TaskState.COMPLETED
    assert plan.lanes[0].tasks[1].status == TaskState.READY
    assert plan.next_action == plan.lanes[0].tasks[1].action
    assert plan.needs_expert is False


def test_company_type_change_uses_matching_basis_from_legal_library() -> None:
    service = ConversionPlannerService(
        ConversionPlannerRepository(_LegalLibraryWithMockTransition())
    )
    request = ConversionPlanRequest.model_validate(
        {"current_model": "COMPANY_LLC", "desired_model": "COMPANY_JSC"}
    )

    plan = service.plan(request)

    assert plan.hard_stops[0].legal_basis == "MOCK-TEST-ONLY — Điều mẫu, Khoản mẫu"


def test_company_type_change_high_risk_flags_request_expert_review() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "COMPANY_LLC",
            "desired_model": "COMPANY_JSC",
            "has_multiple_members": True,
            "has_large_capital_contribution": True,
            "has_dispute": True,
        }
    )

    plan = _service().plan(request)

    assert plan.needs_expert is True


def test_legacy_request_shape_remains_accepted() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "HKD",
            "desired_model": "HKD",
            "new_name_prepared": True,
            "new_address_prepared": True,
            "new_industry_prepared": True,
        }
    )

    plan = _service().plan(request)

    assert plan.conversion_kind == ConversionKind.HKD_TO_HKD
    assert plan.lanes[1].tasks[-1].status == TaskState.READY


def test_hkd_stop_releases_after_old_tax_and_registration_are_confirmed() -> None:
    request = ConversionPlanRequest.model_validate(
        {
            "current_model": "HKD",
            "desired_model": "HKD",
            "old_tax_obligations_settled": True,
            "old_tax_id_termination_confirmed": True,
            "old_registration_termination_confirmed": True,
        }
    )

    plan = _service().plan(request)

    assert plan.hard_stops[0].active is False
    assert plan.lanes[0].progress_percentage == 100
