import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv

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
COLLECTION_NAME = "openscholar_chunks"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Connecting to Qdrant...")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
print("All services connected")

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SynthesizeRequest(BaseModel):
    query: str
    paper_ids: list[str]

@app.get("/")
def root():
    return {"status": "OpenScholar API is running"}

@app.post("/search")
def search(req: SearchRequest):
    try:
        query_vector = model.encode(req.query).tolist()
        
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=req.limit
        )
        
        seen_papers = {}
        chunks = []
        
        for r in results:
            p = r.payload
            paper_id = p["paper_id"]
            
            if paper_id not in seen_papers:
                seen_papers[paper_id] = {
                    "paper_id": paper_id,
                    "title": p["title"],
                    "authors": p["authors"],
                    "abstract": p["abstract"],
                    "published": p["published"],
                    "pdf_url": p["pdf_url"],
                    "score": round(r.score, 3)
                }
            
            chunks.append({
                "chunk_id": p["chunk_id"],
                "paper_id": paper_id,
                "section": p["section"],
                "text": p["text"],
                "score": round(r.score, 3)
            })
        
        return {
            "query": req.query,
            "papers": list(seen_papers.values()),
            "chunks": chunks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    try:
        query_vector = model.encode(req.query).tolist()
        
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=20
        )
        
        relevant_chunks = [
            r for r in results
            if r.payload["paper_id"] in req.paper_ids
        ][:10]
        
        if not relevant_chunks:
            raise HTTPException(
                status_code=400,
                detail="No relevant chunks found for selected papers"
            )
        
        context = ""
        for r in relevant_chunks:
            p = r.payload
            context += f"\n[{p['title'][:50]} — {p['section']}]\n{p['text']}\n"
        
        prompt = f"""You are a research assistant. Based on the following excerpts from academic papers, write a concise literature review paragraph (3-4 sentences) about: "{req.query}"

Excerpts:
{context}

Write a synthesis that connects the key ideas across these papers. Be specific and academic in tone."""

        summary = None
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
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
            "chunks_used": len(relevant_chunks),
            "paper_ids": req.paper_ids
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/papers")
def get_papers():
    try:
        results = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=500
        )
        
        seen = {}
        for point in results[0]:
            p = point.payload
            pid = p["paper_id"]
            if pid not in seen:
                seen[pid] = {
                    "paper_id": pid,
                    "title": p["title"],
                    "authors": p["authors"],
                    "abstract": p["abstract"],
                    "published": p["published"],
                    "pdf_url": p["pdf_url"]
                }
        
        return {"papers": list(seen.values()), "total": len(seen)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))