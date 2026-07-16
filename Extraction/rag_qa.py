import os

_client = None

def _get_client():
    global _client
    if _client is None:
        from groq import Groq
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def _embed(text):
    from rag_store import embed
    return embed(text)

def answer_question(question, contract_clauses):
    if not contract_clauses:
        return "Please upload and analyze a contract first before asking questions."

    import re
    import numpy as np

    mentioned_numbers = re.findall(r'(?:\bclause\b|\bsection\b|§)?\s*(\d+)(?:\.|\b)', question.lower())

    q_vec   = np.array(_embed(question))
    scored  = []
    for clause in contract_clauses:
        boost = 0.0
        clause_id = str(clause.get('id', ''))
        if clause_id in mentioned_numbers:
            boost = 1.0

        text_to_embed = clause.get('full_text') or clause.get('originalText', '')
        c_vec      = np.array(_embed(text_to_embed))
        similarity = float(np.dot(q_vec, c_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(c_vec) + 1e-9))
        scored.append((similarity + boost, clause))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_clauses = [c for _, c in scored[:20]]

    context = "\n\n".join([
        f"Clause ID: {c.get('id', '')} | Title: {c.get('title', '')} | Risk: {c.get('risk_level') or c.get('risk', '')}\n"
        f"Full Text: {(c.get('full_text') or c.get('originalText', ''))[:1500]}\n"
        f"Pre-Analysis: {c.get('ai_explanation') or c.get('plain_english') or c.get('plainEnglish', '')}"
        for c in top_clauses
    ])

    prompt = f"""You are a professional corporate lawyer assisting a client with a contract analysis. 

Available Context from the Contract:
{context}

User Question: {question}

Instructions:
- Answer the user's question directly and professionally based on the provided context.
- If the user asks a general question (e.g., "is this document risky?"), synthesize the overall risk from the context provided and highlight the main concerns.
- If the user's input is strictly a greeting (e.g., "hello", "hi", "hlo"), greet them professionally and ask how you may assist them with the contract. Do not analyze clauses unless asked.
- Provide a concise, clear, and authoritative legal analysis.
- Use clear bullet points on NEW LINES for lists.
- Be decisive. Identify risks clearly but maintain a professional tone.
- Do not use emojis.
- Avoid unnecessarily dense legal jargon, but use standard professional terminology.
- Keep the response under 500 words.
- Ensure the layout is clean and easy to read. """

    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=700,
        messages=[
            {"role": "system", "content": "You are a highly experienced and professional corporate lawyer providing clear, authoritative, and concise legal advice regarding contracts."},
            {"role": "user",   "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def support_answer(question):
    prompt = f"""You are a helpful customer support assistant for ClauseWise, an AI-powered contract analysis platform.

User Question: {question}

Instructions:
- Answer the user's question helpfully and professionally about the ClauseWise platform, its features, or general troubleshooting.
- If they ask about legal advice, clarify that ClauseWise is an AI assistant and not a substitute for a licensed attorney.
- If you don't know the answer, suggest they email support@clausewise.com for further assistance.
- Keep responses concise and friendly.
- Do not use emojis.
- Keep the response under 200 words."""

    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=300,
        messages=[
            {"role": "system", "content": "You are a helpful customer support assistant for the ClauseWise platform."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
