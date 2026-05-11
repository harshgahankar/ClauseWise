import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Upload, Zap, ShieldCheck, ArrowRight,
  FileSearch, Users, Star, CheckCircle, AlertTriangle, XCircle
} from 'lucide-react';
import './LandingPage.css';

const FEATURES = [
  {
    icon: <Upload size={22} />,
    color: 'blue',
    title: 'Upload Any Contract',
    desc: 'PDF, DOCX, or plain text. Our system handles encryption at rest and in transit.',
  },
  {
    icon: <Zap size={22} />,
    color: 'gold',
    title: 'AI Analysis in Seconds',
    desc: 'Our specialized LLM identifies restrictive covenants, indemnity traps, and termination triggers.',
  },
  {
    icon: <ShieldCheck size={22} />,
    color: 'green',
    title: 'Review Flagged Risks',
    desc: 'Get a structured report with red, amber, and green highlights you can actually understand.',
  },
];

const STATS = [
  { value: '50K+', label: 'Contracts Analyzed' },
  { value: '12,000', label: 'Red Flags Caught' },
  { value: '5,000+', label: 'Professionals Trust Us' },
  { value: '4.9★', label: 'Average Rating' },
];

const SAMPLE_FLAGS = [
  { risk: 'unsafe', clause: '14.2', title: 'Non-Compete: 5 years, 100-mile radius', summary: "You won't be able to work in your field for 5 years after leaving." },
  { risk: 'caution', clause: '8.1', title: 'IP Assignment: All personal projects', summary: 'Anything you build at home might belong to your employer.' },
  { risk: 'safe', clause: '7.1', title: 'Base Salary: $120,000/year', summary: 'Clear, fair, and standard compensation clause.' },
];

export default function LandingPage() {
  const heroRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => {
        if (e.isIntersecting) e.target.classList.add('visible');
      }),
      { threshold: 0.15 }
    );
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        <div className="hero__bg-grid" />
        <div className="hero__inner">
          <div className="hero__content">
            <div className="hero__badge">
              <span className="hero__badge-dot" />
              AI-Powered Legal Intelligence
            </div>
            <h1 className="hero__headline">
              Scan Contracts for
              <span className="hero__headline-accent"> Red Flags</span>
              <br />in Seconds.
            </h1>
            <p className="hero__sub">
              Most people sign contracts they don't understand. Hidden auto-renewal clauses,
              liability waivers, and arbitration traps cost ordinary people money and rights.
              ClauseWise reads the fine print — so you don't have to.
            </p>
            <div className="hero__actions">
              <Link to="/scan" className="btn btn--primary btn--lg">
                Start Free Analysis
                <ArrowRight size={18} />
              </Link>
              <Link to="/documents" className="btn btn--ghost btn--lg">
                View Sample Report
              </Link>
            </div>
            <div className="hero__trust">
            </div>
          </div>

          <div className="hero__demo">
            <div className="hero__demo-card">
              <div className="hero__demo-header">
                <div className="hero__demo-dot red" />
                <div className="hero__demo-dot yellow" />
                <div className="hero__demo-dot green" />
                <span className="hero__demo-title">ClauseWise Analysis</span>
              </div>
              <div className="hero__demo-score">
                <div className="hero__score-ring">
                  <svg viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="32" fill="none" stroke="var(--border)" strokeWidth="6"/>
                    <circle cx="40" cy="40" r="32" fill="none" stroke="var(--caution-border)"
                      strokeWidth="6" strokeDasharray="201" strokeDashoffset="57"
                      strokeLinecap="round" transform="rotate(-90 40 40)"/>
                  </svg>
                  <div className="hero__score-value">72</div>
                </div>
                <div className="hero__score-info">
                  <div className="hero__score-label">Safety Score</div>
                  <div className="hero__score-verdict caution">⚠ Needs Attention</div>
                  <div className="hero__score-meta">Employment Agreement · John Doe.pdf</div>
                </div>
              </div>
              <div className="hero__demo-flags">
                {SAMPLE_FLAGS.map((f, i) => (
                  <div key={i} className={`hero__flag hero__flag--${f.risk}`}>
                    <div className="hero__flag-left">
                      {f.risk === 'unsafe' ? <XCircle size={14} /> :
                       f.risk === 'caution' ? <AlertTriangle size={14} /> :
                       <CheckCircle size={14} />}
                      <span className="hero__flag-clause">§{f.clause}</span>
                      <span className="hero__flag-title">{f.title}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* How it works */}
      <section className="how-it-works">
        <div className="section__inner">
          <div className="section__header reveal">
            <div className="section__eyebrow">The Process</div>
            <h2 className="section__title">Three Steps to Clarity</h2>
            <p className="section__sub">Advanced linguistic modeling designed to interpret legal complexity with editorial precision.</p>
          </div>
          <div className="features__grid">
            {FEATURES.map((f, i) => (
              <div key={i} className={`feature-card feature-card--${f.color} reveal`} style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="feature-card__step">0{i + 1}</div>
                <div className={`feature-card__icon feature-card__icon--${f.color}`}>
                  {f.icon}
                </div>
                <h3 className="feature-card__title">{f.title}</h3>
                <p className="feature-card__desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Side by side preview */}
      <section className="preview">
        <div className="section__inner preview__inner">
          <div className="preview__content reveal">
            <div className="section__eyebrow">Deep Analysis</div>
            <h2 className="section__title">Read Between the Lines</h2>
            <p className="preview__desc">
              ClauseWise doesn't just find keywords. It understands context.
              Our interface presents findings as sophisticated annotations —
              preserving the "Lawyer's Commentary" feel.
            </p>
            <ul className="preview__features">
              <li><CheckCircle size={16} /> <strong>Clarity Scoring</strong> — Quantifiable legibility metrics for every clause</li>
              <li><CheckCircle size={16} /> <strong>Historical Comparison</strong> — Compare against 50K+ market-standard agreements</li>
              <li><CheckCircle size={16} /> <strong>Plain-English Summaries</strong> — A 10-year-old could understand every flag</li>
              <li><CheckCircle size={16} /> <strong>Contract Type Detection</strong> — Rent, TOS, Employment, NDA, and more</li>
            </ul>
            <Link to="/scan" className="btn btn--primary">
              Try It Now <ArrowRight size={16} />
            </Link>
          </div>
          <div className="preview__visual reveal">
            <div className="preview__card">
              <div className="preview__flag-badge unsafe">● CRITICAL RED FLAG</div>
              <div className="preview__clause-text">
                "...employee shall not engage in any competitive business activity within a <mark>100-mile radius for a period of 5 years</mark> after termination..."
              </div>
              <div className="preview__explanation">
                <div className="preview__exp-label">🤖 Plain English</div>
                <p>You won't be able to work anywhere nearby in your industry for 5 years after quitting. In most states, this would be unenforceable — but you'd still have to fight it in court.</p>
              </div>
            </div>
            <div className="preview__flag-badge-bottom caution">◆ AMBER CAUTION</div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta__inner">
          <div className="cta__glow" />
          <h2 className="cta__title">Ready to sign with confidence?</h2>
          <div className="cta__actions">
            <Link to="/scan" className="btn btn--white btn--lg">
              Get Started For Free
            </Link>
            <Link to="/help" className="btn btn--outline-white btn--lg">
              Talk to an Expert
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
