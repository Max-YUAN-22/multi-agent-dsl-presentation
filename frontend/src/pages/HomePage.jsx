import React, { useState } from 'react';
import './HomePage.css';
import { useEventContext } from '../contexts/EventContext';
import AutonomousDrivingCard from '../components/AutonomousDrivingCard';
import ParkingUpdateCard from '../components/ParkingUpdateCard';
import SafetyInspectionCard from '../components/SafetyInspectionCard';
import WeatherAlertCard from '../components/WeatherAlertCard';
import InteractionHistory from '../components/InteractionHistory';

const HomePage = () => {
  const { state, sendMessage, readyState, clearEvents } = useEventContext();
  const { events } = state;

  const [formData, setFormData] = useState({
    autonomous_driving: {
      start_location: '',
      end_location: '',
      passengers: 1,
    },
    weather_alert: {
      location: '',
      alert_type: '',
      severity: 5,
    },
    parking_update: {
      location: '',
      available_spots: 0,
    },
    safety_inspection: {
      location: '',
      require_human_intervention: false,
    },
  });

  const handleFormUpdate = (form, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [form]: {
        ...prev[form],
        [field]: value,
      },
    }));
  };

  return (
    <div className="homepage">
      <header className="homepage__header">
        <h1 className="homepage__title">Agent Interaction Platform</h1>
        <p className="homepage__subtitle">
          Monitor and control autonomous systems in real-time
        </p>
      </header>
      <main className="homepage__main">
        <div className="card-grid">
          <AutonomousDrivingCard
            data={formData.autonomous_driving}
            onUpdate={(e) =>
              handleFormUpdate('autonomous_driving', e.target.name, e.target.value)
            }
          />
          <WeatherAlertCard
            data={formData.weather_alert}
            onUpdate={(e) =>
              handleFormUpdate('weather_alert', e.target.name, e.target.value)
            }
          />
          <ParkingUpdateCard
            data={formData.parking_update}
            onUpdate={(e) =>
              handleFormUpdate('parking_update', e.target.name, e.target.value)
            }
          />
          <SafetyInspectionCard
            data={formData.safety_inspection}
            onUpdate={(e) =>
              handleFormUpdate(
                'safety_inspection',
                e.target.name,
                e.target.type === 'checkbox' ? e.target.checked : e.target.value
              )
            }
          />
        </div>
        <InteractionHistory events={events} onClear={clearEvents} readyState={readyState} />
      </main>
    </div>
  );
};

export default HomePage;