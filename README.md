<div align="center">

# 🖧 OpenScholar

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-v4.0-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Deployed on Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-Spaces-FFD21E?style=flat)](https://huggingface.co/spaces/SunbalAzizLCWU/openscholar-api)
[![Deployed on Vercel](https://img.shields.io/badge/Vercel-Hosted-000000?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)

_An intelligent, serverless, zero-cost academic research engine designed to bridge the gap between real-time scientific literature discovery and synthesis. OpenScholar dynamically pulls live papers from arXiv, vectors them on-the-fly, and generates deep synthetic literature reviews using high-throughput LLMs._
<br />

## 🚨 The Problem It Solves

Traditional academic research workflows suffer from three major bottlenecks:
1. **Information Lag:** Standard RAG (Retrieval-Augmented Generation) applications rely on static, pre-indexed vector databases that quickly become obsolete in fast-moving fields like Artificial Intelligence.
2. **Analysis Paralysis:** Reviewing literature requires downloading dozens of heavy PDFs, skimming dense academic prose, manually tracking cross-references, and synthesizing common methodologies.
3. **Infrastructure Costs:** High-performance AI tools and vector databases usually demand expensive cloud compute nodes, GPU servers, and subscription-based scaling.

## 💡 The Solution: How OpenScholar Works

OpenScholar eliminates these constraints by creating a **live, dynamic RAG pipeline** operating entirely over a fully serverless, zero-cost production stack:
* **Dynamic Pipeline:** Instead of reading from a stale dataset, the engine queries the live **arXiv API** in real-time based on the user's explicit research intent.
* **On-the-Fly Vectorization:** Downloaded papers are parsed, split, embedded, and immediately indexed into **Qdrant Cloud** with active payload indexing mapped directly to `paper_id` variables to isolate workspaces.
* **Multi-LLM Synthetic Reviews:** The system utilizes **Groq** as its primary high-throughput engine to perform instant parallel analysis, automatically falling back to **Google Gemini** if rate limits or network exceptions occur.
* **Premium Dual-Pane UI:** Built with **React** and styled via **Tailwind CSS v4**, the interface exposes a side-by-side workflow: exploratory search tracking on the left, and deeply synthesized literature layouts on the right.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([🧑‍💻 Researcher / User]) <--> |Interacts with Dual-Pane UI| Frontend[⚛️ React + Vite UI\nHosted on Vercel]
    Frontend <--> |Secure REST API Requests| Backend[⚡ FastAPI Backend\nHosted on Hugging Face Spaces]
    
    subgraph Core Backend Engine
        Backend -->|1. Real-time Query| ArXiv[📥 Live arXiv API]
        ArXiv -->|2. Returns Metadata & PDFs| Backend
        Backend -->|3. Extracts Texts & Embeds| Embedder[🧠 Embedding Engine]
        Embedder -->|4. Upserts Vectors with paper_id Index| Qdrant[(🗄️ Qdrant Cloud\nVector DB)]
    end
    
    subgraph AI Synthesis Layer
        Backend -->|5. Contextual Query Engine| Groq[🚀 Groq API\nPrimary LLM]
        Backend -.->|Fallback Routing| Gemini[♊ Google Gemini API\nSecondary LLM]
        Groq -->|6. Multi-Paper Literature Review| Frontend
        Gemini -->|6. Multi-Paper Literature Review| Frontend
    end

    style Backend fill:#f9f,stroke:#333,stroke-width:2px
    style Qdrant fill:#bbf,stroke:#333,stroke-width:2px
    style Groq fill:#ffb,stroke:#333,stroke-width:2px

```

---

## 🛠️ The Technology Stack

### Backend Infrastructure

* **Framework:** FastAPI (Python 3.11) — Chosen for lightweight asynchronous request execution and automatic OpenAPI generation.
* **Deployment Platform:** Hugging Face Spaces (Docker Sandbox) — Leveraged for strict card-free, containerized deployment scaling on port `7860`.
* **Vector Database:** Qdrant Cloud (Free Tier) — Outfitted with high-speed payload filters for isolating specific document chunks on targeted lookup spaces.

### Frontend Interface

* **Core:** React 18 + Vite — Engineered for microsecond HMR build speeds and lean build artifact generation.
* **Styling Engine:** Tailwind CSS v4.0 — Utilizing its native CSS-variable-based pipeline for highly responsive grid layouts and premium typography.
* **Deployment Platform:** Vercel — Providing seamless global CDN performance and automated production rollouts from GitHub.

---

## 🔧 Installation & Local Setup

### Prerequisites

* Python 3.11+ installed locally.
* Node.js 18+ and npm installed locally.
* Free API keys for: Groq, Google AI Studio (Gemini), and Qdrant Cloud.

### 1. Backend Setup

Navigate into the backend project workspace:

```bash
cd backend

```

Create a virtual environment and install standard requirements:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

Create a `.env` configuration file in the backend root directory:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cloud_cluster_url
QDRANT_API_KEY=your_qdrant_api_key

```

Execute the local development server:

```bash
uvicorn main:app --reload --port 8000

```

### 2. Frontend Setup

Navigate into the frontend project workspace:

```bash
cd ../frontend

```

Install modern dependencies:

```bash
npm install

```

Create a `.env` file in the frontend root directory:

```env
VITE_API_URL=http://localhost:8000

```

Spin up the local Vite pipeline:

```bash
npm run dev

```

---

## 🚀 Cloud Deployment Pipeline

### Backend Deployment (Hugging Face Spaces)

The backend is packaged within a custom `Dockerfile` designed to expose FastAPI configurations through port `7860`.

```dockerfile
FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

```

1. Deploying to Hugging Face is carried out directly from the working workspace using the standard Hugging Face CLI environment:

```bash
   pip install huggingface_hub
   huggingface-cli login
   huggingface-cli upload YOUR_HF_USERNAME/openscholar-api ./backend . --repo-type space

```

2. Navigate to your Space settings and insert your `.env` variables into the **Repository Secrets** configuration window.

### Frontend Deployment (Vercel)

1. Link your GitHub repository directly within the **Vercel Dashboard**.
2. Pass the production environment parameter explicitly:
* **Key:** `VITE_API_URL`
* **Value:** `https://anberaziz5-openscholar-api.hf.space`


3. Execute the standard Vercel build phase.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
