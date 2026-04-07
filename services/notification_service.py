def send_notification(scored_jobs):
    if not scored_jobs:
        print("[notify] no matching jobs found")
        return

    print(f"\n[notify] {len(scored_jobs)} scored jobs found:\n")

    for idx, item in enumerate(scored_jobs, start=1):
        job = item["job"]
        score = item["score"]
        breakdown = item["breakdown"]

        print(f"{idx}. [{score}/100] {job.title} | {job.company} | {job.location}")
        print(job.link)
        print(f"   Breakdown: {breakdown}")
        print("-" * 80)