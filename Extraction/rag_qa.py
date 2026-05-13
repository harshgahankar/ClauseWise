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

    # 1. Strategic Context Selection
    # For specific questions, use TF-IDF. For general questions, include a summary of ALL clauses.
    specific_context = retrieve_similar(question, top_k=10)
    
    # Create a quick summary of all available clauses so the AI knows the "big picture"
    overall_summary = "\n".join([f"- {c.get('type', 'Clause')}: {c.get('full_text', '')[:100]}" for c in contract_clauses])
    
    context_list = []
    seen_ids = set()
    
    for c in specific_context:
        cid = c.get('id', 'unknown')
        if cid not in seen_ids:
            context_list.append(c)
            seen_ids.add(cid)
            
    # If the user is asking about the "whole" or "all" or "rundown", add more clauses
    if any(word in question.lower() for word in ['all', 'whole', 'complete', 'summary', 'rundown', 'everything']):
        for c in contract_clauses[:20]: # Add up to 20 clauses for broad questions
            if c.get('id', 'unknown') not in seen_ids:
                context_list.append(c)
                seen_ids.add(c.get('id', 'unknown'))

    formatted_context = "\n\n".join([
        f"Clause: {c.get('type', 'General')}\nText: {c.get('full_text', '')[:800]}"
        for c in context_list
    ])

    # 2. Professional but Accessible Prompt
    prompt = f"""You are a Professional Legal Analyst. Your goal is to provide clear, accurate, and professional insights into the provided contract.
    
    Contract Overview (Summary of all detected clauses):
    {overall_summary[:2000]}
    
    Detailed Context for Question:
    {formatted_context[:5000]}
    
    User Question: {question}
    
    Instructions:
    - Maintain a **professional, expert tone**. Avoid "child-like" language, but stay clear and accessible.
    - If the user asks about the "rundown" or "whole contract", use the Overview provided above to give a complete picture.
    - **Bold key terms and critical risks (e.g., **Indemnification**).**
    - Use professional bullet points for clarity.
    - Do NOT say you only have "half" the contract; you have access to the full overview and specific details.
    - If a specific detail is missing from the provided context, state that clearly rather than guessing.
    - Use emojis sparingly and only for status (e.g., ✅ for safe, ⚠️ for caution, 🚩 for high risk).
    - Limit response to 150 words. """

    if not client or not os.getenv("GROQ_API_KEY"):
        return "⚠️ Groq API Key is missing. Please check your configuration."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You are a professional legal expert. You provide clear, concise, and structured legal analysis of contracts."},
                {"role": "user",   "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"❌ Error: {str(e)}"