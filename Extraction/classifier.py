import json
import os

# ── MOCKED for diagnosis ───────────────────────────────────────────────────
print("* NOTE: Running in MOCK mode for BERT classifier to avoid hang...", flush=True)

class MockModel:
    def eval(self): pass

tokenizer = None
model     = MockModel()

LABEL_MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_map.json")
with open(LABEL_MAP_PATH, 'r') as f:
    label_map = json.load(f)
    label_map = {int(k): v for k, v in label_map.items()}

print(f"* Mock BERT classifier ready - {len(label_map)} clause types", flush=True)

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

# ── Predict clause type using MOCK ────────────────────────────────────────────
def detect_type(text):
    # Just return 'general' or a random type for now
    import random
    types = list(RISK_LEVELS.keys())
    return random.choice(types), 100.0

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