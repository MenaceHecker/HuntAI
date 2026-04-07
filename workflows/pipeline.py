from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.dedupe_service import unique_jobs
from services.job_service import save_jobs
from services.notification_service import send_notification


def run_pipeline():
    jobs = fetch_jobs()
    print(f"[pipeline] fetched {len(jobs)} jobs")

    jobs = unique_jobs(jobs)
    print(f"[pipeline] {len(jobs)} jobs after dedupe")

    filtered = filter_jobs(jobs)
    print(f"[pipeline] {len(filtered)} jobs after filtering")

    inserted = save_jobs(filtered)
    print(f"[pipeline] inserted {inserted} new jobs into database")

    send_notification(filtered)