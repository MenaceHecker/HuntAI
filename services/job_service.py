from services.db import conn, cursor


def save_jobs(jobs):
    inserted = 0

    for job in jobs:
        try:
            cursor.execute("""
            INSERT INTO jobs (title, company, location, link, description, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                job.title,
                job.company,
                job.location,
                job.link,
                job.description,
                job.source,
            ))
            inserted += 1
        except Exception:
            # likely duplicate due to UNIQUE link
            continue

    conn.commit()
    return inserted