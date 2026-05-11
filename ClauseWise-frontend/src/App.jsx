import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import LandingPage from './components/pages/LandingPage';
import ScanPage from './components/pages/ScanPage';
import AnalysisPage from './components/pages/AnalysisPage';
import DocumentsPage from './components/pages/DocumentsPage';
import SideBySidePage from './components/pages/SideBySidePage';
import HelpPage from './components/pages/HelpPage';
import LoginPage from './components/pages/LoginPage';
import RegisterPage from './components/pages/RegisterPage';
import NotFoundPage from './components/pages/NotFoundPage';
import './index.css';

function Layout({ children, showFooter = true }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      {showFooter && <Footer />}
    </>
  );
}

// Auth pages manage their own navbar/footer — no Layout wrapper
export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <Layout><LandingPage /></Layout>
          } />
          <Route path="/scan" element={
            <Layout showFooter={false}><ScanPage /></Layout>
          } />
          <Route path="/analysis" element={
            <Layout><AnalysisPage /></Layout>
          } />
          <Route path="/analysis/side-by-side" element={
            <Layout><SideBySidePage /></Layout>
          } />
          <Route path="/documents" element={
            <Layout><DocumentsPage /></Layout>
          } />
          <Route path="/help" element={
            <Layout><HelpPage /></Layout>
          } />
          {/* Auth pages — use shared navbar/footer */}
          <Route path="/login"    element={<Layout showFooter={false}><LoginPage /></Layout>} />
          <Route path="/register" element={<Layout showFooter={false}><RegisterPage /></Layout>} />
          <Route path="*" element={
            <Layout><NotFoundPage /></Layout>
          } />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
