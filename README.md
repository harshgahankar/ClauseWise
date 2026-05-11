# ClauseWise – AI-Powered Contract Risk Analysis Platform

## 📌 Overview
ClauseWise is an AI-powered legal contract analysis platform designed to simplify complex agreements into easy-to-understand language. The platform helps users identify risky clauses, understand legal jargon, and make informed decisions before signing contracts.

Using a combination of Natural Language Processing (NLP), BERT-based Machine Learning, and a Self-Healing RAG-powered AI chatbot, ClauseWise provides intelligent contract analysis with clause-wise explanations, risk scoring, and plain-English translations.

---

## 🚀 Features

- 📄 PDF Contract Analysis
  - Upload contracts in PDF format for instant processing and analysis.

- ⚠️ Risk Detection System
  - Detects and classifies clauses into:
    - ✅ Safe
    - ⚠️ Caution
    - ❌ Unsafe

- 📊 Overall Risk Score
  - Generates a contract risk score for quick understanding.

- 🔍 Clause-wise Analysis
  - Detailed explanation of every important clause.

- 🌐 Plain English Translator
  - Converts complex legal language into simple, user-friendly English.

- 🤖 AI Chatbot with Self-Healing RAG
  - Context-aware chatbot for legal assistance and contract-related queries.
  - Uses Retrieval-Augmented Generation (RAG) with self-healing mechanisms for improved response reliability.

- 📑 Downloadable Reports
  - Export analyzed contract reports for future reference.

- 🔄 Side-by-Side Comparison
  - View original legal clauses alongside simplified explanations.

- 🇮🇳 India-Specific Legal Focus
  - Optimized for common Indian legal agreements and terminology.

- 🔐 Privacy-Focused
  - No login/signup required.
  - Lightweight and user-friendly experience.

---

# 🛠️ Tech Stack

## Frontend
- React.js
- Tailwind CSS

## Backend
- Flask (Python)

## AI / Machine Learning
- BERT-based NLP Pipeline
- Self-Healing RAG Architecture
- GROQ API Integration

## Dataset
- Kaggle-based pretrained legal datasets

## Python Libraries
- Flask
- flask-cors
- groq
- transformers
- torch
- scikit-learn
- pandas
- numpy
- PyMuPDF

---

# 🧠 AI Pipeline

1. User uploads a contract PDF.
2. PyMuPDF extracts text from the document.
3. NLP preprocessing is performed.
4. BERT-based ML pipeline analyzes clauses.
5. Clauses are classified into risk categories.
6. GROQ-powered AI generates simplified explanations.
7. Self-Healing RAG chatbot handles user queries contextually.
8. Final report and risk score are generated.


---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ClauseWise.git
cd ClauseWise
```

---

## 2️⃣ Setup Backend

```bash
cd backend

python -m venv venv

# Activate venv

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 3️⃣ Setup Frontend

```bash
cd frontend

npm install
npm start
```

---

## 4️⃣ Run Flask Backend

```bash
python app.py
```

---

# 📌 Future Improvements

- OCR support for scanned PDFs
- Multi-language contract analysis
- Advanced legal recommendation engine
- Cloud deployment & scalability
- Real-time collaboration features

---

# 🏆 Vision

ClauseWise aims to make legal agreements transparent and understandable for everyone, reducing the gap between complex legal language and everyday users through AI-driven insights.

---

# 👨‍💻 Developed By

Harsh Gahankar  
Computer Engineering Student | AI & Full Stack Developer | NLP Enthusiast
