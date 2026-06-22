import json
from pathlib import Path

def chunk_section(text, section_name, paper_id, chunk_size=400, overlap=50):
    chunks = []
    words = text.split()
    
    if not words:
        return chunks
    
    i = 0
    chunk_index = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        if len(chunk_text.strip()) > 100:
            chunks.append({
                "chunk_id": f"{paper_id}_{section_name}_{chunk_index}",
                "paper_id": paper_id,
                "section": section_name,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })
            chunk_index += 1
        
        i += chunk_size - overlap
    
    return chunks

def chunk_paper(paper):
    all_chunks = []
    paper_id = paper["id"]
    
    abstract = paper.get("abstract", "")
    if abstract:
        all_chunks.append({
            "chunk_id": f"{paper_id}_abstract_0",
            "paper_id": paper_id,
            "section": "abstract",
            "text": abstract,
            "word_count": len(abstract.split())
        })
    
    sections = paper.get("sections", {})
    for section_name, section_text in sections.items():
        if not section_text or not section_text.strip():
            continue
        chunks = chunk_section(
            section_text,
            section_name,
            paper_id
        )
        all_chunks.extend(chunks)
    
    return all_chunks

def chunk_all_papers():
    parsed_path = Path("data/papers_parsed.json")
    if not parsed_path.exists():
        print("No papers_parsed.json found. Run parse_pdf.py first.")
        return
    
    papers = json.load(open(parsed_path))
    all_chunks = []
    
    for i, paper in enumerate(papers):
        print(f"[{i+1}/{len(papers)}] Chunking: {paper['title'][:60]}...")
        chunks = chunk_paper(paper)
        all_chunks.extend(chunks)
        print(f"  Generated {len(chunks)} chunks")
    
    output_path = Path("data/chunks.json")
    with open(output_path, "w") as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"\nDone. {len(all_chunks)} total chunks saved to data/chunks.json")
    
    section_counts = {}
    for chunk in all_chunks:
        s = chunk["section"]
        section_counts[s] = section_counts.get(s, 0) + 1
    
    print("\nChunks by section:")
    for section, count in sorted(section_counts.items()):
        print(f"  {section}: {count}")
    
    return all_chunks

if __name__ == "__main__":
    chunk_all_papers()