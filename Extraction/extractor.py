import re
import fitz  # PyMuPDF

HEADING_PATTERNS = [
    r'^\d+\.\d*\s+[A-Z]',        # matches: 1. PAYMENT  or  1.1 Terms
    r'^\d+\)\s+[A-Z]',            # matches: 1) PAYMENT
    r'^(ARTICLE|SECTION|CLAUSE)\s+[\dIVX]+',  # matches: ARTICLE 1, SECTION IV
    r'^WHEREAS',                   # matches: WHEREAS the parties...
    r'^NOW,?\s*THEREFORE',         # matches: NOW THEREFORE
    r'^[A-Z][A-Z\s]{4,40}$',      # matches: PAYMENT TERMS (all caps line)
]

DOCUMENT_TITLE_KEYWORDS = [
    'agreement', 'contract', 'addendum', 'amendment',
    'certificate', 'license', 'policy', 'notice',
    'waiver', 'release', 'terms', 'consent',
    'affidavit', 'declaration', 'understanding',
    'indenture', 'memorandum', 'stipulation',
]

SIGNATURE_START_PATTERNS = [
    r'^IN\s+WITNESS\s+WHEREOF',
    r'^SIGN(?:ED|ATURE)\s*(?:PAGE|BLOCK)?',
    r'^EXECUTED\s+(?:this|as\s+of)',
    r'^\[?\s*(?:COMPANY|BORROWER|LENDER|EMPLOYER|EMPLOYEE|CONTRACTOR|CLIENT|VENDOR)\s*\]?\s*$',
    r'^By:\s*_{5,}',
    r'^_{10,}\s*$',
    r'^Date[d]?\s*:?\s*_{0,}$',
    r'^\(?(?:CORPORATE\s+)?SEAL\)?\s*$',
    r'^Notary\s+Public',
    r'^(Name|Title|Witness|Attest)\s*:',
    r'^\[?Signature\s*(?:Block)?\]?',
]


def is_document_title(line):
    lower = line.lower().strip()
    for kw in DOCUMENT_TITLE_KEYWORDS:
        if kw in lower:
            return True
    return False


def is_signature_line(line):
    for pattern in SIGNATURE_START_PATTERNS:
        if re.match(pattern, line):
            return True
    return False


def is_heading(line):
    for pattern in HEADING_PATTERNS:
        if re.match(pattern, line):
            return True
    return False


def extract_clauses(pdf_input):
    if isinstance(pdf_input, bytes):
        try:
            pdf = fitz.open(stream=pdf_input, filetype="pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            pdf.close()
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return []
    elif isinstance(pdf_input, str):
        text = pdf_input
    else:
        return []

    text = text.replace('\xa0', ' ')
    lines = text.split('\n')

    clauses = []
    current_clause = None
    in_signature_block = False
    first_heading_seen = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_heading(line):
            if not first_heading_seen and is_document_title(line):
                continue

            first_heading_seen = True
            in_signature_block = False

            if current_clause is not None:
                clauses.append(current_clause)

            current_clause = {
                'id': len(clauses) + 1,
                'title': line,
                'body': [],
                'full_text': line
            }
        elif is_signature_line(line):
            in_signature_block = True
        elif in_signature_block:
            continue
        elif current_clause is not None:
            current_clause['body'].append(line)
            current_clause['full_text'] += ' ' + line
        else:
            current_clause = {
                'id': 1,
                'title': "Introduction / General Terms",
                'body': [line],
                'full_text': line
            }
            first_heading_seen = True

    if current_clause is not None:
        clauses.append(current_clause)

    if not clauses and text.strip():
        clauses.append({
            'id': 1,
            'title': "Full Document",
            'body': [text.strip()],
            'full_text': text.strip()
        })

    return clauses
