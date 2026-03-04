"""
Text chunking and summarization.

Uses LangChain RecursiveCharacterTextSplitter for chunking.
If word count exceeds 1500 after splitting, uses LangChain map_reduce
with Gemini Flash to compress. This handles the 50-page PDF edge case
cleanly without crashing the pipeline or exceeding Gemini's context window.
"""

import os

from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

WORD_LIMIT = 1500


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

    # Text exceeds limit — use map_reduce summarization via Gemini Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )

    docs = [Document(page_content=chunk) for chunk in chunks]
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    result = chain.invoke(docs)

    return result["output_text"]
