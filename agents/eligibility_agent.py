from services.filter_service import is_relevant_role, sponsorship_signal


def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        if not is_relevant_role(job.title):
            continue

        if not sponsorship_signal(job.description):
            continue

        filtered.append(job)

    return filtered