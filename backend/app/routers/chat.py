import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter
from backend.app.database import get_analysis_by_id, get_chat_history, save_chat_message
from backend.app.models import ChatMessageRequest, ChatMessageResponse
from backend.app.services.bedrock_service import bedrock_service
from backend.app.services.redaction_service import redaction_service

router = APIRouter(prefix="/api/chat", tags=["AI Debugging Assistant"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(req: ChatMessageRequest):
    """
    Submits a message to the AI debugging assistant with multi-turn memory
    and optional context linkage to an active analysis.
    """
    # Redact secrets from user input
    clean_user_message = redaction_service.redact(req.message).clean_text

    # Retrieve existing conversational thread
    history = await get_chat_history(req.session_id)

    # Optional analysis context
    context_data = None
    if req.analysis_id:
        analysis = await get_analysis_by_id(req.analysis_id)
        if analysis:
            context_data = (
                f"Analysis Type: {analysis.get('analysis_type')}\n"
                f"Title: {analysis.get('title')}\n"
                f"Summary: {analysis.get('summary')}\n"
                f"Input Snippet: {analysis.get('raw_input', '')[:1000]}"
            )

    # Prepare message list for Bedrock Converse
    converse_messages = []
    for h in history:
        converse_messages.append({"role": h["role"], "content": h["content"]})
    converse_messages.append({"role": "user", "content": clean_user_message})

    # Save user message to database
    user_msg_id = f"msg-{uuid.uuid4().hex[:10]}"
    await save_chat_message(
        message_id=user_msg_id,
        session_id=req.session_id,
        role="user",
        content=clean_user_message,
        provider="user",
        model_id="input",
        analysis_id=req.analysis_id
    )

    # Invoke Bedrock or deterministic fallback
    ai_content, provider, model_id, is_fallback = bedrock_service.converse(
        messages=converse_messages,
        context_data=context_data
    )

    # Save assistant message to database
    asst_msg_id = f"msg-{uuid.uuid4().hex[:10]}"
    await save_chat_message(
        message_id=asst_msg_id,
        session_id=req.session_id,
        role="assistant",
        content=ai_content,
        provider=provider,
        model_id=model_id,
        analysis_id=req.analysis_id
    )

    return ChatMessageResponse(
        id=asst_msg_id,
        session_id=req.session_id,
        analysis_id=req.analysis_id,
        role="assistant",
        content=ai_content,
        provider=provider,
        model_id=model_id,
        is_fallback=is_fallback,
        created_at=datetime.now(timezone.utc).isoformat()
    )

@router.get("/history/{session_id}")
async def fetch_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Returns the message history for a given chat session.
    """
    return await get_chat_history(session_id)
