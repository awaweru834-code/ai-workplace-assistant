import os

from core.models import ChatMessage
from google import genai
from google.genai import types

from services.rag_service import run_rag_query

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def search_hr_policy(query: str) -> str:
    """Search company policy documents for HR guidelines, leave, benefits, and rules."""
    return run_rag_query(query)

def run_hr_chat(user_message: str, user_id: int, db) -> str:
    # 1. Fetch DB conversation history
    history = (
        db.query(ChatMessage)
        .filter_by(user_id=user_id, session="hr-chat")
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    # 2. Build conversation contents for Gemini
    contents = []
    for msg in history:
        role = "user" if msg.role == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)],
            )
        )
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    # 3. Call Gemini with automatic tool execution
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[search_hr_policy],
            temperature=0.3,
        ),
    )

    return response.text