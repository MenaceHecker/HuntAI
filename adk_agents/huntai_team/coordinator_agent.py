from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google.adk.agents.llm_agent import Agent
from adk_agents.huntai.tools import build_opportunity_brief_tool

root_agent = Agent(
    name="huntai_team_coordinator",
    model="gemini-2.5-flash",
    description="Coordinates the Opportunity Brief workflow for software job search.",
    instruction=(
        "You are the coordinator for HuntAI.\n"
        "Your goal is to produce an Opportunity Brief, not just a job list.\n"
        "Use build_opportunity_brief_tool when the user asks for today's best jobs, "
        "a recommended target role, or a positioning plan.\n"
        "Return:\n"
        "- top jobs\n"
        "- recommended job\n"
        "- why this role matters\n"
        "- how the user should position themselves\n"
        "- next action\n"
    ),
    tools=[build_opportunity_brief_tool],
)