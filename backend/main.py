import os
import json
import arxiv
import httpx
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from PyPDF2 import PdfReader
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv
import re
import time
import traceback

load_dotenv()

app = FastAPI(title="OpenScholar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = "openscholar_live"
VECTOR_SIZE = 384

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Connecting to Qdrant...")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
print("All services connected")

def ensure_collection():
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Created collection {COLLECTION_NAME}")

ensure_collection()

def download_and_chunk_pdf(pdf_url, paper_id, title):
    chunks = []
    try:
        headers = {"User-Agent": "OpenScholar/1.0 (research project)"}
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(pdf_url, headers=headers)
            response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(response.content)
            tmp_path = f.name

        reader = PdfReader(tmp_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        os.unlink(tmp_path)

        words = full_text.split()
        chunk_size = 400
        overlap = 50
        i = 0
        idx = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if len(chunk_text.strip()) > 100:
                chunks.append({
                    "chunk_id": f"{paper_id}_chunk_{idx}",
                    "paper_id": paper_id,
                    "text": chunk_text,
                    "title": title
                })
                idx += 1
            i += chunk_size - overlap

        time.sleep(2)

    except Exception as e:
        print(f"Could not process PDF for {paper_id}: {e}")

    return chunks

def store_chunks_in_qdrant(chunks, paper_meta):
    if not chunks:
        return

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, batch_size=32)

    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=abs(hash(chunk["chunk_id"])) % (2**63),
            vector=embedding.tolist(),
            payload={
                **chunk,
                "authors": paper_meta.get("authors", []),
                "abstract": paper_meta.get("abstract", ""),
                "published": paper_meta.get("published", ""),
                "pdf_url": paper_meta.get("pdf_url", "")
            }
        ))

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

class SearchRequest(BaseModel):
    query: str
    max_results: int = 15

class SynthesizeRequest(BaseModel):
    query: str
    paper_ids: list[str]
    papers_meta: list[dict]

@app.get("/")
def root():
    return {"status": "OpenScholar API is running"}

@app.post("/search")
def search(req: SearchRequest):
    try:
        arxiv_client = arxiv.Client()
        arxiv_search = arxiv.Search(
            query=req.query,
            max_results=req.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in arxiv_client.results(arxiv_search):
            papers.append({
                "paper_id": result.entry_id.split("/")[-1],
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "abstract": result.summary,
                "pdf_url": result.pdf_url,
                "published": str(result.published),
                "arxiv_url": result.entry_id
            })

        return {
            "query": req.query,
            "papers": papers,
            "total": len(papers)
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    try:
        all_chunks = []

        for paper_meta in req.papers_meta:
            paper_id = paper_meta["paper_id"]
            print(f"Processing {paper_id}...")

            # THIS IS THE FIX: Using explicit Qdrant Filter objects
            existing = qdrant.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[FieldCondition(key="paper_id", match=MatchValue(value=paper_id))]
                ),
                limit=1
            )

            if existing[0]:
                print(f"  Already in Qdrant, skipping download")
            else:
                print(f"  Downloading and chunking PDF...")
                chunks = download_and_chunk_pdf(
                    paper_meta["pdf_url"],
                    paper_id,
                    paper_meta["title"]
                )
                if chunks:
                    store_chunks_in_qdrant(chunks, paper_meta)
                    print(f"  Stored {len(chunks)} chunks")

        query_vector = model.encode(req.query).tolist()
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=20
        )

        relevant = [
            r for r in results
            if r.payload.get("paper_id") in req.paper_ids
        ][:10]

        if not relevant:
            context_parts = []
            for paper_meta in req.papers_meta:
                context_parts.append(f"[{paper_meta['title']}]\nAbstract: {paper_meta['abstract']}")
            context = "\n\n".join(context_parts)
            source = "abstracts"
        else:
            context = ""
            for r in relevant:
                p = r.payload
                context += f"\n[{p['title'][:60]}]\n{p['text']}\n"
            source = "full text"

        prompt = f"""You are a research assistant. Based on the following excerpts from academic papers, write a concise literature review paragraph (4-5 sentences) about: "{req.query}"

{context}

Write a synthesis that connects the key ideas. Be specific and academic in tone. Mention paper titles where relevant."""

        summary = None

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            summary = response.choices[0].message.content
        except Exception as groq_error:
            print(f"Groq failed: {groq_error} — trying Gemini")
            try:
                gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                response = gemini_model.generate_content(prompt)
                summary = response.text
            except Exception as gemini_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Both LLMs failed. Groq: {groq_error}. Gemini: {gemini_error}"
                )

        return {
            "query": req.query,
            "summary": summary,
            "source": source,
            "papers_processed": len(req.paper_ids)
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
