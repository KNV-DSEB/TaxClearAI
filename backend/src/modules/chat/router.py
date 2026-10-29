from fastapi import APIRouter, Depends

from src.core.schemas import Envelope
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.domain import UserRecord
from src.modules.chat.dependencies import get_chat_service
from src.modules.chat.schemas import ChatReply, ChatRequest
from src.modules.chat.service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/messages", response_model=Envelope[ChatReply])
async def create_message(
    data: ChatRequest,
    user: UserRecord = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> Envelope[ChatReply]:
    return Envelope(data=await service.answer(user.id, data.message))
