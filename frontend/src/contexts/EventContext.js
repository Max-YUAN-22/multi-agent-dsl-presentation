import React, { createContext, useContext, useReducer, useCallback, useRef } from 'react';
import useWebSocket from '../hooks/useWebSocket';

const EventContext = createContext();

const initialState = {
  events: [],
  traffic: {},
  weather: {},
  parking: {},
  safety: {},
};

const eventReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_EVENT':
      return { ...state, events: [action.payload, ...state.events] };
    case 'CLEAR_EVENTS':
      return { ...state, events: [] };
    case 'SET_TRAFFIC':
      return { ...state, traffic: action.payload };
    case 'SET_WEATHER':
      return { ...state, weather: action.payload };
    case 'SET_PARKING':
      return { ...state, parking: action.payload };
    case 'SET_SAFETY':
      return { ...state, safety: action.payload };
    default:
      return state;
  }
};

export const EventProvider = ({ children }) => {
  const [state, dispatch] = useReducer(eventReducer, initialState);
  const idCounter = useRef(0);

  const wsUrl = `ws://localhost:8000/ws`;

  const onMessage = useCallback((message) => {
    const newEvent = {
      ...JSON.parse(message.data),
      id: idCounter.current++, // Use a counter for unique IDs
      at: new Date().toLocaleTimeString(),
    };

    dispatch({ type: 'ADD_EVENT', payload: newEvent });
  }, [dispatch]);

  const clearEvents = useCallback(() => {
    dispatch({ type: 'CLEAR_EVENTS' });
  }, [dispatch]);

  const { sendMessage, readyState } = useWebSocket(wsUrl, onMessage);

  return (
    <EventContext.Provider value={{ state, dispatch, sendMessage, readyState, clearEvents }}>
      {children}
    </EventContext.Provider>
  );
};

export const useEventContext = () => useContext(EventContext);