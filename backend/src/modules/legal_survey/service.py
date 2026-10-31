from src.modules.legal_survey.ai_classifier import SituationClassifier
from src.modules.legal_survey.repository import LegalSurveyRepository
from src.modules.legal_survey.schemas import (
    BusinessStartPeriod,
    ChatContextResponse,
    ClassificationResponse,
    DeclarationStatus,
    EntityType,
    IdleDuration,
    InvoiceStatus,
    Obligation,
    OperatingStatus,
    RegistrationStatus,
    RiskFlag,
    Segment,
    SituationSuggestion,
    SummaryProfile,
    SurveyAIAgreement,
    SurveyAIStatus,
    SurveyAnswers,
    SurveyQuestion,
    TaxIdStatus,
    YesNoUnknown,
)


class LegalSurveyService:
    def __init__(
        self,
        legal_survey_repository: LegalSurveyRepository,
        situation_classifier: SituationClassifier | None = None,
        *,
        survey_ai_enabled: bool = False,
    ) -> None:
        self._legal_survey_repository = legal_survey_repository
        self._situation_classifier = situation_classifier
        self._survey_ai_enabled = survey_ai_enabled

    def get_questions(self) -> list[SurveyQuestion]:
        return self._legal_survey_repository.get_questions()

    async def classify(self, answers: SurveyAnswers) -> ClassificationResponse:
        segment, confidence = self._determine_segment(answers)
        obligations = answers.unpaid_obligations or []
        flags: list[RiskFlag] = []
        if answers.tax_audit_notice == YesNoUnknown.YES:
            flags.append(RiskFlag.HAS_TAX_AUDIT_NOTICE)
        if answers.bank_status == "mismatch":
            flags.append(RiskFlag.BANK_ACCOUNT_MISMATCH)
        if (
            answers.invoice_status == InvoiceStatus.UNRESOLVED
            or Obligation.UNRESOLVED_INVOICES in obligations
        ):
            flags.append(RiskFlag.UNRESOLVED_INVOICES)
        if Obligation.UNPAID_SOCIAL_SECURITY in obligations:
            flags.append(RiskFlag.UNPAID_SOCIAL_SECURITY)
        if answers.idle_duration == IdleDuration.OVER_3Y:
            flags.append(RiskFlag.LONG_INACTIVE)
        if answers.business_start_period == BusinessStartPeriod.BEFORE_2012:
            flags.append(RiskFlag.PRE_2012_ENTITY)
        if (
            answers.entity_type == EntityType.DN
            and answers.operating_status == OperatingStatus.NEVER_HAD_REVENUE
            and answers.has_assets_or_inventory == YesNoUnknown.YES
        ):
            flags.append(RiskFlag.ASSETS_WITHOUT_REVENUE)

        has_registration = answers.registration_status == RegistrationStatus.REGISTERED
        has_declaration = answers.declaration_status in {
            DeclarationStatus.FILED_ALL,
            DeclarationStatus.FILED_SOME,
        }
        has_discrepancy = (
            answers.declaration_matches_reality == YesNoUnknown.NO
            or answers.bank_status == "mismatch"
        )
        has_debt = any(item not in {Obligation.NONE, Obligation.UNKNOWN} for item in obligations)

        if answers.idle_duration != IdleDuration.UNKNOWN:
            confidence = min(1.0, confidence + 0.02)
        if answers.business_start_period != BusinessStartPeriod.UNKNOWN:
            confidence = min(1.0, confidence + 0.02)

        suggestion: SituationSuggestion | None = None
        ai_status = SurveyAIStatus.DISABLED
        if self._survey_ai_enabled:
            ai_status = SurveyAIStatus.UNAVAILABLE
            if self._situation_classifier is not None:
                try:
                    question_ids = {question.id for question in self.get_questions()}
                    suggestion = await self._situation_classifier.classify(answers, question_ids)
                except Exception:
                    ai_status = SurveyAIStatus.UNAVAILABLE
                else:
                    ai_status = (
                        SurveyAIStatus.OK if suggestion is not None else SurveyAIStatus.REJECTED
                    )

        final_flags = list(flags)
        if suggestion is not None:
            final_flags.extend(flag for flag in suggestion.risk_signals if flag not in final_flags)

        agreement = SurveyAIAgreement.AI_NOT_USED
        candidates = [segment]
        needs_user_confirmation = confidence < 0.6
        if suggestion is not None:
            if suggestion.suggested_segment == segment:
                agreement = SurveyAIAgreement.AGREE
            else:
                agreement = SurveyAIAgreement.DISAGREE
                candidates.append(suggestion.suggested_segment)
                needs_user_confirmation = True
            needs_user_confirmation = (
                needs_user_confirmation
                or suggestion.confidence < 0.6
                or bool(suggestion.missing_info)
            )

        expert_flags = {
            RiskFlag.HAS_TAX_AUDIT_NOTICE,
            RiskFlag.BANK_ACCOUNT_MISMATCH,
            RiskFlag.UNRESOLVED_INVOICES,
            RiskFlag.UNPAID_SOCIAL_SECURITY,
            RiskFlag.LONG_INACTIVE,
            RiskFlag.PRE_2012_ENTITY,
            RiskFlag.ASSETS_WITHOUT_REVENUE,
        }
        needs_expert = (
            has_debt
            or has_discrepancy
            or any(flag in expert_flags for flag in final_flags)
            or segment in {Segment.A3, Segment.B2}
            or (suggestion is not None and suggestion.suggested_segment in {Segment.A3, Segment.B2})
        )

        return ClassificationResponse(
            determined_segment=segment,
            confidence_score=confidence,
            risk_flags=final_flags,
            summary_profile=SummaryProfile(
                entity_type=answers.entity_type,
                has_registration=has_registration,
                has_declaration=has_declaration,
                has_discrepancy=has_discrepancy,
                has_debt=has_debt,
                target_action=answers.target_action,
            ),
            rules_segment=segment,
            ai_suggestion=suggestion,
            ai_status=ai_status,
            agreement=agreement,
            needs_user_confirmation=needs_user_confirmation,
            candidates=candidates,
            needs_expert=needs_expert,
        )

    @staticmethod
    def chat_context(classification: ClassificationResponse) -> ChatContextResponse:
        flags = {flag.value: True for flag in classification.risk_flags}
        summary = classification.summary_profile
        return ChatContextResponse(
            context_flags={
                "co_thong_bao_thue": "has_tax_audit_notice" in flags,
                "co_sai_lech_so_lieu": summary.has_discrepancy,
                "co_no": summary.has_debt,
                "co_hoa_don_ton": "unresolved_invoices" in flags,
                "co_bhxh_no": "unpaid_social_security" in flags,
            }
        )

    @staticmethod
    def _determine_segment(answers: SurveyAnswers) -> tuple[Segment, float]:
        if answers.entity_type == EntityType.HKD:
            if (
                answers.registration_status == RegistrationStatus.NOT_REGISTERED
                and answers.operating_status == OperatingStatus.CURRENTLY_ACTIVE
            ):
                segment, base = Segment.A1, 0.96
            elif (
                answers.registration_status == RegistrationStatus.REGISTERED
                and answers.declaration_status == DeclarationStatus.NOT_FILED
            ):
                segment, base = Segment.A2, 0.96
            elif (
                answers.registration_status == RegistrationStatus.REGISTERED
                and answers.declaration_status
                in {DeclarationStatus.FILED_ALL, DeclarationStatus.FILED_SOME}
                and (
                    answers.declaration_matches_reality == YesNoUnknown.NO
                    or answers.bank_status == "mismatch"
                )
            ):
                segment, base = Segment.A3, 0.92
            elif (
                answers.registration_status == RegistrationStatus.REGISTERED
                and answers.declaration_status == DeclarationStatus.FILED_SOME
            ):
                segment, base = Segment.A3, 0.58
            elif answers.registration_status == RegistrationStatus.NOT_REGISTERED:
                segment, base = Segment.A1, 0.45
            elif answers.registration_status == RegistrationStatus.REGISTERED:
                # The five-segment model has no compliant HKD segment; A3 is the closest
                # declared-HKD bucket and the low score signals that no exact fit exists.
                segment, base = Segment.A3, 0.38
            else:
                segment, base = Segment.A1, 0.25
        elif answers.operating_status == OperatingStatus.NEVER_HAD_REVENUE:
            segment, base = Segment.B1, 0.96
        elif answers.operating_status == OperatingStatus.ABANDONED_AFTER_OPERATION:
            has_confirmed_open_items = any(
                item not in {Obligation.NONE, Obligation.UNKNOWN}
                for item in (answers.unpaid_obligations or [])
            )
            obligations_unknown = answers.unpaid_obligations is None or Obligation.UNKNOWN in (
                answers.unpaid_obligations or []
            )
            segment = Segment.B2
            base = 0.92 if has_confirmed_open_items else 0.35 if obligations_unknown else 0.48
        else:
            segment, base = Segment.B2, 0.35

        uncertain = sum(
            [
                answers.registration_status == RegistrationStatus.UNKNOWN,
                answers.tax_id_status == TaxIdStatus.UNKNOWN,
                answers.operating_status == OperatingStatus.UNKNOWN,
                answers.declaration_status == DeclarationStatus.UNKNOWN,
                answers.declaration_matches_reality == YesNoUnknown.UNKNOWN,
                answers.invoice_status == InvoiceStatus.UNKNOWN,
                answers.bank_status == "not_reviewed",
                answers.unpaid_obligations is None
                or Obligation.UNKNOWN in (answers.unpaid_obligations or []),
                answers.tax_audit_notice == YesNoUnknown.UNKNOWN,
            ]
        )
        confidence = max(0.1, base - 0.06 * uncertain)
        return segment, round(confidence, 2)
