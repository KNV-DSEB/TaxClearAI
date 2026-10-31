from fastapi import HTTPException, status

from src.modules.document_checklist.repository import DocumentChecklistRepository
from src.modules.document_checklist.schemas import (
    ChecklistItem,
    ChecklistRequest,
    ChecklistResponse,
    ChecklistStatus,
    DeclaredDocumentState,
)


class DocumentChecklistService:
    def __init__(self, repository: DocumentChecklistRepository) -> None:
        self._repository = repository

    def review(self, request: ChecklistRequest) -> ChecklistResponse:
        documents = self._repository.get_documents(request.segment, request.procedure)
        declarations = {item.doc_id: item.declared_state for item in request.documents}
        known_ids = {document.doc_id for document in documents}
        unknown_ids = set(declarations) - known_ids
        if unknown_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Unknown document IDs for this procedure: {', '.join(sorted(unknown_ids))}",
            )
        checklist: list[ChecklistItem] = []

        for document in documents:
            state = declarations.get(document.doc_id)
            if state == DeclaredDocumentState.MISSING:
                guide = document.missing_guide
            elif state == DeclaredDocumentState.NEEDS_VERIFICATION:
                guide = document.verification_guide
            elif state is None:
                guide = (
                    "Bạn chưa khai báo trạng thái giấy tờ này. Hãy xác nhận đã có hay còn thiếu, "
                    "rồi tự kiểm tra thời hạn, chữ ký, dấu mộc hoặc nghĩa vụ liên quan; không tải "
                    "giấy tờ lên bước rà soát này."
                )
            else:
                guide = (
                    "Bạn khai báo đã có giấy tờ này. Tự lưu giữ an toàn và đối chiếu thông tin; "
                    "hệ thống chưa xem hoặc xác nhận tính hợp lệ của giấy tờ."
                )
            checklist.append(
                ChecklistItem(
                    doc_id=document.doc_id,
                    doc_name=document.doc_name,
                    status=(
                        ChecklistStatus.ALREADY_HAVE
                        if state == DeclaredDocumentState.AVAILABLE
                        else ChecklistStatus(state.value if state else "needs_verification")
                    ),
                    template_download_available=document.template_download_available,
                    action_guide=guide,
                )
            )

        ready_count = sum(item.status == ChecklistStatus.ALREADY_HAVE for item in checklist)
        readiness = round(ready_count * 100 / len(checklist)) if checklist else 100
        return ChecklistResponse(
            total_items=len(checklist),
            readiness_percentage=readiness,
            checklist=checklist,
        )
