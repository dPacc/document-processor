import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Keyboard, X } from 'lucide-react';

const KeyboardShortcuts = () => {
  const [isVisible, setIsVisible] = useState(false);

  const shortcuts = [
    { key: 'Ctrl/⌘ + U', description: 'Upload files' },
    { key: 'Ctrl/⌘ + Enter', description: 'Process files' },
    { key: 'Ctrl/⌘ + D', description: 'Download all results' },
    { key: 'Escape', description: 'Close modal or clear results' },
    { key: 'Delete', description: 'Clear all results' },
    { key: '?', description: 'Show/hide this help' }
  ];

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === '?' && !event.ctrlKey && !event.metaKey) {
        event.preventDefault();
        setIsVisible(prev => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="keyboard-shortcuts-trigger"
        title="Keyboard shortcuts (?)"
        aria-label="Show keyboard shortcuts"
      >
        <Keyboard size={18} />
      </button>

      <AnimatePresence>
        {isVisible && (
          <motion.div
            className="keyboard-shortcuts-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsVisible(false)}
          >
            <motion.div
              className="keyboard-shortcuts-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="shortcuts-header">
                <h3>Keyboard Shortcuts</h3>
                <button
                  onClick={() => setIsVisible(false)}
                  className="close-shortcuts"
                  aria-label="Close shortcuts help"
                >
                  <X size={18} />
                </button>
              </div>
              
              <div className="shortcuts-content">
                {shortcuts.map((shortcut, index) => (
                  <div key={index} className="shortcut-item">
                    <kbd className="shortcut-key">{shortcut.key}</kbd>
                    <span className="shortcut-description">{shortcut.description}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default KeyboardShortcuts;