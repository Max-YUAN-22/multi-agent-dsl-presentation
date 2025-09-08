// frontend/src/components/WeatherAlertCard.jsx
import React from 'react';
import './Card.css';
import { useEventContext } from '../contexts/EventContext';

const WeatherAlertCard = ({ data, onUpdate, onSubmit }) => {
  const { sendMessage } = useEventContext();

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage({ event: 'update_weather_alert', data });
    if (onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <div className="card">
      <h2 className="card__title">Weather Alert</h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form__row">
          <label>
            <span>Location</span>
            <input type="text" name="location" value={data.location} onChange={onUpdate} />
          </label>
          <label>
            <span>Alert Type</span>
            <select name="alert_type" value={data.alert_type} onChange={onUpdate}>
              <option value="">Please select</option>
              <option value="heavy_rain">Heavy Rain</option>
              <option value="high_temperature">High Temperature</option>
              <option value="strong_wind">Strong Wind</option>
              <option value="snow">Snow</option>
            </select>
          </label>
        </div>
        <label>
          <span>Severity</span>
          <input type="number" name="severity" value={data.severity} onChange={onUpdate} />
        </label>
        <div className="quickfill">
          <span>Quick Fill:</span>
          <button type="button" onClick={() => onUpdate({ target: { name: 'location', value: 'C' } })}>C</button>
          <button type="button" onClick={() => onUpdate({ target: { name: 'alert_type', value: 'heavy_rain' } })}>Heavy Rain</button>
        </div>
        <button type="submit" className="btn">Send</button>
      </form>
    </div>
  );
};

export default WeatherAlertCard;