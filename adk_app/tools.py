from __future__ import annotations

from typing import Any

from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.scoring_service import score_jobs


def discover_jobs_tool(limit: int = 25) -> dict[str, Any]:
    """
    Discover jobs from configured sources and return a compact preview.

    Args:
        limit: Maximum number of jobs to include in the response preview.
    """
    jobs = fetch_jobs()
    jobs = unique_jobs(jobs)

    preview = [
        {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "link": job.link,
            "source": job.source,
        }
        for job in jobs[:limit]
    ]

    return {
        "status": "success",
        "count": len(jobs),
        "jobs": preview,
    }