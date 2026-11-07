import re

SPAMMY = [
    "guaranteed", "100% free", "act now", "limited time", "make millions",
    "no risk", "!!!", "dear friend"
]
DECEPTIVE = ["re:", "fwd:", "following up on our call", "as discussed"]
CLICHES = [
    "i hope this email finds you well",
    "i wanted to reach out",
    "just checking in",
    "touch base",
    "circle back",
    "game-changer",
    "game changer",
    "unlock your",
    "supercharge",
    "take your business to the next level",
    "tailored solutions",
    "cutting-edge",
    "in today's fast-paced world",
    "in today’s fast-paced world",
    "boost your business",
    "i came across your company",
    "seamless solution",
]
OBSERVATION_CLAIMS = [
    "i noticed", "i saw that", "i checked your", "after looking at your",
    "your website is", "your site is", "your team is hiring",
]


def local_quality_check(subject: str, body: str, verified_facts=None) -> dict:
    text = f"{subject}\n{body}".lower()
    body_lower = body.lower()
    facts_text = str(verified_facts or "").strip()
    issues = []
    if not subject.strip():
        issues.append("Missing subject line.")
    if len(subject) > 65:
        issues.append("Subject is long; keep it under 65 characters.")
    subject_words = re.findall(r"\b[\w'-]+\b", subject)
    if len(subject_words) > 8:
        issues.append("Subject may be too long; remove unnecessary words.")
    words = re.findall(r"\b[\w'-]+\b", body)
    if len(words) > 130:
        issues.append("Email is long; aim for roughly 50–110 words for a first email.")
    if len(words) < 25:
        issues.append("Email may be too short to establish relevance and value.")
    if body.count("?") > 2:
        issues.append("Use one clear question or CTA.")
    for term in SPAMMY:
        if term in text:
            issues.append(f"Potentially spammy wording: {term}")
    for term in DECEPTIVE:
        if term in subject.lower():
            issues.append(f"Potentially deceptive subject wording: {term}")
    for phrase in CLICHES:
        if phrase in text:
            issues.append(f"Stock phrase or marketing cliché: {phrase}")
    if not facts_text:
        for phrase in OBSERVATION_CLAIMS:
            if phrase in body_lower:
                issues.append(
                    "Possible unsupported prospect observation. Add its source as a verified fact or rewrite without claiming you observed it."
                )
                break
    placeholders = re.findall(r"\[[^\]]+\]|\{\{[^}]+\}\}", body + "\n" + subject)
    if placeholders:
        issues.append("Unresolved merge fields: " + ", ".join(placeholders))
    if body.count("!") > 1:
        issues.append("Reduce exclamation marks.")
    return {
        "passed": not issues,
        "issues": issues,
        "word_count": len(words),
        "subject_word_count": len(subject_words),
        "unresolved_placeholders": placeholders,
    }