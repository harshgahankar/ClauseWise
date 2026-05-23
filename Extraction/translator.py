from groq import Groq
import os

# API Key - using environment variable for security
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def translate_clause(clause_text, clause_type, risk_level):
    """Send one clause to Groq (Llama 3), get back a plain English explanation."""

    prompt = f"""You are a friendly legal assistant helping everyday people understand contracts.
    Explain this like I'm 5 years old.

    A user has found this clause:
    ---
    {clause_text}
    ---

    Clause Type: {clause_type} | Risk: {risk_level}

    Your job:
    1. Explain what this clause ACTUALLY means in very simple words. Use 1-2 emojis.
    2. State clearly what the user might LOSE or AGREE TO.
    3. Give one super-simple tip or warning.

    Keep it friendly, short (under 70 words), and use NO legal jargon."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": "You are a friendly legal assistant who explains contracts in super simple English with emojis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def translate_all(clauses):
    results = []
    for clause in clauses:
        try:
            explanation = translate_clause(
                clause.get('full_text', ''),
                clause.get('type', 'general'),
                clause.get('risk_level', 'low')
            )
            # ── Self-healing ──────────────────────────────────────────────────
            try:
                from rag_healer import is_bad_explanation, heal_explanation
                if is_bad_explanation(explanation):
                    explanation = heal_explanation(
                        clause.get('full_text', ''),
                        clause.get('type', 'general'),
                        clause.get('risk_level', 'low'),
                        explanation
                    )
            except Exception:
                pass
        except Exception as e:
            explanation = clause.get('plain_english', 'Could not generate explanation.')

        results.append({**clause, 'ai_explanation': explanation})
    return results
