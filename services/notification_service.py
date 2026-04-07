def send_notification(jobs):
    if not jobs:
        print("[notify] no matching jobs found")
        return

    print(f"\n[notify] {len(jobs)} matching jobs found:\n")

    for idx, job in enumerate(jobs, start=1):
        print(f"{idx}. {job.title} | {job.company} | {job.location}")
        print(job.link)
        print("-" * 60)