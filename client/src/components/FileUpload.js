import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, Loader, CheckCircle, AlertCircle, Zap } from 'lucide-react';
import { processDocument, processBatch } from '../services/api';

const FileUpload = ({ onProcessingStart, onProcessingComplete, onProcessingError, isProcessing }) => {
  const [files, setFiles] = useState([]);
  const [processingFiles, setProcessingFiles] = useState(new Set());

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(rejection => {
        console.error('File rejected:', rejection.file.name, rejection.errors);
      });
    }

    // Add accepted files
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: 'pending',
      preview: URL.createObjectURL(file)
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: true,
    maxFiles: 20
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

    try {
      let results;
      
      if (files.length === 1) {
        // Single file processing
        const result = await processDocument(files[0].file);
        results = [{
          ...result,
          fileName: files[0].file.name,
          fileId: files[0].id
        }];
      } else {
        // Batch processing
        const filesList = files.map(f => f.file);
        const batchResult = await processBatch(filesList);
        results = batchResult.results.map((result, index) => ({
          ...result,
          fileName: files[index].file.name,
          fileId: files[index].id
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
          <motion.div
            animate={{ 
              rotate: isProcessing ? 360 : 0,
              scale: isDragActive ? 1.1 : 1 
            }}
            transition={{ 
              rotate: { duration: 1, repeat: isProcessing ? Infinity : 0, ease: "linear" },
              scale: { duration: 0.3 }
            }}
          >
            {isProcessing ? (
              <Loader size={48} className="upload-icon processing" />
            ) : (
              <Upload size={48} className="upload-icon" />
            )}
          </motion.div>
          
          <h3 className="dropzone-title">
            {isDragActive ? 'Drop files here' : 'Upload Documents'}
          </h3>
          
          <p className="dropzone-subtitle">
            {isProcessing 
              ? 'Processing your documents...'
              : 'Drag & drop your images here, or click to browse'
            }
          </p>
          
          <p className="dropzone-info">
            Supports JPG, JPEG, PNG • Max 20 files • AI-powered processing
          </p>
        </div>
      </motion.div>

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
                    <p className="file-size">
                      {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
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