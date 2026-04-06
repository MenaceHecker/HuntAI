from services.db import cursor, conn

def save_jobs(jobs):
    for job in jobs:
        cursor.execute("""
        INSERT INTO jobs (title, company, location, link, description, source)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job["title"],
            job["company"],
            job["location"],
            job["link"],
            job["description"],
            job["source"]
        ))
    conn.commit()