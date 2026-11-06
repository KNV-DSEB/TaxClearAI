from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.core.errors import ApplicationError
from src.modules.assessments.content import QUESTIONS, get_questionnaire, is_visible
from src.modules.assessments.schemas import Answers
from src.modules.assessments.service import (
    build_summary,
    normalize_answers,
    prepare_checklist,
)
from tests.fixtures import COMPANY_ANSWERS, HOUSEHOLD_ANSWERS, company, household


def visible_ids(answers: dict) -> list[str]:
    return [question.id for question in QUESTIONS if is_visible(question, answers)]


def checklist_codes(answers: dict) -> list[str]:
    return [item.code for item in prepare_checklist(answers, uuid4())]


def test_classification_follows_procedure_and_business_type():
    assert build_summary(company(hasRevenue="yes")).scope == "b2"
    assert build_summary(company(hasRevenue="no")).scope == "b1"
    assert build_summary(household()).scope == "household"
    assert build_summary(company(procedure="suspension")).scope == "out_of_scope"
    assert build_summary(household(procedure="conversion")).scope == "out_of_scope"


def test_out_of_scope_procedures_get_no_checklist_but_a_clear_reason():
    answers = company(procedure="conversion")
    assert prepare_checklist(answers, uuid4()) == []
    assert any(
        "tạm ngừng hoặc chuyển đổi" in text for text in build_summary(answers).review_reasons
    )


def test_company_asks_company_questions_and_never_household_ones():
    ids = visible_ids(company())
    assert {
        "dnType",
        "dnRegistry",
        "dnDecision",
        "dnDebtGuarantee",
        "dnRecords",
        "dnTaxDebt",
    } <= set(ids)
    assert not any(question_id.startswith("hh") for question_id in ids)


def test_household_asks_household_questions_and_never_company_ones():
    ids = visible_ids(household())
    assert {"hhProvince", "hhLocations", "hhEmployees", "hhInvoiceSystem"} <= set(ids)
    assert not any(question_id.startswith("dn") for question_id in ids)


def test_dissolution_only_questions_are_skipped_for_other_procedures():
    ids = visible_ids(company(procedure="suspension"))
    assert "dnDecision" not in ids and "dnDebtGuarantee" not in ids and "dnApprover" not in ids
    assert "dnRecords" in ids


def test_follow_up_fields_appear_only_after_their_trigger_answer():
    assert "lastRevenue" in visible_ids(company(hasRevenue="yes"))
    assert "lastRevenue" not in visible_ids(company(hasRevenue="no"))
    assert "dnRevenueAmount" not in visible_ids(company(dnRevenue="no"))
    assert "sectorOther" in visible_ids(company(sector="other", sectorOther="Vận tải"))
    assert "sectorOther" not in visible_ids(company(sector="trade"))


def test_answers_of_questions_that_do_not_apply_are_not_stored():
    stale = company(hasRevenue="no", lastRevenue="tháng 3/2020", hhProvince="Hà Nội")
    assert stale["lastRevenue"] is None
    assert stale["hhProvince"] is None


def test_required_questions_must_be_answered():
    with pytest.raises(ApplicationError) as caught:
        household(hhProvince=None)
    assert caught.value.status == 422
    with pytest.raises(ApplicationError):
        company(sector="other", sectorOther=None)


def test_summary_lists_unknown_answers_and_only_applicable_questions():
    summary = build_summary(company(dnDecision="unknown", recordsAccess="unknown_location"))
    assert any(
        text.startswith("Bạn có thể truy xuất hồ sơ không?") for text in summary.unknown_facts
    )
    assert any("quyết định hoặc nghị quyết giải thể" in text for text in summary.unknown_facts)
    texts = summary.known_facts + summary.unknown_facts
    assert not any("Hộ kinh doanh" in text.split(" — ")[0] for text in texts)
    assert "tổng hợp câu trả lời" in summary.notice.lower()


def test_risk_flags_only_ask_for_verification_and_do_not_conclude():
    summary = build_summary(
        company(dnDebtGuarantee="no", dnTaxDebt="yes", operatingStatus="forced", dnRecords="lost")
    )
    assert len(summary.review_reasons) >= 4
    assert all("vi phạm" not in reason.lower() for reason in summary.review_reasons)


def test_company_checklist_adds_items_only_when_answers_point_to_them():
    base = checklist_codes(company(dnDebtGuarantee="yes", dnTaxDebt="no", dnRecords="complete"))
    flagged = checklist_codes(company(dnDebtGuarantee="no", dnTaxDebt="yes", dnRecords="lost"))
    assert len(base) == 19
    assert set(flagged) - set(base) == {"debt_plan", "tax_debt_confirmation", "record_recovery"}


def test_household_checklist_adds_items_from_its_own_answers():
    base = checklist_codes(household())
    assert base == [
        "household_registration",
        "tax_id_termination",
        "household_termination_notice",
        "tax_obligation_confirmation",
    ]
    busy = checklist_codes(
        household(
            hhTaxObligation="yes",
            hhConditional="yes",
            hhEmployees="unresolved",
            hhInvoiceSystem="inaccessible",
            hhLocations="many",
        )
    )
    assert set(busy) - set(base) == {
        "missing_tax_returns",
        "licenses",
        "labor_rights",
        "invoice_data",
        "locations",
    }


def test_draft_checklist_does_not_claim_documents_are_mandatory_or_available():
    items = prepare_checklist(company(), uuid4())
    assert items
    assert all(item.status == "needs_verification" for item in items)
    assert all(item.review_status == "draft" for item in items)


@pytest.mark.parametrize(
    "changes",
    [
        {"establishedYear": 1800},
        {"hhRevenueEstimate": -5},
        {"ownerId": str(uuid4())},
        {"businessType": "unknown"},
        {"lastRevenue": "liên hệ 0901 234 567"},
        {"dnRegistry": "Hà Nội, mã số thuế 0123456789"},
        {"sectorOther": "khach@example.com"},
    ],
)
def test_invalid_client_owned_or_identifying_fields_are_rejected(changes):
    with pytest.raises(ValidationError):
        Answers.model_validate(COMPANY_ANSWERS | HOUSEHOLD_ANSWERS | changes)


def test_questionnaire_is_a_single_source_of_truth_for_the_form():
    questionnaire = get_questionnaire()
    assert questionnaire.version == "groups-draft-3"
    kinds = {question.kind for question in questionnaire.questions}
    assert kinds == {"choice", "text", "number", "year"}
    by_id = {question.id: question for question in questionnaire.questions}
    assert by_id["hhRevenueEstimate"].unit == "đồng"
    assert by_id["dnRegistry"].help and "mã số" in by_id["dnRegistry"].help
    assert all(
        question.options for question in questionnaire.questions if question.kind == "choice"
    )


def test_normalize_keeps_optional_fill_ins_blank_instead_of_inventing_values():
    answers = household()
    assert answers["hhRevenueEstimate"] is None
    assert normalize_answers(Answers.model_validate(HOUSEHOLD_ANSWERS))["hhRevenueEstimate"] is None
