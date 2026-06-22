content = open('/workspaces/openscholar/frontend/write_app.py').read()

jsx = """import { useState } from "react"
import axios from "axios"

const API = import.meta.env.VITE_API_URL

export default function App() {
  const [query, setQuery] = useState("")
  const [papers, setPapers] = useState([])
  const [selected, setSelected] = useState([])
  const [summary, setSummary] = useState("")
  const [loading, setLoading] = useState(false)
  const [synthesizing, setSynthesizing] = useState(false)
  const [tab, setTab] = useState("search")

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setPapers([])
    setSelected([])
    setSummary("")
    try {
      const r = await axios.post(API + "/search", { query, max_results: 15 })
      setPapers(r.data.papers)
      setTab("search")
    } catch (e) {
      alert("Search failed: " + e.message)
    }
    setLoading(false)
  }

  const toggleSelect = (paper) => {
    setSelected(prev =>
      prev.find(p => p.paper_id === paper.paper_id)
        ? prev.filter(p => p.paper_id !== paper.paper_id)
        : [...prev, paper]
    )
  }

  const isSelected = (paper_id) => selected.some(p => p.paper_id === paper_id)

  const synthesize = async () => {
    if (selected.length === 0) return alert("Select at least one paper first")
    setSynthesizing(true)
    setSummary("")
    setTab("synthesis")
    try {
      const r = await axios.post(API + "/synthesize", {
        query,
        paper_ids: selected.map(p => p.paper_id),
        papers_meta: selected
      })
      setSummary(r.data.summary)
    } catch (e) {
      alert("Synthesis failed: " + e.message)
    }
    setSynthesizing(false)
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, margin: "0 0 4px" }}>OpenScholar</h1>
        <p style={{ color: "#666", margin: 0 }}>Search 2M+ arXiv papers and synthesize literature reviews with AI</p>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem" }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="e.g. retrieval augmented generation, vision transformers..."
          style={{ flex: 1, padding: "10px 14px", fontSize: 15, border: "1px solid #ddd", borderRadius: 8 }}
        />
        <button onClick={search} disabled={loading}
          style={{ padding: "10px 20px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer" }}>
          {loading ? "Searching..." : "Search"}
        </button>
        {selected.length > 0 && (
          <button onClick={synthesize} disabled={synthesizing}
            style={{ padding: "10px 20px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer" }}>
            {synthesizing ? "Processing..." : "Synthesize (" + selected.length + ")"}
          </button>
        )}
      </div>

      {selected.length > 0 && (
        <div style={{ marginBottom: "1rem", padding: "8px 14px", background: "#eff6ff", borderRadius: 8, fontSize: 13, color: "#1d4ed8" }}>
          {selected.length} paper(s) selected
          {synthesizing && " — downloading PDFs, this takes ~30 seconds..."}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem", borderBottom: "1px solid #eee", paddingBottom: 8 }}>
        {["search", "synthesis"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "6px 16px", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 14,
              background: tab === t ? "#2563eb" : "#f3f4f6",
              color: tab === t ? "#fff" : "#444" }}>
            {t === "search" ? "Results (" + papers.length + ")" : "Synthesis"}
          </button>
        ))}
      </div>

      {tab === "search" && (
        <div>
          {papers.length === 0 && !loading && (
            <p style={{ color: "#999", textAlign: "center", marginTop: "3rem" }}>
              Search any topic to find papers from all of arXiv
            </p>
          )}
          {papers.map(paper => (
            <div key={paper.paper_id} style={{
              border: isSelected(paper.paper_id) ? "2px solid #2563eb" : "1px solid #e5e7eb",
              borderRadius: 10, padding: "1rem 1.25rem", marginBottom: 12,
              background: isSelected(paper.paper_id) ? "#eff6ff" : "#fff"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: "0 0 4px", fontSize: 16, fontWeight: 600 }}>{paper.title}</h3>
                  <p style={{ margin: "0 0 6px", fontSize: 13, color: "#666" }}>
                    {paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 ? " et al." : ""} · {paper.published ? paper.published.slice(0, 10) : ""}
                  </p>
                  <p style={{ margin: 0, fontSize: 14, color: "#444", lineHeight: 1.6 }}>
                    {paper.abstract ? paper.abstract.slice(0, 250) + "..." : ""}
                  </p>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, minWidth: 90 }}>
                  <button onClick={() => toggleSelect(paper)}
                    style={{ padding: "6px 12px", border: "1px solid #2563eb", borderRadius: 6, cursor: "pointer", fontSize: 13,
                      background: isSelected(paper.paper_id) ? "#2563eb" : "#fff",
                      color: isSelected(paper.paper_id) ? "#fff" : "#2563eb" }}>
                    {isSelected(paper.paper_id) ? "Selected" : "Select"}
                  </button>
                  <a href={paper.pdf_url} target="_blank" rel="noreferrer"
                    style={{ padding: "6px 12px", border: "1px solid #ddd", borderRadius: 6, background: "#fff",
                      color: "#444", fontSize: 13, textAlign: "center", textDecoration: "none" }}>
                    PDF
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "synthesis" && (
        <div>
          {synthesizing && (
            <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
              <p style={{ fontSize: 16, marginBottom: 8 }}>Downloading and processing selected papers...</p>
              <p style={{ fontSize: 13, color: "#999" }}>This takes 30-60 seconds. Reading full PDFs and extracting relevant sections.</p>
            </div>
          )}
          {!synthesizing && !summary && (
            <p style={{ color: "#999", textAlign: "center", marginTop: "3rem" }}>
              Select papers from search results and click Synthesize
            </p>
          )}
          {summary && (
            <div style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: "1.5rem" }}>
              <h3 style={{ margin: "0 0 12px", fontSize: 16 }}>Literature Review</h3>
              <p style={{ fontSize: 15, color: "#333", lineHeight: 1.9, whiteSpace: "pre-wrap", margin: "0 0 16px" }}>{summary}</p>
              <div style={{ paddingTop: 12, borderTop: "1px solid #eee" }}>
                <p style={{ fontSize: 12, color: "#999", margin: "0 0 8px" }}>Based on {selected.length} paper(s) · Query: {query}</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {selected.map(p => (
                    <span key={p.paper_id} style={{ fontSize: 11, background: "#eff6ff", color: "#1d4ed8", padding: "2px 8px", borderRadius: 4 }}>
                      {p.title.slice(0, 50)}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}"""

with open('/workspaces/openscholar/frontend/src/App.jsx', 'w') as f:
    f.write(jsx)
print("Written successfully")
