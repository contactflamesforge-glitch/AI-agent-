import re

SPAMMY = ["guaranteed", "100% free", "act now", "limited time", "make millions", "no risk", "!!!", "dear friend"]
DECEPTIVE = ["re:", "fwd:", "following up on our call", "as discussed"]

def local_quality_check(subject: str, body: str) -> dict:
    text = f"{subject}\n{body}".lower()
    issues = []
    if not subject.strip():
        issues.append("Missing subject line.")
    if len(subject) > 65:
        issues.append("Subject is long; aim for 2–6 words and under 65 characters.")
    words = re.findall(r"\b[\w'-]+\b", body)
    if len(words) > 150:
        issues.append("Email is long; aim for roughly 50–120 words.")
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
    if body.count("!") > 1:
        issues.append("Reduce exclamation marks.")
    return {"passed": not issues, "issues": issues, "word_count": len(words)}
