import json
import os
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, generation_prompt, review_prompt
from .quality import local_quality_check

class ColdMailAgent:
    def __init__(self, api_key=None, model=None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("Set OPENAI_API_KEY in your environment or .env file.")
        self.client = OpenAI(api_key=key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _json(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model, temperature=0.7,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
        )
        return json.loads(response.choices[0].message.content)

    def generate(self, offer, audience, proof="", prospect=None, segment="", step="First email"):
        data = self._json(generation_prompt(offer, audience, proof, prospect or {}, segment, step))
        data.setdefault("subject", "")
        data.setdefault("email", "")
        data["local_check"] = local_quality_check(data["subject"], data["email"])
        return data

    def review(self, email, offer, audience):
        return self._json(review_prompt(email, offer, audience))
