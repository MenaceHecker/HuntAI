from __future__ import annotations

from google.adk.agents.llm_agent import Agent
from adk_agents.huntai.tools import score_jobs_tool

fit_agent = Agent(
    name="fit_agent",
    model="gemini-2.5-flash",
    description="Scores and prioritizes jobs against the user's preferences.",
    instruction=(
        "Use score_jobs_tool to find the best-matching roles. "
        "Prefer concise rankings with score, verdict, and reasons."
    ),
    tools=[score_jobs_tool],
)