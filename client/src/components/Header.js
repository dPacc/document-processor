import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Zap, Shield } from 'lucide-react';

const Header = () => {
  return (
    <header className="header">
      <motion.nav 
        className="navbar"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="nav-container">
          <div className="logo-section">
            <motion.div 
              className="logo"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <div className="logo-icon">
                <FileText size={32} className="logo-icon-svg" />
                <Zap size={16} className="logo-accent" />
              </div>
              <div className="logo-text">
                <h1 className="company-name">NOVA IT</h1>
                <p className="company-subtitle">Subsidiary of AKW Consultants</p>
              </div>
            </motion.div>
          </div>
          
          <div className="nav-features">
            <motion.div 
              className="feature-badge"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <Shield size={16} />
              <span>Enterprise Ready</span>
            </motion.div>
            <motion.div 
              className="feature-badge"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <Zap size={16} />
              <span>AI Powered</span>
            </motion.div>
          </div>
        </div>
      </motion.nav>
    </header>
  );
};

export default Header;