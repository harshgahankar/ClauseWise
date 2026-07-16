import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from extractor import extract_clauses
from classifier import classify_all
from translator import translate_all
from scorer import score_contract
from rag_store import store_all_clauses, get_store_stats
from rag_qa import answer_question, support_answer
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'endpoints': {
            'POST /extract':      'Step 1 only',
            'POST /analyze':      'Steps 1+2',
            'POST /full-analyze': 'Steps 1+2+3',
            'POST /report':       'Steps 1+2+3+4 via text',
            'POST /analyze-pdf':  'Steps 1+2+3+4 via PDF upload',
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Please send JSON with a "text" field'}), 400
    clauses = extract_clauses(data['text'].strip())
    return jsonify({'total_clauses': len(clauses), 'clauses': clauses})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Please send JSON with a "text" field'}), 400
    clauses    = extract_clauses(data['text'].strip())
    classified = classify_all(clauses)
    return jsonify({
        'total_clauses': len(classified),
        'risky_count':   len([c for c in classified if c['is_risky']]),
        'clauses':       classified
    })

@app.route('/full-analyze', methods=['POST'])
def full_analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Please send JSON with a "text" field'}), 400
    clauses    = extract_clauses(data['text'].strip())
    classified = classify_all(clauses)
    translated = translate_all(classified)
    return jsonify({
        'total_clauses': len(translated),
        'risky_count':   len([c for c in translated if c['is_risky']]),
        'clauses':       translated
    })

@app.route('/report', methods=['POST'])
def report():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Please send JSON with a "text" field'}), 400
    text = data['text'].strip()
    if not text:
        return jsonify({'error': 'Text field is empty'}), 400
    
    clauses    = extract_clauses(text)
    classified = classify_all(clauses)
    translated = translate_all(classified)
    final      = score_contract(translated)
    
    contract_id = str(uuid.uuid4())
    try:
        store_all_clauses(translated, contract_id=contract_id)
    except Exception as e:
        print(f"  RAG store skipped: {e}")
    final['contract_id'] = contract_id
    
    return jsonify(final)


@app.route('/analyze-pdf', methods=['POST'])
def analyze_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded. Send a PDF as form-data with key "file"'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    pdf_bytes = file.read()
    clauses = extract_clauses(pdf_bytes)

    if not clauses:
        return jsonify({'error': 'Could not extract text from PDF. It may be a scanned image or protected.'}), 400

    classified = classify_all(clauses)
    translated = translate_all(classified)
    final      = score_contract(translated)
    
    contract_id = str(uuid.uuid4())
    try:
        store_all_clauses(translated, contract_id=contract_id)
    except Exception as e:
        print(f"  RAG store skipped: {e}")
    final['contract_id'] = contract_id
    
    final['extracted_text'] = " ".join([c['full_text'] for c in clauses])

    return jsonify(final)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'Send JSON with "question" and "clauses"'}), 400
    answer = answer_question(data['question'], data.get('clauses', []))
    return jsonify({'answer': answer})

@app.route('/support-chat', methods=['POST'])
def support_chat():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'Send JSON with "question"'}), 400
    answer = support_answer(data['question'])
    return jsonify({'answer': answer})

@app.route('/rag-stats')
def rag_stats():
    return jsonify(get_store_stats())

if __name__ == '__main__':
    print("\n* Contract Analyzer - full pipeline ready")
    print("* POST /analyze-pdf - upload a PDF contract")
    print("* POST /report      - send raw text")
    print("* POST /chat        - ask questions about the contract\n")
    app.run(debug=True, port=5000, host='0.0.0.0')