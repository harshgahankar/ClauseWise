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

def detect_type_llm(text):
    """Use Groq to classify the clause type to save RAM."""
    if not os.getenv("GROQ_API_KEY"):
        return "general", 100.0

    prompt = f"""Classify the following legal clause into ONE of these categories: 
    {', '.join(label_map.values())}
    
    Clause Text: {text[:500]}
    
    Return ONLY the category name."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        prediction = response.choices[0].message.content.strip().lower()
        
        # Match with label map
        for val in label_map.values():
            if val.lower() in prediction:
                return val, 95.0
        return "general", 80.0
    except:
        return "general", 50.0

def classify_clause(clause):
    """Adds classification and risk level to a single clause."""
    text = clause.get('full_text', '')
    
    # Using LLM classification to save RAM (avoiding BERT/Torch)
    clause_type, confidence = detect_type_llm(text)
    
    clause['type'] = clause_type
    clause['confidence'] = confidence
    clause['risk_level'] = RISK_LEVELS.get(clause_type, 'low')
    
    return clause

def classify_all(clauses):
    """Classifies a list of clauses."""
    # To save time/API calls, we only classify the first few or use a faster method
    # For now, let's just do all of them as it's a small number usually
    return [classify_clause(c) for c in clauses]