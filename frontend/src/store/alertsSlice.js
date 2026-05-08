import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: [],
  total: 0,
  isLoading: false,
};

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    setAlerts: (state, action) => {
      state.items = action.payload.alerts;
      state.total = action.payload.total;
      state.isLoading = false;
    },
    setAlertsLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    addAlert: (state, action) => {
      // Prepend the new alert
      state.items = [action.payload, ...state.items];
      state.total += 1;
    }
  },
});

export const { setAlerts, setAlertsLoading, addAlert } = alertsSlice.actions;
export default alertsSlice.reducer;
