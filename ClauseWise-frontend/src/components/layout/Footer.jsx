import React from 'react';
import { Link } from 'react-router-dom';
import { Scale } from 'lucide-react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <div className="footer__logo">
            <Scale size={16} />
          </div>
          <span className="footer__name">ClauseWise</span>
        </div>
        <p className="footer__disclaimer">
          © 2026 ClauseWise. This is not legal advice, but a smart assistant to help you understand your contract.
        </p>
        <nav className="footer__links">
          <Link to="/privacy">Privacy Policy</Link>
          <Link to="/terms">Terms of Service</Link>
          <Link to="/help">Contact Support</Link>
        </nav>
      </div>
    </footer>
  );
}
