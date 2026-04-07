from services.filter_service import is_relevant_role


def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        if not is_relevant_role(job.title):
            continue

        filtered.append(job)

    return filtered