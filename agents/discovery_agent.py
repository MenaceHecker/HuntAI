import requests

from models.job import Job
from services.source_service import load_sources


def fetch_greenhouse_jobs(source):
    jobs = []
    try:
        response = requests.get(
            source["url"],
            params={"content": "true"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("jobs", []):
            content = item.get("content", "") or ""
            location = item.get("location", {}).get("name", "Unknown")
            absolute_url = item.get("absolute_url", "")

            jobs.append(
                Job(
                    title=item.get("title", "Unknown Title"),
                    company=source["name"],
                    location=location,
                    link=absolute_url,
                    description=content,
                    source=source["type"],
                )
            )
    except Exception as e:
        print(f"[discovery] greenhouse source failed: {source['name']} -> {e}")

    return jobs


def fetch_lever_jobs(source):
    jobs = []
    try:
        response = requests.get(source["url"], timeout=20)
        response.raise_for_status()
        data = response.json()

        for item in data:
            description_plain = item.get("descriptionPlain", "") or ""
            categories = item.get("categories", {}) or {}
            location = categories.get("location", "Unknown")
            apply_link = item.get("hostedUrl", "")

            jobs.append(
                Job(
                    title=item.get("text", "Unknown Title"),
                    company=source["name"],
                    location=location,
                    link=apply_link,
                    description=description_plain,
                    source=source["type"],
                )
            )
    except Exception as e:
        print(f"[discovery] lever source failed: {source['name']} -> {e}")

    return jobs


def fetch_jobs():
    all_jobs = []
    sources = load_sources()

    for source in sources:
        source_type = source.get("type")

        if source_type == "greenhouse":
            all_jobs.extend(fetch_greenhouse_jobs(source))
        elif source_type == "lever":
            all_jobs.extend(fetch_lever_jobs(source))
        else:
            print(f"[discovery] unsupported source type: {source_type}")

    return all_jobs
