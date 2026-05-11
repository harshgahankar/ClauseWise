import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { MOCK_ANALYSIS, RISK_COLORS } from '../../utils/mockData';
import './SideBySidePage.css';

const RISK_ICON = { safe: '✓', caution: '⚠', unsafe: '✕' };

export default function SideBySidePage() {
  const navigate = useNavigate();
  const { analysisResult } = useApp();
  const result = analysisResult || MOCK_ANALYSIS;
  const [activeIdx, setActiveIdx] = useState(0);
  const [filter, setFilter] = useState('all');

  const clauses = result.clauses.filter(c => filter === 'all' || c.risk === filter);
  const clause = clauses[activeIdx] || clauses[0];

  const prev = () => setActiveIdx(i => Math.max(0, i - 1));
  const next = () => setActiveIdx(i => Math.min(clauses.length - 1, i + 1));

  if (!clause) return null;

  const colors = RISK_COLORS[clause.risk];

  return (
    <div className="sbs-page">
      <div className="sbs-page__inner">
        {/* Header */}
        <div className="sbs-header">
          <button className="sbs-back" onClick={() => navigate('/analysis')}>
            <ArrowLeft size={16} /> Back to Analysis
          </button>
          <div className="sbs-header__title">
            <h1>Side-by-Side View</h1>
            <p>{result.documentName}</p>
          </div>
          <div className="sbs-filter">
            {['all', 'unsafe', 'caution', 'safe'].map(f => (
              <button
                key={f}
                className={`sbs-filter-btn sbs-filter-btn--${f} ${filter === f ? 'active' : ''}`}
                onClick={() => { setFilter(f); setActiveIdx(0); }}
              >
                {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="sbs-body">
          {/* Sidebar: clause list */}
          <aside className="sbs-sidebar">
            <div className="sbs-sidebar__label">
              {clauses.length} clause{clauses.length !== 1 ? 's' : ''}
            </div>
            {clauses.map((c, i) => {
              const clrs = RISK_COLORS[c.risk];
              return (
                <button
                  key={c.id}
                  className={`sbs-clause-item ${i === activeIdx ? 'sbs-clause-item--active' : ''}`}
                  onClick={() => setActiveIdx(i)}
                  style={{ '--item-color': clrs.text, '--item-border': clrs.border }}
                >
                  <span className={`sbs-clause-dot sbs-clause-dot--${c.risk}`}>
                    {RISK_ICON[c.risk]}
                  </span>
                  <div className="sbs-clause-item__text">
                    <div className="sbs-clause-item__title">{c.title}</div>
                    <div className="sbs-clause-item__num">§ {c.number}</div>
                  </div>
                </button>
              );
            })}
          </aside>

          {/* Main: side by side panels */}
          <div className="sbs-main">
            {/* Clause nav */}
            <div className="sbs-nav">
              <button className="sbs-nav-btn" onClick={prev} disabled={activeIdx === 0}>
                <ChevronLeft size={18} />
              </button>
              <div className={`sbs-clause-badge sbs-clause-badge--${clause.risk}`}
                style={{ background: colors.bg, color: colors.text, border: `1px solid ${colors.border}` }}>
                {RISK_ICON[clause.risk]} {colors.label} · § {clause.number}
              </div>
              <h2 className="sbs-clause-title">{clause.title}</h2>
              <button className="sbs-nav-btn" onClick={next} disabled={activeIdx === clauses.length - 1}>
                <ChevronRight size={18} />
              </button>
            </div>

            <div className="sbs-panels">
              {/* Original */}
              <div className="sbs-panel sbs-panel--original">
                <div className="sbs-panel__header">
                  <div className="sbs-panel__label">
                    <span className="sbs-panel__dot sbs-panel__dot--gray" />
                    Original Legalese
                  </div>
                  <span className="sbs-panel__section">{clause.section}</span>
                </div>
                <div className="sbs-panel__body">
                  <p className="sbs-original-text">{clause.originalText}</p>
                </div>
              </div>

              {/* Divider */}
              <div className="sbs-divider">
                <div className="sbs-divider__line" />
                <div className="sbs-divider__icon">↔</div>
                <div className="sbs-divider__line" />
              </div>

              {/* Plain English */}
              <div className={`sbs-panel sbs-panel--plain sbs-panel--${clause.risk}`}>
                <div className="sbs-panel__header">
                  <div className="sbs-panel__label">
                    <span className={`sbs-panel__dot sbs-panel__dot--${clause.risk}`} />
                    Plain English Translation
                  </div>
                  <span className="sbs-panel__ai-tag">🤖 AI Analysis</span>
                </div>
                <div className="sbs-panel__body">
                  <p className="sbs-plain-text">{clause.plainEnglish}</p>

                  {clause.legalNote && (
                    <div className={`sbs-legal-note sbs-legal-note--${clause.risk}`}>
                      <div className="sbs-legal-note__label">⚖ Lawyer's Note</div>
                      <p>{clause.legalNote}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Pagination indicator */}
            <div className="sbs-pagination">
              {clauses.map((_, i) => (
                <button
                  key={i}
                  className={`sbs-pip ${i === activeIdx ? 'sbs-pip--active' : ''}`}
                  onClick={() => setActiveIdx(i)}
                  aria-label={`Go to clause ${i + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
