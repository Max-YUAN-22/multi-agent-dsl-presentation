// frontend/src/components/AutonomousDrivingCard.jsx
import React from 'react';
import './Card.css';
import { useEventContext } from '../contexts/EventContext';

const AutonomousDrivingCard = ({ data, onUpdate, onSubmit }) => {
  const { sendMessage } = useEventContext();

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage({ event: 'update_autonomous_driving_task', data });
    if (onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <div className="card">
      <h2 className="card__title">Autonomous Driving Task</h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form__row">
          <label>
            <span>Start Location</span>
            <input type="text" name="start_location" value={data.start_location} onChange={onUpdate} />
          </label>
          <label>
            <span>End Location</span>
            <input type="text" name="end_location" value={data.end_location} onChange={onUpdate} />
          </label>
        </div>
        <label>
          <span>Passengers</span>
          <input type="number" name="passengers" value={data.passengers} onChange={onUpdate} />
        </label>
        <div className="quickfill">
          <span>Quick Fill:</span>
          <button type="button" onClick={() => onUpdate({ target: { name: 'start_location', value: 'A' } })}>A</button>
          <button type="button" onClick={() => onUpdate({ target: { name: 'end_location', value: 'B' } })}>B</button>
        </div>
        <button type="submit" className="btn">Send</button>
      </form>
    </div>
  );
};

export default AutonomousDrivingCard;