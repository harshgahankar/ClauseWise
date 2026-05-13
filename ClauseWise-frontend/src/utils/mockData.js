// ── Keep all your existing mock data exactly as-is ────────────────────────────
export const MOCK_ANALYSIS = {
  documentName: 'Employment Agreement - John Doe.pdf',
  contractType: 'Employment',
  safetyScore: 72,
  verdict: 'Needs Attention',
  verdictColor: 'caution',
  summary: 'This document contains several clauses that may limit your rights or impose unexpected liabilities.',
  stats: { safe: 18, caution: 5, unsafe: 3 },
  clauses: [
    {
      id: 'c1', number: '14.2', title: 'Non-Compete Agreement', risk: 'unsafe',
      originalText: '"...employee shall not engage in any competitive business activity within a 100-mile radius for a period of 5 years after termination..."',
      plainEnglish: "After you leave this job, you can't work for any competitor within 100 miles for 5 whole years.",
      legalNote: 'This clause is excessively broad in both duration and geography. In many jurisdictions, this would be unenforceable.',
      section: 'Section 14',
    },
    {
      id: 'c2', number: '8.1', title: 'Intellectual Property Assignment', risk: 'unsafe',
      originalText: '"...all inventions, ideas, and software created by the employee during the term of employment..."',
      plainEnglish: "Anything you invent while you work here belongs to the company — even if you made it at home on weekends.",
      legalNote: '"Whether or not related to company business" means anything you build at home on your own time belongs to the employer.',
      section: 'Section 8',
    },
    {
      id: 'c3', number: '21.5', title: 'Termination without Notice', risk: 'unsafe',
      originalText: '"...employer reserves the right to terminate employment immediately for any reason at its sole discretion..."',
      plainEnglish: "They can fire you at any moment, for any reason, with no warning and no pay.",
      legalNote: 'While at-will employment is common, zero severance for a senior role is atypical and high-risk.',
      section: 'Section 21',
    },
    {
      id: 'c4', number: '4.1', title: 'Mandatory Arbitration', risk: 'caution',
      originalText: '"...any dispute arising from this agreement shall be resolved through binding arbitration..."',
      plainEnglish: "If you have a problem with the company, you can't take them to court.",
      legalNote: 'Mandatory arbitration limits your right to a jury trial.',
      section: 'Section 4',
    },
    {
      id: 'c5', number: '3.2', title: 'Confidentiality Scope', risk: 'caution',
      originalText: '"...employee agrees to maintain strict confidentiality of all information learned during employment..."',
      plainEnglish: "You must keep everything you learn at this company secret — forever.",
      legalNote: 'Standard confidentiality is expected, but unlimited scope with no time limit is worth negotiating.',
      section: 'Section 3',
    },
    {
      id: 'c6', number: '7.1', title: 'Base Compensation', risk: 'safe',
      originalText: '"...employee shall receive an annual base salary of $120,000, payable bi-weekly..."',
      plainEnglish: "You'll earn $120,000 a year, paid every two weeks. This is clear, fair, and standard.",
      legalNote: 'This clause is clear and standard. No concerns.',
      section: 'Section 7',
    },
    {
      id: 'c7', number: '12.1', title: 'Vacation Policy', risk: 'safe',
      originalText: '"...employee is entitled to 15 days of paid vacation per year..."',
      plainEnglish: "You get 15 paid vacation days per year. This is reasonable and standard.",
      legalNote: 'Standard vacation provision. The accrual rate is fair and clearly defined.',
      section: 'Section 12',
    },
  ],
};

export const CONTRACT_TYPES = ['MSA', 'Employment', 'NDA', 'Rental', 'TOS', 'Partnership', 'Freelance', 'Other'];

export const RISK_COLORS = {
  safe:    { bg: 'var(--safe-bg)',    border: 'var(--safe-border)',    text: 'var(--safe)',    label: 'Safe'    },
  caution: { bg: 'var(--caution-bg)', border: 'var(--caution-border)', text: 'var(--caution)', label: 'Caution' },
  unsafe:  { bg: 'var(--unsafe-bg)',  border: 'var(--unsafe-border)',  text: 'var(--unsafe)',  label: 'Unsafe'  },
};

// ── NEW: converts your backend response → your frontend shape ─────────────────
const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';


function mapRiskLevel(backendLevel) {
  if (backendLevel === 'high')   return 'unsafe';
  if (backendLevel === 'medium') return 'caution';
  return 'safe';
}

function mapVerdict(backendVerdict) {
  if (backendVerdict === 'unsafe') return { verdict: 'High Risk',        verdictColor: 'unsafe'  };
  if (backendVerdict === 'medium') return { verdict: 'Needs Attention',  verdictColor: 'caution' };
  return                                   { verdict: 'All Clear',        verdictColor: 'safe'    };
}

function mapSafetyScore(backendScore) {
  // backend score = risk points (higher = worse)
  // frontend score = safety score (higher = better)
  return Math.max(0, 100 - backendScore);
}

function backendToFrontend(apiResponse, fileName) {
  const clauses = (apiResponse.clauses || []).map((c, i) => {
    const risk = mapRiskLevel(c.risk_level);
    return {
      id:           `c${c.id || i + 1}`,
      number:       String(c.id || i + 1),
      title:        c.title || `Clause ${i + 1}`,
      risk,
      originalText: c.full_text || '',
      plainEnglish: c.ai_explanation || c.plain_english || 'No explanation available.',
      legalNote:    c.plain_english || '',
      section:      `Clause ${c.id || i + 1}`,
      type:         c.type || 'general',
      confidence:   c.confidence || null,
    };
  });

  const counts = apiResponse.clause_counts || {};
  const verdictInfo = mapVerdict(apiResponse.verdict);

  return {
    documentName:  fileName,
    contractType:  'Contract',
    safetyScore:   mapSafetyScore(apiResponse.score || 0),
    verdict:       verdictInfo.verdict,
    verdictColor:  verdictInfo.verdictColor,
    summary:       apiResponse.summary || '',
    stats: {
      safe:    counts.low    || clauses.filter(c => c.risk === 'safe').length,
      caution: counts.medium || clauses.filter(c => c.risk === 'caution').length,
      unsafe:  counts.high   || clauses.filter(c => c.risk === 'unsafe').length,
    },
    clauses,
    redFlags: (apiResponse.red_flags || []).map(f => f.title),
  };
}

export async function analyzePDF(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BACKEND_URL}/analyze-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Server error: ${response.status}`);
  }

  const data = await response.json();
  return backendToFrontend(data, file.name);
}