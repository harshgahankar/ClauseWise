import json
import torch
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Load trained model from Hugging Face Hub ──────────────────────────────────
HF_MODEL = "harsh-101/clause-bert-classifier"

print(f"* Loading BERT classifier from Hugging Face Hub ({HF_MODEL})...")
tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
model     = AutoModelForSequenceClassification.from_pretrained(HF_MODEL)
model.eval()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "label_map.json")) as f:
    label_map = json.load(f)
    label_map = {int(k): v for k, v in label_map.items()}

print(f"* BERT classifier ready - {len(label_map)} clause types")

# ── Risk levels ──────────────────────────────────────────────
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
    'auto_renewal':       'Contract renews automatically unless cancelled 🔄',
    'liability_waiver':   'Company not responsible for damages or losses 🛡️',
    'arbitration':        'You waive your right to sue in court ⚖️',
    'data_selling':       'Your data may be sold or shared with third parties 📂',
    'unilateral_changes': 'Company can change terms without notice 📝',
    'exit_penalty':       'Early termination fees apply 💸',
    'price_escalation':   'Price can increase periodically 📈',
    'jurisdiction':       'Disputes handled in another state or country 🏛️',
    'ip_ownership':       'Company owns content you create on the platform 🎨',
    'notice_period':      'Long notice period required to cancel ⏳',
    'general':            'Standard clause — review for context 📄',
}

# ── Predict clause type using BERT ────────────────────────────────────────────
def detect_type(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=True
    )

    with torch.no_grad():                        # no gradient needed for inference
        outputs = model(**inputs)

    logits      = outputs.logits
    predicted_id = torch.argmax(logits, dim=1).item()
    clause_type  = label_map.get(predicted_id, "general")

    # get confidence score (0-100%)
    probabilities = torch.softmax(logits, dim=1)
    confidence    = probabilities[0][predicted_id].item()

    return clause_type, round(confidence * 100, 1)

def classify_all(clauses):
    return [classify_clause(c) for c in clauses]

def classify_clause(clause):
    full_text         = clause.get('full_text', '')
    clause_type, conf = detect_type(full_text)

    # ── Self-healing ──────────────────────────────────────────────────────────
    was_healed = False
    try:
        from rag_healer import heal_classification
        clause_type, conf, was_healed = heal_classification(full_text, clause_type, conf)
    except Exception as e:
        print(f"  Healer skipped: {e}")

    risk = RISK_LEVELS.get(clause_type, RISK_LEVELS['general'])
    return {
        **clause,
        'type':        clause_type,
        'confidence':  conf,
        'self_healed': was_healed,
        'risk_level':  risk['level'],
        'flag_color':  risk['color'],
        'plain_english': PLAIN_ENGLISH.get(clause_type, ''),
        'is_risky':    risk['level'] in ('high', 'medium'),
    }