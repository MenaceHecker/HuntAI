import re
from services.profile_service import load_profile
from services.tailoring_service import extract_keywords

STRONG_TITLE_DOMAINS = {
    "infrastructure": 8,
    "platform": 8,
    "distributed systems": 8,
    "telemetry": 7,
    "observability": 7,
    "monitoring": 7,
    "reliability": 7,
    "backend": 5,
    "ci/cd": 6,
    "developer experience": 5,
    "product platform": 5,
    "full stack": 7,
    "mobile": 6,
}

WEAK_TITLE_DOMAINS = {
    "ads": -8,
    "brands": -6,
    "frontend": -5,
    "ui": -6,
}

STRONG_DESCRIPTION_DOMAINS = {
    "infrastructure",
    "platform",
    "distributed systems",
    "backend",
    "reliability",
    "observability",
    "monitoring",
    "telemetry",
    "sre",
    "cloud",
    "ci/cd",
    "automation",
    "security",
}

WEAK_DESCRIPTION_DOMAINS = {
    "ads",
    "brands",
    "ui",
    "design",
}


def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_any(text: str, terms: list[str]) -> bool:
    text = normalize(text)
    return any(normalize(term) in text for term in terms)


def count_matches(text: str, terms: list[str]) -> int:
    text = normalize(text)
    matches = 0
    for term in terms:
        normalized_term = normalize(term)
        if normalized_term in text:
            matches += 1
    return matches


def compute_title_domain_score(title: str) -> int:
    t = normalize(title)
    score = 0

    for term, points in STRONG_TITLE_DOMAINS.items():
        if term in t:
            score += points

    for term, points in WEAK_TITLE_DOMAINS.items():
        if term in t:
            score += points

    return max(-10, min(score, 12))


def compute_description_domain_score(description: str) -> int:
    keywords = extract_keywords(description)

    strong_matches = len(keywords.intersection(STRONG_DESCRIPTION_DOMAINS))
    weak_matches = len(keywords.intersection(WEAK_DESCRIPTION_DOMAINS))

    score = strong_matches * 2
    score -= weak_matches * 2

    return max(0, min(score, 6))


def get_verdict(score: int) -> str:
    if score >= 80:
        return "Strong Apply"
    if score >= 65:
        return "Good Match"
    if score >= 50:
        return "Maybe Apply"
    return "Skip"


def build_match_reasons(job, breakdown: dict) -> list[str]:
    reasons = []

    location = normalize(job.location)

    if breakdown.get("title_match", 0) > 0:
        reasons.append("strong software engineering title match")

    title_domain = breakdown.get("title_domain", 0)
    description_domain = breakdown.get("description_domain", 0)

    if title_domain >= 8:
        reasons.append("title strongly aligns with your preferred engineering domains")
    elif title_domain > 0:
        reasons.append("title shows some alignment with your target engineering domains")

    if description_domain >= 4:
        reasons.append("job description reinforces backend/platform/infrastructure alignment")
    elif description_domain > 0:
        reasons.append("job description shows some supporting domain overlap")

    if breakdown.get("must_have_skills", 0) >= 10:
        reasons.append("multiple core skills matched")
    elif breakdown.get("must_have_skills", 0) > 0:
        reasons.append("at least one core skill matched")

    if breakdown.get("nice_to_have_skills", 0) >= 6:
        reasons.append("good overlap with supporting tools and stack")
    elif breakdown.get("nice_to_have_skills", 0) > 0:
        reasons.append("some overlap with supporting tools")

    if breakdown.get("location", 0) > 0:
        if "remote" in location:
            reasons.append("preferred remote or U.S. location")
        else:
            reasons.append("preferred location match")

    if breakdown.get("sponsorship", 0) >= 15:
        reasons.append("clear sponsorship signal")
    elif breakdown.get("sponsorship", 0) > 0:
        reasons.append("sponsorship status not explicitly negative")

    return reasons[:4]


def score_job(job) -> dict:
    profile = load_profile()

    title = normalize(job.title)
    description = normalize(job.description)
    location = normalize(job.location)
    combined_text = f"{title} {description}"

    score = 0
    breakdown = {}

    preferred_titles = profile["preferred_titles"]
    title_points = 25 if contains_any(title, preferred_titles) else 0
    score += title_points
    breakdown["title_match"] = title_points

    title_domain_points = compute_title_domain_score(job.title)
    score += title_domain_points
    breakdown["title_domain"] = title_domain_points

    description_domain_points = compute_description_domain_score(job.description)
    score += description_domain_points
    breakdown["description_domain"] = description_domain_points

    positive_sponsorship_terms = [
        "h1b",
        "visa sponsorship",
        "sponsorship available",
        "will sponsor",
        "we sponsor visas",
        "employment visa",
        "opt",
        "cpt",
    ]
    negative_sponsorship_terms = [
        "no sponsorship",
        "do not sponsor",
        "unable to sponsor",
        "must be authorized to work without sponsorship",
        "not provide visa sponsorship",
        "no visa support",
    ]

    if contains_any(description, negative_sponsorship_terms):
        sponsorship_points = 0
    elif contains_any(description, positive_sponsorship_terms):
        sponsorship_points = 15
    else:
        sponsorship_points = 5

    score += sponsorship_points
    breakdown["sponsorship"] = sponsorship_points

    must_have_skills = profile["must_have_skills"]
    must_matches = count_matches(combined_text, must_have_skills)
    must_points = min(25, must_matches * 5)
    score += must_points
    breakdown["must_have_skills"] = must_points

    nice_to_have_skills = profile["nice_to_have_skills"]
    nice_matches = count_matches(combined_text, nice_to_have_skills)
    nice_points = min(12, nice_matches * 3)
    score += nice_points
    breakdown["nice_to_have_skills"] = nice_points

    preferred_locations = profile["preferred_locations"]
    location_points = 5 if contains_any(location, preferred_locations) else 0
    score += location_points
    breakdown["location"] = location_points

    blocked_terms = profile["blocked_seniority_terms"]
    penalty = 20 if contains_any(title, blocked_terms) else 0
    score -= penalty
    breakdown["seniority_penalty"] = -penalty

    final_score = max(0, min(100, score))
    verdict = get_verdict(final_score)
    reasons = build_match_reasons(job, breakdown)

    return {
        "job": job,
        "score": final_score,
        "breakdown": breakdown,
        "verdict": verdict,
        "reasons": reasons,
    }


def score_jobs(jobs: list) -> list[dict]:
    scored = [score_job(job) for job in jobs]
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored