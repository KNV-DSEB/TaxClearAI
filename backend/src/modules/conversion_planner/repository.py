import unicodedata

from src.modules.conversion_planner.schemas import BusinessModel
from src.modules.legal_library.repository import LegalLibraryRepository


class ConversionPlannerRepository:
    def __init__(self, legal_library: LegalLibraryRepository | None = None) -> None:
        self._legal_library = legal_library or LegalLibraryRepository()

    def get_model_label(self, model: BusinessModel) -> str:
        return {
            BusinessModel.HKD: "Hộ kinh doanh",
            BusinessModel.COMPANY_LLC: "Công ty TNHH",
            BusinessModel.COMPANY_JSC: "Công ty cổ phần",
        }[model]

    def get_transition_legal_basis(self, conversion_kind: str) -> str | None:
        markers = {
            "HKD_TO_COMPANY": (
                "chuyen doi tu ho kinh doanh sang doanh nghiep",
                "ho kinh doanh chuyen doi thanh doanh nghiep",
                "thanh lap doanh nghiep tu ho kinh doanh",
            ),
            "COMPANY_TYPE_CHANGE": (
                "chuyen doi loai hinh doanh nghiep",
                "chuyen doi loai hinh cong ty",
                "chuyen doi cong ty tnhh",
                "chuyen doi cong ty co phan",
            ),
        }.get(conversion_kind, ())
        for reference in self._legal_library.get_references(None, None):
            for provision in reference.applicable_provisions:
                text = _normalize(f"{provision.regulated_action} {reference.summary}")
                if any(marker in text for marker in markers):
                    location = ", ".join(
                        part
                        for part in (provision.article, provision.clause, provision.point)
                        if part
                    )
                    return f"{reference.document_number} — {location}"
        return None


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")
