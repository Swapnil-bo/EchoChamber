"""
Text extraction — auto-detects input type.

Handles: PDF file path, Wikipedia URL, any HTTP URL, raw pasted text.
The user never has to configure anything; detection is automatic.
"""

import re

import fitz  # PyMuPDF
import requests
import wikipediaapi
from bs4 import BeautifulSoup


# Initialize Wikipedia client with proper User-Agent.
# CRITICAL: Wikimedia API strictly enforces User-Agent policy.
# Default initialization with no user_agent returns 403 Forbidden.
wiki = wikipediaapi.Wikipedia(
    user_agent="EchoChamber/1.0 (echochamber-podcast@example.com)",
    language="en",
)


def extract_text(user_input: str) -> str:
    """Auto-detects input type and extracts text content.

    Handles:
    - PDF file paths (ending in .pdf)
    - Wikipedia URLs (containing wikipedia.org)
    - Any HTTP/HTTPS URL
    - Raw pasted text (fallback)
    """
    user_input = user_input.strip()

    if user_input.lower().endswith(".pdf"):
        return extract_pdf(user_input)
    elif "wikipedia.org" in user_input:
        return extract_wikipedia(user_input)
    elif user_input.startswith("http://") or user_input.startswith("https://"):
        return extract_url(user_input)
    else:
        return user_input  # treat as raw pasted text


def extract_url(url: str) -> str:
    """Extract readable text from a web page.
    Uses requests + BeautifulSoup, extracting only <p> tags
    and stripping <script>, <nav>, <footer> noise."""
    response = requests.get(url, timeout=15, headers={
        "User-Agent": "EchoChamber/1.0 (podcast generator)"
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Extract paragraph text only
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    if not text.strip():
        raise ValueError("Could not extract meaningful text from the URL.")

    return text


def extract_pdf(file_path: str) -> str:
    """Extract text from a PDF using PyMuPDF.
    Loops all pages, extracts text blocks, joins with newlines."""
    doc = fitz.open(file_path)
    text_parts = []

    for page in doc:
        text_parts.append(page.get_text())

    doc.close()
    text = "\n".join(text_parts)

    if not text.strip():
        raise ValueError("Could not extract text from the PDF.")

    return text


def extract_wikipedia(url: str) -> str:
    """Extract text from a Wikipedia article via the wikipedia-api library.
    Returns summary + full content."""
    # Extract page title from URL
    # Handles: https://en.wikipedia.org/wiki/Page_Title
    match = re.search(r"wikipedia\.org/wiki/(.+?)(?:#.*)?$", url)
    if not match:
        raise ValueError(f"Could not parse Wikipedia URL: {url}")

    page_title = match.group(1).replace("_", " ")
    page = wiki.page(page_title)

    if not page.exists():
        raise ValueError(f"Wikipedia page not found: {page_title}")

    return page.summary + "\n\n" + page.text
