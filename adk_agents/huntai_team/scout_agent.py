from __future__ import annotations

from google.adk.agents.llm_agent import Agent
from adk_agents.huntai.tools import discover_jobs_tool

scout_agent = Agent(
    name="scout_agent",
    model="gemini-2.5-flash",
    description="Finds and previews candidate software jobs.",
    instruction=(
        "Use discover_jobs_tool to gather raw job leads. "
        "Return a compact summary of what kinds of roles are present."
    ),
    tools=[discover_jobs_tool],
)