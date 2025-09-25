import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, 
  Eye, 
  RotateCcw, 
  Clock, 
  FileText, 
  Trash2, 
  ZoomIn,
  ZoomOut,
  RotateLeft,
  X
} from 'lucide-react';

const ProcessingResults = ({ results, onClear }) => {
  const [selectedResult, setSelectedResult] = useState(null);
  const [imageZoom, setImageZoom] = useState(1);

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

  return (
    <div className="processing-results">
      <div className="results-header">
        <h2 className="results-title">
          <FileText size={24} />
          Processing Results ({results.length})
        </h2>
        <button onClick={onClear} className="btn btn-outline">
          <Trash2 size={16} />
          Clear All
        </button>
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
                  <RotateCcw size={16} />
                  <span>Rotation: {formatRotationAngle(result.rotation_angle)}</span>
                </div>
                
                <div className="stat">
                  <Clock size={16} />
                  <span>{formatProcessingTime(result.processing_time_ms)}</span>
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