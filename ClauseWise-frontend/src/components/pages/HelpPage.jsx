import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, ChevronUp, Mail, MessageSquare, FileText, Shield, Zap, Users } from 'lucide-react';
import './HelpPage.css';

const FAQS = [
  {
    q: 'What types of documents can I upload?',
    a: 'ClauseWise supports PDF, DOCX, and plain text (.txt) files up to 20MB. We can analyze employment contracts, NDAs, service agreements, rental leases, terms of service, partnership agreements, and more.',
  },
  {
    q: 'Is my document kept private and secure?',
    a: 'Absolutely. All documents are encrypted in transit (TLS 1.3) and at rest (AES-256). We never sell your data or use it for any purpose other than your analysis. Documents are deleted from our servers after 90 days unless you choose to keep them.',
  },
  {
    q: 'How accurate is the AI analysis?',
    a: 'Our model is trained on 50,000+ legal agreements and benchmarked against licensed attorneys. It performs with high accuracy on common clause types. That said, ClauseWise is a smart assistant — not a licensed lawyer. For high-stakes agreements, we recommend using our findings as a starting point for a conversation with a real attorney.',
  },
  {
    q: 'What does each risk level mean?',
    a: 'Safe (green) means the clause is standard and poses no unusual risk. Caution (amber) means the clause is worth reviewing — it may be unusual or slightly unfavorable. Unsafe (red) means the clause is aggressive, potentially unenforceable, or could significantly harm your rights.',
  },
  {
    q: 'Can I download a PDF report of my analysis?',
    a: 'Yes! On any analysis page, click the "Export Report" button in the top right. You\'ll get a professionally formatted PDF summary including all flagged clauses, risk scores, and plain-English explanations — perfect for sharing with a lawyer or employer.',
  },
  {
    q: 'How is the Safety Score calculated?',
    a: 'The Safety Score (0–100) weighs the number and severity of flagged clauses against the total length and complexity of the document. A score of 80+ is generally considered safe. Below 60 indicates the document has significant concerns worth addressing before signing.',
  },
  {
    q: 'What is the "Ask AI Lawyer" chat feature?',
    a: 'After your analysis runs, you can open a chat window and ask specific questions in plain English — like "Can I negotiate the non-compete?" or "What does indemnification actually mean here?" The AI responds based on the context of your specific document.',
  },
  {
    q: 'Is this legal advice?',
    a: 'No. ClauseWise is an AI-powered document assistant, not a law firm. We help you understand what your contract says, but our analysis is not legal advice and does not create an attorney-client relationship. For binding legal decisions, always consult a licensed attorney.',
  },
];

const SUPPORT_OPTIONS = [
  { icon: <Mail size={22} />, title: 'Email Support', desc: 'We respond within 24 hours on business days.', action: 'support@clausewise.com', type: 'email' },
  { icon: <MessageSquare size={22} />, title: 'Live Chat', desc: 'Talk to our team in real time during business hours.', action: 'Start Chat', type: 'button' },
  { icon: <FileText size={22} />, title: 'Documentation', desc: 'Detailed guides for every feature and integration.', action: 'View Docs →', type: 'link' },
];

function FAQItem({ item }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`faq-item ${open ? 'faq-item--open' : ''}`}>
      <button className="faq-item__q" onClick={() => setOpen(o => !o)}>
        <span>{item.q}</span>
        {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>
      {open && <div className="faq-item__a"><p>{item.a}</p></div>}
    </div>
  );
}

export default function HelpPage() {
  return (
    <div className="help-page">
      <div className="help-hero">
        <div className="help-hero__inner">
          <div className="section__eyebrow">Help Center</div>
          <h1 className="help-hero__title">How can we help?</h1>
          <p className="help-hero__sub">Everything you need to get the most out of ClauseWise.</p>
        </div>
      </div>

      <div className="help-page__inner">
        {/* Quick links */}
        <div className="help-quicklinks">
          {[
            { icon: <Shield size={20} />, title: 'Understanding Risk Scores', link: '#faq' },
            { icon: <Zap size={20} />, title: 'How Analysis Works', link: '#faq' },
            { icon: <FileText size={20} />, title: 'Exporting Reports', link: '#faq' },
            { icon: <Users size={20} />, title: 'Team & Enterprise', link: '#contact' },
          ].map((item, i) => (
            <a key={i} href={item.link} className="help-quicklink">
              <div className="help-quicklink__icon">{item.icon}</div>
              <span>{item.title}</span>
            </a>
          ))}
        </div>

        {/* FAQ */}
        <section className="help-section" id="faq">
          <h2 className="help-section__title">Frequently Asked Questions</h2>
          <div className="faq-list">
            {FAQS.map((item, i) => (
              <FAQItem key={i} item={item} />
            ))}
          </div>
        </section>

        {/* Contact */}
        <section className="help-section" id="contact">
          <h2 className="help-section__title">Still need help?</h2>
          <p className="help-section__sub">Our team is here to assist you.</p>
          <div className="support-grid">
            {SUPPORT_OPTIONS.map((opt, i) => (
              <div key={i} className="support-card">
                <div className="support-card__icon">{opt.icon}</div>
                <div className="support-card__title">{opt.title}</div>
                <p className="support-card__desc">{opt.desc}</p>
                {opt.type === 'email' && (
                  <a href={`mailto:${opt.action}`} className="support-card__link">{opt.action}</a>
                )}
                {opt.type === 'button' && (
                  <button className="support-card__btn">{opt.action}</button>
                )}
                {opt.type === 'link' && (
                  <span className="support-card__link">{opt.action}</span>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <div className="help-cta">
          <div>
            <h3>Ready to scan your first contract?</h3>
            <p>No account needed. Upload any document and get results in seconds.</p>
          </div>
          <Link to="/scan" className="help-cta__btn">Start Free Scan →</Link>
        </div>
      </div>
    </div>
  );
}
