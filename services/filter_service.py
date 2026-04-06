def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def is_relevant_role(title: str) -> bool:
    title = normalize_text(title)

    allowed_keywords = [
        "software engineer",
        "backend engineer",
        "platform engineer",
        "full stack engineer",
        "full-stack engineer",
        "frontend engineer",
        "developer",
        "sre",
        "site reliability",
        "devops",
        "cloud engineer",
        "infrastructure engineer",
    ]

    blocked_keywords = [
        "senior",
        "staff",
        "principal",
        "manager",
        "director",
        "intern",
        "sales",
        "designer",
        "recruiter",
    ]

    if any(word in title for word in blocked_keywords):
        return False

    return any(word in title for word in allowed_keywords)


def sponsorship_signal(description: str) -> bool:
    text = normalize_text(description)

    positive = [
        "h1b",
        "visa sponsorship",
        "sponsorship available",
        "will sponsor",
        "opt",
        "cpt",
    ]

    negative = [
        "no sponsorship",
        "do not sponsor",
        "unable to sponsor",
        "not provide visa sponsorship",
        "must be authorized to work without sponsorship",
    ]

    if any(term in text for term in negative):
        return False

    return any(term in text for term in positive)