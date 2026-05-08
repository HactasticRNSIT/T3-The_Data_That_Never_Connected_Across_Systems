import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import mapReducer from './mapSlice';
import alertsReducer from './alertsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    map: mapReducer,
    alerts: alertsReducer,
  },
});
