import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, FileText, HelpCircle, Plus } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { to: '/scan', label: 'New Scan', icon: <Plus size={15} /> },
    { to: '/documents', label: 'My Documents', icon: <FileText size={15} /> },
    { to: '/help', label: 'Help', icon: <HelpCircle size={15} /> },
  ];

  return (
    <header className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="navbar__inner">
        <Link to="/" className="navbar__brand">
          <div className="navbar__logo">
            <Scale size={18} />
          </div>
          <span className="navbar__name">ClauseWise</span>
        </Link>

        <nav className="navbar__nav">
          {navLinks.map(({ to, label, icon }) => (
            <Link
              key={to}
              to={to}
              className={`navbar__link ${location.pathname === to ? 'navbar__link--active' : ''}`}
            >
              {icon}
              {label}
            </Link>
          ))}
        </nav>

      </div>
    </header>
  );
}
