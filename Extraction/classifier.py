import json
import os
import requests

HF_MODEL = "harsh-101/clause-bert-classifier"
API_URL  = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS  = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "bert_clause_model")

with open(os.path.join(BASE_DIR, "label_map.json")) as f:
    label_map = json.load(f)
    label_map = {int(k): v for k, v in label_map.items()}

KNOWN_TYPES = set(label_map.values()) | {'general'}

RISK_LEVELS = {
    'auto_renewal':       {'level': 'high',   'color': 'red'},
    'liability_waiver':   {'level': 'high',   'color': 'red'},
    'arbitration':        {'level': 'high',   'color': 'red'},
    'data_selling':       {'level': 'high',   'color': 'red'},
    'unilateral_changes': {'level': 'high',   'color': 'red'},
    'exit_penalty':       {'level': 'medium', 'color': 'amber'},
    'price_escalation':   {'level': 'medium', 'color': 'amber'},
    'jurisdiction':       {'level': 'medium', 'color': 'amber'},
    'ip_ownership':       {'level': 'medium', 'color': 'amber'},
    'notice_period':      {'level': 'low',    'color': 'green'},
    'general':            {'level': 'low',    'color': 'green'},
}

PLAIN_ENGLISH = {
    'auto_renewal':       'Contract renews automatically unless cancelled.',
    'liability_waiver':   'Company not responsible for damages or losses.',
    'arbitration':        'You waive your right to sue in court.',
    'data_selling':       'Your data may be sold or shared with third parties.',
    'unilateral_changes': 'Company can change terms without notice.',
    'exit_penalty':       'Early termination fees apply.',
    'price_escalation':   'Price can increase periodically.',
    'jurisdiction':       'Disputes handled in another state or country.',
    'ip_ownership':       'Company owns content you create on the platform.',
    'notice_period':      'Long notice period required to cancel.',
    'general':            'Standard clause — review for context.',
}

def _hf_detect(text):
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": text}, timeout=30)
    result = response.json()
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
        predictions = result[0]
        top = max(predictions, key=lambda x: x['score'])
        label_str = top['label']
        confidence = round(top['score'] * 100, 1)
        if label_str.startswith('LABEL_'):
            idx = int(label_str.split('_')[1])
            return label_map.get(idx, "general"), confidence
        if label_str in KNOWN_TYPES:
            return label_str, confidence
    return None, 0.0

_tokenizer = None
_model = None

def _local_detect(text):
    global _tokenizer, _model
    if _model is None:
        print("  Loading local BERT model (fallback)...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        _model.eval()
        print("  Local model loaded.")
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    import torch
    with torch.no_grad():
        outputs = _model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    confidence, idx = torch.max(probs, dim=-1)
    return label_map.get(int(idx), "general"), round(float(confidence) * 100, 1)

def detect_type(text):
    try:
        clause_type, confidence = _hf_detect(text)
        if clause_type is not None:
            return clause_type, confidence
    except Exception as e:
        print(f"  HF API error (will try local model): {e}")
    try:
        return _local_detect(text)
    except Exception as e:
        print(f"  Local model error: {e}")
    return "general", 0.0

def classify_all(clauses):
    return [classify_clause(c) for c in clauses]

def classify_clause(clause):
    full_text         = clause.get('full_text', '')
    clause_type, conf = detect_type(full_text)

    was_healed = False
    try:
        from rag_healer import heal_classification
        clause_type, conf, was_healed = heal_classification(full_text, clause_type, conf)
    except Exception as e:
        print(f"  Healer skipped: {e}")

    risk = RISK_LEVELS.get(clause_type, RISK_LEVELS['general'])
    return {
        **clause,
        'type':         clause_type,
        'confidence':   conf,
        'self_healed':  was_healed,
        'risk_level':   risk['level'],
        'flag_color':   risk['color'],
        'plain_english': PLAIN_ENGLISH.get(clause_type, ''),
        'is_risky':     risk['level'] in ('high', 'medium'),
    }
