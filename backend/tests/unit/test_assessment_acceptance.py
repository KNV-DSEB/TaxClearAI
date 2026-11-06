from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.modules.assessments.schemas import Answers
from src.modules.assessments.service import build_summary, prepare_checklist


def answers(**changes: object) -> Answers:
    payload: dict[str, object] = {
        "businessType": "company",
        "goal": "dissolution",
        "establishedYear": 2010,
        "revenueStatus": "yes",
        "revenueStartedYear": 2011,
        "filingStatus": "unknown",
        "recordsStatus": "partial",
        "taxNoticeStatus": "unknown",
        "laborInsuranceStatus": "unknown",
        "assetsInventoryStatus": "yes",
        "receivablesPayablesStatus": "unknown",
    }
    return Answers.model_validate(payload | changes)


def test_unknown_answers_remain_unknown_in_summary():
    summary = build_summary(answers())
    assert summary.scope == "b2"
    assert summary.unknown_facts
    assert summary.review_reasons
    assert "tổng hợp câu trả lời" in summary.notice.lower()


def test_registered_household_defaults_to_a2_checklist_and_unregistered_maps_to_a1():
    registered = answers(businessType="household", registrationStatus="yes")
    assert build_summary(registered).scope == "a2"
    assert len(prepare_checklist(registered, uuid4())) == 5

    unregistered = answers(businessType="household", registrationStatus="no")
    assert build_summary(unregistered).scope == "a1"
    assert len(prepare_checklist(unregistered, uuid4())) == 3


def test_missing_revenue_evidence_is_not_classified_as_b2():
    assert build_summary(answers(revenueStatus="unknown")).scope == "needs_confirmation"


def test_classification_all_five_groups():
    cases = [
        (answers(businessType="household", registrationStatus="no"), "a1", 3),
        (
            answers(
                businessType="household",
                registrationStatus="yes",
                filingStatus="incomplete",
            ),
            "a2",
            5,
        ),
        (
            answers(
                businessType="household",
                registrationStatus="yes",
                filingStatus="complete",
                taxNoticeStatus="yes",
            ),
            "a3",
            4,
        ),
        (
            answers(
                businessType="company",
                revenueStatus="no",
                revenueStartedYear=None,
            ),
            "b1",
            5,
        ),
        (answers(businessType="company", revenueStatus="yes"), "b2", 19),
    ]

    for data, expected_scope, expected_count in cases:
        assert build_summary(data).scope == expected_scope
        assert len(prepare_checklist(data, uuid4())) == expected_count


def test_draft_checklist_does_not_claim_documents_are_mandatory_or_available():
    items = prepare_checklist(answers(), uuid4())
    assert 1 <= len(items) <= 19
    assert all(item.status == "needs_verification" for item in items)
    assert all(item.review_status == "draft" for item in items)


@pytest.mark.parametrize(
    "changes",
    [
        {"revenueStartedYear": 2000},
        {"establishedYear": 1800},
        {"revenueStatus": "no", "revenueStartedYear": 2011},
        {"ownerId": str(uuid4())},
    ],
)
def test_invalid_or_client_owned_fields_are_rejected(changes):
    with pytest.raises(ValidationError):
        answers(**changes)


HOUSEHOLD_ONLY = ("Hộ kinh doanh đã đăng ký kinh doanh chưa?", "Mục tiêu đối với hộ kinh doanh")
COMPANY_ONLY = ("Doanh nghiệp được thành lập năm nào?", "Doanh nghiệp còn vấn đề lao động")


def mentioned(summary, labels):
    texts = summary.known_facts + summary.unknown_facts
    return [label for label in labels if any(text.startswith(label) for text in texts)]


def test_company_summary_does_not_list_household_questions():
    summary = build_summary(answers())
    assert mentioned(summary, HOUSEHOLD_ONLY) == []
    assert mentioned(summary, COMPANY_ONLY)


def test_household_summary_does_not_list_company_questions():
    household = answers(
        businessType="household",
        registrationStatus="yes",
        householdGoal="stop",
        filingStatus="incomplete",
        establishedYear=None,
        revenueStartedYear=None,
        revenueStatus="unknown",
    )
    summary = build_summary(household)
    assert summary.scope == "a2"
    assert mentioned(summary, COMPANY_ONLY) == []
    assert mentioned(summary, HOUSEHOLD_ONLY)


def test_questionnaire_exposes_show_conditions_and_clear_registration_labels():
    from src.modules.assessments.content import get_questionnaire, is_visible

    questions = {question.id: question for question in get_questionnaire().questions}
    assert questions["registrationStatus"].show_if == {"businessType": ["household"]}
    assert questions["businessType"].show_if is None
    labels = [option.label for option in questions["registrationStatus"].options]
    assert labels == ["Đã đăng ký", "Chưa đăng ký", "Chưa biết"]
    assert not is_visible(questions["registrationStatus"], {"businessType": "company"})
    assert is_visible(questions["registrationStatus"], {"businessType": "household"})
    assert not is_visible(
        questions["revenueStartedYear"], {"businessType": "company", "revenueStatus": "no"}
    )
