# Verdict thresholds based on SAFETY score (0-100)
def get_verdict(safety_score):
    if safety_score >= 80:
        return {
            'verdict':      'safe',
            'color':        'green',
            'summary':      'This contract looks relatively standard. Still read it fully before signing! ✅',
        }
    elif safety_score >= 50:
        return {
            'verdict':      'medium',
            'color':        'amber',
            'summary':      'This contract has some concerning clauses. Review carefully before signing! ⚠️',
        }
    else:
        return {
            'verdict':      'unsafe',
            'color':        'red',
            'summary':      'This contract has serious red flags. Do not sign without legal advice! 🚩',
        }


def score_contract(clauses):
    """
    Calculates a safety score based on the percentage of safe vs risky clauses.
    This approach is more stable than subtracting fixed points.
    """
    if not clauses:
        return {
            'score': 0, # 0 risk = 100 safety
            'verdict': 'safe',
            'color': 'green',
            'summary': 'No clauses found to analyze.',
            'clause_counts': {'high': 0, 'medium': 0, 'low': 0},
            'red_flags': [],
            'clauses': []
        }

    # Count by risk level
    counts = {'high': 0, 'medium': 0, 'low': 0}
    for clause in clauses:
        level = clause.get('risk_level', 'low')
        counts[level] = counts.get(level, 0) + 1

    # Weighted scoring: 
    # Low risk (Safe) = 100%
    # Medium risk (Caution) = 50%
    # High risk (Unsafe) = 0%
    total_clauses = len(clauses)
    weighted_sum = (counts['low'] * 1.0) + (counts['medium'] * 0.5) + (counts['high'] * 0.0)
    
    safety_score = round((weighted_sum / total_clauses) * 100)

    # Get verdict based on safety score
    verdict_info = get_verdict(safety_score)

    # Pull out the most dangerous clauses (high risk only)
    red_flags = [
        {
            'title':          c.get('type', 'Unknown Clause').replace('_', ' ').title(),
            'type':           c.get('type', ''),
            'ai_explanation': c.get('ai_explanation', c.get('plain_english', 'High risk detected.')),
        }
        for c in clauses if c.get('risk_level') == 'high'
    ]


    # Frontend expects 'score' to be the RISK score (0-100)
    # Risk Score = 100 - Safety Score
    risk_score = 100 - safety_score

    return {
        'score':         risk_score,
        'verdict':       verdict_info['verdict'],
        'color':         verdict_info['color'],
        'summary':       verdict_info['summary'],
        'clause_counts': counts,
        'red_flags':     red_flags,
        'clauses':       clauses,
    }