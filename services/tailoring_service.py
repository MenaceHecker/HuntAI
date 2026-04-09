import json
import re
from pathlib import Path


PRIORITY_TAG_WEIGHTS = {
    "infrastructure": 3,
    "observability": 3,
    "monitoring": 3,
    "telemetry": 3,
    "reliability": 3,
    "backend": 2,
    "platform": 2,
    "cloud": 2,
    "automation": 2,
    "security": 2,
    "distributed systems": 2,
    "sre": 2,
    "performance": 2,
}


def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_experience_bank():
    base_dir = Path(__file__).resolve().parents[1]
    path = base_dir / "data" / "experience_bank.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_keywords(text: str) -> set[str]:
    text = normalize(text)

    keywords = [
        "python", "java", "typescript", "javascript", "sql",
        "aws", "gcp", "docker", "kubernetes", "terraform",
        "react", "next.js", "nextjs", "flask", "fastapi", "spring", "spring boot",
        "backend", "frontend", "platform", "cloud", "infrastructure",
        "security", "observability", "monitoring", "telemetry", "reliability", "sre",
        "distributed systems", "automation", "authentication", "performance",
        "api", "apis", "postgresql", "elasticsearch", "grafana", "prometheus",
        "ci/cd", "agents", "ml", "ai", "nlp"
    ]

    found = {kw for kw in keywords if kw in text}
    return found


def score_bullet(job_keywords: set[str], bullet: dict) -> int:
    tags = {normalize(tag) for tag in bullet.get("tags", [])}
    overlap = job_keywords.intersection(tags)

    score = 0
    for tag in overlap:
        score += PRIORITY_TAG_WEIGHTS.get(tag, 1)

    return score


def tailor_resume_for_job(job_title: str, company: str, job_description: str = "") -> dict:
    bank = load_experience_bank()

    combined_text = f"{job_title} {job_description}"
    job_keywords = extract_keywords(combined_text)

    ranked_bullets = []

    for entry in bank.get("experience", []):
        for bullet in entry.get("bullets", []):
            score = score_bullet(job_keywords, bullet)
            if score > 0:
                ranked_bullets.append({
                    "section": entry["section"],
                    "entry_title": entry["title"],
                    "organization": entry["organization"],
                    "text": bullet["text"],
                    "tags": bullet.get("tags", []),
                    "match_score": score
                })

    ranked_bullets.sort(key=lambda x: x["match_score"], reverse=True)

    top_bullets = ranked_bullets[:6]

    recommended_skills = []
    skill_groups = bank.get("skills", {})
    for _, items in skill_groups.items():
        for item in items:
            if normalize(item) in job_keywords:
                recommended_skills.append(item)

    if not recommended_skills:
        recommended_skills = (
            skill_groups.get("languages", [])[:2]
            + skill_groups.get("frameworks", [])[:2]
            + skill_groups.get("cloud", [])[:1]
            + skill_groups.get("tools", [])[:3]
        )

    focus_areas = sorted(list(job_keywords))[:8]

    return {
        "status": "success",
        "target_job": {
            "title": job_title,
            "company": company
        },
        "focus_areas": focus_areas,
        "recommended_skills": recommended_skills[:10],
        "selected_bullets": top_bullets,
        "rules": bank.get("rules", [])
    }