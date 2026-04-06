def send_notification(jobs):
    print("\n📬 Jobs Found:\n")
    for job in jobs:
        print(f"{job['title']} at {job['company']}")
        print(job["link"])
        print("-" * 40)