// frontend/src/components/ParkingUpdateCard.jsx
import React from 'react';
import './Card.css';
import { useEventContext } from '../contexts/EventContext';

const ParkingUpdateCard = ({ data, onUpdate, onSubmit }) => {
  const { sendMessage } = useEventContext();

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage({ event: 'update_parking_update', data });
    if (onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <div className="card">
      <h2 className="card__title">Parking Update</h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form__row">
          <label>
            <span>Location</span>
            <input type="text" name="location" value={data.location} onChange={onUpdate} />
          </label>
          <label>
            <span>Available Spots</span>
            <input type="number" name="available_spots" value={data.available_spots} onChange={onUpdate} />
          </label>
        </div>
        <div className="quickfill">
          <span>Quick Fill:</span>
          <button type="button" onClick={() => onUpdate({ target: { name: 'location', value: 'D' } })}>D</button>
        </div>
        <button type="submit" className="btn">Send</button>
      </form>
    </div>
  );
};

export default ParkingUpdateCard;