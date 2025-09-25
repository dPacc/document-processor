import React from 'react';
import { motion } from 'framer-motion';
import { Heart, Globe, Mail, Phone } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="footer">
      <motion.div 
        className="footer-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
      >
        <div className="footer-section">
          <div className="footer-brand">
            <h3 className="footer-title">NOVA IT</h3>
            <p className="footer-subtitle">Subsidiary of AKW Consultants</p>
            <p className="footer-description">
              Delivering cutting-edge document processing solutions with enterprise-grade 
              security and AI-powered accuracy.
            </p>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-section-title">Services</h4>
          <ul className="footer-links">
            <li>Document Processing</li>
            <li>AI-Powered OCR</li>
            <li>Enterprise Solutions</li>
            <li>API Integration</li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-section-title">Company</h4>
          <ul className="footer-links">
            <li>About AKW Consultants</li>
            <li>Privacy Policy</li>
            <li>Terms of Service</li>
            <li>Security</li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-section-title">Contact</h4>
          <div className="footer-contact">
            <div className="contact-item">
              <Mail size={16} />
              <span>info@akwconsultants.com</span>
            </div>
            <div className="contact-item">
              <Phone size={16} />
              <span>+971 4 XXX XXXX</span>
            </div>
            <div className="contact-item">
              <Globe size={16} />
              <span>Dubai, UAE | London, UK</span>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <p className="copyright">
            © 2024 NOVA IT, a subsidiary of AKW Consultants. All rights reserved.
          </p>
          <div className="footer-love">
            <span>Made with</span>
            <Heart size={14} className="heart-icon" fill="currentColor" />
            <span>for better document processing</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;