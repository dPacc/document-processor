import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, Loader, CheckCircle, AlertCircle, Zap, Download } from 'lucide-react';
import { processDocument, processBatch } from '../services/api';

const FileUpload = ({ onProcessingStart, onProcessingComplete, onProcessingError, isProcessing }) => {
  const [files, setFiles] = useState([]);
  const [processingFiles, setProcessingFiles] = useState(new Set());
  const [processingProgress, setProcessingProgress] = useState({});
  const [rejectedFiles, setRejectedFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const rejected = rejectedFiles.map(rejection => ({
        file: rejection.file,
        errors: rejection.errors.map(e => e.message).join(', ')
      }));
      setRejectedFiles(prev => [...prev, ...rejected]);
      
      // Clear rejected files after 5 seconds
      setTimeout(() => {
        setRejectedFiles([]);
      }, 5000);
    }

    // Validate file sizes and types
    const validFiles = acceptedFiles.filter(file => {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setRejectedFiles(prev => [...prev, { 
          file, 
          errors: 'File size exceeds 10MB limit' 
        }]);
        return false;
      }
      return true;
    });

    // Add accepted files with enhanced metadata
    const newFiles = validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: 'pending',
      preview: URL.createObjectURL(file),
      uploadedAt: new Date(),
      originalSize: file.size
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: true,
    maxFiles: 20,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const removeFile = (fileId) => {
    setFiles(prev => {
      const file = prev.find(f => f.id === fileId);
      if (file && file.preview) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  const processFiles = async () => {
    if (files.length === 0) return;

    onProcessingStart();
    setProcessingFiles(new Set(files.map(f => f.id)));
    setProcessingProgress({});

    try {
      let results;
      
      if (files.length === 1) {
        // Single file processing with progress
        setProcessingProgress({ [files[0].id]: 50 });
        const result = await processDocument(files[0].file);
        setProcessingProgress({ [files[0].id]: 100 });
        
        results = [{
          ...result,
          fileName: files[0].file.name,
          fileId: files[0].id,
          compressionRatio: ((files[0].originalSize - result.final_size.reduce((a, b) => a * b, 4)) / files[0].originalSize * 100).toFixed(1)
        }];
      } else {
        // Batch processing with individual progress tracking
        const filesList = files.map(f => f.file);
        
        // Simulate individual progress tracking
        files.forEach((file, index) => {
          setTimeout(() => {
            setProcessingProgress(prev => ({
              ...prev,
              [file.id]: Math.min(30 + (index * 10), 90)
            }));
          }, index * 200);
        });
        
        const batchResult = await processBatch(filesList);
        
        // Complete all progress
        const completedProgress = {};
        files.forEach(file => {
          completedProgress[file.id] = 100;
        });
        setProcessingProgress(completedProgress);
        
        results = batchResult.results.map((result, index) => ({
          ...result,
          fileName: files[index].file.name,
          fileId: files[index].id,
          compressionRatio: ((files[index].originalSize - result.final_size.reduce((a, b) => a * b, 4)) / files[index].originalSize * 100).toFixed(1)
        }));
      }

      // Update file statuses
      setFiles(prev => prev.map(file => ({
        ...file,
        status: 'completed'
      })));

      onProcessingComplete(results);
      
      // Clear files after successful processing
      setTimeout(() => {
        files.forEach(file => {
          if (file.preview) {
            URL.revokeObjectURL(file.preview);
          }
        });
        setFiles([]);
        setProcessingProgress({});
      }, 2000);

    } catch (error) {
      // Update file statuses to error
      setFiles(prev => prev.map(file => ({
        ...file,
        status: 'error'
      })));
      
      onProcessingError(error.message || 'Unknown error occurred');
    } finally {
      setProcessingFiles(new Set());
    }
  };

  const clearAll = () => {
    files.forEach(file => {
      if (file.preview) {
        URL.revokeObjectURL(file.preview);
      }
    });
    setFiles([]);
  };

  return (
    <div className="file-upload-container">
      <motion.div
        className={`dropzone ${isDragActive ? 'active' : ''} ${isProcessing ? 'processing' : ''}`}
        {...getRootProps()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          {isProcessing ? (
            <Loader size={32} className="upload-icon processing" />
          ) : (
            <Upload size={32} className="upload-icon" />
          )}
          
          <h3 className="dropzone-title">
            {isDragActive ? 'Drop files here' : 'Upload Documents'}
          </h3>
          
          <p className="dropzone-subtitle">
            {isProcessing 
              ? 'Processing documents...'
              : 'Drag and drop files or click to browse'
            }
          </p>
          
          <p className="dropzone-info">
            JPG, JPEG, PNG files • Maximum 20 files • 10MB per file
          </p>
        </div>
      </motion.div>

      {/* Rejected Files Alert */}
      <AnimatePresence>
        {rejectedFiles.length > 0 && (
          <motion.div
            className="rejected-files-alert"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <AlertCircle size={18} className="alert-icon" />
            <div className="alert-content">
              <h4>Files Rejected</h4>
              {rejectedFiles.map((rejection, index) => (
                <p key={index}>
                  <strong>{rejection.file.name}</strong>: {rejection.errors}
                </p>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            className="file-list"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="file-list-header">
              <h4>Selected Files ({files.length})</h4>
              <div className="file-list-actions">
                <button 
                  onClick={processFiles}
                  disabled={isProcessing}
                  className="btn btn-primary"
                >
                  {isProcessing ? (
                    <>
                      <Loader size={16} className="spinning" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Zap size={16} />
                      Process All
                    </>
                  )}
                </button>
                <button 
                  onClick={clearAll}
                  disabled={isProcessing}
                  className="btn btn-secondary"
                >
                  Clear All
                </button>
              </div>
            </div>

            <div className="file-items">
              {files.map((fileObj, index) => (
                <motion.div
                  key={fileObj.id}
                  className={`file-item ${fileObj.status}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <div className="file-preview">
                    <img 
                      src={fileObj.preview} 
                      alt={fileObj.file.name}
                      className="preview-image"
                    />
                  </div>
                  
                  <div className="file-info">
                    <p className="file-name">{fileObj.file.name}</p>
                    <div className="file-details">
                      <p className="file-size">
                        {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <p className="file-type">
                        {fileObj.file.type.split('/')[1].toUpperCase()}
                      </p>
                      {fileObj.uploadedAt && (
                        <p className="file-uploaded">
                          Added {new Date(fileObj.uploadedAt).toLocaleTimeString()}
                        </p>
                      )}
                    </div>
                    
                    {/* Progress Bar */}
                    {processingProgress[fileObj.id] && (
                      <div className="progress-container">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill"
                            style={{ width: `${processingProgress[fileObj.id]}%` }}
                          />
                        </div>
                        <span className="progress-text">
                          {processingProgress[fileObj.id]}%
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="file-status">
                    {fileObj.status === 'pending' && <File size={20} />}
                    {fileObj.status === 'processing' && <Loader size={20} className="spinning" />}
                    {fileObj.status === 'completed' && <CheckCircle size={20} className="success" />}
                    {fileObj.status === 'error' && <AlertCircle size={20} className="error" />}
                  </div>

                  {!isProcessing && (
                    <button
                      onClick={() => removeFile(fileObj.id)}
                      className="remove-file"
                      aria-label="Remove file"
                    >
                      <X size={16} />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;