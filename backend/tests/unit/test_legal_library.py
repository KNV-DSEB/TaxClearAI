import pytest

from src.core.errors import ApplicationError
from src.modules.legal.repository import LegalRepository
from src.modules.legal.service import LegalService


def test_library_contains_five_documents_with_source_links():
    documents = LegalRepository().list_documents()

    assert len(documents) == 5
    assert all(document.sources for document in documents)
    assert all(document.process_steps and document.checklist for document in documents)


def test_category_and_text_filters_narrow_library_results():
    service = LegalService(LegalRepository())

    result = service.list_documents("hộ kinh doanh", "household")

    assert result.total == 1
    assert result.items[0].slug == "cham-dut-ho-kinh-doanh"


def test_unknown_slug_returns_not_found():
    with pytest.raises(ApplicationError) as error:
        LegalService(LegalRepository()).get_document("unknown-document")

    assert error.value.status == 404
