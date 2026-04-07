from services.db import conn, cursor


def save_jobs(scored_jobs):
    inserted = 0

    for item in scored_jobs:
        job = item["job"]
        score = item["score"]

        try:
            cursor.execute("""
            INSERT INTO jobs (title, company, location, link, description, source, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job.title,
                job.company,
                job.location,
                job.link,
                job.description,
                job.source,
                score,
            ))
            inserted += 1
        except Exception:
            continue

    conn.commit()
    return inserted