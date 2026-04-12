from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEEN_JOBS_PATH = PROJECT_ROOT / "seen_jobs.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.scoring_service import score_jobs
from services.tailoring_service import tailor_resume_for_job


def load_seen_jobs() -> list[dict[str, Any]]:
    if not SEEN_JOBS_PATH.exists():
        return []

    try:
        with SEEN_JOBS_PATH.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    return data if isinstance(data, list) else []


def save_seen_jobs(seen_jobs: list[dict[str, Any]]) -> None:
    with SEEN_JOBS_PATH.open("w") as f:
        json.dump(seen_jobs, f, indent=2)


def apply_strategy_mode(
    scored_jobs: list[dict],
    strategy_mode: str = "safe_apply",
) -> list[dict]:
    brand_priority = {
        "OpenAI",
        "Stripe",
        "Datadog",
        "Snowflake",
        "Dropbox",
        "Figma",
        "Asana",
        "Vercel",
        "Roblox",
        "Coinbase",
        "Airbnb",
    }

    visa_priority = {
        "Stripe",
        "Datadog",
        "Dropbox",
        "Asana",
        "Figma",
        "Vercel",
        "Roblox",
        "Coinbase",
        "Airbnb",
    }

    boosted = []

    for item in scored_jobs:
        adjusted = dict(item)
        adjusted_score = item["score"]
        company = item["job"].company
        sponsorship = item["breakdown"].get("sponsorship", 0)

        if strategy_mode == "safe_apply":
            adjusted_score += 0
        elif strategy_mode == "stretch_apply":
            adjusted_score += 3
        elif strategy_mode == "brand_first":
            if company in brand_priority:
                adjusted_score += 8
        elif strategy_mode == "visa_first":
            if sponsorship >= 15:
                adjusted_score += 8
            elif company in visa_priority:
                adjusted_score += 4

        adjusted["strategy_score"] = adjusted_score
        boosted.append(adjusted)

    boosted.sort(key=lambda item: item["strategy_score"], reverse=True)
    return boosted


def is_us_location(location: str) -> bool:
    location = (location or "").lower()

    explicit_non_us_terms = [
        "poland",
        "mexico",
        "canada",
        "toronto",
        "vancouver",
        "montreal",
        "israel",
        "tel aviv",
        "warsaw",
        "portugal",
        "lisbon",
        "germany",
        "berlin",
        "united kingdom",
        "uk",
        "london",
        "ireland",
        "dublin",
        "india",
        "singapore",
        "tokyo",
        "japan",
        "australia",
        "remote - poland",
        "remote - mexico",
        "remote - canada",
    ]

    if any(term in location for term in explicit_non_us_terms):
        return False

    us_terms = [
        "united states",
        "usa",
        "u.s.",
        " us ",
        "remote - united states",
        "remote in us",
        "remote us",
        "new york",
        "california",
        "san francisco",
        "seattle",
        "austin",
        "atlanta",
        "georgia",
        "boston",
        "chicago",
        "washington",
        "texas",
    ]

    return any(term in location for term in us_terms)


def is_remote_location(location: str) -> bool:
    location = (location or "").lower()
    return "remote" in location


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
    us_only: bool = True,
    remote_only: bool = False,
    strategy_mode: str = "safe_apply",
) -> dict[str, Any]:
    jobs = fetch_jobs()
    jobs = unique_jobs(jobs)
    jobs = filter_jobs(jobs)

    seen = load_seen_jobs()
    seen_links = {job.get("link") for job in seen if isinstance(job, dict)}
    jobs = [job for job in jobs if job.link not in seen_links]

    scored = score_jobs(jobs)

    if us_only:
        scored = [item for item in scored if is_us_location(item["job"].location)]

    if remote_only:
        scored = [item for item in scored if is_remote_location(item["job"].location)]

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

    seen.extend(results)
    save_seen_jobs(seen)

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
    us_only: bool = True,
    remote_only: bool = False,
) -> dict[str, Any]:
    scored_result = score_jobs_tool(
        limit=limit,
        min_score=min_score,
        max_per_company=max_per_company,
        us_only=us_only,
        remote_only=remote_only,
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

def build_opportunity_brief_tool(
    limit: int = 5,
    min_score: int = 45,
    max_per_company: int = 2,
    us_only: bool = True,
    remote_only: bool = False,
    strategy_mode: str = "safe_apply",
) -> dict[str, Any]:
    result = score_and_tailor_top_tool(
        limit=limit,
        min_score=min_score,
        max_per_company=max_per_company,
        us_only=us_only,
        remote_only=remote_only,
    )

    shortlist = result.get("shortlist", [])
    top_plan = result.get("top_job_resume_plan")

    if not shortlist or not top_plan:
        return {
            "status": "success",
            "strategy_mode": strategy_mode,
            "top_jobs": [],
            "recommended_job": None,
            "opportunity_brief": None,
            "message": "No strong matches found for this run.",
        }

    recommended_job = shortlist[0]

    why_this_role = (
        f"{recommended_job['title']} at {recommended_job['company']} ranks highest "
        f"because it aligns with your preferred engineering domains and skill profile."
    )

    positioning_angle = (
        "Position yourself as an engineer with strong backend, platform automation, "
        "reliability, and systems experience, and emphasize the bullets selected below."
    )

    action = "apply_now" if recommended_job["score"] >= 80 else "review_later"

    return {
        "status": "success",
        "strategy_mode": strategy_mode,
        "top_jobs": shortlist[:3],
        "recommended_job": recommended_job,
        "opportunity_brief": {
            "why_this_role": why_this_role,
            "positioning_angle": positioning_angle,
            "focus_areas": top_plan.get("focus_areas", []),
            "recommended_skills": top_plan.get("recommended_skills", []),
            "selected_bullets": top_plan.get("selected_bullets", []),
            "action": action,
        },
    }
