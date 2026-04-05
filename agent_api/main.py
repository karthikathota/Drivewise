from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import asyncio

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
    session_id: Optional[str] = None


class RecommendResponse(BaseModel):
    answer: str
    session_id: str
    profile: Dict[str, Any]  # returned so Streamlit can display it


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend_vehicle(query: UserQuery):
    if not query.session_id:
        query.session_id = str(uuid.uuid4())

    try:
        answer, profile = await asyncio.wait_for(
            handle_user_query(
                user_id=query.session_id,
                user_input=query.question
            ),
            timeout=120.0
        )
    except asyncio.TimeoutError:
        answer = (
            "I wasn't able to pull results in time — please try again. "
            "Try being more specific about your budget or vehicle type."
        )
        profile = {}

    return RecommendResponse(
        answer=answer,
        session_id=query.session_id,
        profile=profile
    )