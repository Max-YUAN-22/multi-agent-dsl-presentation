import React from 'react';
import './App.css';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';

function App() {
  return (
    <MainLayout>
      <HomePage />
    </MainLayout>
  );
}

export default App;
