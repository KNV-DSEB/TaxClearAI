import asyncio

import pytest

from src.modules.legal_survey.repository import LegalSurveyRepository
from src.modules.legal_survey.schemas import (
    RiskFlag,
    Segment,
    SituationSuggestion,
    SurveyAIStatus,
    SurveyAnswers,
)
from src.modules.legal_survey.service import LegalSurveyService


def answers(**overrides: object) -> SurveyAnswers:
    values: dict[str, object] = {
        "entity_type": "HKD",
        "registration_status": "registered",
        "tax_id_status": "active",
        "operating_status": "currently_active",
        "declaration_status": "filed_all",
        "declaration_matches_reality": "yes",
        "invoice_status": "none",
        "bank_status": "matches",
        "unpaid_obligations": ["none"],
        "tax_audit_notice": "no",
        "target_action": "terminate",
    }
    values.update(overrides)
    return SurveyAnswers.model_validate(values)


@pytest.fixture
def service() -> LegalSurveyService:
    return LegalSurveyService(LegalSurveyRepository())


def classify(service: LegalSurveyService, payload: SurveyAnswers):
    return asyncio.run(service.classify(payload))


class FakeSituationClassifier:
    def __init__(
        self, suggestion: SituationSuggestion | None = None, error: Exception | None = None
    ):
        self.suggestion = suggestion
        self.error = error
        self.calls = 0

    async def classify(self, answers: SurveyAnswers, question_ids: set[str]):
        del answers, question_ids
        self.calls += 1
        if self.error:
            raise self.error
        return self.suggestion


@pytest.mark.parametrize(
    ("overrides", "expected_segment"),
    [
        (
            {
                "registration_status": "not_registered",
                "operating_status": "currently_active",
                "declaration_status": "not_filed",
            },
            "A1",
        ),
        ({"declaration_status": "not_filed"}, "A2"),
        ({"declaration_matches_reality": "no"}, "A3"),
        (
            {
                "entity_type": "DN",
                "registration_status": "registered",
                "operating_status": "never_had_revenue",
                "declaration_status": "not_filed",
            },
            "B1",
        ),
        (
            {
                "entity_type": "DN",
                "operating_status": "abandoned_after_operation",
                "declaration_status": "filed_some",
                "unpaid_obligations": ["unpaid_tax", "unpaid_social_security"],
            },
            "B2",
        ),
    ],
)
def test_classifies_each_defined_segment(
    service: LegalSurveyService, overrides: dict[str, object], expected_segment: str
) -> None:
    result = classify(service, answers(**overrides))

    assert result.determined_segment == expected_segment
    assert 0.0 <= result.confidence_score <= 1.0


def test_maps_risks_and_summary_profile(service: LegalSurveyService) -> None:
    result = classify(
        service,
        answers(
            declaration_matches_reality="no",
            invoice_status="unresolved",
            bank_status="mismatch",
            unpaid_obligations=["unpaid_social_security"],
            tax_audit_notice="yes",
            target_action="convert_to_new_entity",
        ),
    )

    assert result.risk_flags == [
        "has_tax_audit_notice",
        "bank_account_mismatch",
        "unresolved_invoices",
        "unpaid_social_security",
    ]
    assert result.summary_profile.model_dump(mode="json") == {
        "entity_type": "HKD",
        "has_registration": True,
        "has_declaration": True,
        "has_discrepancy": True,
        "has_debt": True,
        "target_action": "convert_to_new_entity",
    }


def test_unknown_answers_reduce_confidence(service: LegalSurveyService) -> None:
    certain = classify(service, answers(declaration_matches_reality="no"))
    uncertain = classify(
        service,
        answers(
            tax_id_status="unknown",
            declaration_matches_reality="unknown",
            invoice_status="unknown",
            bank_status="not_reviewed",
            unpaid_obligations=None,
            tax_audit_notice="unknown",
        ),
    )

    assert uncertain.determined_segment == certain.determined_segment
    assert uncertain.confidence_score < certain.confidence_score


def test_registered_hkd_with_no_matching_issue_signals_no_exact_fit(
    service: LegalSurveyService,
) -> None:
    result = classify(service, answers())

    assert result.determined_segment == "A3"
    assert result.confidence_score < 0.5


def test_obligation_sentinels_cannot_be_combined() -> None:
    with pytest.raises(ValueError):
        answers(unpaid_obligations=["none", "unpaid_tax"])


def test_diagnostic_signals_add_flags_without_changing_segment(service: LegalSurveyService) -> None:
    baseline = classify(
        service,
        answers(
            entity_type="DN",
            operating_status="never_had_revenue",
            declaration_status="not_filed",
        ),
    )
    enriched = classify(
        service,
        answers(
            entity_type="DN",
            operating_status="never_had_revenue",
            declaration_status="not_filed",
            business_start_period="before_2012",
            has_assets_or_inventory="yes",
        ),
    )

    assert baseline.determined_segment == enriched.determined_segment == "B1"
    assert "pre_2012_entity" in enriched.risk_flags
    assert "assets_without_revenue" in enriched.risk_flags
    assert enriched.confidence_score > baseline.confidence_score


def test_long_inactive_answer_adds_secondary_flag(service: LegalSurveyService) -> None:
    result = classify(
        service,
        answers(
            entity_type="DN",
            operating_status="abandoned_after_operation",
            declaration_status="filed_some",
            idle_duration="over_3y",
        ),
    )

    assert result.determined_segment == "B2"
    assert "long_inactive" in result.risk_flags


def test_ai_agreement_returns_one_candidate_and_disclosure() -> None:
    classifier = FakeSituationClassifier(
        SituationSuggestion(
            suggested_segment=Segment.A1,
            confidence=0.9,
            reasons=["entity_type=HKD"],
        )
    )
    service = LegalSurveyService(LegalSurveyRepository(), classifier, survey_ai_enabled=True)

    result = classify(
        service,
        answers(
            registration_status="not_registered",
            operating_status="currently_active",
            declaration_status="not_filed",
        ),
    )

    assert result.rules_segment == result.determined_segment == Segment.A1
    assert result.ai_status == SurveyAIStatus.OK
    assert result.agreement == "agree"
    assert result.candidates == [Segment.A1]
    assert result.needs_user_confirmation is False
    assert "bạn là người xác nhận" in result.ai_disclosure


def test_ai_disagreement_never_overwrites_rules_and_unions_risks() -> None:
    classifier = FakeSituationClassifier(
        SituationSuggestion(
            suggested_segment=Segment.A1,
            confidence=0.95,
            reasons=["entity_type=DN"],
            risk_signals=[RiskFlag.HAS_TAX_AUDIT_NOTICE],
        )
    )
    service = LegalSurveyService(LegalSurveyRepository(), classifier, survey_ai_enabled=True)

    result = classify(
        service,
        answers(entity_type="DN", operating_status="never_had_revenue"),
    )

    assert result.rules_segment == result.determined_segment == Segment.B1
    assert result.ai_suggestion is not None
    assert result.agreement == "disagree"
    assert result.candidates == [Segment.B1, Segment.A1]
    assert result.needs_user_confirmation is True
    assert RiskFlag.HAS_TAX_AUDIT_NOTICE in result.risk_flags
    assert result.needs_expert is True


def test_low_ai_confidence_or_missing_answers_requires_confirmation() -> None:
    classifier = FakeSituationClassifier(
        SituationSuggestion(
            suggested_segment=Segment.A1,
            confidence=0.4,
            reasons=["entity_type=HKD"],
            missing_info=["invoice_status"],
        )
    )
    service = LegalSurveyService(LegalSurveyRepository(), classifier, survey_ai_enabled=True)

    result = classify(
        service,
        answers(
            registration_status="not_registered",
            operating_status="currently_active",
            declaration_status="not_filed",
        ),
    )

    assert result.agreement == "agree"
    assert result.needs_user_confirmation is True


def test_classifier_failure_uses_rules_and_marks_ai_unavailable() -> None:
    classifier = FakeSituationClassifier(error=TimeoutError())
    service = LegalSurveyService(LegalSurveyRepository(), classifier, survey_ai_enabled=True)

    result = classify(service, answers(entity_type="DN", operating_status="never_had_revenue"))

    assert result.determined_segment == Segment.B1
    assert result.rules_segment == Segment.B1
    assert result.ai_suggestion is None
    assert result.ai_status == SurveyAIStatus.UNAVAILABLE
    assert result.agreement == "ai_not_used"


def test_missing_key_marks_ai_unavailable_but_preserves_rules() -> None:
    service = LegalSurveyService(LegalSurveyRepository(), survey_ai_enabled=True)

    result = classify(service, answers(entity_type="DN", operating_status="never_had_revenue"))

    assert result.determined_segment == Segment.B1
    assert result.ai_status == SurveyAIStatus.UNAVAILABLE
    assert result.ai_suggestion is None


def test_disabled_ai_marks_status_without_changing_rules() -> None:
    service = LegalSurveyService(LegalSurveyRepository(), survey_ai_enabled=False)

    result = classify(service, answers(entity_type="DN", operating_status="never_had_revenue"))

    assert result.determined_segment == Segment.B1
    assert result.ai_status == SurveyAIStatus.DISABLED


def test_rule_risk_flags_force_expert_even_when_ai_says_no_risk() -> None:
    classifier = FakeSituationClassifier(
        SituationSuggestion(
            suggested_segment=Segment.B1,
            confidence=0.9,
            reasons=["entity_type=DN"],
            risk_signals=[],
        )
    )
    service = LegalSurveyService(LegalSurveyRepository(), classifier, survey_ai_enabled=True)

    result = classify(
        service,
        answers(
            entity_type="DN",
            operating_status="never_had_revenue",
            tax_audit_notice="yes",
        ),
    )

    assert RiskFlag.HAS_TAX_AUDIT_NOTICE in result.risk_flags
    assert result.needs_expert is True
