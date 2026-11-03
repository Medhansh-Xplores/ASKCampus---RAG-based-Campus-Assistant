# AskCampus — Context-Aware RAG-Based Campus Assistant

AskCampus is an intelligent campus information assistant that answers questions about academics, admissions, campus facilities, and student life. It retrieves relevant information from curated FAQs and trusted institute web pages, then uses a language model to generate context-aware responses grounded in the retrieved content.

## Features

- **Retrieval-Augmented Generation (RAG):** Retrieves relevant campus information before generating an answer.
- **Semantic search:** Uses OpenAI embeddings and FAISS for similarity-based document retrieval.
- **Web data ingestion:** Scrapes configured institute pages using Requests and BeautifulSoup.
- **Curated knowledge base:** Supports local FAQ and reference documents in TXT and Markdown formats.
- **Conversational interface:** Flask-powered chat interface with recent conversation context.
- **Source transparency:** Displays the retrieved source names and relevant excerpts alongside answers.
- **Grounded responses:** Instructs the assistant to acknowledge when the knowledge base does not contain enough information instead of inventing details.

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| RAG orchestration | LangChain |
| Embeddings and generation | OpenAI API |
| Vector database | FAISS |
| Data ingestion | BeautifulSoup, Requests |
| Frontend | HTML, CSS, JavaScript |

## Project Structure

```text
askcampus/
├── app.py
├── rag.py
├── ingest.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── faqs/
│       └── sample_campus_faq.txt
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── app.js
```

The `faiss_index/` directory is generated when the ingestion script runs and is excluded from Git.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/askcampus.git
cd askcampus
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the OpenAI API key

Create a `.env` file from the example:

**Windows:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit `.env` or expose your API key in source code.

### 5. Add campus knowledge sources

Add verified campus information to `data/faqs/` as `.txt` or `.md` files.

To scrape official institute pages, add their URLs to the `SOURCE_URLS` list in `ingest.py`:

```python
SOURCE_URLS = [
    "https://www.example.edu/academics",
    "https://www.example.edu/admissions",
]
```

Use official, publicly accessible pages and review their content before indexing. Respect the website's terms of use, robots policies, and request limits.

The included FAQ file is demonstration content. Replace it with verified institute information before relying on the assistant for real campus queries.

### 6. Build the FAISS index

```bash
python ingest.py
```

This script loads local FAQ documents, fetches configured web pages, splits the content into overlapping chunks, generates embeddings using the OpenAI API, and saves a local FAISS index.

Run the ingestion script again whenever the source content changes.

### 7. Start the application

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## How It Works

1. **Data collection:** Curated FAQs are loaded from `data/faqs/`; configured official pages are fetched using Requests and parsed with BeautifulSoup.
2. **Text processing:** LangChain's recursive text splitter divides source documents into manageable chunks with overlap.
3. **Embedding generation:** OpenAI embeddings convert each chunk into a vector representation.
4. **Indexing:** FAISS stores the vectors for efficient similarity search.
5. **Retrieval:** A user question is embedded and the most relevant chunks are retrieved.
6. **Response generation:** The retrieved context and recent conversation are passed to the chat model through a LangChain prompt.
7. **Source display:** The interface presents source names and excerpts used to formulate the response.

## API

### `POST /api/chat`

Accepts JSON:

```json
{
  "question": "What academic programmes are available?",
  "history": [
    {
      "role": "user",
      "content": "I am interested in engineering."
    }
  ]
}
```

Returns:

```json
{
  "answer": "Answer generated using the retrieved campus context.",
  "sources": [
    {
      "name": "academics.txt",
      "excerpt": "Relevant retrieved text..."
    }
  ]
}
```

### `GET /api/health`

Returns the service status and whether a FAISS knowledge index is loaded.

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | — | API key for embeddings and chat |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Response generation model |
| `PORT` | `5000` | Flask server port |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |

## Notes and Limitations

- OpenAI API usage may incur charges.
- The initial indexing process requires an internet connection and a valid API key.
- The FAISS index is generated locally and should be rebuilt when source documents change.
- Some websites may block automated requests or render important content dynamically; those pages may need a different ingestion method.
- Scanned PDFs and image-based documents are not parsed by the current ingestion pipeline.
- Response quality depends on the coverage, accuracy, and freshness of the indexed sources.
- The included sample FAQ is illustrative and must be replaced with verified institutional information.

## Responsible Use

AskCampus is an informational assistant, not an official institute authority. Verify important information such as admission eligibility, application deadlines, fees, academic regulations, and policy changes with the relevant institute office or official website. Do not index private student records or confidential institutional information without authorization.

## License

This project is available under the MIT License. Add a `LICENSE` file if you intend to distribute it under that license.
