import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load label map for reference
LABEL_MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_map.json")
with open(LABEL_MAP_PATH, 'r') as f:
    label_map = json.load(f)
    label_map = {int(k): v for k, v in label_map.items()}

# Risk levels
RISK_LEVELS = {
    'non_compete':       'high',
    'intellectual_prop': 'high',
    'termination':       'high',
    'arbitration':       'medium',
    'confidentiality':   'medium',
    'indemnification':   'high',
    'governing_law':    'low',
    'compensation':      'low',
    'vacation':          'low',
    'general':           'low',
}

def classify_all(clauses):
    """Classifies a list of clauses in batches using Groq LLM to save RAM and avoid rate limits."""
    if not clauses or not os.getenv("GROQ_API_KEY"):
        return clauses

    # Batching to stay under rate limits (RPM)
    BATCH_SIZE = 5
    results = []
    
    for i in range(0, len(clauses), BATCH_SIZE):
        batch = clauses[i:i + BATCH_SIZE]
        
        # Prepare a single prompt for the batch
        batch_texts = "\n---\n".join([f"ID {j}: {c.get('full_text', '')[:300]}" for j, c in enumerate(batch)])
        
        prompt = f"""Classify these {len(batch)} legal clauses into ONE of these categories:
        {', '.join(label_map.values())}
        
        Return a JSON list of objects: [{{"id": index, "category": "category_name"}}]
        
        Clauses:
        {batch_texts}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=500,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt + "\nRespond with a JSON object containing a 'results' array."}]
            )
            
            data = json.loads(response.choices[0].message.content)
            batch_results = data.get('results', [])
            
            for j, clause in enumerate(batch):
                # Try to find matching result by index or default
                pred = "general"
                try:
                    res = next((r for r in batch_results if r.get('id') == j), {})
                    pred = res.get('category', 'general').lower()
                except:
                    pass
                
                # Validation
                final_type = "general"
                for val in label_map.values():
                    if val.lower() in pred:
                        final_type = val
                        break
                
                clause['type'] = final_type
                clause['confidence'] = 90.0
                clause['risk_level'] = RISK_LEVELS.get(final_type, 'low')
                results.append(clause)
                
        except Exception as e:
            print(f"Classification Batch Error: {e}")
            # Fallback for the whole batch
            for clause in batch:
                clause['type'] = 'general'
                clause['confidence'] = 50.0
                clause['risk_level'] = 'low'
                results.append(clause)
                
    return results