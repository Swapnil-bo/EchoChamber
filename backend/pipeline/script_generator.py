"""
Podcast script generation via a single Gemini call.

Design decision: one structured call, not two separate agent calls.
- 50% less API quota
- More coherent dialogue (model sees both sides simultaneously)
- Simpler error handling (single try/except)

Uses the google.genai SDK (current, replaces deprecated google.generativeai).
"""

import json
import os

from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are a podcast script writer. Given the following article text, generate a
lively, argumentative 5-minute podcast dialogue between two hosts:

- HOST (Alex): Skeptical, analytical, devil's advocate. Challenges every claim.
- EXPERT (Maya): Enthusiastic, optimistic, deeply knowledgeable about the subject.

Rules:
1. Generate exactly 16–20 dialogue turns total, strictly alternating HOST then EXPERT.
2. Each turn must be 2–4 sentences. Use natural spoken language only.
3. Start with a 2-sentence intro from HOST setting up the topic for the listener.
4. End with HOST and EXPERT reaching a nuanced, surprising agreement.
5. Optimize the dialogue for Text-to-Speech engines:
   - Write all acronyms with dashes: L-L-M, R-A-G, A-P-I, G-P-T, F-A-S-T-A-P-I
   - Write numbers as words: "forty-two percent" not "42%"
   - No markdown, bullet points, asterisks, or formatting characters anywhere.

Return ONLY a valid JSON array. No preamble, no explanation, no markdown code fences.
Format:
[
  {"speaker": "HOST", "line": "..."},
  {"speaker": "EXPERT", "line": "..."}
]"""


def generate_script(summarized_text: str) -> list:
    """Generate a podcast script from summarized article text.

    Returns a list of dicts with 'speaker' and 'line' keys.
    Raises ValueError on safety blocks or invalid JSON output.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    prompt = f"{SYSTEM_PROMPT}\n\n---\n\nArticle text:\n{summarized_text}"

    # BLOCK_ONLY_HIGH — not OFF.
    # Handles controversial/political articles while blocking genuinely harmful content.
    # OFF is a security smell in public-facing portfolio apps.
    safety_settings = [
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    ]

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(safety_settings=safety_settings),
        )

        # Strip markdown code fences if Gemini wraps the response
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]  # remove first line (```json)
            text = text.rsplit("```", 1)[0]  # remove trailing ```
            text = text.strip()

        script = json.loads(text)
        return script

    except Exception as e:
        error_msg = str(e)
        if "block" in error_msg.lower() or "safety" in error_msg.lower():
            raise ValueError(
                "Content blocked by AI safety filters. Try a different article."
            )
        elif "json" in error_msg.lower():
            raise ValueError(
                "Script generation returned invalid format. Please retry."
            )
        else:
            raise
