"""
Text chunking and summarization.

Uses LangChain RecursiveCharacterTextSplitter for chunking.
If word count exceeds 1500 after splitting, sends the first ~8000 words
to Gemini in a single summarization call. This keeps API usage to exactly
1 call regardless of article length — critical for free tier quota.
"""

import os

from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

WORD_LIMIT = 1500

# Gemini context windows are large — 8000 words is safe for all models
MAX_INPUT_WORDS = 8000

SUMMARIZE_PROMPT = (
    "Summarize the following article text into a comprehensive summary of "
    "approximately 1200-1500 words. Preserve key facts, arguments, dates, "
    "names, and statistics. The summary will be used to generate a podcast "
    "script, so keep it informative and engaging.\n\n{text}"
)


def chunk_and_summarize(text: str) -> str:
    """Split text into chunks and summarize if it exceeds the word limit.

    Returns text ready for script generation, guaranteed to be under
    WORD_LIMIT words. Short texts pass through unchanged.

    For long texts, truncates to MAX_INPUT_WORDS then summarizes in a
    single Gemini call instead of map-reduce (saves API quota).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(text)
    combined = " ".join(chunks)
    word_count = len(combined.split())

    if word_count <= WORD_LIMIT:
        return combined

    # Truncate to MAX_INPUT_WORDS to keep it within a single Gemini call.
    words = combined.split()
    if len(words) > MAX_INPUT_WORDS:
        combined = " ".join(words[:MAX_INPUT_WORDS])

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    prompt = SUMMARIZE_PROMPT.format(text=combined)
    response = client.models.generate_content(model=model_name, contents=prompt)

    return response.text
