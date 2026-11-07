import json
import os
from google import genai
from google.genai import types
from .prompts import SYSTEM_PROMPT, generation_prompt, review_prompt
from .quality import local_quality_check


class ColdMailAgent:
    def __init__(self, api_key=None, model=None, provider="gemini"):
        self.provider = provider
        if provider != "gemini":
            raise ValueError("Unsupported AI provider. Select Google Gemini.")
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Add your Google Gemini API key in the app configuration.")
        self.client = genai.Client(api_key=key)
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def _json(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.55,
                response_mime_type="application/json",
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response. Please try again.")
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini returned a response that was not valid JSON. Please try again.") from exc

    def generate(self, offer, audience, proof="", prospect=None, segment="", step="First email",
                 segment_problem="", desired_outcome="", differentiator=""):
        data = self._json(generation_prompt(
            offer, audience, proof, prospect or {}, segment, step,
            segment_problem, desired_outcome, differentiator
        ))
        data.setdefault("subject", "")
        data.setdefault("email", "")
        data["local_check"] = local_quality_check(
            data["subject"], data["email"], verified_facts=prospect
        )
        return data

    def review(self, email, offer, audience):
        return self._json(review_prompt(email, offer, audience))
