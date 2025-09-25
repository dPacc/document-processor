import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, 
  Eye, 
  RotateCw, 
  Clock, 
  Trash2, 
  ZoomIn,
  ZoomOut,
  X,
  Loader
} from 'lucide-react';

const ProcessingResults = ({ results, onClear }) => {
  const [selectedResult, setSelectedResult] = useState(null);
  const [imageZoom, setImageZoom] = useState(1);
  const [isDownloadingAll, setIsDownloadingAll] = useState(false);

  const downloadImage = (result) => {
    const link = document.createElement('a');
    link.href = `data:image/jpeg;base64,${result.image_base64}`;
    link.download = `processed_${result.fileName}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatProcessingTime = (timeMs) => {
    if (timeMs < 1000) {
      return `${Math.round(timeMs)}ms`;
    } else {
      return `${(timeMs / 1000).toFixed(2)}s`;
    }
  };

  const formatRotationAngle = (angle) => {
    return `${angle > 0 ? '+' : ''}${angle.toFixed(2)}°`;
  };

  const openImageModal = (result) => {
    setSelectedResult(result);
    setImageZoom(1);
  };

  const closeImageModal = () => {
    setSelectedResult(null);
    setImageZoom(1);
  };

  const zoomIn = () => setImageZoom(prev => Math.min(prev * 1.2, 3));
  const zoomOut = () => setImageZoom(prev => Math.max(prev / 1.2, 0.5));

  const downloadAll = async () => {
    if (results.length === 0) return;
    
    setIsDownloadingAll(true);
    
    try {
      // Create a zip file with all processed images
      const JSZip = window.JSZip || require('jszip');
      const zip = new JSZip();
      
      results.forEach((result, index) => {
        // Convert base64 to blob
        const byteCharacters = atob(result.image_base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        
        const filename = `processed_${result.fileName}`;
        zip.file(filename, byteArray);
      });
      
      const content = await zip.generateAsync({ type: 'blob' });
      
      // Download the zip file
      const link = document.createElement('a');
      link.href = URL.createObjectURL(content);
      link.download = `processed_documents_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Cleanup
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Error creating zip file:', error);
      // Fallback: download individually
      results.forEach(result => downloadImage(result));
    } finally {
      setIsDownloadingAll(false);
    }
  };

  const getTotalStats = () => {
    if (results.length === 0) return null;
    
    const totalProcessingTime = results.reduce((sum, result) => sum + result.processing_time_ms, 0);
    const avgProcessingTime = totalProcessingTime / results.length;
    const avgRotation = results.reduce((sum, result) => sum + Math.abs(result.rotation_angle), 0) / results.length;
    
    return {
      totalFiles: results.length,
      totalTime: totalProcessingTime,
      avgTime: avgProcessingTime,
      avgRotation: avgRotation
    };
  };

  const stats = getTotalStats();

  return (
    <div className="processing-results">
      <div className="results-header">
        <div className="results-title-section">
          <h2 className="results-title">
            Results ({results.length})
          </h2>
          {stats && (
            <div className="results-stats-summary">
              <span>Avg: {formatProcessingTime(stats.avgTime)}</span>
              <span>•</span>
              <span>Rotation: {stats.avgRotation.toFixed(1)}°</span>
              <span>•</span>
              <span>Total: {formatProcessingTime(stats.totalTime)}</span>
            </div>
          )}
        </div>
        <div className="results-actions">
          {results.length > 1 && (
            <button 
              onClick={downloadAll} 
              disabled={isDownloadingAll}
              className="btn btn-primary"
            >
              {isDownloadingAll ? (
                <>
                  <Loader size={16} className="spinning" />
                  Creating ZIP...
                </>
              ) : (
                <>
                  <Download size={16} />
                  Download All
                </>
              )}
            </button>
          )}
          <button onClick={onClear} className="btn btn-outline">
            <Trash2 size={16} />
            Clear All
          </button>
        </div>
      </div>

      <div className="results-grid">
        {results.map((result, index) => (
          <motion.div
            key={result.fileId || index}
            className="result-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            whileHover={{ y: -5 }}
          >
            <div className="result-image-container">
              <img
                src={`data:image/jpeg;base64,${result.image_base64}`}
                alt={`Processed ${result.fileName}`}
                className="result-image"
              />
              <div className="image-overlay">
                <button
                  onClick={() => openImageModal(result)}
                  className="overlay-btn"
                  aria-label="View full size"
                >
                  <Eye size={20} />
                </button>
                <button
                  onClick={() => downloadImage(result)}
                  className="overlay-btn"
                  aria-label="Download"
                >
                  <Download size={20} />
                </button>
              </div>
            </div>

            <div className="result-info">
              <h3 className="result-filename">{result.fileName}</h3>
              
              <div className="result-stats">
                <div className="stat">
                  <RotateCw size={14} />
                  <span className="stat-value">{formatRotationAngle(result.rotation_angle)}</span>
                </div>
                
                <div className="stat">
                  <Clock size={14} />
                  <span className="stat-value">{formatProcessingTime(result.processing_time_ms)}</span>
                </div>
              </div>

              <div className="result-dimensions">
                <span>Original: {result.original_size[0]}×{result.original_size[1]}</span>
                <span>Final: {result.final_size[0]}×{result.final_size[1]}</span>
              </div>

              <div className="result-actions">
                <button
                  onClick={() => downloadImage(result)}
                  className="btn btn-primary btn-small"
                >
                  <Download size={14} />
                  Download
                </button>
                <button
                  onClick={() => openImageModal(result)}
                  className="btn btn-outline btn-small"
                >
                  <Eye size={14} />
                  Preview
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Image Modal */}
      <AnimatePresence>
        {selectedResult && (
          <motion.div
            className="image-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeImageModal}
          >
            <motion.div
              className="image-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <div className="modal-title">
                  <h3>{selectedResult.fileName}</h3>
                  <div className="modal-stats">
                    <span>Rotation: {formatRotationAngle(selectedResult.rotation_angle)}</span>
                    <span>•</span>
                    <span>Processing: {formatProcessingTime(selectedResult.processing_time_ms)}</span>
                  </div>
                </div>
                <div className="modal-controls">
                  <button onClick={zoomOut} className="modal-btn" aria-label="Zoom out">
                    <ZoomOut size={18} />
                  </button>
                  <span className="zoom-indicator">{Math.round(imageZoom * 100)}%</span>
                  <button onClick={zoomIn} className="modal-btn" aria-label="Zoom in">
                    <ZoomIn size={18} />
                  </button>
                  <button 
                    onClick={() => downloadImage(selectedResult)} 
                    className="modal-btn" 
                    aria-label="Download"
                  >
                    <Download size={18} />
                  </button>
                  <button onClick={closeImageModal} className="modal-btn close-btn" aria-label="Close">
                    <X size={18} />
                  </button>
                </div>
              </div>
              
              <div className="modal-content">
                <div className="modal-image-container">
                  <img
                    src={`data:image/jpeg;base64,${selectedResult.image_base64}`}
                    alt={`Processed ${selectedResult.fileName}`}
                    className="modal-image"
                    style={{ transform: `scale(${imageZoom})` }}
                  />
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProcessingResults;