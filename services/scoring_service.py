from services.profile_service import load_profile


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def contains_any(text: str, terms: list[str]) -> bool:
    text = normalize(text)
    return any(term in text for term in terms)


def count_matches(text: str, terms: list[str]) -> int:
    text = normalize(text)
    return sum(1 for term in terms if term in text)


def score_job(job) -> dict:
    profile = load_profile()

    title = normalize(job.title)
    description = normalize(job.description)
    location = normalize(job.location)
    combined_text = f"{title} {description}"

    score = 0
    breakdown = {}

    # 1. Title match: 0-25
    preferred_titles = profile["preferred_titles"]
    title_points = 25 if contains_any(title, preferred_titles) else 0
    score += title_points
    breakdown["title_match"] = title_points

    # 2. Sponsorship signal: 0-25
    positive_sponsorship_terms = [
        "h1b",
        "visa sponsorship",
        "sponsorship available",
        "will sponsor",
        "opt",
        "cpt"
    ]
    negative_sponsorship_terms = [
        "no sponsorship",
        "do not sponsor",
        "unable to sponsor",
        "must be authorized to work without sponsorship",
        "not provide visa sponsorship"
    ]

    if contains_any(description, negative_sponsorship_terms):
        sponsorship_points = 0
    elif contains_any(description, positive_sponsorship_terms):
        sponsorship_points = 25
    else:
        sponsorship_points = 15

    score += sponsorship_points
    breakdown["sponsorship"] = sponsorship_points

    # 3. Must-have skills: 0-25
    must_have_skills = profile["must_have_skills"]
    must_matches = count_matches(combined_text, must_have_skills)
    must_points = min(25, must_matches * 5)
    score += must_points
    breakdown["must_have_skills"] = must_points

    # 4. Nice-to-have skills: 0-15
    nice_to_have_skills = profile["nice_to_have_skills"]
    nice_matches = count_matches(combined_text, nice_to_have_skills)
    nice_points = min(15, nice_matches * 3)
    score += nice_points
    breakdown["nice_to_have_skills"] = nice_points

    # 5. Preferred location: 0-10
    preferred_locations = profile["preferred_locations"]
    location_points = 10 if contains_any(location, preferred_locations) else 0
    score += location_points
    breakdown["location"] = location_points

    # 6. Seniority penalty: subtract up to 20
    blocked_terms = profile["blocked_seniority_terms"]
    penalty = 20 if contains_any(title, blocked_terms) else 0
    score -= penalty
    breakdown["seniority_penalty"] = -penalty

    final_score = max(0, min(100, score))

    return {
        "job": job,
        "score": final_score,
        "breakdown": breakdown
    }


def score_jobs(jobs: list) -> list[dict]:
    scored = [score_job(job) for job in jobs]
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored