from src.core.errors import ApplicationError
from src.modules.legal.repository import LegalRepository
from src.modules.legal.schemas import LegalCategory, LegalDocument, LegalDocumentList


class LegalService:
    def __init__(self, repository: LegalRepository) -> None:
        self.repository = repository

    def list_documents(
        self, query: str | None, category: LegalCategory | None
    ) -> LegalDocumentList:
        documents = self.repository.list_documents()
        if category:
            documents = [item for item in documents if category in item.categories]
        if query:
            phrase = query.casefold().strip()
            documents = [
                item
                for item in documents
                if phrase
                in " ".join(
                    [
                        item.document_number,
                        item.document_title,
                        item.authority,
                        item.summary,
                        *item.applies_to,
                    ]
                ).casefold()
            ]
        return LegalDocumentList(items=documents, total=len(documents))

    def get_document(self, slug: str) -> LegalDocument:
        for document in self.repository.list_documents():
            if document.slug == slug:
                return document
        raise ApplicationError(404, "Không tìm thấy tài liệu pháp luật này.")
