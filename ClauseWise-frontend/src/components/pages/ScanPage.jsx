import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, X, CheckCircle, Loader, AlertTriangle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { MOCK_ANALYSIS } from '../../utils/mockData';
import './ScanPage.css';

const ACCEPTED_TYPES = ['.pdf', '.docx', '.txt'];

const ANALYSIS_STEPS = [
  'Extracting document structure…',
  'Identifying clause boundaries…',
  'Running risk classification model…',
  'Generating plain-English summaries…',
  'Computing safety verdict…',
  'Finalizing report…',
];

const CONTRACT_TYPES_HINT = ['Employment', 'NDA', 'Rental', 'SaaS TOS', 'Partnership', 'Freelance', 'MSA', 'Loan'];

export default function ScanPage() {
  const navigate = useNavigate();
  const { setAnalysisResult, setIsAnalyzing, addDocument } = useApp();
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const validateFile = (f) => {
    const ext = '.' + f.name.split('.').pop().toLowerCase();
    if (!ACCEPTED_TYPES.includes(ext)) {
      setError('Please upload a PDF, DOCX, or TXT file.');
      return false;
    }
    if (f.size > 20 * 1024 * 1024) {
      setError('File size must be under 20MB.');
      return false;
    }
    return true;
  };

  const handleFile = useCallback((f) => {
    setError('');
    if (validateFile(f)) setFile(f);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);

  const onFileChange = (e) => {
    const f = e.target.files[0];
    if (f) handleFile(f);
  };

  const startAnalysis = useCallback(async () => {
    if (!file) return;
    setAnalyzing(true);
    setIsAnalyzing(true);
    setProgress(0);
    setCurrentStep(0);
    setError('');

    try {
      const controller = new AbortController();
      const TIMEOUT_MS = 120_000;

      // Animate progress from 0→95% while API call runs
      const stepPromise = (async () => {
        for (let step = 0; step < ANALYSIS_STEPS.length; step++) {
          setCurrentStep(step);
          const start = Math.round((step / ANALYSIS_STEPS.length) * 95);
          const end   = Math.round(((step + 1) / ANALYSIS_STEPS.length) * 95);
          for (let p = start; p <= end; p++) {
            await new Promise(r => setTimeout(r, 80));
            if (controller.signal.aborted) return;
            setProgress(p);
          }
        }
      })();

      const { analyzePDF } = await import('../../utils/mockData');

      const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);
      const result = await analyzePDF(file, controller.signal);
      clearTimeout(timeoutId);

      // Wait for animation to catch up, then jump to 100%
      await stepPromise;
      setProgress(100);
      await new Promise(r => setTimeout(r, 200));

      const newDoc = {
        id: Date.now().toString(),
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(1) + ' MB',
        category: 'Contract',
        type: result.contractType || 'Other',
        scanDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        safetyScore: result.safetyScore,
        riskLevel: result.verdictColor === 'safe' ? 'SAFE' : result.verdictColor === 'caution' ? 'MODERATE' : 'CRITICAL',
        status: 'complete',
        fullResult: result
      };
      addDocument(newDoc);

      setAnalysisResult(result);
      setIsAnalyzing(false);
      navigate('/analysis');

    } catch (err) {
      console.error('Analysis failed:', err);
      if (err.name === 'AbortError') {
        setError('Request timed out. The server took too long to respond. Please try again or check your backend.');
      } else {
        setError(err.message || 'Analysis failed. Make sure your backend server is running on port 5000.');
      }
      setAnalyzing(false);
      setIsAnalyzing(false);
    }
  }, [file, navigate, setAnalysisResult, setIsAnalyzing]);

  return (
    <div className="scan-page">
      <div className="scan-page__inner">
        <div className="scan-page__header">
          <div className="section__eyebrow">New Scan</div>
          <h1 className="scan-page__title">Upload Your Contract</h1>
          <p className="scan-page__sub">
            PDF, DOCX, or plain text. Analysis takes under 30 seconds.
            Your documents are encrypted end-to-end.
          </p>
        </div>

        {!analyzing ? (
          <div className="scan-main">
            {/* Drop zone */}
            <div
              className={`dropzone ${dragOver ? 'dropzone--active' : ''} ${file ? 'dropzone--has-file' : ''}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onClick={() => !file && fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_TYPES.join(',')}
                onChange={onFileChange}
                className="sr-only"
              />
              {file ? (
                <div className="dropzone__file">
                  <div className="dropzone__file-icon">
                    <FileText size={28} />
                  </div>
                  <div className="dropzone__file-info">
                    <div className="dropzone__file-name">{file.name}</div>
                    <div className="dropzone__file-size">{(file.size / 1024 / 1024).toFixed(2)} MB · Ready to analyze</div>
                  </div>
                  <button
                    className="dropzone__file-remove"
                    onClick={(e) => { e.stopPropagation(); setFile(null); setError(''); }}
                    aria-label="Remove file"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <div className="dropzone__prompt">
                  <div className="dropzone__icon-wrap">
                    <Upload size={32} />
                  </div>
                  <div className="dropzone__text">
                    <strong>Drag & drop your file here</strong>
                    <span>or <button className="dropzone__browse" onClick={() => fileInputRef.current?.click()}>browse files</button></span>
                  </div>
                  <div className="dropzone__accepted">PDF · DOCX · TXT &nbsp;·&nbsp; Max 20MB</div>
                </div>
              )}
            </div>

            {error && (
              <div className="scan-error">
                <AlertTriangle size={15} /> {error}
              </div>
            )}

            {/* Contract type hints */}
            <div className="scan-hints">
              <div className="scan-hints__label">We automatically detect:</div>
              <div className="scan-hints__tags">
                {CONTRACT_TYPES_HINT.map(t => (
                  <span key={t} className="scan-hints__tag">{t}</span>
                ))}
              </div>
            </div>

            <button
              className={`scan-btn ${file ? 'scan-btn--active' : 'scan-btn--disabled'}`}
              onClick={startAnalysis}
              disabled={!file}
            >
              {file ? (
                <>
                  <CheckCircle size={18} />
                  Start AI Analysis
                </>
              ) : (
                <>
                  <Upload size={18} />
                  Upload a File to Begin
                </>
              )}
            </button>

            <div className="scan-trust">
              <div className="scan-trust__item">🔒 End-to-end encrypted</div>
              <div className="scan-trust__item">⚡ Results in &lt;30 seconds</div>
              <div className="scan-trust__item">🚫 Never sold or shared</div>
            </div>
          </div>
        ) : (
          <div className="analysis-loading">
            <div className="analysis-loading__ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" fill="none" stroke="var(--border)" strokeWidth="8"/>
                <circle
                  cx="50" cy="50" r="44" fill="none"
                  stroke="var(--accent-blue-light)" strokeWidth="8"
                  strokeDasharray="276"
                  strokeDashoffset={276 - (276 * progress / 100)}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                  style={{ transition: 'stroke-dashoffset 0.3s ease' }}
                />
              </svg>
              <div className="analysis-loading__pct">{progress}%</div>
            </div>

            <div className="analysis-loading__file">
              <FileText size={16} />
              {file?.name}
            </div>

            <div className="analysis-loading__step">
              {ANALYSIS_STEPS[currentStep]}
            </div>

            <div className="analysis-loading__steps">
              {ANALYSIS_STEPS.map((s, i) => (
                <div key={i} className={`analysis-step ${i < currentStep ? 'done' : i === currentStep ? 'active' : ''}`}>
                  {i < currentStep ? <CheckCircle size={14} /> : i === currentStep ? <Loader size={14} className="spin" /> : <div className="step-dot" />}
                  <span>{s}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
