from fastapi import FastAPI
from pydantic import BaseModel
import nest_asyncio

from agents import Runner
from agent_api.agents import vehicle_recommendation_agent

nest_asyncio.apply()

app = FastAPI(title="DriveWise Agent API")


class UserQuery(BaseModel):
    question: str


@app.post("/recommend")
async def recommend_vehicle(query: UserQuery):
    result = await Runner.run(
        vehicle_recommendation_agent,
        query.question
    )
    return {"answer": result.final_output}
