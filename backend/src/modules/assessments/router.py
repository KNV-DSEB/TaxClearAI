from uuid import UUID

from fastapi import APIRouter, Depends, Response

from src.core.schemas import Envelope
from src.modules.assessments.dependencies import get_assessment_service
from src.modules.assessments.schemas import (
    AssessmentView,
    ChecklistItemView,
    CreateAssessment,
    Questionnaire,
    UpdateChecklistItem,
)
from src.modules.assessments.service import AssessmentService, read_questionnaire
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.domain import UserRecord

router = APIRouter(prefix="/api/v1", tags=["assessments"])


@router.get("/questionnaires/b2", response_model=Envelope[Questionnaire])
async def questionnaire(user: UserRecord = Depends(get_current_user)) -> Envelope[Questionnaire]:
    return Envelope(data=read_questionnaire())


@router.post("/assessments", status_code=201, response_model=Envelope[AssessmentView])
async def create_assessment(
    data: CreateAssessment,
    response: Response,
    user: UserRecord = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
) -> Envelope[AssessmentView]:
    result = await service.create(user.id, data)
    response.headers["Location"] = f"/api/v1/assessments/{result.id}"
    return Envelope(data=result)


@router.get("/assessments/{assessment_id}", response_model=Envelope[AssessmentView])
async def read_assessment(
    assessment_id: UUID,
    user: UserRecord = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
) -> Envelope[AssessmentView]:
    return Envelope(data=await service.get(user.id, assessment_id))


@router.patch(
    "/assessments/{assessment_id}/checklist-items/{item_id}",
    response_model=Envelope[ChecklistItemView],
)
async def update_checklist_item(
    assessment_id: UUID,
    item_id: UUID,
    data: UpdateChecklistItem,
    user: UserRecord = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
) -> Envelope[ChecklistItemView]:
    return Envelope(data=await service.update_item(user.id, assessment_id, item_id, data.status))


@router.delete("/assessments/{assessment_id}", status_code=204)
async def delete_assessment(
    assessment_id: UUID,
    user: UserRecord = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
) -> Response:
    await service.remove(user.id, assessment_id)
    return Response(status_code=204)
