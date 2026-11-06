"""Dữ liệu mẫu dùng chung cho test: bộ câu trả lời chuẩn hóa (groups-draft-3), khóa camelCase."""

from typing import Any

from src.modules.assessments.schemas import Answers
from src.modules.assessments.service import normalize_answers

VERSION = "groups-draft-3"

COMPANY_ANSWERS: dict[str, Any] = {
    "businessType": "company",
    "procedure": "dissolution",
    "operatingStatus": "stopped_not_started",
    "sector": "trade",
    "establishedYear": 2010,
    "hasRevenue": "yes",
    "lastRevenue": "tháng 3/2020",
    "hasCosts": "yes",
    "recordsAccess": "partial",
    "dnType": "llc2",
    "dnRegistry": "Hà Nội",
    "dnDecision": "none",
    "dnDebtGuarantee": "yes",
    "dnRevenue": "yes",
    "dnExpenses": "yes",
    "dnRecords": "partial",
    "dnTaxDebt": "no",
}

HOUSEHOLD_ANSWERS: dict[str, Any] = {
    "businessType": "household",
    "procedure": "dissolution",
    "operatingStatus": "stopped_not_started",
    "sector": "hospitality",
    "establishedYear": 2018,
    "hasRevenue": "yes",
    "hasCosts": "yes",
    "recordsAccess": "complete",
    "hhProvince": "Đà Nẵng",
    "hhLocations": "one",
    "hhConditional": "no",
    "hhTaxObligation": "no",
    "hhInvoiceSystem": "none",
    "hhEmployees": "none",
}


def company(**changes: Any) -> dict[str, Any]:
    """Câu trả lời đã chuẩn hóa của một doanh nghiệp, sửa theo `changes`."""
    return normalize_answers(Answers.model_validate(COMPANY_ANSWERS | changes))


def household(**changes: Any) -> dict[str, Any]:
    return normalize_answers(Answers.model_validate(HOUSEHOLD_ANSWERS | changes))
