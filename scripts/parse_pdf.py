import arxiv
import json
import os
import time
import httpx
from pathlib import Path
from PyPDF2 import PdfReader
import io

def download_pdf(pdf_url, paper_id):
    os.makedirs("data/pdfs", exist_ok=True)
    pdf_path = Path(f"data/pdfs/{paper_id}.pdf")
    
    if pdf_path.exists():
        print(f"  Already downloaded: {paper_id}")
        return pdf_path
    
    print(f"  Downloading: {paper_id}")
    headers = {"User-Agent": "OpenScholar/1.0 (research project)"}
    
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        response = client.get(pdf_url, headers=headers)
        response.raise_for_status()
        pdf_path.write_bytes(response.content)
    
    time.sleep(3)
    return pdf_path

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"  Warning: could not read {pdf_path}: {e}")
        return ""
    return text

def detect_sections(text):
    import re
    sections = {
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "conclusion": "",
        "other": ""
    }
    
    patterns = {
        "abstract": r"(abstract)(.*?)(introduction|1\.|background)",
        "introduction": r"(introduction|1\.)(.*?)(related work|2\.|method|background)",
        "methods": r"(method|methodology|approach|3\.)(.*?)(experiment|result|evaluation|4\.)",
        "results": r"(result|experiment|evaluation)(.*?)(conclusion|discussion|5\.)",
        "conclusion": r"(conclusion|discussion)(.*?)(reference|bibliograph)"
    }
    
    text_lower = text.lower()
    
    for section, pattern in patterns.items():
        match = re.search(pattern, text_lower, re.DOTALL)
        if match:
            start = match.start(2)
            end = match.end(2)
            sections[section] = text[start:end][:3000]
    
    if not any(sections.values()):
        sections["other"] = text[:5000]
    
    return sections

def parse_all_papers():
    metadata_path = Path("data/papers_metadata.json")
    if not metadata_path.exists():
        print("No papers_metadata.json found. Run fetch_papers.py first.")
        return
    
    papers = json.load(open(metadata_path))
    parsed = []
    
    for i, paper in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}] {paper['title'][:60]}...")
        
        try:
            pdf_path = download_pdf(paper["pdf_url"], paper["id"])
            text = extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                print("  Skipping — could not extract text")
                continue
            
            sections = detect_sections(text)
            
            parsed_paper = {
                **paper,
                "full_text_length": len(text),
                "sections": sections
            }
            parsed.append(parsed_paper)
            print(f"  Parsed successfully. Text length: {len(text)} chars")
            
        except Exception as e:
            print(f"  Error: {e} — skipping")
            continue
    
    output_path = Path("data/papers_parsed.json")
    with open(output_path, "w") as f:
        json.dump(parsed, f, indent=2)
    
    print(f"\nDone. {len(parsed)} papers parsed and saved to {output_path}")
    return parsed

if __name__ == "__main__":
    parse_all_papers()