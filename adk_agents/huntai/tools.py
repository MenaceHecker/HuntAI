from __future__ import annotations

from typing import Any

from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.scoring_service import score_jobs


def discover_jobs_tool(limit: int = 25) -> dict[str, Any]:
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


def score_jobs_tool(limit: int = 10, min_score: int = 45, max_per_company: int = 2) -> dict[str, Any]:
    jobs = fetch_jobs()
    jobs = unique_jobs(jobs)
    jobs = filter_jobs(jobs)

    scored = score_jobs(jobs)
    scored = [item for item in scored if item["score"] >= min_score]

    company_counts = {}
    diversified = []

    for item in scored:
        company = item["job"].company
        company_counts.setdefault(company, 0)

        if company_counts[company] >= max_per_company:
            continue

        diversified.append(item)
        company_counts[company] += 1

        if len(diversified) >= limit:
            break

    results = []
    for item in diversified:
        job = item["job"]
        results.append(
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "link": job.link,
                "source": job.source,
                "score": item["score"],
                "verdict": item["verdict"],
                "reasons": item["reasons"],
                "breakdown": item["breakdown"],
            }
        )

    return {
        "status": "success",
        "count": len(results),
        "results": results,
    }


def tailor_resume_tool(job_title: str, company: str, job_link: str = "") -> dict[str, Any]:
    """
    Stub for resume tailoring. For now, returns a structured placeholder so the
    agent can include it in orchestration.

    Args:
        job_title: Job title to tailor for.
        company: Company name.
        job_link: Optional job posting link.
    """
    return {
        "status": "success",
        "message": "Resume tailoring stub created. Next step is to connect the experience bank.",
        "target_job": {
            "title": job_title,
            "company": company,
            "link": job_link,
        },
        "resume_plan": {
            "focus_areas": [
                "backend",
                "cloud",
                "automation",
                "observability",
            ],
            "next_step": "Use approved bullets from experience_bank.json only.",
        },
    }