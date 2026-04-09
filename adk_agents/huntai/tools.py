from __future__ import annotations

from typing import Any
from services.tailoring_service import tailor_resume_for_job
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


def tailor_resume_tool(job_title: str, company: str, job_description: str = "", job_link: str = "") -> dict[str, Any]:
    result = tailor_resume_for_job(
        job_title=job_title,
        company=company,
        job_description=job_description,
    )

    result["target_job"]["link"] = job_link
    return result