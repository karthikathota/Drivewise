from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid

from agent_api.agents import handle_user_query

app = FastAPI(title="DriveWise Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserQuery(BaseModel):
    question: str
    session_id: Optional[str] = None  # Optional[str] is Python 3.9+ compatible


@app.get("/health")
async def health_check():
    """Liveness check — hit this before your demo to confirm the server is up."""
    return {"status": "ok"}


@app.post("/recommend")
async def recommend_vehicle(query: UserQuery):
    if not query.session_id:
        query.session_id = str(uuid.uuid4())

    answer = await handle_user_query(
        user_id=query.session_id,
        user_input=query.question
    )

    return {"answer": answer, "session_id": query.session_id}