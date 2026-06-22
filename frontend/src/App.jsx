import { useState } from "react";
import axios from "axios";
import { 
  Search, BookOpen, FileText, CheckCircle2, ExternalLink, 
  Loader2, Network, Sparkles, SlidersHorizontal, Layers, 
  ArrowRight, Bookmark, Clock, User, ArrowUpRight
} from "lucide-react";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  const [query, setQuery] = useState("");
  const [papers, setPapers] = useState([]);
  const [selected, setSelected] = useState([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [synthesizing, setSynthesizing] = useState(false);
  const [synthSource, setSynthSource] = useState("");

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setPapers([]);
    setSelected([]);
    setSummary("");
    try {
      const r = await axios.post(`${API}/search`, { query, max_results: 15 });
      setPapers(r.data.papers);
    } catch (e) {
      alert("Search failed: " + e.message);
    }
    setLoading(false);
  };

  const toggleSelect = (paper) => {
    setSelected((prev) =>
      prev.find((p) => p.paper_id === paper.paper_id)
        ? prev.filter((p) => p.paper_id !== paper.paper_id)
        : [...prev, paper]
    );
  };

  const isSelected = (paper_id) => selected.some((p) => p.paper_id === paper_id);

  const synthesize = async () => {
    if (selected.length === 0) return alert("Select at least one paper first");
    setSynthesizing(true);
    setSummary("");
    try {
      const r = await axios.post(`${API}/synthesize`, {
        query,
        paper_ids: selected.map((p) => p.paper_id),
        papers_meta: selected,
      });
      setSummary(r.data.summary);
      setSynthSource(r.data.source);
    } catch (e) {
      alert("Synthesis failed: " + e.message);
    }
    setSynthesizing(false);
  };

  return (
    <div className="min-h-screen bg-[#fafafa] text-slate-900 font-sans antialiased selection:bg-slate-900 selection:text-white">
      
      {/* Dynamic Top Navigation Bar */}
      <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="bg-slate-950 text-white p-1.5 rounded-md shadow-sm flex items-center justify-center">
            <Network size={16} strokeWidth={2.5} />
          </div>
          <span className="font-semibold tracking-tight text-sm text-slate-900">OpenScholar</span>
          <span className="text-[10px] bg-slate-100 font-mono text-slate-600 px-1.5 py-0.5 rounded border border-slate-200/50">PRO ENGINE</span>
        </div>
        
        <div className="flex items-center gap-4 text-xs font-medium text-slate-500">
          <span className="flex items-center gap-1.5"><Clock size={12} /> Live arXiv Streaming</span>
          <div className="h-3 w-px bg-slate-200" />
          <span className="text-slate-900 font-semibold">Workspace v2.4</span>
        </div>
      </nav>

      {/* Main Multi-Pane Application Layout */}
      <div className="max-w-[1600px] mx-auto min-h-[calc(100vh-3.5rem)] flex flex-col lg:flex-row">
        
        {/* LEFT WORKSPACE: Search Control & Discovery Feed */}
        <div className="flex-1 p-6 lg:p-8 lg:border-r border-slate-200/60 max-w-4xl w-full mx-auto">
          
          {/* Header & Command Center */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 mb-2">Literature Discovery</h1>
            <p className="text-xs text-slate-500 max-w-xl">
              Query global repositories, ingest contextual vector embeddings, and construct verifiable literature synthesis models.
            </p>
          </div>

          {/* Premium Command Input Group */}
          <div className="bg-white border border-slate-200 shadow-[0_2px_8px_rgba(0,0,0,0.04)] rounded-xl p-2 flex items-center gap-2 focus-within:border-slate-400 focus-within:shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-all mb-8">
            <div className="pl-3 text-slate-400">
              <Search size={18} />
            </div>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="Enter research topic, keywords, or vector objectives..."
              className="w-full bg-transparent py-2.5 text-sm text-slate-900 outline-none placeholder:text-slate-400 font-medium"
            />
            <button
              onClick={search}
              disabled={loading}
              className="bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-sm"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              {loading ? "Streaming" : "Analyze"}
            </button>
          </div>

          {/* Suggestions Layer when empty */}
          {papers.length === 0 && !loading && (
            <div className="border border-slate-200/60 bg-white/60 rounded-xl p-6 text-center max-w-xl mx-auto mt-12">
              <Layers className="mx-auto text-slate-300 mb-3" size={24} />
              <h3 className="text-sm font-semibold text-slate-800 mb-1">Initialize Research Directive</h3>
              <p className="text-xs text-slate-500 mb-4">Input a topic above to query full-text preprints and live academic data.</p>
              <div className="flex flex-wrap justify-center gap-2">
                {["Retrieval Augmented Generation", "Vision Transformers", "Sparse MoE Scaling Laws"].map((tag) => (
                  <button 
                    key={tag} 
                    onClick={() => { setQuery(tag); setTimeout(search, 50); }}
                    className="text-[11px] font-medium bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 px-2.5 py-1 rounded-md transition-colors cursor-pointer"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* High-Fidelity Paper Stream */}
          <div className="space-y-4">
            {papers.map((paper) => {
              const active = isSelected(paper.paper_id);
              return (
                <div
                  key={paper.paper_id}
                  onClick={() => toggleSelect(paper)}
                  className={`bg-white border rounded-xl p-5 transition-all duration-200 group cursor-pointer relative select-none ${
                    active
                      ? "border-slate-900 shadow-[0_4px_20px_rgba(0,0,0,0.04)] ring-1 ring-slate-900"
                      : "border-slate-200/70 hover:border-slate-300 hover:shadow-[0_2px_12px_rgba(0,0,0,0.02)]"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    {/* Minimalist Selection Radio Checkbox */}
                    <div className="mt-1">
                      <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${
                        active 
                          ? "bg-slate-900 border-slate-900 text-white animate-in zoom-in-50 duration-150" 
                          : "border-slate-300 group-hover:border-slate-400 bg-white"
                      }`}>
                        {active && <CheckCircle2 size={10} strokeWidth={3} />}
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Meta Information Metadata Tagline */}
                      <div className="flex flex-wrap items-center gap-2 mb-2 text-[11px] font-medium text-slate-400">
                        <span className="bg-slate-50 border border-slate-200/60 px-1.5 py-0.5 rounded text-slate-600 font-mono text-[10px]">
                          {paper.published ? paper.published.slice(0, 10) : "Preprint"}
                        </span>
                        <span>•</span>
                        <span className="truncate flex items-center gap-1 max-w-[240px]">
                          <User size={10} /> {paper.authors.slice(0, 2).join(", ")}{paper.authors.length > 2 && " et al."}
                        </span>
                        <span>•</span>
                        <span className="font-mono tracking-tight text-slate-400/90">{paper.paper_id}</span>
                      </div>

                      {/* Title */}
                      <h3 className="text-sm font-bold text-slate-900 leading-snug tracking-tight mb-2 group-hover:text-slate-800 transition-colors">
                        {paper.title}
                      </h3>

                      {/* Abstract Snippet */}
                      <p className="text-xs text-slate-500 leading-relaxed line-clamp-2 pr-4">
                        {paper.abstract}
                      </p>
                    </div>

                    {/* Quick Link Out To Raw PDF */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-4 right-4">
                      <a
                        href={paper.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-900 block transition-colors"
                        title="Open PDF Document"
                      >
                        <ArrowUpRight size={14} />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* RIGHT WORKSPACE: Real-time Deck Control Station & Editorial Reader View */}
        <div className="w-full lg:w-[480px] xl:w-[580px] bg-white lg:border-l border-slate-200/60 p-6 lg:p-8 flex flex-col lg:h-[calc(100vh-3.5rem)] lg:sticky lg:top-14 overflow-y-auto">
          
          {/* CONTROL STATION MODE: Gathering Phase */}
          {!summary && !synthesizing && (
            <div className="flex-1 flex flex-col justify-between h-full min-h-[300px]">
              <div>
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 mb-6">
                  <SlidersHorizontal size={12} />
                  Synthesis Pipeline Deck
                </div>
                
                <h2 className="text-lg font-bold tracking-tight text-slate-900 mb-2">Build Your Review Context</h2>
                <p className="text-xs text-slate-500 leading-relaxed mb-6">
                  Select papers from the streaming feed on the left. OpenScholar will automatically extract full texts, structure cross-references, and synthesize deep-dive insights.
                </p>

                {selected.length > 0 ? (
                  <div className="space-y-2 max-h-[360px] overflow-y-auto border border-slate-100 rounded-xl p-3 bg-slate-50/50">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide block mb-1 px-1">Selected Payload Queue ({selected.length})</span>
                    {selected.map((p) => (
                      <div key={p.paper_id} className="flex items-center justify-between gap-3 bg-white border border-slate-200/60 p-2.5 rounded-lg text-xs shadow-[0_1px_2px_rgba(0,0,0,0.01)]">
                        <span className="font-semibold text-slate-800 truncate flex-1">{p.title}</span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); toggleSelect(p); }}
                          className="text-[10px] font-medium text-slate-400 hover:text-red-600 transition-colors cursor-pointer"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="border border-dashed border-slate-200 rounded-xl p-8 text-center bg-slate-50/30">
                    <Bookmark size={18} className="mx-auto text-slate-300 mb-2" />
                    <span className="text-xs text-slate-400 font-medium">No documents staged in current payload.</span>
                  </div>
                )}
              </div>

              {/* Execution Drawer */}
              <div className="pt-6 border-t border-slate-100 mt-8">
                <button
                  onClick={synthesize}
                  disabled={selected.length === 0}
                  className="w-full bg-slate-950 hover:bg-slate-900 disabled:bg-slate-100 disabled:text-slate-400 text-white py-3 px-4 rounded-xl text-xs font-semibold tracking-wide transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
                >
                  <BookOpen size={14} />
                  Synthesize Synthesis Document ({selected.length} Sources)
                  <ArrowRight size={12} className="ml-1" />
                </button>
              </div>
            </div>
          )}

          {/* LOADING STATE: Full RAG Processing Pipeline */}
          {synthesizing && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 h-full my-auto">
              <div className="relative mb-6">
                <div className="absolute inset-0 bg-slate-100 rounded-full animate-ping opacity-40 scale-150" />
                <div className="bg-slate-950 text-white p-4 rounded-full relative shadow-md">
                  <Loader2 size={24} className="animate-spin" />
                </div>
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-2">Executing Intelligence Graph Pipeline</h3>
              <div className="space-y-1.5 max-w-sm">
                <p className="text-xs text-slate-500 leading-relaxed">Downloading multi-page PDF records from mirrors...</p>
                <p className="text-[10px] font-mono text-slate-400">Chunking texts • MapReduce Abstract Engine • Context Synthesis</p>
              </div>
            </div>
          )}

          {/* EDITORIAL STATE: High-End Generated Document Viewer */}
          {summary && !synthesizing && (
            <div className="flex-1 flex flex-col h-full animate-in fade-in duration-300">
              {/* Back out button to view configurations */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
                <button 
                  onClick={() => setSummary("")}
                  className="text-xs font-semibold text-slate-500 hover:text-slate-900 flex items-center gap-1 transition-colors cursor-pointer"
                >
                  ← Return to Control Deck
                </button>
                <div className="flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200/50 text-[10px] font-bold px-2 py-0.5 rounded-full">
                  <CheckCircle2 size={10} /> Verified Engine Response
                </div>
              </div>

              {/* Document Metadata Header */}
              <div className="mb-6">
                <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest block mb-1">COMPREHENSIVE LITERATURE REVIEW</span>
                <h2 className="text-xl font-bold tracking-tight text-slate-900 leading-tight">
                  Synthesis: "{query}"
                </h2>
                <div className="mt-2 text-[11px] font-medium text-slate-400 flex items-center gap-2">
                  <span>Engine: {synthSource}</span>
                  <span>•</span>
                  <span>Ingested: {selected.length} Papers</span>
                </div>
              </div>

              {/* Premium Editorial Document Output Area */}
              <div className="flex-1 text-slate-800 text-sm leading-relaxed tracking-normal font-serif space-y-5 overflow-y-auto pr-2 border-b border-slate-100 pb-6">
                {summary.split('\n').filter(p => p.trim()).map((paragraph, idx) => (
                  <p key={idx} className="indent-0 text-justify font-serif text-[14px] leading-7 text-slate-800">
                    {paragraph}
                  </p>
                ))}
              </div>

              {/* Strict Source Matrix and Citations Ledger */}
              <div className="pt-5">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Ingested Document References</h4>
                <div className="space-y-2">
                  {selected.map((p) => (
                    <a
                      key={p.paper_id}
                      href={p.arxiv_url || p.pdf_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center justify-between gap-4 p-2.5 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200/60 group transition-all text-left"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText size={13} className="text-slate-400 shrink-0" />
                        <span className="text-xs font-semibold text-slate-700 truncate group-hover:text-slate-900">
                          {p.title}
                        </span>
                      </div>
                      <ExternalLink size={12} className="text-slate-400 group-hover:text-slate-900 shrink-0" />
                    </a>
                  ))}
                </div>
              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  );
}
