import json
import os

from openai import OpenAI

MODEL = "gpt-4o-mini"
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


class _LLM:
    def complete_json(self, system: str, user: str) -> str:
        """Return a JSON string from the model. Retries once on parse failure."""
        client = _get_client()
        for attempt in range(2):
            response = client.chat.completions.create(
                model=MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            raw = response.choices[0].message.content or ""
            # Strip accidental code fences
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                json.loads(raw)
                return raw
            except json.JSONDecodeError:
                if attempt == 0:
                    user = user + "\n\nRespond with valid JSON only — no prose, no code fences."
        return raw


llm = _LLM()
