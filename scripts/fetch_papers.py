import arxiv
import json
import os
from pathlib import Path

def fetch_papers(category="cs.CL", max_results=50):
    print(f"Fetching {max_results} papers from arXiv category: {category}")
    
    client = arxiv.Client()
    
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in client.results(search):
        paper = {
            "id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "abstract": result.summary,
            "pdf_url": result.pdf_url,
            "published": str(result.published),
            "categories": result.categories
        }
        papers.append(paper)
        print(f"  Fetched: {paper['title'][:60]}...")
    
    os.makedirs("data", exist_ok=True)
    output_path = Path("data/papers_metadata.json")
    with open(output_path, "w") as f:
        json.dump(papers, f, indent=2)
    
    print(f"\nDone. {len(papers)} papers saved to {output_path}")
    return papers

if __name__ == "__main__":
    fetch_papers(category="cs.CL", max_results=20)