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
    assert "chưa" in summary.notice.lower()


def test_household_receives_scope_notice_and_no_company_checklist():
    data = answers(businessType="household")
    assert build_summary(data).scope == "out_of_scope"
    assert prepare_checklist(data, uuid4()) == []


def test_missing_revenue_evidence_is_not_classified_as_b2():
    assert build_summary(answers(revenueStatus="unknown")).scope == "needs_confirmation"


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
