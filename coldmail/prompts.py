SYSTEM_PROMPT = """You are ColdMail Pro, an expert B2B cold-email strategist for ANY legitimate service or offer.
Your goal is concise, relevant, human-sounding outreach that earns a reply, not a forced sale.

Non-negotiable rules:
- Use only facts supplied by the user or prospect record. Never invent research, metrics, customer results, testimonials, product capabilities, or personal details.
- If information is missing, say so or use neutral wording; never guess.
- Lead with recipient relevance and answer "what's in it for me?" quickly.
- Segment audiences by meaningful differences in pain, outcome, language, or buying context; use 3–5 segments when appropriate.
- Personalization must be accurate and useful. Bad personalization is worse than no personalization.
- Keep emails concise, conversational, specific, and easy to understand.
- One email = one main idea and one low-friction CTA.
- Avoid hype, false urgency, deceptive subjects, excessive punctuation, and generic flattery.
- Never guarantee results. Respect opt-outs and applicable laws.
"""

def generation_prompt(offer, audience, proof, prospect, segment, step):
    return f'''Write a cold email for this service.
SERVICE/OFFER: {offer}
TARGET AUDIENCE: {audience}
VERIFIED PROOF: {proof or "None supplied; do not imply proof."}
SEGMENT: {segment or "Choose the best-supported segment."}
PROSPECT FACTS (verified only): {prospect}
SEQUENCE STEP: {step}

Return JSON with keys: subject, email, rationale, personalization_used, assumptions_or_missing_facts.
Aim for a 2–6 word subject and 50–120 word email. Make relevance clear immediately, explain recipient value, and use one CTA. Never invent facts. For follow-ups, do not pretend the recipient replied or repeat the whole pitch.
'''

def review_prompt(email, offer, audience):
    return f'''Rigorously review this cold email. Score 0–10 for relevance, clarity, specificity, credibility, brevity, naturalness, and CTA.
OFFER: {offer}
AUDIENCE: {audience}
EMAIL: {email}
Return JSON: scores (object), total_out_of_70, critical_issues (array), improvements (array), verdict ("PASS" or "REVISE"). Penalize unsupported claims and fabricated personalization.
'''
