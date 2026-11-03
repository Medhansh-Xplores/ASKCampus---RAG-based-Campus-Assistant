"""Build or refresh the local FAISS campus knowledge index.

1. Add curated .txt or .md files under data/faqs/.
2. Add trusted public institute URLs to SOURCE_URLS below.
3. Run: python ingest.py
"""
import os
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
FAQ_DIR = BASE_DIR / "data" / "faqs"
INDEX_DIR = BASE_DIR / "faiss_index"

# Add verified institute pages here. Keep this list restricted to official sources.
SOURCE_URLS = [
    # "https://www.example.edu/admissions",
    # "https://www.example.edu/academics",
]


def scrape_page(url):
    headers = {"User-Agent": "AskCampusKnowledgeBot/1.0 (educational project)"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else urlparse(url).netloc
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(" ", strip=True)
    return Document(page_content=text, metadata={"source": title, "url": url})


def load_faq_documents():
    docs = []
    for path in FAQ_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            content = path.read_text(encoding="utf-8", errors="ignore").strip()
            if content:
                docs.append(Document(
                    page_content=content,
                    metadata={"source": path.name, "file": str(path.relative_to(BASE_DIR))}
                ))
    return docs


def main():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")

    documents = load_faq_documents()
    for url in SOURCE_URLS:
        try:
            documents.append(scrape_page(url))
            print(f"Fetched: {url}")
        except requests.RequestException as exc:
            print(f"Skipped {url}: {exc}")

    if not documents:
        raise SystemExit("No knowledge sources found. Add FAQ files or official URLs, then rerun.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=api_key
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(INDEX_DIR))
    print(f"Indexed {len(documents)} source(s) into {len(chunks)} chunks at {INDEX_DIR}")


if __name__ == "__main__":
    main()
