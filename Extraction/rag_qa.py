import os
import numpy as np
from groq import Groq
from rag_store import retrieve_similar
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

def answer_question(question, contract_clauses):
    if not contract_clauses:
        return "Please upload and analyze a contract first before asking questions."

    # Use the lightweight TF-IDF retriever from rag_store
    # We take a larger set of results (top 15) to provide rich context to the LLM
    top_clauses = retrieve_similar(question, top_k=15)
    
    # Fallback if TF-IDF fails or clauses aren't stored
    if not top_clauses:
        top_clauses = contract_clauses[:10]

    context = "\n\n".join([
        f"Clause ID: {c.get('id', '')} | Title: {c.get('title', '')} | Risk: {c.get('risk_level', '')}\n"
        f"Full Text: {c.get('full_text', '')[:1500]}\n"
        f"Pre-Analysis: {c.get('ai_explanation') or c.get('plain_english', '')}"
        for c in top_clauses
    ])

    prompt = f"""You are a friendly Legal Assistant. Your goal is to explain contract clauses so clearly that even a child could understand.
    
    Available Context:
    {context}
    
    User Question: {question}
    
    Instructions:
    - Provide a simple, clear, and very easy-to-understand answer.
    - **Highlight important terms, key sentences, or risky parts by wrapping them in bold (e.g., **this is risky**).**
    - Use emojis to make the response friendly and engaging (e.g., ✅, ⚠️, 🚩).
    - Use clear bullet points on NEW LINES for lists (e.g., - Item 1).
    - Use double new lines between paragraphs for clear spacing.
    - Be decisive. If a clause is safe, say so. If it has a risk, explain it simply.
    - Avoid all legal jargon and complex words.
    - Keep the response under 100 words.
    - Use "explain like I'm five" (ELI5) logic.
    - Ensure the layout is clean and easy to read at a glance. """

    if not client or not os.getenv("GROQ_API_KEY"):
        return "⚠️ Groq API Key is missing or invalid. Please check your .env file."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=300,
            messages=[
                {"role": "system", "content": "You are a friendly legal expert who simplifies complex contracts with total clarity and uses helpful emojis."},
                {"role": "user",   "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        if "401" in str(e) or "invalid_api_key" in str(e).lower():
            return "🔐 Your Groq API Key is invalid. Please generate a new one from the Groq console and update your .env file."
        return f"❌ Sorry, I encountered an error while thinking: {str(e)}"