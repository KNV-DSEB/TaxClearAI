from fastapi import Request

from src.modules.chat.service import ChatService


def get_chat_service(request: Request) -> ChatService:
    service: ChatService = request.app.state.chat_service
    return service
