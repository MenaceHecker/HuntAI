from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.scoring_service import score_jobs
from services.tailoring_service import tailor_resume_for_job


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


def score_jobs_tool(
    limit: int = 10,
    min_score: int = 45,
    max_per_company: int = 2,
) -> dict[str, Any]:
    jobs = fetch_jobs()
    jobs = unique_jobs(jobs)
    jobs = filter_jobs(jobs)

    scored = score_jobs(jobs)
    scored = [item for item in scored if item["score"] >= min_score]

    company_counts: dict[str, int] = {}
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
                "description": job.description or "",
            }
        )

    return {
        "status": "success",
        "count": len(results),
        "results": results,
    }


def tailor_resume_tool(
    job_title: str,
    company: str,
    job_description: str = "",
    job_link: str = "",
) -> dict[str, Any]:
    result = tailor_resume_for_job(
        job_title=job_title,
        company=company,
        job_description=job_description,
    )

    return {
        "status": result["status"],
        "target_job": {
            "title": job_title,
            "company": company,
            "link": job_link,
        },
        "focus_areas": result["focus_areas"][:5],
        "recommended_skills": result["recommended_skills"][:6],
        "selected_bullets": result["selected_bullets"][:4],
        "rules": result.get("rules", []),
    }


def score_and_tailor_top_tool(
    limit: int = 5,
    min_score: int = 45,
    max_per_company: int = 2,
) -> dict[str, Any]:
    scored_result = score_jobs_tool(
        limit=limit,
        min_score=min_score,
        max_per_company=max_per_company,
    )

    results = scored_result.get("results", [])
    if not results:
        return {
            "status": "success",
            "count": 0,
            "shortlist": [],
            "top_job_resume_plan": None,
            "message": "No matching jobs found above the threshold.",
        }

    top_job = results[0]

    tailored_result = tailor_resume_tool(
        job_title=top_job["title"],
        company=top_job["company"],
        job_description=top_job.get("description", ""),
        job_link=top_job["link"],
    )

    # remove description from shortlist payload to keep response smaller
    cleaned_shortlist = []
    for item in results:
        cleaned = dict(item)
        cleaned.pop("description", None)
        cleaned_shortlist.append(cleaned)

    return {
        "status": "success",
        "count": len(cleaned_shortlist),
        "shortlist": cleaned_shortlist,
        "top_job_resume_plan": tailored_result,
    }