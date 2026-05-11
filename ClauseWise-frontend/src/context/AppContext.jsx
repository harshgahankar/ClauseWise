import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AppContext = createContext(null);

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
};

export const AppProvider = ({ children }) => {
  // Initialize documents from localStorage or an empty array
  const [documents, setDocuments] = useState(() => {
    const savedDocs = localStorage.getItem('clausewise_documents');
    return savedDocs ? JSON.parse(savedDocs) : [];
  });

  // Persist documents to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('clausewise_documents', JSON.stringify(documents));
  }, [documents]);

  const [activeDocument, setActiveDocument] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const addDocument = useCallback((doc) => {
    setDocuments(prev => [doc, ...prev]);
  }, []);

  const removeDocument = useCallback((id) => {
    setDocuments(prev => prev.filter(d => d.id !== id));
  }, []);

  return (
    <AppContext.Provider value={{
      documents, addDocument, removeDocument,
      activeDocument, setActiveDocument,
      uploadProgress, setUploadProgress,
      isAnalyzing, setIsAnalyzing,
      analysisResult, setAnalysisResult,
    }}>
      {children}
    </AppContext.Provider>
  );
};
