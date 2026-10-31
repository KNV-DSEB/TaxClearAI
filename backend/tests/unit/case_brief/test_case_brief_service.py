from src.modules.case_brief.repository import CaseBriefRepository
from src.modules.case_brief.schemas import CaseBriefRequest, CaseSegment
from src.modules.case_brief.service import CaseBriefService


def test_generates_b2_brief_and_keeps_complex_cost_caveat() -> None:
    request = CaseBriefRequest.model_validate(
        {
            "diagnosis": {
                "segment": "B2",
                "entity_type": "Doanh nghiệp nhỏ",
                "procedure": "Giải thể doanh nghiệp",
                "target_action": "terminate",
                "risk_flags": ["unresolved_invoices", "unpaid_social_security"],
                "blockers": ["Còn hóa đơn điện tử chưa xử lý"],
                "notes": [],
            },
            "user_questions": ["phạm vi này gồm những gì?"],
        }
    )

    result = CaseBriefService(CaseBriefRepository()).generate(request)

    assert result.case_classification.startswith("B2")
    assert len(result.main_blockers) == 3
    assert any("lao động/BHXH" in task for task in result.scope_of_work["expert_to_do"])
    assert result.estimated_cost.minimum is None
    assert result.estimated_cost.maximum is None
    assert result.estimated_cost.service_fee.minimum is None
    assert result.estimated_cost.service_fee.maximum is None
    assert result.estimated_cost.quote_requires_survey is True
    assert "khảo sát hồ sơ thực tế" in result.estimated_cost.complexity_note
    assert "hàng tỷ đồng" in result.estimated_cost.state_payments_note
    assert any("phạm vi này" in question for question in result.expert_interview_questions)


def test_redacts_common_identifiers_from_free_text() -> None:
    request = CaseBriefRequest.model_validate(
        {
            "diagnosis": {
                "segment": "A3",
                "entity_type": "HKD",
                "procedure": "Chấm dứt hoạt động",
                "target_action": "terminate",
                "risk_flags": [],
                "blockers": [
                    "Chủ hộ: Nguyễn Văn An, MST: 0123456789, số gọi 0912345678, "
                    "email a@example.vn; "
                    "người liên hệ Nguyễn Văn Bình"
                ],
                "notes": [],
            }
        }
    )

    result = CaseBriefService(CaseBriefRepository()).generate(request)
    brief_text = " ".join(result.main_blockers)

    assert "Nguyễn Văn An" not in brief_text
    assert "0123456789" not in brief_text
    assert "0912345678" not in brief_text
    assert "a@example.vn" not in brief_text
    assert "[email đã ẩn]" in brief_text


def test_cost_references_separate_service_fees_from_state_payments() -> None:
    repository = CaseBriefRepository()
    hkd = repository.get_cost_reference(CaseSegment.A2)
    b1 = repository.get_cost_reference(CaseSegment.B1)

    assert hkd.minimum == 5_000_000
    assert hkd.maximum is None
    assert "không ước tính" in hkd.state_payments_note
    assert b1.service_fee_minimum == 11_500_000
    assert b1.service_fee_maximum == 19_500_000
    assert "1.500.000–4.500.000" in b1.service_fee_note
    assert "10.000.000–15.000.000" in b1.service_fee_note
    assert "15–45 ngày" in b1.complexity_note
    assert "30.000.000–80.000.000" in b1.state_payments_note
    assert "150.000.000" in b1.state_payments_note
    assert b1.sources == ("Ban cố vấn dự án (báo giá tham khảo)",)
