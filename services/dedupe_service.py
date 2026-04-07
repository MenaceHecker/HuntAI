def unique_jobs(jobs):
    seen = set()
    results = []

    for job in jobs:
        key = (
            (job.title or "").strip().lower(),
            (job.company or "").strip().lower(),
            (job.link or "").strip().lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        results.append(job)

    return results