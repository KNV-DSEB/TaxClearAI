import json
from typing import Protocol

from pydantic import ValidationError

from src.core.config import Settings
from src.modules.chatbot.llm import AnthropicLLM, GeminiLLM, MockLLM
from src.modules.chatbot.privacy import redact_sensitive_data
from src.modules.chatbot.validator import validate_situation_reasons
from src.modules.legal_survey.schemas import SituationSuggestion, SurveyAnswers


class SituationLLM(Protocol):
    async def classify_situation(
        self, answers: dict[str, object], free_text: str | None, model: str
    ) -> str: ...


class SituationClassifier:
    def __init__(self, llm: SituationLLM, model: str) -> None:
        self._llm = llm
        self._model = model

    async def classify(
        self, answers: SurveyAnswers, question_ids: set[str]
    ) -> SituationSuggestion | None:
        answer_values = answers.model_dump(mode="json", exclude={"free_text"})
        safe_free_text = redact_sensitive_data(answers.free_text or "") or None
        raw = await self._llm.classify_situation(
            answer_values,
            safe_free_text,
            self._model,
        )
        try:
            suggestion = SituationSuggestion.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
            return None

        if not set(suggestion.missing_info).issubset(question_ids):
            return None
        evidence = {
            f"{key}={value}"
            for key, value in answer_values.items()
            for value in (value if isinstance(value, list) else [value])
        }
        if validate_situation_reasons(
            suggestion.reasons,
            enum_evidence=evidence,
            free_text=safe_free_text,
        ):
            return None
        return suggestion


def create_situation_classifier(settings: Settings) -> SituationClassifier | None:
    if not settings.survey_ai_enabled:
        return None
    if settings.chatbot_llm_provider == "mock":
        llm: SituationLLM = MockLLM()
    elif settings.chatbot_llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            return None
        llm = MockLLM() if settings.chatbot_mock_mode else AnthropicLLM(settings)
    else:
        if not settings.gemini_api_key:
            return None
        llm = MockLLM() if settings.chatbot_mock_mode else GeminiLLM(settings)
    return SituationClassifier(
        llm,
        settings.model_classifier or settings.model_guardrail,
    )
