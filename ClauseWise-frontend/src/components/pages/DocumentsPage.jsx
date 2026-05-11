import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, BarChart2, Download, Trash2, Search, FileText, ShieldCheck, AlertTriangle, XCircle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { generatePDFReport } from '../../utils/reportGenerator';
import './DocumentsPage.css';

const RISK_CONFIG = {
  'SAFE': { color: 'var(--safe)', bg: 'var(--safe-bg)', icon: <ShieldCheck size={14} /> },
  'LOW RISK': { color: 'var(--safe)', bg: 'var(--safe-bg)', icon: <ShieldCheck size={14} /> },
  'MODERATE': { color: 'var(--caution)', bg: 'var(--caution-bg)', icon: <AlertTriangle size={14} /> },
  'CRITICAL': { color: 'var(--unsafe)', bg: 'var(--unsafe-bg)', icon: <XCircle size={14} /> },
};

function ScoreBar({ score, riskLevel }) {
  const cfg = RISK_CONFIG[riskLevel] || RISK_CONFIG['SAFE'];
  return (
    <div className="score-bar-wrap">
      <span className="score-bar-value" style={{ color: cfg.color }}>{score}%</span>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${score}%`, background: cfg.color }} />
      </div>
      <span className="score-bar-label" style={{ background: cfg.bg, color: cfg.color }}>
        {cfg.icon} {riskLevel}
      </span>
    </div>
  );
}

export default function DocumentsPage() {
  const navigate = useNavigate();
  const { documents, removeDocument, setAnalysisResult } = useApp();
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');

  const filtered = documents.filter(d => {
    const matchSearch = d.name.toLowerCase().includes(search.toLowerCase());
    const matchType = filterType === 'all' || d.type === filterType;
    return matchSearch && matchType;
  });

  const types = ['all', ...new Set(documents.map(d => d.type))];

  const totalFlags = documents.reduce((acc, d) => acc + (d.riskLevel === 'CRITICAL' ? 1 : 0), 0);
  const avgScore = documents.length > 0 ? Math.round(documents.reduce((a, d) => a + d.safetyScore, 0) / documents.length) : 0;

  return (
    <div className="docs-page">
      <div className="docs-page__inner">
        <div className="docs-header">
          <div>
            <h1 className="docs-title">Document Library</h1>
            <p className="docs-sub">Secure storage for your scanned legal agreements. AI-driven insights are preserved for every version.</p>
          </div>
          <Link to="/scan" className="docs-new-btn">
            <Plus size={18} />
            New Scan
          </Link>
        </div>

        {/* Stats */}
        <div className="docs-stats">
          <div className="docs-stat">
            <div className="docs-stat__icon docs-stat__icon--blue"><FileText size={18} /></div>
            <div>
              <div className="docs-stat__label">TOTAL ANALYZED</div>
              <div className="docs-stat__value">{documents.length}</div>
            </div>
          </div>
          <div className="docs-stat">
            <div className="docs-stat__icon docs-stat__icon--red"><AlertTriangle size={18} /></div>
            <div>
              <div className="docs-stat__label">HIGH RISK FLAGS</div>
              <div className="docs-stat__value docs-stat__value--red">{totalFlags}</div>
            </div>
          </div>
          <div className="docs-stat">
            <div className="docs-stat__icon docs-stat__icon--gold"><BarChart2 size={18} /></div>
            <div>
              <div className="docs-stat__label">AVG SAFETY SCORE</div>
              <div className="docs-stat__value">{avgScore}%</div>
            </div>
          </div>
        </div>

        {/* Search & filter */}
        <div className="docs-toolbar">
          <div className="docs-search">
            <Search size={16} className="docs-search__icon" />
            <input
              className="docs-search__input"
              type="text"
              placeholder="Search documents…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="docs-type-filter">
            {types.map(t => (
              <button
                key={t}
                className={`docs-type-btn ${filterType === t ? 'active' : ''}`}
                onClick={() => setFilterType(t)}
              >
                {t === 'all' ? 'All Types' : t}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="docs-table">
          <div className="docs-table__head">
            <div className="docs-col docs-col--name">Document Name</div>
            <div className="docs-col docs-col--date">Scan Date</div>
            <div className="docs-col docs-col--type">Type</div>
            <div className="docs-col docs-col--score">Safety Score</div>
            <div className="docs-col docs-col--actions">Actions</div>
          </div>

          {filtered.length === 0 ? (
            <div className="docs-empty">
              <FileText size={40} />
              <p>No documents found. <Link to="/scan">Upload your first contract →</Link></p>
            </div>
          ) : (
            filtered.map(doc => (
              <div key={doc.id} className="docs-table__row">
                <div className="docs-col docs-col--name">
                  <div className={`doc-icon doc-icon--${doc.riskLevel === 'CRITICAL' ? 'red' : doc.riskLevel === 'LOW RISK' || doc.riskLevel === 'SAFE' ? 'blue' : 'gold'}`}>
                    <FileText size={16} />
                  </div>
                  <div>
                    <div className="doc-name">{doc.name}</div>
                    <div className="doc-meta">{doc.size} · {doc.category}</div>
                  </div>
                </div>
                <div className="docs-col docs-col--date">
                  <span className="doc-date">{doc.scanDate}</span>
                </div>
                <div className="docs-col docs-col--type">
                  <span className="doc-type-badge">{doc.type}</span>
                </div>
                <div className="docs-col docs-col--score">
                  <ScoreBar score={doc.safetyScore} riskLevel={doc.riskLevel} />
                </div>
                <div className="docs-col docs-col--actions">
                  <button
                    className="doc-action doc-action--view"
                    title="View Analysis"
                    onClick={() => {
                      setAnalysisResult(doc.fullResult);
                      navigate('/analysis');
                    }}
                  >
                    <BarChart2 size={15} />
                  </button>
                  <button
                    className="doc-action doc-action--download"
                    title="Download Report"
                    onClick={() => generatePDFReport(doc.fullResult)}
                  >
                    <Download size={15} />
                  </button>
                  <button
                    className="doc-action doc-action--delete"
                    title="Delete"
                    onClick={() => removeDocument(doc.id)}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
