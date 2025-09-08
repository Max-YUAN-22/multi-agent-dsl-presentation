// frontend/src/components/Header.jsx
import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="page__header">
      <h1>City Brain Agent</h1>
      <p className="subtitle">A platform for demonstrating multi-agent collaboration based on Large Language Models (LLMs)</p>
    </header>
  );
};

export default Header;