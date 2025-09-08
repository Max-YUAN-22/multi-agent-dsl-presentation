import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { EventProvider } from './contexts/EventContext';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <EventProvider>
    <App />
  </EventProvider>
);

reportWebVitals();
