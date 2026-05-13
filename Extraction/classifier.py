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

# Mapping categories to risk levels (low, medium, high)
# AND mapping internal risk levels to frontend-friendly terms (safe, caution, unsafe)
RISK_LEVELS = {
    'non_compete':       'high',
    'intellectual_prop': 'high',
    'ip_ownership':      'high',
    'termination':       'high',
    'arbitration':       'medium',
    'confidentiality':   'medium',
    'indemnification':   'high',
    'liability_waiver':  'high',
    'limitation_of_liability': 'high',
    'unilateral_changes': 'high',
    'unilateral_modifications': 'high',
    'exit_penalty':      'high',
    'data_selling':      'high',
    'auto_renewal':      'medium',
    'price_escalation':  'medium',
    'governing_law':    'low',
    'compensation':      'low',
    'vacation':          'low',
    'general':           'low',
}

FRONTEND_RISK_MAP = {
    'high':   'unsafe',
    'medium': 'caution',
    'low':    'safe'
}

def classify_all(clauses):
    """Classifies a list of clauses in batches using Groq LLM with improved risk detection."""
    if not clauses or not os.getenv("GROQ_API_KEY"):
        return clauses

    # Batching to stay under rate limits (RPM)
    BATCH_SIZE = 5
    results = []
    
    for i in range(0, len(clauses), BATCH_SIZE):
        batch = clauses[i:i + BATCH_SIZE]
        
        # Prepare a single prompt for the batch
        batch_texts = "\n---\n".join([f"ID {j}: {c.get('full_text', '')[:500]}" for j, c in enumerate(batch)])
        
        prompt = f"""You are a legal expert. Classify these {len(batch)} contract clauses.
        
        Categories to choose from: {', '.join(label_map.values())}, limitation_of_liability, termination, compensation.
        
        For EACH clause, return:
        1. Category name.
        2. A numeric risk score (0-100) where 100 is extremely dangerous for the user.
        
        Return a JSON list of objects: [{{"id": index, "category": "name", "risk_score": 85}}]
        
        Clauses:
        {batch_texts}"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=600,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a professional legal classifier. Return ONLY JSON."},
                    {"role": "user", "content": prompt + "\nRespond with a JSON object containing a 'results' array."}
                ]
            )
            
            data = json.loads(response.choices[0].message.content)
            batch_results = data.get('results', [])
            
            for j, clause in enumerate(batch):
                res = next((r for r in batch_results if r.get('id') == j), {})
                pred_cat = res.get('category', 'general').lower()
                llm_risk_score = res.get('risk_score', 0)
                
                # 1. Determine Category
                final_type = "general"
                for val in list(label_map.values()) + list(RISK_LEVELS.keys()):
                    if val.lower() in pred_cat or pred_cat in val.lower():
                        final_type = val
                        break
                
                # 2. Determine Risk Level (high, medium, low)
                # We combine the category mapping with the LLM's dynamic risk score
                base_level = RISK_LEVELS.get(final_type, 'low')
                
                if llm_risk_score > 75:
                    final_level = 'high'
                elif llm_risk_score > 30:
                    final_level = 'medium'
                else:
                    final_level = base_level

                # 3. Add to clause object
                clause['type'] = final_type
                clause['confidence'] = 95.0
                clause['risk_level'] = final_level  # Internal use (high, medium, low)
                clause['risk'] = FRONTEND_RISK_MAP.get(final_level, 'safe') # Frontend use (unsafe, caution, safe)
                
                # Add legal note if high risk
                if final_level == 'high':
                    clause['legalNote'] = f"This {final_type.replace('_', ' ')} clause is flagged as HIGH RISK. It may significantly limit your rights or impose unexpected obligations."
                
                results.append(clause)
                
        except Exception as e:
            print(f"Classification Batch Error: {e}")
            for clause in batch:
                clause['type'] = 'general'
                clause['risk_level'] = 'low'
                clause['risk'] = 'safe'
                results.append(clause)
                
    return results