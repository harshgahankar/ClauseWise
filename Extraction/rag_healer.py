import os
from groq import Groq
from rag_store import retrieve_similar
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CONFIDENCE_THRESHOLD = 70.0

VALID_TYPES = [
    'auto_renewal', 'liability_waiver', 'arbitration', 'data_selling',
    'unilateral_changes', 'exit_penalty', 'price_escalation',
    'jurisdiction', 'ip_ownership', 'notice_period', 'general'
]

JARGON_WORDS = [
    'herein', 'hereof', 'thereof', 'whereas', 'heretofore',
    'notwithstanding', 'pursuant', 'aforementioned', 'ipso facto',
    'inter alia', 'mutatis mutandis', 'indemnify'
]

# ── Fix 1: bad classification ─────────────────────────────────────────────────
def heal_classification(clause_text, bert_type, bert_confidence):
    if bert_confidence >= CONFIDENCE_THRESHOLD:
        return bert_type, bert_confidence, False   # BERT is confident, no fix needed

    similar = retrieve_similar(clause_text, n=3)
    if not similar:
        return bert_type, bert_confidence, False   # nothing in DB yet to heal with

    examples = "\n".join([
        f"- \"{s['text'][:120]}\" → {s['type']}"
        for s in similar
    ])

    prompt = f"""You are a legal clause classifier.

Clause: "{clause_text}"

BERT predicted "{bert_type}" but was only {bert_confidence:.0f}% confident.

Most similar clauses from our database:
{examples}

What is the correct type? Reply with ONLY one of:
{', '.join(VALID_TYPES)}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )

    healed_type = response.choices[0].message.content.strip().lower()
    if healed_type not in VALID_TYPES:
        healed_type = bert_type

    was_healed = healed_type != bert_type
    if was_healed:
        print(f"  [FIX] Classification healed: {bert_type} -> {healed_type}")

    return healed_type, 95.0, was_healed


# ── Fix 2: bad explanation ────────────────────────────────────────────────────
def is_bad_explanation(text):
    if not text or len(text.strip()) < 40:
        return True
    jargon_count = sum(1 for w in JARGON_WORDS if w in text.lower())
    return jargon_count >= 2

def heal_explanation(clause_text, clause_type, risk_level, bad_explanation):
    similar   = retrieve_similar(clause_text, n=2)
    examples  = ""
    if similar:
        examples = "\nExamples of good explanations for similar clauses:\n"
        examples += "\n".join([
            f"- \"{s['plain_english']}\""
            for s in similar if s.get('plain_english')
        ])

    prompt = f"""You are explaining a contract clause to someone who has never read a contract.
    Explain it like I'm 5 years old. Use emojis!

    Clause: "{clause_text}"
    Type: {clause_type} | Risk: {risk_level}
    {examples}

    Previous attempt was unclear: "{bad_explanation}"

    Write a NEW explanation:
    - Start with "This clause means... 💡"
    - Use 1-2 emojis throughout.
    - Max 2 sentences, zero legal jargon.
    - End with a super simple warning or tip."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    healed = response.choices[0].message.content.strip()
    print(f"  [FIX] Explanation healed for {clause_type}")
    return healed