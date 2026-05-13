import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key - using environment variable for security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client in translator: {e}")
    client = None

def translate_all(clauses):
    """Explains a list of clauses in batches using Groq to avoid rate limits."""
    if not clauses or not client:
        return clauses

    BATCH_SIZE = 3  # Smaller batch for detailed explanations
    results = []
    
    for i in range(0, len(clauses), BATCH_SIZE):
        batch = clauses[i:i + BATCH_SIZE]
        
        batch_input = "\n---\n".join([
            f"Clause {j}:\nText: {c.get('full_text', '')[:1000]}\nType: {c.get('type', '')}" 
            for j, c in enumerate(batch)
        ])
        
        prompt = f"""You are a friendly legal assistant. Explain these {len(batch)} contract clauses in super simple "plain English".
        
        Instructions for EACH clause:
        1. Explain what it means in simple words (ELI5).
        2. **Highlight risky parts using bold text.**
        3. Use 1-2 emojis.
        4. State clearly what the user might lose or agree to.
        
        Return a JSON object with a 'results' array: [{{"id": index, "explanation": "your explanation"}}]
        
        Clauses to explain:
        {batch_input}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=1000,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a helpful legal expert who simplifies contracts into JSON format."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            data = json.loads(response.choices[0].message.content)
            batch_explanations = data.get('results', [])
            
            for j, clause in enumerate(batch):
                explanation = "No explanation generated."
                try:
                    res = next((r for r in batch_explanations if r.get('id') == j), {})
                    explanation = res.get('explanation', "No explanation generated.")
                except:
                    pass
                
                results.append({**clause, 'ai_explanation': explanation})
                
        except Exception as e:
            print(f"Translation Batch Error: {e}")
            # Fallback
            for clause in batch:
                results.append({**clause, 'ai_explanation': 'Could not generate AI explanation due to rate limits. Please try again.'})
                
    return results

def translate_clause(clause_text, clause_type, risk_level):
    """Fallback for single clause explanation."""
    # (Kept for compatibility if needed elsewhere)
    if not client: return "⚠️ Groq client not initialized."
    try:
        prompt = f"Explain this {clause_type} clause ({risk_level} risk) simply: {clause_text[:500]}"
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"