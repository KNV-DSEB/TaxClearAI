import pytest

from src.modules.procedure_roadmap.repository import ProcedureRoadmapRepository
from src.modules.procedure_roadmap.schemas import ProcedureCompareRequest, RoadmapRequest
from src.modules.procedure_roadmap.service import ProcedureRoadmapService


@pytest.fixture
def service() -> ProcedureRoadmapService:
    return ProcedureRoadmapService(ProcedureRoadmapRepository())


@pytest.mark.parametrize(
    ("segment", "target_action", "expected_phase"),
    [
        ("A1", "terminate", "REGISTRATION_RESULT"),
        ("A2", "terminate", "REGISTRATION_RESULT"),
        ("A3", "terminate", "REGISTRATION_RESULT"),
        ("B1", "terminate", "FINAL_RESULT"),
        ("B2", "terminate", "FINAL_RESULT"),
        ("A1", "convert_to_new_entity", "NEW_ENTITY_RESULT"),
        ("A2", "convert_to_new_entity", "NEW_ENTITY_RESULT"),
        ("A3", "convert_to_new_entity", "NEW_ENTITY_RESULT"),
        ("B1", "convert_to_new_entity", "POST_REGISTRATION"),
        ("B2", "convert_to_new_entity", "POST_REGISTRATION"),
    ],
)
def test_composes_ordered_steps_for_each_segment_and_goal(
    service: ProcedureRoadmapService,
    segment: str,
    target_action: str,
    expected_phase: str,
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment=segment, target_action=target_action))

    assert roadmap.steps[-1].phase == expected_phase
    assert [step.step_order for step in roadmap.steps] == list(range(1, len(roadmap.steps) + 1))
    assert all(step.action and step.agency and step.law_reference for step in roadmap.steps)
    assert all(step.expected_duration for step in roadmap.steps)


def test_hkd_closure_uses_current_commune_authority_and_tax_first(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment="A2", target_action="terminate"))
    phases = [step.phase for step in roadmap.steps]

    assert phases.index("TAX_SUBMISSION") < phases.index("REGISTRATION_SUBMISSION")
    assert "cấp xã" in roadmap.steps[5].agency
    assert "quận/huyện" not in " ".join(step.agency for step in roadmap.steps)


def test_same_name_new_household_requires_old_termination_result_first(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(
        RoadmapRequest(segment="A3", target_action="convert_to_new_entity")
    )
    phases = [step.phase for step in roadmap.steps]

    assert phases.index("REGISTRATION_RESULT") < phases.index("NEW_ENTITY_PRECONDITION")
    assert phases.index("NEW_ENTITY_PRECONDITION") < phases.index("NEW_ENTITY_SUBMISSION")


def test_segment_b1_keeps_zero_tax_activity_obligations_in_view(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment="B1", target_action="terminate"))

    assert "không mặc định được miễn nghĩa vụ thuế" in roadmap.steps[0].action


def test_b1_and_b2_termination_roadmaps_have_different_risk_steps(
    service: ProcedureRoadmapService,
) -> None:
    b1 = service.create_roadmap(RoadmapRequest(segment="B1", target_action="terminate"))
    b2 = service.create_roadmap(RoadmapRequest(segment="B2", target_action="terminate"))
    b1_text = " ".join(step.action for step in b1.steps)
    b2_text = " ".join(step.action for step in b2.steps)

    assert len(b2.steps) == len(b1.steps) + 4
    assert "lệ phí môn bài của những năm chưa nộp" in b1_text
    assert "VAT, TNDN, TNCN, nợ thuế, tiền phạt và BHXH" in b2_text
    assert "không tính tiền" in b2_text
    assert "khôi phục sổ sách kế toán và báo cáo tài chính" in b2_text
    assert "thanh lý, xử lý hàng tồn kho và đối chiếu công nợ" in b2_text
    expert_step = next(step for step in b2.steps if step.phase == "B2_EXPERT_SUPPORT")
    assert expert_step.can_self_do is False
    assert expert_step.law_reference == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert expert_step.expected_duration == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert b2.steps.index(expert_step) < next(
        index for index, step in enumerate(b2.steps) if step.phase == "FINAL_DOCUMENT_PREPARATION"
    )


def test_company_conversion_includes_alternative_transfer_path(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(
        RoadmapRequest(segment="B2", target_action="convert_to_new_entity")
    )
    alternative = roadmap.steps[0]

    assert alternative.phase == "ALTERNATIVE_PATH_SELECTION"
    assert "chuyển nhượng phần vốn góp/cổ phần" in alternative.action.lower()
    assert "nhiều thành viên, vốn góp lớn hoặc tranh chấp" in alternative.action
    assert alternative.law_reference == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert alternative.expected_duration == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
    assert alternative.can_self_do is False


def test_b2_company_conversion_adds_outstanding_and_expert_review_before_submission(
    service: ProcedureRoadmapService,
) -> None:
    b1 = service.create_roadmap(RoadmapRequest(segment="B1", target_action="convert_to_new_entity"))
    b2 = service.create_roadmap(RoadmapRequest(segment="B2", target_action="convert_to_new_entity"))
    new_phases = {
        "B2_CONVERSION_OUTSTANDING_SUMMARY",
        "B2_CONVERSION_LEGAL_REVIEW",
    }
    summary = next(step for step in b2.steps if step.phase == "B2_CONVERSION_OUTSTANDING_SUMMARY")
    review = next(step for step in b2.steps if step.phase == "B2_CONVERSION_LEGAL_REVIEW")
    b2_phases = [step.phase for step in b2.steps]

    assert len(b1.steps) == 6
    assert len(b2.steps) == 8
    assert len(b2.steps) > len(b1.steps)
    assert {phase for phase in b2_phases if phase.startswith("B2_CONVERSION_")} == new_phases
    assert b2_phases.index("B2_CONVERSION_OUTSTANDING_SUMMARY") < b2_phases.index("SUBMISSION")
    assert b2_phases.index("B2_CONVERSION_LEGAL_REVIEW") < b2_phases.index("SUBMISSION")
    assert [step.step_order for step in b2.steps] == list(range(1, len(b2.steps) + 1))
    assert all(
        term in summary.action for term in ("VAT", "TNDN", "TNCN", "nợ thuế", "tiền phạt", "BHXH")
    )
    assert "không tính tiền" in summary.action
    assert summary.can_self_do is True
    assert "nhiều thành viên, vốn góp lớn hoặc tranh chấp" in review.action
    assert review.can_self_do is False
    for step in (summary, review):
        assert step.law_reference == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
        assert step.expected_duration == "Chưa xác định căn cứ trong nguồn đã đồng bộ"


def test_a1_does_not_create_a_fictitious_hkd_termination_filing(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment="A1", target_action="terminate"))

    assert not any(step.phase == "REGISTRATION_SUBMISSION" for step in roadmap.steps)
    assert any("chưa từng được cấp đăng ký HKD" in step.action for step in roadmap.steps)


def test_company_conversion_does_not_route_through_dissolution(
    service: ProcedureRoadmapService,
) -> None:
    roadmap = service.create_roadmap(
        RoadmapRequest(segment="B2", target_action="convert_to_new_entity")
    )

    assert all(step.phase != "INITIAL_SUBMISSION" for step in roadmap.steps)
    assert all("dissolution" not in step.action.lower() for step in roadmap.steps)


@pytest.mark.parametrize("segment", ["A1", "A2", "A3", "B1", "B2"])
def test_suspension_steps_are_contiguous_and_use_placeholders(
    service: ProcedureRoadmapService, segment: str
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment=segment, target_action="suspend"))

    assert roadmap.steps
    assert [step.step_order for step in roadmap.steps] == list(range(1, len(roadmap.steps) + 1))
    assert all(
        step.law_reference == "Chưa xác định căn cứ trong nguồn đã đồng bộ"
        for step in roadmap.steps
    )


@pytest.mark.parametrize("target_action", ["terminate", "suspend", "convert_to_new_entity"])
def test_a3_has_expert_review_before_closing_submission(
    service: ProcedureRoadmapService, target_action: str
) -> None:
    a2 = service.create_roadmap(RoadmapRequest(segment="A2", target_action=target_action))
    a3 = service.create_roadmap(RoadmapRequest(segment="A3", target_action=target_action))
    phases = [step.phase for step in a3.steps]
    expert = next(step for step in a3.steps if step.phase == "A3_EXPERT_REVIEW")
    closing_submission = next(
        index
        for index, step in enumerate(a3.steps)
        if step.phase
        in {"REGISTRATION_SUBMISSION", "SUSPENSION_SUBMISSION", "NEW_ENTITY_SUBMISSION"}
    )

    assert a3.steps != a2.steps
    assert phases.index("A3_DECLARATION_RECONCILIATION") < phases.index("A3_EXPERT_REVIEW")
    assert phases.index("A3_EXPERT_REVIEW") < phases.index("A3_OUTSTANDING_OBLIGATIONS")
    assert a3.steps.index(expert) < closing_submission
    assert expert.can_self_do is False
    assert "không đánh giá mức độ sai lệch" in expert.action
    assert "không đề xuất cách xử lý" in expert.action


@pytest.mark.parametrize(
    ("segment", "expected"),
    [("A1", False), ("A2", False), ("A3", True), ("B1", False), ("B2", True)],
)
def test_roadmap_sets_needs_expert_by_segment(
    service: ProcedureRoadmapService, segment: str, expected: bool
) -> None:
    roadmap = service.create_roadmap(RoadmapRequest(segment=segment, target_action="terminate"))

    assert roadmap.needs_expert is expected


@pytest.mark.parametrize("segment", ["B1", "B2"])
def test_comparison_reuses_existing_checklists_and_preserves_boundary(
    service: ProcedureRoadmapService, segment: str
) -> None:
    comparison = service.compare(ProcedureCompareRequest(segment=segment, has_dispute=True))

    assert len(comparison.rows) == 5
    assert comparison.rows[1].dissolution
    assert comparison.rows[1].transfer_or_conversion
    assert "chuyên gia" in comparison.rows[-1].dissolution
    assert "không khuyến nghị chọn hướng nào" in comparison.recommendation_boundary
