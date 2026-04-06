def filter_jobs(jobs):
    keywords = ["visa", "h1b", "sponsor"]

    filtered = []
    for job in jobs:
        desc = job["description"].lower()
        if any(k in desc for k in keywords):
            filtered.append(job)

    return filtered