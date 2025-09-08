// src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { Button, Card, Grid } from '@mui/material';
import WebSocketService from './WebSocketService';
import TrafficChart from './TrafficChart'; // Used to display chart components

const Dashboard = () => {
  const [trafficData, setTrafficData] = useState(null);

  useEffect(() => {
    WebSocketService.connect('ws://127.0.0.1:8000/ws'); // WebSocket service
    WebSocketService.onMessage((data) => {
      setTrafficData(data); // Receive real-time data
    });
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <h2>Real-time Traffic</h2>
            <TrafficChart data={trafficData} />
            <Button variant="contained" color="primary">
              Send Task
            </Button>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;
