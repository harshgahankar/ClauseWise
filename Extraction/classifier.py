import json
import os
import re
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

KEYWORD_RULES = [
    ('arbitration',        re.compile(r'arbitrat|binding\s+arbitration|arbitrator', re.I), 0.75),
    ('liability_waiver',   re.compile(r'indemnif|hold\s+harmless|not\s+(be\s+)?(liable|responsible)|waive.*liability|no\s+liability|limitation\s+of\s+liability|as\s+is|without\s+(any\s+)?warrant', re.I), 0.7),
    ('data_selling',       re.compile(r'personally\s+identifiable\s+information|sell.*(personal|data)|share.*(personal|data)|data.*collect|privacy\s+policy|cookie|tracking', re.I), 0.65),
    ('unilateral_changes', re.compile(r'may\s+(modify|change|amend|update)\s+(these\s+)?terms|at\s+any\s+time\s+(without\s+)?notice|sole\s+discretion|unilaterally|change\s+the\s+terms', re.I), 0.7),
    ('auto_renewal',       re.compile(r'automatic(a(lly)?)?\s+renew|renew.*automatic|auto.?renew|evergreen', re.I), 0.8),
    ('exit_penalty',       re.compile(r'early\s+termination\s+(fee|penalty|charge)|cancellation\s+(fee|penalty|charge)|termination\s+(fee|penalty|charge)|liquidated\s+damages', re.I), 0.7),
    ('price_escalation',   re.compile(r'price\s+(increase|escalation|hike|change)|fee\s+(increase|change)|rate\s+(increase|adjust)|subject\s+to\s+change', re.I), 0.65),
    ('ip_ownership',       re.compile(r'intellectual\s+property|assignment.*invention|work\s+(made\s+)?for\s+hire|owns?\s+(all\s+)?rights|all\s+right,\s+title|exclusive\s+rights', re.I), 0.7),
    ('jurisdiction',       re.compile(r'governed\s+by\s+(the\s+)?laws\s+of|exclusive\s+(jurisdiction|venue)|proper\s+venue|forum|choice\s+of\s+(law|forum)', re.I), 0.6),
    ('notice_period',      re.compile(r'\d+\s+days[.\s]+(written\s+)?notice|notice\s+period|prior\s+written\s+notice|shall\s+give\s+notice', re.I), 0.6),
]

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
    if isinstance(result, dict) and 'error' in result:
        raise Exception(f"HF API error: {result['error']}")
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
    raise Exception(f"Unexpected HF API response format: {type(result).__name__}")

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

def _keyword_detect(text):
    text_lower = text.lower()
    best_type = "general"
    best_conf = 0.0
    for clause_type, pattern, confidence in KEYWORD_RULES:
        if pattern.search(text_lower):
            if confidence > best_conf:
                best_type = clause_type
                best_conf = confidence
    return best_type, round(best_conf * 100, 1)

def detect_type(text):
    try:
        clause_type, confidence = _hf_detect(text)
        if clause_type is not None:
            return clause_type, confidence
    except Exception as e:
        print(f"  HF API error: {e}")
    if os.path.isdir(MODEL_DIR):
        try:
            return _local_detect(text)
        except Exception as e:
            print(f"  Local model error: {e}")
    else:
        print(f"  Local model not found at {MODEL_DIR}, skipping fallback")
    clause_type, confidence = _keyword_detect(text)
    print(f"  Keyword fallback: {clause_type} ({confidence}%)")
    return clause_type, confidence

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
