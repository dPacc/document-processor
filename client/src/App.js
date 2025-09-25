import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ProcessingResults from './components/ProcessingResults';
import Footer from './components/Footer';
import KeyboardShortcuts from './components/KeyboardShortcuts';
import './styles/App.css';

function App() {
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleProcessingComplete = (newResults) => {
    setResults(prev => [...prev, ...newResults]);
    setIsProcessing(false);
    toast.success(`Successfully processed ${newResults.length} document(s)`);
  };

  const handleProcessingError = (error) => {
    setIsProcessing(false);
    toast.error(`Processing failed: ${error}`);
  };

  const handleClearResults = () => {
    setResults([]);
    toast.info('Results cleared');
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ctrl/Cmd + U - Upload files
      if ((event.ctrlKey || event.metaKey) && event.key === 'u') {
        event.preventDefault();
        document.querySelector('input[type="file"]')?.click();
        return;
      }

      // Ctrl/Cmd + Enter - Process files
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        const processButton = document.querySelector('.btn-primary');
        if (processButton && !processButton.disabled) {
          processButton.click();
        }
        return;
      }

      // Ctrl/Cmd + D - Download all
      if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
        event.preventDefault();
        const downloadAllButton = document.querySelector('.btn-primary');
        if (downloadAllButton && downloadAllButton.textContent.includes('Download All')) {
          downloadAllButton.click();
        }
        return;
      }

      // Escape - Clear results or close modal
      if (event.key === 'Escape') {
        const modal = document.querySelector('.image-modal-overlay');
        if (modal) {
          modal.click();
        } else if (results.length > 0) {
          handleClearResults();
        }
        return;
      }

      // Delete - Clear results
      if (event.key === 'Delete' && results.length > 0) {
        handleClearResults();
        return;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [results.length]);

  return (
    <div className="App">
      <Header />
      
      <main className="main-content">
        <div className="split-layout">
          <div className="upload-panel">
            <div className="panel-header">
              <h1>Document Processor</h1>
              <p>Upload and process your documents with AI-powered orientation correction</p>
            </div>
            
            <FileUpload
              onProcessingStart={() => setIsProcessing(true)}
              onProcessingComplete={handleProcessingComplete}
              onProcessingError={handleProcessingError}
              isProcessing={isProcessing}
            />
          </div>

          <div className="results-panel">
            {results.length > 0 ? (
              <ProcessingResults 
                results={results} 
                onClear={handleClearResults}
              />
            ) : (
              <div className="empty-results">
                <h2>Results</h2>
                <p>Processed documents will appear here</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
      
      <KeyboardShortcuts />
      
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
}

export default App;