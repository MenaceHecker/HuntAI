from __future__ import annotations

from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from .tools import discover_jobs_tool, score_jobs_tool, tailor_resume_tool

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
    "- Present shortlisted jobs clearly.\n"
    "- For each shortlisted job, include title, company, location, score, verdict, and link.\n"
    "- Also include 2 to 4 brief reasons explaining why the role matched the profile.\n"
    "- Use verdict labels exactly as returned: Strong Apply, Good Match, Maybe Apply, or Skip.\n"
    "- If the user asks for the best jobs, prioritize the top 5 most relevant ones instead of a long list.\n"
    "- Do not invent resume experience. Tailoring must only use approved experience-bank content.\n"
),
    tools=[
        discover_jobs_tool,
        score_jobs_tool,
        tailor_resume_tool,
    ],
)