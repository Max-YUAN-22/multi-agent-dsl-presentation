// frontend/src/components/SafetyInspectionCard.jsx
import React from 'react';
import './Card.css';
import { useEventContext } from '../contexts/EventContext';

const SafetyInspectionCard = ({ data, onUpdate, onSubmit }) => {
  const { sendMessage } = useEventContext();

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage({ event: 'update_safety_inspection', data });
    if (onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <div className="card">
      <h2 className="card__title">Safety Inspection</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          <span>Location</span>
          <input type="text" name="location" value={data.location} onChange={onUpdate} />
        </label>
        <div className="checkbox">
          <input type="checkbox" name="require_human_intervention" checked={data.require_human_intervention} onChange={onUpdate} />
          <span>Require Human Intervention</span>
        </div>
        <div className="quickfill">
          <span>Quick Fill:</span>
          <button type="button" onClick={() => onUpdate({ target: { name: 'location', value: 'E' } })}>E</button>
        </div>
        <button type="submit" className="btn">Send</button>
      </form>
    </div>
  );
};

export default SafetyInspectionCard;