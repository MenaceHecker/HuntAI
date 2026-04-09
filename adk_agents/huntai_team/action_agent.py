from __future__ import annotations

from google.adk.agents.llm_agent import Agent

action_agent = Agent(
    name="action_agent",
    model="gemini-2.5-flash",
    description="Decides the next action for a shortlisted opportunity.",
    instruction=(
        "Given a shortlist and positioning plan, recommend one action: "
        "apply_now, review_later, or skip. Prefer apply_now for strong, well-aligned roles."
    ),
)