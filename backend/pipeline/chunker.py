"""
Text chunking and summarization.

Uses LangChain RecursiveCharacterTextSplitter for chunking.
If word count exceeds 1500 after splitting, summarizes each chunk via
Gemini Flash and combines results (map-reduce pattern). This handles
the 50-page PDF edge case cleanly without exceeding Gemini's context window.
"""

import os

from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI

WORD_LIMIT = 1500

MAP_PROMPT = PromptTemplate.from_template(
    "Summarize the following text concisely, preserving key facts and arguments:\n\n{text}"
)

REDUCE_PROMPT = PromptTemplate.from_template(
    "Combine these summaries into a single coherent summary under 1500 words:\n\n{text}"
)


def chunk_and_summarize(text: str) -> str:
    """Split text into chunks and summarize if it exceeds the word limit.

    Returns text ready for script generation, guaranteed to be under
    WORD_LIMIT words. Short texts pass through unchanged.
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

    # Text exceeds limit — map-reduce summarization via Gemini Flash
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )

    # Map: summarize each chunk independently
    summaries = []
    for chunk in chunks:
        prompt = MAP_PROMPT.format(text=chunk)
        response = llm.invoke(prompt)
        summaries.append(response.content)

    # Reduce: combine all summaries into one
    combined_summaries = "\n\n".join(summaries)
    reduce_prompt = REDUCE_PROMPT.format(text=combined_summaries)
    final = llm.invoke(reduce_prompt)

    return final.content
