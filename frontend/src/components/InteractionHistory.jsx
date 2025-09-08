// frontend/src/components/InteractionHistory.jsx
import React from 'react';
import './InteractionHistory.css';

const InteractionHistory = ({ events, onClear, readyState }) => {
  const getStatusPill = () => {
    switch (readyState) {
      case WebSocket.CONNECTING:
        return <span className="pill pill-status-connecting">Connecting...</span>;
      case WebSocket.OPEN:
        return <span className="pill pill-status-open">Connected</span>;
      case WebSocket.CLOSING:
        return <span className="pill pill-status-closing">Closing...</span>;
      case WebSocket.CLOSED:
        return <span className="pill pill-status-closed">Service Unavailable</span>;
      default:
        return <span className="pill pill-status-closed">Service Unavailable</span>;
    }
  };

  const renderEvent = (event) => {
    switch (event.type) {
      case 'traffic_incident':
        return (
          <li key={event.id}>
            <div className="history__line">
              <span className="pill">{event.title}</span>
              <span className="loc">{event.payload.location}</span>
            </div>
            <div className="history__meta">
              <span>{event.at}</span>
              <span>{event.payload.description}</span>
              <span>Severity: {event.payload.severity}</span>
            </div>
          </li>
        );
      default:
        return (
          <li key={event.id}>
            <div className="history__line">
              <span className="pill">{event.title || 'Unknown Event'}</span>
            </div>
            <div className="history__meta">
              <span>{event.at}</span>
              <pre>{JSON.stringify(event.payload, null, 2)}</pre>
            </div>
          </li>
        );
    }
  };

  return (
    <div className="interaction-record card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="card__title">Interaction History</h2>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {getStatusPill()}
          <button onClick={onClear} className="clear-btn" style={{ marginLeft: '1rem' }}>Clear History</button>
        </div>
      </div>
      <div className="history-scroll">
        {events.length === 0 ? (
          <p className="muted">No records yet. Send a module to see the history.</p>
        ) : (
          <ul className="history">
            {events.map((event) => renderEvent(event))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default InteractionHistory;