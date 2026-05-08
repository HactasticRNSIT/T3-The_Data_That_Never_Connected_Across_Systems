import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  heatmapData: {
    type: 'FeatureCollection',
    meta: { hex_count: 0 },
    features: []
  },
  selectedHex: null,
  isMapLoading: false,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setHeatmapData: (state, action) => {
      state.heatmapData = action.payload;
      state.isMapLoading = false;
    },
    setMapLoading: (state, action) => {
      state.isMapLoading = action.payload;
    },
    setSelectedHex: (state, action) => {
      state.selectedHex = action.payload;
    },
    updateHexTier: (state, action) => {
      const { hex_id, new_tier, risk_score } = action.payload;
      const feature = state.heatmapData.features.find(f => f.properties.hex_id === hex_id);
      if (feature) {
        feature.properties.risk_tier = new_tier;
        feature.properties.risk_score = risk_score;
      }
      if (state.selectedHex?.hex_id === hex_id) {
        state.selectedHex = { ...state.selectedHex, risk_tier: new_tier, risk_score };
      }
    }
  },
});

export const { setHeatmapData, setMapLoading, setSelectedHex, updateHexTier } = mapSlice.actions;
export default mapSlice.reducer;
