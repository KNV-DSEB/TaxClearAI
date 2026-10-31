import pytest
from fastapi import HTTPException

from src.modules.document_checklist.repository import DocumentChecklistRepository
from src.modules.document_checklist.schemas import ChecklistRequest
from src.modules.document_checklist.service import DocumentChecklistService


@pytest.fixture
def service() -> DocumentChecklistService:
    return DocumentChecklistService(DocumentChecklistRepository())


@pytest.mark.parametrize(
    ("segment", "procedure", "expected_count"),
    [
        ("A1", "terminate", 5),
        ("A2", "terminate", 8),
        ("A3", "terminate", 10),
        ("B1", "terminate", 7),
        ("B2", "terminate", 12),
        ("A1", "convert_to_new_entity", 3),
        ("A2", "convert_to_new_entity", 3),
        ("A3", "convert_to_new_entity", 3),
        ("B1", "convert_to_new_entity", 3),
        ("B2", "convert_to_new_entity", 4),
    ],
)
def test_returns_a_checklist_for_each_segment_and_procedure(
    service: DocumentChecklistService, segment: str, procedure: str, expected_count: int
) -> None:
    result = service.review(ChecklistRequest(segment=segment, procedure=procedure))

    assert result.total_items == len(result.checklist)
    assert result.total_items == expected_count
    assert result.readiness_percentage == 0
    assert result.checklist
    assert all(item.status == "needs_verification" for item in result.checklist)


def test_uses_only_declared_metadata_to_assign_the_three_states(
    service: DocumentChecklistService,
) -> None:
    result = service.review(
        ChecklistRequest(
            segment="A2",
            procedure="terminate",
            documents=[
                {"doc_id": "DOC_TAX_CLOSE", "declared_state": "available"},
                {"doc_id": "DOC_TAX_DECLARATIONS", "declared_state": "needs_verification"},
            ],
        )
    )
    statuses = {item.doc_id: item.status for item in result.checklist}

    assert statuses["DOC_TAX_CLOSE"] == "already_have"
    assert statuses["DOC_TAX_DECLARATIONS"] == "needs_verification"
    assert statuses["DOC_HKD_TERMINATION"] == "needs_verification"
    assert result.readiness_percentage == 12
    assert "chưa xem hoặc xác nhận" in result.checklist[0].action_guide


def test_a1_checklist_does_not_require_a_fictitious_registration_closure_document(
    service: DocumentChecklistService,
) -> None:
    result = service.review(ChecklistRequest(segment="A1", procedure="terminate"))

    doc_ids = {item.doc_id for item in result.checklist}
    assert "DOC_HKD_TERMINATION" not in doc_ids
    assert "DOC_HKD_REGISTRATION_INFO" not in doc_ids
    assert "DOC_HKD_REGISTRATION_CERTIFICATE" not in doc_ids


def test_hkd_and_company_segment_checklists_are_distinct_and_well_formed() -> None:
    repository = DocumentChecklistRepository()
    hkd_a2 = repository.get_documents("A2", "terminate")
    hkd_a3 = repository.get_documents("A3", "terminate")
    company_b1 = repository.get_documents("B1", "terminate")
    company_b2 = repository.get_documents("B2", "terminate")

    assert {document.doc_id for document in hkd_a2} != {document.doc_id for document in hkd_a3}
    assert {document.doc_id for document in company_b1} != {
        document.doc_id for document in company_b2
    }
    for segment in ("A1", "A2", "A3", "B1", "B2"):
        for procedure in ("terminate", "convert_to_new_entity"):
            documents = repository.get_documents(segment, procedure)
            doc_ids = [document.doc_id for document in documents]
            assert len(doc_ids) == len(set(doc_ids))
            assert all(doc_id.startswith("DOC_") for doc_id in doc_ids)
            assert all(document.doc_name.strip() for document in documents)
            assert all(document.missing_guide.strip() for document in documents)
            assert all(document.verification_guide.strip() for document in documents)


def test_rejects_document_ids_that_do_not_belong_to_the_selected_procedure(
    service: DocumentChecklistService,
) -> None:
    with pytest.raises(HTTPException, match="Unknown document IDs"):
        service.review(
            ChecklistRequest(
                segment="A2",
                procedure="terminate",
                documents=[{"doc_id": "DOC_FOR_OTHER_PROCEDURE", "declared_state": "available"}],
            )
        )
