
from core.auth import get_current_user
from core.database import get_db
from core.models import ChatMessage, ChatMessageResponse, ChatRequest, User
from core.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from services.hr_chat_service import run_hr_chat
from sqlalchemy.orm import Session

router = APIRouter(prefix="/hr-chat", tags=["HR Chat"])

@router.post(
    "/",
    response_model=ChatMessageResponse,
    summary="Send a message to the AI HR Co-Worker",
)
@limiter.limit("30/minute")
def hr_chat(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    try:
        reply = run_hr_chat(
            user_message=payload.message,
            user_id=current_user.id,
            db=db,
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")  # noqa: RUF010

    # Persist both turns — this IS the stateless memory
    db.add(ChatMessage(
        user_id=current_user.id,
        session="hr-chat",
        role="user",
        content=payload.message,
    ))
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        session="hr-chat",
        role="assistant",
        content=reply,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return assistant_msg

@router.get(
    "/history",
    response_model=list[ChatMessageResponse],
    summary="Retrieve full HR chat history for the current user",
)
@limiter.limit("30/minute")
def hr_chat_history(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.session  == "hr-chat",
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


