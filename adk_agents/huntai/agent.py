from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

from adk_app.tools import discover_jobs_tool, score_jobs_tool, tailor_resume_tool

load_dotenv()

MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    model=MODEL_NAME,
    name="huntai_orchestrator",
    description="An agent that finds software jobs, scores fit, and prepares resume-tailoring plans.",
    instruction=(
        "You are HuntAI, an AI job-search orchestrator for software engineering roles.\n"
        "\n"
        "Your responsibilities:\n"
        "1. Use discover_jobs_tool when the user asks for raw discovery results.\n"
        "2. Use score_jobs_tool when the user asks for the best matching jobs.\n"
        "3. Use tailor_resume_tool when the user asks for a resume-tailoring plan.\n"
        "\n"
        "Behavior rules:\n"
        "- Prefer score_jobs_tool for ranking jobs.\n"
        "- Summarize results clearly and concisely.\n"
        "- Include job title, company, location, score, and link when available.\n"
        "- Do not invent resume experience. Tailoring must only use approved experience-bank content.\n"
    ),
    tools=[
        discover_jobs_tool,
        score_jobs_tool,
        tailor_resume_tool,
    ],
)