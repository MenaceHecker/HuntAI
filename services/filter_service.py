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
        "software developer",
        "application engineer",
        "cloud engineer",
        "infrastructure engineer",
        "devops engineer",
        "site reliability engineer",
        "sre",
        "new grad software engineer",
        "early career software engineer"
    ]

    blocked_keywords = [
        "senior",
        "staff",
        "principal",
        "manager",
        "director",
        "intern",
        "recruiter",
        "curriculum",
        "developer success",
        "customer success",
        "solutions consultant",
        "sales",
        "security instructor"
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