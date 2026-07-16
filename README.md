# ClauseWise — AI-Powered Contract Risk Analysis Platform

**Demystify legal agreements with AI — detect risky clauses, get plain-English explanations, and ask an AI lawyer.**

ClauseWise is an AI-powered legal contract analysis platform designed to simplify complex agreements into easy-to-understand language. The platform helps users identify risky clauses, understand legal jargon, and make informed decisions before signing contracts.

Using a combination of Natural Language Processing (NLP), BERT-based Machine Learning, and a Self-Healing RAG-powered AI chatbot, ClauseWise provides intelligent contract analysis with clause-wise explanations, risk scoring, and plain-English translations.

---

## 🚀 Features

- 📄 PDF Contract Analysis (upload PDF, DOCX, or paste text)
- ⚠️ Risk Detection with Safe / Caution / Unsafe classification
- 📊 Overall Safety Score (0–100)
- 🔍 Clause-wise Analysis with detailed explanations
- 🌐 Plain English Translator (legal jargon → simple language)
- 🤖 **Ask AI Lawyer** — RAG-based Q&A about your contract
- 💬 **Live Chat** — Platform support bot for help & troubleshooting
- 📑 Downloadable PDF Reports
- 🔄 Side-by-Side view (original clause ⇄ plain English)
- 🔐 No login/signup required, privacy-focused

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, React Router 6, recharts, framer-motion, lucide-react, react-dropzone, jsPDF |
| **Backend** | Python, Flask, PyTorch, Transformers (DistilBERT), Sentence-Transformers, ChromaDB, Groq SDK, PyMuPDF |
| **ML Model 1** | DistilBERT fine-tuned on 1400+ clause examples (10 types) — [Hugging Face Hub](https://huggingface.co/harsh-101/clause-bert-classifier) |
| **ML Model 2** | Llama 3.1 via Groq API for translation & Q&A |
| **Vector Store** | ChromaDB with all-MiniLM-L6-v2 embeddings |

---

## 🗺 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | API overview |
| GET | `/health` | Health check |
| POST | `/extract` | Extract clauses from raw text |
| POST | `/analyze` | Extract + classify clauses |
| POST | `/full-analyze` | Extract + classify + translate to plain English |
| POST | `/report` | Full pipeline via text |
| POST | `/analyze-pdf` | Full pipeline via PDF upload |
| POST | `/chat` | Ask AI Lawyer about analyzed clauses |
| POST | `/support-chat` | Platform support / FAQ bot |
| GET | `/rag-stats` | ChromaDB collection statistics |

---

## ⚙️ Quick Start

### Backend (Flask API)

```bash
cd Extraction
pip install -r requirements.txt
python app.py
```

API available at `http://localhost:5000`.

### Frontend (React Dashboard)

```bash
cd ClauseWise-frontend
npm install
npm start
```

Opens at `http://localhost:3000`.

### Environment Variables

Create `Extraction/.env`:

```
GROQ_API_KEY=gsk_...
HF_TOKEN=hf_...           # only needed for gated models
```

---

## 🧠 ML Pipeline

1. User uploads a contract PDF (or pastes text).
2. PyMuPDF extracts text from the document.
3. Regex-based clause boundary detection splits text into clauses.
4. DistilBERT classifier categorizes each clause into 10 types.
5. Self-healing pipeline: if confidence < 70%, falls back to ChromaDB similarity search + LLM re-classification.
6. Groq-powered Llama 3.1 translates legal jargon into plain English.
7. ChromaDB stores clause embeddings for RAG-based Q&A.
8. AI Lawyer answers user questions based on the analyzed contract.

---

## 👨‍💻 Developed By

Harsh Gahankar
