from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.job_service import save_jobs
from services.notification_service import send_notification
from services.scoring_service import score_jobs


def run_pipeline():
    jobs = fetch_jobs()
    print(f"[pipeline] fetched {len(jobs)} jobs")

    jobs = unique_jobs(jobs)
    print(f"[pipeline] {len(jobs)} jobs after dedupe")

    jobs = filter_jobs(jobs)
    print(f"[pipeline] {len(jobs)} jobs after role filtering")

    scored_jobs = score_jobs(jobs)
    print(f"[pipeline] scored {len(scored_jobs)} jobs")

    for item in scored_jobs:
        job = item["job"]
        print(f"[debug] {item['score']}/100 | {job.title} | {job.company} | {job.location}")
        print(f"[debug] breakdown = {item['breakdown']}")

    min_score_threshold = 35
    shortlisted = [item for item in scored_jobs if item["score"] >= min_score_threshold]
    print(f"[pipeline] {len(shortlisted)} jobs above threshold {min_score_threshold}")

    inserted = save_jobs(shortlisted)
    print(f"[pipeline] inserted {inserted} new scored jobs into database")

    send_notification(shortlisted)
