import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ProcessingResults from './components/ProcessingResults';
import Footer from './components/Footer';
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

  return (
    <div className="App">
      <Header />
      
      <main className="main-content">
        <motion.div 
          className="hero-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="hero-content">
            <h1 className="hero-title">
              Document Processing
              <span className="gradient-text"> Made Simple</span>
            </h1>
            <p className="hero-subtitle">
              Advanced AI-powered document orientation correction and boundary detection.
              Upload your documents and get professionally processed results in seconds.
            </p>
          </div>
        </motion.div>

        <motion.div 
          className="upload-section"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <FileUpload
            onProcessingStart={() => setIsProcessing(true)}
            onProcessingComplete={handleProcessingComplete}
            onProcessingError={handleProcessingError}
            isProcessing={isProcessing}
          />
        </motion.div>

        {results.length > 0 && (
          <motion.div 
            className="results-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <ProcessingResults 
              results={results} 
              onClear={handleClearResults}
            />
          </motion.div>
        )}
      </main>

      <Footer />
      
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