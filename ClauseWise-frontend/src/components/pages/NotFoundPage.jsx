import React from 'react';
import { Link } from 'react-router-dom';
import './NotFoundPage.css';

export default function NotFoundPage() {
  return (
    <div className="notfound">
      <div className="notfound__inner">
        <div className="notfound__glyph">⚖</div>
        <h1 className="notfound__title">404</h1>
        <p className="notfound__sub">
          This page doesn't exist — but unlike a hidden contract clause,
          at least we're telling you about it.
        </p>
        <div className="notfound__actions">
          <Link to="/" className="notfound__btn notfound__btn--primary">Go Home</Link>
          <Link to="/scan" className="notfound__btn notfound__btn--ghost">Start a Scan</Link>
        </div>
      </div>
    </div>
  );
}
