from __future__ import annotations

from google.adk.agents.llm_agent import Agent
from adk_agents.huntai.tools import tailor_resume_tool

positioning_agent = Agent(
    name="positioning_agent",
    model="gemini-2.5-flash",
    description="Builds a positioning plan for a selected role using approved experience only.",
    instruction=(
        "Use tailor_resume_tool to create a positioning plan. "
        "Return focus areas, recommended skills, and selected bullets only from approved experience."
    ),
    tools=[tailor_resume_tool],
)