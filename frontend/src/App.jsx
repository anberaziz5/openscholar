import { useState, useEffect } from "react"
import axios from "axios"

const API = import.meta.env.VITE_API_URL

export default function App() {
  const [query, setQuery] = useState("")
  const [papers, setPapers] = useState([])
  const [chunks, setChunks] = useState([])
  const [selected, setSelected] = useState([])
  const [summary, setSummary] = useState("")
  const [loading, setLoading] = useState(false)
  const [synthesizing, setSynthesizing] = useState(false)
  const [allPapers, setAllPapers] = useState([])
  const [tab, setTab] = useState("search")

  useEffect(() => {
    axios.get(`${API}/papers`).then(r => setAllPapers(r.data.papers))
  }, [])

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setPapers([])
    setChunks([])
    setSummary("")
    try {
      const r = await axios.post(`${API}/search`, { query, limit: 10 })
      setPapers(r.data.papers)
      setChunks(r.data.chunks)
    } catch (e) {
      alert("Search failed: " + e.message)
    }
    setLoading(false)
  }

  const toggleSelect = (paper_id) => {
    setSelected(prev =>
      prev.includes(paper_id)
        ? prev.filter(id => id !== paper_id)
        : [...prev, paper_id]
    )
  }

  const synthesize = async () => {
    if (selected.length === 0) return alert("Select at least one paper first")
    setSynthesizing(true)
    setSummary("")
    try {
      const r = await axios.post(`${API}/synthesize`, {
        query,
        paper_ids: selected
      })
      setSummary(r.data.summary)
      setTab("synthesis")
    } catch (e) {
      alert("Synthesis failed: " + e.message)
    }
    setSynthesizing(false)
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, margin: "0 0 4px" }}>OpenScholar</h1>
        <p style={{ color: "#666", margin: 0 }}>AI-powered academic research discovery and synthesis</p>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: "2rem" }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Search papers..."
          style={{ flex: 1, padding: "10px 14px", fontSize: 15, border: "1px solid #ddd", borderRadius: 8 }}
        />
        <button onClick={search} disabled={loading}
          style={{ padding: "10px 20px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer" }}>
          {loading ? "Searching..." : "Search"}
        </button>
        {selected.length > 0 && (
          <button onClick={synthesize} disabled={synthesizing}
            style={{ padding: "10px 20px", background: "#16a34a", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer" }}>
            {synthesizing ? "Synthesizing..." : "Synthesize (" + selected.length + ")"}
          </button>
        )}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem", borderBottom: "1px solid #eee", paddingBottom: 8 }}>
        {["search", "synthesis", "library"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "6px 16px", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 14,
              background: tab === t ? "#2563eb" : "#f3f4f6", color: tab === t ? "#fff" : "#444" }}>
            {t === "search" ? "Results" : t === "synthesis" ? "Synthesis" : "Library (" + allPapers.length + ")"}
          </button>
        ))}
      </div>

      {tab === "search" && (
        <div>
          {papers.length === 0 && !loading && (
            <p style={{ color: "#999", textAlign: "center", marginTop: "3rem" }}>Search for a topic to find relevant papers</p>
          )}
          {papers.map(paper => (
            <div key={paper.paper_id} style={{
              border: selected.includes(paper.paper_id) ? "2px solid #2563eb" : "1px solid #e5e7eb",
              borderRadius: 10, padding: "1rem 1.25rem", marginBottom: 12,
              background: selected.includes(paper.paper_id) ? "#eff6ff" : "#fff"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: "0 0 4px", fontSize: 16, fontWeight: 600 }}>{paper.title}</h3>
                  <p style={{ margin: "0 0 6px", fontSize: 13, color: "#666" }}>
                    {paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 ? " et al." : ""} · {paper.published ? paper.published.slice(0, 10) : ""}
                  </p>
                  <p style={{ margin: "0 0 8px", fontSize: 14, color: "#444", lineHeight: 1.5 }}>
                    {paper.abstract ? paper.abstract.slice(0, 200) + "..." : ""}
                  </p>
                  <span style={{ fontSize: 12, background: "#f3f4f6", padding: "2px 8px", borderRadius: 4, color: "#555" }}>
                    Score: {paper.score}
                  </span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <button onClick={() => toggleSelect(paper.paper_id)}
                    style={{ padding: "6px 12px", border: "1px solid #2563eb", borderRadius: 6, cursor: "pointer", fontSize: 13,
                      background: selected.includes(paper.paper_id) ? "#2563eb" : "#fff",
                      color: selected.includes(paper.paper_id) ? "#fff" : "#2563eb" }}>
                    {selected.includes(paper.paper_id) ? "Selected" : "Select"}
                  </button>
                  <a href={paper.pdf_url} target="_blank" rel="noreferrer"
                    style={{ padding: "6px 12px", border: "1px solid #ddd", borderRadius: 6, background: "#fff", color: "#444", fontSize: 13, textAlign: "center", textDecoration: "none" }}>
                    PDF
                  </a>
                </div>
              </div>
              {chunks.filter(c => c.paper_id === paper.paper_id).slice(0, 2).map(chunk => (
                <div key={chunk.chunk_id} style={{ marginTop: 10, padding: "8px 12px", background: "#f9fafb", borderRadius: 6, borderLeft: "3px solid #93c5fd" }}>
                  <span style={{ fontSize: 11, color: "#2563eb", fontWeight: 600, textTransform: "uppercase" }}>{chunk.section}</span>
                  <p style={{ margin: "4px 0 0", fontSize: 13, color: "#555", lineHeight: 1.6 }}>
                    {chunk.text.slice(0, 300)}...
                  </p>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {tab === "synthesis" && (
        <div>
          {!summary ? (
            <p style={{ color: "#999", textAlign: "center", marginTop: "3rem" }}>Select papers and click Synthesize to generate a literature review</p>
          ) : (
            <div style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: "1.5rem" }}>
              <h3 style={{ margin: "0 0 12px", fontSize: 16 }}>Literature Review</h3>
              <p style={{ fontSize: 14, color: "#333", lineHeight: 1.8, whiteSpace: "pre-wrap" }}>{summary}</p>
              <div style={{ marginTop: 16, paddingTop: 12, borderTop: "1px solid #eee" }}>
                <p style={{ fontSize: 12, color: "#999", margin: 0 }}>Based on {selected.length} paper(s) · Query: {query}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "library" && (
        <div>
          {allPapers.map(paper => (
            <div key={paper.paper_id} style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: "1rem 1.25rem", marginBottom: 10 }}>
              <h3 style={{ margin: "0 0 4px", fontSize: 15, fontWeight: 600 }}>{paper.title}</h3>
              <p style={{ margin: 0, fontSize: 13, color: "#666" }}>
                {paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 ? " et al." : ""} · {paper.published ? paper.published.slice(0, 10) : ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}