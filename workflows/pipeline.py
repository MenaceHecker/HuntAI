from agents.discovery_agent import fetch_jobs
from agents.eligibility_agent import filter_jobs
from services.job_service import save_jobs
from services.notification_service import send_notification

def run_pipeline():
    jobs = fetch_jobs()
    filtered = filter_jobs(jobs)

    save_jobs(filtered)

    if filtered:
        send_notification(filtered)