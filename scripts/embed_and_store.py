import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "openscholar_chunks"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

def setup_qdrant_collection(client):
    existing = [c.name for c in client.get_collections().collections]
    
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists — skipping creation")
        return
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"Created collection '{COLLECTION_NAME}'")

def embed_and_store():
    chunks_path = Path("data/chunks.json")
    if not chunks_path.exists():
        print("No chunks.json found. Run chunker.py first.")
        return
    
    chunks = json.load(open(chunks_path))
    print(f"Loaded {len(chunks)} chunks")
    
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded")
    
    print("\nConnecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    setup_qdrant_collection(client)
    
    texts = [c["text"] for c in chunks]
    print(f"\nGenerating embeddings for {len(texts)} chunks...")
    print("This will take 1-2 minutes...")
    
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True
    )
    print(f"Embeddings shape: {embeddings.shape}")
    
    print("\nUploading to Qdrant...")
    points = []
    
    papers_path = Path("data/papers_parsed.json")
    papers = json.load(open(papers_path))
    papers_map = {p["id"]: p for p in papers}
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        paper = papers_map.get(chunk["paper_id"], {})
        
        points.append(PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                "chunk_id": chunk["chunk_id"],
                "paper_id": chunk["paper_id"],
                "section": chunk["section"],
                "text": chunk["text"],
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "abstract": paper.get("abstract", ""),
                "published": paper.get("published", ""),
                "pdf_url": paper.get("pdf_url", "")
            }
        ))
    
    batch_size = 50
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
        print(f"  Uploaded {min(i + batch_size, len(points))}/{len(points)} points")
    
    print(f"\nDone. {len(points)} vectors stored in Qdrant")
    
    print("\nTesting search...")
    query = "attention mechanism transformer"
    query_vector = model.encode(query).tolist()
    
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    
    print(f"Top 3 results for '{query}':")
    for r in results:
        print(f"  Score: {r.score:.3f} | {r.payload['title'][:50]} | section: {r.payload['section']}")

if __name__ == "__main__":
    embed_and_store()