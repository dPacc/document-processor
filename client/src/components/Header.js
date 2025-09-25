import React from 'react';
import { FileText } from 'lucide-react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <FileText size={24} className="logo-icon" />
          <span className="logo-text">Document Processor</span>
        </div>
      </div>
    </header>
  );
};

export default Header;