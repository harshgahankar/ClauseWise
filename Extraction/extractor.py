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

def is_heading(line):
    """Check if a line matches any common contract heading patterns."""
    for pattern in HEADING_PATTERNS:
        if re.match(pattern, line):
            return True
    return False

def extract_clauses(pdf_input):
    """
    Extracts clauses from either PDF bytes or raw text.
    Returns a list of dictionaries, each representing a clause.
    """
    import fitz
    import re

    # 1. Get raw text from input
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

    # 2. Pre-process text
    text = text.replace('\xa0', ' ')
    lines = text.split('\n')

    clauses = []
    current_clause = None

    # 3. Split text into clauses based on headings
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_heading(line):
            if current_clause is not None:
                clauses.append(current_clause)

            current_clause = {
                'id': len(clauses) + 1,
                'title': line,
                'body': [],
                'full_text': line
            }
        elif current_clause is not None:
            current_clause['body'].append(line)
            current_clause['full_text'] += ' ' + line
        else:
            # If no heading found yet, create an initial generic clause
            current_clause = {
                'id': 1,
                'title': "Introduction / General Terms",
                'body': [line],
                'full_text': line
            }

    if current_clause is not None:
        clauses.append(current_clause)

    # 4. If still no clauses found, return the whole text as one clause
    if not clauses and text.strip():
        clauses.append({
            'id': 1,
            'title': "Full Document",
            'body': [text.strip()],
            'full_text': text.strip()
        })

    return clauses