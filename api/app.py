from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from pydantic import BaseModel, Field

from adk_agents.huntai.tools import (
    discover_jobs_tool,
    score_jobs_tool,
    tailor_resume_tool,
    score_and_tailor_top_tool,
    build_opportunity_brief_tool,
)

app = FastAPI(title="HuntAI API", version="0.1.0")
strategy_mode: str = Field(default="safe_apply")


class RunHuntRequest(BaseModel):
    mode: str = Field(
        default="score",
        description="discover | score | tailor | score_and_tailor_top",
    )
    limit: int = Field(default=10, ge=1, le=50)
    min_score: int = Field(default=45, ge=0, le=100)
    max_per_company: int = Field(default=2, ge=1, le=10)
    us_only: bool = True
    remote_only: bool = False
    job_title: str | None = None
    company: str | None = None
    job_description: str | None = None
    job_link: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run-hunt")
def run_hunt(payload: RunHuntRequest) -> dict:
    if payload.mode == "discover":
        return discover_jobs_tool(limit=payload.limit)

    if payload.mode == "score":
        return score_jobs_tool(
            limit=payload.limit,
            min_score=payload.min_score,
            max_per_company=payload.max_per_company,
            us_only=payload.us_only,
            remote_only=payload.remote_only,
        )

    if payload.mode == "tailor":
        if not payload.job_title or not payload.company:
            return {
                "status": "error",
                "message": "job_title and company are required for tailor mode.",
            }

        return tailor_resume_tool(
            job_title=payload.job_title,
            company=payload.company,
            job_description=payload.job_description or "",
            job_link=payload.job_link or "",
        )
    if payload.mode == "opportunity_brief":
        return build_opportunity_brief_tool(
        limit=payload.limit,
        min_score=payload.min_score,
        max_per_company=payload.max_per_company,
        us_only=payload.us_only,
        remote_only=payload.remote_only,
        strategy_mode=payload.strategy_mode,
    )

    if payload.mode == "score_and_tailor_top":
        return score_and_tailor_top_tool(
            limit=payload.limit,
            min_score=payload.min_score,
            max_per_company=payload.max_per_company,
            us_only=payload.us_only,
            remote_only=payload.remote_only,
        )

    return {
        "status": "error",
        "message": "Invalid mode. Use discover, score, tailor, or score_and_tailor_top.",
    }