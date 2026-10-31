from src.modules.chatbot.law_source import LawTextRecord, read_law_text_records
from src.modules.legal_library.repository import LegalLibraryRepository
from src.modules.legal_library.schemas import LegalLookupRequest, LegalLookupResponse


class LegalLibraryService:
    def __init__(self, repository: LegalLibraryRepository) -> None:
        self._repository = repository

    def search(self, request: LegalLookupRequest) -> LegalLookupResponse:
        text_records, _ = read_law_text_records()
        references = self._repository.get_references(request.procedure, request.query)
        updated_references = []
        for reference in references:
            document_records = [
                record
                for key, record in text_records.items()
                if key[0] == reference.document_number.strip()
            ]
            latest = _latest_record(document_records)
            updated_references.append(
                reference.model_copy(
                    update={
                        "has_verbatim_text": any(
                            record.has_original_text for record in document_records
                        ),
                        "source_url": latest.source_url if latest else "",
                        "last_synced": latest.fetched_at if latest else None,
                        "effectiveness_status": (
                            latest.effectiveness_status.value if latest else "khong_ro"
                        ),
                    }
                )
            )
        return LegalLookupResponse(
            results=updated_references,
        )


def _latest_record(records: list[LawTextRecord]) -> LawTextRecord | None:
    synced = [record for record in records if record.fetched_at is not None]
    if synced:
        return max(
            synced, key=lambda record: record.fetched_at.timestamp() if record.fetched_at else 0
        )
    return next(
        (record for record in records if record.source_url), records[0] if records else None
    )
